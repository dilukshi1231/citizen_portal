# create_test_users.py
# Run this script to create test users with different profiles

from pymongo import MongoClient
import bcrypt
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
users_col = db["users"]

def get_utc_now():
    return datetime.now(timezone.utc)

def create_test_user(email, password, profile_data):
    """Create a test user with specific profile"""
    
    # Check if user already exists
    existing = users_col.find_one({"email": email})
    if existing:
        print(f"⚠️  User {email} already exists, skipping...")
        return None
    
    # Hash password
    hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user document
    user_doc = {
        "email": email,
        "password": hashed_pwd,
        "created": get_utc_now(),
        "updated": get_utc_now(),
        "profile_completed": True,
        **profile_data
    }
    
    result = users_col.insert_one(user_doc)
    print(f"✅ Created user: {email}")
    return str(result.inserted_id)

# ============================================
# TEST USER PROFILES
# ============================================

def create_all_test_users():
    """Create all test users"""
    
    print("=" * 70)
    print("🔐 CREATING TEST USERS FOR NOTIFICATION TESTING")
    print("=" * 70)
    
    # 1. GOVERNMENT EMPLOYEE
    print("\n1️⃣  Creating Government Employee...")
    create_test_user(
        email="gov.employee@test.com",
        password="test123",
        profile_data={
            "full_name": "Nimal Perera",
            "age": 35,
            "gender": "male",
            "occupation": "Government Officer",
            "job": "Public Service Officer",
            "district": "Colombo",
            "phone": "+94771234567",
            "marital_status": "married",
            "children_count": 0,
            "years_experience": 10,
            "highest_qualification": "Bachelor's Degree",
            "field_of_study": "Public Administration",
            "institution": "University of Colombo",
            "year_graduated": 2015,
            "learning_interests": ["business", "legal"],
            "service_preferences": ["employment", "education"],
            "extended_profile": {
                "family": {
                    "marital_status": "married",
                    "children": [],
                    "children_ages": [],
                    "dependents": 1
                },
                "education": {
                    "highest_qualification": "Bachelor's Degree",
                    "institution": "University of Colombo",
                    "year_graduated": 2015,
                    "field_of_study": "Public Administration"
                },
                "career": {
                    "current_job": "Government Officer",
                    "years_experience": 10,
                    "skills": ["administration", "management"],
                    "goals": "Career advancement in public service"
                }
            }
        }
    )
    
    # 2. PARENT WITH SCHOOL-AGE CHILDREN
    print("\n2️⃣  Creating Parent with School-Age Children...")
    create_test_user(
        email="parent@test.com",
        password="test123",
        profile_data={
            "full_name": "Kumari Silva",
            "age": 38,
            "gender": "female",
            "occupation": "Teacher",
            "job": "School Teacher",
            "district": "Gampaha",
            "phone": "+94772345678",
            "marital_status": "married",
            "children_count": 2,
            "children_ages": [7, 10],
            "years_experience": 12,
            "highest_qualification": "Bachelor's Degree",
            "field_of_study": "Education",
            "institution": "National College of Education",
            "year_graduated": 2012,
            "learning_interests": ["education"],
            "service_preferences": ["education", "healthcare"],
            "extended_profile": {
                "family": {
                    "marital_status": "married",
                    "children": [
                        {"age": 7, "education": "primary"},
                        {"age": 10, "education": "primary"}
                    ],
                    "children_ages": [7, 10],
                    "children_education": ["primary", "primary"],
                    "dependents": 2
                },
                "education": {
                    "highest_qualification": "Bachelor's Degree",
                    "institution": "National College of Education",
                    "year_graduated": 2012,
                    "field_of_study": "Education"
                },
                "career": {
                    "current_job": "Teacher",
                    "years_experience": 12,
                    "skills": ["teaching", "child development"],
                    "goals": "Provide best education for children"
                }
            }
        }
    )
    
    # 3. TECH PROFESSIONAL
    print("\n3️⃣  Creating Tech Professional...")
    create_test_user(
        email="tech.pro@test.com",
        password="test123",
        profile_data={
            "full_name": "Kamal Fernando",
            "age": 28,
            "gender": "male",
            "occupation": "Software Engineer",
            "job": "Software Developer",
            "district": "Colombo",
            "phone": "+94773456789",
            "marital_status": "single",
            "children_count": 0,
            "years_experience": 5,
            "highest_qualification": "Bachelor's Degree",
            "field_of_study": "Computer Science",
            "institution": "University of Moratuwa",
            "year_graduated": 2020,
            "skills": ["Python", "JavaScript", "React", "AI/ML"],
            "learning_interests": ["coding", "technology"],
            "service_preferences": ["technology", "business"],
            "hobbies": ["technology", "reading"],
            "extended_profile": {
                "family": {
                    "marital_status": "single",
                    "children": [],
                    "children_ages": [],
                    "dependents": 0
                },
                "education": {
                    "highest_qualification": "Bachelor's Degree",
                    "institution": "University of Moratuwa",
                    "year_graduated": 2020,
                    "field_of_study": "Computer Science"
                },
                "career": {
                    "current_job": "Software Engineer",
                    "years_experience": 5,
                    "skills": ["Python", "JavaScript", "React", "AI/ML"],
                    "goals": ["Advance in tech career", "Work overseas", "Start startup"]
                },
                "interests": {
                    "hobbies": ["technology", "reading"],
                    "learning": ["coding", "business"],
                    "services": ["technology", "business"]
                }
            }
        }
    )
    
    # 4. STUDENT
    print("\n4️⃣  Creating Student...")
    create_test_user(
        email="student@test.com",
        password="test123",
        profile_data={
            "full_name": "Sanduni Rajapaksha",
            "age": 19,
            "gender": "female",
            "occupation": "Student",
            "job": "University Student",
            "district": "Kandy",
            "phone": "+94774567890",
            "marital_status": "single",
            "children_count": 0,
            "years_experience": 0,
            "highest_qualification": "A-Level",
            "field_of_study": "Science",
            "institution": "Royal College",
            "year_graduated": 2024,
            "learning_interests": ["languages", "coding"],
            "service_preferences": ["education", "employment"],
            "hobbies": ["reading", "music"],
            "extended_profile": {
                "family": {
                    "marital_status": "single",
                    "children": [],
                    "children_ages": [],
                    "dependents": 0
                },
                "education": {
                    "highest_qualification": "A-Level",
                    "institution": "Royal College",
                    "year_graduated": 2024,
                    "field_of_study": "Physical Science"
                },
                "career": {
                    "current_job": "Student",
                    "years_experience": 0,
                    "skills": ["studying", "research"],
                    "goals": ["Complete degree", "Get scholarship", "Find good job"]
                },
                "interests": {
                    "hobbies": ["reading", "music"],
                    "learning": ["languages", "coding"],
                    "services": ["education", "employment"]
                }
            }
        }
    )
    
    # 5. SENIOR CITIZEN
    print("\n5️⃣  Creating Senior Citizen...")
    create_test_user(
        email="senior@test.com",
        password="test123",
        profile_data={
            "full_name": "W.A. Sunil",
            "age": 65,
            "gender": "male",
            "occupation": "Retired",
            "job": "Retired Government Officer",
            "district": "Galle",
            "phone": "+94775678901",
            "marital_status": "married",
            "children_count": 3,
            "children_ages": [35, 32, 28],
            "years_experience": 35,
            "highest_qualification": "Master's Degree",
            "field_of_study": "Economics",
            "institution": "University of Peradeniya",
            "year_graduated": 1985,
            "learning_interests": [],
            "service_preferences": ["healthcare", "social_welfare"],
            "hobbies": ["gardening", "reading"],
            "extended_profile": {
                "family": {
                    "marital_status": "married",
                    "children": [
                        {"age": 35},
                        {"age": 32},
                        {"age": 28}
                    ],
                    "children_ages": [35, 32, 28],
                    "dependents": 1
                },
                "education": {
                    "highest_qualification": "Master's Degree",
                    "institution": "University of Peradeniya",
                    "year_graduated": 1985,
                    "field_of_study": "Economics"
                },
                "career": {
                    "current_job": "Retired",
                    "years_experience": 35,
                    "skills": ["economics", "management"],
                    "goals": "Enjoy retirement"
                }
            }
        }
    )
    
    # 6. BUSINESS OWNER
    print("\n6️⃣  Creating Business Owner...")
    create_test_user(
        email="business@test.com",
        password="test123",
        profile_data={
            "full_name": "Ravi Wickramasinghe",
            "age": 42,
            "gender": "male",
            "occupation": "Business Owner",
            "job": "Entrepreneur",
            "district": "Colombo",
            "phone": "+94776789012",
            "marital_status": "married",
            "children_count": 2,
            "children_ages": [12, 15],
            "years_experience": 15,
            "highest_qualification": "Bachelor's Degree",
            "field_of_study": "Business Management",
            "institution": "University of Sri Jayewardenepura",
            "year_graduated": 2007,
            "learning_interests": ["business", "finance"],
            "service_preferences": ["business", "finance"],
            "hobbies": ["business", "travel"],
            "extended_profile": {
                "family": {
                    "marital_status": "married",
                    "children": [
                        {"age": 12, "education": "secondary"},
                        {"age": 15, "education": "o_level"}
                    ],
                    "children_ages": [12, 15],
                    "children_education": ["secondary", "o_level"],
                    "dependents": 3
                },
                "education": {
                    "highest_qualification": "Bachelor's Degree",
                    "institution": "University of Sri Jayewardenepura",
                    "year_graduated": 2007,
                    "field_of_study": "Business Management"
                },
                "career": {
                    "current_job": "Business Owner",
                    "years_experience": 15,
                    "skills": ["entrepreneurship", "management", "finance"],
                    "goals": ["Expand business", "Export products"]
                }
            }
        }
    )
    
    # 7. REGULAR CITIZEN (NO SPECIAL CATEGORY)
    print("\n7️⃣  Creating Regular Citizen...")
    create_test_user(
        email="citizen@test.com",
        password="test123",
        profile_data={
            "full_name": "Chaminda Jayawardena",
            "age": 45,
            "gender": "male",
            "occupation": "Driver",
            "job": "Private Driver",
            "district": "Kurunegala",
            "phone": "+94777890123",
            "marital_status": "married",
            "children_count": 1,
            "children_ages": [8],
            "years_experience": 20,
            "highest_qualification": "O-Level",
            "service_preferences": ["transport", "employment"],
            "extended_profile": {
                "family": {
                    "marital_status": "married",
                    "children": [{"age": 8, "education": "primary"}],
                    "children_ages": [8],
                    "dependents": 2
                },
                "education": {
                    "highest_qualification": "O-Level"
                },
                "career": {
                    "current_job": "Driver",
                    "years_experience": 20
                }
            }
        }
    )
    
    print("\n" + "=" * 70)
    print("✅ TEST USER CREATION COMPLETE!")
    print("=" * 70)
    print("\n📋 LOGIN CREDENTIALS:")
    print("-" * 70)
    print("1️⃣  Government Employee:")
    print("   Email: gov.employee@test.com | Password: test123")
    print("   🔔 Will see: Salary Update (URGENT)")
    print()
    print("2️⃣  Parent with School-Age Children:")
    print("   Email: parent@test.com | Password: test123")
    print("   🔔 Will see: School Registration (HIGH), System Maintenance")
    print()
    print("3️⃣  Tech Professional:")
    print("   Email: tech.pro@test.com | Password: test123")
    print("   🔔 Will see: Hackathon, System Maintenance")
    print()
    print("4️⃣  Student:")
    print("   Email: student@test.com | Password: test123")
    print("   🔔 Will see: Free A/L Classes (HIGH), Hackathon, System Maintenance")
    print()
    print("5️⃣  Senior Citizen:")
    print("   Email: senior@test.com | Password: test123")
    print("   🔔 Will see: System Maintenance (only)")
    print()
    print("6️⃣  Business Owner:")
    print("   Email: business@test.com | Password: test123")
    print("   🔔 Will see: School Registration, System Maintenance")
    print()
    print("7️⃣  Regular Citizen:")
    print("   Email: citizen@test.com | Password: test123")
    print("   🔔 Will see: School Registration, System Maintenance")
    print()
    print("=" * 70)
    print("\n💡 TIP: Login with different users to see targeted notifications!")
    print("=" * 70)

if __name__ == "__main__":
    create_all_test_users()