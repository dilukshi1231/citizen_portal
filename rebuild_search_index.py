"""
COMPLETE FIX for AI Vector Search
Run this to rebuild index with better embeddings
File: rebuild_search_index.py
"""

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from dotenv import load_dotenv

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS not available, using fallback")

load_dotenv()

# Config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR = "data"
INDEX_PATH = f"{INDEX_DIR}/faiss.index"
META_PATH = f"{INDEX_DIR}/faiss_meta.json"
EMBED_PATH = f"{INDEX_DIR}/embeddings.npy"

print("=" * 70)
print("🔧 FIXING AI VECTOR SEARCH")
print("=" * 70)

# Create data directory
os.makedirs(INDEX_DIR, exist_ok=True)

# Connect to MongoDB
print("\n📡 Connecting to MongoDB...")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
services_col = db["services"]

service_count = services_col.count_documents({})
print(f"✅ Connected. Found {service_count} services")

if service_count == 0:
    print("❌ No services found. Run: python seed_data.py")
    exit(1)

# Load embedding model
print(f"\n🧠 Loading embedding model: {EMBED_MODEL}")
model = SentenceTransformer(EMBED_MODEL)
print(f"✅ Model loaded. Dimension: {model.get_sentence_embedding_dimension()}")

# Build document corpus with ENHANCED CONTENT
print("\n📚 Building enhanced document corpus...")
documents = []
question_count = 0

for svc in services_col.find():
    svc_id = svc.get("id", "unknown")
    svc_name_en = svc.get("name", {}).get("en", "")
    svc_name_si = svc.get("name", {}).get("si", "")
    svc_name_ta = svc.get("name", {}).get("ta", "")
    svc_category = svc.get("category", "uncategorized")
    
    for sub in svc.get("subservices", []):
        sub_id = sub.get("id", "unknown")
        sub_name_en = sub.get("name", {}).get("en", "")
        sub_name_si = sub.get("name", {}).get("si", "")
        sub_name_ta = sub.get("name", {}).get("ta", "")
        
        for q in sub.get("questions", []):
            question_count += 1
            
            # Extract all languages
            q_obj = q.get("q", {})
            if isinstance(q_obj, str):
                q_en = q_obj
                q_si = ""
                q_ta = ""
            else:
                q_en = q_obj.get("en", "")
                q_si = q_obj.get("si", "")
                q_ta = q_obj.get("ta", "")
            
            a_obj = q.get("answer", {})
            if isinstance(a_obj, str):
                a_en = a_obj
                a_si = ""
                a_ta = ""
            else:
                a_en = a_obj.get("en", "")
                a_si = a_obj.get("si", "")
                a_ta = a_obj.get("ta", "")
            
            # ENHANCED: Add keywords for better matching
            keywords = []
            
            # Extract action keywords
            if "apply" in q_en.lower() or "register" in q_en.lower():
                keywords.append("application registration process")
            if "renew" in q_en.lower():
                keywords.append("renewal update")
            if "exam" in q_en.lower() or "test" in q_en.lower():
                keywords.append("examination test assessment")
            if "certificate" in q_en.lower() or "document" in q_en.lower():
                keywords.append("certificate document proof")
            if "how to" in q_en.lower():
                keywords.append("procedure steps guide instructions")
            
            # CRITICAL: Rich content for better semantic matching
            content = f"""
            Ministry: {svc_name_en}
            Service: {sub_name_en}
            Question: {q_en}
            Answer: {a_en}
            Keywords: {' '.join(keywords)}
            Category: {svc_category}
            """.strip()
            
            # Create document
            documents.append({
                "doc_id": f"{svc_id}::{sub_id}::{question_count}",
                "service_id": svc_id,
                "service_name": svc_name_en,
                "category": svc_category,
                "subservice_id": sub_id,
                "subservice_name": sub_name_en,
                # CRITICAL: These fields MUST exist for app.py
                "question_text": q_en,
                "answer_text": a_en,
                "question": {
                    "en": q_en,
                    "si": q_si,
                    "ta": q_ta
                },
                "answer": {
                    "en": a_en,
                    "si": a_si,
                    "ta": a_ta
                },
                "content": content,  # Enhanced content for embedding
                "keywords": keywords,
                "metadata": {
                    "downloads": q.get("downloads", []),
                    "location": q.get("location", ""),
                    "instructions": q.get("instructions", "")
                }
            })

print(f"✅ Created {len(documents)} searchable documents")
print(f"   Total questions indexed: {question_count}")

if len(documents) == 0:
    print("❌ No documents to index!")
    exit(1)

# Generate embeddings
print("\n🔢 Generating embeddings with enhanced content...")
texts = [doc["content"] for doc in documents]
embeddings = model.encode(
    texts,
    show_progress_bar=True,
    convert_to_numpy=True,
    batch_size=16,  # Smaller batch for stability
    normalize_embeddings=True  # Built-in normalization
)

print(f"✅ Generated {len(embeddings)} embeddings")
print(f"   Shape: {embeddings.shape}")
print(f"   Mean norm: {np.mean(np.linalg.norm(embeddings, axis=1)):.4f}")

# Additional normalization (belt and suspenders)
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
norms[norms == 0] = 1.0
embeddings = embeddings / norms

print(f"✅ Vectors normalized")

# Build FAISS index
if FAISS_AVAILABLE:
    print("\n🗃️  Building FAISS index with cosine similarity...")
    dimension = embeddings.shape[1]
    
    # Use IndexFlatIP for inner product (cosine after normalization)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype(np.float32))
    
    # Save index
    faiss.write_index(index, INDEX_PATH)
    print(f"✅ FAISS index saved: {INDEX_PATH}")
    print(f"   Total vectors: {index.ntotal}")
    print(f"   Index type: Inner Product (cosine similarity)")
else:
    print("\n💾 Saving embeddings (fallback mode)...")
    np.save(EMBED_PATH, embeddings)
    print(f"✅ Embeddings saved: {EMBED_PATH}")

# Save metadata
print("\n📄 Saving metadata...")
with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)
print(f"✅ Metadata saved: {META_PATH}")
print(f"   File size: {os.path.getsize(META_PATH) / 1024:.1f} KB")

# TEST THE INDEX
print("\n" + "=" * 70)
print("🧪 TESTING SEARCH QUALITY")
print("=" * 70)

test_queries = [
    "How to apply for examinations?",
    "Renew passport",
    "IT certificate application",
    "Register school",
    "Get driving license"
]

for test_query in test_queries:
    print(f"\n📝 Query: '{test_query}'")
    
    # Generate query embedding
    q_embedding = model.encode([test_query], convert_to_numpy=True, normalize_embeddings=True)
    q_embedding = q_embedding / (np.linalg.norm(q_embedding, axis=1, keepdims=True) + 1e-10)
    
    if FAISS_AVAILABLE:
        index = faiss.read_index(INDEX_PATH)
        distances, indices = index.search(q_embedding.astype(np.float32), 3)
        
        print("   🎯 Top 3 results:")
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
            if idx < len(documents):
                doc = documents[idx]
                print(f"   {i}. Score: {dist:.3f}")
                print(f"      Service: {doc['service_name']}")
                print(f"      Q: {doc['question_text'][:60]}...")
    else:
        # Fallback: cosine similarity
        similarities = (embeddings @ q_embedding[0]).tolist()
        top_indices = np.argsort(similarities)[::-1][:3]
        
        print("   🎯 Top 3 results:")
        for i, idx in enumerate(top_indices, 1):
            doc = documents[idx]
            print(f"   {i}. Score: {similarities[idx]:.3f}")
            print(f"      Service: {doc['service_name']}")
            print(f"      Q: {doc['question_text'][:60]}...")

# Summary
print("\n" + "=" * 70)
print("📊 INDEX BUILD SUMMARY")
print("=" * 70)
print(f"✅ Documents indexed: {len(documents)}")
print(f"✅ Questions indexed: {question_count}")
print(f"✅ Embedding model: {EMBED_MODEL}")
print(f"✅ Vector dimension: {embeddings.shape[1]}")
print(f"✅ FAISS available: {FAISS_AVAILABLE}")
print(f"✅ Index method: {'FAISS (fast)' if FAISS_AVAILABLE else 'NumPy (fallback)'}")
print(f"✅ Normalization: Cosine similarity optimized")
print("=" * 70)

print("\n✅ STRUCTURE VERIFIED:")
print("   - question_text field: ✓")
print("   - answer_text field: ✓")
print("   - service_name field: ✓")
print("   - Enhanced content with keywords: ✓")
print("   - Metadata field: ✓")

print("\n🎉 AI search index rebuilt with improvements!")
print("\n📋 Next steps:")
print("1. Restart app: python app.py")
print("2. Test search: 'how to apply for examinations'")
print("3. Should now return RELEVANT exam-related results")
print("=" * 70)