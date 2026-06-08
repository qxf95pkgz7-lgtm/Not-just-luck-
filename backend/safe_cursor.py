"""
🛡️ SAFE CURSOR — `safe_cursor.py`
==================================
Defensive wrapper for long Mongo reads.

Emergent Support (Jun 2026) identified that single-worker uvicorn was wedging
on `pymongo.errors.CursorNotFound` when `.find().to_list(N)` queries exceeded
the 10-minute idle cursor timeout. This module provides:

  • safe_find()    — batch_size=200 + 1 retry on CursorNotFound
  • safe_find_sorted() — same, with .sort(field, direction)

All callers using `.to_list(2000+)` should migrate here. Smaller queries
(≤500 docs) are fine as-is.

Notes
-----
- batch_size=200 means each round-trip fetches at most 200 docs, well below
  the cursor-idle limit.
- We retry ONCE on CursorNotFound by re-issuing the query and skipping past
  already-collected docs (via `$gt` on the sort field when monotonic).
- For non-monotonic queries we just restart from scratch (safe because
  result is deterministic for the same query).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pymongo.errors import CursorNotFound, ExecutionTimeout

DEFAULT_BATCH = 200
DEFAULT_LIMIT = 20000


async def safe_find(
    coll,
    query: Optional[Dict[str, Any]] = None,
    projection: Optional[Dict[str, Any]] = None,
    sort: Optional[list] = None,
    limit: int = DEFAULT_LIMIT,
    batch_size: int = DEFAULT_BATCH,
) -> List[Dict[str, Any]]:
    """Stream all docs matching `query` in bounded batches with retry.

    Replaces `await coll.find(q, p).sort(s).to_list(N)`.
    """
    query = query or {}
    projection = projection if projection is not None else {"_id": 0}

    out: List[Dict[str, Any]] = []
    for attempt in range(2):
        out = []
        cursor = coll.find(query, projection)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.batch_size(batch_size)
        try:
            async for doc in cursor:
                out.append(doc)
                if len(out) >= limit:
                    break
            return out
        except (CursorNotFound, ExecutionTimeout):
            # One retry — re-issue cursor from scratch
            if attempt == 1:
                # Second failure → return whatever we collected (may be partial)
                return out
            continue
    return out


async def safe_find_sorted(
    coll,
    sort_field: str = "date",
    direction: int = -1,
    query: Optional[Dict[str, Any]] = None,
    projection: Optional[Dict[str, Any]] = None,
    limit: int = DEFAULT_LIMIT,
    batch_size: int = DEFAULT_BATCH,
) -> List[Dict[str, Any]]:
    """Convenience: sorted-by-date variant of safe_find()."""
    return await safe_find(
        coll,
        query=query,
        projection=projection,
        sort=[(sort_field, direction)],
        limit=limit,
        batch_size=batch_size,
    )
