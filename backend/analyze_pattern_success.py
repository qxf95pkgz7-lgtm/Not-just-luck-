"""
🎧 LUCKY JACK'S PATTERN DJ ANALYZER 🎻
=====================================
Backtest ALL patterns against 2025 EuroMillions draws to find which patterns
are actually hitting - then tune the generator like a DJ mixing the best tracks!

PATTERNS TO TEST:
1. Circle Partner (+25/-25)
2. Reverse Logic (flip digits)
3. Star Prophecy (circle(S1), circle(S2), S1+S2)
4. P3 Hunger (missing numbers between neighbors)
5. 49→45 Call
6. 8-Family Tracker
7. P1+P2 Sum Prediction
8. Quarter Echo
9. P4 Sequence
10. Star Diff → Position Gap

Created: April 2026 for the DJ Mission!
"""

from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
from datetime import datetime
from collections import defaultdict, Counter

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def circle(n: int) -> int:
    """Get circle partner (+25 mod 50)"""
    partner = n + 25
    if partner > 50:
        partner -= 50
    return partner

def reverse_num(n: int) -> int:
    """Reverse digits, mod 50 if needed"""
    rev = int(str(n)[::-1])
    if rev > 50:
        rev = rev % 50 if rev % 50 != 0 else 50
    return rev

def parse_date(date_str: str):
    """Parse DD.MM.YYYY to datetime"""
    return datetime.strptime(date_str, "%d.%m.%Y")

def get_2025_draws(all_draws):
    """Get only 2025 draws sorted by date (newest first)"""
    draws_2025 = []
    for d in all_draws:
        dt = parse_date(d['date'])
        if dt.year == 2025:
            draws_2025.append(d)
    # Sort newest first
    draws_2025.sort(key=lambda x: parse_date(x['date']), reverse=True)
    return draws_2025

def get_all_recent_draws(all_draws, year_start=2025):
    """Get draws from year_start onwards, sorted newest first"""
    draws = []
    for d in all_draws:
        dt = parse_date(d['date'])
        if dt.year >= year_start:
            draws.append(d)
    draws.sort(key=lambda x: parse_date(x['date']), reverse=True)
    return draws

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 1: CIRCLE PARTNER TEST
# ═══════════════════════════════════════════════════════════════════════════════

def test_circle_partner(draws):
    """
    Test: If number N appeared in draw i, does circle(N) appear in draw i+1?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        current_nums = set(current_draw['numbers'])
        prev_nums = prev_draw['numbers']
        
        for n in prev_nums:
            partner = circle(n)
            total_tests += 1
            if partner in current_nums:
                hits += 1
                detailed_hits.append({
                    'prev_date': prev_draw['date'],
                    'curr_date': current_draw['date'],
                    'number': n,
                    'partner': partner
                })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Circle Partner (+25)',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 2: REVERSE LOGIC TEST
# ═══════════════════════════════════════════════════════════════════════════════

def test_reverse_logic(draws):
    """
    Test: If number N appeared in draw i, does reverse(N) appear in draw i+1?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        current_nums = set(current_draw['numbers'])
        prev_nums = prev_draw['numbers']
        
        for n in prev_nums:
            if n >= 10:  # Only test numbers with 2 digits
                rev = reverse_num(n)
                total_tests += 1
                if rev in current_nums:
                    hits += 1
                    detailed_hits.append({
                        'prev_date': prev_draw['date'],
                        'curr_date': current_draw['date'],
                        'number': n,
                        'reverse': rev
                    })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Reverse Logic (flip digits)',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 3: STAR PROPHECY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_star_prophecy_circle_s1(draws):
    """
    Test: Does circle(S1) appear in next draw's numbers?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        current_nums = set(current_draw['numbers'])
        s1 = sorted(prev_draw['stars'])[0]
        
        circle_s1 = s1 + 25
        total_tests += 1
        
        if circle_s1 in current_nums:
            hits += 1
            detailed_hits.append({
                'prev_date': prev_draw['date'],
                'curr_date': current_draw['date'],
                's1': s1,
                'circle_s1': circle_s1
            })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Star Prophecy: circle(S1)',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

def test_star_prophecy_circle_s2(draws):
    """
    Test: Does circle(S2) appear in next draw's numbers?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        current_nums = set(current_draw['numbers'])
        s2 = sorted(prev_draw['stars'])[1]
        
        circle_s2 = s2 + 25 if s2 <= 25 else s2 - 25
        total_tests += 1
        
        if 1 <= circle_s2 <= 50 and circle_s2 in current_nums:
            hits += 1
            detailed_hits.append({
                'prev_date': prev_draw['date'],
                'curr_date': current_draw['date'],
                's2': s2,
                'circle_s2': circle_s2
            })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Star Prophecy: circle(S2)',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

def test_star_prophecy_sum(draws):
    """
    Test: Does S1+S2 appear in next draw's numbers?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        current_nums = set(current_draw['numbers'])
        stars = sorted(prev_draw['stars'])
        star_sum = stars[0] + stars[1]
        
        if star_sum <= 50:
            total_tests += 1
            if star_sum in current_nums:
                hits += 1
                detailed_hits.append({
                    'prev_date': prev_draw['date'],
                    'curr_date': current_draw['date'],
                    's1': stars[0],
                    's2': stars[1],
                    'sum': star_sum
                })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Star Prophecy: S1+S2 Sum',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

def test_star_prophecy_s1_repeat(draws):
    """
    Test: Does S1 repeat in next draw's stars?
    """
    hits = 0
    total_tests = 0
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        current_stars = set(current_draw['stars'])
        s1 = sorted(prev_draw['stars'])[0]
        
        total_tests += 1
        if s1 in current_stars:
            hits += 1
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Star Prophecy: S1 Repeat',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': []
    }

def test_star_prophecy_s2_repeat(draws):
    """
    Test: Does S2 repeat in next draw's stars?
    """
    hits = 0
    total_tests = 0
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        current_stars = set(current_draw['stars'])
        s2 = sorted(prev_draw['stars'])[1]
        
        total_tests += 1
        if s2 in current_stars:
            hits += 1
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Star Prophecy: S2 Repeat',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': []
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 4: P3 HUNGER (Neighborhood Gap)
# ═══════════════════════════════════════════════════════════════════════════════

def test_p3_hunger(draws):
    """
    Test: When P2 and P4 have a gap of 2 around P3, does the 'hungry' middle number 
    appear in the next draw?
    Example: P2=27, P4=29 -> 28 is hungry -> does 28 appear next?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        current_nums = set(current_draw['numbers'])
        prev_nums = sorted(prev_draw['numbers'])
        
        # Check for gaps of exactly 2 between consecutive numbers
        for j in range(len(prev_nums) - 1):
            gap = prev_nums[j + 1] - prev_nums[j]
            if gap == 2:
                hungry = prev_nums[j] + 1
                total_tests += 1
                if hungry in current_nums:
                    hits += 1
                    detailed_hits.append({
                        'prev_date': prev_draw['date'],
                        'curr_date': current_draw['date'],
                        'gap_numbers': (prev_nums[j], prev_nums[j + 1]),
                        'hungry': hungry
                    })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'P3 Hunger (Gap=2)',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 5: 49→45 CALL
# ═══════════════════════════════════════════════════════════════════════════════

def test_49_calls_45(draws):
    """
    Test: When 49 appears at P5, does 45 appear in next draw?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        prev_nums = sorted(prev_draw['numbers'])
        current_nums = set(current_draw['numbers'])
        
        # Check if 49 is at P5 (highest position)
        if prev_nums[4] == 49:
            total_tests += 1
            if 45 in current_nums:
                hits += 1
                detailed_hits.append({
                    'prev_date': prev_draw['date'],
                    'curr_date': current_draw['date'],
                    'prev_nums': prev_nums,
                    'hit_45': True
                })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': '49→45 Call (P5=49)',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 6: 8-FAMILY TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

def test_8_family(draws):
    """
    Test: Does any member of 8-family (8, 18, 28, 38, 48) appear in each draw?
    """
    family = [8, 18, 28, 38, 48]
    hits = 0
    member_hits = Counter()
    
    for draw in draws:
        nums = set(draw['numbers'])
        hit_this_draw = False
        for member in family:
            if member in nums:
                member_hits[member] += 1
                hit_this_draw = True
        if hit_this_draw:
            hits += 1
    
    hit_rate = hits / len(draws) * 100 if draws else 0
    return {
        'pattern': '8-Family Presence',
        'hits': hits,
        'total_tests': len(draws),
        'hit_rate': hit_rate,
        'member_breakdown': dict(member_hits),
        'examples': []
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 7: P1+P2 SUM IN NEXT DRAW
# ═══════════════════════════════════════════════════════════════════════════════

def test_p1p2_sum_pattern(draws):
    """
    Test: Does P1+P2 from previous draw appear somewhere in next draw?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        prev_nums = sorted(prev_draw['numbers'])
        current_nums = set(current_draw['numbers'])
        
        p1p2_sum = prev_nums[0] + prev_nums[1]
        
        if p1p2_sum <= 50:
            total_tests += 1
            if p1p2_sum in current_nums:
                hits += 1
                detailed_hits.append({
                    'prev_date': prev_draw['date'],
                    'curr_date': current_draw['date'],
                    'p1': prev_nums[0],
                    'p2': prev_nums[1],
                    'sum': p1p2_sum
                })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'P1+P2 Sum in Next Draw',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 8: DIRECT ADDITION (A+B=C in same ticket)
# ═══════════════════════════════════════════════════════════════════════════════

def test_direct_addition(draws):
    """
    Test: How often does A + B = C exist within the same ticket?
    """
    hits = 0
    detailed_hits = []
    
    for draw in draws:
        nums = sorted(draw['numbers'])
        found_abc = False
        for i, a in enumerate(nums):
            for j, b in enumerate(nums):
                if i < j:
                    c = a + b
                    if c in nums:
                        found_abc = True
                        detailed_hits.append({
                            'date': draw['date'],
                            'a': a,
                            'b': b,
                            'c': c,
                            'numbers': nums
                        })
                        break
            if found_abc:
                break
        if found_abc:
            hits += 1
    
    hit_rate = hits / len(draws) * 100 if draws else 0
    return {
        'pattern': 'Direct Addition (A+B=C)',
        'hits': hits,
        'total_tests': len(draws),
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 9: P1+P2 CONSECUTIVE SUM (new value = old sum ± variance)
# ═══════════════════════════════════════════════════════════════════════════════

def test_p1p2_consecutive_sum(draws):
    """
    Test: Does next draw's P1+P2 equal previous draw's P1+P2 (within ±3)?
    """
    hits_exact = 0
    hits_within_3 = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        curr_nums = sorted(current_draw['numbers'])
        prev_nums = sorted(prev_draw['numbers'])
        
        curr_sum = curr_nums[0] + curr_nums[1]
        prev_sum = prev_nums[0] + prev_nums[1]
        
        total_tests += 1
        diff = abs(curr_sum - prev_sum)
        
        if diff == 0:
            hits_exact += 1
            hits_within_3 += 1
            detailed_hits.append({
                'prev_date': prev_draw['date'],
                'curr_date': current_draw['date'],
                'prev_sum': prev_sum,
                'curr_sum': curr_sum,
                'match': 'EXACT'
            })
        elif diff <= 3:
            hits_within_3 += 1
            detailed_hits.append({
                'prev_date': prev_draw['date'],
                'curr_date': current_draw['date'],
                'prev_sum': prev_sum,
                'curr_sum': curr_sum,
                'match': f'±{diff}'
            })
    
    hit_rate_exact = hits_exact / total_tests * 100 if total_tests > 0 else 0
    hit_rate_within_3 = hits_within_3 / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'P1+P2 Consecutive Sum',
        'hits_exact': hits_exact,
        'hits_within_3': hits_within_3,
        'total_tests': total_tests,
        'hit_rate_exact': hit_rate_exact,
        'hit_rate_within_3': hit_rate_within_3,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 10: STAR DIFF → POSITION GAP
# ═══════════════════════════════════════════════════════════════════════════════

def test_star_diff_position_gap(draws):
    """
    Test: Does star diff (S2-S1) equal any position gap (P2-P1, P3-P2, etc.)?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        prev_stars = sorted(prev_draw['stars'])
        star_diff = prev_stars[1] - prev_stars[0]
        
        curr_nums = sorted(current_draw['numbers'])
        position_gaps = [
            curr_nums[1] - curr_nums[0],  # P2-P1
            curr_nums[2] - curr_nums[1],  # P3-P2
            curr_nums[3] - curr_nums[2],  # P4-P3
            curr_nums[4] - curr_nums[3],  # P5-P4
        ]
        
        total_tests += 1
        if star_diff in position_gaps:
            hits += 1
            detailed_hits.append({
                'prev_date': prev_draw['date'],
                'curr_date': current_draw['date'],
                'star_diff': star_diff,
                'position_gaps': position_gaps
            })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Star Diff → Position Gap',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# BONUS PATTERN: Number ending in S1
# ═══════════════════════════════════════════════════════════════════════════════

def test_number_ending_in_s1(draws):
    """
    Test: Does a number ending in S1 appear in next draw?
    """
    hits = 0
    total_tests = 0
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        s1 = sorted(prev_draw['stars'])[0]
        current_nums = current_draw['numbers']
        
        total_tests += 1
        for n in current_nums:
            if n % 10 == s1:
                hits += 1
                break
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Number ending in S1',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': []
    }

# ═══════════════════════════════════════════════════════════════════════════════
# BONUS PATTERN: Circle of P2 in next draw
# ═══════════════════════════════════════════════════════════════════════════════

def test_circle_p2_in_next(draws):
    """
    Test: Does circle(P2) from previous draw appear in next draw?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        prev_p2 = sorted(prev_draw['numbers'])[1]
        circle_p2 = circle(prev_p2)
        current_nums = set(current_draw['numbers'])
        
        total_tests += 1
        if circle_p2 in current_nums:
            hits += 1
            detailed_hits.append({
                'prev_date': prev_draw['date'],
                'curr_date': current_draw['date'],
                'p2': prev_p2,
                'circle_p2': circle_p2
            })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Circle of P2 in Next Draw',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# BONUS PATTERN: Circle of P3 in next draw
# ═══════════════════════════════════════════════════════════════════════════════

def test_circle_p3_in_next(draws):
    """
    Test: Does circle(P3) from previous draw appear in next draw?
    """
    hits = 0
    total_tests = 0
    detailed_hits = []
    
    for i in range(len(draws) - 1):
        current_draw = draws[i]
        prev_draw = draws[i + 1]
        
        prev_p3 = sorted(prev_draw['numbers'])[2]
        circle_p3 = circle(prev_p3)
        current_nums = set(current_draw['numbers'])
        
        total_tests += 1
        if circle_p3 in current_nums:
            hits += 1
            detailed_hits.append({
                'prev_date': prev_draw['date'],
                'curr_date': current_draw['date'],
                'p3': prev_p3,
                'circle_p3': circle_p3
            })
    
    hit_rate = hits / total_tests * 100 if total_tests > 0 else 0
    return {
        'pattern': 'Circle of P3 in Next Draw',
        'hits': hits,
        'total_tests': total_tests,
        'hit_rate': hit_rate,
        'examples': detailed_hits[:5]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DJ SESSION
# ═══════════════════════════════════════════════════════════════════════════════

def run_dj_session(year=2025):
    """
    🎧 THE DJ SESSION - Analyze all patterns and rank them! 🎻
    """
    print("=" * 60)
    print("🎧 LUCKY JACK'S PATTERN DJ SESSION 🎻")
    print(f"   Analyzing {year} EuroMillions Data")
    print("=" * 60)
    print()
    
    # Get data
    if year == 2025:
        draws = get_2025_draws(EUROMILLIONS_DRAWS_2024_2026)
    else:
        draws = get_all_recent_draws(EUROMILLIONS_DRAWS_2024_2026, year)
    
    print(f"📊 Total draws analyzed: {len(draws)}")
    print(f"📅 Date range: {draws[-1]['date']} to {draws[0]['date']}")
    print()
    
    # Run all tests
    results = []
    
    # Core patterns
    results.append(test_circle_partner(draws))
    results.append(test_reverse_logic(draws))
    results.append(test_star_prophecy_circle_s1(draws))
    results.append(test_star_prophecy_circle_s2(draws))
    results.append(test_star_prophecy_sum(draws))
    results.append(test_star_prophecy_s1_repeat(draws))
    results.append(test_star_prophecy_s2_repeat(draws))
    results.append(test_p3_hunger(draws))
    results.append(test_49_calls_45(draws))
    results.append(test_8_family(draws))
    results.append(test_p1p2_sum_pattern(draws))
    results.append(test_direct_addition(draws))
    results.append(test_p1p2_consecutive_sum(draws))
    results.append(test_star_diff_position_gap(draws))
    results.append(test_number_ending_in_s1(draws))
    results.append(test_circle_p2_in_next(draws))
    results.append(test_circle_p3_in_next(draws))
    
    # Sort by hit rate
    results.sort(key=lambda x: x.get('hit_rate', x.get('hit_rate_within_3', 0)), reverse=True)
    
    print("🎵 PATTERN HIT RATES (sorted best to worst):")
    print("-" * 60)
    
    bangers = []
    decent = []
    fillers = []
    
    for r in results:
        pattern = r['pattern']
        if 'hit_rate_within_3' in r:
            # Special handling for consecutive sum pattern
            rate = r['hit_rate_within_3']
            rate_str = f"{rate:.1f}% (within ±3)"
            exact_rate = r['hit_rate_exact']
            rate_str += f" | {exact_rate:.1f}% exact"
        else:
            rate = r['hit_rate']
            rate_str = f"{rate:.1f}%"
        
        hits = r.get('hits', r.get('hits_within_3', 0))
        tests = r.get('total_tests', 0)
        
        # Categorize
        if rate >= 15:
            category = "🔥 BANGER"
            bangers.append(r)
        elif rate >= 10:
            category = "🎵 DECENT"
            decent.append(r)
        else:
            category = "📉 FILLER"
            fillers.append(r)
        
        print(f"{category} | {pattern}")
        print(f"         Hit Rate: {rate_str} ({hits}/{tests} tests)")
        print()
    
    # Summary
    print("=" * 60)
    print("🎧 DJ RECOMMENDATION SUMMARY")
    print("=" * 60)
    print()
    print(f"🔥 BANGERS (>=15% hit rate): {len(bangers)}")
    for b in bangers:
        rate = b.get('hit_rate', b.get('hit_rate_within_3', 0))
        print(f"   - {b['pattern']}: {rate:.1f}%")
    print()
    print(f"🎵 DECENT (10-15% hit rate): {len(decent)}")
    for d in decent:
        rate = d.get('hit_rate', d.get('hit_rate_within_3', 0))
        print(f"   - {d['pattern']}: {rate:.1f}%")
    print()
    print(f"📉 FILLERS (<10% hit rate): {len(fillers)}")
    for f in fillers:
        rate = f.get('hit_rate', f.get('hit_rate_within_3', 0))
        print(f"   - {f['pattern']}: {rate:.1f}%")
    
    return results, bangers, decent, fillers


if __name__ == "__main__":
    results, bangers, decent, fillers = run_dj_session(2025)
