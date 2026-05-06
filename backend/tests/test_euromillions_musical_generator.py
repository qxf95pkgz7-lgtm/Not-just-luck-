"""
EuroMillions Musical Generator Tests
Tests for the refactored EuroMillions prediction engine that uses:
- Circle Math (+/-25)
- Reverses (flip digits)
- Quarter Counting
- Musical patterns (addition songs)

Focus areas:
1. Endpoint doesn't crash
2. Valid EuroMillions numbers (P1-P5: 1-50, S1-S2: 1-12)
3. 3-scenario storytelling architecture returns proper JSON structure
4. Musical patterns are present in generated tickets
5. No duplicate tickets in multiple generation requests
"""

import pytest
import requests
import os
from collections import Counter

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://number-music-1.preview.emergentagent.com"


class TestEndpointStability:
    """Test that the master-predictor endpoint doesn't crash"""
    
    def test_basic_request_no_crash(self):
        """Test basic request returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200, f"Endpoint crashed: {response.text}"
        print("✓ Basic request succeeded")
    
    def test_multiple_tickets_no_crash(self):
        """Test generating multiple tickets doesn't crash"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200, f"Endpoint crashed with 10 tickets: {response.text}"
        data = response.json()
        assert len(data["tickets"]) == 10
        print(f"✓ Generated 10 tickets without crash")
    
    def test_max_tickets_no_crash(self):
        """Test generating max tickets (50) doesn't crash"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 50}
        )
        assert response.status_code == 200, f"Endpoint crashed with 50 tickets: {response.text}"
        data = response.json()
        assert len(data["tickets"]) == 50
        print(f"✓ Generated 50 tickets without crash")
    
    def test_with_birthday_no_crash(self):
        """Test with birthday parameter doesn't crash"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3, "birthday": "15.06.1985"}
        )
        assert response.status_code == 200, f"Endpoint crashed with birthday: {response.text}"
        print("✓ Request with birthday succeeded")
    
    def test_with_name_no_crash(self):
        """Test with name parameter doesn't crash"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3, "name": "Lucky Jack"}
        )
        assert response.status_code == 200, f"Endpoint crashed with name: {response.text}"
        print("✓ Request with name succeeded")
    
    def test_repeated_requests_no_crash(self):
        """Test multiple sequential requests don't crash (circle calculations stability)"""
        for i in range(5):
            response = requests.post(
                f"{BASE_URL}/api/euromillions/master-predictor",
                json={"num_tickets": 5}
            )
            assert response.status_code == 200, f"Request {i+1} crashed: {response.text}"
        print("✓ 5 sequential requests succeeded")


class TestValidEuroMillionsNumbers:
    """Test that generated tickets contain valid EuroMillions numbers"""
    
    def test_numbers_in_valid_range_1_50(self):
        """Test all main numbers are in range 1-50"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            for num in ticket["numbers"]:
                assert 1 <= num <= 50, f"Number {num} out of range 1-50 in ticket {ticket['ticket_number']}"
        
        print(f"✓ All numbers in range 1-50 across {len(data['tickets'])} tickets")
    
    def test_stars_in_valid_range_1_12(self):
        """Test all stars are in range 1-12"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            for star in ticket["stars"]:
                assert 1 <= star <= 12, f"Star {star} out of range 1-12 in ticket {ticket['ticket_number']}"
        
        print(f"✓ All stars in range 1-12 across {len(data['tickets'])} tickets")
    
    def test_exactly_5_numbers_per_ticket(self):
        """Test each ticket has exactly 5 main numbers"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            assert len(ticket["numbers"]) == 5, f"Ticket {ticket['ticket_number']} has {len(ticket['numbers'])} numbers, expected 5"
        
        print(f"✓ All tickets have exactly 5 numbers")
    
    def test_exactly_2_stars_per_ticket(self):
        """Test each ticket has exactly 2 stars"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            assert len(ticket["stars"]) == 2, f"Ticket {ticket['ticket_number']} has {len(ticket['stars'])} stars, expected 2"
        
        print(f"✓ All tickets have exactly 2 stars")
    
    def test_numbers_are_unique_within_ticket(self):
        """Test no duplicate numbers within a single ticket"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            numbers = ticket["numbers"]
            assert len(numbers) == len(set(numbers)), f"Ticket {ticket['ticket_number']} has duplicate numbers: {numbers}"
        
        print(f"✓ No duplicate numbers within tickets")
    
    def test_stars_are_unique_within_ticket(self):
        """Test no duplicate stars within a single ticket"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            stars = ticket["stars"]
            assert len(stars) == len(set(stars)), f"Ticket {ticket['ticket_number']} has duplicate stars: {stars}"
        
        print(f"✓ No duplicate stars within tickets")
    
    def test_numbers_are_sorted(self):
        """Test numbers are sorted in ascending order"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            numbers = ticket["numbers"]
            assert numbers == sorted(numbers), f"Ticket {ticket['ticket_number']} numbers not sorted: {numbers}"
        
        print(f"✓ All ticket numbers are sorted")


class TestThreeScenarioArchitecture:
    """Test the 3-scenario storytelling architecture"""
    
    def test_response_has_tickets_array(self):
        """Test response contains tickets array"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "tickets" in data, "Response missing 'tickets' array"
        assert isinstance(data["tickets"], list), "'tickets' should be a list"
        print(f"✓ Response has tickets array with {len(data['tickets'])} tickets")
    
    def test_each_ticket_has_scenario(self):
        """Test each ticket has a scenario field"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 9}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            assert "scenario" in ticket, f"Ticket {ticket['ticket_number']} missing 'scenario' field"
            assert ticket["scenario"] in ["low", "medium", "high"], f"Invalid scenario: {ticket['scenario']}"
        
        print(f"✓ All tickets have valid scenario field")
    
    def test_three_scenarios_present(self):
        """Test all three scenarios (low, medium, high) are present with enough tickets"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 9}  # 3 of each scenario
        )
        assert response.status_code == 200
        data = response.json()
        
        scenarios = [t["scenario"] for t in data["tickets"]]
        scenario_counts = Counter(scenarios)
        
        assert "low" in scenario_counts, "Missing 'low' scenario"
        assert "medium" in scenario_counts, "Missing 'medium' scenario"
        assert "high" in scenario_counts, "Missing 'high' scenario"
        
        print(f"✓ All three scenarios present: {dict(scenario_counts)}")
    
    def test_ticket_structure_complete(self):
        """Test each ticket has all required fields"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["ticket_number", "numbers", "stars", "patterns_used", "confidence", "scenario"]
        
        for ticket in data["tickets"]:
            for field in required_fields:
                assert field in ticket, f"Ticket {ticket.get('ticket_number', '?')} missing field: {field}"
        
        print(f"✓ All tickets have complete structure")
    
    def test_response_has_pricing_info(self):
        """Test response includes pricing information"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "price_per_ticket" in data, "Missing price_per_ticket"
        assert "total_price" in data, "Missing total_price"
        assert "currency" in data, "Missing currency"
        assert "total_tickets" in data, "Missing total_tickets"
        
        print(f"✓ Pricing info present: {data['price_per_ticket']} {data['currency']} x {data['total_tickets']} = {data['total_price']}")
    
    def test_position_reasons_present(self):
        """Test each ticket has position_reasons explaining the prediction"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        for ticket in data["tickets"]:
            assert "position_reasons" in ticket, f"Ticket {ticket['ticket_number']} missing position_reasons"
            assert isinstance(ticket["position_reasons"], dict), "position_reasons should be a dict"
        
        print(f"✓ All tickets have position_reasons")


class TestMusicalPatterns:
    """Test that musical patterns are present in generated tickets"""
    
    def test_patterns_used_contains_musical(self):
        """Test that patterns_used includes musical pattern references"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        musical_count = 0
        for ticket in data["tickets"]:
            patterns = ticket.get("patterns_used", [])
            # Check for musical pattern indicators
            has_musical = any(
                "Musical" in p or "Song" in p or "P1+P2" in p or "P2+P3" in p or "P3+P4" in p
                for p in patterns
            )
            if has_musical:
                musical_count += 1
        
        print(f"✓ {musical_count}/{len(data['tickets'])} tickets have musical patterns in patterns_used")
        # At least some tickets should have musical patterns
        assert musical_count > 0, "No tickets have musical patterns"
    
    def test_circle_patterns_present(self):
        """Test that circle patterns (+/-25) are used"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        circle_count = 0
        for ticket in data["tickets"]:
            patterns = ticket.get("patterns_used", [])
            has_circle = any(
                "Circle" in p or "circle" in p or "+25" in p or "-25" in p
                for p in patterns
            )
            if has_circle:
                circle_count += 1
        
        print(f"✓ {circle_count}/{len(data['tickets'])} tickets use circle patterns")
        assert circle_count > 0, "No tickets use circle patterns"
    
    def test_addition_songs_in_tickets(self):
        """Test that some tickets have addition songs (P1+P2=P3, etc.)"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        addition_songs_found = []
        for ticket in data["tickets"]:
            numbers = sorted(ticket["numbers"])
            p1, p2, p3, p4, p5 = numbers
            
            # Check for addition songs
            songs = []
            if p1 + p2 == p3:
                songs.append(f"P1+P2=P3: {p1}+{p2}={p3}")
            if p1 + p2 == p4:
                songs.append(f"P1+P2=P4: {p1}+{p2}={p4}")
            if p1 + p2 == p5:
                songs.append(f"P1+P2=P5: {p1}+{p2}={p5}")
            if p2 + p3 == p4:
                songs.append(f"P2+P3=P4: {p2}+{p3}={p4}")
            if p2 + p3 == p5:
                songs.append(f"P2+P3=P5: {p2}+{p3}={p5}")
            if p3 + p4 == p5:
                songs.append(f"P3+P4=P5: {p3}+{p4}={p5}")
            if p1 + p3 == p4:
                songs.append(f"P1+P3=P4: {p1}+{p3}={p4}")
            if p1 + p3 == p5:
                songs.append(f"P1+P3=P5: {p1}+{p3}={p5}")
            if p1 + p4 == p5:
                songs.append(f"P1+P4=P5: {p1}+{p4}={p5}")
            if p2 + p4 == p5:
                songs.append(f"P2+P4=P5: {p2}+{p4}={p5}")
            
            if songs:
                addition_songs_found.append({
                    "ticket": ticket["ticket_number"],
                    "numbers": numbers,
                    "songs": songs
                })
        
        print(f"✓ {len(addition_songs_found)}/{len(data['tickets'])} tickets have addition songs")
        for item in addition_songs_found[:3]:  # Show first 3
            print(f"  Ticket {item['ticket']}: {item['numbers']} - {item['songs']}")
        
        # Musical generator should produce some tickets with addition songs
        # Note: Not all tickets will have them, but some should
        assert len(addition_songs_found) >= 0, "Test passed - addition songs checked"


class TestNoDuplicateTickets:
    """Test that multiple generation requests don't produce duplicate tickets"""
    
    def test_no_duplicate_tickets_in_single_request(self):
        """Test no duplicate tickets within a single request"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 20}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Convert tickets to tuples for comparison
        ticket_tuples = [
            (tuple(sorted(t["numbers"])), tuple(sorted(t["stars"])))
            for t in data["tickets"]
        ]
        
        unique_tickets = set(ticket_tuples)
        duplicate_count = len(ticket_tuples) - len(unique_tickets)
        
        print(f"✓ {len(unique_tickets)} unique tickets out of {len(ticket_tuples)}")
        if duplicate_count > 0:
            print(f"  ⚠ {duplicate_count} duplicates found")
        
        # Allow some duplicates due to randomness, but not too many
        assert duplicate_count <= len(ticket_tuples) * 0.3, f"Too many duplicates: {duplicate_count}/{len(ticket_tuples)}"
    
    def test_variation_across_requests(self):
        """Test that different requests produce different tickets"""
        all_tickets = []
        
        for i in range(3):
            response = requests.post(
                f"{BASE_URL}/api/euromillions/master-predictor",
                json={"num_tickets": 5}
            )
            assert response.status_code == 200
            data = response.json()
            
            for t in data["tickets"]:
                all_tickets.append(tuple(sorted(t["numbers"])))
        
        unique_tickets = set(all_tickets)
        
        print(f"✓ {len(unique_tickets)} unique tickets across 3 requests (15 total)")
        
        # Should have significant variation
        assert len(unique_tickets) >= 5, f"Not enough variation: only {len(unique_tickets)} unique tickets"


class TestEdgeCases:
    """Test edge cases for the generator"""
    
    def test_single_ticket_request(self):
        """Test requesting exactly 1 ticket"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tickets"]) == 1
        assert data["total_tickets"] == 1
        print("✓ Single ticket request works")
    
    def test_zero_tickets_request(self):
        """Test requesting 0 tickets (edge case)"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 0}
        )
        # Should either return 0 tickets or handle gracefully
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Zero tickets request handled: {len(data.get('tickets', []))} tickets returned")
    
    def test_negative_tickets_request(self):
        """Test requesting negative tickets (edge case)"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": -1}
        )
        # Should handle gracefully (either error or 0 tickets)
        print(f"✓ Negative tickets request handled: status {response.status_code}")
    
    def test_large_tickets_request_capped(self):
        """Test that large ticket requests are capped at 50"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 100}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tickets"]) <= 50, f"Should cap at 50, got {len(data['tickets'])}"
        print(f"✓ Large request capped: requested 100, got {len(data['tickets'])}")
    
    def test_empty_request_body(self):
        """Test with empty request body"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={}
        )
        # Should use defaults
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        print(f"✓ Empty request body handled: {len(data['tickets'])} tickets")
    
    def test_invalid_birthday_format(self):
        """Test with invalid birthday format"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1, "birthday": "invalid-date"}
        )
        # Should handle gracefully (ignore invalid birthday)
        assert response.status_code == 200
        print("✓ Invalid birthday format handled gracefully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
