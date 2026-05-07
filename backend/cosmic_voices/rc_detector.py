"""
🎯 RC DETECTOR — find the last Rare-Cycle anchor (RC0)
======================================================
DJ canon: A "Rare Compact" draw is the harmonic anchor of a ~90-draw cycle.

  Euro:  P1..P4 span ≤ 7  AND  P5 jump ≥ 6
  Swiss: P1..P5 span ≤ 10 AND  P6 jump ≥ 8

Returns the most recent RC anchor BEFORE target_date along with days-since
and the RC seed digits (mains + stars / lucky+replay).
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional


def _is_rc_compact(p: List[int], mode: str) -> bool:
    if mode == "euro":
        if len(p) < 5:
            return False
        front_span = p[3] - p[0]
        back_jump = p[4] - p[3]
        return front_span <= 7 and back_jump >= 6
    # swiss
    if len(p) < 6:
        return False
    front_span = p[4] - p[0]
    back_jump = p[5] - p[4]
    return front_span <= 10 and back_jump >= 8


def detect_rc_anchor(target_dt: datetime, draws: List[Dict], mode: str) -> Optional[Dict]:
    """Walk back through `draws` (must be chronologically ascending with 'dt' fields).
    Return the most recent RC compact draw before target_dt.
    """
    past = [d for d in draws if d["dt"] < target_dt]
    past.sort(key=lambda x: x["dt"], reverse=True)
    for d in past:
        if _is_rc_compact(d["p"], mode):
            anchor = {
                "date": d["date"],
                "mains": d["p"],
                "stars": d.get("stars"),
                "lucky": d.get("lucky"),
                "replay": d.get("replay"),
                "days_since": (target_dt - d["dt"]).days,
                "draws_since": past.index(d),  # how many draws ago
                "front_span": (d["p"][3] - d["p"][0]) if mode == "euro" else (d["p"][4] - d["p"][0]),
                "back_jump": (d["p"][4] - d["p"][3]) if mode == "euro" else (d["p"][5] - d["p"][4]),
            }
            return anchor
    return None
