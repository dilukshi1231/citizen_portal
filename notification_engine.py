"""
Smart Notification Engine
Analyzes user behavior and demographics to trigger personalized advertisements
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

class NotificationEngine:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client["citizen_portal"]
        self.users_col = self.db["users"]
        self.eng_col = self.db["engagements"]
        self.notifications_col = self.db["notifications"]
        self.ads_col = self.db["ads"]
        
    def analyze_user_and_trigger_ads(self, user_id: str, session_data: dict = None) -> List[Dict]:
        """
        Main function to analyze user and trigger relevant advertisements
        
        Args:
            user_id: User's MongoDB ID
            session_data: Current session info (age, job, language, etc.)
        
        Returns:
            List of personalized notifications/ads
        """
        # Get user profile
        user_profile = self._get_user_profile(user_id, session_data)
        
        # Analyze user behavior
        behavior_insights = self._analyze_user_behavior(user_id)
        
        # Get matching advertisements
        relevant_ads = self._match_advertisements(user_profile, behavior_insights)
        
        # Create notifications
        notifications = self._create_notifications(user_id, relevant_ads)
        
        return notifications
    
    def _get_user_profile(self, user_id: str, session_data: dict = None) -> Dict:
        """Get comprehensive user profile"""
        profile = {
            "user_id": user_id,
            "age": None,
            "age_group": None,
            "job": None,
            "job_category": None,
            "education": None,
            "has_children": False,
            "children_ages": [],
            "location": None,
            "language": "en",
            "segments": []
        }
        
        # Try to get from database
        try:
            user = self.users_col.find_one({"_id": ObjectId(user_id)})
            if user:
                profile["age"] = user.get("age")
                profile["job"] = user.get("job") or user.get("occupation")
                profile["location"] = user.get("location") or user.get("district")
                profile["language"] = user.get("language", "en")
                
                # Extended profile
                ext_profile = user.get("extended_profile", {})
                
                # Education
                education = ext_profile.get("education", {})
                profile["education"] = education.get("highest_qualification")
                
                # Family
                family = ext_profile.get("family", {})
                profile["has_children"] = family.get("children_count", 0) > 0
                profile["children_ages"] = family.get("children_ages", [])
        except:
            pass
        
        # Override with session data if provided
        if session_data:
            profile["age"] = session_data.get("age") or profile["age"]
            profile["job"] = session_data.get("job") or profile["job"]
            profile["language"] = session_data.get("language") or profile["language"]
        
        # Derive age group
        if profile["age"]:
            age = int(profile["age"])
            if age < 18:
                profile["age_group"] = "under_18"
            elif 18 <= age <= 25:
                profile["age_group"] = "18_25"
            elif 26 <= age <= 35:
                profile["age_group"] = "26_35"
            elif 36 <= age <= 45:
                profile["age_group"] = "36_45"
            elif 46 <= age <= 60:
                profile["age_group"] = "46_60"
            else:
                profile["age_group"] = "60_plus"
        
        # Categorize job
        if profile["job"]:
            job_lower = profile["job"].lower()
            
            if any(word in job_lower for word in ["teacher", "lecturer", "professor", "educator"]):
                profile["job_category"] = "teacher"
                profile["segments"].append("education_professional")
            
            elif any(word in job_lower for word in ["government", "civil", "public service"]):
                profile["job_category"] = "government"
                profile["segments"].append("government_employee")
            
            elif any(word in job_lower for word in ["engineer", "developer", "programmer", "it"]):
                profile["job_category"] = "tech"
                profile["segments"].append("tech_professional")
            
            elif any(word in job_lower for word in ["doctor", "nurse", "medical"]):
                profile["job_category"] = "healthcare"
                profile["segments"].append("healthcare_professional")
            
            elif any(word in job_lower for word in ["business", "entrepreneur", "owner"]):
                profile["job_category"] = "business"
                profile["segments"].append("entrepreneur")
            
            elif "student" in job_lower:
                profile["job_category"] = "student"
                profile["segments"].append("student")
        
        # Family-based segments
        if profile["has_children"]:
            profile["segments"].append("parent")
            
            for child_age in profile["children_ages"]:
                if 5 <= child_age <= 11:
                    profile["segments"].append("primary_school_parent")
                elif 12 <= child_age <= 16:
                    profile["segments"].append("secondary_school_parent")
                elif 17 <= child_age <= 20:
                    profile["segments"].append("university_age_parent")
        
        return profile
    
    def _analyze_user_behavior(self, user_id: str) -> Dict:
        """Analyze user's recent behavior and search patterns"""
        insights = {
            "recent_searches": [],
            "frequent_services": [],
            "interests": [],
            "search_frequency": 0,
            "needs_help": False,
            "help_topics": []
        }
        
        # Get recent engagements (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_engagements = list(self.eng_col.find({
            "user_id": user_id,
            "timestamp": {"$gte": thirty_days_ago}
        }).sort("timestamp", -1).limit(50))
        
        insights["search_frequency"] = len(recent_engagements)
        
        # Extract search patterns
        search_topics = {}
        service_counts = {}
        
        for eng in recent_engagements:
            # Track questions
            question = eng.get("question_clicked")
            if question:
                insights["recent_searches"].append(question)
                search_topics[question] = search_topics.get(question, 0) + 1
            
            # Track services
            service = eng.get("service")
            if service:
                service_counts[service] = service_counts.get(service, 0) + 1
            
            # Extract interests from desires
            for desire in eng.get("desires", []):
                if desire not in insights["interests"]:
                    insights["interests"].append(desire)
        
        # Identify frequent services
        insights["frequent_services"] = sorted(
            service_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Detect if user needs help (repeated searches)
        for topic, count in search_topics.items():
            if count >= 3:
                insights["needs_help"] = True
                insights["help_topics"].append(topic)
        
        return insights
    
    def _match_advertisements(self, profile: Dict, behavior: Dict) -> List[Dict]:
        """Match user profile with relevant advertisements"""
        matched_ads = []
        
        # Get all active ads
        all_ads = list(self.ads_col.find({"active": True}))
        
        for ad in all_ads:
            score = 0
            reasons = []
            
            # Check target segments
            target_segments = ad.get("target_segments", [])
            if target_segments:
                matching_segments = set(profile["segments"]) & set(target_segments)
                if matching_segments:
                    score += 20 * len(matching_segments)
                    reasons.append(f"Matches your profile: {', '.join(matching_segments)}")
            
            # Check age group targeting
            target_age_groups = ad.get("target_age_groups", [])
            if target_age_groups and profile["age_group"] in target_age_groups:
                score += 15
                reasons.append(f"Relevant for your age group")
            
            # Check job category
            target_jobs = ad.get("target_jobs", [])
            if target_jobs and profile["job_category"] in target_jobs:
                score += 25
                reasons.append(f"Relevant for {profile['job_category']}s")
            
            # Check location targeting
            target_locations = ad.get("target_locations", [])
            if target_locations and profile["location"] in target_locations:
                score += 10
                reasons.append(f"Available in {profile['location']}")
            
            # Check education level
            target_education = ad.get("target_education", [])
            if target_education and profile["education"] in target_education:
                score += 10
                reasons.append("Matches your education level")
            
            # Check behavior-based targeting
            ad_keywords = ad.get("keywords", [])
            if ad_keywords:
                for search in behavior["recent_searches"][:10]:
                    search_lower = search.lower()
                    for keyword in ad_keywords:
                        if keyword.lower() in search_lower:
                            score += 5
                            reasons.append(f"Related to your recent search")
                            break
            
            # Check interest matching
            ad_interests = ad.get("related_interests", [])
            if ad_interests:
                matching_interests = set(behavior["interests"]) & set(ad_interests)
                if matching_interests:
                    score += 10 * len(matching_interests)
                    reasons.append("Matches your interests")
            
            # Priority boost
            priority = ad.get("priority", 0)
            score += priority * 5
            
            # Only include ads with minimum relevance
            if score >= 15:
                ad["relevance_score"] = score
                ad["match_reasons"] = reasons
                matched_ads.append(ad)
        
        # Sort by relevance score
        matched_ads.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return matched_ads[:5]  # Return top 5
    
    def _create_notifications(self, user_id: str, ads: List[Dict]) -> List[Dict]:
        """Create notification records for matched ads"""
        notifications = []
        
        for ad in ads:
            notification = {
                "user_id": user_id,
                "type": "advertisement",
                "priority": ad.get("priority", "medium"),
                "title": ad.get("title", {}).get("en", "New Opportunity"),
                "message": ad.get("body", {}).get("en", ""),
                "link": ad.get("link", ""),
                "image": ad.get("image", ""),
                "category": ad.get("category", "general"),
                "relevance_score": ad.get("relevance_score", 0),
                "match_reasons": ad.get("match_reasons", []),
                "created": datetime.utcnow(),
                "read": False,
                "dismissed": False,
                "expires_at": datetime.utcnow() + timedelta(days=ad.get("duration_days", 7))
            }
            
            # Save to database
            result = self.notifications_col.insert_one(notification)
            notification["_id"] = str(result.inserted_id)
            
            notifications.append(notification)
        
        return notifications
    
    def get_unread_notifications(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get unread notifications for user"""
        notifications = list(self.notifications_col.find({
            "user_id": user_id,
            "read": False,
            "dismissed": False,
            "expires_at": {"$gte": datetime.utcnow()}
        }).sort("relevance_score", -1).limit(limit))
        
        for notif in notifications:
            notif["_id"] = str(notif["_id"])
            notif["created"] = notif["created"].isoformat()
            notif["expires_at"] = notif["expires_at"].isoformat()
        
        return notifications
    
    def mark_as_read(self, notification_id: str):
        """Mark notification as read"""
        self.notifications_col.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"read": True, "read_at": datetime.utcnow()}}
        )
    
    def dismiss_notification(self, notification_id: str):
        """Dismiss a notification"""
        self.notifications_col.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"dismissed": True, "dismissed_at": datetime.utcnow()}}
        )


# Example usage and testing
if __name__ == "__main__":
    engine = NotificationEngine()
    
    # Test with a teacher profile
    test_profile = {
        "age": 35,
        "job": "Teacher",
        "language": "en"
    }
    
    # Simulate user ID
    test_user_id = "test_teacher_001"
    
    print("🔔 Testing Notification Engine")
    print("=" * 70)
    
    # Analyze and generate notifications
    notifications = engine.analyze_user_and_trigger_ads(test_user_id, test_profile)
    
    print(f"\n✅ Generated {len(notifications)} personalized notifications:")
    for i, notif in enumerate(notifications, 1):
        print(f"\n{i}. {notif['title']}")
        print(f"   Priority: {notif['priority']}")
        print(f"   Score: {notif['relevance_score']}")
        print(f"   Reasons: {', '.join(notif['match_reasons'][:2])}")