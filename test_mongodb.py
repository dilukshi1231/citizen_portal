"""
MongoDB Connection Test Script
Run: python test_mongodb.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

print("=" * 60)
print("MongoDB Connection Test")
print("=" * 60)

# Hide password in output
display_uri = MONGO_URI[:30] + "..." if len(MONGO_URI) > 30 else MONGO_URI
print(f"\n📍 Connecting to: {display_uri}")

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Test connection with ping
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    
    # Access the database
    db = client["citizen_portal"]
    
    # List all databases
    print("\n📚 Available Databases:")
    for db_name in client.list_database_names():
        print(f"   - {db_name}")
    
    # Check if citizen_portal exists
    if "citizen_portal" in client.list_database_names():
        print("\n✅ citizen_portal database exists!")
    else:
        print("\n⚠️  citizen_portal database not found (will be created on first insert)")
    
    # List collections in citizen_portal
    print("\n📦 Collections in 'citizen_portal':")
    collections = db.list_collection_names()
    if collections:
        for col in collections:
            count = db[col].count_documents({})
            print(f"   - {col}: {count} documents")
    else:
        print("   (No collections yet - run seed_data.py)")
    
    # Check services collection
    print("\n🔍 Checking 'services' collection:")
    services_col = db["services"]
    service_count = services_col.count_documents({})
    
    if service_count > 0:
        print(f"✅ Found {service_count} services")
        
        # Show first 3 services
        print("\n📋 Sample services:")
        for service in services_col.find().limit(3):
            print(f"   - {service.get('name', {}).get('en', 'Unknown')}")
    else:
        print("⚠️  No services found - run seed_data.py to populate database")
    
    # Check engagements collection
    print("\n🔍 Checking 'engagements' collection:")
    eng_col = db["engagements"]
    eng_count = eng_col.count_documents({})
    print(f"   Found {eng_count} engagement records")
    
    if eng_count > 0:
        print("\n📊 Latest engagement:")
        latest = eng_col.find_one(sort=[("timestamp", -1)])
        if latest:
            print(f"   - User: {latest.get('user_id', 'Anonymous')}")
            print(f"   - Age: {latest.get('age', 'N/A')}")
            print(f"   - Job: {latest.get('job', 'N/A')}")
            print(f"   - Service: {latest.get('service', 'N/A')}")
            print(f"   - Time: {latest.get('timestamp', 'N/A')}")
    
    # Check admins collection
    print("\n🔍 Checking 'admins' collection:")
    admins_col = db["admins"]
    admin_count = admins_col.count_documents({})
    
    if admin_count > 0:
        print(f"✅ Found {admin_count} admin user(s)")
        for admin in admins_col.find({}, {"username": 1, "_id": 0}):
            print(f"   - Username: {admin.get('username')}")
    else:
        print("⚠️  No admin users found - will be created when app runs")
    
    # Test write operation
    print("\n🧪 Testing write operation:")
    test_col = db["test_connection"]
    result = test_col.insert_one({
        "test": True,
        "timestamp": datetime.utcnow(),
        "message": "Connection test successful"
    })
    print(f"✅ Write test successful! Inserted ID: {result.inserted_id}")
    
    # Clean up test
    test_col.delete_one({"_id": result.inserted_id})
    print("✅ Test document cleaned up")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Connection: OK")
    print(f"✅ Database: citizen_portal")
    print(f"✅ Services: {service_count} documents")
    print(f"✅ Engagements: {eng_count} documents")
    print(f"✅ Admins: {admin_count} users")
    print(f"✅ Read/Write: OK")
    
    if service_count == 0:
        print("\n⚠️  ACTION REQUIRED: Run 'python seed_data.py' to populate services")
    else:
        print("\n🎉 Database is ready! You can run 'python app.py' now")
    
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Connection failed!")
    print(f"Error: {str(e)}")
    print("\n🔧 Troubleshooting:")
    print("1. Check your MONGO_URI in .env file")
    print("2. Verify MongoDB Atlas IP whitelist (Network Access)")
    print("3. Check database user credentials")
    print("4. Ensure cluster is not paused")
    print("5. Check internet connection")
    
finally:
    try:
        client.close()
        print("\n🔌 Connection closed")
    except:
        pass
