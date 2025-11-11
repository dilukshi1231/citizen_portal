"""
Complete System Verification Tool
Checks all components of the Citizen Services Portal
Run: python system_verification.py
"""

import os
import sys
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
import importlib.util

load_dotenv()

class SystemVerifier:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def log_success(self, msg):
        self.successes.append(f"✅ {msg}")
        print(f"✅ {msg}")
    
    def log_warning(self, msg):
        self.warnings.append(f"⚠️  {msg}")
        print(f"⚠️  {msg}")
    
    def log_issue(self, msg):
        self.issues.append(f"❌ {msg}")
        print(f"❌ {msg}")
    
    def check_environment(self):
        """Check .env configuration"""
        print("\n" + "="*70)
        print("🔧 CHECKING ENVIRONMENT CONFIGURATION")
        print("="*70)
        
        required_vars = {
            'MONGO_URI': 'MongoDB connection',
            'FLASK_SECRET': 'Flask secret key',
            'GROQ_API_KEY': 'Groq AI API (optional but recommended)',
        }
        
        for var, desc in required_vars.items():
            value = os.getenv(var)
            if value:
                self.log_success(f"{var} configured ({desc})")
            else:
                if var == 'GROQ_API_KEY':
                    self.log_warning(f"{var} not set - AI chat will not work")
                else:
                    self.log_issue(f"{var} missing - {desc}")
    
    def check_database(self):
        """Check MongoDB connection and collections"""
        print("\n" + "="*70)
        print("🗄️  CHECKING DATABASE")
        print("="*70)
        
        try:
            client = MongoClient(os.getenv("MONGO_URI"))
            db = client["citizen_portal"]
            
            # Test connection
            client.server_info()
            self.log_success("MongoDB connection successful")
            
            # Check collections
            collections = {
                'services': 'Service data',
                'users': 'User accounts',
                'admins': 'Admin accounts',
                'engagements': 'Analytics data',
                'categories': 'Service categories',
                'officers': 'Government officers',
                'ads': 'Announcements',
                'products': 'Store products',
                'orders': 'Store orders',
                'payments': 'Payment records',
                'training_programs': 'Training programs',
                'enrollments': 'Training enrollments'
            }
            
            for coll_name, desc in collections.items():
                coll = db[coll_name]
                count = coll.count_documents({})
                
                if count > 0:
                    self.log_success(f"Collection '{coll_name}': {count} documents ({desc})")
                else:
                    self.log_warning(f"Collection '{coll_name}' is empty ({desc})")
            
        except Exception as e:
            self.log_issue(f"Database connection failed: {e}")
    
    def check_files(self):
        """Check critical files"""
        print("\n" + "="*70)
        print("📁 CHECKING FILES")
        print("="*70)
        
        critical_files = {
            'app.py': 'Main application',
            'seed_data.py': 'Data seeding',
            'recommendation_engine.py': 'Recommendation engine',
            'ml_recommendations.py': 'ML recommendations',
            'build_ai_index.py': 'AI index builder',
            'templates/index.html': 'Main page',
            'templates/chatbot.html': 'AI chatbot',
            'templates/admin.html': 'Admin dashboard',
            'templates/store.html': 'Public store',
            'templates/training.html': 'Training programs',
            'static/script.js': 'Main JavaScript',
            'static/chatbot.js': 'Chatbot JavaScript',
            'static/store.js': 'Store JavaScript',
            'static/admin.js': 'Admin JavaScript',
            'static/style.css': 'Main styles'
        }
        
        for file_path, desc in critical_files.items():
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size / 1024
                self.log_success(f"{file_path} exists ({size:.1f} KB) - {desc}")
            else:
                self.log_issue(f"{file_path} MISSING - {desc}")
    
    def check_ai_index(self):
        """Check AI search index"""
        print("\n" + "="*70)
        print("🤖 CHECKING AI SEARCH INDEX")
        print("="*70)
        
        index_files = {
            'data/faiss.index': 'FAISS vector index',
            'data/faiss_meta.json': 'Search metadata',
            'data/embeddings.npy': 'Fallback embeddings'
        }
        
        for file_path, desc in index_files.items():
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size / 1024
                self.log_success(f"{file_path} exists ({size:.1f} KB) - {desc}")
            else:
                self.log_warning(f"{file_path} not found - Run: python build_ai_index.py")
    
    def check_dependencies(self):
        """Check Python dependencies"""
        print("\n" + "="*70)
        print("📦 CHECKING DEPENDENCIES")
        print("="*70)
        
        required_packages = {
            'flask': 'Web framework',
            'pymongo': 'MongoDB driver',
            'bcrypt': 'Password hashing',
            'sentence_transformers': 'AI embeddings',
            'groq': 'Groq AI client',
            'numpy': 'Numerical computing',
            'pandas': 'Data analysis',
            'sklearn': 'Machine learning'
        }
        
        optional_packages = {
            'faiss': 'Vector search (optional)',
        }
        
        for package, desc in required_packages.items():
            spec = importlib.util.find_spec(package)
            if spec:
                self.log_success(f"{package} installed - {desc}")
            else:
                self.log_issue(f"{package} NOT installed - {desc}")
        
        for package, desc in optional_packages.items():
            spec = importlib.util.find_spec(package)
            if spec:
                self.log_success(f"{package} installed - {desc}")
            else:
                self.log_warning(f"{package} not installed - {desc}")
    
    def check_admin_account(self):
        """Check admin account exists"""
        print("\n" + "="*70)
        print("👤 CHECKING ADMIN ACCOUNT")
        print("="*70)
        
        try:
            client = MongoClient(os.getenv("MONGO_URI"))
            db = client["citizen_portal"]
            admins_col = db["admins"]
            
            admin = admins_col.find_one({"username": "admin"})
            if admin:
                self.log_success("Admin account exists (username: admin)")
                print("   ℹ️  Default password: admin123 (change in production!)")
            else:
                self.log_warning("No admin account - will be created on first run")
                
        except Exception as e:
            self.log_warning(f"Could not check admin account: {e}")
    
    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        
        print(f"\n✅ Successes: {len(self.successes)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Issues: {len(self.issues)}")
        
        if self.issues:
            print("\n🔴 CRITICAL ISSUES (Must fix):")
            for issue in self.issues:
                print(f"   {issue}")
        
        if self.warnings:
            print("\n🟡 WARNINGS (Recommended to fix):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        print("\n" + "="*70)
        print("📋 NEXT STEPS")
        print("="*70)
        
        if self.issues:
            print("\n1. Fix critical issues listed above")
            print("2. Run verification again: python system_verification.py")
        else:
            print("\n✅ System appears healthy!")
            print("\nRecommended actions:")
            
            if any('AI index' in w for w in self.warnings):
                print("   • Build AI index: python build_ai_index.py")
            
            if any('empty' in w.lower() for w in self.warnings):
                print("   • Seed database: python seed_data.py")
                print("   • Migrate database: python migrate_db.py")
                print("   • Add products: python seed_store_products.py")
                print("   • Add customers: python sample_customers.py")
            
            print("\nTo start the application:")
            print("   python app.py")
            
            print("\nAccess points:")
            print("   • Main portal: http://localhost:5000/")
            print("   • AI Chatbot: http://localhost:5000/chatbot")
            print("   • Admin panel: http://localhost:5000/admin")
            print("   • Public store: http://localhost:5000/store")
            print("   • Training: http://localhost:5000/training")
        
        print("="*70)
        
        return len(self.issues) == 0

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║        CITIZEN SERVICES PORTAL - SYSTEM VERIFICATION              ║
║                    Complete System Check                          ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    verifier = SystemVerifier()
    
    verifier.check_environment()
    verifier.check_dependencies()
    verifier.check_database()
    verifier.check_files()
    verifier.check_ai_index()
    verifier.check_admin_account()
    
    success = verifier.generate_report()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()