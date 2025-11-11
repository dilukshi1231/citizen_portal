#!/bin/bash

# Complete System Setup Script
# Run: bash complete_setup.sh

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║    CITIZEN SERVICES PORTAL - COMPLETE SETUP                       ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "📦 Installing dependencies..."
echo "   This may take a few minutes..."

pip install flask flask-cors pymongo python-dotenv bcrypt groq > /dev/null 2>&1
echo -e "${GREEN}✅ Core dependencies installed${NC}"

pip install sentence-transformers numpy pandas scikit-learn > /dev/null 2>&1
echo -e "${GREEN}✅ ML dependencies installed${NC}"

# Try to install FAISS (optional)
pip install faiss-cpu > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ FAISS installed (vector search enabled)${NC}"
else
    echo -e "${YELLOW}⚠️  FAISS not installed (will use fallback mode)${NC}"
fi

# Check .env file
echo ""
echo "🔧 Checking configuration..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
MONGO_URI="mongodb+srv://raveen:06ScoF5w0637WpnK@cluster1.sphcfzq.mongodb.net/"
FLASK_SECRET="ec3e37f0cf076567cf6d777982725aaee868755a386d44877ba5510c77c55616"
ADMIN_PWD="admin123"
PORT=5000
DEBUG=True
GROQ_API_KEY="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"
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Create data directory
mkdir -p data
echo -e "${GREEN}✅ Data directory ready${NC}"

# Run verification
echo ""
echo "🔍 Running system verification..."
python system_verification.py

# Check verification result
if [ $? -eq 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ SETUP COMPLETE                              ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📋 Next steps:"
    echo ""
    echo "1. Seed the database:"
    echo "   python seed_data.py"
    echo "   python migrate_db.py"
    echo "   python seed_store_products.py"
    echo "   python sample_customers.py"
    echo ""
    echo "2. Build AI search index:"
    echo "   python build_ai_index.py"
    echo ""
    echo "3. Start the application:"
    echo "   python app.py"
    echo ""
    echo "4. Access the portal:"
    echo "   • Main: http://localhost:5000/"
    echo "   • Admin: http://localhost:5000/admin (admin/admin123)"
    echo "   • Chatbot: http://localhost:5000/chatbot"
    echo "   • Store: http://localhost:5000/store"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Setup completed with issues${NC}"
    echo "   Please review the verification results above"
    echo ""
fi