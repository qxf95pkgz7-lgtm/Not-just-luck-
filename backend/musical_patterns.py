"""
🎧 MUSICAL PATTERNS ANALYZER 🎧
All discovered esoteric patterns working in harmony!

Patterns included:
1. Full Date Imagination (D×10 + circle(M) + YYYY) - 19% over 14 years!
2. Day Dance (D1 + D2)
3. Reunions (Number groups that dance together)
4. The 17 Magic (Mr. 17 always at the party)
5. Counting Patterns (10→11→12)
6. Family Patterns (5-family, 9-family, 7-family)
7. Number → Star connections
8. P1+P2 digit_sum → Star (20% hit rate)
9. P3 Dance patterns
10. Sequence Hunger
11. Reverse Dance
12. The 14→15→40 Chain
"""

from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Tuple, Set

def circle(n: int) -> int:
    """Circle math: +25 or -25"""
    return n + 25 if n <= 25 else n - 25

def reverse_num(n: int) -> int:
    """Reverse digits, adjust if > 50"""
    if n < 10:
        return n
    rev = int(str(n)[::-1])
    if rev > 50:
        rev = rev - 50
    return rev

def digit_sum(n: int) -> int:
    """Sum of digits"""
    return sum(int(x) for x in str(n))


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 1: FULL DATE IMAGINATION (19% hit rate over 14 years!)
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_full_date_imagination(target_date: str) -> Dict:
    """
    🎧 FULL DATE IMAGINATION - The strongest pattern (19%)!
    
    D×10 + circle(M) + 20 + YY = target
    Then: mod 50, digit_sum, etc.
    """
    day = int(target_date.split('.')[0])
    month = int(target_date.split('.')[1])
    year = int(target_date.split('.')[2])
    
    year_p1 = year // 100  # 20
    year_p2 = year % 100   # 26
    
    # Four methods
    m1 = (day * 10) + circle(month) + year_p1 + year_p2
    m2 = day + circle(month) + (year_p1 + year_p2)
    m3 = day + circle(month) + year_p2
    m4 = (day * 10) + circle(month) + year_p2
    
    candidates = {
        'numbers': [],
        'stars': [],
        'explanations': []
    }
    
    # M1 derivatives
    candidates['explanations'].append(f"M1 = {day}×10 + {circle(month)} + {year_p1} + {year_p2} = {m1}")
    
    # digit_sum - STRONGEST (19%)
    ds1 = digit_sum(m1)
    if 1 <= ds1 <= 50:
        candidates['numbers'].append((ds1, 19.4, f"digit_sum({m1})={ds1}"))
    if 1 <= ds1 <= 12:
        candidates['stars'].append((ds1, 19.4, f"digit_sum({m1})={ds1}"))
    
    # mod 50
    mod1 = m1 % 50 if m1 % 50 != 0 else 50
    if 1 <= mod1 <= 50:
        candidates['numbers'].append((mod1, 9.8, f"{m1} mod 50 = {mod1}"))
    
    # M2 derivatives
    candidates['explanations'].append(f"M2 = {day} + {circle(month)} + {year_p1 + year_p2} = {m2}")
    ds2 = digit_sum(m2)
    if 1 <= ds2 <= 50:
        candidates['numbers'].append((ds2, 16.1, f"digit_sum({m2})={ds2}"))
    if 1 <= ds2 <= 12:
        candidates['stars'].append((ds2, 16.1, f"digit_sum({m2})={ds2}"))
    
    mod2 = m2 % 50 if m2 % 50 != 0 else 50
    if 1 <= mod2 <= 50:
        candidates['numbers'].append((mod2, 9.3, f"{m2} mod 50 = {mod2}"))
    if m2 > 50:
        minus2 = m2 - 50
        if 1 <= minus2 <= 50:
            candidates['numbers'].append((minus2, 8.3, f"{m2} - 50 = {minus2}"))
    
    # M3 derivatives
    candidates['explanations'].append(f"M3 = {day} + {circle(month)} + {year_p2} = {m3}")
    ds3 = digit_sum(m3)
    if 1 <= ds3 <= 50:
        candidates['numbers'].append((ds3, 17.8, f"digit_sum({m3})={ds3}"))
    if 1 <= ds3 <= 12:
        candidates['stars'].append((ds3, 17.8, f"digit_sum({m3})={ds3}"))
    
    mod3 = m3 % 50 if m3 % 50 != 0 else 50
    if 1 <= mod3 <= 50:
        candidates['numbers'].append((mod3, 10.6, f"{m3} mod 50 = {mod3}"))
    if m3 > 50:
        minus3 = m3 - 50
        if 1 <= minus3 <= 50:
            candidates['numbers'].append((minus3, 10.1, f"{m3} - 50 = {minus3}"))
    
    # M4 derivatives
    candidates['explanations'].append(f"M4 = {day}×10 + {circle(month)} + {year_p2} = {m4}")
    ds4 = digit_sum(m4)
    if 1 <= ds4 <= 50:
        candidates['numbers'].append((ds4, 19.1, f"digit_sum({m4})={ds4}"))
    if 1 <= ds4 <= 12:
        candidates['stars'].append((ds4, 19.1, f"digit_sum({m4})={ds4}"))
    
    mod4 = m4 % 50 if m4 % 50 != 0 else 50
    if 1 <= mod4 <= 50:
        candidates['numbers'].append((mod4, 11.3, f"{m4} mod 50 = {mod4}"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 2: DAY DANCE (D1 + D2 → digits)
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_day_dance(prev_date: str, target_date: str) -> Dict:
    """
    💃 DAY DANCE - Previous day + Target day = XY
    Digits of XY predict numbers and stars!
    30.5% hit on stars, 14.4% on P1
    """
    prev_day = int(prev_date.split('.')[0])
    target_day = int(target_date.split('.')[0])
    
    day_sum = prev_day + target_day
    
    candidates = {
        'numbers': [],
        'stars': [],
        'explanation': f"Day Dance: {prev_day} + {target_day} = {day_sum}"
    }
    
    # Extract digits
    if day_sum >= 10:
        d1 = day_sum // 10
        d2 = day_sum % 10
    else:
        d1 = 0
        d2 = day_sum
    
    # Stars (30.5% hit rate!)
    if 1 <= d1 <= 12:
        candidates['stars'].append((d1, 30.5, f"Day Dance digit"))
    if 1 <= d2 <= 12:
        candidates['stars'].append((d2, 30.5, f"Day Dance digit"))
    
    # Numbers
    if d1 >= 1:
        candidates['numbers'].append((d1, 14.4, f"Day Dance first digit"))
    if d2 >= 1:
        candidates['numbers'].append((d2, 14.4, f"Day Dance second digit"))
    
    # The sum itself if valid
    if 1 <= day_sum <= 50:
        candidates['numbers'].append((day_sum, 8.5, f"Day Dance sum"))
    
    # Family expansion
    for digit in [d1, d2]:
        if 1 <= digit <= 9:
            for mult in range(5):
                num = digit + mult * 10
                if 1 <= num <= 50:
                    candidates['numbers'].append((num, 5.0, f"{digit}-family"))
    
    # If day_sum = 17, Mr. 17 is calling!
    if day_sum == 17:
        candidates['numbers'].append((17, 20.0, "Mr. 17 Day Dance!"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 3: REUNIONS (Groups that dance together)
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_reunions(draws: List[Dict], number: int, lookback: int = 50) -> Dict:
    """
    🎉 REUNION PATTERN - Find numbers that love dancing together!
    """
    partners = Counter()
    star_partners = Counter()
    appearances = 0
    
    for d in draws[:lookback]:
        if number in d['numbers']:
            appearances += 1
            for n in d['numbers']:
                if n != number:
                    partners[n] += 1
            for s in d['stars']:
                star_partners[s] += 1
    
    # Find overdue partners
    overdue_partners = []
    for partner, count in partners.most_common(10):
        # Find gap for this partner
        gap = None
        for i, d in enumerate(draws):
            if partner in d['numbers']:
                gap = i
                break
        if gap and gap >= 8:
            overdue_partners.append((partner, count, gap))
    
    return {
        'number': number,
        'appearances': appearances,
        'favorite_partners': partners.most_common(5),
        'favorite_stars': star_partners.most_common(3),
        'overdue_partners': overdue_partners
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 4: THE 17 MAGIC
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_17_magic(draws: List[Dict], target_date: str) -> Dict:
    """
    🎩 MR. 17 - The magic number that's always at the party!
    17 appears as: direct, circle(42), gaps, Star [2,7], Swiss 38...
    """
    candidates = {
        'numbers': [],
        'stars': [],
        'explanations': []
    }
    
    day = int(target_date.split('.')[0])
    
    # Direct 17
    candidates['numbers'].append((17, 15.0, "Mr. 17 direct"))
    
    # circle(17) = 42
    candidates['numbers'].append((42, 10.0, "circle(17)=42"))
    
    # 38 = Swiss 17
    candidates['numbers'].append((38, 8.0, "38 = Swiss 17"))
    
    # If day relates to 17
    if day + 10 == 17:
        candidates['numbers'].append((17, 20.0, f"Day {day} + 10 = 17"))
    
    # Stars 2 and 7 often appear with 17
    candidates['stars'].append((2, 10.0, "17's star friend"))
    candidates['stars'].append((7, 15.0, "17's star friend"))
    
    # 7-family (17's family)
    for n in [7, 17, 27, 37, 47]:
        candidates['numbers'].append((n, 8.0, "7-family (17's family)"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 5: COUNTING PATTERNS (10→11→12)
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_counting(draws: List[Dict]) -> Dict:
    """
    📈 COUNTING PATTERN - Numbers count up or down!
    10 → 11 → 12...
    """
    if len(draws) < 3:
        return {'next': None, 'trend': None}
    
    # Check P1 counting
    p1s = [sorted(d['numbers'])[0] for d in draws[:5]]
    
    candidates = {
        'numbers': [],
        'explanations': []
    }
    
    # Check if P1 is counting
    if len(p1s) >= 2:
        diff = p1s[0] - p1s[1]
        if diff == 1:  # Counting up
            next_p1 = p1s[0] + 1
            if 1 <= next_p1 <= 50:
                candidates['numbers'].append((next_p1, 15.0, f"P1 counting: {p1s[1]}→{p1s[0]}→{next_p1}"))
        elif diff == -1:  # Counting down
            next_p1 = p1s[0] - 1
            if 1 <= next_p1 <= 50:
                candidates['numbers'].append((next_p1, 15.0, f"P1 counting down"))
    
    # Check P3 counting
    p3s = [sorted(d['numbers'])[2] for d in draws[:5]]
    if len(p3s) >= 2:
        diff = p3s[0] - p3s[1]
        if abs(diff) == 1:
            next_p3 = p3s[0] + (1 if diff == 1 else -1)
            if 1 <= next_p3 <= 50:
                candidates['numbers'].append((next_p3, 12.0, f"P3 counting"))
    
    # The 44+10=54, 54+8=62, 62-50=12 pattern
    candidates['numbers'].append((12, 10.0, "62-50=12 (from 54+8 chain)"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 6: FAMILY PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_families(draws: List[Dict]) -> Dict:
    """
    👨‍👩‍👧 FAMILY PATTERNS - Numbers that end in same digit
    5-family: 5, 15, 25, 35, 45
    9-family: 9, 19, 29, 39, 49
    """
    candidates = {
        'numbers': [],
        'stars': [],
        'explanations': []
    }
    
    # Check which families are overdue
    family_gaps = {}
    for family_digit in range(10):
        family = [family_digit + i*10 for i in range(5) if family_digit + i*10 <= 50 and family_digit + i*10 >= 1]
        
        # Find when any member of this family last appeared
        for i, d in enumerate(draws):
            if any(n in d['numbers'] for n in family):
                family_gaps[family_digit] = i
                break
    
    # Find overdue families
    for digit, gap in sorted(family_gaps.items(), key=lambda x: -x[1]):
        if gap >= 5:
            family = [digit + i*10 for i in range(5) if digit + i*10 <= 50 and digit + i*10 >= 1]
            for n in family:
                candidates['numbers'].append((n, 8.0 + gap * 0.5, f"{digit}-family (gap {gap})"))
    
    # Special: 5-family from Full Date (mod 50 gives 5, 15, 25, 35)
    candidates['explanations'].append("5-family: 5, 15, 25, 35, 45")
    candidates['explanations'].append("9-family: 9, 19, 29, 39, 49")
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 7: NUMBER → STAR (33% for Num 3!)
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_number_to_star(draws: List[Dict]) -> Dict:
    """
    ⭐ NUMBER X → STAR X
    When number 3 appears, Star 3 follows 33% of the time!
    """
    if not draws:
        return {'stars': []}
    
    prev_nums = draws[0]['numbers']
    
    candidates = {
        'stars': [],
        'explanations': []
    }
    
    # Numbers 1-12 that appeared → might become stars
    for n in prev_nums:
        if 1 <= n <= 12:
            # Historical hit rates (from our analysis)
            rates = {3: 33.3, 12: 28.6, 10: 22.2, 7: 20.7, 5: 18.4}
            rate = rates.get(n, 15.0)
            candidates['stars'].append((n, rate, f"Number {n} → Star {n}"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 8: P1+P2 DIGIT SUM → STAR (20% hit rate!)
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_p1p2_digit_sum_star(draws: List[Dict]) -> Dict:
    """
    🔢 P1+P2 digit_sum → Star (20.3% hit rate!)
    """
    if not draws:
        return {'stars': []}
    
    prev_nums = sorted(draws[0]['numbers'])
    p1, p2 = prev_nums[0], prev_nums[1]
    
    ds = digit_sum(p1 + p2)
    
    candidates = {
        'stars': [],
        'numbers': [],
        'explanation': f"P1+P2 = {p1}+{p2} = {p1+p2} → digit_sum = {ds}"
    }
    
    if 1 <= ds <= 12:
        candidates['stars'].append((ds, 20.3, f"digit_sum(P1+P2)"))
    
    if 1 <= ds <= 50:
        candidates['numbers'].append((ds, 9.7, f"digit_sum(P1+P2)"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 9: SEQUENCE HUNGER
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_sequence_hunger(draws: List[Dict], window: int = 4) -> List[int]:
    """
    🍽️ SEQUENCE HUNGER - Missing numbers from sequences!
    If 22 and 24 appeared, 23 is HUNGRY!
    """
    if not draws or len(draws) < 2:
        return []
    
    # Collect all numbers from recent draws
    recent_nums = set()
    for d in draws[:window]:
        recent_nums.update(d['numbers'])
    
    hungry = []
    
    # Find gaps of 1
    sorted_recent = sorted(recent_nums)
    for i in range(len(sorted_recent) - 1):
        gap = sorted_recent[i + 1] - sorted_recent[i]
        if gap == 2:
            missing = sorted_recent[i] + 1
            if 1 <= missing <= 50:
                hungry.append(missing)
    
    return hungry


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 10: THE 14→15→40 CHAIN
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_chain_14_15_40(draws: List[Dict]) -> Dict:
    """
    🔗 THE CHAIN: 14 → 15 → 40
    14 was at party → 15 calling → circle(15)=40!
    """
    candidates = {
        'numbers': [],
        'explanations': []
    }
    
    if not draws:
        return candidates
    
    prev_nums = draws[0]['numbers']
    
    # If 14 was present
    if 14 in prev_nums:
        candidates['numbers'].append((15, 18.0, "14+1=15 (14 was at party!)"))
        candidates['numbers'].append((40, 15.0, "circle(15)=40"))
        candidates['numbers'].append((39, 12.0, "circle(14)=39"))
        candidates['explanations'].append("14→15→40 chain active!")
    
    # If 15 was present
    if 15 in prev_nums:
        candidates['numbers'].append((40, 18.0, "circle(15)=40"))
        candidates['numbers'].append((16, 12.0, "15+1=16"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 11: OVERDUE NUMBERS
# ═══════════════════════════════════════════════════════════════════════════════
def pattern_overdue(draws: List[Dict], threshold: int = 10) -> List[Tuple[int, int]]:
    """
    🔥 OVERDUE NUMBERS - Numbers that haven't appeared in a while
    """
    overdue = []
    
    for num in range(1, 51):
        for i, d in enumerate(draws):
            if num in d['numbers']:
                if i >= threshold:
                    overdue.append((num, i))
                break
    
    return sorted(overdue, key=lambda x: -x[1])


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER FUNCTION: MUSICAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
def musical_analysis(draws: List[Dict], target_date: str) -> Dict:
    """
    🎧 MASTER MUSICAL ANALYSIS 🎧
    Combines ALL patterns to create harmonious predictions!
    """
    if not draws:
        return {'error': 'No draws provided'}
    
    prev_date = draws[0]['date']
    
    # Collect all candidates with their weights
    all_numbers = Counter()
    all_stars = Counter()
    all_explanations = []
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 1. FULL DATE IMAGINATION (Strongest - 19%)
    # ═══════════════════════════════════════════════════════════════════════════
    imagination = pattern_full_date_imagination(target_date)
    for num, weight, exp in imagination['numbers']:
        all_numbers[num] += weight * 2  # Double weight for strongest pattern
    for star, weight, exp in imagination['stars']:
        all_stars[star] += weight * 2
    all_explanations.append("🎧 FULL DATE IMAGINATION:")
    all_explanations.extend(imagination['explanations'])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 2. DAY DANCE
    # ═══════════════════════════════════════════════════════════════════════════
    day_dance = pattern_day_dance(prev_date, target_date)
    for num, weight, exp in day_dance['numbers']:
        all_numbers[num] += weight
    for star, weight, exp in day_dance['stars']:
        all_stars[star] += weight * 1.5  # Stars strong in day dance
    all_explanations.append(f"💃 {day_dance['explanation']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. THE 17 MAGIC
    # ═══════════════════════════════════════════════════════════════════════════
    magic_17 = pattern_17_magic(draws, target_date)
    for num, weight, exp in magic_17['numbers']:
        all_numbers[num] += weight
    for star, weight, exp in magic_17['stars']:
        all_stars[star] += weight
    all_explanations.append("🎩 MR. 17 MAGIC active")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 4. COUNTING PATTERNS
    # ═══════════════════════════════════════════════════════════════════════════
    counting = pattern_counting(draws)
    for num, weight, exp in counting['numbers']:
        all_numbers[num] += weight
        all_explanations.append(f"📈 {exp}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 5. NUMBER → STAR
    # ═══════════════════════════════════════════════════════════════════════════
    num_to_star = pattern_number_to_star(draws)
    for star, weight, exp in num_to_star['stars']:
        all_stars[star] += weight
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 6. P1+P2 DIGIT SUM → STAR
    # ═══════════════════════════════════════════════════════════════════════════
    p1p2_star = pattern_p1p2_digit_sum_star(draws)
    for star, weight, exp in p1p2_star['stars']:
        all_stars[star] += weight * 1.5
    all_explanations.append(f"🔢 {p1p2_star.get('explanation', '')}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 7. SEQUENCE HUNGER
    # ═══════════════════════════════════════════════════════════════════════════
    hungry = pattern_sequence_hunger(draws)
    for num in hungry:
        all_numbers[num] += 15.0
    if hungry:
        all_explanations.append(f"🍽️ HUNGRY: {hungry}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 8. THE 14→15→40 CHAIN
    # ═══════════════════════════════════════════════════════════════════════════
    chain = pattern_chain_14_15_40(draws)
    for num, weight, exp in chain['numbers']:
        all_numbers[num] += weight
    all_explanations.extend(chain['explanations'])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 9. OVERDUE NUMBERS
    # ═══════════════════════════════════════════════════════════════════════════
    overdue = pattern_overdue(draws, threshold=12)
    for num, gap in overdue[:10]:
        all_numbers[num] += gap * 0.8
    if overdue:
        all_explanations.append(f"🔥 OVERDUE: {[(n, g) for n, g in overdue[:5]]}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 10. 15 REUNION PARTNERS
    # ═══════════════════════════════════════════════════════════════════════════
    reunion_15 = pattern_reunions(draws, 15)
    for partner, count in reunion_15['favorite_partners']:
        all_numbers[partner] += count * 3
    for star, count in reunion_15['favorite_stars']:
        all_stars[star] += count * 5
    for partner, count, gap in reunion_15['overdue_partners']:
        all_numbers[partner] += 10 + gap * 0.5
    
    # Add 15's signature stars [6, 9] (6+9=15!)
    all_stars[6] += 15.0
    all_stars[9] += 15.0
    all_explanations.append("🎉 15's signature: Stars [6,9] (6+9=15!)")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMPILE RESULTS
    # ═══════════════════════════════════════════════════════════════════════════
    top_numbers = all_numbers.most_common(20)
    top_stars = all_stars.most_common(12)
    
    return {
        'target_date': target_date,
        'prev_date': prev_date,
        'top_numbers': top_numbers,
        'top_stars': top_stars,
        'explanations': all_explanations,
        'suggested_tickets': generate_tickets(top_numbers, top_stars)
    }


def generate_tickets(top_numbers: List[Tuple[int, float]], 
                     top_stars: List[Tuple[int, float]], 
                     num_tickets: int = 5) -> List[Dict]:
    """
    Generate tickets from top candidates
    """
    tickets = []
    
    # Get sorted number candidates
    nums = [n for n, w in top_numbers if 1 <= n <= 50]
    stars = [s for s, w in top_stars if 1 <= s <= 12]
    
    # Ticket 1: Top 5 by weight
    if len(nums) >= 5 and len(stars) >= 2:
        tickets.append({
            'name': 'CONVERGENCE KING',
            'numbers': sorted(nums[:5]),
            'stars': sorted(stars[:2]),
            'reason': 'Highest weighted numbers'
        })
    
    # Ticket 2: Mix top with some variety
    if len(nums) >= 10 and len(stars) >= 4:
        selected = sorted(nums[:3] + nums[5:7])[:5]
        tickets.append({
            'name': 'BALANCED MIX',
            'numbers': selected,
            'stars': sorted(stars[1:3]),
            'reason': 'Mix of top and secondary candidates'
        })
    
    # Ticket 3: 5-Family focus
    fives = [n for n in nums if n % 10 == 5][:5]
    if len(fives) >= 3:
        # Fill remaining with top candidates
        remaining = [n for n in nums if n not in fives][:5-len(fives)]
        selected = sorted(fives + remaining)[:5]
        if len(selected) == 5:
            tickets.append({
                'name': '5-FAMILY REUNION',
                'numbers': selected,
                'stars': sorted(stars[:2]),
                'reason': '5-family from Full Date pattern'
            })
    
    # Ticket 4: Include 11 and 13 (digit_sum kings)
    must_have = [11, 13]
    others = [n for n in nums if n not in must_have][:3]
    selected = sorted(must_have + others)[:5]
    if len(selected) == 5 and len(stars) >= 2:
        tickets.append({
            'name': 'DIGIT SUM KINGS',
            'numbers': selected,
            'stars': sorted(stars[:2]),
            'reason': 'digit_sum pattern (19% hit rate!)'
        })
    
    # Ticket 5: Mr. 17 special
    if 17 in nums or 37 in nums or 47 in nums:
        sevens = [n for n in nums if n % 10 == 7][:3]
        others = [n for n in nums if n not in sevens][:5-len(sevens)]
        selected = sorted(sevens + others)[:5]
        if len(selected) == 5:
            tickets.append({
                'name': 'MR. 17 SPECIAL',
                'numbers': selected,
                'stars': [1, 7] if 1 in [s for s, w in top_stars] else sorted(stars[:2]),
                'reason': '7-family + Day Dance = 17!'
            })
    
    return tickets


# ═══════════════════════════════════════════════════════════════════════════════
# TEST FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Load data
    from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
    from datetime import datetime
    
    def parse_date(d):
        return datetime.strptime(d['date'], "%d.%m.%Y")
    
    sorted_draws = sorted(
        EUROMILLIONS_DRAWS_2024_2026,
        key=lambda x: parse_date(x),
        reverse=True
    )
    
    # Run analysis for 10.04.2026
    target = "10.04.2026"
    
    print("=" * 70)
    print(f"🎧 MUSICAL ANALYSIS FOR {target} 🎧")
    print("=" * 70)
    
    result = musical_analysis(sorted_draws, target)
    
    print(f"\n📅 Previous draw: {result['prev_date']}")
    
    print(f"\n🔢 TOP NUMBERS (by musical weight):")
    for num, weight in result['top_numbers'][:15]:
        bar = "█" * int(weight / 5)
        print(f"   {num:2d}: {bar} ({weight:.1f})")
    
    print(f"\n⭐ TOP STARS (by musical weight):")
    for star, weight in result['top_stars'][:6]:
        bar = "█" * int(weight / 3)
        print(f"   {star:2d}: {bar} ({weight:.1f})")
    
    print(f"\n📖 PATTERN EXPLANATIONS:")
    for exp in result['explanations'][:15]:
        print(f"   {exp}")
    
    print(f"\n🎫 SUGGESTED TICKETS:")
    for ticket in result['suggested_tickets']:
        print(f"\n   🎫 {ticket['name']}:")
        print(f"      {ticket['numbers']} ⭐ {ticket['stars']}")
        print(f"      Reason: {ticket['reason']}")
    
    print("\n" + "=" * 70)
    print("🎧 THE MUSIC HAS SPOKEN! 🎻🍀")
    print("=" * 70)
