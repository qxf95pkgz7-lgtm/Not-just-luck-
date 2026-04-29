"""
🎻🎧🥂 HISTORICAL ARCHIVE — DJ's permanent ticket record (29.04.2026)
=========================================================================
Stores every ticket ever generated for past draws. Source-of-truth survives
the pruner (the pruner only trims the LIVE generations collection — this
archive is the permanent memory).

Schema:
  historical_tickets {
    _id, serial, lottery, target_date, generated_at, mode,
    numbers, stars (Euro) | lucky (Swiss),
    hits: { mains, stars/lucky, total },
    actual_draw: {numbers, stars/lucky},
    has_locked, locked_positions,
  }

Public API
──────────
  archive_completed_draws(db)      → for every draw with hits_calculated,
                                     copy tickets to historical_tickets
  fetch_historical(db, mode, ...)  → paginated read for history UI
  export_csv(db, mode, ...)        → CSV string for download
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional


def _bucket_mode_swiss(gen_type: str) -> str:
    return "money" if "money" in (gen_type or "").lower() else "jackpot"


def _bucket_mode_euro(mode_field: str, gen_type: str) -> str:
    raw = (mode_field or gen_type or "").lower()
    return "money" if "money" in raw else "jackpot"


async def archive_completed_draws(db) -> Dict:
    """Walk the live generations and copy every hit-calculated ticket into
    `historical_tickets` (idempotent — keyed by serial+target_date).
    """
    now = datetime.now()
    archived_swiss = 0
    archived_euro = 0
    skipped = 0

    # --- Swiss
    cursor = db.generations.find(
        {"hits_calculated": True},
        {
            "_id": 0, "target_date": 1, "tickets": 1, "generated_at": 1,
            "generation_type": 1, "hit_results": 1, "has_locked": 1,
            "locked_positions": 1,
        },
    )
    async for g in cursor:
        td = g.get("target_date")
        if not td:
            continue
        actual = await db.draws.find_one(
            {"date": td}, {"_id": 0, "numbers": 1, "lucky_number": 1, "replay": 1}
        )
        bucket = _bucket_mode_swiss(g.get("generation_type"))
        for i, t in enumerate(g.get("tickets") or []):
            sn = t.get("serial")
            if not sn:
                # Mint a deterministic fallback serial so we don't lose the row
                sn = f"CH-{td}-#legacy-{i:04d}"
            hr = (g.get("hit_results") or [None] * (i + 1))[i] if i < len(g.get("hit_results") or []) else None
            doc = {
                "serial": sn,
                "lottery": "swiss",
                "target_date": td,
                "generated_at": g.get("generated_at"),
                "mode": bucket,
                "numbers": t.get("numbers", []),
                "lucky": t.get("lucky") or t.get("lucky_number"),
                "replay": t.get("replay") or t.get("replay_number"),
                "story": t.get("story"),
                "has_locked": bool(g.get("has_locked")),
                "locked_positions": g.get("locked_positions") or {},
                "hits": {
                    "mains": int((hr or {}).get("hit_count", 0)),
                    "lucky_hit": bool((hr or {}).get("lucky_hit", False)),
                    "total": int((hr or {}).get("total_matches", 0)),
                } if hr else None,
                "actual_draw": actual,
                "archived_at": now.isoformat(),
            }
            res = await db.historical_tickets.update_one(
                {"serial": sn, "target_date": td, "lottery": "swiss"},
                {"$set": doc},
                upsert=True,
            )
            if res.upserted_id is not None:
                archived_swiss += 1
            else:
                skipped += 1

    # --- Euro
    cursor = db.euromillions_generations.find(
        {"hits_calculated": True},
        {
            "_id": 0, "target_date": 1, "tickets": 1, "generated_at": 1,
            "mode": 1, "generation_type": 1, "hit_results": 1,
            "has_locked": 1, "locked_positions": 1,
        },
    )
    async for g in cursor:
        td = g.get("target_date")
        if not td:
            continue
        actual = await db.euromillions_draws.find_one(
            {"date": td}, {"_id": 0, "numbers": 1, "stars": 1}
        )
        bucket = _bucket_mode_euro(g.get("mode"), g.get("generation_type"))
        for i, t in enumerate(g.get("tickets") or []):
            sn = t.get("serial")
            if not sn:
                sn = f"EU-{td}-#legacy-{i:04d}"
            hr_list = g.get("hit_results") or []
            hr = hr_list[i] if i < len(hr_list) else None
            doc = {
                "serial": sn,
                "lottery": "euro",
                "target_date": td,
                "generated_at": g.get("generated_at"),
                "mode": bucket,
                "numbers": t.get("numbers", []),
                "stars": t.get("stars", []),
                "story": t.get("story"),
                "has_locked": bool(g.get("has_locked")),
                "locked_positions": g.get("locked_positions") or {},
                "hits": {
                    "mains": int((hr or {}).get("hit_count", 0)),
                    "stars": int((hr or {}).get("star_hit_count", 0)),
                    "total": int((hr or {}).get("hit_count", 0))
                              + int((hr or {}).get("star_hit_count", 0)),
                } if hr else None,
                "actual_draw": actual,
                "archived_at": now.isoformat(),
            }
            res = await db.historical_tickets.update_one(
                {"serial": sn, "target_date": td, "lottery": "euro"},
                {"$set": doc},
                upsert=True,
            )
            if res.upserted_id is not None:
                archived_euro += 1
            else:
                skipped += 1

    return {
        "archived_swiss": archived_swiss,
        "archived_euro": archived_euro,
        "skipped_already_archived": skipped,
        "ran_at": now.isoformat(),
    }


async def fetch_historical(
    db,
    mode: str = "swiss",
    limit: int = 200,
    skip: int = 0,
    target_date: Optional[str] = None,
    min_hits: int = 0,
) -> List[Dict]:
    """Paginated read of the archive."""
    q = {"lottery": mode}
    if target_date:
        q["target_date"] = target_date
    if min_hits > 0:
        q["hits.total"] = {"$gte": min_hits}
    cursor = (
        db.historical_tickets
        .find(q, {"_id": 0})
        .sort([("target_date", -1), ("serial", 1)])
        .skip(skip)
        .limit(limit)
    )
    return [doc async for doc in cursor]


async def fetch_historical_dates(db, mode: str) -> List[Dict]:
    """Aggregate per-target_date: count, max hits, archived_at."""
    pipeline = [
        {"$match": {"lottery": mode}},
        {"$group": {
            "_id": "$target_date",
            "n": {"$sum": 1},
            "max_hits": {"$max": "$hits.total"},
            "n_2plus": {"$sum": {"$cond": [
                {"$gte": ["$hits.total", 2]}, 1, 0,
            ]}},
            "n_3plus": {"$sum": {"$cond": [
                {"$gte": ["$hits.total", 3]}, 1, 0,
            ]}},
        }},
        {"$sort": {"_id": -1}},
    ]
    return [
        {"target_date": d["_id"], "count": d["n"],
         "max_hits": d.get("max_hits", 0),
         "n_2plus": d.get("n_2plus", 0),
         "n_3plus": d.get("n_3plus", 0)}
        async for d in db.historical_tickets.aggregate(pipeline)
    ]


async def export_csv(
    db, mode: str, target_date: Optional[str] = None, min_hits: int = 0,
) -> str:
    """Stream a CSV string of historical tickets."""
    headers = ["serial", "target_date", "mode", "numbers", "extras",
               "actual_numbers", "actual_extras", "mains_hit",
               "extras_hit", "total_hits", "has_locked", "locked_positions"]
    rows = [",".join(headers)]
    docs = await fetch_historical(
        db, mode=mode, limit=100000, skip=0,
        target_date=target_date, min_hits=min_hits,
    )
    for d in docs:
        if mode == "swiss":
            extras = str(d.get("lucky") or "")
            extras_hit = "1" if (d.get("hits") or {}).get("lucky_hit") else "0"
            actual_extras = str((d.get("actual_draw") or {}).get("lucky_number") or "")
        else:
            extras = "|".join(str(x) for x in (d.get("stars") or []))
            extras_hit = str((d.get("hits") or {}).get("stars", 0))
            actual_extras = "|".join(str(x) for x in
                                     (d.get("actual_draw") or {}).get("stars") or [])
        row = [
            str(d.get("serial", "")),
            str(d.get("target_date", "")),
            str(d.get("mode", "")),
            "|".join(str(x) for x in (d.get("numbers") or [])),
            extras,
            "|".join(str(x) for x in (d.get("actual_draw") or {}).get("numbers") or []),
            actual_extras,
            str((d.get("hits") or {}).get("mains", 0)),
            extras_hit,
            str((d.get("hits") or {}).get("total", 0)),
            "1" if d.get("has_locked") else "0",
            ";".join(f"{k}={v}" for k, v in (d.get("locked_positions") or {}).items()),
        ]
        rows.append(",".join(f'"{c}"' if "," in c else c for c in row))
    return "\n".join(rows) + "\n"
