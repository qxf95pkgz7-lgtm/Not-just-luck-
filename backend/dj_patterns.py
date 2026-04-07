"""
🎧 LUCKY JACK'S DJ PATTERN ENGINE 🎻
====================================
All patterns discovered through the DJ Session backtesting!
Weights tuned based on 2023-2025 hit rates.

PATTERN HIT RATES (from DJ analysis):
=====================================
MEGA BANGERS (>40%):
  - Same decade pair: 93.8%
  - 9-Family: 49.8%
  - 2+ Primes: 49.3%
  - 7-Family: 47.4%
  - Number ending in S1: 47.6% → 41.3% avg
  - 5-Family: 44.5%
  - 8-Family: 42.3%

HIGH (25-40%):
  - Sum's last digit family: 39.9%
  - Consecutive pair: 38.8%
  - ANY number repeats: 38.5%
  - Number ending in S2: 33.9%
  - Star Diff → Position Gap: 28.7% avg
  - Double digits (11,22,33,44): 29.7%
  - Direct Addition (A+B=C): 25.2% avg

MEDIUM (12-25%):
  - Date Gap Prophecy: 19.6%
  - S1 Repeat: 16.8% avg
  - S2 Repeat: 17.1% avg
  - 49→45 Call: 15.0% avg
  - Day1 + Day2 sum: 12.4%
  - Circle of P2: 12.6%

RARE BUT KEEP (<12%):
  - Circle Partner (+25): 9.3%
  - Reverse Logic: 10.1%
  - P3 Hunger: 9.3%
  - P1 repeats: 2.4%
  - Consecutive triple: 2.9%

SPECIAL PATTERNS:
  - P1 Consecutive Alarm (3→4→5 predicts consecutive)
  - Date numbers hiding between dates
  - Hidden numbers sum to next P5
  - Date day appears in draw: 13.1%

Created: April 2026 - The DJ Session
"""

from typing import List, Dict, Set
from collections import Counter
from datetime import datetime
import random as rnd

# ═══════════════════════════════════════════════════════════════════════════════
# WEIGHT CONFIGURATION - THE DJ MIXER! 🎧
# ═══════════════════════════════════════════════════════════════════════════════

WEIGHTS = {
    # MEGA BANGERS (>40% hit rate)
    "number_ending_s1": 15,      # 47.6% - CHAMPION!
    "number_ending_s2": 10,      # 33.9%
    "eight_family": 12,          # 42.3%
    "seven_family": 12,          # 47.4%
    "nine_family": 12,           # 49.8%
    "five_family": 10,           # 44.5%
    "same_decade": 8,            # 93.8% - almost guaranteed, less weight needed
    
    # HIGH (25-40%)
    "star_diff_gap": 8,          # 28.7%
    "direct_addition": 8,        # 25.2%
    "consecutive_pair": 7,       # 38.8%
    "any_repeat": 7,             # 38.5%
    "double_digits": 5,          # 29.7%
    "sum_last_digit": 5,         # 39.9%
    
    # MEDIUM (12-25%)
    "date_gap_prophecy": 5,      # 19.6%
    "s1_repeat": 4,              # 16.8%
    "s2_repeat": 4,              # 17.1%
    "day_sum": 4,                # 12.4%
    "circle_p2": 3,              # 12.6%
    "forty_nine_forty_five": 6,  # 26.7% when applicable
    
    # RARE BUT PRESENT (<12%)
    "circle_partner": 2,         # 9.3%
    "reverse_logic": 2,          # 10.1%
    "p3_hunger": 2,              # 9.3%
    "date_in_draw": 10,          # 13.1% - BOOSTED! Date is important!
    
    # SPECIAL
    "p1_alarm_consecutive": 6,   # When P1 counts up
    "hidden_sum_p5": 4,          # Hidden numbers sum to P5
    "date_in_p1": 15,            # NEW! Day should appear at P1!
}


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
    if n < 10:
        return n
    rev = int(str(n)[::-1])
    if rev > 50:
        rev = rev % 50 if rev % 50 != 0 else 50
    return rev

def get_decade(n: int) -> int:
    """Get decade: 1-9=0, 10-19=1, 20-29=2, etc."""
    return (n - 1) // 10

def parse_draw_date(date_str: str) -> datetime:
    """Parse DD.MM.YYYY"""
    return datetime.strptime(date_str, "%d.%m.%Y")


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN FUNCTIONS - THE INSTRUMENTS! 🎻
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_number_ending_s1(prev_stars: List[int]) -> List[int]:
    """
    Numbers ending in S1 - 47.6% hit rate!
    If S1=3, return [3, 13, 23, 33, 43]
    """
    s1 = min(prev_stars)
    if s1 > 9:
        return []
    return [s1 + i*10 for i in range(5) if s1 + i*10 <= 50 and s1 + i*10 >= 1]

def pattern_number_ending_s2(prev_stars: List[int]) -> List[int]:
    """
    Numbers ending in S2 - 33.9% hit rate!
    """
    s2 = max(prev_stars)
    if s2 > 9:
        return []
    return [s2 + i*10 for i in range(5) if s2 + i*10 <= 50 and s2 + i*10 >= 1]

def pattern_family(base: int) -> List[int]:
    """Get family numbers: base, base+10, base+20, etc."""
    return [base + i*10 for i in range(5) if base + i*10 <= 50]

def pattern_eight_family() -> List[int]:
    return pattern_family(8)  # [8, 18, 28, 38, 48]

def pattern_seven_family() -> List[int]:
    return pattern_family(7)  # [7, 17, 27, 37, 47]

def pattern_nine_family() -> List[int]:
    return pattern_family(9)  # [9, 19, 29, 39, 49]

def pattern_five_family() -> List[int]:
    return pattern_family(5)  # [5, 15, 25, 35, 45]

def pattern_star_diff_gap(prev_stars: List[int], base_num: int) -> List[int]:
    """
    Star diff predicts position gaps - 28.7%
    If star_diff=7, look for numbers that create gap of 7
    """
    s1, s2 = min(prev_stars), max(prev_stars)
    star_diff = s2 - s1
    
    candidates = []
    # Numbers that would create this gap with base_num
    if base_num + star_diff <= 50:
        candidates.append(base_num + star_diff)
    if base_num - star_diff >= 1:
        candidates.append(base_num - star_diff)
    return candidates

def pattern_direct_addition(nums: List[int]) -> List[int]:
    """
    Find A + B = C candidates - 25.2%
    Given existing numbers, find C where A + B = C
    """
    candidates = []
    for i, a in enumerate(nums):
        for j, b in enumerate(nums):
            if i < j:
                c = a + b
                if 1 <= c <= 50 and c not in nums:
                    candidates.append(c)
    return candidates

def pattern_consecutive_pair(prev_nums: List[int]) -> List[int]:
    """
    Consecutive pairs - 38.8%
    If 23 appeared, 22 and 24 are candidates
    """
    candidates = []
    for n in prev_nums:
        if n > 1:
            candidates.append(n - 1)
        if n < 50:
            candidates.append(n + 1)
    return list(set(candidates))

def pattern_any_repeat(prev_nums: List[int]) -> List[int]:
    """
    Any number can repeat - 38.5%
    """
    return list(prev_nums)

def pattern_double_digits() -> List[int]:
    """Double digits - 29.7%"""
    return [11, 22, 33, 44]

def pattern_sum_last_digit(prev_nums: List[int]) -> List[int]:
    """
    Sum's last digit family - 39.9%
    """
    total = sum(prev_nums)
    last_digit = total % 10
    return [last_digit + i*10 for i in range(5) if last_digit + i*10 <= 50 and last_digit + i*10 >= 1]

def pattern_date_gap_prophecy(date1: str, date2: str) -> List[int]:
    """
    Numbers between dates appear - 19.6%
    Dates 21 and 25 → [22, 23, 24]
    """
    try:
        d1 = int(date1.split('.')[0])
        d2 = int(date2.split('.')[0])
        m1 = int(date1.split('.')[1])
        m2 = int(date2.split('.')[1])
        
        if m1 == m2 and d2 > d1:
            return list(range(d1 + 1, d2))
    except:
        pass
    return []

def pattern_day_sum(date1: str, date2: str) -> int:
    """
    Day1 + Day2 - 12.4%
    """
    try:
        d1 = int(date1.split('.')[0])
        d2 = int(date2.split('.')[0])
        s = d1 + d2
        if 1 <= s <= 50:
            return s
    except:
        pass
    return None

def pattern_circle_partner(n: int) -> int:
    """Circle +25 partner - 9.3%"""
    return circle(n)

def pattern_reverse(n: int) -> int:
    """Reverse digits - 10.1%"""
    return reverse_num(n)

def pattern_p3_hunger(nums: List[int]) -> List[int]:
    """
    Numbers between neighbors are hungry - 9.3%
    If 27 and 29 present, 28 is hungry
    """
    hungry = []
    sorted_nums = sorted(nums)
    for i in range(len(sorted_nums) - 1):
        gap = sorted_nums[i + 1] - sorted_nums[i]
        if gap == 2:
            hungry.append(sorted_nums[i] + 1)
    return hungry

def pattern_49_calls_45(prev_nums: List[int]) -> bool:
    """When 49 at P5, 45 is called - 26.7%"""
    sorted_nums = sorted(prev_nums)
    return sorted_nums[4] == 49

def pattern_star_repeat(prev_stars: List[int]) -> List[int]:
    """S1 and S2 can repeat - 17%"""
    return list(prev_stars)

def pattern_circle_p2(prev_nums: List[int]) -> int:
    """Circle of P2 - 12.6%"""
    p2 = sorted(prev_nums)[1]
    return circle(p2)

def pattern_date_in_draw(target_date: str) -> int:
    """Date day appears in draw - 13.1%"""
    try:
        day = int(target_date.split('.')[0])
        if 1 <= day <= 50:
            return day
    except:
        pass
    return None

def pattern_date_digits(target_date: str) -> List[int]:
    """
    NEW! Date digits appear separately - 16.09 → [1, 6, 9]
    The date SPLITS into its digits!
    """
    try:
        day = int(target_date.split('.')[0])
        month = int(target_date.split('.')[1])
        
        digits = set()
        # Day digits
        for d in str(day):
            if d != '0':
                digits.add(int(d))
        # Month digits  
        for d in str(month):
            if d != '0':
                digits.add(int(d))
        
        # Also add the day itself if <= 31
        if 1 <= day <= 31:
            digits.add(day)
        
        # Create candidates: digit, digit+10, digit+20, etc.
        candidates = []
        for digit in digits:
            if 1 <= digit <= 9:
                candidates.extend([digit + i*10 for i in range(5) if digit + i*10 <= 50])
            elif digit <= 50:
                candidates.append(digit)
        
        return list(set(candidates))
    except:
        return []

def pattern_date_digit_stars(target_date: str) -> List[int]:
    """Date digits can appear in stars too!"""
    try:
        day = int(target_date.split('.')[0])
        month = int(target_date.split('.')[1])
        
        star_candidates = []
        for d in str(day):
            if d != '0' and 1 <= int(d) <= 12:
                star_candidates.append(int(d))
        for d in str(month):
            if d != '0' and 1 <= int(d) <= 12:
                star_candidates.append(int(d))
        
        # Also day and month if they're valid stars
        if 1 <= day <= 12:
            star_candidates.append(day)
        if 1 <= month <= 12:
            star_candidates.append(month)
            
        return list(set(star_candidates))
    except:
        return []

def pattern_p1_alarm(draws: List[Dict]) -> bool:
    """
    Check if P1 is counting up (3→4→5)
    This predicts consecutive numbers coming!
    """
    if len(draws) < 3:
        return False
    
    p1s = [sorted(d['numbers'])[0] for d in draws[:3]]
    # Check if counting up
    if p1s[2] == p1s[1] - 1 == p1s[0] - 2:
        return True
    # Check if counting down toward us
    if p1s[0] == p1s[1] - 1 == p1s[2] - 2:
        return True
    return False

def pattern_hidden_sum_p5(date1: str, date2: str) -> List[int]:
    """
    Hidden numbers between dates sum to P5
    Dates 21, 25 → hidden 22,23,24 → sums: 45, 46, 47
    """
    hidden = pattern_date_gap_prophecy(date1, date2)
    if len(hidden) < 2:
        return []
    
    sums = []
    for i in range(len(hidden) - 1):
        s = hidden[i] + hidden[i + 1]
        if 1 <= s <= 50:
            sums.append(s)
    return sums


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DJ GENERATOR 🎧
# ═══════════════════════════════════════════════════════════════════════════════

def dj_generate_candidates(draws: List[Dict], target_date: str = None) -> Dict:
    """
    🎧 THE DJ GENERATOR - All patterns combined! 🎻
    
    Returns weighted candidates for each position and stars.
    """
    if not draws:
        return {"candidates": {}, "star_candidates": [], "patterns": []}
    
    candidates = {i: [] for i in range(5)}  # P1-P5
    star_candidates = []
    patterns_used = []
    
    prev_draw = draws[0]
    prev_nums = sorted(prev_draw['numbers'])
    prev_stars = sorted(prev_draw['stars'])
    prev_date = prev_draw['date']
    
    # Get second previous draw if available
    prev2_draw = draws[1] if len(draws) > 1 else None
    prev2_date = prev2_draw['date'] if prev2_draw else None
    
    # ═══════════════════════════════════════════════════════════════════
    # MEGA BANGERS (>40% hit rate) - Heavy rotation! 🔥
    # ═══════════════════════════════════════════════════════════════════
    
    # Number ending in S1 - 47.6%!
    s1_endings = pattern_number_ending_s1(prev_stars)
    for pos in range(5):
        candidates[pos].extend(s1_endings * WEIGHTS["number_ending_s1"])
    if s1_endings:
        patterns_used.append(f"🔥 Number ending in S1={prev_stars[0]}: {s1_endings}")
    
    # Number ending in S2 - 33.9%
    s2_endings = pattern_number_ending_s2(prev_stars)
    for pos in range(5):
        candidates[pos].extend(s2_endings * WEIGHTS["number_ending_s2"])
    if s2_endings:
        patterns_used.append(f"🔥 Number ending in S2={prev_stars[1]}: {s2_endings}")
    
    # Family patterns - all ~45% hit rate!
    for fam_name, fam_func, weight_key in [
        ("8-family", pattern_eight_family, "eight_family"),
        ("7-family", pattern_seven_family, "seven_family"),
        ("9-family", pattern_nine_family, "nine_family"),
        ("5-family", pattern_five_family, "five_family"),
    ]:
        fam_nums = fam_func()
        for pos in range(5):
            candidates[pos].extend(fam_nums * WEIGHTS[weight_key])
        patterns_used.append(f"🔥 {fam_name}: {fam_nums}")
    
    # ═══════════════════════════════════════════════════════════════════
    # HIGH (25-40%) - Regular rotation 🎵
    # ═══════════════════════════════════════════════════════════════════
    
    # Star Diff → Position Gap - 28.7%
    star_diff = prev_stars[1] - prev_stars[0]
    for base in prev_nums[:3]:  # Use P1, P2, P3 as bases
        gap_nums = pattern_star_diff_gap(prev_stars, base)
        for pos in range(5):
            candidates[pos].extend(gap_nums * WEIGHTS["star_diff_gap"])
    patterns_used.append(f"🎵 Star diff={star_diff} → gaps")
    
    # Direct Addition (A+B=C) - 25.2%
    addition_candidates = pattern_direct_addition(prev_nums)
    for pos in range(2, 5):  # More likely at P3, P4, P5
        candidates[pos].extend(addition_candidates * WEIGHTS["direct_addition"])
    if addition_candidates:
        patterns_used.append(f"🎵 Direct Addition candidates: {addition_candidates[:5]}")
    
    # Consecutive Pair - 38.8%
    consec = pattern_consecutive_pair(prev_nums)
    for pos in range(5):
        candidates[pos].extend(consec * WEIGHTS["consecutive_pair"])
    patterns_used.append(f"🎵 Consecutive neighbors")
    
    # Any Repeat - 38.5%
    repeats = pattern_any_repeat(prev_nums)
    for pos in range(5):
        candidates[pos].extend(repeats * WEIGHTS["any_repeat"])
    patterns_used.append(f"🎵 Repeat candidates: {repeats}")
    
    # Double Digits - 29.7%
    doubles = pattern_double_digits()
    for pos in range(5):
        candidates[pos].extend(doubles * WEIGHTS["double_digits"])
    patterns_used.append(f"🎵 Double digits: {doubles}")
    
    # Sum's Last Digit Family - 39.9%
    sum_family = pattern_sum_last_digit(prev_nums)
    for pos in range(5):
        candidates[pos].extend(sum_family * WEIGHTS["sum_last_digit"])
    patterns_used.append(f"🎵 Sum last digit family: {sum_family}")
    
    # ═══════════════════════════════════════════════════════════════════
    # MEDIUM (12-25%) - Occasional plays 🎹
    # ═══════════════════════════════════════════════════════════════════
    
    # Date Gap Prophecy - 19.6%
    if prev2_date:
        hidden_nums = pattern_date_gap_prophecy(prev2_date, prev_date)
        for pos in range(5):
            candidates[pos].extend(hidden_nums * WEIGHTS["date_gap_prophecy"])
        if hidden_nums:
            patterns_used.append(f"🎹 Date gap prophecy ({prev2_date}→{prev_date}): {hidden_nums}")
        
        # Hidden Sum P5 - Special pattern!
        hidden_sums = pattern_hidden_sum_p5(prev2_date, prev_date)
        candidates[4].extend(hidden_sums * WEIGHTS["hidden_sum_p5"])  # P5 specifically
        if hidden_sums:
            patterns_used.append(f"🎹 Hidden sums for P5: {hidden_sums}")
    
    # Day Sum - 12.4%
    if prev2_date:
        day_s = pattern_day_sum(prev2_date, prev_date)
        if day_s:
            for pos in range(5):
                candidates[pos].extend([day_s] * WEIGHTS["day_sum"])
            patterns_used.append(f"🎹 Day sum: {day_s}")
    
    # 49→45 Call - 26.7% when applicable
    if pattern_49_calls_45(prev_nums):
        candidates[3].extend([45] * WEIGHTS["forty_nine_forty_five"])  # P4 preferred
        candidates[4].extend([45] * WEIGHTS["forty_nine_forty_five"])
        patterns_used.append(f"🔥 49 at P5 calls 45!")
    
    # Circle of P2 - 12.6%
    circ_p2 = pattern_circle_p2(prev_nums)
    for pos in range(5):
        candidates[pos].extend([circ_p2] * WEIGHTS["circle_p2"])
    patterns_used.append(f"🎹 Circle(P2={prev_nums[1]})={circ_p2}")
    
    # Date in Draw - 13.1% - NOW MEGA BOOSTED!
    if target_date:
        day_num = pattern_date_in_draw(target_date)
        if day_num and 1 <= day_num <= 31:
            # MEGA weight at P1 - the date LOVES P1!
            candidates[0].extend([day_num] * WEIGHTS["date_in_p1"] * 3)  # Triple boost!
            # Also add to P2 with good weight
            candidates[1].extend([day_num] * WEIGHTS["date_in_draw"] * 2)
            # And P3 with normal weight
            candidates[2].extend([day_num] * WEIGHTS["date_in_draw"])
            patterns_used.append(f"📅 DATE DAY = {day_num} (MEGA BOOST at P1!)")
        
        # NEW! DATE DIGITS - The date SPLITS into digits!
        date_digits = pattern_date_digits(target_date)
        if date_digits:
            for digit_num in date_digits:
                # Heavy weight for date digits
                candidates[0].extend([digit_num] * 10)  # P1 loves digits
                candidates[1].extend([digit_num] * 8)   # P2 too
                for pos in range(2, 5):
                    candidates[pos].extend([digit_num] * 5)
            patterns_used.append(f"📅 DATE DIGITS: {sorted(set([d for d in date_digits if d <= 9]))} → families!")
        
        # NEW! DATE DIGITS IN STARS!
        date_stars = pattern_date_digit_stars(target_date)
        if date_stars:
            for s in date_stars:
                star_candidates.extend([s] * 8)  # Boost date digits in stars!
            patterns_used.append(f"⭐ DATE STARS: {date_stars}")
    
    # ═══════════════════════════════════════════════════════════════════
    # RARE BUT PRESENT (<12%) - Subtle notes 🎹
    # ═══════════════════════════════════════════════════════════════════
    
    # Circle Partners - 9.3%
    for n in prev_nums:
        circ = pattern_circle_partner(n)
        for pos in range(5):
            candidates[pos].extend([circ] * WEIGHTS["circle_partner"])
    patterns_used.append(f"🎹 Circle partners (rare)")
    
    # Reverse Logic - 10.1%
    for n in prev_nums:
        if n >= 10:
            rev = pattern_reverse(n)
            for pos in range(5):
                candidates[pos].extend([rev] * WEIGHTS["reverse_logic"])
    patterns_used.append(f"🎹 Reverse logic (rare)")
    
    # P3 Hunger - 9.3%
    hungry = pattern_p3_hunger(prev_nums)
    for h in hungry:
        for pos in range(5):
            candidates[pos].extend([h] * WEIGHTS["p3_hunger"])
    if hungry:
        patterns_used.append(f"🎹 P3 Hunger: {hungry}")
    
    # ═══════════════════════════════════════════════════════════════════
    # SPECIAL PATTERNS
    # ═══════════════════════════════════════════════════════════════════
    
    # P1 Alarm - When P1 counts (3→4→5), expect consecutive!
    if pattern_p1_alarm(draws):
        # Add consecutive triples
        base = rnd.randint(15, 35)
        for pos in [1, 2, 3]:
            candidates[pos].extend([base, base+1, base+2] * WEIGHTS["p1_alarm_consecutive"])
        patterns_used.append(f"🚨 P1 ALARM! Consecutive expected around {base}-{base+2}")
    
    # ═══════════════════════════════════════════════════════════════════
    # STAR CANDIDATES
    # ═══════════════════════════════════════════════════════════════════
    
    # S1 Repeat - 16.8%
    star_candidates.extend([prev_stars[0]] * WEIGHTS["s1_repeat"])
    
    # S2 Repeat - 17.1%
    star_candidates.extend([prev_stars[1]] * WEIGHTS["s2_repeat"])
    
    # Stars from date
    if target_date:
        try:
            day = int(target_date.split('.')[0])
            digit_sum = sum(int(d) for d in str(day))
            if 1 <= digit_sum <= 12:
                star_candidates.extend([digit_sum] * 3)
                patterns_used.append(f"⭐ Day digit sum: {digit_sum}")
        except:
            pass
    
    # Add variety
    for s in range(1, 13):
        star_candidates.append(s)  # Base variety
    
    return {
        "candidates": candidates,
        "star_candidates": star_candidates,
        "patterns": patterns_used,
        "prev_nums": prev_nums,
        "prev_stars": prev_stars,
    }


def dj_select_numbers(candidates: Dict, star_candidates: List[int], locked: Dict = None, date_day: int = None) -> Dict:
    """
    🎧 Select final numbers from weighted candidates
    date_day: If provided, has 30% chance to force this number at P1
    """
    locked = locked or {}
    
    selected = []
    used = set()
    
    # Special: 30% chance to force date_day at P1
    if date_day and 1 <= date_day <= 31 and 0 not in locked:
        if rnd.random() < 0.30:  # 30% chance
            selected.append(date_day)
            used.add(date_day)
        else:
            selected.append(None)  # Placeholder, will be filled below
    
    # Select for each position
    for pos in range(5):
        if pos < len(selected) and selected[pos] is not None:
            continue  # Already selected (date forced)
            
        if pos in locked:
            if pos < len(selected):
                selected[pos] = locked[pos]
            else:
                selected.append(locked[pos])
            used.add(locked[pos])
        else:
            # Get candidates for this position, filter used
            pos_candidates = [c for c in candidates.get(pos, []) if c not in used and 1 <= c <= 50]
            
            if pos_candidates:
                # Weighted random selection
                choice = rnd.choice(pos_candidates)
            else:
                # Fallback to any unused number
                available = [n for n in range(1, 51) if n not in used]
                choice = rnd.choice(available)
            
            if pos < len(selected):
                selected[pos] = choice
            else:
                selected.append(choice)
            used.add(choice)
    
    # Select stars
    star_used = set()
    selected_stars = []
    
    for _ in range(2):
        star_pool = [s for s in star_candidates if s not in star_used and 1 <= s <= 12]
        if star_pool:
            star = rnd.choice(star_pool)
        else:
            available = [s for s in range(1, 13) if s not in star_used]
            star = rnd.choice(available)
        selected_stars.append(star)
        star_used.add(star)
    
    return {
        "numbers": sorted(selected),
        "stars": sorted(selected_stars)
    }


def dj_generate_ticket(draws: List[Dict], target_date: str = None, locked: Dict = None) -> Dict:
    """
    🎧 Generate a single ticket using the DJ engine
    """
    result = dj_generate_candidates(draws, target_date)
    
    # Extract date day for special P1 handling
    date_day = None
    if target_date:
        try:
            date_day = int(target_date.split('.')[0])
        except:
            pass
    
    selection = dj_select_numbers(result["candidates"], result["star_candidates"], locked, date_day)
    
    return {
        "numbers": selection["numbers"],
        "stars": selection["stars"],
        "patterns_used": result["patterns"],
        "prev_draw": {
            "numbers": result["prev_nums"],
            "stars": result["prev_stars"]
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# TEST / SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
    
    # Sort draws newest first
    sorted_draws = sorted(
        EUROMILLIONS_DRAWS_2024_2026,
        key=lambda x: parse_draw_date(x['date']),
        reverse=True
    )
    
    print("=" * 70)
    print("🎧 DJ GENERATOR SIMULATION 🎻")
    print("=" * 70)
    print()
    
    # Show last draw
    print(f"📅 Last draw: {sorted_draws[0]['date']}")
    print(f"   Numbers: {sorted(sorted_draws[0]['numbers'])}")
    print(f"   Stars: {sorted(sorted_draws[0]['stars'])}")
    print()
    
    # Generate 5 tickets
    print("🎫 GENERATING 5 TICKETS:")
    print("-" * 70)
    
    for i in range(5):
        ticket = dj_generate_ticket(sorted_draws, target_date="07.04.2026")
        print(f"\n   Ticket {i+1}: {ticket['numbers']}  ⭐ {ticket['stars']}")
        print(f"   Patterns: {len(ticket['patterns_used'])} active")
    
    print()
    print("=" * 70)
    print("🎵 First ticket pattern breakdown:")
    print("=" * 70)
    ticket = dj_generate_ticket(sorted_draws, target_date="07.04.2026")
    for p in ticket['patterns_used'][:15]:
        print(f"   {p}")
