"""
Advertisement Targeting Algorithm
==================================
Automatically triggers relevant advertisements based on user attributes
including profession, age, education, family status, and search behavior.
"""

from datetime import datetime
from typing import Dict, List, Optional
import json


class AdvertisementTargeting:
    """Main class for handling advertisement targeting logic"""
    
    def __init__(self):
        # Define advertisement database with targeting criteria
        self.advertisements = {
            # Education-related ads
            "degree_completion_program": {
                "id": "ad_001",
                "title": "Complete Your Degree - Government Employee Special",
                "description": "Enhance your career with recognized degree programs designed for working professionals",
                "image_url": "/ads/degree_program.jpg",
                "link": "/services/education/degree-programs",
                "type": "education",
                "priority": "high",
                "targeting_rules": {
                    "profession": ["government", "public sector", "state employee"],
                    "education_level": ["O/L", "A/L", "diploma"],
                    "age_range": [25, 50],
                    "exclude_education": ["bachelor", "master", "phd"]
                }
            },
            
            "teacher_training_program": {
                "id": "ad_002",
                "title": "Advanced Teacher Training & Certifications",
                "description": "Professional development courses for educators. Get certified!",
                "image_url": "/ads/teacher_training.jpg",
                "link": "/services/education/teacher-training",
                "type": "professional_development",
                "priority": "high",
                "targeting_rules": {
                    "profession": ["teacher", "educator", "principal", "tutor", "lecturer"],
                    "age_range": [23, 60],
                    "interests": ["education", "teaching", "career development"]
                }
            },
            
            "ol_exam_prep": {
                "id": "ad_003",
                "title": "O/L Exam Preparation Classes",
                "description": "Expert tutoring for O/L students. Limited seats available!",
                "image_url": "/ads/ol_prep.jpg",
                "link": "/services/education/ol-preparation",
                "type": "child_education",
                "priority": "medium",
                "targeting_rules": {
                    "has_children": True,
                    "children_age_range": [13, 16],
                    "parent_age_range": [30, 55]
                }
            },
            
            "al_exam_prep": {
                "id": "ad_004",
                "title": "A/L Science Stream - Expert Guidance",
                "description": "Specialized coaching for Physics, Chemistry, Biology & Combined Maths",
                "image_url": "/ads/al_prep.jpg",
                "link": "/services/education/al-preparation",
                "type": "child_education",
                "priority": "medium",
                "targeting_rules": {
                    "has_children": True,
                    "children_age_range": [16, 20],
                    "parent_age_range": [35, 60]
                }
            },
            
            # Healthcare ads
            "health_insurance": {
                "id": "ad_005",
                "title": "Family Health Insurance Plans",
                "description": "Comprehensive coverage for you and your family. Get a quote now!",
                "image_url": "/ads/health_insurance.jpg",
                "link": "/services/health/insurance",
                "type": "insurance",
                "priority": "medium",
                "targeting_rules": {
                    "age_range": [25, 65],
                    "marital_status": ["married"],
                    "has_children": True
                }
            },
            
            "senior_healthcare": {
                "id": "ad_006",
                "title": "Senior Citizen Healthcare Package",
                "description": "Specialized healthcare services for seniors. Home visits available.",
                "image_url": "/ads/senior_health.jpg",
                "link": "/services/health/senior-care",
                "type": "healthcare",
                "priority": "high",
                "targeting_rules": {
                    "age_range": [60, 90],
                    "interests": ["health", "wellness"]
                }
            },
            
            # Financial services
            "home_loan": {
                "id": "ad_007",
                "title": "Special Home Loans for Government Employees",
                "description": "Low interest rates. Quick approval. Apply now!",
                "image_url": "/ads/home_loan.jpg",
                "link": "/services/finance/home-loans",
                "type": "finance",
                "priority": "high",
                "targeting_rules": {
                    "profession": ["government", "public sector", "state employee"],
                    "age_range": [25, 55],
                    "marital_status": ["married", "engaged"]
                }
            },
            
            "retirement_planning": {
                "id": "ad_008",
                "title": "Retirement Planning Services",
                "description": "Secure your future with expert financial planning",
                "image_url": "/ads/retirement.jpg",
                "link": "/services/finance/retirement",
                "type": "finance",
                "priority": "medium",
                "targeting_rules": {
                    "age_range": [45, 65],
                    "profession": ["government", "private sector", "business"]
                }
            },
            
            # Career development
            "it_training": {
                "id": "ad_009",
                "title": "IT Certification Programs",
                "description": "Python, Java, Web Development, Data Science courses available",
                "image_url": "/ads/it_training.jpg",
                "link": "/services/training/it-courses",
                "type": "professional_development",
                "priority": "medium",
                "targeting_rules": {
                    "age_range": [18, 45],
                    "profession": ["unemployed", "student", "it", "software"],
                    "interests": ["technology", "coding", "career change"]
                }
            },
            
            "english_classes": {
                "id": "ad_010",
                "title": "Business English for Professionals",
                "description": "Improve your English skills. Weekend batches available.",
                "image_url": "/ads/english.jpg",
                "link": "/services/training/english",
                "type": "skill_development",
                "priority": "low",
                "targeting_rules": {
                    "age_range": [20, 50],
                    "profession": ["government", "private sector", "business"],
                    "interests": ["language", "career development"]
                }
            },
            
            # Targeted by search behavior
            "passport_services": {
                "id": "ad_011",
                "title": "Fast-Track Passport Services",
                "description": "Get your passport quickly with our express service",
                "image_url": "/ads/passport.jpg",
                "link": "/services/government/passport",
                "type": "government_service",
                "priority": "high",
                "targeting_rules": {
                    "recent_searches": ["passport", "travel", "visa"],
                    "age_range": [18, 75]
                }
            },
            
            "business_registration": {
                "id": "ad_012",
                "title": "Register Your Business Today",
                "description": "Complete business registration assistance. Expert guidance.",
                "image_url": "/ads/business_reg.jpg",
                "link": "/services/business/registration",
                "type": "business_service",
                "priority": "high",
                "targeting_rules": {
                    "profession": ["business", "entrepreneur", "self-employed"],
                    "recent_searches": ["business", "company", "registration"],
                    "age_range": [21, 65]
                }
            }
        }
    
    def get_targeted_ads(self, user_profile: Dict, context: Optional[Dict] = None) -> List[Dict]:
        """
        Main method to get targeted advertisements for a user
        
        Args:
            user_profile: User's profile information
            context: Additional context like current search, page viewed, etc.
        
        Returns:
            List of matched advertisements sorted by priority and relevance
        """
        matched_ads = []
        
        for ad_key, ad_data in self.advertisements.items():
            score = self._calculate_match_score(user_profile, ad_data, context)
            
            if score > 0:
                matched_ads.append({
                    **ad_data,
                    "match_score": score,
                    "targeting_reason": self._get_targeting_reason(user_profile, ad_data)
                })
        
        # Sort by priority and match score
        priority_order = {"high": 3, "medium": 2, "low": 1}
        matched_ads.sort(
            key=lambda x: (priority_order.get(x["priority"], 0), x["match_score"]), 
            reverse=True
        )
        
        return matched_ads
    
    def _calculate_match_score(self, user_profile: Dict, ad_data: Dict, context: Optional[Dict]) -> float:
        """
        Calculate how well a user matches an advertisement's targeting rules
        
        Returns a score between 0 and 1 (0 = no match, 1 = perfect match)
        """
        rules = ad_data.get("targeting_rules", {})
        score = 0
        total_criteria = 0
        
        # Extract user information
        age = user_profile.get("age")
        job = (user_profile.get("job") or "").lower()
        extended_profile = user_profile.get("extended_profile", {})
        education = extended_profile.get("education", {})
        family = extended_profile.get("family", {})
        interests = user_profile.get("interests", [])
        recent_searches = user_profile.get("recent_searches", [])
        
        # Add context searches if available
        if context and context.get("current_search"):
            recent_searches.append(context["current_search"].lower())
        
        # Check profession matching
        if "profession" in rules:
            total_criteria += 1
            target_professions = [p.lower() for p in rules["profession"]]
            if any(prof in job for prof in target_professions):
                score += 1
        
        # Check age range
        if "age_range" in rules and age:
            total_criteria += 1
            min_age, max_age = rules["age_range"]
            try:
                user_age = int(age)
                if min_age <= user_age <= max_age:
                    score += 1
            except (ValueError, TypeError):
                pass
        
        # Check education level
        if "education_level" in rules:
            total_criteria += 1
            qual = education.get("highest_qualification", "").lower()
            target_education = [e.lower() for e in rules["education_level"]]
            if any(edu in qual for edu in target_education):
                score += 1
        
        # Exclude certain education levels
        if "exclude_education" in rules:
            qual = education.get("highest_qualification", "").lower()
            exclude_education = [e.lower() for e in rules["exclude_education"]]
            if any(edu in qual for edu in exclude_education):
                return 0  # Hard exclusion
        
        # Check children requirements
        if "has_children" in rules:
            total_criteria += 1
            children_ages = family.get("children_ages", [])
            if rules["has_children"] and len(children_ages) > 0:
                score += 1
            elif not rules["has_children"] and len(children_ages) == 0:
                score += 1
        
        # Check children age range
        if "children_age_range" in rules:
            total_criteria += 1
            children_ages = family.get("children_ages", [])
            min_child_age, max_child_age = rules["children_age_range"]
            if any(min_child_age <= child_age <= max_child_age for child_age in children_ages):
                score += 1
        
        # Check parent age range (when targeting based on children)
        if "parent_age_range" in rules and age:
            total_criteria += 1
            min_parent_age, max_parent_age = rules["parent_age_range"]
            try:
                user_age = int(age)
                if min_parent_age <= user_age <= max_parent_age:
                    score += 1
            except (ValueError, TypeError):
                pass
        
        # Check marital status
        if "marital_status" in rules:
            total_criteria += 1
            user_marital_status = family.get("marital_status", "").lower()
            target_statuses = [s.lower() for s in rules["marital_status"]]
            if user_marital_status in target_statuses:
                score += 1
        
        # Check interests
        if "interests" in rules:
            total_criteria += 1
            target_interests = [i.lower() for i in rules["interests"]]
            user_interests = [i.lower() for i in interests]
            if any(interest in " ".join(user_interests) for interest in target_interests):
                score += 1
        
        # Check recent searches (high weight)
        if "recent_searches" in rules:
            total_criteria += 2  # Give searches double weight
            target_keywords = [k.lower() for k in rules["recent_searches"]]
            user_searches = [s.lower() for s in recent_searches]
            matches = sum(1 for keyword in target_keywords 
                         if any(keyword in search for search in user_searches))
            if matches > 0:
                score += min(matches, 2)  # Cap at 2 points
        
        # Return normalized score
        return score / total_criteria if total_criteria > 0 else 0
    
    def _get_targeting_reason(self, user_profile: Dict, ad_data: Dict) -> str:
        """Generate a human-readable reason for why this ad was shown"""
        rules = ad_data.get("targeting_rules", {})
        reasons = []
        
        job = (user_profile.get("job") or "").lower()
        age = user_profile.get("age")
        
        if "profession" in rules:
            target_professions = rules["profession"]
            if any(prof in job for prof in target_professions):
                reasons.append(f"profession match")
        
        if "age_range" in rules and age:
            min_age, max_age = rules["age_range"]
            try:
                if min_age <= int(age) <= max_age:
                    reasons.append(f"age group")
            except (ValueError, TypeError):
                pass
        
        if "recent_searches" in rules:
            reasons.append("search history")
        
        if "has_children" in rules and rules["has_children"]:
            reasons.append("family profile")
        
        return "Based on: " + ", ".join(reasons) if reasons else "General recommendation"
    
    def trigger_ad_for_page(self, user_profile: Dict, page_type: str, limit: int = 3) -> List[Dict]:
        """
        Trigger advertisements for specific page types
        
        Args:
            user_profile: User's profile data
            page_type: Type of page ('home', 'search', 'service', 'profile', etc.)
            limit: Maximum number of ads to return
        
        Returns:
            List of relevant advertisements
        """
        context = {"page_type": page_type}
        all_ads = self.get_targeted_ads(user_profile, context)
        
        # Filter by page type if needed
        page_relevance = {
            "home": ["education", "finance", "professional_development"],
            "search": ["government_service", "business_service"],
            "education": ["education", "child_education", "skill_development"],
            "health": ["healthcare", "insurance"],
            "finance": ["finance", "insurance"]
        }
        
        if page_type in page_relevance:
            relevant_types = page_relevance[page_type]
            all_ads = [ad for ad in all_ads if ad["type"] in relevant_types] + \
                     [ad for ad in all_ads if ad["type"] not in relevant_types][:limit//2]
        
        return all_ads[:limit]


# Example integration functions
def integrate_with_flask_app():
    """
    Example of how to integrate this with your Flask application
    """
    code_example = '''
# In your app.py

ad_targeting = AdvertisementTargeting()

@app.route('/api/ads/get_ads', methods=['POST'])
def get_user_ads():
    """API endpoint to get targeted ads for a user"""
    data = request.json
    user_id = data.get('user_id')
    page_type = data.get('page_type', 'home')
    limit = data.get('limit', 3)
    
    # Fetch user from database
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get targeted ads
    ads = ad_targeting.trigger_ad_for_page(user, page_type, limit)
    
    # Log ad impressions
    for ad in ads:
        db.ad_impressions.insert_one({
            "user_id": user_id,
            "ad_id": ad["id"],
            "timestamp": datetime.utcnow(),
            "page_type": page_type,
            "match_score": ad["match_score"]
        })
    
    return jsonify({"ads": ads})

@app.route('/api/ads/click/<ad_id>', methods=['POST'])
def track_ad_click(ad_id):
    """Track when a user clicks on an ad"""
    data = request.json
    user_id = data.get('user_id')
    
    db.ad_clicks.insert_one({
        "user_id": user_id,
        "ad_id": ad_id,
        "timestamp": datetime.utcnow()
    })
    
    return jsonify({"status": "success"})
'''
    return code_example


def integrate_with_frontend():
    """
    Example of how to integrate this with your frontend
    """
    code_example = '''
<!-- In your main template or component -->

<div id="ad-container" class="mt-4">
    <!-- Ads will be dynamically loaded here -->
</div>

<script>
async function loadAds(pageType = 'home') {
    const userId = getCurrentUserId(); // Your function to get user ID
    
    const response = await fetch('/api/ads/get_ads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: userId,
            page_type: pageType,
            limit: 3
        })
    });
    
    const data = await response.json();
    displayAds(data.ads);
}

function displayAds(ads) {
    const container = document.getElementById('ad-container');
    container.innerHTML = '';
    
    ads.forEach(ad => {
        const adElement = document.createElement('div');
        adElement.className = 'ad-card bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg shadow mb-3 cursor-pointer hover:shadow-lg transition';
        adElement.innerHTML = `
            <div class="flex items-start">
                <img src="${ad.image_url}" alt="${ad.title}" class="w-20 h-20 object-cover rounded mr-4">
                <div class="flex-1">
                    <h3 class="font-bold text-lg text-gray-800">${ad.title}</h3>
                    <p class="text-sm text-gray-600 mt-1">${ad.description}</p>
                    <p class="text-xs text-gray-500 mt-2">${ad.targeting_reason}</p>
                    <span class="inline-block mt-2 px-3 py-1 bg-blue-600 text-white text-xs rounded-full">
                        Learn More →
                    </span>
                </div>
            </div>
        `;
        
        adElement.addEventListener('click', () => {
            trackAdClick(ad.id);
            window.location.href = ad.link;
        });
        
        container.appendChild(adElement);
    });
}

async function trackAdClick(adId) {
    const userId = getCurrentUserId();
    await fetch(`/api/ads/click/${adId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    });
}

// Load ads when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadAds('home');
});
</script>
'''
    return code_example


# Testing examples
def test_algorithm():
    """Test the algorithm with sample user profiles"""
    
    targeting = AdvertisementTargeting()
    
    # Test Case 1: Teacher, age 35
    print("=" * 80)
    print("TEST CASE 1: Teacher, Age 35")
    print("=" * 80)
    
    teacher_profile = {
        "age": 35,
        "job": "Teacher",
        "interests": ["education", "teaching"],
        "extended_profile": {
            "education": {
                "highest_qualification": "Bachelor"
            },
            "family": {
                "marital_status": "married",
                "children_ages": [14, 17]
            }
        },
        "recent_searches": []
    }
    
    ads = targeting.get_targeted_ads(teacher_profile)
    print(f"\nFound {len(ads)} matching advertisements:")
    for i, ad in enumerate(ads[:5], 1):
        print(f"\n{i}. {ad['title']}")
        print(f"   Type: {ad['type']}")
        print(f"   Priority: {ad['priority']}")
        print(f"   Match Score: {ad['match_score']:.2f}")
        print(f"   {ad['targeting_reason']}")
    
    # Test Case 2: Government employee, age 40, O/L education
    print("\n" + "=" * 80)
    print("TEST CASE 2: Government Employee, Age 40, O/L Education")
    print("=" * 80)
    
    gov_employee_profile = {
        "age": 40,
        "job": "Government Officer",
        "interests": ["career development"],
        "extended_profile": {
            "education": {
                "highest_qualification": "O/L"
            },
            "family": {
                "marital_status": "married",
                "children_ages": []
            }
        },
        "recent_searches": []
    }
    
    ads = targeting.get_targeted_ads(gov_employee_profile)
    print(f"\nFound {len(ads)} matching advertisements:")
    for i, ad in enumerate(ads[:5], 1):
        print(f"\n{i}. {ad['title']}")
        print(f"   Type: {ad['type']}")
        print(f"   Priority: {ad['priority']}")
        print(f"   Match Score: {ad['match_score']:.2f}")
        print(f"   {ad['targeting_reason']}")
    
    # Test Case 3: Parent with teenage children
    print("\n" + "=" * 80)
    print("TEST CASE 3: Parent with Teenage Children (O/L and A/L age)")
    print("=" * 80)
    
    parent_profile = {
        "age": 45,
        "job": "Private Sector Employee",
        "interests": ["family", "education"],
        "extended_profile": {
            "education": {
                "highest_qualification": "Bachelor"
            },
            "family": {
                "marital_status": "married",
                "children_ages": [15, 18]
            }
        },
        "recent_searches": ["education", "tuition classes"]
    }
    
    ads = targeting.get_targeted_ads(parent_profile)
    print(f"\nFound {len(ads)} matching advertisements:")
    for i, ad in enumerate(ads[:5], 1):
        print(f"\n{i}. {ad['title']}")
        print(f"   Type: {ad['type']}")
        print(f"   Priority: {ad['priority']}")
        print(f"   Match Score: {ad['match_score']:.2f}")
        print(f"   {ad['targeting_reason']}")
    
    # Test Case 4: User searching for passport
    print("\n" + "=" * 80)
    print("TEST CASE 4: User Searching for Passport Services")
    print("=" * 80)
    
    passport_searcher = {
        "age": 28,
        "job": "IT Professional",
        "interests": ["travel"],
        "extended_profile": {
            "education": {
                "highest_qualification": "Bachelor"
            },
            "family": {
                "marital_status": "single"
            }
        },
        "recent_searches": ["passport application", "how to get passport", "travel visa"]
    }
    
    ads = targeting.get_targeted_ads(passport_searcher)
    print(f"\nFound {len(ads)} matching advertisements:")
    for i, ad in enumerate(ads[:5], 1):
        print(f"\n{i}. {ad['title']}")
        print(f"   Type: {ad['type']}")
        print(f"   Priority: {ad['priority']}")
        print(f"   Match Score: {ad['match_score']:.2f}")
        print(f"   {ad['targeting_reason']}")


if __name__ == "__main__":
    # Run tests
    test_algorithm()
    
    # Print integration examples
    print("\n" + "=" * 80)
    print("FLASK INTEGRATION EXAMPLE")
    print("=" * 80)
    print(integrate_with_flask_app())
    
    print("\n" + "=" * 80)
    print("FRONTEND INTEGRATION EXAMPLE")
    print("=" * 80)
    print(integrate_with_frontend())