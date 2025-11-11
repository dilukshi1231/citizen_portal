"""
Complete System Functionality Test
Tests all major features
Run: python test_system.py (while app.py is running)
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

class SystemTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test(self, name, func):
        """Run a test"""
        print(f"\n🧪 Testing: {name}")
        try:
            func()
            print(f"   ✅ PASSED")
            self.passed += 1
            self.results.append((name, "PASSED", None))
        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            self.failed += 1
            self.results.append((name, "FAILED", str(e)))
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            self.failed += 1
            self.results.append((name, "ERROR", str(e)))
    
    def test_main_page(self):
        """Test main portal page"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200, "Main page not loading"
        assert "Citizen Services" in response.text, "Page content incorrect"
    
    def test_chatbot_page(self):
        """Test chatbot page"""
        response = requests.get(f"{BASE_URL}/chatbot", allow_redirects=False)
        # Should redirect to login or show page
        assert response.status_code in [200, 302], "Chatbot page not accessible"
    
    def test_store_page(self):
        """Test store page"""
        response = requests.get(f"{BASE_URL}/store")
        assert response.status_code == 200, "Store page not loading"
    
    def test_training_page(self):
        """Test training page"""
        response = requests.get(f"{BASE_URL}/training", allow_redirects=False)
        # Should redirect to login or show page
        assert response.status_code in [200, 302], "Training page not accessible"
    
    def test_api_services(self):
        """Test services API"""
        response = requests.get(f"{BASE_URL}/api/services")
        assert response.status_code == 200, "Services API failed"
        data = response.json()
        assert isinstance(data, list), "Services should return list"
        assert len(data) > 0, "No services found"
    
    def test_api_categories(self):
        """Test categories API"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200, "Categories API failed"
        data = response.json()
        assert isinstance(data, list), "Categories should return list"
    
    def test_api_officers(self):
        """Test officers API"""
        response = requests.get(f"{BASE_URL}/api/officers")
        assert response.status_code == 200, "Officers API failed"
        data = response.json()
        assert isinstance(data, list), "Officers should return list"
    
    def test_api_ads(self):
        """Test ads API"""
        response = requests.get(f"{BASE_URL}/api/ads")
        assert response.status_code == 200, "Ads API failed"
        data = response.json()
        assert isinstance(data, list), "Ads should return list"
    
    def test_api_training_programs(self):
        """Test training programs API"""
        response = requests.get(f"{BASE_URL}/api/training-programs")
        assert response.status_code == 200, "Training programs API failed"
        data = response.json()
        assert isinstance(data, list), "Training programs should return list"
    
    def test_api_store_products(self):
        """Test store products API"""
        response = requests.get(f"{BASE_URL}/api/store/products")
        assert response.status_code == 200, "Store products API failed"
        data = response.json()
        assert isinstance(data, list), "Products should return list"
    
    def test_api_store_categories(self):
        """Test store categories API"""
        response = requests.get(f"{BASE_URL}/api/store/categories")
        assert response.status_code == 200, "Store categories API failed"
        data = response.json()
        assert "categories" in data, "Categories key missing"
    
    def test_ai_search(self):
        """Test AI search"""
        response = requests.post(
            f"{BASE_URL}/api/ai/search",
            json={
                "query": "how to apply for exams",
                "top_k": 3,
                "language": "en"
            }
        )
        assert response.status_code == 200, "AI search failed"
        data = response.json()
        assert "results" in data, "Results key missing"
        assert isinstance(data["results"], list), "Results should be list"
    
    def test_engagement_logging(self):
        """Test engagement logging"""
        response = requests.post(
            f"{BASE_URL}/api/engagement",
            json={
                "user_id": "test_user",
                "age": 25,
                "job": "Student",
                "question_clicked": "Test question",
                "service": "Test service"
            }
        )
        assert response.status_code == 200, "Engagement logging failed"
        data = response.json()
        assert data["status"] == "ok", "Engagement status not ok"
    
    def test_admin_login_page(self):
        """Test admin login page"""
        response = requests.get(f"{BASE_URL}/admin/login")
        assert response.status_code == 200, "Admin login page not loading"
    
    def test_user_register_page(self):
        """Test user registration page"""
        response = requests.get(f"{BASE_URL}/user/register")
        assert response.status_code == 200, "User register page not loading"
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*70)
        print("📊 TEST RESULTS SUMMARY")
        print("="*70)
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n✅ Passed: {self.passed}/{total} ({pass_rate:.1f}%)")
        print(f"❌ Failed: {self.failed}/{total}")
        
        if self.failed > 0:
            print("\n❌ Failed Tests:")
            for name, status, error in self.results:
                if status != "PASSED":
                    print(f"   • {name}")
                    if error:
                        print(f"     Error: {error}")
        
        print("\n" + "="*70)
        
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED!")
            print("\nSystem is fully functional and ready for use.")
        else:
            print("⚠️  SOME TESTS FAILED")
            print("\nPlease review the errors above and fix the issues.")
        
        print("="*70)
        
        return self.failed == 0

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║        CITIZEN SERVICES PORTAL - SYSTEM TESTS                     ║
║              Complete Functionality Testing                        ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    print("⚠️  Make sure app.py is running before starting tests!")
    print("   Run: python app.py")
    input("\nPress Enter when ready to start tests...")
    
    tester = SystemTester()
    
    print("\n" + "="*70)
    print("🧪 RUNNING TESTS")
    print("="*70)
    
    # Page Tests
    print("\n📄 TESTING PAGES")
    tester.test("Main Portal Page", tester.test_main_page)
    tester.test("Chatbot Page", tester.test_chatbot_page)
    tester.test("Store Page", tester.test_store_page)
    tester.test("Training Page", tester.test_training_page)
    tester.test("Admin Login Page", tester.test_admin_login_page)
    tester.test("User Register Page", tester.test_user_register_page)
    
    # API Tests
    print("\n🔌 TESTING APIS")
    tester.test("Services API", tester.test_api_services)
    tester.test("Categories API", tester.test_api_categories)
    tester.test("Officers API", tester.test_api_officers)
    tester.test("Ads API", tester.test_api_ads)
    tester.test("Training Programs API", tester.test_api_training_programs)
    tester.test("Store Products API", tester.test_api_store_products)
    tester.test("Store Categories API", tester.test_api_store_categories)
    
    # Advanced Features
    print("\n🤖 TESTING ADVANCED FEATURES")
    tester.test("AI Search", tester.test_ai_search)
    tester.test("Engagement Logging", tester.test_engagement_logging)
    
    # Generate report
    success = tester.generate_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())