"""
EuroMillions Pattern Analyzer Routes
5 numbers (1-50) + 2 stars (1-12)

🎻 LUCKY JACK'S MUSICAL GENERATOR 🍀
🎧 NOW WITH DJ PATTERN ENGINE! 🎧
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
from collections import Counter, defaultdict
import random as rnd

# Import Lucky Jack's Musical Patterns
from jack_patterns import (
    apply_jack_patterns,
    p1_counting_pattern,
    neighborhood_hunger,
    p5_49_calls_45,
    circle_encode_missing,
    quarter_echo,
    p4_sequence_tracker,
    p1p2_sum_pattern,
    eight_family_tracker,
    star_prophecy_pattern,
    star_diff_gap_pattern,
    circle,
    reverse_num
)

# Import DJ Pattern Engine (from backtesting session!)
from dj_patterns import (
    dj_generate_ticket,
    dj_generate_candidates,
    dj_select_numbers,
    WEIGHTS as DJ_WEIGHTS
)

# Constants for EuroMillions
MAX_NUMBER = 50
MAX_STAR = 12
MAIN_COUNT = 5
STAR_COUNT = 2

# Number families for EuroMillions (1-50)
FAMILIES = {
    1: list(range(1, 11)),    # 1-10
    2: list(range(11, 21)),   # 11-20
    3: list(range(21, 31)),   # 21-30
    4: list(range(31, 41)),   # 31-40
    5: list(range(41, 51)),   # 41-50
}

def get_circle_partner(n: int) -> int:
    """Get +25 partner on the circle"""
    partner = n + 25
    if partner > MAX_NUMBER:
        partner -= MAX_NUMBER
    return partner

def reverse_mod50(n: int) -> int:
    """Reverse digits and mod 50"""
    rev = int(str(n)[::-1])
    if rev > 50:
        rev = rev % 50
        if rev == 0:
            rev = 50
    return rev

def get_reverse_circle_partner(n: int) -> int:
    """Get reverse circle partner: n+25 then reverse digits"""
    plus25 = get_circle_partner(n)
    return reverse_mod50(plus25)

def get_three_circle(n: int) -> int:
    """
    Get 3-circle partner: n → +25 → +25 → reverse digits
    Example: 24 → 49 → 74 → 47
    """
    c1 = get_circle_partner(n)  # +25
    c2 = c1 + 25  # +25 again (may be > 50)
    # Reverse digits of c2
    c3 = int(str(c2)[::-1])
    if c3 > 50:
        c3 = c3 % 50 if c3 % 50 != 0 else 50
    return c3

def get_full_circle(n: int) -> list:
    """Get all numbers in n's circle: n → +25 → reverse → +25 → reverse..."""
    circle = [n]
    current = n
    for i in range(5):
        if i % 2 == 0:
            current = get_circle_partner(current)
        else:
            current = reverse_mod50(current)
        if current not in circle:
            circle.append(current)
    return circle

def get_qc_number(draws: list, target_date: str) -> int:
    """
    Get Quarter Count number for a date
    QC = count of draws in current quarter up to and including target_date
    """
    def parse_date(d):
        parts = d['date'].split('.')
        return (int(parts[2]), int(parts[1]), int(parts[0]))
    
    target_parts = target_date.split('.')
    target_year = int(target_parts[2])
    target_month = int(target_parts[1])
    
    # Determine quarter months
    if target_month in [1, 2, 3]:
        quarter_months = [1, 2, 3]
    elif target_month in [4, 5, 6]:
        quarter_months = [4, 5, 6]
    elif target_month in [7, 8, 9]:
        quarter_months = [7, 8, 9]
    else:
        quarter_months = [10, 11, 12]
    
    # Count draws in quarter up to target
    target_tuple = parse_date({"date": target_date})
    count = 0
    for d in draws:
        dt = parse_date(d)
        if dt[0] == target_year and dt[1] in quarter_months and dt <= target_tuple:
            count += 1
    return count

def get_qc1_prophecy(draws: list, year: int, quarter: int) -> dict:
    """
    Get QC1 (first draw of quarter) - the prophecy draw
    The QC1 date digits form the quarter's prophecy number
    Example: 02.01.2026 → "12" (0,2,0,1 → 1 and 2)
    """
    def parse_date(d):
        parts = d['date'].split('.')
        return (int(parts[2]), int(parts[1]), int(parts[0]))
    
    quarter_months = {1: [1,2,3], 2: [4,5,6], 3: [7,8,9], 4: [10,11,12]}
    months = quarter_months.get(quarter, [1,2,3])
    
    quarter_draws = [d for d in draws if parse_date(d)[0] == year and parse_date(d)[1] in months]
    quarter_draws = sorted(quarter_draws, key=parse_date)
    
    if not quarter_draws:
        return None
    
    qc1 = quarter_draws[0]
    day = int(qc1['date'].split('.')[0])
    month = int(qc1['date'].split('.')[1])
    
    # Prophecy number from date digits
    prophecy = day + month  # e.g., 02.01 → 2+1=3 or concatenate digits
    
    return {
        "draw": qc1,
        "prophecy_number": prophecy,
        "day": day,
        "month": month
    }

def find_hunger_number(present_nums: list) -> list:
    """
    Find hunger numbers - numbers missing between neighbors
    Example: if 33 and 35/53 present, 43 is hungry (33...43...53)
    """
    hungry = []
    sorted_nums = sorted(present_nums)
    
    for n in sorted_nums:
        # Check for reversed number
        rev = int(str(n)[::-1]) if n >= 10 else n * 10 + n
        if rev > 50:
            rev = rev % 50 if rev % 50 != 0 else 50
        
        # Find the gap number between n and its reverse
        if n < rev:
            # Numbers ending in same digit between n and rev
            for gap_candidate in range(n + 10, rev, 10):
                if 1 <= gap_candidate <= 50 and gap_candidate not in present_nums:
                    hungry.append(gap_candidate)
    
    # Also check neighborhood gaps (e.g., 33 present, 35 present → 43 hungry as midpoint to 53)
    for n in sorted_nums:
        if n >= 30:
            # Check for X3 → (X+1)3 pattern
            tens = n // 10
            ones = n % 10
            next_tens = (tens + 1) * 10 + ones
            if next_tens <= 50 and next_tens not in present_nums:
                hungry.append(next_tens)
    
    return list(set(hungry))

def get_hidden_groups(nums: list) -> dict:
    """Find hidden groups in numbers - multiples, +10 family, etc."""
    groups = {}
    
    # Check multiples of 7, 8, etc.
    for base in [7, 8, 9]:
        multiples = [n for n in nums if n % base == 0]
        if len(multiples) >= 2:
            # Find missing member
            all_multiples = [base * i for i in range(1, 8) if base * i <= 50]
            missing = [m for m in all_multiples if m not in nums]
            groups[f"mult_{base}"] = {"present": multiples, "missing": missing[:3]}
    
    # Check +10 families (4-14-24-34-44, etc.)
    for base in range(1, 11):
        family = [base + 10*i for i in range(5) if base + 10*i <= 50]
        present = [n for n in nums if n in family]
        if len(present) >= 2:
            missing = [n for n in family if n not in nums]
            groups[f"fam10_{base}"] = {"present": present, "missing": missing}
    
    return groups

def find_abc_pattern(nums: list) -> list:
    """Find A + B = C patterns within the numbers"""
    patterns = []
    sorted_nums = sorted(nums)
    for i, a in enumerate(sorted_nums):
        for j, b in enumerate(sorted_nums):
            if i < j:
                c = a + b
                if c in sorted_nums:
                    patterns.append((a, b, c))
    return patterns

def find_difference_pattern(nums: list, target: int) -> list:
    """Find A - B = target patterns"""
    patterns = []
    for a in nums:
        for b in nums:
            if a != b and a - b == target:
                patterns.append((a, b))
    return patterns

def decode_hidden_number(n: int) -> dict:
    """Decode hidden patterns in a number (like 49 → 490)"""
    hidden = {
        "original": n,
        "with_zero": n * 10,
        "digit_sum": sum(int(d) for d in str(n)),
        "digit_product": 1,
        "factors": []
    }
    # Digit product
    for d in str(n):
        if int(d) > 0:
            hidden["digit_product"] *= int(d)
    
    # Find factor pairs for n*10
    n10 = n * 10
    for i in range(2, min(51, n10)):
        if n10 % i == 0 and n10 // i <= 50:
            hidden["factors"].append((i, n10 // i))
    
    return hidden

def predict_p1p2_from_hidden(p3: int, p5: int) -> tuple:
    """
    Predict next P1P2 using the hidden pattern:
    P5 as (P5*10) + P3 = P1P2 combined
    """
    hidden = p5 * 10  # 49 → 490
    combined = hidden + p3  # 490 + 24 = 514
    
    # Split into P1 and P2
    combined_str = str(combined)
    if len(combined_str) >= 3:
        p1 = int(combined_str[0])
        p2 = int(combined_str[1:])
        if 1 <= p1 <= 50 and 1 <= p2 <= 50:
            return (p1, p2, combined)
    return None


class EuroMillionsPredictionRequest(BaseModel):
    birthday: Optional[str] = None
    name: Optional[str] = None
    locked_positions: Optional[Dict[str, int]] = None
    num_tickets: int = 1
    use_dj_engine: bool = False  # 🎧 Use DJ Pattern Engine
    target_date: Optional[str] = None  # DD.MM.YYYY for date-based patterns
    scenario: Optional[str] = None  # "dj" for DJ mode


def create_euromillions_router(db):
    """Create EuroMillions router with database access"""
    router = APIRouter(prefix="/api/euromillions", tags=["EuroMillions"])
    
    # Historical EuroMillions data (2014-2016)
    EUROMILLIONS_SEED_DATA = [
        # 2014
        {"date": "03.01.2014", "numbers": [3, 27, 31, 38, 44], "stars": [3, 8]},
        {"date": "07.01.2014", "numbers": [2, 20, 27, 33, 45], "stars": [6, 10]},
        {"date": "10.01.2014", "numbers": [1, 2, 11, 27, 29], "stars": [1, 10]},
        {"date": "14.01.2014", "numbers": [18, 20, 25, 26, 37], "stars": [10, 11]},
        {"date": "17.01.2014", "numbers": [19, 26, 32, 33, 42], "stars": [4, 10]},
        {"date": "21.01.2014", "numbers": [4, 12, 35, 42, 48], "stars": [5, 8]},
        {"date": "24.01.2014", "numbers": [5, 19, 34, 35, 41], "stars": [1, 5]},
        {"date": "28.01.2014", "numbers": [18, 20, 23, 42, 48], "stars": [2, 9]},
        {"date": "31.01.2014", "numbers": [8, 10, 15, 16, 31], "stars": [8, 9]},
        {"date": "04.02.2014", "numbers": [1, 21, 33, 37, 38], "stars": [4, 8]},
        {"date": "07.02.2014", "numbers": [3, 17, 19, 46, 47], "stars": [9, 10]},
        {"date": "11.02.2014", "numbers": [8, 17, 25, 41, 47], "stars": [1, 2]},
        {"date": "14.02.2014", "numbers": [2, 4, 6, 19, 39], "stars": [2, 7]},
        {"date": "18.02.2014", "numbers": [23, 26, 36, 37, 49], "stars": [6, 7]},
        {"date": "21.02.2014", "numbers": [13, 17, 28, 30, 32], "stars": [5, 7]},
        {"date": "25.02.2014", "numbers": [21, 25, 28, 35, 42], "stars": [4, 6]},
        {"date": "28.02.2014", "numbers": [12, 32, 38, 43, 44], "stars": [2, 7]},
        {"date": "04.03.2014", "numbers": [3, 5, 22, 27, 44], "stars": [1, 6]},
        {"date": "07.03.2014", "numbers": [5, 10, 38, 40, 41], "stars": [1, 8]},
        {"date": "11.03.2014", "numbers": [1, 4, 23, 33, 44], "stars": [7, 8]},
        {"date": "14.03.2014", "numbers": [6, 24, 25, 27, 30], "stars": [5, 9]},
        {"date": "18.03.2014", "numbers": [8, 27, 34, 36, 39], "stars": [5, 10]},
        {"date": "21.03.2014", "numbers": [7, 30, 37, 39, 42], "stars": [5, 7]},
        {"date": "25.03.2014", "numbers": [7, 20, 26, 28, 50], "stars": [2, 8]},
        {"date": "28.03.2014", "numbers": [3, 4, 19, 28, 43], "stars": [3, 7]},
        {"date": "01.04.2014", "numbers": [16, 18, 26, 38, 44], "stars": [8, 10]},
        {"date": "04.04.2014", "numbers": [6, 10, 28, 45, 50], "stars": [10, 11]},
        {"date": "08.04.2014", "numbers": [11, 18, 29, 42, 49], "stars": [4, 11]},
        {"date": "11.04.2014", "numbers": [8, 12, 19, 30, 33], "stars": [4, 11]},
        {"date": "15.04.2014", "numbers": [3, 14, 26, 47, 50], "stars": [7, 11]},
        {"date": "22.04.2014", "numbers": [13, 15, 20, 24, 46], "stars": [1, 8]},
        {"date": "25.04.2014", "numbers": [13, 21, 24, 44, 49], "stars": [1, 9]},
        {"date": "29.04.2014", "numbers": [18, 23, 26, 35, 44], "stars": [3, 11]},
        {"date": "02.05.2014", "numbers": [4, 30, 31, 38, 42], "stars": [2, 11]},
        {"date": "06.05.2014", "numbers": [5, 19, 24, 31, 37], "stars": [1, 9]},
        {"date": "09.05.2014", "numbers": [3, 21, 26, 28, 45], "stars": [7, 10]},
        {"date": "13.05.2014", "numbers": [4, 13, 30, 34, 47], "stars": [2, 6]},
        {"date": "16.05.2014", "numbers": [23, 26, 29, 37, 40], "stars": [3, 4]},
        {"date": "20.05.2014", "numbers": [5, 33, 36, 38, 47], "stars": [4, 9]},
        {"date": "23.05.2014", "numbers": [3, 8, 31, 34, 47], "stars": [9, 11]},
        {"date": "27.05.2014", "numbers": [7, 13, 16, 25, 26], "stars": [1, 6]},
        {"date": "30.05.2014", "numbers": [5, 24, 27, 41, 45], "stars": [6, 7]},
        {"date": "03.06.2014", "numbers": [2, 15, 32, 39, 44], "stars": [5, 10]},
        {"date": "06.06.2014", "numbers": [7, 25, 34, 40, 49], "stars": [9, 11]},
        {"date": "10.06.2014", "numbers": [12, 18, 21, 32, 33], "stars": [1, 11]},
        {"date": "13.06.2014", "numbers": [16, 18, 22, 28, 46], "stars": [9, 11]},
        {"date": "17.06.2014", "numbers": [11, 13, 37, 40, 48], "stars": [8, 9]},
        {"date": "20.06.2014", "numbers": [5, 15, 25, 38, 49], "stars": [1, 2]},
        {"date": "24.06.2014", "numbers": [1, 7, 20, 21, 48], "stars": [4, 7]},
        {"date": "27.06.2014", "numbers": [31, 33, 34, 39, 45], "stars": [2, 10]},
        {"date": "01.07.2014", "numbers": [18, 22, 25, 27, 39], "stars": [5, 10]},
        {"date": "04.07.2014", "numbers": [4, 18, 39, 43, 47], "stars": [2, 6]},
        {"date": "08.07.2014", "numbers": [8, 18, 22, 24, 27], "stars": [4, 11]},
        {"date": "11.07.2014", "numbers": [5, 22, 35, 38, 49], "stars": [4, 7]},
        {"date": "15.07.2014", "numbers": [15, 18, 20, 27, 34], "stars": [1, 3]},
        {"date": "18.07.2014", "numbers": [1, 11, 29, 41, 43], "stars": [3, 11]},
        {"date": "22.07.2014", "numbers": [1, 24, 43, 45, 50], "stars": [5, 8]},
        {"date": "25.07.2014", "numbers": [9, 10, 12, 24, 43], "stars": [5, 9]},
        {"date": "29.07.2014", "numbers": [10, 23, 35, 40, 43], "stars": [3, 9]},
        {"date": "01.08.2014", "numbers": [24, 44, 46, 48, 50], "stars": [5, 10]},
        {"date": "05.08.2014", "numbers": [5, 7, 19, 21, 42], "stars": [5, 11]},
        {"date": "08.08.2014", "numbers": [21, 29, 35, 43, 46], "stars": [1, 9]},
        {"date": "12.08.2014", "numbers": [7, 16, 19, 22, 33], "stars": [2, 5]},
        {"date": "15.08.2014", "numbers": [4, 5, 21, 23, 30], "stars": [8, 10]},
        {"date": "19.08.2014", "numbers": [4, 7, 11, 34, 47], "stars": [7, 8]},
        {"date": "22.08.2014", "numbers": [4, 17, 29, 35, 49], "stars": [1, 2]},
        {"date": "26.08.2014", "numbers": [10, 22, 36, 45, 48], "stars": [4, 11]},
        {"date": "29.08.2014", "numbers": [2, 9, 26, 32, 38], "stars": [3, 6]},
        {"date": "02.09.2014", "numbers": [5, 25, 31, 39, 45], "stars": [1, 8]},
        {"date": "05.09.2014", "numbers": [1, 18, 23, 46, 50], "stars": [3, 9]},
        {"date": "09.09.2014", "numbers": [8, 15, 19, 24, 35], "stars": [8, 10]},
        {"date": "12.09.2014", "numbers": [9, 13, 26, 31, 33], "stars": [7, 11]},
        {"date": "16.09.2014", "numbers": [4, 29, 30, 35, 50], "stars": [2, 4]},
        {"date": "19.09.2014", "numbers": [6, 8, 34, 38, 48], "stars": [3, 9]},
        {"date": "23.09.2014", "numbers": [12, 13, 14, 29, 35], "stars": [1, 7]},
        {"date": "26.09.2014", "numbers": [13, 27, 35, 46, 47], "stars": [1, 2]},
        {"date": "30.09.2014", "numbers": [3, 13, 15, 33, 42], "stars": [5, 7]},
        {"date": "03.10.2014", "numbers": [4, 13, 23, 48, 50], "stars": [5, 10]},
        {"date": "07.10.2014", "numbers": [9, 21, 28, 30, 38], "stars": [1, 8]},
        {"date": "10.10.2014", "numbers": [6, 29, 42, 45, 47], "stars": [9, 10]},
        {"date": "14.10.2014", "numbers": [4, 5, 15, 23, 32], "stars": [3, 7]},
        {"date": "17.10.2014", "numbers": [1, 13, 40, 48, 49], "stars": [8, 10]},
        {"date": "21.10.2014", "numbers": [20, 21, 27, 33, 40], "stars": [3, 10]},
        {"date": "24.10.2014", "numbers": [3, 9, 20, 30, 42], "stars": [1, 6]},
        {"date": "28.10.2014", "numbers": [10, 15, 17, 40, 45], "stars": [1, 2]},
        {"date": "31.10.2014", "numbers": [10, 13, 20, 33, 41], "stars": [3, 9]},
        {"date": "04.11.2014", "numbers": [1, 6, 13, 17, 26], "stars": [3, 5]},
        {"date": "07.11.2014", "numbers": [13, 25, 32, 38, 46], "stars": [1, 10]},
        {"date": "11.11.2014", "numbers": [2, 14, 21, 36, 46], "stars": [7, 11]},
        {"date": "14.11.2014", "numbers": [17, 32, 36, 38, 48], "stars": [5, 8]},
        {"date": "18.11.2014", "numbers": [2, 3, 17, 36, 38], "stars": [4, 11]},
        {"date": "21.11.2014", "numbers": [4, 7, 28, 32, 37], "stars": [5, 10]},
        {"date": "25.11.2014", "numbers": [3, 7, 25, 32, 36], "stars": [1, 6]},
        {"date": "28.11.2014", "numbers": [6, 10, 15, 25, 41], "stars": [4, 10]},
        {"date": "02.12.2014", "numbers": [3, 15, 25, 44, 49], "stars": [1, 9]},
        {"date": "05.12.2014", "numbers": [5, 8, 37, 47, 48], "stars": [2, 3]},
        {"date": "09.12.2014", "numbers": [1, 3, 31, 42, 46], "stars": [4, 11]},
        {"date": "12.12.2014", "numbers": [2, 15, 28, 31, 37], "stars": [4, 6]},
        {"date": "16.12.2014", "numbers": [3, 7, 12, 13, 25], "stars": [5, 8]},
        {"date": "19.12.2014", "numbers": [23, 29, 31, 39, 44], "stars": [5, 8]},
        {"date": "23.12.2014", "numbers": [8, 9, 19, 25, 49], "stars": [2, 10]},
        {"date": "26.12.2014", "numbers": [17, 26, 27, 45, 49], "stars": [2, 3]},
        {"date": "30.12.2014", "numbers": [6, 18, 39, 44, 50], "stars": [8, 11]},
        # 2015
        {"date": "02.01.2015", "numbers": [22, 24, 25, 28, 49], "stars": [3, 6]},
        {"date": "06.01.2015", "numbers": [14, 20, 30, 38, 49], "stars": [3, 4]},
        {"date": "09.01.2015", "numbers": [6, 21, 24, 32, 45], "stars": [1, 11]},
        {"date": "13.01.2015", "numbers": [8, 17, 21, 31, 34], "stars": [9, 10]},
        {"date": "16.01.2015", "numbers": [29, 30, 32, 34, 46], "stars": [3, 6]},
        {"date": "20.01.2015", "numbers": [15, 33, 41, 44, 47], "stars": [8, 10]},
        {"date": "23.01.2015", "numbers": [6, 29, 30, 38, 45], "stars": [1, 8]},
        {"date": "27.01.2015", "numbers": [5, 10, 31, 33, 40], "stars": [8, 10]},
        {"date": "30.01.2015", "numbers": [9, 13, 15, 19, 24], "stars": [3, 8]},
        {"date": "03.02.2015", "numbers": [17, 31, 33, 44, 50], "stars": [7, 11]},
        {"date": "06.02.2015", "numbers": [10, 26, 30, 39, 50], "stars": [7, 8]},
        {"date": "10.02.2015", "numbers": [13, 17, 20, 30, 45], "stars": [9, 10]},
        {"date": "13.02.2015", "numbers": [12, 24, 39, 42, 44], "stars": [3, 11]},
        {"date": "17.02.2015", "numbers": [2, 5, 18, 30, 43], "stars": [1, 10]},
        {"date": "20.02.2015", "numbers": [4, 10, 14, 37, 46], "stars": [4, 7]},
        {"date": "24.02.2015", "numbers": [3, 25, 28, 34, 50], "stars": [1, 11]},
        {"date": "27.02.2015", "numbers": [5, 14, 17, 25, 47], "stars": [9, 10]},
        {"date": "03.03.2015", "numbers": [6, 8, 11, 13, 21], "stars": [7, 8]},
        {"date": "06.03.2015", "numbers": [23, 30, 47, 49, 50], "stars": [2, 7]},
        {"date": "10.03.2015", "numbers": [2, 6, 23, 30, 31], "stars": [2, 10]},
        {"date": "13.03.2015", "numbers": [4, 5, 18, 22, 23], "stars": [1, 3]},
        {"date": "17.03.2015", "numbers": [11, 23, 26, 38, 44], "stars": [1, 8]},
        {"date": "20.03.2015", "numbers": [3, 14, 37, 42, 48], "stars": [1, 10]},
        {"date": "24.03.2015", "numbers": [10, 24, 26, 39, 40], "stars": [3, 10]},
        {"date": "27.03.2015", "numbers": [2, 30, 32, 39, 44], "stars": [6, 10]},
        {"date": "31.03.2015", "numbers": [8, 20, 24, 28, 49], "stars": [8, 9]},
        {"date": "03.04.2015", "numbers": [27, 29, 37, 39, 49], "stars": [2, 4]},
        {"date": "07.04.2015", "numbers": [18, 25, 39, 44, 50], "stars": [5, 8]},
        {"date": "10.04.2015", "numbers": [22, 23, 25, 30, 43], "stars": [5, 9]},
        {"date": "14.04.2015", "numbers": [24, 32, 34, 35, 49], "stars": [1, 2]},
        {"date": "17.04.2015", "numbers": [2, 24, 30, 34, 39], "stars": [8, 11]},
        {"date": "21.04.2015", "numbers": [6, 14, 17, 42, 45], "stars": [1, 8]},
        {"date": "24.04.2015", "numbers": [5, 19, 29, 31, 40], "stars": [3, 10]},
        {"date": "28.04.2015", "numbers": [24, 26, 28, 36, 45], "stars": [7, 10]},
        {"date": "01.05.2015", "numbers": [3, 19, 20, 25, 26], "stars": [6, 10]},
        {"date": "05.05.2015", "numbers": [1, 10, 17, 20, 42], "stars": [8, 9]},
        {"date": "08.05.2015", "numbers": [7, 14, 19, 47, 49], "stars": [3, 10]},
        {"date": "12.05.2015", "numbers": [14, 29, 30, 40, 46], "stars": [3, 6]},
        {"date": "15.05.2015", "numbers": [5, 35, 42, 44, 47], "stars": [8, 9]},
        {"date": "19.05.2015", "numbers": [26, 30, 31, 35, 37], "stars": [8, 11]},
        {"date": "22.05.2015", "numbers": [18, 24, 35, 44, 45], "stars": [5, 11]},
        {"date": "26.05.2015", "numbers": [5, 6, 7, 21, 24], "stars": [5, 6]},
        {"date": "29.05.2015", "numbers": [3, 4, 20, 45, 48], "stars": [6, 8]},
        {"date": "02.06.2015", "numbers": [7, 23, 29, 37, 41], "stars": [1, 8]},
        {"date": "05.06.2015", "numbers": [2, 7, 8, 45, 48], "stars": [1, 9]},
        {"date": "09.06.2015", "numbers": [5, 9, 17, 32, 34], "stars": [6, 8]},
        {"date": "12.06.2015", "numbers": [5, 8, 10, 11, 37], "stars": [7, 9]},
        {"date": "16.06.2015", "numbers": [10, 15, 16, 36, 37], "stars": [3, 9]},
        {"date": "19.06.2015", "numbers": [7, 14, 20, 31, 42], "stars": [3, 9]},
        {"date": "23.06.2015", "numbers": [4, 16, 22, 38, 49], "stars": [6, 9]},
        {"date": "26.06.2015", "numbers": [3, 6, 10, 19, 24], "stars": [5, 7]},
        {"date": "30.06.2015", "numbers": [11, 15, 28, 34, 37], "stars": [1, 8]},
        {"date": "03.07.2015", "numbers": [11, 12, 15, 18, 44], "stars": [3, 9]},
        {"date": "07.07.2015", "numbers": [6, 7, 18, 33, 41], "stars": [3, 10]},
        {"date": "10.07.2015", "numbers": [5, 8, 15, 35, 41], "stars": [4, 5]},
        {"date": "14.07.2015", "numbers": [6, 18, 19, 34, 36], "stars": [1, 8]},
        {"date": "17.07.2015", "numbers": [1, 21, 22, 43, 48], "stars": [7, 9]},
        {"date": "21.07.2015", "numbers": [14, 20, 27, 29, 44], "stars": [7, 10]},
        {"date": "24.07.2015", "numbers": [2, 9, 21, 35, 46], "stars": [2, 11]},
        {"date": "28.07.2015", "numbers": [23, 32, 36, 43, 49], "stars": [7, 8]},
        {"date": "31.07.2015", "numbers": [16, 21, 34, 40, 50], "stars": [6, 9]},
        {"date": "04.08.2015", "numbers": [10, 15, 39, 45, 50], "stars": [9, 10]},
        {"date": "07.08.2015", "numbers": [1, 5, 21, 39, 44], "stars": [4, 11]},
        {"date": "11.08.2015", "numbers": [2, 3, 8, 15, 16], "stars": [4, 11]},
        {"date": "14.08.2015", "numbers": [4, 7, 39, 44, 45], "stars": [3, 5]},
        {"date": "18.08.2015", "numbers": [7, 10, 11, 12, 19], "stars": [2, 9]},
        {"date": "21.08.2015", "numbers": [4, 16, 18, 43, 47], "stars": [6, 10]},
        {"date": "25.08.2015", "numbers": [27, 31, 33, 42, 50], "stars": [2, 5]},
        {"date": "28.08.2015", "numbers": [11, 29, 30, 31, 34], "stars": [4, 7]},
        {"date": "01.09.2015", "numbers": [6, 19, 21, 27, 45], "stars": [1, 8]},
        {"date": "04.09.2015", "numbers": [8, 9, 27, 45, 50], "stars": [8, 10]},
        {"date": "08.09.2015", "numbers": [14, 16, 39, 40, 42], "stars": [1, 4]},
        {"date": "11.09.2015", "numbers": [10, 18, 19, 29, 50], "stars": [1, 9]},
        {"date": "15.09.2015", "numbers": [8, 15, 17, 44, 49], "stars": [5, 8]},
        {"date": "18.09.2015", "numbers": [7, 29, 33, 34, 39], "stars": [7, 8]},
        {"date": "22.09.2015", "numbers": [14, 23, 26, 27, 29], "stars": [7, 10]},
        {"date": "25.09.2015", "numbers": [13, 14, 23, 30, 37], "stars": [2, 8]},
        {"date": "29.09.2015", "numbers": [11, 14, 26, 29, 49], "stars": [3, 9]},
        {"date": "02.10.2015", "numbers": [7, 18, 21, 32, 35], "stars": [2, 11]},
        {"date": "06.10.2015", "numbers": [11, 20, 22, 29, 32], "stars": [1, 8]},
        {"date": "09.10.2015", "numbers": [1, 40, 42, 43, 47], "stars": [9, 11]},
        {"date": "13.10.2015", "numbers": [12, 15, 26, 29, 47], "stars": [3, 11]},
        {"date": "16.10.2015", "numbers": [7, 28, 29, 43, 48], "stars": [3, 10]},
        {"date": "20.10.2015", "numbers": [17, 19, 21, 30, 45], "stars": [8, 10]},
        {"date": "23.10.2015", "numbers": [7, 25, 30, 32, 39], "stars": [2, 8]},
        {"date": "27.10.2015", "numbers": [11, 12, 20, 25, 36], "stars": [6, 9]},
        {"date": "30.10.2015", "numbers": [8, 13, 17, 21, 34], "stars": [6, 7]},
        {"date": "03.11.2015", "numbers": [8, 27, 39, 46, 49], "stars": [2, 6]},
        {"date": "06.11.2015", "numbers": [3, 17, 26, 38, 40], "stars": [4, 10]},
        {"date": "10.11.2015", "numbers": [6, 13, 18, 39, 43], "stars": [2, 8]},
        {"date": "13.11.2015", "numbers": [10, 17, 18, 33, 40], "stars": [2, 8]},
        {"date": "17.11.2015", "numbers": [6, 7, 23, 37, 38], "stars": [10, 11]},
        {"date": "20.11.2015", "numbers": [4, 30, 34, 46, 49], "stars": [7, 8]},
        {"date": "24.11.2015", "numbers": [9, 14, 16, 17, 26], "stars": [10, 11]},
        {"date": "27.11.2015", "numbers": [16, 29, 30, 37, 50], "stars": [6, 8]},
        {"date": "01.12.2015", "numbers": [2, 15, 25, 35, 45], "stars": [8, 10]},
        {"date": "04.12.2015", "numbers": [8, 17, 18, 27, 39], "stars": [1, 7]},
        {"date": "08.12.2015", "numbers": [12, 17, 29, 38, 48], "stars": [9, 11]},
        {"date": "11.12.2015", "numbers": [3, 5, 21, 40, 43], "stars": [6, 11]},
        {"date": "15.12.2015", "numbers": [8, 11, 23, 27, 35], "stars": [4, 11]},
        {"date": "18.12.2015", "numbers": [6, 22, 26, 29, 48], "stars": [5, 6]},
        {"date": "22.12.2015", "numbers": [18, 19, 20, 40, 41], "stars": [7, 10]},
        {"date": "25.12.2015", "numbers": [3, 10, 25, 27, 40], "stars": [3, 9]},
        {"date": "29.12.2015", "numbers": [5, 20, 31, 32, 36], "stars": [6, 7]},
        # 2016
        {"date": "01.01.2016", "numbers": [4, 37, 38, 39, 44], "stars": [4, 7]},
        {"date": "05.01.2016", "numbers": [6, 10, 31, 36, 39], "stars": [6, 10]},
        {"date": "08.01.2016", "numbers": [5, 26, 33, 35, 40], "stars": [3, 8]},
        {"date": "12.01.2016", "numbers": [1, 2, 10, 30, 44], "stars": [1, 8]},
        {"date": "15.01.2016", "numbers": [10, 19, 38, 43, 46], "stars": [1, 11]},
        {"date": "19.01.2016", "numbers": [2, 30, 38, 43, 46], "stars": [2, 7]},
        {"date": "22.01.2016", "numbers": [10, 12, 27, 30, 47], "stars": [8, 9]},
        {"date": "26.01.2016", "numbers": [15, 24, 38, 40, 48], "stars": [2, 9]},
        {"date": "29.01.2016", "numbers": [1, 5, 23, 29, 32], "stars": [1, 7]},
        {"date": "02.02.2016", "numbers": [6, 9, 10, 21, 36], "stars": [2, 6]},
        {"date": "05.02.2016", "numbers": [3, 27, 32, 41, 46], "stars": [4, 8]},
        {"date": "09.02.2016", "numbers": [6, 9, 13, 28, 37], "stars": [4, 5]},
        {"date": "12.02.2016", "numbers": [3, 20, 28, 31, 49], "stars": [2, 5]},
        {"date": "16.02.2016", "numbers": [3, 10, 22, 37, 50], "stars": [6, 10]},
        {"date": "19.02.2016", "numbers": [13, 14, 30, 32, 39], "stars": [3, 9]},
        {"date": "23.02.2016", "numbers": [23, 25, 32, 37, 42], "stars": [1, 11]},
        {"date": "26.02.2016", "numbers": [5, 13, 15, 33, 50], "stars": [9, 11]},
        {"date": "01.03.2016", "numbers": [4, 7, 13, 28, 37], "stars": [10, 11]},
        {"date": "04.03.2016", "numbers": [9, 14, 16, 23, 40], "stars": [1, 5]},
        {"date": "08.03.2016", "numbers": [1, 8, 9, 14, 23], "stars": [1, 7]},
        {"date": "11.03.2016", "numbers": [1, 21, 26, 40, 43], "stars": [6, 9]},
        {"date": "15.03.2016", "numbers": [5, 7, 10, 34, 44], "stars": [2, 10]},
        {"date": "18.03.2016", "numbers": [14, 19, 21, 24, 49], "stars": [5, 11]},
        {"date": "22.03.2016", "numbers": [12, 15, 26, 42, 49], "stars": [5, 8]},
        {"date": "25.03.2016", "numbers": [12, 19, 36, 42, 43], "stars": [5, 8]},
        {"date": "29.03.2016", "numbers": [1, 4, 19, 25, 36], "stars": [3, 11]},
        {"date": "01.04.2016", "numbers": [2, 16, 23, 25, 49], "stars": [6, 9]},
        {"date": "05.04.2016", "numbers": [3, 5, 9, 19, 40], "stars": [2, 5]},
        {"date": "08.04.2016", "numbers": [6, 8, 26, 43, 49], "stars": [6, 10]},
        {"date": "12.04.2016", "numbers": [1, 5, 9, 22, 38], "stars": [2, 10]},
        {"date": "15.04.2016", "numbers": [13, 14, 32, 37, 48], "stars": [1, 7]},
        {"date": "19.04.2016", "numbers": [11, 14, 15, 27, 44], "stars": [2, 7]},
        {"date": "22.04.2016", "numbers": [17, 26, 32, 34, 43], "stars": [2, 10]},
        {"date": "26.04.2016", "numbers": [10, 17, 31, 32, 42], "stars": [2, 5]},
        {"date": "29.04.2016", "numbers": [4, 5, 25, 28, 43], "stars": [6, 11]},
        {"date": "03.05.2016", "numbers": [8, 23, 24, 34, 38], "stars": [3, 7]},
        {"date": "06.05.2016", "numbers": [32, 34, 40, 45, 48], "stars": [1, 10]},
        {"date": "10.05.2016", "numbers": [2, 26, 27, 40, 49], "stars": [5, 10]},
        {"date": "13.05.2016", "numbers": [7, 15, 28, 31, 42], "stars": [10, 11]},
        {"date": "17.05.2016", "numbers": [15, 27, 32, 36, 39], "stars": [3, 10]},
        {"date": "20.05.2016", "numbers": [9, 14, 30, 41, 45], "stars": [4, 9]},
        {"date": "24.05.2016", "numbers": [16, 17, 23, 34, 37], "stars": [6, 9]},
        {"date": "27.05.2016", "numbers": [13, 25, 27, 43, 46], "stars": [4, 8]},
        {"date": "31.05.2016", "numbers": [6, 12, 26, 30, 48], "stars": [6, 7]},
        {"date": "03.06.2016", "numbers": [7, 23, 31, 33, 39], "stars": [6, 10]},
        {"date": "07.06.2016", "numbers": [19, 26, 35, 45, 49], "stars": [2, 5]},
        {"date": "10.06.2016", "numbers": [14, 21, 35, 42, 43], "stars": [7, 9]},
        {"date": "14.06.2016", "numbers": [13, 34, 39, 42, 50], "stars": [9, 11]},
        {"date": "17.06.2016", "numbers": [1, 7, 18, 27, 43], "stars": [4, 8]},
        {"date": "21.06.2016", "numbers": [5, 17, 32, 35, 49], "stars": [1, 5]},
        {"date": "24.06.2016", "numbers": [11, 19, 27, 28, 39], "stars": [3, 10]},
        {"date": "28.06.2016", "numbers": [26, 32, 37, 43, 49], "stars": [4, 5]},
        {"date": "01.07.2016", "numbers": [2, 11, 13, 40, 50], "stars": [1, 10]},
        {"date": "05.07.2016", "numbers": [1, 10, 29, 38, 48], "stars": [3, 4]},
        {"date": "08.07.2016", "numbers": [8, 12, 18, 33, 44], "stars": [4, 8]},
    ]
    
    async def get_euromillions_draws():
        """Get all EuroMillions draws - properly sorted by date"""
        cursor = db.euromillions_draws.find({}, {"_id": 0})
        draws = await cursor.to_list(length=None)
        
        # Sort properly by parsing DD.MM.YYYY format
        def parse_date(d):
            try:
                return datetime.strptime(d['date'], '%d.%m.%Y')
            except:
                return datetime.min
        
        return sorted(draws, key=parse_date, reverse=True)
    
    async def seed_euromillions_if_empty():
        """Seed EuroMillions data if collection is empty"""
        count = await db.euromillions_draws.count_documents({})
        if count == 0:
            # Import additional 2018-2020 data
            try:
                from euromillions_data_2018_2020 import EUROMILLIONS_DRAWS_2018_2020
                all_data = EUROMILLIONS_SEED_DATA + EUROMILLIONS_DRAWS_2018_2020
            except ImportError:
                all_data = EUROMILLIONS_SEED_DATA
            
            documents = [{
                "date": d["date"],
                "numbers": sorted(d["numbers"]),
                "stars": sorted(d["stars"]),
                "created_at": datetime.now(timezone.utc).isoformat()
            } for d in all_data]
            await db.euromillions_draws.insert_many(documents)
            return len(documents)
        return 0
    
    async def add_new_draws_if_needed():
        """Add all missing data if not already present"""
        added = 0
        
        # Add 2012-2013 data
        try:
            from euromillions_data_2012_2013 import EUROMILLIONS_DRAWS_2012_2013
            check = await db.euromillions_draws.find_one({"date": "03.01.2012"})
            if not check:
                documents = [{
                    "date": d["date"],
                    "numbers": sorted(d["numbers"]),
                    "stars": sorted(d["stars"]),
                    "created_at": datetime.now(timezone.utc).isoformat()
                } for d in EUROMILLIONS_DRAWS_2012_2013]
                await db.euromillions_draws.insert_many(documents)
                added += len(documents)
        except ImportError:
            pass
        
        # Add 2016-2018 missing data (2017 full year + gaps)
        try:
            from euromillions_data_missing import EUROMILLIONS_DRAWS_MISSING
            check = await db.euromillions_draws.find_one({"date": "03.01.2017"})
            if not check:
                documents = [{
                    "date": d["date"],
                    "numbers": sorted(d["numbers"]),
                    "stars": sorted(d["stars"]),
                    "created_at": datetime.now(timezone.utc).isoformat()
                } for d in EUROMILLIONS_DRAWS_MISSING]
                await db.euromillions_draws.insert_many(documents)
                added += len(documents)
        except ImportError:
            pass
        
        # Add 2018-2020 data
        try:
            from euromillions_data_2018_2020 import EUROMILLIONS_DRAWS_2018_2020
            check = await db.euromillions_draws.find_one({"date": "10.07.2018"})
            if not check:
                documents = [{
                    "date": d["date"],
                    "numbers": sorted(d["numbers"]),
                    "stars": sorted(d["stars"]),
                    "created_at": datetime.now(timezone.utc).isoformat()
                } for d in EUROMILLIONS_DRAWS_2018_2020]
                await db.euromillions_draws.insert_many(documents)
                added += len(documents)
        except ImportError:
            pass
        
        # Add 2021-2023 data
        try:
            from euromillions_data_2021_2023 import EUROMILLIONS_DRAWS_2021_2023
            check = await db.euromillions_draws.find_one({"date": "01.01.2021"})
            if not check:
                documents = [{
                    "date": d["date"],
                    "numbers": sorted(d["numbers"]),
                    "stars": sorted(d["stars"]),
                    "created_at": datetime.now(timezone.utc).isoformat()
                } for d in EUROMILLIONS_DRAWS_2021_2023]
                await db.euromillions_draws.insert_many(documents)
                added += len(documents)
        except ImportError:
            pass
        
        # Add 2024-2026 data
        try:
            from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
            check = await db.euromillions_draws.find_one({"date": "02.01.2024"})
            if not check:
                documents = [{
                    "date": d["date"],
                    "numbers": sorted(d["numbers"]),
                    "stars": sorted(d["stars"]),
                    "created_at": datetime.now(timezone.utc).isoformat()
                } for d in EUROMILLIONS_DRAWS_2024_2026]
                await db.euromillions_draws.insert_many(documents)
                added += len(documents)
        except ImportError:
            pass
        
        return added
    
    def pattern_position_frequency(draws, position):
        counts = Counter()
        for draw in draws:
            if position < len(draw["numbers"]):
                counts[draw["numbers"][position]] += 1
        total = sum(counts.values())
        return {num: count/total for num, count in counts.items()} if total > 0 else {}
    
    def pattern_star_frequency(draws):
        counts = Counter()
        for draw in draws:
            for star in draw["stars"]:
                counts[star] += 1
        total = sum(counts.values())
        return {num: count/total for num, count in counts.items()} if total > 0 else {}
    
    def pattern_gap_analysis(draws):
        last_seen = {i: float('inf') for i in range(1, MAX_NUMBER + 1)}
        for idx, draw in enumerate(draws):
            for num in draw["numbers"]:
                if last_seen[num] == float('inf'):
                    last_seen[num] = idx
        return {num: gap if gap != float('inf') else len(draws) for num, gap in last_seen.items()}
    
    def pattern_star_gap_analysis(draws):
        last_seen = {i: float('inf') for i in range(1, MAX_STAR + 1)}
        for idx, draw in enumerate(draws):
            for star in draw["stars"]:
                if last_seen[star] == float('inf'):
                    last_seen[star] = idx
        return {num: gap if gap != float('inf') else len(draws) for num, gap in last_seen.items()}
    
    def pattern_sum_range(draws):
        sums = [sum(d["numbers"]) for d in draws]
        return min(sums), max(sums), sum(sums) / len(sums) if sums else (0, 0, 0)
    
    def pattern_consecutive_pairs(draws):
        pairs_found = 0
        for draw in draws:
            nums = sorted(draw["numbers"])
            for i in range(len(nums) - 1):
                if nums[i+1] - nums[i] == 1:
                    pairs_found += 1
                    break
        return pairs_found / len(draws) if draws else 0
    
    def pattern_circle_partners(draws):
        found = 0
        for draw in draws:
            nums = set(draw["numbers"])
            for n in nums:
                partner = get_circle_partner(n)
                if partner in nums:
                    found += 1
                    break
        return found / len(draws) if draws else 0
    
    def pattern_odd_even_ratio(draws):
        ratios = Counter()
        for draw in draws:
            odds = sum(1 for n in draw["numbers"] if n % 2 == 1)
            evens = 5 - odds
            ratios[f"{odds}O-{evens}E"] += 1
        total = sum(ratios.values())
        return {r: count/total for r, count in ratios.items()} if total > 0 else {}
    
    def pattern_high_low_ratio(draws):
        ratios = Counter()
        for draw in draws:
            highs = sum(1 for n in draw["numbers"] if n > 25)
            lows = 5 - highs
            ratios[f"{lows}L-{highs}H"] += 1
        total = sum(ratios.values())
        return {r: count/total for r, count in ratios.items()} if total > 0 else {}
    
    def pattern_star_sum(draws):
        sums = Counter()
        for draw in draws:
            sums[sum(draw["stars"])] += 1
        total = sum(sums.values())
        return {s: count/total for s, count in sums.items()} if total > 0 else {}
    
    # ═══════════════════════════════════════════════════════════════════
    # 🎵 MUSICAL NUMBER GENERATION - THE SONGS! 🎵
    # ═══════════════════════════════════════════════════════════════════
    
    def to_circle(n):
        """Convert number to its first digit (circle form): 27 → 2, 35 → 3"""
        if n >= 10:
            return n // 10
        return n
    
    def find_songs_in_ticket(nums):
        """Find all musical patterns (songs) in a ticket"""
        songs = []
        p1, p2, p3, p4, p5 = nums
        
        # Direct addition songs
        if p1 + p2 == p3:
            songs.append(f"P1+P2=P3: {p1}+{p2}={p3}")
        if p1 + p2 == p4:
            songs.append(f"P1+P2=P4: {p1}+{p2}={p4}")
        if p1 + p2 == p5:
            songs.append(f"P1+P2=P5: {p1}+{p2}={p5}")
        if p2 + p3 == p4:
            songs.append(f"P2+P3=P4: {p2}+{p3}={p4}")
        if p2 + p3 == p5:
            songs.append(f"P2+P3=P5: {p2}+{p3}={p5}")
        if p3 + p4 == p5:
            songs.append(f"P3+P4=P5: {p3}+{p4}={p5}")
        if p1 + p3 == p4:
            songs.append(f"P1+P3=P4: {p1}+{p3}={p4}")
        if p1 + p3 == p5:
            songs.append(f"P1+P3=P5: {p1}+{p3}={p5}")
        if p1 + p4 == p5:
            songs.append(f"P1+P4=P5: {p1}+{p4}={p5}")
        if p2 + p4 == p5:
            songs.append(f"P2+P4=P5: {p2}+{p4}={p5}")
        
        # Circle addition songs (first digit + next = another)
        if to_circle(p1) + p2 == p3:
            songs.append(f"circle({p1})={to_circle(p1)}+{p2}={p3}")
        if to_circle(p2) + p3 == p4:
            songs.append(f"circle({p2})={to_circle(p2)}+{p3}={p4}")
        if to_circle(p2) + p3 == p5:
            songs.append(f"circle({p2})={to_circle(p2)}+{p3}={p5}")
        if to_circle(p3) + p4 == p5:
            songs.append(f"circle({p3})={to_circle(p3)}+{p4}={p5}")
        if to_circle(p1) + p3 == p4:
            songs.append(f"circle({p1})={to_circle(p1)}+{p3}={p4}")
        if to_circle(p1) + p4 == p5:
            songs.append(f"circle({p1})={to_circle(p1)}+{p4}={p5}")
        if to_circle(p2) + p4 == p5:
            songs.append(f"circle({p2})={to_circle(p2)}+{p4}={p5}")
        if to_circle(p1) + p2 == p4:
            songs.append(f"circle({p1})={to_circle(p1)}+{p2}={p4}")
        if to_circle(p1) + p2 == p5:
            songs.append(f"circle({p1})={to_circle(p1)}+{p2}={p5}")
        
        return songs
    
    def generate_musical_candidates(p1, p2):
        """Generate P3, P4, P5 candidates that create songs with P1 and P2"""
        candidates = {2: [], 3: [], 4: []}  # For P3, P4, P5
        
        # Direct addition songs
        # P1 + P2 = P3
        if p1 + p2 <= 50:
            candidates[2].extend([p1 + p2] * 5)  # Strong weight for P3
        
        # P1 + P2 = P4
        if p1 + p2 <= 50:
            candidates[3].extend([p1 + p2] * 3)
        
        # P1 + P2 = P5
        if p1 + p2 <= 50:
            candidates[4].extend([p1 + p2] * 2)
        
        # Circle songs: circle(P1) + P2 = P3
        c1 = to_circle(p1)
        if c1 + p2 <= 50 and c1 + p2 > p2:
            candidates[2].extend([c1 + p2] * 4)
        
        # Circle songs: circle(P2) + ? = P4/P5
        c2 = to_circle(p2)
        
        # Generate P3, P4, P5 that work together
        # If we pick P3, then P2 + P3 could = P4
        for p3_candidate in range(p2 + 1, 45):
            # Check if P2 + P3 makes a valid P4
            if p2 + p3_candidate <= 50:
                candidates[2].append(p3_candidate)
                candidates[3].extend([p2 + p3_candidate] * 2)
            
            # Check if circle(P2) + P3 makes valid P4/P5
            if c2 + p3_candidate <= 50 and c2 + p3_candidate > p3_candidate:
                candidates[3].append(c2 + p3_candidate)
        
        # P3 + P4 = P5 patterns
        for p3_candidate in range(p2 + 1, 40):
            for p4_candidate in range(p3_candidate + 1, 48):
                if p3_candidate + p4_candidate <= 50:
                    candidates[4].append(p3_candidate + p4_candidate)
        
        return candidates
    
    def make_ticket_musical(nums, max_attempts=20):
        """Try to adjust a ticket to have at least one song"""
        p1, p2, p3, p4, p5 = nums
        
        # First check if already musical
        songs = find_songs_in_ticket(nums)
        if songs:
            return nums, songs
        
        # Try to make it musical by adjusting P5, P4, P3
        for attempt in range(max_attempts):
            # Try: P3 + P4 = P5
            new_p5 = p3 + p4
            if new_p5 <= 50 and new_p5 > p4 and new_p5 not in [p1, p2, p3, p4]:
                new_nums = sorted([p1, p2, p3, p4, new_p5])
                songs = find_songs_in_ticket(new_nums)
                if songs:
                    return new_nums, songs
            
            # Try: P2 + P3 = P4
            new_p4 = p2 + p3
            if new_p4 <= 50 and new_p4 > p3 and new_p4 not in [p1, p2, p3, p5]:
                new_nums = sorted([p1, p2, p3, new_p4, p5])
                songs = find_songs_in_ticket(new_nums)
                if songs:
                    return new_nums, songs
            
            # Try: P1 + P2 = P3
            new_p3 = p1 + p2
            if new_p3 <= 50 and new_p3 > p2 and new_p3 not in [p1, p2, p4, p5]:
                new_nums = sorted([p1, p2, new_p3, p4, p5])
                songs = find_songs_in_ticket(new_nums)
                if songs:
                    return new_nums, songs
            
            # Try: circle(P2) + P3 = P4
            c2 = to_circle(p2)
            new_p4 = c2 + p3
            if new_p4 <= 50 and new_p4 > p3 and new_p4 not in [p1, p2, p3, p5]:
                new_nums = sorted([p1, p2, p3, new_p4, p5])
                songs = find_songs_in_ticket(new_nums)
                if songs:
                    return new_nums, songs
            
            # Try: P1 + P4 = P5
            new_p5 = p1 + p4
            if new_p5 <= 50 and new_p5 > p4 and new_p5 not in [p1, p2, p3, p4]:
                new_nums = sorted([p1, p2, p3, p4, new_p5])
                songs = find_songs_in_ticket(new_nums)
                if songs:
                    return new_nums, songs
        
        # Return original if can't make musical
        return nums, []
    
    async def master_predictor(draws, birthday=None, name=None, locked_positions=None, ticket_index=0, scenario=None, use_dj_engine=False, target_date=None):
        """
        Master prediction algorithm for EuroMillions
        
        scenario options:
        - "low": P1 is 1-5 (low start)
        - "medium": P1 is 6-15 (medium start)  
        - "high": P1 is 16+ (high start)
        - "dj": Use the new DJ Pattern Engine! 🎧
        - None: auto-select based on ticket_index
        
        use_dj_engine: If True, uses the backtested DJ patterns
        target_date: Target draw date for date-based patterns (DD.MM.YYYY)
        """
        patterns_used = []
        position_reasons = {}
        candidates = {i: [] for i in range(5)}
        star_candidates = []
        
        if not draws:
            nums = sorted(rnd.sample(range(1, 51), 5))
            stars = sorted(rnd.sample(range(1, 13), 2))
            return {
                "numbers": nums,
                "stars": stars,
                "patterns_used": ["Random (no data)"],
                "confidence": 0.1,
                "position_reasons": {},
                "scenario": "random"
            }
        
        # ═══════════════════════════════════════════════════════════════════
        # 🎧 DJ ENGINE MODE - Use backtested patterns! 🎧
        # ═══════════════════════════════════════════════════════════════════
        
        if use_dj_engine or scenario == "dj":
            # Convert draws to format expected by DJ engine
            dj_draws = []
            for d in draws:
                dj_draws.append({
                    'date': d.get('date', '01.01.2025'),
                    'numbers': d.get('numbers', []),
                    'stars': d.get('stars', [])
                })
            
            # Generate ticket using DJ engine
            locked = {}
            if locked_positions:
                for pos_key, value in locked_positions.items():
                    pos_idx = int(pos_key.replace("P", "")) - 1
                    if 0 <= pos_idx < 5 and 1 <= value <= 50:
                        locked[pos_idx] = value
            
            dj_result = dj_generate_ticket(dj_draws, target_date=target_date, locked=locked)
            
            return {
                "numbers": dj_result["numbers"],
                "stars": dj_result["stars"],
                "patterns_used": dj_result["patterns_used"],
                "confidence": 0.85,  # High confidence - backtested!
                "position_reasons": {
                    "P1": "DJ Engine - weighted by hit rates",
                    "P2": "DJ Engine - weighted by hit rates",
                    "P3": "DJ Engine - weighted by hit rates",
                    "P4": "DJ Engine - weighted by hit rates",
                    "P5": "DJ Engine - weighted by hit rates",
                },
                "scenario": "dj",
                "prev_draw": dj_result.get("prev_draw", {})
            }
        
        # ═══════════════════════════════════════════════════════════════════
        # SCENARIO-BASED P1/P2 GENERATION - THE THREE STORIES! 🎭
        # ═══════════════════════════════════════════════════════════════════
        
        # Auto-select scenario based on ticket index if not specified
        if scenario is None:
            scenario_rotation = ["low", "medium", "high"]
            scenario = scenario_rotation[ticket_index % 3]
        
        # P1+P2 Consecutive Sum Pattern (from analysis: ~15% hit rate within ±3)
        # Use PREVIOUS draw's P1+P2 sum as reference, not a fixed value
        prev_p1p2_sum = 37  # Default fallback
        if draws:
            prev_nums = sorted(draws[0]["numbers"])
            prev_p1p2_sum = prev_nums[0] + prev_nums[1]
        
        # Define P1 options for each scenario with their stories
        # Now P2 is calculated dynamically from previous draw's sum!
        scenario_configs = {
            "low": {
                "p1_range": [1, 2, 3, 4, 5],
                "story": "Low Start Story - small beginnings"
            },
            "medium": {
                "p1_range": [8, 9, 10, 13],
                "story": "Medium Start Story - balanced approach"
            },
            "high": {
                "p1_range": [17, 20, 24],
                "story": "High Start Story - bold entry"
            }
        }
        
        config = scenario_configs.get(scenario, scenario_configs["medium"])
        
        # Pick P1 from scenario options (rotate within scenario)
        p1_range = config["p1_range"]
        scenario_p1 = p1_range[(ticket_index // 3) % len(p1_range)]
        scenario_story = config["story"]
        
        # Calculate P2 based on previous draw's sum (the pattern!)
        # But only if it makes sense (P2 > P1)
        scenario_p2 = prev_p1p2_sum - scenario_p1
        
        # Heavily weight P1 position with scenario value
        candidates[0].extend([scenario_p1] * 10)
        
        # Add P2 candidate if it's valid (must be > P1 for sorted order)
        if scenario_p1 < scenario_p2 <= 50:
            candidates[1].extend([scenario_p2] * 8)
            patterns_used.append(f"Scenario {scenario.upper()}: P1={scenario_p1}, target P2={scenario_p2} (prev sum={prev_p1p2_sum})")
        else:
            patterns_used.append(f"Scenario {scenario.upper()}: P1={scenario_p1} ({scenario_story})")
        
        position_reasons["P1"] = f"Scenario {scenario}: {scenario_p1}"
        if scenario_p1 < scenario_p2 <= 50:
            position_reasons["P2"] = f"Prev P1+P2 pattern: {prev_p1p2_sum}-{scenario_p1}={scenario_p2}"
        
        # ═══════════════════════════════════════════════════════════════════
        
        locked = {}
        if locked_positions:
            for pos_key, value in locked_positions.items():
                pos_idx = int(pos_key.replace("P", "")) - 1
                if 0 <= pos_idx < 5 and 1 <= value <= 50:
                    locked[pos_idx] = value
        
        # REMOVED: Position Frequency (hot numbers) - not a valid pattern
        # REMOVED: Gap Analysis (cold/due numbers) - not a valid pattern
        # REMOVED: Recent Hot Numbers - not a valid pattern
        
        # Pattern: Family Spread (decade spread)
        family_nums = [rnd.choice(fam_nums) for fam_nums in FAMILIES.values()]
        for pos in range(5):
            if pos not in locked:
                candidates[pos].extend(family_nums)
        patterns_used.append("Family Spread")
        
        # Pattern: Consecutive Pairs
        consec_rate = pattern_consecutive_pairs(draws)
        if consec_rate > 0.4 and rnd.random() < consec_rate:
            base = rnd.randint(5, 45)
            for pos in [1, 2]:
                if pos not in locked:
                    candidates[pos].append(base)
                    candidates[pos].append(base + 1)
            patterns_used.append(f"Consecutive Pairs ({consec_rate:.1%})")
        
        # Pattern 6: Sum Range
        min_sum, max_sum, avg_sum = pattern_sum_range(draws)
        patterns_used.append(f"Sum Range ({int(min_sum)}-{int(max_sum)})")
        
        # Pattern 7: Odd/Even Balance
        odd_even = pattern_odd_even_ratio(draws)
        best_ratio = max(odd_even.keys(), key=lambda x: odd_even.get(x, 0)) if odd_even else "3O-2E"
        patterns_used.append(f"Odd/Even ({best_ratio})")
        
        # Pattern 8: REVERSE CIRCLE (34.4% hit rate!) ⭐ NEW
        # When a number appears, its reverse circle partner often follows
        if draws:
            recent_nums = draws[0]["numbers"]
            reverse_partners = []
            for n in recent_nums:
                rev_partner = get_reverse_circle_partner(n)
                if rev_partner not in recent_nums:
                    reverse_partners.append(rev_partner)
            if reverse_partners:
                for pos in range(5):
                    if pos not in locked:
                        candidates[pos].extend(reverse_partners)
                patterns_used.append("Reverse Circle (9.5%)")
        
        # Pattern 8b: UNIVERSE ANNOYING - ±1 Neighbors (17.3% hit rate!) ⭐ NEW
        # Every 5th ticket, use the ±1 neighbor instead of exact Reverse Circle
        # When we predict X, universe often gives X+1 or X-1
        if draws and ticket_index % 5 == 4:  # Every 5th ticket (index 4, 9, 14...)
            recent_nums = draws[0]["numbers"]
            annoying_neighbors = []
            for n in recent_nums:
                rev_partner = get_reverse_circle_partner(n)
                # Add ±1 neighbors instead of exact
                for neighbor in [rev_partner - 1, rev_partner + 1]:
                    if 1 <= neighbor <= 50 and neighbor not in recent_nums:
                        annoying_neighbors.append(neighbor)
            if annoying_neighbors:
                for pos in range(5):
                    if pos not in locked:
                        # Weight heavily - these replace exact reverse circle
                        candidates[pos].extend(annoying_neighbors * 3)
                patterns_used.append("Universe Annoying ±1 (17.3%)")
        
        # Pattern 8c: DIGIT FAMILY - Same ending digit (32.9% hit rate!)
        # Predicted 2? Also consider 12, 22, 32, 42
        if draws and ticket_index % 3 == 2:  # Every 3rd ticket
            recent_nums = draws[0]["numbers"]
            digit_family_nums = []
            for n in recent_nums:
                rev_partner = get_reverse_circle_partner(n)
                last_digit = rev_partner % 10
                # Get all numbers ending in same digit
                for family_member in range(last_digit, 51, 10):
                    if family_member >= 1 and family_member != rev_partner and family_member not in recent_nums:
                        digit_family_nums.append(family_member)
            if digit_family_nums:
                for pos in range(5):
                    if pos not in locked:
                        candidates[pos].extend(digit_family_nums * 2)
                patterns_used.append("Digit Family (32.9%)")
        
        # Pattern 9: Full Circle Family
        # Pick a starting number and include its full circle
        if rnd.random() < 0.5:
            seed = rnd.randint(1, 25)
            circle = get_full_circle(seed)
            for pos in range(5):
                if pos not in locked:
                    candidates[pos].extend(circle[:3])
            patterns_used.append(f"Circle Family ({seed})")
        
        # Birthday Integration
        if birthday:
            try:
                bd = datetime.strptime(birthday, "%d.%m.%Y")
                bd_nums = [bd.day, bd.month]
                if bd.year % 100 <= 50:
                    bd_nums.append(bd.year % 100)
                for pos in range(5):
                    if pos not in locked:
                        candidates[pos].extend([n for n in bd_nums if 1 <= n <= 50])
                patterns_used.append(f"Birthday ({birthday})")
            except:
                pass
        
        # Name Numerology
        if name:
            name_values = [ord(c.upper()) - 64 for c in name if c.isalpha()]
            name_sum = sum(name_values) % 50
            if name_sum == 0:
                name_sum = 50
            for pos in range(5):
                if pos not in locked:
                    candidates[pos].append(name_sum)
            patterns_used.append(f"Name Energy ({name})")
        
        # Star patterns
        # REMOVED: Star frequency (hot stars) - not a valid pattern
        # REMOVED: Star gap analysis (due stars) - not a valid pattern
        
        star_sums = pattern_star_sum(draws)
        target_sum = max(star_sums.keys(), key=lambda x: star_sums.get(x, 0)) if star_sums else 13
        patterns_used.append(f"Star Sum Target ({target_sum})")
        
        # ═══════════════════════════════════════════════════════════════════
        # NEW STAR PATTERNS FOR VARIETY! 🌟
        # ═══════════════════════════════════════════════════════════════════
        
        # STAR PATTERN A: Quarter Boundary - Star 10 is constant, other star counts!
        # Q4→Q1: [1,10] → Q1→Q2: [2,10] → Q2→Q3: [3,10]?
        if draws:
            prev_stars = sorted(draws[0]["stars"])
            if 10 in prev_stars:
                # Star 10 likes to continue at quarter boundaries
                star_candidates.extend([10] * 3)
                # The other star might increment
                other_star = prev_stars[0] if prev_stars[1] == 10 else prev_stars[1]
                next_star = other_star + 1 if other_star < 12 else 1
                if 1 <= next_star <= 12:
                    star_candidates.extend([next_star] * 2)
                patterns_used.append(f"Star-10 Anchor + {next_star}")
        
        # STAR PATTERN B: Star = Circle of previous draw's number (CORRECT!)
        # E.g., if prev has 27, circle=2, so star 2 might appear
        # Or if prev has 10, circle=35, reverse=53, in range=3, so star 3!
        if draws:
            prev_nums = draws[0]["numbers"]
            for n in prev_nums:
                # Circle partner
                circ = n + 25 if n <= 25 else n - 25
                if 1 <= circ <= 12:
                    star_candidates.append(circ)
                # Reversed circle for numbers > 12
                if n >= 10:
                    rev = int(str(n)[::-1]) if n >= 10 else n * 10
                    if rev > 50:
                        rev = rev - 50
                    if 1 <= rev <= 12:
                        star_candidates.append(rev)
            patterns_used.append("Star=Circle")
        
        # STAR PATTERN C: Star appears in numbers!
        # If star 10 is hot, check if number 10 is also due
        if draws:
            prev_stars = sorted(draws[0]["stars"])
            for s in prev_stars:
                # Add the star itself (might repeat) and neighboring stars
                star_candidates.append(s)
                if s > 1:
                    star_candidates.append(s - 1)
                if s < 12:
                    star_candidates.append(s + 1)
        
        # STAR PATTERN D: QC in Stars (Real Numbers!)
        # At QC 1, star 1 appeared. At QC 5, star 5 appeared, etc.
        if draws:
            def parse_d(d):
                parts = d['date'].split('.')
                return (int(parts[2]), int(parts[1]), int(parts[0]))
            
            latest = draws[0]
            latest_date = parse_d(latest)
            year = latest_date[0]
            month = latest_date[1]
            
            if month in [1,2,3]: q_months = [1,2,3]
            elif month in [4,5,6]: q_months = [4,5,6]
            elif month in [7,8,9]: q_months = [7,8,9]
            else: q_months = [10,11,12]
            
            q_draws = [d for d in draws if parse_d(d)[0] == year and parse_d(d)[1] in q_months]
            next_qc = len(q_draws) + 1
            
            # If next QC is 1-12, it might appear as a star!
            if 1 <= next_qc <= 12:
                star_candidates.extend([next_qc] * 3)
                patterns_used.append(f"QC={next_qc} Star Candidate")
        
        # Add variety by including less common stars based on ticket index
        variety_stars = [1, 3, 4, 7, 8, 11, 12]  # Less common S1 values
        star_candidates.append(variety_stars[ticket_index % len(variety_stars)])
        
        # NEW PATTERN: Gap 6 Trigger → Extreme Star Gaps
        # When previous draw had star gap 6, expect extreme gaps (8-11)
        prev_star_gap = 0
        extreme_gap_triggered = False
        if len(draws) >= 1:
            prev_stars = sorted(draws[0]["stars"])
            prev_star_gap = prev_stars[1] - prev_stars[0]
            
            if prev_star_gap == 6:
                # Gap 6 triggers extreme gaps - favor 1+9, 1+10, 1+11, 1+12, 2+11, 2+12
                extreme_pairs = [(1, 9), (1, 10), (1, 11), (1, 12), (2, 11), (2, 12), (3, 11), (3, 12)]
                chosen_pair = rnd.choice(extreme_pairs)
                star_candidates.extend(list(chosen_pair) * 3)  # Weight heavily
                extreme_gap_triggered = True
                patterns_used.append(f"Gap-6 Trigger → Extreme Stars")
            
            # Gap oscillation: small→large, large→small
            elif prev_star_gap <= 2:
                # Expect medium-large gap (4-6)
                mid_pairs = [(2, 6), (3, 7), (4, 8), (5, 9), (6, 10)]
                chosen_pair = rnd.choice(mid_pairs)
                star_candidates.extend(list(chosen_pair) * 2)
                patterns_used.append(f"Gap Oscillation (prev={prev_star_gap}→mid)")
            elif prev_star_gap >= 5:
                # Expect small gap (1-3)
                small_pairs = [(2, 3), (3, 4), (8, 9), (9, 10), (2, 4), (3, 5)]
                chosen_pair = rnd.choice(small_pairs)
                star_candidates.extend(list(chosen_pair) * 2)
                patterns_used.append(f"Gap Oscillation (prev={prev_star_gap}→small)")
        
        # NEW PATTERN: Consecutive numbers when extreme gaps expected
        if extreme_gap_triggered:
            # 63% of Gap-11 draws have consecutive numbers
            if rnd.random() < 0.63:
                consec_base = rnd.randint(10, 40)
                # Add triple consecutive to candidates
                for pos in [1, 2, 3]:
                    if pos not in locked:
                        candidates[pos].extend([consec_base, consec_base + 1, consec_base + 2] * 2)
                patterns_used.append(f"Consecutive Cluster ({consec_base}-{consec_base+2})")
        
        # NEW PATTERN 10: Hidden Groups (multiples, +10 family)
        # When 2+ numbers from same group appear, missing member is significant
        if draws:
            recent_nums = draws[0]["numbers"]
            hidden_groups = get_hidden_groups(recent_nums)
            for group_name, group_info in hidden_groups.items():
                if group_info["missing"]:
                    # Add missing members as candidates
                    for missing in group_info["missing"][:2]:
                        for pos in range(5):
                            if pos not in locked:
                                candidates[pos].append(missing)
                    patterns_used.append(f"Hidden Group ({group_name})")
        
        # NEW PATTERN 11: A + B = C (three numbers connected by addition)
        if draws:
            recent_nums = draws[0]["numbers"]
            abc_patterns = find_abc_pattern(recent_nums)
            if abc_patterns:
                # Use these numbers as likely candidates
                for a, b, c in abc_patterns:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([a, b, c])
                patterns_used.append(f"A+B=C Pattern")
        
        # NEW PATTERN 12: P3 Prediction (P3 is most important!)
        # Use previous P3 + hidden calculations
        if draws:
            recent = draws[0]["numbers"]
            recent_sorted = sorted(recent)
            prev_p3 = recent_sorted[2]  # P3 position
            prev_p5 = recent_sorted[4]  # P5 position
            
            # P1P2 prediction from hidden (P5*10 + P3 = P1P2)
            prediction = predict_p1p2_from_hidden(prev_p3, prev_p5)
            if prediction:
                p1, p2, combined = prediction
                if 0 not in locked:
                    candidates[0].extend([p1] * 3)  # Weight P1
                if 1 not in locked:
                    candidates[1].extend([p2] * 3)  # Weight P2
                patterns_used.append(f"P1P2 Hidden ({prev_p5}0+{prev_p3}={combined})")
        
        # NEW PATTERN 13: Fibonacci Addition Connection
        # Numbers that add to Fibonacci (5, 8, 13, 21, 34)
        fib_nums = [5, 8, 13, 21, 34]
        for fib in fib_nums:
            for a in range(1, fib):
                b = fib - a
                if 1 <= b <= 50 and rnd.random() < 0.3:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].append(a)
                            candidates[pos].append(b)
                    break
        patterns_used.append("Fibonacci Addends")
        
        # NEW PATTERN 14: RARE EVENT COUNT (RC) - 22.4% combined hit rate!
        # After a Rare Event (4+ numbers from same DECADE), count the draws
        # The count number OR its +25 circle partner often appears
        # CORRECT DECADES: 1-9, 10-19, 20-29, 30-39, 40-49 (50 is alone)
        if draws:
            # Find Rare Events (4+ in same decade)
            def get_decade_counts(nums):
                d1 = len([n for n in nums if 1 <= n <= 9])      # Ones (1-9)
                d2 = len([n for n in nums if 10 <= n <= 19])    # Tens (10-19)
                d3 = len([n for n in nums if 20 <= n <= 29])    # Twenties (20-29)
                d4 = len([n for n in nums if 30 <= n <= 39])    # Thirties (30-39)
                d5 = len([n for n in nums if 40 <= n <= 49])    # Forties (40-49)
                return max(d1, d2, d3, d4, d5), [d1, d2, d3, d4, d5]
            
            # Scan for last Rare Event
            last_rare_idx = None
            last_rare_outsider = None
            for i, d in enumerate(draws):
                max_decade, decade_counts = get_decade_counts(d["numbers"])
                if max_decade >= 4:
                    last_rare_idx = i
                    # Find the outsider (number not in the dominant decade)
                    decade_ranges = [(1,9), (10,19), (20,29), (30,39), (40,49)]
                    dominant_idx = decade_counts.index(max_decade)
                    low, high = decade_ranges[dominant_idx]
                    outsiders = [n for n in d["numbers"] if n < low or n > high]
                    if outsiders:
                        last_rare_outsider = outsiders[0]
                    break  # Found most recent
            
            if last_rare_idx is not None:
                # Count from last Rare Event
                count_from_rare = last_rare_idx + 1  # +1 because index 0 = 1 draw ago
                
                # The count number (keep 1-50 for EuroMillions)
                count_num = count_from_rare if count_from_rare <= 50 else ((count_from_rare - 1) % 50) + 1
                
                # Circle partner (+25 with wrap)
                circle_partner = count_num + 25 if count_num <= 25 else count_num - 25
                
                # Boost count number and circle partner
                if 1 <= count_num <= 50:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([count_num] * 3)  # Weight heavily
                    patterns_used.append(f"RC Count ({count_from_rare})")
                
                if 1 <= circle_partner <= 50:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([circle_partner] * 2)
                    patterns_used.append(f"RC Circle ({count_num}↔{circle_partner})")
                
                # Outsider circle partner (key number!)
                if last_rare_outsider:
                    out_circle = last_rare_outsider + 25 if last_rare_outsider <= 25 else last_rare_outsider - 25
                    if 1 <= out_circle <= 50:
                        for pos in range(5):
                            if pos not in locked:
                                candidates[pos].extend([out_circle] * 2)
                        patterns_used.append(f"RC Outsider ({last_rare_outsider}↔{out_circle})")
        
        # NEW PATTERN 15: 514 FORMULA GAP PATTERN
        # Track gaps between P1 hits from the 514 formula
        # The gap number OR its circle partner often appears in the hit draw!
        if draws and len(draws) >= 30:
            # Find recent P1 hits from 514 formula
            p1_hit_indices = []
            
            for idx in range(min(len(draws) - 1, 150)):  # Check last 150 draws
                prev_d = draws[idx + 1]
                curr_d = draws[idx]
                
                prev_nums = sorted(prev_d['numbers'])
                prev_stars = sorted(prev_d.get('stars', [1, 2]))
                
                if len(prev_nums) >= 5 and len(prev_stars) >= 2:
                    p4 = prev_nums[3]
                    p5 = prev_nums[4]
                    s1 = prev_stars[0]
                    s2 = prev_stars[1]
                    
                    p4_circle = p4 - 25 if p4 > 25 else p4 + 25
                    formula_result = p4_circle + (p5 * 10) + s1 + s2
                    
                    result_str = str(formula_result)
                    pred_p1 = int(result_str[0]) if result_str else 0
                    
                    curr_nums = sorted(curr_d['numbers'])
                    actual_p1 = curr_nums[0] if curr_nums else 0
                    
                    if pred_p1 == actual_p1:
                        p1_hit_indices.append(idx)
            
            # Calculate gap from most recent P1 hit
            if len(p1_hit_indices) >= 2:
                last_gap = p1_hit_indices[0] - p1_hit_indices[1] if p1_hit_indices[0] > p1_hit_indices[1] else p1_hit_indices[1] - p1_hit_indices[0]
                
                # Current gap (draws since last P1 hit)
                current_gap = p1_hit_indices[0] + 1 if p1_hit_indices else 0
                
                gap_circle = last_gap - 25 if last_gap > 25 else last_gap + 25
                current_gap_circle = current_gap - 25 if current_gap > 25 else current_gap + 25
                
                # Add gap and circle as candidates
                if 1 <= last_gap <= 50:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([last_gap] * 2)
                    patterns_used.append(f"514 Gap ({last_gap})")
                
                if 1 <= gap_circle <= 50:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([gap_circle] * 2)
                    patterns_used.append(f"514 Gap Circle ({last_gap}↔{gap_circle})")
                
                # Also add current gap (count since last hit)
                if 1 <= current_gap <= 50 and current_gap != last_gap:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].append(current_gap)
                    patterns_used.append(f"514 Current Gap ({current_gap})")
        
        # ═══════════════════════════════════════════════════════════════════
        # NEW PATTERNS FROM NUMEROLOGY ANALYSIS SESSION - THE REAL MAGIC! 🎻
        # ═══════════════════════════════════════════════════════════════════
        
        # PATTERN 16: THREE-CIRCLE (24 → 49 → 74 → 47)
        # The third circle partner via double +25 then reverse
        if draws:
            recent_nums = draws[0]["numbers"]
            for n in recent_nums:
                three_circ = get_three_circle(n)
                if 1 <= three_circ <= 50 and three_circ not in recent_nums:
                    # Weight heavily for P4/P5 positions
                    candidates[3].extend([three_circ] * 4)  # P4
                    candidates[4].extend([three_circ] * 4)  # P5
            patterns_used.append("3-Circle Pattern")
        
        # PATTERN 17: P1+P2 CONSTANT SUM
        # The sum of P1+P2 often stays constant across consecutive draws
        if len(draws) >= 2:
            prev_nums = sorted(draws[0]["numbers"])
            prev2_nums = sorted(draws[1]["numbers"])
            
            prev_p1p2_sum = prev_nums[0] + prev_nums[1]
            prev2_p1p2_sum = prev2_nums[0] + prev2_nums[1]
            
            # If sums are close, use same sum for prediction
            if abs(prev_p1p2_sum - prev2_p1p2_sum) <= 5:
                target_sum = prev_p1p2_sum
                # Generate P1/P2 candidates that sum to target
                for p1 in range(1, min(target_sum, 26)):
                    p2 = target_sum - p1
                    if 1 <= p2 <= 50 and p1 < p2:
                        candidates[0].extend([p1] * 3)
                        candidates[1].extend([p2] * 3)
                patterns_used.append(f"P1+P2 Constant ({target_sum})")
        
        # PATTERN 18: P4 ADDITION (Previous P4s add together)
        # P4 = prev_P4 + prev_prev_P4
        if len(draws) >= 3:
            p4_list = [sorted(d["numbers"])[3] for d in draws[:3]]
            predicted_p4 = p4_list[0] + p4_list[1]
            if predicted_p4 > 50:
                predicted_p4 = predicted_p4 % 50 if predicted_p4 % 50 != 0 else 50
            if 1 <= predicted_p4 <= 50:
                candidates[3].extend([predicted_p4] * 5)  # Weight heavily for P4
                patterns_used.append(f"P4 Addition ({p4_list[0]}+{p4_list[1]}={predicted_p4})")
        
        # PATTERN 19: HUNGER PATTERN (Missing number in neighborhood)
        # When 33 and 35/53 present, 43 is "hungry"
        if draws:
            recent_nums = draws[0]["numbers"]
            hungry_nums = find_hunger_number(recent_nums)
            for hungry in hungry_nums[:3]:
                if 1 <= hungry <= 50:
                    candidates[3].extend([hungry] * 4)  # P4 position
                    candidates[4].extend([hungry] * 3)  # P5 position
            if hungry_nums:
                patterns_used.append(f"Hunger ({hungry_nums[:3]})")
        
        # PATTERN 20: QC MIRROR (QC 16 ↔ QC 12)
        # Use QC mirror draw as reference
        if draws and len(draws) >= 20:
            # Get current QC (approximate from draw count in quarter)
            def parse_d(d):
                parts = d['date'].split('.')
                return (int(parts[2]), int(parts[1]), int(parts[0]))
            
            latest = draws[0]
            latest_date = parse_d(latest)
            year = latest_date[0]
            month = latest_date[1]
            
            # Determine quarter
            if month in [1, 2, 3]:
                q_months = [1, 2, 3]
            elif month in [4, 5, 6]:
                q_months = [4, 5, 6]
            elif month in [7, 8, 9]:
                q_months = [7, 8, 9]
            else:
                q_months = [10, 11, 12]
            
            # Get draws in this quarter
            q_draws = [d for d in draws if parse_d(d)[0] == year and parse_d(d)[1] in q_months]
            q_draws_sorted = sorted(q_draws, key=parse_d)
            
            if q_draws_sorted:
                current_qc = len(q_draws_sorted)
                # Mirror: reverse digits of QC
                mirror_qc = int(str(current_qc)[::-1]) if current_qc >= 10 else current_qc
                
                # Find the mirror QC draw
                if mirror_qc <= len(q_draws_sorted) and mirror_qc != current_qc:
                    mirror_draw = q_draws_sorted[mirror_qc - 1]
                    mirror_nums = sorted(mirror_draw["numbers"])
                    
                    # Use mirror draw's P2 + date for prediction
                    mirror_day = int(mirror_draw['date'].split('.')[0])
                    predicted_p2 = mirror_nums[1] + mirror_day
                    if predicted_p2 > 50:
                        predicted_p2 = predicted_p2 % 50 if predicted_p2 % 50 != 0 else 50
                    
                    if 1 <= predicted_p2 <= 50:
                        candidates[1].extend([predicted_p2] * 4)
                        patterns_used.append(f"QC Mirror ({current_qc}↔{mirror_qc})")
        
        # PATTERN 21: DATE MAGIC SIGN
        # When day + month = QC number, it's a SIGN! Use that draw
        if draws and len(draws) >= 15:
            def parse_d(d):
                parts = d['date'].split('.')
                return (int(parts[2]), int(parts[1]), int(parts[0]))
            
            # Find draws where day + month = position in quarter (date magic)
            for i, d in enumerate(draws[:20]):
                day = int(d['date'].split('.')[0])
                month = int(d['date'].split('.')[1])
                if day + month == i + 1:  # Date magic sign!
                    sign_nums = sorted(d["numbers"])
                    # Use this draw's numbers as reference
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].append(sign_nums[pos])
                    patterns_used.append(f"Date Magic Sign ({d['date']})")
                    break
        
        # PATTERN 22: QC1 PROPHECY NUMBER
        # The QC1 date forms the quarter's prophecy number (e.g., 02.01 → 12)
        if draws:
            def parse_d(d):
                parts = d['date'].split('.')
                return (int(parts[2]), int(parts[1]), int(parts[0]))
            
            latest = draws[0]
            latest_date = parse_d(latest)
            year = latest_date[0]
            month = latest_date[1]
            
            # Determine quarter
            if month in [1, 2, 3]:
                q_months = [1, 2, 3]
            elif month in [4, 5, 6]:
                q_months = [4, 5, 6]
            elif month in [7, 8, 9]:
                q_months = [7, 8, 9]
            else:
                q_months = [10, 11, 12]
            
            # Get QC1 (first draw of quarter)
            q_draws = [d for d in draws if parse_d(d)[0] == year and parse_d(d)[1] in q_months]
            q_draws_sorted = sorted(q_draws, key=parse_d)
            
            if q_draws_sorted:
                qc1 = q_draws_sorted[0]
                qc1_day = int(qc1['date'].split('.')[0])
                qc1_month = int(qc1['date'].split('.')[1])
                prophecy = qc1_day + qc1_month
                
                # Use prophecy number for P3 prediction: prev_P3 + prophecy
                if len(draws) >= 2:
                    prev_p3 = sorted(draws[0]["numbers"])[2]
                    predicted_p3 = prev_p3 + prophecy
                    if predicted_p3 > 50:
                        predicted_p3 = predicted_p3 % 50 if predicted_p3 % 50 != 0 else 50
                    if 1 <= predicted_p3 <= 50:
                        candidates[2].extend([predicted_p3] * 4)
                        patterns_used.append(f"Prophecy {prophecy} (P3={predicted_p3})")
        
        # PATTERN 23: HERO PAIRS (24↔49, 8↔33)
        # When one hero appears, boost its partner
        if draws:
            recent_nums = draws[0]["numbers"]
            hero_pairs = [(24, 49), (8, 33)]
            
            for h1, h2 in hero_pairs:
                if h1 in recent_nums and h2 not in recent_nums:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([h2] * 3)
                    patterns_used.append(f"Hero {h1}→{h2}")
                elif h2 in recent_nums and h1 not in recent_nums:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([h1] * 3)
                    patterns_used.append(f"Hero {h2}→{h1}")
        
        # PATTERN 24: STAR SUM = QC
        # Stars often sum to the QC number (e.g., 6+10=16 for QC16)
        if draws:
            def parse_d(d):
                parts = d['date'].split('.')
                return (int(parts[2]), int(parts[1]), int(parts[0]))
            
            latest = draws[0]
            latest_date = parse_d(latest)
            year = latest_date[0]
            month = latest_date[1]
            
            if month in [1, 2, 3]:
                q_months = [1, 2, 3]
            elif month in [4, 5, 6]:
                q_months = [4, 5, 6]
            elif month in [7, 8, 9]:
                q_months = [7, 8, 9]
            else:
                q_months = [10, 11, 12]
            
            q_draws = [d for d in draws if parse_d(d)[0] == year and parse_d(d)[1] in q_months]
            next_qc = len(q_draws) + 1
            
            # Find star pairs that sum to next QC
            if 3 <= next_qc <= 23:  # Valid star sum range (1+2=3 to 11+12=23)
                for s1 in range(1, 13):
                    s2 = next_qc - s1
                    if 1 <= s2 <= 12 and s1 < s2:
                        star_candidates.extend([s1, s2] * 3)
                patterns_used.append(f"Star Sum={next_qc}")
        
        # ═══════════════════════════════════════════════════════════════════
        # PATTERN 25: QUARTER COUNTING MAGIC 🎻 (63.4% hit rate!)
        # QC/Complement + Date → Predicts positions!
        # Each quarter = 27 draws (Q4 = 23), QC + Complement = 28 (or 24 for Q4)
        # ═══════════════════════════════════════════════════════════════════
        if draws:
            def parse_d(d):
                parts = d['date'].split('.')
                return (int(parts[2]), int(parts[1]), int(parts[0]))
            
            latest = draws[0]
            latest_date = parse_d(latest)
            year = latest_date[0]
            month = latest_date[1]
            day = latest_date[2]
            
            # Determine quarter and its length
            if month in [1, 2, 3]:
                q_months = [1, 2, 3]
                quarter_len = 27
            elif month in [4, 5, 6]:
                q_months = [4, 5, 6]
                quarter_len = 27
            elif month in [7, 8, 9]:
                q_months = [7, 8, 9]
                quarter_len = 27
            else:
                q_months = [10, 11, 12]
                quarter_len = 23  # Q4 is shorter!
            
            # Calculate current QC (draw count in quarter)
            q_draws = [d for d in draws if parse_d(d)[0] == year and parse_d(d)[1] in q_months]
            current_qc = len(q_draws)
            
            # Next QC is current + 1
            next_qc_num = current_qc + 1
            
            # Complement base: 28 for 27-draw quarters, 24 for 23-draw quarters
            comp_base = quarter_len + 1
            complement = comp_base - next_qc_num
            
            # Get next draw's likely day (estimate: +3 or +4 days)
            next_day = day + 3  # Tuesday/Friday pattern
            if next_day > 28:  # Simple wrap
                next_day = next_day - 28 + 1
            
            # 🎵 THE COUNTING FORMULAS 🎵
            counting_candidates = []
            
            # Day + QC → Often predicts P1-P5
            day_plus_qc = next_day + next_qc_num
            if 1 <= day_plus_qc <= 50:
                counting_candidates.append(('Day+QC', day_plus_qc))
            
            # Day + Complement → ESPECIALLY predicts P4! (6 hits in Q1 2026)
            day_plus_comp = next_day + complement
            if 1 <= day_plus_comp <= 50:
                counting_candidates.append(('Day+Comp', day_plus_comp))
            
            # QC direct → Sometimes IS the number (QC 5 = P1, QC 13 = P2, etc.)
            if 1 <= next_qc_num <= 50:
                counting_candidates.append(('QC', next_qc_num))
            
            # Complement direct → Can equal P2, P3, P4, P5
            if 1 <= complement <= 50:
                counting_candidates.append(('Comp', complement))
            
            # Month + QC
            month_plus_qc = month + next_qc_num
            if 1 <= month_plus_qc <= 50:
                counting_candidates.append(('Month+QC', month_plus_qc))
            
            # Month + Complement
            month_plus_comp = month + complement
            if 1 <= month_plus_comp <= 50:
                counting_candidates.append(('Month+Comp', month_plus_comp))
            
            # Apply candidates to positions with smart weighting
            for formula, value in counting_candidates:
                if formula == 'Day+Comp':
                    # Day+Comp loves P4! Weight heavily there
                    if 3 not in locked:
                        candidates[3].extend([value] * 5)  # P4 gets heavy weight
                    if 4 not in locked:
                        candidates[4].extend([value] * 3)  # P5 gets medium weight
                elif formula == 'QC':
                    # QC direct → Often P1 or P2
                    if 0 not in locked:
                        candidates[0].extend([value] * 4)  # P1
                    if 1 not in locked:
                        candidates[1].extend([value] * 4)  # P2
                    # Also add to stars if valid!
                    if 1 <= value <= 12:
                        star_candidates.extend([value] * 3)
                elif formula == 'Comp':
                    # Complement → Often P2 (like QC 1 → Comp 27 = P2!)
                    if 1 not in locked:
                        candidates[1].extend([value] * 4)
                    if 2 not in locked:
                        candidates[2].extend([value] * 3)
                    if 3 not in locked:
                        candidates[3].extend([value] * 3)
                elif formula == 'Day+QC':
                    # Day+QC → Various positions
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([value] * 2)
                else:
                    # Month formulas → Light weighting
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].append(value)
            
            # Log the pattern
            patterns_used.append(f"QC Counting {next_qc_num}/{complement} (63.4%)")
            
            # Special: If QC 1 or QC 27, the 27 is THE signature!
            if next_qc_num == 1 or next_qc_num == 27:
                if 1 not in locked:
                    candidates[1].extend([27] * 6)  # P2 = 27 is the quarter signature!
                patterns_used.append("Quarter Signature P2=27!")
        
        # ═══════════════════════════════════════════════════════════════════
        # 🎻 LUCKY JACK'S MUSICAL PATTERNS 🍀
        # Discovered through deep esoteric analysis with the user!
        # ═══════════════════════════════════════════════════════════════════
        
        # JACK PATTERN 1: P1 COUNTING MAGIC
        # P1 follows hidden count: 5→6→7→8→9→10→11...
        # The actual P1 ENCODES the count through additions!
        try:
            p1_counting = p1_counting_pattern(draws)
            if p1_counting.get('predicted_p1_candidates'):
                for p1_candidate, reason in p1_counting['predicted_p1_candidates'][:3]:
                    if 1 <= p1_candidate <= 50 and 0 not in locked:
                        candidates[0].extend([p1_candidate] * 6)  # Heavy weight for P1
                patterns_used.append(f"🎻 P1 Count→{p1_counting.get('count_expected', '?')}")
        except Exception:
            pass
        
        # JACK PATTERN 2: NEIGHBORHOOD HUNGER (GAP DETECTION)
        # When 27 at P2 and 29 at P3, 28 is HUNGRY!
        try:
            hunger = neighborhood_hunger(draws, num_recent=3)
            for hungry_item in hunger[:3]:
                hungry_num = hungry_item['hungry_number']
                if 1 <= hungry_num <= 50:
                    weight = 8 if hungry_item['urgency'] == 'HIGH' else 5
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([hungry_num] * weight)
                    patterns_used.append(f"🍽️ Hungry {hungry_num} (gap {hungry_item['between']})")
        except Exception:
            pass
        
        # JACK PATTERN 3: 49→45 CALL (22% = 2.2x random chance!)
        # When 49 at P5, 45 appears next 22% of the time!
        try:
            call_45 = p5_49_calls_45(draws)
            if call_45.get('should_include_45'):
                if 3 not in locked:
                    candidates[3].extend([45] * 10)  # Very heavy weight for P4!
                if 4 not in locked:
                    candidates[4].extend([45] * 6)
                patterns_used.append("🎵 49@P5→45! (22%=2.2x)")
        except Exception:
            pass
        
        # JACK PATTERN 4: QUARTER ECHO (Q2 2025 → Q2 2026)
        # Same quarter in previous year echoes patterns!
        try:
            if draws:
                latest_date = draws[0]['date']
                echo = quarter_echo(draws, latest_date)
                if echo.get('has_echo'):
                    echo_p2 = echo['echo_candidates'].get('P2')
                    echo_stars = echo['echo_candidates'].get('stars', [])
                    if echo_p2 and 1 <= echo_p2 <= 50 and 1 not in locked:
                        candidates[1].extend([echo_p2] * 5)  # P2 echoes strongly!
                    for s in echo_stars:
                        if 1 <= s <= 12:
                            star_candidates.extend([s] * 4)
                    patterns_used.append(f"🔄 Q-Echo P2={echo_p2}")
        except Exception:
            pass
        
        # JACK PATTERN 5: P4 SEQUENCE TRACKING
        # P4 counts: 44→45→46→47... with reverse encodings!
        try:
            p4_seq = p4_sequence_tracker(draws)
            if p4_seq.get('predictions'):
                for pred, reason in p4_seq['predictions'][:2]:
                    if 1 <= pred <= 50 and 3 not in locked:
                        candidates[3].extend([pred] * 5)
                patterns_used.append(f"📊 P4 Seq→{p4_seq.get('expected_next', '?')}")
        except Exception:
            pass
        
        # JACK PATTERN 6: P1+P2 SUM DIGIT ROOT = 8
        # P1+P2 sums often have digit root 8 (35→8, 17→8, 26→8)
        try:
            p1p2 = p1p2_sum_pattern(draws)
            if p1p2.get('suggested_pairs'):
                # Pick a few pairs that give digit root 8
                for p1, p2, total in p1p2['suggested_pairs'][:5]:
                    if 0 not in locked:
                        candidates[0].append(p1)
                    if 1 not in locked:
                        candidates[1].append(p2)
                patterns_used.append(f"∑ P1+P2→root8")
        except Exception:
            pass
        
        # JACK PATTERN 7: 8-FAMILY TRACKER
        # The 8-family (8,18,28,38,48) is very active!
        try:
            eight_fam = eight_family_tracker(draws)
            if eight_fam.get('hungriest_member'):
                hungry_8 = eight_fam['hungriest_member']
                if 1 <= hungry_8 <= 50:
                    # Add to appropriate positions based on value
                    if hungry_8 <= 20:
                        pos_weights = [(0, 4), (1, 3)]  # P1, P2
                    elif hungry_8 <= 35:
                        pos_weights = [(2, 4), (3, 3)]  # P3, P4
                    else:
                        pos_weights = [(3, 4), (4, 5)]  # P4, P5
                    
                    for pos, weight in pos_weights:
                        if pos not in locked:
                            candidates[pos].extend([hungry_8] * weight)
                    patterns_used.append(f"8️⃣ Family→{hungry_8}")
        except Exception:
            pass
        
        # JACK PATTERN 8: CIRCLE ENCODING OF MISSING NUMBERS
        # Honor missing 47 through 22 (22+25=47)
        # Honor missing 49 through 20+45 encoding
        try:
            # If we detect a "missing sequence" pattern, encode it
            if draws:
                last_nums = sorted(draws[0]['numbers'])
                # Check for 48 without 47 → 47 is missing, add 22
                if 48 in last_nums and 47 not in last_nums:
                    if 1 not in locked:
                        candidates[1].extend([22] * 4)  # 22 encodes missing 47
                    patterns_used.append("🎭 Missing 47→22")
                
                # Check for 50 without 49 → 49 is missing
                if 50 in last_nums and 49 not in last_nums:
                    # 49 encoded as 20+45 (20 "is" 4 via circle, 4+45=49)
                    if 2 not in locked:
                        candidates[2].extend([20] * 3)
                    if 3 not in locked:
                        candidates[3].extend([45] * 3)
                    patterns_used.append("🎭 Missing 49→20+45")
        except Exception:
            pass
        
        # JACK PATTERN 9: 🌟 STAR PROPHECY - Previous Stars Predict Next Draw! 🌟
        # 93.6% of draws have connections from previous stars!
        # The Stars tell the future: circle(S1), circle(S2), S1+S2, ending digits
        try:
            star_prophecy = star_prophecy_pattern(draws, track_gaps=True)
            
            # circle(S1) is a strong candidate (7.7%)
            if star_prophecy.get('circle_s1'):
                c_s1 = star_prophecy['circle_s1']
                if 1 <= c_s1 <= 50:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([c_s1] * 4)
                    patterns_used.append(f"🌟 circle(S1)={c_s1}")
            
            # circle(S2) is also strong (8.5%) - but lighter weight for variety
            if star_prophecy.get('circle_s2'):
                c_s2 = star_prophecy['circle_s2']
                if 1 <= c_s2 <= 50:
                    # Only add to P4, P5 with moderate weight
                    for pos in [3, 4]:
                        if pos not in locked:
                            candidates[pos].extend([c_s2] * 2)
                    patterns_used.append(f"🌟 circle(S2)={c_s2}")
            
            # S1+S2 sum often appears (14%!)
            if star_prophecy.get('star_sum'):
                star_sum = star_prophecy['star_sum']
                if 1 <= star_sum <= 50:
                    for pos in range(5):
                        if pos not in locked:
                            candidates[pos].extend([star_sum] * 4)
                    patterns_used.append(f"🌟 S1+S2={star_sum}")
            
            # Numbers ending in S1 - use sparingly for variety
            prev_s1 = star_prophecy.get('prev_stars', [2, 10])[0]
            if prev_s1 <= 9:
                ending_s1 = [n for n in range(prev_s1, 51, 10) if 1 <= n <= 50]
                # Only add to P2, P3 with light weight, and vary by ticket
                if ticket_index % 2 == 0:  # Every other ticket
                    for num in ending_s1[1:3]:  # Skip the smallest, take 2
                        if 1 not in locked:
                            candidates[1].append(num)
                        if 2 not in locked:
                            candidates[2].append(num)
                    patterns_used.append(f"🌟 ends in S1={prev_s1}")
            
            # Star repeat suggestions for star selection
            for star, reason, weight in star_prophecy.get('star_candidates', [])[:4]:
                if 1 <= star <= 12:
                    star_candidates.extend([star] * weight)
            
            # Boost very overdue patterns - but with controlled weighting for variety!
            for pattern_name, since, avg, factor in star_prophecy.get('due_patterns', [])[:2]:
                if factor > 1.5:  # Very overdue
                    if pattern_name == 'circle_s2' and star_prophecy.get('circle_s2'):
                        c_s2 = star_prophecy['circle_s2']
                        if 1 <= c_s2 <= 50:
                            # Only boost for P3, P4, P5 positions (not every position!)
                            # And use ticket_index to vary which tickets get the boost
                            if ticket_index % 3 != 2:  # 2 out of 3 tickets get boost
                                for pos in [2, 3, 4]:  # P3, P4, P5
                                    if pos not in locked:
                                        candidates[pos].extend([c_s2] * 3)
                                patterns_used.append(f"🔥 OVERDUE circle(S2)={c_s2} ({factor:.1f}x)")
                    
                    if pattern_name == 's2_appears':
                        prev_s2 = star_prophecy.get('prev_stars', [2, 10])[1]
                        if 1 <= prev_s2 <= 50:
                            # Only some tickets, and only certain positions
                            if ticket_index % 4 == 0:  # 1 in 4 tickets
                                for pos in [0, 1]:  # P1, P2
                                    if pos not in locked:
                                        candidates[pos].extend([prev_s2] * 2)
                                patterns_used.append(f"🔥 OVERDUE S2={prev_s2} ({factor:.1f}x)")
        except Exception:
            pass
        
        # JACK PATTERN 10: STAR DIFF → POSITION GAP
        # The gap between stars often equals a gap between positions in next draw
        try:
            if draws:
                prev_stars = sorted(draws[0].get('stars', [2, 10]))
                star_diff = prev_stars[1] - prev_stars[0]
                
                # Suggest number pairs with this gap
                # Particularly for P2-P1, P3-P2, P4-P3
                for base in range(1, 43):
                    partner = base + star_diff
                    if partner <= 50:
                        # Light weighting across positions
                        if 0 not in locked:
                            candidates[0].append(base)
                        if 1 not in locked:
                            candidates[1].append(partner)
                        break  # Just add one pair
                
                patterns_used.append(f"🌟 Gap={star_diff}")
        except Exception:
            pass
        
        # Build final numbers - SCENARIO P1/P2 MUST BE INCLUDED!
        final_numbers = [0] * 5
        used = set()
        
        # First, lock user-specified positions
        for pos, num in locked.items():
            final_numbers[pos] = num
            used.add(num)
            position_reasons[f"P{pos+1}"] = "Locked by user"
        
        # CRITICAL: Force scenario P1 into the ticket (it will be sorted later)
        # We add it to position 0 initially but sorting will place it correctly
        scenario_p1_included = False
        scenario_p2_included = False
        
        for pos in range(5):
            if pos in locked:
                continue
            
            pos_candidates = candidates[pos]
            scored = Counter(pos_candidates)
            
            # Add some randomness based on ticket index
            for num in rnd.sample(range(1, 51), 5):
                scored[num] += ticket_index * 0.1
            
            selected = None
            for num, _ in scored.most_common():
                if num not in used and 1 <= num <= 50:
                    selected = num
                    break
            
            if selected is None:
                available = [n for n in range(1, 51) if n not in used]
                selected = rnd.choice(available) if available else 1
            
            final_numbers[pos] = selected
            used.add(selected)
            
            # Track if scenario numbers got included
            if selected == scenario_p1:
                scenario_p1_included = True
            if selected == scenario_p2:
                scenario_p2_included = True
            
            position_reasons[f"P{pos+1}"] = f"Pattern consensus (score: {scored.get(selected, 0):.1f})"
        
        # FORCE scenario P1 if not included - replace lowest scored non-scenario number
        if not scenario_p1_included and scenario_p1 not in used:
            # Find the position with lowest score to replace
            min_pos = 0
            min_score = float('inf')
            for pos in range(5):
                if pos not in locked and final_numbers[pos] != scenario_p2:
                    score = Counter(candidates[pos]).get(final_numbers[pos], 0)
                    if score < min_score:
                        min_score = score
                        min_pos = pos
            
            old_num = final_numbers[min_pos]
            final_numbers[min_pos] = scenario_p1
            used.discard(old_num)
            used.add(scenario_p1)
            position_reasons[f"P{min_pos+1}"] = f"Scenario {scenario} P1={scenario_p1}"
        
        # FORCE scenario P2 if not included
        if not scenario_p2_included and scenario_p2 not in used and 1 <= scenario_p2 <= 50:
            # Find another position to replace
            min_pos = 0
            min_score = float('inf')
            for pos in range(5):
                if pos not in locked and final_numbers[pos] not in [scenario_p1, scenario_p2]:
                    score = Counter(candidates[pos]).get(final_numbers[pos], 0)
                    if score < min_score:
                        min_score = score
                        min_pos = pos
            
            if final_numbers[min_pos] not in [scenario_p1]:
                old_num = final_numbers[min_pos]
                final_numbers[min_pos] = scenario_p2
                used.discard(old_num)
                used.add(scenario_p2)
                position_reasons[f"P{min_pos+1}"] = f"Scenario {scenario} P2={scenario_p2}"
        
        # Sort for display (EuroMillions requirement)
        final_numbers = sorted(final_numbers)
        
        # ═══════════════════════════════════════════════════════════════════
        # P1+P2 CONSECUTIVE SUM PATTERN (OBSERVATION, NOT ENFORCEMENT!)
        # ═══════════════════════════════════════════════════════════════════
        # Track if current ticket's P1+P2 matches the previous draw's P1+P2
        # This happens ~2% exactly, ~15% within ±3
        # We ADD candidates based on previous P1+P2, but don't force it
        
        current_p1 = final_numbers[0]
        current_p2 = final_numbers[1]
        current_sum = current_p1 + current_p2
        
        # Check if this matches the previous draw's P1+P2 sum
        if draws:
            prev_nums = sorted(draws[0]["numbers"])
            prev_p1p2_sum = prev_nums[0] + prev_nums[1]
            
            if current_sum == prev_p1p2_sum:
                patterns_used.append(f"P1+P2 Consecutive Match! ({current_sum}={prev_p1p2_sum})")
                position_reasons["P1+P2"] = f"Consecutive sum match: {current_p1}+{current_p2}={current_sum}"
            elif abs(current_sum - prev_p1p2_sum) <= 3:
                patterns_used.append(f"P1+P2 Near Match ({current_sum} vs prev {prev_p1p2_sum}, diff={abs(current_sum-prev_p1p2_sum)})")
        
        # ═══════════════════════════════════════════════════════════════════
        # 🎵 MUSICAL TICKET ENFORCEMENT - THE SONGS! 🎵
        # ═══════════════════════════════════════════════════════════════════
        # Every ticket should have at least one "song" - a mathematical harmony
        # where positions add up (directly or via circle) to create other positions
        
        songs_found = find_songs_in_ticket(final_numbers)
        
        if not songs_found:
            # Try to make the ticket musical
            final_numbers, songs_found = make_ticket_musical(final_numbers)
        
        if songs_found:
            patterns_used.append(f"🎵 Musical: {songs_found[0]}")
            if len(songs_found) > 1:
                patterns_used.append(f"🎵 +{len(songs_found)-1} more songs")
            position_reasons["Music"] = f"Songs: {', '.join(songs_found[:2])}"
        
        # Select stars - WITH VARIETY BASED ON TICKET INDEX!
        star_scored = Counter(star_candidates)
        final_stars = []
        
        # Add variety: different tickets should explore different star combinations
        # Based on ticket_index, slightly favor different stars
        variety_boost = {
            0: [(1, 10), (2, 10), (3, 10)],      # Ticket 0: anchor with 10
            1: [(2, 3), (3, 4), (4, 5)],          # Ticket 1: small gap pairs
            2: [(5, 9), (6, 9), (4, 9)],          # Ticket 2: pairs with 9
            3: [(1, 11), (2, 11), (3, 12)],       # Ticket 3: high S2 pairs
            4: [(5, 10), (6, 10), (7, 10)],       # Ticket 4: mid-high with 10
            5: [(3, 7), (4, 8), (5, 7)],          # Ticket 5: medium pairs
            6: [(2, 12), (1, 12), (3, 11)],       # Ticket 6: extreme pairs
            7: [(6, 11), (7, 11), (8, 11)],       # Ticket 7: pairs with 11
            8: [(4, 6), (5, 8), (6, 8)],          # Ticket 8: medium-small pairs
        }
        
        # Get variety pairs for this ticket
        variety_pairs = variety_boost.get(ticket_index % 9, [(2, 10)])
        chosen_variety = variety_pairs[ticket_index % len(variety_pairs)]
        
        # Boost the variety pair
        star_scored[chosen_variety[0]] += 5
        star_scored[chosen_variety[1]] += 5
        
        for _ in range(2):
            selected_star = None
            for star, _ in star_scored.most_common():
                if star not in final_stars and 1 <= star <= 12:
                    selected_star = star
                    break
            
            if selected_star is None:
                available_stars = [s for s in range(1, 13) if s not in final_stars]
                selected_star = rnd.choice(available_stars)
            
            final_stars.append(selected_star)
        
        final_stars = sorted(final_stars)
        
        # Calculate confidence
        base_confidence = 0.25 + (len(patterns_used) * 0.03)
        confidence = min(0.85, base_confidence)
        
        return {
            "numbers": final_numbers,
            "stars": final_stars,
            "patterns_used": patterns_used,
            "confidence": confidence,
            "position_reasons": position_reasons,
            "scenario": scenario
        }
    
    @router.get("/health")
    async def health():
        return {"status": "healthy", "service": "EuroMillions Pattern Analyzer"}
    
    @router.get("/draws")
    async def get_draws(limit: int = 50):
        seeded = await seed_euromillions_if_empty()
        added = await add_new_draws_if_needed()
        draws = await get_euromillions_draws()
        return {"draws": draws[:limit], "count": len(draws[:limit]), "seeded": seeded, "added_new": added, "total_in_db": len(draws)}
    
    @router.get("/stats")
    async def get_stats():
        await seed_euromillions_if_empty()
        await add_new_draws_if_needed()
        draws = await get_euromillions_draws()
        
        if not draws:
            return {"error": "No draws available"}
        
        num_freq = Counter()
        for d in draws:
            for n in d["numbers"]:
                num_freq[n] += 1
        
        star_freq = Counter()
        for d in draws:
            for s in d["stars"]:
                star_freq[s] += 1
        
        gaps = pattern_gap_analysis(draws)
        star_gaps = pattern_star_gap_analysis(draws)
        min_sum, max_sum, avg_sum = pattern_sum_range(draws)
        
        # Calculate star gap patterns
        star_gap_dist = Counter()
        prev_gap_transitions = Counter()
        sorted_draws = sorted(draws, key=lambda x: x.get('date', ''), reverse=True)
        
        for i, d in enumerate(sorted_draws):
            stars = sorted(d["stars"])
            gap = stars[1] - stars[0]
            star_gap_dist[gap] += 1
            
            if i > 0:
                prev_stars = sorted(sorted_draws[i-1]["stars"])
                prev_gap = prev_stars[1] - prev_stars[0]
                prev_gap_transitions[(prev_gap, gap)] += 1
        
        # Find gap 6 trigger stats
        gap6_to_extreme = sum(count for (pg, cg), count in prev_gap_transitions.items() if pg == 6 and cg >= 8)
        gap6_total = sum(count for (pg, _), count in prev_gap_transitions.items() if pg == 6)
        
        return {
            "total_draws": len(draws),
            "number_frequency": dict(num_freq.most_common()),
            "star_frequency": dict(star_freq.most_common()),
            "number_gaps": gaps,
            "star_gaps": star_gaps,
            "sum_stats": {"min": min_sum, "max": max_sum, "avg": round(avg_sum, 1)},
            "consecutive_pair_rate": round(pattern_consecutive_pairs(draws) * 100, 1),
            "circle_partner_rate": round(pattern_circle_partners(draws) * 100, 1),
            "odd_even_distribution": pattern_odd_even_ratio(draws),
            "high_low_distribution": pattern_high_low_ratio(draws),
            "star_gap_distribution": dict(star_gap_dist.most_common()),
            "gap6_trigger_rate": round((gap6_to_extreme / gap6_total * 100) if gap6_total > 0 else 0, 1),
            "last_star_gap": sorted(sorted_draws[0]["stars"])[1] - sorted(sorted_draws[0]["stars"])[0] if sorted_draws else 0,
        }
    
    @router.post("/master-predictor")
    async def predict(request: EuroMillionsPredictionRequest):
        await seed_euromillions_if_empty()
        draws = await get_euromillions_draws()
        
        tickets = []
        num_tickets = min(request.num_tickets, 50)  # Allow up to 50 tickets
        
        # Check if DJ engine mode is requested
        use_dj = getattr(request, 'use_dj_engine', False) or getattr(request, 'scenario', None) == 'dj'
        target_date = getattr(request, 'target_date', None)
        
        # 🎧 DJ ENGINE MODE - Use backtested patterns!
        if use_dj:
            for ticket_idx in range(num_tickets):
                prediction = await master_predictor(
                    draws=draws,
                    birthday=request.birthday,
                    name=request.name,
                    locked_positions=request.locked_positions,
                    ticket_index=ticket_idx,
                    scenario="dj",
                    use_dj_engine=True,
                    target_date=target_date
                )
                tickets.append({
                    "ticket_number": ticket_idx + 1,
                    "numbers": prediction["numbers"],
                    "stars": prediction["stars"],
                    "patterns_used": prediction["patterns_used"],
                    "confidence": prediction["confidence"],
                    "position_reasons": prediction["position_reasons"],
                    "scenario": "dj"
                })
            
            price_per_ticket = 3.50  # EuroMillions price
            total_price = len(tickets) * price_per_ticket
            
            return {
                "tickets": tickets,
                "total_tickets": len(tickets),
                "price_per_ticket": price_per_ticket,
                "total_price": total_price,
                "currency": "CHF",
                "engine": "DJ Pattern Engine 🎧"
            }
        
        # Calculate distribution across scenarios (original mode)
        # For N tickets: ~1/3 low, ~1/3 medium, ~1/3 high
        scenario_counts = {
            "low": num_tickets // 3,
            "medium": num_tickets // 3,
            "high": num_tickets - (num_tickets // 3) * 2
        }
        
        ticket_idx = 0
        for scenario in ["low", "medium", "high"]:
            for _ in range(scenario_counts[scenario]):
                prediction = await master_predictor(
                    draws=draws,
                    birthday=request.birthday,
                    name=request.name,
                    locked_positions=request.locked_positions,
                    ticket_index=ticket_idx,
                    scenario=scenario
                )
                tickets.append({
                    "ticket_number": ticket_idx + 1,
                    "numbers": prediction["numbers"],
                    "stars": prediction["stars"],
                    "patterns_used": prediction["patterns_used"],
                    "confidence": prediction["confidence"],
                    "position_reasons": prediction["position_reasons"],
                    "scenario": prediction.get("scenario", scenario)
                })
                ticket_idx += 1
        
        # Sort by confidence but keep scenario grouping visible
        tickets.sort(key=lambda x: (-x["confidence"], x["scenario"]))
        
        price_per_ticket = 3.50
        total_price = len(tickets) * price_per_ticket
        
        return {
            "tickets": tickets,
            "total_tickets": len(tickets),
            "price_per_ticket": price_per_ticket,
            "total_price": total_price,
            "currency": "CHF"
        }
    
    @router.get("/analyze-ticket")
    async def analyze_ticket(numbers: str, stars: str):
        try:
            nums = [int(n.strip()) for n in numbers.split(",")]
            star_nums = [int(s.strip()) for s in stars.split(",")]
            
            if len(nums) != 5 or not all(1 <= n <= 50 for n in nums):
                raise ValueError("Need exactly 5 numbers between 1-50")
            if len(star_nums) != 2 or not all(1 <= s <= 12 for s in star_nums):
                raise ValueError("Need exactly 2 stars between 1-12")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        await seed_euromillions_if_empty()
        draws = await get_euromillions_draws()
        nums = sorted(nums)
        star_nums = sorted(star_nums)
        
        analysis = {
            "numbers": nums,
            "stars": star_nums,
            "sum": sum(nums),
            "star_sum": sum(star_nums),
            "insights": []
        }
        
        min_sum, max_sum, avg_sum = pattern_sum_range(draws)
        if min_sum <= sum(nums) <= max_sum:
            analysis["insights"].append(f"✓ Sum ({sum(nums)}) is within typical range ({int(min_sum)}-{int(max_sum)})")
        else:
            analysis["insights"].append(f"⚠ Sum ({sum(nums)}) is outside typical range ({int(min_sum)}-{int(max_sum)})")
        
        has_consecutive = any(nums[i+1] - nums[i] == 1 for i in range(len(nums)-1))
        consec_rate = pattern_consecutive_pairs(draws)
        if has_consecutive:
            analysis["insights"].append(f"✓ Has consecutive pair (appears in {consec_rate:.0%} of draws)")
        
        families_used = set()
        for fam_id, fam_nums in FAMILIES.items():
            if any(n in fam_nums for n in nums):
                families_used.add(fam_id)
        analysis["insights"].append(f"Covers {len(families_used)}/5 number families")
        
        odds = sum(1 for n in nums if n % 2 == 1)
        evens = 5 - odds
        odd_even = pattern_odd_even_ratio(draws)
        ratio_key = f"{odds}O-{evens}E"
        ratio_freq = odd_even.get(ratio_key, 0)
        analysis["insights"].append(f"Odd/Even ratio {ratio_key} (appears in {ratio_freq:.0%} of draws)")
        
        gaps = pattern_gap_analysis(draws)
        avg_gap = sum(gaps.get(n, 0) for n in nums) / 5
        analysis["insights"].append(f"Average gap for these numbers: {avg_gap:.1f} draws")
        
        star_gaps = pattern_star_gap_analysis(draws)
        star_avg_gap = sum(star_gaps.get(s, 0) for s in star_nums) / 2
        analysis["insights"].append(f"Average gap for stars: {star_avg_gap:.1f} draws")
        
        score = 50
        if min_sum <= sum(nums) <= max_sum:
            score += 15
        if len(families_used) >= 4:
            score += 10
        if 0.1 <= ratio_freq <= 0.4:
            score += 10
        if has_consecutive and consec_rate > 0.3:
            score += 5
        if avg_gap > 5:
            score += 10
        
        analysis["score"] = min(100, score)
        analysis["rating"] = "Excellent" if score >= 80 else "Good" if score >= 60 else "Average" if score >= 40 else "Poor"
        
        return analysis
    
    # ========== AUTO-UPDATE EUROMILLIONS RESULTS ==========
    @router.post("/update-results")
    async def update_euromillions_results():
        """
        Fetch latest EuroMillions results from API and update database.
        Uses the free pedro-mealha EuroMillions API.
        """
        import httpx
        
        try:
            added_count = 0
            skipped_count = 0
            
            # Fetch current year and last year
            current_year = datetime.now().year
            years_to_fetch = [current_year, current_year - 1]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for year in years_to_fetch:
                    response = await client.get(f"https://euromillions.api.pedromealha.dev/v1/draws?year={year}")
                    
                    if response.status_code != 200:
                        continue
                    
                    draws_data = response.json()
                    
                    for draw in draws_data:
                        draw_date_raw = draw.get("date", "")
                        
                        try:
                            dt = datetime.strptime(draw_date_raw, "%Y-%m-%d")
                            draw_date = dt.strftime("%d.%m.%Y")
                        except:
                            continue
                        
                        numbers_raw = draw.get("numbers", [])
                        stars_raw = draw.get("stars", [])
                        
                        numbers = sorted([int(n) for n in numbers_raw])
                        stars = sorted([int(s) for s in stars_raw])
                        
                        if len(numbers) != 5 or len(stars) != 2:
                            continue
                        
                        existing = await db.euromillions_draws.find_one({"date": draw_date})
                        if existing:
                            skipped_count += 1
                            continue
                        
                        new_draw = {
                            "date": draw_date,
                            "numbers": numbers,
                            "stars": stars,
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                        
                        await db.euromillions_draws.insert_one(new_draw)
                        added_count += 1
            
            total = await db.euromillions_draws.count_documents({})
            
            # Get actual latest draw by parsing dates
            all_draws = await db.euromillions_draws.find().to_list(length=None)
            
            def parse_date(d):
                try:
                    return datetime.strptime(d['date'], '%d.%m.%Y')
                except:
                    return datetime.min
            
            if all_draws:
                latest = max(all_draws, key=parse_date)
                latest_date = latest["date"]
                latest_numbers = latest.get("numbers", [])
                latest_stars = latest.get("stars", [])
            else:
                latest_date = "N/A"
                latest_numbers = []
                latest_stars = []
            
            return {
                "message": f"Update complete! Added {added_count} new draws.",
                "added": added_count,
                "skipped": skipped_count,
                "total": total,
                "latest_draw": {
                    "date": latest_date,
                    "numbers": latest_numbers,
                    "stars": latest_stars
                }
            }
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="API request timed out")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating results: {str(e)}")
    
    @router.get("/last-update")
    async def get_last_update():
        """Get info about the most recent draw in database"""
        total = await db.euromillions_draws.count_documents({})
        
        if total == 0:
            return {"message": "No draws in database", "total": 0}
        
        # Get actual latest draw by parsing dates
        all_draws = await db.euromillions_draws.find().to_list(length=None)
        
        def parse_date(d):
            try:
                return datetime.strptime(d['date'], '%d.%m.%Y')
            except:
                return datetime.min
        
        latest = max(all_draws, key=parse_date)
        
        return {
            "latest_date": latest["date"],
            "latest_numbers": latest.get("numbers", []),
            "latest_stars": latest.get("stars", []),
            "total_draws": total
        }
    
    # =============================================================================
    # 🎻 EUROMILLIONS STORY GENERATOR & HIT TRACKER 🍀
    # =============================================================================
    
    @router.get("/story-generator-save")
    async def generate_and_save_euro_story_predictions(target_date: str = None, num_tickets: int = 8):
        """Generate EuroMillions story predictions AND save them for hit tracking"""
        from datetime import timedelta
        from bson import ObjectId
        
        await seed_euromillions_if_empty()
        draws = await get_euromillions_draws()
        
        if not draws:
            raise HTTPException(status_code=404, detail="No EuroMillions draws found")
        
        # Calculate next draw date if not provided (Tue & Fri for EuroMillions)
        if not target_date:
            today = datetime.now()
            # EuroMillions draws are Tuesday (1) and Friday (4)
            days_until_tue = (1 - today.weekday()) % 7
            days_until_fri = (4 - today.weekday()) % 7
            if days_until_tue == 0:
                days_until_tue = 7
            if days_until_fri == 0:
                days_until_fri = 7
            next_draw = min(days_until_tue, days_until_fri)
            target = today + timedelta(days=next_draw)
            target_date = target.strftime("%d.%m.%Y")
        
        # Generate tickets using the master predictor logic with Jack patterns
        tickets = []
        for i in range(num_tickets):
            scenario = ["low", "medium", "high"][i % 3]
            prediction = await master_predictor(
                draws=draws,
                birthday=None,
                name=None,
                locked_positions={},
                ticket_index=i,
                scenario=scenario
            )
            tickets.append({
                "ticket_number": i + 1,
                "numbers": prediction["numbers"],
                "stars": prediction["stars"],
                "patterns_used": prediction["patterns_used"],
                "confidence": prediction["confidence"],
                "story": ", ".join(prediction["patterns_used"][:2]) if prediction["patterns_used"] else "Musical Pattern"
            })
        
        # Save to euromillions_generations collection for hit tracking
        generation = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "target_date": target_date,
            "generation_type": "euromillions_story",
            "lottery_type": "euromillions",
            "tickets": tickets,
            "hits_calculated": False,
            "hit_results": None,
            "total_hits": 0,
            "star_hits": 0,
            "best_ticket_hits": 0
        }
        
        result = await db.euromillions_generations.insert_one(generation)
        gen_id = str(result.inserted_id)
        
        return {
            "generation_id": gen_id,
            "saved": True,
            "target_date": target_date,
            "num_tickets": len(tickets),
            "cost_estimate": f"{len(tickets) * 3.50:.2f} CHF",
            "tickets": tickets
        }
    
    @router.get("/generation-history")
    async def get_euro_generation_history(limit: int = 50):
        """Get all saved EuroMillions generations with hit data"""
        generations = await db.euromillions_generations.find(
            {},
            {"_id": 1, "generated_at": 1, "target_date": 1, "tickets": 1, 
             "hits_calculated": 1, "hit_results": 1, "total_hits": 1, 
             "star_hits": 1, "best_ticket_hits": 1}
        ).sort("generated_at", -1).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string
        for gen in generations:
            gen["_id"] = str(gen["_id"])
        
        return {
            "count": len(generations),
            "generations": generations
        }
    
    @router.post("/calculate-hits/{generation_id}")
    async def calculate_euro_hits_for_generation(generation_id: str):
        """Calculate hits for a specific EuroMillions generation"""
        from bson import ObjectId
        
        try:
            gen = await db.euromillions_generations.find_one(
                {"_id": ObjectId(generation_id)}
            )
        except Exception:
            return {"error": "Invalid generation ID"}
        
        if not gen:
            return {"error": "Generation not found"}
        
        target_date = gen["target_date"]
        
        # Get actual draw for target date
        actual_draw = await db.euromillions_draws.find_one(
            {"date": target_date},
            {"_id": 0}
        )
        
        if not actual_draw:
            return {
                "error": f"Draw for {target_date} not yet available",
                "generation_id": generation_id,
                "target_date": target_date,
                "status": "PENDING"
            }
        
        actual_numbers = set(actual_draw.get("numbers", []))
        actual_stars = set(actual_draw.get("stars", []))
        
        hit_results = []
        total_number_hits = 0
        total_star_hits = 0
        best_ticket_hits = 0
        
        for i, ticket in enumerate(gen["tickets"]):
            ticket_numbers = set(ticket.get("numbers", []))
            ticket_stars = set(ticket.get("stars", []))
            
            # Find matching numbers and stars
            number_hits = ticket_numbers & actual_numbers
            star_hits = ticket_stars & actual_stars
            
            hit_count = len(number_hits)
            star_hit_count = len(star_hits)
            total_number_hits += hit_count
            total_star_hits += star_hit_count
            
            if hit_count > best_ticket_hits:
                best_ticket_hits = hit_count
            
            hit_results.append({
                "ticket_num": i + 1,
                "number_hits": list(number_hits),
                "star_hits": list(star_hits),
                "hit_count": hit_count,
                "star_hit_count": star_hit_count,
                "total_score": f"{hit_count}/5 + {star_hit_count}/2"
            })
        
        # Update the generation with hit results
        await db.euromillions_generations.update_one(
            {"_id": ObjectId(generation_id)},
            {"$set": {
                "hits_calculated": True,
                "hit_results": hit_results,
                "total_hits": total_number_hits,
                "star_hits": total_star_hits,
                "best_ticket_hits": best_ticket_hits,
                "actual_draw": {
                    "numbers": actual_draw.get("numbers", []),
                    "stars": actual_draw.get("stars", [])
                }
            }}
        )
        
        return {
            "success": True,
            "generation_id": generation_id,
            "target_date": target_date,
            "actual_draw": {
                "numbers": actual_draw.get("numbers", []),
                "stars": actual_draw.get("stars", [])
            },
            "total_number_hits": total_number_hits,
            "total_star_hits": total_star_hits,
            "best_ticket_hits": best_ticket_hits,
            "hit_results": hit_results
        }
    
    @router.post("/recalculate-all-hits")
    async def recalculate_all_euro_hits():
        """Recalculate hits for all pending EuroMillions generations"""
        from bson import ObjectId
        
        pending = await db.euromillions_generations.find(
            {"hits_calculated": False}
        ).to_list(length=100)
        
        calculated = 0
        still_pending = 0
        
        for gen in pending:
            gen_id = str(gen["_id"])
            result = await calculate_euro_hits_for_generation(gen_id)
            if result.get("success"):
                calculated += 1
            else:
                still_pending += 1
        
        return {
            "calculated": calculated,
            "still_pending": still_pending,
            "message": f"Calculated hits for {calculated} generations, {still_pending} still pending"
        }
    
    @router.get("/hit-stats")
    async def get_euro_hit_stats():
        """Get overall EuroMillions hit statistics"""
        # Get all calculated generations
        gens = await db.euromillions_generations.find(
            {"hits_calculated": True}
        ).to_list(length=1000)
        
        if not gens:
            return {
                "last_draw": None,
                "stats": {
                    "total_generations": 0,
                    "total_number_hits": 0,
                    "total_star_hits": 0,
                    "best_ever_hits": 0,
                    "tickets_with_3plus": 0
                }
            }
        
        total_number_hits = sum(g.get("total_hits", 0) for g in gens)
        total_star_hits = sum(g.get("star_hits", 0) for g in gens)
        best_ever = max(g.get("best_ticket_hits", 0) for g in gens)
        
        # Count tickets with 3+ hits
        tickets_3plus = 0
        for gen in gens:
            for result in gen.get("hit_results", []):
                if result.get("hit_count", 0) >= 3:
                    tickets_3plus += 1
        
        # Get last draw
        draws = await db.euromillions_draws.find().to_list(length=None)
        last_draw = None
        if draws:
            def parse_date(d):
                try:
                    return datetime.strptime(d['date'], '%d.%m.%Y')
                except:
                    return datetime.min
            last_draw = max(draws, key=parse_date)
        
        return {
            "last_draw": {
                "date": last_draw.get("date") if last_draw else None,
                "numbers": last_draw.get("numbers", []) if last_draw else [],
                "stars": last_draw.get("stars", []) if last_draw else []
            },
            "stats": {
                "total_generations": len(gens),
                "total_number_hits": total_number_hits,
                "total_star_hits": total_star_hits,
                "best_ever_hits": best_ever,
                "tickets_with_3plus": tickets_3plus
            }
        }
    
    @router.get("/last-draw")
    async def get_euro_last_draw():
        """Get the most recent EuroMillions draw result"""
        draws = await db.euromillions_draws.find().to_list(length=None)
        
        if not draws:
            return {"error": "No draws found"}
        
        def parse_date(d):
            try:
                return datetime.strptime(d['date'], '%d.%m.%Y')
            except:
                return datetime.min
        
        last_draw = max(draws, key=parse_date)
        
        return {
            "date": last_draw.get("date"),
            "numbers": last_draw.get("numbers", []),
            "stars": last_draw.get("stars", [])
        }
    
    return router
