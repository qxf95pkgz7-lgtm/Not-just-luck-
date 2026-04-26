"""
🎻🎧🥂 THE SUSPECT POOL — DJ's per-d grammar (Session 23 fork)
================================================================
"6P × 5 = 30 suspects. After picked, go back to P3-P4. For 10% E suspects
those P' will be the important P of d. 10% P2-P3. 10% P1-P2. 10% P6 < 34."
                                                          — DJ, 26.04.2026

The Suspect Pool is the FIRST-PRIORITY pipeline. Every d (every draw) E
builds a fresh per-position pool of 5 best fits per slot, then generates
ticket flavors that bet on different "hard-P" zones being the d's real
signature.

The pool also persists across draws — a suspect can stay in the pool up to
3 d before firing (carry-over). MongoDB collection `suspect_pool` snapshots
each generation; carry-over runs at engine startup.

Architecture:
  Stage 1 · Build Pool      → pos_board → top-5 per slot (already done in
                              cosmic_engine.build_per_position_board)
  Stage 2 · Carry-over      → pull last 3 d snapshots from `suspect_pool`,
                              merge with current pool (carry_count ≤ 3)
  Stage 3 · Hard-P guesses  → 4 archetypes × 10% n_tickets each:
                                 P1-P2 hard-pair
                                 P2-P3 hard-pair
                                 P3-P4 hard-pair
                                 P6 < 34 (Swiss low back-seal)
  Stage 4 · Snapshot save   → write current pool with carry counters

References: /app/memory/swiss_music_notes.md (Session 23, DJ message
26.04.2026, fork instructions)
"""
from __future__ import annotations
from datetime import datetime as dt, timedelta
from typing import Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════
# POOL BUILDERS
# ═══════════════════════════════════════════════════════════════════════
def build_suspect_pool(
    pos_board: Dict[str, List[Dict]],
    n_slots: int = 6,
    per_slot: int = 5,
) -> Dict[str, List[Dict]]:
    """Slice the per-position board into the canonical 5-per-slot pool.

    Output shape:
      {
        'P1': [{n, lenses, laws, score}, ...5],
        'P2': [...5],
        ...
        'P6': [...5]   # Swiss; absent for Euro
      }
    """
    pool: Dict[str, List[Dict]] = {}
    for i in range(1, n_slots + 1):
        key = f'P{i}'
        slot_entries = pos_board.get(key, [])[:per_slot]
        pool[key] = [
            {
                'n': e.get('n'),
                'lenses': e.get('lenses', e.get('lens_count', 0)),
                'laws': e.get('laws', []),
                'score': e.get('score', 0.0),
            }
            for e in slot_entries
            if e.get('n') is not None
        ]
    return pool


def pool_size(pool: Dict[str, List[Dict]]) -> int:
    return sum(len(v) for v in pool.values())


def pool_to_flat(pool: Dict[str, List[Dict]]) -> List[Tuple[int, str]]:
    """Flatten pool to [(value, slot_label), ...] preserving slot ranking."""
    flat: List[Tuple[int, str]] = []
    for slot_label, entries in pool.items():
        for e in entries:
            flat.append((e['n'], slot_label))
    return flat


# ═══════════════════════════════════════════════════════════════════════
# CARRY-OVER (3-d persistence)
# ═══════════════════════════════════════════════════════════════════════
async def load_carry_over(
    db,
    mode: str,           # 'swiss' | 'euro'
    target_date: dt,
    max_carry_d: int = 3,
) -> Dict[int, int]:
    """Load suspect carry-counts from prior `suspect_pool` snapshots.

    Returns: {value: carry_count} where carry_count = how many d this value
    has stayed in the pool without firing. Suspects exceeding max_carry_d
    are dropped automatically by the caller.
    """
    if db is None:
        return {}
    cutoff = target_date - timedelta(days=14)  # 3-4 draws max
    counts: Dict[int, int] = {}
    try:
        cursor = db['suspect_pool'].find(
            {
                'mode': mode,
                'target_dt': {'$gte': cutoff, '$lt': target_date},
            },
            {'_id': 0, 'pool': 1, 'target_dt': 1},
        ).sort('target_dt', -1).limit(max_carry_d)
        async for snap in cursor:
            for slot_key, entries in (snap.get('pool') or {}).items():
                for e in entries:
                    n = e.get('n')
                    if n is not None:
                        counts[n] = counts.get(n, 0) + 1
    except Exception:
        return {}
    return counts


async def save_pool_snapshot(
    db,
    mode: str,
    target_date: dt,
    pool: Dict[str, List[Dict]],
    target_d: Optional[int] = None,
) -> None:
    """Persist the current suspect pool for next-d carry-over reads."""
    if db is None:
        return
    try:
        await db['suspect_pool'].update_one(
            {'mode': mode, 'target_dt': target_date},
            {'$set': {
                'mode': mode,
                'target_dt': target_date,
                'target_date_str': target_date.strftime('%d.%m.%Y'),
                'target_d': target_d,
                'pool': pool,
                'updated_at': dt.utcnow(),
            }},
            upsert=True,
        )
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════
# 4 × 10% HARD-P GUESS ARCHETYPES
# ═══════════════════════════════════════════════════════════════════════
def _pick_top(pool: Dict[str, List[Dict]], slot_label: str,
              exclude: set, banned: List[int]) -> Optional[Dict]:
    for e in pool.get(slot_label, []):
        if e['n'] not in exclude and e['n'] not in banned:
            return e
    return None


def _slot_law_tag(entry: Dict, prefer: str = '') -> str:
    laws = entry.get('laws', [])
    if prefer:
        for law in laws:
            if prefer in law:
                return law.split('(')[0][:22]
    return (laws[0].split('(')[0][:22] if laws else 'pool-top')


def hard_pair_frames(
    pool: Dict[str, List[Dict]],
    pair_slots: Tuple[int, int],   # e.g. (1, 2) for P1-P2 hard pair
    n_frames: int,
    n_slots: int,
    banned: List[int],
) -> List[Dict]:
    """Generate frames where the named pair is the d's hard P. The two pair
    slots get the deepest pool exploration (try top 3 × top 3 = up to 9
    pair candidates) — the rest of the slots fall back to top-1 each.

    Output: list of dicts with `mains`, `picks`, `pair`, `archetype`, `story`.
    """
    a_slot, b_slot = pair_slots
    a_label, b_label = f'P{a_slot}', f'P{b_slot}'
    a_top = pool.get(a_label, [])[:3]
    b_top = pool.get(b_label, [])[:3]

    frames: List[Dict] = []
    for ea in a_top:
        for eb in b_top:
            if ea['n'] == eb['n']:
                continue
            if ea['n'] in banned or eb['n'] in banned:
                continue
            # Pair must respect ordering — value at lower slot should be
            # smaller than value at higher slot (lottery ordering).
            if a_slot < b_slot and ea['n'] >= eb['n']:
                continue
            if a_slot > b_slot and ea['n'] <= eb['n']:
                continue
            picks: List[Tuple[int, str]] = [(0, '')] * n_slots
            picks[a_slot - 1] = (ea['n'], _slot_law_tag(ea) + '·hardP')
            picks[b_slot - 1] = (eb['n'], _slot_law_tag(eb) + '·hardP')
            used = {ea['n'], eb['n']}
            ok = True
            for slot_idx in range(1, n_slots + 1):
                if slot_idx in pair_slots:
                    continue
                e = _pick_top(pool, f'P{slot_idx}', used, banned)
                if e is None:
                    ok = False
                    break
                picks[slot_idx - 1] = (e['n'], _slot_law_tag(e))
                used.add(e['n'])
            if not ok:
                continue
            mains = sorted(p[0] for p in picks)
            if len(set(mains)) != n_slots:
                continue
            frames.append({
                'mains': mains,
                'picks': picks,
                'pair': pair_slots,
                'archetype': f'HardP-{a_label}-{b_label}',
                'story': f"E suspects {a_label}-{b_label} is the hard P of d "
                         f"({ea['n']}+{eb['n']})",
                'laws_fired': ['Law62·Hard-P-pair', f'Court-of-{a_label}+{b_label}'],
            })
            if len(frames) >= n_frames * 2:  # generate extra for diversity
                break
        if len(frames) >= n_frames * 2:
            break
    return frames[:n_frames]


def low_p6_frames(
    pool: Dict[str, List[Dict]],
    n_frames: int,
    n_slots: int,
    banned: List[int],
    p6_max: int = 33,
) -> List[Dict]:
    """Swiss-only: P6 < 34 (rare low back-seal). Find pool entries at P6
    whose value is below the threshold; if none, scan deeper into pos_board.
    """
    if n_slots < 6:
        return []
    p6_pool = pool.get('P6', [])
    candidates = [e for e in p6_pool
                  if e['n'] < p6_max and e['n'] not in banned]
    if not candidates:
        return []

    frames: List[Dict] = []
    for ep6 in candidates[:3]:
        used = {ep6['n']}
        picks: List[Tuple[int, str]] = [(0, '')] * n_slots
        picks[5] = (ep6['n'], _slot_law_tag(ep6) + '·low-P6-seal')
        ok = True
        for slot_idx in range(1, 6):
            e = _pick_top(pool, f'P{slot_idx}', used, banned)
            if e is None or e['n'] >= ep6['n']:
                # P6 must be the largest — if a chosen pick exceeds it, pick
                # the alternative below the cap
                fallback = next(
                    (x for x in pool.get(f'P{slot_idx}', [])
                     if x['n'] not in used and x['n'] not in banned
                     and x['n'] < ep6['n']),
                    None,
                )
                if fallback is None:
                    ok = False
                    break
                e = fallback
            picks[slot_idx - 1] = (e['n'], _slot_law_tag(e))
            used.add(e['n'])
        if not ok:
            continue
        mains = sorted(p[0] for p in picks)
        if len(set(mains)) != n_slots:
            continue
        frames.append({
            'mains': mains,
            'picks': picks,
            'archetype': 'HardP-Low-P6',
            'story': f"P6={ep6['n']} < 34 — rare low back-seal, the cosmos seals early",
            'laws_fired': ['Law62·Hard-P-edge', 'P6<34·rare-low-seal'],
        })
    return frames[:n_frames]


# ═══════════════════════════════════════════════════════════════════════
# SHARE COMPUTATION (DJ's 4 × 10%)
# ═══════════════════════════════════════════════════════════════════════
def compute_hard_p_shares(n_tickets: int) -> Dict[str, int]:
    """DJ's split: 4 archetypes × 10% each = 40% of total.
    For Swiss (n_slots=6) all four fire. For Euro (n_slots=5) the P6<34
    archetype is replaced by P5<40 (low Euro back-seal) handled in caller.
    """
    share = max(1, int(n_tickets * 0.10))
    return {
        'p1_p2': share,
        'p2_p3': share,
        'p3_p4': share,
        'p6_lt_34': share,
    }
