"""
💧 SATURATION LEDGER — 47×4 type saturation watch
==================================================
S34 canon:
  47 fired at P5 in 4 of last 5 Euro draws → SATURATED → expected to drop
  out and force a P5 collapse (<41 zone).

Generic rule: any number appearing ≥ 3 times in last `window` draws is a
"saturation magnet" — flagged as ABOUT TO BE BENCHED. Conversely, the
position freed up becomes a forward-echo target.
"""
from __future__ import annotations
from collections import Counter
from typing import Dict, List


def saturation_ledger(recent_draws: List[Dict], mode: str, window: int = 5,
                       threshold: int = 3) -> Dict:
    """Count appearances of every main and star across the last `window` draws.
    Flag those at >= `threshold`.
    """
    last = recent_draws[-window:] if len(recent_draws) > window else recent_draws
    main_counts = Counter()
    star_counts = Counter()
    pos_counts: Dict[int, Counter] = {0: Counter(), 1: Counter(), 2: Counter(),
                                       3: Counter(), 4: Counter(), 5: Counter()}
    for d in last:
        for i, n in enumerate(d["p"]):
            main_counts[n] += 1
            if i in pos_counts:
                pos_counts[i][n] += 1
        if mode == "euro" and d.get("stars"):
            for s in d["stars"]:
                star_counts[s] += 1

    saturated_mains = [{"n": n, "count": c}
                       for n, c in main_counts.most_common()
                       if c >= threshold]
    saturated_stars = [{"s": s, "count": c}
                       for s, c in star_counts.most_common()
                       if c >= threshold]
    # Per-position saturation (e.g., 47 always at P5)
    pos_saturation = []
    for i, ctr in pos_counts.items():
        for n, c in ctr.most_common(2):
            if c >= threshold:
                pos_saturation.append({
                    "position": f"P{i+1}",
                    "n": n,
                    "count": c,
                })

    return {
        "window": len(last),
        "saturated_mains": saturated_mains,
        "saturated_stars": saturated_stars,
        "position_saturation": pos_saturation,
        "rule": f">={threshold}/{window} appearances = magnet at saturation. Expect drop-out + forward echo at freed seat.",
    }
