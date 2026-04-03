from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from collections import defaultdict, Counter
import os
import random

app = FastAPI(title="EuroMillions Pattern Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "euromillions_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

api_router = APIRouter(prefix="/api")

# ============================================================
# EUROMILLIONS STRUCTURE:
# - 5 main numbers from 1-50
# - 2 star numbers from 1-12
# ============================================================

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "app": "EuroMillions Pattern Analyzer"}

@api_router.get("/draws")
async def get_draws(limit: int = 500):
    """Get historical EuroMillions draws"""
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).limit(limit).to_list(limit)
    return draws

@api_router.get("/stats")
async def get_stats():
    """Get statistics about the draws"""
    draws = await db.draws.find({}, {"_id": 0}).to_list(2000)
    
    if not draws:
        return {"error": "No draws in database", "total_draws": 0}
    
    # Main numbers frequency (1-50)
    main_freq = Counter()
    # Star numbers frequency (1-12)
    star_freq = Counter()
    
    for d in draws:
        for n in d.get('numbers', []):
            main_freq[n] += 1
        for s in d.get('stars', []):
            star_freq[s] += 1
    
    return {
        "total_draws": len(draws),
        "date_range": {
            "first": draws[-1].get('date') if draws else None,
            "last": draws[0].get('date') if draws else None
        },
        "main_numbers": {
            "hot": main_freq.most_common(10),
            "cold": main_freq.most_common()[-10:]
        },
        "stars": {
            "hot": star_freq.most_common(5),
            "cold": star_freq.most_common()[-5:]
        }
    }

@api_router.get("/master-predictor")
async def get_master_prediction(
    lock_p1: int = None,
    lock_p2: int = None,
    lock_p3: int = None,
    lock_p4: int = None,
    lock_p5: int = None,
    lock_star1: int = None,
    lock_star2: int = None,
    num_tickets: int = 1
):
    """
    EUROMILLIONS MASTER PREDICTOR
    - 5 main numbers from 1-50
    - 2 star numbers from 1-12
    - Adapted patterns from Swiss Lotto
    """
    
    # Validate num_tickets
    num_tickets = max(1, min(20, num_tickets))
    
    # Parse locked positions for main numbers
    locked_main = {}
    lock_params = [lock_p1, lock_p2, lock_p3, lock_p4, lock_p5]
    for i, lock_val in enumerate(lock_params):
        if lock_val is not None and 1 <= lock_val <= 50:
            locked_main[i] = lock_val
    
    # Parse locked stars
    locked_stars = {}
    if lock_star1 is not None and 1 <= lock_star1 <= 12:
        locked_stars[0] = lock_star1
    if lock_star2 is not None and 1 <= lock_star2 <= 12:
        locked_stars[1] = lock_star2
    
    # Validate locks
    if len(locked_main) > 4:
        return {"error": "Maximum 4 locked main positions allowed"}
    locked_main_nums = list(locked_main.values())
    if len(locked_main_nums) != len(set(locked_main_nums)):
        return {"error": "Duplicate locked main numbers not allowed"}
    
    locked_star_nums = list(locked_stars.values())
    if len(locked_star_nums) != len(set(locked_star_nums)):
        return {"error": "Duplicate locked star numbers not allowed"}
    
    # Get historical draws
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).to_list(2000)
    
    if not draws:
        # No data yet - return random prediction
        main_nums = sorted(random.sample(range(1, 51), 5))
        star_nums = sorted(random.sample(range(1, 13), 2))
        return {
            "prediction_date": datetime.now(timezone.utc).isoformat(),
            "main_prediction": main_nums,
            "star_prediction": star_nums,
            "message": "No historical data - using random prediction. Please import data.",
            "confidence": 0
        }
    
    all_draws_sorted = draws  # Already sorted by date desc
    last_draw = draws[0] if draws else None
    
    # Initialize scores for main numbers (1-50)
    scores = {n: {"score": 0, "reasons": []} for n in range(1, 51)}
    
    # Initialize scores for star numbers (1-12)
    star_scores = {n: {"score": 0, "reasons": []} for n in range(1, 13)}
    
    # ============================================================
    # PATTERN 1: HOT NUMBERS (Last 20 draws)
    # ============================================================
    last_20 = all_draws_sorted[:20]
    main_freq = Counter()
    star_freq = Counter()
    
    for d in last_20:
        for n in d.get('numbers', []):
            main_freq[n] += 1
        for s in d.get('stars', []):
            star_freq[s] += 1
    
    for num, freq in main_freq.most_common(15):
        boost = freq * 3
        scores[num]["score"] += boost
        scores[num]["reasons"].append(f"🔥 Hot: {freq}x in last 20")
    
    for star, freq in star_freq.most_common(5):
        boost = freq * 4
        star_scores[star]["score"] += boost
        star_scores[star]["reasons"].append(f"⭐ Hot star: {freq}x in last 20")
    
    # ============================================================
    # PATTERN 2: DUE NUMBERS (Not seen in last 10 draws)
    # ============================================================
    recent_main = set()
    recent_stars = set()
    for d in all_draws_sorted[:10]:
        recent_main.update(d.get('numbers', []))
        recent_stars.update(d.get('stars', []))
    
    for num in range(1, 51):
        if num not in recent_main:
            scores[num]["score"] += 8
            scores[num]["reasons"].append(f"⏰ Due: not in last 10")
    
    for star in range(1, 13):
        if star not in recent_stars:
            star_scores[star]["score"] += 10
            star_scores[star]["reasons"].append(f"⏰ Due star: not in last 10")
    
    # ============================================================
    # PATTERN 3: POSITION ANALYSIS (P1-P5 historical frequency)
    # ============================================================
    position_freq = {i: Counter() for i in range(5)}
    for d in all_draws_sorted[:200]:
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 5:
            for i, n in enumerate(nums):
                position_freq[i][n] += 1
    
    position_names = ["P1", "P2", "P3", "P4", "P5"]
    for pos in range(5):
        for num, freq in position_freq[pos].most_common(8):
            boost = 6 + freq // 5
            scores[num]["score"] += boost
            scores[num]["reasons"].append(f"📍 {position_names[pos]} favorite: {freq}x")
    
    # ============================================================
    # PATTERN 4: P3-P4 DANCE (middle positions)
    # ============================================================
    p3_p4_pairs = Counter()
    for d in all_draws_sorted[:100]:
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 5:
            p3_p4_pairs[(nums[2], nums[3])] += 1
    
    for (p3, p4), count in p3_p4_pairs.most_common(10):
        scores[p3]["score"] += count * 2
        scores[p4]["score"] += count * 2
        scores[p3]["reasons"].append(f"💃 P3-P4 pair: {p3}-{p4} ({count}x)")
    
    # ============================================================
    # PATTERN 5: P4-P5 DANCE (high positions)
    # ============================================================
    p4_p5_pairs = Counter()
    for d in all_draws_sorted[:100]:
        nums = sorted(d.get('numbers', []))
        if len(nums) >= 5:
            p4_p5_pairs[(nums[3], nums[4])] += 1
    
    for (p4, p5), count in p4_p5_pairs.most_common(10):
        scores[p4]["score"] += count * 2
        scores[p5]["score"] += count * 2
        scores[p4]["reasons"].append(f"💃 P4-P5 pair: {p4}-{p5} ({count}x)")
    
    # ============================================================
    # PATTERN 6: DECADE CLUSTER
    # ============================================================
    if last_draw:
        last_nums = last_draw.get('numbers', [])
        decade_counts = Counter(n // 10 for n in last_nums)
        
        for decade, count in decade_counts.items():
            if count >= 2:
                boost = count * 5
                for num in range(max(1, decade * 10), min(decade * 10 + 10, 51)):
                    scores[num]["score"] += boost
                    scores[num]["reasons"].append(f"🎯 Decade cluster: {count}x in {decade}0s")
    
    # ============================================================
    # PATTERN 7: DIGIT ECHO
    # ============================================================
    if last_draw:
        last_nums = last_draw.get('numbers', [])
        last_digits = set()
        for n in last_nums:
            for d in str(n):
                if d != '0':
                    last_digits.add(int(d))
        
        for digit in last_digits:
            boost = 8 if digit <= 3 else 4
            for num in range(1, 51):
                if str(digit) in str(num):
                    scores[num]["score"] += boost
                    scores[num]["reasons"].append(f"🔊 Digit echo: {digit}")
    
    # ============================================================
    # PATTERN 8: FAMILY SYSTEM (numbers ending in same digit)
    # ============================================================
    if last_draw:
        last_nums = last_draw.get('numbers', [])
        families_present = set(n % 10 for n in last_nums)
        
        for family in families_present:
            # Hungry family members
            family_members = [n for n in range(1, 51) if n % 10 == family and n not in last_nums]
            for num in family_members[:3]:
                scores[num]["score"] += 10
                scores[num]["reasons"].append(f"👨‍👩‍👧 Hungry family {family}: {num}")
    
    # ============================================================
    # PATTERN 9: DATE PATTERN
    # ============================================================
    today = datetime.now()
    day = today.day
    month = today.month
    
    if 1 <= day <= 50:
        scores[day]["score"] += 12
        scores[day]["reasons"].append(f"📅 Today's day: {day}")
    
    if 1 <= month <= 12:
        star_scores[month]["score"] += 15
        star_scores[month]["reasons"].append(f"📅 Today's month: {month}")
    
    day_month_sum = day + month
    if 1 <= day_month_sum <= 50:
        scores[day_month_sum]["score"] += 8
        scores[day_month_sum]["reasons"].append(f"📅 Day+Month: {day}+{month}={day_month_sum}")
    
    # ============================================================
    # PATTERN 10: STAR NUMBER PAIRS
    # ============================================================
    star_pairs = Counter()
    for d in all_draws_sorted[:100]:
        stars = sorted(d.get('stars', []))
        if len(stars) >= 2:
            star_pairs[(stars[0], stars[1])] += 1
    
    for (s1, s2), count in star_pairs.most_common(8):
        star_scores[s1]["score"] += count * 3
        star_scores[s2]["score"] += count * 3
        star_scores[s1]["reasons"].append(f"⭐ Star pair: {s1}-{s2} ({count}x)")
    
    # ============================================================
    # PATTERN 11: CONSECUTIVE NUMBERS
    # ============================================================
    consecutive_freq = Counter()
    for d in all_draws_sorted[:100]:
        nums = sorted(d.get('numbers', []))
        for i in range(len(nums) - 1):
            if nums[i+1] == nums[i] + 1:
                consecutive_freq[(nums[i], nums[i+1])] += 1
    
    for (n1, n2), count in consecutive_freq.most_common(10):
        scores[n1]["score"] += count * 2
        scores[n2]["score"] += count * 2
        scores[n1]["reasons"].append(f"👥 Consecutive: {n1}-{n2} ({count}x)")
    
    # ============================================================
    # PATTERN 12: P1+P5 MAGIC SUM
    # ============================================================
    if last_draw:
        last_nums = sorted(last_draw.get('numbers', []))
        if len(last_nums) >= 5:
            p1, p5 = last_nums[0], last_nums[4]
            magic_sum = p1 + p5
            
            if 1 <= magic_sum <= 50:
                scores[magic_sum]["score"] += 10
                scores[magic_sum]["reasons"].append(f"✨ Magic sum: {p1}+{p5}={magic_sum}")
            
            # Digits of magic sum
            for d in str(magic_sum):
                if d != '0':
                    digit = int(d)
                    for num in range(1, 51):
                        if str(digit) in str(num):
                            scores[num]["score"] += 3
                            scores[num]["reasons"].append(f"✨ Magic digit: {digit}")
    
    # ============================================================
    # COMPILE MAIN NUMBER PREDICTIONS
    # ============================================================
    locked_main_set = set(locked_main.values())
    ranked_main = sorted(
        [(n, data) for n, data in scores.items() if n not in locked_main_set],
        key=lambda x: x[1]["score"],
        reverse=True
    )
    
    positions_to_fill = 5 - len(locked_main)
    
    # Weighted random selection from top candidates
    top_candidates = ranked_main[:20]
    if len(top_candidates) >= positions_to_fill:
        weights = [max(1, data["score"]) for n, data in top_candidates]
        selected = []
        selected_indices = set()
        
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
                    selected.append({"number": n, "score": data["score"], "reasons": data["reasons"][:4]})
                    selected_indices.add(idx)
                    break
        main_picks = selected
    else:
        main_picks = [{"number": n, "score": data["score"], "reasons": data["reasons"][:4]} for n, data in ranked_main[:positions_to_fill]]
    
    # Build final main numbers
    final_main = [None] * 5
    for pos, num in locked_main.items():
        final_main[pos] = {"number": num, "score": 999, "reasons": ["🔒 Locked"], "locked": True}
    
    pick_idx = 0
    for i in range(5):
        if final_main[i] is None and pick_idx < len(main_picks):
            final_main[i] = {**main_picks[pick_idx], "locked": False}
            pick_idx += 1
    
    # Sort by number value
    main_numbers = sorted([f["number"] for f in final_main if f])
    
    # ============================================================
    # COMPILE STAR PREDICTIONS
    # ============================================================
    locked_star_set = set(locked_stars.values())
    ranked_stars = sorted(
        [(n, data) for n, data in star_scores.items() if n not in locked_star_set],
        key=lambda x: x[1]["score"],
        reverse=True
    )
    
    stars_to_fill = 2 - len(locked_stars)
    star_picks = [{"number": n, "score": data["score"], "reasons": data["reasons"][:3]} for n, data in ranked_stars[:stars_to_fill]]
    
    final_stars = [None] * 2
    for pos, num in locked_stars.items():
        final_stars[pos] = {"number": num, "score": 999, "reasons": ["🔒 Locked"], "locked": True}
    
    pick_idx = 0
    for i in range(2):
        if final_stars[i] is None and pick_idx < len(star_picks):
            final_stars[i] = {**star_picks[pick_idx], "locked": False}
            pick_idx += 1
    
    star_numbers = sorted([f["number"] for f in final_stars if f])
    
    # ============================================================
    # GENERATE MULTIPLE TICKETS
    # ============================================================
    all_tickets = []
    
    # First ticket
    all_tickets.append({
        "ticket_num": 1,
        "main_numbers": main_numbers,
        "stars": star_numbers,
        "main_details": final_main,
        "star_details": final_stars,
        "confidence": sum(f["score"] for f in final_main if f and not f.get("locked")) / max(1, positions_to_fill)
    })
    
    # Additional tickets
    if num_tickets > 1:
        for ticket_idx in range(2, num_tickets + 1):
            # Pick different numbers with decreasing weights
            ticket_main = list(locked_main_set)
            available = [(n, data) for n, data in ranked_main if n not in ticket_main]
            
            while len(ticket_main) < 5 and available:
                weights = [max(1, data["score"] - ticket_idx * 3) for n, data in available]
                total = sum(weights)
                r = random.random() * total
                cumulative = 0
                for i, ((n, data), w) in enumerate(zip(available, weights)):
                    cumulative += w
                    if r <= cumulative:
                        ticket_main.append(n)
                        available.pop(i)
                        break
            
            # Stars for this ticket
            ticket_stars = list(locked_star_set)
            avail_stars = [(n, data) for n, data in ranked_stars if n not in ticket_stars]
            while len(ticket_stars) < 2 and avail_stars:
                n, data = avail_stars.pop(0)
                ticket_stars.append(n)
            
            all_tickets.append({
                "ticket_num": ticket_idx,
                "main_numbers": sorted(ticket_main),
                "stars": sorted(ticket_stars),
                "confidence": 100 - ticket_idx * 5
            })
    
    # Calculate average confidence
    avg_confidence = sum(f["score"] for f in final_main if f and not f.get("locked")) / max(1, positions_to_fill)
    
    return {
        "prediction_date": datetime.now(timezone.utc).isoformat(),
        "last_draw": {
            "date": last_draw.get("date"),
            "numbers": last_draw.get("numbers"),
            "stars": last_draw.get("stars")
        } if last_draw else None,
        "main_prediction": main_numbers,
        "main_details": final_main,
        "star_prediction": star_numbers,
        "star_details": final_stars,
        "locked_main": {f"P{k+1}": v for k, v in locked_main.items()} if locked_main else None,
        "locked_stars": locked_stars if locked_stars else None,
        "num_tickets": num_tickets,
        "all_tickets": all_tickets if num_tickets > 1 else None,
        "alternates": {
            "main": [n for n, _ in ranked_main[positions_to_fill:positions_to_fill+5]],
            "stars": [n for n, _ in ranked_stars[stars_to_fill:stars_to_fill+3]]
        },
        "average_confidence": round(avg_confidence, 1),
        "patterns_used": [
            "Hot numbers (last 20)",
            "Due numbers",
            "Position analysis (P1-P5)",
            "P3-P4 dance",
            "P4-P5 dance",
            "Decade cluster",
            "Digit echo",
            "Family system",
            "Date patterns",
            "Star pairs",
            "Consecutive numbers",
            "P1+P5 magic sum"
        ]
    }

@api_router.post("/import-draws")
async def import_draws(draws_data: list):
    """
    Import EuroMillions draws.
    Expected format: [{"date": "YYYY-MM-DD", "numbers": [1,2,3,4,5], "stars": [1,2]}, ...]
    """
    if not draws_data:
        return {"error": "No data provided"}
    
    imported = 0
    for draw in draws_data:
        if "date" in draw and "numbers" in draw and "stars" in draw:
            # Validate
            if len(draw["numbers"]) == 5 and len(draw["stars"]) == 2:
                if all(1 <= n <= 50 for n in draw["numbers"]) and all(1 <= s <= 12 for s in draw["stars"]):
                    await db.draws.update_one(
                        {"date": draw["date"]},
                        {"$set": {
                            "date": draw["date"],
                            "numbers": sorted(draw["numbers"]),
                            "stars": sorted(draw["stars"])
                        }},
                        upsert=True
                    )
                    imported += 1
    
    return {"imported": imported, "total_provided": len(draws_data)}

@api_router.get("/dashboard")
async def get_dashboard():
    """Dashboard data for the UI"""
    draws = await db.draws.find({}, {"_id": 0}).sort("date", -1).to_list(100)
    
    if not draws:
        return {"total_draws": 0, "message": "No data yet"}
    
    # Recent draws
    recent = draws[:5]
    
    # Hot/cold analysis
    main_freq = Counter()
    star_freq = Counter()
    for d in draws[:50]:
        for n in d.get('numbers', []):
            main_freq[n] += 1
        for s in d.get('stars', []):
            star_freq[s] += 1
    
    return {
        "total_draws": len(draws),
        "recent_draws": recent,
        "hot_main": main_freq.most_common(10),
        "cold_main": main_freq.most_common()[-10:] if len(main_freq) >= 10 else [],
        "hot_stars": star_freq.most_common(5),
        "last_draw": draws[0] if draws else None
    }

app.include_router(api_router)

@app.on_event("startup")
async def startup_db_client():
    # Create indexes
    await db.draws.create_index("date", unique=True)
    print("EuroMillions API started!")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
