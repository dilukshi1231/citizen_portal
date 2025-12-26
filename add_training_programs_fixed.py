"""
FIXED Script to Add New Training Programs with Enrollment Open
Run this script: python add_training_programs_fixed.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
training_programs_col = db["training_programs"]

print("=" * 70)
print("📚 ADDING NEW TRAINING PROGRAMS (WITH ENROLLMENT OPEN)")
print("=" * 70)

# New training programs to add - WITH enrollment_open=True
new_programs = [
    {
        "id": "train_python_programming_01",
        "title": {
            "en": "Python Programming for Beginners",
            "si": "ආරම්භකයින් සඳහා Python වැඩසටහන්කරණය",
            "ta": "தொடக்க நிலைக்கான Python நிரலாக்கம்"
        },
        "description": {
            "en": "Learn Python programming from scratch. Build real-world applications and automation scripts.",
            "si": "මුල සිට Python වැඩසටහන්කරණය ඉගෙන ගන්න. සැබෑ ලෝක යෙදුම් සහ ස්වයංක්‍රීය ස්ක්‍රිප්ට් තනන්න.",
            "ta": "புதிதாக Python நிரலாக்கத்தை கற்றுக்கொள்ளுங்கள். நிஜ உலக பயன்பாடுகள் மற்றும் தானியங்கு ஸ்கிரிப்ட்களை உருவாக்குங்கள்."
        },
        "category": "programming",
        "level": "Beginner",
        "duration": "8 weeks",
        "hours_per_week": 5,
        "language": ["en", "si"],
        "mode": "online",
        "free": True,
        "instructor": "National IT Academy",
        "topics": [
            "Python basics & syntax",
            "Data types and structures",
            "Functions and modules",
            "File handling",
            "Web scraping basics",
            "Final project"
        ],
        "prerequisites": "Basic computer knowledge",
        "certificate": True,
        "enrollment_link": "https://digital.gov.lk/enroll/python",
        "video_intro": "https://youtube.com/watch?v=python_intro",
        "brochure": "/static/docs/python_brochure.pdf",
        "start_date": datetime(2025, 2, 5),
        "end_date": datetime(2025, 4, 1),
        "max_participants": 300,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED: Added this field
        "active": True,
        "featured": True,
        "tags": ["programming", "python", "coding", "IT"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_data_analytics_01",
        "title": {
            "en": "Data Analytics with Excel",
            "si": "Excel සමඟ දත්ත විශ්ලේෂණය",
            "ta": "Excel உடன் தரவு பகுப்பாய்வு"
        },
        "description": {
            "en": "Master Excel for data analysis. Learn formulas, pivot tables, charts, and data visualization.",
            "si": "දත්ත විශ්ලේෂණය සඳහා Excel ප්‍රගුණ කරන්න. සූත්‍ර, pivot tables, ප්‍රස්තාර සහ දත්ත දෘශ්‍යකරණය ඉගෙන ගන්න.",
            "ta": "தரவு பகுப்பாய்வுக்காக Excel ஐ தேர்ச்சி பெறுங்கள். சூத்திரங்கள், pivot அட்டவணைகள், விளக்கப்படங்கள் மற்றும் தரவு காட்சிப்படுத்தலை கற்றுக்கொள்ளுங்கள்."
        },
        "category": "data_analysis",
        "level": "Intermediate",
        "duration": "5 weeks",
        "hours_per_week": 4,
        "language": ["en", "si", "ta"],
        "mode": "online",
        "free": True,
        "instructor": "Department of Census & Statistics",
        "topics": [
            "Advanced Excel formulas",
            "Pivot tables and charts",
            "Data cleaning",
            "VLOOKUP & HLOOKUP",
            "Dashboard creation",
            "Business reporting"
        ],
        "prerequisites": "Basic Excel knowledge",
        "certificate": True,
        "enrollment_link": "https://digital.gov.lk/enroll/excel",
        "video_intro": "https://youtube.com/watch?v=excel_analytics",
        "brochure": "/static/docs/excel_analytics_brochure.pdf",
        "start_date": datetime(2025, 2, 12),
        "end_date": datetime(2025, 3, 18),
        "max_participants": 400,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED
        "active": True,
        "featured": True,
        "tags": ["excel", "data", "analytics", "business"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_graphic_design_01",
        "title": {
            "en": "Graphic Design Fundamentals",
            "si": "ග්‍රැෆික් නිර්මාණ මූලධර්ම",
            "ta": "வரைகலை வடிவமைப்பு அடிப்படைகள்"
        },
        "description": {
            "en": "Learn graphic design using free tools like Canva, GIMP, and Inkscape. Create professional designs.",
            "si": "Canva, GIMP සහ Inkscape වැනි නොමිලේ මෙවලම් භාවිතයෙන් ග්‍රැෆික් නිර්මාණය ඉගෙන ගන්න. වෘත්තීය නිර්මාණ සාදන්න.",
            "ta": "Canva, GIMP மற்றும் Inkscape போன்ற இலவச கருவிகளைப் பயன்படுத்தி வரைகலை வடிவமைப்பைக் கற்றுக்கொள்ளுங்கள். தொழில்முறை வடிவமைப்புகளை உருவாக்குங்கள்."
        },
        "category": "design",
        "level": "Beginner",
        "duration": "6 weeks",
        "hours_per_week": 4,
        "language": ["en", "si"],
        "mode": "online",
        "free": False,
        "fee": "Rs. 3,500",
        "instructor": "Creative Arts Institute",
        "topics": [
            "Design principles",
            "Color theory",
            "Typography",
            "Logo design",
            "Social media graphics",
            "Print design basics"
        ],
        "prerequisites": "None - Creative mindset preferred",
        "certificate": True,
        "enrollment_link": "https://arts.gov.lk/enroll/graphic-design",
        "video_intro": "https://youtube.com/watch?v=design_intro",
        "brochure": "/static/docs/graphic_design_brochure.pdf",
        "start_date": datetime(2025, 2, 18),
        "end_date": datetime(2025, 3, 31),
        "max_participants": 150,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED
        "active": True,
        "featured": False,
        "tags": ["design", "creative", "graphics", "freelance"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_digital_marketing_01",
        "title": {
            "en": "Digital Marketing Essentials",
            "si": "ඩිජිටල් අලෙවිකරණ අත්‍යවශ්‍යතා",
            "ta": "டிஜிட்டல் சந்தைப்படுத்தல் அடிப்படைகள்"
        },
        "description": {
            "en": "Master social media marketing, SEO, content marketing, and online advertising strategies.",
            "si": "සමාජ මාධ්‍ය අලෙවිකරණය, SEO, අන්තර්ගත අලෙවිකරණය සහ ඔන්ලයින් ප්‍රචාරණ උපාය මාර්ග ප්‍රගුණ කරන්න.",
            "ta": "சமூக ஊடக சந்தைப்படுத்தல், SEO, உள்ளடக்க சந்தைப்படுத்தல் மற்றும் ஆன்லைன் விளம்பர உத்திகளில் தேர்ச்சி பெறுங்கள்."
        },
        "category": "marketing",
        "level": "Intermediate",
        "duration": "7 weeks",
        "hours_per_week": 5,
        "language": ["en", "si"],
        "mode": "hybrid",
        "free": False,
        "fee": "Rs. 8,000",
        "instructor": "Digital Marketing Academy",
        "topics": [
            "Social media strategy",
            "Facebook & Instagram ads",
            "Google Ads basics",
            "SEO fundamentals",
            "Content marketing",
            "Email marketing",
            "Analytics & reporting"
        ],
        "prerequisites": "Basic internet knowledge",
        "certificate": True,
        "enrollment_link": "https://trade.gov.lk/enroll/digital-marketing",
        "video_intro": "https://youtube.com/watch?v=marketing_intro",
        "brochure": "/static/docs/digital_marketing_brochure.pdf",
        "start_date": datetime(2025, 3, 1),
        "end_date": datetime(2025, 4, 19),
        "max_participants": 200,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED
        "active": True,
        "featured": True,
        "tags": ["marketing", "digital", "business", "entrepreneurship"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_english_speaking_01",
        "title": {
            "en": "English Speaking & Communication",
            "si": "ඉංග්‍රීසි කථන හා සන්නිවේදනය",
            "ta": "ஆங்கிலம் பேசுதல் மற்றும் தொடர்பு"
        },
        "description": {
            "en": "Improve your English speaking, listening, and communication skills for professional settings.",
            "si": "වෘත්තීය පරිසර සඳහා ඔබේ ඉංග්‍රීසි කථන, ශ්‍රවණ සහ සන්නිවේදන කුසලතා වැඩිදියුණු කරන්න.",
            "ta": "தொழில்முறை அமைப்புகளுக்கான உங்கள் ஆங்கில பேசுதல், கேட்டல் மற்றும் தொடர்பு திறன்களை மேம்படுத்துங்கள்."
        },
        "category": "language",
        "level": "Intermediate",
        "duration": "10 weeks",
        "hours_per_week": 3,
        "language": ["en"],
        "mode": "online",
        "free": True,
        "instructor": "National Language Centre",
        "topics": [
            "Pronunciation practice",
            "Conversation skills",
            "Business English",
            "Presentation skills",
            "Email writing",
            "Interview preparation"
        ],
        "prerequisites": "Basic English reading ability",
        "certificate": True,
        "enrollment_link": "https://education.gov.lk/enroll/english",
        "video_intro": "https://youtube.com/watch?v=english_intro",
        "brochure": "/static/docs/english_speaking_brochure.pdf",
        "start_date": datetime(2025, 2, 8),
        "end_date": datetime(2025, 4, 20),
        "max_participants": 500,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED
        "active": True,
        "featured": True,
        "tags": ["language", "english", "communication", "career"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_web_development_01",
        "title": {
            "en": "Web Development Bootcamp",
            "si": "වෙබ් සංවර්ධන Bootcamp",
            "ta": "வலை மேம்பாடு பயிற்சி முகாம்"
        },
        "description": {
            "en": "Complete web development course. Learn HTML, CSS, JavaScript, and build responsive websites.",
            "si": "සම්පූර්ණ වෙබ් සංවර්ධන පාඨමාලාව. HTML, CSS, JavaScript ඉගෙන ගෙන ප්‍රතිචාරාත්මක වෙබ් අඩවි තනන්න.",
            "ta": "முழுமையான வலை மேம்பாட்டு பாடநெறி. HTML, CSS, JavaScript கற்று பதிலளிக்கக்கூடிய இணையதளங்களை உருவாக்குங்கள்."
        },
        "category": "programming",
        "level": "Beginner",
        "duration": "12 weeks",
        "hours_per_week": 6,
        "language": ["en"],
        "mode": "online",
        "free": False,
        "fee": "Rs. 12,000",
        "instructor": "Tech Institute of Sri Lanka",
        "topics": [
            "HTML5 & CSS3",
            "JavaScript fundamentals",
            "Responsive design",
            "Bootstrap framework",
            "Git & GitHub",
            "Portfolio project"
        ],
        "prerequisites": "Basic computer skills",
        "certificate": True,
        "enrollment_link": "https://digital.gov.lk/enroll/webdev",
        "video_intro": "https://youtube.com/watch?v=webdev_intro",
        "brochure": "/static/docs/web_development_brochure.pdf",
        "start_date": datetime(2025, 3, 3),
        "end_date": datetime(2025, 5, 26),
        "max_participants": 250,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED
        "active": True,
        "featured": True,
        "tags": ["programming", "web", "development", "coding"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_accounting_basics_01",
        "title": {
            "en": "Basic Accounting & Bookkeeping",
            "si": "මූලික ගිණුම්කරණය සහ පොත් තැබීම",
            "ta": "அடிப்படை கணக்கியல் மற்றும் புத்தகப் பதிவு"
        },
        "description": {
            "en": "Learn fundamental accounting principles for small businesses. Understand financial statements and bookkeeping.",
            "si": "කුඩා ව්‍යාපාර සඳහා මූලික ගිණුම්කරණ මූලධර්ම ඉගෙන ගන්න. මූල්‍ය ප්‍රකාශන සහ පොත් තැබීම තේරුම් ගන්න.",
            "ta": "சிறிய வணிகங்களுக்கான அடிப்படை கணக்கியல் கொள்கைகளை கற்றுக்கொள்ளுங்கள். நிதி அறிக்கைகள் மற்றும் புத்தகப் பதிவை புரிந்து கொள்ளுங்கள்."
        },
        "category": "finance",
        "level": "Beginner",
        "duration": "6 weeks",
        "hours_per_week": 4,
        "language": ["en", "si", "ta"],
        "mode": "online",
        "free": True,
        "instructor": "Ministry of Finance",
        "topics": [
            "Accounting basics",
            "Double-entry bookkeeping",
            "Financial statements",
            "Bank reconciliation",
            "Tax basics",
            "QuickBooks tutorial"
        ],
        "prerequisites": "Basic math skills",
        "certificate": True,
        "enrollment_link": "https://finance.gov.lk/enroll/accounting",
        "video_intro": "https://youtube.com/watch?v=accounting_intro",
        "brochure": "/static/docs/accounting_brochure.pdf",
        "start_date": datetime(2025, 2, 15),
        "end_date": datetime(2025, 3, 29),
        "max_participants": 300,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED
        "active": True,
        "featured": False,
        "tags": ["finance", "accounting", "business", "bookkeeping"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_mobile_photography_01",
        "title": {
            "en": "Mobile Photography & Editing",
            "si": "ජංගම ඡායාරූපකරණය සහ සංස්කරණය",
            "ta": "மொபைல் புகைப்படம் மற்றும் திருத்தம்"
        },
        "description": {
            "en": "Take professional photos with your smartphone. Learn composition, lighting, and mobile editing apps.",
            "si": "ඔබේ ස්මාර්ට්ෆෝනය සමඟ වෘත්තීය ඡායාරූප ගන්න. සංයුතිය, ආලෝකකරණය සහ ජංගම සංස්කරණ යෙදුම් ඉගෙන ගන්න.",
            "ta": "உங்கள் ஸ்மார்ட்போனில் தொழில்முறை புகைப்படங்களை எடுங்கள். கலவை, விளக்கு மற்றும் மொபைல் திருத்த பயன்பாடுகளை கற்றுக்கொள்ளுங்கள்."
        },
        "category": "creative",
        "level": "Beginner",
        "duration": "4 weeks",
        "hours_per_week": 3,
        "language": ["en", "si", "ta"],
        "mode": "online",
        "free": True,
        "instructor": "Creative Media Centre",
        "topics": [
            "Photography basics",
            "Composition rules",
            "Lighting techniques",
            "Mobile editing apps",
            "Portrait photography",
            "Social media content"
        ],
        "prerequisites": "Smartphone with camera",
        "certificate": True,
        "enrollment_link": "https://arts.gov.lk/enroll/photography",
        "video_intro": "https://youtube.com/watch?v=photography_intro",
        "brochure": "/static/docs/mobile_photography_brochure.pdf",
        "start_date": datetime(2025, 2, 22),
        "end_date": datetime(2025, 3, 21),
        "max_participants": 400,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED
        "active": True,
        "featured": False,
        "tags": ["photography", "creative", "mobile", "editing"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_freelancing_guide_01",
        "title": {
            "en": "Freelancing & Remote Work Guide",
            "si": "නිදහස් රැකියා සහ දුරස්ථ වැඩ මාර්ගෝපදේශය",
            "ta": "சுதந்திர மற்றும் தொலைதூர வேலை வழிகாட்டி"
        },
        "description": {
            "en": "Start your freelancing career. Learn how to find clients, manage projects, and work remotely.",
            "si": "ඔබේ නිදහස් රැකියා ජීවිතය ආරම්භ කරන්න. සේවාදායකයින් සොයා ගන්නා ආකාරය, ව්‍යාපෘති කළමනාකරණය සහ දුරස්ථව වැඩ කිරීම ඉගෙන ගන්න.",
            "ta": "உங்கள் சுதந்திர வேலை வாழ்க்கையை தொடங்குங்கள். வாடிக்கையாளர்களை எவ்வாறு கண்டுபிடிப்பது, திட்டங்களை நிர்வகிப்பது மற்றும் தொலைதூரத்தில் வேலை செய்வது என்பதை கற்றுக்கொள்ளுங்கள்."
        },
        "category": "entrepreneurship",
        "level": "Beginner",
        "duration": "5 weeks",
        "hours_per_week": 3,
        "language": ["en", "si"],
        "mode": "online",
        "free": True,
        "instructor": "Freelancers Association of Sri Lanka",
        "topics": [
            "Freelancing platforms",
            "Profile optimization",
            "Proposal writing",
            "Pricing strategies",
            "Client communication",
            "Payment methods"
        ],
        "prerequisites": "Any marketable skill",
        "certificate": True,
        "enrollment_link": "https://youth.gov.lk/enroll/freelancing",
        "video_intro": "https://youtube.com/watch?v=freelancing_intro",
        "brochure": "/static/docs/freelancing_brochure.pdf",
        "start_date": datetime(2025, 2, 25),
        "end_date": datetime(2025, 3, 29),
        "max_participants": 600,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED
        "active": True,
        "featured": True,
        "tags": ["freelancing", "remote work", "entrepreneurship", "career"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    },
    {
        "id": "train_video_editing_01",
        "title": {
            "en": "Video Editing with Free Tools",
            "si": "නොමිලේ මෙවලම් සමඟ වීඩියෝ සංස්කරණය",
            "ta": "இலவச கருவிகளுடன் வீடியோ திருத்தம்"
        },
        "description": {
            "en": "Create professional videos using free editing software. Perfect for YouTube, TikTok, and social media.",
            "si": "නොමිලේ සංස්කරණ මෘදුකාංග භාවිතයෙන් වෘත්තීය වීඩියෝ සාදන්න. YouTube, TikTok සහ සමාජ මාධ්‍ය සඳහා පරිපූර්ණයි.",
            "ta": "இலவச திருத்த மென்பொருளைப் பயன்படுத்தி தொழில்முறை வீடியோக்களை உருவாக்குங்கள். YouTube, TikTok மற்றும் சமூக ஊடகங்களுக்கு சரியானது."
        },
        "category": "creative",
        "level": "Beginner",
        "duration": "6 weeks",
        "hours_per_week": 4,
        "language": ["en", "si"],
        "mode": "online",
        "free": False,
        "fee": "Rs. 4,500",
        "instructor": "Media Production Centre",
        "topics": [
            "Video editing basics",
            "DaVinci Resolve tutorial",
            "Transitions & effects",
            "Color grading",
            "Audio editing",
            "Export settings"
        ],
        "prerequisites": "Basic computer skills",
        "certificate": True,
        "enrollment_link": "https://arts.gov.lk/enroll/video-editing",
        "video_intro": "https://youtube.com/watch?v=video_editing_intro",
        "brochure": "/static/docs/video_editing_brochure.pdf",
        "start_date": datetime(2025, 3, 5),
        "end_date": datetime(2025, 4, 16),
        "max_participants": 200,
        "current_enrollments": 0,
        "enrollment_open": True,  # ✅ FIXED
        "active": True,
        "featured": False,
        "tags": ["video", "editing", "creative", "content creation"],
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    }
]

# Check for existing programs before inserting
print(f"\n🔍 Checking for existing programs...")
existing_ids = set()
for program in new_programs:
    if training_programs_col.find_one({"id": program["id"]}):
        existing_ids.add(program["id"])
        print(f"   ⚠️  Program '{program['id']}' already exists - skipping")

# Filter out existing programs
programs_to_insert = [p for p in new_programs if p["id"] not in existing_ids]

if programs_to_insert:
    print(f"\n📝 Inserting {len(programs_to_insert)} new programs...")
    result = training_programs_col.insert_many(programs_to_insert)
    print(f"✅ Successfully inserted {len(result.inserted_ids)} programs")
else:
    print("\n✓ All programs already exist in the database")

# IMPORTANT: Fix existing programs that don't have enrollment_open
print(f"\n🔧 Fixing existing programs without enrollment_open field...")
fix_result = training_programs_col.update_many(
    {"enrollment_open": {"$exists": False}},
    {"$set": {"enrollment_open": True}}
)
print(f"✅ Updated {fix_result.modified_count} existing programs")

# Print summary
print("\n" + "=" * 70)
print("📊 TRAINING PROGRAMS SUMMARY")
print("=" * 70)

total_programs = training_programs_col.count_documents({})
free_programs = training_programs_col.count_documents({"free": True})
paid_programs = training_programs_col.count_documents({"free": False})
featured_programs = training_programs_col.count_documents({"featured": True})
active_programs = training_programs_col.count_documents({"active": True})
open_enrollment = training_programs_col.count_documents({"enrollment_open": True})

print(f"Total Programs in Database: {total_programs}")
print(f"Free Programs: {free_programs}")
print(f"Paid Programs: {paid_programs}")
print(f"Featured Programs: {featured_programs}")
print(f"Active Programs: {active_programs}")
print(f"Enrollment Open: {open_enrollment}")

# Count by category
print("\nPrograms by Category:")
pipeline = [
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
for result in training_programs_col.aggregate(pipeline):
    print(f"  - {result['_id']}: {result['count']}")

print("\n" + "=" * 70)
print("✅ Training programs update complete!")
print("=" * 70)
print("\n📌 Next steps:")
print("1. Visit http://localhost:5000/training to see all programs")
print("2. All programs now have 'Enroll Now' buttons enabled")
print("3. Users can enroll in programs immediately")
print("=" * 70)