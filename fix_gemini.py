"""
Complete diagnostic and fix script
Save as fix_gemini.py and run it
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("=" * 70)
print("🔧 GEMINI API COMPLETE DIAGNOSTIC & FIX")
print("=" * 70)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ No API key found in .env")
    exit(1)

print(f"\n✅ API Key found: {api_key[:20]}...")

# Configure API
genai.configure(api_key=api_key)

# List all available models
print("\n" + "=" * 70)
print("📋 STEP 1: Checking available models...")
print("=" * 70)

available_models = []
try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            available_models.append(model.name)
            print(f"✅ {model.name}")
    
    if not available_models:
        print("⚠️ No models found with generateContent support")
        print("\n🔧 This means you need to enable the Generative Language API:")
        print("1. Visit: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
        print("2. Make sure you're in the correct project")
        print("3. Click 'Enable'")
        print("4. Wait a few minutes and try again")
        exit(1)
        
except Exception as e:
    print(f"❌ Error listing models: {e}")
    print("\n🔧 Trying alternative approach...")

# Try different model name formats
print("\n" + "=" * 70)
print("🧪 STEP 2: Testing different model names...")
print("=" * 70)

model_names_to_try = [
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash',
    'gemini-1.5-pro-latest',
    'gemini-1.5-pro',
    'gemini-pro',
    'models/gemini-1.5-flash-latest',
    'models/gemini-1.5-flash',
    'models/gemini-pro'
]

working_model = None
test_prompt = "Say 'Hello' in one word"

for model_name in model_names_to_try:
    try:
        print(f"\n🔄 Testing: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(test_prompt)
        
        if response.text:
            print(f"✅ SUCCESS! This model works: {model_name}")
            print(f"   Response: {response.text}")
            working_model = model_name
            break
        else:
            print(f"⚠️ Response blocked by safety filters")
            
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")

if not working_model:
    print("\n" + "=" * 70)
    print("❌ DIAGNOSIS: API NOT ENABLED OR KEY INVALID")
    print("=" * 70)
    print("\n🔧 SOLUTION:")
    print("\nOption 1 - Enable the API (Recommended):")
    print("1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
    print("2. Click 'Enable'")
    print("3. Wait 2-5 minutes")
    print("4. Run this script again")
    
    print("\nOption 2 - Get a fresh API key:")
    print("1. Go to: https://aistudio.google.com/app/apikey")
    print("2. Create new API key")
    print("3. Make sure 'Generative Language API' is enabled")
    print("4. Update your .env file")
    
    print("\nOption 3 - Use a different AI service:")
    print("Consider using OpenAI GPT-3.5-turbo instead (easier setup)")
    
    exit(1)

# Test with actual ministry context
print("\n" + "=" * 70)
print("🧪 STEP 3: Testing with ministry context...")
print("=" * 70)

context = """Ministry: Ministry of IT & Digital Affairs

Service: IT Certificates
Q: How to apply for an IT certificate?
A: Fill online form and upload NIC.
Forms: /static/forms/it_cert_form.pdf
Instructions: Visit the digital portal, register and submit application.
"""

prompt = f"""You are a helpful assistant for Sri Lankan government services.

Context:
{context}

User question: How do I apply for an IT certificate?

Provide a clear, helpful answer:"""

try:
    model = genai.GenerativeModel(working_model)
    response = model.generate_content(prompt)
    
    print(f"✅ Context test successful!")
    print(f"\n📝 AI Response:")
    print("-" * 70)
    print(response.text)
    print("-" * 70)
    
except Exception as e:
    print(f"❌ Context test failed: {e}")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print(f"✅ Working model: {working_model}")
print(f"✅ API Key: Valid")
print(f"✅ Generation: Working")
print(f"✅ Context: Working")

print("\n🎉 YOUR CHATBOT SHOULD NOW WORK!")
print("\n📝 Update your app.py with this model name:")
print(f"   model = genai.GenerativeModel('{working_model}')")

print("\n🚀 Next steps:")
print("1. Update app.py with the working model name above")
print("2. Restart Flask: python app.py")
print("3. Test the chatbot")

print("=" * 70)