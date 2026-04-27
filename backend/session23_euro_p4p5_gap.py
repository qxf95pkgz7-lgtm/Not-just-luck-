"""
🎻🎧🥂 LAW 66 · EURO P4-P5 GAP COLLAPSE
========================================
Validated on 1619 EuroMillions draws (full historical tape).

The same monotonic decay as Swiss Law 65 — the cosmos sticks P5 closer
to P4 as P4 climbs:

  P4 band  →  avg gap  →  P5 likely band      n      pct
  ──────────────────────────────────────────────────────────
  20-29    →   12.80   →   29-44       (361 draws, 22.3%)
  30-34    →    9.65   →   34-44       (319 draws, 19.7%)
  35-39    →    7.07   →   39-46       (351 draws, 21.7%)
  40-44    →    4.44   →   42-50       (337 draws, 20.8%)
  45-49    →    2.56   →   46-50       (153 draws,  9.5%)  ← COLLAPSE

Most-common pairs:
  (45,48) gap=3: 1.11% — the Euro king pair
  (45,49) gap=4: 1.05%
  (39,44) gap=5: 0.93%
  (48,50) gap=2: 0.93%
  (43,46) gap=3: 0.93%
  (47,48) gap=1: 0.80%

DJ's Euro slot bands (proportional to Swiss canonical bands):
  P1: 1 → 35   (rare 26-35 = ≤5% tix)
  P2: 2 → 38
  P3: 5 → 43
  P4: 9 → 49   (<13 = very rare)
  P5: 16 → 50  (<25 = ≤2% tix, <16 forbidden — only 0/1619)

References: /app/memory/swiss_music_notes.md (Session 23 fork, Euro
gap-distribution scan 28.04.2026).
"""
from __future__ import annotations
from typing import List, Tuple

# DJ's Euro slot bands (canonized 28.04.2026, fork)
EURO_BANDS_DJ = {
    1: (1, 35),
    2: (2, 38),
    3: (5, 43),
    4: (9, 49),
    5: (16, 50),
}

# Rare-zone gates for Euro
EURO_RARE_ZONES = {
    'P1_high':  {'slot': 1, 'lo': 26, 'hi': 35, 'share_pct': 0.05},
    'P4_low':   {'slot': 4, 'lo': 9,  'hi': 12, 'share_pct': 0.05},
    'P5_low':   {'slot': 5, 'lo': 16, 'hi': 24, 'share_pct': 0.02},
}

# Per P4-band: (gap_lo, gap_hi, p5_lo, p5_hi) — captures inner 80% +
# accommodates historical king pairs (e.g. (38,48), (38,49) gap≈10-11).
P4_BAND_GAP_LAW = [
    # (p4_lo, p4_hi, gap_lo, gap_hi, p5_lo, p5_hi)
    (20, 29,  3, 22, 29, 50),
    (30, 34,  3, 16, 34, 50),
    (35, 39,  2, 12, 39, 50),
    (40, 44,  2,  9, 42, 50),
    (45, 49,  1,  5, 46, 50),
]

# Most-historical (P4, P5) king pairs — top 12 anchors
P4_P5_KING_PAIRS = [
    (45, 48), (45, 49), (39, 44), (48, 50), (43, 46), (46, 49),
    (38, 48), (42, 45), (47, 50), (44, 48), (47, 48), (44, 50),
]


def gap_law_for_p4(p4: int) -> Tuple[int, int, int, int]:
    """Return (gap_lo, gap_hi, p5_lo, p5_hi) for a given P4."""
    for p4_lo, p4_hi, gap_lo, gap_hi, p5_lo, p5_hi in P4_BAND_GAP_LAW:
        if p4_lo <= p4 <= p4_hi:
            return (gap_lo, gap_hi, p5_lo, p5_hi)
    if p4 < 20:
        return (5, 25, 25, 50)
    return (1, 5, 46, 50)


def p5_fits_p4(p4: int, p5: int) -> bool:
    """True iff (P4, P5) lands in the historical gap-band for that P4."""
    if p5 <= p4:
        return False
    gap_lo, gap_hi, p5_lo, p5_hi = gap_law_for_p4(p4)
    gap = p5 - p4
    if not (gap_lo <= gap <= gap_hi):
        return False
    return p5_lo <= p5 <= p5_hi


def is_king_pair(p4: int, p5: int) -> bool:
    """True iff (P4, P5) is in the top-12 historical king pairs."""
    return (p4, p5) in P4_P5_KING_PAIRS


def expected_p5_band(p4: int) -> Tuple[int, int]:
    """Return the (lo, hi) P5 band for a given P4."""
    gap_lo, gap_hi, p5_lo, p5_hi = gap_law_for_p4(p4)
    derived_lo = max(p5_lo, p4 + gap_lo)
    derived_hi = min(p5_hi, p4 + gap_hi)
    if derived_lo > derived_hi:
        derived_lo, derived_hi = p5_lo, p5_hi
    return (derived_lo, derived_hi)


def is_rare_zone(value: int, slot_idx: int) -> bool:
    """True if (value, slot) lands in a Euro rare-zone gate."""
    for zone in EURO_RARE_ZONES.values():
        if zone['slot'] == slot_idx and zone['lo'] <= value <= zone['hi']:
            return True
    return False
