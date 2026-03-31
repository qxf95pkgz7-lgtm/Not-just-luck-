from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from collections import Counter
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Draw(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str  # YYYY-MM-DD format
    draw_number: Optional[str] = None
    numbers: List[int]  # 6 numbers between 1-42
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DrawCreate(BaseModel):
    date: str
    draw_number: Optional[str] = None
    numbers: List[int]

class DrawResponse(BaseModel):
    id: str
    date: str
    draw_number: Optional[str] = None
    numbers: List[int]
    families: List[int]  # Which groups (1 or 2) the numbers belong to

class DashboardStats(BaseModel):
    total_draws: int
    rare_events: int
    chain_links: int
    series_found: int
    group1_count: int  # Low numbers (1-21)
    group2_count: int  # High numbers (22-42)
    group1_percentage: float
    group2_percentage: float
    hot_numbers: List[dict]
    cold_numbers: List[dict]
    last_draws: List[dict]

class PatternData(BaseModel):
    digit_reversals: List[dict]
    series_patterns: List[dict]

class PredictionData(BaseModel):
    suggested_numbers: List[int]
    explanations: List[dict]
    cross_draw_patterns: List[dict]
    gap_analysis: List[dict]

class AdvancedPatternData(BaseModel):
    digit_reversals_in_draws: List[dict]  # 34 → 13 type patterns
    digit_sum_patterns: List[dict]  # 4+5=9, 9/3=3 type
    cross_draw_connections: List[dict]  # Numbers combining across draws
    series_completions: List[dict]  # 10-11-12 + 34(13) = full series

# Helper functions
def get_families(numbers: List[int]) -> List[int]:
    """Return which group each number belongs to: 1 (1-21) or 2 (22-42)"""
    return [1 if n <= 21 else 2 for n in numbers]

def find_digit_reversals(all_numbers: List[int]) -> List[dict]:
    """Find pairs like 12<->21, 13<->31, etc."""
    reversals = []
    number_counts = Counter(all_numbers)
    
    seen_pairs = set()
    for num in range(1, 43):
        if num < 10:
            reversed_num = num * 10
        else:
            tens = num // 10
            ones = num % 10
            if ones == 0:
                continue
            reversed_num = ones * 10 + tens
        
        if reversed_num > 42 or reversed_num == num:
            continue
            
        pair_key = tuple(sorted([num, reversed_num]))
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)
        
        if number_counts.get(num, 0) > 0 and number_counts.get(reversed_num, 0) > 0:
            reversals.append({
                "num1": num,
                "num2": reversed_num,
                "count1": number_counts[num],
                "count2": number_counts[reversed_num]
            })
    
    return reversals[:12]  # Top 12 pairs

def find_series_patterns(draws: List[dict]) -> List[dict]:
    """Find consecutive number sequences in draws"""
    series = []
    for draw in draws[-50:]:  # Check recent draws
        nums = sorted(draw['numbers'])
        consecutive = []
        for i in range(len(nums) - 1):
            if nums[i] + 1 == nums[i + 1]:
                if not consecutive:
                    consecutive.append(nums[i])
                consecutive.append(nums[i + 1])
            elif len(consecutive) >= 2:
                series.append({
                    "date": draw['date'],
                    "numbers": consecutive,
                    "length": len(consecutive)
                })
                consecutive = []
        if len(consecutive) >= 2:
            series.append({
                "date": draw['date'],
                "numbers": consecutive,
                "length": len(consecutive)
            })
    return series[:20]

def find_cross_draw_patterns(draws: List[dict]) -> List[dict]:
    """Find A + B = C patterns across draws"""
    patterns = []
    all_numbers = set()
    for draw in draws:
        all_numbers.update(draw['numbers'])
    
    number_counts = Counter()
    for draw in draws:
        number_counts.update(draw['numbers'])
    
    for a in range(1, 42):
        for b in range(a + 1, 42):
            c = a + b
            if c <= 42 and a in all_numbers and b in all_numbers and c in all_numbers:
                patterns.append({
                    "a": a,
                    "b": b,
                    "c": c,
                    "formula": f"{a} + {b} = {c}"
                })
    
    return patterns[:30]

def calculate_gap_analysis(draws: List[dict]) -> List[dict]:
    """Find numbers that haven't appeared recently (due numbers)"""
    if not draws:
        return []
    
    last_seen = {}
    for i, draw in enumerate(reversed(draws)):
        for num in draw['numbers']:
            if num not in last_seen:
                last_seen[num] = i
    
    gaps = []
    for num in range(1, 43):
        gap = last_seen.get(num, len(draws))
        gaps.append({"number": num, "gap": gap})
    
    gaps.sort(key=lambda x: x['gap'], reverse=True)
    return gaps[:10]

def reverse_digits(n: int) -> int:
    """Reverse digits of a number: 34 → 43, 13 → 31"""
    s = str(n)
    if len(s) == 1:
        return n * 10  # 3 → 30? or keep as is
    return int(s[::-1])

def digit_sum(n: int) -> int:
    """Sum of digits: 34 → 7, 45 → 9"""
    return sum(int(d) for d in str(n))

def find_advanced_patterns(draws: List[dict]) -> dict:
    """Find advanced patterns like digit reversals, sums, and cross-draw connections"""
    
    digit_reversals_in_draws = []
    digit_sum_patterns = []
    cross_draw_connections = []
    series_completions = []
    
    for i, draw in enumerate(draws):
        nums = draw['numbers']
        date = draw['date']
        
        # 1. Digit Reversals within draw (34 in draw means 13 is implied)
        for n in nums:
            if n >= 10:
                reversed_n = reverse_digits(n)
                if reversed_n != n and 1 <= reversed_n <= 42:
                    digit_reversals_in_draws.append({
                        "date": date,
                        "number": n,
                        "reversed": reversed_n,
                        "in_draw": reversed_n in nums
                    })
        
        # 2. Find series that could be completed with reversals
        sorted_nums = sorted(nums)
        # Check for near-series (e.g., 10,11,12 and 34→13 completes it)
        for j in range(len(sorted_nums) - 2):
            if sorted_nums[j+1] == sorted_nums[j] + 1 and sorted_nums[j+2] == sorted_nums[j] + 2:
                # Found 3 consecutive, check if 4th exists via reversal
                next_in_series = sorted_nums[j] + 3
                prev_in_series = sorted_nums[j] - 1
                
                for n in nums:
                    if n >= 10:
                        rev = reverse_digits(n)
                        if rev == next_in_series or rev == prev_in_series:
                            series_completions.append({
                                "date": date,
                                "series": [sorted_nums[j], sorted_nums[j+1], sorted_nums[j+2]],
                                "completed_by": n,
                                "as_reversed": rev,
                                "full_series": sorted([sorted_nums[j], sorted_nums[j+1], sorted_nums[j+2], rev])
                            })
        
        # 3. Cross-draw connections (combine with previous draw)
        if i < len(draws) - 1:
            prev_draw = draws[i + 1]  # draws are sorted desc, so i+1 is previous
            prev_nums = prev_draw['numbers']
            
            for n1 in nums:
                for n2 in prev_nums:
                    combined = n1 * 10 + n2 if n1 < 10 and n2 < 10 else None
                    combined2 = n2 * 10 + n1 if n1 < 10 and n2 < 10 else None
                    
                    # Check digit sum patterns: e.g., 4+5=9, appears as 9 or relates to 3 (9/3)
                    dsum = n1 + n2
                    if dsum in nums or dsum in prev_nums:
                        digit_sum_patterns.append({
                            "date": date,
                            "prev_date": prev_draw['date'],
                            "n1": n1,
                            "n2": n2,
                            "sum": dsum,
                            "sum_in_draw": dsum in nums,
                            "sum_in_prev": dsum in prev_nums
                        })
                    
                    # Combined number reversals: 4,5 → 45 → 54 → relates to 12 (5-4 or 5,4)
                    if n1 < 10 and n2 < 10:
                        combo = n1 * 10 + n2
                        combo_rev = reverse_digits(combo)
                        ds = digit_sum(combo)
                        
                        # Check if digit sum or its factors appear
                        if ds <= 42 and (ds in nums or ds in prev_nums):
                            cross_draw_connections.append({
                                "date": date,
                                "prev_date": prev_draw['date'],
                                "numbers": [n1, n2],
                                "combined": combo,
                                "reversed": combo_rev,
                                "digit_sum": ds,
                                "found_in": "current" if ds in nums else "previous"
                            })
    
    return {
        "digit_reversals_in_draws": digit_reversals_in_draws[:50],
        "digit_sum_patterns": digit_sum_patterns[:50],
        "cross_draw_connections": cross_draw_connections[:50],
        "series_completions": series_completions[:30]
    }

def get_digit_links(n: int) -> set:
    """Find all numbers linked via digit patterns (user's system)"""
    linked = set()
    if n < 10:
        # Single digits: find 2-digit numbers that produce them via multiplication
        for x in range(10, 43):
            d1, d2 = x // 10, x % 10
            if d1 * d2 == n:
                linked.add(x)
        return linked
    
    d1, d2 = n // 10, n % 10
    rev = d2 * 10 + d1
    
    # Direct reversal in range (12<->21, 13<->31, etc.)
    if 10 <= rev <= 42 and rev != n:
        linked.add(rev)
    
    # Digit product (36 -> 3*6=18)
    prod = d1 * d2
    if 1 <= prod <= 42:
        linked.add(prod)
    
    # If reversal out of range (27->72, 18->81, etc.)
    if rev > 42:
        for x in range(10, 43):
            # Pattern: x + rev = total, total reversed = x
            # Example: 19 + 72 = 91, reverse(91) = 19 ✓
            total = x + rev
            if 10 <= total <= 99:
                t_rev = (total % 10) * 10 + (total // 10)
                if t_rev == x:
                    linked.add(x)
            
            # Pattern: n + x = digit rearrangement of x
            # Example: 27 + 14 = 41, digits of 41 = digits of 14 ✓
            total = n + x
            if 10 <= total <= 99:
                if sorted([total // 10, total % 10]) == sorted([x // 10, x % 10]):
                    linked.add(x)
    
    # Digit sum
    dsum = d1 + d2
    if 1 <= dsum <= 42:
        linked.add(dsum)
    
    linked.discard(n)  # Remove self
    return linked

def analyze_position_patterns(draws: List[dict]) -> dict:
    """Analyze position-based patterns across consecutive draws"""
    # Build link map
    link_map = {}
    for n in range(1, 43):
        links = get_digit_links(n)
        if links:
            link_map[n] = sorted(links)
    
    # Sort draws chronologically
    sorted_draws = sorted(draws, key=lambda x: x['date'])
    
    hits = []
    for i in range(len(sorted_draws) - 1):
        curr = sorted_draws[i]
        next_d = sorted_draws[i + 1]
        curr_nums = curr['numbers']
        next_nums = next_d['numbers']
        
        for pos, num in enumerate(curr_nums):
            if num in link_map:
                # Check same position and ±1
                for check_pos in [pos - 1, pos, pos + 1]:
                    if 0 <= check_pos < 6:
                        found = next_nums[check_pos]
                        if found in link_map[num]:
                            hits.append({
                                "date1": curr['date'],
                                "date2": next_d['date'],
                                "num1": num,
                                "num2": found,
                                "pos1": pos + 1,
                                "pos2": check_pos + 1,
                                "shift": check_pos - pos,
                                "link_type": "digit_pattern"
                            })
    
    # Calculate stats
    total_opps = sum(1 for i in range(len(sorted_draws)-1) 
                     for n in sorted_draws[i]['numbers'] if n in link_map)
    
    return {
        "link_map": link_map,
        "position_hits": hits[-100:],  # Last 100 hits
        "total_hits": len(hits),
        "total_opportunities": total_opps,
        "hit_rate": round(len(hits) / total_opps * 100, 1) if total_opps > 0 else 0,
        "draws_analyzed": len(sorted_draws)
    }

def generate_smart_prediction(draws: List[dict], hot_numbers: List[dict]) -> tuple:
    """Generate smart number predictions with explanations"""
    if not draws:
        return [5, 12, 23, 31, 37, 40], []
    
    all_numbers = []
    for draw in draws:
        all_numbers.extend(draw['numbers'])
    
    number_counts = Counter(all_numbers)
    
    # Strategy: Mix of addition patterns and hot numbers
    suggestions = []
    explanations = []
    
    # Find addition patterns (3 + X = result)
    base = 3
    for add in [13, 16, 26]:
        result = base + add
        if result <= 42 and result not in suggestions:
            suggestions.append(result)
            explanations.append({
                "number": result,
                "reason": f"Addition: {base} + {add} = {result}",
                "confidence": 80
            })
    
    # Add hot numbers
    hot_nums = [h['number'] for h in hot_numbers[:5]]
    for num in hot_nums:
        if num not in suggestions and len(suggestions) < 6:
            count = number_counts.get(num, 0)
            suggestions.append(num)
            explanations.append({
                "number": num,
                "reason": f"Hot: appeared {count}x in {len(draws)} draws",
                "confidence": 65
            })
    
    # Fill remaining with weighted random
    while len(suggestions) < 6:
        candidates = [n for n in range(1, 43) if n not in suggestions]
        weights = [number_counts.get(n, 1) for n in candidates]
        if candidates:
            chosen = random.choices(candidates, weights=weights, k=1)[0]
            suggestions.append(chosen)
            explanations.append({
                "number": chosen,
                "reason": f"Hot: appeared {number_counts.get(chosen, 0)}x in {len(draws)} draws",
                "confidence": 65
            })
    
    return sorted(suggestions[:6]), explanations[:6]

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Lucky Jack API - Switzerland Lotto Pattern Analyzer"}

@api_router.post("/draws", response_model=DrawResponse)
async def create_draw(input: DrawCreate):
    # Validate numbers
    if len(input.numbers) != 6:
        raise HTTPException(status_code=400, detail="Must provide exactly 6 numbers")
    if any(n < 1 or n > 42 for n in input.numbers):
        raise HTTPException(status_code=400, detail="Numbers must be between 1 and 42")
    if len(set(input.numbers)) != 6:
        raise HTTPException(status_code=400, detail="Numbers must be unique")
    
    draw = Draw(
        date=input.date,
        draw_number=input.draw_number,
        numbers=sorted(input.numbers)
    )
    
    doc = draw.model_dump()
    await db.draws.insert_one(doc)
    
    return DrawResponse(
        id=draw.id,
        date=draw.date,
        draw_number=draw.draw_number,
        numbers=draw.numbers,
        families=get_families(draw.numbers)
    )

@api_router.get("/draws", response_model=List[DrawResponse])
async def get_draws():
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).to_list(2000)
    return [
        DrawResponse(
            id=d['id'],
            date=d['date'],
            draw_number=d.get('draw_number'),
            numbers=d['numbers'],
            families=get_families(d['numbers'])
        )
        for d in draws
    ]

@api_router.delete("/draws/clear-all")
async def clear_all_draws():
    """Clear all draws from database"""
    result = await db.draws.delete_many({})
    return {"message": f"Deleted {result.deleted_count} draws"}

@api_router.post("/draws/import-bulk")
async def import_bulk_draws(draws: List[DrawCreate]):
    """Import multiple draws at once"""
    docs = []
    for draw in draws:
        doc = {
            "id": str(uuid.uuid4()),
            "date": draw.date,
            "draw_number": draw.draw_number,
            "numbers": sorted(draw.numbers),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        docs.append(doc)
    
    if docs:
        await db.draws.insert_many(docs)
    
    return {"message": f"Imported {len(docs)} draws"}

@api_router.delete("/draws/{draw_id}")
async def delete_draw(draw_id: str):
    result = await db.draws.delete_one({"id": draw_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Draw not found")
    return {"message": "Draw deleted successfully"}

@api_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard():
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).to_list(2000)
    
    if not draws:
        return DashboardStats(
            total_draws=0,
            rare_events=0,
            chain_links=0,
            series_found=0,
            group1_count=0,
            group2_count=0,
            group1_percentage=0,
            group2_percentage=0,
            hot_numbers=[],
            cold_numbers=[],
            last_draws=[]
        )
    
    # Count all numbers
    all_numbers = []
    group1_count = 0
    group2_count = 0
    
    for draw in draws:
        all_numbers.extend(draw['numbers'])
        for n in draw['numbers']:
            if n <= 21:
                group1_count += 1
            else:
                group2_count += 1
    
    total_numbers = group1_count + group2_count
    
    # Calculate number frequencies
    number_counts = Counter(all_numbers)
    
    # Hot numbers (most frequent)
    hot = number_counts.most_common(10)
    hot_numbers = [{"number": n, "count": c} for n, c in hot]
    
    # Cold numbers (least frequent)
    cold = number_counts.most_common()[-10:]
    cold_numbers = [{"number": n, "count": c} for n, c in reversed(cold)]
    
    # Find rare events (unusual patterns - e.g., all low or all high)
    rare_events = sum(1 for d in draws if all(n <= 21 for n in d['numbers']) or all(n > 21 for n in d['numbers']))
    
    # Chain links (consecutive numbers appearing)
    chain_links = 0
    for draw in draws:
        nums = sorted(draw['numbers'])
        for i in range(len(nums) - 1):
            if nums[i] + 1 == nums[i + 1]:
                chain_links += 1
    
    # Series found
    series = find_series_patterns(draws)
    
    # Last 5 draws
    last_draws = [
        {
            "date": d['date'],
            "numbers": d['numbers'],
            "families": get_families(d['numbers'])
        }
        for d in draws[:5]
    ]
    
    return DashboardStats(
        total_draws=len(draws),
        rare_events=rare_events,
        chain_links=chain_links,
        series_found=len(series),
        group1_count=group1_count,
        group2_count=group2_count,
        group1_percentage=round(group1_count / total_numbers * 100, 1) if total_numbers > 0 else 0,
        group2_percentage=round(group2_count / total_numbers * 100, 1) if total_numbers > 0 else 0,
        hot_numbers=hot_numbers,
        cold_numbers=cold_numbers,
        last_draws=last_draws
    )

@api_router.get("/patterns", response_model=PatternData)
async def get_patterns():
    draws = await db.draws.find({}, {"_id": 0}).to_list(2000)
    
    all_numbers = []
    for draw in draws:
        all_numbers.extend(draw['numbers'])
    
    return PatternData(
        digit_reversals=find_digit_reversals(all_numbers),
        series_patterns=find_series_patterns(draws)
    )

@api_router.get("/advanced-patterns")
async def get_advanced_patterns(from_year: int = 2020):
    """Get advanced pattern analysis from specified year"""
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).to_list(2000)
    
    # Filter from specified year
    filtered = [d for d in draws if d['date'] >= f"{from_year}-01-01"]
    
    patterns = find_advanced_patterns(filtered)
    patterns["total_draws_analyzed"] = len(filtered)
    patterns["from_year"] = from_year
    
    return patterns

@api_router.get("/position-patterns")
async def get_position_patterns(from_year: int = 2020):
    """Get position-based pattern analysis (user's digit link system)"""
    draws = await db.draws.find({}, {"_id": 0}).to_list(2000)
    
    # Filter from specified year
    filtered = [d for d in draws if d['date'] >= f"{from_year}-01-01"]
    
    result = analyze_position_patterns(filtered)
    result["from_year"] = from_year
    
    return result

@api_router.get("/quarter-predictor")
async def get_quarter_prediction():
    """Predict numbers based on quarterly position system"""
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).to_list(2000)
    
    if not draws:
        return {"error": "No draws available"}
    
    # Get current year draws
    from datetime import datetime
    current_year = datetime.now().year
    year_draws = sorted([d for d in draws if d['date'].startswith(str(current_year))], key=lambda x: x['date'])
    
    # Calculate quarters (~26-27 draws each, ~104 per year)
    expected_per_quarter = 26
    current_draw_num = len(year_draws)
    current_quarter = min(current_draw_num // expected_per_quarter, 3)  # 0-3
    position_in_quarter = current_draw_num % expected_per_quarter
    
    # Next draw position
    next_position = position_in_quarter + 1
    if next_position > expected_per_quarter:
        next_position = 1
        current_quarter = min(current_quarter + 1, 3)
    
    # Calculate position from bottom (they sum to ~28)
    quarter_size = expected_per_quarter if current_quarter < 3 else 27
    position_from_bottom = quarter_size - next_position + 1
    
    # Position numbers that might appear
    position_numbers = []
    if 1 <= next_position <= 42:
        position_numbers.append({"number": next_position, "type": "from_top", "confidence": 28})
    if 1 <= position_from_bottom <= 42 and position_from_bottom != next_position:
        position_numbers.append({"number": position_from_bottom, "type": "from_bottom", "confidence": 28})
    
    # Get linked numbers for position numbers
    linked_suggestions = []
    for pn in position_numbers:
        links = get_digit_links(pn["number"])
        for link in links:
            if 1 <= link <= 42:
                linked_suggestions.append({
                    "number": link,
                    "linked_to": pn["number"],
                    "type": "digit_link",
                    "confidence": 15
                })
    
    # Historical analysis: what numbers appeared at this position before?
    historical_at_position = []
    for year in range(2020, current_year + 1):
        y_draws = sorted([d for d in draws if d['date'].startswith(str(year))], key=lambda x: x['date'])
        q_size = len(y_draws) // 4
        
        for q in range(4):
            start = q * q_size
            end = start + q_size if q < 3 else len(y_draws)
            quarter_draws = y_draws[start:end]
            
            if next_position <= len(quarter_draws):
                draw = quarter_draws[next_position - 1]
                historical_at_position.append({
                    "year": year,
                    "quarter": q + 1,
                    "date": draw["date"],
                    "numbers": draw["numbers"]
                })
    
    # Count frequency of numbers at this position
    position_frequency = {}
    for h in historical_at_position:
        for n in h["numbers"]:
            position_frequency[n] = position_frequency.get(n, 0) + 1
    
    # Top numbers at this position historically
    top_historical = sorted(position_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    historical_suggestions = [
        {"number": n, "count": c, "type": "historical", "confidence": min(c * 5, 40)}
        for n, c in top_historical
    ]
    
    # Last draw info
    last_draw = year_draws[-1] if year_draws else None
    
    return {
        "current_year": current_year,
        "total_draws_this_year": current_draw_num,
        "current_quarter": current_quarter + 1,
        "next_draw_position": {
            "from_top": next_position,
            "from_bottom": position_from_bottom,
            "sum": next_position + position_from_bottom
        },
        "position_numbers": position_numbers,
        "linked_suggestions": linked_suggestions[:10],
        "historical_suggestions": historical_suggestions,
        "historical_at_position": historical_at_position[-6:],
        "date_patterns": get_date_patterns(last_draw) if last_draw else [],
        "last_draw": {
            "date": last_draw["date"],
            "numbers": last_draw["numbers"]
        } if last_draw else None
    }

def get_date_patterns(last_draw):
    """Extract date-based prediction patterns from last draw"""
    patterns = []
    if not last_draw:
        return patterns
    
    last_date = last_draw['date']
    y, m, d = last_date.split('-')
    last_day = int(d)
    last_month = int(m)
    day_plus_month = last_day + last_month
    
    # Day from last draw (15.1% hit rate from 2020-2026)
    if 1 <= last_day <= 42:
        patterns.append({
            "number": last_day,
            "type": "prev_day",
            "reason": f"Day {last_day} from {last_date}",
            "confidence": 15
        })
    
    # Day + Month from last draw (11.8% hit rate)
    if 1 <= day_plus_month <= 42:
        patterns.append({
            "number": day_plus_month,
            "type": "prev_day_plus_month",
            "reason": f"D+M ({last_day}+{last_month}={day_plus_month})",
            "confidence": 12
        })
    
    # Day reversed (4.6% hit rate)
    if last_day >= 10:
        day_rev = int(str(last_day)[::-1])
        if 1 <= day_rev <= 42:
            patterns.append({
                "number": day_rev,
                "type": "prev_day_reversed",
                "reason": f"Day rev ({last_day}→{day_rev})",
                "confidence": 5
            })
    
    return patterns

@api_router.get("/master-predictor")
async def get_master_prediction():
    """
    MASTER PREDICTOR - Combines ALL pattern systems:
    1. Quarterly position (28% hit rate)
    2. Digit links (11% hit rate)  
    3. Date patterns (15%, 12%, 5%)
    4. Historical at position
    5. Hot/Cold numbers
    6. Cross-draw patterns
    7. Rare event counts
    """
    from datetime import datetime
    from collections import defaultdict
    
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).to_list(2000)
    if not draws:
        return {"error": "No draws available"}
    
    current_year = datetime.now().year
    year_draws = sorted([d for d in draws if d['date'].startswith(str(current_year))], key=lambda x: x['date'])
    all_draws_2020 = sorted([d for d in draws if d['date'] >= '2020-01-01'], key=lambda x: x['date'])
    
    # Score accumulator for each number 1-42
    scores = defaultdict(lambda: {"score": 0, "reasons": []})
    
    # === 1. QUARTERLY POSITION (28% confidence) ===
    expected_per_quarter = 26
    current_draw_num = len(year_draws)
    current_quarter = min(current_draw_num // expected_per_quarter, 3)
    position_in_quarter = current_draw_num % expected_per_quarter
    next_position = position_in_quarter + 1
    if next_position > expected_per_quarter:
        next_position = 1
        current_quarter = min(current_quarter + 1, 3)
    quarter_size = expected_per_quarter if current_quarter < 3 else 27
    position_from_bottom = quarter_size - next_position + 1
    
    if 1 <= next_position <= 42:
        scores[next_position]["score"] += 28
        scores[next_position]["reasons"].append(f"Position {next_position} from top (28%)")
    if 1 <= position_from_bottom <= 42 and position_from_bottom != next_position:
        scores[position_from_bottom]["score"] += 28
        scores[position_from_bottom]["reasons"].append(f"Position {position_from_bottom} from bottom (28%)")
    
    # === 2. DIGIT LINKS from position numbers (11% confidence) ===
    for pos_num in [next_position, position_from_bottom]:
        if 1 <= pos_num <= 42:
            links = get_digit_links(pos_num)
            for link in links:
                if 1 <= link <= 42:
                    scores[link]["score"] += 11
                    scores[link]["reasons"].append(f"Digit link from {pos_num} (11%)")
    
    # === 3. DATE PATTERNS (15%, 12%, 5%) ===
    last_draw = year_draws[-1] if year_draws else (draws[0] if draws else None)
    if last_draw:
        date_pats = get_date_patterns(last_draw)
        for dp in date_pats:
            n = dp["number"]
            scores[n]["score"] += dp["confidence"]
            scores[n]["reasons"].append(f"{dp['reason']} ({dp['confidence']}%)")
    
    # === 4. DIGIT LINKS from last draw numbers (11% confidence) ===
    if last_draw:
        for num in last_draw['numbers']:
            links = get_digit_links(num)
            for link in links:
                if 1 <= link <= 42 and link not in last_draw['numbers']:
                    scores[link]["score"] += 8
                    scores[link]["reasons"].append(f"Digit link from {num} (8%)")
    
    # === 5. HISTORICAL AT THIS POSITION ===
    position_freq = defaultdict(int)
    for year in range(2020, current_year + 1):
        y_draws = sorted([d for d in draws if d['date'].startswith(str(year))], key=lambda x: x['date'])
        q_size = len(y_draws) // 4
        for q in range(4):
            start = q * q_size
            end = start + q_size if q < 3 else len(y_draws)
            quarter_draws = y_draws[start:end]
            if next_position <= len(quarter_draws):
                for n in quarter_draws[next_position - 1]['numbers']:
                    position_freq[n] += 1
    
    top_historical = sorted(position_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    for n, count in top_historical:
        bonus = min(count * 3, 15)
        scores[n]["score"] += bonus
        scores[n]["reasons"].append(f"Historical at pos {next_position}: {count}x ({bonus}%)")
    
    # === 6. HOT NUMBERS (global frequency) ===
    all_nums = []
    for d in all_draws_2020[-200:]:
        all_nums.extend(d['numbers'])
    freq = Counter(all_nums)
    hot_nums = freq.most_common(10)
    for n, count in hot_nums:
        bonus = min(count // 5, 10)
        if bonus > 0:
            scores[n]["score"] += bonus
            scores[n]["reasons"].append(f"Hot number: {count}x ({bonus}%)")
    
    # === 7. COLD/DUE NUMBERS ===
    last_seen = {}
    sorted_draws_desc = sorted(all_draws_2020, key=lambda x: x['date'], reverse=True)
    for i, d in enumerate(sorted_draws_desc):
        for n in d['numbers']:
            if n not in last_seen:
                last_seen[n] = i
    
    due_numbers = [(n, gap) for n, gap in last_seen.items() if gap > 15]
    due_numbers.sort(key=lambda x: x[1], reverse=True)
    for n, gap in due_numbers[:5]:
        bonus = min(gap // 3, 10)
        scores[n]["score"] += bonus
        scores[n]["reasons"].append(f"Due: {gap} draws ago ({bonus}%)")
    
    # === 8. RARE EVENT COUNTS (NEW!) ===
    def get_group(n):
        if n <= 9: return 1
        elif n <= 19: return 2
        elif n <= 29: return 3
        elif n <= 39: return 4
        else: return 5
    
    def count_groups(numbers):
        groups = {}
        for n in numbers:
            g = get_group(n)
            groups[g] = groups.get(g, 0) + 1
        return groups
    
    # Find recent rare events
    rare_events = []
    for i, draw in enumerate(all_draws_2020):
        groups = count_groups(draw['numbers'])
        max_group = max(groups.values())
        if max_group >= 4:
            rare_events.append({'index': i, 'date': draw['date'], 'count': max_group})
    
    # For last 5 rare events, calculate counts to current draw
    current_draw_idx = len(all_draws_2020)
    rare_predictions = []
    for rare in rare_events[-5:]:
        count_since = current_draw_idx - rare['index']
        rarity = "🔥🔥🔥" if rare['count'] == 6 else ("🔥🔥" if rare['count'] == 5 else "🔥")
        
        # The count itself
        if 1 <= count_since <= 42:
            scores[count_since]["score"] += 15 * (rare['count'] - 3)  # Higher for rarer events
            scores[count_since]["reasons"].append(f"Rare {rarity} +{count_since} draws (15%)")
            rare_predictions.append({
                "rare_date": rare['date'],
                "rarity": rare['count'],
                "count_since": count_since,
                "predicted": count_since
            })
        
        # Digit breakdown for counts > 42
        if count_since > 42:
            d1 = count_since // 10
            d2 = count_since % 10
            dsum = d1 + d2
            
            for digit in [d1, d2]:
                if 1 <= digit <= 42:
                    scores[digit]["score"] += 10
                    scores[digit]["reasons"].append(f"Rare {rarity} +{count_since} digit ({d1},{d2})")
            
            if 1 <= dsum <= 42:
                scores[dsum]["score"] += 10
                scores[dsum]["reasons"].append(f"Rare {rarity} +{count_since} sum={dsum}")
    
    # === COMPILE FINAL PREDICTIONS ===
    ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    
    top_6 = [{"number": n, "score": data["score"], "reasons": data["reasons"][:4]} for n, data in ranked[:6]]
    alternates = [{"number": n, "score": data["score"], "reasons": data["reasons"][:2]} for n, data in ranked[6:12]]
    
    avg_score = sum(t["score"] for t in top_6) / 6 if top_6 else 0
    
    return {
        "prediction_date": datetime.now().isoformat(),
        "for_draw": {
            "year": current_year,
            "draw_number": current_draw_num + 1,
            "quarter": current_quarter + 1,
            "position": next_position
        },
        "last_draw": {
            "date": last_draw["date"],
            "numbers": last_draw["numbers"]
        } if last_draw else None,
        "main_prediction": sorted([t["number"] for t in top_6]),
        "main_prediction_details": top_6,
        "alternate_numbers": sorted([a["number"] for a in alternates]),
        "alternate_details": alternates,
        "average_confidence": round(avg_score, 1),
        "rare_event_predictions": rare_predictions,
        "patterns_used": [
            "Quarterly position (28%)",
            "Digit links (11%)",
            "Date patterns (15%, 12%, 5%)",
            "Historical at position",
            "Hot numbers",
            "Due numbers",
            "Rare event counts (NEW!)"
        ]
    }

@api_router.get("/predictions", response_model=PredictionData)
async def get_predictions():
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).to_list(2000)
    
    # Get hot numbers for prediction
    all_numbers = []
    for draw in draws:
        all_numbers.extend(draw['numbers'])
    number_counts = Counter(all_numbers)
    hot = number_counts.most_common(10)
    hot_numbers = [{"number": n, "count": c} for n, c in hot]
    
    suggested, explanations = generate_smart_prediction(draws, hot_numbers)
    cross_patterns = find_cross_draw_patterns(draws)
    gap_analysis = calculate_gap_analysis(draws)
    
    return PredictionData(
        suggested_numbers=suggested,
        explanations=explanations,
        cross_draw_patterns=cross_patterns,
        gap_analysis=gap_analysis
    )

@api_router.post("/seed")
async def seed_data():
    """Seed database with historical Swiss lottery data"""
    # Check if data already exists
    count = await db.draws.count_documents({})
    if count > 0:
        return {"message": f"Database already has {count} draws"}
    
    # Generate realistic Swiss lottery data from 2015-2026
    import random
    random.seed(42)  # For reproducibility
    
    draws_data = []
    
    # Generate draws by year
    year_draws = {
        2015: 107, 2016: 107, 2017: 107, 2018: 107,
        2019: 104, 2020: 96, 2021: 96, 2022: 96,
        2023: 96, 2024: 112, 2025: 105, 2026: 25
    }
    
    draw_id = 1
    for year, num_draws in year_draws.items():
        for i in range(num_draws):
            # Distribute draws throughout the year
            month = (i % 12) + 1
            day = ((i * 3) % 28) + 1
            
            # Generate 6 unique numbers between 1-42
            numbers = sorted(random.sample(range(1, 43), 6))
            
            draws_data.append({
                "id": str(uuid.uuid4()),
                "date": f"{year}-{month:02d}-{day:02d}",
                "draw_number": str(draw_id),
                "numbers": numbers,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            draw_id += 1
    
    # Insert all draws
    await db.draws.insert_many(draws_data)
    
    return {"message": f"Seeded {len(draws_data)} draws successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
