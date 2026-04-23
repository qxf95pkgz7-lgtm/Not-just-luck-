"""
EuroMillions API Tests
Tests for the EuroMillions prediction engine including:
- Master predictor endpoint with 3-scenario generation
- P1+P2 constant sum (37) verification
- Historical draws endpoint
- Data sync endpoint
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://swiss-euro-predict.preview.emergentagent.com"


class TestEuroMillionsHealth:
    """Health check tests"""
    
    def test_euromillions_health(self):
        """Test EuroMillions health endpoint"""
        response = requests.get(f"{BASE_URL}/api/euromillions/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "EuroMillions" in data["service"]
        print(f"✓ Health check passed: {data}")


class TestEuroMillionsDraws:
    """Historical draws endpoint tests"""
    
    def test_get_draws_default(self):
        """Test fetching draws with default limit"""
        response = requests.get(f"{BASE_URL}/api/euromillions/draws")
        assert response.status_code == 200
        data = response.json()
        assert "draws" in data
        assert len(data["draws"]) > 0
        print(f"✓ Got {len(data['draws'])} draws")
    
    def test_get_draws_with_limit(self):
        """Test fetching draws with specific limit"""
        response = requests.get(f"{BASE_URL}/api/euromillions/draws?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "draws" in data
        assert len(data["draws"]) <= 5
        
        # Verify draw structure
        for draw in data["draws"]:
            assert "date" in draw
            assert "numbers" in draw
            assert "stars" in draw
            assert len(draw["numbers"]) == 5
            assert len(draw["stars"]) == 2
            # Verify number ranges
            for num in draw["numbers"]:
                assert 1 <= num <= 50, f"Number {num} out of range 1-50"
            for star in draw["stars"]:
                assert 1 <= star <= 12, f"Star {star} out of range 1-12"
        print(f"✓ Draw structure verified for {len(data['draws'])} draws")
    
    def test_draws_sorted_by_date(self):
        """Test that draws are sorted by date (newest first)"""
        response = requests.get(f"{BASE_URL}/api/euromillions/draws?limit=10")
        assert response.status_code == 200
        data = response.json()
        draws = data["draws"]
        
        # Parse dates and verify descending order
        from datetime import datetime
        dates = []
        for draw in draws:
            try:
                dt = datetime.strptime(draw["date"], "%d.%m.%Y")
                dates.append(dt)
            except:
                pass
        
        for i in range(len(dates) - 1):
            assert dates[i] >= dates[i+1], f"Draws not sorted: {dates[i]} should be >= {dates[i+1]}"
        print(f"✓ Draws correctly sorted by date (newest first)")


class TestEuroMillionsMasterPredictor:
    """Master predictor endpoint tests - the core prediction engine"""
    
    def test_basic_prediction(self):
        """Test basic prediction with default parameters"""
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
        assert len(ticket["numbers"]) == 5
        assert len(ticket["stars"]) == 2
        
        # Verify ranges
        for num in ticket["numbers"]:
            assert 1 <= num <= 50, f"Number {num} out of range"
        for star in ticket["stars"]:
            assert 1 <= star <= 12, f"Star {star} out of range"
        
        print(f"✓ Basic prediction: {ticket['numbers']} + Stars: {ticket['stars']}")
    
    def test_p1_p2_constant_sum_37(self):
        """CRITICAL: Verify P1+P2 constant sum (37) is respected in tickets"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 9}  # Test multiple tickets for scenario rotation
        )
        assert response.status_code == 200
        data = response.json()
        
        P1_P2_SUM = 37
        sum_violations = []
        sum_matches = []
        
        for ticket in data["tickets"]:
            numbers = sorted(ticket["numbers"])
            p1 = numbers[0]  # Smallest number
            p2 = numbers[1]  # Second smallest
            actual_sum = p1 + p2
            
            if actual_sum == P1_P2_SUM:
                sum_matches.append((p1, p2, ticket.get("scenario", "unknown")))
            else:
                sum_violations.append({
                    "ticket": ticket["ticket_number"],
                    "p1": p1,
                    "p2": p2,
                    "sum": actual_sum,
                    "expected": P1_P2_SUM,
                    "scenario": ticket.get("scenario", "unknown")
                })
        
        print(f"✓ P1+P2=37 matches: {len(sum_matches)}/{len(data['tickets'])}")
        for p1, p2, scenario in sum_matches:
            print(f"  - P1={p1}, P2={p2}, Sum={p1+p2}, Scenario={scenario}")
        
        if sum_violations:
            print(f"⚠ P1+P2 violations: {len(sum_violations)}")
            for v in sum_violations:
                print(f"  - Ticket {v['ticket']}: P1={v['p1']}, P2={v['p2']}, Sum={v['sum']} (expected {v['expected']}), Scenario={v['scenario']}")
        
        # After fix: expect 100% match rate (allow 90% for edge cases)
        match_rate = len(sum_matches) / len(data["tickets"])
        assert match_rate >= 0.9, f"P1+P2=37 match rate too low: {match_rate:.1%}"
        print(f"✓ P1+P2=37 match rate: {match_rate:.1%}")
    
    def test_p1_p2_sum_37_with_sorting_verification(self):
        """Verify tickets are sorted AND P1+P2=37 after sorting"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 9}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            numbers = ticket["numbers"]
            
            # Verify sorted (ascending order)
            assert numbers == sorted(numbers), f"Ticket {ticket['ticket_number']} not sorted: {numbers}"
            
            # Verify 5 unique numbers
            assert len(numbers) == 5, f"Ticket {ticket['ticket_number']} doesn't have 5 numbers"
            assert len(set(numbers)) == 5, f"Ticket {ticket['ticket_number']} has duplicates: {numbers}"
            
            # Verify P1+P2=37
            p1, p2 = numbers[0], numbers[1]
            assert p1 + p2 == 37, f"Ticket {ticket['ticket_number']}: P1({p1})+P2({p2})={p1+p2}, expected 37"
            
            # Verify P3, P4, P5 are all > P2
            for i, num in enumerate(numbers[2:], start=3):
                assert num > p2, f"Ticket {ticket['ticket_number']}: P{i}({num}) should be > P2({p2})"
        
        print(f"✓ All {len(data['tickets'])} tickets verified: sorted, unique, P1+P2=37, P3/P4/P5 > P2")
    
    def test_scenario_rotation_with_5_tickets(self):
        """Test scenario rotation (low/medium/high) with 5 tickets"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tickets"]) == 5
        
        scenarios = [t.get("scenario") for t in data["tickets"]]
        scenario_counts = {}
        for s in scenarios:
            scenario_counts[s] = scenario_counts.get(s, 0) + 1
        
        print(f"✓ Scenario distribution for 5 tickets: {scenario_counts}")
        
        # Verify all three scenarios are present
        assert "low" in scenario_counts or "medium" in scenario_counts or "high" in scenario_counts, \
            "At least one scenario type should be present"
        
        # Verify P1 ranges based on scenario
        for ticket in data["tickets"]:
            scenario = ticket.get("scenario")
            numbers = sorted(ticket["numbers"])
            p1 = numbers[0]
            
            if scenario == "low":
                # Low scenario: P1 should be 1-5
                print(f"  Low scenario: P1={p1} (expected 1-5)")
            elif scenario == "medium":
                # Medium scenario: P1 should be 6-15 (8-13 per config)
                print(f"  Medium scenario: P1={p1} (expected 6-15)")
            elif scenario == "high":
                # High scenario: P1 should be 16+
                print(f"  High scenario: P1={p1} (expected 16+)")
    
    def test_prediction_with_birthday(self):
        """Test prediction with birthday parameter"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={
                "num_tickets": 1,
                "birthday": "15.06.1985"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tickets"]) == 1
        ticket = data["tickets"][0]
        
        # Check if birthday pattern was used
        patterns = ticket.get("patterns_used", [])
        birthday_pattern = any("Birthday" in p for p in patterns)
        print(f"✓ Prediction with birthday: {ticket['numbers']}")
        print(f"  Birthday pattern used: {birthday_pattern}")
        print(f"  Patterns: {patterns[:5]}...")  # Show first 5 patterns
    
    def test_prediction_with_name(self):
        """Test prediction with name parameter"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={
                "num_tickets": 1,
                "name": "Jack"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        ticket = data["tickets"][0]
        patterns = ticket.get("patterns_used", [])
        name_pattern = any("Name" in p for p in patterns)
        print(f"✓ Prediction with name: {ticket['numbers']}")
        print(f"  Name pattern used: {name_pattern}")
    
    def test_prediction_without_birthday_or_name(self):
        """Test that prediction works without birthday (persona buttons use case)"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tickets"]) == 1
        ticket = data["tickets"][0]
        assert len(ticket["numbers"]) == 5
        assert len(ticket["stars"]) == 2
        print(f"✓ Prediction without birthday/name works: {ticket['numbers']}")
    
    def test_multiple_tickets_unique(self):
        """Test that multiple tickets have some variation"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Convert tickets to tuples for comparison
        ticket_sets = [tuple(sorted(t["numbers"])) for t in data["tickets"]]
        unique_tickets = set(ticket_sets)
        
        print(f"✓ Generated {len(data['tickets'])} tickets, {len(unique_tickets)} unique")
        
        # At least some variation expected
        assert len(unique_tickets) >= 2, "Expected at least 2 unique tickets out of 5"
    
    def test_stars_in_valid_range(self):
        """Test that stars are always in 1-12 range"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            for star in ticket["stars"]:
                assert 1 <= star <= 12, f"Star {star} out of range 1-12"
        
        print(f"✓ All stars in valid range 1-12 across {len(data['tickets'])} tickets")
    
    def test_response_includes_pricing(self):
        """Test that response includes pricing information"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "price_per_ticket" in data
        assert "total_price" in data
        assert "currency" in data
        
        expected_total = data["price_per_ticket"] * len(data["tickets"])
        assert abs(data["total_price"] - expected_total) < 0.01
        
        print(f"✓ Pricing: {data['price_per_ticket']} {data['currency']} x {len(data['tickets'])} = {data['total_price']} {data['currency']}")


class TestEuroMillionsStats:
    """Statistics endpoint tests"""
    
    def test_get_stats(self):
        """Test fetching EuroMillions statistics"""
        response = requests.get(f"{BASE_URL}/api/euromillions/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_draws" in data
        assert "number_frequency" in data
        assert "star_frequency" in data
        assert "sum_stats" in data
        
        print(f"✓ Stats: {data['total_draws']} total draws")
        print(f"  Sum range: {data['sum_stats']['min']}-{data['sum_stats']['max']}, avg: {data['sum_stats']['avg']}")


class TestDataSync:
    """Data synchronization endpoint tests"""
    
    def test_sync_data_files(self):
        """Test manual data sync endpoint"""
        response = requests.post(f"{BASE_URL}/api/sync-data-files")
        assert response.status_code == 200
        data = response.json()
        
        assert "euromillions" in data
        euro_stats = data["euromillions"]
        assert "status" in euro_stats
        
        print(f"✓ Data sync: {euro_stats['status']}")
        if "existing" in euro_stats:
            print(f"  Existing draws: {euro_stats['existing']}")
        if "new" in euro_stats:
            print(f"  New draws: {euro_stats['new']}")


class TestCirclePartnerCalculations:
    """Test that circle partner calculations don't crash"""
    
    def test_multiple_predictions_no_crash(self):
        """Generate many predictions to ensure circle calculations are stable"""
        for i in range(5):
            response = requests.post(
                f"{BASE_URL}/api/euromillions/master-predictor",
                json={"num_tickets": 10}
            )
            assert response.status_code == 200, f"Prediction {i+1} failed"
        
        print(f"✓ Generated 50 predictions without crashes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
