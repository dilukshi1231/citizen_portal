import os
import json
import pathlib
from flask import Flask, jsonify, render_template, request, session, redirect, send_file
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from io import StringIO
import csv
from dotenv import load_dotenv
import bcrypt
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq

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

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")
CORS(app)

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

# ============================================
# USER AUTHENTICATION ROUTES
# ============================================
@app.route("/user/login", methods=["GET"])
def user_login_page():
    """Display user login page"""
    if session.get("user_logged_in"):
        return redirect("/chatbot")
    return render_template("user_login.html")

@app.route("/user/register", methods=["GET"])
def user_register_page():
    """Display user registration page"""
    if session.get("user_logged_in"):
        return redirect("/chatbot")
    return render_template("user_register.html")
@app.route("/api/user/login", methods=["POST"])
def user_login_api():
    """User login API endpoint - Load profile data into session"""
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
                # Store ALL profile data in session
                session["user_logged_in"] = True
                session["user_id"] = str(user["_id"])
                session["user_email"] = email
                session["user_name"] = user.get("full_name", "User")
                # CRITICAL: Store age and job
                session["user_age"] = user.get("age")
                session["user_job"] = user.get("job")
                session["user_language"] = user.get("language", "en")
                
                return jsonify({
                    "status": "success",
                    "redirect": "/chatbot"
                })
        
        return jsonify({"error": "Invalid email or password"}), 401
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/register", methods=["POST"])
def user_register_api():
    """User registration API endpoint - Store profile data in session"""
    try:
        data = request.json
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        # MANDATORY FIELDS
        if not email or not password or not data.get("terms"):
            return jsonify({"error": "Email, password and terms are required"}), 400
        
        # Check if user already exists
        if users_col.find_one({"email": email}):
            return jsonify({"error": "Email already registered"}), 400
        
        # Hash password
        hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Extract optional fields
        age = int(data.get("age")) if data.get("age") else None
        job = data.get("job", "").strip() or None
        
        # Create user document
        user_doc = {
            "email": email,
            "password": hashed_pwd,
            "full_name": data.get("full_name", "").strip() or None,
            "phone": data.get("phone", "").strip() or None,
            "age": age,
            "job": job,
            "location": data.get("location", "").strip() or None,
            "language": data.get("language", "en"),
            "interests": data.get("interests", []),
            "terms_accepted": True,
            "created": datetime.now(),
            "updated": datetime.now()
        }
        
        result = users_col.insert_one(user_doc)
        
        # Auto-login and STORE PROFILE DATA IN SESSION
        session["user_logged_in"] = True
        session["user_id"] = str(result.inserted_id)
        session["user_email"] = email
        session["user_name"] = user_doc.get("full_name") or email.split('@')[0]
        # CRITICAL: Store age and job in session
        session["user_age"] = age
        session["user_job"] = job
        session["user_language"] = data.get("language", "en")
        
        return jsonify({
            "status": "success",
            "redirect": "/chatbot",
            "message": "Account created successfully!"
        })
    
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"error": "Registration failed. Please try again."}), 500



@app.route("/api/user/logout", methods=["POST"])
def user_logout():
    """User logout"""
    session.clear()
    return jsonify({"status": "logged out"})

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

# ============================================
# API: SERVICES & CATEGORIES (PUBLIC)
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

@app.route("/api/categories")
def get_categories():
    """Get all service categories"""
    cats = list(categories_col.find({}, {"_id": 0}))
    
    # If not seeded, create dynamic categories
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

@app.route("/api/service/<service_id>")
def get_service(service_id):
    doc = services_col.find_one({"id": service_id}, {"_id": 0})
    return jsonify(doc or {})

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
# AUTOSUGGEST ENDPOINT
# ============================================
@app.route("/api/search/autosuggest")
def autosuggest():
    """Quick text-based search for typeahead"""
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])
    
    regex = {"$regex": q, "$options": "i"}
    results = []
    
    for s in services_col.find(
        {"$or": [
            {"name.en": regex},
            {"name.si": regex},
            {"name.ta": regex},
            {"subservices.name.en": regex}
        ]},
        {"_id": 0, "id": 1, "name": 1, "subservices": 1}
    ).limit(10):
        results.append(s)
    
    return jsonify(results)

# ============================================
# VECTOR SEARCH ENDPOINT
# ============================================
# ============================================
# IMPROVED AI VECTOR SEARCH ENDPOINT
# Replace the /api/ai/search endpoint in app.py
# ============================================

@app.route("/api/ai/search", methods=["POST"])
def ai_vector_search():
    """
    IMPROVED: Vector-based semantic search with better relevance
    Body: {query: "how to apply for examinations?", top_k: 5, language: "en"}
    """
    payload = request.json or {}
    query = payload.get("query", "").strip()
    top_k = int(payload.get("top_k", 5))
    language = payload.get("language", "en")
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    try:
        # Load model and generate embedding
        model = get_embedding_model()
        
        # Preprocess query: expand with common synonyms
        query_expanded = query.lower()
        
        # Add common variations
        if "exam" in query_expanded:
            query_expanded += " examination test assessment"
        if "apply" in query_expanded:
            query_expanded += " application register registration"
        if "renew" in query_expanded:
            query_expanded += " renewal update extend"
        if "certificate" in query_expanded:
            query_expanded += " document certification proof"
        
        print(f"🔍 Search query: '{query}' → Expanded: '{query_expanded}'")
        
        # Generate embedding
        q_embedding = model.encode([query_expanded], convert_to_numpy=True)
        
        # Normalize for cosine similarity
        q_embedding = q_embedding / (np.linalg.norm(q_embedding, axis=1, keepdims=True) + 1e-10)
        
        # Load metadata
        if not META_PATH.exists():
            return jsonify({
                "error": "Search index not built. Please run: python rebuild_search_index.py",
                "query": query,
                "results": []
            }), 500
        
        with open(META_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        results = []
        
        # Search with FAISS (preferred)
        if FAISS_AVAILABLE and INDEX_PATH.exists():
            index = faiss.read_index(str(INDEX_PATH))
            
            # Search for more results initially, then filter
            search_k = min(top_k * 3, len(metadata))
            distances, indices = index.search(q_embedding.astype(np.float32), search_k)
            
            print(f"📊 FAISS returned {len(indices[0])} results")
            
            # Filter and format results
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(metadata):
                    doc = metadata[idx]
                    
                    # Calculate relevance score (0-1)
                    # Higher is better for Inner Product
                    score = float(dist)
                    
                    # Skip very low relevance results
                    if score < 0.3:
                        continue
                    
                    # Format for language
                    question_text = doc.get('question', {}).get(language, 
                                            doc.get('question', {}).get('en', ''))
                    answer_text = doc.get('answer', {}).get(language,
                                          doc.get('answer', {}).get('en', ''))
                    
                    # Fallback to question_text/answer_text fields if question/answer objects don't exist
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
            
            print(f"✅ Returning {len(results)} relevant results (score > 0.3)")
        
        # Fallback: linear scan
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
                "error": "Neither FAISS nor embeddings found. Run: python rebuild_search_index.py",
                "query": query,
                "results": []
            }), 500
        
        # Log search for analytics
        try:
            eng_col.insert_one({
                "user_id": session.get("user_id"),
                "query": query,
                "results_count": len(results),
                "timestamp": datetime.utcnow(),
                "search_type": "vector"
            })
        except:
            pass  # Don't fail search if logging fails
        
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

# ============================================
# GROQ AI CHATBOT
# ============================================
@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    """AI chatbot - Log engagement with user profile data"""
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
    
    # Get ministry context
    ministry = services_col.find_one({"id": ministry_id})
    if not ministry:
        return jsonify({"error": "Ministry not found"}), 404
    
    # Language configuration
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
    
    # Prepare context
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
        
        # Call Groq API
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
        
        # CRITICAL: Log engagement with user profile data from session
        engagement_doc = {
            "user_id": session.get("user_id"),
            "age": session.get("user_age"),  # Get from session
            "job": session.get("user_job"),  # Get from session
            "desires": ["ai_chat"],
            "question_clicked": question,
            "service": ministry['name'].get(language, ministry['name']['en']),
            "timestamp": datetime.utcnow(),
            "chat_type": "ai_enhanced",  # Changed from "ai" to "ai_enhanced"
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
        
        # Log failed engagement
        eng_col.insert_one({
            "user_id": session.get("user_id"),
            "age": session.get("user_age"),
            "job": session.get("user_job"),
            "desires": ["ai_chat"],
            "question_clicked": question,
            "service": ministry['name'].get(language, ministry['name']['en']),
            "timestamp": datetime.utcnow(),
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
# ML RECOMMENDATIONS
# ============================================
@app.route("/api/recommendations", methods=["POST"])
def get_recommendations():
    """Get personalized service recommendations"""
    if not ML_AVAILABLE or not rec_engine:
        return jsonify({"error": "ML engine not available"}), 503
    
    payload = request.json or {}
    user_history = payload.get("history", [])
    
    all_services = list(services_col.find({}, {"_id": 0}))
    recommendations = rec_engine.recommend_services(user_history, all_services, top_k=5)
    
    return jsonify(recommendations)

# ============================================
# ENGAGEMENT & PROFILE
# ============================================
@app.route("/api/engagement", methods=["POST"])
def log_engagement():
    """Log engagement with proper user profile data"""
    payload = request.json or {}
    
    # Get user profile data from session if not provided
    user_id = payload.get("user_id") or session.get("user_id")
    age = payload.get("age")
    if age is None:
        age = session.get("user_age")
    job = payload.get("job") or session.get("user_job")
    
    # Convert age to integer if it's a string
    if age is not None:
        try:
            age = int(age)
        except (ValueError, TypeError):
            age = None
    
    doc = {
        "user_id": user_id,
        "age": age,
        "job": job,
        "desires": payload.get("desires") or [],
        "question_clicked": payload.get("question_clicked"),
        "service": payload.get("service"),
        "language": payload.get("language") or session.get("user_language", "en"),
        "timestamp": datetime.utcnow(),
        "chat_type": payload.get("chat_type", "standard")
    }
    
    eng_col.insert_one(doc)
    return jsonify({"status": "ok"})

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
                {"$set": {f"profile.{step}": data, "updated": datetime.utcnow()}},
                upsert=True
            )
            return jsonify({"status": "ok", "profile_id": profile_id})
        
        elif email:
            result = users_col.find_one_and_update(
                {"email": email},
                {"$set": {f"profile.{step}": data, "updated": datetime.utcnow()}},
                upsert=True,
                return_document=True
            )
            return jsonify({"status": "ok", "profile_id": str(result["_id"])})
        
        else:
            result = users_col.insert_one({
                "profile": {step: data},
                "created": datetime.utcnow(),
                "anonymous": True
            })
            return jsonify({"status": "ok", "profile_id": str(result.inserted_id)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route("/api/admin/categories", methods=["GET", "POST", "DELETE"])
@admin_required
def manage_categories():
    if request.method == "GET":
        return jsonify(list(categories_col.find({}, {"_id": 0})))
    
    elif request.method == "POST":
        payload = request.json
        cat_id = payload.get("id")
        if not cat_id:
            return jsonify({"error": "ID required"}), 400
        categories_col.update_one({"id": cat_id}, {"$set": payload}, upsert=True)
        return jsonify({"status": "ok"})
    
    elif request.method == "DELETE":
        cat_id = request.args.get("id")
        categories_col.delete_one({"id": cat_id})
        return jsonify({"status": "deleted"})

@app.route("/api/admin/officers", methods=["GET", "POST", "DELETE"])
@admin_required
def manage_officers():
    if request.method == "GET":
        return jsonify(list(officers_col.find({}, {"_id": 0})))
    
    elif request.method == "POST":
        payload = request.json
        oid = payload.get("id")
        if not oid:
            return jsonify({"error": "ID required"}), 400
        officers_col.update_one({"id": oid}, {"$set": payload}, upsert=True)
        return jsonify({"status": "ok"})
    
    elif request.method == "DELETE":
        oid = request.args.get("id")
        officers_col.delete_one({"id": oid})
        return jsonify({"status": "deleted"})

@app.route("/api/admin/ads", methods=["GET", "POST", "DELETE"])
@admin_required
def manage_ads():
    if request.method == "GET":
        return jsonify(list(ads_col.find({}, {"_id": 0})))
    
    elif request.method == "POST":
        payload = request.json
        aid = payload.get("id")
        if not aid:
            return jsonify({"error": "ID required"}), 400
        ads_col.update_one({"id": aid}, {"$set": payload}, upsert=True)
        return jsonify({"status": "ok"})
    
    elif request.method == "DELETE":
        aid = request.args.get("id")
        ads_col.delete_one({"id": aid})
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
    
    # Sort all dictionaries by count (descending) to get actual top items
    jobs = dict(sorted(jobs.items(), key=lambda x: x[1], reverse=True))
    services = dict(sorted(services.items(), key=lambda x: x[1], reverse=True))
    questions = dict(sorted(questions.items(), key=lambda x: x[1], reverse=True))
    desires = dict(sorted(desires.items(), key=lambda x: x[1], reverse=True))
    
    # Premium suggestions
    pipeline = [
        {"$group": {"_id": {"user": "$user_id", "question": "$question_clicked"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 2}}}
    ]
    repeated = list(eng_col.aggregate(pipeline))
    premium_suggestions = [
        {"user": r["_id"]["user"], "question": r["_id"]["question"], "count": r["count"]}
        for r in repeated if r["_id"]["user"]
    ]
    
    return jsonify({
        "age_groups": age_groups,
        "jobs": jobs,
        "services": services,
        "questions": questions,
        "desires": desires,
        "premium_suggestions": premium_suggestions
    })

@app.route("/api/admin/engagements")
@admin_required
def admin_engagements():
    items = []
    for e in eng_col.find().sort("timestamp", -1).limit(500):
        e["_id"] = str(e["_id"])
        e["timestamp"] = e.get("timestamp").isoformat() if e.get("timestamp") else ""
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
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Extract document count from output
            output_lines = result.stdout.strip().split('\n')
            count_line = [l for l in output_lines if 'documents' in l.lower()]
            
            return jsonify({
                "status": "success",
                "message": "Index rebuilt successfully",
                "output": result.stdout[-1000:],  # Last 1000 chars
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
            "error": "Index build timeout (>5 minutes). Check if build_ai_index.py is working."
        }), 500
    
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "error": "build_ai_index.py not found. Make sure it's in the same directory."
        }), 500
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# Add these ML endpoints to your app.py

@app.route("/api/admin/ml-insights", methods=["GET"])
@admin_required
def ml_insights():
    """
    ML-powered insights: clustering, premium help detection, recommendations
    """
    if not ML_AVAILABLE or not rec_engine:
        return jsonify({
            "error": "ML engine not available",
            "message": "Install required packages: scikit-learn, pandas",
            "status": "unavailable"
        }), 503
    
    try:
        # Fetch all engagements
        engagements = list(eng_col.find({}, {"_id": 0}))
        
        if len(engagements) < 5:
            return jsonify({
                "error": "Not enough data",
                "message": f"Need at least 5 engagements, found {len(engagements)}",
                "engagements_count": len(engagements)
            })
        
        # 1. Analyze patterns
        patterns = rec_engine.analyze_engagement_patterns(engagements)
        
        # 2. Identify premium help candidates
        premium_users = rec_engine.identify_premium_help_candidates(engagements, threshold=2)
        
        # 3. User clustering
        try:
            clusters, labels = rec_engine.cluster_users(engagements, n_clusters=min(5, len(engagements) // 2))
        except Exception as e:
            print(f"Clustering error: {e}")
            clusters = {"message": "Not enough data for clustering"}
            labels = []
        
        # 4. Service recommendations (sample)
        all_services = list(services_col.find({}, {"_id": 0}))
        sample_history = [patterns.get('popular_services', {}).get(list(patterns.get('popular_services', {}).keys())[0])] if patterns.get('popular_services') else []
        recommended = rec_engine.recommend_services(sample_history, all_services, top_k=5)
        
        # 5. AI search analytics
        ai_searches = eng_col.count_documents({"chat_type": "ai_enhanced"})
        vector_searches = eng_col.count_documents({"chat_type": {"$exists": False}, "question_clicked": {"$exists": True}})
        
        # 6. Language distribution
        language_stats = {}
        for lang in ['en', 'si', 'ta']:
            count = eng_col.count_documents({"language": lang})
            language_stats[lang] = count
        
        # 7. Success rate
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
            "timestamp": datetime.utcnow().isoformat()
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


@app.route("/api/admin/train-recommendations", methods=["POST"])
@admin_required
def train_recommendations():
    """
    Train/retrain the recommendation engine
    """
    if not ML_AVAILABLE or not rec_engine:
        return jsonify({"error": "ML engine not available"}), 503
    
    try:
        # Fetch training data
        engagements = list(eng_col.find({}, {"_id": 0}))
        all_services = list(services_col.find({}, {"_id": 0}))
        
        if len(engagements) < 10:
            return jsonify({
                "error": "Not enough data for training",
                "required": 10,
                "available": len(engagements)
            }), 400
        
        # Train clustering model
        clusters, labels = rec_engine.cluster_users(engagements, n_clusters=5)
        
        # Save models
        rec_engine.save_models()
        
        return jsonify({
            "status": "success",
            "message": "Recommendation engine trained successfully",
            "training_data": {
                "engagements": len(engagements),
                "services": len(all_services),
                "clusters_created": len(set(labels)) if len(labels) > 0 else 0
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/questions-by-age", methods=["POST"])
@admin_required
def questions_by_age():
    """Get top questions by age group across all languages"""
    try:
        payload = request.json or {}
        age_group = payload.get("age_group")
        
        if not age_group:
            return jsonify({"error": "age_group required"}), 400
        
        # Define age ranges
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
        
        # Aggregate questions by age group
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
        
        # Format results
        questions = []
        for r in results:
            questions.append({
                "question": r["_id"],
                "count": r["count"],
                "languages": r.get("languages", []),
                "services": list(set(r.get("services", []))),
                "avg_age": round(r.get("avg_age", 0), 1)
            })
        
        # Get language breakdown
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
        
        # Total engagements for this age group
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
    
@app.route("/api/admin/export-ml-report", methods=["GET"])
@admin_required
def export_ml_report():
    """
    Export detailed ML analysis report
    """
    if not ML_AVAILABLE or not rec_engine:
        return jsonify({"error": "ML engine not available"}), 503
    
    try:
        engagements = list(eng_col.find({}, {"_id": 0}))
        
        # Generate comprehensive report
        patterns = rec_engine.analyze_engagement_patterns(engagements)
        premium_users = rec_engine.identify_premium_help_candidates(engagements, threshold=2)
        clusters, _ = rec_engine.cluster_users(engagements, n_clusters=5)
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_engagements": len(engagements),
            "patterns": patterns,
            "premium_help_candidates": len(premium_users),
            "premium_users_detail": premium_users,
            "user_segments": clusters,
            "recommendations": {
                "immediate_actions": [],
                "suggested_improvements": []
            }
        }
        
        # Add recommendations based on analysis
        if premium_users:
            report["recommendations"]["immediate_actions"].append({
                "action": "Contact High-Priority Users",
                "users": len([u for u in premium_users if u.get('priority') == 'high']),
                "reason": "Multiple repeat interactions indicate need for personalized help"
            })
        
        if patterns.get('popular_questions'):
            top_questions = list(patterns['popular_questions'].items())[:5]
            report["recommendations"]["suggested_improvements"].append({
                "action": "Improve FAQ Content",
                "questions": [q[0] for q in top_questions],
                "reason": "These questions are asked most frequently"
            })
        
        # Create CSV export
        si = StringIO()
        cw = csv.writer(si)
        
        # Write header
        cw.writerow(["ML Insights Report"])
        cw.writerow(["Generated:", report["generated_at"]])
        cw.writerow([])
        
        # Write patterns
        cw.writerow(["Engagement Patterns"])
        cw.writerow(["Total Engagements:", patterns.get('total_engagements', 0)])
        cw.writerow(["Unique Users:", patterns.get('unique_users', 0)])
        cw.writerow(["Average Age:", patterns.get('average_age', 0)])
        cw.writerow([])
        
        # Write premium candidates
        cw.writerow(["Premium Help Candidates"])
        cw.writerow(["User", "Question", "Repeat Count", "Priority"])
        for user in premium_users[:20]:
            cw.writerow([
                user.get('user_id', 'Anonymous'),
                user.get('question', '')[:50],
                user.get('repeat_count', 0),
                user.get('priority', 'unknown')
            ])
        
        si.seek(0)
        return send_file(
            StringIO(si.read()),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"ml_insights_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ============================================
# INITIALIZATION
# ============================================
if __name__ == "__main__":
    # Ensure admin exists
    if admins_col.count_documents({}) == 0:
        pwd = os.getenv("ADMIN_PWD", "admin123")
        hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
        admins_col.insert_one({"username": "admin", "password": hashed})
        print("✅ Created admin user")
    
    print("=" * 70)
    print("🚀 CITIZEN SERVICES PORTAL - STARTING")
    print("=" * 70)
    print(f"📍 Public Portal: http://127.0.0.1:5000/")
    print(f"🤖 AI Chatbot: http://127.0.0.1:5000/chatbot")
    print(f"👨‍💼 Admin Panel: http://127.0.0.1:5000/admin")
    print(f"🔐 Admin Login: http://127.0.0.1:5000/admin/login")
    print(f"👤 User Login: http://127.0.0.1:5000/user/login")
    print(f"📝 User Register: http://127.0.0.1:5000/user/register")
    print(f"🔍 Vector Search: {'✅ Enabled' if INDEX_PATH.exists() else '⚠️ Run build_ai_index.py'}")
    print(f"🧠 FAISS Available: {'✅ Yes' if FAISS_AVAILABLE else '⚠️ Using fallback'}")
    print(f"🤖 Groq AI: {'✅ Configured' if GROQ_API_KEY else '❌ Missing API key'}")
    print(f"📊 ML Engine: {'✅ Available' if ML_AVAILABLE else '⚠️ Not loaded'}")
    print("=" * 70)
    
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))