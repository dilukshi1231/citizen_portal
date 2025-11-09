"""
Fix Admin Password - Recreate with proper bcrypt hash
Run: python fix_admin_password.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
admins_col = db["admins"]

print("=" * 70)
print("🔧 FIX ADMIN PASSWORD")
print("=" * 70)

# Delete existing admin user
print("\n📋 Step 1: Removing old admin user...")
result = admins_col.delete_many({"username": "admin"})
print(f"   Deleted {result.deleted_count} admin user(s)")

# Create new admin with proper bcrypt hash
print("\n📋 Step 2: Creating new admin with bcrypt hash...")
password = os.getenv("ADMIN_PWD", "admin123")
print(f"   Password to hash: {password}")

# Generate proper bcrypt hash
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(f"   Generated hash: {hashed[:30]}... (truncated)")

# Insert new admin
admin_doc = {
    "username": "admin",
    "password": hashed,
    "role": "admin",
    "created": None
}

result = admins_col.insert_one(admin_doc)
print(f"   ✅ Created new admin user with ID: {result.inserted_id}")

# Verify the password works
print("\n📋 Step 3: Verifying password...")
admin = admins_col.find_one({"username": "admin"})
stored_pwd = admin.get("password")

try:
    # Test password verification
    is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_pwd)
    
    if is_valid:
        print("   ✅ Password verification SUCCESSFUL!")
        print(f"   Admin can login with: admin / {password}")
    else:
        print("   ❌ Password verification FAILED!")
except Exception as e:
    print(f"   ❌ Verification error: {e}")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print(f"✅ Admin username: admin")
print(f"✅ Admin password: {password}")
print(f"✅ Password hash stored: {len(stored_pwd)} bytes")
print(f"✅ Hash type: {type(stored_pwd)}")
print("\n🎉 Admin password fixed!")
print("\nYou can now:")
print("1. Run: python app.py")
print("2. Visit: http://localhost:5000/admin/login")
print("3. Login with: admin / admin123")
print("=" * 70)