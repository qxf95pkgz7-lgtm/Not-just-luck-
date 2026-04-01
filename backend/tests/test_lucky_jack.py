"""
Lucky Jack - Swiss Lotto Pattern Analyzer Backend Tests
Tests for master-predictor, draws, and dashboard endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')

class TestMasterPredictor:
    """Tests for /api/master-predictor endpoint"""
    
    def test_master_predictor_returns_main_prediction(self):
        """Test that master-predictor returns 6 main prediction numbers"""
        response = requests.get(f"{BASE_URL}/api/master-predictor")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "main_prediction" in data, "Response should contain main_prediction"
        assert isinstance(data["main_prediction"], list), "main_prediction should be a list"
        assert len(data["main_prediction"]) == 6, f"main_prediction should have 6 numbers, got {len(data['main_prediction'])}"
        
        # Verify all numbers are between 1-42
        for num in data["main_prediction"]:
            assert 1 <= num <= 42, f"Number {num} should be between 1 and 42"
        
        print(f"✓ main_prediction: {data['main_prediction']}")
    
    def test_master_predictor_returns_lucky_prediction(self):
        """Test that master-predictor returns lucky_prediction (1-6)"""
        response = requests.get(f"{BASE_URL}/api/master-predictor")
        assert response.status_code == 200
        
        data = response.json()
        assert "lucky_prediction" in data, "Response should contain lucky_prediction"
        assert isinstance(data["lucky_prediction"], int), "lucky_prediction should be an integer"
        assert 1 <= data["lucky_prediction"] <= 6, f"lucky_prediction should be 1-6, got {data['lucky_prediction']}"
        
        print(f"✓ lucky_prediction: {data['lucky_prediction']}")
    
    def test_master_predictor_returns_lucky_reason(self):
        """Test that master-predictor returns lucky_reason"""
        response = requests.get(f"{BASE_URL}/api/master-predictor")
        assert response.status_code == 200
        
        data = response.json()
        assert "lucky_reason" in data, "Response should contain lucky_reason"
        assert isinstance(data["lucky_reason"], str), "lucky_reason should be a string"
        assert len(data["lucky_reason"]) > 0, "lucky_reason should not be empty"
        
        print(f"✓ lucky_reason: {data['lucky_reason']}")
    
    def test_master_predictor_with_birthday(self):
        """Test master-predictor with birthday parameter"""
        response = requests.get(f"{BASE_URL}/api/master-predictor?birthday=15/08/1990")
        assert response.status_code == 200
        
        data = response.json()
        assert "main_prediction" in data
        assert "lucky_prediction" in data
        assert len(data["main_prediction"]) == 6
        
        # Birthday mode should be present
        if "birthday_mode" in data:
            assert "lucky_numbers" in data["birthday_mode"]
            print(f"✓ Birthday mode active with numbers: {data['birthday_mode']['lucky_numbers'][:4]}")
        else:
            print("✓ Birthday parameter accepted (birthday_mode may not be in response)")
    
    def test_master_predictor_with_name(self):
        """Test master-predictor with name parameter"""
        response = requests.get(f"{BASE_URL}/api/master-predictor?name=John%20Doe")
        assert response.status_code == 200
        
        data = response.json()
        assert "main_prediction" in data
        assert len(data["main_prediction"]) == 6
        
        print(f"✓ Name parameter accepted, prediction: {data['main_prediction']}")
    
    def test_master_predictor_returns_alternate_numbers(self):
        """Test that master-predictor returns alternate_numbers"""
        response = requests.get(f"{BASE_URL}/api/master-predictor")
        assert response.status_code == 200
        
        data = response.json()
        assert "alternate_numbers" in data, "Response should contain alternate_numbers"
        assert isinstance(data["alternate_numbers"], list), "alternate_numbers should be a list"
        
        print(f"✓ alternate_numbers: {data['alternate_numbers']}")
    
    def test_master_predictor_returns_confidence(self):
        """Test that master-predictor returns average_confidence"""
        response = requests.get(f"{BASE_URL}/api/master-predictor")
        assert response.status_code == 200
        
        data = response.json()
        assert "average_confidence" in data, "Response should contain average_confidence"
        
        print(f"✓ average_confidence: {data['average_confidence']}")


class TestDrawsEndpoint:
    """Tests for /api/draws endpoint"""
    
    def test_draws_returns_list(self):
        """Test that draws endpoint returns a list of draws"""
        response = requests.get(f"{BASE_URL}/api/draws")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one draw"
        
        print(f"✓ Total draws: {len(data)}")
    
    def test_draws_contain_required_fields(self):
        """Test that each draw contains required fields"""
        response = requests.get(f"{BASE_URL}/api/draws")
        assert response.status_code == 200
        
        data = response.json()
        first_draw = data[0]
        
        required_fields = ["id", "date", "numbers", "families"]
        for field in required_fields:
            assert field in first_draw, f"Draw should contain {field}"
        
        print(f"✓ First draw: {first_draw['date']} - {first_draw['numbers']}")
    
    def test_draws_contain_lucky_number(self):
        """Test that draws contain lucky_number field"""
        response = requests.get(f"{BASE_URL}/api/draws")
        assert response.status_code == 200
        
        data = response.json()
        first_draw = data[0]
        
        assert "lucky_number" in first_draw, "Draw should contain lucky_number"
        if first_draw["lucky_number"] is not None:
            assert 1 <= first_draw["lucky_number"] <= 6, f"lucky_number should be 1-6, got {first_draw['lucky_number']}"
        
        print(f"✓ lucky_number in first draw: {first_draw['lucky_number']}")
    
    def test_draws_contain_replay_number(self):
        """Test that draws contain replay_number field"""
        response = requests.get(f"{BASE_URL}/api/draws")
        assert response.status_code == 200
        
        data = response.json()
        first_draw = data[0]
        
        assert "replay_number" in first_draw, "Draw should contain replay_number"
        
        print(f"✓ replay_number in first draw: {first_draw['replay_number']}")
    
    def test_draws_numbers_are_valid(self):
        """Test that draw numbers are valid (6 numbers between 1-42)"""
        response = requests.get(f"{BASE_URL}/api/draws")
        assert response.status_code == 200
        
        data = response.json()
        first_draw = data[0]
        
        assert len(first_draw["numbers"]) == 6, f"Should have 6 numbers, got {len(first_draw['numbers'])}"
        for num in first_draw["numbers"]:
            assert 1 <= num <= 42, f"Number {num} should be between 1 and 42"
        
        print(f"✓ Numbers valid: {first_draw['numbers']}")
    
    def test_draws_families_are_valid(self):
        """Test that families are valid (1 or 2 for each number)"""
        response = requests.get(f"{BASE_URL}/api/draws")
        assert response.status_code == 200
        
        data = response.json()
        first_draw = data[0]
        
        assert len(first_draw["families"]) == 6, f"Should have 6 families, got {len(first_draw['families'])}"
        for fam in first_draw["families"]:
            assert fam in [1, 2], f"Family {fam} should be 1 or 2"
        
        print(f"✓ Families valid: {first_draw['families']}")


class TestDashboardEndpoint:
    """Tests for /api/dashboard endpoint"""
    
    def test_dashboard_returns_stats(self):
        """Test that dashboard returns statistics"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_draws" in data, "Should contain total_draws"
        assert data["total_draws"] > 0, "Should have at least one draw"
        
        print(f"✓ total_draws: {data['total_draws']}")
    
    def test_dashboard_contains_hot_numbers(self):
        """Test that dashboard contains hot_numbers"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "hot_numbers" in data, "Should contain hot_numbers"
        assert isinstance(data["hot_numbers"], list), "hot_numbers should be a list"
        assert len(data["hot_numbers"]) > 0, "Should have at least one hot number"
        
        # Verify structure
        first_hot = data["hot_numbers"][0]
        assert "number" in first_hot, "Hot number should have 'number' field"
        assert "count" in first_hot, "Hot number should have 'count' field"
        
        print(f"✓ Top hot number: {first_hot['number']} ({first_hot['count']}x)")
    
    def test_dashboard_contains_cold_numbers(self):
        """Test that dashboard contains cold_numbers"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "cold_numbers" in data, "Should contain cold_numbers"
        assert isinstance(data["cold_numbers"], list), "cold_numbers should be a list"
        
        print(f"✓ cold_numbers count: {len(data['cold_numbers'])}")
    
    def test_dashboard_contains_group_stats(self):
        """Test that dashboard contains group statistics"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        assert "group1_count" in data, "Should contain group1_count"
        assert "group2_count" in data, "Should contain group2_count"
        assert "group1_percentage" in data, "Should contain group1_percentage"
        assert "group2_percentage" in data, "Should contain group2_percentage"
        
        # Percentages should add up to ~100%
        total_pct = data["group1_percentage"] + data["group2_percentage"]
        assert 99 <= total_pct <= 101, f"Group percentages should add to ~100%, got {total_pct}"
        
        print(f"✓ Group1: {data['group1_percentage']}%, Group2: {data['group2_percentage']}%")
    
    def test_dashboard_contains_last_draws(self):
        """Test that dashboard contains last_draws"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "last_draws" in data, "Should contain last_draws"
        assert isinstance(data["last_draws"], list), "last_draws should be a list"
        assert len(data["last_draws"]) > 0, "Should have at least one last draw"
        
        print(f"✓ Last draw: {data['last_draws'][0]['date']} - {data['last_draws'][0]['numbers']}")
    
    def test_dashboard_contains_rare_events(self):
        """Test that dashboard contains rare_events count"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "rare_events" in data, "Should contain rare_events"
        assert isinstance(data["rare_events"], int), "rare_events should be an integer"
        
        print(f"✓ rare_events: {data['rare_events']}")
    
    def test_dashboard_contains_chain_links(self):
        """Test that dashboard contains chain_links count"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "chain_links" in data, "Should contain chain_links"
        
        print(f"✓ chain_links: {data['chain_links']}")


class TestAPIRoot:
    """Tests for API root endpoint"""
    
    def test_api_root(self):
        """Test that API root returns welcome message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        
        print(f"✓ API root: {data['message']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
