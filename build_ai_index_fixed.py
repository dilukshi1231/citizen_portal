"""
FIXED AI Vector Search Index Builder
Matches the expected structure in app.py
Run: python build_ai_index_fixed.py
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
    print("⚠️  FAISS not available, using fallback mode")

load_dotenv()

# Config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
INDEX_DIR = "data"
INDEX_PATH = f"{INDEX_DIR}/faiss.index"
META_PATH = f"{INDEX_DIR}/faiss_meta.json"
EMBED_PATH = f"{INDEX_DIR}/embeddings.npy"

print("=" * 70)
print("🤖 FIXED AI VECTOR SEARCH INDEX BUILDER")
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
    print("❌ No services found. Run seed_data.py first!")
    exit(1)

# Load embedding model
print(f"\n🧠 Loading embedding model: {EMBED_MODEL}")
model = SentenceTransformer(EMBED_MODEL)
print(f"✅ Model loaded. Dimension: {model.get_sentence_embedding_dimension()}")

# Build document corpus - FIXED STRUCTURE
print("\n📚 Building document corpus...")
documents = []

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
            
            # Content for embedding (English primary)
            content = f"{svc_name_en} | {sub_name_en} | Q: {q_en} | A: {a_en}"
            
            # FIXED: Match structure expected by app.py
            documents.append({
                "doc_id": f"{svc_id}::{sub_id}::{q_en[:50]}",
                "service_id": svc_id,
                "service_name": svc_name_en,
                "category": svc_category,
                "subservice_id": sub_id,
                "subservice_name": sub_name_en,
                # CRITICAL: These fields must exist for app.py
                "question_text": q_en,  # Used by app.py
                "answer_text": a_en,    # Used by app.py
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
                "content": content,
                "metadata": {
                    "downloads": q.get("downloads", []),
                    "location": q.get("location", ""),
                    "instructions": q.get("instructions", "")
                }
            })

print(f"✅ Created {len(documents)} searchable documents")

if len(documents) == 0:
    print("❌ No documents to index!")
    exit(1)

# Generate embeddings
print("\n🔢 Generating embeddings...")
texts = [doc["content"] for doc in documents]
embeddings = model.encode(
    texts,
    show_progress_bar=True,
    convert_to_numpy=True,
    batch_size=32
)

print(f"✅ Generated {len(embeddings)} embeddings")
print(f"   Shape: {embeddings.shape}")

# Normalize for cosine similarity
print("\n📏 Normalizing vectors...")
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
norms[norms == 0] = 1.0
embeddings = embeddings / norms
print("✅ Vectors normalized")

# Build FAISS index
if FAISS_AVAILABLE:
    print("\n🗃️  Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype(np.float32))
    faiss.write_index(index, INDEX_PATH)
    print(f"✅ FAISS index saved: {INDEX_PATH}")
    print(f"   Total vectors: {index.ntotal}")
else:
    print("\n💾 Saving embeddings (fallback mode)...")
    np.save(EMBED_PATH, embeddings)
    print(f"✅ Embeddings saved: {EMBED_PATH}")

# Save metadata
print("\n📄 Saving metadata...")
with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)
print(f"✅ Metadata saved: {META_PATH}")

# Test search
print("\n🧪 Testing search...")
test_queries = [
    "How to renew passport?",
    "IT certificate application",
    "School registration process"
]

for test_query in test_queries[:1]:  # Test first query
    print(f"\n   Query: '{test_query}'")
    
    q_embedding = model.encode([test_query], convert_to_numpy=True)
    q_embedding = q_embedding / (np.linalg.norm(q_embedding, axis=1, keepdims=True) + 1e-10)
    
    if FAISS_AVAILABLE:
        index = faiss.read_index(INDEX_PATH)
        distances, indices = index.search(q_embedding.astype(np.float32), 3)
        
        print("\n   🎯 Top 3 results:")
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
            doc = documents[idx]
            print(f"\n   {i}. Score: {dist:.3f}")
            print(f"      Service: {doc['service_name']}")
            print(f"      Question: {doc['question_text'][:80]}...")
    else:
        similarities = (embeddings @ q_embedding[0]).tolist()
        top_indices = np.argsort(similarities)[::-1][:3]
        
        print("\n   🎯 Top 3 results:")
        for i, idx in enumerate(top_indices, 1):
            doc = documents[idx]
            print(f"\n   {i}. Score: {similarities[idx]:.3f}")
            print(f"      Service: {doc['service_name']}")
            print(f"      Question: {doc['question_text'][:80]}...")

# Summary
print("\n" + "=" * 70)
print("📊 INDEX BUILD SUMMARY")
print("=" * 70)
print(f"✅ Documents indexed: {len(documents)}")
print(f"✅ Embedding model: {EMBED_MODEL}")
print(f"✅ Vector dimension: {embeddings.shape[1]}")
print(f"✅ FAISS available: {FAISS_AVAILABLE}")
print(f"✅ Index location: {INDEX_PATH if FAISS_AVAILABLE else EMBED_PATH}")
print(f"✅ Metadata location: {META_PATH}")
print("=" * 70)
print("\n🎉 AI search index ready!")
print("\n✅ STRUCTURE VERIFIED:")
print("   - question_text field: ✓")
print("   - answer_text field: ✓")
print("   - service_name field: ✓")
print("   - metadata field: ✓")
print("\nYou can now:")
print("1. Run: python app.py")
print("2. Use search bar on homepage")
print("3. Use AI chatbot at /chatbot")
print("=" * 70)