"""
🎼 GHOST ORCHESTRATOR — single entry point for the Ghost Engine
================================================================
Fuses ghost births, walks, closures, chainless windows, saturation,
quarter shape, and carrier expansion into one prophecy.

Public:
  build_ghost_ledger(target_date, mode, lookback=10)

Output structure:
  {
    "target_date", "mode", "lookback",
    "draws_window": [...],
    "arithmetic_ledger": [...],         # per-draw ghost births
    "ghost_track": [
       {n, born_date, born_door, age, alive,
        first_closure_age, closure_types, projected_hot_zone, ...}
    ],
    "alive_ghosts": [...],              # ghosts still unpaid → next-draw suspects
    "chainless_windows": [...],         # draws where the engine expects raw cash
    "saturation": {...},
    "quarter_shape": {...},
    "carrier_pool": {...},
    "convergence": {                    # numbers ringing on ≥2 ghost lenses
        "ranked": [(n, score, tags)...],
        "shout": [n,...],  # ≥3 lenses
        "whisper": [n,...] # 2 lenses
    }
  }
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from year_d_ledger import load_draws, parse_dt, quarter_of

from .ghost_arithmetic_ledger import build_arithmetic_ledger
from .ghost_walk_tracker import walk_ghosts_forward
from .ghost_close_detector import detect_closures, summarise_ghost_track
from .internal_chain_detector import detect_chainless_windows
from .saturation_to_rare import saturation_watch
from .quarter_shape_signature import detect_quarter_shape
from .carrier_expansion import unified_pool, expand_carriers


async def build_ghost_ledger(
    target_date: str,
    mode: str = "euro",
    lookback: int = 10,
) -> Dict:
    """Build the full ghost ledger for the target date."""
    mode = mode.lower().strip()
    if mode not in ("euro", "swiss"):
        return {"error": "mode must be 'euro' or 'swiss'"}
    target_dt = parse_dt(target_date)
    if not target_dt:
        return {"error": f"invalid target_date '{target_date}' (use dd.mm.yyyy)"}
    max_n = 50 if mode == "euro" else 42

    all_draws = await load_draws(mode)
    past = [d for d in all_draws if d["dt"] < target_dt]
    past.sort(key=lambda x: x["dt"])
    window = past[-lookback:] if len(past) > lookback else past
    if not window:
        return {"error": "no historical draws found before target_date", "mode": mode}

    # 1. Arithmetic ledger — births
    ledger = build_arithmetic_ledger(window, mode)

    # 2. Walk forward each ghost from its birth and detect closures
    ghost_tracks: List[Dict] = []
    for idx, entry in enumerate(ledger):
        future = window[idx + 1:]
        for g in entry["ghosts"]:
            closures = detect_closures(g, future, mode)
            summary = summarise_ghost_track(
                {**g, "born_date": entry["date"]},
                closures,
            )
            current_age = len(future)
            walked = walk_ghosts_forward(
                {"n": g["n"]}, current_age + 1, mode,
            )
            ghost_tracks.append({
                **summary,
                "born_door": g["door"],
                "born_src": g["src"],
                "born_idx": idx,
                "current_age": current_age + 1,  # age at target_date
                "closures": closures,
                "projection": walked,
            })

    # 3. Alive ghosts → candidates for target_date
    alive = [g for g in ghost_tracks if g["alive"]]
    alive.sort(key=lambda x: -x["current_age"])  # oldest first

    # 4. Chainless windows
    chainless = detect_chainless_windows(window)

    # 5. Saturation watch
    sat = saturation_watch(window, window=min(9, len(window)), threshold=4)

    # 6. Quarter shape signature
    target_q = quarter_of(target_dt, mode)
    quarter_draws = [
        d for d in past
        if d["quarter"] == target_q and d["year"] == target_dt.year
    ]
    qs = detect_quarter_shape(quarter_draws)

    # 7. Carrier pool from alive ghosts
    alive_ns = [g["n"] for g in alive]
    pool = unified_pool(alive_ns[:20], mode)

    # 8. Convergence — score every candidate n by # of ghost lenses ringing
    scores: Dict[int, int] = defaultdict(int)
    tags: Dict[int, List[str]] = defaultdict(list)
    # alive ghost raw + projection hot zones contribute
    for g in alive:
        # The raw alive ghost itself
        scores[g["n"]] += 3
        tags[g["n"]].append(f"alive-ghost (age {g['current_age']})")
        # Its projected hot zone members
        for v in g["projection"]["hot_zone"]:
            if v != g["n"]:
                scores[v] += 1
                tags[v].append(f"hot-zone of ghost {g['n']}")
    # Saturation suspects — boost the saturated decade by tagging all numbers
    for s in sat["saturated"]:
        scores[s["n"]] += 2
        tags[s["n"]].append(f"saturated ×{s['count']}")
    # Chainless next window — flag the most recent chainless draw as "cash"
    last_cw = next((c for c in reversed(chainless) if c["is_cash_window"]), None)
    if last_cw:
        # boost alive ghost raw values (cash window expects raw close)
        for g in alive:
            scores[g["n"]] += 2
            tags[g["n"]].append("cash-window-active")

    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    ranked_list = [
        {"n": n, "score": s, "tags": list(dict.fromkeys(tags[n]))[:5]}
        for n, s in ranked if 1 <= n <= max_n
    ]
    shout = [r["n"] for r in ranked_list if r["score"] >= 5][:12]
    whisper = [r["n"] for r in ranked_list if 3 <= r["score"] < 5][:12]

    return {
        "target_date": target_date,
        "mode": mode,
        "lookback": lookback,
        "draws_window": [
            {"date": d.get("date"), "p": d.get("p"), "lucky": d.get("lucky"),
             "replay": d.get("replay"), "stars": d.get("stars")}
            for d in window
        ],
        "arithmetic_ledger": [
            {"date": e["date"], "p": e["p"],
             "ghost_count": e["ghost_count"], "ghost_ns": e["ghost_ns"]}
            for e in ledger
        ],
        "ghost_track_count": len(ghost_tracks),
        "alive_ghosts": [
            {
                "n": g["n"],
                "born_date": g["born_date"],
                "born_door": g["born_door"],
                "born_src": g["born_src"],
                "age": g["current_age"],
                "projected_hot_zone": g["projection"]["hot_zone"],
                "carriers": g["projection"]["carriers"],
            }
            for g in alive[:20]
        ],
        "closed_ghosts_summary": {
            "total": len(ghost_tracks),
            "alive": len(alive),
            "closed": len(ghost_tracks) - len(alive),
            "deep_sleep_closures": sum(1 for g in ghost_tracks if g["deep_sleep_closure"]),
            "late_4_5_closures": sum(1 for g in ghost_tracks if g["late_closure_4_5"]),
        },
        "chainless_windows": chainless,
        "saturation": sat,
        "quarter_shape": qs,
        "carrier_pool": pool,
        "convergence": {
            "ranked": ranked_list[:30],
            "shout": shout,
            "whisper": whisper,
        },
        "canon": (
            "S38 Ghost-Counting Canon: doors `?+Pa=Pb` birth ghosts; "
            "they walk +1 per draw; closures peak at 4-late + 9-10d "
            "deep-sleep; chainless draws = cash-windows."
        ),
    }
