"""
Smart Recommendation Engine
Handles user segmentation and personalized recommendations
"""

import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

class RecommendationEngine:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client["citizen_portal"]
        self.users_col = self.db["users"]
        self.eng_col = self.db["engagements"]
        self.products_col = self.db["products"]
    
    def get_user_segment(self, user_id):
        """Segment users based on demographics and behavior"""
        try:
            user = self.users_col.find_one({"_id": ObjectId(user_id)})
        except:
            user = self.users_col.find_one({"_id": user_id})
        
        if not user:
            return ["unknown"]
        
        profile = user.get('extended_profile', {})
        segments = []
        
        # Age-based segments
        age = profile.get('family', {}).get('age') or user.get('age')
        if age:
            try:
                age = int(age)
                if age < 25:
                    segments.append("young_adult")
                elif 25 <= age <= 35:
                    segments.append("early_career")
                elif 36 <= age <= 45:
                    segments.append("mid_career_family")
                elif 46 <= age <= 60:
                    segments.append("established_professional")
                else:
                    segments.append("senior")
            except:
                pass
        
        # Education-based segments
        education = profile.get('education', {}).get('highest_qualification', '').lower()
        if education in ['none', 'school', 'ol']:
            segments.append("needs_qualification")
        elif education in ['al', 'diploma']:
            segments.append("mid_education")
        elif education in ['degree', 'masters', 'phd']:
            segments.append("highly_educated")
        
        # Family-based segments
        children = profile.get('family', {}).get('children', [])
        if children:
            segments.append("parent")
            children_ages = profile.get('family', {}).get('children_ages', [])
            
            if any(5 <= age <= 10 for age in children_ages if age):
                segments.append("primary_school_parent")
            if any(11 <= age <= 16 for age in children_ages if age):
                segments.append("secondary_school_parent")
            if any(17 <= age <= 20 for age in children_ages if age):
                segments.append("university_age_parent")
        
        # Career-based segments
        job = (profile.get('career', {}).get('current_job') or user.get('job', '')).lower()
        if 'government' in job:
            segments.append("government_employee")
        if any(word in job for word in ['manager', 'director', 'head']):
            segments.append("management")
        
        return list(set(segments)) if segments else ["general"]
    
    def get_personalized_ads(self, user_id, limit=5):
        """Get personalized product/service recommendations"""
        segments = self.get_user_segment(user_id)
        
        # Get user engagement history
        user_engagements = list(self.eng_col.find({"user_id": user_id}))
        
        # Extract interests
        interests = []
        for eng in user_engagements:
            interests.extend(eng.get('desires', []))
            if eng.get('question_clicked'):
                interests.append(eng['question_clicked'])
            if eng.get('service'):
                interests.append(eng['service'])
        
        # Score products
        products = list(self.products_col.find({"in_stock": True}))
        scored_products = []
        
        for product in products:
            score = 0
            product_tags = product.get('tags', [])
            product_segments = product.get('target_segments', [])
            
            # Segment matching (high weight)
            segment_match = len(set(segments) & set(product_segments))
            score += segment_match * 10
            
            # Interest matching
            interest_match = len(set(interests) & set(product_tags))
            score += interest_match * 5
            
            # Recency boost
            if product.get('created'):
                days_old = (datetime.utcnow() - product['created']).days
                if days_old < 7:
                    score += 5
                elif days_old < 30:
                    score += 2
            
            if score > 0:
                product['relevance_score'] = score
                scored_products.append(product)
        
        # Sort by score
        scored_products.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return scored_products[:limit]
    
    def generate_education_recommendations(self, user_id):
        """Generate education recommendations based on profile"""
        try:
            user = self.users_col.find_one({"_id": ObjectId(user_id)})
        except:
            user = self.users_col.find_one({"_id": user_id})
        
        if not user:
            return []
        
        profile = user.get('extended_profile', {})
        education = profile.get('education', {})
        career = profile.get('career', {})
        age = profile.get('family', {}).get('age') or user.get('age')
        
        recommendations = []
        
        # Degree completion for government employees
        qual = education.get('highest_qualification', '').lower()
        job = (career.get('current_job') or user.get('job', '')).lower()
        
        if qual in ['ol', 'al', 'diploma'] and 'government' in job:
            if age and 25 <= int(age) <= 50:
                recommendations.append({
                    "type": "education",
                    "title": "Complete Your Degree",
                    "message": "Enhance your career with a recognized degree program",
                    "priority": "high",
                    "tags": ["degree", "government", "career_advancement"]
                })
        
        # Children education
        children_ages = profile.get('family', {}).get('children_ages', [])
        for child_age in children_ages:
            if 15 <= child_age <= 18:
                recommendations.append({
                    "type": "child_education",
                    "title": "O/L Exam Preparation",
                    "message": "Special courses for your child's O/L exams",
                    "priority": "medium",
                    "tags": ["ol_exams", "tuition"]
                })
            
            if 17 <= child_age <= 20:
                recommendations.append({
                    "type": "child_education",
                    "title": "A/L Stream Selection Guidance",
                    "message": "Expert guidance for A/L subject selection",
                    "priority": "medium",
                    "tags": ["al_exams", "career_guidance"]
                })
        
        return recommendations