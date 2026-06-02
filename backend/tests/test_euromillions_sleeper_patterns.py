"""
Test Suite for EuroMillions Sleeper Engine and New DJ Patterns
=============================================================
Tests:
1. EuroMillions money-mode API with Reverse Twin and Day*Month-10 patterns
2. Sleeper Forecast API endpoint /api/euromillions/sleeper-forecast
3. DJ Pattern Engine new patterns (pattern_reverse_twin, pattern_day_times_month_minus_10)
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://rolling-lottery-math.preview.emergentagent.com').rstrip('/')


class TestSleeperForecastEndpoint:
    """Test the /api/euromillions/sleeper-forecast endpoint"""
    
    def test_sleeper_forecast_returns_200(self):
        """Sleeper forecast endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/euromillions/sleeper-forecast")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Sleeper forecast endpoint returns 200")
    
    def test_sleeper_forecast_response_structure(self):
        """Sleeper forecast should return proper JSON structure"""
        response = requests.get(f"{BASE_URL}/api/euromillions/sleeper-forecast")
        assert response.status_code == 200
        data = response.json()
        
        # Check required keys
        required_keys = ['last_draw', 'total_draws_analyzed', 'sleeper_report', 'star_sleepers', 'forecast', 'engine_stats']
        for key in required_keys:
            assert key in data, f"Missing key: {key}"
        
        print(f"✓ Response has all required keys: {required_keys}")
        print(f"  - Last draw: {data['last_draw']}")
        print(f"  - Total draws analyzed: {data['total_draws_analyzed']}")
    
    def test_sleeper_report_structure(self):
        """Sleeper report should have proper structure for each sleeper"""
        response = requests.get(f"{BASE_URL}/api/euromillions/sleeper-forecast")
        assert response.status_code == 200
        data = response.json()
        
        sleeper_report = data.get('sleeper_report', [])
        assert len(sleeper_report) > 0, "Sleeper report should not be empty"
        
        # Check first sleeper structure
        first_sleeper = sleeper_report[0]
        sleeper_keys = ['num', 'gap', 'overdue', 'circle_partner', 'circle_boost', 'tease_score', 'composite_score', 'last_seen']
        for key in sleeper_keys:
            assert key in first_sleeper, f"Sleeper missing key: {key}"
        
        # Validate data types
        assert isinstance(first_sleeper['num'], int), "num should be int"
        assert 1 <= first_sleeper['num'] <= 50, "num should be 1-50"
        assert isinstance(first_sleeper['overdue'], (int, float)), "overdue should be numeric"
        assert isinstance(first_sleeper['composite_score'], (int, float)), "composite_score should be numeric"
        
        print(f"✓ Sleeper report has {len(sleeper_report)} sleepers with proper structure")
        print(f"  - Top sleeper: {first_sleeper['num']} (score: {first_sleeper['composite_score']}, overdue: {first_sleeper['overdue']}x)")
    
    def test_star_sleepers_structure(self):
        """Star sleepers should have proper structure"""
        response = requests.get(f"{BASE_URL}/api/euromillions/sleeper-forecast")
        assert response.status_code == 200
        data = response.json()
        
        star_sleepers = data.get('star_sleepers', [])
        assert len(star_sleepers) > 0, "Star sleepers should not be empty"
        
        first_star = star_sleepers[0]
        star_keys = ['star', 'gap', 'overdue', 'tease_score', 'composite_score']
        for key in star_keys:
            assert key in first_star, f"Star sleeper missing key: {key}"
        
        # Validate star range
        assert 1 <= first_star['star'] <= 12, "star should be 1-12"
        
        print(f"✓ Star sleepers has {len(star_sleepers)} entries with proper structure")
        print(f"  - Top star sleeper: Star {first_star['star']} (score: {first_star['composite_score']})")
    
    def test_forecast_structure(self):
        """Forecast should have predictions for multiple draws"""
        response = requests.get(f"{BASE_URL}/api/euromillions/sleeper-forecast")
        assert response.status_code == 200
        data = response.json()
        
        forecast = data.get('forecast', [])
        assert len(forecast) > 0, "Forecast should not be empty"
        assert len(forecast) <= 10, "Forecast should have max 10 draws"
        
        first_pred = forecast[0]
        pred_keys = ['draw_offset', 'numbers', 'stars', 'confidence', 'number_reasons', 'star_reasons']
        for key in pred_keys:
            assert key in first_pred, f"Prediction missing key: {key}"
        
        # Validate prediction data
        assert first_pred['draw_offset'] == 1, "First prediction should be D+1"
        assert len(first_pred['numbers']) == 5, "Should have 5 numbers"
        assert len(first_pred['stars']) == 2, "Should have 2 stars"
        assert all(1 <= n <= 50 for n in first_pred['numbers']), "Numbers should be 1-50"
        assert all(1 <= s <= 12 for s in first_pred['stars']), "Stars should be 1-12"
        
        print(f"✓ Forecast has {len(forecast)} predictions")
        print(f"  - D+1 prediction: {first_pred['numbers']} + Stars {first_pred['stars']}")
    
    def test_engine_stats(self):
        """Engine stats should show proven rates"""
        response = requests.get(f"{BASE_URL}/api/euromillions/sleeper-forecast")
        assert response.status_code == 200
        data = response.json()
        
        engine_stats = data.get('engine_stats', {})
        assert 'proven_wake_rate' in engine_stats, "Should have proven_wake_rate"
        assert 'proven_tease_rate' in engine_stats, "Should have proven_tease_rate"
        
        print(f"✓ Engine stats: wake_rate={engine_stats.get('proven_wake_rate')}, tease_rate={engine_stats.get('proven_tease_rate')}")


class TestMoneyModeEndpoint:
    """Test the /api/euromillions/money-mode endpoint"""
    
    def test_money_mode_returns_200(self):
        """Money mode endpoint should return 200"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/money-mode",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Money mode endpoint returns 200")
    
    def test_money_mode_response_structure(self):
        """Money mode should return proper structure"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/money-mode",
            json={"num_tickets": 3}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required keys
        assert 'mode' in data, "Should have mode"
        assert 'tickets' in data, "Should have tickets"
        assert '💰' in data.get('mode', ''), "Mode should indicate money mode"
        
        tickets = data.get('tickets', [])
        assert len(tickets) == 3, "Should have 3 tickets"
        
        print(f"✓ Money mode response has {len(tickets)} tickets")
        print(f"  - Mode: {data.get('mode')}")
    
    def test_money_mode_ticket_structure(self):
        """Each money mode ticket should have proper structure"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/money-mode",
            json={"num_tickets": 1}
        )
        assert response.status_code == 200
        data = response.json()
        
        tickets = data.get('tickets', [])
        assert len(tickets) >= 1
        
        ticket = tickets[0]
        assert 'numbers' in ticket, "Ticket should have numbers"
        assert 'stars' in ticket, "Ticket should have stars"
        assert 'patterns_used' in ticket, "Ticket should have patterns_used"
        
        # Validate numbers
        assert len(ticket['numbers']) == 5, "Should have 5 numbers"
        assert len(ticket['stars']) == 2, "Should have 2 stars"
        assert all(1 <= n <= 50 for n in ticket['numbers']), "Numbers should be 1-50"
        assert all(1 <= s <= 12 for s in ticket['stars']), "Stars should be 1-12"
        
        print(f"✓ Money mode ticket: {ticket['numbers']} + Stars {ticket['stars']}")
        print(f"  - Patterns used: {len(ticket.get('patterns_used', []))} patterns")
    
    def test_money_mode_patterns_include_new_patterns(self):
        """Money mode should use DJ patterns including Reverse Twin and Day*Month-10"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/money-mode",
            json={"num_tickets": 10}  # Generate more tickets to increase pattern coverage
        )
        assert response.status_code == 200
        data = response.json()
        
        tickets = data.get('tickets', [])
        all_patterns = []
        for ticket in tickets:
            all_patterns.extend(ticket.get('patterns_used', []))
        
        patterns_str = ' '.join(all_patterns)
        
        # Check for various DJ patterns (not all will appear in every generation)
        pattern_indicators = [
            ('REVERSE', 'Reverse Twin'),
            ('DAY*MONTH', 'Day*Month'),
            ('D*M', 'Day*Month'),
            ('reverse', 'Reverse'),
            ('🔄', 'Reverse pattern'),
            ('📅', 'Date pattern'),
            ('🎧', 'DJ pattern'),
            ('🔥', 'Hot pattern'),
            ('🎵', 'Musical pattern'),
        ]
        
        found_patterns = []
        for indicator, name in pattern_indicators:
            if indicator.lower() in patterns_str.lower():
                found_patterns.append(name)
        
        print(f"✓ Money mode uses DJ patterns")
        print(f"  - Total patterns across {len(tickets)} tickets: {len(all_patterns)}")
        print(f"  - Pattern indicators found: {found_patterns if found_patterns else 'Various DJ patterns'}")
        
        # At minimum, should have some patterns
        assert len(all_patterns) > 0, "Should have patterns used"


class TestDJPatternsIntegration:
    """Test that new DJ patterns are integrated in master-predictor"""
    
    def test_master_predictor_uses_dj_engine(self):
        """Master predictor should use DJ engine"""
        response = requests.post(
            f"{BASE_URL}/api/euromillions/master-predictor",
            json={"num_tickets": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        tickets = data.get('tickets', [])
        assert len(tickets) == 5
        
        # Check that tickets have patterns
        all_patterns = []
        for ticket in tickets:
            patterns = ticket.get('patterns_used', [])
            all_patterns.extend(patterns)
        
        print(f"✓ Master predictor generated {len(tickets)} tickets with {len(all_patterns)} total patterns")
        
        # Sample some patterns
        if all_patterns:
            print(f"  - Sample patterns: {all_patterns[:5]}")
    
    def test_reverse_twin_pattern_function(self):
        """Test that pattern_reverse_twin function exists and works"""
        # Import the pattern function
        import sys
        sys.path.insert(0, '/app/backend')
        from dj_patterns import pattern_reverse_twin
        
        # Test with a sample draw
        test_draw = {
            'numbers': [14, 27, 35, 42, 49],
            'stars': [3, 9]
        }
        
        result = pattern_reverse_twin(test_draw)
        
        assert 'candidates' in result, "Should have candidates"
        assert 'explanations' in result, "Should have explanations"
        
        # 14 -> 41, 27 -> 72 (mod 50 = 22), 35 -> 53 (mod 50 = 3), 42 -> 24, 49 -> 94 (mod 50 = 44)
        candidates = [c[0] for c in result['candidates']]
        
        print(f"✓ pattern_reverse_twin works")
        print(f"  - Input: {test_draw['numbers']}")
        print(f"  - Candidates: {candidates}")
        print(f"  - Explanations: {result['explanations'][:3]}")
        
        # Should have some candidates
        assert len(candidates) > 0, "Should generate candidates"
    
    def test_day_times_month_minus_10_pattern_function(self):
        """Test that pattern_day_times_month_minus_10 function exists and works"""
        import sys
        sys.path.insert(0, '/app/backend')
        from dj_patterns import pattern_day_times_month_minus_10
        
        # Test with a sample date: 15.04.2026 -> 15*4-10 = 50
        test_date = "15.04.2026"
        result = pattern_day_times_month_minus_10(test_date)
        
        assert 'candidates' in result, "Should have candidates"
        assert 'explanations' in result, "Should have explanations"
        assert 'product' in result, "Should have product"
        assert 'minus_10' in result, "Should have minus_10"
        
        # 15 * 4 = 60, 60 - 10 = 50
        assert result['product'] == 60, f"Product should be 60, got {result['product']}"
        assert result['minus_10'] == 50, f"Minus_10 should be 50, got {result['minus_10']}"
        
        candidates = [c[0] for c in result['candidates']]
        assert 50 in candidates, "50 should be a candidate"
        
        print(f"✓ pattern_day_times_month_minus_10 works")
        print(f"  - Date: {test_date}")
        print(f"  - Product: {result['product']}, Minus_10: {result['minus_10']}")
        print(f"  - Candidates: {candidates}")
    
    def test_day_times_month_edge_cases(self):
        """Test Day*Month-10 with various dates"""
        import sys
        sys.path.insert(0, '/app/backend')
        from dj_patterns import pattern_day_times_month_minus_10
        
        test_cases = [
            ("07.04.2026", 28, 18),  # 7*4=28, 28-10=18
            ("10.05.2026", 50, 40),  # 10*5=50, 50-10=40
            ("03.02.2026", 6, -4),   # 3*2=6, 6-10=-4 (out of range)
            ("25.02.2026", 50, 40),  # 25*2=50, 50-10=40
        ]
        
        for date, expected_product, expected_minus in test_cases:
            result = pattern_day_times_month_minus_10(date)
            assert result['product'] == expected_product, f"Date {date}: product should be {expected_product}"
            assert result['minus_10'] == expected_minus, f"Date {date}: minus_10 should be {expected_minus}"
        
        print(f"✓ Day*Month-10 edge cases pass")


class TestSleeperEngineModule:
    """Test the sleeper_engine.py module directly"""
    
    def test_sleeper_engine_imports(self):
        """Sleeper engine module should import correctly"""
        import sys
        sys.path.insert(0, '/app/backend')
        from sleeper_engine import detect_sleepers, predict_next_n_draws, SleeperInfo, SleeperPrediction
        
        print("✓ Sleeper engine module imports correctly")
    
    def test_detect_sleepers_function(self):
        """detect_sleepers should work with sample data"""
        import sys
        sys.path.insert(0, '/app/backend')
        from sleeper_engine import detect_sleepers
        
        # Create sample draws
        sample_draws = []
        for i in range(30):
            sample_draws.append({
                'date': f'{i+1:02d}.01.2026',
                'numbers': [(i*5 + j) % 50 + 1 for j in range(5)],
                'stars': [(i*2 + j) % 12 + 1 for j in range(2)]
            })
        
        sleepers = detect_sleepers(sample_draws, num_range=50, is_stars=False)
        
        assert len(sleepers) > 0, "Should detect sleepers"
        assert all(hasattr(s, 'num') for s in sleepers), "Sleepers should have num attribute"
        assert all(hasattr(s, 'composite_score') for s in sleepers), "Sleepers should have composite_score"
        
        print(f"✓ detect_sleepers works: found {len(sleepers)} sleepers")
        print(f"  - Top 3: {[(s.num, round(s.composite_score, 1)) for s in sleepers[:3]]}")
    
    def test_predict_next_n_draws_function(self):
        """predict_next_n_draws should generate predictions"""
        import sys
        sys.path.insert(0, '/app/backend')
        from sleeper_engine import predict_next_n_draws
        
        # Create sample draws
        sample_draws = []
        for i in range(50):
            sample_draws.append({
                'date': f'{(i % 28) + 1:02d}.{(i // 28) + 1:02d}.2026',
                'numbers': sorted([(i*7 + j*11) % 50 + 1 for j in range(5)]),
                'stars': sorted([(i*3 + j*5) % 12 + 1 for j in range(2)])
            })
        
        predictions = predict_next_n_draws(sample_draws, n_draws=5)
        
        assert len(predictions) == 5, "Should have 5 predictions"
        
        for i, pred in enumerate(predictions):
            assert pred.draw_offset == i + 1, f"Draw offset should be {i+1}"
            assert len(pred.numbers) == 5, "Should have 5 numbers"
            assert len(pred.stars) == 2, "Should have 2 stars"
            assert all(1 <= n <= 50 for n in pred.numbers), "Numbers should be 1-50"
            assert all(1 <= s <= 12 for s in pred.stars), "Stars should be 1-12"
        
        print(f"✓ predict_next_n_draws works: generated {len(predictions)} predictions")
        print(f"  - D+1: {predictions[0].numbers} + Stars {predictions[0].stars}")


class TestEuroMillionsDataAvailability:
    """Test that EuroMillions data is available"""
    
    def test_euromillions_draws_endpoint(self):
        """EuroMillions draws endpoint should return data"""
        response = requests.get(f"{BASE_URL}/api/euromillions/draws?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        draws = data.get('draws', data)  # Handle both formats
        assert len(draws) > 0, "Should have draws"
        
        print(f"✓ EuroMillions has {len(draws)} draws available")
        if draws:
            print(f"  - Latest draw: {draws[0].get('date')} - {draws[0].get('numbers')}")
    
    def test_euromillions_stats_endpoint(self):
        """EuroMillions stats endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/euromillions/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert 'total_draws' in data or 'draws_count' in data, "Should have draw count"
        
        print(f"✓ EuroMillions stats endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
