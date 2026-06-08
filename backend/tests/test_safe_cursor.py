"""
Tests for safe_cursor.py — Mongo cursor hardening.

Validates:
  • safe_find returns same docs as plain .to_list()
  • safe_find respects limit
  • safe_find with empty query returns []
"""
import asyncio
import os
import sys

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

sys.path.insert(0, "/app/backend")
load_dotenv("/app/backend/.env")

from safe_cursor import safe_find, safe_find_sorted

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]


def _db():
    return AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)[DB_NAME]


def test_safe_find_matches_plain_to_list():
    async def go():
        db = _db()
        plain = await db.draws.find({}, {"_id": 0}).to_list(100)
        safe = await safe_find(db.draws, limit=100, batch_size=20)
        plain_dates = sorted(d["date"] for d in plain if "date" in d)
        safe_dates = sorted(d["date"] for d in safe if "date" in d)
        assert plain_dates == safe_dates
        assert len(safe) == len(plain)
    asyncio.get_event_loop().run_until_complete(go())


def test_safe_find_sorted_returns_results():
    async def go():
        docs = await safe_find_sorted(_db().draws, "date", -1, limit=5, batch_size=5)
        assert len(docs) == 5
        assert all("date" in d for d in docs)
    asyncio.get_event_loop().run_until_complete(go())


def test_safe_find_empty_query():
    async def go():
        out = await safe_find(_db().draws, {"date": "00.00.0000"}, limit=10)
        assert out == []
    asyncio.get_event_loop().run_until_complete(go())


def test_safe_find_respects_limit():
    async def go():
        out = await safe_find(_db().draws, limit=3, batch_size=2)
        assert len(out) == 3
    asyncio.get_event_loop().run_until_complete(go())
