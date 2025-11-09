# 🆓 Google Gemini API - Free Setup Guide

## Why Gemini?

✅ **Completely FREE** - 60 requests per minute  
✅ **No credit card required**  
✅ **Better than GPT-3.5** in many tasks  
✅ **Multilingual support** - Perfect for Sinhala/Tamil  
✅ **Easy to set up** - 5 minutes  

---

## 🚀 Step 1: Get Free API Key

### **1. Visit Google AI Studio**
Go to: https://makersuite.google.com/app/apikey

### **2. Sign in with Google**
Use any Gmail account (free)

### **3. Click "Create API Key"**
- Click **"Create API key in new project"**
- Your key will appear immediately
- Copy the key (starts with `AIza...`)

### **4. Save Your API Key**
⚠️ **IMPORTANT**: Copy and save it immediately - you won't see it again!

---

## 🔐 Step 2: Configure Your App

### **Add to `.env` file:**

```env
# Google Gemini API (FREE!)
GEMINI_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# MongoDB (existing)
MONGO_URI="mongodb+srv://your-connection-string"
FLASK_SECRET="your-secret-key"
ADMIN_PWD="admin123"
PORT=5000
```

---

## ✅ Step 3: Install Dependencies

```bash
# Install Gemini SDK
pip install google-generativeai==0.3.2

# Or install all AI dependencies
pip install -r requirements_ai.txt
```

---

## 🧪 Step 4: Test Your Setup

Create `test_gemini.py`:

```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Test
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Say hello in Sinhala and Tamil")

print("✅ Gemini is working!")
print(f"Response: {response.text}")
```

Run it:
```bash
python test_gemini.py
```

**Expected output:**
```
✅ Gemini is working!
Response: Hello in Sinhala: ආයුබෝවන් (Ayubowan)
Hello in Tamil: வணக்கம் (Vanakkam)
```

---

## 📊 Free Tier Limits

| Feature | Free Tier |
|---------|-----------|
| **Requests per minute** | 60 |
| **Requests per day** | 1,500 |
| **Tokens per request** | 32,000 |
| **Cost** | $0 (FREE!) |

**Note**: This is MORE than enough for:
- 90,000 questions per day
- 1 million+ per month
- Completely FREE forever!

---

## 🆚 Comparison: Gemini vs Others

| Feature | Gemini (Free) | OpenAI GPT-4 | Claude |
|---------|---------------|--------------|--------|
| **Cost** | ✅ FREE | ❌ $0.03/1K tokens | ❌ $0.015/1K tokens |
| **Setup** | ✅ No credit card | ❌ Requires payment | ❌ Requires payment |
| **Rate Limit** | ✅ 60/min | ❌ 3/min (free tier) | ❌ No free tier |
| **Multilingual** | ✅ Excellent | ✅ Good | ✅ Good |
| **Quality** | ✅ GPT-3.5 level | ✅ Best | ✅ Best |

**Winner for this project: Gemini** 🏆

---

## 🔄 Alternative: 100% Offline (No API Needed!)

If you don't want to use any API at all:

### **Option 1: Use Hugging Face (Runs locally, FREE)**

```python
from transformers import pipeline

# Loads once, runs forever - no API!
llm = pipeline("text2text-generation", model="google/flan-t5-small")

answer = llm("How to renew passport?", max_length=200)
print(answer[0]['generated_text'])
```

### **Option 2: Use Ollama (Runs locally, more powerful)**

```bash
# Install Ollama (FREE)
curl https://ollama.ai/install.sh | sh

# Download Llama 2 (FREE)
ollama pull llama2

# Use in Python
pip install ollama-python
```

```python
import ollama

response = ollama.chat(model='llama2', messages=[
  {'role': 'user', 'content': 'How to renew passport in Sri Lanka?'}
])
print(response['message']['content'])
```

---

## 🎯 Recommended Setup for Your Project

### **For Best Results (Recommended):**

```env
# Use Gemini for answer generation (FREE!)
GEMINI_API_KEY="your-key-here"

# Embedding model runs locally (no API needed)
# FAISS search runs locally (no API needed)
```

**This gives you:**
- ✅ High-quality AI answers (Gemini)
- ✅ Fast semantic search (local embeddings)
- ✅ Zero API cost for search (runs on your server)
- ✅ Only pay API cost for final answer generation (FREE with Gemini!)

### **For 100% Offline (No API at all):**

```python
# In ai_search.py, use:
search_engine = LocalLLMSearchEngine()

# This loads:
# - Local embeddings (all-MiniLM-L6-v2)
# - Local LLM (flan-t5-small)
# - FAISS (local vector search)
# 
# Result: 100% FREE, runs on your server, no internet needed!
```

---

## 🔍 Troubleshooting

### **Error: "API key not valid"**

1. Check your API key in `.env`
2. Make sure it starts with `AIza`
3. Regenerate key at https://makersuite.google.com/app/apikey

### **Error: "Quota exceeded"**

You hit the free limit (60/min or 1500/day):
- Wait a few seconds
- Or switch to LocalLLMSearchEngine (no limits!)

### **Error: "Model not found"**

Use the correct model name:
```python
# Correct
model = genai.GenerativeModel('gemini-pro')

# Wrong
model = genai.GenerativeModel('gemini-1.5-pro')  # Not in free tier
```

---

## 📈 Cost Estimation

**Your app will handle:**
- 1000 users/day
- 5 questions each = 5000 questions/day

**Cost with Gemini FREE tier:** $0
**Cost with OpenAI:** $150/month
**Cost with Claude:** $75/month

**Savings: $1,800/year** 💰

---

## 🎓 Next Steps

1. ✅ Get Gemini API key (5 minutes)
2. ✅ Add to `.env` file
3. ✅ Install dependencies: `pip install google-generativeai`
4. ✅ Run test script
5. ✅ Start your AI-powered app!

---

## 📚 Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **Get API Key**: https://makersuite.google.com/app/apikey
- **Python SDK**: https://github.com/google/generative-ai-python
- **Pricing**: https://ai.google.dev/pricing (FREE tier is generous!)

---

**Ready to add FREE AI to your app?** 🚀

Get your API key and let's go!