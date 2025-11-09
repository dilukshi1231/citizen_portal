"""
Fix User Collection - Remove problematic index and clean data
Run: python fix_user_collection.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
users_col = db["users"]

print("=" * 70)
print("🔧 FIXING USER COLLECTION")
print("=" * 70)

# Step 1: Check existing indexes
print("\n📋 Step 1: Checking indexes...")
indexes = list(users_col.list_indexes())
print(f"   Found {len(indexes)} indexes:")
for idx in indexes:
    print(f"   - {idx['name']}: {idx.get('key', {})}")

# Step 2: Drop the problematic user_id index
print("\n📋 Step 2: Dropping user_id_1 index...")
try:
    users_col.drop_index("user_id_1")
    print("   ✅ Dropped user_id_1 index")
except Exception as e:
    print(f"   ℹ️  Index not found or already dropped: {e}")

# Step 3: Clean up users with null user_id
print("\n📋 Step 3: Cleaning up broken user records...")
result = users_col.delete_many({"user_id": None})
print(f"   ✅ Deleted {result.deleted_count} users with null user_id")

# Step 4: Ensure email index exists (for uniqueness)
print("\n📋 Step 4: Creating email index...")
try:
    users_col.create_index("email", unique=True, sparse=True)
    print("   ✅ Email index created")
except Exception as e:
    print(f"   ℹ️  Email index already exists: {e}")

# Step 5: Show current state
print("\n📋 Step 5: Current collection state...")
total_users = users_col.count_documents({})
print(f"   Total users: {total_users}")

if total_users > 0:
    print("   Sample users:")
    for user in users_col.find({}, {"email": 1, "full_name": 1, "_id": 0}).limit(3):
        print(f"      - {user.get('full_name', 'N/A')} ({user.get('email', 'N/A')})")

# Step 6: List final indexes
print("\n📋 Step 6: Final indexes:")
indexes = list(users_col.list_indexes())
for idx in indexes:
    print(f"   - {idx['name']}: {idx.get('key', {})}")

print("\n" + "=" * 70)
print("✅ USER COLLECTION FIXED!")
print("=" * 70)
print("\nNext steps:")
print("1. Run: python app.py")
print("2. Try registering at: http://localhost:5000/user/register")
print("=" * 70)