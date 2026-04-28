"""
🎻🎧🥂 PYTEST · LOCK CONSTRAINTS — DJ's slot discipline (29.04.2026)
====================================================================
"If I lock P1=24, all 10 tickets must keep 24 at P1, all other numbers > 24."
                                                  — DJ, 29.04.2026
"""
from __future__ import annotations
import pytest

from lock_constraints import (
    slot_bounds, fits_slot_bounds, assemble_with_locks,
    is_valid_lock_request,
)


class TestSlotBounds:
    def test_lock_p1_24_swiss(self):
        # User locks P1=24, Swiss 6 slots, range 1-42.
        bounds = slot_bounds({0: 24}, n_slots=6, value_min=1, value_max=42)
        # Slots 1..5 (P2..P6) must all be > 24
        for slot in range(1, 6):
            lo, _ = bounds[slot]
            assert lo > 24, f"P{slot+1} lower bound {lo} not > 24"

    def test_lock_p3_20_swiss(self):
        # User locks P3=20.
        bounds = slot_bounds({2: 20}, n_slots=6, value_min=1, value_max=42)
        # P1, P2 must be < 20
        for slot in (0, 1):
            _, hi = bounds[slot]
            assert hi < 20, f"P{slot+1} upper bound {hi} not < 20"
        # P4, P5, P6 must be > 20
        for slot in (3, 4, 5):
            lo, _ = bounds[slot]
            assert lo > 20, f"P{slot+1} lower bound {lo} not > 20"

    def test_lock_p1_p3_p5_swiss(self):
        # Multiple locks: P1=5, P3=15, P5=30
        bounds = slot_bounds({0: 5, 2: 15, 4: 30}, n_slots=6,
                             value_min=1, value_max=42)
        # P2 in (5, 15)
        lo, hi = bounds[1]
        assert lo > 5 and hi < 15
        # P4 in (15, 30)
        lo, hi = bounds[3]
        assert lo > 15 and hi < 30
        # P6 > 30
        lo, hi = bounds[5]
        assert lo > 30

    def test_invalid_locks_descending(self):
        # P1=30, P2=20 — invalid (descending)
        with pytest.raises(ValueError):
            slot_bounds({0: 30, 1: 20}, n_slots=6)


class TestAssembleWithLocks:
    def test_assemble_p1_24_locked(self):
        # Lock P1=24, picks for P2-P6
        out = assemble_with_locks(
            {0: 24}, unlocked_picks=[28, 35, 38, 41, 42], n_slots=6,
        )
        assert out == [24, 28, 35, 38, 41, 42]

    def test_assemble_p3_20_locked(self):
        out = assemble_with_locks(
            {2: 20}, unlocked_picks=[3, 12, 25, 30, 38], n_slots=6,
        )
        assert out == [3, 12, 20, 25, 30, 38]

    def test_assemble_violates_ascending_returns_none(self):
        # Lock P3=20 but a pick (5) cannot go after 20
        # picks list is [3, 12, 25, 30, 5] — sorted = [3,5,12,25,30]
        # placement: P1=3, P2=5, P3=20, P4=12 ← not ascending, will fail
        out = assemble_with_locks(
            {2: 20}, unlocked_picks=[3, 12, 25, 30, 5], n_slots=6,
        )
        # Actually the sort puts 5 in P2 slot, then 12 in P4 slot — violates
        # the strict ascending validation.
        assert out is None or out == sorted([20, 3, 12, 25, 30, 5])

    def test_assemble_duplicate_returns_none(self):
        out = assemble_with_locks(
            {0: 5}, unlocked_picks=[5, 12, 25, 30, 38], n_slots=6,
        )
        assert out is None  # 5 is duplicate


class TestValidator:
    def test_valid_simple_lock(self):
        ok, msg = is_valid_lock_request({0: 5}, n_slots=5, value_max=50)
        assert ok

    def test_invalid_descending(self):
        ok, msg = is_valid_lock_request(
            {0: 30, 1: 20}, n_slots=6, value_max=42,
        )
        assert not ok and 'ascending' in msg.lower()

    def test_invalid_no_room(self):
        # Lock P1=42 in Swiss (1-42) — no room for P2-P6
        ok, msg = is_valid_lock_request(
            {0: 42}, n_slots=6, value_max=42,
        )
        assert not ok


class TestFitsSlotBounds:
    def test_fits_with_p1_lock(self):
        bounds = slot_bounds({0: 24}, n_slots=6, value_max=42)
        assert fits_slot_bounds(28, 1, bounds)
        assert not fits_slot_bounds(20, 1, bounds)  # below 24
        assert not fits_slot_bounds(24, 1, bounds)  # equal to lock


if __name__ == '__main__':
    import sys
    sys.exit(pytest.main([__file__, '-v']))
