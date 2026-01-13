"""
Seed sample advertisements for notification system
Run: python seed_ads.py
"""

import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
ads_col = db["ads"]

# Sample advertisements targeting different user segments
sample_ads = [
    # For Teachers
    {
        "title": {
            "en": "📚 Professional Development Course for Teachers",
            "si": "ගුරුවරුන් සඳහා වෘත්තීය සංවර්ධන පාඨමාලාව",
            "ta": "ஆசிரியர்களுக்கான தொழில்முறை மேம்பாட்டு பாடநெறி"
        },
        "body": {
            "en": "Enhance your teaching skills with our certified professional development program. Government-recognized certificate upon completion. Limited seats available!",
            "si": "අපගේ සහතික කළ වෘත්තීය සංවර්ධන වැඩසටහන සමඟ ඔබගේ ගුරු කුසලතා වැඩි දියුණු කරන්න. රජය විසින් පිළිගත් සහතිකයක්. සීමිත ආසන!",
            "ta": "எங்கள் சான்றளிக்கப்பட்ட தொழில்முறை மேம்பாட்டு திட்டத்துடன் உங்கள் கற்பித்தல் திறன்களை மேம்படுத்தவும். அரசாங்கத்தால் அங்கீகரிக்கப்பட்ட சான்றிதழ்!"
        },
        "link": "/training",
        "image": "/static/img/teacher_training.jpg",
        "category": "education",
        "priority": "high",
        "active": True,
        "target_segments": ["education_professional", "teacher"],
        "target_jobs": ["teacher"],
        "target_age_groups": ["26_35", "36_45", "46_60"],
        "keywords": ["teaching", "education", "school", "certificate"],
        "related_interests": ["professional_development", "education"],
        "duration_days": 14,
        "created": datetime.utcnow()
    },
    
    # For Government Employees
    {
        "title": {
            "en": "🎓 Complete Your Degree - Special Program for Government Employees",
            "si": "රජයේ සේවකයින් සඳහා විශේෂ උපාධි වැඩසටහන",
            "ta": "அரசாங்க ஊழியர்களுக்கான பட்டப்படிப்பு முடிக்க சிறப்பு திட்டம்"
        },
        "body": {
            "en": "Flexible evening and weekend classes designed for working professionals. Recognized by UGC. Boost your career with a degree!",
            "si": "වැඩ කරන වෘත්තිකයන් සඳහා නිර්මාණය කර ඇති නම්‍යශීලී සන්ධ්‍යා හා සති අන්ත පන්ති. UGC විසින් පිළිගත්. උපාධියක් සමඟ ඔබේ වෘත්තීය ජීවිතය ඉහළ නංවන්න!",
            "ta": "பணிபுரியும் நிபுணர்களுக்காக வடிவமைக்கப்பட்ட நெகிழ்வான மாலை மற்றும் வார இறுதி வகுப்புகள். UGC ஆல் அங்கீகரிக்கப்பட்டது!"
        },
        "link": "/training",
        "image": "/static/img/degree_program.jpg",
        "category": "education",
        "priority": "high",
        "active": True,
        "target_segments": ["government_employee", "needs_qualification"],
        "target_jobs": ["government"],
        "target_age_groups": ["26_35", "36_45"],
        "target_education": ["ol", "al", "diploma"],
        "keywords": ["degree", "university", "qualification", "education"],
        "related_interests": ["career_growth", "education"],
        "duration_days": 21,
        "created": datetime.utcnow()
    },
    
    # For Parents with School-Age Children
    {
        "title": {
            "en": "🎯 O/L Exam Preparation - Expert Tuition Classes",
            "si": "O/L විභාග සූදානම - ප්‍රවීණ පෞද්ගලික පන්ති",
            "ta": "O/L தேர்வுத் தயாரிப்பு - நிபுணர் பயிற்சி வகுப்புகள்"
        },
        "body": {
            "en": "Help your child excel in O/L exams with our proven teaching methods. Small batches, individual attention. Free trial class available!",
            "si": "අපගේ ඔප්පු කරන ලද ඉගැන්වීම් ක්‍රම සමඟ ඔබේ දරුවාට O/L විභාගවල විශිෂ්ට වීමට උදව් කරන්න. කුඩා කණ්ඩායම්, පුද්ගල අවධානය!",
            "ta": "எங்கள் நிரூபிக்கப்பட்ட கற்பித்தல் முறைகளுடன் உங்கள் குழந்தை O/L தேர்வுகளில் சிறந்து விளங்க உதவுங்கள்!"
        },
        "link": "/training",
        "image": "/static/img/ol_tuition.jpg",
        "category": "education",
        "priority": "high",
        "active": True,
        "target_segments": ["parent", "primary_school_parent", "secondary_school_parent"],
        "target_age_groups": ["36_45", "46_60"],
        "keywords": ["ol exam", "tuition", "school", "children", "exam preparation"],
        "related_interests": ["child_education", "tuition"],
        "duration_days": 30,
        "created": datetime.utcnow()
    },
    
    # For Young Professionals
    {
        "title": {
            "en": "🌍 IELTS Coaching - Achieve Your Dream Score",
            "si": "IELTS පුහුණුව - ඔබගේ සිහින ලකුණු ලබා ගන්න",
            "ta": "IELTS பயிற்சி - உங்கள் கனவு மதிப்பெண்ணை அடையுங்கள்"
        },
        "body": {
            "en": "Prepare for overseas opportunities! Expert IELTS coaching with proven results. 90% students achieve band 7+. Flexible timings for working professionals.",
            "si": "විදේශ අවස්ථා සඳහා සූදානම් වන්න! ප්‍රවීණ IELTS පුහුණුව. 90% සිසුන් band 7+ ලබා ගනී!",
            "ta": "வெளிநாட்டு வாய்ப்புகளுக்கு தயாராகுங்கள்! நிபுணர் IELTS பயிற்சி. 90% மாணவர்கள் band 7+ அடைகிறார்கள்!"
        },
        "link": "/training",
        "image": "/static/img/ielts.jpg",
        "category": "language",
        "priority": "medium",
        "active": True,
        "target_segments": ["young_adult", "early_career"],
        "target_age_groups": ["18_25", "26_35"],
        "keywords": ["ielts", "overseas", "abroad", "english", "migration"],
        "related_interests": ["career_growth", "overseas_jobs"],
        "duration_days": 14,
        "created": datetime.utcnow()
    },
    
    # For Students
    {
        "title": {
            "en": "💻 Learn Programming - Free Online Course",
            "si": "වැඩසටහන් නිර්මාණය ඉගෙන ගන්න - නොමිලේ මාර්ගගත පාඨමාලාව",
            "ta": "நிரலாக்கத்தைக் கற்றுக்கொள்ளுங்கள் - இலவச ஆன்லைன் பாடநெறி"
        },
        "body": {
            "en": "Start your IT career with our beginner-friendly programming course. Python, JavaScript, Web Development. Government-certified program. Enroll now!",
            "si": "අපගේ ආරම්භකයින් සඳහා මිත්‍රශීලී වැඩසටහන් නිර්මාණ පාඨමාලාව සමඟ ඔබේ IT වෘත්තීය ජීවිතය ආරම්භ කරන්න!",
            "ta": "எங்கள் தொடக்கநிலை நட்பு நிரலாக்க பாடநெறியுடன் உங்கள் IT வாழ்க்கையைத் தொடங்குங்கள்!"
        },
        "link": "/training",
        "image": "/static/img/programming.jpg",
        "category": "technology",
        "priority": "medium",
        "active": True,
        "target_segments": ["student", "young_adult"],
        "target_age_groups": ["18_25"],
        "keywords": ["programming", "coding", "it", "technology", "python"],
        "related_interests": ["technology", "career_growth"],
        "duration_days": 30,
        "created": datetime.utcnow()
    },
    
    # For Seniors
    {
        "title": {
            "en": "💰 Senior Citizen Pension Benefits - Apply Now",
            "si": "ජ්‍යෙෂ්ඨ පුරවැසි විශ්‍රාම වැටුප් ප්‍රතිලාභ - දැන් අයදුම් කරන්න",
            "ta": "மூத்த குடிமக்கள் ஓய்வூதிய சலுகைகள் - இப்போது விண்ணப்பிக்கவும்"
        },
        "body": {
            "en": "Are you 60 or above? You may be eligible for senior citizen benefits. Free consultation available. Get help with your application process.",
            "si": "ඔබට වයස අවුරුදු 60 හෝ ඊට වැඩිද? ඔබට ජ්‍යෙෂ්ඨ පුරවැසි ප්‍රතිලාභ සඳහා සුදුසුකම් ලැබිය හැක!",
            "ta": "உங்களுக்கு 60 அல்லது அதற்கு மேற்பட்ட வயதா? நீங்கள் மூத்த குடிமக்கள் நன்மைகளுக்கு தகுதியுடையவராக இருக்கலாம்!"
        },
        "link": "/services",
        "image": "/static/img/pension.jpg",
        "category": "social_welfare",
        "priority": "high",
        "active": True,
        "target_segments": ["senior"],
        "target_age_groups": ["60_plus"],
        "keywords": ["pension", "senior", "retirement", "benefits"],
        "related_interests": ["social_welfare", "retirement"],
        "duration_days": 60,
        "created": datetime.utcnow()
    },
    
    # For Entrepreneurs
    {
        "title": {
            "en": "🚀 Small Business Loans - Low Interest Rates",
            "si": "කුඩා ව්‍යාපාර ණය - අඩු පොලී අනුපාත",
            "ta": "சிறு வணிகக் கடன்கள் - குறைந்த வட்டி விகிதங்கள்"
        },
        "body": {
            "en": "Grow your business with our special SME loan program. Easy application process, quick approval. Up to LKR 5 million at competitive rates.",
            "si": "අපගේ විශේෂ SME ණය වැඩසටහන සමඟ ඔබේ ව්‍යාපාරය වර්ධනය කරන්න. ලක්ෂ 50 දක්වා!",
            "ta": "எங்கள் சிறப்பு SME கடன் திட்டத்துடன் உங்கள் வணிகத்தை வளர்க்கவும். 50 இலட்சம் வரை!"
        },
        "link": "/services",
        "image": "/static/img/business_loan.jpg",
        "category": "business",
        "priority": "medium",
        "active": True,
        "target_segments": ["entrepreneur", "management"],
        "target_jobs": ["business"],
        "keywords": ["loan", "business", "entrepreneur", "finance"],
        "related_interests": ["business_services", "loans"],
        "duration_days": 30,
        "created": datetime.utcnow()
    }
]

# Insert or update advertisements
print("=" * 70)
print("📢 SEEDING ADVERTISEMENTS")
print("=" * 70)

for ad in sample_ads:
    result = ads_col.update_one(
        {"title.en": ad["title"]["en"]},
        {"$set": ad},
        upsert=True
    )
    
    if result.upserted_id:
        print(f"✅ Added: {ad['title']['en']}")
    else:
        print(f"🔄 Updated: {ad['title']['en']}")

total_ads = ads_col.count_documents({"active": True})

print("=" * 70)
print(f"✅ Total active advertisements: {total_ads}")
print("=" * 70)
print("\nNow run the Flask app and visit the home page!")
print("The notification system will automatically detect user profiles and trigger relevant ads.")
print("=" * 70)