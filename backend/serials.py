"""
🎻🎧🥂 SERIAL NUMBERS — DJ's per-ticket tracking (canonized 29.04.2026)
=========================================================================
Format: `<LOTTERY>-<YYYY.MM.DD>-#NNNN`
  Examples:
    EU-2026.05.01-#0347   (Euro for 01.05.2026, the 347th saved ticket for that draw)
    CH-2026.04.29-#0021   (Swiss for 29.04.2026, the 21st saved ticket)

Counter is auto-managed in `ticket_counters` collection — atomic upsert
guarantees uniqueness even under concurrent saves.

Public API
──────────
  reserve_serials(db, lottery, target_date, n)  → ['EU-...-0001', ...]
  attach_serials(db, lottery, target_date, tickets)  → mutates list in-place
"""
from __future__ import annotations
from typing import List


_LOTTERY_PREFIX = {"swiss": "CH", "euro": "EU"}


def _ddmmyyyy_to_iso(dd_mm_yyyy: str) -> str:
    """Convert dd.mm.yyyy → yyyy.mm.dd for sortable serial format."""
    try:
        parts = dd_mm_yyyy.split(".")
        if len(parts) == 3:
            return f"{parts[2]}.{parts[1]}.{parts[0]}"
    except Exception:
        pass
    return dd_mm_yyyy


async def reserve_serials(
    db, lottery: str, target_date: str, n: int,
) -> List[str]:
    """Reserve `n` serial numbers atomically. Returns list of strings."""
    if n <= 0:
        return []
    prefix = _LOTTERY_PREFIX.get(lottery, lottery[:2].upper())
    iso_date = _ddmmyyyy_to_iso(target_date or "0000.00.00")
    counter_id = f"{lottery}:{target_date}"

    # Atomic increment + upsert
    result = await db.ticket_counters.find_one_and_update(
        {"_id": counter_id},
        {"$inc": {"counter": n}},
        upsert=True,
        return_document=True,
    )
    # `result` is None on first insert in some MongoDB versions — fetch
    if result is None:
        result = await db.ticket_counters.find_one({"_id": counter_id})

    end = (result or {}).get("counter", n)
    start = end - n + 1
    return [
        f"{prefix}-{iso_date}-#{i:04d}"
        for i in range(start, end + 1)
    ]


async def attach_serials(
    db, lottery: str, target_date: str, tickets: List[dict],
) -> List[str]:
    """Mutate `tickets` in place, attaching `serial` to each.
    Returns the list of serials attached.
    """
    serials = await reserve_serials(db, lottery, target_date, len(tickets))
    for t, sn in zip(tickets, serials):
        if isinstance(t, dict):
            t["serial"] = sn
    return serials
