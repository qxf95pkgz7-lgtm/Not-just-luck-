"""🎻 Session 26 · P5 Deep Dive
Why does E miss 45 (24.04) and bury 47 (28.04 & 01.05)?
What lenses did the actual P5 catch? Who did E love instead?
"""
import asyncio
import sys
import os
from datetime import datetime as dt

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from cosmic_engine import (
    load_euro_draws, find_last_family_rare,
    build_convergence_board, build_per_position_board,
    rank_suspects, apply_hold_fatigue, compute_slot_history_rates,
)
from motor.motor_asyncio import AsyncIOMotorClient


async def deep_dive(db, target_date_str: str):
    draws = await load_euro_draws(db)
    target_date = dt.strptime(target_date_str, '%d.%m.%Y')
    actual = next((d for d in draws if d['_dt'] == target_date), None)
    prior = [d for d in draws if d['_dt'] < target_date]
    found = find_last_family_rare(prior, target_date)
    _, rc0 = found
    cycle = [d for d in prior if rc0['dt'] < d['_dt']]
    target_d = len(cycle) + 1

    lenses = build_convergence_board(rc0, cycle, target_date, target_d, [])
    ranked = rank_suspects(lenses)
    ranked = apply_hold_fatigue(ranked, cycle, last_n_draws=3)
    slot_rates = compute_slot_history_rates(prior)
    pos_board = build_per_position_board(
        lenses, ranked, [], top_n=50,
        cycle=cycle, slot_history_rates=slot_rates,
    )

    actual_p5 = actual['_n'][4]
    bd_draw = cycle[-1] if cycle else None

    print(f"\n{'='*80}")
    print(f"🎧 {target_date_str} · BD={bd_draw['date']} {bd_draw['_n']} ⭐{bd_draw['_s']} · d{target_d}")
    print(f"   Actual draw: {actual['_n']} ⭐{actual['_s']}  →  P5 = {actual_p5}")
    print(f"{'='*80}")

    # Lenses on actual P5
    p5_lenses = lenses.get(actual_p5, [])
    print(f"\n🔍 Lenses on {actual_p5} (actual P5): {len(p5_lenses)} total")
    for lens in p5_lenses:
        print(f"     • {lens}")

    # Slot rate for actual at P5
    p5_hist = slot_rates.get(5, {}).get(actual_p5, 0.0)
    print(f"\n📈 Historical P5 rate for {actual_p5}: {p5_hist:.2f}%")

    # Show full P5 board (top 15)
    p5_board = pos_board.get('P5', [])
    print(f"\n🎻 Full P5 board (top 15):")
    rank_actual = None
    for i, e in enumerate(p5_board[:15], 1):
        marker = " ← ACTUAL" if e['n'] == actual_p5 else ""
        if e['n'] == actual_p5:
            rank_actual = i
        print(f"   #{i:2d} · n={e['n']:2d}  score={e['score']:.1f}  laws={e['laws'][:3]}{marker}")

    if rank_actual:
        print(f"\n🎯 {actual_p5} is at P5 rank #{rank_actual}")
    else:
        print(f"\n💀 {actual_p5} NOT IN P5 BOARD (failed struct-fit or hist-rate gate)")

    # Diagnostic: how many lenses does actual P5 have overall vs the winners?
    winner = p5_board[0] if p5_board else None
    if winner:
        w_lenses = lenses.get(winner['n'], [])
        print(f"\n🆚 E's #1 P5 pick: {winner['n']} ({len(w_lenses)} lenses) vs actual {actual_p5} ({len(p5_lenses)} lenses)")


async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    for date_str in ['24.04.2026', '28.04.2026', '01.05.2026']:
        await deep_dive(db, date_str)


if __name__ == '__main__':
    asyncio.run(main())
