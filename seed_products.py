"""
Product Database Seeding
File: seed_products.py
Run: python seed_products.py
"""

import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["citizen_portal"]
products_col = db["products"]

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
        "features": [
            "3-year program",
            "Weekend classes",
            "Online support",
            "Government discount"
        ],
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
        "features": [
            "4-week intensive",
            "Expert trainers",
            "Mock tests",
            "Speaking practice"
        ],
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
        "features": [
            "Visa processing",
            "Job matching",
            "Document preparation",
            "Pre-departure orientation"
        ],
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
        "features": [
            "Intel i5 processor",
            "8GB RAM",
            "256GB SSD",
            "2-year warranty",
            "Government discount"
        ],
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
        "features": [
            "Pure cotton",
            "Handmade",
            "Traditional designs",
            "Multiple colors"
        ],
        "tags": ["saree", "batik", "handloom", "traditional", "fashion"],
        "target_segments": ["mid_career_family", "established_professional", "senior"],
        "in_stock": True,
        "delivery_options": ["delivery", "pickup"],
        "rating": 4.6,
        "reviews_count": 203,
        "created": datetime.utcnow()
    },
    {
        "id": "prod_ol_tuition_01",
        "name": "O/L Mathematics Tuition Classes",
        "category": "education",
        "subcategory": "tuition",
        "price": 3500,
        "currency": "LKR",
        "images": ["/static/store/ol_math.jpg"],
        "description": "Expert O/L Mathematics tuition by experienced teachers. Small batch sizes.",
        "features": [
            "Experienced teachers",
            "Small batches (15 students)",
            "Weekly practice papers",
            "Monthly assessments"
        ],
        "tags": ["ol", "mathematics", "tuition", "exams"],
        "target_segments": ["primary_school_parent", "secondary_school_parent"],
        "in_stock": True,
        "delivery_options": ["classroom", "online"],
        "rating": 4.8,
        "reviews_count": 267,
        "created": datetime.utcnow()
    }
]

# Insert products
products_col.insert_many(products)
print(f"✅ Seeded {len(products)} products")
print(f"Total products in database: {products_col.count_documents({})}")