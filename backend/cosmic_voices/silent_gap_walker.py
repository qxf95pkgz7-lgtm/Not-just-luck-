"""
🥂 SILENT GAP WALKER — `cosmic_voices/silent_gap_walker.py` (Lens #12)
======================================================================
DJ canon (Session 35, 07.05.2026 night):

> "Maybe p2-15 p3-23 p4-35 p5-47. 12 is silent here. Hide in the gap."

When a number `N` is the deepest unpaid debt of a quarter (e.g., 12),
the SNEAKY UNIVERSE pays it through repeating GAPS instead of as a raw
main. The cosmos walks the value as a rhythm, not a note.

5-yr scan validation:
  • silent-12 ×2 events: 4 in 5y (0.7%) — RARE
  • silent-12 ×3 events: 0 in 5y (0.0%) — pure SNEAKY-UNIVERSE territory
  • after silent-12 BD: 12 lands as ND main 25% (vs 10% base = 2.5× lift)
  • after silent-12 BD: 12 fires as ⭐ in same draw or ND ~50% (16.01.2024 twin)

This lens:
  • Detects silent-gap repeats in BD (and projects ND debt payments)
  • Builds sneaky tail-shapes (e.g., [_, 15, 23, 35, 47] = 12-walk)
  • Boosts the silent number in convergence (as both main + star candidate)
  • Surfaces 12-walk-compatible mains (numbers that fit a 12-gap rhythm)
"""
from __future__ import annotations
from collections import Counter
from typing import Dict, List, Optional


def _gap_walk(p: List[int]) -> Dict:
    """Compute inter-position gaps + flag silent-repeats."""
    if len(p) < 2:
        return {"gaps": [], "silent_repeats": []}
    gaps = [p[i + 1] - p[i] for i in range(len(p) - 1)]
    counts = Counter(gaps)
    silent_repeats: List[Dict] = []
    for g, c in counts.items():
        if c >= 2 and 1 <= g <= 50 and g not in p:
            silent_repeats.append({"gap": g, "count": c})
    silent_repeats.sort(key=lambda x: (-x["count"], x["gap"]))
    return {"gaps": gaps, "silent_repeats": silent_repeats}


def _build_sneaky_tails(silent_n: int, main_max: int = 50,
                         max_shapes: int = 8) -> List[Dict]:
    """For a silent number `n` (e.g., 12), build tail shapes [P3, P4, P5]
    where consecutive gaps = n. Then list the (P1, P2) families that complete
    a silent-n ×3 walk.

    Returns a list of {tail: [P3,P4,P5], p1_options: [...]} dicts.
    """
    shapes = []
    # P3 from n+1 .. main_max-2n  (so P3+n = P4, P4+n = P5 ≤ main_max)
    for p3 in range(silent_n + 1, main_max - 2 * silent_n + 1):
        p4 = p3 + silent_n
        p5 = p4 + silent_n
        if p5 > main_max:
            continue
        if silent_n in (p3, p4, p5):
            continue  # not silent if n appears as a main
        # P1 candidates: P1 < P2 < P3 with P2 = P1 + silent_n  (silent-n ×3)
        p1_options = []
        for p1 in range(1, p3 - silent_n):
            p2 = p1 + silent_n
            if p2 >= p3:
                continue
            if silent_n in (p1, p2):
                continue
            p1_options.append({"P1": p1, "P2": p2, "gaps": [silent_n, p3 - p2, silent_n, silent_n]})
        if p1_options:
            shapes.append({
                "tail": [p3, p4, p5],
                "p1_options": p1_options,
                "rule": f"silent-{silent_n} ×3 walk (gaps: {silent_n}, ?, {silent_n}, {silent_n})",
            })
        if len(shapes) >= max_shapes:
            break
    return shapes


def silent_gap_walker(recent_draws: List[Dict],
                       deep_debt_numbers: Optional[List[int]] = None,
                       main_max: int = 50) -> Dict:
    """Run the silent-gap lens on the BD and last 3 draws.

    Args:
      recent_draws: chronologically ascending; uses last 3 (BD-2, BD-1, BD)
      deep_debt_numbers: list of "deepest unpaid" candidates from other
                         lenses (e.g., 12 from RC-debt + melody-debt). The
                         lens will build sneaky-tail projections for these
                         specifically.
    """
    if not recent_draws:
        return {"available": False, "reason": "no recent draws"}

    window = recent_draws[-3:]
    scan = []
    for d in window:
        gw = _gap_walk(d["p"])
        scan.append({
            "date": d["date"],
            "mains": d["p"],
            "gaps": gw["gaps"],
            "silent_repeats": gw["silent_repeats"],
        })

    bd = scan[-1]
    bd_silent = bd["silent_repeats"]

    # Aggregate silent-numbers across the window (any silent-gap-repeat in any of 3 draws)
    all_silent: Dict[int, List[Dict]] = {}
    for s in scan:
        for sr in s["silent_repeats"]:
            all_silent.setdefault(sr["gap"], []).append({
                "date": s["date"], "count": sr["count"], "mains": s["mains"],
            })

    # If BD has a silent-gap, it's a "live carrier" — flag it
    live_silent = [{"n": sr["gap"], "count": sr["count"]} for sr in bd_silent]

    # Even ONE silent gap (count=1, not a repeat) of a deep-debt number = mini-signal
    bd_solo_debt: List[Dict] = []
    if deep_debt_numbers:
        for debt_n in deep_debt_numbers:
            if debt_n in (bd["gaps"]) and debt_n not in bd["mains"]:
                ct = bd["gaps"].count(debt_n)
                bd_solo_debt.append({
                    "n": debt_n,
                    "appearances_in_bd_gaps": ct,
                    "is_repeat": ct >= 2,
                })

    # Build sneaky-tail shapes for deep-debt numbers
    projections = []
    for n in (deep_debt_numbers or []):
        shapes = _build_sneaky_tails(n, main_max=main_max, max_shapes=12)
        if shapes:
            projections.append({
                "silent_n": n,
                "rule": (f"If cosmos pays {n} sneakily tonight, expect a tail "
                          f"with 2-3 gaps of value {n}."),
                "shapes": shapes,
            })

    # Boost candidates: numbers that fit "silent-n compatible" tail
    # i.e., for a deep-debt n, candidates = {p3, p4, p5} pairs across all shapes
    boost_candidates: Dict[int, List[str]] = {}
    for proj in projections:
        n = proj["silent_n"]
        for shape in proj["shapes"]:
            for v in shape["tail"]:
                if 1 <= v <= main_max:
                    boost_candidates.setdefault(v, []).append(f"silent-{n}-tail")
            for opt in shape["p1_options"]:
                for v in (opt["P1"], opt["P2"]):
                    if 1 <= v <= main_max:
                        boost_candidates.setdefault(v, []).append(f"silent-{n}-front")

    return {
        "available": True,
        "scan_window": scan,
        "bd_silent_repeats": live_silent,
        "bd_solo_debt": bd_solo_debt,
        "all_silent_in_window": [
            {"n": k, "events": v} for k, v in sorted(all_silent.items())
        ],
        "deep_debt_projections": projections,
        "boost_candidates": [
            {"n": n, "tags": sorted(set(tags))}
            for n, tags in sorted(boost_candidates.items())
        ],
        "rule": ("Silent-Gap Walker — when a number is silent in mains but "
                  "fires 2+ times as a gap, the cosmos is paying its debt "
                  "sneakily. ND likely pays through repetition or as ⭐. "
                  "Sneaky Universe Canon: any silent-walk projection is a "
                  "0% historical event = MIN 3 tickets coverage."),
        "sneaky_universe_warning": "0% historical exact-match shapes still require ≥3 ticket cover.",
    }
