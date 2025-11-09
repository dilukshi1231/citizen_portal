"""
AI Search Diagnostic Tool
Run: python diagnose_search.py
"""

import os
import json
import requests
from pathlib import Path

print("=" * 70)
print("🔍 AI SEARCH DIAGNOSTIC TOOL")
print("=" * 70)

# Check 1: Files exist
print("\n📁 Checking files...")
files_to_check = [
    "data/faiss.index",
    "data/faiss_meta.json",
    "data/embeddings.npy"
]

for filepath in files_to_check:
    if Path(filepath).exists():
        size = Path(filepath).stat().st_size / 1024
        print(f"   ✅ {filepath} ({size:.1f} KB)")
    else:
        print(f"   ❌ {filepath} NOT FOUND")

# Check 2: Metadata structure
print("\n📋 Checking metadata structure...")
meta_path = Path("data/faiss_meta.json")
if meta_path.exists():
    with open(meta_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"   ✅ Total documents: {len(metadata)}")
    
    if len(metadata) > 0:
        sample = metadata[0]
        required_fields = ["question_text", "answer_text", "service_name", "content"]
        
        for field in required_fields:
            if field in sample:
                print(f"   ✅ Field '{field}' exists")
            else:
                print(f"   ❌ Field '{field}' MISSING")
        
        # Show sample
        print(f"\n   📝 Sample document:")
        print(f"      Service: {sample.get('service_name', 'N/A')}")
        print(f"      Question: {sample.get('question_text', 'N/A')[:60]}...")
        print(f"      Answer: {sample.get('answer_text', 'N/A')[:60]}...")
else:
    print("   ❌ Metadata file not found")

# Check 3: Test API endpoint
print("\n🌐 Testing API endpoint...")
try:
    response = requests.post(
        "http://127.0.0.1:5000/api/ai/search",
        json={
            "query": "how to apply for examinations",
            "top_k": 5,
            "language": "en"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API responded successfully")
        print(f"   📊 Results returned: {data.get('count', 0)}")
        
        if data.get('results'):
            print(f"\n   🎯 Top result:")
            top = data['results'][0]
            print(f"      Service: {top.get('service_name')}")
            print(f"      Question: {top.get('question_text', 'N/A')[:60]}...")
            print(f"      Score: {top.get('score', 0):.3f}")
            print(f"      Relevance: {top.get('relevance', 'N/A')}")
    else:
        print(f"   ❌ API error: {response.status_code}")
        print(f"      {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to app. Is it running? (python app.py)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 4: Index quality test
print("\n🧪 Testing search quality...")
test_cases = [
    ("how to apply for examinations", "education", "exam"),
    ("renew passport", "immigration", "passport"),
    ("IT certificate", "IT", "certificate"),
]

for query, expected_service, expected_keyword in test_cases:
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/ai/search",
            json={"query": query, "top_k": 3},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if results:
                top_result = results[0]
                service = top_result.get('service_name', '').lower()
                question = top_result.get('question_text', '').lower()
                
                # Check if result is relevant
                is_relevant = (
                    expected_service.lower() in service or
                    expected_keyword.lower() in question
                )
                
                status = "✅" if is_relevant else "❌"
                print(f"\n   {status} Query: '{query}'")
                print(f"      Expected: {expected_service}/{expected_keyword}")
                print(f"      Got: {top_result.get('service_name')} - {question[:50]}...")
                print(f"      Score: {top_result.get('score', 0):.3f}")
            else:
                print(f"\n   ❌ Query: '{query}' - No results")
    except:
        print(f"\n   ⚠️  Query: '{query}' - API error")

# Summary and recommendations
print("\n" + "=" * 70)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 70)

recommendations = []

if not Path("data/faiss_meta.json").exists():
    recommendations.append("❌ Index not built - Run: python rebuild_search_index.py")

if Path("data/faiss_meta.json").exists():
    with open("data/faiss_meta.json", 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        if len(metadata) < 10:
            recommendations.append("⚠️  Very few documents indexed - Run seed_data.py first")
        elif "question_text" not in metadata[0]:
            recommendations.append("❌ Wrong index structure - Run: python rebuild_search_index.py")

if recommendations:
    print("\n🔧 RECOMMENDED ACTIONS:")
    for rec in recommendations:
        print(f"   {rec}")
else:
    print("\n✅ All checks passed! Search should be working.")

print("\n" + "=" * 70)