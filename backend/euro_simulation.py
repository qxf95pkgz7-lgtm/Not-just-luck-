"""
Euro Engine Simulation — Compare spread vs no-spread across random dates
"""
import asyncio
import random
import sys
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Connect to DB
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

# Import the DJ engine
from dj_patterns import dj_generate_ticket, dj_select_numbers
import dj_patterns as djp

async def run_simulation(num_dates=20, tickets_per_date=20):
    """Run simulation on random dates from last 2 years"""
    
    # Fetch all Euro draws
    draws_raw = await db.euromillions_draws.find({}, {"_id": 0}).to_list(5000)
    
    def parse_date(d):
        for fmt in ['%d.%m.%Y', '%Y-%m-%d']:
            try:
                return datetime.strptime(d['date'], fmt)
            except:
                continue
        return datetime.min
    
    draws_raw = sorted(draws_raw, key=parse_date, reverse=True)
    
    # Filter to last 2 years
    cutoff = datetime.now() - timedelta(days=730)
    recent_draws = [d for d in draws_raw if parse_date(d) > cutoff]
    
    if len(recent_draws) < 30:
        print(f"Only {len(recent_draws)} draws in last 2 years, need at least 30")
        return
    
    # Pick random test dates (skip first 10 to have history)
    test_indices = sorted(random.sample(range(5, min(len(recent_draws), 200)), min(num_dates, len(recent_draws) - 10)))
    
    print(f"\n{'='*80}")
    print(f"EURO ENGINE SIMULATION — {len(test_indices)} dates x {tickets_per_date} tickets")
    print(f"{'='*80}\n")
    
    # Results tracking
    results_with_spread = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    results_no_spread = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    star_hits_spread = {"0": 0, "1": 0, "2": 0}
    star_hits_no_spread = {"0": 0, "1": 0, "2": 0}
    best_per_draw_spread = []
    best_per_draw_no_spread = []
    
    total_tickets = 0
    
    for idx in test_indices:
        actual_draw = recent_draws[idx]
        actual_nums = set(actual_draw.get('numbers', []))
        actual_stars = set(actual_draw.get('stars', []))
        actual_date = actual_draw['date']
        
        # History = all draws BEFORE this one
        history = recent_draws[idx+1:]
        if len(history) < 5:
            continue
            
        draw_best_spread = 0
        draw_best_no_spread = 0
        
        for t in range(tickets_per_date):
            total_tickets += 1
            
            # === WITH SPREAD (current engine) ===
            try:
                ticket = dj_generate_ticket(history[:50], target_date=actual_date)
                pred_nums = set(ticket['numbers'])
                pred_stars = set(ticket['stars'])
                hits = len(pred_nums & actual_nums)
                s_hits = len(pred_stars & actual_stars)
                results_with_spread[str(hits)] += 1
                star_hits_spread[str(s_hits)] += 1
                draw_best_spread = max(draw_best_spread, hits)
            except Exception as e:
                pass
            
            # === WITHOUT SPREAD (bypass spread logic) ===
            try:
                # Temporarily monkey-patch to skip spread
                original_select = djp.dj_select_numbers
                
                def no_spread_select(candidates, star_candidates, locked=None, date_day=None, 
                                     p1_king_candidates=None, p2_prince_candidates=None, draws=None):
                    result = original_select(candidates, star_candidates, locked, date_day,
                                            p1_king_candidates, p2_prince_candidates, draws)
                    return result
                
                # Generate without spread by using the raw engine before our change
                # We'll generate candidates and select without the spread guarantee
                result_raw = djp.dj_generate_candidates(history[:50], actual_date)
                
                date_day = None
                p1_king_candidates = []
                p2_prince_candidates = []
                try:
                    date_day = int(actual_date.split('.')[0])
                    p1r = djp.pattern_p1_king(actual_date, history[0], history[1] if len(history) > 1 else None)
                    p1_king_candidates = p1r.get('candidates', [])
                    p2r = djp.pattern_p2_prince(actual_date, history[0], history[1] if len(history) > 1 else None)
                    p2_prince_candidates = p2r.get('candidates', [])
                except:
                    pass
                
                # Raw selection without spread
                locked = {}
                p1_kc = p1_king_candidates or []
                p2_pc = p2_prince_candidates or []
                cands = result_raw["candidates"]
                star_cands = result_raw["star_candidates"]
                
                # Direct selection (no spread enforcement)
                selected = []
                used = set()
                
                # P1 King
                if p1_kc:
                    p1_pool = []
                    for num, weight, reason in p1_kc:
                        if 1 <= num <= 20:
                            p1_pool.extend([num] * weight)
                    if p1_pool and random.random() < 0.60:
                        p1 = random.choice(p1_pool)
                        selected.append(p1)
                        used.add(p1)
                    else:
                        selected.append(None)
                else:
                    selected.append(None)
                
                # P2 Prince
                if p2_pc:
                    p2_pool = []
                    for num, weight, reason in p2_pc:
                        if 5 <= num <= 35 and num not in used:
                            p2_pool.extend([num] * weight)
                    if p2_pool and random.random() < 0.55:
                        p2 = random.choice(p2_pool)
                        selected.append(p2)
                        used.add(p2)
                    else:
                        selected.append(None)
                else:
                    selected.append(None)
                
                # Fill remaining
                for pos in range(5):
                    if pos < len(selected) and selected[pos] is not None:
                        continue
                    pos_c = [c for c in cands.get(pos, []) if c not in used and 1 <= c <= 50]
                    if pos_c:
                        ch = random.choice(pos_c)
                    else:
                        ch = random.choice([n for n in range(1, 51) if n not in used])
                    if pos < len(selected):
                        selected[pos] = ch
                    else:
                        selected.append(ch)
                    used.add(ch)
                
                ns_nums = set(sorted(selected))
                
                # Stars
                ns_stars = set()
                star_used = set()
                for _ in range(2):
                    sp = [s for s in star_cands if s not in star_used and 1 <= s <= 12]
                    if sp:
                        st = random.choice(sp)
                    else:
                        st = random.choice([s for s in range(1, 13) if s not in star_used])
                    ns_stars.add(st)
                    star_used.add(st)
                
                ns_hits = len(ns_nums & actual_nums)
                ns_star_hits = len(ns_stars & actual_stars)
                results_no_spread[str(ns_hits)] += 1
                star_hits_no_spread[str(ns_star_hits)] += 1
                draw_best_no_spread = max(draw_best_no_spread, ns_hits)
            except Exception as e:
                pass
        
        best_per_draw_spread.append(draw_best_spread)
        best_per_draw_no_spread.append(draw_best_no_spread)
        
        print(f"  {actual_date} | Actual: {sorted(actual_nums)} Stars:{sorted(actual_stars)} | Best WITH spread: {draw_best_spread}/5 | Best NO spread: {draw_best_no_spread}/5")
    
    # Summary
    total_per_mode = len(test_indices) * tickets_per_date
    
    print(f"\n{'='*80}")
    print(f"RESULTS SUMMARY — {len(test_indices)} draws x {tickets_per_date} tickets = {total_per_mode} tickets per mode")
    print(f"{'='*80}")
    
    print(f"\n--- NUMBER HITS (out of 5) ---")
    print(f"{'Hits':>6} | {'WITH Spread':>15} | {'NO Spread':>15}")
    print(f"{'-'*6}-+-{'-'*15}-+-{'-'*15}")
    for h in ["0", "1", "2", "3", "4", "5"]:
        ws = results_with_spread[h]
        ns = results_no_spread[h]
        ws_pct = ws / total_per_mode * 100 if total_per_mode else 0
        ns_pct = ns / total_per_mode * 100 if total_per_mode else 0
        marker = " <--" if int(h) >= 3 else ""
        print(f"  {h}/5  | {ws:>5} ({ws_pct:>5.1f}%) | {ns:>5} ({ns_pct:>5.1f}%){marker}")
    
    print(f"\n--- STAR HITS (out of 2) ---")
    print(f"{'Hits':>6} | {'WITH Spread':>15} | {'NO Spread':>15}")
    print(f"{'-'*6}-+-{'-'*15}-+-{'-'*15}")
    for h in ["0", "1", "2"]:
        ws = star_hits_spread[h]
        ns = star_hits_no_spread[h]
        ws_pct = ws / total_per_mode * 100 if total_per_mode else 0
        ns_pct = ns / total_per_mode * 100 if total_per_mode else 0
        print(f"  {h}/2  | {ws:>5} ({ws_pct:>5.1f}%) | {ns:>5} ({ns_pct:>5.1f}%)")
    
    avg_best_spread = sum(best_per_draw_spread) / len(best_per_draw_spread) if best_per_draw_spread else 0
    avg_best_no_spread = sum(best_per_draw_no_spread) / len(best_per_draw_no_spread) if best_per_draw_no_spread else 0
    
    hits3plus_spread = sum(1 for b in best_per_draw_spread if b >= 3)
    hits3plus_no_spread = sum(1 for b in best_per_draw_no_spread if b >= 3)
    
    print(f"\n--- BEST TICKET PER DRAW (from {tickets_per_date} tickets) ---")
    print(f"  Avg best hits WITH spread:  {avg_best_spread:.2f}/5")
    print(f"  Avg best hits NO spread:    {avg_best_no_spread:.2f}/5")
    print(f"  Draws with 3+ hit ticket WITH spread:  {hits3plus_spread}/{len(best_per_draw_spread)} ({hits3plus_spread/len(best_per_draw_spread)*100:.0f}%)")
    print(f"  Draws with 3+ hit ticket NO spread:    {hits3plus_no_spread}/{len(best_per_draw_no_spread)} ({hits3plus_no_spread/len(best_per_draw_no_spread)*100:.0f}%)")
    
    print(f"\n{'='*80}")
    if avg_best_spread >= avg_best_no_spread:
        print(f"  VERDICT: SPREAD is {'EQUAL' if avg_best_spread == avg_best_no_spread else 'BETTER'}! Numbers spread across decades without losing accuracy.")
    else:
        diff = avg_best_no_spread - avg_best_spread
        print(f"  VERDICT: Spread costs {diff:.2f} avg hits — may need tuning.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(run_simulation(num_dates=20, tickets_per_date=20))
