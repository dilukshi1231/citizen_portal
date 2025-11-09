#!/bin/bash

# Quick Setup Script for Citizen Services Portal
# Run: bash setup_quick.sh

echo "========================================"
echo "🚀 QUICK SETUP - Citizen Services Portal"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "Create .env file with:"
    echo "MONGO_URI='your_mongodb_connection_string'"
    echo "GROQ_API_KEY='your_groq_api_key'"
    echo "FLASK_SECRET='$(openssl rand -hex 32)'"
    echo "ADMIN_PWD='admin123'"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Seed database
echo "🌱 Seeding database..."
python seed_data.py
if [ $? -eq 0 ]; then
    echo "✅ Database seeded"
else
    echo "❌ Seeding failed"
    exit 1
fi
echo ""

# Build AI index
echo "🤖 Building AI search index..."
python build_ai_index.py
if [ $? -eq 0 ]; then
    echo "✅ AI index built"
else
    echo "⚠️ AI index build failed (optional)"
fi
echo ""

# Fix admin password
echo "🔐 Setting up admin password..."
python fix_admin_password.py <<EOF
admin123
EOF
echo ""

echo "========================================"
echo "✅ SETUP COMPLETE!"
echo "========================================"
echo ""
echo "🚀 Start the server:"
echo "   python app.py"
echo ""
echo "🌐 Access URLs:"
echo "   Public:  http://127.0.0.1:5000/"
echo "   Chatbot: http://127.0.0.1:5000/chatbot"
echo "   Admin:   http://127.0.0.1:5000/admin"
echo ""
echo "🔑 Admin Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo "========================================"