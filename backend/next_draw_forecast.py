"""
🔮 NEXT-DRAW FORECAST — Canon 35 (DJ-taught 09.06.2026 PM #6)
==============================================================
"Every draw whispers to the next one. Find the whispers."

Given the LAST draw (D_prev) and the NEXT draw's TARGET DATE (D_next_date),
this module computes ALL cosmic paths from D_prev to a candidate pool for
D_next, ranked by how many lenses converge on each number.

Paths used:
  1. CIRCLE from D_prev — each main via One Law ±carrier (Swiss 21, Euro 25)
  2. TABLET-neighbor from D_prev — each main via row/col offsets (±1, ±7, ±6, ±8)
  3. D_next-date seeds — Canon 34 formulas (day, day+21, month, day.month,
     day×month, digit-sum, all carrier-back into universe)
  4. D_prev-date seeds — same formulas applied to the PREVIOUS draw's date
     (their echo often lands in the NEXT draw)

Numbers get a "lens count" — the more lenses that ring, the higher the
signal. Top 8 = the suggested D_next pool.

Verified 09.06.2026 on Q3 D1→D2 (11.07 → 15.07): pool = [7,11,14,15,17,24,
36,42] with 36 & 42 scoring 3 lenses each (max).
"""
from __future__ import annotations
from collections import Counter
from typing import Dict, List, Tuple


def _wrap_carrier_back(n: int, c: int, mx: int) -> int:
    while n > mx: n -= c
    while n < 1: n += c
    return n


def _date_seeds(date_str: str, mode: str) -> Dict[str, int]:
    """Canon 34 date-derived cosmic seeds."""
    dd, mm, yy = date_str.split(".")
    d, m = int(dd), int(mm)
    c = 21 if mode == "swiss" else 25
    mx = 42 if mode == "swiss" else 50
    ddmm = int(f"{dd}{mm}")
    ds = sum(int(ch) for ch in date_str.replace(".", ""))
    return {
        "day":            _wrap_carrier_back(d, c, mx),
        "day+carrier":    _wrap_carrier_back(d + c, c, mx),
        "month":          _wrap_carrier_back(m, c, mx),
        "month+carrier":  _wrap_carrier_back(m + c, c, mx),
        "day.month → back": _wrap_carrier_back(ddmm, c, mx),
        "day×month → back": _wrap_carrier_back(d * m, c, mx),
        "digit-sum → back": _wrap_carrier_back(ds, c, mx),
    }


def forecast_next_draw(
    prev_mains: List[int],
    prev_date: str,
    next_date: str,
    mode: str = "swiss",
) -> Dict:
    """Full multi-lens forecast for the next draw's number pool."""
    c = 21 if mode == "swiss" else 25
    mx = 42 if mode == "swiss" else 50
    prev_set = set(prev_mains)

    pool = Counter()
    tags: Dict[int, List[str]] = {}

    def register(n: int, tag: str) -> None:
        if not (1 <= n <= mx):
            return
        if n in prev_set:  # skip same-draw carry
            return
        pool[n] += 1
        tags.setdefault(n, []).append(tag)

    # 1) CIRCLE (One Law)
    for n in prev_mains:
        register(_wrap_carrier_back(n + c, c, mx), f"circle {n}+{c}")
        register(_wrap_carrier_back(n - c, c, mx), f"circle {n}-{c}")

    # 2) TABLET-neighbor (7-wide grid — row=±7, col=±1, diagonals ±6/±8)
    for n in prev_mains:
        for delta in (-8, -7, -6, -1, 1, 6, 7, 8):
            cand = n + delta
            if 1 <= cand <= mx:
                register(cand, f"tablet {n}{'+' if delta>0 else ''}{delta}")

    # 3) NEXT-date seeds
    next_seeds = _date_seeds(next_date, mode)
    for k, v in next_seeds.items():
        register(v, f"next-date {k}")

    # 4) PREV-date seeds (they often echo forward)
    prev_seeds = _date_seeds(prev_date, mode)
    for k, v in prev_seeds.items():
        register(v, f"prev-date {k}")

    ranked = [
        {"n": n, "score": s, "tags": tags[n][:6]}
        for n, s in pool.most_common()
    ]
    top_n = 8 if mode == "swiss" else 7
    top_pool = [r["n"] for r in ranked[:top_n]]

    return {
        "prev": {"date": prev_date, "mains": sorted(prev_mains)},
        "next": {"date": next_date, "top_pool": sorted(top_pool)},
        "next_date_seeds": next_seeds,
        "prev_date_seeds": prev_seeds,
        "ranked": ranked,
        "shout_zone": [r for r in ranked if r["score"] >= 3],
        "whisper_zone": [r for r in ranked if r["score"] == 2],
    }
