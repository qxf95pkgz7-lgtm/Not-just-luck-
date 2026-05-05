#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class LuckyJackAPITester:
    def __init__(self, base_url="https://euro-music-brain.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            self.log_test("API Root", success, details)
            return success
        except Exception as e:
            self.log_test("API Root", False, str(e))
            return False

    def test_dashboard_endpoint(self):
        """Test dashboard endpoint"""
        try:
            response = requests.get(f"{self.api_url}/dashboard", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                # Check required fields
                required_fields = ['total_draws', 'hot_numbers', 'cold_numbers', 'group1_count', 'group2_count']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    success = False
                    details += f", Missing fields: {missing_fields}"
                else:
                    details += f", Total draws: {data['total_draws']}"
                    details += f", Hot numbers: {len(data['hot_numbers'])}"
                    details += f", Cold numbers: {len(data['cold_numbers'])}"
                    
            self.log_test("Dashboard Endpoint", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Dashboard Endpoint", False, str(e))
            return False, {}

    def test_draws_endpoint(self):
        """Test draws endpoint"""
        try:
            response = requests.get(f"{self.api_url}/draws", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Total draws returned: {len(data)}"
                if data:
                    # Check first draw structure
                    first_draw = data[0]
                    required_fields = ['id', 'date', 'numbers', 'families']
                    missing_fields = [field for field in required_fields if field not in first_draw]
                    if missing_fields:
                        success = False
                        details += f", Missing fields in draw: {missing_fields}"
                    else:
                        details += f", Sample draw: {first_draw['date']} - {first_draw['numbers']}"
                        
            self.log_test("Draws Endpoint", success, details)
            return success, response.json() if success else []
        except Exception as e:
            self.log_test("Draws Endpoint", False, str(e))
            return False, []

    def test_patterns_endpoint(self):
        """Test patterns endpoint"""
        try:
            response = requests.get(f"{self.api_url}/patterns", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                required_fields = ['digit_reversals', 'series_patterns']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    success = False
                    details += f", Missing fields: {missing_fields}"
                else:
                    details += f", Digit reversals: {len(data['digit_reversals'])}"
                    details += f", Series patterns: {len(data['series_patterns'])}"
                    
            self.log_test("Patterns Endpoint", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Patterns Endpoint", False, str(e))
            return False, {}

    def test_predictions_endpoint(self):
        """Test predictions endpoint"""
        try:
            response = requests.get(f"{self.api_url}/predictions", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                required_fields = ['suggested_numbers', 'explanations', 'cross_draw_patterns', 'gap_analysis']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    success = False
                    details += f", Missing fields: {missing_fields}"
                else:
                    details += f", Suggested numbers: {data['suggested_numbers']}"
                    details += f", Explanations: {len(data['explanations'])}"
                    details += f", Cross patterns: {len(data['cross_draw_patterns'])}"
                    details += f", Gap analysis: {len(data['gap_analysis'])}"
                    
            self.log_test("Predictions Endpoint", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Predictions Endpoint", False, str(e))
            return False, {}

    def test_create_draw(self):
        """Test creating a new draw"""
        try:
            test_draw = {
                "date": "2026-12-01",
                "draw_number": "TEST123",
                "numbers": [1, 5, 12, 23, 31, 42]
            }
            
            response = requests.post(f"{self.api_url}/draws", json=test_draw, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                required_fields = ['id', 'date', 'numbers', 'families']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    success = False
                    details += f", Missing fields: {missing_fields}"
                else:
                    details += f", Created draw ID: {data['id']}"
                    details += f", Numbers: {data['numbers']}"
                    details += f", Families: {data['families']}"
                    return success, data['id']
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:100]}"
                    
            self.log_test("Create Draw", success, details)
            return success, None
        except Exception as e:
            self.log_test("Create Draw", False, str(e))
            return False, None

    def test_delete_draw(self, draw_id):
        """Test deleting a draw"""
        if not draw_id:
            self.log_test("Delete Draw", False, "No draw ID provided")
            return False
            
        try:
            response = requests.delete(f"{self.api_url}/draws/{draw_id}", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:100]}"
                    
            self.log_test("Delete Draw", success, details)
            return success
        except Exception as e:
            self.log_test("Delete Draw", False, str(e))
            return False

    def test_invalid_draw_creation(self):
        """Test invalid draw creation scenarios"""
        test_cases = [
            {
                "name": "Invalid numbers count",
                "data": {"date": "2026-12-01", "numbers": [1, 2, 3, 4, 5]},  # Only 5 numbers
                "expected_status": 400
            },
            {
                "name": "Numbers out of range",
                "data": {"date": "2026-12-01", "numbers": [1, 2, 3, 4, 5, 50]},  # 50 > 42
                "expected_status": 400
            },
            {
                "name": "Duplicate numbers",
                "data": {"date": "2026-12-01", "numbers": [1, 1, 3, 4, 5, 6]},  # Duplicate 1
                "expected_status": 400
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(f"{self.api_url}/draws", json=test_case["data"], timeout=10)
                success = response.status_code == test_case["expected_status"]
                details = f"Status: {response.status_code}, Expected: {test_case['expected_status']}"
                
                if not success:
                    try:
                        error_data = response.json()
                        details += f", Error: {error_data.get('detail', 'Unknown error')}"
                    except:
                        details += f", Response: {response.text[:100]}"
                        
                self.log_test(f"Invalid Draw - {test_case['name']}", success, details)
            except Exception as e:
                self.log_test(f"Invalid Draw - {test_case['name']}", False, str(e))

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Lucky Jack API Tests...")
        print(f"Testing against: {self.api_url}")
        print("=" * 60)
        
        # Test basic connectivity
        if not self.test_api_root():
            print("❌ API root failed - stopping tests")
            return self.get_summary()
        
        # Test all GET endpoints
        dashboard_success, dashboard_data = self.test_dashboard_endpoint()
        draws_success, draws_data = self.test_draws_endpoint()
        patterns_success, patterns_data = self.test_patterns_endpoint()
        predictions_success, predictions_data = self.test_predictions_endpoint()
        
        # Test CRUD operations
        create_success, draw_id = self.test_create_draw()
        if create_success and draw_id:
            self.test_delete_draw(draw_id)
        
        # Test error handling
        self.test_invalid_draw_creation()
        
        return self.get_summary()

    def get_summary(self):
        """Get test summary"""
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check details above.")
            
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": round((self.tests_passed / self.tests_run) * 100, 1) if self.tests_run > 0 else 0,
            "test_results": self.test_results
        }

def main():
    """Main test runner"""
    tester = LuckyJackAPITester()
    summary = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if summary["passed_tests"] == summary["total_tests"] else 1

if __name__ == "__main__":
    sys.exit(main())