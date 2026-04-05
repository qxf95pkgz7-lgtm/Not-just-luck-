"""
STORY PATTERN GENERATOR
=======================
All patterns learned from Avi's numerology teachings.

RC (Rare Count) starts from 18.03.2023 - the 5-in-same-decade rare event.

KEY DISCOVERIES:
- P4 is the "heart" position - tells the story
- RC sum = 5 signals potential rare events
- 28 + 8 = 36 (The RC origin date digits sum = 28, 8-count dance)
- Date Dance: D, M, D-M, D+M, D×M, D×M+D+M
- Circle of D often = P4 when D >= 10
- (D+M) × 2 often = P4 when D+M <= 10

STORY PATTERNS (Combined):
- The 26 Family: [13, 26, 27, 30, 31, 38] with circle swaps
- The 18-39 Circle: 18 at P3, 39 at P6, gap of 3
- The 33-12 Reunion: 30 draws apart, 12 at P1-P3, 33 at P4-P6
- The P4 Heart Rule: 12 at P4 blocks 33 (100%)
- Mr. 13 Jail Story: Track when 13 is in P8 (jail) vs free
- P4 + M = P5 on Day 28
- P8 = Circle(Hungry Middle)
- 7 Ladder: [7, 14, 21, 28, 35, 42]
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
from collections import defaultdict


# ==============================================================================
# RC CONSTANTS
# ==============================================================================

RC_START_DATE = "18.03.2023"
RC_START_DRAW = [1, 3, 4, 7, 9, 23]  # 5 numbers from 1-9 decade!
RC_DATE_DIGIT_SUM = 28  # 1+8+0+3+2+0+2+3 = 28
EIGHT_COUNT_MAGIC = 8  # 28 + 8 = 36
RC_5_PATTERN = [5, 14, 23, 32, 41, 50, 104, 113, 122, 131, 140, 203, 212, 221, 230, 302, 311, 320, 401, 410, 500]
RC_CIRCLE_MULTIPLIER = 84  # 4 × 21

# ==============================================================================
# STORY 1: THE 26 FAMILY (from 42 tickets)
# ==============================================================================

STORY_26_FAMILY = {
    'main_ticket': [13, 26, 27, 30, 31, 38],
    'circles': {
        13: 34,
        26: 5,
        27: 6,
        30: 9,
        31: 10,
        38: 17
    },
    'description': 'The 26 family with circle swaps'
}

# ==============================================================================
# STORY 2: THE 18-39 CIRCLE PARTNERSHIP
# ==============================================================================

CIRCLE_18_39 = {
    'pair': (18, 39),
    '18_typical_pos': 3,  # P3 (58.5%)
    '39_typical_pos': 6,  # P6 (78%)
    'typical_gap': 3,     # 3 positions apart (61%)
    'common_companions': [32, 11, 25, 4, 42],
    'total_reunions': 41,
    'description': '18 at P3, 39 at P6, gap of 3'
}

# ==============================================================================
# STORY 3: THE 33-12 REUNION
# ==============================================================================

STORY_33_12 = {
    'pair': (33, 12),
    'last_reunion': '13.12.2025',
    'last_reunion_draw': [10, 11, 12, 33, 36, 38],
    'draws_apart': 30,  # As of Q1 2026 end
    'rule_12_position': [1, 2, 3],  # 12 must be P1-P3
    'rule_33_position': [4, 5, 6],  # 33 at P4-P6
    'p4_blocking': '12 at P4 blocks 33 (100%)',
    'description': '30 draws apart, waiting for reunion'
}

# ==============================================================================
# STORY 4: MR. 13 - THE HERO
# ==============================================================================

STORY_MR_13 = {
    'hero': 13,
    'circle': 34,
    'family': [10, 13, 14, 15, 21, 23, 31, 34],
    'throne_combo': [13, 14, 15],  # Sum = 42!
    'day_28_pattern': 'On Day 28, 13 claims P1',
    'jail_status': 'P8 = jail, track when free/jailed',
    'last_known_status': 'P1 on 28.03.2026'
}

# ==============================================================================
# STORY 5: THE 7 LADDER
# ==============================================================================

SEVEN_LADDER = [7, 14, 21, 28, 35, 42]  # All multiples of 7!
SEVEN_LADDER_COMBOS = {
    'p1_p6_42': [(7, 35), (14, 28), (21, 21)],  # P1+P6=42 combos
    'magical_draw': '14.06.2014',
    'description': 'All multiples of 7, contains multiple P1+P6=42 combos'
}

# ==============================================================================
# STORY 6: P4 PATTERNS
# ==============================================================================

P4_PATTERNS = {
    'p4_plus_m_equals_p5': 'On Day 28, P4 + M = P5',
    'p8_reveals_hungry': 'P8 = Circle of hungry middle number',
    'circle_of_d': 'When D >= 10, Circle(D) often = P4',
    'double_sum': 'When D+M <= 10, (D+M)×2 often = P4'
}

# ==============================================================================
# STORY 7: POSITION GAP PREDICTIONS (from last 3 draws)
# ==============================================================================

POSITION_GAPS = {
    'P1': {'gaps': [3, 7], 'next_predict': 20},
    'P2': {'gaps': [11, 1], 'next_predict': 18},
    'P3': {'gaps': [20, -8], 'next_predict': 11},
    'P4': {'gaps': [7, -2], 'next_predict': 24},
    'P5': {'gaps': [-2, -6], 'next_predict': 23},  # P5 series: 37→35→29→23
    'P6': {'gaps': [0, 1], 'next_predict': 41}
}

# ==============================================================================
# STORY 8: COLD NUMBERS (missing from last 3 draws)
# ==============================================================================

COLD_NUMBERS = [1, 2, 4, 8, 9, 10, 11, 12, 14, 15, 18, 20, 22, 23, 24]

# ==============================================================================
# 4+ SINGLES CYCLE
# ==============================================================================

CYCLE_MIN = 288
CYCLE_MAX = 305
CYCLE_AVG = 296

FOUR_PLUS_SINGLES_HISTORY = [
    ('23.11.2013', 90),
    ('29.10.2016', 395),
    ('30.01.2019', 629),
    ('03.11.2021', 917),
    ('18.03.2023', 1060),
    ('10.01.2024', 1145),
]

LAST_FOUR_PLUS_DATE = '10.01.2024'
LAST_FOUR_PLUS_RC = 85


# ==============================================================================
# HERO TRACKER - Track current hero and jail status
# ==============================================================================

class HeroTracker:
    """Track the current hero's journey - jail, free, throne"""
    
    def __init__(self):
        self.current_hero = 13  # Mr. 13 is the current hero
        self.hero_history = {
            13: {
                'name': 'Mr. 13',
                'status': 'free',  # free, jail, throne
                'last_position': 1,  # P1 on 28.03.2026
                'jail_count': 0,
                'throne_count': 2,  # P1 on 28.02 and 28.03
                'family': [10, 14, 15, 21, 23, 31, 34]
            }
        }
        self.next_hero_candidates = [33, 39, 26]  # Potential next heroes
    
    def update_hero_status(self, draw_nums: List[int], replay: int):
        """Update hero status based on latest draw"""
        hero = self.current_hero
        
        if replay == hero:
            self.hero_history[hero]['status'] = 'jail'
            self.hero_history[hero]['jail_count'] += 1
        elif hero in draw_nums:
            pos = sorted(draw_nums).index(hero) + 1
            self.hero_history[hero]['last_position'] = pos
            if pos == 1:
                self.hero_history[hero]['status'] = 'throne'
                self.hero_history[hero]['throne_count'] += 1
            else:
                self.hero_history[hero]['status'] = 'free'
        else:
            self.hero_history[hero]['status'] = 'hiding'
    
    def get_hero_prediction(self) -> Dict:
        """Get prediction based on hero's current status"""
        hero = self.current_hero
        status = self.hero_history[hero]['status']
        
        if status == 'jail':
            return {
                'hero': hero,
                'prediction': f'{hero} in jail - family members likely to appear',
                'hot_numbers': self.hero_history[hero]['family']
            }
        elif status == 'throne':
            return {
                'hero': hero,
                'prediction': f'{hero} was on throne - may stay or retreat',
                'hot_numbers': [hero] + self.hero_history[hero]['family'][:3]
            }
        else:
            return {
                'hero': hero,
                'prediction': f'{hero} is free - watch for return',
                'hot_numbers': [hero, hero + 1, hero - 1]
            }


# Initialize global hero tracker
HERO_TRACKER = HeroTracker()


def get_singles_cycle_info(rc: int) -> Dict:
    """
    Track where we are in the 4+ singles cycle.
    Based on REAL data: cycles range 143-305 draws, avg ~250.
    
    The cycle counts from the LAST 4+ singles event, not the jackpot!
    """
    # Gap since last 4+ singles (RC 85 = 10.01.2024)
    gap_since_last_4plus = rc - LAST_FOUR_PLUS_RC
    
    # Are we in the predicted window?
    in_window = CYCLE_MIN <= gap_since_last_4plus <= CYCLE_MAX
    approaching = gap_since_last_4plus >= (CYCLE_MIN - 30)
    
    # Next predicted window
    window_start_rc = LAST_FOUR_PLUS_RC + CYCLE_MIN
    window_end_rc = LAST_FOUR_PLUS_RC + CYCLE_MAX
    
    return {
        'current_rc': rc,
        'last_4plus_rc': LAST_FOUR_PLUS_RC,
        'last_4plus_date': LAST_FOUR_PLUS_DATE,
        'gap_since_last_4plus': gap_since_last_4plus,
        'in_rare_window': in_window,
        'approaching_window': approaching,
        'window_start_rc': window_start_rc,  # RC 373
        'window_end_rc': window_end_rc,      # RC 390
        'draws_to_window': max(0, window_start_rc - rc)
    }


def get_rc_circle_value(rc: int) -> Dict:
    """
    Calculate the RC Circle Value.
    Formula: RC - (floor(RC/100) × 84) = Circle Value
    Then apply -8 dance for hot number.
    
    Example:
      RC 100: 100 - 84 = 16
      RC 200: 200 - 168 = 32
      RC 300: 300 - 252 = 48
      RC 302: 302 - 252 = 50, 50-8 = 42 (THE MAX!)
    """
    n = rc // 100  # How many hundreds
    subtract = n * RC_CIRCLE_MULTIPLIER
    circle_value = rc - subtract
    
    # The -8 dance gives us a hot number
    dance_value = circle_value - EIGHT_COUNT_MAGIC
    if dance_value < 1:
        dance_value = circle_value + EIGHT_COUNT_MAGIC
    
    # Circle partner of the value (within 1-42 lotto range)
    if circle_value > 21:
        circle_partner = circle_value - 21
        while circle_partner > 42:
            circle_partner -= 21
    else:
        circle_partner = circle_value + 21
    
    return {
        'rc': rc,
        'hundreds': n,
        'subtracted': subtract,
        'circle_value': circle_value,
        'dance_value': dance_value,  # circle_value - 8
        'circle_partner': circle_partner,
        'hot_numbers': [
            n for n in [circle_value, dance_value, circle_partner] 
            if 1 <= n <= 42
        ]
    }


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


def calculate_rc_for_date(target_date: str) -> int:
    """
    Calculate exact RC number for a given date.
    RC = number of draws since 18.03.2023 (which is RC 0)
    Swiss Lotto: Wednesday (2) and Saturday (5)
    """
    rc_start = datetime.strptime(RC_START_DATE, "%d.%m.%Y")
    target = datetime.strptime(target_date, "%d.%m.%Y")
    
    if target < rc_start:
        return -1
    
    # Count Wed/Sat between dates
    count = 0
    current = rc_start
    while current <= target:
        if current.weekday() in [2, 5]:  # Wed or Sat
            count += 1
        current += timedelta(days=1)
    
    return count - 1  # RC 0 is the start date itself


def get_rc_sum(rc: int) -> int:
    """Get sum of RC digits"""
    if rc < 0:
        return 0
    return sum(int(d) for d in str(rc))


def is_rare_event_signal(rc: int) -> bool:
    """Check if RC number signals potential rare event (RC sum = 5)"""
    return get_rc_sum(rc) == 5


def get_eight_count_dance(start_num: int) -> int:
    """
    The 8-count dance: from any number, add 8 to find its dance partner.
    28 + 8 = 36 (RC origin connection)
    """
    return start_num + EIGHT_COUNT_MAGIC


def predict_p4_from_date(date_str: str) -> List[int]:
    """
    Predict P4 candidates based on Date Dance rules:
    - When D >= 10: Circle(D) = P4
    - When D+M <= 10: (D+M) × 2 = P4
    - Always consider: D×M + D+M
    """
    dn = get_date_numbers(date_str)
    d, m = dn['day'], dn['month']
    
    p4_candidates = []
    
    # Rule 1: Circle of D (when D >= 10)
    if d >= 10:
        circle_d = get_circle(d)
        if 1 <= circle_d <= 42:
            p4_candidates.append(circle_d)
    
    # Rule 2: (D+M) × 2 (when D+M <= 10)
    if d + m <= 10:
        double_sum = (d + m) * 2
        if 1 <= double_sum <= 42:
            p4_candidates.append(double_sum)
    
    # Rule 3: D×M + D+M (always)
    combo = d * m + d + m
    if 1 <= combo <= 42:
        p4_candidates.append(combo)
    
    return list(set(p4_candidates))


def detect_decade_clustering(nums: List[int]) -> Dict:
    """
    Analyze how many numbers from each decade.
    5+ from 1-9 decade = RARE EVENT!
    """
    decades = {
        '1-9': 0,
        '10-19': 0,
        '20-29': 0,
        '30-39': 0,
        '40-42': 0
    }
    
    for n in nums:
        if 1 <= n <= 9:
            decades['1-9'] += 1
        elif 10 <= n <= 19:
            decades['10-19'] += 1
        elif 20 <= n <= 29:
            decades['20-29'] += 1
        elif 30 <= n <= 39:
            decades['30-39'] += 1
        elif 40 <= n <= 42:
            decades['40-42'] += 1
    
    return {
        'distribution': decades,
        'is_rare': decades['1-9'] >= 5,
        'single_digit_count': decades['1-9']
    }


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
    7. P4 HUNTERS: Target the heart position
    8. RARE EVENT RADAR: When RC sum = 5, heavy single digits!
    9. THE 28→36 DANCE: 8-count magic
    """
    
    tickets = []
    
    # Get date numbers
    dn = get_date_numbers(target_date)
    d, m = dn['day'], dn['month']
    
    # Calculate RC for target date
    rc = calculate_rc_for_date(target_date)
    rc_digits = [int(x) for x in str(rc)] if rc > 0 else [0]
    rc_sum = get_rc_sum(rc)
    
    # Check if we're in the RARE WINDOW (based on real cycle data)
    cycle_info = get_singles_cycle_info(rc)
    is_in_rare_window = cycle_info['in_rare_window']
    is_approaching = cycle_info['approaching_window']
    
    # RC sum = 5 is still a signal, but not the only one
    rc_sum_is_5 = (rc_sum == 5)
    
    # Get P4 predictions
    p4_candidates = predict_p4_from_date(target_date)
    
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
    
    # Track 28 appearances for 8-count dance
    draws_with_28 = []
    for i, (date, nums, _, _) in enumerate(previous_draws[-10:]):
        if 28 in nums:
            draws_with_28.append((i, date))
    
    # If 28 appeared ~8 draws ago, 36 is HOT!
    thirty_six_is_hot = len(draws_with_28) > 0 and (10 - draws_with_28[-1][0]) >= 7
    
    # TICKET 1: DATE DANCE (P1-P3 focus)
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
            for n in top_frequent:
                if n not in t1_nums:
                    t1_nums.append(n)
                    break
    
    t1_nums = sorted(list(set(t1_nums)))[:6]
    tickets.append({
        'numbers': t1_nums,
        'lucky': rc_sum if 1 <= rc_sum <= 6 else d % 6 + 1,
        'story': 'DATE DANCE',
        'confidence': 'HIGH'
    })
    
    # TICKET 2: P4 HUNTERS (Target the heart!)
    t2_nums = p4_candidates.copy()
    # Add circles of P4 candidates
    for p4 in p4_candidates:
        c = get_circle(p4)
        if c not in t2_nums and 1 <= c <= 42:
            t2_nums.append(c)
    # Fill with date dance
    for n in [d, m, dn['d_minus_m'], dn['d_plus_m']]:
        if n and 1 <= n <= 42 and n not in t2_nums:
            t2_nums.append(n)
    t2_nums = sorted(list(set(t2_nums)))[:6]
    tickets.append({
        'numbers': t2_nums,
        'lucky': 4,  # P4!
        'story': 'P4 HUNTERS',
        'confidence': 'HIGH',
        'p4_targets': p4_candidates
    })
    
    # TICKET 3: RARE EVENT RADAR (Based on REAL cycle data!)
    # Activates when: in rare window OR approaching window OR RC sum = 5
    if is_in_rare_window:
        # IN THE WINDOW! Load up on single digits!
        t3_nums = [1, 3, 4, 7, 9]  # From the original jackpot
        t3_nums.append(23)  # The one double-digit from jackpot
        t3_story = f'RARE WINDOW ACTIVE! (Gap={cycle_info["gap_since_last_4plus"]})'
        t3_confidence = 'IN RARE WINDOW!'
    elif is_approaching:
        # Approaching window - start mixing singles
        t3_nums = [1, 3, 7, 9]  # Core singles
        t3_nums.extend([13, 23])  # Add some teens/twenties
        t3_story = f'APPROACHING RARE WINDOW (Gap={cycle_info["gap_since_last_4plus"]}, Window at {cycle_info["window_start_rc"]})'
        t3_confidence = 'ELEVATED'
    elif rc_sum_is_5:
        # RC sum = 5 is still notable
        t3_nums = [1, 3, 4, 7, 9, 23]
        t3_story = f'RC SUM=5 SIGNAL (RC {rc})'
        t3_confidence = 'MEDIUM-HIGH'
    else:
        # Normal mode: circle pairs
        t3_nums = [5, 26, 13, 34, 9, 30]
        t3_story = 'CIRCLE PAIRS'
        t3_confidence = 'MEDIUM'
    
    t3_nums = sorted(list(set(t3_nums)))[:6]
    tickets.append({
        'numbers': t3_nums,
        'lucky': 5,
        'story': t3_story,
        'confidence': t3_confidence,
        'rc': rc,
        'rc_sum': rc_sum,
        'cycle_info': {
            'gap': cycle_info['gap_since_last_4plus'],
            'window_start': cycle_info['window_start_rc'],
            'window_end': cycle_info['window_end_rc']
        }
    })
    
    # TICKET 4: THE 28→36 DANCE
    t4_nums = [28, 36]  # The core dance
    t4_nums.append(get_circle(28))  # 7
    t4_nums.append(get_circle(36))  # 15
    t4_nums.append(EIGHT_COUNT_MAGIC)  # 8
    # Add RC connection
    if rc_sum not in t4_nums and 1 <= rc_sum <= 42:
        t4_nums.append(rc_sum)
    else:
        t4_nums.append(RC_DATE_DIGIT_SUM - 21)  # 28-21=7, but we have that
        t4_nums.append(18)  # RC origin day
    t4_nums = sorted(list(set([n for n in t4_nums if 1 <= n <= 42])))[:6]
    tickets.append({
        'numbers': t4_nums,
        'lucky': 3,
        'story': '28→36 DANCE (8-COUNT)',
        'confidence': 'HIGH' if thirty_six_is_hot else 'MEDIUM',
        'thirty_six_hot': thirty_six_is_hot
    })
    
    # TICKET 5: HUNGRY REVENGE
    t5_nums = recent_hungry[:6] if len(recent_hungry) >= 6 else recent_hungry + top_frequent[:6-len(recent_hungry)]
    t5_nums = sorted(list(set(t5_nums)))[:6]
    tickets.append({
        'numbers': t5_nums,
        'lucky': 4,
        'story': 'HUNGRY REVENGE',
        'confidence': 'MEDIUM'
    })
    
    # TICKET 6: RC COUNT
    t6_nums = rc_digits.copy()
    t6_nums.append(rc_sum)
    t6_nums.append(21)  # The bridge
    for n in top_frequent:
        if n not in t6_nums and len(t6_nums) < 6:
            t6_nums.append(n)
    t6_nums = [n for n in t6_nums if 1 <= n <= 42]
    t6_nums = sorted(list(set(t6_nums)))[:6]
    tickets.append({
        'numbers': t6_nums,
        'lucky': 3,
        'story': f'RC COUNT (RC={rc})',
        'confidence': 'MEDIUM'
    })
    
    # TICKET 7: THE 13 FAMILY
    t7_nums = [13, 10, 21, 23, 31, 34]
    tickets.append({
        'numbers': sorted(t7_nums),
        'lucky': 5,
        'story': '13 FAMILY',
        'confidence': 'MEDIUM'
    })
    
    # TICKET 8: MEGA CONVERGENCE (When signals align!)
    # Combines: RC Circle, Date Dance, cycle position
    rc_circle = get_rc_circle_value(rc)
    t8_nums = []
    
    # From RC Circle calculation (still valid math)
    for n in rc_circle['hot_numbers']:
        if n not in t8_nums and 1 <= n <= 42:
            t8_nums.append(n)
    
    # From Date Dance
    date_nums = [dn['d_minus_m'], d, m, dn['d_plus_m']]
    for n in date_nums:
        if n and n not in t8_nums and 1 <= n <= 42 and len(t8_nums) < 6:
            t8_nums.append(n)
    
    # If in rare window, prioritize singles
    if is_in_rare_window:
        for n in [1, 3, 7, 9]:
            if n not in t8_nums and len(t8_nums) < 6:
                t8_nums.append(n)
    
    # D×M + D+M
    if dn['d_times_plus_sum'] and dn['d_times_plus_sum'] not in t8_nums and len(t8_nums) < 6:
        t8_nums.append(dn['d_times_plus_sum'])
    
    t8_nums = sorted(list(set([n for n in t8_nums if 1 <= n <= 42])))[:6]
    
    # Determine confidence
    t8_confidence = 'MEDIUM'
    if is_in_rare_window:
        t8_confidence = 'IN RARE WINDOW!'
    elif is_approaching and rc_sum_is_5:
        t8_confidence = 'HIGH (Approaching + RC sum=5)'
    elif rc_circle['dance_value'] in [21, 42]:
        t8_confidence = 'HIGH (Circle dance hit)'
    
    tickets.append({
        'numbers': t8_nums,
        'lucky': 6,
        'story': 'MEGA CONVERGENCE',
        'confidence': t8_confidence,
        'rc_circle_value': rc_circle['circle_value'],
        'rc_dance_value': rc_circle['dance_value'],
        'in_rare_window': is_in_rare_window
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

# P4 Rules
P4_RULES = {
    'circle_of_d': 'When D >= 10, Circle(D) often = P4',
    'double_sum': 'When D+M <= 10, (D+M)×2 often = P4',
    'date_combo': 'D×M + D+M is always a P4 candidate'
}

# Rare Event Signals
RARE_EVENT_SIGNALS = {
    'rc_sum_5': 'RC sum = 5 signals potential rare event',
    'single_digit_cluster': '5+ numbers from 1-9 decade = RARE',
    'date_alignment': 'When RC sum matches date = SIGNAL'
}

# The 28→36 Dance
DANCE_28_36 = {
    'origin': 'RC date digit sum = 28 (1+8+0+3+2+0+2+3)',
    'step': 8,
    'destination': 36,
    'circle_28': 7,
    'circle_36': 15,
    'circle_dance': '7 + 8 = 15 (circles also dance by 8!)'
}


def get_rare_event_analysis(target_date: str, previous_draws: List[Tuple]) -> Dict:
    """
    Full rare event analysis for a target date.
    CORRECTED: Based on real data showing ~288-305 draw cycles
    between 4+ singles events.
    """
    rc = calculate_rc_for_date(target_date)
    rc_sum = get_rc_sum(rc)
    dn = get_date_numbers(target_date)
    
    # Get cycle info (distance from last 4+ singles)
    cycle_info = get_singles_cycle_info(rc)
    
    signals = []
    probability = 'LOW'
    
    # Check if in rare window
    if cycle_info['in_rare_window']:
        signals.append(f'IN RARE WINDOW! (Gap={cycle_info["gap_since_last_4plus"]} draws)')
        probability = 'HIGH'
    elif cycle_info['approaching_window']:
        signals.append(f'Approaching rare window (Gap={cycle_info["gap_since_last_4plus"]}, Window at RC {cycle_info["window_start_rc"]})')
        probability = 'ELEVATED'
    
    # RC sum = 5 is still a signal
    if rc_sum == 5:
        signals.append(f'RC {rc} sum = 5')
        if probability == 'LOW':
            probability = 'MEDIUM'
    
    # Check if D-M is single digit
    if 1 <= dn['d_minus_m'] <= 9:
        signals.append(f"D-M = {dn['d_minus_m']} (single digit)")
    
    # Check if D+M produces jackpot numbers
    jackpot_nums = [1, 3, 4, 7, 9, 23]
    if dn['d_plus_m'] in jackpot_nums:
        signals.append(f"D+M = {dn['d_plus_m']} (jackpot number!)")
    
    # Check date connection to jackpot
    d, m = dn['day'], dn['month']
    if d in jackpot_nums:
        signals.append(f"Day {d} is a jackpot number!")
    if m in jackpot_nums:
        signals.append(f"Month {m} is a jackpot number!")
    
    return {
        'date': target_date,
        'rc': rc,
        'rc_sum': rc_sum,
        'signals': signals,
        'probability': probability,
        'cycle_info': cycle_info,
        'recommendation': 'LOAD SINGLE DIGITS!' if probability == 'HIGH' else (
            'Mix in more singles' if probability == 'ELEVATED' else 'Normal play'
        )
    }


def generate_combined_story_tickets(
    target_date: str,
    previous_draws: List[Tuple],
    num_tickets: int = 8
) -> List[Dict]:
    """
    Generate tickets combining ALL story patterns:
    - 26 Family (from 42 tickets)
    - 18-39 Circle Partnership  
    - 33-12 Reunion
    - Mr. 13 Hero Story
    - 7 Ladder
    - Position Gap Predictions
    - Cold Numbers
    - Date Dance
    - RC Patterns
    """
    
    tickets = []
    dn = get_date_numbers(target_date)
    d, m = dn['day'], dn['month']
    rc = calculate_rc_for_date(target_date)
    rc_sum = get_rc_sum(rc)
    
    # TICKET 1: 26 FAMILY + 18-39 CIRCLE
    t1 = [5, 18, 26, 27, 30, 39]
    tickets.append({
        'numbers': sorted(t1),
        'lucky': 5,
        'story': '26 FAMILY + 18-39 CIRCLE',
        'patterns': ['26 family', '18-39 circle', '26↔5']
    })
    
    # TICKET 2: 13 FAMILY + 33-12 REUNION
    t2 = [10, 12, 13, 31, 33, 34]
    tickets.append({
        'numbers': sorted(t2),
        'lucky': 1,
        'story': '13 FAMILY + 33-12 REUNION',
        'patterns': ['13 family', '33-12 reunion', '13↔34']
    })
    
    # TICKET 3: 18-39 + 33 HUNGRY MIDDLE + GAP P6
    t3 = [11, 18, 33, 36, 39, 41]
    tickets.append({
        'numbers': sorted(t3),
        'lucky': 3,
        'story': '18-39 CIRCLE + 33 HUNGRY + GAP',
        'patterns': ['18-39 circle', '33 hungry', 'P6 gap=41']
    })
    
    # TICKET 4: 26 STORY + 7 LADDER
    t4 = [6, 13, 26, 28, 35, 38]
    tickets.append({
        'numbers': sorted(t4),
        'lucky': 6,
        'story': '26 STORY + 7 LADDER',
        'patterns': ['26 family', '7 ladder (28,35)', '27↔6']
    })
    
    # TICKET 5: 33 HUNGER + P8 REVELATION + COLD
    t5 = [3, 11, 12, 32, 33, 34]
    tickets.append({
        'numbers': sorted(t5),
        'lucky': 6,
        'story': '33 HUNGER + P8 + COLD',
        'patterns': ['33=3×11', 'P8→32,33', 'cold 11,12']
    })
    
    # TICKET 6: DATE DANCE + 26↔5 + P5 SERIES
    t6_base = [dn['d_minus_m'], m, d, dn['d_plus_m']]
    t6_base = [n for n in t6_base if n and 1 <= n <= 42]
    t6_base.extend([5, 23, 26])  # Add story elements
    t6 = sorted(list(set(t6_base)))[:6]
    tickets.append({
        'numbers': t6,
        'lucky': 2,
        'story': 'DATE DANCE + 26 + P5 SERIES',
        'patterns': ['date dance', '26↔5', 'P5→23']
    })
    
    # TICKET 7: 7 LADDER (P1+P6=42)
    t7 = SEVEN_LADDER.copy()
    tickets.append({
        'numbers': t7,
        'lucky': 6,
        'story': '7 LADDER + P1+P6=42',
        'patterns': ['7 ladder', '7+35=42', '14+28=42']
    })
    
    # TICKET 8: TRIPLE REUNION (26↔5, 18↔39, 12↔33)
    t8 = [5, 12, 18, 26, 33, 39]
    tickets.append({
        'numbers': sorted(t8),
        'lucky': 4,
        'story': 'TRIPLE REUNION',
        'patterns': ['26↔5', '18↔39', '12↔33']
    })
    
    return tickets[:num_tickets]


def get_hero_status() -> Dict:
    """Get current hero (Mr. 13) status and prediction"""
    return HERO_TRACKER.get_hero_prediction()


def update_hero_from_draw(draw_nums: List[int], replay: int):
    """Update hero tracker with new draw"""
    HERO_TRACKER.update_hero_status(draw_nums, replay)


if __name__ == "__main__":
    # Test the generator
    print("Story Pattern Generator loaded!")
    print(f"Circle constant: {CIRCLE_CONSTANT}")
    print(f"13 Family: {FAMILY_13}")
    print(f"21/42 Family: {FAMILY_21_42}")
    print()
    print("=== STORY PATTERNS ===")
    print(f"26 Family: {STORY_26_FAMILY['main_ticket']}")
    print(f"18-39 Circle: {CIRCLE_18_39['pair']}")
    print(f"33-12 Reunion: {STORY_33_12['draws_apart']} draws apart")
    print(f"Mr. 13: {STORY_MR_13['hero']} with family {STORY_MR_13['family']}")
    print(f"7 Ladder: {SEVEN_LADDER}")
    print()
    print("=== RC PATTERNS ===")
    print(f"RC Date Sum: {RC_DATE_DIGIT_SUM}")
    print(f"8-Count Magic: {EIGHT_COUNT_MAGIC}")
    print()
    print("=== HERO STATUS ===")
    hero_status = get_hero_status()
    print(f"Current Hero: {hero_status['hero']}")
    print(f"Prediction: {hero_status['prediction']}")
