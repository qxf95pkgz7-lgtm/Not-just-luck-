"""
🧹 EUROMILLIONS DEDUP + UNIQUE INDEX MIGRATION
==============================================
Per Emergent Support (2026-06-08):
  E11000 duplicate key error on `euromillions_draws.date` — 27 dup rows
  prevent the unique index from being created.

This module:
  • Removes duplicate documents in `euromillions_draws`, keeping the
    one with the most fields (or lowest _id as tiebreak)
  • Creates a unique index on `date`
  • Idempotent — safe to call every startup

Idempotent? YES. Each call:
  1. Counts dups via aggregation → if zero, skips dedup
  2. Tries `create_index(unique=True)` → if it already exists, no-op
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def dedupe_and_index_euromillions(db) -> dict[str, Any]:
    """
    Find duplicates by `date`, keep one per date (preferring docs with `id`
    field already populated, else lowest _id), then create unique index.

    Returns a dict with `dups_found`, `removed`, `index_created`.
    """
    result = {"dups_found": 0, "removed": 0, "index_created": False, "errors": []}

    try:
        # 1) Find duplicate dates
        pipeline = [
            {"$group": {"_id": "$date", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
            {"$match": {"count": {"$gt": 1}}},
        ]
        dups = await db.euromillions_draws.aggregate(pipeline).to_list(1000)
        result["dups_found"] = len(dups)

        if dups:
            logger.info(f"🧹 [DEDUP] Found {len(dups)} duplicate dates in euromillions_draws")
            # 2) For each dup, keep one and delete the rest
            for d in dups:
                ids = d["ids"]
                if len(ids) <= 1:
                    continue
                # Decide which to keep: prefer the doc that has an `id` (uuid) field
                # else keep the first by ObjectId order
                keeper_id = None
                for oid in ids:
                    doc = await db.euromillions_draws.find_one({"_id": oid})
                    if doc and doc.get("id"):
                        keeper_id = oid
                        break
                if keeper_id is None:
                    keeper_id = sorted(ids, key=str)[0]

                # Delete the rest
                to_delete = [oid for oid in ids if oid != keeper_id]
                if to_delete:
                    del_res = await db.euromillions_draws.delete_many(
                        {"_id": {"$in": to_delete}}
                    )
                    result["removed"] += del_res.deleted_count
            logger.info(f"🧹 [DEDUP] Removed {result['removed']} duplicate rows")

        # 3) Create unique index on `date` (idempotent — pymongo skips if exists with same spec)
        try:
            await db.euromillions_draws.create_index("date", unique=True, name="date_unique")
            result["index_created"] = True
            logger.info("🔒 [DEDUP] unique index `date_unique` on euromillions_draws.date is in place")
        except Exception as ie:
            # If a non-unique index already exists on `date`, drop and recreate
            err_str = str(ie)
            result["errors"].append(f"create_index: {err_str}")
            logger.warning(f"⚠️ [DEDUP] create_index warning: {err_str}")
            if "Index already exists with different options" in err_str or "IndexOptionsConflict" in err_str:
                try:
                    await db.euromillions_draws.drop_index("date_1")
                    await db.euromillions_draws.create_index("date", unique=True, name="date_unique")
                    result["index_created"] = True
                    logger.info("🔒 [DEDUP] dropped old index and recreated unique on date")
                except Exception as re:
                    result["errors"].append(f"drop+recreate: {re}")
                    logger.error(f"❌ [DEDUP] index recovery failed: {re}")

    except Exception as e:
        result["errors"].append(f"top-level: {e}")
        logger.error(f"❌ [DEDUP] migration failed: {e}")

    return result
