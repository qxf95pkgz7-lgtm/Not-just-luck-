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
      • Snapshot a per-draw **recap** to `draw_recaps` (so the
        random-vs-engine box keeps a stable comparison even after pruning)
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

    # 🎻 Build per-draw recaps BEFORE pruning destroys the per-ticket data
    recap_acc: Dict[str, Dict] = {}

    cursor = db.generations.find({}, {
        "_id": 1, "target_date": 1, "tickets": 1, "generation_type": 1,
        "hit_results": 1, "hits_calculated": 1, "best_ticket_hits": 1,
    })
    async for g in cursor:
        td = _parse_date(g.get("target_date") or "")
        if td is None or td > cutoff:
            untouched += 1
            continue

        target = g.get("target_date")
        gtype = (g.get("generation_type") or "").lower()
        bucket = "money" if "money" in gtype else "jackpot"
        # accumulate recap for this draw
        if g.get("hits_calculated") and g.get("hit_results"):
            r = recap_acc.setdefault(target, {
                "target_date": target,
                "lottery": "swiss",
                "jackpot": _empty_recap(),
                "money": _empty_recap(),
            })
            for hr in g["hit_results"]:
                m = int(hr.get("hit_count", 0))
                L = int(bool(hr.get("lucky_hit", False)))
                tot = int(hr.get("total_matches", m + L))
                _bump_recap(r[bucket], m, L=L, tot=tot, mode="swiss")

        if not g.get("hits_calculated"):
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

    # Persist recaps (one per draw_date, idempotent upsert)
    for target, r in recap_acc.items():
        r["last_pruned_at"] = today.isoformat()
        await db.draw_recaps.update_one(
            {"target_date": target, "lottery": "swiss"},
            {"$set": r},
            upsert=True,
        )

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
        "recaps_written": len(recap_acc),
    }


def _empty_recap() -> Dict:
    return {
        "n": 0,
        "c2_main": 0, "c3_main": 0, "c4_main": 0, "c5_main": 0, "c6_main": 0,
        "c2_total": 0, "c3_total": 0, "c4_total": 0,
        "c1_star": 0, "c2_star": 0, "c_lucky": 0,
    }


def _bump_recap(r: Dict, m: int, L: int = 0, tot: int = 0, s: int = 0,
                mode: str = "swiss") -> None:
    r["n"] += 1
    if m >= 2: r["c2_main"] += 1
    if m >= 3: r["c3_main"] += 1
    if m >= 4: r["c4_main"] += 1
    if m >= 5: r["c5_main"] += 1
    if m >= 6: r["c6_main"] += 1
    if mode == "swiss":
        if tot >= 2: r["c2_total"] += 1
        if tot >= 3: r["c3_total"] += 1
        if tot >= 4: r["c4_total"] += 1
        if L: r["c_lucky"] += 1
    else:  # euro
        if m + s >= 2: r["c2_total"] += 1
        if m + s >= 3: r["c3_total"] += 1
        if m + s >= 4: r["c4_total"] += 1
        if s >= 1: r["c1_star"] += 1
        if s >= 2: r["c2_star"] += 1


async def prune_euro_generations(
    db, days: int = 3, threshold: int = 2,
) -> Dict:
    """Prune Euro `euromillions_generations` collection.

    Euro `hit_results[i]` shape: `{hit_count, star_hit_count, total_score}`.
    A ticket is "kept" if `(hit_count + star_hit_count) >= threshold`.
    Also snapshots a per-draw recap to `draw_recaps`.
    """
    today = datetime.now()
    cutoff = today - timedelta(days=days)

    deleted = 0
    trimmed = 0
    tickets_removed = 0
    tickets_kept = 0
    untouched = 0

    recap_acc: Dict[str, Dict] = {}

    cursor = db.euromillions_generations.find({}, {
        "_id": 1, "target_date": 1, "tickets": 1, "mode": 1,
        "generation_type": 1,
        "hit_results": 1, "hits_calculated": 1, "best_ticket_hits": 1,
    })
    async for g in cursor:
        td = _parse_date(g.get("target_date") or "")
        if td is None or td > cutoff:
            untouched += 1
            continue

        target = g.get("target_date")
        m_field = (g.get("mode") or g.get("generation_type") or "").lower()
        bucket = "money" if "money" in m_field else "jackpot"
        if g.get("hits_calculated") and g.get("hit_results"):
            r = recap_acc.setdefault(target, {
                "target_date": target,
                "lottery": "euro",
                "jackpot": _empty_recap(),
                "money": _empty_recap(),
            })
            for hr in g["hit_results"]:
                m = int(hr.get("hit_count", 0))
                s = int(hr.get("star_hit_count", 0))
                _bump_recap(r[bucket], m, s=s, mode="euro")

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

    for target, r in recap_acc.items():
        r["last_pruned_at"] = today.isoformat()
        await db.draw_recaps.update_one(
            {"target_date": target, "lottery": "euro"},
            {"$set": r},
            upsert=True,
        )

    return {
        "mode": "euro",
        "cutoff_days": days,
        "threshold": threshold,
        "deleted_generations": deleted,
        "trimmed_generations": trimmed,
        "tickets_removed": tickets_removed,
        "tickets_kept": tickets_kept,
        "untouched_generations": untouched,
        "recaps_written": len(recap_acc),
    }


async def prune_all(db, days: int = 3, threshold: int = 2) -> Dict:
    swiss = await prune_swiss_generations(db, days=days, threshold=threshold)
    euro = await prune_euro_generations(db, days=days, threshold=threshold)
    return {"swiss": swiss, "euro": euro}
