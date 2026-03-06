#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class EzPartsAPITester:
    def __init__(self):
        # Use the public URL from frontend/.env
        self.base_url = "https://kimi-dialog-preview.preview.emergentagent.com/api"
        self.session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        
        if success:
            self.tests_passed += 1
        else:
            self.failed_tests.append({"name": name, "details": details})

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f" | Message: {data.get('message', '')}"
            self.log_test("Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {str(e)}")
            return False

    def test_get_categories(self):
        """Test categories endpoint"""
        try:
            response = requests.get(f"{self.base_url}/categories", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                categories_count = len(data)
                expected_categories = ["Engine", "Brakes", "Suspension", "Electrical", "Transmission", "Exhaust"]
                found_categories = [cat.get("name") for cat in data]
                
                categories_present = all(cat in found_categories for cat in expected_categories)
                success = categories_present and categories_count >= 6
                
                details = f"Status: {response.status_code} | Categories: {categories_count} | Expected categories present: {categories_present}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Categories", success, details)
            return success, data if success else []
        except Exception as e:
            self.log_test("Get Categories", False, f"Error: {str(e)}")
            return False, []

    def test_get_parts(self):
        """Test parts endpoint - basic fetch"""
        try:
            response = requests.get(f"{self.base_url}/parts", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                parts_count = len(data)
                success = parts_count >= 5  # Should have sample parts
                
                # Check first part structure
                if data:
                    first_part = data[0]
                    required_fields = ["id", "name", "part_number", "category", "type", "brand", "price", "supplier"]
                    has_required_fields = all(field in first_part for field in required_fields)
                    success = success and has_required_fields
                    
                    details = f"Status: {response.status_code} | Parts: {parts_count} | Required fields: {has_required_fields}"
                else:
                    details = f"Status: {response.status_code} | No parts returned"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Parts", success, details)
            return success, data if success else []
        except Exception as e:
            self.log_test("Get Parts", False, f"Error: {str(e)}")
            return False, []

    def test_search_parts(self):
        """Test parts search functionality"""
        try:
            # Test search by name
            response = requests.get(f"{self.base_url}/parts?search=brake", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                parts_count = len(data)
                
                # Verify search results contain brake-related parts
                brake_parts = [p for p in data if "brake" in p.get("name", "").lower() or 
                             "brake" in p.get("description", "").lower() or
                             "brake" in p.get("category", "").lower()]
                
                search_working = len(brake_parts) > 0
                success = search_working
                details = f"Status: {response.status_code} | Results: {parts_count} | Brake-related: {len(brake_parts)}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Search Parts", success, details)
            return success
        except Exception as e:
            self.log_test("Search Parts", False, f"Error: {str(e)}")
            return False

    def test_filter_parts(self):
        """Test parts filtering by type and category"""
        try:
            # Test OEM filter
            response = requests.get(f"{self.base_url}/parts?type=OEM", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                oem_parts = [p for p in data if p.get("type") == "OEM"]
                filter_working = len(oem_parts) == len(data) and len(data) > 0
                
                details = f"Status: {response.status_code} | OEM parts: {len(data)} | Filter working: {filter_working}"
                success = filter_working
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Filter Parts by Type", success, details)
            return success
        except Exception as e:
            self.log_test("Filter Parts by Type", False, f"Error: {str(e)}")
            return False

    def test_get_single_part(self, parts_data):
        """Test getting a single part by ID"""
        if not parts_data:
            self.log_test("Get Single Part", False, "No parts available to test")
            return False
        
        try:
            part_id = parts_data[0]["id"]
            response = requests.get(f"{self.base_url}/parts/{part_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                correct_part = data.get("id") == part_id
                success = correct_part
                details = f"Status: {response.status_code} | Correct part returned: {correct_part}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Single Part", success, details)
            return success
        except Exception as e:
            self.log_test("Get Single Part", False, f"Error: {str(e)}")
            return False

    def test_get_suppliers(self):
        """Test suppliers endpoint"""
        try:
            response = requests.get(f"{self.base_url}/suppliers", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                suppliers_count = len(data)
                
                # Check supplier structure
                if data:
                    first_supplier = data[0]
                    required_fields = ["id", "name", "location", "state", "specialties", "rating"]
                    has_required_fields = all(field in first_supplier for field in required_fields)
                    success = suppliers_count >= 3 and has_required_fields
                    
                    details = f"Status: {response.status_code} | Suppliers: {suppliers_count} | Required fields: {has_required_fields}"
                else:
                    details = f"Status: {response.status_code} | No suppliers returned"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Suppliers", success, details)
            return success
        except Exception as e:
            self.log_test("Get Suppliers", False, f"Error: {str(e)}")
            return False

    def test_favorites_endpoints(self, parts_data):
        """Test favorites CRUD operations"""
        if not parts_data:
            self.log_test("Favorites Operations", False, "No parts available to test")
            return False
        
        try:
            part_id = parts_data[0]["id"]
            
            # Test add favorite
            add_response = requests.post(f"{self.base_url}/favorites", 
                                       json={"part_id": part_id}, timeout=10)
            add_success = add_response.status_code == 200
            
            if not add_success:
                self.log_test("Add Favorite", add_success, f"Status: {add_response.status_code}")
                return False
            
            # Test get favorites
            get_response = requests.get(f"{self.base_url}/favorites", timeout=10)
            get_success = get_response.status_code == 200
            
            if get_success:
                favorites = get_response.json()
                favorite_found = any(f.get("part", {}).get("id") == part_id for f in favorites)
                get_success = favorite_found
            
            # Test remove favorite
            remove_response = requests.delete(f"{self.base_url}/favorites/{part_id}", timeout=10)
            remove_success = remove_response.status_code == 200
            
            overall_success = add_success and get_success and remove_success
            details = f"Add: {add_response.status_code} | Get: {get_response.status_code} | Remove: {remove_response.status_code}"
            
            self.log_test("Favorites Operations", overall_success, details)
            return overall_success
        except Exception as e:
            self.log_test("Favorites Operations", False, f"Error: {str(e)}")
            return False

    def test_ai_chat(self):
        """Test AI chat endpoint"""
        try:
            chat_data = {
                "session_id": self.session_id,
                "message": "What are the best brake pads for a Ford F-150?"
            }
            
            response = requests.post(f"{self.base_url}/chat", 
                                   json=chat_data, timeout=30)  # Longer timeout for AI
            success = response.status_code == 200
            
            if success:
                data = response.json()
                has_response = "response" in data and len(data["response"]) > 10
                correct_session = data.get("session_id") == self.session_id
                success = has_response and correct_session
                
                details = f"Status: {response.status_code} | Has response: {has_response} | Session match: {correct_session}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("AI Chat", success, details)
            return success
        except Exception as e:
            self.log_test("AI Chat", False, f"Error: {str(e)}")
            return False

    def test_chat_history(self):
        """Test chat history endpoints"""
        try:
            # Get chat history
            response = requests.get(f"{self.base_url}/chat/{self.session_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                has_messages = len(data) > 0
                details = f"Status: {response.status_code} | Messages: {len(data)}"
                success = has_messages  # Should have messages from previous chat test
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Chat History", success, details)
            
            # Test clear chat history
            clear_response = requests.delete(f"{self.base_url}/chat/{self.session_id}", timeout=10)
            clear_success = clear_response.status_code == 200
            
            self.log_test("Clear Chat History", clear_success, f"Status: {clear_response.status_code}")
            
            return success and clear_success
        except Exception as e:
            self.log_test("Chat History", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🔍 Starting EzParts API Tests...")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test basic connectivity
        if not self.test_root_endpoint():
            print("❌ Critical: Root endpoint failed - stopping tests")
            return self.get_summary()
        
        # Test categories
        categories_success, categories_data = self.test_get_categories()
        
        # Test parts endpoints
        parts_success, parts_data = self.test_get_parts()
        self.test_search_parts()
        self.test_filter_parts()
        
        if parts_data:
            self.test_get_single_part(parts_data)
            self.test_favorites_endpoints(parts_data)
        
        # Test suppliers
        self.test_get_suppliers()
        
        # Test AI chat (requires valid API key)
        self.test_ai_chat()
        self.test_chat_history()
        
        return self.get_summary()
    
    def get_summary(self):
        """Get test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print(f"Total tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test['name']}: {test['details']}")
        
        return {
            "total_tests": self.tests_run,
            "passed": self.tests_passed,
            "failed": len(self.failed_tests),
            "success_rate": self.tests_passed/self.tests_run*100 if self.tests_run > 0 else 0,
            "failed_tests": self.failed_tests
        }


def main():
    """Main test function"""
    tester = EzPartsAPITester()
    summary = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())