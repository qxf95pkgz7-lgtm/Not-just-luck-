"""
EuroMillions Pattern Analyzer - "Lucky Stars"
Adapted from Swiss Lotto "Lucky Jack" with patterns suited for 5/50 + 2/12 format
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from collections import Counter, defaultdict
import random as rnd
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="EuroMillions Pattern Analyzer API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "euromillions_db")
client: AsyncIOMotorClient = None
db = None

# Constants for EuroMillions
MAX_NUMBER = 50  # Main numbers 1-50
MAX_STAR = 12    # Star numbers 1-12
MAIN_COUNT = 5   # 5 main numbers
STAR_COUNT = 2   # 2 star numbers

# Number families for EuroMillions (1-50)
FAMILIES = {
    1: list(range(1, 10)),    # 1-9
    2: list(range(10, 20)),   # 10-19
    3: list(range(20, 30)),   # 20-29
    4: list(range(30, 40)),   # 30-39
    5: list(range(40, 51)),   # 40-50
}

# Circle partners (+25 in EuroMillions instead of +21)
def get_circle_partner(n: int) -> int:
    partner = n + 25
    if partner > MAX_NUMBER:
        partner -= MAX_NUMBER
    return partner


class PredictionRequest(BaseModel):
    birthday: Optional[str] = None
    name: Optional[str] = None
    locked_positions: Optional[Dict[str, int]] = None
    num_tickets: int = 1


class PredictionResponse(BaseModel):
    numbers: List[int]
    stars: List[int]
    patterns_used: List[str]
    confidence: float
    position_reasons: Dict[str, str]


@app.on_event("startup")
async def startup_db_client():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Seed data if collection is empty
    count = await db.draws.count_documents({})
    if count == 0:
        await seed_database()
    print(f"Connected to MongoDB. {await db.draws.count_documents({})} draws loaded.")


@app.on_event("shutdown")
async def shutdown_db_client():
    global client
    if client:
        client.close()


async def seed_database():
    """Seed the database with historical EuroMillions draws"""
    from seed_data import EUROMILLIONS_DRAWS
    
    documents = []
    for draw in EUROMILLIONS_DRAWS:
        documents.append({
            "date": draw["date"],
            "numbers": sorted(draw["numbers"]),
            "stars": sorted(draw["stars"]),
            "created_at": datetime.now(timezone.utc)
        })
    
    if documents:
        await db.draws.insert_many(documents)
        print(f"Seeded {len(documents)} EuroMillions draws")


async def get_all_draws() -> List[dict]:
    """Get all draws sorted by date descending"""
    cursor = db.draws.find({}, {"_id": 0}).sort("date", -1)
    return await cursor.to_list(length=None)


async def get_recent_draws(limit: int = 20) -> List[dict]:
    """Get most recent draws"""
    cursor = db.draws.find({}, {"_id": 0}).sort("date", -1).limit(limit)
    return await cursor.to_list(length=None)


# ============== PATTERN ALGORITHMS ==============

def pattern_position_frequency(draws: List[dict], position: int) -> Dict[int, float]:
    """Analyze frequency of numbers at specific positions (P1-P5)"""
    counts = Counter()
    for draw in draws:
        if position < len(draw["numbers"]):
            counts[draw["numbers"][position]] += 1
    
    total = sum(counts.values())
    return {num: count/total for num, count in counts.items()} if total > 0 else {}


def pattern_star_frequency(draws: List[dict]) -> Dict[int, float]:
    """Analyze frequency of star numbers"""
    counts = Counter()
    for draw in draws:
        for star in draw["stars"]:
            counts[star] += 1
    
    total = sum(counts.values())
    return {num: count/total for num, count in counts.items()} if total > 0 else {}


def pattern_family_spread(draws: List[dict]) -> Dict[int, float]:
    """Analyze family distribution patterns"""
    family_combos = Counter()
    for draw in draws:
        families_used = tuple(sorted(set(
            fam for fam, nums in FAMILIES.items() 
            for n in draw["numbers"] if n in nums
        )))
        family_combos[families_used] += 1
    
    total = sum(family_combos.values())
    return {combo: count/total for combo, count in family_combos.items()} if total > 0 else {}


def pattern_consecutive_pairs(draws: List[dict]) -> float:
    """Calculate probability of consecutive number pairs"""
    pairs_found = 0
    for draw in draws:
        nums = sorted(draw["numbers"])
        for i in range(len(nums) - 1):
            if nums[i+1] - nums[i] == 1:
                pairs_found += 1
                break
    return pairs_found / len(draws) if draws else 0


def pattern_sum_range(draws: List[dict]) -> tuple:
    """Analyze typical sum ranges for winning tickets"""
    sums = [sum(d["numbers"]) for d in draws]
    return min(sums), max(sums), sum(sums) / len(sums) if sums else (0, 0, 0)


def pattern_gap_analysis(draws: List[dict]) -> Dict[int, int]:
    """How many draws since each number appeared"""
    last_seen = {i: float('inf') for i in range(1, MAX_NUMBER + 1)}
    
    for idx, draw in enumerate(draws):
        for num in draw["numbers"]:
            if last_seen[num] == float('inf'):
                last_seen[num] = idx
    
    return {num: gap if gap != float('inf') else len(draws) 
            for num, gap in last_seen.items()}


def pattern_star_gap_analysis(draws: List[dict]) -> Dict[int, int]:
    """How many draws since each star appeared"""
    last_seen = {i: float('inf') for i in range(1, MAX_STAR + 1)}
    
    for idx, draw in enumerate(draws):
        for star in draw["stars"]:
            if last_seen[star] == float('inf'):
                last_seen[star] = idx
    
    return {num: gap if gap != float('inf') else len(draws) 
            for num, gap in last_seen.items()}


def pattern_decade_distribution(draws: List[dict]) -> Dict[str, float]:
    """Analyze distribution across decades (1-10, 11-20, etc.)"""
    decades = defaultdict(int)
    total = 0
    
    for draw in draws:
        for num in draw["numbers"]:
            decade = ((num - 1) // 10) + 1
            decades[decade] += 1
            total += 1
    
    return {f"D{d}": count/total for d, count in decades.items()} if total > 0 else {}


def pattern_odd_even_ratio(draws: List[dict]) -> Dict[str, float]:
    """Analyze odd/even number distribution"""
    ratios = Counter()
    
    for draw in draws:
        odds = sum(1 for n in draw["numbers"] if n % 2 == 1)
        evens = 5 - odds
        ratios[f"{odds}O-{evens}E"] += 1
    
    total = sum(ratios.values())
    return {r: count/total for r, count in ratios.items()} if total > 0 else {}


def pattern_high_low_ratio(draws: List[dict]) -> Dict[str, float]:
    """Analyze high (26-50) vs low (1-25) distribution"""
    ratios = Counter()
    
    for draw in draws:
        highs = sum(1 for n in draw["numbers"] if n > 25)
        lows = 5 - highs
        ratios[f"{lows}L-{highs}H"] += 1
    
    total = sum(ratios.values())
    return {r: count/total for r, count in ratios.items()} if total > 0 else {}


def pattern_mirror_numbers(draws: List[dict]) -> Dict[int, float]:
    """Check for mirror patterns (e.g., 12 and 21, 13 and 31)"""
    mirror_pairs = Counter()
    
    for draw in draws:
        nums = set(draw["numbers"])
        for n in nums:
            if n >= 10:
                mirror = int(str(n)[::-1])
                if mirror != n and 1 <= mirror <= 50 and mirror in nums:
                    mirror_pairs[tuple(sorted([n, mirror]))] += 1
    
    total = sum(mirror_pairs.values())
    return dict(mirror_pairs)


def pattern_circle_partners(draws: List[dict]) -> float:
    """Check frequency of circle partner pairs (+25)"""
    found = 0
    for draw in draws:
        nums = set(draw["numbers"])
        for n in nums:
            partner = get_circle_partner(n)
            if partner in nums:
                found += 1
                break
    return found / len(draws) if draws else 0


def pattern_star_sum(draws: List[dict]) -> Dict[int, float]:
    """Analyze sum of star numbers"""
    sums = Counter()
    for draw in draws:
        sums[sum(draw["stars"])] += 1
    
    total = sum(sums.values())
    return {s: count/total for s, count in sums.items()} if total > 0 else {}


def pattern_number_pairs(draws: List[dict]) -> Dict[tuple, int]:
    """Find frequently appearing number pairs"""
    pairs = Counter()
    
    for draw in draws:
        nums = draw["numbers"]
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                pairs[tuple(sorted([nums[i], nums[j]]))] += 1
    
    # Return top 20 pairs
    return dict(pairs.most_common(20))


def pattern_date_connection(draws: List[dict], today: datetime) -> List[int]:
    """Numbers connected to today's date"""
    day = today.day
    month = today.month
    year = today.year % 100
    
    candidates = [day, month]
    if year <= 50:
        candidates.append(year)
    
    # Add transformations
    if day + month <= 50:
        candidates.append(day + month)
    if abs(day - month) >= 1:
        candidates.append(abs(day - month))
    
    return [c for c in candidates if 1 <= c <= 50]


# ============== MASTER PREDICTOR ==============

async def master_predictor(
    draws: List[dict],
    birthday: Optional[str] = None,
    name: Optional[str] = None,
    locked_positions: Optional[Dict[str, int]] = None,
    ticket_index: int = 0
) -> PredictionResponse:
    """
    Master prediction algorithm combining multiple patterns for EuroMillions
    """
    patterns_used = []
    position_reasons = {}
    candidates = {i: [] for i in range(5)}  # 5 positions for main numbers
    star_candidates = []
    
    if not draws:
        # Random fallback
        nums = sorted(rnd.sample(range(1, 51), 5))
        stars = sorted(rnd.sample(range(1, 13), 2))
        return PredictionResponse(
            numbers=nums,
            stars=stars,
            patterns_used=["Random (no data)"],
            confidence=0.1,
            position_reasons={}
        )
    
    # Initialize locked positions
    locked = {}
    if locked_positions:
        for pos_key, value in locked_positions.items():
            pos_idx = int(pos_key.replace("P", "")) - 1
            if 0 <= pos_idx < 5 and 1 <= value <= 50:
                locked[pos_idx] = value
    
    # === PATTERN 1: Position Frequency Analysis ===
    for pos in range(5):
        if pos not in locked:
            freq = pattern_position_frequency(draws, pos)
            top_nums = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)[:10]
            candidates[pos].extend(top_nums)
    patterns_used.append("Position Frequency")
    
    # === PATTERN 2: Gap Analysis (due numbers) ===
    gaps = pattern_gap_analysis(draws)
    due_numbers = sorted(gaps.keys(), key=lambda x: gaps[x], reverse=True)[:15]
    for pos in range(5):
        if pos not in locked:
            candidates[pos].extend(due_numbers[:5])
    patterns_used.append("Gap Analysis")
    
    # === PATTERN 3: Family Spread ===
    # Ensure good family coverage
    family_nums = []
    for fam_id, fam_nums in FAMILIES.items():
        family_nums.append(rnd.choice(fam_nums))
    for pos in range(5):
        if pos not in locked:
            candidates[pos].extend(family_nums)
    patterns_used.append("Family Spread")
    
    # === PATTERN 4: Recent Draw Analysis ===
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
    
    # === PATTERN 5: Consecutive Pair Pattern ===
    consec_rate = pattern_consecutive_pairs(draws)
    if consec_rate > 0.4 and rnd.random() < consec_rate:
        base = rnd.randint(5, 45)
        for pos in [1, 2]:
            if pos not in locked:
                candidates[pos].append(base)
                candidates[pos].append(base + 1)
        patterns_used.append(f"Consecutive Pairs ({consec_rate:.1%})")
    
    # === PATTERN 6: Sum Range Validation ===
    min_sum, max_sum, avg_sum = pattern_sum_range(draws)
    patterns_used.append(f"Sum Range ({int(min_sum)}-{int(max_sum)})")
    
    # === PATTERN 7: Circle Partners ===
    circle_rate = pattern_circle_partners(draws)
    if rnd.random() < circle_rate:
        base = rnd.randint(1, 25)
        partner = get_circle_partner(base)
        candidates[0].append(base)
        candidates[4].append(partner)
        patterns_used.append(f"Circle Partners (+25, {circle_rate:.1%})")
    
    # === PATTERN 8: Odd/Even Balance ===
    odd_even = pattern_odd_even_ratio(draws)
    best_ratio = max(odd_even.keys(), key=lambda x: odd_even[x]) if odd_even else "3O-2E"
    patterns_used.append(f"Odd/Even ({best_ratio})")
    
    # === PATTERN 9: High/Low Balance ===
    high_low = pattern_high_low_ratio(draws)
    best_hl = max(high_low.keys(), key=lambda x: high_low[x]) if high_low else "3L-2H"
    patterns_used.append(f"High/Low ({best_hl})")
    
    # === PATTERN 10: Decade Distribution ===
    decades = pattern_decade_distribution(draws)
    patterns_used.append("Decade Distribution")
    
    # === PATTERN 11: Date Connection ===
    today = datetime.now()
    date_nums = pattern_date_connection(draws, today)
    for pos in range(5):
        if pos not in locked:
            candidates[pos].extend(date_nums)
    if date_nums:
        patterns_used.append(f"Date Magic ({today.strftime('%d.%m')})")
    
    # === PATTERN 12: Birthday Integration ===
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
    
    # === PATTERN 13: Name Numerology ===
    if name:
        name_values = [ord(c.upper()) - 64 for c in name if c.isalpha()]
        name_sum = sum(name_values) % 50
        if name_sum == 0:
            name_sum = 50
        for pos in range(5):
            if pos not in locked:
                candidates[pos].append(name_sum)
        patterns_used.append(f"Name Energy ({name})")
    
    # === STAR NUMBER PATTERNS ===
    
    # Star frequency
    star_freq = pattern_star_frequency(draws)
    top_stars = sorted(star_freq.keys(), key=lambda x: star_freq.get(x, 0), reverse=True)[:6]
    star_candidates.extend(top_stars)
    
    # Star gap analysis
    star_gaps = pattern_star_gap_analysis(draws)
    due_stars = sorted(star_gaps.keys(), key=lambda x: star_gaps[x], reverse=True)[:4]
    star_candidates.extend(due_stars)
    
    # Star sum pattern
    star_sums = pattern_star_sum(draws)
    target_sum = max(star_sums.keys(), key=lambda x: star_sums.get(x, 0)) if star_sums else 13
    patterns_used.append(f"Star Sum Target ({target_sum})")
    
    # === BUILD FINAL NUMBERS ===
    final_numbers = [0] * 5
    used = set()
    
    # First, place locked numbers
    for pos, num in locked.items():
        final_numbers[pos] = num
        used.add(num)
        position_reasons[f"P{pos+1}"] = f"Locked by user"
    
    # Then fill remaining positions
    for pos in range(5):
        if pos in locked:
            continue
            
        # Score candidates
        pos_candidates = candidates[pos]
        scored = Counter(pos_candidates)
        
        # Add ticket variation
        for num in rnd.sample(range(1, 51), 5):
            scored[num] += ticket_index * 0.1
        
        # Select best unused
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
    
    # Sort numbers
    final_numbers = sorted(final_numbers)
    
    # === VALIDATE SUM ===
    current_sum = sum(final_numbers)
    attempts = 0
    while (current_sum < min_sum * 0.9 or current_sum > max_sum * 1.1) and attempts < 10:
        # Adjust if outside typical range
        if current_sum < min_sum * 0.9:
            # Replace smallest with higher
            idx = 0
            new_num = rnd.randint(30, 50)
            while new_num in final_numbers:
                new_num = rnd.randint(30, 50)
            final_numbers[idx] = new_num
        else:
            # Replace largest with lower
            idx = 4
            new_num = rnd.randint(1, 20)
            while new_num in final_numbers:
                new_num = rnd.randint(1, 20)
            final_numbers[idx] = new_num
        
        final_numbers = sorted(final_numbers)
        current_sum = sum(final_numbers)
        attempts += 1
    
    # === SELECT STARS ===
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
    
    # Validate star sum
    if target_sum and abs(sum(final_stars) - target_sum) > 5:
        # Try to adjust
        available_stars = [s for s in range(1, 13) if s not in final_stars]
        for s in available_stars:
            if abs(final_stars[0] + s - target_sum) < abs(sum(final_stars) - target_sum):
                final_stars[1] = s
                break
    
    final_stars = sorted(final_stars)
    
    # Calculate confidence
    base_confidence = 0.25 + (len(patterns_used) * 0.03)
    confidence = min(0.85, base_confidence)
    
    return PredictionResponse(
        numbers=final_numbers,
        stars=final_stars,
        patterns_used=patterns_used,
        confidence=confidence,
        position_reasons=position_reasons
    )


# ============== API ENDPOINTS ==============

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "EuroMillions Pattern Analyzer"}


@app.get("/api/draws")
async def get_draws(limit: int = 50):
    """Get historical draws"""
    draws = await get_recent_draws(limit)
    return {"draws": draws, "count": len(draws)}


@app.get("/api/stats")
async def get_stats():
    """Get statistical analysis"""
    draws = await get_all_draws()
    
    if not draws:
        return {"error": "No draws available"}
    
    # Number frequency
    num_freq = Counter()
    for d in draws:
        for n in d["numbers"]:
            num_freq[n] += 1
    
    # Star frequency
    star_freq = Counter()
    for d in draws:
        for s in d["stars"]:
            star_freq[s] += 1
    
    # Gaps
    gaps = pattern_gap_analysis(draws)
    star_gaps = pattern_star_gap_analysis(draws)
    
    # Sum stats
    min_sum, max_sum, avg_sum = pattern_sum_range(draws)
    
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
    }


@app.post("/api/master-predictor")
async def predict(request: PredictionRequest):
    """Generate predictions using master algorithm"""
    draws = await get_all_draws()
    
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
            "numbers": prediction.numbers,
            "stars": prediction.stars,
            "patterns_used": prediction.patterns_used,
            "confidence": prediction.confidence,
            "position_reasons": prediction.position_reasons,
        })
    
    # Sort by confidence
    tickets.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Calculate price (EuroMillions is €2.50 per ticket)
    price_per_ticket = 2.50
    total_price = len(tickets) * price_per_ticket
    
    return {
        "tickets": tickets,
        "total_tickets": len(tickets),
        "price_per_ticket": price_per_ticket,
        "total_price": total_price,
        "currency": "EUR"
    }


@app.get("/api/analyze-ticket")
async def analyze_ticket(numbers: str, stars: str):
    """Analyze a user's ticket against historical patterns"""
    try:
        nums = [int(n.strip()) for n in numbers.split(",")]
        star_nums = [int(s.strip()) for s in stars.split(",")]
        
        if len(nums) != 5 or not all(1 <= n <= 50 for n in nums):
            raise ValueError("Need exactly 5 numbers between 1-50")
        if len(star_nums) != 2 or not all(1 <= s <= 12 for s in star_nums):
            raise ValueError("Need exactly 2 stars between 1-12")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    draws = await get_all_draws()
    nums = sorted(nums)
    star_nums = sorted(star_nums)
    
    # Analyze
    analysis = {
        "numbers": nums,
        "stars": star_nums,
        "sum": sum(nums),
        "star_sum": sum(star_nums),
        "insights": []
    }
    
    # Sum range check
    min_sum, max_sum, avg_sum = pattern_sum_range(draws)
    if min_sum <= sum(nums) <= max_sum:
        analysis["insights"].append(f"✓ Sum ({sum(nums)}) is within typical range ({int(min_sum)}-{int(max_sum)})")
    else:
        analysis["insights"].append(f"⚠ Sum ({sum(nums)}) is outside typical range ({int(min_sum)}-{int(max_sum)})")
    
    # Consecutive check
    has_consecutive = any(nums[i+1] - nums[i] == 1 for i in range(len(nums)-1))
    consec_rate = pattern_consecutive_pairs(draws)
    if has_consecutive:
        analysis["insights"].append(f"✓ Has consecutive pair (appears in {consec_rate:.0%} of draws)")
    
    # Family spread
    families_used = set()
    for fam_id, fam_nums in FAMILIES.items():
        if any(n in fam_nums for n in nums):
            families_used.add(fam_id)
    analysis["insights"].append(f"Covers {len(families_used)}/5 number families")
    
    # Odd/Even
    odds = sum(1 for n in nums if n % 2 == 1)
    evens = 5 - odds
    odd_even = pattern_odd_even_ratio(draws)
    ratio_key = f"{odds}O-{evens}E"
    ratio_freq = odd_even.get(ratio_key, 0)
    analysis["insights"].append(f"Odd/Even ratio {ratio_key} (appears in {ratio_freq:.0%} of draws)")
    
    # High/Low
    highs = sum(1 for n in nums if n > 25)
    lows = 5 - highs
    analysis["insights"].append(f"Low/High ratio: {lows}L-{highs}H")
    
    # Gap analysis - how overdue are these numbers?
    gaps = pattern_gap_analysis(draws)
    avg_gap = sum(gaps.get(n, 0) for n in nums) / 5
    analysis["insights"].append(f"Average gap for these numbers: {avg_gap:.1f} draws")
    
    # Star analysis
    star_gaps = pattern_star_gap_analysis(draws)
    star_avg_gap = sum(star_gaps.get(s, 0) for s in star_nums) / 2
    analysis["insights"].append(f"Average gap for stars: {star_avg_gap:.1f} draws")
    
    # Calculate overall score
    score = 50  # Base score
    if min_sum <= sum(nums) <= max_sum:
        score += 15
    if len(families_used) >= 4:
        score += 10
    if 0.1 <= ratio_freq <= 0.4:
        score += 10
    if has_consecutive and consec_rate > 0.3:
        score += 5
    if avg_gap > 5:
        score += 10  # Overdue numbers
    
    analysis["score"] = min(100, score)
    analysis["rating"] = "Excellent" if score >= 80 else "Good" if score >= 60 else "Average" if score >= 40 else "Poor"
    
    return analysis


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
