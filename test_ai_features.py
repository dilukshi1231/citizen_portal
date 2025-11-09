"""
Test AI Features - Verify Gemini Integration
Run: python test_ai_features.py
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("=" * 70)
print("🤖 AI FEATURES TEST")
print("=" * 70)

# Test 1: Check Gemini API Key
print("\n📋 TEST 1: Checking Gemini API Key...")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ FAILED: GEMINI_API_KEY not found in .env file")
    print("\n🔧 How to fix:")
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Click 'Create API Key'")
    print("3. Copy the key (starts with AIza...)")
    print("4. Add to .env file: GEMINI_API_KEY='your-key-here'")
    exit(1)
elif not GEMINI_API_KEY.startswith('AIza'):
    print(f"⚠️  WARNING: API key doesn't look valid")
    print(f"   Key should start with 'AIza' but starts with: {GEMINI_API_KEY[:10]}...")
else:
    print(f"✅ PASSED: Found API key (starts with {GEMINI_API_KEY[:10]}...)")

# Test 2: Configure Gemini
print("\n📋 TEST 2: Configuring Gemini API...")
try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ PASSED: Gemini API configured")
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
    exit(1)

# Test 3: Initialize Model
print("\n📋 TEST 3: Initializing Gemini Pro model...")
try:
    model = genai.GenerativeModel('gemini-pro')
    print("✅ PASSED: Model initialized")
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
    exit(1)

# Test 4: Simple Text Generation
print("\n📋 TEST 4: Testing text generation...")
try:
    response = model.generate_content("Say hello in one sentence")
    result = response.text
    print(f"✅ PASSED: Generated response")
    print(f"   Response: {result[:100]}...")
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
    print("\n🔧 Possible issues:")
    print("1. Invalid API key")
    print("2. API quota exceeded (1,500/day free limit)")
    print("3. Network connection issue")
    print("4. API key not activated yet (wait a few minutes)")
    exit(1)

# Test 5: Government Service Query Simulation
print("\n📋 TEST 5: Testing government service query...")
try:
    context = """
    [Ministry of Immigration - Passport Services]
    Q: How to renew passport?
    A: Visit immigration office with current passport, NIC, and 2 photos. 
       Fee: Rs.3000. Processing time: 2-3 weeks.
    Instructions: Bring original documents and photocopies.
    """
    
    prompt = f"""You are a helpful assistant for Sri Lankan government services.

Context Information:
{context}

User Question: How do I renew my passport?

Instructions:
1. Answer based ONLY on the context provided
2. Mention the source ministry and service
3. Keep answer clear and concise
4. Include relevant instructions

Answer:"""
    
    response = model.generate_content(prompt)
    answer = response.text
    
    print(f"✅ PASSED: Generated contextual answer")
    print(f"\n📝 Sample AI Answer:")
    print("-" * 70)
    print(answer)
    print("-" * 70)
    
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
    exit(1)

# Test 6: Check MongoDB Connection
print("\n📋 TEST 6: Checking MongoDB connection...")
try:
    from pymongo import MongoClient
    
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        print("⚠️  WARNING: MONGO_URI not found in .env")
        print("   AI features will work, but database features won't")
    else:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        db = client["citizen_portal"]
        services_count = db["services"].count_documents({})
        
        print(f"✅ PASSED: MongoDB connected")
        print(f"   Database: citizen_portal")
        print(f"   Services: {services_count} documents")
        
        if services_count == 0:
            print("\n⚠️  WARNING: No services in database")
            print("   Run: python seed_data.py")
        
except Exception as e:
    print(f"⚠️  WARNING: MongoDB connection issue: {str(e)}")
    print("   AI search will still work, but won't load from database")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print("✅ Gemini API: Working")
print("✅ Text Generation: Working")
print("✅ Contextual Answers: Working")
print("✅ Government Service Queries: Working")

print("\n🎉 ALL AI FEATURES ARE OPERATIONAL!")
print("\n📝 Next steps:")
print("1. Run: python app.py")
print("2. Open: http://localhost:5000")
print("3. Try AI search: 'How to renew passport?'")
print("\n💡 Free Tier Limits:")
print("   - 60 requests per minute")
print("   - 1,500 requests per day")
print("   - Check usage: https://makersuite.google.com/app/apikey")
print("=" * 70)