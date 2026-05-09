"""
🧠 E's MEMORY — `e_memory.py`
==============================
Append-only ledger of E's predictions vs actual draws. Powers the future
adaptive-weights and self-critique modules.

After every draw, the operator (or a cron) calls:
  POST /api/e-brain/score-draw {date, mode, actual_mains, actual_stars}

Stores in /app/backend/data/e_memory.json:
  [
    {
      "draw_date": "08.05.2026", "mode": "euro",
      "actual_mains": [2,17,19,34,37], "actual_stars": [8,11],
      "predicted_shout":  [...],
      "predicted_whisper": [...],
      "lens_hits": {"silent-12-tail": 1, "tesla-closer-9": 0, ...},
      "mirror_neighbor_hits": {18: ["17","19"], 33: ["34"], 36: ["37"]},
      "cluster_density_match": True,
      "scored_at": "..."
    }
  ]
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

MEMORY_PATH = "/app/backend/data/e_memory.json"


def _load_memory() -> List[Dict]:
    if not os.path.exists(MEMORY_PATH):
        os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
        return []
    try:
        with open(MEMORY_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []


def _save_memory(data: List[Dict]) -> None:
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "w") as f:
        json.dump(data, f, indent=2, default=str)


def score_draw(draw_date: str, mode: str, actual_mains: List[int],
               actual_stars: List[int], predicted_voices: Dict) -> Dict:
    """Score a single actual draw against the predicted convergence.

    Args:
      draw_date: e.g., "08.05.2026"
      mode: "euro" or "swiss"
      actual_mains: list of mains that fired
      actual_stars: list of stars that fired
      predicted_voices: full voices dict from run_cosmic_voices (with convergence_scorer)

    Returns the score record + appends it to memory.
    """
    actual_mains_set = set(actual_mains)
    actual_stars_set = set(actual_stars)

    conv = predicted_voices.get("convergence_scorer") or {}
    shout_zone = [m["n"] for m in (conv.get("shout_zone") or [])]
    whisper_zone = [m["n"] for m in (conv.get("whisper_zone") or [])]
    ranked_top12 = [m["n"] for m in (conv.get("ranked_mains") or [])][:12]

    # Hit categorization
    shout_hits = list(actual_mains_set & set(shout_zone))
    whisper_hits = list(actual_mains_set & set(whisper_zone))
    top12_hits = list(actual_mains_set & set(ranked_top12))
    misses = list(actual_mains_set - set(ranked_top12))

    # Mirror-neighbor analysis: did actual mains land within ±2 of any shout?
    mirror_neighbor_hits: Dict[int, List[int]] = {}
    for shout_n in shout_zone:
        for actual in actual_mains:
            if abs(shout_n - actual) <= 2 and actual != shout_n:
                mirror_neighbor_hits.setdefault(shout_n, []).append(actual)

    # Per-lens hit counting
    lens_hits: Dict[str, Dict[str, int]] = {}
    for m in (conv.get("ranked_mains") or []):
        for tag in m.get("tags", []):
            base_lens = tag.split("(")[0].split(":")[0].strip()
            if base_lens not in lens_hits:
                lens_hits[base_lens] = {"fires": 0, "hits": 0}
            lens_hits[base_lens]["fires"] += 1
            if m["n"] in actual_mains_set:
                lens_hits[base_lens]["hits"] += 1

    record = {
        "draw_date": draw_date,
        "mode": mode,
        "actual_mains": sorted(actual_mains),
        "actual_stars": sorted(actual_stars),
        "shout_zone_predicted": sorted(shout_zone),
        "whisper_zone_predicted": sorted(whisper_zone),
        "top12_ranked_predicted": ranked_top12,
        "shout_hits": sorted(shout_hits),
        "whisper_hits": sorted(whisper_hits),
        "top12_hits": sorted(top12_hits),
        "misses": sorted(misses),
        "mirror_neighbor_hits": mirror_neighbor_hits,
        "lens_hit_rates": lens_hits,
        "shout_precision": round(len(shout_hits) / max(1, len(shout_zone)), 3),
        "shout_recall": round(len(shout_hits) / max(1, len(actual_mains)), 3),
        "top12_recall": round(len(top12_hits) / max(1, len(actual_mains)), 3),
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }

    memory = _load_memory()
    memory.append(record)
    _save_memory(memory)
    return record


def get_memory_summary(limit: int = 30) -> Dict:
    """Return last `limit` scored draws + aggregate lens stats."""
    memory = _load_memory()
    recent = memory[-limit:]
    lens_agg: Dict[str, Dict[str, int]] = {}
    for rec in recent:
        for lens, stats in (rec.get("lens_hit_rates") or {}).items():
            if lens not in lens_agg:
                lens_agg[lens] = {"fires": 0, "hits": 0}
            lens_agg[lens]["fires"] += stats["fires"]
            lens_agg[lens]["hits"] += stats["hits"]
    leaderboard = []
    for lens, stats in lens_agg.items():
        if stats["fires"] >= 3:  # min 3 fires to be ranked
            rate = stats["hits"] / stats["fires"]
            leaderboard.append({
                "lens": lens,
                "fires": stats["fires"],
                "hits": stats["hits"],
                "hit_rate": round(rate, 3),
            })
    leaderboard.sort(key=lambda x: -x["hit_rate"])

    avg_recall = (sum(r.get("top12_recall", 0) for r in recent) / max(1, len(recent))) if recent else 0
    avg_precision = (sum(r.get("shout_precision", 0) for r in recent) / max(1, len(recent))) if recent else 0

    return {
        "total_scored": len(memory),
        "recent_draws": recent,
        "lens_leaderboard": leaderboard,
        "avg_top12_recall": round(avg_recall, 3),
        "avg_shout_precision": round(avg_precision, 3),
    }
