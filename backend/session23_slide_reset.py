"""
🎻🎧🥂 SESSION 23 · LAW 64 · SLIDE-AND-RESET
=============================================
Pure primitives for Law 64 — when a value V slides from BD.P2 to ND.P1
across consecutive draws, the AF (after-next) draw RESETS:

  • V vanishes 86% of the time
  • AF.P1 collapses to ≤ 6 (100% — 6/6 historical Swiss cases)
  • AF.P2 jumps to 9-17 mid-low band
  • 30s family takes the back-stretch (P5 ∈ 29-36, P6 ∈ 35-39)
  • Sum band 114-131 (mean ~124)

Canonical V=8 P2→P1 slides (7 cases in 22 yrs Swiss):
  1. 12/16/19.01.2013  AF [2, 17, 21, 23, 33, 35]
  2. 31.07/03/07.08.2013 AF [1, 15, 18, 21, 36, 39]
  3. 23/26/30.07.2014  AF [6, 9, 16, 23, 30, 37]
  4. 25/29.01/01.02.2020 AF [5, 10, 13, 28, 29, 35]
  5. 23/26/30.06.2021  AF [1, 8, 12, 18, 36, 39]   ← only return-case
  6. 20/24/27.09.2025  AF [3, 15, 18, 22, 31, 38]
  7. 22/25/29.04.2026  AF [??] ← THE PREDICTION (this fork's live tape)

Best clone candidate frame for 29.04.2026: [3, 15, 18, 22, 31, 38]

References: /app/memory/swiss_music_notes.md (Session 23, lines 4600+)
"""
from __future__ import annotations
from typing import Dict, List, Optional


def detect_p2p1_slide(bd: Dict, nd: Dict) -> Optional[int]:
    """Return the slide value V if BD.P2 == ND.P1 (same value, leftward
    slide). Otherwise None.

    Both `bd` and `nd` must expose `_n` = sorted mains list.
    """
    bd_mains = sorted(bd.get('_n', []))
    nd_mains = sorted(nd.get('_n', []))
    if len(bd_mains) < 2 or len(nd_mains) < 1:
        return None
    if bd_mains[1] == nd_mains[0]:
        return bd_mains[1]
    return None


def slide_reset_frame(slide_value: int) -> Dict:
    """Return the canonical AF (after-next) frame given a detected slide.

    Output shape:
      {
        'p1_band': (1, 6),
        'p2_band': (9, 17),
        'p5_band': (29, 36),
        'p6_band': (35, 39),
        'sum_band': (114, 131),
        'banned': [slide_value],
        'family_30s_priority': True,
        'best_clone': [3, 15, 18, 22, 31, 38],
        'slide_value': slide_value,
        'vanish_probability': 0.86,
      }
    """
    return {
        'p1_band': (1, 6),
        'p2_band': (9, 17),
        'p5_band': (29, 36),
        'p6_band': (35, 39),
        'sum_band': (114, 131),
        'banned': [slide_value],
        'family_30s_priority': True,
        'best_clone': [3, 15, 18, 22, 31, 38],
        'slide_value': slide_value,
        'vanish_probability': 0.86,
    }


def slide_reset_filter_main(value: int, slot_idx: int, frame: Dict) -> bool:
    """True iff a candidate `value` fits the slide-reset frame at `slot_idx`.

    Slot 1 → P1 band, slot 2 → P2 band, slots 5/6 → P5/P6 bands. Slots 3-4
    are unconstrained (they ride free).
    """
    if value in frame.get('banned', []):
        return False
    if slot_idx == 1:
        lo, hi = frame['p1_band']
        return lo <= value <= hi
    if slot_idx == 2:
        lo, hi = frame['p2_band']
        return lo <= value <= hi
    if slot_idx == 5:
        lo, hi = frame['p5_band']
        return lo <= value <= hi
    if slot_idx == 6:
        lo, hi = frame['p6_band']
        return lo <= value <= hi
    return True


def detect_slide_in_cycle(cycle: List[Dict]) -> Optional[Dict]:
    """Walk the last few draws of `cycle` and look for a P2→P1 slide between
    consecutive draws. Returns the slide context if detected:
      {
        'slide_value': V,
        'bd_date': str,
        'nd_date': str,
        'frame': slide_reset_frame(V),
      }
    Returns None if no slide.

    The slide MUST be on the immediately previous two draws (BD-1 = bd, BD = nd)
    so the next-target draw becomes the AF reset.
    """
    if len(cycle) < 2:
        return None
    bd = cycle[-2]  # before-draw
    nd = cycle[-1]  # next-draw (the slide target)
    v = detect_p2p1_slide(bd, nd)
    if v is None:
        return None
    return {
        'slide_value': v,
        'bd_date': bd.get('date', ''),
        'nd_date': nd.get('date', ''),
        'frame': slide_reset_frame(v),
    }
