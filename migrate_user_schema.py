"""
Update existing users with new schema fields
Run: python migrate_user_schema.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
users_col = db["users"]

print("=" * 60)
print("🔄 USER SCHEMA MIGRATION")
print("=" * 60)

# Add new fields to existing users
result = users_col.update_many(
    {},  # All users
    {
        "$set": {
            # Only set if field doesn't exist
            "gender": None,
            "marital_status": None,
            "children_count": 0,
            "children_ages": [],
            "dependents": 0,
            "years_experience": None,
            "highest_qualification": None,
            "field_of_study": None,
            "institution": None,
            "year_graduated": None,
            "skills": [],
            "career_goals": None,
            "hobbies": [],
            "learning_interests": [],
            "service_preferences": [],
            "marketing_emails": False,
            "personalized_ads": False,
            "data_analytics": True,
            "profile_completed": False,
            "updated": datetime.now()
        }
    }
)

print(f"✅ Updated {result.modified_count} users")
print("=" * 60)