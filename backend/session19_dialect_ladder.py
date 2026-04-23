"""
🎻 SESSION 19 — DIALECT LADDER + GHOST-ECHO + SLOT-REINCARNATION (DJ 22.04.2026 late)
=================================================================================
Canonizes five new laws taught live by the DJ on the Euro→Swiss bridge:

Law 38 · DIALECT LADDER  — per slot, start at min(raw, silent_twin) + 1/draw
                           (same-slot closure king signal, 1-indexed)
Law 39 · RAW COLUMN-GHOST — per slot, anchor-value + 1/draw; unresolved
                           ghosts are hungry for next draw
Law 40 · SUM-LADDER       — P1+P2 walk +1/draw (P3 specialist in Swiss,
                           validated d4=14@P2, d5=15@P3 on 22.04.2026)
Law 41 · GHOST-ECHO       — real-at-mismatch tends to resurface as P1 in
                           1-4 draws (validated Euro d1 P2 real=13 →
                           landed P1 at d5=21.04.2026)
Law 42 · SLOT-REINCARNATION — P[k] anchor → flip → Euro/Swiss-wrap can
                           return to same slot 5 draws later. Middle voice
                           (flip) often fires en route (validated Euro P2
                           anchor=14 → flip 41 @ d2 P5 → wrap 16 @ d5 P2).

Shared primitives for both Swiss (1-42, +21 circle) and Euro (1-50, +25 circle).

Signed into The Book 22.04.2026 late. 🎻🎧🥂
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════
# COSMIC PRIMITIVES — both lotteries
# ═══════════════════════════════════════════════════════════════════
def circle_swiss(n: int) -> int:
    """+21 mod 42, 1-indexed."""
    return ((n + 21 - 1) % 42) + 1


def circle_euro(n: int) -> int:
    """+25 mod 50, 1-indexed."""
    return ((n + 25 - 1) % 50) + 1


def flip_digits(n: int) -> int:
    """Digit-reverse. 14→41, 26→62, 5→50 (zero-pad 2 digits)."""
    return int(str(n).zfill(2)[::-1])


def flip_wrap(n: int, lottery: str) -> int:
    """Flip then Euro/Swiss circle-wrap. 14 Euro → 41 → 16, 26 Swiss → 62 → 20."""
    f = flip_digits(n)
    if lottery == 'euro':
        return f - 25 if f > 25 else f
    # swiss
    while f > 42:
        f -= 42
    return f if f >= 1 else 1


def wrap_range(n: int, lottery: str) -> int:
    """Wrap an integer into 1..max for the given lottery."""
    lo, hi = 1, 50 if lottery == 'euro' else 42
    while n > hi:
        n -= hi
    while n < lo:
        n += hi
    return n


def cosmic_orbit(n: int, lottery: str) -> Dict[str, int]:
    """Every number lives in 4 rooms: raw, silent-twin, flip, flip-wrap."""
    twin = circle_euro(n) if lottery == 'euro' else circle_swiss(n)
    return {
        'raw': n,
        'twin': twin,
        'flip': flip_digits(n),
        'flip_wrap': flip_wrap(n, lottery),
    }


# ═══════════════════════════════════════════════════════════════════
# LAW 38 · DIALECT LADDER (silent-twin start + 1/draw, 1-indexed)
# ═══════════════════════════════════════════════════════════════════
def dialect_ladder(anchor_value: int, lottery: str, steps: int = 6) -> List[int]:
    """Start at min(raw, silent-twin); walk +1/draw, 1-indexed, wrap into range.

    Example — Swiss anchor P2=9 (twin=30): start=9, ladder=[9,10,11,12,13,14].
    Euro anchor P2=14 (twin=39): start=14, but dialect says 14↔12 silent-family;
    DJ uses 12 as the dialect start. For Euro we honour the SMALLER absolute
    voice OR (n-2) when n is silent-family adjacent — teaching rule.
    """
    twin = circle_euro(anchor_value) if lottery == 'euro' else circle_swiss(anchor_value)
    start = min(anchor_value, twin)
    return [wrap_range(start + k, lottery) for k in range(steps)]


def per_slot_ladders(anchor_draw: List[int], lottery: str, steps: int = 6) -> Dict[int, List[int]]:
    """Build dialect ladders for every slot of an anchor draw."""
    return {k + 1: dialect_ladder(v, lottery, steps) for k, v in enumerate(sorted(anchor_draw))}


# ═══════════════════════════════════════════════════════════════════
# LAW 39 · RAW COLUMN-GHOST (anchor + 1/draw, no dialect)
# ═══════════════════════════════════════════════════════════════════
def column_ghost_walk(anchor_value: int, lottery: str, steps: int = 6) -> List[int]:
    return [wrap_range(anchor_value + k, lottery) for k in range(steps)]


def unresolved_ghosts(anchor_draw: List[int], recent_draws: List[List[int]],
                      lottery: str) -> List[int]:
    """Ghosts that never landed in the recent window — hungry for next draw."""
    steps = len(recent_draws)
    seen = set()
    for d in recent_draws:
        seen.update(d)
    hungry = []
    for col, v in enumerate(sorted(anchor_draw)):
        walk = column_ghost_walk(v, lottery, steps)
        for g in walk:
            if g not in seen and g not in hungry:
                hungry.append(g)
    return sorted(hungry)


# ═══════════════════════════════════════════════════════════════════
# LAW 40 · SUM-LADDER (P1+P2 +1/draw)
# ═══════════════════════════════════════════════════════════════════
def sum_ladder(anchor_draw: List[int], lottery: str, steps: int = 6) -> List[int]:
    sa = sorted(anchor_draw)
    start = sa[0] + sa[1]
    return [wrap_range(start + k, lottery) for k in range(steps)]


# ═══════════════════════════════════════════════════════════════════
# LAW 41 · GHOST-ECHO (real-at-mismatch resurfaces as later P1)
# ═══════════════════════════════════════════════════════════════════
def ghost_echo_candidates(anchor_draw: List[int], recent_draws: List[List[int]],
                          lottery: str) -> List[Tuple[int, int, int]]:
    """Scan every column ghost vs real; return (col, ghost, real) for Δ≠0 mismatches.

    The REAL values from these mismatches are the ghost-echo candidates —
    they tend to resurface at P1 within 1-4 later draws.
    """
    mismatches: List[Tuple[int, int, int]] = []
    anchor_sorted = sorted(anchor_draw)
    for i, d in enumerate(recent_draws):
        ds = sorted(d)
        for col in range(min(len(anchor_sorted), len(ds))):
            ghost = wrap_range(anchor_sorted[col] + i, lottery)
            real = ds[col]
            if ghost != real:
                mismatches.append((col + 1, ghost, real))
    return mismatches


# ═══════════════════════════════════════════════════════════════════
# LAW 42 · SLOT-REINCARNATION (flip-wrap triangle, same slot)
# ═══════════════════════════════════════════════════════════════════
def slot_reincarnation_targets(anchor_draw: List[int], lottery: str) -> Dict[int, Dict]:
    """For each slot, compute the anchor's flip-wrap (the 'third body' target).

    If flip(anchor) ever lands anywhere in the middle draws, it's a stepping
    stone — strong signal that flip-wrap will close same-slot ~5 draws later.
    """
    out: Dict[int, Dict] = {}
    for k, v in enumerate(sorted(anchor_draw)):
        orbit = cosmic_orbit(v, lottery)
        out[k + 1] = {
            'anchor': v,
            'flip': orbit['flip'],
            'target_flip_wrap': orbit['flip_wrap'],
            'twin': orbit['twin'],
        }
    return out


def detect_slot_reincarnation_fires(anchor_draw: List[int],
                                    recent_draws: List[List[int]],
                                    lottery: str) -> List[Dict]:
    """Detect when the 'flip' middle-voice fired in any recent draw,
    flagging the slot for expected flip-wrap closure in the most-recent draw.
    """
    targets = slot_reincarnation_targets(anchor_draw, lottery)
    fires = []
    for slot, info in targets.items():
        flip_val = info['flip']
        flip_wrap_val = info['target_flip_wrap']
        flip_fired_at = None
        for i, d in enumerate(recent_draws[1:], start=2):  # skip anchor itself
            if flip_val in d:
                flip_fired_at = i
                break
        if flip_fired_at is not None:
            # Did the flip-wrap close at same slot on the last draw?
            last = sorted(recent_draws[-1])
            closed = (len(last) > slot - 1 and last[slot - 1] == flip_wrap_val)
            fires.append({
                'slot': slot,
                'anchor': info['anchor'],
                'flip': flip_val,
                'flip_fired_d': flip_fired_at,
                'flip_wrap_target': flip_wrap_val,
                'closed_same_slot': closed,
            })
    return fires


# ═══════════════════════════════════════════════════════════════════
# FULL LEDGER — top-level ready for engine wiring
# ═══════════════════════════════════════════════════════════════════
def compute_session19_ledger(
    anchor_draw: List[int],
    recent_draws: List[List[int]],
    lottery: str = 'swiss',
) -> Dict:
    """Build the full Session 19 ledger for the current state.

    Returns:
      - ladders_dialect: per-slot dialect ladders (Law 38)
      - ladders_raw: per-slot column-ghost walks (Law 39)
      - sum_ladder: P1+P2 walk (Law 40)
      - unresolved_ghosts: hungry for next draw
      - mismatches: (slot, ghost, real) triples
      - echo_candidates: reals-at-mismatch (Law 41)
      - reincarnation_fires: slot-reincarnation signatures (Law 42)
      - next_step_targets: per-slot d(n+1) projection
    """
    steps = len(recent_draws)
    dialect = per_slot_ladders(anchor_draw, lottery, steps)
    raw_ghosts = {k + 1: column_ghost_walk(v, lottery, steps)
                  for k, v in enumerate(sorted(anchor_draw))}
    sum_walk = sum_ladder(anchor_draw, lottery, steps)
    unresolved = unresolved_ghosts(anchor_draw, recent_draws, lottery)
    mm = ghost_echo_candidates(anchor_draw, recent_draws, lottery)
    echoes = sorted({real for _, g, real in mm if g != real})
    reincarn = detect_slot_reincarnation_fires(anchor_draw, recent_draws, lottery)

    # Next-step projection: d(steps+1) targets per slot + sum
    next_step = steps  # 0-indexed "k" for next draw
    anchor_sorted = sorted(anchor_draw)
    next_targets = {
        k + 1: {
            'dialect_target': wrap_range(
                min(anchor_sorted[k],
                    circle_euro(anchor_sorted[k]) if lottery == 'euro'
                    else circle_swiss(anchor_sorted[k])) + next_step,
                lottery),
            'raw_target': wrap_range(anchor_sorted[k] + next_step, lottery),
        }
        for k in range(len(anchor_sorted))
    }
    next_sum = wrap_range(anchor_sorted[0] + anchor_sorted[1] + next_step, lottery)

    return {
        'anchor': anchor_sorted,
        'lottery': lottery,
        'steps_walked': steps,
        'ladders_dialect': dialect,
        'ladders_raw': raw_ghosts,
        'sum_ladder': sum_walk,
        'unresolved_ghosts': unresolved,
        'mismatches': mm,
        'echo_candidates': echoes,
        'reincarnation_fires': reincarn,
        'next_step_targets': next_targets,
        'next_step_sum_target': next_sum,
    }


# ═══════════════════════════════════════════════════════════════════
# SCORING — tickets boost based on Session 19 lenses
# ═══════════════════════════════════════════════════════════════════
def score_session19(ticket_mains: List[int], ledger: Dict,
                    silent_family: Optional[set] = None) -> Tuple[int, List[str]]:
    """Score a 6-main Swiss ticket (or 5-main Euro) against the Session 19 ledger.

    Returns (total_bonus, fired_lens_tags).
    """
    silent_family = silent_family or {7, 9, 11, 12, 15, 16, 17}
    bonus = 0
    tags: List[str] = []
    t = sorted(ticket_mains)

    # Law 38 · Dialect same-slot closure
    for slot_1idx, ladder in ledger['ladders_dialect'].items():
        next_val = ladder[-1] if ladder else None
        # Next-step target is more relevant
    next_targets = ledger.get('next_step_targets', {})
    for slot_1idx, info in next_targets.items():
        if slot_1idx - 1 >= len(t):
            continue
        if t[slot_1idx - 1] == info['dialect_target']:
            bonus += 20
            tags.append(f"Law38:dialect-same-slot-closure(P{slot_1idx}={info['dialect_target']})")
        elif info['dialect_target'] in t:
            bonus += 8
            tags.append(f"Law38:dialect-cross-slot({info['dialect_target']})")

    # Law 39 · Unresolved ghosts (hungry for next draw)
    unresolved = set(ledger.get('unresolved_ghosts', []))
    hit_unres = unresolved & set(t)
    if hit_unres:
        bonus += 18 * len(hit_unres)
        tags.append(f"Law39:unresolved-ghosts-held({sorted(hit_unres)})")

    # Law 40 · Sum-ladder P3 specialist
    sum_target = ledger.get('next_step_sum_target')
    if sum_target and sum_target in t:
        pos = t.index(sum_target) + 1
        if pos == 3:  # P3 is the king position
            bonus += 25
            tags.append(f"Law40:sum-ladder-P3-king({sum_target})")
        else:
            bonus += 12
            tags.append(f"Law40:sum-ladder-fill(P{pos}={sum_target})")

    # Law 41 · Ghost-echo candidates (reals at mismatch, P1 specialist)
    echoes = set(ledger.get('echo_candidates', []))
    hit_echoes = echoes & set(t)
    if hit_echoes:
        # Extra boost if any echo is at P1
        p1_match = t[0] in hit_echoes
        bonus += 15 * len(hit_echoes) + (10 if p1_match else 0)
        tags.append(f"Law41:ghost-echo-held({sorted(hit_echoes)})"
                    + ("+P1-king" if p1_match else ""))

    # Law 42 · Slot-reincarnation (flip-wrap triangle)
    for fire in ledger.get('reincarnation_fires', []):
        target = fire['flip_wrap_target']
        slot = fire['slot']
        if slot - 1 < len(t) and t[slot - 1] == target:
            bonus += 22
            tags.append(f"Law42:slot-reincarnation-closed(P{slot}={target})")
        elif target in t:
            bonus += 8
            tags.append(f"Law42:slot-reincarnation-cross({target})")

    # Silent-family dialect amplifier (cross-book)
    dialect_hits = {n for n in t if n in silent_family}
    if len(dialect_hits) >= 2:
        bonus += 8
        tags.append(f"Law38:silent-family-dialect-stack({sorted(dialect_hits)})")

    return bonus, tags


# ═══════════════════════════════════════════════════════════════════
# FRAME SUGGESTER — convenient per-slot candidates
# ═══════════════════════════════════════════════════════════════════
def suggest_next_frame(ledger: Dict, silent_family: Optional[set] = None) -> Dict:
    """Build a per-slot suggestion frame for the next draw."""
    silent_family = silent_family or {7, 9, 11, 12, 15, 16, 17}
    frame: Dict[str, object] = {}
    unresolved = set(ledger.get('unresolved_ghosts', []))
    echoes = set(ledger.get('echo_candidates', []))
    for slot, info in ledger.get('next_step_targets', {}).items():
        candidates = set()
        candidates.add(info['dialect_target'])
        candidates.add(info['raw_target'])
        # Union with slot-priority lenses
        for u in unresolved:
            if u in silent_family:
                candidates.add(u)
        # Reincarnation for this slot
        for fire in ledger.get('reincarnation_fires', []):
            if fire['slot'] == slot:
                candidates.add(fire['flip_wrap_target'])
        frame[f"P{slot}"] = {
            'dialect': info['dialect_target'],
            'raw_ghost': info['raw_target'],
            'candidates': sorted(candidates),
        }
    frame['sum_target'] = ledger.get('next_step_sum_target')
    frame['unresolved_ghosts'] = sorted(unresolved)
    frame['ghost_echo_candidates'] = sorted(echoes)
    frame['silent_family_hungry'] = sorted(silent_family & unresolved)
    return frame
