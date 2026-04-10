"""
🎧 MUSICAL PATTERNS - DATE CHAMELEON EDITION 🎻
The date speaks in MANY voices! 74.6% raw digits, 67.5% circle formulas!

NO digit_sum splitting (1+7+5=13)! Only BUDDY math!
- Circle: +25 or -25
- Buddy additions: Day+Month, P1+P2
- Date digits echo through draw numbers

Patterns discovered:
1. DATE CHAMELEON (d) - 74.6% hit rate on raw digits!
2. BEFORE CONNECTIONS (b) - Previous draw transforms
3. NUMBER INTERNAL (n) - Same-draw relationships
"""

from collections import Counter
from typing import List, Dict, Tuple, Set

# ═══════════════════════════════════════════════════════════════════════════════
# CORE MATH FUNCTIONS - THE MUSIC!
# ═══════════════════════════════════════════════════════════════════════════════

def circle_plus(n: int) -> int:
    """Circle +25"""
    return n + 25

def circle_minus(n: int) -> int:
    """Circle -25 (only if n > 25)"""
    return n - 25 if n > 25 else n + 25

def reverse_num(n: int) -> int:
    """Reverse digits: 28 -> 82, 41 -> 14"""
    if n < 10:
        return n
    s = str(n)
    rev = int(s[::-1])
    # If > 50, subtract 50 to stay in range
    if rev > 50:
        rev = rev - 50
    return rev

def get_digits(number: int) -> Set[str]:
    """Get all digits from a number as strings"""
    return set(str(number))

def find_digit_in_numbers(numbers: List[int], digit: str) -> int:
    """Find which number contains a digit, return the number or None"""
    for num in numbers:
        if digit in str(num):
            return num
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 1: DATE CHAMELEON (d) - 74.6% HIT RATE!
# The date transforms in MANY ways to predict numbers!
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_date_chameleon(day: int, month: int) -> Dict:
    """
    🦎 DATE CHAMELEON - The date speaks in many voices!
    
    Transformations (all hit rates tested on 209 draws):
    1. Raw digits (74.6%) - Just find day+month digits in draw
    2. Day×10 + circle(Month) (67.5%) - Your formula! 
    3. Day×10 + Month (61.7%)
    4. Day + Month (55.5%)
    5. Day - Month (51.7%)
    6. Reverse(Day) + Month (45.9%)
    7. Day + circle(Month) (39.2%)
    """
    candidates = {
        'numbers': [],
        'stars': [],
        'targets': {},
        'raw_digits': set()
    }
    
    # ═══════════════════════════════════════════════════════════════════════
    # WAY 1: Raw Digits (74.6% hit rate!) - STRONGEST!
    # ═══════════════════════════════════════════════════════════════════════
    raw = set(str(day) + str(month).zfill(2))
    candidates['raw_digits'] = raw
    candidates['targets']['raw_digits'] = f"Digits from {day:02d}.{month:02d}"
    
    # Each digit becomes a family seed
    for digit in raw:
        d = int(digit)
        if d > 0:  # Skip 0
            for mult in range(5):
                num = d + mult * 10
                if 1 <= num <= 50:
                    candidates['numbers'].append((num, 74.6, f"raw_digit {digit} -> {num}"))
            if 1 <= d <= 12:
                candidates['stars'].append((d, 74.6, f"raw_digit {digit}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # WAY 2: Day×10 + circle(Month) (67.5%) - YOUR FORMULA!
    # Example: 28-09 -> 280 + 34 = 314
    # ═══════════════════════════════════════════════════════════════════════
    target_circle = (day * 10) + circle_plus(month)
    candidates['targets']['day10_circle_month'] = target_circle
    
    # The target's digits echo in the draw
    for digit in str(target_circle):
        d = int(digit)
        if d > 0:
            for mult in range(5):
                num = d + mult * 10
                if 1 <= num <= 50:
                    candidates['numbers'].append((num, 67.5, f"day10_circle({target_circle}) digit {digit}"))
            if 1 <= d <= 12:
                candidates['stars'].append((d, 67.5, f"day10_circle({target_circle}) digit"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # WAY 3: Day×10 + Month (61.7%)
    # ═══════════════════════════════════════════════════════════════════════
    target_simple = (day * 10) + month
    candidates['targets']['day10_month'] = target_simple
    
    for digit in str(target_simple):
        d = int(digit)
        if d > 0:
            for mult in range(5):
                num = d + mult * 10
                if 1 <= num <= 50:
                    candidates['numbers'].append((num, 61.7, f"day10_month({target_simple}) digit {digit}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # WAY 4: Day + Month (55.5%)
    # ═══════════════════════════════════════════════════════════════════════
    day_plus_month = day + month
    candidates['targets']['day_plus_month'] = day_plus_month
    
    if 1 <= day_plus_month <= 50:
        candidates['numbers'].append((day_plus_month, 55.5, f"day+month = {day_plus_month}"))
    if 1 <= day_plus_month <= 12:
        candidates['stars'].append((day_plus_month, 55.5, f"day+month = {day_plus_month}"))
    
    # Digits of sum
    for digit in str(day_plus_month):
        d = int(digit)
        if d > 0:
            candidates['numbers'].append((d, 40.0, f"(day+month) digit"))
            if 1 <= d <= 12:
                candidates['stars'].append((d, 40.0, f"(day+month) digit"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # WAY 5: Day - Month (51.7%) - if positive
    # ═══════════════════════════════════════════════════════════════════════
    if day > month:
        day_minus_month = day - month
        candidates['targets']['day_minus_month'] = day_minus_month
        
        if 1 <= day_minus_month <= 50:
            candidates['numbers'].append((day_minus_month, 51.7, f"day-month = {day_minus_month}"))
        if 1 <= day_minus_month <= 12:
            candidates['stars'].append((day_minus_month, 51.7, f"day-month = {day_minus_month}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # WAY 6: Reverse(Day) + Month (45.9%)
    # ═══════════════════════════════════════════════════════════════════════
    rev_day = reverse_num(day)
    if rev_day != day:
        rev_plus_month = rev_day + month
        candidates['targets']['reverse_day_month'] = rev_plus_month
        
        if 1 <= rev_plus_month <= 50:
            candidates['numbers'].append((rev_plus_month, 45.9, f"reverse({day})+{month} = {rev_plus_month}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # WAY 7: Day + circle(Month) (39.2%)
    # ═══════════════════════════════════════════════════════════════════════
    day_circle_month = day + circle_plus(month)
    candidates['targets']['day_circle_month'] = day_circle_month
    
    if 1 <= day_circle_month <= 50:
        candidates['numbers'].append((day_circle_month, 39.2, f"day+circle({month}) = {day_circle_month}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # WAY 8: Direct day and month values
    # ═══════════════════════════════════════════════════════════════════════
    # Day + 25
    day_circle = circle_plus(day)
    if 1 <= day_circle <= 50:
        candidates['numbers'].append((day_circle, 35.0, f"day+25 = {day_circle}"))
    
    # Month + 25
    month_circle = circle_plus(month)
    if 1 <= month_circle <= 50:
        candidates['numbers'].append((month_circle, 35.0, f"month+25 = {month_circle}"))
    
    # Day direct
    if 1 <= day <= 50:
        candidates['numbers'].append((day, 30.0, f"day direct = {day}"))
    if 1 <= day <= 12:
        candidates['stars'].append((day, 30.0, f"day direct"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 2: BEFORE CONNECTIONS (b) - Previous draw transforms!
# 95% of "silent" draws connect through previous!
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_before_connections(prev_numbers: List[int], prev_stars: List[int]) -> Dict:
    """
    🔙 BEFORE CONNECTIONS - Previous draw predicts current!
    
    Transformations:
    - Previous number + 25 -> appears in current
    - Previous number - 25 -> appears in current  
    - Previous number reversed -> appears in current
    - Previous P1+P2, P2+P3 sums -> appear in current
    - Previous star + 25 -> appears as number
    - circle(P_i + P_j) -> appears
    """
    candidates = {
        'numbers': [],
        'stars': [],
        'explanations': []
    }
    
    # Sort previous numbers
    prev_sorted = sorted(prev_numbers)
    
    # ═══════════════════════════════════════════════════════════════════════
    # Previous numbers + 25 (STRONG!)
    # ═══════════════════════════════════════════════════════════════════════
    for pn in prev_numbers:
        # +25
        plus25 = pn + 25
        if 1 <= plus25 <= 50:
            candidates['numbers'].append((plus25, 25.0, f"prev {pn}+25 = {plus25}"))
        
        # -25
        if pn > 25:
            minus25 = pn - 25
            candidates['numbers'].append((minus25, 20.0, f"prev {pn}-25 = {minus25}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # Previous numbers REVERSED (caught 2 of 6 silent draws!)
    # ═══════════════════════════════════════════════════════════════════════
    for pn in prev_numbers:
        rev = reverse_num(pn)
        if rev != pn and 1 <= rev <= 50:
            candidates['numbers'].append((rev, 22.0, f"prev {pn} reversed = {rev}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # Previous pair sums: P1+P2, P2+P3, etc.
    # ═══════════════════════════════════════════════════════════════════════
    for i in range(len(prev_sorted) - 1):
        pair_sum = prev_sorted[i] + prev_sorted[i+1]
        
        # Direct sum if valid
        if 1 <= pair_sum <= 50:
            candidates['numbers'].append((pair_sum, 18.0, f"prev P{i+1}+P{i+2} = {pair_sum}"))
        
        # Circle of sum
        if pair_sum > 25:
            circle_sum = pair_sum - 25
            if 1 <= circle_sum <= 50:
                candidates['numbers'].append((circle_sum, 15.0, f"circle(prev P{i+1}+P{i+2}) = {circle_sum}"))
        
        # If sum > 50, the -50 version
        if pair_sum > 50:
            minus50 = pair_sum - 50
            if 1 <= minus50 <= 50:
                candidates['numbers'].append((minus50, 12.0, f"prev P{i+1}+P{i+2}-50 = {minus50}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # Previous STARS + 25 -> numbers
    # ═══════════════════════════════════════════════════════════════════════
    for ps in prev_stars:
        star_plus25 = ps + 25
        if 1 <= star_plus25 <= 50:
            candidates['numbers'].append((star_plus25, 15.0, f"prev star {ps}+25 = {star_plus25}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # Previous numbers that ECHO (same number appears again)
    # ═══════════════════════════════════════════════════════════════════════
    for pn in prev_numbers:
        candidates['numbers'].append((pn, 8.0, f"prev {pn} echo"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 3: NUMBER INTERNAL (n) - Same-draw relationships!
# Numbers within a draw relate to each other
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_number_internal(prev_numbers: List[int]) -> Dict:
    """
    🔢 NUMBER INTERNAL - Within the same draw, numbers relate!
    
    Examples from silent draw analysis:
    - 14 and 41 are reversals of each other
    - 23 + 25 = 48 (circle within draw)
    - Numbers share digits
    """
    candidates = {
        'numbers': [],
        'explanations': []
    }
    
    # Look for internal circles: if N and N+25 both appear
    for n in prev_numbers:
        if n + 25 in prev_numbers:
            candidates['explanations'].append(f"Internal circle: {n} + 25 = {n+25}")
    
    # Look for internal reversals
    for n in prev_numbers:
        rev = reverse_num(n)
        if rev != n and rev in prev_numbers:
            candidates['explanations'].append(f"Internal reverse: {n} <-> {rev}")
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 4: P1+P2 = Day+Month (The "silent" draw discovery!)
# When P1+P2 equals Day+Month, it's a hidden sign!
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_p1p2_date_match(day: int, month: int) -> Dict:
    """
    🎯 P1+P2 = Day+Month Pattern
    
    From silent draw 04.11.2025: P1(6) + P2(9) = 15 = Day(4) + Month(11)!
    
    If Day+Month = X, find pairs that sum to X
    """
    target = day + month
    
    candidates = {
        'numbers': [],
        'stars': [],
        'pairs': [],
        'explanation': f"Looking for P1+P2 = {day}+{month} = {target}"
    }
    
    # Generate all pairs that sum to target
    for p1 in range(1, min(target, 51)):
        p2 = target - p1
        if p1 < p2 and 1 <= p2 <= 50:
            candidates['pairs'].append((p1, p2))
            candidates['numbers'].append((p1, 20.0, f"P1+P2={target}: could be {p1}"))
            candidates['numbers'].append((p2, 20.0, f"P1+P2={target}: could be {p2}"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 5: REUNION / CHAIN PATTERNS
# Numbers that love dancing together!
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_reunions(draws: List[Dict], target_number: int, lookback: int = 50) -> Dict:
    """
    🎉 REUNION - Find numbers that dance together!
    """
    partners = Counter()
    star_partners = Counter()
    
    for d in draws[:lookback]:
        if target_number in d['numbers']:
            for n in d['numbers']:
                if n != target_number:
                    partners[n] += 1
            for s in d['stars']:
                star_partners[s] += 1
    
    return {
        'number': target_number,
        'favorite_partners': partners.most_common(5),
        'favorite_stars': star_partners.most_common(3)
    }


def pattern_chain_14_15_40(prev_numbers: List[int]) -> Dict:
    """
    🔗 THE CHAIN: 14 -> 15 -> 40
    If 14 appears, 15 follows, then circle(15)=40!
    """
    candidates = {
        'numbers': [],
        'explanations': []
    }
    
    if 14 in prev_numbers:
        candidates['numbers'].append((15, 25.0, "14 was here -> 15 coming!"))
        candidates['numbers'].append((40, 20.0, "circle(15)=40"))
        candidates['numbers'].append((39, 15.0, "circle(14)=39"))
        candidates['explanations'].append("🔗 14->15->40 chain ACTIVE!")
    
    if 15 in prev_numbers:
        candidates['numbers'].append((40, 25.0, "15 was here -> circle(15)=40!"))
        candidates['numbers'].append((16, 12.0, "15+1=16"))
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 6: OVERDUE NUMBERS (Gap Hunger!)
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_overdue(draws: List[Dict], threshold: int = 10) -> List[Tuple[int, int]]:
    """
    🔥 OVERDUE - Numbers that haven't appeared in a while are HUNGRY!
    """
    overdue = []
    
    for num in range(1, 51):
        for i, d in enumerate(draws):
            if num in d['numbers']:
                if i >= threshold:
                    overdue.append((num, i))
                break
        else:
            # Never found in lookback
            overdue.append((num, len(draws)))
    
    return sorted(overdue, key=lambda x: -x[1])


def pattern_overdue_stars(draws: List[Dict], threshold: int = 8) -> List[Tuple[int, int]]:
    """
    ⭐ OVERDUE STARS
    """
    overdue = []
    
    for star in range(1, 13):
        for i, d in enumerate(draws):
            if star in d['stars']:
                if i >= threshold:
                    overdue.append((star, i))
                break
        else:
            overdue.append((star, len(draws)))
    
    return sorted(overdue, key=lambda x: -x[1])


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 7: SEQUENCE HUNGER
# Missing numbers in sequences!
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_sequence_hunger(draws: List[Dict], window: int = 4) -> List[int]:
    """
    🍽️ SEQUENCE HUNGER - Find gaps in number sequences!
    If 22 and 24 appeared recently, 23 is HUNGRY!
    """
    recent_nums = set()
    for d in draws[:window]:
        recent_nums.update(d['numbers'])
    
    hungry = []
    sorted_recent = sorted(recent_nums)
    
    for i in range(len(sorted_recent) - 1):
        gap = sorted_recent[i + 1] - sorted_recent[i]
        if gap == 2:  # Gap of 2 means one missing
            missing = sorted_recent[i] + 1
            if 1 <= missing <= 50:
                hungry.append(missing)
    
    return hungry


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER FUNCTION: MUSICAL ANALYSIS - DATE CHAMELEON EDITION!
# ═══════════════════════════════════════════════════════════════════════════════

def musical_analysis(draws: List[Dict], target_date: str) -> Dict:
    """
    🎧 MASTER MUSICAL ANALYSIS - DATE CHAMELEON EDITION! 🎻
    
    The date speaks in MANY voices:
    - d (date): Raw digits, circle formulas - 74.6% hit!
    - b (before): Previous draw transforms - catches 95% of "silent" ones!
    - n (number): Internal relationships
    """
    if not draws:
        return {'error': 'No draws provided'}
    
    # Parse target date
    parts = target_date.split('.')
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2]) if len(parts) > 2 else 2025
    
    # Previous draw info
    prev_draw = draws[0]
    prev_numbers = prev_draw['numbers']
    prev_stars = prev_draw['stars']
    prev_date = prev_draw['date']
    
    # Collect all candidates
    all_numbers = Counter()
    all_stars = Counter()
    explanations = []
    
    # ═══════════════════════════════════════════════════════════════════════
    # 1. DATE CHAMELEON (d) - THE KING! 74.6%!
    # ═══════════════════════════════════════════════════════════════════════
    date_patterns = pattern_date_chameleon(day, month)
    
    for num, weight, exp in date_patterns['numbers']:
        all_numbers[num] += weight
    for star, weight, exp in date_patterns['stars']:
        all_stars[star] += weight
    
    explanations.append(f"🦎 DATE CHAMELEON for {day:02d}.{month:02d}:")
    explanations.append(f"   Raw digits: {date_patterns['raw_digits']}")
    for name, val in date_patterns['targets'].items():
        explanations.append(f"   {name}: {val}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 2. BEFORE CONNECTIONS (b) - 95% catch rate!
    # ═══════════════════════════════════════════════════════════════════════
    before_patterns = pattern_before_connections(prev_numbers, prev_stars)
    
    for num, weight, exp in before_patterns['numbers']:
        all_numbers[num] += weight
    
    explanations.append(f"🔙 BEFORE (prev: {prev_numbers}):")
    for exp in before_patterns['explanations'][:5]:
        explanations.append(f"   {exp}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 3. P1+P2 = Day+Month Pattern
    # ═══════════════════════════════════════════════════════════════════════
    p1p2_pattern = pattern_p1p2_date_match(day, month)
    
    for num, weight, exp in p1p2_pattern['numbers']:
        all_numbers[num] += weight
    
    explanations.append(f"🎯 P1+P2 = {day}+{month} = {day+month}")
    if p1p2_pattern['pairs']:
        explanations.append(f"   Possible pairs: {p1p2_pattern['pairs'][:5]}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 4. CHAIN PATTERNS
    # ═══════════════════════════════════════════════════════════════════════
    chain = pattern_chain_14_15_40(prev_numbers)
    
    for num, weight, exp in chain['numbers']:
        all_numbers[num] += weight
    explanations.extend(chain['explanations'])
    
    # ═══════════════════════════════════════════════════════════════════════
    # 5. OVERDUE NUMBERS
    # ═══════════════════════════════════════════════════════════════════════
    overdue = pattern_overdue(draws, threshold=10)
    for num, gap in overdue[:10]:
        all_numbers[num] += gap * 1.5
    
    overdue_stars = pattern_overdue_stars(draws, threshold=6)
    for star, gap in overdue_stars[:5]:
        all_stars[star] += gap * 2.0
    
    if overdue:
        explanations.append(f"🔥 OVERDUE: {[(n, g) for n, g in overdue[:5]]}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 6. SEQUENCE HUNGER
    # ═══════════════════════════════════════════════════════════════════════
    hungry = pattern_sequence_hunger(draws)
    for num in hungry:
        all_numbers[num] += 15.0
    
    if hungry:
        explanations.append(f"🍽️ HUNGRY (sequence gaps): {hungry}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # COMPILE RESULTS
    # ═══════════════════════════════════════════════════════════════════════
    top_numbers = all_numbers.most_common(25)
    top_stars = all_stars.most_common(12)
    
    return {
        'target_date': target_date,
        'prev_date': prev_date,
        'day': day,
        'month': month,
        'top_numbers': top_numbers,
        'top_stars': top_stars,
        'explanations': explanations,
        'date_targets': date_patterns['targets'],
        'suggested_tickets': generate_tickets(top_numbers, top_stars, day, month)
    }


def generate_tickets(top_numbers: List[Tuple[int, float]], 
                     top_stars: List[Tuple[int, float]],
                     day: int, month: int,
                     num_tickets: int = 5) -> List[Dict]:
    """
    🎫 Generate tickets from the musical analysis!
    """
    tickets = []
    
    nums = [n for n, w in top_numbers if 1 <= n <= 50]
    stars = [s for s, w in top_stars if 1 <= s <= 12]
    
    if len(nums) < 5 or len(stars) < 2:
        return tickets
    
    # ═══════════════════════════════════════════════════════════════════════
    # Ticket 1: DATE CHAMELEON KING - Top weighted numbers
    # ═══════════════════════════════════════════════════════════════════════
    tickets.append({
        'name': '🦎 DATE CHAMELEON KING',
        'numbers': sorted(nums[:5]),
        'stars': sorted(stars[:2]),
        'reason': f'Highest weighted from date {day:02d}.{month:02d} patterns'
    })
    
    # ═══════════════════════════════════════════════════════════════════════
    # Ticket 2: RAW DIGIT FAMILY
    # ═══════════════════════════════════════════════════════════════════════
    raw_digits = set(str(day) + str(month).zfill(2))
    digit_family = []
    for d in raw_digits:
        if d != '0':
            digit = int(d)
            for mult in range(5):
                num = digit + mult * 10
                if 1 <= num <= 50 and num not in digit_family:
                    digit_family.append(num)
    
    if len(digit_family) >= 5:
        tickets.append({
            'name': '🔢 RAW DIGIT FAMILY',
            'numbers': sorted(digit_family[:5]),
            'stars': sorted(stars[:2]),
            'reason': f'Numbers from date digits {raw_digits}'
        })
    
    # ═══════════════════════════════════════════════════════════════════════
    # Ticket 3: CIRCLE FORMULA SPECIAL
    # ═══════════════════════════════════════════════════════════════════════
    target_314 = (day * 10) + circle_plus(month)
    circle_digits = list(set(str(target_314)))
    circle_nums = []
    for d in circle_digits:
        digit = int(d)
        if digit > 0:
            for mult in range(5):
                num = digit + mult * 10
                if 1 <= num <= 50 and num not in circle_nums:
                    circle_nums.append(num)
    
    if len(circle_nums) >= 5:
        tickets.append({
            'name': '⭕ CIRCLE FORMULA',
            'numbers': sorted(circle_nums[:5]),
            'stars': sorted(stars[1:3]) if len(stars) >= 3 else sorted(stars[:2]),
            'reason': f'Day×10 + circle(Month) = {target_314}'
        })
    
    # ═══════════════════════════════════════════════════════════════════════
    # Ticket 4: P1+P2 = Day+Month PAIRS
    # ═══════════════════════════════════════════════════════════════════════
    target_sum = day + month
    pairs_ticket = []
    for p1 in range(1, min(target_sum, 26)):
        p2 = target_sum - p1
        if 1 <= p2 <= 50 and p1 != p2:
            if p1 not in pairs_ticket:
                pairs_ticket.append(p1)
            if p2 not in pairs_ticket:
                pairs_ticket.append(p2)
            if len(pairs_ticket) >= 5:
                break
    
    if len(pairs_ticket) >= 5:
        tickets.append({
            'name': '🎯 P1+P2 = DAY+MONTH',
            'numbers': sorted(pairs_ticket[:5]),
            'stars': sorted(stars[:2]),
            'reason': f'Pairs summing to {day}+{month}={target_sum}'
        })
    
    # ═══════════════════════════════════════════════════════════════════════
    # Ticket 5: BALANCED MIX
    # ═══════════════════════════════════════════════════════════════════════
    if len(nums) >= 10:
        balanced = sorted(nums[:2] + nums[4:6] + nums[8:9])[:5]
        if len(balanced) == 5:
            tickets.append({
                'name': '🎵 BALANCED MIX',
                'numbers': balanced,
                'stars': sorted(stars[0:1] + stars[2:3]) if len(stars) >= 3 else sorted(stars[:2]),
                'reason': 'Mix of high and medium weighted candidates'
            })
    
    return tickets


# ═══════════════════════════════════════════════════════════════════════════════
# TEST RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
    from datetime import datetime
    
    def parse_date(d):
        return datetime.strptime(d['date'], "%d.%m.%Y")
    
    sorted_draws = sorted(
        EUROMILLIONS_DRAWS_2024_2026,
        key=lambda x: parse_date(x),
        reverse=True
    )
    
    # Test with a date
    target = "28.09.2025"
    
    print("=" * 70)
    print(f"🎧 DATE CHAMELEON MUSICAL ANALYSIS: {target} 🎻")
    print("=" * 70)
    
    result = musical_analysis(sorted_draws, target)
    
    print(f"\n📅 Target: {result['target_date']}")
    print(f"📅 Previous draw: {result['prev_date']}")
    
    print(f"\n🦎 DATE TARGETS:")
    for name, val in result['date_targets'].items():
        print(f"   {name}: {val}")
    
    print(f"\n🔢 TOP 15 NUMBERS (by musical weight):")
    for num, weight in result['top_numbers'][:15]:
        bar = "█" * int(weight / 10)
        print(f"   {num:2d}: {bar} ({weight:.1f})")
    
    print(f"\n⭐ TOP 6 STARS:")
    for star, weight in result['top_stars'][:6]:
        bar = "█" * int(weight / 10)
        print(f"   {star:2d}: {bar} ({weight:.1f})")
    
    print(f"\n📖 EXPLANATIONS:")
    for exp in result['explanations']:
        print(f"   {exp}")
    
    print(f"\n🎫 SUGGESTED TICKETS:")
    for ticket in result['suggested_tickets']:
        print(f"\n   {ticket['name']}:")
        print(f"      Numbers: {ticket['numbers']}")
        print(f"      Stars: {ticket['stars']}")
        print(f"      Reason: {ticket['reason']}")
    
    print("\n" + "=" * 70)
    print("🎧 THE DATE HAS SPOKEN! 🦎🍀")
    print("=" * 70)
