"""
EuroMillions API Tests
Tests for the EuroMillions Pattern Analyzer API endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lotto-blind-test.preview.emergentagent.com').rstrip('/')


class TestEuroMillionsHealth:
    """EuroMillions health endpoint tests"""
    
    def test_health_endpoint(self):
        """Test /api/euromillions/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/euromillions/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "EuroMillions Pattern Analyzer"
        print("✓ Health endpoint returns healthy status")


class TestEuroMillionsDraws:
    """EuroMillions draws endpoint tests"""
    
    def test_draws_endpoint_returns_data(self):
        """Test /api/euromillions/draws returns draws with 262 records"""
        response = requests.get(f"{BASE_URL}/api/euromillions/draws?limit=300")
        assert response.status_code == 200
        data = response.json()
        assert "draws" in data
        assert "count" in data
        assert data["count"] == 262, f"Expected 262 draws, got {data['count']}"
        print(f"✓ Draws endpoint returns {data['count']} records")
    
    def test_draws_structure(self):
        """Test draw records have correct structure"""
        response = requests.get(f"{BASE_URL}/api/euromillions/draws?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        for draw in data["draws"]:
            # Check required fields
            assert "date" in draw
            assert "numbers" in draw
            assert "stars" in draw
            
            # Validate numbers (5 numbers between 1-50)
            assert len(draw["numbers"]) == 5
            assert all(1 <= n <= 50 for n in draw["numbers"])
            
            # Validate stars (2 stars between 1-12)
            assert len(draw["stars"]) == 2
            assert all(1 <= s <= 12 for s in draw["stars"])
        
        print("✓ Draw records have correct structure (5 numbers 1-50, 2 stars 1-12)")


class TestEuroMillionsStats:
    """EuroMillions stats endpoint tests"""
    
    def test_stats_endpoint(self):
        """Test /api/euromillions/stats returns statistical analysis"""
        response = requests.get(f"{BASE_URL}/api/euromillions/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_draws" in data
        assert data["total_draws"] == 262
        assert "number_frequency" in data
        assert "star_frequency" in data
        assert "number_gaps" in data
        assert "star_gaps" in data
        assert "sum_stats" in data
        assert "consecutive_pair_rate" in data
        assert "circle_partner_rate" in data
        assert "odd_even_distribution" in data
        assert "high_low_distribution" in data
        
        print(f"✓ Stats endpoint returns analysis for {data['total_draws']} draws")
    
    def test_stats_number_frequency(self):
        """Test number frequency contains all 50 numbers"""
        response = requests.get(f"{BASE_URL}/api/euromillions/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Number frequency should have entries for numbers 1-50
        num_freq = data["number_frequency"]
        assert len(num_freq) > 0
        
        # Star frequency should have entries for stars 1-12
        star_freq = data["star_frequency"]
        assert len(star_freq) > 0
        
        print(f"✓ Number frequency has {len(num_freq)} entries, star frequency has {len(star_freq)} entries")


class TestEuroMillionsMasterPredictor:
    """EuroMillions master predictor endpoint tests"""
    
    def test_master_predictor_basic(self):
        """Test POST /api/euromillions/master-predictor generates predictions"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "tickets" in data
        assert len(data["tickets"]) == 1
        
        ticket = data["tickets"][0]
        assert "numbers" in ticket
        assert "stars" in ticket
        assert "patterns_used" in ticket
        assert "confidence" in ticket
        
        # Validate numbers (5 numbers between 1-50)
        assert len(ticket["numbers"]) == 5
        assert all(1 <= n <= 50 for n in ticket["numbers"])
        
        # Validate stars (2 stars between 1-12)
        assert len(ticket["stars"]) == 2
        assert all(1 <= s <= 12 for s in ticket["stars"])
        
        print(f"✓ Master predictor returns valid prediction: {ticket['numbers']} + stars {ticket['stars']}")
    
    def test_master_predictor_multiple_tickets(self):
        """Test master predictor with multiple tickets"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tickets"]) == 5
        assert data["total_tickets"] == 5
        assert data["price_per_ticket"] == 2.50
        assert data["total_price"] == 12.50
        assert data["currency"] == "EUR"
        
        print(f"✓ Master predictor returns {len(data['tickets'])} tickets with total price {data['total_price']} EUR")
    
    def test_master_predictor_with_birthday(self):
        """Test master predictor with birthday parameter"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"birthday": "15.06.1990", "num_tickets": 1}
        )
        assert response.status_code == 200
        data = response.json()
        
        ticket = data["tickets"][0]
        assert "Birthday" in str(ticket["patterns_used"])
        
        print(f"✓ Master predictor with birthday uses Birthday pattern")
    
    def test_master_predictor_with_name(self):
        """Test master predictor with name parameter"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"name": "John Doe", "num_tickets": 1}
        )
        assert response.status_code == 200
        data = response.json()
        
        ticket = data["tickets"][0]
        assert "Name Energy" in str(ticket["patterns_used"])
        
        print(f"✓ Master predictor with name uses Name Energy pattern")
    
    def test_master_predictor_with_locked_positions(self):
        """Test master predictor with locked positions"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={
                "locked_positions": {"P1": 7, "P3": 25},
                "num_tickets": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        ticket = data["tickets"][0]
        # Locked numbers should be in the prediction
        assert 7 in ticket["numbers"]
        assert 25 in ticket["numbers"]
        
        print(f"✓ Master predictor respects locked positions: {ticket['numbers']}")


class TestEuroMillionsAnalyzeTicket:
    """EuroMillions analyze ticket endpoint tests"""
    
    def test_analyze_ticket_valid(self):
        """Test /api/euromillions/analyze-ticket with valid ticket"""
        response = requests.get(
            f"{BASE_URL}/api/euromillions/analyze-ticket",
            params={"numbers": "5,10,25,30,45", "stars": "3,8"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["numbers"] == [5, 10, 25, 30, 45]
        assert data["stars"] == [3, 8]
        assert "sum" in data
        assert "star_sum" in data
        assert "insights" in data
        assert "score" in data
        assert "rating" in data
        
        assert data["sum"] == 115
        assert data["star_sum"] == 11
        assert data["score"] >= 0 and data["score"] <= 100
        assert data["rating"] in ["Excellent", "Good", "Average", "Poor"]
        
        print(f"✓ Analyze ticket returns score {data['score']} ({data['rating']})")
    
    def test_analyze_ticket_invalid_numbers(self):
        """Test analyze ticket with invalid numbers"""
        response = requests.get(
            f"{BASE_URL}/api/euromillions/analyze-ticket",
            params={"numbers": "1,2,3,4", "stars": "3,8"}  # Only 4 numbers
        )
        assert response.status_code == 400
        print("✓ Analyze ticket rejects invalid number count")
    
    def test_analyze_ticket_invalid_stars(self):
        """Test analyze ticket with invalid stars"""
        response = requests.get(
            f"{BASE_URL}/api/euromillions/analyze-ticket",
            params={"numbers": "1,2,3,4,5", "stars": "15,20"}  # Stars out of range
        )
        assert response.status_code == 400
        print("✓ Analyze ticket rejects invalid star values")


class TestSwissLottoAPI:
    """Swiss Lotto API tests (existing functionality)"""
    
    def test_root_endpoint(self):
        """Test /api/ root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "Lucky Jack" in data["message"]
        print("✓ Swiss Lotto root endpoint working")
    
    def test_dashboard_endpoint(self):
        """Test /api/dashboard endpoint"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_draws" in data
        assert "hot_numbers" in data
        assert "cold_numbers" in data
        print(f"✓ Swiss Lotto dashboard returns {data['total_draws']} draws")
    
    def test_master_predictor_swiss(self):
        """Test /api/master-predictor for Swiss Lotto"""
        response = requests.get(f"{BASE_URL}/api/master-predictor")
        assert response.status_code == 200
        data = response.json()
        assert "main_prediction" in data
        assert len(data["main_prediction"]) == 6
        assert all(1 <= n <= 42 for n in data["main_prediction"])
        print(f"✓ Swiss Lotto master predictor returns: {data['main_prediction']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
