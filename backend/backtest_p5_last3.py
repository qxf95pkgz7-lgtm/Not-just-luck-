"""🎻 Session 26 · P5 Backtest Harness
DJ's ask: Euro, last 3 draws, check P5.
Compares per-position P5 board WITH vs WITHOUT Session 26 laws (83-86).
"""
import asyncio
import sys
import os
from datetime import datetime as dt

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import cosmic_engine
from cosmic_engine import (
    load_euro_draws, find_last_family_rare,
    build_convergence_board, build_per_position_board,
    rank_suspects, apply_hold_fatigue, compute_slot_history_rates,
)
from motor.motor_asyncio import AsyncIOMotorClient


# Monkeypatch switch for Session 26 laws
_ORIGINAL_S26 = None

def disable_session26():
    import session26_laws
    global _ORIGINAL_S26
    _ORIGINAL_S26 = session26_laws.session26_lenses
    session26_laws.session26_lenses = lambda *a, **kw: ([], False)

def enable_session26():
    import session26_laws
    if _ORIGINAL_S26 is not None:
        session26_laws.session26_lenses = _ORIGINAL_S26


async def run_for_date(db, target_date_str: str, with_s26: bool):
    if with_s26:
        enable_session26()
    else:
        disable_session26()

    draws = await load_euro_draws(db)
    target_date = dt.strptime(target_date_str, '%d.%m.%Y')
    actual = next((d for d in draws if d['_dt'] == target_date), None)
    if not actual:
        return None

    prior = [d for d in draws if d['_dt'] < target_date]
    found = find_last_family_rare(prior, target_date)
    if not found:
        return None
    _, rc0 = found
    cycle = [d for d in prior if rc0['dt'] < d['_dt']]
    target_d = len(cycle) + 1

    lenses = build_convergence_board(rc0, cycle, target_date, target_d, [])
    ranked = rank_suspects(lenses)
    ranked = apply_hold_fatigue(ranked, cycle, last_n_draws=3)
    slot_rates = compute_slot_history_rates(prior)
    pos_board = build_per_position_board(
        lenses, ranked, [], top_n=10,
        cycle=cycle, slot_history_rates=slot_rates,
    )

    actual_p5 = actual['_n'][4]
    p5_board = pos_board.get('P5', [])
    p5_numbers = [e['n'] for e in p5_board]
    rank_of_actual = p5_numbers.index(actual_p5) + 1 if actual_p5 in p5_numbers else None

    return {
        'date': target_date_str,
        'actual_p5': actual_p5,
        'actual_draw': actual['_n'],
        'target_d': target_d,
        'rc0': rc0['date'],
        'p5_top10': [(e['n'], round(e['score'], 1)) for e in p5_board],
        'rank_of_actual': rank_of_actual,
        'in_top5': rank_of_actual is not None and rank_of_actual <= 5,
    }


async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]

    TARGETS = ['24.04.2026', '28.04.2026', '01.05.2026']

    print("\n" + "="*78)
    print(" 🎻🎧🥂  SESSION 26 · P5 BACKTEST · LAST 3 EURO DRAWS")
    print("="*78)

    rows = []
    for date_str in TARGETS:
        with_r = await run_for_date(db, date_str, with_s26=True)
        without_r = await run_for_date(db, date_str, with_s26=False)
        rows.append((date_str, with_r, without_r))

    print(f"\n{'Date':<13}{'Actual P5':<12}{'Draw':<32}{'d':<4}{'RC0':<13}")
    for d, w, _ in rows:
        if w:
            draw_str = str(w['actual_draw'])
            print(f"{d:<13}{w['actual_p5']:<12}{draw_str:<32}d{w['target_d']:<3}{w['rc0']:<13}")

    print("\n" + "-"*78)
    print(" P5 BOARD · WITH Session 26 Laws (83-86)  vs  WITHOUT (baseline)")
    print("-"*78)
    hits_with = 0
    hits_without = 0
    total_rank_with = 0
    total_rank_without = 0
    for d, w, wo in rows:
        print(f"\n🎻 {d} · actual P5 = {w['actual_p5']}")
        print(f"   WITH   s26: rank={w['rank_of_actual']}  top5={w['in_top5']}")
        print(f"               top10: {w['p5_top10']}")
        print(f"   WITHOUT   : rank={wo['rank_of_actual']}  top5={wo['in_top5']}")
        print(f"               top10: {wo['p5_top10']}")

        if w['in_top5']:
            hits_with += 1
        if wo['in_top5']:
            hits_without += 1
        if w['rank_of_actual']:
            total_rank_with += w['rank_of_actual']
        else:
            total_rank_with += 11  # penalize miss
        if wo['rank_of_actual']:
            total_rank_without += wo['rank_of_actual']
        else:
            total_rank_without += 11

    print("\n" + "="*78)
    print(" 🥂 SCORECARD")
    print("="*78)
    print(f"   Top-5 hits  · WITH s26: {hits_with}/3   WITHOUT: {hits_without}/3")
    print(f"   Avg rank    · WITH s26: {total_rank_with/3:.2f}   WITHOUT: {total_rank_without/3:.2f}  (lower=better, 11=miss)")
    if hits_with > hits_without:
        print("   📈 Session 26 laws SHARPEN P5 listening")
    elif hits_with < hits_without:
        print("   📉 Session 26 laws DULL P5 listening")
    else:
        print("   ⚖️ Session 26 laws NEUTRAL at P5 (as expected — laws tag P1-P4)")
    print("="*78)


if __name__ == '__main__':
    asyncio.run(main())
