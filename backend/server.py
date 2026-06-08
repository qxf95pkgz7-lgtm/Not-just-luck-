from fastapi import FastAPI, APIRouter, HTTPException, Body
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from collections import Counter
import random
from safe_cursor import safe_find, safe_find_sorted

# Import Pattern 60: Story Signs
from pattern_60_story_signs import analyze_story_signs, get_circle as get_circle_60


# Import Story Pattern Generator
from story_pattern_generator import (
    generate_predictions,
    analyze_draw,
    get_date_numbers,
    find_hungry_numbers,
    get_circle as get_circle_story,
    calculate_rc
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (with fast-fail timeouts so a slow DB doesn't hang every request)
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=20,
    serverSelectionTimeoutMS=5000,    # fail Mongo handshake fast (5s vs default 30s)
    connectTimeoutMS=5000,
    socketTimeoutMS=30000,            # 30s per round-trip; with batch_size=200 each batch is sub-second
)
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
    lucky_number: Optional[int] = None
    replay_number: Optional[int] = None

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
    digit_flips: List[dict]
    series_patterns: List[dict]

class PredictionData(BaseModel):
    suggested_numbers: List[int]
    explanations: List[dict]
    cross_draw_patterns: List[dict]
    gap_analysis: List[dict]

class AdvancedPatternData(BaseModel):
    digit_flips_in_draws: List[dict]  # 34 → 13 type patterns
    digit_sum_patterns: List[dict]  # 4+5=9, 9/3=3 type
    cross_draw_connections: List[dict]  # Numbers combining across draws
    series_completions: List[dict]  # 10-11-12 + 34(13) = full series

class PredictionHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    lottery_type: str  # 'swiss' or 'euromillions'
    target_draw_date: Optional[str] = None  # The draw date this prediction is for
    numbers: List[int]
    lucky_number: Optional[int] = None  # Swiss Lotto only
    stars: Optional[List[int]] = None  # EuroMillions only
    confidence: float = 0
    top_reasons: List[str] = []
    actual_numbers: Optional[List[int]] = None  # Filled in after draw
    actual_lucky: Optional[int] = None
    actual_stars: Optional[List[int]] = None
    matches: Optional[int] = None  # How many numbers matched
    lucky_match: Optional[bool] = None
    stars_matched: Optional[int] = None

# Helper functions
def get_families(numbers: List[int]) -> List[int]:
    """Return which group each number belongs to: 1 (1-21) or 2 (22-42)"""
    return [1 if n <= 21 else 2 for n in numbers]

def find_digit_flips(all_numbers: List[int]) -> List[dict]:
    """Find pairs like 12<->21, 13<->31, etc."""
    flips = []
    number_counts = Counter(all_numbers)
    
    seen_pairs = set()
    for num in range(1, 43):
        if num < 10:
            flipped_num = num * 10
        else:
            tens = num // 10
            ones = num % 10
            if ones == 0:
                continue
            flipped_num = ones * 10 + tens
        
        if flipped_num > 42 or flipped_num == num:
            continue
            
        pair_key = tuple(sorted([num, flipped_num]))
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)
        
        if number_counts.get(num, 0) > 0 and number_counts.get(flipped_num, 0) > 0:
            flips.append({
                "num1": num,
                "num2": flipped_num,
                "count1": number_counts[num],
                "count2": number_counts[flipped_num]
            })
    
    return flips[:12]  # Top 12 pairs

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

def flip_digits(n: int) -> int:
    """Flip digits of a number: 34 → 43, 13 → 31"""
    s = str(n)
    if len(s) == 1:
        return n * 10  # 3 → 30
    return int(s[::-1])

def digit_sum(n: int) -> int:
    """Sum of digits: 34 → 7, 45 → 9"""
    return sum(int(d) for d in str(n))

def find_advanced_patterns(draws: List[dict]) -> dict:
    """Find advanced patterns like digit flips, sums, and cross-draw connections"""
    
    digit_flips_in_draws = []
    digit_sum_patterns = []
    cross_draw_connections = []
    series_completions = []
    
    for i, draw in enumerate(draws):
        nums = draw['numbers']
        date = draw['date']
        
        # 1. Digit Flips within draw (34 in draw means 13 is implied)
        for n in nums:
            if n >= 10:
                flipped_n = flip_digits(n)
                if flipped_n != n and 1 <= flipped_n <= 42:
                    digit_flips_in_draws.append({
                        "date": date,
                        "number": n,
                        "flipped": flipped_n,
                        "in_draw": flipped_n in nums
                    })
        
        # 2. Find series that could be completed with flips
        sorted_nums = sorted(nums)
        # Check for near-series (e.g., 10,11,12 and 34→13 completes it)
        for j in range(len(sorted_nums) - 2):
            if sorted_nums[j+1] == sorted_nums[j] + 1 and sorted_nums[j+2] == sorted_nums[j] + 2:
                # Found 3 consecutive, check if 4th exists via flip
                next_in_series = sorted_nums[j] + 3
                prev_in_series = sorted_nums[j] - 1
                
                for n in nums:
                    if n >= 10:
                        rev = flip_digits(n)
                        if rev == next_in_series or rev == prev_in_series:
                            series_completions.append({
                                "date": date,
                                "series": [sorted_nums[j], sorted_nums[j+1], sorted_nums[j+2]],
                                "completed_by": n,
                                "as_flipped": rev,
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
                    
                    # Combined number flips: 4,5 → 45 → 54 → relates to 12 (5-4 or 5,4)
                    if n1 < 10 and n2 < 10:
                        combo = n1 * 10 + n2
                        combo_rev = flip_digits(combo)
                        ds = digit_sum(combo)
                        
                        # Check if digit sum or its factors appear
                        if ds <= 42 and (ds in nums or ds in prev_nums):
                            cross_draw_connections.append({
                                "date": date,
                                "prev_date": prev_draw['date'],
                                "numbers": [n1, n2],
                                "combined": combo,
                                "flipped": combo_rev,
                                "digit_sum": ds,
                                "found_in": "current" if ds in nums else "previous"
                            })
    
    return {
        "digit_flips_in_draws": digit_flips_in_draws[:50],
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
    
    # Direct flip in range (12<->21, 13<->31, etc.)
    if 10 <= rev <= 42 and rev != n:
        linked.add(rev)
    
    # Digit product (36 -> 3*6=18)
    prod = d1 * d2
    if 1 <= prod <= 42:
        linked.add(prod)
    
    # If flip out of range (27->72, 18->81, etc.)
    if rev > 42:
        for x in range(10, 43):
            # Pattern: x + rev = total, total flipped = x
            # Example: 19 + 72 = 91, flip(91) = 19 ✓
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

@api_router.get("/version")
async def version():
    """🪞 Truth-teller route — confirms what code build is running."""
    return {
        "build": "session46.2-mp-cache",
        "shipped": "2026-06-08",
        "fixes": [
            "🚀 NEW: 60s in-memory cache on /api/master-predictor (Swiss + Euro) for default-param calls (Emergent Support Jun 8 #3)",
            "🚀 NEW: Procfile dropped to --workers 1 to free memory on tier_1 (Emergent Support recommendation)",
            "🧹 Euro dedup migration (27 rows) + unique index on euromillions_draws.date (Emergent Support Jun 8 #2)",
            "🧹 All 9 insert_one/insert_many for euromillions_draws converted to upsert (idempotent)",
            "🛡️ safe_cursor.safe_find() wrapper with CursorNotFound + ExecutionTimeout retry (Emergent Support Jun 8 #1)",
            "🛡️ NEW: All .to_list(5000+) calls in server.py routed through safe_find (prediction-history, hit-tracker, story endpoints)",
            "🛡️ NEW: .batch_size(200) added to all .to_list(2000+) / .to_list(3000) Motor cursors (server.py, hit_tracker.py, euro_simulation.py)",
            "🛡️ NEW: socketTimeoutMS bumped 10s→30s (each batch round-trip has breathing room)",
            "🚀 uvicorn --workers 2 via Procfile (Emergent Support Jun 6)",
            "🛡️ CursorNotFound retry + batch_size=100 on year_d_ledger.load_draws (Emergent Support Jun 6)",
            "MongoDB index on active_users.visitor_id",
            "10s TTL cache on _real_user_counts",
            "24h prune of stale active_users at startup",
            "All startup events fire as asyncio.create_task (non-blocking)",
            "Frontend animation halved (Swiss 15s→6s, Euro 13s→5s)",
            "VIP unlock auto-recovers visitor_id (iOS Safari safe)",
        ],
        "canon_endpoints": [
            "/api/dj-pool/{target_date}/{mode}",
            "/api/healthz",
            "/api/readyz",
        ],
    }

@api_router.get("/healthz")
async def healthz():
    """🩺 Liveness probe — DB-FREE, used by orchestrator + uptime checks.
    Returns immediately so Kubernetes can tell the container is alive
    even if MongoDB is slow/unreachable."""
    return {"status": "ok", "service": "lucky-jack-api"}

@api_router.get("/readyz")
async def readyz():
    """🩺 Readiness probe — checks DB ping with short timeout."""
    try:
        await asyncio.wait_for(client.admin.command("ping"), timeout=3.0)
        return {"status": "ready", "db": "ok"}
    except asyncio.TimeoutError:
        return {"status": "degraded", "db": "timeout"}
    except Exception as e:
        return {"status": "degraded", "db": "error", "error": str(e)[:200]}

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
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).batch_size(200).to_list(2000)
    return [
        DrawResponse(
            id=d.get('id', ''),
            date=d['date'],
            draw_number=d.get('draw_number'),
            numbers=d['numbers'],
            families=get_families(d['numbers']),
            lucky_number=d.get('lucky_number'),
            replay_number=d.get('replay_number')
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
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).batch_size(200).to_list(2000)
    
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
    draws = await db.draws.find({}, {"_id": 0}).batch_size(200).to_list(2000)
    
    all_numbers = []
    for draw in draws:
        all_numbers.extend(draw['numbers'])
    
    return PatternData(
        digit_flips=find_digit_flips(all_numbers),
        series_patterns=find_series_patterns(draws)
    )

@api_router.get("/advanced-patterns")
async def get_advanced_patterns(from_year: int = 2020):
    """Get advanced pattern analysis from specified year"""
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).batch_size(200).to_list(2000)
    
    # Filter from specified year
    filtered = [d for d in draws if d['date'] >= f"{from_year}-01-01"]
    
    patterns = find_advanced_patterns(filtered)
    patterns["total_draws_analyzed"] = len(filtered)
    patterns["from_year"] = from_year
    
    return patterns

@api_router.get("/position-patterns")
async def get_position_patterns(from_year: int = 2020):
    """Get position-based pattern analysis (user's digit link system)"""
    draws = await db.draws.find({}, {"_id": 0}).batch_size(200).to_list(2000)
    
    # Filter from specified year
    filtered = [d for d in draws if d['date'] >= f"{from_year}-01-01"]
    
    result = analyze_position_patterns(filtered)
    result["from_year"] = from_year
    
    return result

@api_router.get("/quarter-predictor")
async def get_quarter_prediction():
    """Predict numbers based on quarterly position system"""
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).batch_size(200).to_list(2000)
    
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
    # Handle both DD.MM.YYYY and YYYY-MM-DD formats
    if '.' in last_date:
        d, m, y = last_date.split('.')
    else:
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
    
    # Day flipped (4.6% hit rate)
    if last_day >= 10:
        day_rev = int(str(last_day)[::-1])
        if 1 <= day_rev <= 42:
            patterns.append({
                "number": day_rev,
                "type": "prev_day_flipped",
                "reason": f"Day rev ({last_day}→{day_rev})",
                "confidence": 5
            })
    
    return patterns

@api_router.get("/master-predictor")
async def get_master_prediction(
    birthday: str = None, 
    name: str = None,
    lock_p1: int = None,
    lock_p2: int = None,
    lock_p3: int = None,
    lock_p4: int = None,
    lock_p5: int = None,
    lock_p6: int = None,
    num_tickets: int = 1,
    visitor_id: str = ""
):
    """
    MASTER PREDICTOR - Combines ALL pattern systems:
    1. Quarterly position (28% hit rate)
    2. Digit links (11% hit rate)  
    3. Date patterns (15%, 12%, 5%)
    4. Historical at position
    5. Hot/Cold numbers
    6. Cross-draw patterns
    7. Rare event counts
    8. Birthday mode (optional) - pass as DD/MM/YYYY or DD-MM-YYYY
    9. Name mode (optional) - A=1, B=2, ... Z=26
    10. Locked positions (optional) - lock_p1 through lock_p6, max 4 locks
    11. Multiple tickets (optional) - num_tickets=1-20 for multiple predictions
    """
    from datetime import datetime
    from collections import defaultdict
    
    # 🕒 Draw-time generator cutoff (Swiss)
    if visitor_id:
        await _assert_generator_open("swiss", visitor_id)
    
    # 🚀 Default-param cache — covers the initial page-load ball-spin call
    # which is the same for every visitor. 60s TTL is safe because draws only
    # update on Wed/Sat at 21:00 UTC.
    _no_params = (
        birthday is None and name is None and num_tickets == 1
        and all(v is None for v in [lock_p1, lock_p2, lock_p3, lock_p4, lock_p5, lock_p6])
    )
    if _no_params:
        import time
        global _MASTER_PRED_CACHE
        try:
            _MASTER_PRED_CACHE
        except NameError:
            _MASTER_PRED_CACHE = {"ts": 0, "data": None}
        if _MASTER_PRED_CACHE.get("data") and (time.time() - _MASTER_PRED_CACHE["ts"] < 60):
            return _MASTER_PRED_CACHE["data"]
    
    # Ticket limit check (VIP-aware)
    if visitor_id:
        if not await _is_visitor_unlimited(visitor_id):
            used = await _count_visitor_tickets(visitor_id)
            if used >= TICKET_LIMIT:
                raise HTTPException(status_code=429, detail=f"Ticket limit reached! You've generated {used}/{TICKET_LIMIT} tickets for the next draw.")
            num_tickets = min(num_tickets, TICKET_LIMIT - used)
    
    # Validate num_tickets
    num_tickets = max(1, min(20, num_tickets))
    
    # Parse locked positions
    locked_positions = {}  # {position_index: number}
    lock_params = [lock_p1, lock_p2, lock_p3, lock_p4, lock_p5, lock_p6]
    for i, lock_val in enumerate(lock_params):
        if lock_val is not None and 1 <= lock_val <= 42:
            locked_positions[i] = lock_val
    
    # Validate: max 4 locks, no duplicate numbers
    if len(locked_positions) > 4:
        return {"error": "Maximum 4 locked positions allowed"}
    locked_numbers = list(locked_positions.values())
    if len(locked_numbers) != len(set(locked_numbers)):
        return {"error": "Duplicate locked numbers not allowed"}

    # 🔒 Validate lock-position slot ordering (Swiss range 1-42, 6 slots)
    from lock_constraints import is_valid_lock_request, slot_bounds, assemble_with_locks
    _ok, _msg = is_valid_lock_request(
        locked_positions, n_slots=6, value_min=1, value_max=42,
    )
    if not _ok:
        return {"error": f"Invalid lock: {_msg}"}
    _lock_bounds = slot_bounds(locked_positions, n_slots=6,
                               value_min=1, value_max=42) if locked_positions else {}
    
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).batch_size(200).to_list(2000)
    if not draws:
        return {"error": "No draws available"}
    
    current_year = datetime.now().year
    year_draws = sorted([d for d in draws if d['date'].startswith(str(current_year))], key=lambda x: x['date'])
    all_draws_2020 = sorted([d for d in draws if d['date'] >= '2020-01-01'], key=lambda x: x['date'])
    
    # Score accumulator for each number 1-42
    scores = defaultdict(lambda: {"score": 0, "reasons": []})
    
    # === NAME MODE (if provided) ===
    name_numbers = []
    name_info = None
    if name:
        try:
            name_clean = name.upper().strip()
            letter_values = {chr(65 + i): i + 1 for i in range(26)}  # A=1, B=2, ... Z=26
            
            # Split into words
            words = name_clean.split()
            word_sums = []
            all_letters = []
            
            for word in words:
                word_sum = 0
                for char in word:
                    if char in letter_values:
                        val = letter_values[char]
                        all_letters.append({"letter": char, "value": val})
                        word_sum += val
                        # Individual letter values (if 1-42)
                        if 1 <= val <= 42:
                            name_numbers.append({"num": val, "reason": f"Letter {char}={val}"})
                if word_sum > 0:
                    word_sums.append({"word": word, "sum": word_sum})
                    # Word sum (if 1-42)
                    if 1 <= word_sum <= 42:
                        name_numbers.append({"num": word_sum, "reason": f"'{word}'={word_sum}"})
                    # Word sum digits
                    if word_sum > 42:
                        d1 = word_sum // 10
                        d2 = word_sum % 10
                        if 1 <= d1 <= 42:
                            name_numbers.append({"num": d1, "reason": f"'{word}' digit {d1}"})
                        if 1 <= d2 <= 42 and d2 != d1:
                            name_numbers.append({"num": d2, "reason": f"'{word}' digit {d2}"})
                        # Digit sum
                        dsum = sum(int(d) for d in str(word_sum))
                        if 1 <= dsum <= 42:
                            name_numbers.append({"num": dsum, "reason": f"'{word}' reduced={dsum}"})
            
            # Full name sum
            full_sum = sum(ws["sum"] for ws in word_sums)
            if full_sum > 0:
                # Full sum digits
                if 1 <= full_sum <= 42:
                    name_numbers.append({"num": full_sum, "reason": f"Full name={full_sum}"})
                else:
                    d1 = (full_sum // 10) % 10
                    d2 = full_sum % 10
                    if 1 <= d1 <= 42:
                        name_numbers.append({"num": d1, "reason": f"Name digit {d1}"})
                    if 1 <= d2 <= 42 and d2 != d1:
                        name_numbers.append({"num": d2, "reason": f"Name digit {d2}"})
                
                # Reduce to single digit (numerology style)
                reduced = full_sum
                while reduced > 9:
                    reduced = sum(int(d) for d in str(reduced))
                if 1 <= reduced <= 9:
                    name_numbers.append({"num": reduced, "reason": f"Name number={reduced}"})
            
            name_info = {
                "name": name,
                "words": word_sums,
                "full_sum": full_sum,
                "letters": all_letters[:10]  # First 10 letters
            }
            
            # Apply name bonuses
            seen = set()
            for nn in name_numbers:
                n = nn["num"]
                if n not in seen:
                    scores[n]["score"] += 20
                    scores[n]["reasons"].append(f"🔤 {nn['reason']} (20%)")
                    seen.add(n)
        except:
            pass
    
    # === BIRTHDAY MODE (if provided) ===
    birthday_numbers = []
    birthday_info = None
    if birthday:
        try:
            parts = birthday.replace('/', '-').split('-')
            if len(parts) == 3:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])
                
                birthday_info = {"day": day, "month": month, "year": year}
                
                if 1 <= day <= 42:
                    birthday_numbers.append({"num": day, "reason": f"Birth day {day}"})
                if 1 <= month <= 42:
                    birthday_numbers.append({"num": month, "reason": f"Birth month {month}"})
                
                year_str = str(year)
                if len(year_str) == 4:
                    first_two = int(year_str[:2])
                    last_two = int(year_str[2:])
                    if 1 <= first_two <= 42:
                        birthday_numbers.append({"num": first_two, "reason": f"Year {first_two}"})
                    if 1 <= last_two <= 42:
                        birthday_numbers.append({"num": last_two, "reason": f"Year {last_two}"})
                    
                    for d in year_str:
                        digit = int(d)
                        if 1 <= digit <= 9:
                            birthday_numbers.append({"num": digit, "reason": f"Year digit {digit}"})
                
                day_plus_month = day + month
                if 1 <= day_plus_month <= 42:
                    birthday_numbers.append({"num": day_plus_month, "reason": f"D+M={day_plus_month}"})
                
                year_digit_sum = sum(int(d) for d in year_str)
                if 1 <= year_digit_sum <= 42:
                    birthday_numbers.append({"num": year_digit_sum, "reason": f"Year sum={year_digit_sum}"})
                
                if day >= 10:
                    day_rev = int(str(day)[::-1])
                    if 1 <= day_rev <= 42:
                        birthday_numbers.append({"num": day_rev, "reason": f"Day rev {day}→{day_rev}"})
                
                total = day + month + sum(int(d) for d in year_str)
                while total > 9:
                    total = sum(int(d) for d in str(total))
                if 1 <= total <= 9:
                    birthday_numbers.append({"num": total, "reason": f"Life path {total}"})
                
                seen = set()
                for bn in birthday_numbers:
                    n = bn["num"]
                    if n not in seen:
                        scores[n]["score"] += 25
                        scores[n]["reasons"].append(f"🎂 {bn['reason']} (25%)")
                        seen.add(n)
        except:
            pass
    
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
    
    # === 4. DIGIT LINKS from last draw numbers (8% confidence) ===
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
    
    # === 8. VACUUM PATTERN (69.9% hit rate!) ===
    # When 3+ consecutive numbers leave, nearby/original return
    last_5 = all_draws_2020[-5:] if len(all_draws_2020) >= 5 else all_draws_2020
    if len(last_5) >= 3:
        for idx, draw in enumerate(last_5[:-1]):
            nums = sorted(draw['numbers'])
            # Find consecutive sequences
            seq = [nums[0]]
            for j in range(1, len(nums)):
                if nums[j] == nums[j-1] + 1:
                    seq.append(nums[j])
                else:
                    if len(seq) >= 3:
                        # Consecutive found - boost nearby numbers
                        nearby_low = seq[0] - 1
                        nearby_high = seq[-1] + 1
                        for n in [nearby_low, nearby_high] + seq:
                            if 1 <= n <= 42:
                                scores[n]["score"] += 12
                                scores[n]["reasons"].append(f"🌀 Vacuum: {seq} consecutive")
                    seq = [nums[j]]
            if len(seq) >= 3:
                nearby_low = seq[0] - 1
                nearby_high = seq[-1] + 1
                for n in [nearby_low, nearby_high] + seq:
                    if 1 <= n <= 42:
                        scores[n]["score"] += 12
                        scores[n]["reasons"].append(f"🌀 Vacuum: {seq} consecutive")
    
    # === 9. HIGH/LOW BALANCE (88.8% hit rate!) ===
    if last_draw:
        last_nums = last_draw['numbers']
        lows = sum(1 for n in last_nums if n <= 21)
        highs = 6 - lows
        if lows >= 5:  # Too many lows, boost highs
            for n in range(22, 43):
                scores[n]["score"] += 15
                scores[n]["reasons"].append(f"⚖️ Balance: last had {lows} lows")
        elif highs >= 5:  # Too many highs, boost lows
            for n in range(1, 22):
                scores[n]["score"] += 15
                scores[n]["reasons"].append(f"⚖️ Balance: last had {highs} highs")
    
    # === 10. ODD/EVEN BALANCE (81.6% hit rate!) ===
    if last_draw:
        last_nums = last_draw['numbers']
        odds = sum(1 for n in last_nums if n % 2 == 1)
        evens = 6 - odds
        if odds >= 5:  # Too many odds, boost evens
            for n in range(2, 43, 2):
                scores[n]["score"] += 12
                scores[n]["reasons"].append(f"⚖️ Balance: last had {odds} odds")
        elif evens >= 5:  # Too many evens, boost odds
            for n in range(1, 43, 2):
                scores[n]["score"] += 12
                scores[n]["reasons"].append(f"⚖️ Balance: last had {evens} evens")
    
    # === 11. GAP FILLING (64% hit rate!) ===
    if last_draw:
        last_nums = sorted(last_draw['numbers'])
        for j in range(len(last_nums)-1):
            gap = last_nums[j+1] - last_nums[j]
            if gap >= 10:  # Big gap
                middle = (last_nums[j] + last_nums[j+1]) // 2
                for n in [middle-1, middle, middle+1]:
                    if 1 <= n <= 42:
                        scores[n]["score"] += 10
                        scores[n]["reasons"].append(f"🕳️ Gap fill: {last_nums[j]}-{last_nums[j+1]}")
    
    # === 12. DIGIT FAMILY CONNECTION (47.9% hit rate!) ===
    if last_draw:
        last_nums = last_draw['numbers']
        for n in last_nums:
            digit_family = n % 10  # Last digit
            # Boost other numbers ending in same digit
            for other in range(digit_family, 43, 10):
                if other != n and 1 <= other <= 42:
                    scores[other]["score"] += 8
                    scores[other]["reasons"].append(f"👨‍👩‍👧 Family: ends in {digit_family}")
    
    # === 13. DISTANCE FAMILY (flip - 42s) ===
    def get_distance_family(n):
        flipped_n = int(str(n)[::-1])
        result = flipped_n
        while result > 42:
            result -= 42
        return result
    
    if last_draw:
        last_nums = last_draw['numbers']
        for n in last_nums:
            dist_fam = get_distance_family(n)
            if dist_fam != n and 1 <= dist_fam <= 42:
                scores[dist_fam]["score"] += 6
                scores[dist_fam]["reasons"].append(f"🔄 Distance: {n}→{dist_fam}")
    
    # === 14. DATE NUMEROLOGY (year + month) ===
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Year pattern: 2026 → 20+26=46 → 46-42=4
    year_num = (current_year // 100) + (current_year % 100)  # 20+26=46
    while year_num > 42:
        year_num -= 42
    scores[year_num]["score"] += 8
    scores[year_num]["reasons"].append(f"📅 Year: {current_year}→{year_num}")
    
    # Month + year combo
    month_year = current_month + (current_year % 100)  # e.g., 4+26=30
    if 1 <= month_year <= 42:
        scores[month_year]["score"] += 8
        scores[month_year]["reasons"].append(f"📅 Month+Year: {current_month}+{current_year%100}={month_year}")
    elif month_year > 42:
        month_year -= 42
        if 1 <= month_year <= 42:
            scores[month_year]["score"] += 8
            scores[month_year]["reasons"].append(f"📅 Month+Year: reduced to {month_year}")
    
    # === 15. LUCKY NUMBER FAMILY PATTERN (47.2% hit rate!) ===
    # If last draw had Lucky Number, boost numbers ending in that digit
    if last_draw and last_draw.get('lucky_number'):
        lucky = last_draw['lucky_number']
        # Numbers ending in lucky number digit (e.g., lucky=3 -> 3,13,23,33)
        for n in range(lucky, 43, 10):
            if 1 <= n <= 42:
                scores[n]["score"] += 12
                scores[n]["reasons"].append(f"🍀 Lucky family: ends in {lucky}")
        # Also boost the lucky number itself
        if 1 <= lucky <= 42:
            scores[lucky]["score"] += 8
            scores[lucky]["reasons"].append(f"🍀 Lucky number: {lucky}")
    
    # === 16. REPLAY NUMBER PATTERN (18.9% hit rate) ===
    # Replay number has slight tendency to appear in next draw
    if last_draw and last_draw.get('replay_number'):
        replay = last_draw['replay_number']
        if 1 <= replay <= 42:
            scores[replay]["score"] += 10
            scores[replay]["reasons"].append(f"🔄 Replay number: {replay}")
        # Also boost numbers ending in replay's digit
        replay_digit = replay % 10
        for n in range(replay_digit, 43, 10):
            if 1 <= n <= 42 and n != replay:
                scores[n]["score"] += 5
                scores[n]["reasons"].append(f"🔄 Replay family: ends in {replay_digit}")
    
    # === 17. LUCKY NUMBER → FIRST POSITION PATTERN (13.9% vs 2.4%) ===
    # Lucky number often equals the first (smallest) number in next draw
    if last_draw and last_draw.get('lucky_number'):
        lucky = last_draw['lucky_number']
        # Boost the lucky number itself (might be first position)
        if 1 <= lucky <= 6:  # Lucky is 1-6, these are often first position
            scores[lucky]["score"] += 15
            scores[lucky]["reasons"].append(f"🎯 Lucky→First: {lucky} (13.9% pattern)")
    
    # === 18. POSITION 6 + LUCKY → DIGITS PATTERN (18% P1, 6.4% P2) ===
    # Sum of Position 6 + Lucky number → digits become next P1 and P2
    # Example: P6=35, Lucky=1 → 36 → digits 3,6 → next draw P1=3, P2=6
    if last_draw and last_draw.get('lucky_number'):
        p6 = last_draw['numbers'][5]  # Position 6 (last/highest number)
        lucky = last_draw['lucky_number']
        sum_p6_lucky = p6 + lucky
        
        # Extract digits
        digit1 = sum_p6_lucky // 10  # tens digit
        digit2 = sum_p6_lucky % 10   # ones digit
        
        # Boost digit1 (18% hit rate for P1!)
        if 1 <= digit1 <= 9:
            scores[digit1]["score"] += 18
            scores[digit1]["reasons"].append(f"🔢 P6+Lucky: {p6}+{lucky}={sum_p6_lucky} → digit {digit1} (18%)")
        
        # Boost digit2 (6.4% hit rate for P2)
        if 1 <= digit2 <= 9 and digit2 != digit1:
            scores[digit2]["score"] += 10
            scores[digit2]["reasons"].append(f"🔢 P6+Lucky: {p6}+{lucky}={sum_p6_lucky} → digit {digit2}")
        
        # Also boost combined number if ≤42
        if 10 <= sum_p6_lucky <= 42:
            scores[sum_p6_lucky]["score"] += 8
            scores[sum_p6_lucky]["reasons"].append(f"🔢 P6+Lucky sum: {sum_p6_lucky}")
        
        # Boost numbers starting with digit1 (e.g., digit1=3 → 30,31,32...)
        if 1 <= digit1 <= 4:
            for n in range(digit1 * 10, min(digit1 * 10 + 10, 43)):
                if 1 <= n <= 42:
                    scores[n]["score"] += 5
                    scores[n]["reasons"].append(f"🔢 P6+Lucky family: starts with {digit1}")
    
    # === 19. QUARTER FIRST SERIES - HIDDEN NUMBER SEQUENCE ===
    # Pattern: First draw P1 represents hidden number (found via nextP1 - P2)
    # Count sequence from hidden, track through P1 and P2
    # P1 sums predict next (5+7=12 → next P1=13)
    # Serial sequences (32,33,34) minus offset = hidden sequence (11,12,13)
    
    # Get quarter draws
    quarter_size = 27  # First 3 quarters have 27 draws
    current_quarter_start = (len(year_draws) // quarter_size) * quarter_size
    quarter_draws = year_draws[current_quarter_start:] if year_draws else []
    
    if len(quarter_draws) >= 2:
        # Find hidden number: nextP1 - P2 from first draw
        first_draw = quarter_draws[0]
        second_draw = quarter_draws[1]
        hidden_num = second_draw['numbers'][0] - first_draw['numbers'][1]
        
        if 1 <= abs(hidden_num) <= 20:
            # Current position in quarter
            pos_in_quarter = len(quarter_draws)
            
            # Calculate expected sequence number
            seq_num = abs(hidden_num) + pos_in_quarter
            
            # Boost sequence number if valid
            if 1 <= seq_num <= 42:
                scores[seq_num]["score"] += 15
                scores[seq_num]["reasons"].append(f"🔮 Quarter hidden seq: {abs(hidden_num)}+{pos_in_quarter}={seq_num}")
            
            # P1 sum pattern: sum of last two P1s predicts next
            if len(quarter_draws) >= 2:
                last_p1 = quarter_draws[-1]['numbers'][0]
                prev_p1 = quarter_draws[-2]['numbers'][0]
                p1_sum = last_p1 + prev_p1
                
                # Next P1 might be p1_sum or p1_sum + 1
                for candidate in [p1_sum, p1_sum + 1]:
                    if 1 <= candidate <= 42:
                        scores[candidate]["score"] += 12
                        scores[candidate]["reasons"].append(f"🔮 P1 sum: {prev_p1}+{last_p1}={p1_sum} → {candidate}")
            
            # Serial pattern: look for consecutive runs, missing = appears at P1
            if last_draw:
                nums = sorted(last_draw['numbers'])
                for j in range(len(nums) - 1):
                    if nums[j+1] - nums[j] == 1:  # Consecutive
                        # Check what's missing in the run
                        if j + 2 < len(nums) and nums[j+2] - nums[j+1] == 2:
                            missing = nums[j+1] + 1
                            # The missing number minus offset might appear at P1
                            offset = nums[j] - abs(hidden_num)
                            predicted = missing - offset
                            if 1 <= predicted <= 42:
                                scores[predicted]["score"] += 10
                                scores[predicted]["reasons"].append(f"🔮 Serial missing: {missing}→P1={predicted}")
    
    # === 23. BASE NUMBER PATTERN ===
    # Base Number = Draw 2 P1 + Hidden
    # This base number appears at P4 in Draw 1
    # Can predict P4 early: nextP1 + hidden = P4
    if len(quarter_draws) >= 2:
        d1 = quarter_draws[0]
        d2 = quarter_draws[1]
        
        # Hidden number
        p1_hidden = abs(d2['numbers'][0] - d1['numbers'][1])
        
        # Base number = Draw 2 P1 + Hidden
        base_number = d2['numbers'][0] + p1_hidden
        
        if 1 <= base_number <= 42:
            scores[base_number]["score"] += 15
            scores[base_number]["reasons"].append(f"🎯 Base number: D2_P1({d2['numbers'][0]})+hidden({p1_hidden})={base_number}")
        
        # Also: current P1 + hidden might predict future P4
        if last_draw:
            predicted_p4 = last_draw['numbers'][0] + p1_hidden
            if 1 <= predicted_p4 <= 42:
                scores[predicted_p4]["score"] += 10
                scores[predicted_p4]["reasons"].append(f"🎯 P4 predict: lastP1({last_draw['numbers'][0]})+hidden({p1_hidden})={predicted_p4}")
    
    # === 22. P4 HIDDEN NUMBER PATTERN ===
    # P4 Hidden = P1 Hidden + P2 (from first draw)
    # Then count sequence and track P4 matches
    if len(quarter_draws) >= 2:
        d1 = quarter_draws[0]
        d2 = quarter_draws[1]
        
        # P1 hidden
        p1_hidden = d2['numbers'][0] - d1['numbers'][1]
        
        # P4 hidden = P1 hidden + P2 from first draw
        p4_hidden = abs(p1_hidden) + d1['numbers'][1]
        
        # Current position in quarter
        pos = len(quarter_draws)
        
        # P4 sequence number
        p4_seq = p4_hidden + pos - 1
        
        if 1 <= p4_seq <= 42:
            scores[p4_seq]["score"] += 12
            scores[p4_seq]["reasons"].append(f"🎲 P4 hidden seq: {p4_hidden}+{pos-1}={p4_seq}")
        
        # Also: P4 might equal P4_hidden + P1_hidden
        p4_combo = p4_hidden + abs(p1_hidden)
        if 1 <= p4_combo <= 42 and p4_combo != p4_seq:
            scores[p4_combo]["score"] += 8
            scores[p4_combo]["reasons"].append(f"🎲 P4 combo: {p4_hidden}+{abs(p1_hidden)}={p4_combo}")
    
    # === 21. SAME DATE HISTORY PATTERN ===
    # Numbers that appeared on same date (month-day) in previous years
    from collections import Counter as Cnt
    current_date = datetime.now()
    current_md = f"{current_date.month:02d}-{current_date.day:02d}"
    
    # Find all draws on same month-day from previous years
    same_date_draws = [d for d in draws if d['date'][5:] == current_md]
    if len(same_date_draws) >= 2:
        same_date_nums = []
        for sd in same_date_draws:
            same_date_nums.extend(sd['numbers'])
        
        sd_freq = Cnt(same_date_nums)
        # Boost numbers that appeared 2+ times on this date
        for n, count in sd_freq.items():
            if count >= 2 and 1 <= n <= 42:
                bonus = min(count * 5, 15)
                scores[n]["score"] += bonus
                scores[n]["reasons"].append(f"📅 Same date history: {count}x on {current_md}")
    
    # === 20. P2 DRAW POINTER PATTERN ===
    # When P2 breaks sequence, P2 value = draw number to find the answer
    # Example: Draw 5 P2=9 (expected 12) → Draw 9 P1=12!
    if len(quarter_draws) >= 2:
        # Get last P2 value - it might point to a future draw
        last_p2 = quarter_draws[-1]['numbers'][1] if quarter_draws else 0
        pos_in_q = len(quarter_draws)
        
        # If P2 < current position, it pointed backward (already happened)
        # If P2 > current position, it's pointing forward!
        if last_p2 > pos_in_q and last_p2 <= 27:
            # P2 is pointing to a future draw
            # The sequence number at that draw = hidden + P2 value
            future_seq = abs(hidden_num) + last_p2 if 'hidden_num' in dir() else last_p2
            if 1 <= future_seq <= 42:
                scores[future_seq]["score"] += 12
                scores[future_seq]["reasons"].append(f"🎯 P2 pointer: P2={last_p2}→Draw {last_p2} expects {future_seq}")
        
        # Also: current draw number might be pointed to by earlier P2
        # If we're at draw N, check if any earlier P2 = N
        for j, qd in enumerate(quarter_draws[:-1], start=1):
            if qd['numbers'][1] == pos_in_q:
                # Earlier draw's P2 pointed to current draw!
                # Current P1 should relate to sequence
                expected_seq = abs(hidden_num) + pos_in_q if 'hidden_num' in dir() else pos_in_q
                if 1 <= expected_seq <= 42:
                    scores[expected_seq]["score"] += 15
                    scores[expected_seq]["reasons"].append(f"🎯 P2 pointed here: Draw {j} P2={pos_in_q}→P1={expected_seq}")
    
    # === 25. RARE EVENT COUNT SEQUENCE (Your Pattern!) ===
    # Count from last VERY rare event (5 in same gruppe)
    # Count number OR its circle partner (+/-21) appears in draws
    # ALWAYS USE DATE CONNECTION
    
    # Find all very rare events (5+ in same gruppe 1-9, 10-19, 20-29, 30-39)
    def get_gruppe(n):
        if n <= 9: return "1-9"
        elif n <= 19: return "10-19"
        elif n <= 29: return "20-29"
        elif n <= 39: return "30-39"
        else: return "40-42"
    
    very_rare_events = []
    sorted_all = sorted(draws, key=lambda x: x['date'])
    
    for i, d in enumerate(sorted_all):
        nums = d['numbers']
        g1 = len([n for n in nums if 1 <= n <= 9])
        g2 = len([n for n in nums if 10 <= n <= 19])
        g3 = len([n for n in nums if 20 <= n <= 29])
        g4 = len([n for n in nums if 30 <= n <= 39])
        
        if max(g1, g2, g3, g4) >= 5:
            outsider = None
            if g1 >= 5:
                outsider = [n for n in nums if n > 9]
            elif g2 >= 5:
                outsider = [n for n in nums if n < 10 or n > 19]
            elif g3 >= 5:
                outsider = [n for n in nums if n < 20 or n > 29]
            elif g4 >= 5:
                outsider = [n for n in nums if n < 30 or n > 39]
            
            very_rare_events.append({
                'index': i,
                'date': d['date'],
                'numbers': nums,
                'outsider': outsider[0] if outsider else None
            })
    
    # Count from most recent very rare event
    if very_rare_events:
        last_rare = very_rare_events[-1]
        current_idx = len(sorted_all)
        count_from_rare = current_idx - last_rare['index']
        
        # The count number (wrapped to 1-42)
        count_num = count_from_rare if count_from_rare <= 42 else ((count_from_rare - 1) % 42) + 1
        circle_partner = count_num + 21 if count_num + 21 <= 42 else count_num - 21
        
        # Boost count number and circle partner
        if 1 <= count_num <= 42:
            scores[count_num]["score"] += 20
            scores[count_num]["reasons"].append(f"🔢 Rare count: {count_from_rare} from {last_rare['date']}")
        
        if 1 <= circle_partner <= 42:
            scores[circle_partner]["score"] += 18
            scores[circle_partner]["reasons"].append(f"🔢 Rare circle: {count_num}↔{circle_partner}")
        
        # Also boost the outsider's circle partner (key number!)
        if last_rare['outsider']:
            out = last_rare['outsider']
            out_circle = out + 21 if out + 21 <= 42 else out - 21
            if 1 <= out_circle <= 42:
                scores[out_circle]["score"] += 15
                scores[out_circle]["reasons"].append(f"🔢 Rare outsider: {out}↔{out_circle}")
    
    # === 26. DATE ALWAYS PATTERN (Always Active!) ===
    # Date connections are ALWAYS used
    current_date = datetime.now()
    day = current_date.day
    month = current_date.month
    
    # Day and its circle
    day_circle = day + 21 if day + 21 <= 42 else day - 21
    scores[day]["score"] += 12
    scores[day]["reasons"].append(f"📅 Date day: {day}")
    if 1 <= day_circle <= 42:
        scores[day_circle]["score"] += 12
        scores[day_circle]["reasons"].append(f"📅 Date day circle: {day}↔{day_circle}")
    
    # Month and its circle  
    month_circle = month + 21 if month + 21 <= 42 else month - 21
    scores[month]["score"] += 10
    scores[month]["reasons"].append(f"📅 Date month: {month}")
    if 1 <= month_circle <= 42:
        scores[month_circle]["score"] += 10
        scores[month_circle]["reasons"].append(f"📅 Date month circle: {month}↔{month_circle}")
    
    # Day + Month combination
    day_month_sum = day + month
    if 1 <= day_month_sum <= 42:
        scores[day_month_sum]["score"] += 8
        scores[day_month_sum]["reasons"].append(f"📅 Day+Month: {day}+{month}={day_month_sum}")
    
    # === SMART PATTERN SELECTION ===
    # Not all patterns fire every time - some are situational
    # Date patterns (25, 26) ALWAYS active
    # Others activate based on conditions
    active_patterns = ["Date (always)", "Rare Count (if recent)"]
    
    # 15. RARE EVENT COUNTS ===
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
    
    rare_events = []
    for i, draw in enumerate(all_draws_2020):
        groups = count_groups(draw['numbers'])
        max_group = max(groups.values())
        if max_group >= 4:
            rare_events.append({'index': i, 'date': draw['date'], 'count': max_group})
    
    current_draw_idx = len(all_draws_2020)
    rare_predictions = []
    for rare in rare_events[-5:]:
        count_since = current_draw_idx - rare['index']
        rarity = "🔥🔥🔥" if rare['count'] == 6 else ("🔥🔥" if rare['count'] == 5 else "🔥")
        
        if 1 <= count_since <= 42:
            scores[count_since]["score"] += 15 * (rare['count'] - 3)
            scores[count_since]["reasons"].append(f"Rare {rarity} +{count_since} draws (15%)")
            rare_predictions.append({
                "rare_date": rare['date'],
                "rarity": rare['count'],
                "count_since": count_since,
                "predicted": count_since
            })
        
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
    
    # === 27. STORY TRACKER PATTERN (Position Gap Analysis) ===
    # Find numbers missing for long at specific positions
    # Track their connection chain appearing = story building up to return
    # When connections appear frequently, the missing number is due!
    
    def get_number_connections(num):
        """Get all numbers connected to a number via circle, multiples, digits"""
        conns = set([num])
        # Circle partner (+/- 21)
        if num + 21 <= 42: conns.add(num + 21)
        if num - 21 >= 1: conns.add(num - 21)
        # Digit flip
        if num >= 10:
            rev = int(str(num)[::-1])
            if 1 <= rev <= 42: conns.add(rev)
        # Digit sum
        dsum = sum(int(d) for d in str(num))
        if 1 <= dsum <= 42: conns.add(dsum)
        # Multiples and factors
        for m in [2, 3, 4, 5, 6, 7]:
            if num * m <= 42: conns.add(num * m)
            if num % m == 0 and num // m >= 1: conns.add(num // m)
        return conns
    
    # Track last appearance at each position
    sorted_draws = sorted(draws, key=lambda x: x['date'], reverse=True)
    position_gaps = {}  # {(pos, num): gap_count}
    
    for pos in range(1, 7):
        for num in range(1, 43):
            for i, d in enumerate(sorted_draws):
                if d['numbers'][pos-1] == num:
                    position_gaps[(pos, num)] = i
                    break
            else:
                position_gaps[(pos, num)] = len(sorted_draws)  # Never appeared
    
    # Find numbers with big gaps (story candidates)
    story_candidates = []
    for (pos, num), gap in position_gaps.items():
        if gap >= 50:  # Missing for 50+ draws at this position
            conns = get_number_connections(num)
            story_candidates.append({
                'pos': pos,
                'num': num,
                'gap': gap,
                'connections': conns
            })
    
    # Sort by gap (longest first)
    story_candidates.sort(key=lambda x: -x['gap'])
    
    # Check recent draws for connection activity (story building)
    recent_10 = sorted_draws[:10]
    
    for story in story_candidates[:10]:  # Top 10 longest gaps
        conn_hits = 0
        recent_conn_positions = []
        
        for d in recent_10:
            for conn in story['connections']:
                if conn in d['numbers']:
                    conn_hits += 1
                    recent_conn_positions.append(d['numbers'].index(conn) + 1)
        
        # If connections appearing frequently, story is building!
        if conn_hits >= 3:
            # Boost the missing number
            boost = min(25, 10 + conn_hits * 3)  # 13-25 points based on activity
            scores[story['num']]["score"] += boost
            scores[story['num']]["reasons"].append(
                f"📖 Story: {story['num']}@P{story['pos']} missing {story['gap']}x, {conn_hits} conn hits!"
            )
            
            # Also boost numbers that transform INTO the missing number
            # Based on the 7@P4 pattern: anchor numbers can predict return
            if last_draw:
                last_nums = last_draw['numbers']
                # Check if sum/diff of last numbers = missing number
                for i in range(6):
                    for j in range(i+1, 6):
                        if last_nums[i] + last_nums[j] == story['num']:
                            scores[story['num']]["score"] += 10
                            scores[story['num']]["reasons"].append(
                                f"📖 Transform: {last_nums[i]}+{last_nums[j]}={story['num']}"
                            )
                        diff = abs(last_nums[i] - last_nums[j])
                        if diff == story['num']:
                            scores[story['num']]["score"] += 10
                            scores[story['num']]["reasons"].append(
                                f"📖 Transform: |{last_nums[i]}-{last_nums[j]}|={story['num']}"
                            )
    
    # === 28. LUCKY/REPLAY POSITION FLOW PATTERN ===
    # Lucky/Replay numbers flow through P1/P2 positions
    # Lucky from previous draw often appears at P1 in next (77.5%)
    # Replay from previous draw often appears at P1/P2 in next (87.5% combined)
    if last_draw:
        lucky = last_draw.get('lucky_number')
        replay = last_draw.get('replay_number')
        
        if lucky and 1 <= lucky <= 42:
            # Lucky → P1 prediction (77.5% when it hits)
            scores[lucky]["score"] += 15
            scores[lucky]["reasons"].append(f"🍀→P1 Lucky {lucky} flow (15.2% hit, 77.5% at P1)")
            
            # Lucky's circle partner
            lucky_circle = lucky + 21 if lucky + 21 <= 42 else lucky - 21 if lucky - 21 >= 1 else None
            if lucky_circle and 1 <= lucky_circle <= 42:
                scores[lucky_circle]["score"] += 10
                scores[lucky_circle]["reasons"].append(f"🍀 Lucky circle: {lucky}↔{lucky_circle}")
        
        if replay and 1 <= replay <= 42:
            # Replay → P1/P2 prediction (50% P1, 37.5% P2)
            scores[replay]["score"] += 12
            scores[replay]["reasons"].append(f"🔄→P1/P2 Replay {replay} flow (14% hit)")
            
            # Replay's circle partner
            replay_circle = replay + 21 if replay + 21 <= 42 else replay - 21 if replay - 21 >= 1 else None
            if replay_circle and 1 <= replay_circle <= 42:
                scores[replay_circle]["score"] += 8
                scores[replay_circle]["reasons"].append(f"🔄 Replay circle: {replay}↔{replay_circle}")
        
        # Combined transformation: Lucky - Replay or Replay - Lucky
        if lucky and replay and lucky != replay:
            diff = abs(lucky - replay)
            summ = lucky + replay
            if 1 <= diff <= 42:
                scores[diff]["score"] += 8
                scores[diff]["reasons"].append(f"🍀🔄 |L-R|: |{lucky}-{replay}|={diff}")
            if 1 <= summ <= 42:
                scores[summ]["score"] += 8
                scores[summ]["reasons"].append(f"🍀🔄 L+R: {lucky}+{replay}={summ}")
    
    # === 29. ANCHOR TRANSFORMATION PATTERN ===
    # Based on 7@P4: [1,3,4,7,16,25] → [1,3,4,7,9,23]
    # Numbers in anchor whose digit sums equal the key number transform!
    # 1+6=7, 2+5=7 → 25-16=9, 16+7=23
    if last_draw:
        last_nums = last_draw['numbers']
        
        # Find the "key" - a number whose digit sum matches other numbers' digit sums
        digit_sums = {n: sum(int(d) for d in str(n)) for n in last_nums}
        
        # Group by digit sum
        sum_groups = {}
        for n, ds in digit_sums.items():
            if ds not in sum_groups:
                sum_groups[ds] = []
            sum_groups[ds].append(n)
        
        # If 2+ numbers share same digit sum = potential key!
        for ds, nums_with_ds in sum_groups.items():
            if len(nums_with_ds) >= 2 and ds <= 21:  # Key must be valid
                # The key is the digit sum
                key = ds
                # Predict transformations
                for i in range(len(nums_with_ds)):
                    for j in range(i+1, len(nums_with_ds)):
                        diff = abs(nums_with_ds[i] - nums_with_ds[j])
                        plus_key = nums_with_ds[0] + key
                        
                        if 1 <= diff <= 42:
                            scores[diff]["score"] += 12
                            scores[diff]["reasons"].append(
                                f"🔑 Key {key}: |{nums_with_ds[i]}-{nums_with_ds[j]}|={diff}"
                            )
                        if 1 <= plus_key <= 42:
                            scores[plus_key]["score"] += 10
                            scores[plus_key]["reasons"].append(
                                f"🔑 Key {key}: {nums_with_ds[0]}+{key}={plus_key}"
                            )
    
    # === 30. P1/P2 POSITION ANALYSIS PATTERN ===
    # Analyze historical frequency of numbers at Position 1 (smallest) and Position 2
    # P1 typically ranges 1-15 (avg ~6), P2 typically ranges 2-20 (avg ~12)
    # Boost numbers that frequently appear at P1/P2
    
    p1_counter = Counter()
    p2_counter = Counter()
    
    for d in draws:
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 6:
            p1_counter[nums[0]] += 1
            p2_counter[nums[1]] += 1
    
    # Top P1 numbers (most frequent at position 1)
    p1_top = p1_counter.most_common(10)  # Top 10
    for num, count in p1_top[:5]:  # Top 5 get strong boost
        pct = count / len(draws) * 100 if draws else 0
        boost = min(15, int(pct * 1.2))  # Scale boost by frequency
        scores[num]["score"] += boost
        scores[num]["reasons"].append(f"🥇P1 hot: {num} appears {count}x ({pct:.1f}%)")
    
    # Top P2 numbers (most frequent at position 2)
    p2_top = p2_counter.most_common(10)
    for num, count in p2_top[:5]:
        pct = count / len(draws) * 100 if draws else 0
        boost = min(12, int(pct * 1.0))
        scores[num]["score"] += boost
        scores[num]["reasons"].append(f"🥈P2 hot: {num} appears {count}x ({pct:.1f}%)")
    
    # Recent P1/P2 trend analysis (last 20 draws)
    recent_p1 = []
    recent_p2 = []
    for d in sorted(draws, key=lambda x: x['date'], reverse=True)[:20]:
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 6:
            recent_p1.append(nums[0])
            recent_p2.append(nums[1])
    
    # Numbers appearing frequently in recent P1
    recent_p1_counter = Counter(recent_p1)
    for num, count in recent_p1_counter.most_common(3):
        if count >= 2:  # Appeared 2+ times in last 20 at P1
            scores[num]["score"] += 8
            scores[num]["reasons"].append(f"🥇P1 trend: {num} hit {count}x in last 20")
    
    # Numbers appearing frequently in recent P2
    recent_p2_counter = Counter(recent_p2)
    for num, count in recent_p2_counter.most_common(3):
        if count >= 2:
            scores[num]["score"] += 6
            scores[num]["reasons"].append(f"🥈P2 trend: {num} hit {count}x in last 20")
    
    # P1/P2 GAP ANALYSIS - numbers overdue at these positions
    # If a typical P1 number hasn't appeared at P1 recently, it's due
    p1_typical = set(num for num, _ in p1_top[:8])  # Numbers that often hit P1
    for num in p1_typical:
        last_at_p1 = None
        for i, d in enumerate(sorted(draws, key=lambda x: x['date'], reverse=True)):
            nums = sorted(d.get('numbers', []))
            if len(nums) >= 6 and nums[0] == num:
                last_at_p1 = i
                break
        if last_at_p1 is None or last_at_p1 > 30:
            gap = last_at_p1 if last_at_p1 else 50
            scores[num]["score"] += min(10, gap // 5)
            scores[num]["reasons"].append(f"🥇P1 due: {num} missing {gap}+ draws at P1")
    
    # === 31. P1/P2 TRANSFORMATION PATTERN ===
    # |P1 - P2| from last draw often appears at P1 (8.1%) or P2 (4.8%) of next draw
    # P1 + P2 from last draw often appears somewhere in next draw (14.6%)
    # Get the absolute most recent draw
    all_draws_sorted = sorted(draws, key=lambda x: x['date'], reverse=True)
    most_recent = all_draws_sorted[0] if all_draws_sorted else None
    
    if most_recent:
        last_nums = sorted(most_recent['numbers'])
        if len(last_nums) >= 2:
            last_p1 = last_nums[0]
            last_p2 = last_nums[1]
            
            # |P1 - P2| → Strong P1/P2 predictor (12.9% combined)
            diff = abs(last_p1 - last_p2)
            if 1 <= diff <= 42:
                scores[diff]["score"] += 18  # Strong boost
                scores[diff]["reasons"].append(f"🔗P1-P2: |{last_p1}-{last_p2}|={diff} → likely P1/P2 (12.9%)")
            
            # P1 + P2 → Appears somewhere (14.6%)
            summ = last_p1 + last_p2
            if 1 <= summ <= 42:
                scores[summ]["score"] += 12
                scores[summ]["reasons"].append(f"🔗P1+P2: {last_p1}+{last_p2}={summ} → any pos (14.6%)")
    
    # === 32. FAMILY HUNGER PATTERN ===
    # If multiple numbers from same family (ending in same digit) appeared recently,
    # the missing family member is "hungry" and likely to appear
    families = {
        1: [1, 11, 21, 31, 41],
        2: [2, 12, 22, 32, 42],
        3: [3, 13, 23, 33],
        4: [4, 14, 24, 34],
        5: [5, 15, 25, 35],
        6: [6, 16, 26, 36],
        7: [7, 17, 27, 37],
        8: [8, 18, 28, 38],
        9: [9, 19, 29, 39],
        0: [10, 20, 30, 40],
    }
    
    # Track last appearance
    num_last_seen = {}
    for i, d in enumerate(all_draws_sorted):
        for num in d.get('numbers', []):
            if num not in num_last_seen:
                num_last_seen[num] = i
    
    # Check last 10 draws for chain building
    recent_10_nums = set()
    for d in all_draws_sorted[:10]:
        recent_10_nums.update(d.get('numbers', []))
    
    for digit, family in families.items():
        appeared = [n for n in family if n in recent_10_nums]
        missing = [n for n in family if n not in recent_10_nums]
        
        if len(appeared) >= 2 and missing:  # Chain building!
            for m in missing:
                gap = num_last_seen.get(m, 50)
                # More chain members = stronger hunger
                boost = len(appeared) * 5 + min(15, gap // 2)
                scores[m]["score"] += boost
                scores[m]["reasons"].append(f"🍽️ Hungry: Family-{digit} chain {appeared}, gap {gap}")
    
    # === 33. MIRROR/REVERSE PATTERN (15% hit rate) ===
    # Numbers from last draw often appear flipped in next draw
    # e.g., 13→31, 24→42, 30→3
    if most_recent:
        for n in most_recent['numbers']:
            s = str(n)
            if len(s) == 2:
                rev = int(s[::-1])
                if 1 <= rev <= 42 and rev != n:
                    scores[rev]["score"] += 12
                    scores[rev]["reasons"].append(f"🔄 Mirror: {n}→{rev} (15% hit)")
    
    # === 34. CONSECUTIVE PAIR PREDICTION ===
    # 54.3% of draws have consecutive pairs. Hot pairs: 13-14, 41-42, 5-6
    # If one number from a hot pair is likely, boost its partner
    hot_pairs = [(13, 14), (41, 42), (5, 6), (37, 38), (3, 4), (16, 17), (35, 36), (22, 23)]
    
    # Get current top candidates
    temp_ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    top_candidates = [n for n, _ in temp_ranked[:20]]
    
    for a, b in hot_pairs:
        if a in top_candidates and b not in top_candidates:
            scores[b]["score"] += 10
            scores[b]["reasons"].append(f"👥 Pair: {a}-{b} hot consecutive")
        elif b in top_candidates and a not in top_candidates:
            scores[a]["score"] += 10
            scores[a]["reasons"].append(f"👥 Pair: {a}-{b} hot consecutive")
    
    # === 35. LUCKY NUMBER CONNECTION ===
    # Lucky × 7 appears in next draw (14.6%), Lucky direct (15.2%), Lucky doubled (6.8%)
    if most_recent:
        prev_lucky = most_recent.get('lucky_number')
        if prev_lucky and 1 <= prev_lucky <= 6:
            # Lucky × 7 (strongest: 14.6%)
            times7 = prev_lucky * 7
            if 1 <= times7 <= 42:
                scores[times7]["score"] += 12
                scores[times7]["reasons"].append(f"⭐ Lucky×7: {prev_lucky}×7={times7} (14.6%)")
            
            # Lucky direct (15.2%)
            scores[prev_lucky]["score"] += 10
            scores[prev_lucky]["reasons"].append(f"⭐ Lucky direct: {prev_lucky} (15.2%)")
            
            # Lucky doubled (6.8%) - only for 1-4
            if prev_lucky <= 4:
                doubled = prev_lucky * 10 + prev_lucky  # 1→11, 2→22, 3→33, 4→44(invalid)
                if 1 <= doubled <= 42:
                    scores[doubled]["score"] += 6
                    scores[doubled]["reasons"].append(f"⭐ Lucky doubled: {prev_lucky}→{doubled} (6.8%)")
    
    # === 36. P3/P4 POSITION ANALYSIS ===
    # P3 hot numbers (avg 18.2): 21, 19, 14, 17, 16
    # P4 hot numbers (avg 24.5): 28, 21, 31, 22, 23, 29
    p3_counter = Counter()
    p4_counter = Counter()
    
    for d in draws:
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 6:
            p3_counter[nums[2]] += 1
            p4_counter[nums[3]] += 1
    
    # Top P3 numbers
    p3_top = p3_counter.most_common(8)
    for num, count in p3_top[:5]:
        pct = count / len(draws) * 100 if draws else 0
        boost = min(10, int(pct * 1.5))
        scores[num]["score"] += boost
        scores[num]["reasons"].append(f"🥉P3 hot: {num} appears {count}x ({pct:.1f}%)")
    
    # Top P4 numbers
    p4_top = p4_counter.most_common(8)
    for num, count in p4_top[:5]:
        pct = count / len(draws) * 100 if draws else 0
        boost = min(10, int(pct * 1.5))
        scores[num]["score"] += boost
        scores[num]["reasons"].append(f"🏅P4 hot: {num} appears {count}x ({pct:.1f}%)")
    
    # === 37. P3/P4 TRANSFORMATION PATTERNS ===
    # |P3-P4| → often P1/P2 (14.4%), P3-P1 (16.2%), P4-P2 (14.6%), P3+P1 (13.7%)
    if most_recent:
        last_nums = sorted(most_recent['numbers'])
        if len(last_nums) >= 4:
            p1, p2, p3, p4 = last_nums[0], last_nums[1], last_nums[2], last_nums[3]
            
            # |P3-P4| → likely P1/P2 (14.4%)
            diff_34 = abs(p3 - p4)
            if 1 <= diff_34 <= 42:
                scores[diff_34]["score"] += 12
                scores[diff_34]["reasons"].append(f"🔗|P3-P4|: |{p3}-{p4}|={diff_34} → P1/P2 (14.4%)")
            
            # P3-P1 (16.2% - strongest!)
            val = p3 - p1
            if 1 <= val <= 42:
                scores[val]["score"] += 15
                scores[val]["reasons"].append(f"🔗P3-P1: {p3}-{p1}={val} (16.2%)")
            
            # P4-P2 (14.6%)
            val = p4 - p2
            if 1 <= val <= 42:
                scores[val]["score"] += 12
                scores[val]["reasons"].append(f"🔗P4-P2: {p4}-{p2}={val} (14.6%)")
            
            # P3+P1 (13.7%)
            val = p3 + p1
            if 1 <= val <= 42:
                scores[val]["score"] += 11
                scores[val]["reasons"].append(f"🔗P3+P1: {p3}+{p1}={val} (13.7%)")
    
    # === 38. DATE DIGIT STORY PATTERN (79.3% hit rate!) ===
    # Previous draw's date digits form combos that appear in next draw
    # D, M, Y digits combine: e.g., 8/12/26 → 8, 1, 2, 6 → 12, 21, 26, 28, etc.
    if most_recent:
        prev_date = most_recent.get('date', '')
        if prev_date:
            parts = prev_date.split('-')
            if len(parts) == 3:
                day = int(parts[2])
                month = int(parts[1])
                y_short = int(parts[0]) % 100
                
                # Extract all digits
                date_digits = []
                for d in str(day):
                    date_digits.append(int(d))
                for d in str(month):
                    date_digits.append(int(d))
                for d in str(y_short):
                    date_digits.append(int(d))
                
                # Generate all valid combos
                date_combos = set()
                for d in date_digits:
                    if 1 <= d <= 42:
                        date_combos.add(d)
                for i in range(len(date_digits)):
                    for j in range(len(date_digits)):
                        if i != j:
                            val = date_digits[i] * 10 + date_digits[j]
                            if 1 <= val <= 42:
                                date_combos.add(val)
                
                # Boost all date combos (79.3% hit rate!)
                for combo in date_combos:
                    scores[combo]["score"] += 15
                    scores[combo]["reasons"].append(f"📅 Date story: {prev_date} digits → {combo} (79%)")
    
    # === 39. CURRENT DATE PATTERN (75% hit rate) ===
    # Today's date digits also appear in today's draw
    from datetime import datetime
    today = datetime.now()
    today_day = today.day
    today_month = today.month
    today_year = today.year % 100
    
    today_digits = []
    for d in str(today_day):
        today_digits.append(int(d))
    for d in str(today_month):
        today_digits.append(int(d))
    for d in str(today_year):
        today_digits.append(int(d))
    
    today_combos = set()
    for d in today_digits:
        if 1 <= d <= 42:
            today_combos.add(d)
    for i in range(len(today_digits)):
        for j in range(len(today_digits)):
            if i != j:
                val = today_digits[i] * 10 + today_digits[j]
                if 1 <= val <= 42:
                    today_combos.add(val)
    
    for combo in today_combos:
        scores[combo]["score"] += 10
        scores[combo]["reasons"].append(f"📅 Today: {today_day}/{today_month} → {combo} (75%)")
    
    # === 40. NUMBER 9 AT P1 PREDICTOR ===
    # Special pattern: When does 9 appear as smallest number (P1)?
    # Signals: Family 9 (29/39) in prev draw (43%), 9 missing 10+ draws (hunger)
    if most_recent:
        last_nums = sorted(most_recent.get('numbers', []))
        
        # Check family 9 in last draw
        family_9_present = [n for n in last_nums if n in [9, 19, 29, 39]]
        
        # Check 9 gap
        nine_gap = 0
        for d in all_draws_sorted:
            if 9 in d.get('numbers', []):
                break
            nine_gap += 1
        
        # Calculate 9@P1 likelihood
        signals = 0
        reasons_9 = []
        
        if family_9_present:
            signals += 1
            reasons_9.append(f"Family 9 {family_9_present} triggers")
        
        if nine_gap >= 15:
            signals += 1
            reasons_9.append(f"9 hungry ({nine_gap} draws)")
        
        if len(last_nums) >= 2 and last_nums[0] in [2, 5, 6, 7, 12]:
            signals += 1
            reasons_9.append(f"P1={last_nums[0]} pattern")
        
        if signals >= 2:
            scores[9]["score"] += 20
            scores[9]["reasons"].append(f"🔢 9@P1 likely: {', '.join(reasons_9)}")
    
    # === 41. 9 ↔ 19 CONNECTION PATTERN ===
    # 19 in prev draw → 9 next (18.8%), 9 in prev → 19 next (15.9%)
    # Average gap between 9 and 19: 3.2 draws
    if most_recent:
        last_nums = most_recent.get('numbers', [])
        
        # 19 appeared → boost 9 (18.8%)
        if 19 in last_nums:
            scores[9]["score"] += 15
            scores[9]["reasons"].append(f"🔗 19→9: 19 in prev → 9 likely (18.8%)")
        
        # 9 appeared → boost 19 (15.9%)
        if 9 in last_nums:
            scores[19]["score"] += 12
            scores[19]["reasons"].append(f"🔗 9→19: 9 in prev → 19 likely (15.9%)")
        
        # Check gaps - if one is due and other appeared recently, boost the due one
        nine_gap = 0
        nineteen_gap = 0
        for i, d in enumerate(all_draws_sorted):
            if nine_gap == 0 and 9 in d.get('numbers', []):
                nine_gap = i
            if nineteen_gap == 0 and 19 in d.get('numbers', []):
                nineteen_gap = i
            if nine_gap > 0 and nineteen_gap > 0:
                break
        
        # 9-19 oscillation: if one appeared recently and other is overdue
        if nineteen_gap <= 3 and nine_gap >= 10:
            scores[9]["score"] += 12
            scores[9]["reasons"].append(f"🔗 9↔19 oscillation: 19 recent, 9 due ({nine_gap} gap)")
        elif nine_gap <= 3 and nineteen_gap >= 10:
            scores[19]["score"] += 12
            scores[19]["reasons"].append(f"🔗 9↔19 oscillation: 9 recent, 19 due ({nineteen_gap} gap)")
    
    # === 42. GAP DIGITS PATTERN (Last Time Position Count) ===
    # When a number returns to a specific position (e.g., 9@P1), the number of draws since 
    # its last appearance at that position predicts accompanying numbers.
    # Example: 9@P1 last appeared 61 draws ago → digits 6 and 1 → boost 1, 6, 11, 16, 21, 26, 61(if valid)
    # Validation showed ~25% accuracy for this pattern!
    
    # Track position-specific gaps for numbers that might appear at specific positions
    position_trackers = {}  # {(number, position): draws_since_last}
    
    for pos in range(6):  # P1 to P6 (positions 0-5)
        for d_idx, d in enumerate(all_draws_sorted):
            nums = sorted(d.get('numbers', []))
            if len(nums) >= 6:
                num_at_pos = nums[pos]
                key = (num_at_pos, pos)
                if key not in position_trackers:
                    position_trackers[key] = d_idx  # First time we see it = gap
    
    # For numbers likely to appear at specific positions, calculate gap digits boost
    # Focus on numbers already scoring high for a position
    temp_ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    position_names = ["P1", "P2", "P3", "P4", "P5", "P6"]
    
    for num, data in temp_ranked[:20]:  # Check top 20 candidates
        # Determine likely position for this number based on typical ranges
        # P1: 1-15, P2: 2-20, P3: 10-25, P4: 15-32, P5: 25-38, P6: 30-42
        likely_positions = []
        if num <= 15:
            likely_positions.append(0)  # P1
        if 2 <= num <= 20:
            likely_positions.append(1)  # P2
        if 10 <= num <= 25:
            likely_positions.append(2)  # P3
        if 15 <= num <= 32:
            likely_positions.append(3)  # P4
        if 25 <= num <= 38:
            likely_positions.append(4)  # P5
        if num >= 30:
            likely_positions.append(5)  # P6
        
        for pos in likely_positions:
            key = (num, pos)
            gap = position_trackers.get(key, 0)
            
            if gap >= 10:  # Only for significant gaps
                # Extract digits from the gap number
                gap_str = str(gap)
                gap_digits = [int(d) for d in gap_str if d != '0']
                
                # Generate numbers containing these digits
                gap_derived = set()
                for digit in gap_digits:
                    if 1 <= digit <= 42:
                        gap_derived.add(digit)
                    # Numbers starting with this digit (e.g., 6 → 6, 61, 62...)
                    for tens in range(0, 5):
                        val = digit + tens * 10
                        if 1 <= val <= 42:
                            gap_derived.add(val)
                    # Numbers ending with this digit (e.g., 1 → 1, 11, 21, 31, 41)
                    for tens in range(0, 5):
                        val = tens * 10 + digit
                        if 1 <= val <= 42:
                            gap_derived.add(val)
                
                # Also add the gap number itself if valid
                if 1 <= gap <= 42:
                    gap_derived.add(gap)
                
                # Boost derived numbers (25% hit rate!)
                for derived in gap_derived:
                    if derived != num:  # Don't boost the trigger number itself
                        boost = min(12, 6 + gap // 10)  # Scale with gap size
                        scores[derived]["score"] += boost
                        scores[derived]["reasons"].append(
                            f"🔢 Gap digits: {num}@{position_names[pos]} gap={gap} → digits {gap_digits} (25%)"
                        )
    
    # === 43. P4-P5 DANCE PATTERN ===
    # P4 and P5 love to dance close together! Average gap only 6.4
    # Consecutive (P5=P4+1): 13.8%, Small gaps (1-3): 37.7%
    # Hot pairs: 31-33, 31-32, 30-31, 22-23, 32-33 - Numbers 30-33 dominate!
    
    # Analyze recent P4-P5 patterns
    p4_p5_diffs = []
    recent_p4_p5_pairs = []
    for d in all_draws_sorted[:50]:  # Last 50 draws
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 6:
            p4, p5 = nums[3], nums[4]
            p4_p5_diffs.append(p5 - p4)
            recent_p4_p5_pairs.append((p4, p5))
    
    # Hot P4-P5 dance partners (historically proven)
    hot_p4_p5_pairs = [(31, 33), (31, 32), (30, 31), (22, 23), (32, 33), (33, 36), (28, 30), (34, 37)]
    
    # Boost numbers that frequently appear at P4-P5
    p4_p5_hot_numbers = {30, 31, 32, 33, 34, 22, 23, 28, 36, 37}
    for num in p4_p5_hot_numbers:
        scores[num]["score"] += 8
        scores[num]["reasons"].append(f"💃 P4-P5 dancer: {num} dominates mid-high positions")
    
    # If we see a pattern in recent diffs, predict similar gap
    if p4_p5_diffs:
        avg_recent_diff = sum(p4_p5_diffs[:10]) / min(10, len(p4_p5_diffs))
        # Boost pairs that match recent gap pattern
        for p4 in range(20, 36):
            p5_predicted = p4 + int(round(avg_recent_diff))
            if 1 <= p5_predicted <= 42:
                scores[p4]["score"] += 5
                scores[p5_predicted]["score"] += 5
                scores[p4]["reasons"].append(f"💃 P4-P5 gap pattern: avg diff={avg_recent_diff:.1f}")
    
    # Boost hot pairs specifically
    for p4, p5 in hot_p4_p5_pairs:
        scores[p4]["score"] += 6
        scores[p5]["score"] += 6
        scores[p4]["reasons"].append(f"💃 Hot P4-P5 pair: {p4}-{p5}")
    
    # === 44. DATE ±3 WINDOW PATTERN (58.3% hit rate!) ===
    # Day number has 58% chance to appear within ±3 draws!
    # This is a strong predictor
    
    today = datetime.now()
    day_num = today.day
    month_num = today.month
    
    # Boost the day number strongly (58% hit rate!)
    if 1 <= day_num <= 42:
        scores[day_num]["score"] += 18  # Strong boost for 58% pattern
        scores[day_num]["reasons"].append(f"📅 Date ±3 window: Day {day_num} (58.3% hit rate!)")
    
    # Also boost day ± 1,2,3 (nearby days often hit)
    for offset in [-3, -2, -1, 1, 2, 3]:
        nearby_day = day_num + offset
        if 1 <= nearby_day <= 42:
            scores[nearby_day]["score"] += 8
            scores[nearby_day]["reasons"].append(f"📅 Date ±3 window: near day {day_num}")
    
    # Month number boost
    if 1 <= month_num <= 12:
        scores[month_num]["score"] += 10
        scores[month_num]["reasons"].append(f"📅 Month {month_num} in play")
    
    # Day + Month combinations
    day_month_sum = day_num + month_num
    if 1 <= day_month_sum <= 42:
        scores[day_month_sum]["score"] += 8
        scores[day_month_sum]["reasons"].append(f"📅 Day+Month: {day_num}+{month_num}={day_month_sum}")
    
    day_month_diff = abs(day_num - month_num)
    if 1 <= day_month_diff <= 42:
        scores[day_month_diff]["score"] += 6
        scores[day_month_diff]["reasons"].append(f"📅 |Day-Month|: |{day_num}-{month_num}|={day_month_diff}")
    
    # === 45. P5-P6 DANCE PATTERN ===
    # P5-P6 are the highest positions, they stay close! Average gap: 6.1
    # Consecutive (P6=P5+1): 13.8%, Small gaps (1-3): 38.6%
    # Hot pairs: 41-42 (2.2%), 37-40, 40-42, 39-42, 39-41
    # Hot P6: 42 (14.3%), 40 (12.2%), 41 (11.6%)
    # Hot P5: 36 (7.1%), 33 (6.9%), 32 (6.7%)
    
    # Analyze recent P5-P6 patterns
    p5_p6_diffs = []
    recent_p5_p6_pairs = []
    for d in all_draws_sorted[:50]:
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 6:
            p5, p6 = nums[4], nums[5]
            p5_p6_diffs.append(p6 - p5)
            recent_p5_p6_pairs.append((p5, p6))
    
    # Hot P5-P6 dance partners
    hot_p5_p6_pairs = [(41, 42), (37, 40), (40, 42), (39, 42), (39, 41), (37, 38), (39, 40), (36, 42)]
    
    # Hot P6 numbers (highest position loves high numbers)
    p6_hot = {42, 40, 41, 39, 38, 37}
    for num in p6_hot:
        boost = 12 if num == 42 else 10 if num in {40, 41} else 8
        scores[num]["score"] += boost
        scores[num]["reasons"].append(f"🎯 P6 favorite: {num} dominates P6 ({14 if num==42 else 12 if num==40 else 11}%)")
    
    # Hot P5 numbers
    p5_hot = {36, 33, 32, 37, 35, 31, 30, 34}
    for num in p5_hot:
        scores[num]["score"] += 8
        scores[num]["reasons"].append(f"🎯 P5 favorite: {num} at P5 position")
    
    # Boost hot P5-P6 pairs
    for p5, p6 in hot_p5_p6_pairs:
        scores[p5]["score"] += 6
        scores[p6]["score"] += 6
        scores[p5]["reasons"].append(f"💃 Hot P5-P6 pair: {p5}-{p6}")
    
    # Recent gap pattern prediction
    if p5_p6_diffs:
        avg_recent_gap = sum(p5_p6_diffs[:10]) / min(10, len(p5_p6_diffs))
        # If recent gaps are small, boost consecutive high numbers
        if avg_recent_gap <= 4:
            for base in [37, 38, 39, 40, 41]:
                scores[base]["score"] += 4
                scores[base + 1]["score"] += 4 if base + 1 <= 42 else 0
                scores[base]["reasons"].append(f"💃 P5-P6 tight gap trend: {avg_recent_gap:.1f}")
    
    # === 46. P1P2 DATE CODE + P3 PREDICTOR (43.3% hit rate!) ===
    # When P1-P2 forms a date pattern (matches day/month or ends in year),
    # P3 from that draw predicts numbers in the next draw!
    
    if last_draw:
        last_nums = sorted(last_draw.get('numbers', []))
        if len(last_nums) >= 6:
            last_p1, last_p2, last_p3 = last_nums[0], last_nums[1], last_nums[2]
            last_date = last_draw.get('date', '')
            
            # Check if last draw's P1P2 matched a date pattern
            is_date_pattern = False
            
            if len(last_date) >= 10:
                try:
                    last_month = int(last_date[5:7])
                    last_day = int(last_date[8:10])
                    last_year = last_date[2:4]  # e.g., "25" for 2025
                    
                    p1p2_str = f"{last_p1:02d}{last_p2:02d}"
                    
                    # Pattern checks
                    if last_p1 == last_day or last_p2 == last_month:
                        is_date_pattern = True
                    if last_p1 == last_month or last_p2 == last_day:
                        is_date_pattern = True
                    if p1p2_str[-2:] == last_year:
                        is_date_pattern = True
                except:
                    pass
            
            if is_date_pattern:
                # P3 and its derivatives are hot! (43.3% hit rate)
                p3_digit = last_p3 % 10
                p3_derived = [last_p3]
                for tens in [0, 10, 20, 30, 40]:
                    val = p3_digit + tens
                    if 1 <= val <= 42:
                        p3_derived.append(val)
                
                for num in set(p3_derived):
                    boost = 15 if num == last_p3 else 10
                    scores[num]["score"] += boost
                    scores[num]["reasons"].append(f"🔢 P1P2 date code: P3={last_p3} predicts {num} (43.3%)")
    
    # === 47. DECADE CLUSTER PATTERN (44-54% hit rate!) ===
    # When 3+ numbers from same decade appear, that decade continues next draw
    # 30-39 is BEST: 54% continuation!
    
    if last_draw:
        last_nums = last_draw.get('numbers', [])
        decade_counts = {}
        for n in last_nums:
            decade = n // 10  # 0=1-9, 1=10-19, 2=20-29, 3=30-39, 4=40-42
            decade_counts[decade] = decade_counts.get(decade, 0) + 1
        
        for decade, count in decade_counts.items():
            if count >= 3:
                # This decade is clustering! Boost numbers in same decade
                boost = 18 if decade == 3 else 14  # 30s are strongest
                decade_start = decade * 10 if decade > 0 else 1
                decade_end = min((decade + 1) * 10 - 1, 42)
                
                for num in range(decade_start, decade_end + 1):
                    if 1 <= num <= 42:
                        scores[num]["score"] += boost
                        scores[num]["reasons"].append(f"🎯 Decade cluster: {count}x in {decade*10}s → continues (54%)")
            elif count == 2:
                # Weaker cluster, still boost slightly
                decade_start = decade * 10 if decade > 0 else 1
                decade_end = min((decade + 1) * 10 - 1, 42)
                for num in range(decade_start, decade_end + 1):
                    if 1 <= num <= 42:
                        scores[num]["score"] += 5
                        scores[num]["reasons"].append(f"🎯 Decade pair: 2x in {decade*10}s")
    
    # === 48. P1+P6 MAGIC SUM PATTERN (up to 54%!) ===
    # The sum of smallest + largest predicts next draw
    # Best sums: 53 (54%), 42 (35%), 48 (35%)
    
    if last_draw:
        last_nums = sorted(last_draw.get('numbers', []))
        if len(last_nums) >= 6:
            p1, p6 = last_nums[0], last_nums[5]
            magic_sum = p1 + p6
            
            # Boost based on magic sum
            boost_map = {53: 18, 42: 14, 48: 14, 43: 12, 44: 12, 47: 12, 49: 12}
            base_boost = boost_map.get(magic_sum, 8)
            
            # The magic sum itself (if valid)
            if 1 <= magic_sum <= 42:
                scores[magic_sum]["score"] += base_boost
                scores[magic_sum]["reasons"].append(f"✨ P1+P6 magic sum: {p1}+{p6}={magic_sum}")
            
            # Digits of magic sum
            for d in str(magic_sum):
                if d != '0':
                    digit = int(d)
                    for tens in [0, 10, 20, 30, 40]:
                        val = digit + tens
                        if 1 <= val <= 42:
                            scores[val]["score"] += base_boost // 2
                            scores[val]["reasons"].append(f"✨ Magic sum digit: {magic_sum}→{d}")
    
    # === 49. DIGIT ECHO PATTERN (85-89%!) ===
    # Digits 1, 2, 3 echo strongly across draws
    # If last draw has digit X, next draw likely has numbers with digit X
    
    if last_draw:
        last_nums = last_draw.get('numbers', [])
        last_digits = set()
        for n in last_nums:
            for d in str(n):
                if d != '0':
                    last_digits.add(int(d))
        
        # Boost numbers containing echoing digits
        # Digits 1, 2, 3 echo strongest (85-87%)
        for digit in last_digits:
            if digit in [1, 2, 3]:
                boost = 12  # Strong echo
            else:
                boost = 6   # Weaker echo
            
            # Find all numbers containing this digit
            for num in range(1, 43):
                if str(digit) in str(num):
                    scores[num]["score"] += boost
                    scores[num]["reasons"].append(f"🔊 Digit echo: {digit} repeats ({87 if digit <= 3 else 50}%)")
    
    # === 50. REPLAY PREDICTOR PATTERN (up to 50%!) ===
    # The replay number predicts next draw
    # Replay 4 → 50%, Replay 6 → 46%, Replay 8 → 45%
    
    if last_draw:
        replay = last_draw.get('replay_number')
        if replay and 1 <= replay <= 42:
            # Best replay numbers
            replay_boost = {4: 16, 6: 14, 8: 14, 3: 12, 5: 12, 10: 12, 12: 12}
            boost = replay_boost.get(replay, 8)
            
            # Boost the replay number itself
            scores[replay]["score"] += boost
            scores[replay]["reasons"].append(f"🔄 Replay predictor: {replay} (up to 50%)")
            
            # Boost replay ± 1
            for offset in [-1, 1]:
                val = replay + offset
                if 1 <= val <= 42:
                    scores[val]["score"] += boost // 2
                    scores[val]["reasons"].append(f"🔄 Near replay: {replay}±1")
            
            # Boost replay family
            replay_digit = replay % 10
            for tens in [0, 10, 20, 30, 40]:
                val = replay_digit + tens
                if 1 <= val <= 42 and val != replay:
                    scores[val]["score"] += boost // 2
                    scores[val]["reasons"].append(f"🔄 Replay family: {replay}→{val}")
    
    # === 51. P4 > 33 SIGNAL PATTERN ===
    # P4 > 33 is rare (10.3%) but when it happens:
    # - P6 = 42: 41% (vs normal 11%) - 3.6x more likely!
    # - P5 = 37-41 dominates
    # Signal: Many 30s in previous draws (47%) or P1 very low (35%)
    
    if last_draw:
        last_nums = sorted(last_draw.get('numbers', []))
        if len(last_nums) >= 6:
            last_p1 = last_nums[0]
            last_p4 = last_nums[3]
            
            # Count 30s in last draw
            count_30s = sum(1 for n in last_nums if 30 <= n <= 39)
            
            # Signal 1: Previous P1 was very low (1-3) → P4 > 33 likely
            if last_p1 <= 3:
                # Boost high P4-P5-P6 numbers
                for num in range(34, 43):
                    scores[num]["score"] += 10
                    scores[num]["reasons"].append(f"📈 P4>33 signal: P1={last_p1} low → high numbers coming")
            
            # Signal 2: Many 30s in last draw → more 30s/40s coming
            if count_30s >= 2:
                for num in range(35, 43):
                    scores[num]["score"] += count_30s * 4
                    scores[num]["reasons"].append(f"📈 30s cluster ({count_30s}x) → 35-42 hot")
            
            # Signal 3: If P4 was > 33, P6=42 is 41% likely!
            if last_p4 > 33:
                scores[42]["score"] += 15
                scores[42]["reasons"].append(f"📈 P4>33 ({last_p4}) → P6=42 is 41%!")
                scores[41]["score"] += 10
                scores[40]["score"] += 10
                scores[41]["reasons"].append(f"📈 P4>33 → high P6 expected")
                scores[40]["reasons"].append(f"📈 P4>33 → high P6 expected")
    
    # === 52. MAGIC NUMBER PATTERN (17 & 38 - EuroMillions Bridge) ===
    # When 17 or 38 appears in a draw, it's a "magic trigger"
    # 17 + 21 = 38 (Circle partners) - the MAGIC PAIR
    # 21 in Swiss = 71 in EuroMillions thinking → digits 7,1 = 17
    # After 17 appears: digit 1 and 7 often appear next
    # After 38 appears: digit 3 and 8 often appear next
    # Magic + 21 together = TRIPLE CONNECTION (strongest signal!)
    
    if last_draw:
        last_nums = last_draw.get('numbers', [])
        has_17 = 17 in last_nums
        has_38 = 38 in last_nums
        has_21 = 21 in last_nums
        
        if has_17 or has_38:
            # Magic trigger activated!
            magic_type = "17+38" if (has_17 and has_38) else ("17" if has_17 else "38")
            
            if has_17 and has_38:
                # DOUBLE MAGIC - both circle partners appeared!
                # This is very rare - boost their digit echoes strongly
                scores[1]["score"] += 20
                scores[7]["score"] += 20
                scores[3]["score"] += 20
                scores[8]["score"] += 20
                scores[1]["reasons"].append(f"✨✨ Double Magic 17+38! Digit 1 echo")
                scores[7]["reasons"].append(f"✨✨ Double Magic 17+38! Digit 7 echo")
                scores[3]["reasons"].append(f"✨✨ Double Magic 17+38! Digit 3 echo")
                scores[8]["reasons"].append(f"✨✨ Double Magic 17+38! Digit 8 echo")
                
                # Also boost 17 and 38 family numbers
                for n in [11, 21, 31, 41, 27, 37]:  # 7-family and 1-family
                    if 1 <= n <= 42:
                        scores[n]["score"] += 12
                        scores[n]["reasons"].append(f"✨✨ Double Magic: 17 family")
                for n in [13, 23, 33, 18, 28]:  # 3-family and 8-family
                    if 1 <= n <= 42:
                        scores[n]["score"] += 12
                        scores[n]["reasons"].append(f"✨✨ Double Magic: 38 family")
            
            elif has_17:
                # Magic 17 - boost digit echoes
                scores[1]["score"] += 15
                scores[7]["score"] += 15
                scores[17]["score"] += 10  # 17 might repeat
                scores[1]["reasons"].append(f"✨ Magic 17! Digit 1 echo")
                scores[7]["reasons"].append(f"✨ Magic 17! Digit 7 echo")
                scores[17]["reasons"].append(f"✨ Magic 17 might repeat")
                
                # 17's circle partner 38 is now activated
                scores[38]["score"] += 12
                scores[38]["reasons"].append(f"✨ Magic 17 → Circle 38 activated")
            
            elif has_38:
                # Magic 38 - boost digit echoes
                scores[3]["score"] += 15
                scores[8]["score"] += 15
                scores[38]["score"] += 10  # 38 might repeat
                scores[3]["reasons"].append(f"✨ Magic 38! Digit 3 echo")
                scores[8]["reasons"].append(f"✨ Magic 38! Digit 8 echo")
                scores[38]["reasons"].append(f"✨ Magic 38 might repeat")
                
                # 38's circle partner 17 is now activated
                scores[17]["score"] += 12
                scores[17]["reasons"].append(f"✨ Magic 38 → Circle 17 activated")
            
            # TRIPLE CONNECTION: Magic + 21 together!
            if has_21 and (has_17 or has_38):
                # 21 = 71 in Euro thinking = digits 17!
                # This is the BRIDGE between Swiss and EuroMillions
                scores[21]["score"] += 18
                scores[21]["reasons"].append(f"✨✨✨ TRIPLE: Magic + 21 (Euro bridge)")
                
                # 21's connections get boost
                scores[12]["score"] += 15  # 21 reversed = 12
                scores[12]["reasons"].append(f"✨✨✨ TRIPLE: 21↔12 flip active")
                
                # Circle partners of 21
                scores[42]["score"] += 12  # 21 + 21 = 42
                scores[42]["reasons"].append(f"✨✨✨ TRIPLE: 21 circle to 42")
            
            # ESSENCE PREDICTION when magic appears
            # Most common essences: E=9 (6x), E=8 (5x), E=10 (4x)
            # Boost numbers that create these essences
            magic_essences = [9, 8, 10]
            for target_e in magic_essences:
                # Numbers whose digit sum = target essence
                for n in range(1, 43):
                    if sum(int(d) for d in str(n)) == target_e:
                        scores[n]["score"] += 6
                        scores[n]["reasons"].append(f"✨ Magic essence E={target_e}")
    
    # Check for 12↔21 reversal pattern (the BRIDGE)
    # This reversal appeared multiple times with magic numbers
    if last_draw:
        last_nums = last_draw.get('numbers', [])
        if 12 in last_nums and 21 in last_nums:
            # The reversal pair is present - strong magic signal!
            scores[17]["score"] += 15
            scores[38]["score"] += 15
            scores[17]["reasons"].append(f"🔮 12↔21 reversal → Magic 17 likely")
            scores[38]["reasons"].append(f"🔮 12↔21 reversal → Magic 38 likely")
        elif 12 in last_nums:
            scores[21]["score"] += 12
            scores[21]["reasons"].append(f"🔮 12 present → 21 reversal likely")
        elif 21 in last_nums:
            scores[12]["score"] += 12
            scores[12]["reasons"].append(f"🔮 21 present → 12 reversal likely")
    
    # === 53. SHADOW NUMBER STRATEGY (Missing 9 Pattern) ===
    # When a number is "missing" (avoided), boost its echoes instead:
    # - Circle partner (+/- 21)
    # - Multiples (×2, ×3, ×4)
    # - Digit sum family
    # - Neighborhood (±1)
    # This is the "Shadow 9" strategy from our analysis
    
    def get_shadow_echoes(n):
        """Get all echo numbers for a 'shadow' number we're avoiding"""
        echoes = set()
        # Circle partner
        circle = n + 21 if n + 21 <= 42 else n - 21 if n - 21 >= 1 else None
        if circle and 1 <= circle <= 42:
            echoes.add((circle, f"circle {n}↔{circle}"))
        # Multiples
        for mult in [2, 3, 4]:
            if 1 <= n * mult <= 42:
                echoes.add((n * mult, f"×{mult}={n*mult}"))
        # Digit sum family (numbers with same essence)
        essence = sum(int(d) for d in str(n))
        for x in range(1, 43):
            if sum(int(d) for d in str(x)) == essence and x != n:
                echoes.add((x, f"essence={essence}"))
        # Neighborhood
        if 1 <= n - 1 <= 42:
            echoes.add((n - 1, f"neighbor-"))
        if 1 <= n + 1 <= 42:
            echoes.add((n + 1, f"neighbor+"))
        return echoes
    
    # Check for "shadow" numbers - numbers that are overdue but we invoke via echoes
    shadow_numbers = []
    for num in range(1, 43):
        gap = num_last_seen.get(num, 100)
        if gap >= 20:  # Missing for 20+ draws = potential shadow
            shadow_numbers.append((num, gap))
    
    # Boost shadows' echoes (especially 9 if missing long)
    for shadow_num, gap in sorted(shadow_numbers, key=lambda x: x[1], reverse=True)[:3]:
        echoes = get_shadow_echoes(shadow_num)
        boost = min(20, gap // 3)
        for echo_num, echo_type in echoes:
            if echo_num != shadow_num:  # Don't boost the shadow itself
                scores[echo_num]["score"] += boost
                scores[echo_num]["reasons"].append(f"👻 Shadow {shadow_num} ({gap} gap): {echo_type}")
    
    # === 54. P6 MOMENTUM TRACKING ===
    # When the same number appears at P6 (highest position) multiple times recently,
    # it has "momentum" - either continue riding it or transform to its circle
    
    p6_counter = Counter()
    for d in all_draws_sorted[:20]:  # Last 20 draws
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 6:
            p6_counter[nums[5]] += 1  # P6 = index 5
    
    # Find P6 with momentum (appeared 2+ times in last 20)
    p6_momentum = [(num, count) for num, count in p6_counter.items() if count >= 2]
    
    for p6_num, count in p6_momentum:
        # Boost the momentum number - INSERT AT FRONT for visibility
        boost = count * 12  # Increased from count * 8
        scores[p6_num]["score"] += boost
        scores[p6_num]["reasons"].insert(0, f"🎯 P6 MOMENTUM: {p6_num} hit {count}x at P6 ({boost}%)")
        
        # Also boost its circle partner (transformation option)
        p6_circle = p6_num + 21 if p6_num + 21 <= 42 else p6_num - 21 if p6_num - 21 >= 1 else None
        if p6_circle and 1 <= p6_circle <= 42:
            circle_boost = count * 10  # Increased from count * 6
            scores[p6_circle]["score"] += circle_boost
            scores[p6_circle]["reasons"].insert(0, f"🌀 P6 CIRCLE: {p6_num}↔{p6_circle} ({circle_boost}%)")
    
    # === 55. AIR PATTERN (P1+P2 Sum Analysis) ===
    # When P1+P2 from recent draws sums to a specific value (like 20),
    # boost that "Air" number and its family
    # Air family: the sum, its factors, its circle, numbers that create it
    
    p1p2_sums = []
    for d in all_draws_sorted[:10]:  # Last 10 draws
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 2:
            p1p2_sums.append(nums[0] + nums[1])
    
    # Find recurring P1+P2 sums
    sum_counter = Counter(p1p2_sums)
    air_numbers = [(s, c) for s, c in sum_counter.items() if c >= 2 and 1 <= s <= 42]
    
    for air_sum, count in air_numbers:
        # Boost the Air number itself
        scores[air_sum]["score"] += count * 10
        scores[air_sum]["reasons"].append(f"💨 AIR: P1+P2={air_sum} appeared {count}x")
        
        # Air circle
        air_circle = air_sum + 21 if air_sum + 21 <= 42 else air_sum - 21 if air_sum - 21 >= 1 else None
        if air_circle and 1 <= air_circle <= 42:
            scores[air_circle]["score"] += count * 8
            scores[air_circle]["reasons"].append(f"💨 AIR circle: {air_sum}↔{air_circle}")
        
        # Numbers that sum to Air (P1+P2 candidates)
        for a in range(1, min(air_sum, 22)):
            b = air_sum - a
            if 1 <= b <= 42 and a < b:
                scores[a]["score"] += 4
                scores[b]["score"] += 4
                scores[a]["reasons"].append(f"💨 AIR pair: {a}+{b}={air_sum}")
                scores[b]["reasons"].append(f"💨 AIR pair: {a}+{b}={air_sum}")
    
    # === 56. POSITION ANCHORS (Quarterly Repeat Detection) ===
    # Detect numbers that repeat at specific positions in recent draws
    # These become "anchors" with high confidence
    
    # Track position frequencies for P3, P4, P5, P6 in last quarter (~27 draws)
    quarter_draws = all_draws_sorted[-27:] if len(all_draws_sorted) >= 27 else all_draws_sorted
    
    position_counters = {
        3: Counter(),  # P3
        4: Counter(),  # P4
        5: Counter(),  # P5
        6: Counter(),  # P6
    }
    
    for d in quarter_draws:
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 6:
            position_counters[3][nums[2]] += 1
            position_counters[4][nums[3]] += 1
            position_counters[5][nums[4]] += 1
            position_counters[6][nums[5]] += 1
    
    # Find position anchors (appeared 3+ times at same position)
    position_names = {3: "P3", 4: "P4", 5: "P5", 6: "P6"}
    for pos, counter in position_counters.items():
        anchors = [(num, count) for num, count in counter.items() if count >= 3]
        for anchor_num, count in anchors:
            boost = count * 6
            scores[anchor_num]["score"] += boost
            scores[anchor_num]["reasons"].append(f"⚓ {position_names[pos]} anchor: {anchor_num} hit {count}x")
    
    # === 57. CIRCLE TRANSFORMATION STRATEGY ===
    # For top scoring numbers, also boost their circle partners
    # This creates the "RIDE vs SWAP" strategy options
    
    # Get current top 10 candidates
    temp_ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)[:10]
    
    for num, data in temp_ranked:
        if data["score"] >= 50:  # Only for strong candidates
            circle = num + 21 if num + 21 <= 42 else num - 21 if num - 21 >= 1 else None
            if circle and 1 <= circle <= 42:
                # Add smaller boost to circle (transformation option)
                circle_boost = min(15, data["score"] // 5)
                scores[circle]["score"] += circle_boost
                scores[circle]["reasons"].append(f"🔄 Circle of hot {num}: {num}↔{circle}")
    
    # === 58. DATE ESSENCE DOUBLING ===
    # When date digits repeat (like 4/4), that essence is DOUBLED in power
    # Boost that number and its entire family heavily
    # INSERT AT BEGINNING of reasons list for visibility!
    
    today = datetime.now()
    if today.day == today.month:  # Same day and month!
        double_essence = today.day
        
        # Heavy boost to the doubled number - INSERT AT FRONT
        if 1 <= double_essence <= 42:
            scores[double_essence]["score"] += 50  # Increased from 25
            scores[double_essence]["reasons"].insert(0, f"✨✨ DATE DOUBLE: {double_essence}/{double_essence}! (50%)")
        
        # Boost circle partner - INSERT AT FRONT
        double_circle = double_essence + 21 if double_essence + 21 <= 42 else double_essence - 21
        if 1 <= double_circle <= 42:
            scores[double_circle]["score"] += 40  # Increased from 20
            scores[double_circle]["reasons"].insert(0, f"✨✨ DATE DOUBLE circle: {double_essence}↔{double_circle} (40%)")
        
        # Boost family (numbers ending in that digit) - INSERT AT FRONT
        for n in range(double_essence + 10, 43, 10):
            scores[n]["score"] += 20  # Increased from 12
            scores[n]["reasons"].insert(0, f"✨ DATE family: ends in {double_essence} (20%)")
    
    # === 59. COMBINED D PATTERN (72.1% hit rate!) ===
    # The "D" (Day) from draw dates combined with previous draw positions
    # creates high-probability number predictions:
    # - D (target day) + P1 from previous draw
    # - D (target day) + P2 from previous draw
    # - D(-1) + D(-2) (sum of days from last two draws)
    # - D + M (day + month of target draw)
    # This pattern shows 72.1% connection rate across 1374 Swiss Lotto draws!
    
    if most_recent and len(all_draws_sorted) >= 2:
        # Get previous draws data
        prev_draw_1 = all_draws_sorted[0]  # Most recent
        prev_draw_2 = all_draws_sorted[1] if len(all_draws_sorted) >= 2 else None
        
        # Extract day numbers from previous draws
        def get_day_from_date(date_str):
            """Extract day number from YYYY-MM-DD format"""
            try:
                parts = date_str.split('-')
                if len(parts) == 3:
                    return int(parts[2])
            except:
                pass
            return None
        
        prev_day_1 = get_day_from_date(prev_draw_1.get('date', ''))
        prev_day_2 = get_day_from_date(prev_draw_2.get('date', '')) if prev_draw_2 else None
        
        # Get P1 and P2 from most recent draw
        prev_nums = sorted(prev_draw_1.get('numbers', []))
        prev_p1 = prev_nums[0] if len(prev_nums) >= 1 else None
        prev_p2 = prev_nums[1] if len(prev_nums) >= 2 else None
        
        # Today's date for target predictions
        target_day = today.day
        target_month = today.month
        
        # Pattern 59a: D (target) + P1 (previous) - STRONGEST
        if prev_p1 and target_day:
            d_plus_p1 = target_day + prev_p1
            if 1 <= d_plus_p1 <= 42:
                scores[d_plus_p1]["score"] += 25
                scores[d_plus_p1]["reasons"].insert(0, f"🔷 D+P1: {target_day}+{prev_p1}={d_plus_p1} (72%!)")
            elif d_plus_p1 > 42:
                # Reduce to valid range
                reduced = d_plus_p1 - 42
                if 1 <= reduced <= 42:
                    scores[reduced]["score"] += 18
                    scores[reduced]["reasons"].insert(0, f"🔷 D+P1 reduced: {d_plus_p1}→{reduced}")
        
        # Pattern 59b: D (target) + P2 (previous)
        if prev_p2 and target_day:
            d_plus_p2 = target_day + prev_p2
            if 1 <= d_plus_p2 <= 42:
                scores[d_plus_p2]["score"] += 22
                scores[d_plus_p2]["reasons"].insert(0, f"🔷 D+P2: {target_day}+{prev_p2}={d_plus_p2} (72%!)")
            elif d_plus_p2 > 42:
                reduced = d_plus_p2 - 42
                if 1 <= reduced <= 42:
                    scores[reduced]["score"] += 15
                    scores[reduced]["reasons"].insert(0, f"🔷 D+P2 reduced: {d_plus_p2}→{reduced}")
        
        # Pattern 59c: D(-1) + D(-2) (sum of days from last two draws)
        if prev_day_1 and prev_day_2:
            d_sum = prev_day_1 + prev_day_2
            if 1 <= d_sum <= 42:
                scores[d_sum]["score"] += 20
                scores[d_sum]["reasons"].insert(0, f"🔷 D(-1)+D(-2): {prev_day_1}+{prev_day_2}={d_sum} (72%!)")
            elif d_sum > 42:
                reduced = d_sum - 42
                if 1 <= reduced <= 42:
                    scores[reduced]["score"] += 14
                    scores[reduced]["reasons"].insert(0, f"🔷 D(-1)+D(-2) reduced: {d_sum}→{reduced}")
        
        # Pattern 59d: D + M (target day + month)
        d_plus_m = target_day + target_month
        if 1 <= d_plus_m <= 42:
            scores[d_plus_m]["score"] += 18
            scores[d_plus_m]["reasons"].insert(0, f"🔷 D+M: {target_day}+{target_month}={d_plus_m}")
        
        # Pattern 59e: Previous D + P1 from -2 draw (chain pattern)
        if prev_day_1 and prev_draw_2:
            prev_2_nums = sorted(prev_draw_2.get('numbers', []))
            if len(prev_2_nums) >= 1:
                prev_2_p1 = prev_2_nums[0]
                chain_val = prev_day_1 + prev_2_p1
                if 1 <= chain_val <= 42:
                    scores[chain_val]["score"] += 16
                    scores[chain_val]["reasons"].insert(0, f"🔷 D(-1)+P1(-2): {prev_day_1}+{prev_2_p1}={chain_val}")
        
        # Pattern 59f: Circle partners of D patterns (transformation)
        for d_pattern_num in [d_plus_p1 if prev_p1 else 0, d_plus_p2 if prev_p2 else 0]:
            if d_pattern_num and 1 <= d_pattern_num <= 42:
                d_circle = d_pattern_num + 21 if d_pattern_num + 21 <= 42 else d_pattern_num - 21 if d_pattern_num - 21 >= 1 else None
                if d_circle and 1 <= d_circle <= 42:
                    scores[d_circle]["score"] += 12
                    scores[d_circle]["reasons"].append(f"🔷 D-circle: {d_pattern_num}↔{d_circle}")
    
    # === 60. STORY SIGNS PATTERN (Pattern 60 - The Ultimate!) ===
    # Analyzes circles, hunger, consecutive sequences, P1+P2 sums,
    # secret counting, family tracking, position memory, and date codes
    # This pattern discovered:
    # - 07/02/2026: 4 consecutive numbers (35-36-37-38) AND 4 consecutive circles (14-15-16-17)!
    # - Circle warming: When circle appears at position multiple times, actual number comes next
    # - Hunger pattern: Neighbors appear without the number = number is coming
    # - Secret counting: value + gap = next value at same position
    # - Mirror to 42: last_P4 + next_P4 often = 42
    
    try:
        # Analyze story signs from all draws
        story_result = analyze_story_signs(draws, quarter_size=27)
        
        if story_result and story_result.get("scores"):
            for num, data in story_result["scores"].items():
                if 1 <= num <= 42 and data.get("score", 0) > 0:
                    # Apply story sign scores (capped at 30 to balance with other patterns)
                    story_bonus = min(data["score"], 30)
                    scores[num]["score"] += story_bonus
                    # Add reasons (max 3 to avoid clutter)
                    for reason in data.get("reasons", [])[:3]:
                        scores[num]["reasons"].append(reason)
        
        # Log rare events if found
        if story_result.get("rare_events"):
            for event in story_result["rare_events"]:
                logging.info(f"Story Pattern - Rare Event: {event}")
                
    except Exception as e:
        logging.warning(f"Pattern 60 Story Signs error: {e}")
    
    # === 61. STORY NUMBERS MEGA BOOST (THE AVI PATTERNS!) ===
    # These are the numbers discovered through deep numerology analysis:
    # - 13 Family: Mr. 13 the hero, escaped from Replay Jail
    # - 26 Family: The connector number, circle partner of 5
    # - 18-39 Circle: The reunion couple, gap of 21
    # - 33-12 Tragic Love: 30 draws apart, waiting for reunion
    # - 7 Ladder: 7, 14, 21, 28, 35, 42 - the complete ladder
    
    # === 13 FAMILY - MR. 13 THE HERO ===
    FAMILY_13 = [10, 13, 14, 15, 21, 23, 31, 34]
    for num in FAMILY_13:
        scores[num]["score"] += 25
        scores[num]["reasons"].append(f"🦸 13 FAMILY: Mr. 13's crew")
    scores[13]["score"] += 35  # Extra boost for the hero himself
    scores[13]["reasons"].append("🦸 MR. 13: The HERO!")
    
    # === 26 FAMILY - THE CONNECTOR ===
    FAMILY_26 = [5, 13, 26, 27, 30, 31, 38]  # From the 42 tickets
    for num in FAMILY_26:
        scores[num]["score"] += 25
        scores[num]["reasons"].append(f"👨‍👩‍👧‍👦 26 FAMILY: The connector")
    scores[26]["score"] += 35  # Extra for 26 itself
    scores[26]["reasons"].append("👨‍👩‍👧‍👦 26: Family head (circle=5)")
    scores[5]["score"] += 20  # Circle partner
    scores[5]["reasons"].append("⭕ 26↔5: Circle reunion")
    
    # === 18-39 CIRCLE PARTNERSHIP ===
    scores[18]["score"] += 40
    scores[18]["reasons"].append("💑 18-39 CIRCLE: Reunion at P3!")
    scores[39]["score"] += 40
    scores[39]["reasons"].append("💑 18-39 CIRCLE: Reunion at P6!")
    # Common companions
    for num in [32, 11, 25, 4, 42]:
        scores[num]["score"] += 15
        scores[num]["reasons"].append("💑 18-39 companions")
    
    # === 33-12 TRAGIC LOVE STORY ===
    scores[33]["score"] += 35
    scores[33]["reasons"].append("💔 33-12 REUNION: Waiting 30 draws!")
    scores[12]["score"] += 35
    scores[12]["reasons"].append("💔 33-12 REUNION: The blocker becomes friend!")
    # Related numbers
    for num in [10, 11, 36, 38]:
        scores[num]["score"] += 12
        scores[num]["reasons"].append("💔 33-12 neighbors")
    
    # === 7 LADDER (P1 + P6 = 42) ===
    SEVEN_LADDER = [7, 14, 21, 28, 35, 42]
    for num in SEVEN_LADDER:
        scores[num]["score"] += 30
        scores[num]["reasons"].append("🪜 7 LADDER: P1+P6=42!")
    
    # === CIRCLE CONSTANT (+/-21) ===
    # Apply circle awareness to hot numbers
    if last_draw:
        for num in last_draw['numbers']:
            circle_up = num + 21 if num + 21 <= 42 else num + 21 - 42
            circle_down = num - 21 if num > 21 else num - 21 + 42
            if 1 <= circle_up <= 42:
                scores[circle_up]["score"] += 15
                scores[circle_up]["reasons"].append(f"⭕ Circle of {num}")
            if 1 <= circle_down <= 42 and circle_down != circle_up:
                scores[circle_down]["score"] += 15
                scores[circle_down]["reasons"].append(f"⭕ Circle of {num}")
    
    # === DATE DANCE BOOST ===
    # D, M, D+M, D-M, D*M often appear
    today = datetime.now()
    d, m = today.day, today.month
    date_numbers = [
        (d, f"📅 Day={d}"),
        (m, f"📅 Month={m}"),
        (d + m, f"📅 D+M={d+m}"),
        (abs(d - m), f"📅 |D-M|={abs(d-m)}"),
        (d * m, f"📅 D×M={d*m}"),
    ]
    for num, reason in date_numbers:
        if 1 <= num <= 42:
            scores[num]["score"] += 20
            scores[num]["reasons"].append(reason)
    
    # === COMPILE FINAL PREDICTIONS ===
    # Filter out locked numbers from candidates
    locked_nums_set = set(locked_positions.values()) if locked_positions else set()
    ranked = sorted(
        [(n, data) for n, data in scores.items() if n not in locked_nums_set],
        key=lambda x: x[1]["score"], 
        reverse=True
    )
    
    # Calculate how many positions we need to fill
    positions_to_fill = 6 - len(locked_positions)
    
    # Add slight randomization to top candidates for variety
    # Take top 15 and randomly select needed positions weighted by score
    top_candidates = ranked[:15]
    if len(top_candidates) >= positions_to_fill:
        weights = [max(1, data["score"]) for n, data in top_candidates]
        selected_indices = set()
        selected = []
        while len(selected) < positions_to_fill and len(selected_indices) < len(top_candidates):
            remaining = [(i, top_candidates[i], weights[i]) for i in range(len(top_candidates)) if i not in selected_indices]
            if not remaining:
                break
            total_weight = sum(w for _, _, w in remaining)
            r = random.random() * total_weight
            cumulative = 0
            for idx, (n, data), w in remaining:
                cumulative += w
                if r <= cumulative:
                    selected.append({"number": n, "score": data["score"], "reasons": data["reasons"][:10]})
                    selected_indices.add(idx)
                    break
        generated_picks = selected
    else:
        generated_picks = [{"number": n, "score": data["score"], "reasons": data["reasons"][:10]} for n, data in ranked[:positions_to_fill]]
    
    # Build final 6-number array respecting locked positions
    # Position 0 = P1 (smallest), Position 5 = P6 (largest)
    final_numbers = [None] * 6
    
    # Place locked numbers first
    for pos_idx, locked_num in locked_positions.items():
        final_numbers[pos_idx] = {
            "number": locked_num, 
            "score": 999,  # Special score for locked
            "reasons": [f"🔒 Locked at P{pos_idx + 1}"],
            "locked": True
        }
    
    # Fill remaining positions with generated picks
    gen_idx = 0
    for i in range(6):
        if final_numbers[i] is None and gen_idx < len(generated_picks):
            pick = generated_picks[gen_idx].copy() if isinstance(generated_picks[gen_idx], dict) else generated_picks[gen_idx]
            if isinstance(pick, dict):
                pick["locked"] = False
            final_numbers[i] = pick
            gen_idx += 1
    
    # Sort the final array by number value (P1 smallest to P6 largest)
    # with full respect for locked-position constraints (DJ 29.04.2026).
    # Use lock_constraints.assemble_with_locks: locked values pin their slot,
    # unlocked values fill the gaps in strict ascending order.
    if locked_positions:
        from lock_constraints import assemble_with_locks as _assemble
        from lock_constraints import pick_values_for_gaps as _pick_gaps
        positions_to_fill_local = 6 - len(locked_positions)

        # Build score lookup from generated_picks + ranked
        _score_map = {e["number"]: e.get("score", 0) for e in generated_picks}
        for n, data in ranked:
            if n not in _score_map:
                _score_map[n] = data.get("score", 0)

        def _score_fn_first(v: int) -> float:
            return float(_score_map.get(v, 0))

        # Gap-aware pick: each gap gets exactly the right count of values
        # strictly within (gap_lower, gap_upper).
        unlocked_values = _pick_gaps(
            locked_positions, n_slots=6, score_fn=_score_fn_first,
            used=set(), value_min=1, value_max=42,
            randomize=False,
        )
        if unlocked_values is None:
            # Should not happen after is_valid_lock_request, but guard anyway
            unlocked_values = [n for n in range(1, 43)
                               if n not in locked_nums_set][:positions_to_fill_local]

        assembled = _assemble(locked_positions, unlocked_values, n_slots=6)
        if assembled is None:
            # Greedy fallback
            assembled = [None] * 6
            for s, v in locked_positions.items():
                assembled[s] = v
            sorted_unlocked = sorted(unlocked_values)
            j = 0
            for s in range(6):
                if assembled[s] is None and j < len(sorted_unlocked):
                    assembled[s] = sorted_unlocked[j]
                    j += 1

        # Build top_6 with details for each value
        meta_lookup = {e["number"]: e for e in generated_picks}
        top_6 = []
        for s in range(6):
            v = assembled[s]
            if s in locked_positions:
                top_6.append({
                    "number": v, "score": 999,
                    "reasons": [f"🔒 Locked at P{s+1}"],
                    "locked": True,
                })
            else:
                m = meta_lookup.get(v) or {
                    "number": v,
                    "score": _score_map.get(v, 0),
                    "reasons": ["Pattern fill (locked-bound)"],
                }
                top_6.append({**m, "locked": False, "number": v})
    else:
        # No locks → original sorted-by-number flow
        unlocked_entries = [(i, final_numbers[i]) for i in range(6)
                            if final_numbers[i]
                            and not final_numbers[i].get("locked")]
        unlocked_nums = sorted([e[1]["number"] for e in unlocked_entries])
        top_6 = [None] * 6
        unlocked_idx = 0
        for i in range(6):
            if unlocked_idx < len(unlocked_nums):
                num = unlocked_nums[unlocked_idx]
                for entry in generated_picks:
                    if entry["number"] == num:
                        top_6[i] = {**entry, "locked": False}
                        break
                unlocked_idx += 1
        for i in range(6):
            if top_6[i] is None and generated_picks:
                top_6[i] = {**generated_picks[0], "locked": False}
    
    # === GENERATE MULTIPLE TICKETS (if num_tickets > 1) ===
    all_tickets = []
    
    # First ticket is the main prediction (top_6)
    # Build numbers array RESPECTING locked slots (do NOT re-sort if locks!)
    if locked_positions:
        ticket_1_numbers = [t["number"] for t in top_6 if t]
    else:
        ticket_1_numbers = sorted([t["number"] for t in top_6 if t])
    all_tickets.append({
        "ticket_num": 1,
        "numbers": ticket_1_numbers,
        "details": top_6,
        "confidence": sum(t["score"] for t in top_6 if t and not t.get("locked")) / max(1, positions_to_fill)
    })
    
    # Generate additional tickets from remaining candidates
    if num_tickets > 1:
        used_numbers = set(ticket_1_numbers)
        used_numbers.update(locked_nums_set)
        
        # Get all available numbers sorted by score
        available = [(n, data) for n, data in ranked if n not in locked_nums_set]
        
        for ticket_idx in range(2, num_tickets + 1):
            ticket_details = []

            # Place locked numbers (their slot is fixed)
            for pos_idx, locked_num in locked_positions.items():
                ticket_details.append({
                    "pos_idx": pos_idx,
                    "number": locked_num,
                    "score": 999,
                    "reasons": [f"🔒 Locked at P{pos_idx + 1}"],
                    "locked": True
                })

            # GAP-AWARE picking — each gap between locks gets exactly the
            # right number of distinct values from its valid value range.
            score_lookup = {n: data.get("score", 0) for n, data in available}

            def _score_fn(v: int) -> float:
                base = score_lookup.get(v, 0)
                # Slight de-emphasis based on ticket_idx for variety
                return max(1, base - (ticket_idx - 1) * 5)

            from lock_constraints import pick_values_for_gaps
            picked_unlocked = None
            if locked_positions:
                picked_unlocked = pick_values_for_gaps(
                    locked_positions, n_slots=6, score_fn=_score_fn,
                    used=set(), value_min=1, value_max=42,
                    randomize=True, rng=random,
                )
            if picked_unlocked is None:
                # No locks (or rare exhaustion) — fall back to weighted pick
                positions_to_fill_local = 6 - len(locked_positions)
                pool = [(n, d) for n, d in available
                        if n not in locked_nums_set]
                picks_so_far_pairs = []
                while (len(picks_so_far_pairs) < positions_to_fill_local
                       and pool):
                    weights = [max(1, d.get("score", 0) - (ticket_idx - 1) * 5)
                               for n, d in pool]
                    total_weight = sum(weights)
                    if total_weight <= 0:
                        n, data = pool[0]
                    else:
                        r = random.random() * total_weight
                        cumulative = 0
                        n, data = pool[0]
                        for (nn, dd), w in zip(pool, weights):
                            cumulative += w
                            if r <= cumulative:
                                n, data = nn, dd
                                break
                    picks_so_far_pairs.append((n, data))
                    pool = [(nn, dd) for nn, dd in pool if nn != n]
                picked_unlocked = sorted(n for n, _ in picks_so_far_pairs)

            # Assemble using lock_constraints
            assembled = assemble_with_locks(
                locked_positions, picked_unlocked, n_slots=6,
            ) if locked_positions else sorted(picked_unlocked)

            if assembled is None:
                # Greedy fallback: place locked, sort unlocked into gaps
                assembled = [None] * 6
                for s, v in locked_positions.items():
                    assembled[s] = v
                sorted_unlocked = sorted(picked_unlocked)
                j = 0
                for s in range(6):
                    if assembled[s] is None and j < len(sorted_unlocked):
                        assembled[s] = sorted_unlocked[j]
                        j += 1

            # Build final ticket details with correct ordering
            details_by_value = {n: {"score": score_lookup.get(n, 0),
                                    "reasons": next(
                                        (d.get("reasons", []) for nn, d in available
                                         if nn == n), [])}
                                for n in (picked_unlocked or [])}
            full_details = []
            for s in range(6):
                v = assembled[s]
                if v is None:
                    continue
                if s in locked_positions:
                    full_details.append({
                        "number": v, "score": 999,
                        "reasons": [f"🔒 Locked at P{s+1}"],
                        "locked": True,
                    })
                else:
                    d = details_by_value.get(v, {"score": 0, "reasons": []})
                    full_details.append({
                        "number": v,
                        "score": d.get("score", 0),
                        "reasons": d.get("reasons", [])[:3],
                        "locked": False,
                    })

            # Numbers in final SLOT order (NOT re-sorted when locks present)
            final_numbers_ordered = [v for v in assembled if v is not None]
            confidence_vals = [d["score"] for d in full_details
                               if not d.get("locked")]
            confidence = (sum(confidence_vals) / max(1, len(confidence_vals))
                          if confidence_vals else 0)

            all_tickets.append({
                "ticket_num": ticket_idx,
                "numbers": final_numbers_ordered,
                "details": full_details,
                "confidence": round(confidence, 1)
            })
    
    alternates = [{"number": n, "score": data["score"], "reasons": data["reasons"][:2]} for n, data in ranked[positions_to_fill:positions_to_fill+6]]
    
    avg_score = sum(t["score"] for t in top_6 if t and not t.get("locked")) / max(1, positions_to_fill) if top_6 else 0
    
    # === PREDICT LUCKY NUMBER (1-6) ===
    # Based on patterns: Story (gaps), P1/P2 of last draw, last Lucky, last Replay, date
    lucky_candidates = []
    
    # STORY PATTERN: Track Lucky number gaps (which ones haven't appeared)
    lucky_history = []
    for d in sorted(draws, key=lambda x: x['date'], reverse=True)[:50]:  # Last 50 draws
        ln = d.get('lucky_number', 0)
        if 1 <= ln <= 6:
            lucky_history.append(ln)
    
    # Find gaps for each Lucky number (1-6)
    lucky_gaps = {}
    for num in range(1, 7):
        try:
            gap = lucky_history.index(num)
        except ValueError:
            gap = 50  # Not found in last 50
        lucky_gaps[num] = gap
    
    # Story: Numbers with bigger gaps are more due!
    print(f"Lucky number gaps: {lucky_gaps}")  # Debug
    for num, gap in lucky_gaps.items():
        if gap >= 8:  # Missing 8+ draws = story building
            score = min(40, 15 + gap * 2)  # Higher gap = higher score
            lucky_candidates.append((num, score, f"📖 Story: missing {gap} draws"))
        elif gap >= 5:
            lucky_candidates.append((num, 12, f"Due: missing {gap} draws"))
    
    if last_draw:
        p1 = last_draw['numbers'][0]
        p2 = last_draw['numbers'][1]
        last_lucky = last_draw.get('lucky_number', 0)
        last_replay = last_draw.get('replay_number', 0)
        
        # P1 if <= 6
        if 1 <= p1 <= 6:
            lucky_candidates.append((p1, 20, "P1 of last draw"))
        
        # P2 if <= 6
        if 1 <= p2 <= 6:
            lucky_candidates.append((p2, 15, "P2 of last draw"))
        
        # Last Lucky - might repeat or move to next
        if 1 <= last_lucky <= 6:
            # Repeat chance
            lucky_candidates.append((last_lucky, 18, "Last Lucky repeat"))
            # Next in sequence (Lucky numbers often follow pattern)
            next_lucky = (last_lucky % 6) + 1
            lucky_candidates.append((next_lucky, 22, f"Lucky sequence: {last_lucky}→{next_lucky}"))
            # Circle pattern: +3 or -3 (half of 6)
            circle_lucky = ((last_lucky + 2) % 6) + 1  # +3 mod 6
            lucky_candidates.append((circle_lucky, 12, f"Lucky circle: {last_lucky}→{circle_lucky}"))
        
        # Last Replay if <= 6
        if 1 <= last_replay <= 6:
            lucky_candidates.append((last_replay, 15, "Last Replay"))
        
        # Digit connections from main numbers
        for n in last_draw['numbers'][:3]:  # P1, P2, P3
            digit = n % 10 if n % 10 != 0 else n // 10
            if 1 <= digit <= 6:
                lucky_candidates.append((digit, 8, f"Digit of P{last_draw['numbers'].index(n)+1}"))
    
    # Date-based
    day = datetime.now().day
    month = datetime.now().month
    day_mod = ((day - 1) % 6) + 1  # 1-6
    month_mod = ((month - 1) % 6) + 1  # 1-6
    lucky_candidates.append((day_mod, 8, f"Day {day}→{day_mod}"))
    lucky_candidates.append((month_mod, 6, f"Month {month}→{month_mod}"))
    
    # Weighted random selection for Lucky Number
    if lucky_candidates:
        # Combine scores for same numbers
        combined_scores = {}
        combined_reasons = {}
        for num, weight, reason in lucky_candidates:
            if num not in combined_scores:
                combined_scores[num] = 0
                combined_reasons[num] = []
            combined_scores[num] += weight
            combined_reasons[num].append(reason)
        
        total_weight = sum(combined_scores.values())
        r = random.random() * total_weight
        cumulative = 0
        lucky_prediction = 1
        lucky_reason = "Random"
        
        for num in sorted(combined_scores.keys(), key=lambda x: -combined_scores[x]):
            cumulative += combined_scores[num]
            if r <= cumulative:
                lucky_prediction = num
                lucky_reason = combined_reasons[num][0]  # Primary reason
                break
    else:
        lucky_prediction = random.randint(1, 6)
        lucky_reason = "Random"
    
    result = {
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
        "main_prediction": sorted([t["number"] for t in top_6 if t]),
        "main_prediction_details": top_6,
        "locked_positions": {f"P{k+1}": v for k, v in locked_positions.items()} if locked_positions else None,
        "num_tickets": num_tickets,
        "all_tickets": all_tickets if num_tickets > 1 else None,
        "lucky_prediction": lucky_prediction,
        "lucky_reason": lucky_reason,
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
            "Rare event counts",
            "✨ Magic Number (17/38 EuroMillions Bridge)"
        ],
        "magic_status": {
            "last_draw_magic": (17 in last_draw.get('numbers', []) or 38 in last_draw.get('numbers', [])) if last_draw else False,
            "has_17": 17 in last_draw.get('numbers', []) if last_draw else False,
            "has_38": 38 in last_draw.get('numbers', []) if last_draw else False,
            "has_21": 21 in last_draw.get('numbers', []) if last_draw else False,
            "triple_connection": (21 in last_draw.get('numbers', []) and (17 in last_draw.get('numbers', []) or 38 in last_draw.get('numbers', []))) if last_draw else False
        }
    }
    
    if birthday_info:
        result["birthday_mode"] = {
            "birthday": birthday,
            "parsed": birthday_info,
            "lucky_numbers": list(set([bn["num"] for bn in birthday_numbers]))[:8]
        }
        result["patterns_used"].append("🎂 Birthday mode (25%)")
    
    if name_info:
        result["name_mode"] = {
            "name": name,
            "words": name_info["words"],
            "full_sum": name_info["full_sum"],
            "lucky_numbers": list(set([nn["num"] for nn in name_numbers]))[:8]
        }
        result["patterns_used"].append("🔤 Name mode (20%)")
    
    # === SAVE ALL TICKETS TO PREDICTION HISTORY ===
    tickets_to_save = all_tickets if num_tickets > 1 else [{
        "ticket_num": 1,
        "numbers": sorted([t["number"] for t in top_6 if t]),
        "details": top_6,
        "confidence": round(avg_score, 1)
    }]
    
    for ticket in tickets_to_save:
        # Get top reasons from ticket details
        top_reasons = []
        for detail in ticket.get("details", [])[:3]:
            if detail.get("reasons"):
                top_reasons.append(f"{detail['number']}: {detail['reasons'][0][:50]}")
        
        history_doc = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "lottery_type": "swiss",
            "target_draw_date": None,  # Could be set based on next draw date
            "numbers": ticket["numbers"],
            "lucky_number": lucky_prediction,
            "stars": None,
            "confidence": ticket.get("confidence", 0),
            "top_reasons": top_reasons,
            "actual_numbers": None,
            "actual_lucky": None,
            "actual_stars": None,
            "matches": None,
            "lucky_match": None,
            "stars_matched": None
        }
        await db.prediction_history.insert_one(history_doc)
    
    # === ALSO SAVE TO HIT TRACKER (generations collection) ===
    try:
        from datetime import timedelta
        today = datetime.now()
        # 🎻 DJ-rule (29.04.2026): if today is a draw day and today's draw
        # is NOT yet stored, target today (still-pending). Otherwise nearest
        # future draw day.
        target_date_str = None
        wd = today.weekday()
        if wd in (2, 5):
            today_str = today.strftime("%d.%m.%Y")
            stored_today = await db.draws.find_one(
                {"date": today_str}, {"_id": 1}
            )
            if not stored_today:
                target_date_str = today_str
        if not target_date_str:
            days_until_wed = (2 - wd) % 7 or 7
            days_until_sat = (5 - wd) % 7 or 7
            next_draw = min(days_until_wed, days_until_sat)
            target = today + timedelta(days=next_draw)
            target_date_str = target.strftime("%d.%m.%Y")
        
        tracker_tickets = []
        for ticket in tickets_to_save:
            tracker_tickets.append({
                "numbers": ticket.get("numbers", []),
                "lucky": lucky_prediction,
                "story": "master-predictor",
            })
        
        gen_id = await hit_tracker.save_generation(
            target_date=target_date_str,
            tickets=tracker_tickets,
            generation_type="master-predictor",
            visitor_id=visitor_id,
            has_locked=bool(locked_positions),
            locked_positions={f"P{k+1}": v for k, v in locked_positions.items()} if locked_positions else {},
        )
        # 🎫 Propagate serials from tracker_tickets back to the response
        for src_t, tracker_t in zip(tickets_to_save, tracker_tickets):
            if isinstance(src_t, dict) and "serial" in tracker_t:
                src_t["serial"] = tracker_t["serial"]
        # Mirror to result['all_tickets'] / result['tickets'] if present
        for key in ("all_tickets", "tickets"):
            for r_t, tr_t in zip(result.get(key, []) or [], tracker_tickets):
                if isinstance(r_t, dict) and "serial" in tr_t:
                    r_t["serial"] = tr_t["serial"]
        result["target_date"] = target_date_str
        # Auto-trigger hit calc if the actual draw is already in the DB
        try:
            await hit_tracker.calculate_hits(gen_id)
        except Exception:
            pass  # actual draw not yet available — recalc later
    except Exception as e:
        logger.warning(f"swiss master-predictor save_to_tracker failed: {e}")
    
    # 🚀 Populate default-param cache for next 60s
    if _no_params:
        import time as _t
        _MASTER_PRED_CACHE["ts"] = _t.time()
        _MASTER_PRED_CACHE["data"] = result
    
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# 💰 SWISS LOTTO MONEY MODE - Focus on 3+ numbers for consistent small wins! 💰
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/money-mode")
async def get_swiss_money_mode(
    num_tickets: int = 2,
    lock_p1: int = None,
    lock_p2: int = None,
    lock_p3: int = None,
    lock_p4: int = None,
    lock_p5: int = None,
    lock_p6: int = None,
    target_date: str = None,
    visitor_id: str = ""
):
    """
    SWISS LOTTO MONEY MODE v2 — Digit DNA + Patterns + Crazy Tickets
    
    Backtested: 40% of 10-ticket sets hit 3+ numbers (2015-2026)
    
    Ticket strategy:
    - T1-T6: DNA + Position Echoes + Circle + Date (core tickets)
    - T7-T8: DNA + Decade Spread (coverage tickets)
    - T9-T10: High-range CRAZY tickets (catch 30+ numbers)
    """
    from datetime import datetime, timedelta
    import random
    from digit_dna import digit_dna_scores, swiss_circle, p123_concat_scores, p123_concat_analysis, family_rhythm_weights, family_rhythm_analysis
    
    # 🕒 Draw-time generator cutoff (Swiss)
    if visitor_id:
        await _assert_generator_open("swiss", visitor_id)
    
    # Ticket limit check
    if visitor_id:
        if not await _is_visitor_unlimited(visitor_id):
            used = await _count_visitor_tickets(visitor_id)
            if used >= TICKET_LIMIT:
                raise HTTPException(status_code=429, detail=f"Ticket limit reached! You've generated {used}/{TICKET_LIMIT} tickets for the next draw.")
            num_tickets = min(num_tickets, TICKET_LIMIT - used)
    
    num_tickets = max(2, min(20, num_tickets))
    
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).to_list(500)
    if not draws:
        return {"error": "No draws available"}
    
    def parse_date_fn(d):
        try:
            return datetime.strptime(d['date'], '%d.%m.%Y')
        except:
            return datetime.min
    draws = sorted(draws, key=parse_date_fn, reverse=True)
    
    last_draw = draws[0] if draws else None
    prev_draw = draws[1] if len(draws) > 1 else None
    prev2_draw = draws[2] if len(draws) > 2 else None
    
    # Determine target date
    today = datetime.now()
    if target_date:
        try:
            target_dt = datetime.strptime(target_date, '%d.%m.%Y')
        except ValueError:
            target_dt = today
    else:
        days_until_wed = (2 - today.weekday()) % 7
        days_until_sat = (5 - today.weekday()) % 7
        if days_until_wed == 0: days_until_wed = 7
        if days_until_sat == 0: days_until_sat = 7
        next_draw_days = min(days_until_wed, days_until_sat)
        target_dt = today + timedelta(days=next_draw_days)
    
    target_date_str = target_dt.strftime("%d.%m.%Y")
    day = target_dt.day
    month = target_dt.month
    
    # Get Digit DNA scores
    last_nums = sorted(last_draw['numbers']) if last_draw else []
    prev_nums_for_p123 = sorted(prev_draw['numbers']) if prev_draw else []
    prev2_nums_for_p123 = sorted(prev2_draw['numbers']) if prev2_draw else []
    dna_scores = digit_dna_scores(target_date_str, last_nums, weighted=True)
    dna_ranked = sorted(dna_scores.items(), key=lambda x: -x[1])
    dna_top15 = [n for n, s in dna_ranked[:15]]
    
    # Get P123 Concat scores (56% at 3+ when 5 unique digits!)
    p123_scores = p123_concat_scores(target_date_str, last_nums, prev_nums_for_p123)
    p123_analysis = p123_concat_analysis(target_date_str, last_nums, prev_nums_for_p123)
    p123_top = [n for n, s in sorted(p123_scores.items(), key=lambda x: -x[1]) if s >= 2]
    
    # Compute Swiss Sleepers (numbers overdue to appear)
    all_swiss_draws = sorted(draws, key=parse_date_fn, reverse=True)
    expected_gap = 42 / 6  # ~7 draws
    last_seen = {}
    for i, d in enumerate(all_swiss_draws):
        for n in d.get('numbers', []):
            if n not in last_seen:
                last_seen[n] = i
    sleeper_data = []
    for n in range(1, 43):
        gap = last_seen.get(n, len(all_swiss_draws))
        ratio = gap / expected_gap
        sleeper_data.append((n, gap, ratio))
    sleeper_data.sort(key=lambda x: -x[2])
    
    # Compute Family Rhythm weights (the bass of the orchestra)
    family_weights = family_rhythm_weights(all_swiss_draws)
    family_analysis = family_rhythm_analysis(all_swiss_draws)
    
    all_tickets = []
    
    for ticket_idx in range(num_tickets):
        candidates = []
        patterns_used = []
        
        # === DIGIT DNA (all tickets) ===
        for n, s in dna_scores.items():
            if s > 0:
                candidates.extend([n] * int(s))
        patterns_used.append(f"🧬 Digit DNA Top: {dna_top15[:8]}")
        
        # === P123 CONCAT PATTERN (56% at 3+ with 5 unique digits!) ===
        for n, s in p123_scores.items():
            if s >= 2:
                candidates.extend([n] * (s * 12))  # Strong boost for multi-pool numbers
            elif s == 1:
                candidates.extend([n] * 6)
        if p123_top:
            patterns_used.append(f"🔢 P123 Concat ({p123_analysis['unique_digit_count']} digits): {p123_top[:8]}")
        
        # === SWISS SLEEPER BOOST (overdue numbers wake up!) ===
        if sleeper_data:
            for n, gap, ratio in sleeper_data:
                if ratio >= 2.0:  # DEEP sleeper (2x+ overdue)
                    candidates.extend([n] * 15)
                elif ratio >= 1.0:  # WAKE zone (due to appear)
                    candidates.extend([n] * 10)
            deep = [n for n, g, r in sleeper_data if r >= 2.0][:5]
            wake = [n for n, g, r in sleeper_data if 1.0 <= r < 2.0][:5]
            if deep:
                patterns_used.append(f"😴 Deep sleepers: {deep}")
            if wake:
                patterns_used.append(f"⏰ Wake zone: {wake}")
        
        # === FAMILY RHYTHM (the bass — weight adjustments) ===
        if family_analysis:
            pred_miss = family_analysis.get('predicted_missing', '')
            pred_gath = family_analysis.get('predicted_gather', '')
            miss_ratio = family_analysis.get('missing_overdue', {}).get(pred_miss, 0)
            gath_ratio = family_analysis.get('gather_overdue', {}).get(pred_gath, 0)
            fam_names = {'S': 'Singles', 'T': 'Teens', 'W': 'Twenties', 'H': 'Thirties+'}
            # Apply family weights to existing candidates
            weighted_candidates = []
            for n in candidates:
                fw = family_weights.get(n, 1.0)
                count = max(1, round(fw))
                weighted_candidates.extend([n] * count)
            candidates = weighted_candidates
            
            parts = []
            if miss_ratio >= 1.0:
                parts.append(f"dim {fam_names.get(pred_miss, pred_miss)} ({miss_ratio:.1f}x)")
            if gath_ratio >= 1.0:
                parts.append(f"boost {fam_names.get(pred_gath, pred_gath)} ({gath_ratio:.1f}x)")
            if parts:
                patterns_used.append(f"🎵 Rhythm: {' | '.join(parts)}")
        
        # === POSITION ECHOES (T1-T8) ===
        if last_draw and ticket_idx < 8:
            last_lucky = last_draw.get('lucky_number')
            for n in last_nums:
                candidates.extend([n] * 12)
                if n > 1: candidates.extend([n - 1] * 7)
                if n < 42: candidates.extend([n + 1] * 7)
            if last_lucky and 1 <= last_lucky <= 42:
                candidates.extend([last_lucky] * 10)
                if last_lucky < 42: candidates.extend([last_lucky + 1] * 5)
            patterns_used.append(f"🔥 Echoes from {last_nums}")
        
        # === CIRCLE MATH ±21 (T1-T8) ===
        if last_draw and ticket_idx < 8:
            circle_hits = []
            for n in last_nums[:3]:
                for c in swiss_circle(n):
                    candidates.extend([c] * 5)
                    circle_hits.append(c)
            if circle_hits:
                patterns_used.append(f"🔄 Circle(±21): {circle_hits[:4]}")
        
        # === TWO-DRAW ECHO (T1-T6) ===
        if prev_draw and ticket_idx < 6:
            prev_nums = sorted(prev_draw['numbers'])
            for n in prev_nums:
                candidates.extend([n] * 5)
        
        # === DATE PATTERNS (all tickets) ===
        dm_sum = day + month
        dm_diff = abs(day - month)
        dm_prod = day * month
        if 1 <= dm_sum <= 42: candidates.extend([dm_sum] * 8)
        if 1 <= dm_diff <= 42 and dm_diff > 0: candidates.extend([dm_diff] * 5)
        if 1 <= day <= 42: candidates.extend([day] * 6)
        if 1 <= dm_prod <= 42: candidates.extend([dm_prod] * 4)
        patterns_used.append(f"📅 Date {target_date_str}: D+M={dm_sum}")
        
        # === DECADE SPREAD (T7-T8) ===
        if ticket_idx in [6, 7]:
            decades = {0: list(range(1, 10)), 1: list(range(10, 20)),
                       2: list(range(20, 30)), 3: list(range(30, 40)), 4: [40, 41, 42]}
            for dec_nums in decades.values():
                for n in dec_nums:
                    candidates.extend([n] * 5)
            patterns_used.append("🎯 Decade spread coverage")
        
        # === CRAZY HIGH-RANGE (T9-T10) ===
        if ticket_idx >= num_tickets - 2 and num_tickets >= 4:
            for n in range(30, 43):
                candidates.extend([n] * 20)
            for n in range(1, 22):
                c = n + 21
                if c <= 42:
                    candidates.extend([c] * 10)
            patterns_used.append("🤪 CRAZY high-range boost (30+)")
        
        # === HIGH-RANGE GUARANTEE (avg 1.9 numbers 30+ per draw, mostly P5-P6) ===
        # Only 1 guaranteed high — frees a slot for stronger DNA/P2 picks
        high_pool = []
        for n, s in dna_scores.items():
            if n >= 30 and s > 0:
                high_pool.extend([n] * int(s * 2))
        if last_draw:
            for n in last_nums:
                if n >= 30:
                    high_pool.extend([n] * 8)
                    if n > 30: high_pool.extend([n - 1] * 4)
                    if n < 42: high_pool.extend([n + 1] * 4)
                for c in swiss_circle(n):
                    if c >= 30:
                        high_pool.extend([c] * 6)
        
        # === P2 PREDICTION (5.3x random! prev_P2 +/- 1) ===
        p2_candidates = []
        if last_draw:
            last_p2 = last_nums[1] if len(last_nums) >= 2 else None
            last_p1 = last_nums[0] if len(last_nums) >= 1 else None
            last_lk = last_draw.get('lucky_number', 0)
            if last_p2:
                for delta in [-1, 0, 1]:
                    v = last_p2 + delta
                    if 1 <= v <= 42:
                        p2_candidates.extend([v] * 15)
                if last_p1 and last_lk:
                    v = last_p1 + last_lk
                    if 1 <= v <= 42:
                        p2_candidates.extend([v] * 8)
                if 1 <= month <= 42:
                    p2_candidates.extend([month] * 5)
            patterns_used.append(f"P2: prev={last_p2} +/-1, P1+L={last_p1}+{last_lk}")
        candidates.extend(p2_candidates)
        
        # === SELECT 6 NUMBERS ===
        selected = []
        used = set()
        
        lock_params = [lock_p1, lock_p2, lock_p3, lock_p4, lock_p5, lock_p6]
        for lock_val in lock_params:
            if lock_val is not None and 1 <= lock_val <= 42:
                used.add(lock_val)
        
        locked_high = sum(1 for lv in lock_params if lv is not None and lv >= 30)
        is_crazy = ticket_idx >= num_tickets - 2 and num_tickets >= 4
        # Crazy tickets: guarantee 3 from 30+ family (31.1% of draws have this!)
        # Normal tickets: guarantee 1 from 30+
        high_target = 3 if is_crazy else 1
        high_needed = max(0, high_target - locked_high)
        high_placed = 0
        
        for pos in range(6):
            if lock_params[pos] is not None and 1 <= lock_params[pos] <= 42:
                selected.append(lock_params[pos])
            elif high_placed < high_needed and pos >= (6 - high_needed):
                # Place high numbers at last positions
                h_pool = [n for n in high_pool if n not in used and 30 <= n <= 42]
                if h_pool:
                    chosen = random.choice(h_pool)
                else:
                    h_available = [n for n in range(30, 43) if n not in used]
                    chosen = random.choice(h_available) if h_available else 30
                selected.append(chosen)
                used.add(chosen)
                high_placed += 1
            else:
                pool = [n for n in candidates if n not in used and 1 <= n <= 42]
                if pool:
                    chosen = random.choice(pool)
                else:
                    available = [n for n in range(1, 43) if n not in used]
                    chosen = random.choice(available) if available else 1
                selected.append(chosen)
                used.add(chosen)
        
        # Lucky number prediction
        lucky_candidates = []
        if last_draw and last_draw.get('lucky_number'):
            l = last_draw['lucky_number']
            lucky_candidates.extend([l] * 5)
            if l > 1: lucky_candidates.extend([l - 1] * 3)
            if l < 6: lucky_candidates.extend([l + 1] * 3)
        lucky_candidates.extend([day % 6 + 1] * 3)
        lucky_prediction = random.choice(lucky_candidates) if lucky_candidates else random.randint(1, 6)
        
        ticket_type = "core"
        if ticket_idx >= num_tickets - 2 and num_tickets >= 4:
            ticket_type = "crazy"
        elif ticket_idx in [6, 7]:
            ticket_type = "spread"
        
        all_tickets.append({
            "ticket_number": ticket_idx + 1,
            "numbers": sorted(selected),
            "lucky_number": lucky_prediction,
            "patterns_used": patterns_used,
            "confidence": 0.75,
            "mode": "money",
            "ticket_type": ticket_type,
            "target": "3+ numbers"
        })
    
    price_per_ticket = 2.50
    total_price = round(len(all_tickets) * price_per_ticket, 2)
    
    # Auto-save to hit tracker
    try:
        tracker_tickets = []
        for t in all_tickets:
            tracker_tickets.append({
                "numbers": t.get("numbers", []),
                "lucky": t.get("lucky_number", 1),
                "story": f"money-mode-v2-{t.get('ticket_type', 'core')}",
            })
        
        await hit_tracker.save_generation(
            target_date=target_date_str,
            tickets=tracker_tickets,
            generation_type="money-mode-v2",
            visitor_id=visitor_id
        )
    except Exception:
        pass
    
    return {
        "mode": "💰 MONEY MODE v2 — Digit DNA Engine",
        "strategy": "DNA + Patterns + Crazy Tickets | Backtested: 40% hit 3+ from 10 tickets",
        "target_date": target_date_str,
        "target_prizes": {
            "3_correct": "~10 CHF",
            "4_correct": "~100 CHF",
            "5_correct": "~1000 CHF"
        },
        "digit_dna": {
            "top_15": dna_top15,
            "top_scores": [(n, round(s, 1)) for n, s in dna_ranked[:10]],
        },
        "p123_concat": {
            "pools": p123_analysis.get("pools", []),
            "unique_digits": p123_analysis.get("combined_digits", []),
            "digit_count": p123_analysis.get("unique_digit_count", 0),
            "numbers_in_all_pools": p123_analysis.get("numbers_in_all", []),
            "numbers_in_2_plus": p123_analysis.get("numbers_in_2_plus", []),
        },
        "sleepers": {
            "deep": [{"number": n, "gap": g, "ratio": round(r, 1)} for n, g, r in sleeper_data if r >= 2.0],
            "wake": [{"number": n, "gap": g, "ratio": round(r, 1)} for n, g, r in sleeper_data if 1.0 <= r < 2.0],
        },
        "family_rhythm": {
            "predicted_missing": family_analysis.get("predicted_missing", ""),
            "predicted_gather": family_analysis.get("predicted_gather", ""),
            "missing_overdue": family_analysis.get("missing_overdue", {}),
            "gather_overdue": family_analysis.get("gather_overdue", {}),
        },
        "tickets": all_tickets,
        "total_tickets": len(all_tickets),
        "price_per_ticket": price_per_ticket,
        "total_price": total_price,
        "currency": "CHF",
        "engine": "🧬 Digit DNA v2 + Swiss Money Mode 🍀"
    }


@api_router.get("/swiss-sleepers")
async def get_swiss_sleepers():
    """Swiss Lotto Sleeper Analysis — numbers overdue to appear.
    🌠 Also returns `pool_top_6` from the live Ghost Pool (Laws 69-72)
    so the Celestial Radar can display the 6 best suspects for the
    next draw, refreshed on every d.
    """
    from datetime import datetime as dt_cls, timedelta as _td
    swiss_draws = await safe_find(db.draws, limit=5000)
    if not swiss_draws:
        return {"error": "No draws available"}
    
    def parse_d(d):
        try: return dt_cls.strptime(d['date'], '%d.%m.%Y')
        except: return dt_cls.min
    swiss_draws.sort(key=parse_d, reverse=True)
    
    expected_gap = 42 / 6
    last_seen = {}
    for i, d in enumerate(swiss_draws):
        for n in d.get('numbers', []):
            if n not in last_seen:
                last_seen[n] = i
    
    sleepers = []
    for n in range(1, 43):
        gap = last_seen.get(n, len(swiss_draws))
        ratio = round(gap / expected_gap, 1)
        status = "DEEP" if ratio >= 2.0 else ("WAKE" if ratio >= 1.0 else "FRESH")
        sleepers.append({"number": n, "gap": gap, "ratio": ratio, "status": status})
    
    sleepers.sort(key=lambda x: -x["ratio"])

    # 🌠 Celestial Radar — top 6 pool suspects for the next d
    pool_top_6: list = []
    pool_target_date = None
    pool_built_from = None
    try:
        from ghost_pool import get_top_pool_suspects
        last_d = swiss_draws[0]
        pool_built_from = last_d.get("date")
        # Resolve next draw date — Wed/Sat
        last_dt = parse_d(last_d)
        if last_dt != dt_cls.min:
            for delta in range(1, 8):
                cand = last_dt + _td(days=delta)
                if cand.weekday() in (2, 5):
                    pool_target_date = cand.strftime("%d.%m.%Y")
                    break
        target_dt = (dt_cls.strptime(pool_target_date, "%d.%m.%Y")
                     if pool_target_date else None)
        pool_top_6 = get_top_pool_suspects(
            last_mains=sorted(last_d.get("numbers", [])),
            last_stars=[],
            target_date=target_dt,
            lottery='swiss',
            k=6,
            min_depth=2,
        )
    except Exception as e:
        logger.warning(f"swiss-sleepers pool_top_6 failed: {e}")
        pool_top_6 = []

    return {
        "expected_gap": round(expected_gap, 1),
        "last_draw": swiss_draws[0]["date"] if swiss_draws else None,
        "sleepers": sleepers,
        "deep": [s for s in sleepers if s["status"] == "DEEP"],
        "wake": [s for s in sleepers if s["status"] == "WAKE"],
        "fresh": [s for s in sleepers if s["status"] == "FRESH"],
        # 🌠 Pool radar
        "pool_top_6": pool_top_6,
        "pool_target_date": pool_target_date,
        "pool_built_from": pool_built_from,
    }



@api_router.get("/digit-dna/simulate")
async def simulate_digit_dna_endpoint(target_date: str):
    """
    Simulate Digit DNA for a specific date.
    Returns DNA scores, top candidates, and 10 tickets in 2 modes.
    """
    from datetime import datetime
    import random
    from digit_dna import digit_dna_scores, swiss_circle
    
    try:
        target_dt = datetime.strptime(target_date, '%d.%m.%Y')
    except ValueError:
        return {"error": "Invalid date format. Use DD.MM.YYYY"}
    
    draws = await safe_find_sorted(db.draws, limit=5000)
    if not draws:
        return {"error": "No draws available"}
    
    def parse_date_fn(d):
        try:
            return datetime.strptime(d['date'], '%d.%m.%Y')
        except:
            return datetime.min
    draws = sorted(draws, key=parse_date_fn)
    
    # Find the target draw and previous draw
    prev_draw = None
    actual_draw = None
    for i, d in enumerate(draws):
        if d['date'] == target_date:
            actual_draw = d
            if i > 0: prev_draw = draws[i - 1]
            break
    
    if not actual_draw:
        for i, d in enumerate(draws):
            if parse_date_fn(d) >= target_dt:
                actual_draw = d
                if i > 0: prev_draw = draws[i - 1]
                break
    
    if not actual_draw or not prev_draw:
        return {"error": f"Could not find draw for {target_date}"}
    
    actual_nums = sorted(actual_draw['numbers'])
    prev_nums = sorted(prev_draw['numbers'])
    prev_lucky = prev_draw.get('lucky_number', 0)
    actual_lucky = actual_draw.get('lucky_number', 0)
    
    day = target_dt.day
    month = target_dt.month
    
    # Get DNA scores
    scores = digit_dna_scores(actual_draw['date'], prev_nums, weighted=True)
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    
    # MODE 1: DNA Only (10 tickets)
    random.seed(42)
    mode1_tickets = []
    for t in range(10):
        pool = []
        for n, s in scores.items():
            if s > 0:
                pool.extend([n] * int(s))
        selected = []
        used = set()
        for pos in range(6):
            available = [n for n in pool if n not in used and 1 <= n <= 42]
            if available:
                chosen = random.choice(available)
            else:
                remaining = [n for n in range(1, 43) if n not in used]
                chosen = random.choice(remaining)
            selected.append(chosen)
            used.add(chosen)
        selected.sort()
        hits = [n for n in selected if n in actual_nums]
        mode1_tickets.append({"numbers": selected, "hits": hits, "hit_count": len(hits)})
    
    # MODE 2: DNA + Patterns + Crazy (10 tickets)
    random.seed(43)
    mode2_tickets = []
    for t in range(10):
        pool = []
        for n, s in scores.items():
            if s > 0:
                pool.extend([n] * int(s))
        for n in prev_nums:
            pool.extend([n] * 12)
            if n > 1: pool.extend([n - 1] * 7)
            if n < 42: pool.extend([n + 1] * 7)
        if prev_lucky and 1 <= prev_lucky <= 42:
            pool.extend([prev_lucky] * 10)
        for n in prev_nums[:3]:
            for c in swiss_circle(n):
                pool.extend([c] * 5)
        dm_sum = day + month
        dm_diff = abs(day - month)
        if 1 <= dm_sum <= 42: pool.extend([dm_sum] * 8)
        if 1 <= dm_diff <= 42 and dm_diff > 0: pool.extend([dm_diff] * 5)
        if 1 <= day <= 42: pool.extend([day] * 6)
        if t >= 8:
            for n in range(30, 43): pool.extend([n] * 20)
            for n in range(1, 22):
                c = n + 21
                if c <= 42: pool.extend([c] * 10)
        
        selected = []
        used = set()
        for pos in range(6):
            available = [n for n in pool if n not in used and 1 <= n <= 42]
            if available:
                chosen = random.choice(available)
            else:
                remaining = [n for n in range(1, 43) if n not in used]
                chosen = random.choice(remaining)
            selected.append(chosen)
            used.add(chosen)
        selected.sort()
        hits = [n for n in selected if n in actual_nums]
        ticket_type = "crazy" if t >= 8 else "core"
        mode2_tickets.append({"numbers": selected, "hits": hits, "hit_count": len(hits), "type": ticket_type})
    
    m1_best = max(t["hit_count"] for t in mode1_tickets)
    m2_best = max(t["hit_count"] for t in mode2_tickets)
    
    return {
        "target_date": actual_draw['date'],
        "actual_draw": actual_nums,
        "actual_lucky": actual_lucky,
        "prev_draw": {"date": prev_draw['date'], "numbers": prev_nums, "lucky": prev_lucky},
        "dna_top_15": [(n, round(s, 1)) for n, s in ranked[:15]],
        "mode1_dna_only": {
            "tickets": mode1_tickets,
            "best_hits": m1_best,
            "avg_hits": round(sum(t["hit_count"] for t in mode1_tickets) / 10, 1),
        },
        "mode2_dna_patterns": {
            "tickets": mode2_tickets,
            "best_hits": m2_best,
            "avg_hits": round(sum(t["hit_count"] for t in mode2_tickets) / 10, 1),
        },
    }



@api_router.get("/predictions", response_model=PredictionData)
async def get_predictions():
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).batch_size(200).to_list(2000)
    
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

# === PREDICTION HISTORY ENDPOINTS ===

@api_router.get("/prediction-history")
async def get_prediction_history(limit: int = 100, lottery_type: str = None):
    """Get prediction history with optional filtering.
    
    🎻 Enriches each entry with V2 Detective 'suspect_story' — the Circle, 
    P4-P5, chain, date patterns that pointed to each number in the prediction.
    Highlights ONE 'hero_number' with highest conviction.
    """
    query = {}
    if lottery_type:
        query["lottery_type"] = lottery_type
    
    history = await db.prediction_history.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    
    # 🎧 Compute V2 Detective convictions once for the latest Swiss + Euro draw
    try:
        from dj_patterns import find_suspects
        
        swiss_draws = await safe_find(db.draws, limit=5000)
        def _pd(s):
            try: return datetime.strptime(s, '%d.%m.%Y')
            except: return datetime.min
        swiss_draws.sort(key=lambda x: _pd(x.get('date', '')), reverse=True)
        
        euro_draws = []
        async for d in db.euromillions_draws.find({}, {"_id": 0}).limit(500):
            euro_draws.append({"date": d.get("date", ""), "numbers": d.get("numbers", []), "stars": d.get("stars", [])})
        euro_draws.sort(key=lambda x: _pd(x.get('date', '')), reverse=True)

        # Build pattern maps — one for Swiss, one for Euro
        def _build_map(draws):
            if not draws: return {}
            # Compute next draw date: today → next Wed/Sat for Swiss, Tue/Fri for Euro (let find_suspects infer)
            try:
                res = find_suspects(draws[:15], target_date=None)
                m = {}
                for s in res.get("suspects", []):
                    m[s["number"]] = {
                        "conviction": s["conviction"],
                        "patterns": s.get("patterns", [])[:4],
                    }
                return m
            except Exception:
                return {}
        
        swiss_map = _build_map(swiss_draws)
        euro_map = _build_map(euro_draws)
    except Exception:
        swiss_map, euro_map = {}, {}
    
    # Enrich every history row
    for h in history:
        lot = h.get("lottery_type", "swiss")
        pmap = euro_map if lot == "euro" else swiss_map
        story = []
        hero = None
        hero_conv = 0
        for n in h.get("numbers", []):
            info = pmap.get(n)
            if info and info["conviction"] >= 1:
                story.append({
                    "n": n,
                    "conviction": info["conviction"],
                    "patterns": info["patterns"],
                })
                if info["conviction"] > hero_conv:
                    hero_conv = info["conviction"]
                    hero = n
        # Keep only top 3 most convicted
        story.sort(key=lambda x: -x["conviction"])
        h["suspect_story"] = story[:3]
        h["hero_number"] = hero
    
    # Calculate stats
    total = len(history)
    with_results = [h for h in history if h.get("matches") is not None]
    
    stats = {
        "total_predictions": total,
        "with_results": len(with_results),
        "avg_matches": sum(h.get("matches", 0) for h in with_results) / len(with_results) if with_results else 0,
        "perfect_matches": sum(1 for h in with_results if h.get("matches") == 6),
        "lucky_matches": sum(1 for h in with_results if h.get("lucky_match")),
    }
    
    return {
        "history": history,
        "stats": stats
    }

@api_router.post("/prediction-history/compare/{draw_date}")
async def compare_predictions_to_draw(draw_date: str):
    """Compare all predictions for a draw date with actual results"""
    # Get the actual draw
    actual_draw = await db.draws.find_one({"date": draw_date}, {"_id": 0})
    if not actual_draw:
        raise HTTPException(status_code=404, detail=f"No draw found for {draw_date}")
    
    actual_numbers = set(actual_draw.get("numbers", []))
    actual_lucky = actual_draw.get("lucky_number")
    
    # Get all predictions that haven't been compared yet
    # (predictions made before the draw date)
    predictions = await db.prediction_history.find({
        "lottery_type": "swiss",
        "matches": None,
        "created_at": {"$lt": draw_date + "T23:59:59"}
    }, {"_id": 0}).to_list(1000)
    
    results = []
    for pred in predictions:
        pred_numbers = set(pred.get("numbers", []))
        matches = len(pred_numbers & actual_numbers)
        lucky_match = pred.get("lucky_number") == actual_lucky if actual_lucky else None
        
        # Update the prediction with results
        await db.prediction_history.update_one(
            {"id": pred["id"]},
            {"$set": {
                "actual_numbers": list(actual_numbers),
                "actual_lucky": actual_lucky,
                "matches": matches,
                "lucky_match": lucky_match
            }}
        )
        
        results.append({
            "id": pred["id"],
            "predicted": pred.get("numbers"),
            "actual": list(actual_numbers),
            "matches": matches,
            "lucky_match": lucky_match
        })
    
    return {
        "draw_date": draw_date,
        "actual_numbers": list(actual_numbers),
        "actual_lucky": actual_lucky,
        "predictions_compared": len(results),
        "results": results,
        "summary": {
            "avg_matches": sum(r["matches"] for r in results) / len(results) if results else 0,
            "best_match": max(r["matches"] for r in results) if results else 0,
            "with_3_plus": sum(1 for r in results if r["matches"] >= 3),
            "with_4_plus": sum(1 for r in results if r["matches"] >= 4),
            "with_5_plus": sum(1 for r in results if r["matches"] >= 5),
        }
    }

@api_router.delete("/prediction-history/clear")
async def clear_prediction_history():
    """Clear all prediction history"""
    result = await db.prediction_history.delete_many({})
    return {"message": f"Deleted {result.deleted_count} predictions"}


@api_router.get("/ticket-counter")
async def get_ticket_counter():
    """Total tickets generated across all lotteries.
    🛡️ Hardened per Emergent Support: batch_size=100 + CursorNotFound retry."""
    from pymongo.errors import CursorNotFound, ExecutionTimeout

    async def _safe_sum(coll):
        total = 0
        for _ in range(3):
            try:
                async for g in coll.find({}, {'tickets': 1}).batch_size(100).limit(10000):
                    total += len(g.get('tickets', []))
                return total
            except (CursorNotFound, ExecutionTimeout):
                total = 0  # restart count, retry
        return total

    swiss_gen_count = await _safe_sum(db.generations)
    swiss_pred_count = await db.prediction_history.count_documents({})
    euro_count = await _safe_sum(db.euromillions_generations)
    total = swiss_gen_count + swiss_pred_count + euro_count
    return {"total_tickets": total, "swiss_tickets": swiss_gen_count + swiss_pred_count, "euro_tickets": euro_count}

@api_router.get("/pending-tickets")
async def get_pending_tickets(mode: str = "swiss", visitor_id: str = ""):
    """
    Get tickets generated for the NEXT upcoming draw.
    
    🎻 ALL tickets are included, including those with LOCKED positions.
        Locked tickets are tagged with `locked_positions` so the user can
        recognise their own pinned slots in the pending widget.
    🎧 Returns the TOP 10 best tickets (ranked by V2 Detective conviction for the next draw)
       plus "archive files" grouped by 50 tickets (sorted by generation time, newest first).
    """
    from datetime import timedelta
    today = datetime.now()

    async def _resolve_next_draw_date(weekdays, draws_collection):
        """🎻 DJ-rule (29.04.2026): if today IS a draw day and today's
        actual result is NOT yet in the DB, TODAY is the upcoming draw —
        do NOT roll forward to the next draw day. Otherwise compute the
        nearest future draw day.
        """
        wd = today.weekday()
        today_str = today.strftime("%d.%m.%Y")
        if wd in weekdays:
            already_stored = await draws_collection.find_one(
                {"date": today_str}, {"_id": 1}
            )
            if not already_stored:
                return today_str
        # Otherwise pick the nearest FUTURE draw day
        deltas = []
        for w in weekdays:
            d = (w - wd) % 7
            if d == 0:
                d = 7
            deltas.append(d)
        return (today + timedelta(days=min(deltas))).strftime("%d.%m.%Y")

    if mode == "euro":
        # Euro draws on Tue (1) and Fri (4)
        next_date = await _resolve_next_draw_date(
            [1, 4], db.euromillions_draws
        )
        
        # Collect ALL tickets (incl. locked) so user's own picks show up.
        # 🎻 DJ-rule (29.04.2026): never filter by visitor_id at the
        # query level — we want the community top10, but tag the
        # requesting user's own locked tickets so we can pin them first.
        q = {"target_date": next_date}
        all_tickets = []
        async for g in db.euromillions_generations.find(q, {"_id": 0, "visitor_id": 1, "tickets": 1, "mode": 1, "generated_at": 1, "has_locked": 1, "locked_positions": 1}):
            ga = g.get("generated_at", "")
            g_locked = g.get("has_locked", False)
            g_lock_pos = g.get("locked_positions") or {}
            g_vid = g.get("visitor_id", "")
            is_mine = bool(visitor_id) and g_vid == visitor_id
            for t in g.get("tickets", []):
                all_tickets.append({
                    "serial": t.get("serial"),
                    "numbers": t.get("numbers", []),
                    "stars": t.get("stars", []),
                    "story": t.get("story", g.get("mode", "")),
                    "generated_at": ga,
                    "has_locked": bool(g_locked),
                    "locked_positions": g_lock_pos if g_locked else {},
                    "is_mine": is_mine,
                })
        
        # 🎧 Score by V2 Detective conviction for the upcoming draw
        try:
            from dj_patterns import find_suspects
            euro_draws = []
            async for d in db.euromillions_draws.find({}, {"_id": 0}).limit(500):
                euro_draws.append({"date": d.get("date", ""), "numbers": d.get("numbers", []), "stars": d.get("stars", [])})
            # sort by date desc (string sort won't work; parse)
            def _pd(s):
                try: return datetime.strptime(s, '%d.%m.%Y')
                except: return datetime.min
            euro_draws.sort(key=lambda x: _pd(x['date']), reverse=True)
            suspect_res = find_suspects(euro_draws[:15], target_date=next_date) if euro_draws else {"suspects": []}
            conv_map = {s['number']: s['conviction'] for s in suspect_res.get('suspects', [])}
        except Exception:
            conv_map = {}
        
        # 🎻 Euro Date-Echo Neighborhood resonance (Session-3 rules)
        try:
            from euro_date_tuning import score_euro_date_resonance
        except Exception:
            score_euro_date_resonance = None
        # 🚨 Rare-Event Cycle scorer (Session-3 universal law)
        try:
            from rare_event_scorer import score_rare_event_echo, find_recent_rare_seed
            _rare_seed_info = find_recent_rare_seed(euro_draws, "euro", lookback=12) if euro_draws else None
        except Exception:
            score_rare_event_echo = None
            _rare_seed_info = None
        # 🪞 DJ-Call scorer (mirror-of-banned, back-door circles, DJ locks)
        try:
            from dj_call_scorer import score_dj_calls, load_dj_calls
            _dj_calls = load_dj_calls().get("euro", {}) or {}
        except Exception:
            score_dj_calls = None
            _dj_calls = {}
        
        for t in all_tickets:
            score = sum(conv_map.get(n, 0) for n in t.get("numbers", []))
            t["_score"] = score
            if score_euro_date_resonance is not None:
                try:
                    res = score_euro_date_resonance(
                        t.get("numbers", []), t.get("stars", []), next_date
                    )
                    t["date_resonance"] = {
                        "score": res["score"],
                        "badge": res["badge"],
                        "tier": res["tier"],
                        "signals": res["signals"],
                    }
                except Exception:
                    t["date_resonance"] = None
            if score_rare_event_echo is not None:
                try:
                    rr = score_rare_event_echo(
                        t.get("numbers", []), t.get("stars", []),
                        euro_draws, mode="euro"
                    )
                    if rr["score"] > 0:
                        t["rare_echo"] = {
                            "score": rr["score"],
                            "held_mains": rr["unreleased_held"]["mains"],
                            "held_stars": rr["unreleased_held"]["stars"],
                            "active": rr["active"],
                        }
                        t["_score"] += rr["score"]
                except Exception:
                    pass
            if score_dj_calls is not None:
                try:
                    dj = score_dj_calls(t.get("numbers", []), t.get("stars", []), mode="euro")
                    t["dj_call"] = {
                        "score": dj["score"],
                        "badge": dj["badge"],
                        "signals": dj["signals"],
                        "ban_hits": dj["ban_hits"],
                    }
                    t["_score"] += dj["score"]
                except Exception:
                    pass
        
        # Top 10 = best-scored. Archive = the rest, sorted by time (newest first), 50 per file.
        # 🎻 DJ-rule: pin requesting user's own LOCKED tickets at the head
        # of top10 so they always see their pinned slots in the pending sidebar.
        scored_sorted = sorted(all_tickets, key=lambda x: -x["_score"])
        my_locked = [t for t in scored_sorted
                     if t.get("is_mine") and t.get("has_locked")]
        seen_ser = {t.get("serial") for t in my_locked if t.get("serial")}
        community_pool = [t for t in scored_sorted
                          if t.get("serial") not in seen_ser
                          or not t.get("serial")]
        # Re-include user's non-locked or locked-without-serial fallback
        community_pool = [t for t in community_pool
                          if not (t.get("is_mine") and t.get("has_locked"))]
        top10 = (my_locked + community_pool)[:10]
        # Build the rest from anything not in top10 (by serial-or-id)
        in_top = {id(t) for t in top10}
        rest_pool = [t for t in scored_sorted if id(t) not in in_top]
        rest = sorted(rest_pool, key=lambda x: x.get("generated_at", ""), reverse=True)
        
        archive_files = []
        for idx in range(0, len(rest), 50):
            chunk = rest[idx:idx+50]
            archive_files.append({
                "file_name": f"50-tickets-#{idx//50 + 1}",
                "count": len(chunk),
                "tickets": [{k: v for k, v in t.items() if k != "_score"} for t in chunk],
            })
        
        # Top-level rare seed descriptor for UI banner
        rare_seed_out = None
        if _rare_seed_info:
            rare_seed_out = {
                "date": _rare_seed_info["rare_date"],
                "numbers": _rare_seed_info["rare_numbers"],
                "stars": _rare_seed_info["rare_stars"],
                "draws_since": _rare_seed_info["draws_since"],
                "unreleased_mains": _rare_seed_info["unreleased_mains"],
                "unreleased_stars": _rare_seed_info["unreleased_stars"],
            }
        
        # 🔬 Live diagnostic (self-aware engine)
        diagnostics_out = None
        try:
            from draw_diagnostics import run_diagnostics
            # Build q1d1 if we can find the first Euro draw of the target year
            from datetime import datetime as _dt
            _target_year = None
            try:
                _tdt = _dt.strptime(next_date, "%d.%m.%Y")
                _target_year = _tdt.year
            except Exception:
                pass
            _q1d1 = None
            if _target_year:
                _year_draws = [d for d in euro_draws if str(_target_year) in (d.get("date") or "")]
                _year_draws_sorted = sorted(_year_draws, key=lambda x: _pd(x.get("date")) or datetime.min)
                if _year_draws_sorted:
                    _q1d1 = _year_draws_sorted[0]
            diagnostics_out = run_diagnostics(
                euro_draws, next_date,
                q1d1=_q1d1,
                banned=_dj_calls.get("banned_mains") or [],
            )
            # strip bulky "laws" detail in response — keep narrative + hints
            diagnostics_out = {
                "narrative": diagnostics_out.get("dj_narrative", []),
                "scoring_hints": diagnostics_out.get("scoring_hints", {}),
                "snap_back_active": diagnostics_out["laws"]["snap_back"].get("active", False),
                "rare_active": diagnostics_out["laws"]["rare_event"].get("active", False),
                "backrow_echo": diagnostics_out["laws"]["backrow_echo"].get("echo_candidates", []),
            }
        except Exception as _e:
            diagnostics_out = {"error": str(_e)}
        
        return {
            "next_date": next_date,
            "count": len(all_tickets),
            "top_count": len(top10),
            "tickets": [{k: v for k, v in t.items() if k != "_score"} for t in top10],
            "archive_files": archive_files,
            "rare_seed": rare_seed_out,
            "dj_calls": _dj_calls,
            "diagnostics": diagnostics_out,
        }
    else:
        # Swiss draws on Wed (2) and Sat (5)
        next_date = await _resolve_next_draw_date([2, 5], db.draws)
        
        # 🎻 DJ-rule (29.04.2026): never filter by visitor_id at the
        # query level — we want the community top10, but tag the
        # requesting user's own locked tickets so we can pin them first.
        q = {"target_date": next_date}
        all_tickets = []
        async for g in db.generations.find(q, {"_id": 0, "visitor_id": 1, "tickets": 1, "generation_type": 1, "generated_at": 1, "has_locked": 1, "locked_positions": 1}):
            ga = g.get("generated_at", "")
            g_locked = g.get("has_locked", False)
            g_lock_pos = g.get("locked_positions") or {}
            g_vid = g.get("visitor_id", "")
            is_mine = bool(visitor_id) and g_vid == visitor_id
            for t in g.get("tickets", []):
                all_tickets.append({
                    "serial": t.get("serial"),
                    "numbers": t.get("numbers", []),
                    "lucky": t.get("lucky") or t.get("lucky_number"),
                    "story": t.get("story", g.get("generation_type", "")),
                    "generated_at": ga,
                    "has_locked": bool(g_locked),
                    "locked_positions": g_lock_pos if g_locked else {},
                    "is_mine": is_mine,
                })
        
        # 🎧 Score by Swiss Lotto previous-draw pattern conviction
        try:
            from dj_patterns import find_suspects
            swiss_draws = []
            async for d in db.draws.find({}, {"_id": 0}).limit(500):
                swiss_draws.append({"date": d.get("date", ""), "numbers": d.get("numbers", [])})
            def _pd(s):
                try: return datetime.strptime(s, '%d.%m.%Y')
                except: return datetime.min
            swiss_draws.sort(key=lambda x: _pd(x['date']), reverse=True)
            suspect_res = find_suspects(swiss_draws[:15], target_date=next_date) if swiss_draws else {"suspects": []}
            conv_map = {s['number']: s['conviction'] for s in suspect_res.get('suspects', [])}
        except Exception:
            conv_map = {}
        
        # 🚨 Rare-Event Cycle scorer (Session-3 universal law)
        try:
            from rare_event_scorer import score_rare_event_echo, find_recent_rare_seed
            _rare_seed_info = find_recent_rare_seed(swiss_draws, "swiss", lookback=12) if swiss_draws else None
        except Exception:
            score_rare_event_echo = None
            _rare_seed_info = None
        
        for t in all_tickets:
            score = sum(conv_map.get(n, 0) for n in t.get("numbers", []))
            t["_score"] = score
            if score_rare_event_echo is not None:
                try:
                    rr = score_rare_event_echo(
                        t.get("numbers", []), None, swiss_draws, mode="swiss"
                    )
                    if rr["score"] > 0:
                        t["rare_echo"] = {
                            "score": rr["score"],
                            "held_mains": rr["unreleased_held"]["mains"],
                            "held_stars": [],
                            "active": rr["active"],
                        }
                        t["_score"] += rr["score"]
                except Exception:
                    pass
        
        # 🎻 DJ-rule: pin requesting user's own LOCKED tickets at the head
        # of top10 so they always see their pinned slots in the pending sidebar.
        scored_sorted = sorted(all_tickets, key=lambda x: -x["_score"])
        my_locked = [t for t in scored_sorted
                     if t.get("is_mine") and t.get("has_locked")]
        community_pool = [t for t in scored_sorted
                          if not (t.get("is_mine") and t.get("has_locked"))]
        top10 = (my_locked + community_pool)[:10]
        in_top = {id(t) for t in top10}
        rest_pool = [t for t in scored_sorted if id(t) not in in_top]
        rest = sorted(rest_pool, key=lambda x: x.get("generated_at", ""), reverse=True)
        
        archive_files = []
        for idx in range(0, len(rest), 50):
            chunk = rest[idx:idx+50]
            archive_files.append({
                "file_name": f"50-tickets-#{idx//50 + 1}",
                "count": len(chunk),
                "tickets": [{k: v for k, v in t.items() if k != "_score"} for t in chunk],
            })
        
        rare_seed_out = None
        if _rare_seed_info:
            rare_seed_out = {
                "date": _rare_seed_info["rare_date"],
                "numbers": _rare_seed_info["rare_numbers"],
                "stars": _rare_seed_info["rare_stars"],
                "draws_since": _rare_seed_info["draws_since"],
                "unreleased_mains": _rare_seed_info["unreleased_mains"],
                "unreleased_stars": _rare_seed_info["unreleased_stars"],
            }
        
        return {
            "next_date": next_date,
            "count": len(all_tickets),
            "top_count": len(top10),
            "tickets": [{k: v for k, v in t.items() if k != "_score"} for t in top10],
            "archive_files": archive_files,
            "rare_seed": rare_seed_out,
        }


    
    # Next draw tickets
    from datetime import timedelta
    today = datetime.now()
    days_wed = (2 - today.weekday()) % 7
    days_sat = (5 - today.weekday()) % 7
    if days_wed == 0: days_wed = 7
    if days_sat == 0: days_sat = 7
    next_draw = today + timedelta(days=min(days_wed, days_sat))
    next_date = next_draw.strftime("%d.%m.%Y")
    
    next_draw_count = 0
    async for g in db.generations.find({'target_date': next_date}, {'tickets': 1}):
        next_draw_count += len(g.get('tickets', []))
    next_draw_preds = await db.prediction_history.count_documents({'target_draw_date': next_date})
    next_draw_count += next_draw_preds
    
    return {
        "total": total,
        "swiss": swiss_gen_count + swiss_pred_count,
        "euro": euro_count,
        "next_draw_date": next_date,
        "next_draw_tickets": next_draw_count,
    }


@api_router.get("/prediction-history/stats")
async def get_prediction_stats():
    """Get detailed statistics about prediction accuracy"""
    history = await safe_find(db.prediction_history, {"matches": {"$ne": None}}, limit=10000)
    
    if not history:
        return {"message": "No compared predictions yet", "stats": {}}
    
    # Number frequency in predictions vs actual matches
    predicted_freq = Counter()
    matched_freq = Counter()
    
    for h in history:
        for num in h.get("numbers", []):
            predicted_freq[num] += 1
        for num in h.get("numbers", []):
            if num in h.get("actual_numbers", []):
                matched_freq[num] += 1
    
    # Calculate hit rate per number
    number_stats = {}
    for num in range(1, 43):
        predicted = predicted_freq.get(num, 0)
        matched = matched_freq.get(num, 0)
        hit_rate = (matched / predicted * 100) if predicted > 0 else 0
        number_stats[num] = {
            "predicted": predicted,
            "matched": matched,
            "hit_rate": round(hit_rate, 1)
        }
    
    # Best performing numbers (by hit rate, min 10 predictions)
    best_numbers = sorted(
        [(n, s) for n, s in number_stats.items() if s["predicted"] >= 10],
        key=lambda x: x[1]["hit_rate"],
        reverse=True
    )[:10]
    
    # Match distribution
    match_dist = Counter(h.get("matches", 0) for h in history)
    
    return {
        "total_predictions": len(history),
        "match_distribution": {str(k): v for k, v in sorted(match_dist.items())},
        "avg_matches": round(sum(h.get("matches", 0) for h in history) / len(history), 2),
        "best_numbers": [{"number": n, **s} for n, s in best_numbers],
        "worst_numbers": [{"number": n, **s} for n, s in best_numbers[-10:]],
        "lucky_accuracy": round(
            sum(1 for h in history if h.get("lucky_match")) / len(history) * 100, 1
        ) if history else 0
    }

# ============ AUTO-FETCH LOTTERY RESULTS ============
from lottery_fetcher import auto_sync_all, sync_euromillions_to_db, sync_swisslotto_to_db, fetch_euromillions_latest

@api_router.post("/sync-results")
async def sync_lottery_results():
    """
    Manually trigger sync of latest lottery results from external sources
    - EuroMillions: Fetches from free API (euromillions.api.pedromealha.dev)
    - Swiss Lotto: Scrapes from lottolyzer.com (primary) / lotteryextreme.com (fallback)
    """
    stats = await auto_sync_all(db)
    return {
        "message": f"Sync complete! Added {stats['total_new']} new draws",
        "details": stats
    }


class ManualDrawInput(BaseModel):
    """Input model for manual draw entry"""
    date: str  # DD.MM.YYYY format
    numbers: List[int]  # 6 numbers
    lucky_number: int
    replay_number: Optional[int] = None


@api_router.post("/add-draw")
async def add_draw_manually(draw: ManualDrawInput):
    """
    Manually add a Swiss Lotto draw result.
    Use this when auto-sync doesn't work or for quick updates.
    """
    # Validate date format
    try:
        datetime.strptime(draw.date, "%d.%m.%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in DD.MM.YYYY format")
    
    # Validate numbers
    if len(draw.numbers) != 6:
        raise HTTPException(status_code=400, detail="Must provide exactly 6 numbers")
    
    if not all(1 <= n <= 42 for n in draw.numbers):
        raise HTTPException(status_code=400, detail="Numbers must be between 1 and 42")
    
    if not 1 <= draw.lucky_number <= 6:
        raise HTTPException(status_code=400, detail="Lucky number must be between 1 and 6")
    
    # Check if draw already exists
    existing = await db.draws.find_one({"date": draw.date})
    
    doc = {
        "date": draw.date,
        "numbers": sorted(draw.numbers),
        "lucky_number": draw.lucky_number,
        "replay_number": draw.replay_number or 1,
        "source": "manual"
    }
    
    if existing:
        # Update existing
        await db.draws.update_one(
            {"date": draw.date},
            {"$set": doc}
        )
        return {
            "message": f"Updated draw for {draw.date}",
            "draw": doc,
            "action": "updated"
        }
    else:
        # Insert new
        doc["id"] = str(uuid.uuid4())
        doc["created_at"] = datetime.now(timezone.utc).isoformat()
        await db.draws.insert_one(doc)
        return {
            "message": f"Added new draw for {draw.date}",
            "draw": doc,
            "action": "created"
        }


@api_router.post("/add-draws-bulk")
async def add_draws_bulk(draws: List[ManualDrawInput]):
    """
    Add multiple Swiss Lotto draws at once.
    Useful for importing historical data from 6richtige.ch
    """
    results = {"added": 0, "updated": 0, "errors": []}
    
    for draw in draws:
        try:
            # Validate
            datetime.strptime(draw.date, "%d.%m.%Y")
            if len(draw.numbers) != 6:
                results["errors"].append(f"{draw.date}: Must have 6 numbers")
                continue
            
            existing = await db.draws.find_one({"date": draw.date})
            
            doc = {
                "date": draw.date,
                "numbers": sorted(draw.numbers),
                "lucky_number": draw.lucky_number,
                "replay_number": draw.replay_number or 1,
                "source": "manual_bulk"
            }
            
            if existing:
                await db.draws.update_one({"date": draw.date}, {"$set": doc})
                results["updated"] += 1
            else:
                doc["id"] = str(uuid.uuid4())
                doc["created_at"] = datetime.now(timezone.utc).isoformat()
                await db.draws.insert_one(doc)
                results["added"] += 1
                
        except Exception as e:
            results["errors"].append(f"{draw.date}: {str(e)}")
    
    return {
        "message": f"Bulk import complete: {results['added']} added, {results['updated']} updated",
        "results": results
    }

@api_router.post("/sync-euromillions")
async def sync_euromillions_only():
    """Sync only EuroMillions results"""
    stats = await sync_euromillions_to_db(db, limit=50)
    return {
        "message": f"EuroMillions sync complete! Added {stats['new']} new draws",
        "stats": stats
    }

@api_router.post("/sync-swisslotto")
async def sync_swisslotto_only():
    """Sync only Swiss Lotto results"""
    stats = await sync_swisslotto_to_db(db, limit=50)
    return {
        "message": f"Swiss Lotto sync complete! Added {stats['new']} new draws",
        "stats": stats
    }

@api_router.post("/sync-data-files")
async def sync_data_files():
    """
    Sync the static Python data files with latest from APIs.
    This updates the source files used by the prediction engine.
    Use this to get the latest draws without restarting the server.
    """
    try:
        from data_sync import sync_euromillions_data
        stats = await sync_euromillions_data()
        return {
            "message": f"Data file sync complete! Status: {stats['status']}",
            "euromillions": stats,
            "note": "Server may need restart for new draws to appear in predictions" if stats.get('new', 0) > 0 else "Data is up to date"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@api_router.get("/story-signs")
async def get_story_signs_analysis():
    """
    Pattern 60: Story Signs - Advanced pattern analysis
    
    Analyzes the last quarter (27 draws) to find:
    - Circle warming patterns (when circle appears, actual number follows)
    - Hunger patterns (neighbors appear without the number)
    - Consecutive sequences (rare 4+ in a row)
    - Secret counting (value + gap = next value at same position)
    - Mirror to 42 patterns
    - Date code analysis
    - Family tracking
    
    Returns scores and reasons for each number 1-42.
    """
    try:
        # Get all Swiss Lotto draws
        draws = await db.draws.find({}, {"_id": 0}).batch_size(200).to_list(3000)
        
        if not draws:
            raise HTTPException(status_code=404, detail="No draws found")
        
        # Run Pattern 60 analysis
        result = analyze_story_signs(draws, quarter_size=27)
        
        # Sort scores by value
        sorted_scores = sorted(
            [(num, data) for num, data in result['scores'].items()],
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Format top predictions
        top_predictions = []
        for num, data in sorted_scores[:15]:
            top_predictions.append({
                "number": num,
                "score": data['score'],
                "reasons": data['reasons']
            })
        
        # Check our prediction numbers
        our_prediction = [13, 26, 27, 30, 31, 38]
        our_numbers_analysis = []
        for num in our_prediction:
            if num in result['scores']:
                data = result['scores'][num]
                our_numbers_analysis.append({
                    "number": num,
                    "score": data['score'],
                    "reasons": data['reasons']
                })
            else:
                our_numbers_analysis.append({
                    "number": num,
                    "score": 0,
                    "reasons": []
                })
        
        return {
            "pattern": "60 - Story Signs",
            "quarter_analyzed": result['quarter_analyzed'],
            "rare_events": result['rare_events'],
            "signs": result['signs'][:20],
            "top_15_predictions": top_predictions,
            "our_prediction_analysis": our_numbers_analysis,
            "prediction": {
                "numbers": our_prediction,
                "lucky": 5,
                "source": "Story of 26 - Full Circle from 19.06.2024"
            }
        }
        
    except Exception as e:
        logging.error(f"Story Signs analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/latest-results")
async def get_latest_external_results():
    """
    Preview latest results from external sources WITHOUT saving to database
    Useful for checking what new draws are available
    """
    euro_draws = await fetch_euromillions_latest(5)
    return {
        "euromillions": euro_draws,
        "swisslotto": [],  # Scraping may not always work
        "note": "Use POST /sync-results to save these to database"
    }

@api_router.get("/sync-schedule")
async def get_sync_schedule():
    """
    Get the auto-sync schedule status
    Shows when the next automatic syncs will happen
    """
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    jobs = []
    
    try:
        for job in scheduler.get_jobs():
            next_run = job.next_run_time.isoformat() if job.next_run_time else None
            jobs.append({
                "id": job.id,
                "next_run": next_run,
                "trigger": str(job.trigger)
            })
    except:
        pass
    
    return {
        "scheduler_running": scheduler.running if 'scheduler' in globals() else False,
        "schedule": {
            "swiss_lotto": "Wednesday & Saturday at 21:00 UTC (after 20:30 CET draws)",
            "euromillions": "Tuesday & Friday at 21:00 UTC (after 20:30 CET draws)"
        },
        "jobs": jobs,
        "note": "Draws are automatically fetched ~30 minutes after official draw times"
    }


@api_router.get("/story-generator")
async def generate_story_predictions(target_date: str = None, num_tickets: int = 8):
    """Generate lottery predictions using the COMBINED Story Patterns - ALL STORIES in 8 tickets!"""
    try:
        from story_pattern_generator import generate_combined_story_tickets, get_date_numbers as story_get_date_numbers
        
        draws = await db.draws.find({}, {"_id": 0}).batch_size(200).to_list(3000)
        if not draws:
            raise HTTPException(status_code=404, detail="No draws found")
        
        draw_tuples = []
        for d in draws:
            nums = d.get('numbers', [])
            lucky = d.get('lucky_number', d.get('lucky', 1))
            replay = d.get('replay_number', d.get('replay', 1))
            draw_tuples.append((d['date'], nums, lucky, replay))
        
        draw_tuples.sort(key=lambda x: datetime.strptime(x[0], "%d.%m.%Y"))
        
        if not target_date:
            from datetime import timedelta
            today = datetime.now()
            days_until_wed = (2 - today.weekday()) % 7
            days_until_sat = (5 - today.weekday()) % 7
            if days_until_wed == 0:
                days_until_wed = 7
            if days_until_sat == 0:
                days_until_sat = 7
            next_draw = min(days_until_wed, days_until_sat)
            target = today + timedelta(days=next_draw)
            target_date = target.strftime("%d.%m.%Y")
        
        # Use the NEW combined story ticket generator with ALL patterns!
        tickets = generate_combined_story_tickets(
            target_date=target_date,
            previous_draws=draw_tuples,
            num_tickets=num_tickets
        )
        
        date_nums = story_get_date_numbers(target_date)
        
        # Build story coverage summary
        story_coverage = {
            "26 Family": sum(1 for t in tickets if 26 in t.get('numbers', [])),
            "13 Family": sum(1 for t in tickets if 13 in t.get('numbers', [])),
            "18-39 Circle": sum(1 for t in tickets if 18 in t.get('numbers', []) or 39 in t.get('numbers', [])),
            "33-12 Reunion": sum(1 for t in tickets if 33 in t.get('numbers', []) or 12 in t.get('numbers', [])),
            "7 Ladder": sum(1 for t in tickets if all(n in t.get('numbers', []) for n in [7, 14, 21, 28, 35, 42]))
        }
        
        return {
            "target_date": target_date,
            "date_analysis": date_nums,
            "num_tickets": len(tickets),
            "cost_estimate": f"{len(tickets) * 2.5} CHF",
            "tickets": tickets,
            "story_coverage": story_coverage,
            "patterns_used": [
                "26 FAMILY + 18-39 CIRCLE",
                "13 FAMILY + 33-12 REUNION", 
                "18-39 CIRCLE + 33 HUNGRY + GAP",
                "26 STORY + 7 LADDER",
                "33 HUNGER + P8 + COLD",
                "DATE DANCE + 26 + P5 SERIES",
                "7 LADDER + P1+P6=42",
                "TRIPLE REUNION (26↔5, 18↔39, 12↔33)"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# HIT TRACKER ENDPOINTS - Track Generated Tickets vs Actual Draws
# =============================================================================

from hit_tracker import HitTracker
hit_tracker = HitTracker(db)


@api_router.get("/last-draw")
async def get_last_draw():
    """Get the most recent draw result"""
    try:
        last_draw = await hit_tracker.get_last_draw()
        if not last_draw:
            return {"error": "No draws found"}
        return {
            "date": last_draw.get("date"),
            "numbers": last_draw.get("numbers", []),
            "lucky_number": last_draw.get("lucky_number", last_draw.get("lucky")),
            "replay_number": last_draw.get("replay_number", last_draw.get("replay"))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/save-generation")
async def save_generation(target_date: str, tickets: List[dict]):
    """Save a generation for hit tracking"""
    try:
        gen_id = await hit_tracker.save_generation(
            target_date=target_date,
            tickets=tickets,
            generation_type="story"
        )
        return {
            "success": True,
            "generation_id": gen_id,
            "message": f"Saved {len(tickets)} tickets for {target_date}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/story-generator-save")
async def generate_and_save_story_predictions(target_date: str = None, num_tickets: int = 8):
    """Generate story predictions AND save them for hit tracking"""
    try:
        from story_pattern_generator import generate_combined_story_tickets, get_date_numbers as story_get_date_numbers
        
        draws = await db.draws.find({}, {"_id": 0}).batch_size(200).to_list(3000)
        if not draws:
            raise HTTPException(status_code=404, detail="No draws found")
        
        draw_tuples = []
        for d in draws:
            nums = d.get('numbers', [])
            lucky = d.get('lucky_number', d.get('lucky', 1))
            replay = d.get('replay_number', d.get('replay', 1))
            draw_tuples.append((d['date'], nums, lucky, replay))
        
        draw_tuples.sort(key=lambda x: datetime.strptime(x[0], "%d.%m.%Y"))
        
        if not target_date:
            from datetime import timedelta
            today = datetime.now()
            days_until_wed = (2 - today.weekday()) % 7
            days_until_sat = (5 - today.weekday()) % 7
            if days_until_wed == 0:
                days_until_wed = 7
            if days_until_sat == 0:
                days_until_sat = 7
            next_draw = min(days_until_wed, days_until_sat)
            target = today + timedelta(days=next_draw)
            target_date = target.strftime("%d.%m.%Y")
        
        tickets = generate_combined_story_tickets(
            target_date=target_date,
            previous_draws=draw_tuples,
            num_tickets=num_tickets
        )
        
        # Save for hit tracking
        gen_id = await hit_tracker.save_generation(
            target_date=target_date,
            tickets=tickets,
            generation_type="story"
        )
        
        date_nums = story_get_date_numbers(target_date)
        
        return {
            "generation_id": gen_id,
            "saved": True,
            "target_date": target_date,
            "date_analysis": date_nums,
            "num_tickets": len(tickets),
            "cost_estimate": f"{len(tickets) * 2.5} CHF",
            "tickets": tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/hit-tracker")
async def get_hit_tracker(last_draws: int = 3, limit: int = 100,
                          include_all: bool = False, min_match: int = 2):
    """
    CLEAN HIT TRACKER — Auto-calculates, shows tickets per draw.
    
    Default behavior: shows tickets with `min_match`+ total matches (mains+🍀).
    Set `include_all=true` to return ALL tickets for each draw window, even 
    those with 0 hits — so the DJ has a complete file for every draw.
    """
    from datetime import datetime as dt_cls
    
    def parse_d(date_str):
        try: return dt_cls.strptime(date_str, '%d.%m.%Y')
        except: return dt_cls.min
    
    # Get last N Swiss draws (sorted properly)
    all_swiss = await safe_find(db.draws, limit=5000)
    all_swiss.sort(key=lambda d: parse_d(d.get('date', '')), reverse=True)
    last_n_draws = all_swiss[:last_draws]
    last_n_dates = set(d['date'] for d in last_n_draws)
    
    # Map each target_date to the PREVIOUS (BD) draw date for "draw-to-draw" window
    bd_map = {}  # target_date -> bd_date
    sorted_all = sorted(all_swiss, key=lambda d: parse_d(d.get('date', '')))
    sorted_date_strs = [d.get('date') for d in sorted_all if d.get('date')]
    for i, d in enumerate(sorted_all):
        if i > 0:
            bd_map[d['date']] = sorted_all[i-1]['date']

    # Precompute (draw-time datetime, date-string) once — reused by both helpers
    import bisect
    _dates_dt19 = [parse_d(ds).replace(hour=19) for ds in sorted_date_strs]

    def _gen_window_bd(generated_at: str) -> Optional[str]:
        """Last Swiss draw strictly BEFORE generated_at (draw ~19:00 UTC)."""
        if not generated_at or not _dates_dt19:
            return None
        try:
            gen_dt = dt_cls.fromisoformat(generated_at.replace('Z','+00:00')).replace(tzinfo=None)
        except Exception:
            return None
        # bisect: find rightmost date < gen_dt
        idx = bisect.bisect_left(_dates_dt19, gen_dt)
        return sorted_date_strs[idx - 1] if idx > 0 else None

    def _true_target(generated_at: str) -> Optional[str]:
        """First Swiss draw whose draw-time (19 UTC) is AFTER generated_at."""
        if not generated_at or not _dates_dt19:
            return None
        try:
            gen_dt = dt_cls.fromisoformat(generated_at.replace('Z','+00:00')).replace(tzinfo=None)
        except Exception:
            return None
        # bisect: find leftmost date > gen_dt
        idx = bisect.bisect_right(_dates_dt19, gen_dt)
        return sorted_date_strs[idx] if idx < len(sorted_date_strs) else None
    
    results = []
    
    # === SWISS GENERATIONS (from hit_tracker/money-mode) ===
    # Pull generated_at + visitor_id too for the enriched view
    swiss_gens = await safe_find(db.generations, projection={
        "_id": 1, "target_date": 1, "tickets": 1,
        "hits_calculated": 1, "hit_results": 1, "generation_type": 1,
        "generated_at": 1, "visitor_id": 1,
    }, limit=5000)

    # REGROUP by TRUE target (first draw after generated_at), not saved target_date
    # This is what DJ asked: tickets generated before last draw don't count for next draw
    gens_by_true_target: dict = {}
    for gen in swiss_gens:
        ga = gen.get('generated_at', '')
        true_td = _true_target(ga)
        if not true_td:
            continue
        gens_by_true_target.setdefault(true_td, []).append(gen)
    for td in gens_by_true_target:
        gens_by_true_target[td].sort(key=lambda g: g.get('generated_at', ''))
    
    for td in gens_by_true_target:
        if td not in last_n_dates:
            continue
        actual = next((d for d in last_n_draws if d['date'] == td), None)
        if not actual:
            continue
        actual_nums = set(actual.get('numbers', []))
        actual_lucky = actual.get('lucky_number')
        bd_date = bd_map.get(td)
        bd_dt = parse_d(bd_date).replace(hour=19) if bd_date else None
        tgt_dt = parse_d(td)

        global_ticket_num = 0
        for gen in gens_by_true_target[td]:
            # Recalculate hits vs the TRUE target's actual draw (ignore stale hits_calculated)
            hr = []
            for i, ticket in enumerate(gen.get('tickets', [])):
                t_nums = set(ticket.get('numbers', []))
                hits_set = t_nums & actual_nums
                lucky_hit = (ticket.get('lucky') == actual_lucky or
                             ticket.get('lucky_number') == actual_lucky)
                hr.append({
                    "ticket_num": i + 1,
                    "hits": sorted(hits_set),
                    "hit_count": len(hits_set),
                    "lucky_hit": lucky_hit,
                })

            gen_at = gen.get('generated_at', '')
            visitor_id = gen.get('visitor_id') or ''
            for i, ticket in enumerate(gen.get('tickets', [])):
                global_ticket_num += 1
                t_nums = set(ticket.get('numbers', []))
                hit_count = hr[i]['hit_count']
                hits = hr[i]['hits']
                lucky_hit = hr[i]['lucky_hit']

                total_match = hit_count + (1 if lucky_hit else 0)
                # 🎯 DJ canon 16.05.2026: include_all shows every ticket, 
                # not just 2+ matches — the full file per draw.
                if include_all or total_match >= min_match:
                    # Draw-to-draw days_from_bd
                    days_from_bd = None
                    if bd_dt and gen_at:
                        try:
                            gen_dt = dt_cls.fromisoformat(gen_at.replace('Z','+00:00'))
                            gen_dt_naive = gen_dt.replace(tzinfo=None)
                            days_from_bd = (gen_dt_naive - bd_dt).total_seconds() / 86400
                            days_from_bd = round(days_from_bd, 2)
                        except Exception:
                            pass
                    # REAL window: find Swiss draw immediately before ticket gen
                    real_bd = _gen_window_bd(gen_at) or bd_date
                    results.append({
                        "lottery": "swiss",
                        "target_date": td,
                        "bd_date": bd_date,
                        "gen_bd": real_bd,
                        "window_label": f"{real_bd} → {td}" if real_bd else td,
                        "ticket_num": global_ticket_num,
                        "generated_at": gen_at,
                        "days_from_bd": days_from_bd,
                        "visitor_id": visitor_id,
                        "numbers": sorted(ticket.get('numbers', [])),
                        "lucky": ticket.get('lucky') or ticket.get('lucky_number'),
                        "story": ticket.get('story', gen.get('generation_type', '')),
                        "generation_type": gen.get('generation_type', 'story'),
                        "hit_count": hit_count,
                        "hits": sorted(hits) if isinstance(hits, set) else sorted(hits or []),
                        "lucky_hit": lucky_hit,
                        "total_match": total_match,
                        "actual_numbers": sorted(actual_nums),
                        "actual_lucky": actual_lucky,
                    })
    
    # === SWISS PREDICTION_HISTORY (from master-predictor) ===
    swiss_preds = await safe_find(
        db.prediction_history, {"lottery_type": "swiss"}, limit=5000
    )
    
    pred_seq = {}  # target_date -> running count
    for pred in swiss_preds:
        pred_nums = set(pred.get('numbers', []))
        pred_lucky = pred.get('lucky_number')
        created = pred.get('created_at', '') or pred.get('generated_at', '')
        # TRUE target = first Swiss draw after creation
        true_td = _true_target(created)
        if not true_td or true_td not in last_n_dates:
            continue
        draw = next((d for d in last_n_draws if d['date'] == true_td), None)
        if not draw:
            continue
        actual_nums = set(draw.get('numbers', []))
        actual_lucky = draw.get('lucky_number')
        hits = pred_nums & actual_nums
        lucky_hit = pred_lucky == actual_lucky
        total_match = len(hits) + (1 if lucky_hit else 0)
        if include_all or total_match >= min_match:
            td = draw['date']
            pred_seq[td] = pred_seq.get(td, 0) + 1
            bd_date = bd_map.get(td)
            bd_dt = parse_d(bd_date).replace(hour=19) if bd_date else None
            days_from_bd = None
            if bd_dt and created:
                try:
                    gen_dt = dt_cls.fromisoformat(created.replace('Z','+00:00'))
                    days_from_bd = round((gen_dt.replace(tzinfo=None) - bd_dt).total_seconds() / 86400, 2)
                except Exception:
                    pass
            real_bd = _gen_window_bd(created) or bd_date
            results.append({
                "lottery": "swiss",
                "target_date": td,
                "bd_date": bd_date,
                "gen_bd": real_bd,
                "window_label": f"{real_bd} → {td}" if real_bd else td,
                "ticket_num": pred_seq[td],
                "generated_at": created,
                "days_from_bd": days_from_bd,
                "visitor_id": pred.get('visitor_id', ''),
                "numbers": sorted(pred.get('numbers', [])),
                "lucky": pred_lucky,
                "story": "master-predictor",
                "generation_type": "master-predictor",
                "hit_count": len(hits),
                "hits": sorted(hits),
                "lucky_hit": lucky_hit,
                "total_match": total_match,
                "actual_numbers": sorted(actual_nums),
                "actual_lucky": actual_lucky,
            })
    
    # Sort: by date (latest draw first), then highest total_match, then hit_count
    results.sort(key=lambda r: (
        -parse_d(r['target_date']).timestamp(),
        -r.get('total_match', 0),
        -r['hit_count'],
    ))
    
    # Deduplicate (same numbers for same date)
    seen = set()
    unique_results = []
    for r in results:
        key = f"{r['target_date']}|{tuple(sorted(r['numbers']))}"
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    # Cap at `limit` best (default 100). When include_all=true, lift cap to
    # 500 so every draw's file is complete.
    total_with_2plus = len(unique_results)
    effective_limit = max(limit, 500) if include_all else limit
    unique_results = unique_results[:effective_limit]
    
    # === PER-DRAW STATS — total generated, hits, best, rate per draw ===
    per_draw_stats = []
    for d in last_n_draws:
        td = d['date']
        actual_nums = set(d.get('numbers', []))
        actual_lucky = d.get('lucky_number')
        bd_date = bd_map.get(td)
        bd_dt = parse_d(bd_date).replace(hour=19) if bd_date else None

        total_generated = 0
        hits_2plus = 0
        hits_3plus = 0
        hits_4plus = 0
        best_hit = 0
        best_total_match = 0
        best_ticket_info = None

        # ONLY tickets whose TRUE target equals this draw (generated after BD)
        gens_for_draw = gens_by_true_target.get(td, [])
        # Filter to only in-window tickets (sanity: generated_at > BD of this draw)
        for g in gens_for_draw:
            ga = g.get('generated_at', '')
            # Extra filter: must be generated AFTER the BD of this draw
            if bd_dt and ga:
                try:
                    if dt_cls.fromisoformat(ga.replace('Z','+00:00')).replace(tzinfo=None) <= bd_dt:
                        continue
                except Exception:
                    pass
            tickets = g.get('tickets', [])
            for i, t in enumerate(tickets):
                total_generated += 1
                t_nums = set(t.get('numbers', []))
                hc = len(t_nums & actual_nums)
                lh = t.get('lucky') == actual_lucky or t.get('lucky_number') == actual_lucky
                tm = hc + (1 if lh else 0)
                if tm >= 2: hits_2plus += 1
                if tm >= 3: hits_3plus += 1
                if tm >= 4: hits_4plus += 1
                if hc > best_hit: best_hit = hc
                if (tm, hc) > (best_total_match, best_ticket_info.get('hit_count', -1) if best_ticket_info else -1):
                    best_total_match = tm
                    best_ticket_info = {
                        "ticket_num_in_window": total_generated,
                        "numbers": sorted(t.get('numbers', [])),
                        "lucky": t.get('lucky') or t.get('lucky_number'),
                        "hit_count": hc,
                        "lucky_hit": lh,
                        "total_match": tm,
                        "generated_at": g.get('generated_at', ''),
                        "generation_type": g.get('generation_type', 'story'),
                        "visitor_id": g.get('visitor_id') or '',
                        "nickname": _lucky_nickname(
                            g.get('visitor_id') or '',
                            total_generated,
                            g.get('generated_at', ''),
                        ),
                        "hits": sorted(t_nums & actual_nums),
                    }

        # Count from prediction_history — ONLY if TRUE target == this draw
        for p in swiss_preds:
            ga = p.get('created_at', '') or p.get('generated_at', '')
            if _true_target(ga) != td:
                continue
            if bd_dt and ga:
                try:
                    if dt_cls.fromisoformat(ga.replace('Z','+00:00')).replace(tzinfo=None) <= bd_dt:
                        continue
                except Exception:
                    pass
            total_generated += 1
            p_nums = set(p.get('numbers', []))
            hc = len(p_nums & actual_nums)
            lh = p.get('lucky_number') == actual_lucky
            tm = hc + (1 if lh else 0)
            if tm >= 2: hits_2plus += 1
            if tm >= 3: hits_3plus += 1
            if tm >= 4: hits_4plus += 1
            if hc > best_hit: best_hit = hc
            if (tm, hc) > (best_total_match, best_ticket_info.get('hit_count', -1) if best_ticket_info else -1):
                best_total_match = tm
                best_ticket_info = {
                    "ticket_num_in_window": total_generated,
                    "numbers": sorted(p.get('numbers', [])),
                    "lucky": p.get('lucky_number'),
                    "hit_count": hc,
                    "lucky_hit": lh,
                    "total_match": tm,
                    "generated_at": ga,
                    "generation_type": "master-predictor",
                    "visitor_id": p.get('visitor_id', ''),
                    "nickname": _lucky_nickname(
                        p.get('visitor_id', ''),
                        total_generated,
                        ga,
                    ),
                    "hits": sorted(p_nums & actual_nums),
                }

        hit_rate = round((hits_2plus / total_generated * 100), 1) if total_generated > 0 else 0.0
        
        per_draw_stats.append({
            "date": td,
            "bd_date": bd_date,
            "window_label": f"{bd_date} → {td}" if bd_date else td,
            "total_generated": total_generated,
            "hits_2plus": hits_2plus,
            "hits_3plus": hits_3plus,
            "hits_4plus": hits_4plus,
            "best_hit": best_hit,
            "best_total_match": best_total_match,
            "best_ticket": best_ticket_info,
            "hit_rate_pct": hit_rate,
        })
    
    return {
        "last_draws": [{
            "date": d['date'],
            "numbers": sorted(d.get('numbers', [])),
            "lucky": d.get('lucky_number'),
        } for d in last_n_draws],
        "tickets_with_2_plus": total_with_2plus,
        "tickets_shown": len(unique_results),
        "results": unique_results,
        "per_draw_stats": per_draw_stats,
    }


def _lucky_nickname(visitor_id: str, ticket_num: int, generated_at: str) -> str:
    """Generate a friendly Lucky User name for a ticket."""
    if visitor_id:
        vid_tail = visitor_id[-6:] if len(visitor_id) > 6 else visitor_id
        return f"Lucky-{vid_tail}"
    # No visitor_id → anonymous ticket nickname based on ticket number + time
    tags = ["Silent", "Cosmic", "Starlight", "Midnight", "Twilight",
            "Dawn", "Sunset", "Moonlit", "Astral", "Drunken"]
    tag = tags[ticket_num % len(tags)]
    hour_label = ""
    try:
        from datetime import datetime as dtc
        dtp = dtc.fromisoformat(generated_at.replace('Z','+00:00'))
        h = dtp.hour
        if h < 6: hour_label = "Owl"
        elif h < 12: hour_label = "Lark"
        elif h < 18: hour_label = "Sage"
        else: hour_label = "Bard"
    except Exception:
        hour_label = "Seer"
    return f"{tag}-Jack-{hour_label}-#{ticket_num}"


@api_router.get("/tickets-archive")
async def get_tickets_archive(
    mode: str = "swiss",
    target_date: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 500,
    offset: int = 0,
    min_hits: int = 0,
    group_by_date: bool = False,
):
    """
    🎻 FULL ARCHIVE — every ticket ever generated, with generated_at timestamp,
    target_date, hit status (when draw known), and Lucky-Jack nickname.

    Filters:
      · mode: 'swiss' | 'euro' | 'all'
      · target_date: exact dd.mm.yyyy match
      · from_date / to_date: filter by ticket generated_at (ISO)
      · min_hits: only return tickets with ≥ N total matches
      · group_by_date: if true, return grouped {target_date: [tickets]}

    Returns: list of tickets sorted by generated_at desc, with:
      ticket_num_global · target_date · generated_at · generation_type ·
      numbers · lucky/stars/replay · hits · lucky_hit · total_match ·
      nickname · visitor_id · archive_window (BD → target when draw known)
    """
    from datetime import datetime as dtc

    def parse_d(s):
        try: return dtc.strptime(s, '%d.%m.%Y')
        except: return dtc.min

    # Build ticket list from both Swiss and Euro collections
    tickets_out: List[dict] = []

    # Map target_date -> actual draw (for hit calc)
    swiss_draws = await safe_find(db.draws, limit=5000)
    swiss_by_date = {d['date']: d for d in swiss_draws if d.get('date')}
    euro_draws = await safe_find(db.euromillions_draws, limit=5000)
    euro_by_date = {d['date']: d for d in euro_draws if d.get('date')}

    # BD map (previous draw date) per mode
    def build_bd(by_date):
        sorted_keys = sorted(by_date.keys(), key=parse_d)
        bd = {}
        for i, dt_key in enumerate(sorted_keys):
            if i > 0:
                bd[dt_key] = sorted_keys[i-1]
        return bd
    swiss_bd = build_bd(swiss_by_date)
    euro_bd = build_bd(euro_by_date)

    # Sorted draw-date lists for "find the draw BEFORE generated_at" lookup
    swiss_dates_sorted = sorted(swiss_by_date.keys(), key=parse_d)
    euro_dates_sorted = sorted(euro_by_date.keys(), key=parse_d)
    import bisect
    _swiss_dt19 = [parse_d(ds).replace(hour=19) for ds in swiss_dates_sorted]
    _euro_dt19 = [parse_d(ds).replace(hour=19) for ds in euro_dates_sorted]

    def _gen_window_bd(generated_at: str, dates_sorted: list) -> Optional[str]:
        """Last draw strictly BEFORE generated_at (draws ~19:00 UTC)."""
        if not generated_at or not dates_sorted:
            return None
        try:
            gen_dt = dtc.fromisoformat(generated_at.replace('Z', '+00:00')).replace(tzinfo=None)
        except Exception:
            return None
        dt_arr = _swiss_dt19 if dates_sorted is swiss_dates_sorted else _euro_dt19
        idx = bisect.bisect_left(dt_arr, gen_dt)
        return dates_sorted[idx - 1] if idx > 0 else None

    def _true_target(generated_at: str, dates_sorted: list) -> Optional[str]:
        """First draw whose draw-time is AFTER generated_at — ticket's real target."""
        if not generated_at or not dates_sorted:
            return None
        try:
            gen_dt = dtc.fromisoformat(generated_at.replace('Z', '+00:00')).replace(tzinfo=None)
        except Exception:
            return None
        dt_arr = _swiss_dt19 if dates_sorted is swiss_dates_sorted else _euro_dt19
        idx = bisect.bisect_right(dt_arr, gen_dt)
        return dates_sorted[idx] if idx < len(dates_sorted) else None

    # --- SWISS ---
    if mode in ("swiss", "all"):
        q: dict = {}
        # if target_date filter is set, interpret as TRUE target filter
        want_target = target_date
        cursor = db.generations.find({}, {
            "_id": 0, "tickets": 1, "target_date": 1, "generated_at": 1,
            "generation_type": 1, "visitor_id": 1,
        })
        async for g in cursor:
            ga = g.get("generated_at", "")
            if from_date and ga < from_date: continue
            if to_date and ga > to_date: continue
            # TRUE target = first Swiss draw after generated_at
            true_td = _true_target(ga, swiss_dates_sorted)
            if want_target and true_td != want_target: continue
            saved_td = g.get("target_date", "")
            actual = swiss_by_date.get(true_td) if true_td else None
            actual_nums = set(actual.get('numbers', [])) if actual else set()
            actual_lucky = actual.get('lucky_number') if actual else None
            real_bd = _gen_window_bd(ga, swiss_dates_sorted)
            for t in g.get("tickets", []):
                nums = sorted(t.get("numbers", []))
                if len(nums) != 6: continue
                lucky = t.get("lucky") or t.get("lucky_number")
                hits = sorted(set(nums) & actual_nums) if actual else []
                lucky_hit = (lucky == actual_lucky) if actual else False
                total_match = len(hits) + (1 if lucky_hit else 0)
                if total_match < min_hits: continue
                tickets_out.append({
                    "mode": "swiss",
                    "target_date": true_td or saved_td,   # TRUE target for scoring
                    "saved_target_date": saved_td,
                    "bd_date": real_bd,
                    "gen_bd": real_bd,
                    "window_label": f"{real_bd} → {true_td}" if real_bd and true_td else (true_td or saved_td),
                    "generated_at": ga,
                    "generation_type": g.get("generation_type", "story"),
                    "visitor_id": g.get("visitor_id") or "",
                    "numbers": nums,
                    "lucky": lucky,
                    "story": t.get("story", ""),
                    "hits": hits,
                    "lucky_hit": lucky_hit,
                    "total_match": total_match,
                    "draw_known": actual is not None,
                    "actual_numbers": sorted(actual_nums) if actual else None,
                    "actual_lucky": actual_lucky,
                })

        # ALSO include prediction_history (master-predictor)
        async for p in db.prediction_history.find({"lottery_type": "swiss"}, {"_id": 0}):
            ga = p.get("created_at") or p.get("generated_at") or ""
            if from_date and ga < from_date: continue
            if to_date and ga > to_date: continue
            true_td = _true_target(ga, swiss_dates_sorted)
            if want_target and true_td != want_target: continue
            saved_td = p.get("target_draw_date", "")
            actual = swiss_by_date.get(true_td) if true_td else None
            actual_nums = set(actual.get('numbers', [])) if actual else set()
            actual_lucky = actual.get('lucky_number') if actual else None
            real_bd = _gen_window_bd(ga, swiss_dates_sorted)
            nums = sorted(p.get("numbers", []))
            if len(nums) != 6: continue
            lucky = p.get("lucky_number")
            hits = sorted(set(nums) & actual_nums) if actual else []
            lucky_hit = (lucky == actual_lucky) if actual else False
            total_match = len(hits) + (1 if lucky_hit else 0)
            if total_match < min_hits: continue
            tickets_out.append({
                "mode": "swiss",
                "target_date": true_td or saved_td,
                "saved_target_date": saved_td,
                "bd_date": real_bd,
                "gen_bd": real_bd,
                "window_label": f"{real_bd} → {true_td}" if real_bd and true_td else (true_td or saved_td),
                "generated_at": ga,
                "generation_type": "master-predictor",
                "visitor_id": p.get("visitor_id") or "",
                "numbers": nums,
                "lucky": lucky,
                "story": "master-predictor",
                "hits": hits,
                "lucky_hit": lucky_hit,
                "total_match": total_match,
                "draw_known": actual is not None,
                "actual_numbers": sorted(actual_nums) if actual else None,
                "actual_lucky": actual_lucky,
            })

    # --- EURO ---
    if mode in ("euro", "all"):
        want_target = target_date
        cursor = db.euromillions_generations.find({}, {
            "_id": 0, "tickets": 1, "target_date": 1, "generated_at": 1,
            "mode": 1, "visitor_id": 1,
        })
        async for g in cursor:
            ga = g.get("generated_at", "")
            if from_date and ga < from_date: continue
            if to_date and ga > to_date: continue
            true_td = _true_target(ga, euro_dates_sorted)
            if want_target and true_td != want_target: continue
            saved_td = g.get("target_date", "")
            actual = euro_by_date.get(true_td) if true_td else None
            actual_nums = set(actual.get('numbers', [])) if actual else set()
            actual_stars = set(actual.get('stars', [])) if actual else set()
            real_bd = _gen_window_bd(ga, euro_dates_sorted)
            for t in g.get("tickets", []):
                nums = sorted(t.get("numbers", []))
                if len(nums) != 5: continue
                stars = sorted(t.get("stars", []))
                hits = sorted(set(nums) & actual_nums) if actual else []
                star_hits = sorted(set(stars) & actual_stars) if actual else []
                total_match = len(hits) + len(star_hits)
                if total_match < min_hits: continue
                tickets_out.append({
                    "mode": "euro",
                    "target_date": true_td or saved_td,
                    "saved_target_date": saved_td,
                    "bd_date": real_bd,
                    "gen_bd": real_bd,
                    "window_label": f"{real_bd} → {true_td}" if real_bd and true_td else (true_td or saved_td),
                    "generated_at": ga,
                    "generation_type": g.get("mode", "story"),
                    "visitor_id": g.get("visitor_id") or "",
                    "numbers": nums,
                    "stars": stars,
                    "story": t.get("story", ""),
                    "hits": hits,
                    "star_hits": star_hits,
                    "total_match": total_match,
                    "draw_known": actual is not None,
                    "actual_numbers": sorted(actual_nums) if actual else None,
                    "actual_stars": sorted(actual_stars) if actual else None,
                })

    # Sort newest first
    tickets_out.sort(key=lambda t: t.get("generated_at", ""), reverse=True)

    # Dedupe: master-predictor saves to BOTH generations AND prediction_history.
    # Key = (numbers, lucky/stars, generated_at truncated to minute, mode)
    def _dedupe_key(t):
        if t.get("mode") == "euro":
            stars = tuple(t.get("stars", []) or [])
        else:
            stars = ()
        return (
            tuple(t.get("numbers", [])),
            t.get("lucky"),
            stars,
            (t.get("generated_at") or "")[:16],  # minute precision
            t.get("mode"),
        )
    seen_keys = set()
    deduped = []
    for t in tickets_out:
        k = _dedupe_key(t)
        if k in seen_keys:
            continue
        seen_keys.add(k)
        # Drop entries with no target_date (orphan prediction_history rows)
        if not t.get("target_date"):
            continue
        deduped.append(t)
    tickets_out = deduped

    # Assign global sequential ticket_num (oldest=#1 → newest=#N)
    total_all = len(tickets_out)
    for idx, t in enumerate(tickets_out):
        t["ticket_num_global"] = total_all - idx
        t["nickname"] = _lucky_nickname(
            t.get("visitor_id") or "",
            t["ticket_num_global"],
            t.get("generated_at", ""),
        )

    # Apply limit + offset
    sliced = tickets_out[offset:offset + limit]

    # Group by target_date if requested
    if group_by_date:
        grouped: dict = {}
        for t in sliced:
            grouped.setdefault(t["target_date"], []).append(t)
        grouped_list = [
            {"target_date": td, "window_label": v[0]["window_label"],
             "count": len(v), "tickets": v}
            for td, v in grouped.items()
        ]
        grouped_list.sort(key=lambda x: parse_d(x["target_date"]), reverse=True)
        return {
            "mode": mode,
            "total_tickets": total_all,
            "offset": offset,
            "limit": limit,
            "returned": len(sliced),
            "groups": grouped_list,
        }

    return {
        "mode": mode,
        "total_tickets": total_all,
        "offset": offset,
        "limit": limit,
        "returned": len(sliced),
        "tickets": sliced,
    }


@api_router.get("/tickets-archive/dates")
async def get_archive_date_index(mode: str = "swiss"):
    """List all target_dates (by TRUE target = first draw after generation)
    that have generations, with counts. Used for archive navigation.
    🎧 Tuned with bisect — drops lookup from O(n*m) → O(n log m). Deploy-safe."""
    from datetime import datetime as dtc
    import bisect

    def parse_d(s):
        try: return dtc.strptime(s, '%d.%m.%Y')
        except: return dtc.min

    async def _load_sorted_dates(collection):
        """Return (date_strings_sorted, dt19_sorted_list) — cached once per request."""
        raw = [d['date'] async for d in collection.find({}, {'_id': 0, 'date': 1}) if d.get('date')]
        parsed = sorted([(parse_d(s).replace(hour=19), s) for s in raw], key=lambda x: x[0])
        dt19_arr = [p[0] for p in parsed]
        date_strs = [p[1] for p in parsed]
        return date_strs, dt19_arr

    def _find_true_target_fast(ga, date_strs, dt19_arr):
        if not ga or not dt19_arr:
            return None
        try:
            gen_dt = dtc.fromisoformat(ga.replace('Z', '+00:00')).replace(tzinfo=None)
        except Exception:
            return None
        # bisect: find leftmost draw-at-19:00 strictly greater than gen_dt
        idx = bisect.bisect_right(dt19_arr, gen_dt)
        return date_strs[idx] if idx < len(date_strs) else None

    out_counts: dict = {}

    if mode in ("swiss", "all"):
        swiss_strs, swiss_dt19 = await _load_sorted_dates(db.draws)
        async for g in db.generations.find({}, {'_id': 0, 'tickets': 1, 'generated_at': 1}):
            ga = g.get('generated_at', '')
            true_td = _find_true_target_fast(ga, swiss_strs, swiss_dt19)
            if not true_td: continue
            key = ('swiss', true_td)
            out_counts[key] = out_counts.get(key, 0) + len(g.get('tickets', []))
        async for p in db.prediction_history.find({'lottery_type': 'swiss'}, {'_id': 0, 'created_at': 1, 'generated_at': 1}):
            ga = p.get('created_at') or p.get('generated_at') or ''
            true_td = _find_true_target_fast(ga, swiss_strs, swiss_dt19)
            if not true_td: continue
            key = ('swiss', true_td)
            out_counts[key] = out_counts.get(key, 0) + 1

    if mode in ("euro", "all"):
        euro_strs, euro_dt19 = await _load_sorted_dates(db.euromillions_draws)
        async for g in db.euromillions_generations.find({}, {'_id': 0, 'tickets': 1, 'generated_at': 1}):
            ga = g.get('generated_at', '')
            true_td = _find_true_target_fast(ga, euro_strs, euro_dt19)
            if not true_td: continue
            key = ('euro', true_td)
            out_counts[key] = out_counts.get(key, 0) + len(g.get('tickets', []))

    out = [{'mode': m, 'target_date': td, 'count': c}
           for (m, td), c in out_counts.items()]
    out.sort(key=lambda r: parse_d(r['target_date']), reverse=True)
    return {"mode": mode, "total_dates": len(out), "dates": out}



@api_router.get("/generation-history")
async def get_generation_history(limit: int = 50):
    """Get all saved generations with hit data"""
    try:
        generations = await hit_tracker.get_generation_history(limit=limit)
        return {
            "count": len(generations),
            "generations": generations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/calculate-hits/{generation_id}")
async def calculate_hits_for_generation(generation_id: str):
    """Calculate hits for a specific generation"""
    try:
        result = await hit_tracker.calculate_hits(generation_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/recalculate-all-hits")
async def recalculate_all_hits():
    """Recalculate hits for all pending generations"""
    try:
        result = await hit_tracker.recalculate_all_hits()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/hit-stats")
async def get_hit_stats():
    """Get overall hit statistics"""
    try:
        stats = await hit_tracker.get_overall_stats()
        last_draw = await hit_tracker.get_last_draw()
        
        return {
            "last_draw": {
                "date": last_draw.get("date") if last_draw else None,
                "numbers": last_draw.get("numbers", []) if last_draw else [],
                "lucky": last_draw.get("lucky_number", last_draw.get("lucky")) if last_draw else None
            },
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── ACTIVE USER TRACKING ───────────────────────────────────
class HeartbeatRequest(BaseModel):
    visitor_id: str

# Test/bot visitor_id patterns to exclude from analytics (our own debug IDs)
_TEST_VID_PREFIXES = ("test", "vip_test", "bot", "cutoff_test", "scrub_test",
                      "testdj", "vip_scrub", "vip_cutoff")

def _is_real_vid(vid: str) -> bool:
    if not vid: return False
    low = vid.lower()
    return not any(low.startswith(p) for p in _TEST_VID_PREFIXES)

async def _real_user_counts(now_iso_cutoff: str):
    """Return (active_unique, total_unique) counting DISTINCT real visitor_ids only.

    🚀 Optimized: uses indexed $group aggregation instead of .distinct() which
    times out at 10s on production-sized collections. Per Emergent Support.
    """
    # Active: visitor_ids seen in the heartbeat window
    active_pipeline = [
        {"$match": {"last_seen": {"$gte": now_iso_cutoff}}},
        {"$group": {"_id": "$visitor_id"}},
    ]
    active_cursor = db.active_users.aggregate(active_pipeline, maxTimeMS=8000)
    active_ids = [doc["_id"] async for doc in active_cursor]

    # Total: all distinct visitor_ids (indexed-grouped, fast)
    total_pipeline = [
        {"$group": {"_id": "$visitor_id"}},
    ]
    total_cursor = db.active_users.aggregate(total_pipeline, maxTimeMS=8000)
    total_ids = [doc["_id"] async for doc in total_cursor]

    active_real = [v for v in active_ids if _is_real_vid(v)]
    total_real = [v for v in total_ids if _is_real_vid(v)]
    return len(active_real), len(total_real)


# ─── HEARTBEAT CACHE — counts only refresh every 10s ──────────────────────
# The heartbeat endpoint hits per-visitor every few seconds. Recomputing the
# global active/total counts on EVERY call (even with indexes) wastes I/O at
# scale. Cache the global counts with a 10-second TTL so multiple concurrent
# heartbeats share the same result.
import time as _time
_user_count_cache = {"active": 0, "total": 0, "expires_at": 0.0}
_USER_COUNT_TTL = 10.0  # seconds


async def _real_user_counts_cached(now_iso_cutoff: str):
    """TTL-cached wrapper around _real_user_counts. Safe to call from heartbeat."""
    now = _time.monotonic()
    if now < _user_count_cache["expires_at"]:
        return _user_count_cache["active"], _user_count_cache["total"]
    try:
        active, total = await _real_user_counts(now_iso_cutoff)
        _user_count_cache.update({
            "active": active, "total": total,
            "expires_at": now + _USER_COUNT_TTL,
        })
        return active, total
    except Exception as e:
        # If the aggregation times out or fails, return stale cache rather than 5xx
        logger.warning(f"⚠️ user-count refresh failed (using stale cache): {str(e)[:200]}")
        return _user_count_cache["active"], _user_count_cache["total"]

@api_router.post("/prune-generations")
async def prune_generations_endpoint(days: int = 3, threshold: int = 2):
    """🎻 DJ's RAM-saver — prune old generations (default: D+3, keep ≥2 hits).

    For every generation whose target_date is older than `days`:
      • Trim tickets to only those with `total_hits >= threshold`
      • If 0 keepers → delete the generation document entirely

    Args:
      days: cutoff in days past the draw (default 3)
      threshold: minimum total hits to keep a ticket (default 2)
    """
    from pruner import prune_all
    report = await prune_all(db, days=days, threshold=threshold)
    return report

# In-memory cache for /random-vs-engine results.
# Key: (mode, target_date_str) → (payload_dict, expires_at_monotonic)
# Short TTL while hits are still being calculated; long TTL once the draw is
# closed (recap fallback active or all samples are in).
_rve_cache: dict = {}
_RVE_TTL_LIVE  = 300    # 5 min — hits may still be trickling in
_RVE_TTL_FINAL = 3600   # 1 hour — draw closed / recap snapshot in use

@api_router.get("/random-vs-engine")
async def random_vs_engine(mode: str = "euro", date: str = ""):
    """🎻 Random-vs-E reality check (DJ canon 29.04.2026).

    Returns the closed-form RANDOM hit-rate baseline alongside E's actual
    observed hit-rate on the requested draw (default = the most recent
    completed draw). Two engine views per lottery:
      • **jackpot** — the standard `master-predictor` / `dreaming` flavor
      • **money**   — the `money-mode` flavor (3+ focused)

    Falls back to the `draw_recaps` snapshot when the live per-ticket data
    has already been pruned (D+3) — so the box keeps its truth even after
    the noise is purged.
    """
    from random_baseline import (
        euro_baseline, swiss_baseline,
        compute_engine_rates_euro, compute_engine_rates_swiss,
    )
    from datetime import datetime as _dt, timedelta
    import time as _time

    today = _dt.now()

    # Return cached result if still fresh (date="" resolves to latest draw
    # after the _last_completed_draw lookup, so we cache after resolution).
    _cache_key_early = (mode, date) if date else None
    if _cache_key_early:
        _cached = _rve_cache.get(_cache_key_early)
        if _cached and _time.monotonic() < _cached[1]:
            return _cached[0]

    async def _last_completed_draw(coll, weekdays):
        """Pick the most recent draw_date that is also stored in coll."""
        for back in range(0, 14):
            d = today - timedelta(days=back)
            if d.weekday() not in weekdays:
                continue
            ds = d.strftime("%d.%m.%Y")
            stored = await coll.find_one({"date": ds}, {"_id": 1})
            if stored:
                return ds
        return None

    def _rates_from_recap(r: dict, mode_name: str) -> dict:
        """Reconstruct per-ticket rates from a stored recap counter doc."""
        n = r.get("n", 0)
        if n <= 0:
            return None
        out = {
            "n": n,
            "p_2plus_mains": r["c2_main"] / n,
            "p_3plus_mains": r["c3_main"] / n,
            "p_4plus_mains": r["c4_main"] / n,
            "p_2plus_total": r["c2_total"] / n,
            "p_3plus_total": r["c3_total"] / n,
            "p_4plus_total": r["c4_total"] / n,
        }
        if mode_name == "swiss":
            out["p_5plus_mains"] = r.get("c5_main", 0) / n
            out["p_6_mains"] = r.get("c6_main", 0) / n
            out["p_lucky_hit"] = r.get("c_lucky", 0) / n
        else:
            out["p_5_mains"] = r.get("c5_main", 0) / n
            out["p_1plus_stars"] = r.get("c1_star", 0) / n
            out["p_2_stars"] = r.get("c2_star", 0) / n
        return out

    if mode == "euro":
        target = date
        if not target:
            target = await _last_completed_draw(
                db.euromillions_draws, [1, 4]
            )
        # Post-resolution cache check (covers date="" → latest draw path)
        if target:
            _cached = _rve_cache.get((mode, target))
            if _cached and _time.monotonic() < _cached[1]:
                return _cached[0]
        actual = await db.euromillions_draws.find_one(
            {"date": target}, {"_id": 0}
        ) if target else None

        jackpot_hits = []
        money_hits = []
        any_mode_n = 0
        if target:
            cursor = db.euromillions_generations.find(
                {"target_date": target, "hits_calculated": True},
                {"_id": 0, "tickets": 1, "hit_results": 1, "mode": 1, "generation_type": 1},
            ).limit(1000)
            async for g in cursor:
                m = (g.get("mode") or g.get("generation_type") or "").lower()
                hr = g.get("hit_results") or []
                any_mode_n += len(hr)
                if "money" in m:
                    money_hits.extend(hr)
                else:
                    jackpot_hits.extend(hr)

        random_pct = euro_baseline()
        jackpot_pct = compute_engine_rates_euro([], jackpot_hits) if jackpot_hits else None
        money_pct = compute_engine_rates_euro([], money_hits) if money_hits else None

        # 🔁 Fallback to recap snapshot if live data was pruned
        recap_used = False
        if (not jackpot_pct and not money_pct) or any_mode_n == 0:
            recap = await db.draw_recaps.find_one(
                {"target_date": target, "lottery": "euro"}, {"_id": 0}
            )
            if recap:
                recap_used = True
                if not jackpot_pct and recap.get("jackpot", {}).get("n", 0):
                    jackpot_pct = _rates_from_recap(recap["jackpot"], "euro")
                if not money_pct and recap.get("money", {}).get("n", 0):
                    money_pct = _rates_from_recap(recap["money"], "euro")

        _result = {
            "mode": "euro",
            "target_date": target,
            "actual_draw": actual,
            "random": random_pct,
            "engine": {"jackpot": jackpot_pct, "money": money_pct},
            "sample_sizes": {
                "jackpot": (jackpot_pct or {}).get("n", 0),
                "money":   (money_pct or {}).get("n", 0),
                "any_mode": any_mode_n or
                            ((jackpot_pct or {}).get("n", 0) +
                             (money_pct or {}).get("n", 0)),
            },
            "recap_fallback": recap_used,
        }
        if target:
            _ttl = _RVE_TTL_FINAL if (recap_used or any_mode_n > 0) else _RVE_TTL_LIVE
            _rve_cache[(mode, target)] = (_result, _time.monotonic() + _ttl)
        return _result

    else:  # swiss
        target = date
        if not target:
            target = await _last_completed_draw(db.draws, [2, 5])
        # Post-resolution cache check (covers date="" → latest draw path)
        if target:
            _cached = _rve_cache.get((mode, target))
            if _cached and _time.monotonic() < _cached[1]:
                return _cached[0]
        actual = await db.draws.find_one(
            {"date": target}, {"_id": 0}
        ) if target else None

        jackpot_hits = []
        money_hits = []
        any_mode_n = 0
        if target:
            cursor = db.generations.find(
                {"target_date": target, "hits_calculated": True},
                {"_id": 0, "tickets": 1, "hit_results": 1, "generation_type": 1},
            ).limit(1000)
            async for g in cursor:
                gt = (g.get("generation_type") or "").lower()
                hr = g.get("hit_results") or []
                any_mode_n += len(hr)
                if "money" in gt:
                    money_hits.extend(hr)
                else:
                    jackpot_hits.extend(hr)

        random_pct = swiss_baseline()
        jackpot_pct = compute_engine_rates_swiss([], jackpot_hits) if jackpot_hits else None
        money_pct = compute_engine_rates_swiss([], money_hits) if money_hits else None

        recap_used = False
        if (not jackpot_pct and not money_pct) or any_mode_n == 0:
            recap = await db.draw_recaps.find_one(
                {"target_date": target, "lottery": "swiss"}, {"_id": 0}
            )
            if recap:
                recap_used = True
                if not jackpot_pct and recap.get("jackpot", {}).get("n", 0):
                    jackpot_pct = _rates_from_recap(recap["jackpot"], "swiss")
                if not money_pct and recap.get("money", {}).get("n", 0):
                    money_pct = _rates_from_recap(recap["money"], "swiss")

        _result = {
            "mode": "swiss",
            "target_date": target,
            "actual_draw": actual,
            "random": random_pct,
            "engine": {"jackpot": jackpot_pct, "money": money_pct},
            "sample_sizes": {
                "jackpot": (jackpot_pct or {}).get("n", 0),
                "money":   (money_pct or {}).get("n", 0),
                "any_mode": any_mode_n or
                            ((jackpot_pct or {}).get("n", 0) +
                             (money_pct or {}).get("n", 0)),
            },
            "recap_fallback": recap_used,
        }
        if target:
            _ttl = _RVE_TTL_FINAL if (recap_used or any_mode_n > 0) else _RVE_TTL_LIVE
            _rve_cache[(mode, target)] = (_result, _time.monotonic() + _ttl)
        return _result


@api_router.post("/history/archive-now")
async def history_archive_now():
    """🎻 Snapshot every hit-calculated generation into historical_tickets.
    Idempotent — keyed by serial+target_date, safe to call multiple times.
    """
    from historical_archive import archive_completed_draws
    return await archive_completed_draws(db)


@api_router.get("/history/dates")
async def history_dates(mode: str = "swiss"):
    """List of past draw dates with archive stats (count, max hits, etc.)."""
    from historical_archive import fetch_historical_dates
    dates = await fetch_historical_dates(db, mode=mode)
    return {"mode": mode, "dates": dates}


@api_router.get("/history/tickets")
async def history_tickets(
    mode: str = "swiss",
    target_date: str = "",
    limit: int = 200,
    skip: int = 0,
    min_hits: int = 0,
):
    """Paginated archive read."""
    from historical_archive import fetch_historical
    docs = await fetch_historical(
        db, mode=mode, limit=limit, skip=skip,
        target_date=target_date or None,
        min_hits=min_hits,
    )
    return {
        "mode": mode,
        "target_date": target_date or None,
        "count": len(docs),
        "tickets": docs,
    }


@api_router.get("/history/export.csv")
async def history_export_csv(
    mode: str = "swiss",
    target_date: str = "",
    min_hits: int = 0,
):
    """CSV download of the archive (stream as text/csv)."""
    from historical_archive import export_csv
    from fastapi.responses import Response
    csv_text = await export_csv(
        db, mode=mode, target_date=target_date or None,
        min_hits=min_hits,
    )
    fn_date = target_date or "all"
    filename = f"luckyjack_{mode}_history_{fn_date}.csv"
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )







@api_router.post("/heartbeat")
async def user_heartbeat(req: HeartbeatRequest):
    """Register a heartbeat from a visitor. Returns cached active/total counts
    (10s TTL) so heavy traffic never blocks on the count aggregation."""
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    # Upsert is indexed on visitor_id — fast
    await db.active_users.update_one(
        {"visitor_id": req.visitor_id},
        {"$set": {"last_seen": now.isoformat()}, "$setOnInsert": {"first_seen": now.isoformat()}},
        upsert=True
    )
    cutoff = (now - timedelta(minutes=10)).isoformat()
    active, total = await _real_user_counts_cached(cutoff)
    return {"active_users": active, "total_users": total}

@api_router.get("/active-users")
async def get_active_users():
    """Get count of currently active users (cached, 10s TTL)."""
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    cutoff = (now - timedelta(minutes=10)).isoformat()
    active, total = await _real_user_counts_cached(cutoff)
    return {"active_users": active, "total_users": total}

# ─── TICKET LIMIT (12 per user per draw period — resets when new draw lands) ─────────────
TICKET_LIMIT = 20  # 🎻 Session 4: bumped 12→20 per mode per draw (40 total across Swiss+Euro)
MASTER_PROMO_CODE = "93928"  # 🎻 VIP bypass — unlimited tickets for holder

# ═══════════════════════════════════════════════════════════════════════════
# 🕒 DRAW-TIME GENERATOR CUTOFF (Europe/Zurich local time)
# ─── Euro: Tue & Fri close 19:30, reopen 23:00 (after results update)
# ─── Swiss: Wed close 19:00, Sat close 17:00, reopen 23:00
# ═══════════════════════════════════════════════════════════════════════════
def _now_zurich():
    from zoneinfo import ZoneInfo
    return datetime.now(tz=ZoneInfo("Europe/Zurich"))

def _generator_status(mode: str):
    """Return dict: {open: bool, reason: str, reopens_at: iso|None}."""
    # Normalize mode aliases
    if mode in ("euromillions", "em"): mode = "euro"
    if mode in ("swisslotto", "swiss_lotto"): mode = "swiss"
    now = _now_zurich()
    wd = now.weekday()  # Mon=0
    mins = now.hour * 60 + now.minute
    if mode == "euro":
        # Euro draws Tue(1) and Fri(4)
        if wd in (1, 4):
            if 19*60 + 30 <= mins < 23*60:
                reopen = now.replace(hour=23, minute=0, second=0, microsecond=0)
                return {"open": False, "reason": "Euro draw window 19:30–23:00",
                        "reopens_at": reopen.isoformat()}
        return {"open": True, "reason": "", "reopens_at": None}
    elif mode == "swiss":
        # Swiss: Wed(2) close 19:00, Sat(5) close 17:00
        if wd == 2 and 19*60 <= mins < 23*60:
            reopen = now.replace(hour=23, minute=0, second=0, microsecond=0)
            return {"open": False, "reason": "Swiss Wed draw window 19:00–23:00",
                    "reopens_at": reopen.isoformat()}
        if wd == 5 and 17*60 <= mins < 23*60:
            reopen = now.replace(hour=23, minute=0, second=0, microsecond=0)
            return {"open": False, "reason": "Swiss Sat draw window 17:00–23:00",
                    "reopens_at": reopen.isoformat()}
        return {"open": True, "reason": "", "reopens_at": None}
    return {"open": True, "reason": "", "reopens_at": None}

async def _assert_generator_open(mode: str, visitor_id: str = ""):
    """Raise 423 if the generator is closed (VIP bypass allowed)."""
    st = _generator_status(mode)
    if st["open"]:
        return
    # VIP bypass still allowed
    if visitor_id and await _is_visitor_unlimited(visitor_id):
        return
    raise HTTPException(
        status_code=423,
        detail=f"🎻 Generator closed — {st['reason']}. Reopens at {st['reopens_at'][11:16]}. Ya man, listen to the draw first 🎧",
    )

async def _is_visitor_unlimited(visitor_id: str) -> bool:
    """Check if this visitor has redeemed a valid promo code."""
    if not visitor_id:
        return False
    doc = await db.promo_redeemed.find_one({"visitor_id": visitor_id})
    return bool(doc and doc.get("unlimited"))

def _get_next_draw_dates():
    """Get next Swiss and Euro draw dates."""
    from datetime import timedelta
    today = datetime.now()
    # Swiss: Wed & Sat
    dw = (2 - today.weekday()) % 7
    ds = (5 - today.weekday()) % 7
    if dw == 0: dw = 7
    if ds == 0: ds = 7
    swiss_next = (today + timedelta(days=min(dw, ds))).strftime("%d.%m.%Y")
    # Euro: Tue & Fri
    dt_ = (1 - today.weekday()) % 7
    df = (4 - today.weekday()) % 7
    if dt_ == 0: dt_ = 7
    if df == 0: df = 7
    euro_next = (today + timedelta(days=min(dt_, df))).strftime("%d.%m.%Y")
    return swiss_next, euro_next

async def _count_visitor_tickets(visitor_id: str, mode: str = "swiss") -> int:
    """Count tickets a visitor generated for the next draw of a specific lottery."""
    swiss_next, euro_next = _get_next_draw_dates()
    count = 0
    if mode == "swiss":
        async for g in db.generations.find({"visitor_id": visitor_id, "target_date": swiss_next}, {"tickets": 1}):
            count += len(g.get("tickets", []))
    else:
        async for g in db.euromillions_generations.find({"visitor_id": visitor_id, "target_date": euro_next}, {"tickets": 1}):
            count += len(g.get("tickets", []))
    return count

@api_router.get("/ticket-limit")
async def check_ticket_limit(visitor_id: str = "", mode: str = "swiss"):
    """Check how many tickets a visitor has left for a specific lottery."""
    gs = _generator_status(mode)
    base = {"generator_open": gs["open"], "closed_reason": gs["reason"],
            "reopens_at": gs["reopens_at"]}
    if not visitor_id:
        return {**base, "used": 0, "limit": TICKET_LIMIT, "remaining": TICKET_LIMIT, "unlimited": False}
    # 🎻 VIP promo bypass
    if await _is_visitor_unlimited(visitor_id):
        used = await _count_visitor_tickets(visitor_id, mode)
        return {**base, "used": used, "limit": 9999, "remaining": 9999, "unlimited": True}
    used = await _count_visitor_tickets(visitor_id, mode)
    return {**base, "used": used, "limit": TICKET_LIMIT, "remaining": max(0, TICKET_LIMIT - used), "unlimited": False}


@api_router.get("/generator-status")
async def generator_status_endpoint(mode: Optional[str] = None):
    """Return open/closed status for generator, optionally per-mode."""
    if mode:
        return _generator_status(mode)
    return {
        "euro": _generator_status("euro"),
        "swiss": _generator_status("swiss"),
        "zurich_now": _now_zurich().isoformat(),
    }


class RedeemCodeRequest(BaseModel):
    visitor_id: str
    code: str

@api_router.post("/redeem-code")
async def redeem_promo_code(request: RedeemCodeRequest):
    """🎻 Redeem a promo code. Valid codes unlock unlimited tickets for the visitor."""
    if not request.visitor_id:
        raise HTTPException(status_code=400, detail="Missing visitor_id")
    code = (request.code or "").strip()
    if code != MASTER_PROMO_CODE:
        raise HTTPException(status_code=400, detail="Invalid code")
    # Upsert redemption record
    await db.promo_redeemed.update_one(
        {"visitor_id": request.visitor_id},
        {"$set": {
            "visitor_id": request.visitor_id,
            "unlimited": True,
            "redeemed_at": datetime.now(timezone.utc).isoformat(),
            "code_used": code,
        }},
        upsert=True,
    )
    return {"success": True, "unlimited": True, "message": "🎻 VIP unlocked — unlimited tickets!"}


# ─────────────────────────────────────────────────────────────
# 🎯 HUNT BOX endpoints — persistent "wait-for-50" targeting boxes
# ─────────────────────────────────────────────────────────────
import hunt_box as _hunt_box


class HuntBoxCreate(BaseModel):
    mode: str  # 'euro' or 'swiss'
    target_type: str = "p5_value"  # 'p5_value' | 'any_position' | 'p4_value'
    target_value: int  # e.g. 50
    jack_picks: List[int] = []
    label: Optional[str] = None


class HuntBoxSuspectUpdate(BaseModel):
    jack_picks: List[int]


@api_router.get("/hunt-box/active")
async def list_active_hunt_boxes(mode: Optional[str] = None):
    """List all active (unresolved) hunt boxes, optionally filtered by mode."""
    q = {"status": "active"}
    if mode:
        q["mode"] = mode
    boxes = await db.hunt_boxes.find(q, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"boxes": boxes}


@api_router.get("/hunt-box/{box_id}/tickets")
async def get_hunt_box_tickets(box_id: str):
    """Generate the current 5 tickets for this hunt box, targeting the next draw."""
    box = await db.hunt_boxes.find_one({"id": box_id}, {"_id": 0})
    if not box:
        raise HTTPException(status_code=404, detail="Hunt box not found")
    if box["status"] != "active":
        return {"box": box, "tickets": [], "status": "resolved"}

    swiss_next, euro_next = _get_next_draw_dates()
    target_date = euro_next if box["mode"] == "euro" else swiss_next

    dj_call = None
    try:
        dj_path = Path(__file__).parent / "dj_calls.json"
        if dj_path.exists():
            import json as _json
            dj_call = _json.loads(dj_path.read_text())
    except Exception:
        dj_call = None

    tickets = _hunt_box.generate_hunt_tickets(
        target_date=target_date,
        mode=box["mode"],
        target_value=box["target_value"],
        jack_picks=box.get("jack_picks", []),
        dj_call=dj_call,
        num_tickets=5,
    )
    return {
        "box": box,
        "target_date": target_date,
        "tickets": tickets,
    }


@api_router.post("/hunt-box")
async def create_hunt_box(req: HuntBoxCreate):
    """Create a new hunt box."""
    if req.mode not in ("euro", "swiss"):
        raise HTTPException(status_code=400, detail="mode must be 'euro' or 'swiss'")
    mx = 50 if req.mode == "euro" else 42
    if not (1 <= req.target_value <= mx):
        raise HTTPException(status_code=400, detail=f"target_value out of range (1-{mx})")
    box = {
        "id": str(uuid.uuid4()),
        "mode": req.mode,
        "target_type": req.target_type,
        "target_value": req.target_value,
        "jack_picks": sorted(set(req.jack_picks)),
        "label": req.label or f"{req.mode.upper()} P5={req.target_value} Hunt",
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "draws_covered": 0,
    }
    await db.hunt_boxes.insert_one(box)
    box.pop("_id", None)
    return {"box": box}


@api_router.put("/hunt-box/{box_id}/suspects")
async def update_hunt_box_suspects(box_id: str, req: HuntBoxSuspectUpdate):
    """Replace the jack_picks list for a hunt box."""
    box = await db.hunt_boxes.find_one({"id": box_id})
    if not box:
        raise HTTPException(status_code=404, detail="Hunt box not found")
    mx = 50 if box["mode"] == "euro" else 42
    clean = sorted(set(n for n in req.jack_picks if 1 <= n <= mx and n != box["target_value"]))
    await db.hunt_boxes.update_one(
        {"id": box_id},
        {"$set": {"jack_picks": clean, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"success": True, "jack_picks": clean}


@api_router.delete("/hunt-box/{box_id}")
async def delete_hunt_box(box_id: str):
    """Delete/resolve a hunt box."""
    res = await db.hunt_boxes.delete_one({"id": box_id})
    return {"deleted": res.deleted_count > 0}


@api_router.post("/hunt-box/seed-default")
async def seed_default_hunt_box():
    """Seed the DJ's default P5=50 Euro hunt box with jack picks [10, 27, 32]."""
    existing = await db.hunt_boxes.find_one({
        "mode": "euro",
        "target_value": 50,
        "target_type": "p5_value",
        "status": "active",
    })
    if existing:
        existing.pop("_id", None)
        return {"box": existing, "seeded": False}
    box = {
        "id": str(uuid.uuid4()),
        "mode": "euro",
        "target_type": "p5_value",
        "target_value": 50,
        "jack_picks": [10, 27, 32],
        "label": "🌌 Crown Cosmos — P5=50 Orbit",
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "draws_covered": 0,
    }
    await db.hunt_boxes.insert_one(box)
    box.pop("_id", None)
    return {"box": box, "seeded": True}


# ═══════════════════════════════════════════════════════════════════════════
# 🎻 COSMIC ENGINE — Production endpoint (all 34 Book laws baked in)
# ═══════════════════════════════════════════════════════════════════════════
from cosmic_engine import run_cosmic_engine as _run_cosmic_engine

class CosmicEngineRequest(BaseModel):
    target_date: str  # 'dd.mm.yyyy'
    n_tickets: int = 30
    banned: List[int] = []

@api_router.post("/cosmic-engine")
async def cosmic_engine_endpoint(req: CosmicEngineRequest):
    """Run the full cosmic engine for a target date with banned numbers."""
    try:
        result = await _run_cosmic_engine(req.target_date, req.n_tickets, req.banned)
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}

@api_router.get("/cosmic-engine/{target_date}")
async def cosmic_engine_get(target_date: str, n_tickets: int = 30):
    """GET variant — target_date is dd.mm.yyyy, no banned list."""
    try:
        result = await _run_cosmic_engine(target_date, n_tickets, [])
        return result
    except Exception as e:
        return {"error": str(e)}


# ─── SESSION 28 — P3-FOCUSED GHOST ORCHESTRA ───────────────────────────────
@api_router.get("/p3-ghost-orchestra/{target_date}")
async def p3_ghost_orchestra_endpoint(
    target_date: str,
    top_n_p3: int = 5,
    n_per_archetype: int = 2,
):
    """Run the P3-Focused Ghost Orchestra for a target date.

    Flow (Session 28 canon):
      1. Engine runs for target_date → produces P3 board
      2. Top N P3 candidates are picked by E
      3. For each P3: 2-year history mined → ghost picked → 10 tickets
      4. Related-P3 rotation options returned for each

    Args:
      target_date: dd.mm.yyyy
      top_n_p3: how many P3 candidates to build orchestras for (default 5)
      n_per_archetype: tickets per archetype (5 archetypes × N = total per P3)
    """
    try:
        from p3_ghost_live import run_p3_live
        result = await run_p3_live(target_date, top_n_p3=top_n_p3,
                                    n_per_archetype=n_per_archetype)
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# ─── SESSION 30 — DJ COSMIC BRAIN + 20-TICKET ORCHESTRA ───────────────────
@api_router.get("/dj-brain/{target_date}")
async def dj_brain_endpoint(
    target_date: str,
    seed_mains: str = "3,9,42,46,47",
    seed_stars: str = "1,11",
    pin_mains: str = "",
    pin_stars: str = "",
):
    """🧠 E's Cosmic Brain — full prophecy stack for a target date.
    Wires every Session 1-30 sight: 432 frequency rule, ⭐[1,11] history,
    precedent fold, hungry maps, family-of-seed, sneaky cousins,
    Q-d cell history, Law 89/90, 47-saturation, suspect ranker.
    """
    try:
        from dj_brain import cosmic_brain
        sm = [int(x) for x in seed_mains.split(",") if x.strip()]
        ss = [int(x) for x in seed_stars.split(",") if x.strip()]
        pm = [int(x) for x in pin_mains.split(",") if x.strip()] or None
        ps = [int(x) for x in pin_stars.split(",") if x.strip()] or None
        return await cosmic_brain(
            target_date=target_date,
            seed_mains=sm,
            seed_stars=ss,
            user_pin_mains=pm,
            user_pin_stars=ps,
        )
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@api_router.get("/dj-orchestra/{target_date}")
async def dj_orchestra_endpoint(
    target_date: str,
    seed_mains: str = "3,9,42,46,47",
    seed_stars: str = "1,11",
    pin_mains: str = "",
    pin_stars: str = "",
    cosmic_seed: int = 432,
):
    """🎼 The 20-ticket symphony: 7 archetypes covering every cosmic angle
    (frequency-pure, 28-axis, 67-bridge, precedent, Law 90, 47-collapse,
    star wildcards). Each ticket carries a reasoning tag.
    """
    try:
        from dj_orchestra import generate_orchestra
        sm = [int(x) for x in seed_mains.split(",") if x.strip()]
        ss = [int(x) for x in seed_stars.split(",") if x.strip()]
        pm = [int(x) for x in pin_mains.split(",") if x.strip()] or None
        ps = [int(x) for x in pin_stars.split(",") if x.strip()] or None
        return await generate_orchestra(
            target_date=target_date,
            seed_mains=sm,
            seed_stars=ss,
            user_pin_mains=pm,
            user_pin_stars=ps,
            seed=cosmic_seed,
        )
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# ─── SESSION 33 — GHOST COUNTING ENGINE (Wed/Sat separated per DJ canon) ──
@api_router.get("/ghost-counter/{target_date}/{mode}")
async def ghost_counter_endpoint(target_date: str, mode: str,
                                  weekday_split: bool = True):
    """👻 Ghost Counting Engine — per-weekday-stream P1 ghost ledger.

    DJ canon (Session 33): Wed and Sat (Tue and Fri for Euro) have DIFFERENT
    vibes. This endpoint keeps them separate by default. Returns ghost-debt
    arrays + chord projection (back-closer candidates).
    """
    try:
        from ghost_p1_counter import build_p1_ghost_ledger
        from ghost_chord_engine import build_ghost_chord
        mode_l = mode.lower().strip()
        if mode_l not in ("swiss", "euro"):
            return {"error": "mode must be 'swiss' or 'euro'"}
        ledger = await build_p1_ghost_ledger(target_date, mode_l)
        chord = build_ghost_chord(ledger, mode_l)
        return {
            "ledger": ledger,
            "chord": chord,
            "weekday_split": weekday_split,
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# ─── SESSION 36 — E's BRAIN v0.1 (memory + scoring) ───────────────────────
class ScoreDrawIn(BaseModel):
    actual_mains: List[int]
    actual_stars: List[int] = []


@api_router.post("/e-brain/score-draw/{target_date}/{mode}")
async def e_brain_score_draw(target_date: str, mode: str, body: ScoreDrawIn):
    """🧠 Score E's prediction for a draw vs the actual numbers.

    Loads the predicted convergence for `target_date`/`mode`, compares against
    the provided `actual_mains` + `actual_stars`, and stores the record in
    E's persistent memory at /app/backend/data/e_memory.json.
    """
    try:
        from cosmic_voices.orchestrator import run_cosmic_voices
        from e_memory import score_draw
        mode_l = mode.lower().strip()
        cv = await run_cosmic_voices(target_date=target_date, mode=mode_l, lens="all")
        record = score_draw(
            draw_date=target_date, mode=mode_l,
            actual_mains=body.actual_mains, actual_stars=body.actual_stars,
            predicted_voices=cv.get("voices") or {},
        )
        return {"scored": True, "record": record}
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@api_router.get("/e-brain/memory")
async def e_brain_memory(limit: int = 30):
    """🧠 Returns last `limit` scored draws + lens leaderboard."""
    try:
        from e_memory import get_memory_summary
        return get_memory_summary(limit=limit)
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# ─── SESSION 35 — SNEAKY UNIVERSE SYMPHONY ────────────────────────────────
@api_router.get("/sneaky-symphony/{target_date}/{mode}")
async def sneaky_symphony_endpoint(target_date: str, mode: str,
                                    pin_mains: str = ""):
    """🎫 Sneaky Universe Symphony — multi-signature ticket batch.

    DJ canon (S35): no chance still means ≥3 tickets per signature.
    Builds 5 (2-2-1) + 3 (2-1-1-1) + 3 (3-1-1) + 3 (4-1) + 3 (1-1-1-1-1)
    = 17 tickets covering every shape, with starved-family bias.
    """
    try:
        from cosmic_voices.orchestrator import run_cosmic_voices
        from cosmic_voices.sneaky_symphony import build_sneaky_symphony
        mode_l = mode.lower().strip()
        if mode_l != "euro":
            return {"error": "sneaky-symphony currently Euro-only (family signature lens)"}
        pins: list = []
        if pin_mains:
            try:
                pins = [int(x.strip()) for x in pin_mains.split(",") if x.strip()]
            except Exception:
                pins = []
        cv = await run_cosmic_voices(
            target_date=target_date, mode=mode_l, lens="all",
            user_pins=pins or None,
        )
        symphony = build_sneaky_symphony(cv.get("voices") or {})
        return {
            "target_date": target_date,
            "mode": mode_l,
            "symphony": symphony,
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# ─── SESSION 34 — COSMIC VOICES ENGINE (10 lenses + convergence) ──────────
# ─── SESSION 43 — RC-WALKS ENCRYPTION DECODER ───────────────────────────
@api_router.get("/encryption-decoder/{target_date}/{mode}")
async def encryption_decoder_endpoint(target_date: str, mode: str):
    """🔐 RC-Walks Encryption Decoder — Session 43 (Euro) + Session 44 (Swiss).

    Euro: 5-walk RC0 encryption (Canons 17-20).
    Swiss: 6-walk HUGE encryption with family-rare ghost collapse (Canons 21-29).
    """
    try:
        from cosmic_voices.rc_detector import detect_rc_anchor
        from cosmic_voices.rc_walks_encryption import compose_encryption_reading
        from cosmic_voices.orchestrator import _detect_swiss_huge
        from year_d_ledger import load_draws, parse_dt, quarter_of

        mode_l = mode.lower().strip()
        if mode_l not in ("euro", "swiss"):
            return {"available": False, "reason": "mode must be 'euro' or 'swiss'."}
        target_dt = parse_dt(target_date)
        if not target_dt:
            return {"error": f"invalid target_date '{target_date}' (use dd.mm.yyyy)"}

        draws = await load_draws(mode_l)
        past = [d for d in draws if d["dt"] < target_dt]
        past.sort(key=lambda x: x["dt"])
        tq = quarter_of(target_dt, mode_l)
        quarter_draws = [d for d in past if d["quarter"] == tq and d["year"] == target_dt.year]
        recent = past[-10:]

        if mode_l == "euro":
            rc0 = detect_rc_anchor(target_dt, draws, mode_l)
            post_rc = [d for d in past if rc0 and d["date"] != rc0["date"]
                       and d["dt"] > parse_dt(rc0["date"])] if rc0 else []
            reading = compose_encryption_reading(
                target_date, mode_l, rc0, quarter_draws, recent,
                post_rc_draws=post_rc,
            )
            return reading
        else:
            # Swiss: HUGE anchor (6-in-decade family-rare draw)
            huge = _detect_swiss_huge(past)
            if not huge:
                return {"available": False, "reason": "no Swiss HUGE detected in history"}
            huge_dt = parse_dt(huge["date"])
            post_huge = [d for d in past if d["dt"] > huge_dt] if huge_dt else []
            reading = compose_encryption_reading(
                target_date, mode_l, huge, quarter_draws, recent,
                post_rc_draws=post_huge,
            )
            return reading
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@api_router.get("/hungry/{target_date}/{mode}")
async def hungry_engine_endpoint(target_date: str, mode: str, top: int = 20):
    """🌀 HUNGRY-NUMBER ENGINE — Canon 31 (Session 45 DJ-taught 29.05.2026).

    No statistical laws. Pure cosmic ops:
       🌀 CIRCLE (carrier rotation ±25 Euro / ±21 Swiss)
       🔄 FLIP (digit reverse + wrap)
       ➕ ADD/SUB (ghost ±7, digit-sum, digit-reduction)
       🗺 TABLET (7-wide grid neighbors)
       cross-position math from db (P_i ± carrier + P_j, P_i + ⭐_k)

    Returns ranked hungry pool with EVERY op-path explained.
    """
    try:
        from cosmic_voices.hungry_engine import hungry_pool
        from year_d_ledger import load_draws, parse_dt

        mode_l = mode.lower().strip()
        target_dt = parse_dt(target_date)
        if not target_dt:
            return {"error": f"invalid target_date '{target_date}'"}
        draws = await load_draws(mode_l)
        past = sorted([d for d in draws if d["dt"] < target_dt], key=lambda x: x["dt"])
        if not past:
            return {"available": False, "reason": "no past draws"}

        db = past[-1]
        db_p = sorted(db["p"])
        seeds = list(db_p)  # all 5 (Euro) or 6 (Swiss) mains as seeds
        seeds.append(target_dt.day)  # date day as seed
        # add Euro/Swiss carrier as seed
        seeds.append(25 if mode_l == "euro" else 21)

        # Build db dict for cross-position
        db_for_cp = {
            "p": db_p,
            "stars": db.get("stars") or ([db["lucky"]] if db.get("lucky") else []),
        }

        pool = hungry_pool(seeds, db_draw=db_for_cp, mode=mode_l, min_paths=1)
        # Multi-path = stronger; sort already done
        return {
            "available": True,
            "mode": mode_l,
            "target_date": target_date,
            "db": {"date": db["date"], "mains": db_p, "stars": db_for_cp["stars"]},
            "seeds": seeds,
            "pool_size": len(pool),
            "top_hungry": pool[:top],
            "multi_path_hungry": [p for p in pool if p["path_count"] >= 2][:top],
            "verdict": (
                f"Hungry pool built from db {db['date']} {db_p} + date-day {target_dt.day}. "
                f"{len(pool)} candidates reachable via cosmic ops. "
                f"Strongest {len([p for p in pool if p['path_count']>=2])} have ≥2 op-paths."
            ),
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@api_router.get("/dj-pool/{target_date}/{mode}")
async def dj_pool_endpoint(target_date: str, mode: str, top: int = 12):
    """🪞 DJ-POOL — Session 45 Canon Fusion (Mirror-28, Bridge-22, Day-of-Month,
    Codec-x10, Carrier-Symmetry, BD-Walk, Year-Cap, Mirror-Day-Universal, etc.)

    Returns 12-number ranked pool with full canon receipts for any target date
    in either Euro or Swiss mode.
    """
    try:
        from cosmic_voices.dj_pool_builder import build_pool
        from year_d_ledger import load_draws, parse_dt

        mode_l = mode.lower().strip()
        target_dt = parse_dt(target_date)
        if not target_dt:
            return {"error": f"invalid target_date '{target_date}'"}
        draws = await load_draws(mode_l)
        past = sorted([d for d in draws if d["dt"] < target_dt], key=lambda x: x["dt"])
        if not past:
            return {"available": False, "reason": "no past draws"}

        db = past[-1]
        db_p = sorted(db["p"])
        bd_dict = {
            "date": db["date"],
            "mains": db_p,
            "stars": db.get("stars") or [],
            "lucky": db.get("lucky"),
        }
        result = build_pool(
            target_date=target_date,
            bd=bd_dict,
            mode=mode_l,
            pool_size=top,
        )
        result["available"] = True
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}





@api_router.get("/cosmic-voices/{target_date}/{mode}")
async def cosmic_voices_endpoint(target_date: str, mode: str,
                                  lens: str = "all",
                                  pin_mains: str = ""):
    """🎼 Cosmic Voices — Session 34's 13-lens chord engine.

    Lenses: rc_detector · climbing_voice · sinking_voice · gap_echo_97 ·
    star_product_door · q_opening_melody · internal_mirror · stance_tracker ·
    saturation_ledger · convergence_scorer (the meta-fuse).

    Query params:
      • lens=all (default) | one of the lens names
      • pin_mains=12,18 (DJ-pinned mains, comma-separated)
    """
    try:
        from cosmic_voices.orchestrator import run_cosmic_voices
        mode_l = mode.lower().strip()
        if mode_l not in ("swiss", "euro"):
            return {"error": "mode must be 'swiss' or 'euro'"}
        pins: list = []
        if pin_mains:
            try:
                pins = [int(x.strip()) for x in pin_mains.split(",") if x.strip()]
            except Exception:
                pins = []
        result = await run_cosmic_voices(
            target_date=target_date, mode=mode_l, lens=lens, user_pins=pins or None,
        )
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# ─── SESSION 38/39 — GHOST ENGINE (Ghost-Counting Canon) ─────────────────
@api_router.get("/ghost-ledger/{target_date}/{mode}")
async def ghost_ledger_endpoint(target_date: str, mode: str,
                                  lookback: int = 10):
    """👻 Ghost Ledger — Session 38 Ghost-Counting Canon (S39 build).

    Extracts every born ghost via `?+Pa=Pb` arithmetic doors, walks them +1
    per draw with mirror-neighbor / digit-swap / carrier-form probes,
    detects closures (raw / 4-late / 9-10d-deep-sleep / cross-carrier),
    flags chainless cash-windows, and fuses everything into convergence
    shout / whisper zones for the target date.

    Query params:
      • lookback=10 (window size for ghost tracking)
    """
    try:
        from ghost_engine import build_ghost_ledger
        return await build_ghost_ledger(
            target_date=target_date, mode=mode, lookback=lookback,
        )
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# ─── SESSION 39 — HIDDEN PRINCE (2-2-2 Prime Fugue Builder) ──────────────
@api_router.get("/hidden-prince/{target_date}/{mode}")
async def hidden_prince_endpoint(target_date: str, mode: str):
    """🎼 Hidden Prince — DJ's 2-2-2 Prime Fugue auto-builder (S39 canon).

    Identifies the cosmic 'hidden conductor' number — one that is hungry,
    mirrored from recent Euro raw, recently Lucky, AND ghost-ringing — and
    builds 3 pairs of mains around it (missing-middle, gap-ladder,
    digit-cousins), crowning it as the Lucky number.
    """
    try:
        from ghost_engine import build_ghost_ledger, hidden_prince_pipeline
        # Pull ghost ledger first
        gl = await build_ghost_ledger(target_date, mode, lookback=10)
        if gl.get("error"):
            return gl
        # Build hungry pool from alive ghosts + shout/whisper
        hungry_pool = set()
        for g in gl.get("alive_ghosts", []):
            hungry_pool.add(g["n"])
            hungry_pool.update(g.get("projected_hot_zone", []))
        for n in gl.get("convergence", {}).get("shout", []):
            hungry_pool.add(n)
        # Last Euro mains: use draws_window if Euro, else look up
        from year_d_ledger import load_draws, parse_dt
        from datetime import timedelta
        target_dt = parse_dt(target_date)
        last_euro_mains = []
        last_swiss_lucky = []
        if mode == "swiss":
            euros = await load_draws("euro")
            past_eu = [d for d in euros if d["dt"] < target_dt]
            past_eu.sort(key=lambda x: x["dt"])
            if past_eu:
                last_euro_mains = past_eu[-1].get("p", [])
        # Build recent draws (for last-Lucky check)
        sw = await load_draws("swiss")
        past_sw = sorted(
            [d for d in sw if d["dt"] < target_dt],
            key=lambda x: x["dt"],
        )
        recent_draws = past_sw[-3:] if past_sw else []
        # Adjust max constraints for mode
        max_main = 42 if mode == "swiss" else 50
        max_lucky = 6 if mode == "swiss" else 12
        fugues = hidden_prince_pipeline(
            recent_draws=recent_draws,
            hungry_pool=hungry_pool,
            last_euro_mains=last_euro_mains,
            ghost_shout=gl.get("convergence", {}).get("shout", []),
            max_lucky=max_lucky,
            max_main=max_main,
            top_k=5,
        )
        return {
            "target_date": target_date,
            "mode": mode,
            "hungry_pool_size": len(hungry_pool),
            "last_euro_mains": last_euro_mains,
            "fugues": fugues,
            "canon": (
                "S39 Hidden Prince — when a number is hungry + mirrored + "
                "recent-Lucky + ghost-ringing, the cosmos hides it from the "
                "mains and crowns it as Lucky. Build 3 pairs of mains each "
                "carrying the prince's signature."
            ),
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# ─── SESSION 40 — STORY COMPOSER (DJ canon, 13.05.2026 EOD) ──────────────
@api_router.get("/story-tickets/{target_date}/{mode}")
async def story_tickets_endpoint(target_date: str, mode: str, count: int = 10,
                                 save: bool = True):
    """📖 Story Composer — E's narrative engine (S40 DJ canon).

    Fuses Brain (cosmic_voices) + Ghost Pool + Hungry Plate (S39 Canon 8) +
    Hidden Prince (S39 Canon 9) + Sister-Date Precedents + Swiss Brain into
    one narrative palette. Composes `count` ticket-stories backward
    (P6 → P5 → P4 → P3 → P2 → P1) along themed story arcs. Each number
    wears its full lens-DNA.

    Query params:
      • count=10 (number of stories to generate; 5-15 sensible)
      • save=true (auto-save to Hit Tracker for retro hit-rate analysis)
    """
    try:
        from ghost_engine import compose_stories
        count = max(3, min(int(count or 10), 15))
        result = await compose_stories(
            target_date=target_date, mode=mode, count=count,
        )
        # 💾 S40.2 — Auto-save story tickets to Hit Tracker (DJ canon 16.05.2026)
        # Every Story Composer generation creates a file with all tickets so the
        # tracker can score them retrospectively when the actual draw lands.
        if save and not result.get("error") and result.get("stories"):
            try:
                tickets = []
                for s in result["stories"]:
                    t = {
                        "numbers": list(s.get("mains", [])),
                        "story": f"S40:{s.get('theme', '?')[:48]}",
                        "narrative": s.get("narrative", ""),
                        "theme": s.get("theme"),
                        "cosmic_score": s.get("cosmic_score", 0),
                    }
                    if mode == "swiss":
                        t["lucky"] = s.get("lucky")
                        t["replay"] = s.get("replay")
                    else:
                        t["stars"] = list(s.get("stars", []))
                    tickets.append(t)
                if mode == "swiss":
                    await hit_tracker.save_generation(
                        target_date=target_date,
                        tickets=tickets,
                        generation_type="story-composer",
                    )
                else:
                    # Euro: save to euromillions_generations
                    await db.euromillions_generations.insert_one({
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "target_date": target_date,
                        "generation_type": "story-composer",
                        "mode": "euro",
                        "tickets": tickets,
                        "hits_calculated": False,
                    })
                result["saved_to_hit_tracker"] = True
            except Exception as save_err:
                result["saved_to_hit_tracker"] = False
                result["save_error"] = str(save_err)
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# ─── SESSION 37 — SWISS BRAIN v1.0 (10-ticket Swiss symphony) ────────────
@api_router.get("/swiss-symphony/{target_date}")
async def swiss_symphony_endpoint(target_date: str, count: int = 10,
                                    extra_envelopes: str = ""):
    """🧠 Swiss Brain v1.0 — 10-ticket symphony (6 mains + 🍀 + R).

    Combines all Swiss canons:
      • Existing cosmic_voices lenses (mode-aware)
      • swiss_back_chord (🍀↔R signals)
      • q1_stencil_projector (same-d prior-quarter delta)
      • gap_pattern (P2 ±6, P4/P5 sign-flip 86%, P6 freeze)
      • d_count_walker (9-clock mult-9 detection)
      • date_envelope (between-digit hide)
      • cross_lottery_bridge (Eu→Sw +21/-25/+1)
      • e_memory leaderboard weights

    Query params:
      • count=10 (number of tickets to generate)
      • extra_envelopes=3-7,1-4 (additional date envelopes, comma-separated)
    """
    try:
        from swiss_brain import build_swiss_symphony
        envs = []
        if extra_envelopes:
            for pair in extra_envelopes.split(","):
                pair = pair.strip()
                if "-" in pair:
                    a, b = pair.split("-", 1)
                    envs.append((int(a.strip()), int(b.strip())))
        result = await build_swiss_symphony(target_date, count=count,
                                             extra_envelopes=envs or None)
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@api_router.get("/dj-suspects")
async def get_dj_suspects(mode: str = "euro"):
    """🎻 Get the DJ's 3 big suspects for the upcoming draw.
    Returns the most recent suspects doc for the given mode.
    """
    doc = await db.dj_suspects.find_one(
        {"mode": mode}, {"_id": 0}, sort=[("updated_at", -1)]
    )
    if not doc:
        return {"mode": mode, "suspects": [], "target_date": "", "note": "", "updated_at": ""}
    return doc


@api_router.post("/dj-suspects")
async def set_dj_suspects(payload: dict = Body(...)):
    """🎻 Set the DJ's 3 big suspects for the upcoming draw.
    Body: {"mode": "euro", "target_date": "05.05.2026",
           "suspects": [7, 6, 34], "note": "..."}
    """
    mode = (payload.get("mode") or "euro").strip().lower()
    target_date = (payload.get("target_date") or "").strip()
    suspects = payload.get("suspects") or []
    note = (payload.get("note") or "").strip()
    # Validation
    try:
        suspects = [int(x) for x in suspects][:3]
    except Exception:
        return {"error": "suspects must be a list of up to 3 integers"}
    if not suspects:
        return {"error": "suspects required"}
    pool_max = 50 if mode == "euro" else 42
    for n in suspects:
        if n < 1 or n > pool_max:
            return {"error": f"suspect {n} out of range 1-{pool_max} for mode={mode}"}
    doc = {
        "mode": mode,
        "target_date": target_date,
        "suspects": suspects,
        "note": note,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.dj_suspects.update_one(
        {"mode": mode, "target_date": target_date},
        {"$set": doc},
        upsert=True,
    )
    return {"ok": True, **doc}


@api_router.get("/p3-ghost-orchestra-single/{target_date}/{p3_value}")
async def p3_ghost_single_endpoint(target_date: str, p3_value: int,
                                     n_per_archetype: int = 10):
    """Run an orchestra for a SPECIFIC P3 value (the DJ picks, E plays).
    Produces up to 5 × n_per_archetype = 50 tickets by default.
    """
    try:
        from p3_ghost_orchestra import (
            mine_p3_history, pick_ghost, build_p3_tickets,
            related_p3_candidates, load_draws,
        )
        draws2y = load_draws(2024)
        hist = mine_p3_history(p3_value, draws2y)
        ghosts = pick_ghost(p3_value, hist, draws2y, top_k=3)
        ghost = ghosts[0][0] if ghosts else 21
        tickets = build_p3_tickets(p3_value, ghost, hist, draws2y,
                                    n_per_archetype=n_per_archetype)
        related = related_p3_candidates(p3_value)
        return {
            'target_date': target_date,
            'p3': p3_value,
            'history_matches': hist['count'],
            'top_co_partners': hist['co_partners_top'][:10],
            'top_p1_partners': hist['p1_top'],
            'top_p5_partners': hist['p5_top'],
            'top_s1': hist['s1_top'],
            'top_s2': hist['s2_top'],
            'ghost': ghost,
            'ghost_alternates': [(g, t) for g, t in ghosts[1:3]],
            'tickets': tickets,
            'related_p3s': related,
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}




# ─── SESSION 15/16 — Silent P1 Compass + DJ Live Call endpoints ───
async def _load_swiss_history_sorted():
    """Load Swiss draws chronologically oldest→newest."""
    from datetime import datetime as _dt
    draws = await db.draws.find({}, {"_id": 0}).to_list(length=10000)
    def _pk(d):
        try:
            return _dt.strptime(d.get('date', ''), '%d.%m.%Y')
        except Exception:
            return _dt.min
    draws.sort(key=_pk)
    return draws


@api_router.get("/swiss/silent-compass")
async def swiss_silent_compass():
    """Session 15: Live Silent-P1 Compass state + frame suggestion."""
    try:
        from silent_p1_compass import (
            compute_p1_silence_state, suggest_silent_frame,
            SILENT_FAMILY, WELCOME_COMPANION, HUGE_TWIN_LOCK,
        )
        history = await _load_swiss_history_sorted()
        if not history:
            return {"error": "no swiss draws in db"}
        last_draw = history[-1]
        state = compute_p1_silence_state(history)
        frame = suggest_silent_frame(state, last_draw)
        return {
            "target_inferred": "next Swiss draw",
            "last_draw": {
                "date": last_draw.get('date'),
                "numbers": sorted(last_draw.get('numbers', [])),
                "lucky": last_draw.get('lucky_number'),
                "replay": last_draw.get('replay_number'),
            },
            "silent_state": state,
            "silent_family": sorted(SILENT_FAMILY),
            "welcome_companion": WELCOME_COMPANION,
            "huge_twin_lock": HUGE_TWIN_LOCK,
            "frame": frame,
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@api_router.get("/swiss/session16")
async def swiss_session16_snapshot():
    """Session 16: Full live-call snapshot (frame + anchors + variants)."""
    try:
        from session16_live_call import get_session16_snapshot
        return get_session16_snapshot()
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@api_router.get("/swiss/session16/tickets")
async def swiss_session16_tickets(n: int = 12, seed: Optional[int] = None):
    """Session 16: Generate DJ-determined tickets (core-locked + variants)."""
    try:
        from session16_live_call import (
            generate_session16_tickets, get_determination_piece,
            generate_whatif_variants,
        )
        history = await _load_swiss_history_sorted()
        last_draw = history[-1] if history else None
        tickets = generate_session16_tickets(
            n=n, last_draw=last_draw, history=history, seed=seed,
        )
        whatif = generate_whatif_variants(last_draw=last_draw, history=history)
        return {
            "target_date": "22.04.2026",
            "mode": "swiss",
            "determination_piece": get_determination_piece(),
            "last_draw_bd": {
                "date": last_draw.get('date') if last_draw else None,
                "numbers": sorted(last_draw.get('numbers', [])) if last_draw else [],
                "lucky": last_draw.get('lucky_number') if last_draw else None,
                "replay": last_draw.get('replay_number') if last_draw else None,
            },
            "tickets": tickets,
            "whatif_broken_core": whatif,
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


class SwissCosmicEngineRequest(BaseModel):
    target_date: str      # 'dd.mm.yyyy'
    n_tickets: int = 12
    banned: List[int] = []


@api_router.post("/swiss-cosmic-engine")
async def swiss_cosmic_engine_post(req: SwissCosmicEngineRequest):
    """Run the full Swiss cosmic engine — all Session 14/15/16 laws."""
    try:
        from swiss_cosmic_engine import run_swiss_cosmic_engine
        result = await run_swiss_cosmic_engine(
            req.target_date, req.n_tickets, req.banned, db=db,
        )
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@api_router.get("/swiss-cosmic-engine/{target_date}")
async def swiss_cosmic_engine_get(target_date: str, n_tickets: int = 12):
    """GET variant — target_date dd.mm.yyyy."""
    try:
        from swiss_cosmic_engine import run_swiss_cosmic_engine
        result = await run_swiss_cosmic_engine(
            target_date, n_tickets, [], db=db,
        )
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@api_router.get("/swiss/session19")
async def swiss_session19_snapshot(target_date: str = ""):
    """Session 19: Dialect Ladder + Ghost-Echo + Slot-Reincarnation live state.

    Uses last 5 Swiss draws as the walking window. Returns full ledger
    (ladders, unresolved ghosts, mismatches, echo candidates, reincarnation
    fires) and a per-slot frame suggestion for the next draw.
    """
    try:
        from session19_dialect_ladder import (
            compute_session19_ledger, suggest_next_frame, score_session19,
        )
        history = await _load_swiss_history_sorted()
        if len(history) < 5:
            return {"error": "need ≥5 Swiss draws in db"}
        window = history[-5:]
        anchor_nums = sorted(window[0].get('numbers', []))
        recent_nums = [sorted(d.get('numbers', [])) for d in window]
        ledger = compute_session19_ledger(anchor_nums, recent_nums, 'swiss')
        frame = suggest_next_frame(ledger)
        # Demo scoring: 3 DJ-signature tickets
        demo_tickets = [
            {'mains': [2, 9, 16, 27, 33, 42], 'name': 'Dialect-Ladder-v1'},
            {'mains': [7, 14, 16, 24, 33, 39], 'name': 'HUGE-Twin-Ladder'},
            {'mains': [2, 12, 16, 29, 38, 42], 'name': 'Silent-Compass-Close'},
        ]
        for t in demo_tickets:
            b, tags = score_session19(t['mains'], ledger)
            t['session19_bonus'] = b
            t['fired_lenses'] = tags
        return {
            "target_date": target_date or "25.04.2026 (next Swiss)",
            "mode": "swiss",
            "window_start": window[0].get('date'),
            "window_end": window[-1].get('date'),
            "anchor_draw": anchor_nums,
            "recent_draws": [
                {"date": d.get('date'), "numbers": sorted(d.get('numbers', []))}
                for d in window
            ],
            "ledger": ledger,
            "frame": frame,
            "demo_tickets": demo_tickets,
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


async def _load_euro_history_sorted():
    """Load Euro draws chronologically oldest→newest."""
    from datetime import datetime as _dt
    draws = await db.euromillions_draws.find({}, {"_id": 0}).to_list(length=10000)
    def _pk(d):
        try:
            return _dt.strptime(d.get('date', ''), '%d.%m.%Y')
        except Exception:
            return _dt.min
    draws.sort(key=_pk)
    return draws


@api_router.get("/euro/session19")
async def euro_session19_snapshot(target_date: str = ""):
    """Session 19: Dialect Ladder + Ghost-Echo + Slot-Reincarnation for Euro.

    Uses last 5 Euro draws as the walking window. Mirrors the Swiss variant.
    Validates the DJ's canonical triangle (14→41→16 P2) live.
    """
    try:
        from session19_dialect_ladder import (
            compute_session19_ledger, suggest_next_frame, score_session19,
        )
        history = await _load_euro_history_sorted()
        if len(history) < 5:
            return {"error": "need ≥5 Euro draws in db"}
        window = history[-5:]
        anchor_nums = sorted(window[0].get('numbers', []))
        recent_nums = [sorted(d.get('numbers', [])) for d in window]
        ledger = compute_session19_ledger(anchor_nums, recent_nums, 'euro')
        frame = suggest_next_frame(ledger, silent_family={15, 17, 18, 27})
        # DJ's live call for 24.04.2026: P2=18 (hungry ghost from d5 Δ=-2 mismatch)
        dj_call_24_04 = {
            'target_date': '24.04.2026',
            'p2_ghost_call': 18,
            'rationale': 'Euro P2 raw-ghost walk d5=18, real landed 16 (Δ=-2). '
                         '18 is unresolved ghost AND RC0 P4 still-silent since 24.03.2026.',
        }
        return {
            "target_date": target_date or "24.04.2026 (next Euro)",
            "mode": "euro",
            "window_start": window[0].get('date'),
            "window_end": window[-1].get('date'),
            "anchor_draw": anchor_nums,
            "recent_draws": [
                {"date": d.get('date'), "numbers": sorted(d.get('numbers', []))}
                for d in window
            ],
            "ledger": ledger,
            "frame": frame,
            "dj_call_24_04": dj_call_24_04,
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


# Include the router in the main app
app.include_router(api_router)

# Include EuroMillions router
from euromillions_routes import create_euromillions_router
euromillions_router = create_euromillions_router(db)
app.include_router(euromillions_router)

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

@app.on_event("startup")
async def startup_create_indexes():
    """🚀 Ensure critical MongoDB indexes exist (per Emergent Support — production
    was timing out on active_users.distinct because no index on visitor_id).
    Runs as BACKGROUND task so it never blocks server startup.
    """
    async def _ensure_indexes():
        # Define indexes as (collection, key_spec, name) tuples.
        # Each is wrapped in try/except so one collision doesn't block the rest.
        targets = [
            (db.active_users, "visitor_id", "lj_visitor_id_idx"),
            (db.active_users, "last_seen", "lj_last_seen_idx"),
            (db.active_users, [("visitor_id", 1), ("last_seen", -1)], "lj_vid_last_seen_idx"),
            (db.generations, "visitor_id", "lj_gen_vid_idx"),
            (db.generations, "target_date", "lj_gen_target_date_idx"),
            (db.generations, "created_at", "lj_gen_created_at_idx"),
            (db.draws, "date", "lj_draws_date_idx"),
            (db.euromillions_draws, "date", "lj_euro_date_idx"),
        ]
        for coll, key, name in targets:
            try:
                await coll.create_index(key, name=name, background=True)
            except Exception as ix_err:
                msg = str(ix_err)
                if "already exists" in msg or "IndexOptionsConflict" in msg or "IndexKeySpecsConflict" in msg or "duplicate key" in msg.lower():
                    continue
                logger.warning(f"⚠️ [BG] Could not create index {name}: {msg[:200]}")
        # 🧹 Prune old active_users records (>24h) — keeps the collection lean
        # so the aggregation stays fast forever, even on production scale.
        try:
            from datetime import timedelta
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
            res = await db.active_users.delete_many({"last_seen": {"$lt": cutoff}})
            if res.deleted_count:
                logger.info(f"🧹 [BG] Pruned {res.deleted_count} stale active_users (>24h old)")
        except Exception as prune_err:
            logger.warning(f"⚠️ [BG] active_users prune failed (non-fatal): {str(prune_err)[:200]}")
        logger.info("🚀 [BG] MongoDB index pass complete (idempotent, safe)")

    asyncio.create_task(_ensure_indexes())
    logger.info("🚀 Index creation scheduled as BACKGROUND task — server ready immediately")

    # 🧹 Dedup + unique-index on euromillions_draws.date (Emergent Support 2026-06-08)
    async def _dedupe_euro_bg():
        try:
            from dedupe_euromillions import dedupe_and_index_euromillions
            res = await dedupe_and_index_euromillions(db)
            logger.info(f"🧹 [BG] Euro dedup pass complete: {res}")
        except Exception as e:
            logger.warning(f"⚠️ [BG] Euro dedup failed (non-fatal): {str(e)[:200]}")
    asyncio.create_task(_dedupe_euro_bg())


@app.on_event("startup")
async def startup_auto_seed():
    """🚀 Fire DB seeding in BACKGROUND so the server accepts requests
    immediately on cold start. (Per Emergent Support — production
    container was timing out on blocking startup work.)
    """
    async def _seed_in_background():
        try:
            # Check if Swiss Lotto draws collection is empty
            swiss_count = await db.draws.count_documents({})
            if swiss_count == 0:
                logger.info("🍀 Swiss Lotto draws collection empty - auto-seeding with real historical data...")
                from import_real_data import REAL_DRAWS
                docs = []
                seen = set()
                for date_str, numbers, lucky, replay in REAL_DRAWS:
                    if date_str in seen:
                        continue
                    seen.add(date_str)
                    if len(numbers) != 6:
                        continue
                    docs.append({
                        "id": str(uuid.uuid4()),
                        "date": date_str,
                        "numbers": sorted(numbers),
                        "lucky_number": lucky,
                        "replay_number": replay,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
                if docs:
                    await db.draws.insert_many(docs)
                swiss_count = await db.draws.count_documents({})
                logger.info(f"✅ Auto-seeded {swiss_count} REAL Swiss Lotto draws!")
            else:
                logger.info(f"🍀 Swiss Lotto: {swiss_count} draws already in database")

            # Check if EuroMillions draws collection is empty
            euro_count = await db.euromillions_draws.count_documents({})
            if euro_count == 0:
                logger.info("🇪🇺 EuroMillions draws collection empty - auto-seeding with real historical data...")
                try:
                    from euromillions_data_2012_2013 import EUROMILLIONS_DRAWS_2012_2013
                    from euromillions_data_2018_2020 import EUROMILLIONS_DRAWS_2018_2020
                    from euromillions_data_2021_2023 import EUROMILLIONS_DRAWS_2021_2023
                    from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
                    from euromillions_data_missing import EUROMILLIONS_DRAWS_MISSING

                    all_euro_draws = (
                        EUROMILLIONS_DRAWS_2012_2013 +
                        EUROMILLIONS_DRAWS_2018_2020 +
                        EUROMILLIONS_DRAWS_2021_2023 +
                        EUROMILLIONS_DRAWS_2024_2026 +
                        EUROMILLIONS_DRAWS_MISSING
                    )

                    docs = []
                    seen = set()
                    for draw in all_euro_draws:
                        if isinstance(draw, dict):
                            date_str = draw.get("date", "")
                            numbers = draw.get("numbers", [])
                            stars = draw.get("stars", [])
                        else:
                            date_str = draw[0]
                            numbers = draw[1]
                            stars = draw[2] if len(draw) > 2 else []

                        if date_str in seen:
                            continue
                        seen.add(date_str)
                        if len(numbers) != 5:
                            continue
                        docs.append({
                            "id": str(uuid.uuid4()),
                            "date": date_str,
                            "numbers": sorted(numbers),
                            "stars": sorted(stars) if stars else [],
                            "created_at": datetime.now(timezone.utc).isoformat()
                        })
                    if docs:
                        # Upsert by date so unique index never trips on re-run
                        from pymongo import UpdateOne
                        ops = [UpdateOne({"date": d["date"]}, {"$setOnInsert": d}, upsert=True) for d in docs if d.get("date")]
                        if ops:
                            await db.euromillions_draws.bulk_write(ops, ordered=False)
                    euro_count = await db.euromillions_draws.count_documents({})
                    logger.info(f"✅ Auto-seeded {euro_count} REAL EuroMillions draws!")
                except ImportError as e:
                    logger.warning(f"⚠️ Could not import EuroMillions data files: {e}")
            else:
                logger.info(f"🇪🇺 EuroMillions: {euro_count} draws already in database")

        except Exception as e:
            logger.error(f"❌ Auto-seed background task error: {e}")

    # 🚀 Fire-and-forget — never block server startup
    asyncio.create_task(_seed_in_background())
    logger.info("🚀 Auto-seed scheduled as BACKGROUND task — server ready immediately")

@app.on_event("shutdown")
async def shutdown_db_client():
    # Stop the scheduler
    if scheduler.running:
        scheduler.shutdown()
    client.close()

# ============ SCHEDULED AUTO-SYNC ============
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from lottery_fetcher import auto_sync_all
from pruner import prune_all as _prune_all_generations

# Initialize the scheduler
scheduler = AsyncIOScheduler()

async def scheduled_sync_job():
    """Background job to sync lottery results"""
    logger.info("⏰ Scheduled sync triggered!")
    try:
        stats = await auto_sync_all(db)
        if stats["total_new"] > 0:
            logger.info(f"✅ Scheduled sync: Added {stats['total_new']} new draws!")
        else:
            logger.info("✅ Scheduled sync: No new draws found")
    except Exception as e:
        logger.error(f"❌ Scheduled sync error: {e}")

async def scheduled_prune_job():
    """🎻 DJ-canon (29.04.2026): every day at 04:00 UTC, archive every
    hit-calculated generation into `historical_tickets`, THEN prune the
    live collections. Survives forever in the archive, lean in live.
    """
    logger.info("🧹 Scheduled prune triggered!")
    try:
        # Archive first so nothing is ever lost
        try:
            from historical_archive import archive_completed_draws
            arch = await archive_completed_draws(db)
            logger.info(
                "📜 Archived: swiss=%d euro=%d (skipped %d already-known)",
                arch["archived_swiss"], arch["archived_euro"],
                arch["skipped_already_archived"],
            )
        except Exception as ex:
            logger.error(f"❌ Archive step failed: {ex}")
        report = await _prune_all_generations(db, days=3, threshold=2)
        s = report["swiss"]; e = report["euro"]
        logger.info(
            "🧹 Prune done · Swiss: del=%d trim=%d removed=%d kept=%d · "
            "Euro: del=%d trim=%d removed=%d kept=%d",
            s["deleted_generations"], s["trimmed_generations"],
            s["tickets_removed"], s["tickets_kept"],
            e["deleted_generations"], e["trimmed_generations"],
            e["tickets_removed"], e["tickets_kept"],
        )
    except Exception as exc:
        logger.error(f"❌ Scheduled prune error: {exc}")

# Schedule syncs after draw times (draws typically at 20:30-21:00 CET)
# Swiss Lotto: Wednesday & Saturday at 21:30 CET
# EuroMillions: Tuesday & Friday at 21:30 CET

# Run sync at 22:00 CET (21:00 UTC in winter, 20:00 UTC in summer) to catch all results
# Using UTC times for consistency

# Tuesday 21:00 UTC - EuroMillions
scheduler.add_job(scheduled_sync_job, CronTrigger(day_of_week='tue', hour=21, minute=0), id='euro_tuesday')
# Wednesday 21:00 UTC - Swiss Lotto  
scheduler.add_job(scheduled_sync_job, CronTrigger(day_of_week='wed', hour=21, minute=0), id='swiss_wednesday')
# Friday 21:00 UTC - EuroMillions
scheduler.add_job(scheduled_sync_job, CronTrigger(day_of_week='fri', hour=21, minute=0), id='euro_friday')
# Saturday 21:00 UTC - Swiss Lotto
scheduler.add_job(scheduled_sync_job, CronTrigger(day_of_week='sat', hour=21, minute=0), id='swiss_saturday')

# 🧹 Daily prune at 04:00 UTC — keeps only ≥2-hit tickets after D+3
scheduler.add_job(scheduled_prune_job, CronTrigger(hour=4, minute=0), id='daily_prune')

# Also run once at startup (30 seconds after start to let everything initialize)
scheduler.add_job(scheduled_sync_job, 'date', run_date=datetime.now(timezone.utc).replace(microsecond=0) + __import__('datetime').timedelta(seconds=30), id='startup_sync')

@app.on_event("startup")
async def start_scheduler():
    """Start the APScheduler when the app starts"""
    scheduler.start()
    logger.info("📅 Scheduler started - Auto-sync scheduled for:")
    logger.info("   🇨🇭 Swiss Lotto: Wednesday & Saturday at 21:00 UTC")
    logger.info("   🇪🇺 EuroMillions: Tuesday & Friday at 21:00 UTC")

@app.on_event("startup")
async def sync_data_files_on_startup():
    """🚀 Sync static data files with latest from APIs — FIRED AS BACKGROUND TASK
    so the server accepts requests immediately on cold start. The external
    EuroMillions API call can hang on rate-limit (429) — never block boot.
    (Per Emergent Support — production was timing out here.)
    """
    async def _sync_in_background():
        try:
            from data_sync import startup_sync
            logger.info("🔄 [BG] Starting data file sync...")
            result = await startup_sync()
            if result.get("euromillions", {}).get("new", 0) > 0:
                logger.info(f"✅ [BG] Data sync complete: {result['euromillions']['new']} new EuroMillions draws added")
            else:
                logger.info("✅ [BG] Data files are up to date")
        except Exception as e:
            logger.error(f"❌ [BG] Data sync failed: {e}")

    # 🚀 Fire-and-forget — NEVER block server startup on external HTTP
    asyncio.create_task(_sync_in_background())
    logger.info("🚀 Data file sync scheduled as BACKGROUND task — server ready immediately")


@app.on_event("startup")
async def create_db_indexes():
    """Ensure MongoDB indexes exist for frequently queried fields."""
    from pymongo import ASCENDING, DESCENDING, IndexModel

    async def _safe_create(coll, models, label):
        try:
            await coll.create_indexes(models)
        except Exception as ix_err:
            msg = str(ix_err)
            # Benign — conflicting name on an already-existing equivalent index
            if "IndexOptionsConflict" in msg or "Index already exists" in msg or "IndexKeySpecsConflict" in msg:
                logger.info(f"ℹ️  Index for {label} already present (skipping)")
                return
            logger.warning(f"⚠️ Index creation for {label} failed (non-fatal): {msg[:200]}")

    try:
        await _safe_create(db.generations, [
            IndexModel([("target_date", ASCENDING), ("hits_calculated", ASCENDING)]),
            IndexModel([("visitor_id", ASCENDING), ("target_date", ASCENDING)]),
            IndexModel([("target_date", ASCENDING)]),
        ], "generations")
        await _safe_create(db.euromillions_generations, [
            IndexModel([("target_date", ASCENDING), ("hits_calculated", ASCENDING)]),
            IndexModel([("visitor_id", ASCENDING), ("target_date", ASCENDING)]),
        ], "euromillions_generations")
        await _safe_create(db.draws, [
            IndexModel([("date", ASCENDING)], unique=True),
        ], "draws")
        await _safe_create(db.euromillions_draws, [
            IndexModel([("date", ASCENDING)], unique=True),
        ], "euromillions_draws")
        await _safe_create(db.prediction_history, [
            IndexModel([("lottery_type", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("target_draw_date", ASCENDING)]),
        ], "prediction_history")
        await _safe_create(db.promo_redeemed, [
            IndexModel([("visitor_id", ASCENDING)], unique=True),
        ], "promo_redeemed")
        await _safe_create(db.hunt_boxes, [
            IndexModel([("id", ASCENDING)], unique=True),
        ], "hunt_boxes")
        logger.info("✅ DB indexes ensured")
    except Exception as e:
        logger.error(f"❌ DB index creation failed: {e}")

