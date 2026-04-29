"""
🎻🎧🥂 PRUNER — DJ's RAM-saver (canonized 29.04.2026)
====================================================================
Daily cleanup of old generations. After D+3 (3 days past the target draw),
all tickets with fewer than 2 total hits (mains + stars/lucky) are deleted.
Generations where NO ticket clears the threshold are removed entirely.

This keeps the hit-tracker memory bound to the actual signal:
"only winners survive past 3 days".

Public API
──────────
  prune_swiss_generations(db, days=3, threshold=2)  → cleanup report
  prune_euro_generations(db, days=3, threshold=2)   → cleanup report
  prune_all(db, days=3, threshold=2)                → both modes
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List


def _parse_date(s: str):
    try:
        return datetime.strptime(s, "%d.%m.%Y")
    except Exception:
        return None


async def prune_swiss_generations(
    db, days: int = 3, threshold: int = 2,
) -> Dict:
    """Prune Swiss `generations` collection.

    Swiss `hit_results[i]` shape: `{hit_count, lucky_hit, total_matches}`.
    A ticket is "kept" if `total_matches >= threshold`.

    For generations targeting a draw that happened > `days` ago:
      • Filter `tickets[]` + `hit_results[]` down to keepers
      • If 0 keepers → delete the entire generation document
      • Otherwise → update the doc with the filtered lists
    """
    today = datetime.now()
    cutoff = today - timedelta(days=days)

    deleted = 0
    trimmed = 0
    tickets_removed = 0
    tickets_kept = 0
    untouched = 0
    skipped_pending = 0

    cursor = db.generations.find({}, {
        "_id": 1, "target_date": 1, "tickets": 1,
        "hit_results": 1, "hits_calculated": 1, "best_ticket_hits": 1,
    })
    async for g in cursor:
        td = _parse_date(g.get("target_date") or "")
        if td is None or td > cutoff:
            untouched += 1
            continue

        if not g.get("hits_calculated"):
            # Old doc with no hit calc yet — assume it's pure noise
            # (the scheduled recalc would have fired by now). Delete.
            await db.generations.delete_one({"_id": g["_id"]})
            deleted += 1
            tickets_removed += len(g.get("tickets") or [])
            continue

        hit_results = g.get("hit_results") or []
        tickets = g.get("tickets") or []
        if not hit_results or not tickets:
            await db.generations.delete_one({"_id": g["_id"]})
            deleted += 1
            tickets_removed += len(tickets)
            continue

        # Keep tickets where total_matches >= threshold
        keep_indices: List[int] = []
        for i, hr in enumerate(hit_results):
            total = hr.get(
                "total_matches",
                int(hr.get("hit_count", 0)) + int(bool(hr.get("lucky_hit", False))),
            )
            if total >= threshold:
                keep_indices.append(i)

        if not keep_indices:
            await db.generations.delete_one({"_id": g["_id"]})
            deleted += 1
            tickets_removed += len(tickets)
            continue

        kept_tickets = []
        kept_hits = []
        for i in keep_indices:
            if i < len(tickets):
                kept_tickets.append(tickets[i])
            if i < len(hit_results):
                kept_hits.append(hit_results[i])

        removed_now = len(tickets) - len(kept_tickets)
        if removed_now == 0:
            untouched += 1
            tickets_kept += len(kept_tickets)
            continue

        await db.generations.update_one(
            {"_id": g["_id"]},
            {"$set": {
                "tickets": kept_tickets,
                "hit_results": kept_hits,
                "pruned_at": today.isoformat(),
                "pruned_threshold": threshold,
            }},
        )
        trimmed += 1
        tickets_removed += removed_now
        tickets_kept += len(kept_tickets)

    return {
        "mode": "swiss",
        "cutoff_days": days,
        "threshold": threshold,
        "deleted_generations": deleted,
        "trimmed_generations": trimmed,
        "tickets_removed": tickets_removed,
        "tickets_kept": tickets_kept,
        "untouched_generations": untouched,
        "skipped_still_pending": skipped_pending,
    }


async def prune_euro_generations(
    db, days: int = 3, threshold: int = 2,
) -> Dict:
    """Prune Euro `euromillions_generations` collection.

    Euro `hit_results[i]` shape: `{hit_count, star_hit_count, total_score}`.
    A ticket is "kept" if `(hit_count + star_hit_count) >= threshold`.
    """
    today = datetime.now()
    cutoff = today - timedelta(days=days)

    deleted = 0
    trimmed = 0
    tickets_removed = 0
    tickets_kept = 0
    untouched = 0

    cursor = db.euromillions_generations.find({}, {
        "_id": 1, "target_date": 1, "tickets": 1,
        "hit_results": 1, "hits_calculated": 1, "best_ticket_hits": 1,
    })
    async for g in cursor:
        td = _parse_date(g.get("target_date") or "")
        if td is None or td > cutoff:
            untouched += 1
            continue

        if not g.get("hits_calculated"):
            await db.euromillions_generations.delete_one({"_id": g["_id"]})
            deleted += 1
            tickets_removed += len(g.get("tickets") or [])
            continue

        hit_results = g.get("hit_results") or []
        tickets = g.get("tickets") or []
        if not hit_results or not tickets:
            await db.euromillions_generations.delete_one({"_id": g["_id"]})
            deleted += 1
            tickets_removed += len(tickets)
            continue

        keep_indices: List[int] = []
        for i, hr in enumerate(hit_results):
            total = int(hr.get("hit_count", 0)) + int(hr.get("star_hit_count", 0))
            if total >= threshold:
                keep_indices.append(i)

        if not keep_indices:
            await db.euromillions_generations.delete_one({"_id": g["_id"]})
            deleted += 1
            tickets_removed += len(tickets)
            continue

        kept_tickets = []
        kept_hits = []
        for i in keep_indices:
            if i < len(tickets):
                kept_tickets.append(tickets[i])
            if i < len(hit_results):
                kept_hits.append(hit_results[i])

        removed_now = len(tickets) - len(kept_tickets)
        if removed_now == 0:
            untouched += 1
            tickets_kept += len(kept_tickets)
            continue

        await db.euromillions_generations.update_one(
            {"_id": g["_id"]},
            {"$set": {
                "tickets": kept_tickets,
                "hit_results": kept_hits,
                "pruned_at": today.isoformat(),
                "pruned_threshold": threshold,
            }},
        )
        trimmed += 1
        tickets_removed += removed_now
        tickets_kept += len(kept_tickets)

    return {
        "mode": "euro",
        "cutoff_days": days,
        "threshold": threshold,
        "deleted_generations": deleted,
        "trimmed_generations": trimmed,
        "tickets_removed": tickets_removed,
        "tickets_kept": tickets_kept,
        "untouched_generations": untouched,
    }


async def prune_all(db, days: int = 3, threshold: int = 2) -> Dict:
    swiss = await prune_swiss_generations(db, days=days, threshold=threshold)
    euro = await prune_euro_generations(db, days=days, threshold=threshold)
    return {"swiss": swiss, "euro": euro}
