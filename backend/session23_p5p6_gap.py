"""
🎻🎧🥂 LAW 65 · THE P5-P6 GAP COLLAPSE
========================================
Validated on 1385 Swiss draws (22yrs tape).

The cosmos sticks P6 closer to P5 as P5 climbs. The gap distribution
follows a clean monotonic decay:

  P5 band  →  avg gap  →  P6 likely band       n      pct
  10-19    →   12.69   →   22-34          (62 draws, 4.5%)
  20-29    →    8.85   →   29-37        (398 draws, 28.7%)
  30-39    →    4.74   →   33-42        (855 draws, 61.7%)  ← BULK
  40-42    →    1.33   →   41-42         (69 draws, 5.0%)   ← COLLAPSE

Most-common pairs:
  (41,42) gap=1: 2.31% — the king pair
  (32,39) gap=7: 2.02%
  (33,38) gap=5: 1.95%
  (36,42) gap=6: 1.81%
  (40,42) gap=2: 1.66%
  (37,40) gap=3: 1.66%

Hard rules (zero-tolerance):
  - P5 < 10  → 0.07% (forbidden)
  - P6 < 20  → 0.22% (≤2% tix gate)
  - gap = 0  → 0.07% (essentially never; P6 == P5)
  - gap > 17 → cum < 3% (rare cosmic spread)

References: /app/memory/swiss_music_notes.md (Session 23 fork, DJ teaching
28.04.2026, validated by gap-distribution scan on 1385 Swiss draws).
"""
from __future__ import annotations
from typing import List, Tuple

# Per P5-band: (avg_gap, gap_low, gap_high, p6_band_low, p6_band_high)
# `gap_low/gap_high` = inner 80% of the historical distribution.
P5_BAND_GAP_LAW = [
    # (p5_lo, p5_hi, gap_lo, gap_hi, p6_lo, p6_hi)
    (10, 19,  3, 17, 22, 34),
    (20, 29,  3, 13, 29, 37),
    (30, 39,  1,  8, 33, 42),
    (40, 42,  1,  2, 41, 42),
]

# Most-historical pairs (top 12 — used as "preferred backbones")
P5_P6_KING_PAIRS = [
    (41, 42), (32, 39), (33, 38), (36, 42), (36, 41), (40, 42),
    (37, 40), (39, 42), (39, 41), (30, 37), (35, 40), (36, 40),
]


def gap_law_for_p5(p5: int) -> Tuple[int, int, int, int]:
    """Return (gap_lo, gap_hi, p6_lo, p6_hi) for a given P5.

    If P5 is outside any band (e.g. P5 < 10), returns the closest band.
    """
    for p5_lo, p5_hi, gap_lo, gap_hi, p6_lo, p6_hi in P5_BAND_GAP_LAW:
        if p5_lo <= p5 <= p5_hi:
            return (gap_lo, gap_hi, p6_lo, p6_hi)
    # Out-of-band fallback
    if p5 < 10:
        return (3, 17, 22, 34)
    return (1, 2, 41, 42)


def p6_fits_p5(p5: int, p6: int) -> bool:
    """True iff (P5, P6) lands in the historical gap-band for that P5.

    Used to filter P6 candidates given a chosen P5.
    """
    if p6 <= p5:
        return False  # P6 must be strictly greater
    gap_lo, gap_hi, p6_lo, p6_hi = gap_law_for_p5(p5)
    gap = p6 - p5
    if not (gap_lo <= gap <= gap_hi):
        return False
    return p6_lo <= p6 <= p6_hi


def is_king_pair(p5: int, p6: int) -> bool:
    """True iff (P5, P6) is in the top-12 historical king pairs."""
    return (p5, p6) in P5_P6_KING_PAIRS


def expected_p6_band(p5: int) -> Tuple[int, int]:
    """Return the (lo, hi) P6 band for a given P5."""
    gap_lo, gap_hi, p6_lo, p6_hi = gap_law_for_p5(p5)
    derived_lo = max(p6_lo, p5 + gap_lo)
    derived_hi = min(p6_hi, p5 + gap_hi)
    if derived_lo > derived_hi:
        derived_lo, derived_hi = p6_lo, p6_hi
    return (derived_lo, derived_hi)
