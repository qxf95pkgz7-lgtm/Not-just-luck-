"""
💤 GHOST CLOSE DETECTOR — closures across multiple windows
============================================================
S38 canon: ghosts close in characteristic windows:
  • RAW         — ghost_n in draw at age k (any k)
  • MIRROR      — ghost_n ± 1 in draw (mirror-neighbor closure)
  • DIGIT-SWAP  — digit-swapped form in draw
  • 4-LATE      — closure at age ∈ [3, 5] (mid-Q sweet spot)
  • 9-10-DEEP   — closure at age ∈ [9, 10] (Q-anchor deep-sleep)
  • CARRIER     — ghost_n's in-lottery carrier (±25 Eu / ±21 Sw) in draw
"""
from __future__ import annotations
from typing import Dict, List

from .carrier_expansion import expand_carriers


def _digit_swap(n: int) -> int:
    s = str(n)
    return int(s[::-1]) if len(s) >= 2 else n


def detect_closures(ghost_birth: Dict, future_draws: List[Dict], mode: str) -> List[Dict]:
    """For a ghost, scan future draws and tag every closure with its window/type.

    Returns list of {age, date, draw, closure_type[s]: [...], closure_value}
    sorted by age. Empty list if never closed in window.
    """
    n = ghost_birth["n"]
    carriers = set(expand_carriers(n, mode)) - {n}
    swap = _digit_swap(n)
    out: List[Dict] = []
    for age, d in enumerate(future_draws, start=1):
        draw_set = set(d.get("p") or [])
        if not draw_set:
            continue
        types: List[str] = []
        value = None
        if n in draw_set:
            types.append("raw")
            value = n
        if (n - 1) in draw_set or (n + 1) in draw_set:
            types.append("mirror_neighbor")
            value = value if value is not None else (n - 1 if (n - 1) in draw_set else n + 1)
        if swap != n and swap in draw_set:
            types.append("digit_swap")
            value = value if value is not None else swap
        hit_carrier = draw_set & carriers
        if hit_carrier:
            types.append("carrier")
            value = value if value is not None else next(iter(hit_carrier))
        if not types:
            continue
        # Window tags
        windows: List[str] = []
        if 3 <= age <= 5:
            windows.append("4_late")
        if 9 <= age <= 10:
            windows.append("9_10_deep_sleep")
        out.append({
            "age": age,
            "date": d.get("date"),
            "closure_types": types,
            "closure_value": value,
            "windows": windows,
        })
    return out


def summarise_ghost_track(ghost_birth: Dict, closures: List[Dict]) -> Dict:
    """Summarise a ghost's life: first closure age, all closure types, alive?"""
    first = closures[0] if closures else None
    return {
        "n": ghost_birth["n"],
        "born_date": ghost_birth.get("born_date"),
        "born_door": ghost_birth.get("door"),
        "alive": len(closures) == 0,
        "first_closure_age": first["age"] if first else None,
        "first_closure_type": first["closure_types"] if first else None,
        "closure_count": len(closures),
        "deep_sleep_closure": any("9_10_deep_sleep" in c.get("windows", []) for c in closures),
        "late_closure_4_5": any("4_late" in c.get("windows", []) for c in closures),
    }
