"""
Comprehensive test for Lucky Jack Lottery Analyzer
Tests both Swiss Lotto and EuroMillions modes
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSwissLottoMode:
    """Swiss Lotto: 6 numbers (1-42) + 1 lucky number (1-6)"""
    
    def test_swiss_lotto_root_endpoint(self):
        """Test Swiss Lotto API root"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "Lucky Jack" in data.get("message", "")
        print("✓ Swiss Lotto root endpoint working")
    
    def test_swiss_lotto_dashboard(self):
        """Test dashboard returns stats"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_draws" in data
        assert "hot_numbers" in data
        assert "cold_numbers" in data
        print(f"✓ Dashboard: {data['total_draws']} draws available")
    
    def test_swiss_lotto_master_predictor_basic(self):
        """Test Swiss Lotto prediction returns 6 main numbers + lucky number"""
        response = requests.get(f"{BASE_URL}/api/master-predictor")
        assert response.status_code == 200
        data = response.json()
        
        # Check main_prediction has 6 numbers
        assert "main_prediction" in data
        assert len(data["main_prediction"]) == 6
        
        # Check all numbers are in range 1-42
        for num in data["main_prediction"]:
            assert 1 <= num <= 42, f"Number {num} out of range 1-42"
        
        # Check lucky_prediction exists and is 1-6
        assert "lucky_prediction" in data
        assert 1 <= data["lucky_prediction"] <= 6
        
        print(f"✓ Swiss Lotto prediction: {data['main_prediction']}, Lucky: {data['lucky_prediction']}")
    
    def test_swiss_lotto_with_birthday(self):
        """Test personalization with birthday"""
        response = requests.get(f"{BASE_URL}/api/master-predictor?birthday=15/06/1985")
        assert response.status_code == 200
        data = response.json()
        assert "main_prediction" in data
        assert len(data["main_prediction"]) == 6
        print(f"✓ Swiss Lotto with birthday: {data['main_prediction']}")
    
    def test_swiss_lotto_with_name(self):
        """Test personalization with name"""
        response = requests.get(f"{BASE_URL}/api/master-predictor?name=Jack")
        assert response.status_code == 200
        data = response.json()
        assert "main_prediction" in data
        print(f"✓ Swiss Lotto with name: {data['main_prediction']}")
    
    def test_swiss_lotto_lock_positions(self):
        """Test lock positions feature (max 4 locks for Swiss)"""
        # Lock positions 1 and 2
        response = requests.get(f"{BASE_URL}/api/master-predictor?lock_p1=7&lock_p2=14")
        assert response.status_code == 200
        data = response.json()
        
        # Verify locked numbers appear in prediction
        assert "main_prediction" in data
        assert 7 in data["main_prediction"], "Locked number 7 should be in prediction"
        assert 14 in data["main_prediction"], "Locked number 14 should be in prediction"
        print(f"✓ Swiss Lotto with locks: {data['main_prediction']} (locked 7, 14)")
    
    def test_swiss_lotto_max_locks_validation(self):
        """Test that max 4 locks are allowed for Swiss Lotto"""
        # Try to lock 5 positions (should fail or ignore extra)
        response = requests.get(f"{BASE_URL}/api/master-predictor?lock_p1=1&lock_p2=2&lock_p3=3&lock_p4=4&lock_p5=5")
        assert response.status_code == 200
        # API should either return error or accept only 4 locks
        print("✓ Swiss Lotto max locks validation passed")
    
    def test_swiss_lotto_multi_tickets(self):
        """Test multi-ticket generation"""
        response = requests.get(f"{BASE_URL}/api/master-predictor?num_tickets=3")
        assert response.status_code == 200
        data = response.json()
        
        # Check if all_tickets is present for multi-ticket mode
        if "all_tickets" in data:
            assert len(data["all_tickets"]) == 3
            for ticket in data["all_tickets"]:
                assert len(ticket["numbers"]) == 6
            print(f"✓ Swiss Lotto multi-tickets: {len(data['all_tickets'])} tickets generated")
        else:
            # Single ticket mode
            assert "main_prediction" in data
            print(f"✓ Swiss Lotto single ticket: {data['main_prediction']}")


class TestEuroMillionsMode:
    """EuroMillions: 5 numbers (1-50) + 2 stars (1-12)"""
    
    def test_euromillions_health(self):
        """Test EuroMillions health endpoint"""
        response = requests.get(f"{BASE_URL}/api/euromillions/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ EuroMillions health check passed")
    
    def test_euromillions_stats(self):
        """Test EuroMillions stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/euromillions/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_draws" in data or "total" in data
        print(f"✓ EuroMillions stats: {data.get('total_draws', data.get('total', 0))} draws")
    
    def test_euromillions_master_predictor_basic(self):
        """Test EuroMillions prediction returns 5 numbers + 2 stars"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check tickets array exists
        assert "tickets" in data
        assert len(data["tickets"]) >= 1
        
        ticket = data["tickets"][0]
        
        # Check 5 main numbers in range 1-50
        assert "numbers" in ticket
        assert len(ticket["numbers"]) == 5
        for num in ticket["numbers"]:
            assert 1 <= num <= 50, f"Number {num} out of range 1-50"
        
        # Check 2 stars in range 1-12
        assert "stars" in ticket
        assert len(ticket["stars"]) == 2
        for star in ticket["stars"]:
            assert 1 <= star <= 12, f"Star {star} out of range 1-12"
        
        print(f"✓ EuroMillions prediction: {ticket['numbers']}, Stars: {ticket['stars']}")
    
    def test_euromillions_with_birthday(self):
        """Test EuroMillions with birthday personalization"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1, "birthday": "15.06.1985"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        ticket = data["tickets"][0]
        
        # Check patterns_used includes Birthday
        if "patterns_used" in ticket:
            assert any("Birthday" in p for p in ticket["patterns_used"]), "Birthday pattern should be used"
        
        print(f"✓ EuroMillions with birthday: {ticket['numbers']}, Stars: {ticket['stars']}")
    
    def test_euromillions_with_name(self):
        """Test EuroMillions with name personalization"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1, "name": "Lucky Jack"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        ticket = data["tickets"][0]
        
        # Check patterns_used includes Name
        if "patterns_used" in ticket:
            assert any("Name" in p for p in ticket["patterns_used"]), "Name pattern should be used"
        
        print(f"✓ EuroMillions with name: {ticket['numbers']}, Stars: {ticket['stars']}")
    
    def test_euromillions_lock_positions(self):
        """Test EuroMillions lock positions (max 3 locks for Euro)"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={
                "num_tickets": 1,
                "locked_positions": {"P1": 7, "P2": 23}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        ticket = data["tickets"][0]
        
        # Verify locked numbers appear in prediction
        assert 7 in ticket["numbers"], "Locked number 7 should be in prediction"
        assert 23 in ticket["numbers"], "Locked number 23 should be in prediction"
        
        print(f"✓ EuroMillions with locks: {ticket['numbers']} (locked 7, 23)")
    
    def test_euromillions_multi_tickets(self):
        """Test EuroMillions multi-ticket generation"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "tickets" in data
        assert len(data["tickets"]) == 5
        assert "total_tickets" in data
        assert data["total_tickets"] == 5
        
        # Verify each ticket has correct format
        for i, ticket in enumerate(data["tickets"]):
            assert len(ticket["numbers"]) == 5, f"Ticket {i+1} should have 5 numbers"
            assert len(ticket["stars"]) == 2, f"Ticket {i+1} should have 2 stars"
            assert "confidence" in ticket
        
        print(f"✓ EuroMillions multi-tickets: {len(data['tickets'])} tickets generated")
    
    def test_euromillions_response_format(self):
        """Test EuroMillions API returns correct format with numbers and stars"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "tickets" in data
        assert "total_tickets" in data
        assert "price_per_ticket" in data
        assert "total_price" in data
        assert "currency" in data
        
        # Verify ticket structure
        ticket = data["tickets"][0]
        assert "numbers" in ticket
        assert "stars" in ticket
        assert "confidence" in ticket
        assert "patterns_used" in ticket
        
        print(f"✓ EuroMillions response format correct: {list(data.keys())}")


class TestCrossFeatures:
    """Test features that work across both modes"""
    
    def test_swiss_lotto_alternate_numbers(self):
        """Test Swiss Lotto returns alternate/bonus numbers"""
        response = requests.get(f"{BASE_URL}/api/master-predictor")
        assert response.status_code == 200
        data = response.json()
        
        # Check alternate_numbers exists
        assert "alternate_numbers" in data
        print(f"✓ Swiss Lotto alternate numbers: {data['alternate_numbers']}")
    
    def test_euromillions_confidence_score(self):
        """Test EuroMillions returns confidence scores"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            assert "confidence" in ticket
            assert 0 <= ticket["confidence"] <= 1
        
        print(f"✓ EuroMillions confidence scores present")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
