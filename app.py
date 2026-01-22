import os
import json
import pathlib
from flask import Flask, jsonify, render_template, request, session, redirect, send_file
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from io import StringIO
import csv
from dotenv import load_dotenv
import bcrypt
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
from bson.objectid import ObjectId
import uuid
from io import StringIO
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId
import base64

import hashlib
# Try FAISS import
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Try ML recommendations import
try:
    from ml_recommendations import RecommendationEngine
    ML_AVAILABLE = True
    rec_engine = RecommendationEngine()
except ImportError:
    ML_AVAILABLE = False
    rec_engine = None
MERCHANT_ID="1233555"
MERCHANT_SECRET_ENCODED="MzkwNDE1MzcwMTEwMDAwNjYxNTYzNDcxMzgyNTAyMjkzMTI4NDAwMQ=="
MERCHANT_SECRET_BASE64="MzkwNDE1MzcwMTEwMDAwNjYxNTYzNDcxMzgyNTAyMjkzMTI4NDAwMQ=="
MERCHANT_SECRET = base64.b64decode(MERCHANT_SECRET_ENCODED).decode('utf-8')
print(f"✅ Using decoded merchant secret: {MERCHANT_SECRET}")

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")
CORS(app)
def serialize_mongo_doc(doc):
    """
    Convert MongoDB document to JSON-serializable format
    Converts ObjectId to string and datetime to ISO format
    """
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    
    if isinstance(doc, dict):
        serialized = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                serialized[key] = str(value)
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = serialize_mongo_doc(value)
            elif isinstance(value, list):
                serialized[key] = serialize_mongo_doc(value)
            else:
                serialized[key] = value
        return serialized
    
    return doc
# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
services_col = db["services"]
eng_col = db["engagements"]
admins_col = db["admins"]
categories_col = db["categories"]
officers_col = db["officers"]
ads_col = db["ads"]
users_col = db["users"]
products_col = db["products"]
orders_col = db["orders"]
payments_col = db["payments"]
training_programs_col = db["training_programs"]
enrollments_col = db["enrollments"]
recommendations_col = db["recommendations"]
segments_col = db["user_segments"]

# Embedding model (lazy-init)
EMBED_MODEL = None

# Paths
INDEX_PATH = pathlib.Path("./data/faiss.index")
META_PATH = pathlib.Path("./data/faiss_meta.json")
EMBED_PATH = pathlib.Path("./data/embeddings.npy")

# Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None

def get_utc_now():
    """Get current UTC time (Python 3.13 compatible)"""
    return datetime.now(timezone.utc)
def get_embedding_model():
    """Lazy load embedding model"""
    global EMBED_MODEL
    if EMBED_MODEL is None:
        model_name = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        print(f"Loading embedding model: {model_name}")
        EMBED_MODEL = SentenceTransformer(model_name)
    return EMBED_MODEL

# --- Helpers ---
def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "unauthorized"}), 401
        return fn(*a, **kw)
    return wrapper

# Replace the UserSegmentationEngine class in app.py with this fixed version:

class UserSegmentationEngine:
    """Intelligent user segmentation based on profile data"""
    
    @staticmethod
    def segment_user(user_profile: dict) -> dict:
        """
        Segment user based on comprehensive profile data
        Returns segment info with recommendations
        """
        # FIXED: Safely handle None values
        age = user_profile.get('age', 0)
        job = (user_profile.get('job') or '').lower()  # Handle None safely
        education = user_profile.get('extended_profile', {}).get('education', {})
        family = user_profile.get('extended_profile', {}).get('family', {})
        career = user_profile.get('extended_profile', {}).get('career', {})
        
        segments = []
        priorities = []
        
        # 1. Government Employee Segment
        if 'government' in job or 'public service' in job or 'civil servant' in job:
            segments.append('government_employee')
            
            qualification = (education.get('highest_qualification') or '').lower()
            if qualification and 'degree' not in qualification and 'bachelor' not in qualification:
                priorities.append({
                    'type': 'degree_program',
                    'reason': 'Government employee without degree',
                    'recommended_services': ['degree_programs', 'professional_development'],
                    'priority': 'high'
                })
        
        # 2. Parent Segment
        children = family.get('children', [])
        if children or family.get('dependents', 0) > 0:
            segments.append('parent')
            
            children_ages = family.get('children_ages', [])
            for child_age in children_ages:
                if 5 <= child_age <= 18:
                    priorities.append({
                        'type': 'child_education',
                        'reason': f'Child aged {child_age} - school age',
                        'recommended_services': ['tuition', 'exam_prep', 'school_registration'],
                        'priority': 'high'
                    })
        
        # 3. Young Professional Segment
        if age and 22 <= age <= 35:  # Check age exists
            segments.append('young_professional')
            priorities.append({
                'type': 'career_growth',
                'reason': 'Young professional age group',
                'recommended_services': ['ielts_courses', 'overseas_jobs', 'skill_training'],
                'priority': 'medium'
            })
        
        # 4. Senior Citizen Segment
        if age and age >= 60:
            segments.append('senior_citizen')
            priorities.append({
                'type': 'senior_services',
                'reason': 'Senior citizen benefits',
                'recommended_services': ['pension_services', 'health_checkups', 'social_welfare'],
                'priority': 'medium'
            })
        
        # 5. Student Segment
        if (age and 15 <= age <= 25) or 'student' in job:
            segments.append('student')
            priorities.append({
                'type': 'student_services',
                'reason': 'Student age group',
                'recommended_services': ['exam_prep', 'scholarships', 'career_guidance'],
                'priority': 'medium'
            })
        
        # 6. Entrepreneur/Business Owner
        if 'business' in job or 'entrepreneur' in job or 'owner' in job:
            segments.append('entrepreneur')
            priorities.append({
                'type': 'business_services',
                'reason': 'Business owner/entrepreneur',
                'recommended_services': ['business_registration', 'loans', 'export_services'],
                'priority': 'high'
            })
        
        return {
            'segments': segments,
            'primary_segment': segments[0] if segments else 'general_citizen',
            'priorities': priorities,
            'profile_completeness': UserSegmentationEngine._calculate_completeness(user_profile)
        }
    
    @staticmethod
    def _calculate_completeness(profile: dict) -> float:
        """Calculate profile completeness percentage"""
        fields = ['age', 'job', 'location', 'phone']
        extended_fields = ['education', 'family', 'career', 'interests']
        
        # Safely check if fields exist and are not None/empty
        basic_score = sum(1 for f in fields if profile.get(f)) / len(fields) * 50
        
        extended_profile = profile.get('extended_profile', {})
        extended_score = sum(1 for f in extended_fields if extended_profile.get(f)) / len(extended_fields) * 50
        
        return round(basic_score + extended_score, 1)


class ProductRecommendationEngine:
    """AI-powered product recommendations based on user segments"""
    
    @staticmethod
    def get_recommendations(user_id: str, segment_info: dict) -> list:
        """Get personalized product recommendations"""
        segments = segment_info.get('segments', [])
        priorities = segment_info.get('priorities', [])
        
        recommendations = []
        
        segment_products = {
            'government_employee': ['degree_programs', 'professional_courses', 'certification'],
            'parent': ['tuition', 'exam_prep', 'school_supplies', 'educational_toys'],
            'young_professional': ['ielts_courses', 'overseas_jobs', 'laptops', 'career_coaching'],
            'senior_citizen': ['health_insurance', 'medical_devices', 'pension_planning'],
            'student': ['study_materials', 'exam_prep', 'scholarships', 'laptops'],
            'entrepreneur': ['business_software', 'consultation', 'loans', 'marketing_services']
        }
        
        for segment in segments:
            categories = segment_products.get(segment, [])
            
            products = list(products_col.find({
                'category': {'$in': categories},
                'active': True
            }).limit(5))
            
            for product in products:
                product['_id'] = str(product['_id'])
                product['recommendation_reason'] = f"Recommended for {segment.replace('_', ' ')}"
                recommendations.append(product)
        
        for priority in priorities:
            if priority['priority'] == 'high':
                services = priority['recommended_services']
                products = list(products_col.find({
                    'tags': {'$in': services},
                    'active': True
                }).limit(3))
                
                for product in products:
                    product['_id'] = str(product['_id'])
                    product['recommendation_reason'] = priority['reason']
                    product['priority'] = 'high'
                    recommendations.append(product)
        
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            rec_id = rec.get('id', rec.get('_id'))
            if rec_id not in seen:
                seen.add(rec_id)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]

# ============================================
# PUBLIC PAGES
# ============================================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot_page():
    """AI Chatbot Interface - requires user login"""
    if not session.get("user_logged_in"):
        return redirect("/user/login")
    return render_template("chatbot.html")

@app.route("/admin")
def admin_page():
    """Admin dashboard page - requires login"""
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")
    return render_template("admin.html")

@app.route("/dashboard")
def dashboard_page():
    """User Dashboard - Main page after login"""
    if not session.get("user_logged_in"):
        return redirect("/user/login")
    return render_template("chatbot_dashboard.html")

@app.route("/training")
def training_page():
    """Training programs page"""
    if not session.get("user_logged_in"):
        return redirect("/user/login")
    return render_template("training.html")

@app.route("/store")
def store_page():
    """Public store frontend"""
    return render_template("store.html")

@app.route("/profile/complete")
def profile_complete_page():
    if not session.get("user_logged_in"):
        return redirect("/user/login")
    return render_template("profile_complete.html")

@app.route("/recommendations")
def recommendations_page():
    if not session.get("user_logged_in"):
        return redirect("/user/login")
    return render_template("recommendations.html")

@app.route("/admin/segment-analytics")
def admin_segment_analytics():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")
    return render_template("admin_segment_analytics.html")

@app.route("/my-training")
def my_training_page():
    """My Training page - shows user enrollments"""
    if not session.get("user_logged_in"):
        return redirect("/user/login")
    return render_template("training.html")

# ============================================
# USER PROFILE & SEGMENTATION API
# ============================================
@app.route("/api/user/profile", methods=["GET"])
def get_user_profile():
    """Get complete user profile"""
    if not session.get("user_logged_in"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get("user_id")
    user = users_col.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    
    if user:
        user['_id'] = str(user['_id'])
        return jsonify(user)
    
    return jsonify({"error": "User not found"}), 404

"""
@app.route("/api/user/profile/complete", methods=["POST"])
def complete_user_profile():
    
    if not session.get("user_logged_in"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get("user_id")
    data = request.json or {}
    
    extended_profile = {
        "family": {
            "marital_status": data.get("marital_status"),
            "children": data.get("children", []),
            "children_ages": data.get("children_ages", []),
            "children_education": data.get("children_education", []),
            "dependents": data.get("dependents", 0)
        },
        "education": {
            "highest_qualification": data.get("highest_qualification"),
            "institution": data.get("institution"),
            "year_graduated": data.get("year_graduated"),
            "field_of_study": data.get("field_of_study")
        },
        "career": {
            "current_job": data.get("current_job"),
            "years_experience": data.get("years_experience"),
            "skills": data.get("skills", []),
            "career_goals": data.get("career_goals", [])
        },
        "interests": {
            "hobbies": data.get("hobbies", []),
            "learning_interests": data.get("learning_interests", []),
            "service_preferences": data.get("service_preferences", [])
        },
        "consent": {
            "marketing_emails": data.get("marketing_emails", False),
            "personalized_ads": data.get("personalized_ads", False),
            "data_analytics": data.get("data_analytics", False),
            "updated": get_utc_now()
        }
    }
    
    users_col.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "extended_profile": extended_profile,
                "profile_completed": True,
                "updated": get_utc_now()
            }
        }
    )
    
    user = users_col.find_one({"_id": ObjectId(user_id)})
    segment_info = UserSegmentationEngine.segment_user(user)
    
    segments_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                **segment_info,
                "updated": get_utc_now()
            }
        },
        upsert=True
    )
    
    return jsonify({
        "status": "success",
        "message": "Profile completed successfully",
        "segment_info": segment_info
    })

"""
# In your main Flask app file (likely app.py or routes.py)

@app.route('/api/user/profile/complete', methods=['POST'])
def complete_profile():
    try:
        data = request.get_json()
        user_id = session.get('user_id')  # or however you track logged-in users
        
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Update user profile in MongoDB
        result = users_col.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'gender': data.get('gender'),
                    'marital_status': data.get('marital_status'),
                    'children_count': data.get('children_count', 0),
                    'children_ages': data.get('children_ages', []),
                    'dependents': data.get('dependents', 0),
                    'years_experience': data.get('years_experience'),
                    'highest_qualification': data.get('highest_qualification'),
                    'field_of_study': data.get('field_of_study'),
                    'institution': data.get('institution'),
                    'year_graduated': data.get('year_graduated'),
                    'skills': data.get('skills', []),
                    'career_goals': data.get('career_goals'),
                    'hobbies': data.get('hobbies', []),
                    'learning_interests': data.get('learning_interests', []),
                    'service_preferences': data.get('service_preferences', []),
                    'marketing_emails': data.get('marketing_emails', False),
                    'personalized_ads': data.get('personalized_ads', False),
                    'data_analytics': data.get('data_analytics', True),
                    'profile_completed': True,
                    'updated': datetime.now()
                }
            }
        )
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({'error': str(e)}), 500
@app.route("/api/user/recommendations", methods=["GET"])
def get_user_recommendations():
    """Get personalized recommendations for user"""
    if not session.get("user_logged_in"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get("user_id")
    
    segment_info = segments_col.find_one({"user_id": user_id})
    
    if not segment_info:
        user = users_col.find_one({"_id": ObjectId(user_id)})
        segment_info = UserSegmentationEngine.segment_user(user)
        
        segments_col.update_one(
            {"user_id": user_id},
            {"$set": {**segment_info, "updated": get_utc_now()}},
            upsert=True
        )
    
    recommendations = ProductRecommendationEngine.get_recommendations(user_id, segment_info)
    
    eng_col.insert_one({
        "user_id": user_id,
        "type": "recommendation_view",
        "recommendations": [r.get('id', r.get('_id')) for r in recommendations],
        "timestamp": get_utc_now()
    })
    
    return jsonify({
        "recommendations": recommendations,
        "segment_info": {
            "segments": segment_info.get('segments', []),
            "primary_segment": segment_info.get('primary_segment'),
            "profile_completeness": segment_info.get('profile_completeness', 0)
        }
    })


@app.route("/api/user/segment", methods=["GET"])
def get_user_segment():
    """Get user's segment information"""
    if not session.get("user_logged_in"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get("user_id")
    segment_info = segments_col.find_one({"user_id": user_id}, {"_id": 0})
    
    if not segment_info:
        return jsonify({"message": "No segmentation data yet"}), 404
    
    return jsonify(segment_info)

# ============================================
# USER AUTHENTICATION ROUTES
# ============================================
@app.route("/user/login", methods=["GET"])
def user_login_page():
    """Display user login page"""
    if session.get("user_logged_in"):
        return redirect("/dashboard")
    return render_template("user_login.html")

@app.route("/user/register", methods=["GET"])
def user_register_page():
    """Display user registration page"""
    if session.get("user_logged_in"):
        return redirect("/dashboard")
    return render_template("user_register.html")

@app.route("/api/user/login", methods=["POST"])
def user_login_api():
    """User login API endpoint"""
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        user = users_col.find_one({"email": email})
        if user:
            stored_pwd = user.get("password")
            
            try:
                if isinstance(stored_pwd, str):
                    stored_pwd = stored_pwd.encode('utf-8')
                is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_pwd)
            except:
                is_valid = (stored_pwd == password)
            
            if is_valid:
                session["user_logged_in"] = True
                session["user_id"] = str(user["_id"])
                session["user_email"] = email
                session["user_name"] = user.get("full_name", "User")
                session["user_age"] = user.get("age")
                session["user_job"] = user.get("job")
                session["user_language"] = user.get("language", "en")
                
                return jsonify({
                    "status": "success",
                    "redirect": "/dashboard"
                })
        
        return jsonify({"error": "Invalid email or password"}), 401
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# FIXED REGISTRATION ENDPOINT ONLY
# Replace your existing @app.route("/api/user/register", methods=["POST"]) function with this

@app.route("/api/user/register", methods=["POST"])
def user_register_api():
    """Enhanced user registration with complete profile - handles optional fields"""
    try:
        data = request.json
        
        # Helper function to safely get and strip string values
        def safe_strip(value, default=""):
            """Safely strip a value, returning default if None or empty"""
            if value is None:
                return default
            return str(value).strip() if str(value).strip() else default
        
        # Helper function to safely get integer values
        def safe_int(value, default=0):
            """Safely convert to int, returning default if invalid"""
            try:
                return int(value) if value else default
            except (ValueError, TypeError):
                return default
        
        # MANDATORY FIELDS - validate first
        email = safe_strip(data.get("email"), "")
        password = data.get("password", "")
        terms = data.get("terms", False)
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        if not terms:
            return jsonify({"error": "You must accept the Terms and Conditions"}), 400
        
        # Check if email already registered
        if users_col.find_one({"email": email}):
            return jsonify({"error": "Email already registered"}), 400
        
        # Hash password
        hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Parse children ages - handle both array and comma-separated string
        children_ages = data.get("children_ages", [])
        if isinstance(children_ages, str):
            children_ages = [
                int(age.strip()) 
                for age in children_ages.split(',') 
                if age.strip().isdigit()
            ]
        elif not isinstance(children_ages, list):
            children_ages = []
        
        # Parse skills - handle both array and comma-separated string
        skills = data.get("skills", [])
        if isinstance(skills, str):
            skills = [
                skill.strip() 
                for skill in skills.split(',') 
                if skill.strip()
            ]
        elif not isinstance(skills, list):
            skills = []
        
        # Create user document with complete profile
        user_doc = {
            # MANDATORY Basic Information
            "email": email,
            "password": hashed_pwd,
            
            # OPTIONAL Basic Information
            "full_name": safe_strip(data.get("full_name"), None),
            "phone": safe_strip(data.get("phone"), None),
            
            # OPTIONAL Demographics
            "age": safe_int(data.get("age"), None),
            "gender": data.get("gender") if data.get("gender") else None,
            "occupation": safe_strip(data.get("occupation"), None),
            "district": data.get("district") if data.get("district") else None,
            "marital_status": data.get("marital_status") if data.get("marital_status") else None,
            "children_count": safe_int(data.get("children_count"), 0),
            "children_ages": children_ages,
            "dependents": safe_int(data.get("dependents"), 0),
            
            # Legacy fields for backward compatibility
            "location": safe_strip(data.get("location"), None),
            "language": data.get("language", "en"),
            "job": safe_strip(data.get("job") or data.get("occupation"), None),
            
            # OPTIONAL Education & Career
            "years_experience": safe_int(data.get("years_experience"), None),
            "highest_qualification": data.get("highest_qualification") if data.get("highest_qualification") else None,
            "field_of_study": safe_strip(data.get("field_of_study"), None),
            "institution": safe_strip(data.get("institution"), None),
            "year_graduated": safe_int(data.get("year_graduated"), None),
            "skills": skills,
            "career_goals": safe_strip(data.get("career_goals"), None),
            
            # OPTIONAL Interests
            "hobbies": data.get("hobbies", []) if isinstance(data.get("hobbies"), list) else [],
            "learning_interests": data.get("learning_interests", []) if isinstance(data.get("learning_interests"), list) else [],
            "service_preferences": data.get("service_preferences", []) if isinstance(data.get("service_preferences"), list) else [],
            
            # Consent (terms is mandatory, others optional)
            "terms_accepted": True,
            "marketing_emails": data.get("marketing_emails", False),
            "personalized_ads": data.get("personalized_ads", False),
            "data_analytics": data.get("data_analytics", True),
            
            # Metadata
            "created": get_utc_now(),
            "updated": get_utc_now(),
            "profile_completed": False
        }
        
        # Insert user
        result = users_col.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Immediately segment the user (even with minimal data)
        try:
            segment_info = UserSegmentationEngine.segment_user(user_doc)
            
            # Store segmentation
            segments_col.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        **segment_info,
                        "user_id": user_id,
                        "created": get_utc_now(),
                        "updated": get_utc_now()
                    }
                },
                upsert=True
            )
            
            # Store extended profile in users collection
            extended_profile = {
                "family": {
                    "marital_status": user_doc.get("marital_status"),
                    "children": children_ages,
                    "children_ages": children_ages,
                    "dependents": user_doc.get("dependents", 0)
                },
                "education": {
                    "highest_qualification": user_doc.get("highest_qualification"),
                    "institution": user_doc.get("institution"),
                    "year_graduated": user_doc.get("year_graduated"),
                    "field_of_study": user_doc.get("field_of_study")
                },
                "career": {
                    "current_job": user_doc.get("job") or user_doc.get("occupation"),
                    "years_experience": user_doc.get("years_experience"),
                    "skills": skills,
                    "goals": user_doc.get("career_goals")
                },
                "interests": {
                    "hobbies": user_doc.get("hobbies", []),
                    "learning": user_doc.get("learning_interests", []),
                    "services": user_doc.get("service_preferences", [])
                }
            }
            
            users_col.update_one(
                {"_id": result.inserted_id},
                {"$set": {"extended_profile": extended_profile}}
            )
            
        except Exception as segment_err:
            print(f"Segmentation error (non-critical): {segment_err}")
            # Don't fail registration if segmentation fails
        
        return jsonify({
            "message": "Registration successful",
            "user_id": user_id,
            "profile_completed": user_doc["profile_completed"]
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Registration failed. Please try again."}), 500

@app.route("/api/user/complete-profile", methods=["POST"])
def complete_user_profile():
    """Allow users to complete their profile after initial registration"""
    try:
        # Check if user is logged in (implement your auth check here)
        if 'user_id' not in session:
            return jsonify({"error": "Not authenticated"}), 401
        
        user_id = session['user_id']
        data = request.json
        
        # Helper functions (same as above)
        def safe_strip(value, default=""):
            if value is None:
                return default
            return str(value).strip() if str(value).strip() else default
        
        def safe_int(value, default=0):
            try:
                return int(value) if value else default
            except (ValueError, TypeError):
                return default
        
        # Parse arrays
        children_ages = data.get("children_ages", [])
        if isinstance(children_ages, str):
            children_ages = [int(age.strip()) for age in children_ages.split(',') if age.strip().isdigit()]
        
        skills = data.get("skills", [])
        if isinstance(skills, str):
            skills = [skill.strip() for skill in skills.split(',') if skill.strip()]
        
        # Update fields
        update_data = {
            "full_name": safe_strip(data.get("full_name"), None),
            "phone": safe_strip(data.get("phone"), None),
            "age": safe_int(data.get("age"), None),
            "gender": data.get("gender"),
            "occupation": safe_strip(data.get("occupation"), None),
            "district": data.get("district"),
            "marital_status": data.get("marital_status"),
            "children_count": safe_int(data.get("children_count"), 0),
            "children_ages": children_ages,
            "dependents": safe_int(data.get("dependents"), 0),
            "years_experience": safe_int(data.get("years_experience"), None),
            "highest_qualification": data.get("highest_qualification"),
            "field_of_study": safe_strip(data.get("field_of_study"), None),
            "institution": safe_strip(data.get("institution"), None),
            "year_graduated": safe_int(data.get("year_graduated"), None),
            "skills": skills,
            "career_goals": safe_strip(data.get("career_goals"), None),
            "hobbies": data.get("hobbies", []),
            "learning_interests": data.get("learning_interests", []),
            "service_preferences": data.get("service_preferences", []),
            "profile_completed": True,
            "updated": get_utc_now()
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Update user
        users_col.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        return jsonify({"message": "Profile updated successfully"}), 200
        
    except Exception as e:
        print(f"Profile update error: {str(e)}")
        return jsonify({"error": "Failed to update profile"}), 500



@app.route("/api/user/logout", methods=["POST"])
def user_logout():
    """User logout"""
    session.clear()
    return jsonify({"status": "logged out"})

@app.route("/api/user/stats")
def get_user_stats():
    """Get user activity statistics"""
    if not session.get("user_logged_in"):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session.get("user_id")
        
        training_count = enrollments_col.count_documents({
            "user_id": user_id,
            "status": "enrolled"
        })
        
        orders_count = orders_col.count_documents({
            "user_id": user_id
        })
        
        services_count = eng_col.count_documents({
            "user_id": user_id
        })
        
        return jsonify({
            "training_enrolled": training_count,
            "orders": orders_count,
            "services_used": services_count
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# ADMIN AUTHENTICATION ROUTES
# ============================================
@app.route("/admin/login", methods=["GET"])
def admin_login_page():
    """Display admin login page"""
    if session.get("admin_logged_in"):
        return redirect("/admin")
    return render_template("admin_login.html")

@app.route("/api/admin/login", methods=["POST"])
def admin_login_api():
    """Admin login API endpoint"""
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password", "")
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        admin = admins_col.find_one({"username": username})
        if admin:
            stored_pwd = admin.get("password")
            
            try:
                if isinstance(stored_pwd, str):
                    stored_pwd = stored_pwd.encode('utf-8')
                is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_pwd)
            except:
                is_valid = (stored_pwd == password)
            
            if is_valid:
                session["admin_logged_in"] = True
                session["admin_user"] = username
                return jsonify({
                    "status": "success",
                    "redirect": "/admin"
                })
        
        return jsonify({"error": "Invalid username or password"}), 401
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    session.clear()
    return jsonify({"status": "logged out"})
@app.route("/api/admin/users/stats", methods=["GET"])
@admin_required
def get_users_stats():
    """Get user statistics"""
    try:
        # Total users
        total_users = users_col.count_documents({})
        
        # Active users (last 30 days)
        thirty_days_ago = get_utc_now() - timedelta(days=30)
        active_users = users_col.count_documents({
            "updated": {"$gte": thirty_days_ago}
        })
        
        # New users (last 7 days)
        seven_days_ago = get_utc_now() - timedelta(days=7)
        new_users = users_col.count_documents({
            "created": {"$gte": seven_days_ago}
        })
        
        return jsonify({
            "total_users": total_users,
            "active_users": active_users,
            "new_users_week": new_users
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ============================================
# TRAINING PROGRAMS API
# ============================================

@app.route("/api/training-programs")
def get_training_programs():
    """Get all active training programs"""
    category = request.args.get("category")
    level = request.args.get("level")
    free_only = request.args.get("free")
    
    query = {"active": True}
    
    if category:
        query["category"] = category
    if level:
        query["level"] = level
    if free_only == "true":
        query["free"] = True
    
    programs = list(training_programs_col.find(query, {"_id": 0}).sort("start_date", 1))
    
    # Calculate enrollment statistics for each program
    for program in programs:
        current = program.get("current_enrollments", 0)
        max_participants = program.get("max_participants", 0)
        
        program["enrollment_percentage"] = (
            round((current / max_participants) * 100) if max_participants > 0 else 0
        )
        program["spots_remaining"] = max_participants - current
    
    return jsonify(programs)
@app.route("/api/training-programs/<program_id>")
def get_training_program(program_id):
    """Get single training program details with enrollment stats"""
    try:
        program = training_programs_col.find_one({"id": program_id}, {"_id": 0})
        
        if not program:
            return jsonify({"error": "Program not found"}), 404
        
        # Calculate enrollment statistics
        current = program.get("current_enrollments", 0)
        max_participants = program.get("max_participants", 0)
        
        program["enrollment_percentage"] = (
            round((current / max_participants) * 100) if max_participants > 0 else 0
        )
        program["spots_remaining"] = max_participants - current
        
        # Check if user is enrolled (if logged in)
        user_id = session.get("user_id")
        if user_id:
            enrollment = enrollments_col.find_one({
                "user_id": user_id,
                "program_id": program_id
            })
            program["user_enrolled"] = enrollment is not None
        else:
            program["user_enrolled"] = False
        
        return jsonify(program), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/training-programs/<program_id>/enroll", methods=["POST"])
def enroll_in_program(program_id):
    """Enroll user in training program"""
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Please log in to enroll"}), 401
    
    program = training_programs_col.find_one({"id": program_id})
    
    if not program:
        return jsonify({"error": "Program not found"}), 404
    
    if not program.get("active"):
        return jsonify({"error": "Program is not active"}), 400
    
    # Check if enrollment is open
    if not program.get("enrollment_open", False):
        return jsonify({"error": "Enrollment is currently closed for this program"}), 400
    
    # Check if program is full
    current = program.get("current_enrollments", 0)
    max_participants = program.get("max_participants", 0)
    
    if current >= max_participants:
        return jsonify({"error": "Program is full"}), 400
    
    # Check if already enrolled
    existing = enrollments_col.find_one({
        "user_id": user_id,
        "program_id": program_id
    })
    
    if existing:
        return jsonify({"error": "Already enrolled in this program"}), 400
    
    # Create enrollment
    enrollment = {
        "user_id": user_id,
        "program_id": program_id,
        "status": "enrolled",
        "enrolled_date": datetime.utcnow(),
        "completion_status": None,
        "progress": 0
    }
    
    enrollments_col.insert_one(enrollment)
    
    # Increment enrollment count
    result = training_programs_col.update_one(
        {"id": program_id},
        {"$inc": {"current_enrollments": 1}}
    )
    
    # Log engagement (if you have this collection)
    try:
        eng_col.insert_one({
            "user_id": user_id,
            "type": "training_enrollment",
            "program_id": program_id,
            "program_name": program.get("title", {}).get("en"),
            "timestamp": datetime.utcnow()
        })
    except:
        pass  # Engagement logging is optional
    
    # Get updated program data
    updated_program = training_programs_col.find_one({"id": program_id}, {"_id": 0})
    current = updated_program.get("current_enrollments", 0)
    max_participants = updated_program.get("max_participants", 0)
    
    return jsonify({
        "status": "success",
        "message": "Successfully enrolled in program",
        "current_enrollments": current,
        "enrollment_percentage": round((current / max_participants) * 100) if max_participants > 0 else 0,
        "spots_remaining": max_participants - current
    })
@app.route("/api/training-programs/<program_id>/unenroll", methods=["POST"])
def unenroll_from_program(program_id):
    """Unenroll user from training program"""
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    
    result = enrollments_col.delete_one({
        "user_id": user_id,
        "program_id": program_id
    })
    
    if result.deleted_count > 0:
        # Decrement enrollment count
        training_programs_col.update_one(
            {"id": program_id},
            {"$inc": {"current_enrollments": -1}}
        )
        
        # Get updated program data
        updated_program = training_programs_col.find_one({"id": program_id}, {"_id": 0})
        current = updated_program.get("current_enrollments", 0)
        max_participants = updated_program.get("max_participants", 0)
        
        return jsonify({
            "status": "success", 
            "message": "Unenrolled from program",
            "current_enrollments": current,
            "enrollment_percentage": round((current / max_participants) * 100) if max_participants > 0 else 0,
            "spots_remaining": max_participants - current
        })
    else:
        return jsonify({"error": "Not enrolled in this program"}), 404


@app.route("/api/my-training")
def get_my_training():
    """Get user's enrolled training programs"""
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    
    enrollments = list(enrollments_col.find({"user_id": user_id}, {"_id": 0}))
    
    for enrollment in enrollments:
        program = training_programs_col.find_one(
            {"id": enrollment["program_id"]},
            {"_id": 0}
        )
        if program:
            enrollment["program"] = program
            enrollment["program"]["user_enrolled"] = True
    
    return jsonify(enrollments)

# ============================================
# SERVICES & CATEGORIES API
# ============================================
@app.route("/api/services")
def get_services():
    try:
        docs = list(services_col.find({}))
        for doc in docs:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        return jsonify(docs)
    except Exception as e:
        print(f"Error fetching services: {e}")
        return jsonify([]), 500

@app.route("/api/service/<service_id>")
def get_service(service_id):
    doc = services_col.find_one({"id": service_id}, {"_id": 0})
    return jsonify(doc or {})

@app.route("/api/categories")
def get_categories():
    """Get all service categories"""
    cats = list(categories_col.find({}, {"_id": 0}))
    
    if not cats:
        pipeline = [
            {"$project": {"id": 1, "name": 1, "category": 1, "subservices": 1}},
            {"$group": {
                "_id": "$category",
                "ministries": {"$push": {"id": "$id", "name": "$name"}}
            }}
        ]
        try:
            groups = list(services_col.aggregate(pipeline))
            cats = [{
                "id": g["_id"] or "uncategorized",
                "name": {"en": g["_id"] or "Uncategorized"},
                "ministries": g["ministries"]
            } for g in groups]
        except Exception:
            cats = []
    
    return jsonify(cats)

@app.route("/api/officers")
def get_officers():
    """Get all government officers"""
    ministry_id = request.args.get("ministry_id")
    query = {"ministry_id": ministry_id} if ministry_id else {}
    officers = list(officers_col.find(query, {"_id": 0}))
    return jsonify(officers)

@app.route("/api/ads")
def get_ads():
    """Get active ads and announcements"""
    ads = list(ads_col.find({"active": True}, {"_id": 0}).sort("priority", 1))
    return jsonify(ads)

# ============================================
# PROFILE & ENGAGEMENT
# ============================================
@app.route("/api/profile/extended", methods=["POST"])
def extended_profile():
    """Enhanced user profile with family, career, and interests"""
    payload = request.json or {}
    profile_id = payload.get("profile_id") or session.get("user_id")
    
    if not profile_id:
        return jsonify({"error": "profile_id required"}), 400
    
    try:
        extended_data = {
            "family": {
                "marital_status": payload.get("marital_status"),
                "children": payload.get("children", []),
                "children_ages": payload.get("children_ages", []),
                "children_education": payload.get("children_education", []),
                "dependents": payload.get("dependents", 0)
            },
            "education": {
                "highest_qualification": payload.get("highest_qualification"),
                "institution": payload.get("institution"),
                "year_graduated": payload.get("year_graduated"),
                "field_of_study": payload.get("field_of_study")
            },
            "career": {
                "current_job": payload.get("current_job"),
                "years_experience": payload.get("years_experience"),
                "skills": payload.get("skills", []),
                "career_goals": payload.get("career_goals", [])
            },
            "interests": {
                "hobbies": payload.get("hobbies", []),
                "learning_interests": payload.get("learning_interests", []),
                "service_preferences": payload.get("service_preferences", [])
            },
            "consent": {
                "marketing_emails": payload.get("marketing_emails", False),
                "personalized_ads": payload.get("personalized_ads", False),
                "data_analytics": payload.get("data_analytics", False),
                "updated": get_utc_now()
            }
        }
        
        users_col.update_one(
            {"_id": ObjectId(profile_id)},
            {"$set": {"extended_profile": extended_data, "updated": get_utc_now()}}
        )
        
        return jsonify({"status": "ok", "message": "Extended profile saved"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/engagement", methods=["POST"])
def log_engagement():
    """Log engagement with proper user profile data"""
    payload = request.json or {}
    
    user_id = payload.get("user_id") or session.get("user_id")
    age = payload.get("age")
    if age is None:
        age = session.get("user_age")
    job = payload.get("job") or session.get("user_job")
    question = payload.get("question_clicked")
    service = payload.get("service")
    
    # Validate age
    if age is not None:
        try:
            age = int(age)
        except (ValueError, TypeError):
            age = None
    
    # Only log if at least one meaningful field has data
    if not any([
        user_id,
        age is not None,
        job and job != "Unknown",
        question and question != "Unknown",
        service and service != "Unknown"
    ]):
        # Skip logging empty engagements
        return jsonify({"status": "skipped", "reason": "no meaningful data"})
    
    doc = {
        "user_id": user_id,
        "age": age,
        "job": job,
        "desires": payload.get("desires") or [],
        "question_clicked": question,
        "service": service,
        "language": payload.get("language") or session.get("user_language", "en"),
        "timestamp": get_utc_now(),
        "chat_type": payload.get("chat_type", "standard")
    }
    
    eng_col.insert_one(doc)
    return jsonify({"status": "ok"})
# CLEANUP SCRIPT: Remove existing N/A entries
@app.route("/api/admin/cleanup-engagements", methods=["POST"])
@admin_required
def cleanup_engagements():
    """Remove engagement entries with N/A values"""
    try:
        # Delete entries where ALL key fields are N/A or missing
        result = eng_col.delete_many({
            "$or": [
                {"question_clicked": {"$in": [None, "N/A", ""]}},
                {"service": {"$in": [None, "N/A", ""]}},
                {
                    "$and": [
                        {"question_clicked": {"$exists": False}},
                        {"service": {"$exists": False}}
                    ]
                }
            ]
        })
        
        return jsonify({
            "status": "success",
            "deleted_count": result.deleted_count,
            "message": f"Removed {result.deleted_count} incomplete engagement entries"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/profile/step", methods=["POST"])
def profile_step():
    """Save progressive profile data"""
    payload = request.json or {}
    profile_id = payload.get("profile_id")
    email = payload.get("email")
    step = payload.get("step", "unknown")
    data = payload.get("data", {})
    
    try:
        if profile_id:
            users_col.update_one(
                {"_id": profile_id},
                {"$set": {f"profile.{step}": data, "updated": get_utc_now()}},
                upsert=True
            )
            return jsonify({"status": "ok", "profile_id": profile_id})
        
        elif email:
            result = users_col.find_one_and_update(
                {"email": email},
                {"$set": {f"profile.{step}": data, "updated": get_utc_now()}},
                upsert=True,
                return_document=True
            )
            return jsonify({"status": "ok", "profile_id": str(result["_id"])})
        
        else:
            result = users_col.insert_one({
                "profile": {step: data},
                "created": get_utc_now(),
                "anonymous": True
            })
            return jsonify({"status": "ok", "profile_id": str(result.inserted_id)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# STORE API
# ============================================
@app.route("/api/store/products")
def get_store_products():
    """Get product catalog with filtering"""
    category = request.args.get("category")
    subcategory = request.args.get("subcategory")
    tags = request.args.get("tags", "").split(",") if request.args.get("tags") else []
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    
    query = {"in_stock": True}
    
    if category:
        query["category"] = category
    if subcategory:
        query["subcategory"] = subcategory
    if tags and tags[0]:
        query["tags"] = {"$in": tags}
    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price
    
    products = list(products_col.find(query, {"_id": 0}).limit(50))
    return jsonify(products)

@app.route("/api/store/categories")
def get_store_categories():
    """Get store categories and subcategories"""
    categories = products_col.distinct("category")
    subcategories = {}
    
    for cat in categories:
        subcategories[cat] = products_col.distinct("subcategory", {"category": cat})
    
    return jsonify({
        "categories": categories,
        "subcategories": subcategories
    })

@app.route("/api/store/products/recommended", methods=["GET"])
def get_recommended_products():
    """Get recommended products for current user"""
    user_id = session.get("user_id")
    
    if user_id:
        segment_info = segments_col.find_one({"user_id": user_id})
        if segment_info:
            recommendations = ProductRecommendationEngine.get_recommendations(user_id, segment_info)
            return jsonify(recommendations)
    
    popular = list(products_col.find({"featured": True}).limit(10))
    for p in popular:
        p['_id'] = str(p['_id'])
    
    return jsonify(popular)

@app.route("/api/store/products/segment/<segment>", methods=["GET"])
def get_products_by_segment(segment):
    """Get products for specific segment"""
    segment_products = {
        'government_employee': ['degree_programs', 'professional_courses'],
        'parent': ['tuition', 'exam_prep', 'school_supplies'],
        'young_professional': ['ielts_courses', 'overseas_jobs', 'laptops'],
        'senior_citizen': ['health_insurance', 'medical_devices'],
        'student': ['study_materials', 'exam_prep', 'laptops'],
        'entrepreneur': ['business_software', 'consultation', 'loans']
    }
    
    categories = segment_products.get(segment, [])
    products = list(products_col.find({
        'category': {'$in': categories},
        'active': True
    }))
    
    for p in products:
        p['_id'] = str(p['_id'])
    
    return jsonify(products)

@app.route("/api/store/order", methods=["POST"])
def create_store_order():
    """Create new order with unique ID"""
    try:
        print("=" * 50)
        print("🛒 ORDER CREATION REQUEST")
        print("=" * 50)
        
        payload = request.json or {}
        print(f"📥 Received payload: {payload}")
        
        # Validate items
        items = payload.get("items", [])
        if not items or len(items) == 0:
            raise ValueError("No items in cart")
        
        print(f"📦 Items count: {len(items)}")
        for item in items:
            print(f"   - {item.get('name')}: {item.get('quantity')} x LKR {item.get('price')}")
        
        # Generate unique order ID
        unique_suffix = str(uuid.uuid4())[:8]
        timestamp = get_utc_now().strftime('%Y%m%d%H%M%S')
        order_id = f"ORD{timestamp}-{unique_suffix}"
        print(f"🆔 Generated Order ID: {order_id}")
        
        total_amount = float(payload.get("total_amount", 0))
        print(f"💰 Total Amount: LKR {total_amount}")
        
        if total_amount <= 0:
            raise ValueError("Invalid total amount")
        
        order = {
            "order_id": order_id,
            "user_id": payload.get("user_id") or session.get("user_id"),
            "items": items,
            "total_amount": total_amount,
            "status": "pending",
            "payment_status": "pending",
            "shipping_address": payload.get("shipping_address", {}),
            "payment_method": payload.get("payment_method", "payhere"),
            "created": get_utc_now(),
            "updated": get_utc_now()
        }
        
        print(f"💾 Saving order to database...")
        result = orders_col.insert_one(order)
        print(f"✅ Order saved with MongoDB ID: {result.inserted_id}")
        
        response_data = {
            "status": "success",
            "order_id": order_id,
            "order": serialize_mongo_doc(order)
        }
        
        print(f"📤 Response: order_id={order_id}")
        print("=" * 50)
        
        return jsonify(response_data), 201
        
    except ValueError as ve:
        error_msg = str(ve)
        print(f"❌ Validation Error: {error_msg}")
        return jsonify({"error": error_msg}), 400
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Order Creation Error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500
@app.route('/api/payhere/return')
def payhere_return():
    """Handle PayHere return after payment"""
    order_id = request.args.get('order_id')
    return redirect(f'/store?order_success={order_id}')
@app.route('/api/payhere/cancel')
def payhere_cancel():
    """Handle PayHere cancel"""
    return redirect('/store?payment_cancelled=true')

@app.route("/api/store/payment", methods=["POST"])
def process_payment():
    """Process payment for order"""
    payload = request.json or {}
    
    # Generate unique payment ID
    unique_suffix = str(uuid.uuid4())[:8]
    timestamp = get_utc_now().strftime('%Y%m%d%H%M%S')
    
    payment = {
        "payment_id": f"PAY{timestamp}-{unique_suffix}",
        "order_id": payload.get("order_id"),
        "user_id": payload.get("user_id") or session.get("user_id"),
        "amount": payload.get("amount", 0),
        "currency": payload.get("currency", "LKR"),
        "method": payload.get("method"),
        "status": "completed",
        "transaction_id": payload.get("transaction_id"),
        "created": get_utc_now()
    }
    
    # Update order status
    orders_col.update_one(
        {"order_id": payload.get("order_id")},
        {"$set": {
            "status": "pending",  # Changed from "paid"
            "payment_status": "completed",  # Track payment separately
            "updated": get_utc_now()
        }}
    )
    
    payments_col.insert_one(payment)
    
    # Log engagement
    eng_col.insert_one({
        "user_id": payment["user_id"],
        "type": "purchase",
        "product_ids": [item.get("product_id") for item in payload.get("items", [])],
        "amount": payload.get("amount", 0),
        "timestamp": get_utc_now()
    })
    
    return jsonify({"status": "ok", "payment_id": payment["payment_id"]})

# ============================================
# AI SEARCH & CHAT
# ============================================
@app.route("/api/ai/search", methods=["POST"])
def ai_vector_search():
    """Vector-based semantic search"""
    payload = request.json or {}
    query = payload.get("query", "").strip()
    top_k = int(payload.get("top_k", 5))
    language = payload.get("language", "en")
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    try:
        model = get_embedding_model()
        
        query_expanded = query.lower()
        
        if "exam" in query_expanded:
            query_expanded += " examination test assessment"
        if "apply" in query_expanded:
            query_expanded += " application register registration"
        if "renew" in query_expanded:
            query_expanded += " renewal update extend"
        if "certificate" in query_expanded:
            query_expanded += " document certification proof"
        
        print(f"🔍 Search query: '{query}' → Expanded: '{query_expanded}'")
        
        q_embedding = model.encode([query_expanded], convert_to_numpy=True)
        q_embedding = q_embedding / (np.linalg.norm(q_embedding, axis=1, keepdims=True) + 1e-10)
        
        if not META_PATH.exists():
            return jsonify({
                "error": "Search index not built. Please run: python build_ai_index.py",
                "query": query,
                "results": []
            }), 500
        
        with open(META_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        results = []
        
        if FAISS_AVAILABLE and INDEX_PATH.exists():
            index = faiss.read_index(str(INDEX_PATH))
            
            search_k = min(top_k * 3, len(metadata))
            distances, indices = index.search(q_embedding.astype(np.float32), search_k)
            
            print(f"📊 FAISS returned {len(indices[0])} results")
            
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(metadata):
                    doc = metadata[idx]
                    
                    score = float(dist)
                    
                    if score < 0.3:
                        continue
                    
                    question_text = doc.get('question', {}).get(language, 
                                            doc.get('question', {}).get('en', ''))
                    answer_text = doc.get('answer', {}).get(language,
                                          doc.get('answer', {}).get('en', ''))
                    
                    if not question_text:
                        question_text = doc.get('question_text', 'N/A')
                    if not answer_text:
                        answer_text = doc.get('answer_text', 'N/A')
                    
                    result = {
                        "doc_id": doc.get("doc_id"),
                        "service_id": doc.get("service_id"),
                        "service_name": doc.get("service_name", "Unknown Service"),
                        "subservice_name": doc.get("subservice_name", ""),
                        "category": doc.get("category", ""),
                        "question_text": question_text,
                        "answer_text": answer_text,
                        "question": doc.get("question", {}),
                        "answer": doc.get("answer", {}),
                        "metadata": doc.get("metadata", {}),
                        "score": score,
                        "relevance": "high" if score > 0.7 else "medium" if score > 0.5 else "low"
                    }
                    
                    results.append(result)
                    
                    if len(results) >= top_k:
                        break
            
            print(f"✅ Returning {len(results)} relevant results")
        
        elif EMBED_PATH.exists():
            embeddings = np.load(EMBED_PATH)
            similarities = (embeddings @ q_embedding[0]).tolist()
            top_indices = np.argsort(similarities)[::-1][:top_k * 2]
            
            for idx in top_indices:
                if similarities[idx] < 0.3:
                    continue
                    
                doc = metadata[idx]
                
                question_text = doc.get('question', {}).get(language, 
                                        doc.get('question', {}).get('en', ''))
                answer_text = doc.get('answer', {}).get(language,
                                      doc.get('answer', {}).get('en', ''))
                
                if not question_text:
                    question_text = doc.get('question_text', 'N/A')
                if not answer_text:
                    answer_text = doc.get('answer_text', 'N/A')
                
                results.append({
                    "doc_id": doc.get("doc_id"),
                    "service_id": doc.get("service_id"),
                    "service_name": doc.get("service_name", "Unknown"),
                    "question_text": question_text,
                    "answer_text": answer_text,
                    "question": doc.get("question", {}),
                    "answer": doc.get("answer", {}),
                    "metadata": doc.get("metadata", {}),
                    "score": float(similarities[idx]),
                    "relevance": "high" if similarities[idx] > 0.7 else "medium"
                })
                
                if len(results) >= top_k:
                    break
        
        else:
            return jsonify({
                "error": "Neither FAISS nor embeddings found. Run: python build_ai_index.py",
                "query": query,
                "results": []
            }), 500
        
        try:
            eng_col.insert_one({
                "user_id": session.get("user_id"),
                "query": query,
                "results_count": len(results),
                "timestamp": get_utc_now(),
                "search_type": "vector"
            })
        except:
            pass
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results),
            "language": language,
            "method": "faiss" if FAISS_AVAILABLE else "linear",
            "status": "success"
        })
    
    except Exception as e:
        print(f"❌ Vector search error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": str(e),
            "query": query,
            "results": [],
            "status": "error"
        }), 500

@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    """AI chatbot"""
    payload = request.json or {}
    question = payload.get("question", "").strip()
    ministry_id = payload.get("ministry_id")
    language = payload.get("language", "en")
    
    if not question:
        return jsonify({"error": "Question required"}), 400
    
    if not GROQ_API_KEY or not groq_client:
        return jsonify({
            "answer": "AI service is not configured. Please add GROQ_API_KEY to .env file.",
            "status": "error"
        }), 500
    
    ministry = services_col.find_one({"id": ministry_id})
    if not ministry:
        return jsonify({"error": "Ministry not found"}), 404
    
    language_config = {
        'en': {
            'name': 'English',
            'instruction': 'You MUST respond ONLY in English language.'
        },
        'si': {
            'name': 'Sinhala (සිංහල)',
            'instruction': 'ඔබ සිංහල භාෂාවෙන් පමණක් පිළිතුරු දිය යුතුය. You MUST respond ONLY in Sinhala language.'
        },
        'ta': {
            'name': 'Tamil (தமிழ்)',
            'instruction': 'நீங்கள் தமிழ் மொழியில் மட்டுமே பதிலளிக்க வேண்டும். You MUST respond ONLY in Tamil language.'
        }
    }
    
    lang_config = language_config.get(language, language_config['en'])
    
    context = f"Ministry: {ministry['name'].get(language, ministry['name']['en'])}\n\n"
    
    for sub in ministry.get('subservices', []):
        sub_name = sub['name'].get(language, sub['name']['en'])
        context += f"Service: {sub_name}\n"
        
        for q in sub.get('questions', []):
            question_text = q['q'].get(language, q['q']['en'])
            answer_text = q['answer'].get(language, q['answer']['en'])
            context += f"Q: {question_text}\nA: {answer_text}\n"
            
            if q.get('downloads'):
                context += f"Forms: {', '.join(q['downloads'])}\n"
            if q.get('location'):
                context += f"Location: {q['location']}\n"
            if q.get('instructions'):
                context += f"Instructions: {q['instructions']}\n"
            context += "\n"
    
    try:
        system_prompt = f"""You are a helpful assistant for {ministry['name'].get(language, ministry['name']['en'])} in Sri Lanka.

CRITICAL LANGUAGE REQUIREMENT:
{lang_config['instruction']}

Context about available services:
{context}

Instructions:
- Provide helpful, accurate answers based on the context above
- Be specific and cite available services when relevant
- Include information about forms and documents when mentioned
- Keep answers clear and easy to understand
- Use bullet points when appropriate
- If you cannot answer from context, politely say so
- IMPORTANT: Respond in {lang_config['name']} language ONLY"""
        
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        engagement_doc = {
            "user_id": session.get("user_id"),
            "age": session.get("user_age"),
            "job": session.get("user_job"),
            "desires": ["ai_chat"],
            "question_clicked": question,
            "service": ministry['name'].get(language, ministry['name']['en']),
            "timestamp": get_utc_now(),
            "chat_type": "ai_enhanced",
            "ministry_id": ministry_id,
            "language": language,
            "model_used": "llama-3.3-70b-groq",
            "success": True
        }
        
        eng_col.insert_one(engagement_doc)
        
        return jsonify({
            "answer": answer,
            "ministry": ministry['name'].get(language, ministry['name']['en']),
            "status": "success"
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Groq API error: {error_msg}")
        
        eng_col.insert_one({
            "user_id": session.get("user_id"),
            "age": session.get("user_age"),
            "job": session.get("user_job"),
            "desires": ["ai_chat"],
            "question_clicked": question,
            "service": ministry['name'].get(language, ministry['name']['en']),
            "timestamp": get_utc_now(),
            "chat_type": "ai_enhanced",
            "ministry_id": ministry_id,
            "language": language,
            "success": False,
            "error": error_msg
        })
        
        error_responses = {
            'en': "I apologize, but I encountered an error. Please try again.",
            'si': "මට කණගාටුයි, නමුත් මට දෝෂයක් ඇති විය. කරුණාකර නැවත උත්සාහ කරන්න.",
            'ta': "மன்னிக்கவும், ஆனால் எனக்கு ஒரு பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
        }
        
        return jsonify({
            "error": "AI service unavailable",
            "answer": error_responses.get(language, error_responses['en']),
            "status": "error"
        }), 500

# ============================================
# ADMIN ANALYTICS & INSIGHTS
# ============================================
@app.route("/api/admin/analytics/segments", methods=["GET"])
@admin_required
def get_segment_analytics():
    """Get analytics on user segments"""
    pipeline = [
        {"$group": {
            "_id": "$primary_segment",
            "count": {"$sum": 1},
            "avg_completeness": {"$avg": "$profile_completeness"}
        }},
        {"$sort": {"count": -1}}
    ]
    
    segment_stats = list(segments_col.aggregate(pipeline))
    
    priority_pipeline = [
        {"$unwind": "$priorities"},
        {"$group": {
            "_id": "$priorities.type",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    priority_stats = list(segments_col.aggregate(priority_pipeline))
    
    return jsonify({
        "segment_distribution": segment_stats,
        "priority_distribution": priority_stats,
        "total_segmented_users": segments_col.count_documents({})
    })

@app.route("/api/admin/analytics/revenue", methods=["GET"])
@admin_required
def get_revenue_analytics():
    """Get revenue analytics by segment"""
    pipeline = [
        {
            "$lookup": {
                "from": "user_segments",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "segment_info"
            }
        },
        {"$unwind": {"path": "$segment_info", "preserveNullAndEmptyArrays": True}},
        {
            "$group": {
                "_id": "$segment_info.primary_segment",
                "total_revenue": {"$sum": "$total_amount"},
                "order_count": {"$sum": 1},
                "avg_order_value": {"$avg": "$total_amount"}
            }
        },
        {"$sort": {"total_revenue": -1}}
    ]
    
    revenue_by_segment = list(orders_col.aggregate(pipeline))
    
    product_pipeline = [
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product_id",
                "total_sold": {"$sum": "$items.quantity"},
                "revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
            }
        },
        {"$sort": {"revenue": -1}},
        {"$limit": 10}
    ]
    
    top_products = list(orders_col.aggregate(product_pipeline))
    
    return jsonify({
        "revenue_by_segment": revenue_by_segment,
        "top_products": top_products,
        "total_revenue": sum(r.get('total_revenue', 0) for r in revenue_by_segment)
    })

@app.route("/api/user/data/export", methods=["GET"])
def export_user_data():
    """Export all user data (GDPR compliance)"""
    if not session.get("user_logged_in"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get("user_id")
    
    user_data = {
        "profile": users_col.find_one({"_id": ObjectId(user_id)}, {"password": 0, "_id": 0}),
        "segments": segments_col.find_one({"user_id": user_id}, {"_id": 0}),
        "orders": list(orders_col.find({"user_id": user_id}, {"_id": 0})),
        "enrollments": list(enrollments_col.find({"user_id": user_id}, {"_id": 0})),
        "engagements": list(eng_col.find({"user_id": user_id}, {"_id": 0}).limit(100))
    }
    
    return jsonify({
        "status": "success",
        "data": user_data,
        "exported_at": get_utc_now().isoformat()
    })

@app.route("/api/user/data/delete", methods=["POST"])
def delete_user_data():
    """Delete user account and all data (GDPR compliance)"""
    if not session.get("user_logged_in"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get("user_id")
    
    if not request.json.get("confirm"):
        return jsonify({"error": "Confirmation required"}), 400
    
    eng_col.update_many(
        {"user_id": user_id},
        {"$set": {"user_id": "DELETED_USER", "anonymized": True}}
    )
    
    users_col.delete_one({"_id": ObjectId(user_id)})
    segments_col.delete_one({"user_id": user_id})
    orders_col.update_many({"user_id": user_id}, {"$set": {"user_id": "DELETED_USER"}})
    enrollments_col.delete_many({"user_id": user_id})
    
    session.clear()
    
    return jsonify({
        "status": "success",
        "message": "All personal data deleted successfully"
    })

@app.route("/api/dashboard/analytics")
@admin_required
def get_dashboard_analytics():
    """Enhanced dashboard with store metrics"""
    total_users = users_col.count_documents({})
    active_users = users_col.count_documents({
        "last_active": {"$gte": get_utc_now() - timedelta(days=30)}
    })
    new_users_7d = users_col.count_documents({
        "created": {"$gte": get_utc_now() - timedelta(days=7)}
    })
    
    total_engagements = eng_col.count_documents({})
    recent_engagements = eng_col.count_documents({
        "timestamp": {"$gte": get_utc_now() - timedelta(days=7)}
    })
    
    total_orders = orders_col.count_documents({})
    total_revenue = list(payments_col.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]))
    total_revenue_amount = total_revenue[0]["total"] if total_revenue else 0
    
    popular_products = list(products_col.find().sort("rating", -1).limit(5))
    
    return jsonify({
        "user_metrics": {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_7d": new_users_7d
        },
        "engagement_metrics": {
            "total_engagements": total_engagements,
            "recent_engagements": recent_engagements
        },
        "store_metrics": {
            "total_orders": total_orders,
            "total_revenue": total_revenue_amount,
            "conversion_rate": "3.2%"
        },
        "popular_products": popular_products
    })

# ============================================
# ADMIN CRUD & INSIGHTS
# ============================================
@app.route("/api/admin/services", methods=["GET", "POST"])
@admin_required
def admin_services():
    if request.method == "GET":
        docs = list(services_col.find({}))
        for doc in docs:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        return jsonify(docs)
    
    payload = request.json
    sid = payload.get("id")
    if not sid:
        return jsonify({"error": "id required"}), 400
    services_col.update_one({"id": sid}, {"$set": payload}, upsert=True)
    return jsonify({"status": "ok"})

@app.route("/api/admin/services/<service_id>", methods=["DELETE"])
@admin_required
def delete_service(service_id):
    services_col.delete_one({"id": service_id})
    return jsonify({"status": "deleted"})

@app.route("/api/admin/insights")
@admin_required
def admin_insights():
    # Age groups
    age_groups = {"<18": 0, "18-25": 0, "26-40": 0, "41-60": 0, "60+": 0}
    for e in eng_col.find({}, {"age": 1}):
        age = e.get("age")
        if not age:
            continue
        try:
            age = int(age)
            if age < 18:
                age_groups["<18"] += 1
            elif age <= 25:
                age_groups["18-25"] += 1
            elif age <= 40:
                age_groups["26-40"] += 1
            elif age <= 60:
                age_groups["41-60"] += 1
            else:
                age_groups["60+"] += 1
        except:
            continue
    
    # Jobs, services, questions
    jobs = {}
    services = {}
    questions = {}
    desires = {}
    
    for e in eng_col.find({}, {"job": 1, "service": 1, "question_clicked": 1, "desires": 1}):
        j = (e.get("job") or "Unknown").strip()
        jobs[j] = jobs.get(j, 0) + 1
        
        s = e.get("service") or "Unknown"
        services[s] = services.get(s, 0) + 1
        
        q = e.get("question_clicked") or "Unknown"
        questions[q] = questions.get(q, 0) + 1
        
        for d in e.get("desires") or []:
            desires[d] = desires.get(d, 0) + 1
    
    # Sort all dictionaries
    jobs = dict(sorted(jobs.items(), key=lambda x: x[1], reverse=True))
    services = dict(sorted(services.items(), key=lambda x: x[1], reverse=True))
    questions = dict(sorted(questions.items(), key=lambda x: x[1], reverse=True))
    desires = dict(sorted(desires.items(), key=lambda x: x[1], reverse=True))
    
    # Premium suggestions - FIXED VERSION
    pipeline = [
        {"$match": {"question_clicked": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": {"user": "$user_id", "question": "$question_clicked"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 2}}}
    ]
    
    repeated = list(eng_col.aggregate(pipeline))
    premium_suggestions = []
    
    for r in repeated:
        if r["_id"].get("user") and r["_id"].get("question"):
            premium_suggestions.append({
                "user": r["_id"]["user"],
                "question": r["_id"]["question"],
                "count": r["count"]
            })
    
    return jsonify({
        "age_groups": age_groups,
        "jobs": jobs,
        "services": services,
        "questions": questions,
        "desires": desires,
        "premium_suggestions": premium_suggestions
    })


@app.route("/api/admin/training/stats", methods=["GET"])
@admin_required
def get_training_stats():
    """Get comprehensive training enrollment statistics"""
    try:
        # Overall statistics
        total_programs = training_programs_col.count_documents({"active": True})
        total_enrollments = enrollments_col.count_documents({})
        active_students = len(enrollments_col.distinct("user_id"))
        
        # Programs by status
        programs_with_enrollment = training_programs_col.aggregate([
            {"$match": {"active": True}},
            {
                "$project": {
                    "id": 1,
                    "title": 1,
                    "current_enrollments": 1,
                    "max_participants": 1,
                    "enrollment_open": 1,
                    "enrollment_percentage": {
                        "$cond": {
                            "if": {"$eq": ["$max_participants", 0]},
                            "then": 0,
                            "else": {
                                "$multiply": [
                                    {"$divide": ["$current_enrollments", "$max_participants"]},
                                    100
                                ]
                            }
                        }
                    }
                }
            }
        ])
        
        programs_list = list(programs_with_enrollment)
        programs_full = sum(1 for p in programs_list if p.get('current_enrollments', 0) >= p.get('max_participants', 1))
        programs_near_full = sum(1 for p in programs_list if 80 <= p.get('enrollment_percentage', 0) < 100)
        
        # Enrollment trends (last 30 days)
        thirty_days_ago = get_utc_now() - timedelta(days=30)
        recent_enrollments = list(enrollments_col.find(
            {"enrolled_date": {"$gte": thirty_days_ago}},
            {"enrolled_date": 1, "program_id": 1}
        ))
        
        # Daily enrollment counts
        daily_enrollments = defaultdict(int)
        for enrollment in recent_enrollments:
            date_key = enrollment['enrolled_date'].strftime('%Y-%m-%d')
            daily_enrollments[date_key] += 1
        
        # Sort by date
        enrollment_trend = [
            {"date": date, "count": count}
            for date, count in sorted(daily_enrollments.items())
        ]
        
        # Completion statistics
        completed_count = enrollments_col.count_documents({"completion_status": "completed"})
        in_progress_count = enrollments_col.count_documents({"completion_status": {"$ne": "completed"}})
        completion_rate = (completed_count / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Average progress
        progress_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_progress": {"$avg": "$progress"}
                }
            }
        ]
        progress_result = list(enrollments_col.aggregate(progress_pipeline))
        avg_progress = progress_result[0]['avg_progress'] if progress_result else 0
        
        return jsonify({
            "overview": {
                "total_programs": total_programs,
                "total_enrollments": total_enrollments,
                "active_students": active_students,
                "programs_full": programs_full,
                "programs_near_full": programs_near_full,
                "completion_rate": round(completion_rate, 2),
                "avg_progress": round(avg_progress, 2)
            },
            "enrollment_trend": enrollment_trend,
            "status_breakdown": {
                "completed": completed_count,
                "in_progress": in_progress_count
            }
        })
        
    except Exception as e:
        print(f"Error getting training stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/training/programs", methods=["GET"])
@admin_required
def get_admin_training_programs():
    """Get detailed program statistics for admin"""
    try:
        programs = list(training_programs_col.find({"active": True}, {"_id": 0}))
        
        # Enrich each program with enrollment statistics
        for program in programs:
            program_id = program.get('id')
            
            # Get enrollment count
            enrollment_count = enrollments_col.count_documents({"program_id": program_id})
            
            # Get completion statistics
            completed = enrollments_col.count_documents({
                "program_id": program_id,
                "completion_status": "completed"
            })
            
            # Get average progress
            progress_pipeline = [
                {"$match": {"program_id": program_id}},
                {
                    "$group": {
                        "_id": None,
                        "avg_progress": {"$avg": "$progress"}
                    }
                }
            ]
            progress_result = list(enrollments_col.aggregate(progress_pipeline))
            avg_progress = progress_result[0]['avg_progress'] if progress_result else 0
            
            # Get recent enrollments (last 7 days)
            seven_days_ago = get_utc_now() - timedelta(days=7)
            recent_enrollments = enrollments_col.count_documents({
                "program_id": program_id,
                "enrolled_date": {"$gte": seven_days_ago}
            })
            
            # Calculate enrollment percentage
            max_participants = program.get('max_participants', 1)
            current_enrollments = program.get('current_enrollments', 0)
            enrollment_percentage = (current_enrollments / max_participants * 100) if max_participants > 0 else 0
            
            # Add statistics to program
            program['statistics'] = {
                "total_enrolled": enrollment_count,
                "completed": completed,
                "avg_progress": round(avg_progress, 2),
                "recent_enrollments_7d": recent_enrollments,
                "enrollment_percentage": round(enrollment_percentage, 2),
                "completion_rate": round((completed / enrollment_count * 100), 2) if enrollment_count > 0 else 0
            }
        
        # Sort by enrollment count (descending)
        programs.sort(key=lambda x: x['statistics']['total_enrolled'], reverse=True)
        
        return jsonify(programs)
        
    except Exception as e:
        print(f"Error getting program stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/training/program/<program_id>/enrollments", methods=["GET"])
@admin_required
def get_program_enrollments(program_id):
    """Get detailed enrollment list for a specific program"""
    try:
        # Get program details
        program = training_programs_col.find_one({"id": program_id}, {"_id": 0})
        if not program:
            return jsonify({"error": "Program not found"}), 404
        
        # Get all enrollments for this program
        enrollments = list(enrollments_col.find({"program_id": program_id}, {"_id": 0}))
        
        # Enrich with user data
        for enrollment in enrollments:
            user_id = enrollment.get('user_id')
            user = users_col.find_one({"_id": ObjectId(user_id)}, {"_id": 0, "full_name": 1, "email": 1, "age": 1, "job": 1})
            if user:
                enrollment['user'] = user
            else:
                enrollment['user'] = {"full_name": "Unknown", "email": "N/A"}
            
            # Format dates
            if 'enrolled_date' in enrollment:
                enrollment['enrolled_date_formatted'] = enrollment['enrolled_date'].strftime('%Y-%m-%d %H:%M')
        
        # Sort by enrollment date (newest first)
        enrollments.sort(key=lambda x: x.get('enrolled_date', datetime.min), reverse=True)
        
        return jsonify({
            "program": program,
            "enrollments": enrollments,
            "total_count": len(enrollments)
        })
        
    except Exception as e:
        print(f"Error getting program enrollments: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/training/analytics", methods=["GET"])
@admin_required
def get_training_analytics():
    """Get advanced analytics for training programs"""
    try:
        # Most popular programs (by enrollment)
        popular_programs = list(training_programs_col.aggregate([
            {"$match": {"active": True}},
            {"$sort": {"current_enrollments": -1}},
            {"$limit": 5},
            {
                "$project": {
                    "title": 1,
                    "current_enrollments": 1,
                    "category": 1,
                    "level": 1
                }
            }
        ]))
        
        # Category distribution
        category_pipeline = [
            {"$match": {"active": True}},
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "total_enrollments": {"$sum": "$current_enrollments"}
                }
            },
            {"$sort": {"total_enrollments": -1}}
        ]
        category_stats = list(training_programs_col.aggregate(category_pipeline))
        
        # Level distribution
        level_pipeline = [
            {"$match": {"active": True}},
            {
                "$group": {
                    "_id": "$level",
                    "count": {"$sum": 1},
                    "total_enrollments": {"$sum": "$current_enrollments"}
                }
            }
        ]
        level_stats = list(training_programs_col.aggregate(level_pipeline))
        
        # Enrollment status distribution
        status_pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        status_stats = list(enrollments_col.aggregate(status_pipeline))
        
        # Average completion time (for completed enrollments)
        completion_time_pipeline = [
            {"$match": {"completion_status": "completed"}},
            {
                "$project": {
                    "days_to_complete": {
                        "$divide": [
                            {"$subtract": ["$completion_date", "$enrolled_date"]},
                            86400000  # milliseconds in a day
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_days": {"$avg": "$days_to_complete"}
                }
            }
        ]
        completion_time = list(enrollments_col.aggregate(completion_time_pipeline))
        avg_completion_days = completion_time[0]['avg_days'] if completion_time else 0
        
        return jsonify({
            "popular_programs": popular_programs,
            "category_distribution": category_stats,
            "level_distribution": level_stats,
            "status_distribution": status_stats,
            "avg_completion_days": round(avg_completion_days, 1) if avg_completion_days else 0
        })
        
    except Exception as e:
        print(f"Error getting training analytics: {e}")
        return jsonify({"error": str(e)}), 500
@app.route("/admin/training")
@admin_required
def admin_training_page():
    """Training programs admin dashboard"""
    return render_template("admin_training.html")
@app.route("/api/admin/training/export", methods=["GET"])
@admin_required
def export_training_data():
    """Export training enrollment data as CSV"""
    try:
        import csv
        from io import StringIO
        
        # Get all enrollments with user and program data
        enrollments = list(enrollments_col.find({}, {"_id": 0}))
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'User ID', 'User Email', 'User Name', 'Program ID', 'Program Title', 
            'Enrolled Date', 'Status', 'Progress', 'Completion Status', 'Completion Date'
        ])
        
        # Write data
        for enrollment in enrollments:
            user = users_col.find_one({"_id": ObjectId(enrollment.get('user_id'))}, {"_id": 0, "email": 1, "full_name": 1})
            program = training_programs_col.find_one({"id": enrollment.get('program_id')}, {"_id": 0, "title": 1})
            
            writer.writerow([
                enrollment.get('user_id', 'N/A'),
                user.get('email', 'N/A') if user else 'N/A',
                user.get('full_name', 'N/A') if user else 'N/A',
                enrollment.get('program_id', 'N/A'),
                program.get('title', {}).get('en', 'N/A') if program else 'N/A',
                enrollment.get('enrolled_date', 'N/A'),
                enrollment.get('status', 'N/A'),
                enrollment.get('progress', 0),
                enrollment.get('completion_status', 'N/A'),
                enrollment.get('completion_date', 'N/A')
            ])
        
        # Return CSV
        output.seek(0)
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=training_enrollments.csv'}
        )
        
    except Exception as e:
        print(f"Error exporting training data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/engagements")
@admin_required
def admin_engagements():
    items = []
    for e in eng_col.find().sort("timestamp", -1).limit(500):
        e["_id"] = str(e["_id"])
        e["timestamp"] = e.get("timestamp").isoformat() if e.get("timestamp") else ""
        
        # Skip rows where all key fields are None/empty
        age = e.get("age")
        job = e.get("job")
        question = e.get("question_clicked")
        service = e.get("service")
        
        # Only include if at least one meaningful field has data
        if any([
            age is not None and age != "",
            job is not None and job != "" and job != "Unknown",
            question is not None and question != "" and question != "Unknown",
            service is not None and service != "" and service != "Unknown"
        ]):
            items.append(e)
    
    return jsonify(items)

@app.route("/api/admin/export_csv")
@admin_required
def export_csv():
    cursor = eng_col.find()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["user_id", "age", "job", "desire", "question", "service", "timestamp"])
    
    for e in cursor:
        cw.writerow([
            e.get("user_id"), e.get("age"), e.get("job"),
            ",".join(e.get("desires") or []),
            e.get("question_clicked"), e.get("service"),
            e.get("timestamp").isoformat() if e.get("timestamp") else ""
        ])
    
    si.seek(0)
    return send_file(
        StringIO(si.read()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="engagements.csv"
    )

@app.route("/api/admin/rebuild-index", methods=["POST"])
@admin_required
def admin_rebuild_index():
    """Manually trigger FAISS index rebuild"""
    try:
        import subprocess
        
        result = subprocess.run(
            ["python", "build_ai_index.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            count_line = [l for l in output_lines if 'documents' in l.lower()]
            
            return jsonify({
                "status": "success",
                "message": "Index rebuilt successfully",
                "output": result.stdout[-1000:],
                "details": count_line[0] if count_line else "Check logs"
            })
        else:
            return jsonify({
                "status": "error",
                "error": result.stderr or "Unknown error",
                "output": result.stdout
            }), 500
    
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "error": "Index build timeout (>5 minutes)."
        }), 500
    
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "error": "build_ai_index.py not found."
        }), 500
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
# Add these new analytics endpoints to app.py

@app.route("/api/admin/analytics/realtime", methods=["GET"])
@admin_required
def get_realtime_analytics():
    """Get real-time dashboard analytics"""
    try:
        # === USER METRICS ===
        total_users = users_col.count_documents({})
        
        # Active users (logged in last 30 days)
        thirty_days_ago = get_utc_now() - timedelta(days=30)
        active_users = users_col.count_documents({
            "last_login": {"$gte": thirty_days_ago}
        })
        
        # New users (last 7 days)
        seven_days_ago = get_utc_now() - timedelta(days=7)
        new_users_week = users_col.count_documents({
            "created": {"$gte": seven_days_ago}
        })
        
        # Users by segment
        segment_pipeline = [
            {"$group": {
                "_id": "$primary_segment",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        segments_data = list(segments_col.aggregate(segment_pipeline))
        
        # === ORDER METRICS ===
        total_orders = orders_col.count_documents({})
        
        # Orders this month
        start_of_month = get_utc_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        orders_this_month = orders_col.count_documents({
            "created": {"$gte": start_of_month}
        })
        
        # Pending orders
        pending_orders = orders_col.count_documents({"status": "pending"})
        
        # === REVENUE METRICS ===
        revenue_pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }}
        ]
        revenue_data = list(payments_col.aggregate(revenue_pipeline))
        total_revenue = revenue_data[0]["total"] if revenue_data else 0
        completed_payments = revenue_data[0]["count"] if revenue_data else 0
        
        # Revenue this month
        revenue_month_pipeline = [
            {"$match": {
                "status": "completed",
                "created": {"$gte": start_of_month}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }}
        ]
        revenue_month_data = list(payments_col.aggregate(revenue_month_pipeline))
        revenue_this_month = revenue_month_data[0]["total"] if revenue_month_data else 0
        
        # === TOP 5 TRAINING COURSES ===
        top_courses_pipeline = [
            {"$match": {"active": True}},
            {"$sort": {"current_enrollments": -1}},
            {"$limit": 5},
            {"$project": {
                "_id": 0,
                "id": 1,
                "title": 1,
                "category": 1,
                "enrollments": "$current_enrollments",
                "max_participants": 1,
                "level": 1,
                "free": 1
            }}
        ]
        top_courses = list(training_programs_col.aggregate(top_courses_pipeline))
        
        # === TOP 5 PRODUCTS ===
        # Get most ordered products
        top_products_pipeline = [
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items.id",
                "product_name": {"$first": "$items.name"},
                "total_quantity": {"$sum": "$items.quantity"},
                "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                "order_count": {"$sum": 1}
            }},
            {"$sort": {"total_quantity": -1}},
            {"$limit": 5}
        ]
        top_products = list(orders_col.aggregate(top_products_pipeline))
        
        # === RECENT ENROLLMENTS ===
        recent_enrollments_pipeline = [
            {"$sort": {"enrolled_date": -1}},
            {"$limit": 10},
            {"$lookup": {
                "from": "training_programs",
                "localField": "program_id",
                "foreignField": "id",
                "as": "program"
            }},
            {"$unwind": "$program"},
            {"$project": {
                "_id": 0,
                "user_id": 1,
                "program_name": "$program.title.en",
                "enrolled_date": 1,
                "status": 1
            }}
        ]
        recent_enrollments = list(enrollments_col.aggregate(recent_enrollments_pipeline))
        
        # === ENGAGEMENT METRICS ===
        total_engagements = eng_col.count_documents({})
        
        # Engagements this week
        engagements_week = eng_col.count_documents({
            "timestamp": {"$gte": seven_days_ago}
        })
        
        # AI chat usage
        ai_chats = eng_col.count_documents({"chat_type": "ai_enhanced"})
        
        # Most searched services
        service_pipeline = [
            {"$match": {"service": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": "$service",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_services = list(eng_col.aggregate(service_pipeline))
        
        # === SYSTEM METRICS ===
        total_products = products_col.count_documents({"active": True})
        total_training_programs = training_programs_col.count_documents({"active": True})
        
        # Average profile completeness
        completeness_pipeline = [
            {"$match": {"profile_completeness": {"$exists": True}}},
            {"$group": {
                "_id": None,
                "avg_completeness": {"$avg": "$profile_completeness"}
            }}
        ]
        completeness_data = list(segments_col.aggregate(completeness_pipeline))
        avg_profile_completeness = round(completeness_data[0]["avg_completeness"], 1) if completeness_data else 0
        
        return jsonify({
            "status": "success",
            "timestamp": get_utc_now().isoformat(),
            
            # User Metrics
            "users": {
                "total": total_users,
                "active": active_users,
                "new_this_week": new_users_week,
                "by_segment": segments_data,
                "avg_profile_completeness": avg_profile_completeness
            },
            
            # Order Metrics
            "orders": {
                "total": total_orders,
                "this_month": orders_this_month,
                "pending": pending_orders
            },
            
            # Revenue Metrics
            "revenue": {
                "total": total_revenue,
                "this_month": revenue_this_month,
                "completed_payments": completed_payments,
                "avg_order_value": round(total_revenue / max(completed_payments, 1), 2)
            },
            
            # Training Metrics
            "training": {
                "total_programs": total_training_programs,
                "top_courses": top_courses,
                "recent_enrollments": recent_enrollments,
                "total_enrollments": enrollments_col.count_documents({})
            },
            
            # Product Metrics
            "products": {
                "total_active": total_products,
                "top_selling": top_products
            },
            
            # Engagement Metrics
            "engagement": {
                "total": total_engagements,
                "this_week": engagements_week,
                "ai_chats": ai_chats,
                "top_services": top_services
            }
        })
        
    except Exception as e:
        print(f"Analytics error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route("/api/admin/analytics/trends", methods=["GET"])
@admin_required
def get_analytics_trends():
    """Get trend data for charts (last 30 days)"""
    try:
        # Daily user registrations (last 30 days)
        thirty_days_ago = get_utc_now() - timedelta(days=30)
        
        user_trend_pipeline = [
            {"$match": {"created": {"$gte": thirty_days_ago}}},
            {"$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created"
                    }
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        user_trends = list(users_col.aggregate(user_trend_pipeline))
        
        # Daily revenue (last 30 days)
        revenue_trend_pipeline = [
            {"$match": {
                "status": "completed",
                "created": {"$gte": thirty_days_ago}
            }},
            {"$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created"
                    }
                },
                "revenue": {"$sum": "$amount"}
            }},
            {"$sort": {"_id": 1}}
        ]
        revenue_trends = list(payments_col.aggregate(revenue_trend_pipeline))
        
        # Daily enrollments (last 30 days)
        enrollment_trend_pipeline = [
            {"$match": {"enrolled_date": {"$gte": thirty_days_ago}}},
            {"$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$enrolled_date"
                    }
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        enrollment_trends = list(enrollments_col.aggregate(enrollment_trend_pipeline))
        
        return jsonify({
            "status": "success",
            "user_registrations": user_trends,
            "revenue": revenue_trends,
            "enrollments": enrollment_trends
        })
        
    except Exception as e:
        print(f"Trends error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
@app.route("/api/admin/ml-insights", methods=["GET"])
@admin_required
def ml_insights():
    """ML-powered insights"""
    if not ML_AVAILABLE or not rec_engine:
        return jsonify({
            "error": "ML engine not available",
            "message": "Install required packages: scikit-learn, pandas",
            "status": "unavailable"
        }), 503
    
    try:
        engagements = list(eng_col.find({}, {"_id": 0}))
        
        if len(engagements) < 5:
            return jsonify({
                "error": "Not enough data",
                "message": f"Need at least 5 engagements, found {len(engagements)}",
                "engagements_count": len(engagements)
            })
        
        patterns = rec_engine.analyze_engagement_patterns(engagements)
        premium_users = rec_engine.identify_premium_help_candidates(engagements, threshold=2)
        
        try:
            clusters, labels = rec_engine.cluster_users(engagements, n_clusters=min(5, len(engagements) // 2))
        except Exception as e:
            print(f"Clustering error: {e}")
            clusters = {"message": "Not enough data for clustering"}
            labels = []
        
        all_services = list(services_col.find({}, {"_id": 0}))
        sample_history = [patterns.get('popular_services', {}).get(list(patterns.get('popular_services', {}).keys())[0])] if patterns.get('popular_services') else []
        recommended = rec_engine.recommend_services(sample_history, all_services, top_k=5)
        
        ai_searches = eng_col.count_documents({"chat_type": "ai_enhanced"})
        vector_searches = eng_col.count_documents({"chat_type": {"$exists": False}, "question_clicked": {"$exists": True}})
        
        language_stats = {}
        for lang in ['en', 'si', 'ta']:
            count = eng_col.count_documents({"language": lang})
            language_stats[lang] = count
        
        total_ai_queries = eng_col.count_documents({"chat_type": "ai_enhanced"})
        successful_ai_queries = eng_col.count_documents({"chat_type": "ai_enhanced", "success": True})
        success_rate = (successful_ai_queries / total_ai_queries * 100) if total_ai_queries > 0 else 0
        
        return jsonify({
            "status": "success",
            "patterns": patterns,
            "premium_candidates": premium_users,
            "user_segments": clusters,
            "recommended_services": [
                {
                    "id": s.get("id"),
                    "name": s.get("name", {}).get("en"),
                    "category": s.get("category")
                } for s in recommended[:5]
            ],
            "analytics": {
                "ai_chat_queries": ai_searches,
                "vector_searches": vector_searches,
                "total_engagements": len(engagements),
                "success_rate": round(success_rate, 2),
                "language_distribution": language_stats
            },
            "timestamp": get_utc_now().isoformat()
        })
    
    except Exception as e:
        print(f"ML insights error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "error"
        }), 500
@app.route("/api/admin/orders", methods=["GET"])
@admin_required
def get_admin_orders():
    """Get all orders for admin dashboard"""
    try:
        # Get filter parameters
        status = request.args.get("status", "all")
        limit = int(request.args.get("limit", 100))
        
        # Build query
        query = {}
        if status != "all":
            query["status"] = status
        
        # Fetch orders with user information
        orders = list(orders_col.find(query).sort("created", -1).limit(limit))
        
        # Enrich orders with user details
        for order in orders:
            order["_id"] = str(order["_id"])
            
            # Get user info
            if order.get("user_id"):
                user = users_col.find_one({"_id": ObjectId(order["user_id"])}, {"email": 1, "full_name": 1, "phone": 1})
                if user:
                    order["user_info"] = {
                        "email": user.get("email"),
                        "full_name": user.get("full_name"),
                        "phone": user.get("phone")
                    }
            
            # Format dates
            if order.get("created"):
                order["created"] = order["created"].isoformat()
            if order.get("updated"):
                order["updated"] = order["updated"].isoformat()
        
        return jsonify({
            "status": "success",
            "orders": orders,
            "total": len(orders)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/admin/orders/<order_id>/approve", methods=["POST"])
@admin_required
def approve_order(order_id):
    """Approve an order"""
    try:
        order = orders_col.find_one({"order_id": order_id})
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Update order status
        result = orders_col.update_one(
            {"order_id": order_id},
            {
                "$set": {
                    "status": "approved",
                    "admin_action": "approved",
                    "admin_action_by": session.get("admin_user"),
                    "admin_action_date": get_utc_now(),
                    "updated": get_utc_now()
                }
            }
        )
        
        if result.modified_count > 0:
            # Log the action
            eng_col.insert_one({
                "type": "admin_action",
                "action": "order_approved",
                "order_id": order_id,
                "admin_user": session.get("admin_user"),
                "timestamp": get_utc_now()
            })
            
            # TODO: Send email notification to customer
            # send_order_status_email(order["user_id"], order_id, "approved")
            
            return jsonify({
                "status": "success",
                "message": "Order approved successfully"
            })
        else:
            return jsonify({"error": "Failed to approve order"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/orders/<order_id>/cancel", methods=["POST"])
@admin_required
def cancel_order(order_id):
    """Cancel an order"""
    try:
        data = request.json or {}
        cancel_reason = data.get("reason", "Cancelled by admin")
        
        order = orders_col.find_one({"order_id": order_id})
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Update order status
        result = orders_col.update_one(
            {"order_id": order_id},
            {
                "$set": {
                    "status": "cancelled",
                    "admin_action": "cancelled",
                    "cancel_reason": cancel_reason,
                    "admin_action_by": session.get("admin_user"),
                    "admin_action_date": get_utc_now(),
                    "updated": get_utc_now()
                }
            }
        )
        
        if result.modified_count > 0:
            # Log the action
            eng_col.insert_one({
                "type": "admin_action",
                "action": "order_cancelled",
                "order_id": order_id,
                "reason": cancel_reason,
                "admin_user": session.get("admin_user"),
                "timestamp": get_utc_now()
            })
            
            # TODO: Send email notification to customer
            # send_order_status_email(order["user_id"], order_id, "cancelled", cancel_reason)
            
            return jsonify({
                "status": "success",
                "message": "Order cancelled successfully"
            })
        else:
            return jsonify({"error": "Failed to cancel order"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/orders/stats", methods=["GET"])
@admin_required
def get_order_stats():
    """Get order statistics for admin dashboard"""
    try:
        total_orders = orders_col.count_documents({})
        pending_orders = orders_col.count_documents({"status": "pending"})
        approved_orders = orders_col.count_documents({"status": "approved"})
        cancelled_orders = orders_col.count_documents({"status": "cancelled"})
        
        # Revenue calculation
        total_revenue_pipeline = [
            {"$match": {"status": {"$in": ["approved", "paid"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]
        revenue_result = list(orders_col.aggregate(total_revenue_pipeline))
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        # Today's orders
        today_start = get_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_orders = orders_col.count_documents({
            "created": {"$gte": today_start}
        })
        
        return jsonify({
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "approved_orders": approved_orders,
            "cancelled_orders": cancelled_orders,
            "total_revenue": total_revenue,
            "today_orders": today_orders
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/admin/questions-by-age", methods=["POST"])
@admin_required
def questions_by_age():
    """Get top questions by age group"""
    try:
        payload = request.json or {}
        age_group = payload.get("age_group")
        
        if not age_group:
            return jsonify({"error": "age_group required"}), 400
        
        age_ranges = {
            "<18": (0, 17),
            "18-25": (18, 25),
            "26-40": (26, 40),
            "41-60": (41, 60),
            "60+": (61, 150)
        }
        
        if age_group not in age_ranges:
            return jsonify({"error": "Invalid age group"}), 400
        
        min_age, max_age = age_ranges[age_group]
        
        pipeline = [
            {
                "$match": {
                    "age": {"$gte": min_age, "$lte": max_age},
                    "question_clicked": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$question_clicked",
                    "count": {"$sum": 1},
                    "languages": {"$addToSet": "$language"},
                    "services": {"$addToSet": "$service"},
                    "avg_age": {"$avg": "$age"}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 10
            }
        ]
        
        results = list(eng_col.aggregate(pipeline))
        
        questions = []
        for r in results:
            questions.append({
                "question": r["_id"],
                "count": r["count"],
                "languages": r.get("languages", []),
                "services": list(set(r.get("services", []))),
                "avg_age": round(r.get("avg_age", 0), 1)
            })
        
        lang_pipeline = [
            {
                "$match": {
                    "age": {"$gte": min_age, "$lte": max_age},
                    "language": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": "$language",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        lang_results = list(eng_col.aggregate(lang_pipeline))
        language_breakdown = {r["_id"]: r["count"] for r in lang_results if r["_id"]}
        
        total = eng_col.count_documents({
            "age": {"$gte": min_age, "$lte": max_age}
        })
        
        return jsonify({
            "age_group": age_group,
            "total_engagements": total,
            "questions": questions,
            "language_breakdown": language_breakdown,
            "age_range": {
                "min": min_age,
                "max": max_age
            }
        })
    
    except Exception as e:
        print(f"Error in questions_by_age: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/storepay')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        product=PRODUCT,
        merchant_id=MERCHANT_ID
    )
@app.route('/api/payhere/generate-hash', methods=['POST'])
def generate_hash():
    try:
        print("\n" + "=" * 70)
        print("🔐 PAYHERE HASH GENERATION - FIXED VERSION")
        print("=" * 70)
        
        data = request.json
        order_id = data.get('order_id')
        amount = float(data.get('amount'))
        currency = data.get('currency', 'LKR')
        
        # Format amount to exactly 2 decimal places
        amount_formatted = "{:.2f}".format(amount)
        
        # CRITICAL: Try decoding the merchant secret if it's base64
        merchant_secret_to_use = MERCHANT_SECRET
        
        # Check if it's base64 and decode
        if MERCHANT_SECRET_BASE64.endswith('=='):
            try:
                merchant_secret_to_use = base64.b64decode(MERCHANT_SECRET_BASE64).decode('utf-8')
                print(f"✅ Using DECODED merchant secret")
                print(f"   Original: {MERCHANT_SECRET_BASE64[:20]}...")
                print(f"   Decoded:  {merchant_secret_to_use}")
            except:
                merchant_secret_to_use = MERCHANT_SECRET_BASE64
                print(f"⚠️  Using ORIGINAL merchant secret")
        
        print(f"\n📋 Payment Details:")
        print(f"   Merchant ID: {MERCHANT_ID}")
        print(f"   Order ID: {order_id}")
        print(f"   Amount: {amount_formatted}")
        print(f"   Currency: {currency}")
        print(f"   Using Secret: {merchant_secret_to_use[:20]}... (length: {len(merchant_secret_to_use)})")
        
        # Step 1: Hash the merchant secret (UPPERCASE)
        merchant_secret_md5 = hashlib.md5(merchant_secret_to_use.encode('utf-8')).hexdigest().upper()
        print(f"\n🔐 Step 1: Merchant Secret MD5: {merchant_secret_md5}")
        
        # Step 2: Build hash string
        # FORMAT: merchant_id + order_id + amount + currency + merchant_secret_md5
        hash_string = f"{MERCHANT_ID}{order_id}{amount_formatted}{currency}{merchant_secret_md5}"
        print(f"\n🔐 Step 2: Hash String: {hash_string}")
        
        # Step 3: Generate final hash (UPPERCASE)
        final_hash = hashlib.md5(hash_string.encode('utf-8')).hexdigest().upper()
        print(f"\n🔐 Step 3: Final Hash: {final_hash}")
        
        print("\n" + "=" * 70)
        
        return jsonify({
            'success': True,
            'hash': final_hash,
            'merchant_id': MERCHANT_ID,
            'order_id': order_id,
            'amount': amount_formatted,
            'currency': currency,
            'debug': {
                'merchant_secret_used': 'decoded' if merchant_secret_to_use != MERCHANT_SECRET_BASE64 else 'original',
                'merchant_secret_length': len(merchant_secret_to_use),
                'merchant_secret_md5': merchant_secret_md5,
                'hash_string': hash_string
            }
        })
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route("/payhere-test")
def payhere_test():
    return render_template("payhere_test.html") 
@app.route('/payment-notify', methods=['POST'])
def payment_notify():
    """Handle PayHere payment notification (IPN)"""
    try:
        # PayHere sends payment details as form data
        merchant_id = request.form.get('merchant_id')
        order_id = request.form.get('order_id')
        payment_id = request.form.get('payment_id')
        payhere_amount = request.form.get('payhere_amount')
        payhere_currency = request.form.get('payhere_currency')
        status_code = request.form.get('status_code')
        md5sig = request.form.get('md5sig')
        
        # Verify hash
        merchant_secret_hash = hashlib.md5(MERCHANT_SECRET.encode()).hexdigest().upper()
        local_md5sig = hashlib.md5(
            f"{merchant_id}{order_id}{payhere_amount}{payhere_currency}{status_code}{merchant_secret_hash}".encode()
        ).hexdigest().upper()
        
        if local_md5sig == md5sig and status_code == '2':
            print(f"Payment verified! Order: {order_id}, Payment ID: {payment_id}")
            # Here you would update your database
            return 'OK', 200
        else:
            print(f"Payment verification failed for order: {order_id}")
            return 'FAILED', 400
            
    except Exception as e:
        print(f"Notify error: {e}")
        return str(e), 400
@app.route('/payment-return')
def payment_return():
    return '''
    <h2>Payment Processing Complete</h2>
    <p>Thank you! Your payment has been processed.</p>
    <a href="/">Back to Home</a>
    '''
@app.route('/payment-cancel')
def payment_cancel():
    return '''
 <h2>Payment Cancelled</h2>
    <p>Your payment was cancelled.</p>
    <a href="/">Try Again</a>

'''
   
# ============================================
# INITIALIZATION & STARTUP
# ============================================
# Replace the bottom section of app.py (after line 2300+) with this:

if __name__ == "__main__":
    # Ensure admin exists
    if admins_col.count_documents({}) == 0:
        pwd = os.getenv("ADMIN_PWD", "admin123")
        hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
        admins_col.insert_one({"username": "admin", "password": hashed})
        print("✅ Created admin user")
    
    # Check if running in production
    is_production = os.getenv("DEBUG", "False").lower() == "false"
    
    print("=" * 70)
    print("🚀 ENHANCED CITIZEN SERVICES PORTAL")
    print("=" * 70)
    print(f"🌍 Environment: {'PRODUCTION' if is_production else 'DEVELOPMENT'}")
    print(f"🔒 Debug Mode: {'OFF' if is_production else 'ON'}")
    print(f"🔍 Vector Search: {'✅ Enabled' if INDEX_PATH.exists() else '⚠️ Run build_ai_index.py'}")
    print(f"🧠 FAISS Available: {'✅ Yes' if FAISS_AVAILABLE else '⚠️ Using fallback'}")
    print(f"🤖 Groq AI: {'✅ Configured' if GROQ_API_KEY else '❌ Missing API key'}")
    print(f"📊 ML Engine: {'✅ Available' if ML_AVAILABLE else '⚠️ Not loaded'}")
    print("=" * 70)
    print("✅ User Segmentation: Enabled")
    print("✅ Personalized Recommendations: Enabled")
    print("✅ Privacy Controls: Enabled")
    print("=" * 70)
    
    if is_production:
        # Production: Let Gunicorn handle the server
        print("🚀 Running in production mode (Gunicorn)")
        print("=" * 70)
    else:
        # Development: Use Flask's built-in server
        print("🔧 Running in development mode")
        print(f"📍 Public Portal: http://127.0.0.1:5000/")
        print(f"🤖 AI Chatbot: http://127.0.0.1:5000/chatbot")
        print(f"📊 Dashboard: http://127.0.0.1:5000/dashboard")
        print(f"👨‍💼 Admin Panel: http://127.0.0.1:5000/admin")
        print("=" * 70)
        app.run(
            debug=True, 
            host="0.0.0.0", 
            port=int(os.getenv("PORT", 5000))
        )