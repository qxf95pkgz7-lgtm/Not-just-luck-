"""
🎻🎧🥂 LOCK CONSTRAINTS — DJ's slot-discipline helper (29.04.2026)
====================================================================
When the user pins P3 = 20, the rest of the ticket must obey:
  P1 < P2 < 20 (locked) < P4 < P5 < P6
Same when locking P1 = 24:
  24 (locked) < P2 < P3 < P4 < P5 < P6  → all picks MUST be > 24

This module gives both engines (Swiss + Euro) a single shared truth
for slot bounds + post-pick assembly.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


def slot_bounds(
    locked: Dict[int, int],
    n_slots: int,
    value_min: int = 1,
    value_max: int = 50,
) -> Dict[int, Tuple[int, int]]:
    """For each unlocked slot index `s` (0-indexed), return the (min, max)
    range a candidate must satisfy so the final ticket stays strictly
    ascending P1<P2<...<Pn while keeping locked values at their slot.

    Locked slots are NOT in the output dict.

    Raises ValueError if locked values themselves violate ascending order.
    """
    # Validate locked positions are strictly ascending by slot
    locked_sorted = sorted(locked.items(), key=lambda kv: kv[0])
    prev_slot = -1
    prev_val = -1
    for s, v in locked_sorted:
        if s <= prev_slot:
            raise ValueError(f"Duplicate locked slot {s}")
        if v <= prev_val:
            raise ValueError(
                f"Locked positions violate ascending order: P{prev_slot+1}={prev_val} "
                f"but P{s+1}={v} (must be strictly greater)"
            )
        prev_slot = s
        prev_val = v

    # Compute per-slot bounds for unlocked slots
    bounds: Dict[int, Tuple[int, int]] = {}
    for slot in range(n_slots):
        if slot in locked:
            continue
        # Lower bound = 1 above the highest locked value at any slot < `slot`
        lo = value_min
        # Plus enough room for unlocked slots that come BEFORE this one
        # (each must take a distinct value lower than this slot's value)
        unlocked_before = sum(
            1 for s in range(slot) if s not in locked
        )
        # Find nearest locked slot LEFT of `slot`
        left_locked_val = None
        for s in range(slot - 1, -1, -1):
            if s in locked:
                left_locked_val = locked[s]
                break
        if left_locked_val is not None:
            # Must be greater than left_locked_val + (unlocked slots between
            # the locked slot and `slot`, since each needs a distinct value)
            unlocked_between = sum(
                1 for s in range(_left_index(locked, slot) + 1, slot)
                if s not in locked
            )
            lo = max(lo, left_locked_val + 1 + unlocked_between)
        else:
            lo = max(lo, value_min + unlocked_before)

        # Upper bound = 1 below nearest locked slot RIGHT of `slot`
        hi = value_max
        right_locked_val = None
        right_locked_idx = None
        for s in range(slot + 1, n_slots):
            if s in locked:
                right_locked_val = locked[s]
                right_locked_idx = s
                break
        unlocked_after = sum(
            1 for s in range(slot + 1, n_slots) if s not in locked
        )
        if right_locked_val is not None:
            unlocked_between_right = sum(
                1 for s in range(slot + 1, right_locked_idx)
                if s not in locked
            )
            hi = min(hi, right_locked_val - 1 - unlocked_between_right)
        else:
            hi = min(hi, value_max - (unlocked_after - (n_slots - 1 - slot)))
            # simpler: leave room for slots AFTER this one
            slots_after = n_slots - 1 - slot
            hi = min(hi, value_max - slots_after)

        bounds[slot] = (lo, hi)
    return bounds


def _left_index(locked: Dict[int, int], slot: int) -> int:
    """Return the index of the nearest locked slot left of `slot`, or -1."""
    left = -1
    for s in locked.keys():
        if s < slot and s > left:
            left = s
    return left


def fits_slot_bounds(
    value: int,
    slot: int,
    bounds: Dict[int, Tuple[int, int]],
) -> bool:
    """True if `value` is allowed at slot `slot` given pre-computed bounds."""
    if slot not in bounds:
        return False
    lo, hi = bounds[slot]
    return lo <= value <= hi


def assemble_with_locks(
    locked: Dict[int, int],
    unlocked_picks: List[int],
    n_slots: int,
) -> Optional[List[int]]:
    """Given locked positions and a list of `unlocked_picks` (unsorted,
    one value per unlocked slot), return the final n_slots-length list
    with locked values at their pinned slots and unlocked values placed
    in ascending order across the remaining slots.

    Returns None if the assembly violates ascending order.
    """
    if len(unlocked_picks) + len(locked) != n_slots:
        return None
    if len(set(unlocked_picks) | set(locked.values())) != n_slots:
        return None  # duplicate value somewhere

    # Place unlocked values into the gaps between locked slots, where each
    # gap must hold values strictly greater than the lower-bound locked
    # value and strictly less than the upper-bound locked value.
    locked_slots = sorted(locked.keys())
    out: List[Optional[int]] = [None] * n_slots
    for s, v in locked.items():
        out[s] = v

    # Compute gaps: list of (start_slot, end_slot_exclusive, lower, upper)
    gaps: List[Tuple[int, int, int, int]] = []
    prev_end = 0
    prev_val = 0  # values must be > 0
    for ls in locked_slots:
        if ls > prev_end:
            gaps.append((prev_end, ls, prev_val, locked[ls]))
        prev_end = ls + 1
        prev_val = locked[ls]
    if prev_end < n_slots:
        gaps.append((prev_end, n_slots, prev_val, 10**6))  # open upper

    # For each gap, take the appropriate count of values from unlocked_picks
    # that fall strictly within (lower, upper), sorted ascending.
    available = sorted(unlocked_picks)
    for start, end, lo, hi in gaps:
        slots_in_gap = end - start
        if slots_in_gap == 0:
            continue
        gap_pool = [v for v in available if lo < v < hi]
        if len(gap_pool) < slots_in_gap:
            return None  # not enough values to fill this gap
        chosen = gap_pool[:slots_in_gap]
        for v in chosen:
            available.remove(v)
        for i, v in enumerate(chosen):
            out[start + i] = v

    if any(o is None for o in out):
        return None

    # Final ascending sanity check
    for i in range(1, n_slots):
        if out[i] <= out[i - 1]:
            return None
    return list(out)


def is_valid_lock_request(
    locked: Dict[int, int],
    n_slots: int,
    value_min: int = 1,
    value_max: int = 50,
) -> Tuple[bool, str]:
    """Validate the lock request before generation. Returns (ok, message)."""
    if not locked:
        return True, "no locks"
    for s, v in locked.items():
        if not (0 <= s < n_slots):
            return False, f"slot index P{s+1} out of range (1..{n_slots})"
        if not (value_min <= v <= value_max):
            return False, f"value {v} out of range [{value_min}, {value_max}]"
    try:
        bounds = slot_bounds(locked, n_slots, value_min, value_max)
    except ValueError as e:
        return False, str(e)
    # Make sure each unlocked slot has at least 1 valid value
    for slot, (lo, hi) in bounds.items():
        used = set(locked.values())
        valid_count = sum(1 for v in range(lo, hi + 1) if v not in used)
        if valid_count < 1:
            return False, (
                f"P{slot+1} has no valid value left "
                f"(bounds [{lo}, {hi}] after locks)"
            )
    return True, "ok"


def gap_slots(
    locked: Dict[int, int],
    n_slots: int,
    value_min: int = 1,
    value_max: int = 50,
) -> List[Tuple[int, int, int, int]]:
    """Decompose unlocked slots into contiguous "gaps" between locks.

    Returns list of (start_slot, end_slot_exclusive, value_lower_excl,
    value_upper_excl). Values picked for slots in [start, end) must be
    strictly within (value_lower_excl, value_upper_excl).
    """
    locked_slots = sorted(locked.keys())
    gaps: List[Tuple[int, int, int, int]] = []
    prev_end = 0
    prev_val = value_min - 1
    for ls in locked_slots:
        if ls > prev_end:
            gaps.append((prev_end, ls, prev_val, locked[ls]))
        prev_end = ls + 1
        prev_val = locked[ls]
    if prev_end < n_slots:
        gaps.append((prev_end, n_slots, prev_val, value_max + 1))
    return gaps


def pick_values_for_gaps(
    locked: Dict[int, int],
    n_slots: int,
    score_fn,
    used: Optional[set] = None,
    value_min: int = 1,
    value_max: int = 50,
    randomize: bool = False,
    rng=None,
) -> Optional[List[int]]:
    """For each gap, pick the required number of distinct values strictly
    within (gap_lower, gap_upper) and not in `used`. `score_fn(v)` returns
    a numeric score (higher = better). Returns flat list (sorted by slot
    index) of picked unlocked values, or None if any gap can't be filled.
    """
    used = set(used or [])
    used.update(locked.values())
    picks_by_slot: Dict[int, int] = {}
    for start, end, lo_excl, hi_excl in gap_slots(
        locked, n_slots, value_min, value_max,
    ):
        slots_in_gap = end - start
        candidates = [
            v for v in range(max(value_min, lo_excl + 1),
                             min(value_max, hi_excl - 1) + 1)
            if v not in used
        ]
        if len(candidates) < slots_in_gap:
            return None
        # Sort candidates by score descending; if randomize, weighted sample
        if randomize and rng is not None:
            scored = [(v, max(0.0001, float(score_fn(v)))) for v in candidates]
            chosen: List[int] = []
            pool = list(scored)
            for _ in range(slots_in_gap):
                if not pool:
                    return None
                total = sum(w for _, w in pool)
                r = rng.random() * total
                cum = 0
                pick = pool[0][0]
                for v, w in pool:
                    cum += w
                    if r <= cum:
                        pick = v
                        break
                chosen.append(pick)
                pool = [(v, w) for v, w in pool if v != pick]
            chosen.sort()
        else:
            scored = sorted(candidates, key=lambda v: -float(score_fn(v)))
            chosen = sorted(scored[:slots_in_gap])
        for i, v in enumerate(chosen):
            picks_by_slot[start + i] = v
            used.add(v)
    return [picks_by_slot[s] for s in sorted(picks_by_slot.keys())]
