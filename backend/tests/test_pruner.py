"""
🎻🎧🥂 PYTEST · PRUNER (Laws-of-RAM, 29.04.2026)
=================================================
Validates the ≥2-hit retention rule and D+3 cutoff.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from pruner import prune_swiss_generations, prune_euro_generations


def _run(coro):
    """Run an async coroutine in tests without pytest-asyncio."""
    return asyncio.get_event_loop().run_until_complete(coro) if asyncio.get_event_loop().is_running() else asyncio.run(coro)


def _mock_collection(docs):
    """Build a mock async collection."""
    state = {"docs": list(docs), "deleted": [], "updated": []}

    class _AsyncIterator:
        def __init__(self, items):
            self.items = list(items)

        def __aiter__(self):
            return self

        async def __anext__(self):
            if not self.items:
                raise StopAsyncIteration
            return self.items.pop(0)

    coll = MagicMock()

    def find(query=None, projection=None):
        return _AsyncIterator(state["docs"])

    async def delete_one(q):
        state["deleted"].append(q.get("_id"))
        return MagicMock()

    async def update_one(q, update):
        state["updated"].append({"_id": q.get("_id"), "set": update.get("$set")})
        return MagicMock()

    coll.find = find
    coll.delete_one = AsyncMock(side_effect=delete_one)
    coll.update_one = AsyncMock(side_effect=update_one)
    coll._state = state
    return coll


def _mock_db(swiss_docs=None, euro_docs=None):
    db = MagicMock()
    db.generations = _mock_collection(swiss_docs or [])
    db.euromillions_generations = _mock_collection(euro_docs or [])
    return db


def _old_date_str(days_ago: int) -> str:
    return (datetime.now() - timedelta(days=days_ago)).strftime("%d.%m.%Y")


class TestSwissPruner:
    def test_keeps_recent_generations_intact(self):
        docs = [{
            "_id": "recent",
            "target_date": _old_date_str(1),
            "tickets": [{"numbers": [1,2,3,4,5,6]}],
            "hits_calculated": True,
            "hit_results": [{"hit_count": 0, "lucky_hit": False, "total_matches": 0}],
        }]
        db = _mock_db(swiss_docs=docs)
        report = asyncio.run(prune_swiss_generations(db, days=3, threshold=2))
        assert report["deleted_generations"] == 0
        assert report["trimmed_generations"] == 0
        assert report["untouched_generations"] == 1

    def test_deletes_old_zero_hit_generations(self):
        docs = [{
            "_id": "old-zero",
            "target_date": _old_date_str(5),
            "tickets": [{"numbers": [1,2,3,4,5,6]}, {"numbers": [7,8,9,10,11,12]}],
            "hits_calculated": True,
            "hit_results": [
                {"hit_count": 0, "lucky_hit": False, "total_matches": 0},
                {"hit_count": 1, "lucky_hit": False, "total_matches": 1},
            ],
        }]
        db = _mock_db(swiss_docs=docs)
        report = asyncio.run(prune_swiss_generations(db, days=3, threshold=2))
        assert report["deleted_generations"] == 1
        assert report["tickets_removed"] == 2

    def test_trims_old_partial_hits(self):
        docs = [{
            "_id": "old-mixed",
            "target_date": _old_date_str(5),
            "tickets": [
                {"numbers": [1,2,3,4,5,6]},
                {"numbers": [10,12,18,21,27,30]},
            ],
            "hits_calculated": True,
            "hit_results": [
                {"hit_count": 0, "lucky_hit": False, "total_matches": 0},
                {"hit_count": 2, "lucky_hit": True, "total_matches": 3},
            ],
        }]
        db = _mock_db(swiss_docs=docs)
        report = asyncio.run(prune_swiss_generations(db, days=3, threshold=2))
        assert report["deleted_generations"] == 0
        assert report["trimmed_generations"] == 1
        assert report["tickets_removed"] == 1
        assert report["tickets_kept"] == 1
        update = db.generations._state["updated"][0]["set"]
        assert len(update["tickets"]) == 1
        assert update["tickets"][0]["numbers"] == [10,12,18,21,27,30]

    def test_threshold_2_includes_lucky_only(self):
        docs = [{
            "_id": "lucky",
            "target_date": _old_date_str(5),
            "tickets": [{"numbers": [1,2,3,4,5,6]}],
            "hits_calculated": True,
            "hit_results": [{"hit_count": 1, "lucky_hit": True, "total_matches": 2}],
        }]
        db = _mock_db(swiss_docs=docs)
        report = asyncio.run(prune_swiss_generations(db, days=3, threshold=2))
        assert report["deleted_generations"] == 0
        assert report["tickets_kept"] == 1

    def test_old_uncalculated_is_purged(self):
        docs = [{
            "_id": "old-stale",
            "target_date": _old_date_str(10),
            "tickets": [{"numbers": [1,2,3,4,5,6]}],
        }]
        db = _mock_db(swiss_docs=docs)
        report = asyncio.run(prune_swiss_generations(db, days=3, threshold=2))
        assert report["deleted_generations"] == 1


class TestEuroPruner:
    def test_keeps_2_main_zero_star(self):
        docs = [{
            "_id": "euro-2m",
            "target_date": _old_date_str(5),
            "tickets": [{"numbers": [1,2,3,4,5], "stars": [1,2]}],
            "hits_calculated": True,
            "hit_results": [{"hit_count": 2, "star_hit_count": 0, "total_score": "2/5 + 0/2"}],
        }]
        db = _mock_db(euro_docs=docs)
        report = asyncio.run(prune_euro_generations(db, days=3, threshold=2))
        assert report["deleted_generations"] == 0
        assert report["tickets_kept"] == 1

    def test_keeps_1m_1s_combined_2(self):
        docs = [{
            "_id": "euro-mixed",
            "target_date": _old_date_str(5),
            "tickets": [{"numbers": [1,2,3,4,5], "stars": [1,2]}],
            "hits_calculated": True,
            "hit_results": [{"hit_count": 1, "star_hit_count": 1, "total_score": "1/5 + 1/2"}],
        }]
        db = _mock_db(euro_docs=docs)
        report = asyncio.run(prune_euro_generations(db, days=3, threshold=2))
        assert report["tickets_kept"] == 1

    def test_drops_1m_0s(self):
        docs = [{
            "_id": "euro-1m",
            "target_date": _old_date_str(5),
            "tickets": [{"numbers": [1,2,3,4,5], "stars": [1,2]}],
            "hits_calculated": True,
            "hit_results": [{"hit_count": 1, "star_hit_count": 0}],
        }]
        db = _mock_db(euro_docs=docs)
        report = asyncio.run(prune_euro_generations(db, days=3, threshold=2))
        assert report["deleted_generations"] == 1


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
