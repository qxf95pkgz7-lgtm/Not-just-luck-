"""🎻🎧🥂 P3-Ghost Live Generator — runs E on a target date.

Flow:
  1. Run cosmic_engine for target date → get P3 board nominees
  2. For each top P3 nominee, mine 2-year history → pick ghost → 10 tickets
  3. Return full orchestra + related-P3 rotation options
"""
import asyncio, os, sys
from typing import List, Dict
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from cosmic_engine import run_cosmic_engine, load_euro_draws
from p3_ghost_orchestra import (
    mine_p3_history, pick_ghost, build_p3_tickets, related_p3_candidates,
    load_draws,
)
from motor.motor_asyncio import AsyncIOMotorClient


async def run_p3_live(target_date_str: str, top_n_p3: int = 5,
                      n_per_archetype: int = 2) -> Dict:
    """End-to-end: engine → P3 nominees → orchestras."""
    engine_out = await run_cosmic_engine(target_date_str, n_tickets=5)
    pos_board = engine_out.get('pos_board', {})
    p3_board = pos_board.get('P3', [])[:top_n_p3]
    draws2y = load_draws(2024)

    sub_orchestras = []
    for e in p3_board:
        p3_val = e['n']
        hist = mine_p3_history(p3_val, draws2y)
        ghosts = pick_ghost(p3_val, hist, draws2y, top_k=3)
        ghost = ghosts[0][0] if ghosts else 21
        ghost_tag = ghosts[0][1] if ghosts else 'default'
        tickets = build_p3_tickets(p3_val, ghost, hist, draws2y,
                                     n_per_archetype=n_per_archetype)
        related = related_p3_candidates(p3_val)
        sub_orchestras.append({
            'p3': p3_val,
            'engine_score': e.get('score'),
            'engine_lenses': e.get('laws', [])[:5],
            'history_matches': hist['count'],
            'top_co_partners': hist['co_partners_top'][:6],
            'ghost': ghost,
            'ghost_tag': ghost_tag,
            'ghost_alternates': ghosts[1:3],
            'tickets': tickets,
            'related_p3s': related,
        })
    return {
        'target_date': target_date_str,
        'rc0': engine_out.get('rc0', {}),
        'p3_nominees': [e['n'] for e in p3_board],
        'orchestras': sub_orchestras,
    }


def print_report(r: Dict):
    print("="*92)
    print(f" 🎻🎧🥂 LIVE P3-GHOST ORCHESTRA · target {r['target_date']}")
    print(f"     RC0 = {r['rc0'].get('date','-')} {r['rc0'].get('mains','')}")
    print(f"     E's P3 nominees: {r['p3_nominees']}")
    print("="*92)

    for o in r['orchestras']:
        print(f"\n🎯 P3 = {o['p3']}  (engine-score {o['engine_score']})")
        if o['engine_lenses']:
            print(f"   Lenses: {o['engine_lenses']}")
        print(f"   📚 2-yr history: {o['history_matches']} matches · top co-partners: {o['top_co_partners']}")
        print(f"   👻 Ghost: {o['ghost']}  ({o['ghost_tag']})")
        if o['ghost_alternates']:
            alts = ', '.join(f"{g}({t})" for g, t in o['ghost_alternates'])
            print(f"      alternates: {alts}")
        print(f"   🎫 {len(o['tickets'])} tickets:")
        for t in o['tickets']:
            print(f"      [{t['archetype']:<18}] {t['mains']} ⭐{t['stars']}")
            print(f"         ↳ {t['story']}")
        print(f"   🔁 Related P3s (rotate next): {o['related_p3s'][:6]}")


async def main():
    target = sys.argv[1] if len(sys.argv) > 1 else '05.05.2026'
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    r = await run_p3_live(target, top_n_p3=top_n, n_per_archetype=2)
    print_report(r)


if __name__ == '__main__':
    asyncio.run(main())
