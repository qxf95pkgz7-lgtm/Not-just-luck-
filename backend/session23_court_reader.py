"""
🎻🎧🥂 SESSION 23 · COURT-OF-SLOT + HARD-P SHAPES THE D
=========================================================
Laws 62 (Hard-P) + 63 (Court-of-Slot) pure primitives.

Every d has ONE structurally hard P that defines its shape. The hard P is
identified by the slot whose court (its last 2-3 verdicts) speaks loudest.

Court verdicts (per slot, per d):
  HOLD          - same value as prior draw at same slot (4-5 weight)
  WALK          - +1/-1 staircase from prior 2 draws (3.5 weight, Euro-mostly)
  EDGE          - extreme value vs slot band (3 weight)
  ANCHOR-RETURN - value seen 2-3 draws ago at same slot (2 weight)

Q1 2026 Swiss grammar = 48% HOLD · 40% EDGE · 0% WALK
Euro is WALK-friendly. Don't apply Euro grammar to Swiss frames.

Canonical examples (validated against The Book):
  - 24.04.2026 Euro P3 walked 28→29→30 (DJ's call)
  - HUGE 07.02.2026 Swiss telegraphed by P6=38 HOLD ×2 in a row

References: /app/memory/swiss_music_notes.md (Session 23, lines 4505+)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

# Slot bands (low/high tolerated values) — used for EDGE detection.
# Swiss-friendly defaults; tighten externally for Euro if needed.
SWISS_SLOT_BANDS = {
    1: (1, 12),  # P1 — front edge
    2: (5, 22),
    3: (10, 28),
    4: (16, 34),
    5: (22, 39),
    6: (28, 42),  # P6 — back edge
}

EURO_SLOT_BANDS = {
    1: (1, 18),
    2: (6, 26),
    3: (14, 36),
    4: (22, 44),
    5: (30, 50),
}

VERDICT_WEIGHT = {
    'HOLD': 4.5,
    'WALK': 3.5,
    'EDGE': 3.0,
    'ANCHOR-RETURN': 2.0,
}


def _slot_history(cycle: List[Dict], slot_idx: int, look_back: int = 3) -> List[int]:
    """Return the last `look_back` values that appeared at `slot_idx` (1-indexed)
    across the most recent draws of `cycle`. Each draw must expose `_n` (sorted
    mains list)."""
    history: List[int] = []
    for d in reversed(cycle):
        mains = sorted(d.get('_n', []))
        if len(mains) >= slot_idx:
            history.append(mains[slot_idx - 1])
            if len(history) >= look_back:
                break
    return history  # most-recent first


def _is_edge(value: int, slot_idx: int, bands: Dict[int, Tuple[int, int]]) -> bool:
    band = bands.get(slot_idx)
    if not band:
        return False
    lo, hi = band
    span = max(1, hi - lo)
    # Edge = within bottom or top 20% of the band
    return value <= lo + span * 0.20 or value >= hi - span * 0.20


def slot_court(
    cycle: List[Dict],
    slot_idx: int,
    bands: Optional[Dict[int, Tuple[int, int]]] = None,
    look_back: int = 3,
) -> Dict:
    """Read the court of one slot.

    Returns:
        {
          'slot': int,
          'history': List[int]           # most-recent-first
          'flavor': 'HOLD'|'WALK'|'EDGE'|'ANCHOR-RETURN'|None,
          'predicted_value': int|None,   # what the court is likely to deliver
          'score': float,                # verdict weight (0 if no verdict)
        }
    """
    bands = bands or SWISS_SLOT_BANDS
    h = _slot_history(cycle, slot_idx, look_back=look_back)
    if not h:
        return {'slot': slot_idx, 'history': [], 'flavor': None,
                'predicted_value': None, 'score': 0.0}

    flavor = None
    predicted = None
    score = 0.0

    # HOLD — last two values identical (e.g. P6=38, 38)
    if len(h) >= 2 and h[0] == h[1]:
        flavor = 'HOLD'
        predicted = h[0]
        score = VERDICT_WEIGHT['HOLD']
    # WALK — strict staircase +1 or -1 across the last 3 draws
    elif len(h) >= 3 and (h[2] + 1 == h[1] and h[1] + 1 == h[0]):
        flavor = 'WALK'
        predicted = h[0] + 1
        if predicted > 50:
            predicted = h[0]
        score = VERDICT_WEIGHT['WALK']
    elif len(h) >= 3 and (h[2] - 1 == h[1] and h[1] - 1 == h[0]):
        flavor = 'WALK'
        predicted = max(1, h[0] - 1)
        score = VERDICT_WEIGHT['WALK']
    # ANCHOR-RETURN — same value 2-3 draws ago
    elif len(h) >= 3 and h[2] == h[0]:
        flavor = 'ANCHOR-RETURN'
        predicted = h[0]
        score = VERDICT_WEIGHT['ANCHOR-RETURN']
    # EDGE — last value sits in the slot's outer 20%
    elif _is_edge(h[0], slot_idx, bands):
        flavor = 'EDGE'
        predicted = h[0]  # cosmos likes to repeat the edge
        score = VERDICT_WEIGHT['EDGE']

    return {'slot': slot_idx, 'history': h, 'flavor': flavor,
            'predicted_value': predicted, 'score': score}


def find_hard_p(
    cycle: List[Dict],
    bands: Optional[Dict[int, Tuple[int, int]]] = None,
    n_slots: int = 6,
) -> Optional[Dict]:
    """Read every slot's court and return the loudest one.

    Returns the slot with the highest verdict score. Tie-breaker: highest
    slot index (per Book — back slots carry more structural weight).
    """
    bands = bands or SWISS_SLOT_BANDS
    courts = [slot_court(cycle, i, bands) for i in range(1, n_slots + 1)]
    voiced = [c for c in courts if c['flavor'] is not None]
    if not voiced:
        return None
    voiced.sort(key=lambda c: (c['score'], c['slot']), reverse=True)
    return voiced[0]


def all_courts(
    cycle: List[Dict],
    bands: Optional[Dict[int, Tuple[int, int]]] = None,
    n_slots: int = 6,
) -> List[Dict]:
    """Return every slot's court for transparency (UI/DJ widget)."""
    bands = bands or SWISS_SLOT_BANDS
    return [slot_court(cycle, i, bands) for i in range(1, n_slots + 1)]
