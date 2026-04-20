"""
🎯 HUNT BOX — "P5-50 and friends"

Persistent targeting boxes. Each box carries:
  • target_type  → currently 'p5_value' (P5 = target_value, e.g., 50)
  • jack_picks   → list of suspect mains the DJ must include
  • mode         → 'euro' or 'swiss'
  • status       → 'active' or 'resolved'
  • created_at / resolved_at

Every draw, the box generates FIVE music tickets that all carry:
  • the target (e.g., P5 = 50)
  • as many jack_picks as fit
  • remaining slots filled from convergence radar + story archetypes

When a draw completes, if the target fires, the box resolves 🏆.
Otherwise, the next draw re-generates a fresh 5 tickets.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import sys

import os
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from lottery_simulator import run_simulator, CFG, parse_date


# ─────────────────────────────────────────────────────────────
# Core generator — builds 5 tickets that carry target + jack picks
# ─────────────────────────────────────────────────────────────
def _pick_fill(convergence, used: set, banned: set, n: int, constraint=None):
    """Pick n numbers from convergence not already used/banned, respecting constraint fn."""
    out = []
    for c in convergence:
        if len(out) >= n:
            break
        if c["n"] in used or c["n"] in banned or c["n"] in out:
            continue
        if constraint and not constraint(c["n"]):
            continue
        out.append(c["n"])
    return out


def generate_hunt_tickets(target_date: str, mode: str, target_value: int,
                          jack_picks: List[int], dj_call: dict = None,
                          num_tickets: int = 5) -> List[dict]:
    """
    Produce `num_tickets` 5-main tickets (Euro) or 6-main (Swiss) such that:
      • max(ticket) == target_value   (P5 = target)
      • jack_picks priority-included
      • remaining slots filled from convergence (different per ticket)
    Returns list of {mains, stars, story, score, lens_coverage}
    """
    sim = run_simulator(target_date, mode, dj_call=dj_call)
    conv = sim.get("convergence", [])
    star_suspects = sim.get("star_suspects", [])
    banned = set(sim.get("banned", []))

    # Star choice (DJ locks first, then star suspects)
    star_locks = []
    if dj_call and dj_call.get(mode, {}).get("star_locks"):
        star_locks = list(dj_call[mode]["star_locks"])[:2]
    if len(star_locks) < 2:
        for s in star_suspects:
            if s["s"] not in star_locks:
                star_locks.append(s["s"])
                if len(star_locks) == 2:
                    break
    star_locks = sorted(star_locks[:2]) if mode == "euro" else []

    mx = CFG[mode]["max_main"]
    npos = CFG[mode]["npos"]  # 5 euro, 6 swiss

    # Sanity: target must be valid
    if not (1 <= target_value <= mx):
        return []

    # Clean jack picks — must be in range, not banned, not == target
    jack_picks = [n for n in jack_picks if 1 <= n <= mx and n not in banned and n != target_value]
    jack_picks = sorted(set(jack_picks))

    # Jack picks must all be < target (so target stays the max)
    jack_picks = [n for n in jack_picks if n < target_value]

    tickets = []
    prior_fills = set()  # track free-slot picks across archetypes to force diversity
    # Archetypes for variation: each ticket uses a different "fill strategy"
    archetypes = [
        ("🎻 All-Cosmos Fill",      "Top-convergence symphony around resonators + crown"),
        ("🪞 Mirror Orbit",          "28-mirror pair partners circle the crown in balance"),
        ("⭐ Star-King Harmonics",  "Star-king formula partners weave the free notes"),
        ("🌌 Starved Nebula",       "Deep-hungry and silent-band voices carry the song"),
        ("🌠 Meridian Bridge",      "Cross-lottery Δ±2 and self-circle orbits fill in"),
    ][:num_tickets]

    for idx, (arch_name, story) in enumerate(archetypes):
        mains = list(jack_picks)  # start with DJ resonators
        used = set(mains) | {target_value} | prior_fills
        constraint = lambda n: n < target_value  # nothing above target (it's the max)
        needed = npos - 1 - len(mains)  # minus 1 because we add target last

        if arch_name == "🎻 All-Cosmos Fill":
            fill = _pick_fill(conv, used, banned, needed, constraint)
        elif arch_name == "🪞 Mirror Orbit":
            mirror_pool = []
            mirror_rest = []
            for c in conv:
                if c["n"] == target_value or c["n"] in banned or c["n"] in used:
                    continue
                if c["n"] < target_value:
                    if any(j + c["n"] == 28 for j in mains):
                        mirror_pool.append(c)
                    else:
                        mirror_rest.append(c)
            ordered = mirror_pool + mirror_rest
            fill = _pick_fill(ordered, used, banned, needed, constraint)
        elif arch_name == "⭐ Star-King Harmonics":
            kingy = [c for c in conv if any(l.startswith("star-king") for l in c["laws"])
                     and c["n"] < target_value and c["n"] not in banned and c["n"] not in used]
            rest = [c for c in conv if c not in kingy and c["n"] < target_value
                    and c["n"] not in banned and c["n"] not in used]
            fill = _pick_fill(kingy + rest, used, banned, needed, constraint)
        elif arch_name == "🌌 Starved Nebula":
            hungry = [c for c in conv if any(l.startswith("seed-hungry") or l.startswith("silent-band") or l.startswith("dj-hungry") for l in c["laws"])
                      and c["n"] < target_value and c["n"] not in banned and c["n"] not in used]
            rest = [c for c in conv if c not in hungry and c["n"] < target_value
                    and c["n"] not in banned and c["n"] not in used]
            fill = _pick_fill(hungry + rest, used, banned, needed, constraint)
        elif arch_name == "🌠 Meridian Bridge":
            bridge = [c for c in conv if any(l.startswith("cross") or l.startswith("self-circle") for l in c["laws"])
                      and c["n"] < target_value and c["n"] not in banned and c["n"] not in used]
            rest = [c for c in conv if c not in bridge and c["n"] < target_value
                    and c["n"] not in banned and c["n"] not in used]
            fill = _pick_fill(bridge + rest, used, banned, needed, constraint)
        else:
            fill = _pick_fill(conv, used, banned, needed, constraint)

        # Fallback fill if short
        while len(mains) + len(fill) < npos - 1:
            # pad with safe low numbers not banned/used
            for n in range(1, target_value):
                if n not in mains and n not in fill and n not in banned:
                    fill.append(n)
                    if len(mains) + len(fill) >= npos - 1:
                        break
            break  # one-shot to avoid loop

        mains = sorted(mains + fill + [target_value])
        if len(mains) != npos:
            continue

        # Record this archetype's fill choices to push later archetypes elsewhere
        prior_fills.update(fill)

        # Score via lens sum
        score = 0
        lenses_hit = set()
        for c in conv:
            if c["n"] in mains:
                score += c["lens_count"]
                lenses_hit.update(c["laws"])

        tickets.append({
            "archetype": arch_name,
            "story": story,
            "mains": mains,
            "stars": star_locks,
            "score": score,
            "unique_laws_hit": len(lenses_hit),
            "contains_suspects": sorted(set(mains) & set(jack_picks)),
            "contains_target": target_value in mains,
        })

    # De-dup identical main-combos (preserve best score)
    seen = {}
    for t in tickets:
        k = tuple(t["mains"])
        if k not in seen or t["score"] > seen[k]["score"]:
            seen[k] = t
    return sorted(seen.values(), key=lambda t: -t["score"])


# ─────────────────────────────────────────────────────────────
# Resolution check — did the target fire in the actual draw?
# ─────────────────────────────────────────────────────────────
def check_resolution(box: dict, actual_draw: dict) -> bool:
    """
    Returns True if the hunt target was satisfied by the actual draw.
    target_type options:
      • p5_value      → P5 == target_value
      • any_position  → target_value appears anywhere in mains
    """
    if not actual_draw or not actual_draw.get("numbers"):
        return False
    nums = sorted(actual_draw["numbers"])
    tt = box.get("target_type", "p5_value")
    tv = box.get("target_value")
    if tt == "p5_value":
        return nums[-1] == tv
    if tt == "any_position":
        return tv in nums
    if tt == "p4_value":
        return len(nums) >= 4 and nums[-2] == tv
    return False
