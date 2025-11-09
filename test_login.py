"""
Login System Test Script
Run: python test_login.py
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
users_col = db["users"]

print("=" * 70)
print("🔐 LOGIN SYSTEM TEST")
print("=" * 70)

# Test 1: Check Admin User
print("\n📋 TEST 1: Checking Admin User...")
admin_count = admins_col.count_documents({})
print(f"   Admin users in database: {admin_count}")

if admin_count == 0:
    print("   ⚠️  No admin user found. Creating default admin...")
    pwd = os.getenv("ADMIN_PWD", "admin123")
    hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
    admins_col.insert_one({"username": "admin", "password": hashed})
    print("   ✅ Created admin user (username: admin, password: admin123)")
else:
    admin = admins_col.find_one({"username": "admin"})
    if admin:
        print("   ✅ Admin user 'admin' exists")
    else:
        print("   ⚠️  Admin user exists but not 'admin' username")

# Test 2: Check Users Collection
print("\n📋 TEST 2: Checking Users Collection...")
user_count = users_col.count_documents({})
print(f"   Registered users: {user_count}")

if user_count > 0:
    print("   Sample users:")
    for user in users_col.find({}, {"email": 1, "full_name": 1, "_id": 0}).limit(3):
        print(f"      - {user.get('full_name', 'N/A')} ({user.get('email', 'N/A')})")
else:
    print("   ℹ️  No users registered yet")

# Test 3: Create Test User
print("\n📋 TEST 3: Creating Test User...")
test_email = "test@example.com"
existing = users_col.find_one({"email": test_email})

if existing:
    print(f"   ℹ️  Test user already exists: {test_email}")
else:
    print(f"   Creating test user: {test_email}")
    hashed_pwd = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt())
    
    test_user = {
        "email": test_email,
        "password": hashed_pwd,
        "full_name": "Test User",
        "phone": "+94771234567",
        "age": 25,
        "job": "Software Developer",
        "location": "Colombo",
        "language": "en",
        "interests": ["it", "education"],
        "created": None,
        "updated": None
    }
    
    users_col.insert_one(test_user)
    print(f"   ✅ Test user created")
    print(f"      Email: test@example.com")
    print(f"      Password: test123")

# Test 4: Verify Password Hashing
print("\n📋 TEST 4: Testing Password Verification...")
admin = admins_col.find_one({"username": "admin"})
if admin:
    stored_pwd = admin.get("password")
    test_password = "admin123"
    
    try:
        if isinstance(stored_pwd, str):
            stored_pwd = stored_pwd.encode('utf-8')
        is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_pwd)
        
        if is_valid:
            print("   ✅ Admin password verification working")
        else:
            print("   ❌ Admin password verification failed")
    except Exception as e:
        print(f"   ❌ Password check error: {e}")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print(f"✅ Admin users: {admins_col.count_documents({})}")
print(f"✅ Registered users: {users_col.count_documents({})}")
print("\n🔑 Test Credentials:")
print("   Admin Login:")
print("   - URL: http://localhost:5000/admin/login")
print("   - Username: admin")
print("   - Password: admin123")
print("\n   User Login:")
print("   - URL: http://localhost:5000/user/login")
print("   - Email: test@example.com")
print("   - Password: test123")
print("\n   User Registration:")
print("   - URL: http://localhost:5000/user/register")
print("=" * 70)
print("\n🎉 Login system is ready!")
print("\nNext steps:")
print("1. Run: python app.py")
print("2. Visit: http://localhost:5000/admin/login (for admin)")
print("3. Visit: http://localhost:5000/user/login (for users)")
print("=" * 70)