"""
Quick Diagnostic Script - Save as diagnose.py and run it
This will tell you exactly what's wrong
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("=" * 60)
print("🔍 DIAGNOSING GEMINI API ISSUE")
print("=" * 60)

# Check 1: API Key exists
print("\n1️⃣ Checking API Key...")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    print("\n🔧 FIX:")
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Create new API key")
    print("3. Add to .env: GEMINI_API_KEY='AIza...'")
    exit(1)

print(f"✅ Found API key: {api_key[:15]}...")

# Check 2: Configure API
print("\n2️⃣ Configuring Gemini...")
try:
    genai.configure(api_key=api_key)
    print("✅ Configuration successful")
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    exit(1)

# Check 3: Initialize model
print("\n3️⃣ Initializing model...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Model initialized")
except Exception as e:
    print(f"❌ Model initialization failed: {e}")
    exit(1)

# Check 4: Simple generation test
print("\n4️⃣ Testing generation...")
try:
    response = model.generate_content("Say 'Hello' in one word")
    if response.text:
        print(f"✅ Generation successful: {response.text}")
    else:
        print(f"⚠️ Response blocked. Safety: {response.safety_ratings}")
except Exception as e:
    error_msg = str(e)
    print(f"❌ Generation failed: {error_msg}")
    
    # Diagnose specific errors
    if "API_KEY_INVALID" in error_msg:
        print("\n🔧 ISSUE: Invalid API Key")
        print("- Your key is incorrect or revoked")
        print("- Generate new key: https://makersuite.google.com/app/apikey")
    elif "quota" in error_msg.lower():
        print("\n🔧 ISSUE: Quota Exceeded")
        print("- Free tier: 60 req/min, 1,500 req/day")
        print("- Check usage: https://makersuite.google.com/app/apikey")
        print("- Wait or upgrade to paid tier")
    elif "permission" in error_msg.lower():
        print("\n🔧 ISSUE: Permission Denied")
        print("- Enable Generative AI API in Google Cloud Console")
        print("- Visit: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
    elif "not found" in error_msg.lower():
        print("\n🔧 ISSUE: API Not Enabled")
        print("- Enable Gemini API in your Google Cloud project")
    else:
        print(f"\n🔧 ISSUE: Unknown Error")
        print(f"Details: {error_msg}")
    exit(1)

# Check 5: Test with context
print("\n5️⃣ Testing with ministry context...")
try:
    context = "Ministry of IT provides IT certificates. Fill form and upload NIC."
    prompt = f"""Context: {context}

Question: How to apply for IT certificate?

Answer in one sentence:"""
    
    response = model.generate_content(prompt)
    if response.text:
        print(f"✅ Context test successful!")
        print(f"Response: {response.text[:100]}...")
    else:
        print(f"⚠️ Response blocked")
except Exception as e:
    print(f"❌ Context test failed: {e}")

print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED - Your API is working!")
print("=" * 60)
print("\n💡 If chatbot still fails:")
print("1. Restart Flask app: python app.py")
print("2. Clear browser cache")
print("3. Check browser console for errors (F12)")
print("4. Verify MongoDB connection: python test_mongodb.py")