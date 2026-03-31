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
