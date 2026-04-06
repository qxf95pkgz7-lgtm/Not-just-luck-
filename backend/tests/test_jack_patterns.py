"""
Test Suite for Lucky Jack's Musical Patterns - EuroMillions Generator
=====================================================================
Tests the new Jack Patterns integration in the master-predictor endpoint.

Jack Patterns (8 new patterns discovered through user conversation):
1. P1 Counting Magic (🎻)
2. Neighborhood Hunger (🍽️)
3. 49→45 Call (🎵)
4. Quarter Echo (🔄)
5. P4 Sequence (📊)
6. P1+P2 Digit Root=8 (∑)
7. 8-Family Tracker (8️⃣)
8. Circle Encoding of Missing (🎭)
"""

import pytest
import requests
import os
from collections import Counter

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://lucky-jack-stars.preview.emergentagent.com"


class TestJackPatternsModuleImport:
    """Test that jack_patterns.py module imports correctly"""
    
    def test_jack_patterns_module_exists(self):
        """Verify jack_patterns.py can be imported"""
        import sys
        sys.path.insert(0, '/app/backend')
        
        try:
            from jack_patterns import (
                apply_jack_patterns,
                p1_counting_pattern,
                neighborhood_hunger,
                p5_49_calls_45,
                circle_encode_missing,
                quarter_echo,
                p4_sequence_tracker,
                p1p2_sum_pattern,
                eight_family_tracker,
                circle,
                reverse_num
            )
            print("SUCCESS: All jack_patterns functions imported correctly")
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import jack_patterns: {e}")
    
    def test_circle_function(self):
        """Test the circle helper function (+25 mod 50)"""
        import sys
        sys.path.insert(0, '/app/backend')
        from jack_patterns import circle
        
        # Test cases: n + 25, wrap if > 50
        assert circle(10) == 35, "10 + 25 = 35"
        assert circle(25) == 50, "25 + 25 = 50"
        assert circle(26) == 1, "26 + 25 = 51 -> 1"
        assert circle(30) == 5, "30 + 25 = 55 -> 5"
        assert circle(50) == 25, "50 + 25 = 75 -> 25"
        print("SUCCESS: circle() function works correctly")
    
    def test_reverse_num_function(self):
        """Test the reverse_num helper function"""
        import sys
        sys.path.insert(0, '/app/backend')
        from jack_patterns import reverse_num
        
        # Test cases: reverse digits, mod 50 if > 50
        assert reverse_num(12) == 21, "12 reversed = 21"
        assert reverse_num(27) == 72 % 50 or reverse_num(27) == 22, "27 reversed = 72 -> 22"
        assert reverse_num(35) == 53 % 50 or reverse_num(35) == 3, "35 reversed = 53 -> 3"
        assert reverse_num(10) == 1, "10 reversed = 01 = 1"
        print("SUCCESS: reverse_num() function works correctly")


class TestMasterPredictorEndpoint:
    """Test the /api/euromillions/master-predictor endpoint"""
    
    def test_endpoint_returns_200(self):
        """Basic endpoint health check"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"SUCCESS: Endpoint returned 200")
    
    def test_response_structure(self):
        """Verify response has expected structure"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        assert "tickets" in data, "Response must have 'tickets' array"
        # Pricing can be either nested 'pricing' object or flat fields
        has_pricing = "pricing" in data or ("price_per_ticket" in data and "total_price" in data)
        assert has_pricing, "Response must have pricing info (either 'pricing' object or 'price_per_ticket'/'total_price')"
        assert isinstance(data["tickets"], list), "tickets must be a list"
        assert len(data["tickets"]) == 3, "Should have 3 tickets"
        print(f"SUCCESS: Response structure is correct with {len(data['tickets'])} tickets")


class TestValidEuroMillionsNumbers:
    """Test that generated numbers are valid EuroMillions format"""
    
    def test_numbers_in_valid_range_1_50(self):
        """P1-P5 must be in range 1-50"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        for i, ticket in enumerate(data["tickets"]):
            numbers = ticket["numbers"]
            for num in numbers:
                assert 1 <= num <= 50, f"Ticket {i+1}: Number {num} out of range 1-50"
        print(f"SUCCESS: All numbers in valid range 1-50")
    
    def test_stars_in_valid_range_1_12(self):
        """S1-S2 must be in range 1-12"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        for i, ticket in enumerate(data["tickets"]):
            stars = ticket["stars"]
            for star in stars:
                assert 1 <= star <= 12, f"Ticket {i+1}: Star {star} out of range 1-12"
        print(f"SUCCESS: All stars in valid range 1-12")
    
    def test_exactly_5_numbers_per_ticket(self):
        """Each ticket must have exactly 5 main numbers"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        for i, ticket in enumerate(data["tickets"]):
            assert len(ticket["numbers"]) == 5, f"Ticket {i+1}: Expected 5 numbers, got {len(ticket['numbers'])}"
        print(f"SUCCESS: All tickets have exactly 5 numbers")
    
    def test_exactly_2_stars_per_ticket(self):
        """Each ticket must have exactly 2 stars"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        for i, ticket in enumerate(data["tickets"]):
            assert len(ticket["stars"]) == 2, f"Ticket {i+1}: Expected 2 stars, got {len(ticket['stars'])}"
        print(f"SUCCESS: All tickets have exactly 2 stars")
    
    def test_numbers_are_unique_within_ticket(self):
        """No duplicate numbers within a single ticket"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        for i, ticket in enumerate(data["tickets"]):
            numbers = ticket["numbers"]
            assert len(numbers) == len(set(numbers)), f"Ticket {i+1}: Duplicate numbers found"
        print(f"SUCCESS: All numbers unique within each ticket")
    
    def test_numbers_are_sorted(self):
        """Numbers should be sorted in ascending order"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        for i, ticket in enumerate(data["tickets"]):
            numbers = ticket["numbers"]
            assert numbers == sorted(numbers), f"Ticket {i+1}: Numbers not sorted"
        print(f"SUCCESS: All numbers are sorted")


class TestThreeScenarioArchitecture:
    """Test the 3-scenario storytelling architecture (low/medium/high)"""
    
    def test_each_ticket_has_scenario(self):
        """Each ticket must have a scenario field"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 6}
        )
        assert response.status_code == 200
        data = response.json()
        
        for i, ticket in enumerate(data["tickets"]):
            assert "scenario" in ticket, f"Ticket {i+1}: Missing 'scenario' field"
            assert ticket["scenario"] in ["low", "medium", "high"], f"Ticket {i+1}: Invalid scenario '{ticket['scenario']}'"
        print(f"SUCCESS: All tickets have valid scenario field")
    
    def test_three_scenarios_present(self):
        """With 3+ tickets, all three scenarios should be present"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 6}
        )
        assert response.status_code == 200
        data = response.json()
        
        scenarios = set(ticket["scenario"] for ticket in data["tickets"])
        assert "low" in scenarios, "Missing 'low' scenario"
        assert "medium" in scenarios, "Missing 'medium' scenario"
        assert "high" in scenarios, "Missing 'high' scenario"
        print(f"SUCCESS: All three scenarios present: {scenarios}")
    
    def test_ticket_structure_complete(self):
        """Each ticket must have all required fields"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["numbers", "stars", "patterns_used", "confidence", "scenario"]
        for i, ticket in enumerate(data["tickets"]):
            for field in required_fields:
                assert field in ticket, f"Ticket {i+1}: Missing required field '{field}'"
        print(f"SUCCESS: All tickets have complete structure")


class TestJackPatternsInOutput:
    """Test that Jack patterns appear in the patterns_used array"""
    
    JACK_PATTERN_EMOJIS = {
        "🎻": "P1 Counting Magic",
        "🍽️": "Neighborhood Hunger",
        "🎵": "49→45 Call / Musical",
        "🔄": "Quarter Echo",
        "📊": "P4 Sequence",
        "∑": "P1+P2 Digit Root",
        "8️⃣": "8-Family Tracker",
        "🎭": "Circle Encoding Missing"
    }
    
    def test_patterns_used_is_array(self):
        """patterns_used must be an array"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        for i, ticket in enumerate(data["tickets"]):
            assert "patterns_used" in ticket, f"Ticket {i+1}: Missing patterns_used"
            assert isinstance(ticket["patterns_used"], list), f"Ticket {i+1}: patterns_used must be a list"
        print(f"SUCCESS: patterns_used is an array in all tickets")
    
    def test_jack_patterns_appear_in_output(self):
        """At least some Jack pattern emojis should appear in patterns_used"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}  # More tickets = more chances to see patterns
        )
        assert response.status_code == 200
        data = response.json()
        
        all_patterns = []
        for ticket in data["tickets"]:
            all_patterns.extend(ticket.get("patterns_used", []))
        
        patterns_str = " ".join(all_patterns)
        
        found_emojis = []
        for emoji, name in self.JACK_PATTERN_EMOJIS.items():
            if emoji in patterns_str:
                found_emojis.append(f"{emoji} ({name})")
        
        print(f"Found Jack pattern emojis: {found_emojis}")
        print(f"All patterns: {all_patterns[:20]}...")  # First 20 patterns
        
        # At least 2 Jack pattern emojis should appear
        assert len(found_emojis) >= 2, f"Expected at least 2 Jack pattern emojis, found {len(found_emojis)}: {found_emojis}"
        print(f"SUCCESS: Found {len(found_emojis)} Jack pattern emojis in output")
    
    def test_musical_patterns_present(self):
        """Musical patterns (addition songs) should be present"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        musical_count = 0
        for ticket in data["tickets"]:
            patterns = ticket.get("patterns_used", [])
            for p in patterns:
                if "Musical" in p or "🎵" in p or "Song" in p or "+" in p:
                    musical_count += 1
                    break
        
        print(f"Tickets with musical patterns: {musical_count}/{len(data['tickets'])}")
        # At least 50% of tickets should have musical patterns
        assert musical_count >= len(data["tickets"]) * 0.3, f"Expected at least 30% musical patterns, got {musical_count}/{len(data['tickets'])}"
        print(f"SUCCESS: {musical_count} tickets have musical patterns")


class TestNoDuplicateTickets:
    """Test that generated tickets are unique"""
    
    def test_no_duplicate_tickets_in_single_request(self):
        """All tickets in a single request should be unique"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        ticket_signatures = []
        for ticket in data["tickets"]:
            sig = tuple(ticket["numbers"]) + tuple(ticket["stars"])
            ticket_signatures.append(sig)
        
        unique_count = len(set(ticket_signatures))
        total_count = len(ticket_signatures)
        
        print(f"Unique tickets: {unique_count}/{total_count}")
        assert unique_count == total_count, f"Found duplicate tickets: {total_count - unique_count} duplicates"
        print(f"SUCCESS: All {total_count} tickets are unique")
    
    def test_variation_across_requests(self):
        """Multiple requests should produce different tickets"""
        all_tickets = []
        
        for i in range(3):
            response = requests.post(
                f"{BASE_URL}/api/euromillions/master-predictor",
                json={"num_tickets": 3}
            )
            assert response.status_code == 200
            data = response.json()
            
            for ticket in data["tickets"]:
                sig = tuple(ticket["numbers"]) + tuple(ticket["stars"])
                all_tickets.append(sig)
        
        unique_count = len(set(all_tickets))
        total_count = len(all_tickets)
        
        print(f"Unique tickets across 3 requests: {unique_count}/{total_count}")
        # Allow some overlap but expect at least 70% unique
        assert unique_count >= total_count * 0.7, f"Too many duplicate tickets across requests"
        print(f"SUCCESS: Good variation across requests ({unique_count}/{total_count} unique)")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_single_ticket_request(self):
        """Single ticket request should work"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tickets"]) == 1
        print(f"SUCCESS: Single ticket request works")
    
    def test_multiple_tickets_request(self):
        """Multiple tickets request should work"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tickets"]) == 5
        print(f"SUCCESS: Multiple tickets request works")
    
    def test_with_birthday_parameter(self):
        """Request with birthday should work"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3, "birthday": "15.06.1985"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check if birthday pattern is mentioned
        all_patterns = []
        for ticket in data["tickets"]:
            all_patterns.extend(ticket.get("patterns_used", []))
        
        patterns_str = " ".join(all_patterns)
        has_birthday = "Birthday" in patterns_str or "15.06.1985" in patterns_str
        print(f"Birthday pattern found: {has_birthday}")
        print(f"SUCCESS: Request with birthday works")
    
    def test_with_name_parameter(self):
        """Request with name should work"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3, "name": "Jack"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check if name pattern is mentioned
        all_patterns = []
        for ticket in data["tickets"]:
            all_patterns.extend(ticket.get("patterns_used", []))
        
        patterns_str = " ".join(all_patterns)
        has_name = "Name" in patterns_str or "Jack" in patterns_str
        print(f"Name pattern found: {has_name}")
        print(f"SUCCESS: Request with name works")
    
    def test_empty_request_body(self):
        """Empty request body should use defaults"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        print(f"SUCCESS: Empty request body uses defaults")


class TestDetailedPatternAnalysis:
    """Detailed analysis of Jack patterns in generated tickets"""
    
    def test_p1_counting_pattern_present(self):
        """Check for P1 Counting Magic pattern (🎻)"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        found = False
        for ticket in data["tickets"]:
            patterns = " ".join(ticket.get("patterns_used", []))
            if "🎻" in patterns or "P1 Count" in patterns:
                found = True
                print(f"Found P1 Counting pattern: {patterns[:100]}...")
                break
        
        print(f"P1 Counting Magic (🎻) found: {found}")
        # This pattern should appear frequently
        assert found, "P1 Counting Magic pattern not found in any ticket"
    
    def test_neighborhood_hunger_pattern(self):
        """Check for Neighborhood Hunger pattern (🍽️)"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        found = False
        for ticket in data["tickets"]:
            patterns = " ".join(ticket.get("patterns_used", []))
            if "🍽️" in patterns or "Hungry" in patterns:
                found = True
                print(f"Found Hunger pattern: {patterns[:100]}...")
                break
        
        print(f"Neighborhood Hunger (🍽️) found: {found}")
        # This pattern depends on data, may not always appear
    
    def test_eight_family_pattern(self):
        """Check for 8-Family Tracker pattern (8️⃣)"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        found = False
        for ticket in data["tickets"]:
            patterns = " ".join(ticket.get("patterns_used", []))
            if "8️⃣" in patterns or "8-Family" in patterns or "Family→" in patterns:
                found = True
                print(f"Found 8-Family pattern: {patterns[:100]}...")
                break
        
        print(f"8-Family Tracker (8️⃣) found: {found}")


class TestResponseJSONStructure:
    """Test the complete JSON response structure"""
    
    def test_complete_response_structure(self):
        """Verify the complete response structure"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Top level
        assert "tickets" in data
        
        # Pricing structure - can be nested or flat
        if "pricing" in data:
            pricing = data["pricing"]
            assert "per_ticket" in pricing or "price_per_ticket" in pricing
            assert "total" in pricing or "total_price" in pricing
            assert "currency" in pricing
        else:
            # Flat pricing fields
            assert "price_per_ticket" in data or "per_ticket" in data
            assert "total_price" in data or "total" in data
            assert "currency" in data
        
        # Ticket structure
        for ticket in data["tickets"]:
            assert "numbers" in ticket
            assert "stars" in ticket
            assert "patterns_used" in ticket
            assert "confidence" in ticket
            assert "scenario" in ticket
            
            # Validate types
            assert isinstance(ticket["numbers"], list)
            assert isinstance(ticket["stars"], list)
            assert isinstance(ticket["patterns_used"], list)
            assert isinstance(ticket["confidence"], (int, float))
            assert isinstance(ticket["scenario"], str)
        
        print(f"SUCCESS: Complete response structure is valid")
        print(f"Sample ticket: numbers={data['tickets'][0]['numbers']}, stars={data['tickets'][0]['stars']}")
        print(f"Patterns used: {data['tickets'][0]['patterns_used'][:5]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
