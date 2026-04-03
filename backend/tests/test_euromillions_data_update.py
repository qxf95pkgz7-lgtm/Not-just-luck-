"""
Test EuroMillions API after 2018-2020 data addition
Verifies that total draws count is now 521+ (262 original + 259 new)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEuroMillionsDataUpdate:
    """Tests to verify 2018-2020 data was added correctly"""
    
    def test_draws_endpoint_returns_521_plus_total(self):
        """Verify /api/euromillions/draws returns 521+ total draws"""
        response = requests.get(f"{BASE_URL}/api/euromillions/draws?limit=1000")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "total_in_db" in data, "Response should include total_in_db field"
        total_draws = data["total_in_db"]
        
        print(f"Total draws in database: {total_draws}")
        assert total_draws >= 521, f"Expected at least 521 draws, got {total_draws}"
        
        # Verify draws array is returned
        assert "draws" in data, "Response should include draws array"
        assert len(data["draws"]) > 0, "Draws array should not be empty"
        
    def test_stats_endpoint_shows_521_plus_total(self):
        """Verify /api/euromillions/stats shows total_draws >= 521"""
        response = requests.get(f"{BASE_URL}/api/euromillions/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "total_draws" in data, "Response should include total_draws field"
        total_draws = data["total_draws"]
        
        print(f"Stats total_draws: {total_draws}")
        assert total_draws >= 521, f"Expected at least 521 draws in stats, got {total_draws}"
        
        # Verify other stats fields exist
        assert "number_frequency" in data, "Should have number_frequency"
        assert "star_frequency" in data, "Should have star_frequency"
        assert "sum_stats" in data, "Should have sum_stats"
        
    def test_master_predictor_works_with_larger_dataset(self):
        """Verify POST /api/euromillions/master-predictor works with 521+ draws"""
        payload = {
            "num_tickets": 3,
            "birthday": "15.06.1985",
            "name": "TestUser"
        }
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "tickets" in data, "Response should include tickets array"
        assert len(data["tickets"]) == 3, f"Expected 3 tickets, got {len(data['tickets'])}"
        
        # Verify ticket structure
        for ticket in data["tickets"]:
            assert "numbers" in ticket, "Ticket should have numbers"
            assert "stars" in ticket, "Ticket should have stars"
            assert len(ticket["numbers"]) == 5, "Should have 5 numbers"
            assert len(ticket["stars"]) == 2, "Should have 2 stars"
            
            # Verify number ranges
            for num in ticket["numbers"]:
                assert 1 <= num <= 50, f"Number {num} out of range 1-50"
            for star in ticket["stars"]:
                assert 1 <= star <= 12, f"Star {star} out of range 1-12"
                
        print(f"Master predictor generated {len(data['tickets'])} valid tickets")
        
    def test_draws_include_2018_2020_data(self):
        """Verify draws include data from 2018-2020 years"""
        response = requests.get(f"{BASE_URL}/api/euromillions/draws?limit=1000")
        assert response.status_code == 200
        
        data = response.json()
        draws = data["draws"]
        
        # Check for presence of 2018, 2019, 2020 dates
        years_found = set()
        for draw in draws:
            date = draw.get("date", "")
            if "2018" in date:
                years_found.add(2018)
            elif "2019" in date:
                years_found.add(2019)
            elif "2020" in date:
                years_found.add(2020)
                
        print(f"Years found in draws: {sorted(years_found)}")
        
        # Should have all three new years
        assert 2018 in years_found, "Should have 2018 draws"
        assert 2019 in years_found, "Should have 2019 draws"
        assert 2020 in years_found, "Should have 2020 draws"
        
    def test_health_endpoint_still_works(self):
        """Verify health endpoint is still functional"""
        response = requests.get(f"{BASE_URL}/api/euromillions/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "healthy"
        print("EuroMillions health check: OK")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
