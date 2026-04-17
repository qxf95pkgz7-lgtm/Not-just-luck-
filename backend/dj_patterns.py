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
  - Flip Logic: 10.1%
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

# Import the Date Chameleon and Real Numbers from musical_patterns!
from musical_patterns import pattern_date_chameleon, pattern_real_numbers

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
    
    # DATE PATTERNS - The Date speaks! 📅
    "day_plus_month": 12,        # Day + Month = candidate (16% hit rate! 1.6x random!)
    "day_minus_month": 4,        # |Day - Month| = candidate
    "day_times_month": 4,        # Day × Month = candidate (if ≤ 50)
    
    # SPECIAL
    "p1_alarm_consecutive": 6,   # When P1 counts up
    "hidden_sum_p5": 4,          # Hidden numbers sum to P5
    "date_in_p1": 15,            # NEW! Day should appear at P1!
    
    # 🍀 CROSS-LOTTERY PATTERNS (Swiss → Euro) - NEW!
    "cross_swiss_day_month": 8,  # 13.3% hit rate! SwissDay + EuroMonth
    "cross_lucky_mult": 8,       # 13.3% hit rate! Lucky × EuroMonth
    "cross_swiss_minus_days": 6, # 11.1% hit rate! Swiss - DaysDiff
    "cross_swiss_direct": 4,     # 10% - Swiss numbers ≤ 50
    "cross_lucky_star": 8,       # 16.7% - Lucky → Star prediction
    
    # 🇨🇭 SWISS P1 → EURO P1 BRIDGE (Backtested: 1407 draws)
    "swiss_p1_to_euro_p1": 18,       # 3.48x random! Last Swiss P1 → Euro P1
    "swiss_p1_prev_to_euro_p1": 12,  # 2.84x random! Last-2 Swiss P1 → Euro P1
    "swiss_p1_set_to_euro": 10,      # 2.57x random! 3x Swiss P1 SET → any Euro
    "swiss_p2_to_euro_p1": 8,        # 2.10x random! Last Swiss P2 → Euro P1
    
    # 💤 SLEEPER WAKE ALARM - NEW! Proven by 30 sims!
    "sleeper_tease_hot": 10,     # 72% of wakers get teased first
    "sleeper_sweet_spot": 8,     # 1.0-1.5x overdue = 51.2% fast wake
    "sleeper_snap_back": 6,      # 3.0x+ overdue = 47.9% fast wake
    "sleeper_circle_pump": 5,    # Circle boost = 41.9% fast wake
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

def flip(n: int) -> int:
    """Flip digits — 28 becomes 82, 4 stays 4. Mod 50 if needed"""
    if n < 10:
        return n
    rev = int(str(n)[::-1])
    if rev > 50:
        rev = rev % 50 if rev % 50 != 0 else 50
    return rev


def flip_circle_chain(n: int) -> List[int]:
    """
    🎻 FLIP+CIRCLE CHAIN — Follow the FULL chain, not just one step!
    
    28 → flip → 82 → mod50 → 32 → circle → 7
    39 → flip → 93 → mod50 → 43
    43 → flip → 34 → circle → 9
    Single digits: circle FIRST, then flip: 4 → circle → 29 → flip → 92 → mod50 → 42
    14 → 41 → 91(+50) → flip → 19 (long distance family)
    
    Returns all numbers in the chain (the full family).
    """
    family = set()
    family.add(n)
    
    if n < 10:
        # Single digit: circle FIRST, then flip
        c = circle(n)
        family.add(c)
        # Now flip the circle result
        if c >= 10:
            f = int(str(c)[::-1])
            if 1 <= f <= 50:
                family.add(f)
            elif f > 50:
                landed = f - 50
                if 1 <= landed <= 50:
                    family.add(landed)
                # Also circle the landed value
                family.add(circle(landed))
    else:
        # Two digits: flip first
        raw_flip = int(str(n)[::-1])
        if 1 <= raw_flip <= 50:
            family.add(raw_flip)
            # Circle the flip
            family.add(circle(raw_flip))
        elif raw_flip > 50:
            # Bring to range via mod50
            landed = raw_flip - 50 if raw_flip <= 100 else raw_flip % 50
            if landed == 0: landed = 50
            if 1 <= landed <= 50:
                family.add(landed)
                # Circle the landed value
                family.add(circle(landed))
        
        # Long distance: n+50 → flip
        extended = n + 50
        ext_flip = int(str(extended)[::-1])
        if 1 <= ext_flip <= 50 and ext_flip != n:
            family.add(ext_flip)
    
    family.discard(n)  # Remove original
    return [x for x in sorted(family) if 1 <= x <= 50]


def date_reading(date_str: str) -> dict:
    """
    🎧 DATE READING — Read the date in ALL possible ways!
    
    The date is the sheet music. Every reading gives candidate digits/numbers.
    Example 17.04.2026:
      - 174 (D+M concat) → digits 1,7,4
      - 199 (170+29, D×10 + circle(M)) → digits 1,9,9
      - 42 (D circle) → digits 4,2
      - 424 (D_circle concat M) → digits 4,2,4
      - 449 (420+29, D_circle×10 + circle(M)) → digits 4,4,9
      - D+M, D-M, D×M sums and their digits
      - D circle chain → full date story
    """
    try:
        parts = date_str.split('.')
        day = int(parts[0])
        month = int(parts[1])
    except:
        return {"digits": set(), "numbers": [], "explanations": []}
    
    digits = set()
    numbers = []
    explanations = []
    
    # 1. Day and Month as digits
    for ch in str(day) + str(month):
        if ch != '0':
            digits.add(int(ch))
    explanations.append(f"Date digits: {sorted(digits)}")
    
    # 2. D+M concat (e.g., 174 from 17+4)
    concat_dm = int(f"{day}{month}")
    for ch in str(concat_dm):
        if ch != '0':
            digits.add(int(ch))
    explanations.append(f"D+M concat: {concat_dm} -> digits {[int(c) for c in str(concat_dm) if c != '0']}")
    
    # 3. Day circle
    if 1 <= day <= 50:
        d_circle = circle(day)
        numbers.append(d_circle)
        for ch in str(d_circle):
            if ch != '0':
                digits.add(int(ch))
        explanations.append(f"Day circle: {day}+25={d_circle}")
    
    # 4. Month circle
    if 1 <= month <= 50:
        m_circle = circle(month)
        numbers.append(m_circle)
        explanations.append(f"Month circle: {month}+25={m_circle}")
    
    # 5. D×10 + circle(M) (e.g., 170+29=199)
    dm_expand = day * 10 + circle(month) if month <= 12 else 0
    if dm_expand > 0:
        for ch in str(dm_expand):
            if ch != '0':
                digits.add(int(ch))
        explanations.append(f"D×10+circle(M): {day*10}+{circle(month)}={dm_expand}")
    
    # 6. D_circle × 10 + circle(M) (e.g., 420+29=449)
    if 1 <= day <= 50:
        dc_expand = circle(day) * 10 + circle(month) if month <= 12 else 0
        if dc_expand > 0:
            for ch in str(dc_expand):
                if ch != '0':
                    digits.add(int(ch))
            explanations.append(f"Dcircle×10+circle(M): {circle(day)*10}+{circle(month)}={dc_expand}")
    
    # 7. D+M, D-M, D×M
    d_plus_m = day + month
    d_minus_m = abs(day - month)
    d_times_m = day * month
    for val in [d_plus_m, d_minus_m, d_times_m]:
        for ch in str(val):
            if ch != '0':
                digits.add(int(ch))
        if 1 <= val <= 50:
            numbers.append(val)
    explanations.append(f"D+M={d_plus_m}, D-M={d_minus_m}, D×M={d_times_m}")
    
    # 8. Day circle chain → then flip
    if 1 <= day <= 50:
        chain = flip_circle_chain(day)
        for c in chain:
            if 1 <= c <= 50:
                numbers.append(c)
                for ch in str(c):
                    if ch != '0':
                        digits.add(int(ch))
        if chain:
            explanations.append(f"Day flip+circle chain: {day} -> {chain}")
    
    # 9. Month circle chain
    if 1 <= month <= 50:
        m_chain = flip_circle_chain(month)
        for c in m_chain:
            if 1 <= c <= 50:
                numbers.append(c)
        if m_chain:
            explanations.append(f"Month flip+circle chain: {month} -> {m_chain}")
    
    return {
        "digits": digits,
        "numbers": list(set(n for n in numbers if 1 <= n <= 50)),
        "explanations": explanations
    }


def star_q_count_decode(stars: List[int], prev_q_draws: List[dict]) -> dict:
    """
    🌟 STAR → Q COUNT → P1 DECODE
    
    Stars from the current draw index into the PREVIOUS quarter's draw count.
    The P1 of that Q(N) draw predicts P1/P2 of the current Q(N+1) draw.
    
    Validated: 75% hit rate Q1→Q2 2026!
    
    Rules:
    - Star S → go to prev Q draw #S → read P1
    - Star 12 wraps to 1 (clock)
    - Star digits: Star 12 = digits 1,2 → both positions referenced
    - Allow ±1 dancing between predicted and actual
    
    Args:
        stars: current draw's star values [S1, S2]
        prev_q_draws: list of draws from previous quarter (sorted by date)
    
    Returns:
        dict with p1_candidates, p2_candidates, and explanations
    """
    if not prev_q_draws or not stars:
        return {"p1_candidates": [], "p2_candidates": [], "explanations": []}
    
    # Build P1 map: draw_count -> P1 value
    p1_map = {}
    for i, d in enumerate(prev_q_draws):
        nums = sorted(d.get('numbers', []))
        if nums:
            p1_map[i + 1] = nums[0]  # dc -> P1
    
    p1_candidates = []
    p2_candidates = []
    explanations = []
    
    for s in sorted(stars):
        # Direct star → Q count lookup
        if s in p1_map:
            val = p1_map[s]
            p1_candidates.append((val, 60, f"Star {s} -> Q count {s} -> P1={val}"))
            # ±1 variants
            if val - 1 >= 1:
                p1_candidates.append((val - 1, 30, f"Star {s} -> c{s} -> P1={val} ±1 -> {val-1}"))
            if val + 1 <= 50:
                p1_candidates.append((val + 1, 30, f"Star {s} -> c{s} -> P1={val} ±1 -> {val+1}"))
            explanations.append(f"Star {s} -> prev Q draw #{s} -> P1={val}")
        
        # Star 12 = 1 (clock wrapping)
        if s == 12 and 1 in p1_map:
            val = p1_map[1]
            p1_candidates.append((val, 40, f"Star 12=1 -> Q count 1 -> P1={val}"))
            explanations.append(f"Star 12 wraps to 1 -> prev Q draw #1 -> P1={val}")
        
        # Star digit decomposition: 12 → digits 1,2 → both Q counts
        if s >= 10:
            for ch in str(s):
                d = int(ch)
                if d > 0 and d in p1_map:
                    val = p1_map[d]
                    p2_candidates.append((val, 40, f"Star {s} digit {d} -> Q count {d} -> P1={val}"))
                    explanations.append(f"Star {s} digit {d} -> prev Q draw #{d} -> P1={val}")
    
    return {
        "p1_candidates": p1_candidates,
        "p2_candidates": p2_candidates,
        "explanations": explanations
    }

def get_decade(n: int) -> int:
    """Get decade: 1-9=0, 10-19=1, 20-29=2, etc."""
    return (n - 1) // 10

def parse_draw_date(date_str: str) -> datetime:
    """Parse DD.MM.YYYY"""
    return datetime.strptime(date_str, "%d.%m.%Y")


# ═══════════════════════════════════════════════════════════════════════════════
# 🍀 CROSS-LOTTERY PATTERNS (Swiss → Euro) - NEW!
# ═══════════════════════════════════════════════════════════════════════════════

def cross_lottery_swiss_to_euro(swiss_draw: dict, swiss_date_str: str, euro_date_str: str) -> dict:
    """
    🍀 Generate Euro candidates from recent Swiss draw!
    
    Backtested hit rates:
    - SwissDay + EuroMonth: 13.3% (1.3x random!)
    - Lucky × EuroMonth: 13.3% (1.3x random!)
    - Swiss - DaysDiff: 11.1% (1.1x random!)
    - Direct Echo: 10%
    - Lucky → Star: 16.7%
    
    Args:
        swiss_draw: dict with 'numbers' and 'lucky_number'
        swiss_date_str: Swiss draw date "DD.MM.YYYY"
        euro_date_str: Target Euro date "DD.MM.YYYY"
    
    Returns:
        dict with pattern_name -> list of candidates
    """
    candidates = {}
    
    swiss_nums = swiss_draw.get('numbers', [])
    swiss_lucky = swiss_draw.get('lucky_number')
    
    try:
        swiss_dt = parse_draw_date(swiss_date_str)
        euro_dt = parse_draw_date(euro_date_str)
    except:
        return candidates
    
    days_diff = (euro_dt - swiss_dt).days
    if days_diff <= 0 or days_diff > 14:
        return candidates  # Only use Swiss draws 1-14 days before
    
    swiss_day = swiss_dt.day
    euro_month = euro_dt.month
    
    # 1. SwissDay + EuroMonth (13.3% hit rate!)
    combo1 = swiss_day + euro_month
    if 1 <= combo1 <= 50:
        candidates['swiss_day_month'] = [combo1]
    
    # 2. Lucky × EuroMonth (13.3% hit rate!)
    if swiss_lucky:
        combo2 = swiss_lucky * euro_month
        if 1 <= combo2 <= 50:
            candidates['lucky_mult'] = [combo2]
    
    # 3. Swiss - DaysDiff (11.1% hit rate!)
    minus_cands = [n - days_diff for n in swiss_nums if 1 <= n - days_diff <= 50]
    if minus_cands:
        candidates['swiss_minus_days'] = minus_cands
    
    # 4. Direct Echo (10%)
    direct = [n for n in swiss_nums if 1 <= n <= 50]
    if direct:
        candidates['swiss_direct'] = direct
    
    # 5. Lucky → Star (16.7%)
    if swiss_lucky and 1 <= swiss_lucky <= 12:
        candidates['lucky_star'] = [swiss_lucky]
    
    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# 🇨🇭 SWISS P1 → EURO P1 BRIDGE (Backtested: 1407 draws, 3.48x random!)
# ═══════════════════════════════════════════════════════════════════════════════

def swiss_p1_bridge(swiss_draws: List[Dict]) -> Dict:
    """
    THE BRIDGE: Swiss P1 positions predict Euro numbers!
    
    Backtested results (1407 draws):
    - Last Swiss P1 → Euro P1: 7.0% (3.48x random!) ★★★
    - Last-2 Swiss P1 → Euro P1: 5.7% (2.84x random!) ★★★
    - 3x Swiss P1 SET → any Euro: 25.7% (2.57x random!) ★★★
    - Last Swiss P2 → Euro P1: 4.2% (2.10x random!) ★★
    
    Returns P1 priority candidates and general candidates
    """
    if not swiss_draws or len(swiss_draws) < 3:
        return {'p1_candidates': [], 'general_candidates': [], 'explanations': []}
    
    # Swiss draws may come sorted newest-first OR oldest-first
    # Detect and ensure we get: last1=newest, last2=second newest, last3=third newest
    # Try parsing dates to sort properly
    try:
        from datetime import datetime as dt
        parsed = []
        for s in swiss_draws[:10]:
            try:
                d = dt.strptime(s.get('date', ''), '%d.%m.%Y')
                parsed.append((d, s))
            except:
                pass
        if len(parsed) >= 3:
            parsed.sort(key=lambda x: x[0], reverse=True)  # Newest first
            last1 = parsed[0][1]  # Most recent
            last2 = parsed[1][1]  # Second most recent
            last3 = parsed[2][1]  # Third most recent
        else:
            return {'p1_candidates': [], 'general_candidates': [], 'explanations': []}
    except:
        # Fallback: assume newest first
        last1 = swiss_draws[0]
        last2 = swiss_draws[1]
        last3 = swiss_draws[2]
    
    s1_nums = sorted(last1.get('numbers', []))
    s2_nums = sorted(last2.get('numbers', []))
    s3_nums = sorted(last3.get('numbers', []))
    
    if not s1_nums or not s2_nums or not s3_nums:
        return {'p1_candidates': [], 'general_candidates': [], 'explanations': []}
    
    s1_p1 = s1_nums[0]  # Last Swiss P1
    s2_p1 = s2_nums[0]  # Last-2 Swiss P1
    s3_p1 = s3_nums[0]  # Last-3 Swiss P1
    s1_p2 = s1_nums[1] if len(s1_nums) > 1 else None  # Last Swiss P2
    
    p1_candidates = []  # These get HEAVY boost for Euro P1 position
    general_candidates = []  # These get lighter boost for any position
    explanations = []
    
    # RULE B1: Last Swiss P1 → Euro P1 (3.48x!) - STRONGEST
    if 1 <= s1_p1 <= 50:
        p1_candidates.append((s1_p1, 18, f"Swiss P1 Bridge: {s1_p1} (3.48x)"))
        explanations.append(f"SWISS P1→EURO P1: Last Swiss P1={s1_p1} (3.48x random)")
    
    # RULE B2: Last-2 Swiss P1 → Euro P1 (2.84x!)
    if 1 <= s2_p1 <= 50 and s2_p1 != s1_p1:
        p1_candidates.append((s2_p1, 12, f"Swiss P1[-2] Bridge: {s2_p1} (2.84x)"))
        explanations.append(f"SWISS P1[-2]→EURO P1: Last-2 Swiss P1={s2_p1} (2.84x random)")
    
    # RULE E4: Last Swiss P2 → Euro P1 (2.10x!)
    if s1_p2 and 1 <= s1_p2 <= 50 and s1_p2 not in [s1_p1, s2_p1]:
        p1_candidates.append((s1_p2, 8, f"Swiss P2 Bridge: {s1_p2} (2.10x)"))
    
    # RULE H1: 3x Swiss P1 SET → any Euro (25.7% = 2.57x!)
    p1_set = set([s1_p1, s2_p1, s3_p1])
    for p in p1_set:
        if 1 <= p <= 50:
            general_candidates.append((p, 10, f"Swiss P1 SET: {p}"))
    
    if p1_set:
        explanations.append(f"SWISS P1 SET: {sorted(p1_set)} → any Euro (25.7%, 2.57x)")
    
    return {
        'p1_candidates': p1_candidates,
        'general_candidates': general_candidates,
        'explanations': explanations,
        'swiss_p1s': [s1_p1, s2_p1, s3_p1],
    }


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

# ═══════════════════════════════════════════════════════════════════════════════
# NEW! DEEP DATE PATTERNS - The date cooperates! 📅
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_circle_date(target_date: str) -> Dict:
    """
    Circle of day and month ± 1
    16.09 → circle(16)=41 ±1, circle(9)=34 ±1
    """
    try:
        day = int(target_date.split('.')[0])
        month = int(target_date.split('.')[1])
        
        candidates = []
        
        # Circle of day ± 1
        circle_day = day + 25 if day <= 25 else day - 25
        for offset in [-1, 0, 1]:
            val = circle_day + offset
            if 1 <= val <= 50:
                candidates.append(val)
        
        # Circle of month ± 1
        circle_month = month + 25
        for offset in [-1, 0, 1]:
            val = circle_month + offset
            if 1 <= val <= 50:
                candidates.append(val)
        
        return {
            "candidates": candidates,
            "circle_day": circle_day,
            "circle_month": circle_month
        }
    except:
        return {"candidates": [], "circle_day": 0, "circle_month": 0}

def pattern_date_sum(target_date: str) -> List[int]:
    """
    Day + Month sum and its derivatives
    16.09 → 16+9=25, circle(25)=50
    """
    try:
        day = int(target_date.split('.')[0])
        month = int(target_date.split('.')[1])
        
        candidates = []
        
        # Day + Month
        date_sum = day + month
        if 1 <= date_sum <= 50:
            candidates.append(date_sum)
        
        # Circle of sum
        circle_sum = date_sum + 25 if date_sum <= 25 else date_sum - 25
        if 1 <= circle_sum <= 50:
            candidates.append(circle_sum)
        
        # Day - Month (absolute)
        diff = abs(day - month)
        if 1 <= diff <= 50:
            candidates.append(diff)
        
        # Day × Month digit sum (if reasonable)
        product = day * month
        if product <= 50:
            candidates.append(product)
        elif product <= 99:
            # Digit sum
            digit_sum = sum(int(d) for d in str(product))
            if 1 <= digit_sum <= 50:
                candidates.append(digit_sum)
        
        return list(set(candidates))
    except:
        return []

def pattern_serial_45(target_date: str) -> int:
    """
    The 45 connection - day + month derivatives
    When digits sum to 9 (month), 45 is calling!
    """
    try:
        day = int(target_date.split('.')[0])
        month = int(target_date.split('.')[1])
        
        # 45 special: 4+5=9
        if month == 9:
            return 45
        
        # Or if day digits sum to 9
        if sum(int(d) for d in str(day)) == 9:
            return 45
            
        return None
    except:
        return None

def pattern_star_times_month(target_date: str, prev_stars: List[int]) -> List[int]:
    """
    Star × Month = hidden number
    Star 5 × Month 9 = 45
    """
    try:
        month = int(target_date.split('.')[1])
        
        candidates = []
        for star in prev_stars:
            product = star * month
            if 1 <= product <= 50:
                candidates.append(product)
            # Also digit sum of product
            elif product <= 99:
                digit_sum = sum(int(d) for d in str(product))
                if 1 <= digit_sum <= 50:
                    candidates.append(digit_sum)
        
        return candidates
    except:
        return []

def pattern_circle_partner(n: int) -> int:
    """Circle +25 partner - 9.3%"""
    return circle(n)

def pattern_flip(n: int) -> int:
    """Flip digits - 10.1%"""
    return flip(n)

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


def beast_block_filter(star_candidates: List[int], draws: List[Dict]) -> List[int]:
    """
    666 BEAST BLOCK - The universe resists Star 6 three times in a row!
    
    Data proof (1,587 draws):
    - After Star 6 appears 2x in a row, the 3rd draw BLOCKS it 77% of the time
    - Only 8 beast events ever occurred (once per 198 draws)
    
    When Star 6 is on a 2-streak, we crush its weight to near-zero.
    This makes the engine respect the universal resistance pattern.
    """
    if len(draws) < 2:
        return star_candidates
    
    stars_d1 = draws[0].get('stars', [])
    stars_d2 = draws[1].get('stars', [])
    
    if 6 in stars_d1 and 6 in stars_d2:
        # Beast alert! Star 6 has appeared 2x in a row
        # Strip almost ALL Star 6 entries from candidates (keep 1 for the 23% chance)
        count_6 = star_candidates.count(6)
        if count_6 > 1:
            filtered = [s for s in star_candidates if s != 6]
            filtered.append(6)  # Keep exactly 1 for the rare 23% case
            return filtered
    
    return star_candidates

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

def pattern_deep_date_expansion(target_date: str) -> Dict:
    """
    🎧 THE DEEP DATE EXPANSION PATTERN! 🎧
    
    User's esoteric formula discovered April 2026:
    - Day 7 → 70 (expand single digit by ×10!)
    - Month 4 → 4 (raw) OR 29 (circle: 4+25)
    - 70 + 4 = 74 → reverse=47, circle(74-50)=24, or 74-25=49
    - 70 + 29 = 99 → 9-Family (9,19,29,39,49) OR 99-50=49
    
    On April 7th draw: 11-14-19-36-49 → 19 and 49 both HIT via this pattern!
    """
    try:
        day = int(target_date.split('.')[0])
        month = int(target_date.split('.')[1])
        
        candidates = []
        explanations = []
        
        # Step 1: Expand day to tens (7 → 70)
        expanded_day = day * 10  # 7 → 70
        
        # Step 2: Month raw and circled
        month_raw = month  # 4
        month_circle = month + 25 if month <= 25 else month - 25  # 4 → 29
        
        # ═══════════════════════════════════════════════════════════════
        # Pattern A: expanded_day + month_raw = X
        # 70 + 4 = 74
        sum_a = expanded_day + month_raw
        explanations.append(f"D×10+M = {expanded_day}+{month_raw} = {sum_a}")
        
        # Derivatives of sum_a:
        # - If 1-50, direct candidate
        if 1 <= sum_a <= 50:
            candidates.append(sum_a)
        # - If > 50, subtract 50 (circle down)
        if sum_a > 50:
            circled_a = sum_a - 50  # 74 - 50 = 24
            if 1 <= circled_a <= 50:
                candidates.append(circled_a)
                explanations.append(f"{sum_a}-50 = {circled_a}")
            # Also try -25 (circle logic)
            circled_a2 = sum_a - 25  # 74 - 25 = 49
            if 1 <= circled_a2 <= 50:
                candidates.append(circled_a2)
                explanations.append(f"{sum_a}-25 = {circled_a2}")
        
        # Reverse of sum_a (74 → 47)
        if sum_a >= 10:
            reversed_a = int(str(sum_a)[::-1])
            if reversed_a > 50:
                reversed_a = reversed_a - 50 if reversed_a <= 100 else reversed_a % 50
            if 1 <= reversed_a <= 50:
                candidates.append(reversed_a)
                explanations.append(f"reverse({sum_a}) = {reversed_a}")
        
        # ═══════════════════════════════════════════════════════════════
        # Pattern B: expanded_day + month_circle = Y
        # 70 + 29 = 99
        sum_b = expanded_day + month_circle
        explanations.append(f"D×10+circle(M) = {expanded_day}+{month_circle} = {sum_b}")
        
        # Derivatives of sum_b:
        # - If 1-50, direct
        if 1 <= sum_b <= 50:
            candidates.append(sum_b)
        # - If > 50, subtract 50
        if sum_b > 50:
            circled_b = sum_b - 50  # 99 - 50 = 49
            if 1 <= circled_b <= 50:
                candidates.append(circled_b)
                explanations.append(f"{sum_b}-50 = {circled_b}")
        
        # 99 → "9 Family" search!
        if sum_b >= 90 and sum_b <= 99:
            # Last digit is the family
            family_base = sum_b % 10  # 99 → 9
            if family_base == 0:
                family_base = 10
            family = [family_base + i*10 for i in range(5) if family_base + i*10 <= 50]
            candidates.extend(family)
            explanations.append(f"{sum_b} → {family_base}-Family: {family}")
        
        # Reverse of sum_b
        if sum_b >= 10:
            reversed_b = int(str(sum_b)[::-1])
            if reversed_b > 50:
                reversed_b = reversed_b - 50 if reversed_b <= 100 else reversed_b % 50
            if 1 <= reversed_b <= 50 and reversed_b not in candidates:
                candidates.append(reversed_b)
                explanations.append(f"reverse({sum_b}) = {reversed_b}")
        
        return {
            "candidates": list(set(candidates)),
            "explanations": explanations,
            "expanded_day": expanded_day,
            "month_raw": month_raw,
            "month_circle": month_circle,
            "sum_a": sum_a,
            "sum_b": sum_b
        }
    except:
        return {"candidates": [], "explanations": [], "expanded_day": 0, "month_raw": 0, "month_circle": 0, "sum_a": 0, "sum_b": 0}


def pattern_sequence_hunger(draws: List[Dict], window: int = 4) -> List[int]:
    """
    🎧 SEQUENCE HUNGER TRACKER 🎧
    
    When part of a consecutive sequence appears across recent draws,
    the MISSING pieces are "hungry" and want to appear!
    
    Example: 22 and 24 appeared → 23 is HUNGRY!
    Example: 16, 17, 18 appeared → 19 is NEXT in sequence!
    """
    if not draws or len(draws) < 2:
        return []
    
    # Collect all numbers from recent draws (flattened)
    recent_nums = set()
    for d in draws[:window]:
        recent_nums.update(d['numbers'])
    
    hungry = []
    
    # Find gaps of 1 (direct hunger)
    sorted_recent = sorted(recent_nums)
    for i in range(len(sorted_recent) - 1):
        gap = sorted_recent[i + 1] - sorted_recent[i]
        if gap == 2:  # Missing one number between
            missing = sorted_recent[i] + 1
            if 1 <= missing <= 50:
                hungry.append(missing)
    
    # Find sequence continuations
    # If 16, 17, 18 present → 19 is the continuation
    for n in sorted_recent:
        # Check if n-1 and n-2 are present (counting UP)
        if (n - 1) in recent_nums and (n - 2) in recent_nums:
            next_in_seq = n + 1
            if 1 <= next_in_seq <= 50 and next_in_seq not in recent_nums:
                hungry.append(next_in_seq)
        # Check if n+1 and n+2 are present (counting DOWN)
        if (n + 1) in recent_nums and (n + 2) in recent_nums:
            prev_in_seq = n - 1
            if 1 <= prev_in_seq <= 50 and prev_in_seq not in recent_nums:
                hungry.append(prev_in_seq)
    
    return list(set(hungry))


def pattern_p3_counting_echo(draws: List[Dict]) -> Dict:
    """
    🎧 P3 COUNTING PATTERN 🎧
    
    P3 has been observed counting: 16→17→18→19
    Track what P3 is doing and predict its next step!
    
    Also detects hidden counting via math:
    29 - 10 = 19 (hidden 19 in the position)
    """
    if len(draws) < 3:
        return {"next_p3": None, "trend": None, "confidence": 0}
    
    # Get P3 values from recent draws
    p3_values = []
    for d in draws[:5]:
        nums = sorted(d['numbers'])
        if len(nums) >= 3:
            p3_values.append(nums[2])
    
    if len(p3_values) < 3:
        return {"next_p3": None, "trend": None, "confidence": 0}
    
    # Check for counting pattern
    diffs = [p3_values[i] - p3_values[i+1] for i in range(len(p3_values)-1)]
    
    # All +1 or all -1?
    if all(d == -1 for d in diffs[:3]):  # Counting UP (older → newer)
        next_p3 = p3_values[0] + 1
        trend = "UP"
        confidence = 0.8
    elif all(d == 1 for d in diffs[:3]):  # Counting DOWN
        next_p3 = p3_values[0] - 1
        trend = "DOWN"
        confidence = 0.8
    elif all(d == 0 for d in diffs[:2]):  # Repeating
        next_p3 = p3_values[0]
        trend = "REPEAT"
        confidence = 0.5
    else:
        # No clear pattern, but return the average neighborhood
        next_p3 = p3_values[0]
        trend = "UNCLEAR"
        confidence = 0.3
    
    return {
        "next_p3": next_p3 if 1 <= next_p3 <= 50 else None,
        "trend": trend,
        "confidence": confidence,
        "recent_p3s": p3_values[:5]
    }


def pattern_group_shift(draws: List[Dict], window: int = 4) -> List[int]:
    """
    🎧 GROUP SHIFT TRACKING 🎧
    
    Numbers shift in groups: +10, +20, +30 cohorts.
    If 12-18 appeared, watch for 22-28 (+10) or 42-48 (+30).
    
    Example from user: "The numbers shift in groups!"
    """
    if not draws or len(draws) < 2:
        return []
    
    candidates = []
    
    # Get numbers from the draw BEFORE the most recent
    # (because we're predicting what comes AFTER current)
    prev_nums = set(draws[0]['numbers']) if draws else set()
    
    # For each number, calculate its +10, +20, +30 shifts
    for n in prev_nums:
        for shift in [10, 20, 30]:
            shifted = n + shift
            if 1 <= shifted <= 50 and shifted not in prev_nums:
                candidates.append(shifted)
            # Also consider negative shifts
            shifted_neg = n - shift
            if 1 <= shifted_neg <= 50 and shifted_neg not in prev_nums:
                candidates.append(shifted_neg)
    
    return list(set(candidates))


def pattern_flip_dance(draws: List[Dict]) -> List[int]:
    """
    🎧 FLIP DANCE PATTERN 🎧
    
    Numbers dance with their flips!
    72 → 27, 47 echoes from 74, etc.
    
    When X appears, flip(X) is calling!
    """
    if not draws:
        return []
    
    candidates = []
    prev_nums = draws[0]['numbers']
    
    for n in prev_nums:
        if n >= 10:
            rev = int(str(n)[::-1])
            # Handle > 50 cases
            if rev > 50:
                rev = rev - 50 if rev <= 100 else rev % 50
                if rev == 0:
                    rev = 50
            if 1 <= rev <= 50 and rev not in prev_nums:
                candidates.append(rev)
    
    return candidates


def pattern_day_dance(draws: List[Dict], target_date: str = None) -> Dict:
    """
    🎧 DAY DANCE PATTERN 🎧
    
    D1 + D2 = XY → X and Y appear in next draw!
    
    Example from user:
    - 27.03 + 31.03 = 58
    - On 31.03.2026: P1=5, P2=8! BOTH HIT!
    
    Statistical validation:
    - D1+D2 digit hits Star: 30.5%! ⭐
    - D1+D2 digit hits P1: 14.4%
    - D1+D2 sum in draw: 8.5%
    """
    if not draws or len(draws) < 2:
        return {"candidates": [], "star_candidates": [], "day_sum": 0, "digits": []}
    
    # Get the two most recent dates
    day1 = int(draws[0]['date'].split('.')[0])
    day2 = int(draws[1]['date'].split('.')[0])
    
    # If we have a target date, use that as day1
    if target_date:
        try:
            day1 = int(target_date.split('.')[0])
            day2 = int(draws[0]['date'].split('.')[0])  # Previous draw's day
        except:
            pass
    
    day_sum = day1 + day2
    
    # Extract digits
    if day_sum >= 10:
        digit1 = day_sum // 10
        digit2 = day_sum % 10
    else:
        digit1 = 0
        digit2 = day_sum
    
    candidates = []
    star_candidates = []
    
    # The digits themselves
    if digit1 >= 1:
        candidates.append(digit1)
        if 1 <= digit1 <= 12:
            star_candidates.append(digit1)
    if digit2 >= 1:
        candidates.append(digit2)
        if 1 <= digit2 <= 12:
            star_candidates.append(digit2)
    
    # The full sum if valid
    if 1 <= day_sum <= 50:
        candidates.append(day_sum)
    
    # Family expansion of digits (5 → 5, 15, 25, 35, 45)
    for digit in [digit1, digit2]:
        if 1 <= digit <= 9:
            for mult in range(5):
                num = digit + mult * 10
                if 1 <= num <= 50:
                    candidates.append(num)
    
    return {
        "candidates": list(set(candidates)),
        "star_candidates": list(set(star_candidates)),
        "day_sum": day_sum,
        "digits": [digit1, digit2],
        "day1": day1,
        "day2": day2
    }


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

def dj_generate_candidates(draws: List[Dict], target_date: str = None, swiss_draws: List[Dict] = None) -> Dict:
    """
    🎧 THE DJ GENERATOR - All patterns combined! 🎻
    
    Returns weighted candidates for each position and stars.
    
    Args:
        draws: List of EuroMillions draws
        target_date: Target draw date DD.MM.YYYY
        swiss_draws: Optional list of Swiss Lotto draws for cross-lottery patterns
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
        # NEW! DEEP DATE PATTERNS - The date cooperates! 📅
        # ═══════════════════════════════════════════════════════════════════
        
        # Circle of Day and Month ± 1
        circle_date_result = pattern_circle_date(target_date)
        circle_candidates = circle_date_result["candidates"]
        if circle_candidates:
            for pos in range(3, 5):  # P4, P5 love circle dates
                candidates[pos].extend(circle_candidates * 8)
            for pos in range(0, 3):  # P1-P3 also get some
                candidates[pos].extend(circle_candidates * 4)
            patterns_used.append(f"⭕ CIRCLE(day)={circle_date_result['circle_day']}±1, CIRCLE(month)={circle_date_result['circle_month']}±1")
        
        # Day + Month sum and derivatives - BOOSTED! (missed 14 = 10+4 on 10.04.2026!)
        date_sum_candidates = pattern_date_sum(target_date)
        if date_sum_candidates:
            # Day + Month direct is the FIRST candidate - give it extra boost!
            day_plus_month = date_sum_candidates[0] if date_sum_candidates else None
            if day_plus_month:
                for pos in range(5):
                    candidates[pos].extend([day_plus_month] * WEIGHTS.get("day_plus_month", 8))
                patterns_used.append(f"📅 DAY+MONTH = {day_plus_month} (BOOSTED!)")
            
            # Other date sum derivatives
            for num in date_sum_candidates[1:]:
                for pos in range(5):
                    candidates[pos].extend([num] * 6)
            patterns_used.append(f"📅 DATE SUM: {date_sum_candidates}")
        
        # The 45 connection (when month=9 or digits sum to 9)
        serial_45 = pattern_serial_45(target_date)
        if serial_45:
            candidates[3].extend([45] * 10)  # P4
            candidates[4].extend([45] * 10)  # P5
            patterns_used.append(f"🔢 SERIAL 45 (month=9 connection!)")
        
        # Star × Month = hidden number
        star_month_nums = pattern_star_times_month(target_date, prev_stars)
        if star_month_nums:
            for pos in range(2, 5):  # P3-P5
                candidates[pos].extend(star_month_nums * 6)
            patterns_used.append(f"⭐×📅 Star × Month: {star_month_nums}")
        
        # ═══════════════════════════════════════════════════════════════════
        # 🦎 DATE CHAMELEON - THE KING PATTERN! 🦎
        # PROVEN: 70.3% raw digits, 61.2% circle formula, 56.5% day×10+month!
        # The date speaks in MANY voices!
        # ═══════════════════════════════════════════════════════════════════
        try:
            chameleon_day = int(target_date.split('.')[0])
            chameleon_month = int(target_date.split('.')[1])
            chameleon = pattern_date_chameleon(chameleon_day, chameleon_month)
        except:
            chameleon = None
        if chameleon:
            # Get all the transformation targets
            chameleon_candidates = chameleon.get("numbers", [])
            chameleon_stars = chameleon.get("stars", [])
            targets = chameleon.get("targets", {})
            
            # Apply with weights based on hit rates!
            for num, hit_rate, reason in chameleon_candidates[:30]:  # Top 30 candidates
                if 1 <= num <= 50:
                    # Weight based on hit rate: 70% = weight 14, 60% = weight 12, etc.
                    weight = max(2, int(hit_rate / 5))
                    for pos in range(5):
                        candidates[pos].extend([num] * weight)
            
            for star, hit_rate, reason in chameleon_stars[:10]:  # Top 10 star candidates
                if 1 <= star <= 12:
                    weight = max(2, int(hit_rate / 5))
                    star_candidates.extend([star] * weight)
            
            # Log the chameleon transformations
            patterns_used.append(f"🦎 DATE CHAMELEON ({target_date}):")
            if 'day10_circle_month' in targets:
                patterns_used.append(f"   ↳ Day×10+circle(M) = {targets['day10_circle_month']} (67.5%)")
            if 'day10_month' in targets:
                patterns_used.append(f"   ↳ Day×10+M = {targets['day10_month']} (61.7%)")
            if 'day_plus_month' in targets:
                patterns_used.append(f"   ↳ Day+M = {targets['day_plus_month']} (55.5%)")
            if 'day_minus_month' in targets:
                patterns_used.append(f"   ↳ Day-M = {targets['day_minus_month']} (51.7%)")
        
        # ═══════════════════════════════════════════════════════════════════
        # 🎧 DEEP DATE EXPANSION - User's April 2026 Discovery! 🎧
        # D×10 + M/circle(M) = X → reverse/circle derivatives
        # ═══════════════════════════════════════════════════════════════════
        deep_date_result = pattern_deep_date_expansion(target_date)
        deep_candidates = deep_date_result.get("candidates", [])
        if deep_candidates:
            # Heavy weight - this pattern hit 19 AND 49 on April 7th!
            for pos in range(5):
                candidates[pos].extend(deep_candidates * 12)
            patterns_used.append(f"🎧 DEEP DATE: D×10+M/circle(M) → {deep_candidates[:5]}")
            for exp in deep_date_result.get("explanations", [])[:3]:
                patterns_used.append(f"   ↳ {exp}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 💃 DAY DANCE PATTERN - D1 + D2 = XY! 💃
    # 30.5% hit rate on Stars, 14.4% on P1!
    # ═══════════════════════════════════════════════════════════════════
    day_dance_result = pattern_day_dance(draws, target_date)
    day_dance_candidates = day_dance_result.get("candidates", [])
    day_dance_stars = day_dance_result.get("star_candidates", [])
    
    if day_dance_candidates:
        # Heavy weight on P1 and P2 - that's where the magic happens!
        for c in day_dance_candidates:
            candidates[0].extend([c] * 15)  # P1 loves day dance!
            candidates[1].extend([c] * 12)  # P2 too!
            for pos in range(2, 5):
                candidates[pos].extend([c] * 5)
        patterns_used.append(f"💃 DAY DANCE: D1+D2={day_dance_result['day1']}+{day_dance_result['day2']}={day_dance_result['day_sum']} → digits {day_dance_result['digits']}")
    
    if day_dance_stars:
        # 30.5% hit rate on stars!
        for s in day_dance_stars:
            star_candidates.extend([s] * 10)
        patterns_used.append(f"⭐ DAY DANCE STARS: {day_dance_stars}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 🎯 REAL NUMBERS - Quarter Start Pattern! 🎯
    # P(x) + days_between = appears in next draw (11% hit rate over 4 years!)
    # P2 is THE KING with 47% of all hits!
    # ═══════════════════════════════════════════════════════════════════
    if draws:
        real_numbers_result = pattern_real_numbers(draws[0], target_date)
        real_candidates = real_numbers_result.get("numbers", [])
        
        if real_numbers_result.get("is_quarter_start"):
            patterns_used.append("🎯 REAL NUMBERS (Quarter Start!):")
            
            for num, weight, reason in real_candidates:
                if 1 <= num <= 50:
                    # Apply heavy weight - this is a proven pattern!
                    w = int(weight / 3)  # Scale weight appropriately
                    for pos in range(5):
                        candidates[pos].extend([num] * w)
                    
                    if "P2 King" in reason:
                        patterns_used.append(f"   ↳ {reason}")
            
            # Add explanations
            for exp in real_numbers_result.get("explanations", [])[:5]:
                if "REAL NUMBERS ACTIVE" not in exp:
                    patterns_used.append(exp)
    
    # ═══════════════════════════════════════════════════════════════════
    # 🎧 NEW ESOTERIC PATTERNS - The Deep Music! 🎧
    # ═══════════════════════════════════════════════════════════════════
    
    # Sequence Hunger Tracker - Missing numbers from consecutive sequences
    hungry_sequences = pattern_sequence_hunger(draws, window=4)
    if hungry_sequences:
        for h in hungry_sequences:
            for pos in range(5):
                candidates[pos].extend([h] * 10)  # High weight - hungry numbers want to appear!
        patterns_used.append(f"🍽️ SEQUENCE HUNGER: {hungry_sequences[:5]}")
    
    # P3 Counting Echo - P3 has been counting!
    p3_echo = pattern_p3_counting_echo(draws)
    if p3_echo.get("next_p3") and p3_echo.get("confidence", 0) >= 0.5:
        next_p3 = p3_echo["next_p3"]
        candidates[2].extend([next_p3] * 15)  # Strong weight at P3
        # Also add ±1 neighbors
        if next_p3 > 1:
            candidates[2].extend([next_p3 - 1] * 5)
        if next_p3 < 50:
            candidates[2].extend([next_p3 + 1] * 5)
        patterns_used.append(f"📈 P3 COUNTING: trend={p3_echo['trend']}, next≈{next_p3}")
    
    # Group Shift Tracking - Numbers shift in +10/+20/+30 cohorts
    shifted_nums = pattern_group_shift(draws, window=4)
    if shifted_nums:
        for s in shifted_nums[:10]:  # Top 10 shift candidates
            for pos in range(5):
                candidates[pos].extend([s] * 4)
        patterns_used.append(f"↔️ GROUP SHIFT: {shifted_nums[:5]}")
    
    # Flip Dance - Numbers dance with their flips
    flip_dancers = pattern_flip_dance(draws)
    if flip_dancers:
        for r in flip_dancers:
            for pos in range(5):
                candidates[pos].extend([r] * 6)
        patterns_used.append(f"🔄 FLIP DANCE: {flip_dancers}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 🎵 NEW DJ SESSION PATTERNS - April 2026 Discoveries! 🎵
    # P1-1, P2-6, Circle P3, Twin Bridges, Chain Patterns
    # ═══════════════════════════════════════════════════════════════════
    
    # P1-1 Pattern (8.5% hit rate!)
    p1m1_result = pattern_p1_minus_1(prev_draw)
    if p1m1_result['candidate']:
        c = p1m1_result['candidate']
        w = p1m1_result['weight']
        for pos in range(5):
            candidates[pos].extend([c] * (w // 10))
        patterns_used.append(p1m1_result['explanation'])
    
    # P2-6 Pattern (8.1% hit rate!)
    p2m6_result = pattern_p2_minus_6(prev_draw)
    if p2m6_result['candidate']:
        c = p2m6_result['candidate']
        w = p2m6_result['weight']
        for pos in range(5):
            candidates[pos].extend([c] * (w // 10))
        patterns_used.append(p2m6_result['explanation'])
    
    # Circle P3 Pattern (10.2% hit rate!)
    cp3_result = pattern_circle_p3(prev_draw)
    if cp3_result['candidate']:
        c = cp3_result['candidate']
        ds = cp3_result['digit_sum']
        w = cp3_result['weight']
        for pos in range(5):
            candidates[pos].extend([c] * (w // 10))
            if 1 <= ds <= 50:
                candidates[pos].extend([ds] * 4)  # Digit sum also good
        patterns_used.append(cp3_result['explanation'])
    
    # Twin Bridges Pattern (up to 22.4% for ±2 twins!)
    twins_result = pattern_twin_bridges(prev_draw)
    for num, weight, reason in twins_result['candidates']:
        if 1 <= num <= 50:
            for pos in range(5):
                candidates[pos].extend([num] * (weight // 10))
    for exp in twins_result['explanations'][:3]:
        patterns_used.append(exp)
    
    # Consecutive Trio → Minus Digit Pattern (50% when trio found!)
    trio_result = pattern_consecutive_trio_minus_digit(prev_draw)
    if trio_result['prediction']:
        pred = trio_result['prediction']
        w = trio_result['weight']
        # Heavy weight - this is a powerful pattern!
        for pos in range(5):
            candidates[pos].extend([pred] * (w // 5))
        patterns_used.append(trio_result['explanation'])
    
    # Circle Bridge 35 Pattern (multiple predictions!)
    if prev2_draw:
        bridge_result = pattern_circle_bridge_35(prev_draw, prev2_draw)
        for num, weight, reason in bridge_result['candidates']:
            if 1 <= num <= 50:
                for pos in range(5):
                    candidates[pos].extend([num] * (weight // 10))
        for exp in bridge_result['explanations'][:2]:
            patterns_used.append(exp)
    
    # The Chain: 22-28-15-40-29 (static chain numbers call each other)
    chain_result = pattern_p2_chain_22_28_15_40_29()
    chain_nums = chain_result['chain']
    # If any chain number is in previous draw, boost the others
    for num in prev_nums:
        if num in chain_nums:
            for c in chain_nums:
                if c != num and 1 <= c <= 50:
                    for pos in range(5):
                        candidates[pos].extend([c] * 3)
            patterns_used.append(f"🔗 CHAIN ACTIVE: {num} calls {[c for c in chain_nums if c != num]}")
            break
    
    # ═══════════════════════════════════════════════════════════════════
    # RARE BUT PRESENT (<12%) - Subtle notes 🎹
    # ═══════════════════════════════════════════════════════════════════
    
    # Circle Partners - 9.3%
    for n in prev_nums:
        circ = pattern_circle_partner(n)
        for pos in range(5):
            candidates[pos].extend([circ] * WEIGHTS["circle_partner"])
    patterns_used.append(f"🎹 Circle partners (rare)")
    
    # Flip Logic - 10.1%
    for n in prev_nums:
        if n >= 10:
            rev = pattern_flip(n)
            for pos in range(5):
                candidates[pos].extend([rev] * WEIGHTS["reverse_logic"])
    patterns_used.append(f"🎹 Flip logic")
    
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
    # 🌟 FLIP+CIRCLE CHAIN — The Full Family! (April 2026 Discovery)
    # Not just single flip — follow the ENTIRE chain!
    # ═══════════════════════════════════════════════════════════════════
    for n in prev_nums:
        chain = flip_circle_chain(n)
        for c in chain:
            if 1 <= c <= 50:
                for pos in range(5):
                    candidates[pos].extend([c] * 5)
        if chain:
            patterns_used.append(f"🔗 FLIP+CIRCLE CHAIN: {n} -> {chain}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 📅 DATE READING — The Date is the Sheet Music!
    # Read the target date in ALL ways to extract candidate digits
    # ═══════════════════════════════════════════════════════════════════
    if target_date:
        dr = date_reading(target_date)
        date_digits = dr["digits"]
        date_numbers = dr["numbers"]
        
        # Date digits boost: any number containing these digits gets weight
        for d in date_digits:
            # Numbers that START with this digit
            for n in range(d * 1, min(d * 10 + 10, 51)):
                if 1 <= n <= 50:
                    for pos in range(5):
                        candidates[pos].extend([n] * 2)
            # Numbers that END with this digit
            for n in range(1, 51):
                if n % 10 == d:
                    for pos in range(5):
                        candidates[pos].extend([n] * 2)
        
        # Direct date numbers (circles, sums, chains)
        for n in date_numbers:
            for pos in range(5):
                candidates[pos].extend([n] * 6)
        
        if date_digits:
            patterns_used.append(f"📅 DATE READING: digits={sorted(date_digits)}, numbers={date_numbers[:5]}")
        for exp in dr["explanations"][:3]:
            patterns_used.append(f"📅 {exp}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 🌟 STAR → Q COUNT → P1 DECODE (75% hit rate Q1→Q2 2026!)
    # Stars index into previous quarter's draw count to predict P1/P2
    # ═══════════════════════════════════════════════════════════════════
    if draws and len(draws) >= 10:
        # Determine current quarter and find previous quarter's draws
        try:
            from datetime import datetime as dt_cls
            current_date = dt_cls.strptime(target_date, "%d.%m.%Y") if target_date else dt_cls.now()
            current_q = (current_date.month - 1) // 3 + 1
            current_year = current_date.year
            
            # Previous quarter
            if current_q == 1:
                prev_q, prev_year = 4, current_year - 1
            else:
                prev_q, prev_year = current_q - 1, current_year
            
            prev_q_start_month = (prev_q - 1) * 3 + 1
            prev_q_end_month = prev_q * 3
            
            # Filter draws from previous quarter
            prev_q_draws = []
            for d in draws:
                try:
                    dd = dt_cls.strptime(d['date'], "%d.%m.%Y")
                    if dd.year == prev_year and prev_q_start_month <= dd.month <= prev_q_end_month:
                        prev_q_draws.append(d)
                except:
                    continue
            
            prev_q_draws.sort(key=lambda x: dt_cls.strptime(x['date'], "%d.%m.%Y"))
            
            if prev_q_draws and prev_stars:
                sq_result = star_q_count_decode(prev_stars, prev_q_draws)
                
                # P1 candidates get heavy weight at position 0
                for val, weight, reason in sq_result.get("p1_candidates", []):
                    if 1 <= val <= 50:
                        candidates[0].extend([val] * weight)
                        candidates[1].extend([val] * (weight // 3))
                
                # P2 candidates
                for val, weight, reason in sq_result.get("p2_candidates", []):
                    if 1 <= val <= 50:
                        candidates[1].extend([val] * weight)
                        candidates[0].extend([val] * (weight // 3))
                
                for exp in sq_result.get("explanations", [])[:3]:
                    patterns_used.append(f"🌟 STAR-Q: {exp}")
        except Exception as e:
            pass  # Silently skip if date parsing fails
    
    # ═══════════════════════════════════════════════════════════════════
    # STAR CANDIDATES
    # ═══════════════════════════════════════════════════════════════════
    
    # S1 Repeat - 16.8% 🔥 BOOSTED!
    star_candidates.extend([prev_stars[0]] * 6)  # Was WEIGHTS["s1_repeat"], now boosted
    patterns_used.append(f"⭐ S1 ECHO: {prev_stars[0]} (16.8%)")
    
    # S2 Repeat - 18.1% 🔥🔥 STRONGEST STAR PATTERN!
    star_candidates.extend([prev_stars[1]] * 7)  # Was WEIGHTS["s2_repeat"], now boosted more
    patterns_used.append(f"⭐ S2 ECHO: {prev_stars[1]} (18.1%)")
    
    # ═══════════════════════════════════════════════════════════════════
    # 🔥 NEW STAR PATTERNS (September 2025 Session) 🔥
    # ═══════════════════════════════════════════════════════════════════
    
    # |S2-S1| → Star (17.4% hit rate!) 🔥🔥
    s_diff_result = pattern_star_diff_to_star(prev_draw)
    if s_diff_result['candidate']:
        star_candidates.extend([s_diff_result['candidate']] * 6)  # Heavy weight
        patterns_used.append(s_diff_result['explanation'])
    
    # S1 × 2 → Star (16.1%) and S1+S2 → Star (8.7%) 🔥
    s_times_result = pattern_star_times_2(prev_draw)
    for cand, weight, reason in s_times_result.get('candidates', []):
        if 1 <= cand <= 12:
            star_candidates.extend([cand] * (weight // 10))
    for exp in s_times_result.get('explanations', []):
        patterns_used.append(exp)
    
    # ═══════════════════════════════════════════════════════════════════
    # 🔥 NEW NUMBER PATTERNS (September 2025 Session) 🔥
    # ═══════════════════════════════════════════════════════════════════
    
    # P4+P5 first digit → Number (12.8%) 🔥
    p4p5_result = pattern_p4_p5_digit(prev_draw)
    if p4p5_result.get('candidate'):
        c = p4p5_result['candidate']
        for pos in range(5):
            candidates[pos].extend([c] * 5)
        patterns_used.append(p4p5_result['explanation'])
    
    # Month × 2 → Number (10.7%) 🔥
    if target_date:
        m2_result = pattern_month_times_2(target_date)
        if m2_result.get('candidate'):
            c = m2_result['candidate']
            for pos in range(5):
                candidates[pos].extend([c] * 4)
            patterns_used.append(m2_result['explanation'])
        
        # Day ÷ 2 → Number (8.3%) 🔥
        d2_result = pattern_day_div_2(target_date)
        if d2_result.get('candidate'):
            c = d2_result['candidate']
            for pos in range(5):
                candidates[pos].extend([c] * 4)
            patterns_used.append(d2_result['explanation'])
    
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
    
    # ═══════════════════════════════════════════════════════════════════
    # 🔥 TUNED PATTERNS - May 2025 Session (09.05.2025 Analysis) 🔥
    # P2 Family, P5 Echo, P4 Family, P3+1, Day=Star
    # ═══════════════════════════════════════════════════════════════════
    
    # P2 MINUS FAMILY (P2-3, P2-4, P2-5) - 8-9% each!
    p2_family = pattern_p2_minus_family(prev_draw)
    for num, weight, reason in p2_family.get('candidates', []):
        if 1 <= num <= 50:
            for pos in range(5):
                candidates[pos].extend([num] * (weight // 10))
    for exp in p2_family.get('explanations', []):
        patterns_used.append(exp)
    
    # P5 ECHO & P5-1 (14.8% and 11.4%) - STRONG!
    p5_result = pattern_p5_echo_and_minus(prev_draw)
    for num, weight, reason in p5_result.get('candidates', []):
        if 1 <= num <= 50:
            for pos in range(5):
                candidates[pos].extend([num] * (weight // 10))
    for exp in p5_result.get('explanations', []):
        patterns_used.append(exp)
    
    # P4 ECHO & FAMILY (P4-1, P4+1) - 8-10%!
    p4_result = pattern_p4_echo_and_family(prev_draw)
    for num, weight, reason in p4_result.get('candidates', []):
        if 1 <= num <= 50:
            for pos in range(5):
                candidates[pos].extend([num] * (weight // 10))
    for exp in p4_result.get('explanations', []):
        patterns_used.append(exp)
    
    # P3 + 1 (9.4%)
    p3_p1_result = pattern_p3_plus_1(prev_draw)
    if p3_p1_result.get('candidate'):
        c = p3_p1_result['candidate']
        for pos in range(5):
            candidates[pos].extend([c] * 4)
        patterns_used.append(p3_p1_result['explanation'])
    
    # Day = Star (17.2%) - VERY STRONG for stars!
    if target_date:
        day_star_result = pattern_day_equals_star(target_date)
        if day_star_result.get('candidate'):
            star_candidates.extend([day_star_result['candidate']] * 6)
            patterns_used.append(day_star_result['explanation'])
    
    # STAR→P3 DANCE (17.5% combined - discovered April 2026!)
    # Stars predict P3 via concat, reverse, and circle
    star_p3_vals = []
    # concat(S2,S1) -> circle (6.2% strongest!)
    try:
        c_val = int(f"{s2}{s1}")
        while c_val > 50: c_val -= 25
        if 1 <= c_val <= 50: star_p3_vals.append(c_val)
        # concat(S1,S2) -> circle
        c_val2 = int(f"{s1}{s2}")
        while c_val2 > 50: c_val2 -= 25
        if 1 <= c_val2 <= 50: star_p3_vals.append(c_val2)
        # rev(S1+S2) (3.8%)
        rv = int(str(s1 + s2)[::-1])
        if rv > 50: rv -= 25
        if 1 <= rv <= 50: star_p3_vals.append(rv)
        # S1+S2+25 (2.8%)
        sc = s1 + s2 + 25
        if sc > 50: sc -= 25
        if 1 <= sc <= 50: star_p3_vals.append(sc)
        # S2+25
        s2c = s2 + 25
        if 1 <= s2c <= 50: star_p3_vals.append(s2c)
    except:
        pass
    
    for sp3 in star_p3_vals:
        candidates[2].extend([sp3] * 5)  # P3 focus
        candidates[1].extend([sp3] * 2)
        candidates[3].extend([sp3] * 2)
    if star_p3_vals:
        patterns_used.append(f"Star->P3 Dance: {star_p3_vals[:4]}")
    
    # ═══════════════════════════════════════════════════════════════════
    # REVERSE TWIN GENERATOR (P1 pattern - new!)
    # If N appeared, reverse(N) is calling!
    # ═══════════════════════════════════════════════════════════════════
    rev_twin_result = pattern_flip_twin(prev_draw)
    for num, weight, reason in rev_twin_result.get('candidates', []):
        if 1 <= num <= 50:
            for pos in range(5):
                candidates[pos].extend([num] * (weight // 10))
    for exp in rev_twin_result.get('explanations', [])[:3]:
        patterns_used.append(exp)
    
    # ═══════════════════════════════════════════════════════════════════
    # DAY x MONTH - 10 (P1 pattern - new!)
    # Esoteric formula: Day * Month - 10 = candidate
    # ═══════════════════════════════════════════════════════════════════
    if target_date:
        dm10_result = pattern_day_times_month_minus_10(target_date)
        for num, weight, reason in dm10_result.get('candidates', []):
            if 1 <= num <= 50:
                for pos in range(5):
                    candidates[pos].extend([num] * (weight // 10))
        for exp in dm10_result.get('explanations', [])[:2]:
            patterns_used.append(exp)
    
    # DRAW-TO-DRAW LEARNING (DJ Engine)
    if len(draws) >= 3:
        from collections import Counter as C2
        rc = C2()
        for d in draws[:5]:
            for n in d['numbers']:
                rc[n] += 1
        for hn in [n for n, c in rc.items() if c >= 2]:
            for pos in range(5):
                candidates[pos].extend([hn] * 2)
        
        # Cold sleeper circle boost
        recent_all = set()
        for d in draws[:8]:
            recent_all.update(d['numbers'])
        for cn in range(1, 51):
            if cn not in recent_all:
                cp = cn + 25 if cn + 25 <= 50 else cn - 25
                if cp in recent_all and 1 <= cp <= 50:
                    for pos in range(5):
                        candidates[pos].append(cn)
        
        # Star momentum
        rs = C2()
        for d in draws[:3]:
            for s in d.get('stars', []):
                rs[s] += 1
        for hs in [s for s, c in rs.items() if c >= 2 and 1 <= s <= 12]:
            star_candidates.extend([hs] * 3)
        for cs in range(1, 13):
            ars = set()
            for d in draws[:5]:
                ars.update(d.get('stars', []))
            if cs not in ars:
                star_candidates.append(cs)
    
    # ═══════════════════════════════════════════════════════════════════
    # 🍀 CROSS-LOTTERY PATTERNS (Swiss → Euro) - NEW! 🍀
    # The lotteries talk to each other through TIME and DATE!
    # ═══════════════════════════════════════════════════════════════════
    # Check for swiss_draws from parameter OR function attribute
    available_swiss = swiss_draws
    if not available_swiss and hasattr(dj_generate_candidates, 'swiss_draws'):
        available_swiss = dj_generate_candidates.swiss_draws
    
    if target_date and available_swiss:
        # Find Swiss draw 1-14 days before target Euro date
        try:
            euro_dt = parse_draw_date(target_date)
            
            for swiss in available_swiss[:5]:  # Check last 5 Swiss
                swiss_dt = parse_draw_date(swiss['date'])
                days_diff = (euro_dt - swiss_dt).days
                
                if 1 <= days_diff <= 14:
                    cross_cands = cross_lottery_swiss_to_euro(swiss, swiss['date'], target_date)
                    
                    # SwissDay + EuroMonth (13.3% hit rate!)
                    if 'swiss_day_month' in cross_cands:
                        for n in cross_cands['swiss_day_month']:
                            for pos in range(5):
                                candidates[pos].extend([n] * WEIGHTS.get("cross_swiss_day_month", 8))
                        patterns_used.append(f"🍀 Swiss→Euro: SwissDay({swiss_dt.day})+EuroMonth({euro_dt.month})={cross_cands['swiss_day_month'][0]} (13.3%)")
                    
                    # Lucky × EuroMonth (13.3% hit rate!)
                    if 'lucky_mult' in cross_cands:
                        for n in cross_cands['lucky_mult']:
                            for pos in range(5):
                                candidates[pos].extend([n] * WEIGHTS.get("cross_lucky_mult", 8))
                        patterns_used.append(f"🍀 Swiss→Euro: Lucky({swiss.get('lucky_number')})×EuroMonth({euro_dt.month})={cross_cands['lucky_mult'][0]} (13.3%)")
                    
                    # Swiss - DaysDiff (11.1% hit rate!)
                    if 'swiss_minus_days' in cross_cands:
                        for n in cross_cands['swiss_minus_days']:
                            for pos in range(5):
                                candidates[pos].extend([n] * WEIGHTS.get("cross_swiss_minus_days", 6))
                        patterns_used.append(f"🍀 Swiss→Euro: Swiss-{days_diff}d → {cross_cands['swiss_minus_days'][:3]} (11.1%)")
                    
                    # Swiss Direct Echo (10%)
                    if 'swiss_direct' in cross_cands:
                        for n in cross_cands['swiss_direct']:
                            for pos in range(5):
                                candidates[pos].extend([n] * WEIGHTS.get("cross_swiss_direct", 4))
                        patterns_used.append(f"🍀 Swiss→Euro: Direct echo {cross_cands['swiss_direct'][:3]}")
                    
                    # Lucky → Star (16.7%!)
                    if 'lucky_star' in cross_cands:
                        for s in cross_cands['lucky_star']:
                            star_candidates.extend([s] * WEIGHTS.get("cross_lucky_star", 8))
                        patterns_used.append(f"🍀⭐ Swiss→Euro: Lucky 🍀{swiss.get('lucky_number')} → Star ⭐{cross_cands['lucky_star'][0]} (16.7%)")
                    
                    break  # Use only the closest Swiss draw
        except Exception as e:
            patterns_used.append(f"🍀 Cross-lottery error: {str(e)}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 🇨🇭 SWISS P1 → EURO P1 BRIDGE (3.48x random!)
    # Last 3 Swiss P1 positions predict Euro P1 and general numbers
    # ═══════════════════════════════════════════════════════════════════
    if available_swiss and len(available_swiss) >= 3:
        bridge = swiss_p1_bridge(available_swiss)
        
        # P1 candidates get HEAVY boost at position 0 (P1)
        for num, weight, reason in bridge.get('p1_candidates', []):
            if 1 <= num <= 50:
                candidates[0].extend([num] * weight)  # P1 position only!
                candidates[1].extend([num] * (weight // 3))  # Light P2 backup
        
        # General candidates (the 3x SET) get spread across all positions
        for num, weight, reason in bridge.get('general_candidates', []):
            if 1 <= num <= 50:
                for pos in range(5):
                    candidates[pos].extend([num] * (weight // 2))
        
        for exp in bridge.get('explanations', []):
            patterns_used.append(f"🇨🇭 {exp}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 💤 SLEEPER WAKE ALARM - Numbers about to snap back! 💤
    # PROVEN: 88% wake within 20 draws, 72% get teased first!
    # Stars at 1.8x random, tease-hot picks outperform!
    # ═══════════════════════════════════════════════════════════════════
    try:
        from sleeper_engine import detect_sleepers
        
        # Detect number sleepers
        num_sleepers = detect_sleepers(draws, num_range=50, is_stars=False, tease_window=3)
        
        sleeper_weight_map = {
            'tease_hot': 10,      # Heavy teasing = about to wake
            'sweet_spot': 8,      # 1.0-1.5x overdue = 51.2% fast wake
            'snap_back': 6,       # 3x+ overdue = snap-back territory
            'circle_pump': 5,     # Circle partner pumping
        }
        
        sleeper_nums_added = []
        for s in num_sleepers[:12]:  # Top 12 sleeper candidates
            w = 0
            label = ""
            
            if s.tease_score >= 3 and s.overdue >= 0.7:
                w = sleeper_weight_map['tease_hot']
                label = "TEASE-HOT"
            elif 1.0 <= s.overdue <= 1.5 and s.tease_score >= 1:
                w = sleeper_weight_map['sweet_spot']
                label = "SWEET"
            elif s.overdue >= 3.0:
                w = sleeper_weight_map['snap_back']
                label = "SNAP"
            elif s.circ_boost >= 1.5 and s.tease_score >= 1:
                w = sleeper_weight_map['circle_pump']
                label = "CIRC"
            elif s.tease_score >= 2:
                w = 4
                label = "TEASE"
            
            if w > 0:
                for pos in range(5):
                    candidates[pos].extend([s.num] * w)
                sleeper_nums_added.append((s.num, label, s.overdue, s.tease_score))
        
        if sleeper_nums_added:
            top3 = sleeper_nums_added[:3]
            patterns_used.append(
                "💤 SLEEPER ALARM: " + ", ".join(
                    ["%d[%s %.1fx t%.0f]" % (n, l, o, t) for n, l, o, t in top3]
                )
            )
        
        # Detect star sleepers
        star_sleepers = detect_sleepers(draws, num_range=12, is_stars=True, tease_window=3)
        
        star_sleeper_added = []
        for s in star_sleepers[:4]:
            w = 0
            if s.tease_score >= 2:
                w = 6
            elif s.overdue >= 1.5:
                w = 5
            elif s.overdue >= 1.0 and s.tease_score >= 1:
                w = 4
            
            if w > 0:
                star_candidates.extend([s.num] * w)
                star_sleeper_added.append(s.num)
        
        if star_sleeper_added:
            patterns_used.append("💤⭐ STAR SLEEPERS: %s" % star_sleeper_added)
    
    except Exception as e:
        patterns_used.append("💤 Sleeper engine skipped: %s" % str(e))
    
    return {
        "candidates": candidates,
        "star_candidates": star_candidates,
        "patterns": patterns_used,
        "prev_nums": prev_nums,
        "prev_stars": prev_stars,
    }


def pattern_p2_prince(target_date: str, prev_draw: Dict, prev2_draw: Dict = None) -> Dict:
    """
    👑 P2 PRINCE PATTERN - The music that predicts P2! 👑
    
    TOP P2 GENERATORS (backtested hit rates):
    1. prev P2 + 1 = P2 (6.0%)
    2. prev P3 last digit + 10 = P2 (6.0%)
    3. Day direct = P2 (4.7%)
    4. prev P2 + Day digit = P2 (4.7%)
    5. Day - Month = P2 (4.2%)
    6. D1+D2 last digit family = P2 (4.0%)
    7. prev P2 echo = P2 (4.0%)
    8. prev S2 + prev P1 = P2 (4.0%)
    
    P2 typically ranges from 8-25 (average ~18)
    """
    candidates = []
    explanations = []
    
    # Parse dates
    day = int(target_date.split('.')[0])
    month = int(target_date.split('.')[1])
    
    prev_nums = sorted(prev_draw['numbers'])
    prev_p1, prev_p2, prev_p3 = prev_nums[0], prev_nums[1], prev_nums[2]
    prev_stars = sorted(prev_draw['stars'])
    prev_s1, prev_s2 = prev_stars[0], prev_stars[1]
    
    prev_day = int(prev_draw['date'].split('.')[0])
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🥇 #1: PREV P2 + 1 (6.0% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    p2_plus1 = prev_p2 + 1
    if 5 <= p2_plus1 <= 35:  # P2 range
        candidates.append((p2_plus1, 50, f"P2+1: {prev_p2}+1={p2_plus1}"))
        explanations.append(f"👑 P2+1: {prev_p2}+1={p2_plus1} (6.0%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🥇 #2: PREV P3 LAST DIGIT + 10 (6.0% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    p3_last = prev_p3 % 10
    if p3_last > 0:
        p3_family_10 = p3_last + 10
        p3_family_20 = p3_last + 20
        if 5 <= p3_family_10 <= 35:
            candidates.append((p3_family_10, 50, f"P3 last+10: {prev_p3}→{p3_last}+10={p3_family_10}"))
        if 5 <= p3_family_20 <= 35:
            candidates.append((p3_family_20, 45, f"P3 last+20: {prev_p3}→{p3_last}+20={p3_family_20}"))
        explanations.append(f"👑 P3 digit: {prev_p3}→{p3_last} +10/20 (6.0%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🥉 #3: DAY DIRECT (4.7% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    if 5 <= day <= 31:
        candidates.append((day, 40, f"Day direct: {day}"))
        explanations.append(f"👑 Day direct: {day} (4.7%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # #4: PREV P2 + DAY DIGIT (4.7% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    day_digit = int(str(day)[0])
    p2_day_digit = prev_p2 + day_digit
    if 5 <= p2_day_digit <= 35:
        candidates.append((p2_day_digit, 40, f"P2+digit(D): {prev_p2}+{day_digit}={p2_day_digit}"))
        explanations.append(f"👑 P2+digit: {prev_p2}+{day_digit}={p2_day_digit} (4.7%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # #5: DAY - MONTH (4.2% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    if day > month:
        dm_diff = day - month
        if 5 <= dm_diff <= 35:
            candidates.append((dm_diff, 38, f"D-M: {day}-{month}={dm_diff}"))
            explanations.append(f"👑 D-M: {day}-{month}={dm_diff} (4.2%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # #6: D1+D2 LAST DIGIT FAMILY (4.0% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    d_sum = day + prev_day
    d_last = d_sum % 10
    if d_last > 0:
        d_family_10 = d_last + 10
        d_family_20 = d_last + 20
        if 5 <= d_family_10 <= 35:
            candidates.append((d_family_10, 35, f"D1+D2 last+10: {d_sum}→{d_last}+10={d_family_10}"))
        if 5 <= d_family_20 <= 35:
            candidates.append((d_family_20, 32, f"D1+D2 last+20: {d_sum}→{d_last}+20={d_family_20}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # #7: PREV P2 ECHO (4.0% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    if 5 <= prev_p2 <= 35:
        candidates.append((prev_p2, 35, f"P2 echo: {prev_p2}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # #8: PREV S2 + PREV P1 (4.0% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    s2_p1 = prev_s2 + prev_p1
    if 5 <= s2_p1 <= 35:
        candidates.append((s2_p1, 35, f"S2+P1: {prev_s2}+{prev_p1}={s2_p1}"))
        explanations.append(f"👑 S2+P1: {prev_s2}+{prev_p1}={s2_p1} (4.0%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # #9: PREV P2 - 1 (3.4% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    p2_minus1 = prev_p2 - 1
    if 5 <= p2_minus1 <= 35:
        candidates.append((p2_minus1, 30, f"P2-1: {prev_p2}-1={p2_minus1}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # #10: DAY + PREV P1 (3.4% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    day_p1 = day + prev_p1
    if 5 <= day_p1 <= 35:
        candidates.append((day_p1, 30, f"Day+P1: {day}+{prev_p1}={day_p1}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # #11: MONTH + PREV P2 (3.4% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    month_p2 = month + prev_p2
    if 5 <= month_p2 <= 35:
        candidates.append((month_p2, 30, f"M+P2: {month}+{prev_p2}={month_p2}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # #12: (S1+S2) + DAY DIGIT (3.4% hit rate!)
    # ═══════════════════════════════════════════════════════════════════════
    s_sum_day = prev_s1 + prev_s2 + day_digit
    if 5 <= s_sum_day <= 35:
        candidates.append((s_sum_day, 28, f"(S1+S2)+digit: {prev_s1}+{prev_s2}+{day_digit}={s_sum_day}"))
    
    # Determine top P2 candidate
    top_p2 = p2_plus1 if 5 <= p2_plus1 <= 35 else (p3_family_10 if p3_last > 0 and 5 <= p3_family_10 <= 35 else day)
    
    return {
        'candidates': candidates,
        'explanations': explanations,
        'top_p2': top_p2
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 🎧 NEW PATTERNS FROM THE DJ SESSION - April 2026 🎻
# P1-1, P2-6, Circle P3, Twin Bridges, Chain Patterns
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_p1_minus_1(prev_draw: Dict) -> Dict:
    """
    🎵 P1-1 PATTERN - 8.5% hit rate!
    Previous P1 minus 1 appears in next draw.
    """
    prev_nums = sorted(prev_draw['numbers'])
    p1 = prev_nums[0]
    p1_minus_1 = p1 - 1
    
    if 1 <= p1_minus_1 <= 50:
        return {
            'candidate': p1_minus_1,
            'weight': 40,
            'explanation': f"🎵 P1-1: {p1}-1={p1_minus_1} (8.5%)"
        }
    return {'candidate': None, 'weight': 0, 'explanation': ''}


def pattern_p2_minus_6(prev_draw: Dict) -> Dict:
    """
    🎵 P2-6 PATTERN - 8.1% hit rate!
    Previous P2 minus 6 appears in next draw.
    Example: 24.03 P2=16 → 16-6=10 → 10 appears on 27.03!
    """
    prev_nums = sorted(prev_draw['numbers'])
    p2 = prev_nums[1]
    p2_minus_6 = p2 - 6
    
    if 1 <= p2_minus_6 <= 50:
        return {
            'candidate': p2_minus_6,
            'weight': 40,
            'explanation': f"🎵 P2-6: {p2}-6={p2_minus_6} (8.1%)"
        }
    return {'candidate': None, 'weight': 0, 'explanation': ''}


def pattern_circle_p3(prev_draw: Dict) -> Dict:
    """
    🎵 CIRCLE P3 PATTERN - 10.2% hit rate!
    Circle of P3 appears in next draw.
    """
    prev_nums = sorted(prev_draw['numbers'])
    p3 = prev_nums[2]
    circle_p3 = p3 + 25 if p3 <= 25 else p3 - 25
    
    # Also get digit sum of circle
    digit_sum = sum(int(d) for d in str(circle_p3))
    
    return {
        'candidate': circle_p3,
        'digit_sum': digit_sum,
        'weight': 45,
        'explanation': f"🎵 circle(P3): circle({p3})={circle_p3}, digits={digit_sum} (10.2%)"
    }


def pattern_twin_bridges(prev_draw: Dict) -> Dict:
    """
    🎵 TWIN BRIDGE PATTERNS 🎵
    
    Discovered pairs that call each other:
    - 12 ↔ 13: consecutive twins (7.4%)
    - 26 ↔ 31: +5 twins (13.9%)
    - 22 ↔ 28: +6 twins (8.6%)
    - 15 ↔ 40: CIRCLE TWINS! circle(15)=40 (2.4%)
    - 14 ↔ 16: ±2 twins (22.4%)
    """
    prev_nums = sorted(prev_draw['numbers'])
    candidates = []
    explanations = []
    
    # Define twin pairs and their weights
    twin_pairs = {
        12: [(13, 35, "+1 twin")],
        13: [(12, 35, "-1 twin")],
        26: [(31, 50, "+5 twin")],
        31: [(26, 50, "-5 twin")],
        22: [(28, 40, "+6 twin")],
        28: [(22, 40, "-6 twin")],
        15: [(40, 30, "circle twin")],
        40: [(15, 30, "circle twin")],
    }
    
    # ±2 twins for any P2 (22.4% hit rate!)
    p2 = prev_nums[1]
    if p2 + 2 <= 50:
        candidates.append((p2 + 2, 55, f"P2+2 twin: {p2}+2={p2+2}"))
    if p2 - 2 >= 1:
        candidates.append((p2 - 2, 55, f"P2-2 twin: {p2}-2={p2-2}"))
    explanations.append(f"🎵 ±2 Twin: P2={p2} → {p2-2}, {p2+2} (22.4%)")
    
    # Check if any twin pairs are in previous draw
    for num in prev_nums:
        if num in twin_pairs:
            for twin, weight, desc in twin_pairs[num]:
                candidates.append((twin, weight, f"{num}→{twin} ({desc})"))
                explanations.append(f"🎵 Twin Bridge: {num}→{twin} ({desc})")
    
    return {
        'candidates': candidates,
        'explanations': explanations
    }


def pattern_consecutive_trio_minus_digit(prev_draw: Dict) -> Dict:
    """
    🔥 CONSECUTIVE TRIO → MINUS DIGIT PATTERN 🔥
    
    When 3 consecutive numbers appear (16-17-18):
    - 16-6=10, 17-7=10, 18-8=10 → ALL = 10!
    - That 10 appears in next draw!
    
    50% hit rate when trio found!
    """
    prev_nums = sorted(prev_draw['numbers'])
    
    # Find consecutive trio
    for i in range(len(prev_nums) - 2):
        if prev_nums[i+1] == prev_nums[i] + 1 and prev_nums[i+2] == prev_nums[i] + 2:
            trio = (prev_nums[i], prev_nums[i+1], prev_nums[i+2])
            
            # Calculate minus-digit value
            # 16-6=10, 17-7=10, 18-8=10 → all point to same!
            first = trio[0]
            minus_digit = first - (first % 10) if first >= 10 else first
            if minus_digit == 0:
                minus_digit = 10
            
            return {
                'trio': trio,
                'prediction': minus_digit,
                'weight': 60,
                'explanation': f"🔥 TRIO {trio} → all minus digit = {minus_digit} (50%!)"
            }
    
    return {'trio': None, 'prediction': None, 'weight': 0, 'explanation': ''}


def pattern_circle_bridge_35(prev_draw: Dict, prev2_draw: Dict = None) -> Dict:
    """
    🔥 THE 35 CIRCLE BRIDGE PATTERN 🔥
    
    When 10 appears:
    - circle(10) = 35 (THE MASTER KEY!)
    - 35 - 27 = 8 (8 appears next!)
    - 35 - 8 = 27 (27 appears after!)
    - 3 + 5 = 8 (digit sum also works!)
    
    The 35 PREDICTS MULTIPLE draws ahead!
    """
    prev_nums = sorted(prev_draw['numbers'])
    candidates = []
    explanations = []
    
    for num in prev_nums:
        circle_num = num + 25 if num <= 25 else num - 25
        
        # If circle is around 35 range
        if 30 <= circle_num <= 40:
            # Digit sum
            digit_sum = sum(int(d) for d in str(circle_num))
            if 1 <= digit_sum <= 50:
                candidates.append((digit_sum, 45, f"circle({num})={circle_num} → digits={digit_sum}"))
            
            # Minus 27 (the traveler)
            minus_27 = circle_num - 27
            if 1 <= minus_27 <= 50:
                candidates.append((minus_27, 40, f"circle({num})={circle_num} - 27 = {minus_27}"))
            
            # Minus 25 (circle back)
            minus_25 = circle_num - 25
            if 1 <= minus_25 <= 50:
                candidates.append((minus_25, 35, f"circle({num})={circle_num} - 25 = {minus_25}"))
            
            explanations.append(f"🔥 Circle Bridge: {num}→{circle_num} (Master Key!)")
    
    # Special case: if prev P2 and this creates a chain
    prev_p2 = prev_nums[1]
    if prev2_draw:
        prev2_nums = sorted(prev2_draw['numbers'])
        prev2_p2 = prev2_nums[1]
        
        # Check if we can do: circle(prev2_P2) - prev_P2 = next candidate
        circle_prev2_p2 = prev2_p2 + 25 if prev2_p2 <= 25 else prev2_p2 - 25
        chain_pred = abs(circle_prev2_p2 - prev_p2)
        if 1 <= chain_pred <= 50:
            candidates.append((chain_pred, 35, f"Chain: circle({prev2_p2})-{prev_p2}={chain_pred}"))
    
    return {
        'candidates': candidates,
        'explanations': explanations
    }


def pattern_p2_chain_22_28_15_40_29() -> Dict:
    """
    🎵 THE CHAIN: 22 → 28 → 15 → 40 → 29 🎵
    
    Discovered chain pattern:
    - 22 + 6 = 28 ✅
    - 28 - 13 = 15 ✅
    - 15 + 25 = 40 (CIRCLE!) ✅
    - 40 - 11 = 29 ✅
    
    15 and 40 are CIRCLE TWINS!
    """
    # This is a static chain - these numbers call each other
    chain = [22, 28, 15, 40, 29]
    
    return {
        'chain': chain,
        'circle_twins': [(15, 40), (40, 15)],
        'explanation': "🎵 The Chain: 22↔28↔15↔40↔29"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 🎧 NEW PATTERNS FROM BACKTEST - September 2025 Session 🎻
# Star Multiplication, P4+P5 Digit, Month×2, Day÷2
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_star_diff_to_star(prev_draw: Dict) -> Dict:
    """
    ⭐ STAR DIFF → NEXT STAR (17.4% hit rate!) 🔥🔥
    |S2 - S1| becomes a star in the next draw.
    """
    prev_stars = sorted(prev_draw['stars'])
    s_diff = abs(prev_stars[1] - prev_stars[0])
    
    if 1 <= s_diff <= 12:
        return {
            'candidate': s_diff,
            'weight': 60,  # High weight - 17.4%!
            'explanation': f"⭐ |S2-S1|: |{prev_stars[1]}-{prev_stars[0]}|={s_diff} → Star (17.4%)"
        }
    return {'candidate': None, 'weight': 0, 'explanation': ''}


def pattern_star_times_2(prev_draw: Dict) -> Dict:
    """
    ⭐ S1 × 2 → NEXT STAR (16.1% hit rate!) 🔥🔥
    S1 doubled becomes a star in the next draw.
    Example: S1=6 → 6×2=12 → Star 12 appears!
    """
    prev_stars = sorted(prev_draw['stars'])
    s1_x2 = prev_stars[0] * 2
    
    candidates = []
    explanations = []
    
    if 1 <= s1_x2 <= 12:
        candidates.append((s1_x2, 55, f"S1×2: {prev_stars[0]}×2={s1_x2}"))
        explanations.append(f"⭐ S1×2: {prev_stars[0]}×2={s1_x2} → Star (16.1%)")
    
    # Also add S1+S2 → Star (8.7%)
    s_sum = prev_stars[0] + prev_stars[1]
    if 1 <= s_sum <= 12:
        candidates.append((s_sum, 40, f"S1+S2: {prev_stars[0]}+{prev_stars[1]}={s_sum}"))
        explanations.append(f"⭐ S1+S2: {prev_stars[0]}+{prev_stars[1]}={s_sum} → Star (8.7%)")
    
    return {
        'candidates': candidates,
        'explanations': explanations
    }


def pattern_p4_p5_digit(prev_draw: Dict) -> Dict:
    """
    🎵 P4+P5 FIRST DIGIT → NEXT NUMBER (12.8% hit rate!) 🔥
    The first digit of (P4 + P5) appears in the next draw.
    Example: P4=35, P5=40 → 35+40=75 → first digit 7 appears!
    """
    prev_nums = sorted(prev_draw['numbers'])
    p4, p5 = prev_nums[3], prev_nums[4]
    
    p4_p5_sum = p4 + p5
    first_digit = int(str(p4_p5_sum)[0])
    
    if 1 <= first_digit <= 50:
        return {
            'candidate': first_digit,
            'weight': 50,  # Good weight - 12.8%!
            'explanation': f"🎵 P4+P5: {p4}+{p5}={p4_p5_sum} → digit {first_digit} (12.8%)"
        }
    return {'candidate': None, 'weight': 0, 'explanation': ''}


def pattern_month_times_2(target_date: str) -> Dict:
    """
    🎵 MONTH × 2 → NEXT NUMBER (10.7% hit rate!) 🔥
    The month doubled appears in the draw.
    Example: April (4) → 4×2=8 → 8 appears!
    """
    month = int(target_date.split('.')[1])
    m_x2 = month * 2
    
    if 1 <= m_x2 <= 50:
        return {
            'candidate': m_x2,
            'weight': 45,
            'explanation': f"🎵 M×2: {month}×2={m_x2} (10.7%)"
        }
    return {'candidate': None, 'weight': 0, 'explanation': ''}


def pattern_day_div_2(target_date: str) -> Dict:
    """
    🎵 DAY ÷ 2 → NEXT NUMBER (8.3% hit rate!) 🔥
    Even days divided by 2 appear in the draw.
    Example: Day 24 → 24÷2=12 → 12 appears!
    """
    day = int(target_date.split('.')[0])
    
    if day % 2 == 0:  # Only even days
        d_div = day // 2
        if 1 <= d_div <= 50:
            return {
                'candidate': d_div,
                'weight': 40,
                'explanation': f"🎵 D÷2: {day}÷2={d_div} (8.3%)"
            }
    return {'candidate': None, 'weight': 0, 'explanation': ''}


# ═══════════════════════════════════════════════════════════════════════════════
# 🎧 TUNED PATTERNS - May 2025 Session (09.05.2025 Analysis) 🎻
# P2-5, P5 Echo, P4-1, P5-1, Day=Star, P3+1
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_p2_minus_family(prev_draw: Dict) -> Dict:
    """
    🎵 P2 MINUS FAMILY (P2-3, P2-4, P2-5) - 8-9% hit rate each! 🔥
    Previous P2 minus 3/4/5 appears in next draw.
    We already have P2-6 (8.1%), now adding the family!
    """
    prev_nums = sorted(prev_draw['numbers'])
    p2 = prev_nums[1]
    
    candidates = []
    explanations = []
    
    # P2 - 5 (8.1%)
    p2_m5 = p2 - 5
    if 1 <= p2_m5 <= 50:
        candidates.append((p2_m5, 40, f"P2-5: {p2}-5={p2_m5}"))
    
    # P2 - 4 (9.4%)
    p2_m4 = p2 - 4
    if 1 <= p2_m4 <= 50:
        candidates.append((p2_m4, 42, f"P2-4: {p2}-4={p2_m4}"))
    
    # P2 - 3 (8.1%)
    p2_m3 = p2 - 3
    if 1 <= p2_m3 <= 50:
        candidates.append((p2_m3, 40, f"P2-3: {p2}-3={p2_m3}"))
    
    if candidates:
        explanations.append(f"🎵 P2 Family: {p2}-3={p2_m3}, -4={p2_m4}, -5={p2_m5}")
    
    return {
        'candidates': candidates,
        'explanations': explanations
    }


def pattern_p5_echo_and_minus(prev_draw: Dict) -> Dict:
    """
    🔥 P5 ECHO & P5-1 PATTERN 🔥
    P5 ECHO: 14.8% hit rate! (Previous P5 appears again!)
    P5 - 1: 11.4% hit rate! (P5 minus 1 appears!)
    
    Example: P5=48 → 48 echoes OR 47 appears!
    """
    prev_nums = sorted(prev_draw['numbers'])
    p5 = prev_nums[4]
    
    candidates = []
    explanations = []
    
    # P5 ECHO (14.8%) - STRONG!
    candidates.append((p5, 55, f"P5 ECHO: {p5}"))
    explanations.append(f"🔥 P5 ECHO: {p5} (14.8%)")
    
    # P5 - 1 (11.4%)
    p5_m1 = p5 - 1
    if 1 <= p5_m1 <= 50:
        candidates.append((p5_m1, 48, f"P5-1: {p5}-1={p5_m1}"))
        explanations.append(f"🔥 P5-1: {p5}-1={p5_m1} (11.4%)")
    
    return {
        'candidates': candidates,
        'explanations': explanations
    }


def pattern_p4_echo_and_family(prev_draw: Dict) -> Dict:
    """
    🎵 P4 ECHO & FAMILY (P4-1, P4+1) 🎵
    P4 ECHO: 8.1% hit rate!
    P4 - 1: 10.7% hit rate!
    P4 + 1: 8.1% hit rate!
    """
    prev_nums = sorted(prev_draw['numbers'])
    p4 = prev_nums[3]
    
    candidates = []
    explanations = []
    
    # P4 ECHO (8.1%)
    candidates.append((p4, 40, f"P4 ECHO: {p4}"))
    
    # P4 - 1 (10.7%) - Stronger!
    p4_m1 = p4 - 1
    if 1 <= p4_m1 <= 50:
        candidates.append((p4_m1, 45, f"P4-1: {p4}-1={p4_m1}"))
    
    # P4 + 1 (8.1%)
    p4_p1 = p4 + 1
    if 1 <= p4_p1 <= 50:
        candidates.append((p4_p1, 40, f"P4+1: {p4}+1={p4_p1}"))
    
    explanations.append(f"🎵 P4 Family: {p4} echo, {p4_m1}, {p4_p1}")
    
    return {
        'candidates': candidates,
        'explanations': explanations
    }


def pattern_p3_plus_1(prev_draw: Dict) -> Dict:
    """
    🎵 P3 + 1 PATTERN (9.4% hit rate!) 🔥
    Previous P3 plus 1 appears in next draw.
    Example: P3=24 → 25 appears!
    """
    prev_nums = sorted(prev_draw['numbers'])
    p3 = prev_nums[2]
    p3_p1 = p3 + 1
    
    if 1 <= p3_p1 <= 50:
        return {
            'candidate': p3_p1,
            'weight': 42,
            'explanation': f"🎵 P3+1: {p3}+1={p3_p1} (9.4%)"
        }
    return {'candidate': None, 'weight': 0, 'explanation': ''}


def pattern_day_equals_star(target_date: str) -> Dict:
    """
    ⭐ DAY = STAR PATTERN (17.2% hit rate!) 🔥🔥
    When Day ≤ 12, the day number becomes a star!
    Example: Day 9 → Star 9 appears!
    """
    day = int(target_date.split('.')[0])
    
    if 1 <= day <= 12:
        return {
            'candidate': day,
            'weight': 60,  # High weight - 17.2%!
            'explanation': f"⭐ Day=Star: Day {day} → Star {day} (17.2%)"
        }
    return {'candidate': None, 'weight': 0, 'explanation': ''}


# ═══════════════════════════════════════════════════════════════════════════════
# NEW P1 PATTERNS - April 2026 Session (Fork 3)
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_flip_twin(prev_draw: Dict) -> Dict:
    """
    FLIP TWIN GENERATOR
    If N appears, flip(N) is calling!
    14 → 41, 28 → 82 → 32, single digits expand: 4 → 40
    """
    prev_nums = sorted(prev_draw['numbers'])
    candidates = []
    explanations = []
    
    for n in prev_nums:
        if n >= 10:
            # Direct flip
            rev = int(str(n)[::-1])
            if rev > 50:
                rev_mod = rev - 50 if rev <= 100 else rev % 50
                if rev_mod == 0:
                    rev_mod = 50
                if 1 <= rev_mod <= 50 and rev_mod != n and rev_mod not in prev_nums:
                    candidates.append((rev_mod, 40, f"flip({n})→{rev}→{rev_mod}"))
                    explanations.append(f"FLIP TWIN: {n} → flip={rev} → {rev_mod}")
            elif 1 <= rev <= 50 and rev != n and rev not in prev_nums:
                candidates.append((rev, 50, f"flip({n})={rev}"))
                explanations.append(f"FLIP TWIN: {n} → {rev}")
        else:
            # Single digit: 4 → 40 (digit flips position)
            expanded = n * 10
            if 1 <= expanded <= 50 and expanded not in prev_nums:
                candidates.append((expanded, 30, f"flip({n})={expanded}"))
                explanations.append(f"FLIP TWIN: {n} → {expanded}")
    
    return {
        'candidates': candidates,
        'explanations': explanations
    }


def pattern_day_times_month_minus_10(target_date: str) -> Dict:
    """
    DAY x MONTH - 10 PATTERN
    Esoteric formula: Day * Month - 10 = candidate number
    Example: 15 * 4 - 10 = 50, 7 * 4 - 10 = 18
    Also adds Day * Month direct if in range
    """
    try:
        day = int(target_date.split('.')[0])
        month = int(target_date.split('.')[1])
        
        candidates = []
        explanations = []
        
        product = day * month
        minus_10 = product - 10
        
        if 1 <= minus_10 <= 50:
            candidates.append((minus_10, 45, f"D*M-10: {day}*{month}-10={minus_10}"))
            explanations.append(f"DAY*MONTH-10: {day}x{month}={product} - 10 = {minus_10}")
        
        # Also the product itself if in range
        if 1 <= product <= 50 and product != minus_10:
            candidates.append((product, 30, f"D*M: {day}*{month}={product}"))
            explanations.append(f"DAY*MONTH: {day}x{month} = {product}")
        
        # And product + 10 for the inverse
        plus_10 = product + 10
        if 1 <= plus_10 <= 50 and plus_10 != minus_10 and plus_10 != product:
            candidates.append((plus_10, 20, f"D*M+10: {day}*{month}+10={plus_10}"))
        
        # Circle of the result
        if 1 <= minus_10 <= 50:
            circ = minus_10 + 25 if minus_10 <= 25 else minus_10 - 25
            if 1 <= circ <= 50 and circ != minus_10:
                candidates.append((circ, 25, f"circle(D*M-10): circle({minus_10})={circ}"))
                explanations.append(f"CIRCLE(D*M-10): circle({minus_10}) = {circ}")
        
        return {
            'candidates': candidates,
            'explanations': explanations,
            'product': product,
            'minus_10': minus_10
        }
    except:
        return {'candidates': [], 'explanations': [], 'product': 0, 'minus_10': 0}


def pattern_p1_king(target_date: str, prev_draw: Dict, prev2_draw: Dict = None) -> Dict:
    """
    👑 P1 KING PATTERN - The music that predicts P1! 👑
    
    TOP P1 GENERATORS (backtested hit rates):
    1. D1+D2 first digit (DAY DANCE!) - 9.4%
    2. Day + prev_P1 digit - 8.1%
    3. Gap P2-P1 - 7.4%
    4. P1+P2 first digit - 6.7%
    5. P1+P2+P3 digit sum - 6.0%
    6. P2/P3 last digit - 5.4%
    7. Day × Month first digit - 5.4%
    """
    candidates = []
    explanations = []
    
    # Parse dates
    day = int(target_date.split('.')[0])
    month = int(target_date.split('.')[1])
    
    prev_nums = sorted(prev_draw['numbers'])
    prev_p1, prev_p2, prev_p3 = prev_nums[0], prev_nums[1], prev_nums[2]
    
    prev_day = int(prev_draw['date'].split('.')[0])
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🥇 #1: D1+D2 FIRST DIGIT (DAY DANCE!) - 9.4% hit rate!
    # ═══════════════════════════════════════════════════════════════════════
    d_sum = day + prev_day
    d_first = int(str(d_sum)[0]) if d_sum >= 10 else d_sum
    if 1 <= d_first <= 15:  # P1 range
        candidates.append((d_first, 50, f"DAY DANCE: D1+D2={day}+{prev_day}={d_sum} → digit {d_first}"))
        explanations.append(f"👑 DAY DANCE: {day}+{prev_day}={d_sum} → P1={d_first} (9.4%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🥈 #2: DAY + PREV_P1 DIGIT - 8.1% hit rate!
    # ═══════════════════════════════════════════════════════════════════════
    day_p1_sum = day + prev_p1
    day_p1_digit = int(str(day_p1_sum)[0]) if day_p1_sum >= 10 else day_p1_sum
    if 1 <= day_p1_digit <= 15 and day_p1_digit != d_first:
        candidates.append((day_p1_digit, 45, f"DAY+P1: {day}+{prev_p1}={day_p1_sum} → digit {day_p1_digit}"))
        explanations.append(f"👑 DAY+P1: {day}+{prev_p1}={day_p1_sum} → P1={day_p1_digit} (8.1%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🥉 #3: GAP P2-P1 - 7.4% hit rate!
    # ═══════════════════════════════════════════════════════════════════════
    gap_p2_p1 = prev_p2 - prev_p1
    if 1 <= gap_p2_p1 <= 15:
        candidates.append((gap_p2_p1, 40, f"GAP P2-P1: {prev_p2}-{prev_p1}={gap_p2_p1}"))
        explanations.append(f"👑 GAP: P2-P1={prev_p2}-{prev_p1}={gap_p2_p1} (7.4%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # #4: P1+P2 FIRST DIGIT - 6.7% hit rate!
    # ═══════════════════════════════════════════════════════════════════════
    p1_p2_sum = prev_p1 + prev_p2
    p1_p2_digit = int(str(p1_p2_sum)[0])
    if 1 <= p1_p2_digit <= 15:
        candidates.append((p1_p2_digit, 35, f"P1+P2: {prev_p1}+{prev_p2}={p1_p2_sum} → digit {p1_p2_digit}"))
        explanations.append(f"👑 P1+P2: {prev_p1}+{prev_p2}={p1_p2_sum} → {p1_p2_digit} (6.7%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # #5: P1+P2+P3 DIGIT SUM - 6.0% hit rate!
    # ═══════════════════════════════════════════════════════════════════════
    trio_sum = prev_p1 + prev_p2 + prev_p3
    trio_digit = sum(int(d) for d in str(trio_sum))
    if trio_digit > 9:
        trio_digit = sum(int(d) for d in str(trio_digit))
    if 1 <= trio_digit <= 15:
        candidates.append((trio_digit, 30, f"P1+P2+P3: {trio_sum} → digits {trio_digit}"))
        explanations.append(f"👑 TRIO: P1+P2+P3={trio_sum} → {trio_digit} (6.0%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # #6: P2/P3 LAST DIGIT - 5.4% hit rate each!
    # ═══════════════════════════════════════════════════════════════════════
    p2_last = prev_p2 % 10
    if 1 <= p2_last <= 15:
        candidates.append((p2_last, 28, f"P2 last: {prev_p2} → {p2_last}"))
    
    p3_last = prev_p3 % 10
    if 1 <= p3_last <= 15 and p3_last != p2_last:
        candidates.append((p3_last, 28, f"P3 last: {prev_p3} → {p3_last}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # #7: DAY × MONTH FIRST DIGIT - 5.4% hit rate!
    # ═══════════════════════════════════════════════════════════════════════
    dm_product = day * month
    dm_first = int(str(dm_product)[0])
    if 1 <= dm_first <= 15:
        candidates.append((dm_first, 28, f"D×M: {day}×{month}={dm_product} → {dm_first}"))
        explanations.append(f"👑 D×M: {day}×{month}={dm_product} → {dm_first} (5.4%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # #8: GAP P3-P2 - 4.7% hit rate!
    # ═══════════════════════════════════════════════════════════════════════
    gap_p3_p2 = prev_p3 - prev_p2
    if 1 <= gap_p3_p2 <= 15:
        candidates.append((gap_p3_p2, 25, f"GAP P3-P2: {prev_p3}-{prev_p2}={gap_p3_p2}"))
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAR CONNECTIONS TO P1
    # ═══════════════════════════════════════════════════════════════════════
    prev_stars = sorted(prev_draw['stars'])
    s_sum = prev_stars[0] + prev_stars[1]
    if 1 <= s_sum <= 15:
        candidates.append((s_sum, 20, f"S1+S2: {prev_stars[0]}+{prev_stars[1]}={s_sum}"))
    
    return {
        'candidates': candidates,
        'explanations': explanations,
        'top_p1': d_first if 1 <= d_first <= 15 else day_p1_digit if 1 <= day_p1_digit <= 15 else gap_p2_p1
    }


def dj_select_numbers(candidates: Dict, star_candidates: List[int], locked: Dict = None, date_day: int = None, p1_king_candidates: List = None, p2_prince_candidates: List = None, draws: List[Dict] = None) -> Dict:
    """
    🎧 Select final numbers from weighted candidates
    👑 P1 KING: Uses special P1 prediction patterns!
    👑 P2 PRINCE: Uses special P2 prediction patterns!
    date_day: If provided, has 30% chance to force this number at P1
    p1_king_candidates: Special P1 candidates from pattern_p1_king
    p2_prince_candidates: Special P2 candidates from pattern_p2_prince
    """
    locked = locked or {}
    p1_king_candidates = p1_king_candidates or []
    p2_prince_candidates = p2_prince_candidates or []
    
    selected = []
    used = set(locked.values())  # Pre-populate used with ALL locked values to prevent duplicates
    
    # ═══════════════════════════════════════════════════════════════════════
    # 👑 P1 KING SELECTION - The music predicts P1!
    # ═══════════════════════════════════════════════════════════════════════
    if 0 not in locked and p1_king_candidates:
        # Build weighted pool from P1 King candidates
        p1_pool = []
        for num, weight, reason in p1_king_candidates:
            if 1 <= num <= 20:  # P1 is always small!
                p1_pool.extend([num] * weight)
        
        if p1_pool:
            # 60% chance to use P1 King prediction
            if rnd.random() < 0.60:
                p1_choice = rnd.choice(p1_pool)
                selected.append(p1_choice)
                used.add(p1_choice)
            else:
                selected.append(None)  # Will be filled from regular candidates
        else:
            selected.append(None)
    elif date_day and 1 <= date_day <= 31 and 0 not in locked:
        # Fallback: 30% chance to force date_day at P1
        if rnd.random() < 0.30:
            selected.append(date_day)
            used.add(date_day)
        else:
            selected.append(None)
    else:
        selected.append(None)
    
    # ═══════════════════════════════════════════════════════════════════════
    # 👑 P2 PRINCE SELECTION - The music predicts P2!
    # ═══════════════════════════════════════════════════════════════════════
    if 1 not in locked and p2_prince_candidates:
        # Build weighted pool from P2 Prince candidates
        p2_pool = []
        for num, weight, reason in p2_prince_candidates:
            if 5 <= num <= 35 and num not in used:  # P2 typical range
                p2_pool.extend([num] * weight)
        
        if p2_pool:
            # 55% chance to use P2 Prince prediction
            if rnd.random() < 0.55:
                p2_choice = rnd.choice(p2_pool)
                selected.append(p2_choice)
                used.add(p2_choice)
            else:
                selected.append(None)  # Will be filled from regular candidates
        else:
            selected.append(None)
    else:
        selected.append(None)
    
    # Select for each position
    for pos in range(5):
        if pos < len(selected) and selected[pos] is not None:
            continue  # Already selected (P1 King or P2 Prince)
            
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
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🌍 SPREAD GUARANTEE — Ensure numbers cover at least 3 decades
    # ═══════════════════════════════════════════════════════════════════════
    decades = set((n - 1) // 10 for n in selected)  # 0=1-10, 1=11-20, 2=21-30, 3=31-40, 4=41-50
    max_retries = 10
    retry = 0
    while len(decades) < 3 and retry < max_retries:
        retry += 1
        # Find the most crowded decade
        decade_counts = {}
        for n in selected:
            d = (n - 1) // 10
            decade_counts[d] = decade_counts.get(d, 0) + 1
        crowded = max(decade_counts, key=decade_counts.get)
        if decade_counts[crowded] <= 1:
            break
        # Find which decades are missing
        missing = [d for d in range(5) if d not in decades]
        if not missing:
            break
        target_decade = rnd.choice(missing)
        # Pick a number from the target decade
        decade_range = list(range(target_decade * 10 + 1, target_decade * 10 + 11))
        decade_range = [n for n in decade_range if 1 <= n <= 50 and n not in selected]
        if not decade_range:
            continue
        # Replace one number from the crowded decade (not P1 or locked)
        replaceable = [i for i, n in enumerate(selected) if (n - 1) // 10 == crowded and i not in locked and i > 0]
        if not replaceable:
            replaceable = [i for i, n in enumerate(selected) if (n - 1) // 10 == crowded and i not in locked]
        if replaceable:
            # Pick from candidates in the target decade if possible
            target_nums = [n for n in decade_range if n in [c for c in candidates.get(replaceable[0], [])]]
            if target_nums:
                new_num = rnd.choice(target_nums)
            else:
                new_num = rnd.choice(decade_range)
            selected[replaceable[-1]] = new_num
            decades = set((n - 1) // 10 for n in selected)
    
    selected = sorted(selected)

    # Select stars
    # 🔥 BEAST BLOCK: Suppress Star 6 when on a 2-streak (77% block rate)
    if draws:
        star_candidates = beast_block_filter(star_candidates, draws)
    
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


def find_suspects(draws: List[Dict], target_date: str = None, swiss_draws: List[Dict] = None) -> dict:
    """
    🔍 THE DETECTIVE — Find where all patterns CONVERGE!
    
    Runs every pattern, scores each number by how many DIFFERENT patterns
    point to it. Numbers with 3+ pattern convergence are PRIME SUSPECTS.
    
    Returns suspects ranked by conviction level, with their family alternatives.
    """
    if not draws:
        return {"suspects": [], "star_suspects": [], "explanations": []}
    
    prev_draw = draws[0]
    prev_nums = sorted(prev_draw['numbers'])
    prev_stars = sorted(prev_draw.get('stars', []))
    
    # Each number gets a set of REASONS (unique pattern names)
    evidence = {n: set() for n in range(1, 51)}
    star_evidence = {s: set() for s in range(1, 13)}
    explanations = []
    
    # ── 1. FLIP+CIRCLE CHAIN ──
    for n in prev_nums:
        for c in flip_circle_chain(n):
            if 1 <= c <= 50:
                evidence[c].add(f"chain({n})")
    
    # ── 2. CIRCLES ──
    for n in prev_nums:
        c = circle(n)
        evidence[c].add(f"circle({n})")
    
    # ── 3. NEIGHBOURHOOD ──
    for n in prev_nums:
        if n-1 >= 1: evidence[n-1].add(f"neighbour({n})")
        if n+1 <= 50: evidence[n+1].add(f"neighbour({n})")
    
    # ── 4. HUNGRY ──
    for i in range(len(prev_nums)-1):
        if prev_nums[i+1] - prev_nums[i] == 2:
            h = prev_nums[i] + 1
            evidence[h].add(f"HUNGRY({prev_nums[i]},{prev_nums[i+1]})")
    
    # ── 5. ADDITION ──
    for i in range(len(prev_nums)):
        for j in range(i+1, len(prev_nums)):
            s = prev_nums[i] + prev_nums[j]
            if 1 <= s <= 50:
                evidence[s].add(f"add({prev_nums[i]}+{prev_nums[j]})")
    
    # ── 6. SUM FAMILY ──
    total = sum(prev_nums)
    last_d = total % 10
    for n in range(1, 51):
        if n % 10 == last_d:
            evidence[n].add(f"sum-family({total})")
    
    # ── 7. REPEAT ──
    for n in prev_nums:
        evidence[n].add("repeat")
    
    # ── 8. DATE READING ──
    if target_date:
        dr = date_reading(target_date)
        for n in dr.get("numbers", []):
            if 1 <= n <= 50:
                evidence[n].add("date-number")
        for d in dr.get("digits", set()):
            for n in range(1, 51):
                if str(d) in str(n):
                    evidence[n].add(f"date-digit({d})")
        # Day chain = 25.3% hit rate!
        try:
            day = int(target_date.split('.')[0])
            month = int(target_date.split('.')[1])
            if 1 <= day <= 50:
                evidence[day].add("DAY-DIRECT(12.7%)")
                dc = circle(day)
                evidence[dc].add("DAY-CIRCLE(12%)")
                dcf = flip(dc)
                if 1 <= dcf <= 50:
                    evidence[dcf].add("DAY-CIRCLE-FLIP")
                for c in flip_circle_chain(day):
                    if 1 <= c <= 50:
                        evidence[c].add("DAY-CHAIN(25.3%)")
            dm = day + month
            if 1 <= dm <= 50:
                evidence[dm].add("D+M")
            if 1 <= day * month <= 50:
                evidence[day * month].add("DxM")
        except: pass
    
    # ── 9. P4-P5 HIDDEN (cross digit pairs) ──
    p4, p5 = prev_nums[3], prev_nums[4]
    concat = f"{p4}{p5}"
    digits = [int(c) for c in concat]
    pairs = set()
    for a in range(len(digits)):
        for b in range(len(digits)):
            if a != b:
                num = digits[a]*10 + digits[b]
                if num > 0: pairs.add(num)
    for p in pairs:
        if 1 <= p <= 50:
            evidence[p].add(f"P4P5-hidden({p4},{p5})")
        elif p > 50 and 1 <= p-50 <= 50:
            evidence[p-50].add(f"P4P5-minus50({p})")
    
    # ── 10. STAR→Q COUNT ──
    if target_date and len(draws) >= 10:
        try:
            from datetime import datetime as dt_cls
            current_date = dt_cls.strptime(target_date, "%d.%m.%Y")
            current_q = (current_date.month - 1) // 3 + 1
            current_year = current_date.year
            prev_q = current_q - 1 if current_q > 1 else 4
            prev_year = current_year if current_q > 1 else current_year - 1
            pqs, pqe = (prev_q-1)*3+1, prev_q*3
            
            prev_q_draws = []
            for d in draws:
                try:
                    dd = dt_cls.strptime(d['date'], "%d.%m.%Y")
                    if dd.year == prev_year and pqs <= dd.month <= pqe:
                        prev_q_draws.append(d)
                except: continue
            prev_q_draws.sort(key=lambda x: dt_cls.strptime(x['date'], "%d.%m.%Y"))
            
            if prev_q_draws and prev_stars:
                sq = star_q_count_decode(prev_stars, prev_q_draws)
                for val, w, reason in sq.get("p1_candidates", []):
                    if 1 <= val <= 50:
                        evidence[val].add(f"star-Q({reason[:20]})")
                for val, w, reason in sq.get("p2_candidates", []):
                    if 1 <= val <= 50:
                        evidence[val].add(f"star-Q-digit")
        except: pass
    
    # ── 11. FLIP of prev numbers (simple) ──
    for n in prev_nums:
        f = flip(n)
        if 1 <= f <= 50 and f != n:
            evidence[f].add(f"flip({n})")
    
    # ── 12. CROSS-LOTTERY (Swiss→Euro) ──
    if swiss_draws:
        sw = sorted(swiss_draws[0].get('numbers', []))
        if sw:
            sw_p1 = sw[0]
            evidence[sw_p1].add("swiss-P1-bridge")
            c_sw = circle(sw_p1) if sw_p1 <= 50 else None
            if c_sw and 1 <= c_sw <= 50:
                evidence[c_sw].add("swiss-P1-circle")
    
    # ── BUILD SUSPECT LIST ──
    suspects = []
    for n in range(1, 51):
        count = len(evidence[n])
        if count >= 2:  # At least 2 different patterns
            # Build family
            fam = flip_circle_chain(n)
            suspects.append({
                "number": n,
                "conviction": count,
                "patterns": sorted(evidence[n]),
                "family": [f for f in fam if 1 <= f <= 50]
            })
    
    suspects.sort(key=lambda x: -x["conviction"])
    
    return {
        "suspects": suspects,
        "evidence": evidence,
        "explanations": explanations
    }


def dj_generate_ticket_v2(draws: List[Dict], target_date: str = None, locked: Dict = None, 
                           swiss_draws: List[Dict] = None, ticket_index: int = 0, total_tickets: int = 1) -> Dict:
    """
    🎧 V2 TICKET GENERATOR — Suspect-Based! 🔍
    
    1. Find suspects (convergence of all patterns)
    2. Top suspects with 3+ patterns = LOCKED into 60% of tickets
    3. Remaining tickets use family alternatives (circle/flip of suspects)
    4. Stars predicted from star progression + star-Q decode
    """
    available_swiss = swiss_draws
    if not available_swiss and hasattr(dj_generate_ticket, 'swiss_draws'):
        available_swiss = dj_generate_ticket.swiss_draws
    
    # Find suspects
    suspect_result = find_suspects(draws, target_date, swiss_draws=available_swiss)
    suspects = suspect_result["suspects"]
    
    # Also get regular candidates for fallback
    result = dj_generate_candidates(draws, target_date, swiss_draws=available_swiss)
    
    prev_nums = sorted(draws[0]['numbers'])
    prev_stars = sorted(draws[0].get('stars', []))
    
    # Decide: story ticket (60%) or family ticket (40%)
    use_direct = (ticket_index / max(total_tickets, 1)) < 0.6
    
    selected = []
    used = set()
    
    # Handle locked positions
    locked = locked or {}
    for pos, val in locked.items():
        if isinstance(pos, int) and 1 <= val <= 50:
            used.add(val)
    
    if suspects:
        # Top suspects sorted by conviction
        prime = [s for s in suspects if s["conviction"] >= 3][:7]
        secondary = [s for s in suspects if s["conviction"] == 2][:10]
        
        if use_direct:
            # STORY TICKET — use prime suspects, but vary which ones
            # Shuffle among top suspects with some randomness
            prime_pool = list(prime)
            rnd.shuffle(prime_pool)
            # Always include top 2-3, randomize the rest
            must_have = prime_pool[:min(3, len(prime_pool))]
            rest = prime_pool[3:] + secondary[:5]
            rnd.shuffle(rest)
            
            for s in must_have:
                n = s["number"]
                if n not in used and len(selected) < 5:
                    selected.append(n)
                    used.add(n)
            for s in rest:
                n = s["number"]
                if n not in used and len(selected) < 5:
                    selected.append(n)
                    used.add(n)
        else:
            # FAMILY TICKET — use suspect families (circles, flips)
            for s in prime[:3]:
                n = s["number"]
                # Pick from family instead
                fam = [f for f in s["family"] if f not in used and 1 <= f <= 50]
                if fam and len(selected) < 5:
                    pick = rnd.choice(fam)
                    selected.append(pick)
                    used.add(pick)
            # Add some direct from secondary
            for s in secondary:
                n = s["number"]
                if n not in used and len(selected) < 5:
                    selected.append(n)
                    used.add(n)
    
    # Fill remaining from weighted candidates
    while len(selected) < 5:
        pos = len(selected)
        pool = [c for c in result["candidates"].get(pos, []) if c not in used and 1 <= c <= 50]
        if pool:
            pick = rnd.choice(pool)
        else:
            pick = rnd.choice([n for n in range(1, 51) if n not in used])
        selected.append(pick)
        used.add(pick)
    
    selected = sorted(selected)
    
    # ── SPREAD GUARANTEE (3+ decades) ──
    decades = set((n-1)//10 for n in selected)
    retry = 0
    while len(decades) < 3 and retry < 10:
        retry += 1
        decade_counts = {}
        for n in selected:
            d = (n-1)//10
            decade_counts[d] = decade_counts.get(d, 0) + 1
        crowded = max(decade_counts, key=decade_counts.get)
        missing = [d for d in range(5) if d not in decades]
        if not missing: break
        target_decade = rnd.choice(missing)
        decade_range = [n for n in range(target_decade*10+1, target_decade*10+11) if 1<=n<=50 and n not in selected]
        if not decade_range: continue
        replaceable = [i for i, n in enumerate(selected) if (n-1)//10 == crowded]
        if replaceable:
            selected[replaceable[-1]] = rnd.choice(decade_range)
            decades = set((n-1)//10 for n in selected)
    
    selected = sorted(selected)
    
    # ── STARS ──
    star_pool = result.get("star_candidates", list(range(1, 13)))
    if not star_pool: star_pool = list(range(1, 13))
    star_pool = [s for s in star_pool if 1 <= s <= 12]
    if not star_pool: star_pool = list(range(1, 13))
    
    star1 = rnd.choice(star_pool)
    star_pool2 = [s for s in star_pool if s != star1]
    star2 = rnd.choice(star_pool2) if star_pool2 else (star1 % 12 + 1)
    
    # Build patterns description
    patterns = result.get("patterns", [])
    suspect_info = []
    for s in suspects[:5]:
        suspect_info.append(f"🔍 SUSPECT {s['number']} (conviction:{s['conviction']}): {', '.join(s['patterns'][:3])}")
    
    return {
        "numbers": selected,
        "stars": sorted([star1, star2]),
        "patterns_used": suspect_info + patterns[:20],
        "suspects": [(s["number"], s["conviction"]) for s in suspects[:10]],
        "ticket_type": "story" if use_direct else "family",
        "prev_draw": {"numbers": prev_nums, "stars": prev_stars}
    }



def dj_generate_ticket(draws: List[Dict], target_date: str = None, locked: Dict = None, swiss_draws: List[Dict] = None, use_v2: bool = True, ticket_index: int = 0, total_tickets: int = 1) -> Dict:
    """
    🎧 Generate a single ticket using the DJ engine
    V2: Suspect-based detective mode (default)
    V1: Original weighted random (fallback)
    """
    if use_v2:
        return dj_generate_ticket_v2(draws, target_date, locked, swiss_draws, ticket_index, total_tickets)
    
    # V1 original flow
    # Get swiss_draws from parameter or function attribute
    available_swiss = swiss_draws
    if not available_swiss and hasattr(dj_generate_ticket, 'swiss_draws'):
        available_swiss = dj_generate_ticket.swiss_draws
    
    result = dj_generate_candidates(draws, target_date, swiss_draws=available_swiss)
    
    # Extract date day for special handling
    date_day = None
    p1_king_result = None
    p2_prince_result = None
    p1_king_candidates = []
    p2_prince_candidates = []
    
    if target_date and draws:
        try:
            date_day = int(target_date.split('.')[0])
            
            # 👑 P1 KING - Get special P1 predictions!
            p1_king_result = pattern_p1_king(target_date, draws[0], draws[1] if len(draws) > 1 else None)
            p1_king_candidates = p1_king_result.get('candidates', [])
            
            # 👑 P2 PRINCE - Get special P2 predictions!
            p2_prince_result = pattern_p2_prince(target_date, draws[0], draws[1] if len(draws) > 1 else None)
            p2_prince_candidates = p2_prince_result.get('candidates', [])
            
            # Add P1 King and P2 Prince explanations to patterns
            for exp in p1_king_result.get('explanations', []):
                result["patterns"].insert(0, exp)
            for exp in p2_prince_result.get('explanations', []):
                result["patterns"].insert(0, exp)
        except:
            pass
    
    selection = dj_select_numbers(
        result["candidates"], 
        result["star_candidates"], 
        locked, 
        date_day,
        p1_king_candidates,
        p2_prince_candidates,
        draws
    )
    
    return {
        "numbers": selection["numbers"],
        "stars": selection["stars"],
        "patterns_used": result["patterns"],
        "p1_king": p1_king_result,
        "p2_prince": p2_prince_result,
        "prev_draw": {
            "numbers": result["prev_nums"],
            "stars": result["prev_stars"]
        }
    }


def dj_generate_money_mode_ticket(draws: List[Dict], target_date: str = None, swiss_draws: List[Dict] = None, locked: Dict = None) -> Dict:
    """
    💰 MONEY MODE - Focus on hitting 3 numbers + stars for consistent small wins! 💰
    
    Strategy:
    - Use ONLY the highest hit-rate patterns (10%+ proven)
    - Prioritize STAR accuracy (smaller pool = higher probability)
    - Use cross-lottery vibes (Swiss→Euro 13.3% hit rate!)
    - Generate tickets with OVERLAPPING high-confidence numbers
    
    Target prizes:
    - 3 + 2⭐ = ~€50-100
    - 3 + 1⭐ = ~€15-20
    - 3 + 0⭐ = ~€10-15
    """
    if not draws:
        return {"numbers": [], "stars": [], "patterns_used": [], "mode": "money"}
    
    # Get swiss_draws from parameter or function attribute
    available_swiss = swiss_draws
    if not available_swiss and hasattr(dj_generate_money_mode_ticket, 'swiss_draws'):
        available_swiss = dj_generate_money_mode_ticket.swiss_draws
    
    candidates = {i: [] for i in range(5)}  # P1-P5
    star_candidates = []
    patterns_used = ["💰 MONEY MODE - Target: 3 numbers + stars"]
    
    prev_draw = draws[0]
    prev_nums = sorted(prev_draw['numbers'])
    prev_stars = sorted(prev_draw.get('stars', []))
    p1, p2, p3, p4, p5 = prev_nums
    s1 = prev_stars[0] if prev_stars else 1
    s2 = prev_stars[1] if len(prev_stars) > 1 else 1
    
    # ═══════════════════════════════════════════════════════════════════
    # ONLY USE HIGH HIT-RATE PATTERNS (10%+)
    # ═══════════════════════════════════════════════════════════════════
    
    # Also look at draw before prev for more signal
    prev2_draw = draws[1] if len(draws) > 1 else prev_draw
    prev2_nums = sorted(prev2_draw['numbers'])
    prev2_stars = sorted(prev2_draw.get('stars', []))
    
    # 1. P5 ECHO (14.8% hit rate!) - but only boost P4/P5 positions
    candidates[3].extend([p5] * 8)
    candidates[4].extend([p5] * 10)
    patterns_used.append(f"P5 Echo: {p5} (14.8%)")
    
    # 2. P5-1 (11.4% hit rate!) - natural P4/P5
    p5_minus_1 = p5 - 1 if p5 > 1 else None
    if p5_minus_1:
        candidates[3].extend([p5_minus_1] * 6)
        candidates[4].extend([p5_minus_1] * 8)
        patterns_used.append(f"P5-1: {p5}-1={p5_minus_1} (11.4%)")
    
    # 3. P4 ECHO (12.5% hit rate!) - P3/P4 positions
    candidates[2].extend([p4] * 5)
    candidates[3].extend([p4] * 8)
    patterns_used.append(f"P4 Echo: {p4} (12.5%)")
    
    # 4. P1 ECHO (11.1% hit rate!) - P1 position only
    candidates[0].extend([p1] * 8)
    candidates[1].extend([p1] * 4)
    patterns_used.append(f"P1 Echo: {p1} (11.1%)")
    
    # 5. P2/P3 ECHO - add coverage for middle positions
    candidates[1].extend([p2] * 6)
    candidates[2].extend([p3] * 6)
    
    # 6. CIRCLE MATH (10%+ hit rate)
    circle_hits = []
    for n in prev_nums:
        c_plus = n + 25 if n + 25 <= 50 else None
        c_minus = n - 25 if n - 25 > 0 else None
        if c_plus:
            circle_hits.append(c_plus)
            # Place in appropriate position range
            if c_plus <= 15:
                candidates[0].extend([c_plus] * 5)
            elif c_plus <= 25:
                candidates[1].extend([c_plus] * 5)
                candidates[2].extend([c_plus] * 4)
            elif c_plus <= 40:
                candidates[2].extend([c_plus] * 4)
                candidates[3].extend([c_plus] * 5)
            else:
                candidates[3].extend([c_plus] * 4)
                candidates[4].extend([c_plus] * 5)
        if c_minus:
            circle_hits.append(c_minus)
            if c_minus <= 15:
                candidates[0].extend([c_minus] * 5)
                candidates[1].extend([c_minus] * 4)
            elif c_minus <= 25:
                candidates[1].extend([c_minus] * 4)
                candidates[2].extend([c_minus] * 5)
            else:
                candidates[2].extend([c_minus] * 4)
                candidates[3].extend([c_minus] * 5)
    if circle_hits:
        patterns_used.append(f"Circle Math: {circle_hits[:4]}")
    
    # 7. SLEEPER INJECTION - numbers not seen in last 5 draws get a boost
    recent_nums = set()
    for d in draws[:5]:
        recent_nums.update(d['numbers'])
    sleepers = [n for n in range(1, 51) if n not in recent_nums]
    import random as rng
    if sleepers:
        for pos in range(5):
            # Add 3 random sleepers per position
            for _ in range(3):
                s = rng.choice(sleepers)
                candidates[pos].extend([s] * 3)
        patterns_used.append(f"Sleeper injection: {len(sleepers)} numbers sleeping")
    
    # 8. DANCE PATTERN: P1(prev2) + P2(prev) -> circle -> candidate
    dance_val = prev2_nums[0] + prev_nums[1]
    while dance_val > 25:
        dance_val -= 25
    if 1 <= dance_val <= 50:
        candidates[0].extend([dance_val] * 6)
        candidates[1].extend([dance_val] * 4)
        patterns_used.append(f"Dance: P1({prev2_nums[0]})+P2({prev_nums[1]})={dance_val}")
    
    # 9. S1+S1=12 SCREAM: if prev two S1s add to 12, boost number 12
    if len(draws) > 1:
        s1_a = min(draws[0].get('stars', [1]))
        s1_b = min(draws[1].get('stars', [1]))
        if s1_a + s1_b == 12:
            candidates[0].extend([12] * 5)
            candidates[1].extend([12] * 5)
            candidates[2].extend([12] * 4)
            patterns_used.append(f"12 Scream: S1({s1_a})+S1({s1_b})=12")
    
    # 10. STAR→P3 DANCE (17.5% combined hit rate!)
    # Top 3 formulas discovered: concat(S2,S1)->circle, rev(S1+S2), S1+S2+25
    star_p3_candidates = []
    
    # Formula 1: concat(S2, S1) then circle (6.2% - STRONGEST!)
    concat_val = int(f"{s2}{s1}")
    while concat_val > 50:
        concat_val -= 25
    if 1 <= concat_val <= 50:
        star_p3_candidates.append(concat_val)
    
    # Also try concat(S1, S2) then circle
    concat_val2 = int(f"{s1}{s2}")
    while concat_val2 > 50:
        concat_val2 -= 25
    if 1 <= concat_val2 <= 50:
        star_p3_candidates.append(concat_val2)
    
    # Formula 2: reverse(S1+S2) (3.8%)
    star_sum_str = str(s1 + s2)
    rev_sum = int(star_sum_str[::-1])
    if rev_sum > 50:
        rev_sum -= 25
    if 1 <= rev_sum <= 50:
        star_p3_candidates.append(rev_sum)
    
    # Formula 3: S1+S2+25 circle (2.8%)
    sum_circle = s1 + s2 + 25
    if sum_circle > 50:
        sum_circle -= 25
    if 1 <= sum_circle <= 50:
        star_p3_candidates.append(sum_circle)
    
    # Formula 4: S2+25 (star circle)
    s2_circle = s2 + 25
    if s2_circle <= 50:
        star_p3_candidates.append(s2_circle)
    
    # Formula 5: rev(S1*S2) then circle
    prod_rev = int(str(s1 * s2)[::-1])
    while prod_rev > 50:
        prod_rev -= 25
    if 1 <= prod_rev <= 50:
        star_p3_candidates.append(prod_rev)
    
    # Inject star-P3 dance candidates at P3 position with strong weight
    for sp3 in star_p3_candidates:
        candidates[2].extend([sp3] * 6)  # Strong P3 weight
        candidates[1].extend([sp3] * 2)  # Some P2 weight too
        candidates[3].extend([sp3] * 2)  # Some P4 weight
    
    if star_p3_candidates:
        patterns_used.append(f"Star->P3 Dance: {star_p3_candidates[:4]}")
    
    # ═══════════════════════════════════════════════════════════════════
    # P2 PREDICTION (2.5x random on Euro! prev P2 ±1 = 15%)
    # ═══════════════════════════════════════════════════════════════════
    p2_pm1_hits = []
    if prev_p2 := prev_nums[1] if len(prev_nums) >= 2 else None:
        for delta in [-1, 0, 1]:
            v = p2 + delta
            if 1 <= v <= 50:
                candidates[1].extend([v] * 12)
                p2_pm1_hits.append(v)
        patterns_used.append(f"🎯 P2 predict: prev={p2}±1 → {p2_pm1_hits} (15%, 2.5x!)")
    
    # ═══════════════════════════════════════════════════════════════════
    # P123 CONCAT DIGIT PATTERN (16% at 3+ with 5 unique digits!)
    # ═══════════════════════════════════════════════════════════════════
    def euro_concat_derived(digit_str):
        nums = set()
        for c in digit_str:
            d = int(c)
            if 1 <= d <= 50: nums.add(d)
        for j in range(len(digit_str)-1):
            v = int(digit_str[j:j+2])
            if 1 <= v <= 50: nums.add(v)
        unique = list(set(digit_str))
        for a in unique:
            for b in unique:
                v = int(a+b)
                if 1 <= v <= 50: nums.add(v)
        return sorted(nums)
    
    # Pool 1: P123 from prev draw
    p123_concat = str(p1) + str(p2) + str(p3)
    p123_derived = euro_concat_derived(p123_concat)
    p123_unique = len(set(p123_concat))
    
    # Pool 2: date digits
    date_pool = []
    if target_date:
        try:
            dt = parse_draw_date(target_date)
            date_concat = str(dt.day) + str(dt.month)
            date_pool = euro_concat_derived(date_concat)
        except:
            pass
    
    # Score: numbers in both pools get double weight
    p123_boosted = []
    for n in p123_derived:
        weight = 8 if n in date_pool else 4
        for pos in range(5):
            if n <= 15: candidates[pos if pos < 2 else 0].extend([n] * weight)
            elif n <= 30: candidates[min(pos, 2)].extend([n] * weight)
            else: candidates[max(pos, 2)].extend([n] * weight)
        if n in date_pool:
            p123_boosted.append(n)
    
    patterns_used.append(f"🔢 P123 \"{p123_concat}\" ({p123_unique}dig) → {p123_derived[:6]}")
    if p123_boosted:
        patterns_used.append(f"🔢 P123+Date overlap: {p123_boosted[:5]}")
    
    # ═══════════════════════════════════════════════════════════════════
    # P6 CIRCLE BRIDGE — Swiss P6 to Euro (40% hit rate over 2 years!)
    # Swiss P6 - 21 (Swiss circle) or Swiss P6 - 25 (Euro circle)
    # ═══════════════════════════════════════════════════════════════════
    if swiss_draws and len(swiss_draws) >= 2:
        swiss_sorted = sorted(swiss_draws, key=lambda d: parse_draw_date(d.get('date', '01.01.2000')), reverse=True)
        sw_last = sorted(swiss_sorted[0].get('numbers', []))
        sw_prev = sorted(swiss_sorted[1].get('numbers', []))
        
        if len(sw_last) >= 6 and len(sw_prev) >= 6:
            sw_p6_a = sw_prev[5]
            sw_p6_b = sw_last[5]
            sw_p6_sum = sw_p6_a + sw_p6_b
            sw_p2_a = sw_prev[1]
            sw_p2_b = sw_last[1]
            
            # Bridge: Swiss P6 - 21 and Swiss P6 - 25
            bridge_nums = set()
            for p6 in [sw_p6_a, sw_p6_b]:
                t21 = p6 - 21
                t25 = p6 - 25
                if 1 <= t21 <= 50:
                    bridge_nums.add(t21)
                if 1 <= t25 <= 50:
                    bridge_nums.add(t25)
            
            # 69 Math: digit arithmetic from P2 concat and P6 sum
            math_nums = set()
            for a, b in [(sw_p2_a, sw_p2_b), (sw_p6_a - 30, sw_p6_b - 30)]:
                s = a + b
                d = abs(a - b)
                p = a * b
                if 1 <= s <= 50: math_nums.add(s)
                if 1 <= d <= 50: math_nums.add(d)
                if 1 <= p <= 50: math_nums.add(p)
            
            # Circle of P2 digits in Euro context
            for p2 in [sw_p2_a, sw_p2_b]:
                c_euro = p2 + 25 if p2 + 25 <= 50 else p2 + 25 - 50
                if 1 <= c_euro <= 50:
                    math_nums.add(c_euro)
            
            # Apply bridge numbers (strong: 40% hit rate)
            for n in bridge_nums:
                for pos in range(5):
                    if n <= 15: candidates[pos if pos < 2 else 0].extend([n] * 10)
                    elif n <= 30: candidates[min(pos, 2)].extend([n] * 10)
                    else: candidates[max(pos, 2)].extend([n] * 10)
            
            # Apply 69 math numbers (moderate boost)
            for n in math_nums:
                for pos in range(5):
                    candidates[pos].extend([n] * 5)
            
            patterns_used.append(f"🌉 P6 Bridge: Swiss P6={sw_p6_b},{sw_p6_a} sum={sw_p6_sum} → {sorted(bridge_nums)}")
            if math_nums:
                patterns_used.append(f"🔢 69 Math: P2={sw_p2_a},{sw_p2_b} → {sorted(math_nums)[:6]}")
    
    # ═══════════════════════════════════════════════════════════════════
    # REVERSE TWIN GENERATOR (new!)
    # ═══════════════════════════════════════════════════════════════════
    rev_twin_result = pattern_flip_twin(prev_draw)
    for num, weight, reason in rev_twin_result.get('candidates', []):
        if 1 <= num <= 50:
            for pos in range(5):
                candidates[pos].extend([num] * (weight // 10))
    for exp in rev_twin_result.get('explanations', [])[:2]:
        patterns_used.append(exp)
    
    # ═══════════════════════════════════════════════════════════════════
    # DAY x MONTH - 10 (new!)
    # ═══════════════════════════════════════════════════════════════════
    if target_date:
        dm10_result = pattern_day_times_month_minus_10(target_date)
        for num, weight, reason in dm10_result.get('candidates', []):
            if 1 <= num <= 50:
                for pos in range(5):
                    candidates[pos].extend([num] * (weight // 10))
        for exp in dm10_result.get('explanations', [])[:2]:
            patterns_used.append(exp)
    
    # ═══════════════════════════════════════════════════════════════════
    # 11. DRAW-TO-DRAW LEARNING: The machine learns momentum
    # Hot numbers (2+ in last 5), cold sleepers with circle partners,
    # P3 trend projection, star momentum
    # ═══════════════════════════════════════════════════════════════════
    if len(draws) >= 3:
        import random as rng
        
        # Hot numbers: appeared 2+ times in last 5 draws
        recent_counter = Counter()
        for d in draws[:5]:
            for n in d['numbers']:
                recent_counter[n] += 1
        
        hot_nums = [n for n, c in recent_counter.items() if c >= 2]
        for hn in hot_nums:
            for pos in range(5):
                candidates[pos].extend([hn] * 3)
        
        # Cold sleepers: not in last 8 draws, but circle partner IS recent
        recent_all = set()
        for d in draws[:8]:
            recent_all.update(d['numbers'])
        
        cold_nums = [n for n in range(1, 51) if n not in recent_all]
        for cn in cold_nums:
            circle_partner = cn + 25 if cn + 25 <= 50 else cn - 25
            if circle_partner in recent_all and 1 <= circle_partner <= 50:
                for pos in range(5):
                    candidates[pos].extend([cn] * 2)
        
        # P3 momentum: project next P3 from trend
        p3_values = [sorted(d['numbers'])[2] for d in draws[:5]]
        if len(p3_values) >= 3:
            projected_p3 = p3_values[0] + (p3_values[0] - p3_values[1])
            if 1 <= projected_p3 <= 50:
                candidates[2].extend([projected_p3] * 3)
        
        # Star momentum: hot stars (2+ in last 3 draws)
        recent_stars = Counter()
        for d in draws[:3]:
            for s in d.get('stars', []):
                recent_stars[s] += 1
        
        hot_stars = [s for s, c in recent_stars.items() if c >= 2 and 1 <= s <= 12]
        for hs in hot_stars:
            star_candidates.extend([hs] * 4)
        
        # Cold stars: not seen in 5 draws, add small representation
        all_recent_stars = set()
        for d in draws[:5]:
            all_recent_stars.update(d.get('stars', []))
        for cs in range(1, 13):
            if cs not in all_recent_stars:
                star_candidates.extend([cs] * 2)
        
        if hot_nums:
            patterns_used.append(f"Learning hot: {hot_nums[:5]}")
        if hot_stars:
            patterns_used.append(f"Learning hot stars: {hot_stars}")
    
    # ═══════════════════════════════════════════════════════════════════
    # CROSS-LOTTERY PATTERNS (13.3%+ hit rate!) - MONEY MODE LOVES THIS!
    # ═══════════════════════════════════════════════════════════════════
    if target_date and available_swiss:
        try:
            euro_dt = parse_draw_date(target_date)
            
            for swiss in available_swiss[:3]:
                swiss_dt = parse_draw_date(swiss['date'])
                days_diff = (euro_dt - swiss_dt).days
                
                if 1 <= days_diff <= 14:
                    swiss_day = swiss_dt.day
                    swiss_lucky = swiss.get('lucky_number')
                    euro_month = euro_dt.month
                    
                    # SwissDay + EuroMonth (13.3%!) - VERY STRONG
                    combo1 = swiss_day + euro_month
                    if 1 <= combo1 <= 50:
                        for pos in range(5):
                            candidates[pos].extend([combo1] * 15)  # High weight!
                        patterns_used.append(f"🍀💰 Swiss({swiss_day})+Month({euro_month})={combo1} (13.3%)")
                    
                    # Lucky × EuroMonth (13.3%!) - VERY STRONG
                    if swiss_lucky:
                        combo2 = swiss_lucky * euro_month
                        if 1 <= combo2 <= 50:
                            for pos in range(5):
                                candidates[pos].extend([combo2] * 15)
                            patterns_used.append(f"🍀💰 Lucky({swiss_lucky})×Month({euro_month})={combo2} (13.3%)")
                        
                        # Lucky → Star (16.7%!) - CRITICAL FOR MONEY MODE
                        if 1 <= swiss_lucky <= 12:
                            star_candidates.extend([swiss_lucky] * 20)
                            patterns_used.append(f"🍀⭐ Lucky {swiss_lucky} → Star! (16.7%)")
                    
                    break  # Only use closest Swiss
        except:
            pass
    
    # ═══════════════════════════════════════════════════════════════════
    # 🇨🇭 SWISS P1 → EURO P1 BRIDGE (3.48x random!) - MONEY MODE
    # ═══════════════════════════════════════════════════════════════════
    if available_swiss and len(available_swiss) >= 3:
        bridge = swiss_p1_bridge(available_swiss)
        
        # P1 candidates get MASSIVE boost at P1 position in Money Mode
        for num, weight, reason in bridge.get('p1_candidates', []):
            if 1 <= num <= 50:
                candidates[0].extend([num] * (weight * 2))  # Double weight for Money Mode P1!
                candidates[1].extend([num] * (weight // 2))
        
        # General candidates spread across positions
        for num, weight, reason in bridge.get('general_candidates', []):
            if 1 <= num <= 50:
                for pos in range(5):
                    candidates[pos].extend([num] * weight)
        
        for exp in bridge.get('explanations', []):
            patterns_used.append(f"🇨🇭💰 {exp}")
    
    # ═══════════════════════════════════════════════════════════════════
    # STAR FOCUS - IMPROVED COVERAGE! (only 12 options)
    # ═══════════════════════════════════════════════════════════════════
    
    # Previous stars echo (high probability)
    star_candidates.extend([s1] * 10)
    star_candidates.extend([s2] * 10)
    patterns_used.append(f"Prev stars: {s1}, {s2}")
    
    # |S2 - S1| pattern
    star_diff = abs(s2 - s1)
    if 1 <= star_diff <= 12:
        star_candidates.extend([star_diff] * 8)
        patterns_used.append(f"|S2-S1|={star_diff}")
    
    # S1 + S2 mod 12
    star_sum = (s1 + s2) % 12
    if star_sum == 0: star_sum = 12
    star_candidates.extend([star_sum] * 6)
    patterns_used.append(f"(S1+S2)%12={star_sum}")
    
    # S1 × 2 and S2 × 2 (capped at 12) - catches higher stars!
    s1x2 = min(s1 * 2, 12)
    s2x2 = min(s2 * 2, 12)
    star_candidates.extend([s1x2] * 5)
    star_candidates.extend([s2x2] * 5)
    
    # Stars from draw before prev (adds variety)
    if prev2_stars:
        ps1 = prev2_stars[0]
        ps2 = prev2_stars[1] if len(prev2_stars) > 1 else ps1
        star_candidates.extend([ps1] * 4)
        star_candidates.extend([ps2] * 4)
    
    # Ensure some high star representation (10, 11, 12)
    for high_s in [10, 11, 12]:
        star_candidates.extend([high_s] * 2)
    
    # Date day as star (if valid)
    if target_date:
        try:
            day = int(target_date.split('.')[0])
            if 1 <= day <= 12:
                star_candidates.extend([day] * 8)
                patterns_used.append(f"Day={day} as star")
        except:
            pass
    
    # ═══════════════════════════════════════════════════════════════════
    # SELECT NUMBERS (Weighted random with DECADE SPREAD!)
    # ═══════════════════════════════════════════════════════════════════
    import random
    locked = locked or {}
    
    selected = []
    used = set(locked.values())  # Pre-populate used with ALL locked values to prevent duplicates
    
    for pos in range(5):
        if pos in locked:
            selected.append(locked[pos])
            used.add(locked[pos])
        else:
            pool = [n for n in candidates[pos] if n not in used and 1 <= n <= 50]
            if pool:
                chosen = random.choice(pool)
            else:
                available = [n for n in range(1, 51) if n not in used]
                chosen = random.choice(available) if available else 1
            selected.append(chosen)
            used.add(chosen)
    
    # DECADE SPREAD CHECK: If all 5 numbers are in 2 or fewer decades, swap one
    decades_covered = set(n // 10 for n in selected)
    if len(decades_covered) <= 2:
        # Find a missing decade and swap the weakest number
        all_decades = {0, 1, 2, 3, 4}
        missing = all_decades - decades_covered
        if missing:
            target_decade = random.choice(list(missing))
            # Pick a number from that decade
            decade_nums = [n for n in range(target_decade*10 + 1, min(target_decade*10 + 10, 50) + 1) if n not in used]
            if decade_nums:
                swap_num = random.choice(decade_nums)
                # Replace the position with least candidate support
                swap_pos = None
                for pos in range(4, -1, -1):
                    if pos not in locked and selected[pos] not in locked.values():
                        swap_pos = pos
                        break
                if swap_pos is not None:
                    used.discard(selected[swap_pos])
                    selected[swap_pos] = swap_num
                    used.add(swap_num)
    
    # SELECT STARS (from focused pool)
    # 🔥 BEAST BLOCK: Suppress Star 6 when on a 2-streak
    star_candidates = beast_block_filter(star_candidates, draws)
    
    star_pool = [s for s in star_candidates if 1 <= s <= 12]
    if not star_pool:
        star_pool = list(range(1, 13))
    
    star1 = random.choice(star_pool)
    star_pool2 = [s for s in star_pool if s != star1]
    star2 = random.choice(star_pool2) if star_pool2 else (star1 % 12 + 1)
    
    return {
        "numbers": sorted(selected),
        "stars": sorted([star1, star2]),
        "patterns_used": patterns_used,
        "mode": "money",
        "target": "3+ numbers + stars",
        "prev_draw": {
            "numbers": prev_nums,
            "stars": prev_stars
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
