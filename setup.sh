#!/bin/bash

# Citizen Services Portal - Automated Setup Script
# Run: bash setup.sh

echo "=================================================="
echo "🏛️  CITIZEN SERVICES PORTAL - SETUP"
echo "=================================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version < 3.9" | bc) -eq 1 ]]; then
    echo "❌ Python 3.9+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check .env file
echo "🔐 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# MongoDB Connection
MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"

# Groq AI API (Free tier: groq.com)
GROQ_API_KEY="gsk_..."

# Flask Configuration
FLASK_SECRET="$(openssl rand -hex 32)"
ADMIN_PWD="admin123"
PORT=5000
DEBUG=True

# Optional: Embedding Model
EMBED_MODEL="sentence-transformers/all-MiniLM-L6-v2"
EOF
    echo "✅ .env template created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   1. Add MongoDB URI (from MongoDB Atlas)"
    echo "   2. Add Groq API key (from console.groq.com)"
    echo ""
    echo "Press Enter when done..."
    read
else
    echo "✅ .env file found"
fi
echo ""

# Check if MongoDB URI is set
mongo_uri=$(grep MONGO_URI .env | cut -d '=' -f2 | tr -d '"')
if [[ $mongo_uri == *"username:password"* ]]; then
    echo "❌ Please configure MONGO_URI in .env file"
    exit 1
fi

# Check if Groq API key is set
groq_key=$(grep GROQ_API_KEY .env | cut -d '=' -f2 | tr -d '"')
if [[ $groq_key == "gsk_..." ]]; then
    echo "⚠️  WARNING: GROQ_API_KEY not configured. AI chatbot won't work."
    echo "Get free key at: https://console.groq.com/"
    echo ""
fi

# Test MongoDB connection
echo "🔗 Testing MongoDB connection..."
python test_mongodb.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ MongoDB connection successful"
else
    echo "❌ MongoDB connection failed. Check MONGO_URI in .env"
    exit 1
fi
echo ""

# Seed database
echo "🌱 Seeding database..."
python seed_data.py
if [ $? -eq 0 ]; then
    echo "✅ Database seeded with 20+ ministries"
else
    echo "❌ Database seeding failed"
    exit 1
fi
echo ""

# Build AI index
echo "🤖 Building AI search index..."
python build_ai_index.py
if [ $? -eq 0 ]; then
    echo "✅ AI index built successfully"
else
    echo "⚠️  AI index build failed (may work without FAISS)"
fi
echo ""

# Create data directory
mkdir -p data
echo "✅ Data directory created"
echo ""

# Summary
echo "=================================================="
echo "🎉 SETUP COMPLETE!"
echo "=================================================="
echo ""
echo "📍 Next steps:"
echo ""
echo "1. Start the server:"
echo "   python app.py"
echo ""
echo "2. Access the application:"
echo "   🌐 Public Portal: http://127.0.0.1:5000/"
echo "   🤖 AI Chatbot:    http://127.0.0.1:5000/chatbot"
echo "   👨‍💼 Admin Panel:   http://127.0.0.1:5000/admin"
echo ""
echo "3. Admin credentials:"
echo "   Username: admin"
echo "   Password: $(grep ADMIN_PWD .env | cut -d '=' -f2 | tr -d '"')"
echo ""
echo "=================================================="
echo "📚 Documentation: See README.md"
echo "🐛 Issues: Check troubleshooting section"
echo "=================================================="