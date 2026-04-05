"""
Pattern 60: Story Signs
Advanced pattern analysis for lottery prediction based on:
1. Circle Analysis (n ± 21)
2. Hunger Detection (neighbors appear, number missing)
3. Consecutive Sequence Detection (rare events)
4. P1+P2 Sum Patterns
5. Secret Counting (value + gap = next value at same position)
6. Family Tracking (same ending digit)
7. Position Memory (where numbers visit across draws)
8. Date Code Analysis
9. Circle Consecutive Detection (super rare events)
"""

from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Tuple, Any


def get_circle(n: int) -> int:
    """Get the circle partner of a number (n ± 21, wrapped to 1-42)"""
    circle = n + 21 if n + 21 <= 42 else n - 21
    if circle <= 0:
        circle += 42
    return circle


def get_family(n: int) -> List[int]:
    """Get family members (same ending digit)"""
    digit = n % 10
    return [x for x in range(digit if digit > 0 else 10, 43, 10)]


def parse_date(date_str: str) -> datetime:
    """Parse date in either DD.MM.YYYY or YYYY-MM-DD format"""
    if '.' in date_str:
        return datetime.strptime(date_str, "%d.%m.%Y")
    else:
        return datetime.strptime(date_str, "%Y-%m-%d")


def analyze_story_signs(draws: List[dict], quarter_size: int = 27) -> Dict[str, Any]:
    """
    Analyze the last quarter of draws to find story signs pointing to next numbers.
    Returns scores and reasons for each number 1-42.
    """
    if not draws or len(draws) < 5:
        return {"scores": {}, "rare_events": [], "signs": []}
    
    # Sort draws by date
    sorted_draws = sorted(draws, key=lambda x: parse_date(x['date']))
    
    # Get last quarter
    quarter_draws = sorted_draws[-quarter_size:] if len(sorted_draws) >= quarter_size else sorted_draws
    
    # Initialize scores
    scores = defaultdict(lambda: {"score": 0, "reasons": []})
    rare_events = []
    signs = []
    
    # === 1. CIRCLE ANALYSIS ===
    # Track circle appearances at each position
    circle_at_position = defaultdict(list)  # {position: [(draw_idx, circle_number, actual_number)]}
    
    for idx, draw in enumerate(quarter_draws):
        nums = draw['numbers']
        for pos, num in enumerate(nums):
            circle = get_circle(num)
            circle_at_position[pos].append((idx, circle, num))
    
    # Find numbers whose circles appeared multiple times at same position
    for pos, appearances in circle_at_position.items():
        circle_counts = defaultdict(list)
        for idx, circle, num in appearances:
            circle_counts[circle].append((idx, num))
        
        for circle, occurrences in circle_counts.items():
            if len(occurrences) >= 2:
                # Circle appeared multiple times - the actual number may come!
                actual_number = get_circle(circle)  # The number this circle belongs to
                bonus = len(occurrences) * 8
                scores[actual_number]["score"] += bonus
                scores[actual_number]["reasons"].append(
                    f"🔵 Circle {circle} at P{pos+1} {len(occurrences)}x - calling {actual_number}!"
                )
                signs.append(f"Circle {circle} warming P{pos+1} for {actual_number}")
    
    # === 2. HUNGER DETECTION ===
    # Find numbers missing between neighbors
    last_5 = quarter_draws[-5:]
    hunger_counts = defaultdict(int)
    
    for draw in last_5:
        nums = sorted(draw['numbers'])
        for i in range(len(nums) - 1):
            gap = nums[i+1] - nums[i]
            if gap == 2:
                # One number missing
                missing = nums[i] + 1
                hunger_counts[missing] += 1
            elif gap > 2:
                # Multiple numbers missing
                for missing in range(nums[i] + 1, nums[i+1]):
                    if 1 <= missing <= 42:
                        hunger_counts[missing] += 1
    
    for num, count in hunger_counts.items():
        if count >= 2:
            bonus = count * 6
            scores[num]["score"] += bonus
            scores[num]["reasons"].append(f"🍽️ HUNGRY: neighbors appeared {count}x without {num}")
    
    # === 3. CONSECUTIVE SEQUENCE DETECTION (Rare Events) ===
    for idx, draw in enumerate(quarter_draws):
        nums = sorted(draw['numbers'])
        consecutive = 1
        max_consecutive = 1
        start_of_seq = nums[0]
        
        for i in range(1, len(nums)):
            if nums[i] == nums[i-1] + 1:
                consecutive += 1
                if consecutive > max_consecutive:
                    max_consecutive = consecutive
                    start_of_seq = nums[i - consecutive + 1]
            else:
                consecutive = 1
        
        if max_consecutive >= 4:
            rare_events.append({
                "draw_idx": idx,
                "date": draw['date'],
                "sequence": list(range(start_of_seq, start_of_seq + max_consecutive)),
                "length": max_consecutive
            })
            
            # Numbers adjacent to sequence are hot
            before = start_of_seq - 1
            after = start_of_seq + max_consecutive
            for n in [before, after]:
                if 1 <= n <= 42:
                    bonus = max_consecutive * 5
                    scores[n]["score"] += bonus
                    scores[n]["reasons"].append(f"🔥 RARE: adjacent to {max_consecutive}-consecutive!")
    
    # Check circles of consecutive numbers too
    for idx, draw in enumerate(quarter_draws):
        circles = sorted([get_circle(n) for n in draw['numbers']])
        consecutive = 1
        max_consecutive = 1
        
        for i in range(1, len(circles)):
            if circles[i] == circles[i-1] + 1:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 1
        
        if max_consecutive >= 4:
            rare_events.append({
                "draw_idx": idx,
                "date": draw['date'],
                "type": "circle_consecutive",
                "length": max_consecutive
            })
            signs.append(f"SUPER RARE: {max_consecutive} consecutive circles on {draw['date']}")
    
    # === 4. P1+P2 SUM PATTERNS ===
    p1p2_sums = []
    for draw in quarter_draws:
        nums = draw['numbers']
        p1p2 = nums[0] + nums[1]
        p1p2_sums.append(p1p2)
    
    # Check for recurring sums
    sum_counts = defaultdict(int)
    for s in p1p2_sums[-10:]:
        sum_counts[s] += 1
    
    for s, count in sum_counts.items():
        if count >= 2 and 1 <= s <= 42:
            bonus = count * 5
            scores[s]["score"] += bonus
            scores[s]["reasons"].append(f"➕ P1+P2={s} appeared {count}x")
    
    # Special sums
    last_p1p2 = p1p2_sums[-1] if p1p2_sums else 0
    special_targets = {
        9: "The 9 Story!",
        39: "13+26!",
        27: "Our P3!",
        30: "Our P4!",
        26: "Our P2!"
    }
    
    if last_p1p2 in special_targets:
        signs.append(f"Latest P1+P2={last_p1p2}: {special_targets[last_p1p2]}")
    
    # === 5. SECRET COUNTING (value + gap = next value at same position) ===
    for pos in range(6):
        pos_values = [(i, d['numbers'][pos]) for i, d in enumerate(quarter_draws)]
        
        # Find counting patterns
        for i in range(len(pos_values) - 1):
            draw1, val1 = pos_values[i]
            for j in range(i + 1, len(pos_values)):
                draw2, val2 = pos_values[j]
                gap = draw2 - draw1
                diff = val2 - val1
                
                if gap == diff and 1 <= gap <= 10:
                    # Found a count! Predict next
                    next_draw = draw2 + gap
                    next_val = val2 + gap
                    
                    if next_draw == len(quarter_draws) and 1 <= next_val <= 42:
                        # This count predicts the next draw!
                        bonus = 15
                        scores[next_val]["score"] += bonus
                        scores[next_val]["reasons"].append(
                            f"🔢 Secret count: {val1}→{val2}→{next_val} at P{pos+1}"
                        )
    
    # === 6. FAMILY TRACKING ===
    # If family members appeared, boost other family members
    last_draw = quarter_draws[-1]
    for num in last_draw['numbers']:
        family = get_family(num)
        for fam in family:
            if fam != num and 1 <= fam <= 42:
                scores[fam]["score"] += 5
                scores[fam]["reasons"].append(f"👨‍👩‍👧 Family of {num}")
    
    # === 7. POSITION MEMORY ===
    # Track where each number appeared across the quarter
    number_positions = defaultdict(list)  # {number: [positions]}
    
    for draw in quarter_draws:
        for pos, num in enumerate(draw['numbers']):
            number_positions[num].append(pos)
    
    # Numbers that appeared at multiple positions are "visiting"
    for num, positions in number_positions.items():
        if len(positions) >= 3 and len(set(positions)) >= 2:
            # Number is moving around - might settle
            most_common_pos = max(set(positions), key=positions.count)
            scores[num]["score"] += 8
            scores[num]["reasons"].append(f"🚶 {num} visiting, favors P{most_common_pos+1}")
    
    # === 8. DATE CODE ANALYSIS ===
    last_date = parse_date(quarter_draws[-1]['date'])
    day = last_date.day
    month = last_date.month
    year = last_date.year % 100  # Last 2 digits
    
    date_numbers = []
    
    # D + M
    dm_sum = day + month
    if 1 <= dm_sum <= 42:
        date_numbers.append((dm_sum, f"D+M={dm_sum}"))
    
    # D + M + Y
    dmy_sum = day + month + year
    if 1 <= dmy_sum <= 42:
        date_numbers.append((dmy_sum, f"D+M+Y={dmy_sum}"))
    elif dmy_sum > 42:
        reduced = dmy_sum
        while reduced > 42:
            reduced = sum(int(d) for d in str(reduced))
        if 1 <= reduced <= 42:
            date_numbers.append((reduced, f"D+M+Y reduced={reduced}"))
    
    # D × M
    dm_prod = day * month
    if 1 <= dm_prod <= 42:
        date_numbers.append((dm_prod, f"D×M={dm_prod}"))
    
    # Reversed digits
    if day >= 10:
        day_rev = int(str(day)[::-1])
        if 1 <= day_rev <= 42 and day_rev != day:
            date_numbers.append((day_rev, f"Day reversed={day_rev}"))
    
    for num, reason in date_numbers:
        scores[num]["score"] += 6
        scores[num]["reasons"].append(f"📅 {reason}")
    
    # === 9. CIRCLE OF LAST P4+P5 PREDICTS P6 ===
    if len(quarter_draws) >= 1:
        last = quarter_draws[-1]
        p4 = last['numbers'][3]
        p5 = last['numbers'][4]
        
        p4_circle = get_circle(p4)
        p5_circle = get_circle(p5)
        
        # Sum of circles
        circle_sum = p4_circle + p5_circle
        doubled = circle_sum * 2
        
        if 1 <= doubled <= 42:
            scores[doubled]["score"] += 10
            scores[doubled]["reasons"].append(
                f"🎯 P4({p4})circle={p4_circle} + P5({p5})circle={p5_circle} = {circle_sum}, doubled={doubled}"
            )
        elif doubled > 42:
            reduced = doubled - 42
            if 1 <= reduced <= 42:
                scores[reduced]["score"] += 10
                scores[reduced]["reasons"].append(
                    f"🎯 Circles sum doubled: {doubled}-42={reduced}"
                )
    
    # === 10. MIRROR TO 42 PATTERN ===
    # If last P4 + predicted P4 should = 42
    if len(quarter_draws) >= 1:
        last_p4 = quarter_draws[-1]['numbers'][3]
        mirror = 42 - last_p4
        if 1 <= mirror <= 42:
            scores[mirror]["score"] += 12
            scores[mirror]["reasons"].append(f"🪞 Mirror: {last_p4} + {mirror} = 42")
    
    return {
        "scores": dict(scores),
        "rare_events": rare_events,
        "signs": signs,
        "quarter_analyzed": len(quarter_draws)
    }


def get_story_sign_scores(draws: List[dict]) -> Dict[int, Dict]:
    """
    Main entry point for Pattern 60.
    Returns a dictionary of {number: {"score": int, "reasons": list}}
    """
    result = analyze_story_signs(draws)
    return result["scores"]


def find_rare_consecutive_events(draws: List[dict]) -> List[Dict]:
    """Find all rare consecutive events (4+ in a row) in the draws"""
    result = analyze_story_signs(draws)
    return result["rare_events"]


def get_hunger_analysis(draws: List[dict], last_n: int = 5) -> Dict[int, int]:
    """Get hunger counts for numbers missing between neighbors"""
    if not draws:
        return {}
    
    sorted_draws = sorted(draws, key=lambda x: parse_date(x['date']))
    last_draws = sorted_draws[-last_n:]
    
    hunger = defaultdict(int)
    
    for draw in last_draws:
        nums = sorted(draw['numbers'])
        for i in range(len(nums) - 1):
            gap = nums[i+1] - nums[i]
            if gap >= 2:
                for missing in range(nums[i] + 1, nums[i+1]):
                    if 1 <= missing <= 42:
                        hunger[missing] += 1
    
    return dict(hunger)
