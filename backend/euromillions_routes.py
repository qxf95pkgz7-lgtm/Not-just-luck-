"""
EuroMillions Pattern Analyzer Routes
5 numbers (1-50) + 2 stars (1-12)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
from collections import Counter, defaultdict
import random as rnd

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
    
    async def master_predictor(draws, birthday=None, name=None, locked_positions=None, ticket_index=0):
        """Master prediction algorithm for EuroMillions"""
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
                "position_reasons": {}
            }
        
        locked = {}
        if locked_positions:
            for pos_key, value in locked_positions.items():
                pos_idx = int(pos_key.replace("P", "")) - 1
                if 0 <= pos_idx < 5 and 1 <= value <= 50:
                    locked[pos_idx] = value
        
        # Pattern 1: Position Frequency
        for pos in range(5):
            if pos not in locked:
                freq = pattern_position_frequency(draws, pos)
                top_nums = sorted(freq.keys(), key=lambda x: freq.get(x, 0), reverse=True)[:10]
                candidates[pos].extend(top_nums)
        patterns_used.append("Position Frequency")
        
        # Pattern 2: Gap Analysis
        gaps = pattern_gap_analysis(draws)
        due_numbers = sorted(gaps.keys(), key=lambda x: gaps[x], reverse=True)[:15]
        for pos in range(5):
            if pos not in locked:
                candidates[pos].extend(due_numbers[:5])
        patterns_used.append("Gap Analysis")
        
        # Pattern 3: Family Spread
        family_nums = [rnd.choice(fam_nums) for fam_nums in FAMILIES.values()]
        for pos in range(5):
            if pos not in locked:
                candidates[pos].extend(family_nums)
        patterns_used.append("Family Spread")
        
        # Pattern 4: Recent Hot Numbers
        recent = draws[:5]
        recent_hot = Counter()
        for d in recent:
            for n in d["numbers"]:
                recent_hot[n] += 1
        hot_nums = [n for n, _ in recent_hot.most_common(10)]
        for pos in range(5):
            if pos not in locked:
                candidates[pos].extend(hot_nums[:3])
        patterns_used.append("Recent Hot Numbers")
        
        # Pattern 5: Consecutive Pairs
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
        star_freq = pattern_star_frequency(draws)
        top_stars = sorted(star_freq.keys(), key=lambda x: star_freq.get(x, 0), reverse=True)[:6]
        star_candidates.extend(top_stars)
        
        star_gaps = pattern_star_gap_analysis(draws)
        due_stars = sorted(star_gaps.keys(), key=lambda x: star_gaps[x], reverse=True)[:4]
        star_candidates.extend(due_stars)
        
        star_sums = pattern_star_sum(draws)
        target_sum = max(star_sums.keys(), key=lambda x: star_sums.get(x, 0)) if star_sums else 13
        patterns_used.append(f"Star Sum Target ({target_sum})")
        
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
        
        # Build final numbers
        final_numbers = [0] * 5
        used = set()
        
        for pos, num in locked.items():
            final_numbers[pos] = num
            used.add(num)
            position_reasons[f"P{pos+1}"] = "Locked by user"
        
        for pos in range(5):
            if pos in locked:
                continue
            
            pos_candidates = candidates[pos]
            scored = Counter(pos_candidates)
            
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
            position_reasons[f"P{pos+1}"] = f"Pattern consensus (score: {scored.get(selected, 0):.1f})"
        
        final_numbers = sorted(final_numbers)
        
        # Select stars
        star_scored = Counter(star_candidates)
        final_stars = []
        
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
            "position_reasons": position_reasons
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
        for i in range(min(request.num_tickets, 20)):
            prediction = await master_predictor(
                draws=draws,
                birthday=request.birthday,
                name=request.name,
                locked_positions=request.locked_positions,
                ticket_index=i
            )
            tickets.append({
                "ticket_number": i + 1,
                "numbers": prediction["numbers"],
                "stars": prediction["stars"],
                "patterns_used": prediction["patterns_used"],
                "confidence": prediction["confidence"],
                "position_reasons": prediction["position_reasons"],
            })
        
        tickets.sort(key=lambda x: x["confidence"], reverse=True)
        
        price_per_ticket = 2.50
        total_price = len(tickets) * price_per_ticket
        
        return {
            "tickets": tickets,
            "total_tickets": len(tickets),
            "price_per_ticket": price_per_ticket,
            "total_price": total_price,
            "currency": "EUR"
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
    
    return router
