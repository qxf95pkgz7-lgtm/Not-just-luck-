"""
🪞 INTERNAL MIRROR LAW — 56-pair / 28-pair scanner + SWITCH detection
=====================================================================
S34 canon:
  56-pair INSIDE a single draw: 15.2% baseline (rises to 40% in hot streak)
  28-pair INSIDE a single draw: 7.1% baseline (rare but meaningful)

  The cosmos ALTERNATES between 56-song and 28-song. When a 28-pair returns
  AFTER 3+ straight 56-pair draws → SWITCH TRIGGER (next 2-3 draws ride the
  new tune).
"""
from __future__ import annotations
from typing import Dict, List


def _has_pair_summing(nums: List[int], target_sum: int) -> List:
    pairs = []
    s = set(nums)
    for n in nums:
        partner = target_sum - n
        if partner != n and partner in s and partner > n:
            pairs.append([n, partner])
    return pairs


def internal_mirror_scan(recent_draws: List[Dict], lookback: int = 10) -> Dict:
    """For each of the last `lookback` draws, detect internal 56/28 pairs.
    Then identify any 56→28 SWITCH event in the sequence.
    """
    window = recent_draws[-lookback:] if len(recent_draws) > lookback else recent_draws

    series = []
    for d in window:
        p56 = _has_pair_summing(d["p"], 56)
        p28 = _has_pair_summing(d["p"], 28)
        tune = "56" if p56 else ("28" if p28 else "—")
        series.append({
            "date": d["date"],
            "p56_pairs": p56,
            "p28_pairs": p28,
            "tune": tune,
        })

    # Detect SWITCH: 3+ consecutive 56 entries → followed by a 28 entry
    switch_events: List[Dict] = []
    for i in range(3, len(series)):
        if (series[i]["tune"] == "28"
                and all(series[j]["tune"] == "56" for j in range(i - 3, i))):
            switch_events.append({
                "switched_at": series[i]["date"],
                "from": "56-song",
                "to": "28-song",
                "preceding_56_streak": 3,
            })

    p56_count = sum(1 for s in series if s["tune"] == "56")
    p28_count = sum(1 for s in series if s["tune"] == "28")
    hot_streak_56 = round(100 * p56_count / max(1, len(series)), 1)

    return {
        "series": series,
        "p56_count": p56_count,
        "p28_count": p28_count,
        "hot_streak_56_pct": hot_streak_56,
        "switch_events": switch_events,
        "current_tune": series[-1]["tune"] if series else "—",
        "rule": "56/28-pair confirmation lens. 56→28 SWITCH = +30 weight signal for next 2-3 draws.",
    }
