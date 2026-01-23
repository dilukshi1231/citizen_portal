"""
COMPLETE NOTIFICATION SYSTEM RESET
Clears all caches, read records, and recreates from scratch
"""

from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
notifications_col = db["notifications"]
notification_reads_col = db["notification_reads"]
users_col = db["users"]

def get_utc_now():
    return datetime.now(timezone.utc)

def extract_user_categories(user):
    """Extract categories - simplified for debugging"""
    categories = set(['citizen'])
    
    # Job/Occupation
    job = (user.get("occupation") or user.get("job") or "").lower()
    if job:
        if 'government' in job or 'officer' in job:
            categories.add("government_employee")
        if 'engineer' in job or 'developer' in job:
            categories.add("tech_professional")
        if 'business' in job or 'entrepreneur' in job:
            categories.add("business_owner")
        if 'teacher' in job:
            categories.add("educator")
        if 'doctor' in job or 'nurse' in job:
            categories.add("healthcare_worker")
    
    # Age
    age = user.get("age")
    if age:
        if age < 18:
            categories.add("student")
        elif age <= 25:
            categories.add("student")
            categories.add("young_adult")
        elif age <= 40:
            categories.add("young_professional")
        elif age > 60:
            categories.add("senior_citizen")
    
    # Family
    if user.get("children_count", 0) > 0:
        categories.add("parent")
        categories.add("parent_school_age")
    
    return list(categories)

def complete_reset():
    """Nuclear option: Delete everything and start fresh"""
    print("\n" + "="*80)
    print("🔥 COMPLETE NOTIFICATION SYSTEM RESET")
    print("="*80)
    
    # Step 1: Delete ALL notifications
    print("\n1️⃣ Deleting all existing notifications...")
    deleted_notifs = notifications_col.delete_many({})
    print(f"   ✅ Deleted {deleted_notifs.deleted_count} notifications")
    
    # Step 2: Delete ALL read records
    print("\n2️⃣ Deleting all notification read records...")
    deleted_reads = notification_reads_col.delete_many({})
    print(f"   ✅ Deleted {deleted_reads.deleted_count} read records")
    
    # Step 3: Show all users and their categories
    print("\n3️⃣ Analyzing existing users...")
    users = list(users_col.find({}, {
        "email": 1, "full_name": 1, "age": 1, 
        "occupation": 1, "job": 1, "children_count": 1
    }))
    
    print(f"\n   Found {len(users)} users:")
    user_map = {}
    
    for i, user in enumerate(users, 1):
        categories = extract_user_categories(user)
        user_map[str(user['_id'])] = {
            'email': user.get('email', 'Unknown'),
            'categories': categories
        }
        
        print(f"\n   User {i}: {user.get('email', 'Unknown')}")
        print(f"      Age: {user.get('age', 'N/A')}")
        print(f"      Job: {user.get('occupation') or user.get('job', 'N/A')}")
        print(f"      Children: {user.get('children_count', 0)}")
        print(f"      Categories: {', '.join(categories)}")
    
    return user_map

def create_ultra_specific_notifications(user_map):
    """Create notifications that are IMPOSSIBLE to overlap"""
    print("\n" + "="*80)
    print("✨ CREATING ULTRA-SPECIFIC NOTIFICATIONS")
    print("="*80)
    
    notifications = []
    
    # ONLY for government employees
    notifications.append({
        "title": {"en": "🏛️ GOVERNMENT EMPLOYEES ONLY: Salary Update", "si": "රජයේ සේවකයන්ට පමණක්: වැටුප් යාවත්කාලීනය"},
        "message": {"en": "New salary scales for public servants. Check your grade now.", "si": "රාජ්‍ය සේවකයන් සඳහා නව වැටුප් පරිමාණ. දැන් ඔබගේ ශ්‍රේණිය පරීක්ෂා කරන්න."},
        "target_categories": ["government_employee"],
        "target_roles": ["officer"],
        "type": "announcement",
        "priority": "urgent",
        "category": "employment",
        "is_active": True,
        "created_at": get_utc_now(),
        "read_count": 0,
        "metadata": {"exclusive_to": "government_employee"}
    })
    
    # ONLY for parents
    notifications.append({
        "title": {"en": "👨‍👩‍👧 PARENTS ONLY: School Registration", "si": "මව්පියන්ට පමණක්: පාසල් ලියාපදිංචිය"},
        "message": {"en": "Grade 1 admission for 2027. Register your child before Feb 15.", "si": "2027 සඳහා ශ්‍රේණි 1 ඇතුළත් කිරීම. පෙබරවාරි 15 ට පෙර ඔබේ දරුවා ලියාපදිංචි කරන්න."},
        "target_categories": ["parent", "parent_school_age"],
        "target_roles": ["citizen"],
        "type": "announcement",
        "priority": "high",
        "category": "education",
        "is_active": True,
        "created_at": get_utc_now(),
        "read_count": 0,
        "metadata": {"exclusive_to": "parent"}
    })
    
    # ONLY for tech professionals
    notifications.append({
        "title": {"en": "💻 TECH PROFESSIONALS ONLY: Hackathon", "si": "තාක්ෂණ වෘත්තිකයන්ට පමණක්: Hackathon"},
        "message": {"en": "Join Colombo AI Hackathon 2026. Win LKR 500,000! Register now.", "si": "Colombo AI Hackathon 2026 සඳහා එක්වන්න. LKR 500,000 ජයගන්න!"},
        "target_categories": ["tech_professional", "developer", "engineer"],
        "target_roles": ["citizen"],
        "type": "announcement",
        "priority": "medium",
        "category": "technology",
        "is_active": True,
        "created_at": get_utc_now(),
        "read_count": 0,
        "metadata": {"exclusive_to": "tech_professional"}
    })
    
    # ONLY for students
    notifications.append({
        "title": {"en": "📚 STUDENTS ONLY: Free A/L Classes", "si": "සිසුන්ට පමණක්: නොමිලේ උ.පෙ පන්ති"},
        "message": {"en": "Government scholarship: Free A/L tuition for 2026 students.", "si": "රජයේ ශිෂ්‍යත්වය: 2026 සිසුන් සඳහා නොමිලේ උ.පෙ ක්ෂණික පන්ති."},
        "target_categories": ["student", "young_adult"],
        "target_roles": ["student"],
        "type": "training",
        "priority": "high",
        "category": "education",
        "is_active": True,
        "created_at": get_utc_now(),
        "read_count": 0,
        "metadata": {"exclusive_to": "student"}
    })
    
    # ONLY for business owners
    notifications.append({
        "title": {"en": "💼 BUSINESS OWNERS ONLY: Tax Deadline", "si": "ව්‍යාපාර හිමියන්ට පමණක්: බදු අවසාන දිනය"},
        "message": {"en": "Q4 2025 tax filing deadline: January 31, 2026. File now to avoid penalties!", "si": "Q4 2025 බදු ගොනු කිරීමේ අවසාන දිනය: ජනවාරි 31, 2026. දඩ මග හැරීමට දැන් ගොනු කරන්න!"},
        "target_categories": ["business_owner", "entrepreneur"],
        "target_roles": ["citizen"],
        "type": "payment_reminder",
        "priority": "urgent",
        "category": "business",
        "is_active": True,
        "created_at": get_utc_now(),
        "read_count": 0,
        "metadata": {"exclusive_to": "business_owner"}
    })
    
    # ONLY for senior citizens
    notifications.append({
        "title": {"en": "👴 SENIOR CITIZENS ONLY: Pension Increase", "si": "ජ්‍යෙෂ්ඨ පුරවැසියන්ට පමණක්: විශ්‍රාම වැටුප් වැඩිකිරීම"},
        "message": {"en": "Your monthly pension increased by 20% from February 2026.", "si": "2026 පෙබරවාරි සිට ඔබගේ මාසික විශ්‍රාම වැටුප 20% කින් වැඩි විය."},
        "target_categories": ["senior_citizen", "elderly"],
        "target_roles": ["citizen"],
        "type": "announcement",
        "priority": "high",
        "category": "social_welfare",
        "is_active": True,
        "created_at": get_utc_now(),
        "read_count": 0,
        "metadata": {"exclusive_to": "senior_citizen"}
    })
    
    # ONLY for young professionals
    notifications.append({
        "title": {"en": "🌟 YOUNG PROFESSIONALS ONLY: Career Fair", "si": "තරුණ වෘත්තිකයන්ට පමණක්: වෘත්තීය ප්‍රදර්ශනය"},
        "message": {"en": "International career fair: Jobs in USA, UK, Australia. IELTS help available.", "si": "ජාත්‍යන්තර වෘත්තීය ප්‍රදර්ශනය: ඇමරිකාව, එංගලන්තය, ඕස්ට්‍රේලියාව හි රැකියා."},
        "target_categories": ["young_professional"],
        "target_roles": ["citizen"],
        "type": "announcement",
        "priority": "medium",
        "category": "career",
        "is_active": True,
        "created_at": get_utc_now(),
        "read_count": 0,
        "metadata": {"exclusive_to": "young_professional"}
    })
    
    # Insert all
    result = notifications_col.insert_many(notifications)
    print(f"\n✅ Created {len(result.inserted_ids)} ultra-specific notifications\n")
    
    # Show what was created
    for notif in notifications:
        title = notif['title']['en']
        targets = ', '.join(notif['target_categories'])
        exclusive = notif['metadata']['exclusive_to']
        print(f"   • {title}")
        print(f"     Exclusive to: {exclusive}")
        print(f"     Target categories: {targets}")
        print()

def verify_user_specific_retrieval(user_map):
    """Verify each user sees DIFFERENT notifications"""
    print("\n" + "="*80)
    print("🧪 VERIFICATION: Each User Sees Different Notifications")
    print("="*80)
    
    for user_id, user_info in user_map.items():
        categories = user_info['categories']
        email = user_info['email']
        
        # Query exactly as the API does
        matching = list(notifications_col.find({
            "is_active": True,
            "target_categories": {"$in": categories}
        }).sort("created_at", -1))
        
        print(f"\n👤 User: {email}")
        print(f"   Categories: {', '.join(categories)}")
        print(f"   📬 Should see {len(matching)} notifications:")
        
        if len(matching) == 0:
            print(f"      ⚠️ WARNING: No matching notifications!")
        else:
            for notif in matching:
                title = notif.get('title', {}).get('en', 'No title')
                exclusive = notif.get('metadata', {}).get('exclusive_to', 'unknown')
                print(f"      ✅ {title} (for {exclusive})")

def create_test_api_query():
    """Generate exact API query for testing"""
    print("\n" + "="*80)
    print("📋 TEST API QUERY")
    print("="*80)
    
    user = users_col.find_one({})
    if not user:
        print("❌ No users found")
        return
    
    categories = extract_user_categories(user)
    user_id = str(user['_id'])
    
    print(f"\nTest User: {user.get('email')}")
    print(f"User ID: {user_id}")
    print(f"Categories: {categories}")
    
    print("\n🔍 MongoDB Query:")
    query = {
        "is_active": True,
        "target_categories": {"$in": categories}
    }
    print(f"{query}")
    
    print("\n📡 API Endpoint Test:")
    print(f"GET /api/user/notifications?user_id={user_id}&lang=en")
    
    print("\n🌐 Test in Browser Console:")
    print(f"""
fetch('/api/user/notifications?lang=en&limit=50')
  .then(r => r.json())
  .then(d => console.log('Notifications:', d))
    """)

if __name__ == "__main__":
    try:
        print("\n🚨 WARNING: This will DELETE ALL notifications and read records!")
        print("Press Ctrl+C to cancel, or Enter to continue...")
        input()
        
        # Step 1: Complete reset
        user_map = complete_reset()
        
        # Step 2: Create ultra-specific notifications
        create_ultra_specific_notifications(user_map)
        
        # Step 3: Verify each user sees different notifications
        verify_user_specific_retrieval(user_map)
        
        # Step 4: Show test queries
        create_test_api_query()
        
        print("\n" + "="*80)
        print("✅ RESET COMPLETE")
        print("="*80)
        
        print("\n📝 What to do next:")
        print("1. 🔄 RESTART your Flask server (Ctrl+C then run again)")
        print("2. 🌐 Clear browser cache (Ctrl+Shift+Delete)")
        print("3. 🚪 Log out completely")
        print("4. 🔐 Log in as DIFFERENT users")
        print("5. 🔔 Check notification bell - each user sees DIFFERENT notifications")
        
        print("\n🎯 Expected Results:")
        print("   • Government employee sees: Salary Update")
        print("   • Parent sees: School Registration")
        print("   • Tech professional sees: Hackathon")
        print("   • Student sees: Free A/L Classes")
        print("   • Business owner sees: Tax Deadline")
        print("   • Each user sees ONLY notifications for THEIR category")
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()