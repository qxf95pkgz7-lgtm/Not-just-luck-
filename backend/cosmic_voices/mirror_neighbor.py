"""
🪞 MIRROR NEIGHBOR LENS — `cosmic_voices/mirror_neighbor.py` (Lens #13)
=======================================================================
DJ canon (Session 36, 08.05.2026 post-draw analysis):

Tonight's draw [2, 17, 19, 34, 37] paid through ±1 NEIGHBORS of every shout:
  • 18 (5-lens)  →  17 ✓  +  19 ✓  (sandwich!)
  • 33 (3-lens)  →  34 ✓
  • 36 (4-lens)  →  37 ✓

The cosmos lands in the GRAVITATIONAL WELL — the densest neighborhood —
not on the peak itself. Mirror-neighbor expansion is the brain's first
spatial-reasoning layer.

Rule:
  for every n with score s in shout/whisper:
    score(n±1) += 0.5 · s
    score(n±2) += 0.25 · s
"""
from __future__ import annotations
from collections import defaultdict
from typing import Dict, List


def mirror_neighbor_expand(ranked_mains: List[Dict], main_max: int = 50) -> Dict:
    """Expand a ranked list with ±1, ±2 neighbor seeds.

    Args:
      ranked_mains: list of {n, score, tags} dicts (e.g., conv ranked_mains)

    Returns:
      {neighbor_seeds: {n: [tags]}, expanded_ranked: [...]}
    """
    seeds: Dict[int, List[str]] = defaultdict(list)
    base_score: Dict[int, float] = {m["n"]: float(m["score"]) for m in ranked_mains}

    for m in ranked_mains:
        n = m["n"]
        s = float(m["score"])
        for delta, weight in ((1, 0.5), (-1, 0.5), (2, 0.25), (-2, 0.25)):
            neighbor = n + delta
            if 1 <= neighbor <= main_max and neighbor != n:
                seeds[neighbor].append(f"mirror±{abs(delta)}-of-{n}(+{weight*s:.1f})")
                base_score[neighbor] = base_score.get(neighbor, 0) + weight * s

    # Recompute ranked list with expansion
    expanded = []
    for n in range(1, main_max + 1):
        if n in base_score:
            existing = next((m for m in ranked_mains if m["n"] == n), None)
            tags = list(existing["tags"]) if existing else []
            tags.extend(seeds.get(n, []))
            expanded.append({
                "n": n,
                "score": round(base_score[n], 2),
                "tags": tags,
                "is_neighbor_only": existing is None,
            })
    expanded.sort(key=lambda x: (-x["score"], x["n"]))

    return {
        "neighbor_seeds": dict(seeds),
        "expanded_ranked": expanded[:25],
        "shout_expanded": [m for m in expanded if m["score"] >= 3],
        "whisper_expanded": [m for m in expanded if 2 <= m["score"] < 3],
        "rule": "Cosmos lands in densest neighborhood. ±1 = 0.5 weight, ±2 = 0.25 weight.",
    }
