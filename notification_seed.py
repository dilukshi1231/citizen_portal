"""
Notification System Test & Seed Script
Run this to create test notifications for all user categories
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
notifications_col = db["notifications"]
users_col = db["users"]

def get_utc_now():
    """Get current UTC time"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)

def create_test_notifications():
    """Create diverse test notifications for different user categories"""
    
    print("\n" + "="*70)
    print("🔔 CREATING TEST NOTIFICATIONS")
    print("="*70)
    
    notifications = [
        # For all citizens
        {
            "title": {
                "en": "System Maintenance Notice",
                "si": "පද්ධති නඩත්තු දැනුම්දීම",
                "ta": "அமைப்பு பராமரிப்பு அறிவிப்பு"
            },
            "message": {
                "en": "Portal will undergo maintenance on Jan 25, 2026 from 10 PM - 2 AM",
                "si": "2026 ජනවාරි 25 දින රාත්‍රී 10 - පෙ.ව. 2 දක්වා නඩත්තු කටයුතු සඳහා ද්වාරය අක්‍රිය වේ",
                "ta": "ஜனவரி 25, 2026 இரவு 10 மணி முதல் காலை 2 மணி வரை பராமரிப்புக்காக போர்ட்டல் செயலிழக்கும்"
            },
            "target_categories": ["all"],
            "target_roles": ["all"],
            "type": "system_alert",
            "priority": "urgent",
            "category": "system",
            "is_active": True,
            "created_at": get_utc_now(),
            "read_count": 0
        },
        
        # For government employees
        {
            "title": {
                "en": "New Professional Development Course Available",
                "si": "නව වෘත්තීය සංවර්ධන පාඨමාලාව ලබා ගත හැකිය",
                "ta": "புதிய தொழில்முறை மேம்பாட்டு பாடநெறி கிடைக்கிறது"
            },
            "message": {
                "en": "Enroll in our Public Administration Excellence program. Limited seats available!",
                "si": "අපගේ රාජ්‍ය පරිපාලන විශිෂ්ටත්ව වැඩසටහනට ලියාපදිංචි වන්න. සීමිත ආසන!",
                "ta": "எங்கள் பொது நிர்வாக சிறப்பு திட்டத்தில் சேரவும். வரையறுக்கப்பட்ட இடங்கள்!"
            },
            "target_categories": ["government_employee", "officer"],
            "target_roles": ["officer", "citizen"],
            "type": "training",
            "priority": "high",
            "category": "education",
            "action_url": "/training",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=14),
            "read_count": 0
        },
        
        # For parents
        {
            "title": {
                "en": "School Registration for 2026 Now Open",
                "si": "2026 සඳහා පාසල් ලියාපදිංචිය දැන් විවෘතයි",
                "ta": "2026க்கான பள்ளி பதிவு இப்போது திறந்துள்ளது"
            },
            "message": {
                "en": "Register your child for Grade 1 admission. Deadline: February 15, 2026",
                "si": "ශ්‍රේණි 1 ඇතුළත් කිරීම සඳහා ඔබේ දරුවා ලියාපදිංචි කරන්න. අවසාන දිනය: 2026 පෙබරවාරි 15",
                "ta": "வகுப்பு 1 சேர்க்கைக்கு உங்கள் குழந்தையை பதிவு செய்யவும். கடைசி தேதி: பிப்ரவரி 15, 2026"
            },
            "target_categories": ["parent", "parent_school_age"],
            "target_roles": ["citizen"],
            "type": "announcement",
            "priority": "high",
            "category": "education",
            "action_url": "/services/education",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=23),
            "read_count": 0
        },
        
        # For students
        {
            "title": {
                "en": "Scholarship Applications Open",
                "si": "ශිෂ්‍යත්ව අයදුම්පත් විවෘතය",
                "ta": "உதவித்தொகை விண்ணப்பங்கள் திறந்துள்ளன"
            },
            "message": {
                "en": "Apply for government scholarships for higher education. Don't miss this opportunity!",
                "si": "උසස් අධ්‍යාපනය සඳහා රජයේ ශිෂ්‍යත්ව සඳහා අයදුම් කරන්න. මෙම අවස්ථාව අතපසු නොකරන්න!",
                "ta": "உயர்கல்விக்கான அரசு உதவித்தொகைகளுக்கு விண்ணப்பிக்கவும். இந்த வாய்ப்பை தவறவிடாதீர்கள்!"
            },
            "target_categories": ["student", "youth"],
            "target_roles": ["student", "citizen"],
            "type": "announcement",
            "priority": "high",
            "category": "education",
            "action_url": "/services/scholarships",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=30),
            "read_count": 0
        },
        
        # For business owners
        {
            "title": {
                "en": "New Business Tax Regulations",
                "si": "නව ව්‍යාපාර බදු රෙගුලාසි",
                "ta": "புதிய வணிக வரி விதிமுறைகள்"
            },
            "message": {
                "en": "Important changes to SME tax regulations effective February 1, 2026. Review now.",
                "si": "2026 පෙබරවාරි 1 සිට කුඩා හා මධ්‍ය ව්‍යාපාර බදු නියමවලට වැදගත් වෙනස්කම්. දැන් සමාලෝචනය කරන්න.",
                "ta": "பிப்ரவரி 1, 2026 முதல் SME வரி விதிமுறைகளில் முக்கிய மாற்றங்கள். இப்போதே மதிப்பாய்வு செய்யவும்."
            },
            "target_categories": ["business_owner", "entrepreneur"],
            "target_roles": ["citizen"],
            "type": "service_update",
            "priority": "urgent",
            "category": "business",
            "action_url": "/services/business-registration",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=10),
            "read_count": 0
        },
        
        # For healthcare workers
        {
            "title": {
                "en": "Mandatory Health Worker Training",
                "si": "අනිවාර්ය සෞඛ්‍ය සේවක පුහුණුව",
                "ta": "கட்டாய சுகாதார பணியாளர் பயிற்சி"
            },
            "message": {
                "en": "All healthcare workers must complete emergency response training by January 30, 2026",
                "si": "සියලුම සෞඛ්‍ය සේවකයින් 2026 ජනවාරි 30 වන විට හදිසි ප්‍රතිචාර පුහුණුව සම්පූර්ණ කළ යුතුය",
                "ta": "அனைத்து சுகாதார பணியாளர்களும் ஜனவரி 30, 2026க்குள் அவசர மறுமொழி பயிற்சியை முடிக்க வேண்டும்"
            },
            "target_categories": ["healthcare_worker", "doctor", "nurse"],
            "target_roles": ["officer", "citizen"],
            "type": "training",
            "priority": "urgent",
            "category": "health",
            "action_url": "/training",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=7),
            "read_count": 0
        },
        
        # For tech professionals
        {
            "title": {
                "en": "Free Digital Skills Workshop",
                "si": "නොමිලේ ඩිජිටල් කුසලතා වැඩමුළුව",
                "ta": "இலவச டிஜிட்டல் திறன் பட்டறை"
            },
            "message": {
                "en": "Join our advanced AI & Machine Learning workshop. Register before seats fill up!",
                "si": "අපගේ උසස් AI සහ යන්ත්‍ර ඉගෙනීමේ වැඩමුළුවට එක්වන්න. ආසන පිරෙන්නට පෙර ලියාපදිංචි වන්න!",
                "ta": "எங்கள் மேம்பட்ட AI & இயந்திர கற்றல் பட்டறையில் சேரவும். இடங்கள் நிரம்புவதற்கு முன் பதிவு செய்யவும்!"
            },
            "target_categories": ["tech_professional", "engineer", "developer"],
            "target_roles": ["citizen"],
            "type": "training",
            "priority": "medium",
            "category": "technology",
            "action_url": "/training",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=21),
            "read_count": 0
        },
        
        # For young professionals
        {
            "title": {
                "en": "Career Development Opportunities Abroad",
                "si": "විදේශයන්හි වෘත්තීය සංවර්ධන අවස්ථා",
                "ta": "வெளிநாடுகளில் தொழில் மேம்பாட்டு வாய்ப்புகள்"
            },
            "message": {
                "en": "Explore international job opportunities and IELTS preparation courses",
                "si": "ජාත්‍යන්තර රැකියා අවස්ථා සහ IELTS සූදානම් පාඨමාලා ගවේෂණය කරන්න",
                "ta": "சர்வதேச வேலை வாய்ப்புகள் மற்றும் IELTS தயாரிப்பு பாடநெறிகளை ஆராயுங்கள்"
            },
            "target_categories": ["young_professional", "young_adult"],
            "target_roles": ["citizen"],
            "type": "announcement",
            "priority": "medium",
            "category": "career",
            "action_url": "/store",
            "is_active": True,
            "created_at": get_utc_now(),
            "expires_at": get_utc_now() + timedelta(days=45),
            "read_count": 0
        }
    ]
    
    # Clear existing test notifications (optional)
    # notifications_col.delete_many({})
    
    # Insert notifications
    result = notifications_col.insert_many(notifications)
    
    print(f"\n✅ Created {len(result.inserted_ids)} test notifications")
    print("\nNotifications by category:")
    
    for notif in notifications:
        categories = notif.get('target_categories', [])
        priority = notif.get('priority', 'medium')
        title = notif.get('title', {}).get('en', 'No title')
        print(f"  • [{priority.upper()}] {title}")
        print(f"    Categories: {', '.join(categories)}")
    
    print("\n" + "="*70)
    
    return result.inserted_ids

def verify_user_categories():
    """Check what categories a test user has"""
    print("\n" + "="*70)
    print("👤 CHECKING USER CATEGORIES")
    print("="*70)
    
    # Get first user as example
    user = users_col.find_one({})
    
    if not user:
        print("❌ No users found in database")
        return
    
    print(f"\nUser: {user.get('email', 'Unknown')}")
    print(f"Name: {user.get('full_name', 'N/A')}")
    print(f"Age: {user.get('age', 'N/A')}")
    print(f"Job: {user.get('occupation') or user.get('job', 'N/A')}")
    
    # Extract categories (simplified version)
    categories = set(['citizen'])
    
    # From job
    job = (user.get('occupation') or user.get('job') or '').lower()
    if job:
        categories.add(job)
        if 'government' in job:
            categories.add('government_employee')
    
    # From children
    if user.get('children_count', 0) > 0:
        categories.add('parent')
    
    # From age
    age = user.get('age')
    if age:
        if age <= 25:
            categories.add('young_adult')
        elif age <= 40:
            categories.add('young_professional')
    
    # From interests
    if user.get('learning_interests'):
        categories.update(user['learning_interests'])
    
    print(f"\nExtracted categories: {list(categories)}")
    
    # Check matching notifications
    matching = notifications_col.count_documents({
        "is_active": True,
        "$or": [
            {"target_categories": {"$in": list(categories)}},
            {"target_categories": "all"}
        ]
    })
    
    print(f"\n✅ Found {matching} notifications for this user")
    
    print("="*70)

def test_notification_api():
    """Test notification retrieval"""
    print("\n" + "="*70)
    print("🧪 TESTING NOTIFICATION API")
    print("="*70)
    
    # Get a sample user
    user = users_col.find_one({})
    if not user:
        print("❌ No users found")
        return
    
    user_id = str(user['_id'])
    
    # Simulate API call
    categories = ['citizen', 'young_professional', 'tech_professional']
    
    notifications = list(notifications_col.find({
        "is_active": True,
        "$or": [
            {"target_categories": {"$in": categories}},
            {"target_categories": "all"}
        ]
    }).sort("created_at", -1))
    
    print(f"\n✅ Found {len(notifications)} notifications for categories: {categories}")
    
    for i, notif in enumerate(notifications[:5], 1):
        title = notif.get('title', {})
        if isinstance(title, dict):
            title = title.get('en', 'No title')
        print(f"\n{i}. {title}")
        print(f"   Type: {notif.get('type')}")
        print(f"   Priority: {notif.get('priority')}")
        print(f"   Categories: {notif.get('target_categories')}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        # Create test notifications
        notification_ids = create_test_notifications()
        
        # Verify user categories
        verify_user_categories()
        
        # Test API retrieval
        test_notification_api()
        
        print("\n✅ NOTIFICATION SYSTEM TEST COMPLETE")
        print("\nNext steps:")
        print("1. Refresh your dashboard at http://localhost:5000/dashboard")
        print("2. Click the 🔔 bell icon to see notifications")
        print("3. Check both 'All' and 'Unread' tabs")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()