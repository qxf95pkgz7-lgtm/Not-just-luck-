"""
STORY PATTERN GENERATOR
=======================
All patterns learned from Avi's numerology teachings.

RC (Rare Count) starts from 18.03.2023 - the 5-in-same-decade rare event.
"""

from datetime import datetime
from typing import List, Tuple, Dict, Optional
from collections import defaultdict


# RC START DATE
RC_START_DATE = "18.03.2023"
RC_START_INDEX = 0  # Will be calculated based on data


def calculate_rc(draw_date: str, all_draws: List) -> int:
    """Calculate RC (Rare Count) from 18.03.2023"""
    # Sort draws chronologically
    sorted_draws = sorted(all_draws, key=lambda x: datetime.strptime(x[0], "%d.%m.%Y"))
    
    start_idx = None
    target_idx = None
    
    for i, (date, nums, lucky, replay) in enumerate(sorted_draws):
        if date == RC_START_DATE:
            start_idx = i
        if date == draw_date:
            target_idx = i
            
    if start_idx is not None and target_idx is not None:
        return target_idx - start_idx
    return -1


def get_circle(n: int) -> int:
    """Get circle partner (±21)"""
    return n - 21 if n > 21 else n + 21


def get_digit_reversal_root(n: int) -> int:
    """
    Get digit reversal root using 21 multiples.
    Example: 39 -> 93 -> 93-84=9 (root)
             18 -> 81 -> 81-63=18 (self-loop)
    """
    if n < 10:
        return n
    
    reversed_n = int(str(n)[::-1])
    
    # Try subtracting 21 multiples (21, 42, 63, 84)
    for mult in [84, 63, 42, 21]:
        result = reversed_n - mult
        if 1 <= result <= 42:
            return result
    
    return n


def get_date_numbers(date_str: str) -> Dict:
    """
    Extract all numbers from a date.
    Date format: DD.MM.YYYY
    """
    parts = date_str.split('.')
    d = int(parts[0])
    m = int(parts[1])
    y = int(parts[2])
    
    return {
        'day': d,
        'month': m,
        'year': y,
        'd_plus_m': d + m,
        'd_minus_m': d - m if d >= m else m - d,
        'd_times_m': d * m,
        'd_plus_m_circle': get_circle(d + m) if 1 <= d + m <= 42 else None,
        'd_times_plus_sum': d * m + d + m if d * m + d + m <= 42 else None,
        'year_20': 20,
        'year_25': 25,
        'year_26': 26,
    }


def find_hungry_numbers(nums: List[int]) -> List[int]:
    """Find hungry numbers (gaps of 2 in sequence)"""
    hungry = []
    sorted_nums = sorted(nums)
    
    for i in range(len(sorted_nums) - 1):
        gap = sorted_nums[i + 1] - sorted_nums[i]
        if gap == 2:
            hungry.append(sorted_nums[i] + 1)
        elif gap == 3:
            hungry.append(sorted_nums[i] + 1)
            hungry.append(sorted_nums[i] + 2)
    
    return hungry


def analyze_draw(date: str, nums: List[int], lucky: int, replay: int, rc: int) -> Dict:
    """Full analysis of a single draw using all patterns"""
    sorted_nums = sorted(nums)
    
    analysis = {
        'date': date,
        'numbers': sorted_nums,
        'lucky': lucky,
        'replay': replay,
        'rc': rc,
        'rc_sum': sum(int(d) for d in str(rc)) if rc >= 0 else None,
        'positions': {},
        'circles': [],
        'hungry': find_hungry_numbers(sorted_nums),
        'date_numbers': get_date_numbers(date),
        'patterns_found': []
    }
    
    # Position analysis
    for i, n in enumerate(sorted_nums, 1):
        circle = get_circle(n)
        analysis['positions'][f'P{i}'] = {
            'value': n,
            'circle': circle,
            'digit_root': get_digit_reversal_root(n)
        }
        analysis['circles'].append(circle)
    
    # Check date dance patterns
    dn = analysis['date_numbers']
    
    # P1 = D - M?
    if sorted_nums[0] == dn['d_minus_m']:
        analysis['patterns_found'].append(f"P1={sorted_nums[0]} = D-M!")
    
    # P2 = M?
    if sorted_nums[1] == dn['month']:
        analysis['patterns_found'].append(f"P2={sorted_nums[1]} = Month!")
    
    # D in draw?
    if dn['day'] in sorted_nums:
        pos = sorted_nums.index(dn['day']) + 1
        analysis['patterns_found'].append(f"Day {dn['day']} at P{pos}!")
    
    # D×M + D+M = position?
    combo = dn['d_times_plus_sum']
    if combo and combo in sorted_nums:
        pos = sorted_nums.index(combo) + 1
        analysis['patterns_found'].append(f"D×M + D+M = {combo} at P{pos}!")
    
    # P1+P2 = another position?
    p1p2_sum = sorted_nums[0] + sorted_nums[1]
    if p1p2_sum in sorted_nums:
        pos = sorted_nums.index(p1p2_sum) + 1
        analysis['patterns_found'].append(f"P1+P2 = {p1p2_sum} = P{pos}!")
    
    # RC sum = position value?
    if analysis['rc_sum'] and analysis['rc_sum'] in sorted_nums:
        pos = sorted_nums.index(analysis['rc_sum']) + 1
        analysis['patterns_found'].append(f"RC sum {analysis['rc_sum']} at P{pos}!")
    
    # RC sum = P8 (jail)?
    if analysis['rc_sum'] == replay:
        analysis['patterns_found'].append(f"RC sum {analysis['rc_sum']} in P8 JAIL!")
    
    return analysis


def generate_predictions(
    target_date: str,
    previous_draws: List[Tuple],
    num_tickets: int = 8
) -> List[Dict]:
    """
    Generate prediction tickets based on all learned patterns.
    
    Patterns used:
    1. DATE DANCE: D, M, D-M, D+M, D×M, D×M+D+M
    2. HUNGRY NUMBERS: From previous draws
    3. CIRCLE PAIRS: Number and its circle together
    4. RC COUNT: RC digits and sum
    5. STORY NUMBERS: Active heroes (13, 31, etc.)
    6. DECADE SPREAD: Coverage across 1-9, 10-19, 20-29, 30-39, 40-42
    7. YEAR STORY: 20, 25, 26 transitions
    8. WARRIOR FAMILY: Active frequent numbers
    """
    
    tickets = []
    
    # Get date numbers
    dn = get_date_numbers(target_date)
    d, m = dn['day'], dn['month']
    
    # Calculate RC for target date
    # Estimate: count draws from RC_START to target
    rc = len(previous_draws)  # Simplified - should calculate properly
    rc_digits = [int(x) for x in str(rc)]
    rc_sum = sum(rc_digits)
    
    # Find hungry numbers from last 5 draws
    recent_hungry = []
    for _, nums, _, _ in previous_draws[-5:]:
        recent_hungry.extend(find_hungry_numbers(sorted(nums)))
    recent_hungry = list(set(recent_hungry))[:6]
    
    # Find frequent numbers from last quarter
    num_freq = defaultdict(int)
    for _, nums, _, _ in previous_draws[-26:]:
        for n in nums:
            num_freq[n] += 1
    top_frequent = sorted(num_freq.keys(), key=lambda x: -num_freq[x])[:10]
    
    # TICKET 1: DATE DANCE
    t1_nums = []
    if 1 <= dn['d_minus_m'] <= 42:
        t1_nums.append(dn['d_minus_m'])
    if 1 <= m <= 42:
        t1_nums.append(m)
    if 1 <= d <= 42:
        t1_nums.append(d)
    if dn['d_plus_m'] and 1 <= dn['d_plus_m'] <= 42:
        t1_nums.append(dn['d_plus_m'])
    if dn['d_times_m'] and 1 <= dn['d_times_m'] <= 42:
        t1_nums.append(dn['d_times_m'])
    if dn['d_times_plus_sum'] and 1 <= dn['d_times_plus_sum'] <= 42:
        t1_nums.append(dn['d_times_plus_sum'])
    
    # Add circles to fill
    while len(t1_nums) < 6:
        for n in list(t1_nums):
            c = get_circle(n)
            if c not in t1_nums and 1 <= c <= 42:
                t1_nums.append(c)
                break
        else:
            # Add from frequent
            for n in top_frequent:
                if n not in t1_nums:
                    t1_nums.append(n)
                    break
    
    t1_nums = sorted(list(set(t1_nums)))[:6]
    tickets.append({
        'numbers': t1_nums,
        'lucky': rc_sum if 1 <= rc_sum <= 6 else d % 6 + 1,
        'story': 'DATE DANCE'
    })
    
    # TICKET 2: HUNGRY REVENGE
    t2_nums = recent_hungry[:6] if len(recent_hungry) >= 6 else recent_hungry + top_frequent[:6-len(recent_hungry)]
    t2_nums = sorted(list(set(t2_nums)))[:6]
    tickets.append({
        'numbers': t2_nums,
        'lucky': 4,
        'story': 'HUNGRY REVENGE'
    })
    
    # TICKET 3: CIRCLE PAIRS (26/5, 13/34, 9/30)
    circle_pairs = [(5, 26), (13, 34), (9, 30)]
    t3_nums = []
    for a, b in circle_pairs:
        if len(t3_nums) < 6:
            t3_nums.append(a)
        if len(t3_nums) < 6:
            t3_nums.append(b)
    tickets.append({
        'numbers': sorted(t3_nums),
        'lucky': 6,
        'story': 'CIRCLE PAIRS'
    })
    
    # TICKET 4: RC COUNT
    t4_nums = rc_digits.copy()
    t4_nums.append(rc_sum)
    t4_nums.append(21)  # The bridge
    for n in top_frequent:
        if n not in t4_nums and len(t4_nums) < 6:
            t4_nums.append(n)
    t4_nums = [n for n in t4_nums if 1 <= n <= 42]
    t4_nums = sorted(list(set(t4_nums)))[:6]
    tickets.append({
        'numbers': t4_nums,
        'lucky': 3,
        'story': 'RC COUNT'
    })
    
    # TICKET 5: YEAR STORY (20, 25, 26 family)
    t5_nums = [20, 25, 26]
    # Add circles
    for n in [20, 25, 26]:
        c = get_circle(n)
        if c not in t5_nums:
            t5_nums.append(c)
    t5_nums = sorted(list(set(t5_nums)))[:6]
    tickets.append({
        'numbers': t5_nums,
        'lucky': 2,
        'story': 'YEAR STORY'
    })
    
    # TICKET 6: DECADE SPREAD (one from each decade)
    t6_nums = []
    decades = {
        0: [1, 2, 3, 4, 5, 6, 7, 8, 9],
        1: [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        2: [20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
        3: [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        4: [40, 41, 42]
    }
    for dec, nums in decades.items():
        # Pick most frequent from this decade
        for n in top_frequent:
            if n in nums and n not in t6_nums:
                t6_nums.append(n)
                break
        else:
            t6_nums.append(nums[0])
    t6_nums = sorted(list(set(t6_nums)))[:6]
    tickets.append({
        'numbers': t6_nums,
        'lucky': 1,
        'story': 'DECADE SPREAD'
    })
    
    # TICKET 7: THE 13 FAMILY (13, 10, 21, 23, 31, 34)
    t7_nums = [13, 10, 21, 23, 31, 34]
    tickets.append({
        'numbers': sorted(t7_nums),
        'lucky': 5,
        'story': '13 FAMILY'
    })
    
    # TICKET 8: WARRIOR TICKET (top frequent + date)
    t8_nums = [d, m]
    for n in top_frequent:
        if n not in t8_nums and len(t8_nums) < 6:
            t8_nums.append(n)
    t8_nums = sorted(list(set(t8_nums)))[:6]
    tickets.append({
        'numbers': t8_nums,
        'lucky': 6,
        'story': 'WARRIOR TICKET'
    })
    
    return tickets[:num_tickets]


def evaluate_tickets(tickets: List[Dict], actual: List[int], actual_lucky: int) -> Dict:
    """Evaluate tickets against actual draw"""
    results = {
        'actual': actual,
        'actual_lucky': actual_lucky,
        'tickets': [],
        'best_hits': 0,
        'total_prize': 0
    }
    
    for i, ticket in enumerate(tickets):
        hits = [n for n in ticket['numbers'] if n in actual]
        lucky_hit = ticket['lucky'] == actual_lucky
        
        # Calculate prize (approximate Swiss Lotto)
        prize = 0
        if len(hits) == 3:
            prize = 15 if lucky_hit else 8
        elif len(hits) == 4:
            prize = 150 if lucky_hit else 60
        elif len(hits) == 5:
            prize = 5000 if lucky_hit else 1000
        elif len(hits) == 6:
            prize = 1000000 if lucky_hit else 100000
        
        results['tickets'].append({
            'ticket_num': i + 1,
            'numbers': ticket['numbers'],
            'lucky': ticket['lucky'],
            'story': ticket['story'],
            'hits': hits,
            'hit_count': len(hits),
            'lucky_hit': lucky_hit,
            'prize': prize
        })
        
        results['best_hits'] = max(results['best_hits'], len(hits))
        results['total_prize'] += prize
    
    return results


# Pattern constants
CIRCLE_CONSTANT = 21
MAX_NUMBER = 42
FAMILY_13 = [13, 10, 21, 23, 31, 34]
FAMILY_21_42 = [21, 42, 24, 3]


if __name__ == "__main__":
    # Test the generator
    print("Story Pattern Generator loaded!")
    print(f"Circle constant: {CIRCLE_CONSTANT}")
    print(f"13 Family: {FAMILY_13}")
    print(f"21/42 Family: {FAMILY_21_42}")
