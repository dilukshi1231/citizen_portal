"""
Seed Store Products Database
Run: python seed_store_products.py
"""

import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["citizen_portal"]
products_col = db["products"]

print("=" * 60)
print("🛒 SEEDING STORE PRODUCTS DATABASE")
print("=" * 60)

# Clear existing products
products_col.delete_many({})

# Sample products for public store
products = [
    {
        "id": "prod_degree_01",
        "name": "Bachelor of IT (SpaceXP Campus)",
        "category": "education",
        "subcategory": "degree_programs",
        "price": 185000,
        "original_price": 225000,
        "currency": "LKR",
        "images": ["/static/store/degree_it.jpg"],
        "description": "Complete your IT degree with flexible payment options. Government employee discount available.",
        "features": ["3-year program", "Weekend classes", "Online support", "Government discount"],
        "tags": ["degree", "it", "government", "career_advancement"],
        "target_segments": ["needs_qualification", "government_employee", "mid_career_family"],
        "in_stock": True,
        "delivery_options": ["online", "campus"],
        "rating": 4.5,
        "reviews_count": 47,
        "created": datetime.utcnow()
    },
    {
        "id": "prod_ielts_01",
        "name": "IELTS Preparation Course",
        "category": "education",
        "subcategory": "language_courses",
        "price": 25000,
        "original_price": 35000,
        "currency": "LKR",
        "images": ["/static/store/ielts_course.jpg"],
        "description": "Comprehensive IELTS preparation with mock tests and speaking practice.",
        "features": ["4-week intensive", "Expert trainers", "Mock tests", "Speaking practice"],
        "tags": ["ielts", "english", "overseas", "government"],
        "target_segments": ["government_employee", "early_career", "mid_education"],
        "in_stock": True,
        "delivery_options": ["online", "classroom"],
        "rating": 4.7,
        "reviews_count": 89,
        "created": datetime.utcnow()
    },
    {
        "id": "prod_japan_visa_01",
        "name": "Japan Work Visa Assistance",
        "category": "visa_services",
        "subcategory": "job_visas",
        "price": 45000,
        "currency": "LKR",
        "images": ["/static/store/japan_visa.jpg"],
        "description": "Complete assistance for Japan work visa applications. IT and healthcare opportunities.",
        "features": ["Visa processing", "Job matching", "Document preparation", "Pre-departure orientation"],
        "tags": ["japan", "work_visa", "overseas_jobs", "it_jobs"],
        "target_segments": ["early_career", "mid_career_family", "needs_qualification"],
        "in_stock": True,
        "delivery_options": ["consultation"],
        "rating": 4.3,
        "reviews_count": 34,
        "created": datetime.utcnow()
    },
    {
        "id": "prod_laptop_01",
        "name": "Government Employee Laptop Deal",
        "category": "electronics",
        "subcategory": "computers",
        "price": 85000,
        "original_price": 115000,
        "currency": "LKR",
        "images": ["/static/store/laptop_deal.jpg"],
        "description": "Special laptop package for government employees with extended warranty.",
        "features": ["Intel i5 processor", "8GB RAM", "256GB SSD", "2-year warranty", "Government discount"],
        "tags": ["laptop", "electronics", "government_deal", "technology"],
        "target_segments": ["government_employee", "early_career", "mid_career_family"],
        "in_stock": True,
        "delivery_options": ["delivery", "pickup"],
        "rating": 4.4,
        "reviews_count": 156,
        "created": datetime.utcnow()
    },
    {
        "id": "prod_saree_01",
        "name": "Handloom Batik Saree Collection",
        "category": "fashion",
        "subcategory": "traditional_wear",
        "price": 4500,
        "original_price": 6500,
        "currency": "LKR",
        "images": ["/static/store/batik_saree.jpg"],
        "description": "Authentic handloom batik sarees with traditional designs. Limited edition.",
        "features": ["Pure cotton", "Handmade", "Traditional designs", "Multiple colors"],
        "tags": ["saree", "batik", "handloom", "traditional", "fashion"],
        "target_segments": ["mid_career_family", "established_professional", "senior"],
        "in_stock": True,
        "delivery_options": ["delivery", "pickup"],
        "rating": 4.6,
        "reviews_count": 203,
        "created": datetime.utcnow()
    },
    {
        "id": "prod_tuition_01",
        "name": "O/L Mathematics Tuition (Online)",
        "category": "education",
        "subcategory": "tuition",
        "price": 8000,
        "original_price": 12000,
        "currency": "LKR",
        "images": ["/static/store/ol_maths.jpg"],
        "description": "Expert O/L Mathematics tuition with proven track record. Small batch sizes.",
        "features": ["Experienced teacher", "Weekly tests", "Past papers", "Video lessons"],
        "tags": ["ol", "mathematics", "tuition", "education"],
        "target_segments": ["parent", "secondary_school_parent"],
        "in_stock": True,
        "delivery_options": ["online"],
        "rating": 4.8,
        "reviews_count": 124,
        "created": datetime.utcnow()
    },
    {
        "id": "prod_slas_01",
        "name": "SLAS Exam Preparation Course",
        "category": "education",
        "subcategory": "government_exams",
        "price": 35000,
        "currency": "LKR",
        "images": ["/static/store/slas_prep.jpg"],
        "description": "Comprehensive SLAS exam preparation by former SLAS officers. High success rate.",
        "features": ["6-month program", "Mock interviews", "Essay practice", "Current affairs"],
        "tags": ["slas", "government", "career", "exam_prep"],
        "target_segments": ["government_employee", "early_career", "highly_educated"],
        "in_stock": True,
        "delivery_options": ["classroom", "online"],
        "rating": 4.9,
        "reviews_count": 67,
        "created": datetime.utcnow()
    },
    {
        "id": "prod_career_01",
        "name": "Career Guidance & CV Building",
        "category": "career_services",
        "subcategory": "consulting",
        "price": 5000,
        "currency": "LKR",
        "images": ["/static/store/career_guidance.jpg"],
        "description": "Professional career guidance and CV building services. LinkedIn optimization included.",
        "features": ["One-on-one session", "Professional CV", "LinkedIn profile", "Interview prep"],
        "tags": ["career", "cv", "jobs", "professional"],
        "target_segments": ["young_adult", "early_career"],
        "in_stock": True,
        "delivery_options": ["online", "consultation"],
        "rating": 4.6,
        "reviews_count": 89,
        "created": datetime.utcnow()
    }
]

result = products_col.insert_many(products)

print(f"\n✅ Inserted {len(products)} products")
print("\n📊 PRODUCT BREAKDOWN:")
print(f"   - Education: {len([p for p in products if p['category'] == 'education'])}")
print(f"   - Visa Services: {len([p for p in products if p['category'] == 'visa_services'])}")
print(f"   - Electronics: {len([p for p in products if p['category'] == 'electronics'])}")
print(f"   - Fashion: {len([p for p in products if p['category'] == 'fashion'])}")
print(f"   - Career Services: {len([p for p in products if p['category'] == 'career_services'])}")

# Create indexes
products_col.create_index("id", unique=True)
products_col.create_index("category")
products_col.create_index("in_stock")
products_col.create_index([("tags", 1)])

print("\n✅ Created database indexes")
print("\n" + "=" * 60)
print("🎉 Store products database ready!")
print("\nNext steps:")
print("1. Run: python sample_customers.py")
print("2. Visit: http://localhost:5000/store")
print("=" * 60)