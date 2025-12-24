"""
Seed Products Database with Segment-Targeted Products
Run: python seed_products.py
"""

import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
products_col = db["products"]

print("=" * 70)
print("🛒 SEEDING PRODUCT DATABASE")
print("=" * 70)

# Clear existing products
products_col.delete_many({})

# Comprehensive product catalog
products = [
    # ============================================
    # EDUCATION PROGRAMS (For Government Employees & Parents)
    # ============================================
    {
        "id": "prod_degree_management",
        "name": "Bachelor's Degree - Management Studies",
        "category": "degree_programs",
        "subcategory": "business",
        "description": "Accredited online degree program perfect for working professionals. Complete in 3 years with flexible schedules.",
        "price": 350000,
        "original_price": 450000,
        "currency": "LKR",
        "rating": 4.7,
        "reviews_count": 156,
        "in_stock": True,
        "stock_quantity": 50,
        "images": ["/static/products/degree_management.jpg"],
        "features": [
            "Fully accredited university degree",
            "Weekend classes available",
            "Online and in-person options",
            "Career counseling included",
            "Recognized by UGC"
        ],
        "target_segments": ["government_employee", "entrepreneur", "young_professional"],
        "tags": ["degree_programs", "professional_development", "education"],
        "featured": True,
        "active": True,
        "created": datetime.utcnow()
    },
    
    {
        "id": "prod_tuition_maths",
        "name": "O/L Mathematics - Complete Program",
        "category": "tuition",
        "subcategory": "secondary_education",
        "description": "Comprehensive O/L Mathematics preparation with experienced teachers. Small batch sizes (max 15 students).",
        "price": 8500,
        "currency": "LKR",
        "rating": 4.9,
        "reviews_count": 287,
        "in_stock": True,
        "stock_quantity": 30,
        "images": ["/static/products/tuition_maths.jpg"],
        "features": [
            "3 months intensive program",
            "Past paper practice",
            "Weekly assessments",
            "Small batch sizes",
            "Free study materials"
        ],
        "target_segments": ["parent"],
        "tags": ["tuition", "exam_prep", "education"],
        "featured": True,
        "active": True,
        "created": datetime.utcnow()
    },
    
    {
        "id": "prod_exam_prep_al",
        "name": "A/L Combined Mathematics Crash Course",
        "category": "exam_prep",
        "subcategory": "advanced_level",
        "description": "Intensive A/L Combined Maths preparation. Covers full syllabus in 6 weeks with guaranteed results.",
        "price": 12000,
        "original_price": 15000,
        "currency": "LKR",
        "rating": 4.8,
        "reviews_count": 198,
        "in_stock": True,
        "stock_quantity": 25,
        "images": ["/static/products/al_maths.jpg"],
        "features": [
            "6-week intensive course",
            "Top teachers (20+ years exp)",
            "Complete past papers",
            "Video recordings provided",
            "Money-back guarantee"
        ],
        "target_segments": ["parent", "student"],
        "tags": ["exam_prep", "a_level", "education"],
        "featured": True,
        "active": True,
        "created": datetime.utcnow()
    },
    
    # ============================================
    # OVERSEAS OPPORTUNITIES (For Young Professionals)
    # ============================================
    {
        "id": "prod_ielts_course",
        "name": "IELTS Complete Preparation Package",
        "category": "ielts_courses",
        "subcategory": "language_training",
        "description": "Full IELTS preparation with guaranteed score improvement. Includes speaking practice sessions.",
        "price": 25000,
        "original_price": 35000,
        "currency": "LKR",
        "rating": 4.9,
        "reviews_count": 432,
        "in_stock": True,
        "stock_quantity": 40,
        "images": ["/static/products/ielts_course.jpg"],
        "features": [
            "8-week comprehensive program",
            "British Council certified trainers",
            "Speaking practice sessions",
            "Mock tests included",
            "Score guarantee (6.5+)",
            "Free re-enrollment if not achieved"
        ],
        "target_segments": ["young_professional", "student"],
        "tags": ["ielts_courses", "overseas_jobs", "career_growth"],
        "featured": True,
        "active": True,
        "created": datetime.utcnow()
    },
    
    {
        "id": "prod_visa_consultation",
        "name": "UK/Canada Work Visa Consultation",
        "category": "overseas_jobs",
        "subcategory": "visa_services",
        "description": "Expert consultation for UK and Canada work visas. Over 95% success rate.",
        "price": 15000,
        "currency": "LKR",
        "rating": 4.7,
        "reviews_count": 267,
        "in_stock": True,
        "stock_quantity": 100,
        "images": ["/static/products/visa_consultation.jpg"],
        "features": [
            "Document preparation assistance",
            "Interview coaching",
            "95% success rate",
            "Post-arrival support",
            "Job placement assistance"
        ],
        "target_segments": ["young_professional"],
        "tags": ["overseas_jobs", "visa", "migration"],
        "featured": True,
        "active": True,
        "created": datetime.utcnow()
    },
    
    {
        "id": "prod_job_placement_overseas",
        "name": "Overseas Job Placement - IT Sector",
        "category": "overseas_jobs",
        "subcategory": "job_placement",
        "description": "Guaranteed job placement in UK, Canada, Australia for IT professionals.",
        "price": 50000,
        "currency": "LKR",
        "rating": 4.6,
        "reviews_count": 189,
        "in_stock": True,
        "stock_quantity": 20,
        "images": ["/static/products/job_placement.jpg"],
        "features": [
            "Direct employer connections",
            "Resume optimization",
            "Interview preparation",
            "Work visa support",
            "No placement, full refund"
        ],
        "target_segments": ["young_professional"],
        "tags": ["overseas_jobs", "career_growth", "it"],
        "featured": True,
        "active": True,
        "created": datetime.utcnow()
    },
    
    # ============================================
    # ELECTRONICS (Government Deals)
    # ============================================
    {
        "id": "prod_laptop_dell",
        "name": "Dell Inspiron 15 - Government Special",
        "category": "electronics",
        "subcategory": "laptops",
        "description": "Special government employee pricing. High-performance laptop for work and study.",
        "price": 125000,
        "original_price": 155000,
        "currency": "LKR",
        "rating": 4.5,
        "reviews_count": 312,
        "in_stock": True,
        "stock_quantity": 15,
        "images": ["/static/products/laptop_dell.jpg"],
        "features": [
            "Intel Core i5 11th Gen",
            "8GB RAM, 512GB SSD",
            "15.6\" FHD Display",
            "2-year warranty",
            "Government employee discount"
        ],
        "target_segments": ["government_employee", "student", "young_professional"],
        "tags": ["laptops", "electronics", "government_special"],
        "featured": True,
        "active": True,
        "created": datetime.utcnow()
    },
    
    {
        "id": "prod_tablet_samsung",
        "name": "Samsung Galaxy Tab A8 - Education Edition",
        "category": "electronics",
        "subcategory": "tablets",
        "description": "Perfect for students and online learning. Includes educational apps.",
        "price": 45000,
        "original_price": 52000,
        "currency": "LKR",
        "rating": 4.6,
        "reviews_count": 198,
        "in_stock": True,
        "stock_quantity": 30,
        "images": ["/static/products/tablet_samsung.jpg"],
        "features": [
            "10.5\" display",
            "4GB RAM, 64GB storage",
            "Education apps pre-installed",
            "Long battery life",
            "Stylus pen included"
        ],
        "target_segments": ["parent", "student"],
        "tags": ["tablets", "education", "electronics"],
        "featured": False,
        "active": True,
        "created": datetime.utcnow()
    },
    
    # ============================================
    # PROFESSIONAL SERVICES
    # ============================================
    {
        "id": "prod_certification_pmp",
        "name": "PMP Certification Training",
        "category": "professional_courses",
        "subcategory": "project_management",
        "description": "Complete PMP certification preparation. PMI authorized training provider.",
        "price": 75000,
        "original_price": 95000,
        "currency": "LKR",
        "rating": 4.8,
        "reviews_count": 145,
        "in_stock": True,
        "stock_quantity": 20,
        "images": ["/static/products/pmp_certification.jpg"],
        "features": [
            "PMI authorized training",
            "35 contact hours certificate",
            "Exam preparation materials",
            "Online and classroom options",
            "Free exam simulator"
        ],
        "target_segments": ["government_employee", "young_professional", "entrepreneur"],
        "tags": ["professional_courses", "certification", "career_growth"],
        "featured": False,
        "active": True,
        "created": datetime.utcnow()
    },
    
    {
        "id": "prod_business_consultation",
        "name": "Business Startup Consultation Package",
        "category": "consultation",
        "subcategory": "business_advisory",
        "description": "Complete business startup guidance from registration to launch.",
        "price": 35000,
        "currency": "LKR",
        "rating": 4.7,
        "reviews_count": 89,
        "in_stock": True,
        "stock_quantity": 50,
        "images": ["/static/products/business_consultation.jpg"],
        "features": [
            "Business plan development",
            "Registration assistance",
            "Licensing guidance",
            "Financial planning",
            "3-month follow-up support"
        ],
        "target_segments": ["entrepreneur"],
        "tags": ["consultation", "business_services", "entrepreneur"],
        "featured": False,
        "active": True,
        "created": datetime.utcnow()
    },
    
    # ============================================
    # SENIOR CITIZEN SERVICES
    # ============================================
    {
        "id": "prod_health_insurance_senior",
        "name": "Senior Citizen Health Insurance",
        "category": "health_insurance",
        "subcategory": "insurance",
        "description": "Comprehensive health coverage for senior citizens. No medical test required.",
        "price": 15000,
        "currency": "LKR",
        "rating": 4.5,
        "reviews_count": 234,
        "in_stock": True,
        "stock_quantity": 100,
        "images": ["/static/products/health_insurance.jpg"],
        "features": [
            "Hospitalization coverage",
            "Outpatient benefits",
            "No medical test required",
            "Lifetime renewal",
            "Pre-existing conditions covered after 2 years"
        ],
        "target_segments": ["senior_citizen"],
        "tags": ["health_insurance", "senior_services"],
        "featured": False,
        "active": True,
        "created": datetime.utcnow()
    },
    
    # ============================================
    # STUDY MATERIALS
    # ============================================
    {
        "id": "prod_study_books_ol",
        "name": "Complete O/L Study Material Set (All Subjects)",
        "category": "study_materials",
        "subcategory": "textbooks",
        "description": "Complete set of study materials for O/L. Covers all subjects.",
        "price": 12500,
        "original_price": 15000,
        "currency": "LKR",
        "rating": 4.8,
        "reviews_count": 345,
        "in_stock": True,
        "stock_quantity": 50,
        "images": ["/static/products/ol_books.jpg"],
        "features": [
            "All 9 subjects covered",
            "Latest syllabus",
            "Past papers included",
            "Answer keys provided",
            "Free shipping"
        ],
        "target_segments": ["parent", "student"],
        "tags": ["study_materials", "education", "exam_prep"],
        "featured": False,
        "active": True,
        "created": datetime.utcnow()
    }
]

# Insert products
result = products_col.insert_many(products)
print(f"✅ Inserted {len(products)} products")

# Create indexes
products_col.create_index("id", unique=True)
products_col.create_index("category")
products_col.create_index("target_segments")
products_col.create_index("tags")
products_col.create_index("featured")
products_col.create_index([("price", 1)])
products_col.create_index([("rating", -1)])

print("✅ Created indexes")

# Print summary
print("\n" + "=" * 70)
print("📊 PRODUCT CATALOG SUMMARY")
print("=" * 70)

categories = {}
for product in products:
    cat = product['category']
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count} products")

print(f"\nTotal Products: {len(products)}")
print(f"Featured Products: {sum(1 for p in products if p['featured'])}")
print("=" * 70)
print("\n✅ Product database seeded successfully!")
print("\nNext: Run python seed_segments.py to test segmentation")