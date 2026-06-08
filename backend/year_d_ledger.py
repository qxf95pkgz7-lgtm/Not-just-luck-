"""
🗓️ YEAR-D LEDGER — `year_d_ledger.py`
=====================================
Per-weekday-stream ledger for Swiss + Euro draws.

DJ canon (Session 33): Wednesday and Saturday have DIFFERENT vibes.
Their ghost ledgers MUST be separated. Same for Euro Tue / Fri.

Provides:
  • build_ledger(mode) → list of draws sorted chronologically
  • split_by_weekday(draws) → {"Wed": [...], "Sat": [...]} for Swiss / {"Tue":..., "Fri":...} for Euro
  • current_quarter_stream(target_date, weekday, draws) → list of draws in target's quarter, same weekday
  • position_sequence(draws_in_stream, p_index) → e.g., P1 sequence
  • ghost_set(played, max_n) → unplayed numbers
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv("/app/backend/.env")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")

SWISS_MAINS_MAX = 42
EURO_MAINS_MAX = 50

# Quarter starts (Swiss + Euro share the same calendar quarters per DJ canon)
# Per The Book: Swiss Q2 starts 08.04 (transition week 01-04 skipped).
# Euro Q1d1 = 02.01.2026 (no New-Year skip), Euro Q2d1 = 07.04.2026 (03.04 transition skipped).
QUARTER_STARTS_SWISS = {
    1: (1, 8),      # Q1: 08.01 onwards
    2: (4, 8),      # Q2: 08.04 onwards
    3: (7, 8),      # Q3: 08.07 onwards
    4: (10, 8),     # Q4: 08.10 onwards
}
QUARTER_STARTS_EURO = {
    1: (1, 2),      # Q1: 02.01
    2: (4, 7),      # Q2: 07.04
    3: (7, 7),      # Q3: 07.07
    4: (10, 7),     # Q4: 07.10
}

WEEKDAY_NAME = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}


def parse_dt(s: str) -> Optional[datetime]:
    if not s:
        return None
    s = str(s)[:10]
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def quarter_of(dt: datetime, mode: str) -> int:
    """Return 1..4 — the quarter the given date belongs to.
    Per DJ canon: transition weeks (between quarters) belong to the PREVIOUS quarter
    until the canonical Q-start day passes.
    """
    starts = QUARTER_STARTS_SWISS if mode == "swiss" else QUARTER_STARTS_EURO
    m, d = dt.month, dt.day
    if (m, d) >= starts[4]:
        return 4
    if (m, d) >= starts[3]:
        return 3
    if (m, d) >= starts[2]:
        return 2
    if (m, d) >= starts[1]:
        return 1
    # Before Q1 start (e.g., 01.01 to 07.01 Swiss / 01.01 Euro) → previous Q4
    return 4


async def load_draws(mode: str) -> List[Dict]:
    """Load all draws for given mode, sorted ascending by date. Adds 'dt' and 'wd' fields.

    🛡️ Hardened per Emergent Support (Jun 2026):
      (a) CursorNotFound retry: re-issues cursor from last _id processed
      (b) batch_size=100 keeps each round-trip well under 10-min idle timeout
      (c) async-for streaming so a stuck cursor never deadlocks event loop
    """
    from pymongo.errors import CursorNotFound, ExecutionTimeout

    client = AsyncIOMotorClient(
        MONGO_URL,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=30000,
    )
    db = client[DB_NAME]
    try:
        col_name = "draws" if mode == "swiss" else "euromillions_draws"
        coll = db[col_name]

        raw: List[Dict] = []
        last_date: str | None = None
        # Stream up to 20000 docs in batches of 100 with CursorNotFound retry
        for attempt in range(3):
            try:
                query: Dict = {} if last_date is None else {"date": {"$gt": last_date}}
                cursor = coll.find(query, {"_id": 0}).sort("date", 1).batch_size(100)
                async for d in cursor:
                    raw.append(d)
                    last_date = d.get("date") or last_date
                    if len(raw) >= 20000:
                        break
                break  # success — exit retry loop
            except (CursorNotFound, ExecutionTimeout) as cursor_err:
                # Re-issue from last processed point
                continue

        out = []
        for d in raw:
            dt = parse_dt(d.get("date"))
            if not dt or not d.get("numbers"):
                continue
            nums = sorted(d["numbers"])
            out.append({
                "date": d["date"],
                "dt": dt,
                "p": nums,
                "lucky": d.get("lucky_number"),
                "replay": d.get("replay_number"),
                "stars": sorted(d.get("stars") or []) if mode == "euro" else None,
                "wd": WEEKDAY_NAME[dt.weekday()],
                "year": dt.year,
                "quarter": quarter_of(dt, mode),
            })
        out.sort(key=lambda x: x["dt"])
        return out
    finally:
        client.close()


def split_by_weekday(draws: List[Dict], mode: str) -> Dict[str, List[Dict]]:
    """Split into the canonical streams for the given lottery."""
    if mode == "swiss":
        keys = ("Wed", "Sat")
    else:  # euro
        keys = ("Tue", "Fri")
    streams: Dict[str, List[Dict]] = {k: [] for k in keys}
    for d in draws:
        if d["wd"] in streams:
            streams[d["wd"]].append(d)
    return streams


def current_quarter_stream(target_dt: datetime, weekday: str, draws: List[Dict],
                           mode: str) -> List[Dict]:
    """Return draws in target's quarter+year, same weekday, BEFORE target_dt.
    The d-position (1-based) is added on the fly.
    """
    target_q = quarter_of(target_dt, mode)
    target_y = target_dt.year
    same = [
        d for d in draws
        if d["wd"] == weekday and d["quarter"] == target_q and d["year"] == target_y
        and d["dt"] < target_dt
    ]
    same.sort(key=lambda x: x["dt"])
    for i, d in enumerate(same, start=1):
        d["d_position"] = i  # 1-based d-count within (year, quarter, weekday)
    return same


def position_sequence(stream_draws: List[Dict], p_index: int) -> List[int]:
    """Return P{p_index+1} sequence (0=P1, 1=P2, ..., 5=P6 Swiss / 4=P5 Euro)."""
    return [d["p"][p_index] for d in stream_draws if len(d["p"]) > p_index]


def ghost_set(played: List[int], max_n: int) -> List[int]:
    """Numbers in 1..max_n that did NOT appear in played."""
    seen = set(played)
    return [n for n in range(1, max_n + 1) if n not in seen]
