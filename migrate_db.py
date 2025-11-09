"""
Database Migration Script - Add new collections for Task 07
Run: python migrate_db.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
training_programs_col = db["training_programs"]
enrollments_col = db["enrollments"]

print("=" * 60)
print("🎓 TRAINING PROGRAMS - DATABASE SETUP")
print("=" * 60)

# Clear existing data
training_programs_col.delete_many({})
enrollments_col.delete_many({})

# Sample training programs
training_programs = [
    {
        "id": "train_digital_basics_01",
        "title": {
            "en": "Digital Skills for Everyone",
            "si": "සියලු දෙනා සඳහා ඩිජිටල් කුසලතා",
            "ta": "அனைவருக்கும் டிஜிட்டல் திறன்கள்"
        },
        "description": {
            "en": "Learn essential digital skills to access government services online. Perfect for beginners!",
            "si": "රජයේ සේවා ඔන්ලයින් ලබා ගැනීමට අත්‍යවශ්‍ය ඩිජිටල් කුසලතා ඉගෙන ගන්න. ආරම්භකයින් සඳහා සුදුසුයි!",
            "ta": "அரசாங்க சேவைகளை ஆன்லைனில் அணுக அத்தியாவசிய டிஜிட்டல் திறன்களை கற்றுக்கொள்ளுங்கள். ஆரம்பநிலைக்கு ஏற்றது!"
        },
        "category": "digital_literacy",
        "level": "Beginner",
        "duration": "4 weeks",
        "hours_per_week": 3,
        "language": ["en", "si", "ta"],
        "mode": "online",
        "free": True,
        "instructor": "Ministry of IT & Digital Affairs",
        "topics": [
            "Basic computer skills",
            "Internet navigation",
            "Email usage",
            "Government portal access",
            "Digital payments",
            "Online form filling"
        ],
        "prerequisites": "None - Open to all citizens",
        "certificate": True,
        "enrollment_link": "https://digital.gov.lk/enroll/basics",
        "video_intro": "https://youtube.com/watch?v=sample1",
        "brochure": "/static/docs/digital_basics_brochure.pdf",
        "start_date": datetime(2025, 2, 1),
        "end_date": datetime(2025, 2, 28),
        "max_participants": 500,
        "current_enrollments": 0,
        "active": True,
        "featured": True,
        "tags": ["beginner", "essential", "government services"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_cyber_security_01",
        "title": {
            "en": "Cybersecurity Awareness",
            "si": "සයිබර් ආරක්ෂාව පිළිබඳ දැනුවත්භාවය",
            "ta": "இணைய பாதுகாப்பு விழிப்புணர்வு"
        },
        "description": {
            "en": "Stay safe online! Learn how to protect yourself from cyber threats, scams, and identity theft.",
            "si": "ඔන්ලයින් ආරක්ෂිතව සිටින්න! සයිබර් තර්ජන, වංචා සහ අනන්‍යතා සොරකමෙන් ඔබව ආරක්ෂා කර ගන්නා ආකාරය ඉගෙන ගන්න.",
            "ta": "ஆன்லைனில் பாதுகாப்பாக இருங்கள்! இணைய அச்சுறுத்தல்கள், மோசடிகள் மற்றும் அடையாள திருட்டுகளிலிருந்து உங்களை எவ்வாறு பாதுகாத்துக் கொள்வது என்பதை அறியுங்கள்."
        },
        "category": "cybersecurity",
        "level": "Intermediate",
        "duration": "2 weeks",
        "hours_per_week": 2,
        "language": ["en", "si", "ta"],
        "mode": "online",
        "free": True,
        "instructor": "Ministry of Defence - Cyber Division",
        "topics": [
            "Password security",
            "Phishing awareness",
            "Safe browsing habits",
            "Two-factor authentication",
            "Mobile security",
            "Social media privacy"
        ],
        "prerequisites": "Basic internet knowledge",
        "certificate": True,
        "enrollment_link": "https://digital.gov.lk/enroll/cyber",
        "video_intro": "https://youtube.com/watch?v=sample2",
        "brochure": "/static/docs/cyber_security_brochure.pdf",
        "start_date": datetime(2025, 3, 1),
        "end_date": datetime(2025, 3, 14),
        "max_participants": 300,
        "current_enrollments": 0,
        "active": True,
        "featured": True,
        "tags": ["security", "safety", "privacy"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_ecommerce_01",
        "title": {
            "en": "Starting Your Online Business",
            "si": "ඔබේ ඔන්ලයින් ව්‍යාපාරය ආරම්භ කිරීම",
            "ta": "உங்கள் ஆன்லைன் வணிகத்தைத் தொடங்குதல்"
        },
        "description": {
            "en": "Learn how to start and manage an online business. Covers registration, digital marketing, and e-commerce platforms.",
            "si": "ඔන්ලයින් ව්‍යාපාරයක් ආරම්භ කර කළමනාකරණය කරන්නේ කෙසේදැයි ඉගෙන ගන්න. ලියාපදිංචිය, ඩිජිටල් අලෙවිකරණය සහ ඊ-වාණිජ වේදිකා ආවරණය කරයි.",
            "ta": "ஆன்லைன் வணிகத்தை எவ்வாறு தொடங்குவது மற்றும் நிர்வகிப்பது என்பதை அறியுங்கள். பதிவு, டிஜிட்டல் சந்தைப்படுத்தல் மற்றும் மின்-வர்த்தக தளங்களை உள்ளடக்கியது."
        },
        "category": "entrepreneurship",
        "level": "Intermediate",
        "duration": "6 weeks",
        "hours_per_week": 4,
        "language": ["en", "si", "ta"],
        "mode": "hybrid",
        "free": False,
        "fee": "Rs. 5,000",
        "instructor": "Ministry of Industry & Trade",
        "topics": [
            "Business registration",
            "E-commerce platforms",
            "Digital marketing",
            "Payment gateways",
            "Tax compliance",
            "Customer service"
        ],
        "prerequisites": "Basic computer skills",
        "certificate": True,
        "enrollment_link": "https://trade.gov.lk/enroll/ecommerce",
        "video_intro": "https://youtube.com/watch?v=sample3",
        "brochure": "/static/docs/ecommerce_brochure.pdf",
        "start_date": datetime(2025, 2, 15),
        "end_date": datetime(2025, 3, 30),
        "max_participants": 100,
        "current_enrollments": 0,
        "active": True,
        "featured": False,
        "tags": ["business", "entrepreneurship", "e-commerce"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_govt_services_01",
        "title": {
            "en": "Mastering Government Online Services",
            "si": "රජයේ ඔන්ලයින් සේවා ප්‍රගුණ කිරීම",
            "ta": "அரசாங்க ஆன்லைன் சேவைகளை தேர்ச்சி பெறுதல்"
        },
        "description": {
            "en": "Complete guide to accessing all government services online - from applications to certificate downloads.",
            "si": "සියලුම රජයේ සේවා ඔන්ලයින් ලබා ගැනීම සඳහා සම්පූර්ණ මාර්ගෝපදේශය - අයදුම්පත් සිට සහතික බාගත කිරීම දක්වා.",
            "ta": "அனைத்து அரசாங்க சேவைகளையும் ஆன்லைனில் அணுகுவதற்கான முழுமையான வழிகாட்டி - விண்ணப்பங்கள் முதல் சான்றிதழ் பதிவிறக்கங்கள் வரை."
        },
        "category": "government_services",
        "level": "Beginner",
        "duration": "3 weeks",
        "hours_per_week": 2,
        "language": ["en", "si", "ta"],
        "mode": "online",
        "free": True,
        "instructor": "Ministry of Public Administration",
        "topics": [
            "Citizen portal navigation",
            "Document verification",
            "Online applications",
            "Status tracking",
            "Certificate downloads",
            "Payment methods"
        ],
        "prerequisites": "None",
        "certificate": True,
        "enrollment_link": "https://public.gov.lk/enroll/services",
        "video_intro": "https://youtube.com/watch?v=sample4",
        "brochure": "/static/docs/govt_services_brochure.pdf",
        "start_date": datetime(2025, 2, 10),
        "end_date": datetime(2025, 3, 2),
        "max_participants": 1000,
        "current_enrollments": 0,
        "active": True,
        "featured": True,
        "tags": ["government", "services", "essential"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_youth_employment_01",
        "title": {
            "en": "Youth Employment Skills",
            "si": "තරුණ රැකියා කුසලතා",
            "ta": "இளைஞர் வேலைவாய்ப்பு திறன்கள்"
        },
        "description": {
            "en": "Job search skills, resume writing, interview preparation, and professional networking for young job seekers.",
            "si": "තරුණ රැකියා සොයන්නන් සඳහා රැකියා සෙවීමේ කුසලතා, ජීව දත්ත ලිවීම, සම්මුඛ පරීක්ෂණ සූදානම සහ වෘත්තීය ජාලකරණය.",
            "ta": "இளம் வேலை தேடுபவர்களுக்கான வேலை தேடல் திறன்கள், சுயவிவர எழுதுதல், நேர்காணல் தயாரிப்பு மற்றும் தொழில்முறை நெட்வொர்க்கிங்."
        },
        "category": "employment",
        "level": "Beginner",
        "duration": "4 weeks",
        "hours_per_week": 3,
        "language": ["en", "si", "ta"],
        "mode": "hybrid",
        "free": True,
        "instructor": "Ministry of Youth Affairs",
        "topics": [
            "Job search strategies",
            "Resume/CV writing",
            "Interview techniques",
            "LinkedIn profile",
            "Professional communication",
            "Career planning"
        ],
        "prerequisites": "Age 18-35",
        "certificate": True,
        "enrollment_link": "https://youth.gov.lk/enroll/employment",
        "video_intro": "https://youtube.com/watch?v=sample5",
        "brochure": "/static/docs/youth_employment_brochure.pdf",
        "start_date": datetime(2025, 2, 20),
        "end_date": datetime(2025, 3, 19),
        "max_participants": 500,
        "current_enrollments": 0,
        "active": True,
        "featured": False,
        "tags": ["youth", "employment", "career"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    }
]

# Insert programs
result = training_programs_col.insert_many(training_programs)
print(f"✅ Created {len(training_programs)} training programs")

# Create indexes
training_programs_col.create_index("id", unique=True)
training_programs_col.create_index("category")
training_programs_col.create_index("active")
training_programs_col.create_index("featured")
training_programs_col.create_index("start_date")
enrollments_col.create_index([("user_id", 1), ("program_id", 1)], unique=True)
enrollments_col.create_index("program_id")
enrollments_col.create_index("status")

print("✅ Created database indexes")

print("\n" + "=" * 60)
print("📊 TRAINING PROGRAMS SUMMARY")
print("=" * 60)
print(f"Total Programs: {len(training_programs)}")
print(f"Free Programs: {sum(1 for p in training_programs if p['free'])}")
print(f"Paid Programs: {sum(1 for p in training_programs if not p['free'])}")
print(f"Featured Programs: {sum(1 for p in training_programs if p['featured'])}")
print("=" * 60)
print("\n🎉 Training programs database setup complete!")
print("\nNext steps:")
print("1. Add API endpoints to app.py")
print("2. Create training.html template")
print("3. Update navigation menu")
print("=" * 60)
# New collections
categories_col = db["categories"]
officers_col = db["officers"]
ads_col = db["ads"]
users_col = db["users"]

print("=" * 60)
print("🔄 DATABASE MIGRATION - Task 07")
print("=" * 60)

# 1. Create Categories
print("\n📁 Creating categories...")
categories = [
    {
        "id": "cat_it",
        "name": {
            "en": "IT & Digital Services",
            "si": "තොරතුරු තාක්ෂණ සේවා",
            "ta": "தகவல் தொழில்நுட்ப சேவைகள்"
        },
        "ministry_ids": ["ministry_it"],
        "icon": "💻",
        "order": 1
    },
    {
        "id": "cat_education",
        "name": {
            "en": "Education & Exams",
            "si": "අධ්‍යාපන හා විභාග",
            "ta": "கல்வி மற்றும் தேர்வுகள்"
        },
        "ministry_ids": ["ministry_education"],
        "icon": "📚",
        "order": 2
    },
    {
        "id": "cat_health",
        "name": {
            "en": "Health Services",
            "si": "සෞඛ්‍ය සේවා",
            "ta": "சுகாதார சேவைகள்"
        },
        "ministry_ids": ["ministry_health"],
        "icon": "🏥",
        "order": 3
    },
    {
        "id": "cat_transport",
        "name": {
            "en": "Transport & Vehicles",
            "si": "ප්‍රවාහන සේවා",
            "ta": "போக்குவரத்து சேவைகள்"
        },
        "ministry_ids": ["ministry_transport"],
        "icon": "🚗",
        "order": 4
    },
    {
        "id": "cat_immigration",
        "name": {
            "en": "Immigration & Passports",
            "si": "ආගමන හා විගමන",
            "ta": "குடிவரவு சேவைகள்"
        },
        "ministry_ids": ["ministry_imm"],
        "icon": "🛂",
        "order": 5
    },
    {
        "id": "cat_public",
        "name": {
            "en": "Public Administration",
            "si": "රාජ්‍ය පරිපාලන",
            "ta": "பொது நிர்வாகம்"
        },
        "ministry_ids": ["ministry_public"],
        "icon": "🏛️",
        "order": 6
    }
]

categories_col.delete_many({})
categories_col.insert_many(categories)
print(f"✅ Created {len(categories)} categories")

# 2. Create Sample Officers
print("\n👤 Creating sample officers...")
officers = [
    {
        "id": "off_it_01",
        "name": "Ms. Nayana Perera",
        "role": "Director - Digital Services",
        "ministry_id": "ministry_it",
        "contact": {
            "email": "nayana@it.gov.lk",
            "phone": "071-2345678"
        },
        "photo": "/static/img/officer1.jpg",
        "bio": "Leading digital transformation initiatives"
    },
    {
        "id": "off_edu_01",
        "name": "Mr. Ruwan Silva",
        "role": "Assistant Secretary - Education",
        "ministry_id": "ministry_education",
        "contact": {
            "email": "ruwan@edu.gov.lk",
            "phone": "071-3456789"
        },
        "photo": "/static/img/officer2.jpg",
        "bio": "Managing education services and exams"
    },
    {
        "id": "off_health_01",
        "name": "Dr. Priya Fernando",
        "role": "Director - Health Services",
        "ministry_id": "ministry_health",
        "contact": {
            "email": "priya@health.gov.lk",
            "phone": "071-4567890"
        },
        "photo": "/static/img/officer3.jpg",
        "bio": "Overseeing public health initiatives"
    }
]

officers_col.delete_many({})
officers_col.insert_many(officers)
print(f"✅ Created {len(officers)} officers")

# 3. Create Sample Ads/Announcements
print("\n📢 Creating sample ads...")
ads = [
    {
        "id": "ad_courses_01",
        "type": "training",
        "title": {
            "en": "Free Digital Skills Course",
            "si": "නොමිලේ ඩිජිටල් කුසලතා පාඨමාලාව",
            "ta": "இலவச டிஜிட்டல் திறன் பயிற்சி"
        },
        "body": {
            "en": "Enroll now for government digital skills training. Limited seats available!",
            "si": "රජයේ ඩිජිටල් කුසලතා පුහුණුව සඳහා දැන් ලියාපදිංචි වන්න!",
            "ta": "அரசாங்க டிஜிட்டல் திறன் பயிற்சிக்கு இப்போதே பதிவு செய்யுங்கள்!"
        },
        "link": "https://digital.gov.lk/courses",
        "image": "/static/img/course-card.png",
        "start_date": datetime(2025, 1, 1),
        "end_date": datetime(2025, 12, 31),
        "active": True,
        "priority": 1
    },
    {
        "id": "ad_exams_01",
        "type": "announcement",
        "title": {
            "en": "2025 Exam Results Available",
            "si": "2025 විභාග ප්‍රතිඵල නිකුත් කෙරේ",
            "ta": "2025 தேர்வு முடிவுகள் வெளியிடப்பட்டுள்ளன"
        },
        "body": {
            "en": "Check your exam results on the official portal",
            "si": "නිල පෝටලයෙන් ඔබේ විභාග ප්‍රතිඵල පරීක්ෂා කරන්න",
            "ta": "உத்தியோகபூர்வ போர்ட்டலில் உங்கள் தேர்வு முடிவுகளைச் சரிபார்க்கவும்"
        },
        "link": "https://exam.gov.lk/results",
        "image": "/static/img/exam-results.png",
        "start_date": datetime(2025, 3, 1),
        "end_date": datetime(2025, 3, 31),
        "active": True,
        "priority": 2
    },
    {
        "id": "ad_passport_01",
        "type": "service",
        "title": {
            "en": "Online Passport Renewal",
            "si": "ඔන්ලයින් විදේශ ගමන් බලපත්‍ර අලුත් කිරීම",
            "ta": "ஆன்லைன் கடவுச்சீட்டு புதுப்பித்தல்"
        },
        "body": {
            "en": "Renew your passport online - fast and convenient",
            "si": "ඔබේ විදේශ ගමන් බලපත්‍රය ඔන්ලයින්ව අලුත් කරන්න",
            "ta": "உங்கள் கடவுச்சீட்டை ஆன்லைனில் புதுப்பிக்கவும்"
        },
        "link": "https://immigration.gov.lk/passport",
        "image": "/static/img/passport-renewal.png",
        "start_date": None,
        "end_date": None,
        "active": True,
        "priority": 3
    }
]

ads_col.delete_many({})
ads_col.insert_many(ads)
print(f"✅ Created {len(ads)} ads/announcements")

# 4. Update existing services with category field
print("\n🔄 Updating services with categories...")
services_col = db["services"]

category_mapping = {
    "ministry_it": "cat_it",
    "ministry_education": "cat_education",
    "ministry_health": "cat_health",
    "ministry_transport": "cat_transport",
    "ministry_imm": "cat_immigration",
    "ministry_foreign": "cat_immigration",
    "ministry_finance": "cat_public",
    "ministry_labour": "cat_public",
    "ministry_public": "cat_public",
    "ministry_justice": "cat_public",
    "ministry_housing": "cat_public",
    "ministry_agri": "cat_public",
    "ministry_youth": "cat_public",
    "ministry_defence": "cat_public",
    "ministry_tourism": "cat_public",
    "ministry_trade": "cat_public",
    "ministry_energy": "cat_public",
    "ministry_water": "cat_public",
    "ministry_env": "cat_public",
    "ministry_culture": "cat_public"
}

updated = 0
for ministry_id, category_id in category_mapping.items():
    result = services_col.update_one(
        {"id": ministry_id},
        {"$set": {"category": category_id}}
    )
    if result.modified_count > 0:
        updated += 1

print(f"✅ Updated {updated} services with categories")

# 5. Create indexes for better performance
print("\n📑 Creating database indexes...")
categories_col.create_index("id", unique=True)
officers_col.create_index("id", unique=True)
officers_col.create_index("ministry_id")
ads_col.create_index("id", unique=True)
ads_col.create_index("active")
users_col.create_index("email", unique=True, sparse=True)
print("✅ Created indexes")

# Add to migrate_db.py:

# Training Programs
print("\n🎓 Creating training programs...")
training_programs = [
    {
        "id": "train_digital_01",
        "title": {
            "en": "Digital Skills for Everyone",
            "si": "සියලු දෙනා සඳහා ඩිජිටල් කුසලතා",
            "ta": "அனைவருக்கும் டிஜிட்டல் திறன்கள்"
        },
        "description": {
            "en": "Learn essential digital skills for government services",
            "si": "රජයේ සේවා සඳහා අත්‍යවශ්‍ය ඩිජිටල් කුසලතා ඉගෙන ගන්න",
            "ta": "அரசாங்க சேவைகளுக்கான அத்தியாவசிய டிஜிட்டல் திறன்களை கற்றுக்கொள்ளுங்கள்"
        },
        "duration": "4 weeks",
        "level": "Beginner",
        "free": True,
        "enrollment_link": "https://digital.gov.lk/enroll",
        "start_date": datetime(2025, 2, 1),
        "active": True
    },
    {
        "id": "train_cyber_01",
        "title": {
            "en": "Cybersecurity Awareness",
            "si": "සයිබර් ආරක්ෂාව පිළිබඳ දැනුවත්භාවය",
            "ta": "இணைய பாதுகாப்பு விழிப்புணர்வு"
        },
        "description": {
            "en": "Stay safe online - government approved course",
            "si": "ඔන්ලයින් ආරක්ෂිතව සිටින්න - රජය විසින් අනුමත පාඨමාලාව",
            "ta": "ஆன்லைனில் பாதுகாப்பாக இருங்கள் - அரசாங்கத்தால் அங்கீகரிக்கப்பட்ட பாடநெறி"
        },
        "duration": "2 weeks",
        "level": "All levels",
        "free": True,
        "enrollment_link": "https://digital.gov.lk/cyber",
        "start_date": datetime(2025, 3, 1),
        "active": True
    }
]

training_programs_col = db["training_programs"]
training_programs_col.delete_many({})
training_programs_col.insert_many(training_programs)
print(f"✅ Created {len(training_programs)} training programs")

# Create indexes
training_programs_col.create_index("id", unique=True)
training_programs_col.create_index("active")
feedback_col.create_index([("service_id", 1), ("rating", -1)])
notifications_col.create_index([("user_id", 1), ("read", 1)])
# Summary
print("\n" + "=" * 60)
print("📊 MIGRATION SUMMARY")
print("=" * 60)
print(f"✅ Categories: {categories_col.count_documents({})}")
print(f"✅ Officers: {officers_col.count_documents({})}")
print(f"✅ Ads: {ads_col.count_documents({})}")
print(f"✅ Services: {services_col.count_documents({})}")
print(f"✅ Users Collection: Ready")
print("=" * 60)
print("\n🎉 Migration complete!")
print("\nNext steps:")
print("1. Run: python build_ai_index.py  (to create vector search)")
print("2. Run: python app.py  (to start the upgraded app)")
print("=" * 60)