"""
Fix Existing Engagement Data
This script updates existing engagement records with user profile data
Run: python fix_existing_engagement_data.py
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
eng_col = db["engagements"]

print("=" * 70)
print("🔧 FIXING EXISTING ENGAGEMENT DATA")
print("=" * 70)

# Step 1: Count records needing fix
print("\n📋 Step 1: Analyzing data...")
total_engagements = eng_col.count_documents({})
missing_age = eng_col.count_documents({"age": None})
missing_job = eng_col.count_documents({"job": None})
missing_age_or_job = eng_col.count_documents({"$or": [{"age": None}, {"job": None}]})

print(f"   Total engagements: {total_engagements}")
print(f"   Missing age: {missing_age}")
print(f"   Missing job: {missing_job}")
print(f"   Missing age OR job: {missing_age_or_job}")

# Step 2: Create a user lookup dictionary
print("\n📋 Step 2: Building user profile lookup...")
user_profiles = {}
for user in users_col.find({}, {"_id": 1, "age": 1, "job": 1}):
    user_id = str(user["_id"])
    user_profiles[user_id] = {
        "age": user.get("age"),
        "job": user.get("job")
    }

print(f"   Found {len(user_profiles)} user profiles")

# Step 3: Update engagements
print("\n📋 Step 3: Updating engagement records...")
updated_count = 0
skipped_count = 0

for engagement in eng_col.find({"$or": [{"age": None}, {"job": None}]}):
    user_id = engagement.get("user_id")
    
    if not user_id or user_id not in user_profiles:
        skipped_count += 1
        continue
    
    profile = user_profiles[user_id]
    update_fields = {}
    
    # Only update if age is missing and profile has age
    if engagement.get("age") is None and profile.get("age") is not None:
        update_fields["age"] = profile["age"]
    
    # Only update if job is missing and profile has job
    if not engagement.get("job") and profile.get("job"):
        update_fields["job"] = profile["job"]
    
    if update_fields:
        eng_col.update_one(
            {"_id": engagement["_id"]},
            {"$set": update_fields}
        )
        updated_count += 1

print(f"   ✅ Updated {updated_count} engagement records")
print(f"   ⚠️  Skipped {skipped_count} records (no matching user profile)")

# Step 4: Verify results
print("\n📋 Step 4: Verifying results...")
after_missing_age = eng_col.count_documents({"age": None})
after_missing_job = eng_col.count_documents({"job": None})

print(f"   Missing age after fix: {after_missing_age} (was {missing_age})")
print(f"   Missing job after fix: {after_missing_job} (was {missing_job})")

# Step 5: Add language field to old engagements without it
print("\n📋 Step 5: Adding language field to old records...")
result = eng_col.update_many(
    {"language": {"$exists": False}},
    {"$set": {"language": "en"}}
)
print(f"   ✅ Updated {result.modified_count} records with default language")

# Step 6: Add chat_type to records without it
print("\n📋 Step 6: Adding chat_type field...")
result = eng_col.update_many(
    {"chat_type": {"$exists": False}},
    {"$set": {"chat_type": "standard"}}
)
print(f"   ✅ Updated {result.modified_count} records with chat_type")

# Step 7: Show sample data
print("\n📋 Step 7: Sample engagement records:")
for eng in eng_col.find().limit(5):
    print(f"\n   User: {eng.get('user_id', 'N/A')}")
    print(f"   Age: {eng.get('age', 'N/A')}")
    print(f"   Job: {eng.get('job', 'N/A')}")
    print(f"   Question: {eng.get('question_clicked', 'N/A')[:50]}...")
    print(f"   Language: {eng.get('language', 'N/A')}")
    print(f"   Chat Type: {eng.get('chat_type', 'N/A')}")

print("\n" + "=" * 70)
print("✅ ENGAGEMENT DATA FIXED!")
print("=" * 70)
print("\nNext steps:")
print("1. Restart your Flask app: python app.py")
print("2. Login to admin panel: http://localhost:5000/admin")
print("3. Check 'User Analytics' section")
print("4. Check 'Questions by Age Group & Language'")
print("=" * 70)