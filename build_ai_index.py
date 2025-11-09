"""
AI Vector Search Index Builder
Builds FAISS index from services content for semantic search
Run: python build_ai_index.py
"""

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from dotenv import load_dotenv

# Try to import FAISS (optional)
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS not available, will use fallback mode")

load_dotenv()

# Config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
INDEX_DIR = "data"
INDEX_PATH = f"{INDEX_DIR}/faiss.index"
META_PATH = f"{INDEX_DIR}/faiss_meta.json"
EMBED_PATH = f"{INDEX_DIR}/embeddings.npy"

print("=" * 70)
print("🤖 AI VECTOR SEARCH INDEX BUILDER")
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
print("   (This may take a few minutes on first run...)")
model = SentenceTransformer(EMBED_MODEL)
print(f"✅ Model loaded. Dimension: {model.get_sentence_embedding_dimension()}")

# Build document corpus
print("\n📚 Building document corpus...")
documents = []

for svc in services_col.find():
    svc_id = svc.get("id", "unknown")
    svc_name = svc.get("name", {}).get("en", "")
    svc_category = svc.get("category", "uncategorized")
    
    for sub in svc.get("subservices", []):
        sub_id = sub.get("id", "unknown")
        sub_name = sub.get("name", {}).get("en", "")
        
        for q in sub.get("questions", []):
            # Extract question and answer in all languages
            q_en = q.get("q", {}).get("en", "")
            q_si = q.get("q", {}).get("si", "")
            q_ta = q.get("q", {}).get("ta", "")
            
            a_en = q.get("answer", {}).get("en", "")
            a_si = q.get("answer", {}).get("si", "")
            a_ta = q.get("answer", {}).get("ta", "")
            
            # Combine for rich context (English primary for embedding)
            content = f"{svc_name} | {sub_name} | Q: {q_en} | A: {a_en}"
            
            documents.append({
                "doc_id": f"{svc_id}::{sub_id}::{q_en[:50]}",
                "service_id": svc_id,
                "service_name": svc_name,
                "category": svc_category,
                "subservice_id": sub_id,
                "subservice_name": sub_name,
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
print("\n📐 Normalizing vectors...")
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
norms[norms == 0] = 1.0  # Avoid division by zero
embeddings = embeddings / norms
print("✅ Vectors normalized")

# Build FAISS index
if FAISS_AVAILABLE:
    print("\n🏗️  Building FAISS index...")
    dimension = embeddings.shape[1]
    
    # Use IndexFlatIP for inner product (cosine similarity after normalization)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype(np.float32))
    
    # Save index
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
test_query = "How to renew passport?"
print(f"   Query: '{test_query}'")

q_embedding = model.encode([test_query], convert_to_numpy=True)
q_embedding = q_embedding / (np.linalg.norm(q_embedding, axis=1, keepdims=True) + 1e-10)

if FAISS_AVAILABLE:
    index = faiss.read_index(INDEX_PATH)
    distances, indices = index.search(q_embedding.astype(np.float32), 3)
    
    print("\n🎯 Top 3 results:")
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
        doc = documents[idx]
        print(f"\n   {i}. Score: {dist:.3f}")
        print(f"      Service: {doc['service_name']}")
        print(f"      Question: {doc['question']['en'][:80]}...")
else:
    # Fallback: linear scan
    similarities = (embeddings @ q_embedding[0]).tolist()
    top_indices = np.argsort(similarities)[::-1][:3]
    
    print("\n🎯 Top 3 results:")
    for i, idx in enumerate(top_indices, 1):
        doc = documents[idx]
        print(f"\n   {i}. Score: {similarities[idx]:.3f}")
        print(f"      Service: {doc['service_name']}")
        print(f"      Question: {doc['question']['en'][:80]}...")

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
print("\nYou can now:")
print("1. Run: python app.py")
print("2. Use AI search endpoint: /api/ai/search")
print("3. Try queries like: 'How to get IT certificate?'")
print("=" * 70)