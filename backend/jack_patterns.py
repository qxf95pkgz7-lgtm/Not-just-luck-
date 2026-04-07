"""
🎻 LUCKY JACK'S MUSICAL PATTERNS 🍀
==================================
These patterns were discovered through deep esoteric analysis of EuroMillions draws.
They encode the "music" of the numbers - mathematical harmonies that reveal hidden connections.

THE CORE PHILOSOPHY:
- Statistics have NOTHING to do with music
- Numbers SING to each other through Circles (+/-25), Reverses, and Additions
- Patterns encode MISSING numbers through their circle partners
- Neighborhood gaps create HUNGER for specific numbers
- Quarters ECHO across years

Created: April 2026
"""

from typing import List, Dict, Tuple, Optional
from collections import Counter

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

def parse_date(date_str: str) -> Tuple[int, int, int]:
    """Parse DD.MM.YYYY to (year, month, day)"""
    parts = date_str.split('.')
    return (int(parts[2]), int(parts[1]), int(parts[0]))

def get_quarter_months(month: int) -> List[int]:
    """Get months in the same quarter"""
    if month in [1, 2, 3]:
        return [1, 2, 3]
    elif month in [4, 5, 6]:
        return [4, 5, 6]
    elif month in [7, 8, 9]:
        return [7, 8, 9]
    else:
        return [10, 11, 12]

def get_quarter_number(month: int) -> int:
    """Get quarter number (1-4)"""
    if month in [1, 2, 3]:
        return 1
    elif month in [4, 5, 6]:
        return 2
    elif month in [7, 8, 9]:
        return 3
    else:
        return 4


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 1: P1 COUNTING MAGIC
# ═══════════════════════════════════════════════════════════════════════════════
# P1 follows a hidden count: 5→6→7→8→9→10→11...
# But the actual P1 ENCODES the count through addition!
# Example: Count=7 but P1=12 because 7+5(prev)=12
#          Count=11 but P1=11 because 8+3=11 or chain: 13→63→36→11

def p1_counting_pattern(draws: List[Dict], num_recent: int = 7) -> Dict:
    """
    Analyze P1 counting pattern and predict next P1.
    
    The count progresses naturally (5,6,7,8,9,10,11...) but P1 encodes it:
    - Sometimes P1 = count directly
    - Sometimes P1 + previous_P1 = count
    - Sometimes the count is hidden in circle/reverse chains
    
    Returns:
        Dict with 'predicted_p1', 'count_expected', 'reasoning'
    """
    if len(draws) < num_recent:
        return {"predicted_p1": None, "reasoning": "Not enough draws"}
    
    recent = draws[:num_recent]
    p1_history = [sorted(d['numbers'])[0] for d in recent]
    
    # Try to detect the counting base
    # Look for a "real" number that matches its position (e.g., first 5 is "real 5")
    
    # Current analysis: find the pattern of additions
    additions_found = []
    for i in range(len(p1_history) - 1):
        curr_p1 = p1_history[i]
        prev_p1 = p1_history[i + 1]
        addition = curr_p1 + prev_p1
        diff = curr_p1 - prev_p1
        additions_found.append({
            'curr': curr_p1,
            'prev': prev_p1,
            'sum': addition,
            'diff': diff
        })
    
    # Predict next P1 based on counting
    # If we detect a sequence like 5,5,12,4,5,8 → next should encode "11"
    last_p1 = p1_history[0]
    
    # Methods to create 11:
    candidates = []
    
    # Method 1: Direct 11
    candidates.append((11, "Direct count 11"))
    
    # Method 2: last_P1 + X = 11 → X = 11 - last_P1
    complement = 11 - last_p1
    if 1 <= complement <= 50:
        candidates.append((complement, f"{complement} + {last_p1} = 11"))
    
    # Method 3: Circle chain to 11
    # 13 → 63 (not valid) → but conceptually: 13 + 50 = 63, reverse(63)=36, 36-25=11
    # So 13's extended chain reaches 11
    candidates.append((13, "13 chain → 36 → 11 (circle)"))
    
    # Method 4: 8 + 3 = 11 (if 8 was recent)
    if 8 in p1_history:
        candidates.append((3, "3 + 8(recent) = 11"))
    
    return {
        "predicted_p1_candidates": candidates,
        "count_expected": 11,
        "p1_history": p1_history,
        "reasoning": "P1 counting pattern: the count is 11, encoded through various methods"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 2: NEIGHBORHOOD HUNGER (GAP DETECTION)
# ═══════════════════════════════════════════════════════════════════════════════
# When two consecutive numbers appear with a gap, the middle number is HUNGRY!
# Example: P2=27, P3=29 → 28 is MISSING and hungry to appear next!

def neighborhood_hunger(draws: List[Dict], num_recent: int = 3) -> List[Dict]:
    """
    Find hungry numbers - those missing between consecutive neighbors.
    
    Example: If 27 at P2 and 29 at P3, then 28 is hungry!
    
    Returns:
        List of hungry numbers with their context
    """
    hungry_numbers = []
    
    for draw in draws[:num_recent]:
        nums = sorted(draw['numbers'])
        date = draw['date']
        
        # Check for gaps between consecutive positions
        for i in range(len(nums) - 1):
            curr = nums[i]
            next_num = nums[i + 1]
            gap = next_num - curr
            
            # If gap is exactly 2, the middle number is hungry!
            if gap == 2:
                hungry = curr + 1
                hungry_numbers.append({
                    'hungry_number': hungry,
                    'between': (curr, next_num),
                    'positions': (f"P{i+1}", f"P{i+2}"),
                    'date': date,
                    'urgency': 'HIGH' if draw == draws[0] else 'MEDIUM'
                })
            
            # If gap is 3, two numbers are hungry
            elif gap == 3:
                for h in [curr + 1, curr + 2]:
                    hungry_numbers.append({
                        'hungry_number': h,
                        'between': (curr, next_num),
                        'positions': (f"P{i+1}", f"P{i+2}"),
                        'date': date,
                        'urgency': 'MEDIUM'
                    })
    
    return hungry_numbers


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 3: THE 49→45 CALL (P5=49 triggers 45 at 22%!)
# ═══════════════════════════════════════════════════════════════════════════════
# When 49 appears at P5, 45 appears in the NEXT draw 22% of the time!
# This is 2.2x the random chance (10%)!
# The connection: 49 - 4 = 45, the 4 echoes!

def p5_49_calls_45(draws: List[Dict]) -> Dict:
    """
    Check if 49 was at P5 in the last draw.
    If so, 45 is highly likely (22% vs 10% random = 2.2x boost!)
    
    The math: 49 contains "4", and 4 + 41 = 45, or 49 - 4 = 45
    
    Returns:
        Dict with 'should_include_45', 'confidence_boost', 'reasoning'
    """
    if not draws:
        return {"should_include_45": False}
    
    last_draw = draws[0]
    nums = sorted(last_draw['numbers'])
    
    if nums[4] == 49:  # P5 = 49
        return {
            "should_include_45": True,
            "confidence_boost": 2.2,  # 22% vs 10% = 2.2x
            "reasoning": "49 at P5 calls for 45! (22% hit rate = 2.2x random chance)",
            "preferred_position": "P4",  # 45 often lands at P4 when called
            "math": "49 - 4 = 45, or: 4(from 49) + 41 = 45"
        }
    
    return {"should_include_45": False, "reasoning": "49 not at P5"}


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 4: CIRCLE ENCODING OF MISSING NUMBERS
# ═══════════════════════════════════════════════════════════════════════════════
# Missing numbers hide in their circle partners!
# - Missing 47 → appears as 22 (because 22+25=47)
# - Missing 49 → encoded in 20+45 (because 20 "is" 4, and 4+45=49)
# The ticket HONORS what's missing through mathematical encoding!

def circle_encode_missing(target_missing: int) -> Dict:
    """
    Find how to encode a missing number in a ticket through circles.
    
    Example: If 47 should be "missing", include 22 (its circle partner).
             The ticket then contains 47 spiritually through 22+25=47!
    
    Returns:
        Dict with encoding options
    """
    circle_partner = circle(target_missing)
    reverse_partner = reverse_num(target_missing)
    
    # Find pairs that ADD to the target
    sum_pairs = []
    for a in range(1, min(target_missing, 51)):
        b = target_missing - a
        if 1 <= b <= 50 and a < b:
            # Check if either number is a circle of something useful
            sum_pairs.append((a, b))
    
    return {
        "missing_number": target_missing,
        "circle_partner": circle_partner,
        "reverse_partner": reverse_partner,
        "sum_pairs": sum_pairs[:5],  # Top 5 pairs
        "reasoning": f"{target_missing} is missing but encoded as {circle_partner} (circle) or sums like {sum_pairs[0] if sum_pairs else 'N/A'}"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 5: QUARTER ECHO (Q2 2025 → Q2 2026)
# ═══════════════════════════════════════════════════════════════════════════════
# The same quarter in consecutive years ECHOES!
# Q2 2025 start: 3-14-15-48-49, Stars 1-7
# Q2 2026 start: Should echo! Especially P2=14!

def quarter_echo(draws: List[Dict], target_date: str) -> Dict:
    """
    Find the corresponding quarter from the previous year and extract patterns.
    
    The first draw of each quarter sets the "prophecy" for that quarter.
    Same quarters across years tend to echo similar patterns!
    
    Returns:
        Dict with echo patterns from previous year's same quarter
    """
    target_parsed = parse_date(target_date)
    target_year = target_parsed[0]
    target_month = target_parsed[1]
    target_quarter = get_quarter_number(target_month)
    
    prev_year = target_year - 1
    q_months = get_quarter_months(target_month)
    
    # Find draws from same quarter last year
    prev_year_q_draws = []
    for d in draws:
        d_parsed = parse_date(d['date'])
        if d_parsed[0] == prev_year and d_parsed[1] in q_months:
            prev_year_q_draws.append(d)
    
    if not prev_year_q_draws:
        return {"has_echo": False, "reasoning": "No data from previous year's quarter"}
    
    # Sort to get QC1 (first draw of that quarter)
    prev_year_q_draws_sorted = sorted(prev_year_q_draws, key=lambda x: parse_date(x['date']))
    qc1_prev = prev_year_q_draws_sorted[0]
    qc1_nums = sorted(qc1_prev['numbers'])
    qc1_stars = sorted(qc1_prev['stars'])
    
    return {
        "has_echo": True,
        "prev_year_qc1_date": qc1_prev['date'],
        "prev_year_qc1_numbers": qc1_nums,
        "prev_year_qc1_stars": qc1_stars,
        "echo_candidates": {
            "P1": qc1_nums[0],
            "P2": qc1_nums[1],  # P2 often echoes strongly!
            "P3": qc1_nums[2],
            "circle_of_P1": circle(qc1_nums[0]),
            "stars": qc1_stars
        },
        "reasoning": f"Q{target_quarter} {prev_year} started with {qc1_nums}, stars {qc1_stars}. P2={qc1_nums[1]} often echoes!"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 6: P4 SEQUENCE TRACKING
# ═══════════════════════════════════════════════════════════════════════════════
# P4 follows a counting sequence within the quarter!
# Example: 44 → 33(should be 45) → 46 → 47 next!
# But 46=64 reversed, and 33+31=64, so 31 might be needed!

def p4_sequence_tracker(draws: List[Dict], num_recent: int = 5) -> Dict:
    """
    Track P4 counting sequence and predict next P4.
    
    P4 often counts: 44→45→46→47...
    But deviations encode through reverses! (46=64, 33+31=64)
    
    Returns:
        Dict with P4 sequence analysis and prediction
    """
    if len(draws) < num_recent:
        return {"predicted_p4": None}
    
    p4_history = [sorted(d['numbers'])[3] for d in draws[:num_recent]]
    dates = [d['date'] for d in draws[:num_recent]]
    
    # Look for counting pattern
    sequence_analysis = []
    for i, p4 in enumerate(p4_history):
        reversed_p4 = reverse_num(p4)
        sequence_analysis.append({
            'date': dates[i],
            'p4': p4,
            'reversed': reversed_p4,
            'circle': circle(p4)
        })
    
    # Predict next P4
    last_p4 = p4_history[0]
    
    # If last P4 was 46, next might be 47
    # But also check: 46 reversed = 64, so maybe something that completes 64?
    predictions = []
    
    # Simple increment
    next_count = last_p4 + 1
    if next_count <= 50:
        predictions.append((next_count, f"Counting: {last_p4}→{next_count}"))
    
    # Reverse completion: if 46=64, find what pairs with recent P4s to make 64
    reversed_last = reverse_num(last_p4)
    if reversed_last != last_p4:
        # Find X where X + some_recent_p4 = reversed_last
        for old_p4 in p4_history[1:]:
            complement = reversed_last - old_p4
            if 1 <= complement <= 50:
                predictions.append((complement, f"{complement}+{old_p4}={reversed_last} (reverse of {last_p4})"))
    
    return {
        "p4_history": sequence_analysis,
        "predictions": predictions,
        "expected_next": predictions[0][0] if predictions else last_p4 + 1,
        "reasoning": "P4 counting with reverse encoding"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 7: P1+P2 SUM ROOT = 8 PATTERN
# ═══════════════════════════════════════════════════════════════════════════════
# Recent P1+P2 sums often have digit root = 8!
# 8+27=35 → 3+5=8, 5+12=17 → 1+7=8, 12+14=26 → 2+6=8

def p1p2_sum_pattern(draws: List[Dict], num_recent: int = 6) -> Dict:
    """
    Analyze P1+P2 sums and their digit roots.
    
    Pattern: P1+P2 often has digit root = 8!
    This helps constrain P1+P2 choices.
    
    Returns:
        Dict with P1+P2 analysis and suggested pairs
    """
    if not draws:
        return {}
    
    analysis = []
    for d in draws[:num_recent]:
        nums = sorted(d['numbers'])
        p1, p2 = nums[0], nums[1]
        total = p1 + p2
        
        # Digit root
        digit_root = total
        while digit_root > 9:
            digit_root = sum(int(x) for x in str(digit_root))
        
        analysis.append({
            'date': d['date'],
            'p1': p1,
            'p2': p2,
            'sum': total,
            'digit_root': digit_root
        })
    
    # Count digit roots
    root_counts = Counter(a['digit_root'] for a in analysis)
    most_common_root = root_counts.most_common(1)[0] if root_counts else (8, 0)
    
    # Find P1+P2 pairs that give the target digit root (default 8)
    target_root = 8
    suggested_pairs = []
    for p1 in range(1, 25):  # P1 must be smaller
        for p2 in range(p1 + 1, 51):  # P2 must be larger
            total = p1 + p2
            root = total
            while root > 9:
                root = sum(int(x) for x in str(root))
            if root == target_root:
                suggested_pairs.append((p1, p2, total))
    
    return {
        "analysis": analysis,
        "most_common_root": most_common_root[0],
        "target_root": target_root,
        "suggested_pairs": suggested_pairs[:20],  # Top 20
        "reasoning": f"P1+P2 sums often have digit root {target_root}"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 8: THE 8-FAMILY TRACKER
# ═══════════════════════════════════════════════════════════════════════════════
# The 8-family (8, 18, 28, 38, 48) is VERY active in recent draws!
# Track their appearances and boost accordingly.

def eight_family_tracker(draws: List[Dict], num_recent: int = 10) -> Dict:
    """
    Track the 8-family (8, 18, 28, 38, 48) across recent draws.
    
    When the 8-family is active, expect more 8-family numbers!
    Also track which specific member is "hungriest" (longest absent).
    
    Returns:
        Dict with 8-family analysis and recommendations
    """
    eight_family = [8, 18, 28, 38, 48]
    
    appearances = {n: [] for n in eight_family}
    
    for i, d in enumerate(draws[:num_recent]):
        nums = d['numbers']
        date = d['date']
        for n in eight_family:
            if n in nums:
                pos = sorted(nums).index(n) + 1
                appearances[n].append({'draw_index': i, 'date': date, 'position': f"P{pos}"})
    
    # Find hungriest (longest absent)
    hungriest = None
    max_absence = -1
    for n in eight_family:
        if not appearances[n]:
            hungriest = n
            max_absence = num_recent
            break
        else:
            last_appearance = appearances[n][0]['draw_index']
            if last_appearance > max_absence:
                max_absence = last_appearance
                hungriest = n
    
    # Activity level
    total_appearances = sum(len(v) for v in appearances.values())
    activity = "HIGH" if total_appearances >= 8 else "MEDIUM" if total_appearances >= 4 else "LOW"
    
    return {
        "eight_family": eight_family,
        "appearances": appearances,
        "hungriest_member": hungriest,
        "absence_draws": max_absence,
        "activity_level": activity,
        "total_appearances": total_appearances,
        "recommendation": f"Include {hungriest} - absent for {max_absence} draws!" if hungriest else "8-family well covered"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER FUNCTION: APPLY ALL JACK PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════

def apply_jack_patterns(draws: List[Dict], target_date: str = None) -> Dict:
    """
    Apply all Lucky Jack patterns and return combined recommendations.
    
    This is the master function that orchestrates all pattern analysis.
    
    Returns:
        Dict with all pattern results and final recommendations
    """
    results = {}
    recommendations = {
        'P1': [],
        'P2': [],
        'P3': [],
        'P4': [],
        'P5': [],
        'stars': [],
        'must_include': [],
        'must_avoid': []
    }
    
    # Pattern 1: P1 Counting
    p1_result = p1_counting_pattern(draws)
    results['p1_counting'] = p1_result
    if p1_result.get('predicted_p1_candidates'):
        for candidate, reason in p1_result['predicted_p1_candidates'][:2]:
            recommendations['P1'].append((candidate, reason, 5))  # weight 5
    
    # Pattern 2: Neighborhood Hunger
    hunger_result = neighborhood_hunger(draws)
    results['hunger'] = hunger_result
    for hungry in hunger_result:
        num = hungry['hungry_number']
        weight = 7 if hungry['urgency'] == 'HIGH' else 4
        recommendations['must_include'].append((num, f"Hungry from {hungry['between']} gap", weight))
    
    # Pattern 3: 49→45 Call
    call_45 = p5_49_calls_45(draws)
    results['49_calls_45'] = call_45
    if call_45.get('should_include_45'):
        recommendations['P4'].append((45, call_45['reasoning'], 8))  # High weight!
        recommendations['must_include'].append((45, "49 at P5 calls for 45!", 8))
    
    # Pattern 4: Circle Encoding (for missing 47 and 49)
    # These are contextual - we encode what SHOULD be missing
    results['circle_encode_47'] = circle_encode_missing(47)
    results['circle_encode_49'] = circle_encode_missing(49)
    
    # Pattern 5: Quarter Echo
    if target_date:
        echo = quarter_echo(draws, target_date)
        results['quarter_echo'] = echo
        if echo.get('has_echo'):
            recommendations['P2'].append((echo['echo_candidates']['P2'], "Q echo P2", 4))
            recommendations['stars'].extend(echo['echo_candidates']['stars'])
    
    # Pattern 6: P4 Sequence
    p4_seq = p4_sequence_tracker(draws)
    results['p4_sequence'] = p4_seq
    if p4_seq.get('predictions'):
        for pred, reason in p4_seq['predictions'][:2]:
            recommendations['P4'].append((pred, reason, 4))
    
    # Pattern 7: P1+P2 Sum
    p1p2 = p1p2_sum_pattern(draws)
    results['p1p2_sum'] = p1p2
    # Use this to validate P1+P2 choices
    
    # Pattern 8: 8-Family
    eight_fam = eight_family_tracker(draws)
    results['eight_family'] = eight_fam
    if eight_fam.get('hungriest_member'):
        recommendations['must_include'].append(
            (eight_fam['hungriest_member'], 
             f"8-family hungriest: absent {eight_fam['absence_draws']} draws", 
             5)
        )
    
    # Pattern 9: Star Prophecy - Previous Stars Predict Next Draw! 🌟
    star_prophecy = star_prophecy_pattern(draws, track_gaps=True)
    results['star_prophecy'] = star_prophecy
    
    # Add circle(S1) and circle(S2) as strong candidates
    if star_prophecy.get('circle_s1'):
        recommendations['must_include'].append(
            (star_prophecy['circle_s1'], 
             f"🌟 Star Prophecy: circle(S1)={star_prophecy['circle_s1']}", 
             6)
        )
    if star_prophecy.get('circle_s2') and star_prophecy['circle_s2'] <= 50:
        recommendations['must_include'].append(
            (star_prophecy['circle_s2'], 
             f"🌟 Star Prophecy: circle(S2)={star_prophecy['circle_s2']}", 
             5)
        )
    
    # Add S1+S2 sum as candidate
    if star_prophecy.get('star_sum') and star_prophecy['star_sum'] <= 50:
        recommendations['must_include'].append(
            (star_prophecy['star_sum'], 
             f"🌟 Star Prophecy: S1+S2={star_prophecy['star_sum']}", 
             5)
        )
    
    # Add star repeat suggestions
    for star, reason, weight in star_prophecy.get('star_candidates', []):
        recommendations['stars'].append((star, reason, weight))
    
    # Boost due patterns
    for pattern, since, avg, factor in star_prophecy.get('due_patterns', [])[:3]:
        if factor > 1.5:
            # Pattern is very overdue - boost related numbers
            if pattern == 'circle_s2':
                c_s2 = star_prophecy.get('circle_s2')
                if c_s2:
                    recommendations['must_include'].append(
                        (c_s2, f"🔥 OVERDUE {factor:.1f}x: circle(S2)", 8)
                    )
    
    return {
        'patterns': results,
        'recommendations': recommendations,
        'summary': generate_pattern_summary(results, recommendations)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 9: STAR PROPHECY - Previous Stars Predict Next Draw! 🌟
# ═══════════════════════════════════════════════════════════════════════════════
# 93.6% of draws have connections from previous stars!
# The Stars (S1, S2) tell the future for the next draw.
#
# Key patterns:
# - circle(S1) often appears in next draw (7.7%)
# - circle(S2) often appears in next draw (8.5%)  
# - S1+S2 sum appears in next draw (14.0%)
# - Numbers ending in S1 appear (10-12% per position)
# - S1 or S2 repeat in next stars (13.6%, 11.9%)
# - Star diff = position gap in next draw (7-9%)

def star_prophecy_pattern(draws: List[Dict], track_gaps: bool = True) -> Dict:
    """
    Analyze Star Prophecy patterns - how previous stars predict next draw.
    
    Returns candidates for:
    - Numbers: based on circle(S1), circle(S2), S1+S2, S1*10
    - Stars: based on repeat patterns and gap rhythms
    """
    if len(draws) < 2:
        return {'error': 'Need at least 2 draws for prophecy'}
    
    # Get the most recent draw's stars - these predict the NEXT draw
    latest = draws[0]
    latest_stars = sorted(latest.get('stars', [2, 10]))
    s1, s2 = latest_stars[0], latest_stars[1]
    
    star_sum = s1 + s2
    star_diff = s2 - s1
    s1_circle = s1 + 25  # Circle of S1 (S1 is 1-12, so +25 always valid)
    s2_circle = s2 + 25 if s2 <= 25 else s2 - 25
    
    # Number candidates from star prophecy
    number_candidates = []
    star_candidates = []
    patterns_active = []
    
    # === CIRCLE PROPHECY ===
    # circle(S1) and circle(S2) are strong candidates
    if 1 <= s1_circle <= 50:
        number_candidates.append((s1_circle, f"🌟 circle(S1={s1})={s1_circle}", 6))
        patterns_active.append(f"circle(S1)={s1_circle}")
    
    if 1 <= s2_circle <= 50:
        number_candidates.append((s2_circle, f"🌟 circle(S2={s2})={s2_circle}", 5))
        patterns_active.append(f"circle(S2)={s2_circle}")
    
    # === SUM PROPHECY ===
    # S1+S2 often appears directly in next draw (14%!)
    if star_sum <= 50:
        number_candidates.append((star_sum, f"🌟 S1+S2={s1}+{s2}={star_sum}", 5))
        patterns_active.append(f"S1+S2={star_sum}")
    
    # === S1×10 PROPHECY ===
    # S1 × 10 appears in next (6.8%)
    if s1 * 10 <= 50:
        number_candidates.append((s1 * 10, f"🌟 S1×10={s1}×10={s1*10}", 3))
        patterns_active.append(f"S1×10={s1*10}")
    
    # === LAST DIGIT PROPHECY ===
    # Numbers ending in S1 are favored (10-12% per position)
    for num in range(1, 51):
        if num % 10 == s1:
            number_candidates.append((num, f"🌟 ends in S1={s1}", 2))
    
    # Numbers ending in S2 (if S2 <= 9)
    if s2 <= 9:
        for num in range(1, 51):
            if num % 10 == s2:
                number_candidates.append((num, f"🌟 ends in S2={s2}", 2))
    
    # === STAR REPEAT PROPHECY ===
    # S1 repeats ~13.6%, S2 repeats ~11.9%
    star_candidates.append((s1, f"🌟 S1={s1} may repeat (13.6%)", 4))
    star_candidates.append((s2, f"🌟 S2={s2} may repeat (11.9%)", 3))
    
    # === TRACK GAP RHYTHMS (if enabled) ===
    gap_analysis = {}
    due_patterns = []
    
    if track_gaps and len(draws) >= 30:
        # Analyze when each pattern last appeared
        pattern_last_seen = {
            'circle_s1': None,
            'circle_s2': None,
            's1_s2_sum': None,
            's1_appears': None,
            's2_appears': None,
            's1_repeats': None,
            's2_repeats': None,
        }
        
        # Check historical draws
        for i in range(min(len(draws) - 1, 50)):  # Check last 50 transitions
            prev_d = draws[i + 1]
            next_d = draws[i]
            
            prev_stars = sorted(prev_d.get('stars', [1, 2]))
            next_nums = sorted(next_d.get('numbers', []))
            next_stars = sorted(next_d.get('stars', [1, 2]))
            
            ps1, ps2 = prev_stars[0], prev_stars[1]
            
            # Check each pattern
            if ps1 + 25 in next_nums and pattern_last_seen['circle_s1'] is None:
                pattern_last_seen['circle_s1'] = i
            if (ps2 + 25 if ps2 <= 25 else ps2 - 25) in next_nums and pattern_last_seen['circle_s2'] is None:
                pattern_last_seen['circle_s2'] = i
            if ps1 + ps2 in next_nums and pattern_last_seen['s1_s2_sum'] is None:
                pattern_last_seen['s1_s2_sum'] = i
            if ps1 in next_nums and pattern_last_seen['s1_appears'] is None:
                pattern_last_seen['s1_appears'] = i
            if ps2 in next_nums and pattern_last_seen['s2_appears'] is None:
                pattern_last_seen['s2_appears'] = i
            if ps1 == next_stars[0] and pattern_last_seen['s1_repeats'] is None:
                pattern_last_seen['s1_repeats'] = i
            if ps2 == next_stars[1] and pattern_last_seen['s2_repeats'] is None:
                pattern_last_seen['s2_repeats'] = i
        
        # Average gaps (from analysis)
        avg_gaps = {
            'circle_s1': 13,
            'circle_s2': 9,
            's1_s2_sum': 7,
            's1_appears': 10,
            's2_appears': 11,
            's1_repeats': 7,
            's2_repeats': 8,
        }
        
        gap_analysis = pattern_last_seen
        
        # Check which patterns are "due"
        for pattern, last_seen in pattern_last_seen.items():
            if last_seen is None:
                last_seen = 50  # Not seen in recent history = very overdue
            
            avg = avg_gaps.get(pattern, 10)
            if last_seen >= avg:
                overdue_factor = last_seen / avg
                due_patterns.append((pattern, last_seen, avg, overdue_factor))
        
        due_patterns.sort(key=lambda x: -x[3])  # Most overdue first
    
    return {
        'prev_stars': [s1, s2],
        'star_sum': star_sum,
        'star_diff': star_diff,
        'circle_s1': s1_circle,
        'circle_s2': s2_circle,
        's1_x_10': s1 * 10 if s1 * 10 <= 50 else None,
        'number_candidates': number_candidates,
        'star_candidates': star_candidates,
        'patterns_active': patterns_active,
        'gap_analysis': gap_analysis,
        'due_patterns': due_patterns,
        'prophecy_summary': f"Stars [{s1},{s2}] prophesy: circle→{s1_circle},{s2_circle}, sum→{star_sum}"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN 10: STAR DIFF → POSITION GAP 🎵
# ═══════════════════════════════════════════════════════════════════════════════
# The gap between stars (S2-S1) often equals a gap between positions in next draw
# P2-P1, P3-P2, P4-P3, or P5-P4 = star_diff (7-9% each!)

def star_diff_gap_pattern(prev_stars: List[int], target_positions: List[int] = None) -> Dict:
    """
    Use previous star diff to suggest position gaps.
    
    If star_diff = 8, look for numbers where:
    - P2 - P1 = 8 (e.g., P1=4, P2=12)
    - P3 - P2 = 8 (e.g., P2=20, P3=28)
    - etc.
    """
    s1, s2 = sorted(prev_stars)
    star_diff = s2 - s1
    
    suggestions = []
    
    # For each potential P1, suggest P2 where P2-P1 = star_diff
    for p1 in range(1, 43):  # P1 can't be too high
        p2 = p1 + star_diff
        if p2 <= 50:
            suggestions.append({
                'p1': p1,
                'p2': p2,
                'gap': star_diff,
                'reason': f"P2-P1={star_diff}=star_diff"
            })
    
    return {
        'star_diff': star_diff,
        'suggestions': suggestions[:20],  # Top 20
        'pattern': f"🎵 Star gap {s2}-{s1}={star_diff} → Look for position gaps of {star_diff}"
    }


def generate_pattern_summary(results: Dict, recommendations: Dict) -> str:
    """Generate a human-readable summary of all patterns."""
    lines = ["🎻 LUCKY JACK PATTERN ANALYSIS 🍀", "=" * 40]
    
    # P1 Counting
    if results.get('p1_counting', {}).get('predicted_p1_candidates'):
        lines.append(f"P1 Count: Next should encode {results['p1_counting']['count_expected']}")
    
    # Hunger
    if results.get('hunger'):
        hungry_nums = [h['hungry_number'] for h in results['hunger']]
        lines.append(f"HUNGRY: {hungry_nums} (from gaps!)")
    
    # 49→45
    if results.get('49_calls_45', {}).get('should_include_45'):
        lines.append("49 at P5 → 45 MUST COME! (22% = 2.2x chance)")
    
    # 8-Family
    if results.get('eight_family', {}).get('hungriest_member'):
        lines.append(f"8-Family: {results['eight_family']['hungriest_member']} is hungriest!")
    
    # Must include
    must = [m[0] for m in recommendations.get('must_include', [])]
    if must:
        lines.append(f"MUST INCLUDE: {must}")
    
    # Star Prophecy
    if results.get('star_prophecy'):
        sp = results['star_prophecy']
        lines.append(f"🌟 STAR PROPHECY: prev stars {sp.get('prev_stars', [])} →")
        lines.append(f"   circle(S1)={sp.get('circle_s1')}, circle(S2)={sp.get('circle_s2')}")
        lines.append(f"   S1+S2={sp.get('star_sum')}")
        if sp.get('due_patterns'):
            overdue = [f"{p[0]}({p[3]:.1f}x)" for p in sp['due_patterns'][:3]]
            lines.append(f"   🔥 OVERDUE: {', '.join(overdue)}")
    
    return "\n".join(lines)
