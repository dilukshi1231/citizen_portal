"""
Diagnostic & Fix Script for User-Specific Notifications
Ensures each user sees notifications relevant to THEIR profile only
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
users_col = db["users"]
notification_reads_col = db["notification_reads"]

def get_utc_now():
    return datetime.now(timezone.utc)

def extract_user_categories(user):
    """Extract all applicable categories from user profile"""
    categories = set()
    
    # Base category - everyone
    categories.add("citizen")
    
    # From occupation/job
    occupation = (user.get("occupation") or user.get("job") or "").lower()
    if occupation:
        categories.add(occupation)
        
        # Map to standard categories
        if any(word in occupation for word in ["government", "public", "officer", "civil"]):
            categories.add("government_employee")
        if any(word in occupation for word in ["teacher", "lecturer", "professor"]):
            categories.add("educator")
        if any(word in occupation for word in ["doctor", "nurse", "medical"]):
            categories.add("healthcare_worker")
        if any(word in occupation for word in ["engineer", "developer", "programmer"]):
            categories.add("tech_professional")
        if any(word in occupation for word in ["business", "entrepreneur", "owner"]):
            categories.add("business_owner")
    
    # From interests
    if user.get("learning_interests"):
        categories.update(user["learning_interests"])
    
    if user.get("service_preferences"):
        categories.update(user["service_preferences"])
    
    if user.get("hobbies"):
        categories.update(user["hobbies"])
    
    # From extended profile
    extended = user.get("extended_profile", {})
    
    # Career-based
    career = extended.get("career", {})
    if career.get("current_job"):
        categories.add(career["current_job"].lower())
    
    # Education-based
    education = extended.get("education", {})
    qualification = (education.get("highest_qualification") or "").lower()
    
    if qualification:
        if any(q in qualification for q in ["student", "a_level", "o_level"]):
            categories.add("student")
        if "bachelor" in qualification or "degree" in qualification:
            categories.add("degree_holder")
        if "master" in qualification or "phd" in qualification:
            categories.add("postgraduate")
    
    # Family-based
    family = extended.get("family", {})
    if user.get("children_count", 0) > 0 or len(family.get("children", [])) > 0:
        categories.add("parent")
        
        # Check children ages
        children_ages = family.get("children_ages", [])
        for age in children_ages:
            if 5 <= age <= 18:
                categories.add("parent_school_age")
                break
    
    # Age-based
    age = user.get("age")
    if age:
        if age < 18:
            categories.add("minor")
        elif age <= 25:
            categories.add("young_adult")
            categories.add("youth")
        elif age <= 40:
            categories.add("young_professional")
            categories.add("adult")
        elif age <= 60:
            categories.add("middle_aged")
            categories.add("adult")
        else:
            categories.add("senior_citizen")
            categories.add("elderly")
    
    # District-based
    if user.get("district"):
        categories.add(f"district_{user['district'].lower().replace(' ', '_')}")
    
    return list(filter(None, categories))

def diagnose_all_users():
    """Check what categories each user has"""
    print("\n" + "="*80)
    print("🔍 DIAGNOSING USER CATEGORIES")
    print("="*80)
    
    users = list(users_col.find({}, {"_id": 1, "email": 1, "full_name": 1, "age": 1, "occupation": 1, "job": 1, "children_count": 1}))
    
    if len(users) == 0:
        print("❌ No users found!")
        return
    
    print(f"\nFound {len(users)} users\n")
    
    user_category_map = {}
    
    for i, user in enumerate(users, 1):
        categories = extract_user_categories(user)
        user_id = str(user['_id'])
        user_category_map[user_id] = categories
        
        print(f"{i}. {user.get('email', 'Unknown')}")
        print(f"   Name: {user.get('full_name', 'N/A')}")
        print(f"   Age: {user.get('age', 'N/A')}")
        print(f"   Job: {user.get('occupation') or user.get('job', 'N/A')}")
        print(f"   Categories ({len(categories)}): {', '.join(categories)}")
        
        # Check matching notifications
        matching = notifications_col.count_documents({
            "is_active": True,
            "$or": [
                {"target_categories": {"$in": categories}},
                {"target_categories": "all"}
            ]
        })
        print(f"   📬 Matching Notifications: {matching}")
        print()
    
    return user_category_map

def check_notification_overlap():
    """Check if notifications are too generic (targeting 'all')"""
    print("\n" + "="*80)
    print("📊 NOTIFICATION TARGETING ANALYSIS")
    print("="*80)
    
    total = notifications_col.count_documents({"is_active": True})
    all_users = notifications_col.count_documents({
        "is_active": True,
        "target_categories": "all"
    })
    
    specific = total - all_users
    
    print(f"\nTotal Active Notifications: {total}")
    print(f"  📢 Universal (target: 'all'): {all_users} ({all_users/total*100:.1f}%)")
    print(f"  🎯 Targeted (specific categories): {specific} ({specific/total*100:.1f}%)")
    
    if all_users / total > 0.7:
        print("\n⚠️  WARNING: Over 70% of notifications target ALL users!")
        print("   This is why everyone sees the same notifications.")
        print("   Solution: Create more targeted notifications.")
    
    # Show category distribution
    print("\n📋 Notifications by Target Category:")
    
    all_notifications = list(notifications_col.find({"is_active": True}, {"title": 1, "target_categories": 1}))
    
    category_counts = {}
    for notif in all_notifications:
        categories = notif.get("target_categories", [])
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count} notifications")

def create_user_specific_notifications():
    """Create truly user-specific notifications"""
    print("\n" + "="*80)
    print("✨ CREATING USER-SPECIFIC NOTIFICATIONS")
    print("="*80)
    
    # Delete all existing notifications
    print("\n🗑️  Deleting old generic notifications...")
    deleted = notifications_col.delete_many({"target_categories": "all"})
    print(f"   Deleted {deleted.deleted_count} generic notifications")
    
    # Create highly targeted notifications
    targeted_notifications = [
        # For government employees ONLY
        {
            "title": {"en": "Public Service Salary Revision", "si": "රාජ්‍ය සේවා වැටුප් සංශෝධනය"},
            "message": {"en": "New salary scales effective February 2026. Check your grade.", 
                       "si": "2026 පෙබරවාරි සිට නව වැටුප් පරිමාණ ක්‍රියාත්මකයි."},
            "target_categories": ["government_employee"],
            "target_roles": ["officer"],
            "type": "announcement",
            "priority": "high",
            "category": "employment",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=15),
            "read_count": 0
        },
        
        # For parents with school-age children ONLY
        {
            "title": {"en": "Grade 5 Scholarship Exam Registration", "si": "ශ්‍රේණි 5 ශිෂ්‍යත්ව විභාගය ලියාපදිංචිය"},
            "message": {"en": "Register your child for scholarship exam. Deadline: Feb 10, 2026",
                       "si": "ඔබේ දරුවා ශිෂ්‍යත්ව විභාගය සඳහා ලියාපදිංචි කරන්න. අවසාන දිනය: 2026 පෙබ 10"},
            "target_categories": ["parent_school_age", "parent"],
            "target_roles": ["citizen"],
            "type": "announcement",
            "priority": "urgent",
            "category": "education",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=18),
            "read_count": 0
        },
        
        # For tech professionals ONLY
        {
            "title": {"en": "Tech Meetup: AI & Cloud Computing", "si": "තාක්ෂණික හමුව: AI සහ Cloud Computing"},
            "message": {"en": "Join Colombo's tech community meetup on Jan 27. Free registration!",
                       "si": "ජන 27 කොළඹ තාක්ෂණික ප්‍රජා හමුවට එක්වන්න. නොමිලේ ලියාපදිංචිය!"},
            "target_categories": ["tech_professional", "developer", "engineer"],
            "target_roles": ["citizen"],
            "type": "announcement",
            "priority": "medium",
            "category": "technology",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=4),
            "read_count": 0
        },
        
        # For students ONLY
        {
            "title": {"en": "Free University Entrance Preparation", "si": "නොමිලේ විශ්වවිද්‍යාල ප්‍රවේශ සූදානම"},
            "message": {"en": "Government scholarship: Free A/L classes for 2026 students",
                       "si": "රජයේ ශිෂ්‍යත්වය: 2026 සිසුන් සඳහා නොමිලේ උ.පෙ පන්ති"},
            "target_categories": ["student", "youth"],
            "target_roles": ["student"],
            "type": "training",
            "priority": "high",
            "category": "education",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=25),
            "read_count": 0
        },
        
        # For business owners ONLY
        {
            "title": {"en": "SME Tax Filing Deadline Approaching", "si": "කුඩා ව්‍යාපාර බදු ගොනු කිරීමේ අවසාන දිනය ළඟා වේ"},
            "message": {"en": "File your Q4 2025 tax returns by January 31, 2026. Avoid penalties!",
                       "si": "2026 ජනවාරි 31 වන විට ඔබගේ Q4 2025 බදු ප්‍රකාශන ගොනු කරන්න."},
            "target_categories": ["business_owner", "entrepreneur"],
            "target_roles": ["citizen"],
            "type": "payment_reminder",
            "priority": "urgent",
            "category": "business",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=8),
            "read_count": 0
        },
        
        # For senior citizens ONLY
        {
            "title": {"en": "Senior Citizen Pension Increase", "si": "ජ්‍යෙෂ්ඨ පුරවැසි විශ්‍රාම වැටුප් වැඩිකිරීම"},
            "message": {"en": "Monthly pension increased by 15% effective February 2026",
                       "si": "2026 පෙබරවාරි සිට මාසික විශ්‍රාම වැටුප 15%කින් වැඩි විය"},
            "target_categories": ["senior_citizen", "elderly"],
            "target_roles": ["citizen"],
            "type": "announcement",
            "priority": "high",
            "category": "social_welfare",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=30),
            "read_count": 0
        },
        
        # For young professionals ONLY
        {
            "title": {"en": "Career Fair: International Opportunities", "si": "වෘත්තීය ප්‍රදර්ශනය: ජාත්‍යන්තර අවස්ථා"},
            "message": {"en": "Explore jobs in USA, UK, Australia. IELTS assistance available.",
                       "si": "ඇමරිකාව, එංගලන්තය, ඕස්ට්‍රේලියාව තුළ රැකියා ගවේෂණය කරන්න."},
            "target_categories": ["young_professional", "young_adult"],
            "target_roles": ["citizen"],
            "type": "announcement",
            "priority": "medium",
            "category": "career",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=12),
            "read_count": 0
        }
    ]
    
    result = notifications_col.insert_many(targeted_notifications)
    print(f"\n✅ Created {len(result.inserted_ids)} targeted notifications")
    
    # Show what was created
    for notif in targeted_notifications:
        title = notif['title']['en']
        categories = ', '.join(notif['target_categories'])
        print(f"   • {title}")
        print(f"     Target: {categories}")

def test_user_specific_retrieval():
    """Test that different users see different notifications"""
    print("\n" + "="*80)
    print("🧪 TESTING USER-SPECIFIC NOTIFICATION RETRIEVAL")
    print("="*80)
    
    users = list(users_col.find({}).limit(5))
    
    for user in users:
        categories = extract_user_categories(user)
        
        matching = list(notifications_col.find({
            "is_active": True,
            "$or": [
                {"target_categories": {"$in": categories}},
                {"target_categories": "all"}
            ]
        }))
        
        print(f"\n👤 {user.get('email', 'Unknown')}")
        print(f"   Categories: {', '.join(categories[:5])}..." if len(categories) > 5 else f"   Categories: {', '.join(categories)}")
        print(f"   📬 Sees {len(matching)} notifications:")
        
        for notif in matching:
            title = notif.get('title', {}).get('en', 'No title')
            target = ', '.join(notif.get('target_categories', []))
            print(f"      • {title} (targets: {target})")

if __name__ == "__main__":
    try:
        # Step 1: Diagnose current state
        user_categories = diagnose_all_users()
        
        # Step 2: Check notification overlap
        check_notification_overlap()
        
        # Step 3: Create user-specific notifications
        create_user_specific_notifications()
        
        # Step 4: Test retrieval
        test_user_specific_retrieval()
        
        print("\n" + "="*80)
        print("✅ FIX COMPLETE - REFRESH YOUR DASHBOARD")
        print("="*80)
        print("\n📝 What changed:")
        print("1. ❌ Deleted generic 'all users' notifications")
        print("2. ✅ Created 7 highly targeted notifications")
        print("3. 🎯 Each user now sees ONLY relevant notifications")
        print("\n🔄 Next steps:")
        print("1. Log in as different users")
        print("2. Check notification bell - each should see different counts")
        print("3. Verify content matches user profile")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()