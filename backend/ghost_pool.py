"""
🎻🎧🥂 GHOST POOL — DJ's Laws 69, 70, 71, 72 (canonized 28.04.2026)
====================================================================
The cure for Law 67 (Combinatorial Gap). Builds the suspect pool from
the GHOSTS of last d's actual numbers walked through the 5 mirror doors,
gates by mirror-stack depth (≥3 stacked clues = real voice), commits to
≤20 suspects per d with max 4 per P slot, and rotates every 30 tickets
to break tunnel vision.

References /app/memory/swiss_music_notes.md Laws 69-72 (lines 5146-5454).

Public API
──────────
  walk_5_doors(value, lottery)        Law 70 step 1 — Raw/Circle/Flip/Flip-Wrap/Sum-Circle
  ladder_on_fire(last_draw)           Law 70 step 2 — boost active ladder members
  mirror_stack_depth(n, ctx)          Law 69 — count independent Book clues
  build_ghost_pool(...)               Law 70 — full pool seeded from last d
  apply_20_suspect_discipline(pool)   Law 71 — max 4 per P, ≤20 total
  rotate_pool(...)                    Law 72 — keep top-3 + inject 2 fresh
  detect_drunk_cosmos(n, ctx)         Law 69 amp — 3+ mirrors → anchor
  build_ghost_tickets(...)            full 90-ticket batch with rotation
"""
from __future__ import annotations
from datetime import datetime as dt
from typing import Dict, List, Optional, Tuple


# ════════════════════════════════════════════════════════════════════
# RANGE TABLES (Euro / Swiss)
# ════════════════════════════════════════════════════════════════════
RANGES = {
    'euro':  {'max': 50, 'circle': 25, 'n_slots': 5,
              'bands': {1: (1, 25), 2: (2, 35), 3: (5, 43),
                        4: (9, 49), 5: (16, 50)}},
    'swiss': {'max': 42, 'circle': 21, 'n_slots': 6,
              'bands': {1: (1, 18), 2: (3, 25), 3: (8, 30),
                        4: (12, 35), 5: (18, 40), 6: (25, 42)}},
}


def _circle(n: int, lottery: str) -> int:
    cfg = RANGES[lottery]
    return ((n + cfg['circle'] - 1) % cfg['max']) + 1


def _flip(n: int) -> int:
    s = str(n).zfill(2)
    f = int(s[::-1])
    return f if f > 0 else n


def _flip_wrap(n: int, lottery: str) -> int:
    cfg = RANGES[lottery]
    f = _flip(n)
    if f == 0:
        return n
    return f if f <= cfg['max'] else f - cfg['max']


def _sum_circle(a: int, b: int, lottery: str) -> int:
    cfg = RANGES[lottery]
    s = a + b
    while s > cfg['max']:
        s = ((s - 1) % cfg['max']) + 1
    return s


# ════════════════════════════════════════════════════════════════════
# LAW 70 · STEP 1 — WALK THE 5 DOORS
# ════════════════════════════════════════════════════════════════════
def walk_5_doors(value: int, lottery: str = 'euro') -> Dict[str, int]:
    """Return the 5 mirror echoes of `value`. Same-value collapses are
    kept (a value that maps to itself counts as a single door fire).
    """
    cfg = RANGES[lottery]
    if not (1 <= value <= cfg['max']):
        return {}
    return {
        'raw':       value,
        'circle':    _circle(value, lottery),
        'flip':      _flip(value) if 1 <= _flip(value) <= cfg['max'] else value,
        'flip_wrap': _flip_wrap(value, lottery),
        # sum-circle alone needs a partner; we expose self-sum as a stub
        'sum_self':  _sum_circle(value, value, lottery),
    }


def walk_inner_circles(mains: List[int], lottery: str) -> List[int]:
    """Sum-circle bridges WITHIN one draw across all (i,j) pairs."""
    out: List[int] = []
    for i in range(len(mains)):
        for j in range(i + 1, len(mains)):
            out.append(_sum_circle(mains[i], mains[j], lottery))
    return out


# ════════════════════════════════════════════════════════════════════
# LAW 70 · STEP 2 — LADDER-ON-FIRE
# ════════════════════════════════════════════════════════════════════
def _digit_unit(n: int) -> int:
    return n % 10


def ladder_on_fire(last_draw: List[int], lottery: str = 'euro') -> Dict[int, List[int]]:
    """Detect digit-unit ladders with ≥2 members fired in last draw.
    Returns {unit_digit: [remaining_members]} for boosted members.
    """
    cfg = RANGES[lottery]
    units: Dict[int, List[int]] = {}
    for v in last_draw:
        u = _digit_unit(v)
        units.setdefault(u, []).append(v)
    on_fire: Dict[int, List[int]] = {}
    for u, fired in units.items():
        if len(fired) < 2:
            continue
        full = [n for n in range(1, cfg['max'] + 1)
                if _digit_unit(n) == u]
        remaining = [n for n in full if n not in fired]
        on_fire[u] = remaining
    return on_fire


# ════════════════════════════════════════════════════════════════════
# DATE-TARGET ARITHMETIC (Law 70 step 3)
# ════════════════════════════════════════════════════════════════════
def _date_targets(target_date: dt, lottery: str) -> List[int]:
    """Day, day-flip, day-circle, date-sum-wrap candidates."""
    cfg = RANGES[lottery]
    out: set = set()
    if target_date is None:
        return []
    d = target_date.day
    m = target_date.month
    y = target_date.year
    ds = d + m + (y // 100) + (y % 100)
    if 1 <= d <= cfg['max']:
        out.add(d)
    out.add(_circle(d, lottery))
    fw = _flip_wrap(d, lottery) if d >= 10 else d
    if 1 <= fw <= cfg['max']:
        out.add(fw)
    # Date-sum wrap into range
    s = ds
    while s > cfg['max']:
        s = ((s - 1) % cfg['max']) + 1
    out.add(s)
    out.add(_circle(s, lottery))
    if 1 <= m <= cfg['max']:
        out.add(m)
    return [n for n in out if 1 <= n <= cfg['max']]


# ════════════════════════════════════════════════════════════════════
# LAW 69 · MIRROR-STACK DEPTH
# ════════════════════════════════════════════════════════════════════
def mirror_stack_depth(
    n: int,
    last_mains: List[int],
    last_stars: Optional[List[int]] = None,
    inner_circles: Optional[List[int]] = None,
    on_fire_members: Optional[List[int]] = None,
    date_targets: Optional[List[int]] = None,
    extra_lenses: Optional[List[str]] = None,
    lottery: str = 'euro',
) -> Tuple[int, List[str]]:
    """Count INDEPENDENT Book clues firing on candidate n.
    Returns (depth, fired_lens_list). DJ canon: ≥3 = real voice, ≥5 = drunk.
    """
    fired: List[str] = []
    last_mains = list(last_mains or [])
    last_stars = list(last_stars or [])
    inner_circles = list(inner_circles or [])
    on_fire_members = list(on_fire_members or [])
    date_targets = list(date_targets or [])

    # 1. raw self in last d
    if n in last_mains:
        fired.append(f'raw-last-d({n})')

    # 2. circle pair (n's circle is a last-d main) OR last-d main's circle == n
    for v in last_mains:
        if _circle(v, lottery) == n:
            fired.append(f'circle({v}->{n})')
            break

    # 3. flip pair (bidirectional)
    n_flip = _flip(n)
    for v in last_mains:
        f = _flip(v)
        if (f == n and f != v) or (n_flip == v and n_flip != n):
            fired.append(f'flip({v}<->{n})')
            break

    # 4. flip-wrap pair (Law 8) — bidirectional
    n_fw = _flip_wrap(n, lottery)
    for v in last_mains:
        fw = _flip_wrap(v, lottery)
        if (fw == n and fw != v) or (n_fw == v and n_fw != n):
            fired.append(f'flip-wrap({v}<->{n})')
            break

    # 5. sum-circle / inner-circle
    if n in inner_circles:
        fired.append(f'inner-circle({n})')

    # 6. star-shift (last d's stars become mains)
    if n in last_stars:
        fired.append(f'star-shift({n})')

    # 7. date-target overlap
    if n in date_targets:
        fired.append(f'date-target({n})')

    # 8. ladder-on-fire member
    if n in on_fire_members:
        fired.append(f'ladder-on-fire({n})')

    # 9. extra lenses passed in (compass, hunger, snap-back from engines)
    if extra_lenses:
        fired.extend(extra_lenses)

    return len(fired), fired


def detect_drunk_cosmos(depth: int) -> bool:
    """Law 69 amp — 3+ converging mirrors = drunk cosmos chord (anchor)."""
    return depth >= 5


# ════════════════════════════════════════════════════════════════════
# LAW 70 · BUILD GHOST POOL
# ════════════════════════════════════════════════════════════════════
def _fits_band(n: int, slot: int, lottery: str) -> bool:
    cfg = RANGES[lottery]
    if slot not in cfg['bands']:
        return False
    lo, hi = cfg['bands'][slot]
    return lo <= n <= hi


def build_ghost_pool(
    last_mains: List[int],
    last_stars: Optional[List[int]] = None,
    target_date: Optional[dt] = None,
    lottery: str = 'euro',
    extra_lens_map: Optional[Dict[int, List[str]]] = None,
    min_depth: int = 3,
) -> Dict[str, List[Dict]]:
    """Law 70 — generate a per-slot ghost pool from last d's mains.

    Pipeline:
      1. Walk every landed main through 5 doors → candidate set
      2. Add ladder-on-fire members
      3. Add star-shift candidates
      4. Add date-target candidates
      5. Score every candidate by mirror-stack depth (Law 69)
      6. Reject thin echoes (<min_depth lenses)
      7. Assign to each slot whose band the candidate fits

    Output (for caller to apply 20-suspect discipline / rotation):
      {'P1': [{n, depth, lenses, drunk}, ...sorted], 'P2': [...], ...}
    """
    cfg = RANGES[lottery]
    last_mains = sorted(last_mains or [])
    last_stars = sorted(last_stars or [])
    extra_lens_map = extra_lens_map or {}

    # Build candidate universe via doors
    cand: set = set()
    for v in last_mains:
        if not (1 <= v <= cfg['max']):
            continue
        doors = walk_5_doors(v, lottery)
        cand.update(d_val for d_val in doors.values()
                    if 1 <= d_val <= cfg['max'])
    # Inner circles
    inner = walk_inner_circles(last_mains, lottery)
    cand.update(n for n in inner if 1 <= n <= cfg['max'])
    # Stars become mains
    cand.update(s for s in last_stars if 1 <= s <= cfg['max'])
    # Ladder-on-fire
    fire_map = ladder_on_fire(last_mains, lottery)
    fire_members: List[int] = []
    for members in fire_map.values():
        fire_members.extend(members)
        cand.update(members)
    # Date targets
    dtargets = _date_targets(target_date, lottery)
    cand.update(dtargets)

    # Score every candidate
    ranked: List[Dict] = []
    for n in cand:
        depth, fired = mirror_stack_depth(
            n, last_mains, last_stars,
            inner_circles=inner,
            on_fire_members=fire_members,
            date_targets=dtargets,
            extra_lenses=extra_lens_map.get(n),
            lottery=lottery,
        )
        if depth < min_depth:
            continue  # Law 69 thin-echo gate
        ranked.append({
            'n': n,
            'depth': depth,
            'lenses': fired,
            'drunk': detect_drunk_cosmos(depth),
        })
    # Sort: drunk-cosmos first, then by depth, then by n
    ranked.sort(key=lambda e: (-int(e['drunk']), -e['depth'], e['n']))

    # Assign to slots by band
    pool: Dict[str, List[Dict]] = {}
    for slot in range(1, cfg['n_slots'] + 1):
        slot_key = f'P{slot}'
        pool[slot_key] = [
            dict(e) for e in ranked
            if _fits_band(e['n'], slot, lottery)
        ]
    return pool


# ════════════════════════════════════════════════════════════════════
# LAW 71 · 20-SUSPECT DISCIPLINE
# ════════════════════════════════════════════════════════════════════
def apply_20_suspect_discipline(
    pool: Dict[str, List[Dict]],
    per_slot_max: int = 4,
    total_cap: int = 20,
) -> Dict[str, List[Dict]]:
    """Cap per-slot to top-`per_slot_max` and total unique to `total_cap`.
    Drops trailing slots' tail entries to enforce the global cap.
    """
    # First trim each slot to per_slot_max
    capped: Dict[str, List[Dict]] = {
        k: list(v[:per_slot_max]) for k, v in pool.items()
    }
    # Compute unique-value count, trim from lowest-priority slot tails
    def _unique_count(p: Dict[str, List[Dict]]) -> int:
        seen: set = set()
        for entries in p.values():
            for e in entries:
                seen.add(e['n'])
        return len(seen)

    if _unique_count(capped) <= total_cap:
        return capped

    # Walk slots back-to-front popping the WEAKEST entry across slots
    # until total_cap reached.
    while _unique_count(capped) > total_cap:
        # Find weakest tail entry across all slots
        weakest_slot = None
        weakest_idx = -1
        weakest_depth = 9999
        for slot_key, entries in capped.items():
            if len(entries) <= 1:  # always keep at least 1 per slot
                continue
            tail = entries[-1]
            if tail['depth'] < weakest_depth:
                weakest_depth = tail['depth']
                weakest_slot = slot_key
                weakest_idx = len(entries) - 1
        if weakest_slot is None:
            break
        capped[weakest_slot].pop(weakest_idx)
    return capped


# ════════════════════════════════════════════════════════════════════
# LAW 72 · POOL ROTATION
# ════════════════════════════════════════════════════════════════════
def rotate_pool(
    old_pool: Dict[str, List[Dict]],
    full_ranked: List[Dict],
    banned: List[int],
    prior_pools: List[Dict[str, List[Dict]]],
    lottery: str = 'euro',
    keep: int = 3,
    inject: int = 2,
) -> Dict[str, List[Dict]]:
    """Law 72 — for next batch, keep top-`keep` per P from `old_pool`,
    inject `inject` fresh deep voices that have NOT appeared in any
    `prior_pools[-3:]` (3-d look-back). Fresh voices respect slot bands
    and require `depth >= 3` (Law 69 gate already enforced upstream).
    """
    cfg = RANGES[lottery]
    new_pool: Dict[str, List[Dict]] = {}

    # Black-list: every value that appeared as TOP-3 in any prior pool
    # (look-back 3 batches). Tail entries (<top-3) are eligible to refresh.
    blacklist: set = set()
    for prior in prior_pools[-3:]:
        for slot_key, entries in prior.items():
            for e in entries[:keep]:
                blacklist.add(e['n'])

    for slot in range(1, cfg['n_slots'] + 1):
        slot_key = f'P{slot}'
        kept = list(old_pool.get(slot_key, [])[:keep])
        kept_n = {e['n'] for e in kept}
        fresh: List[Dict] = []
        for entry in full_ranked:
            if len(fresh) >= inject:
                break
            n = entry['n']
            if n in kept_n or n in banned:
                continue
            if n in blacklist:
                continue
            if not _fits_band(n, slot, lottery):
                continue
            if entry.get('depth', 0) < 3:
                continue
            fresh.append(dict(entry))
        new_pool[slot_key] = kept + fresh
    return new_pool


# ════════════════════════════════════════════════════════════════════
# 90-TICKET BATCH ASSEMBLY (3 batches × 30 with rotation)
# ════════════════════════════════════════════════════════════════════
def _ranked_universe(
    last_mains: List[int],
    last_stars: List[int],
    target_date: Optional[dt],
    lottery: str,
    extra_lens_map: Optional[Dict[int, List[str]]],
    min_depth: int,
) -> List[Dict]:
    """Flat ranked list (across all slots) for rotation injection."""
    pool = build_ghost_pool(
        last_mains, last_stars, target_date, lottery,
        extra_lens_map=extra_lens_map, min_depth=min_depth,
    )
    seen: set = set()
    flat: List[Dict] = []
    for entries in pool.values():
        for e in entries:
            if e['n'] in seen:
                continue
            seen.add(e['n'])
            flat.append(e)
    flat.sort(key=lambda e: (-e['depth'], e['n']))
    return flat


def _pick_one_ticket(
    pool: Dict[str, List[Dict]],
    lottery: str,
    seed: int,
    banned: List[int],
) -> Optional[List[int]]:
    """Pick one main per slot respecting ascending order + uniqueness.
    `seed` is used as a deterministic rotation index across slot top-4.
    """
    cfg = RANGES[lottery]
    used: set = set()
    picks: List[int] = []
    for slot in range(1, cfg['n_slots'] + 1):
        entries = pool.get(f'P{slot}', [])
        if not entries:
            return None
        chosen = None
        # Try entries in (seed-rotated) order
        for offset in range(len(entries)):
            e = entries[(seed + offset) % len(entries)]
            v = e['n']
            if v in used or v in banned:
                continue
            # Ascending uniqueness
            if picks and v <= picks[-1]:
                continue
            chosen = v
            break
        if chosen is None:
            return None
        picks.append(chosen)
        used.add(chosen)
    return picks


def _enumerate_pool_tickets(
    pool: Dict[str, List[Dict]],
    lottery: str,
    banned: List[int],
    max_tickets: int,
) -> List[Tuple[List[int], int, int]]:
    """Cartesian enumeration over slot top entries, filtered to valid
    ascending unique combos. Returns up to `max_tickets` tickets sorted
    by total depth (desc). Each entry: (mains_sorted, total_depth, drunk_count).
    """
    import itertools
    cfg = RANGES[lottery]
    slot_lists = []
    for slot in range(1, cfg['n_slots'] + 1):
        entries = pool.get(f'P{slot}', [])
        if not entries:
            return []
        slot_lists.append(entries)

    out: List[Tuple[List[int], int, int]] = []
    seen: set = set()
    # Cap product to avoid blow-up: 4^6 = 4096 (Swiss), 4^5=1024 (Euro).
    for combo in itertools.product(*slot_lists):
        values = [e['n'] for e in combo]
        if any(v in banned for v in values):
            continue
        sv = sorted(set(values))
        if len(sv) != cfg['n_slots']:
            continue
        # Ascending check on the original slot order — values[i] should
        # increase strictly with slot index (after sort, values must equal
        # original to enforce slot-band ordering).
        if values != sv:
            continue
        key = tuple(sv)
        if key in seen:
            continue
        seen.add(key)
        depth_sum = sum(e['depth'] for e in combo)
        drunk_count = sum(int(e.get('drunk', False)) for e in combo)
        out.append((sv, depth_sum, drunk_count))
    out.sort(key=lambda x: (-x[1], -x[2]))
    return out[:max_tickets * 3]  # extra headroom for downstream dedup


def build_ghost_tickets(
    last_mains: List[int],
    last_stars: Optional[List[int]] = None,
    target_date: Optional[dt] = None,
    lottery: str = 'euro',
    extra_lens_map: Optional[Dict[int, List[str]]] = None,
    n_total: int = 90,
    batch_size: int = 30,
    banned: Optional[List[int]] = None,
    wildcard_fraction: float = 0.10,
    min_depth: int = 3,
) -> Dict:
    """Generate `n_total` tickets (default 90) using Laws 69-72.
    3 batches × 30 default · rotate pool every 30 tix · 10% wildcard
    (drawn outside the pool). Returns:
      {
        'tickets': [{'mains', 'batch', 'pool_id', 'archetype', 'story',
                     'laws_fired', 'lens_count', 'drunk_anchors', 'is_wildcard'}, ...],
        'pools': [pool_batch_1, pool_batch_2, pool_batch_3],
        'meta': {...},
      }
    """
    banned = list(banned or [])
    last_mains = list(last_mains or [])
    last_stars = list(last_stars or [])
    cfg = RANGES[lottery]

    # Adaptive depth — try strict (≥3), fall back to ≥2 if pool is too
    # thin to fill all slots. The DJ's "5+ stacked = drunk cosmos" stays
    # the GOAL, but ≥2 is acceptable when the historical clue map is sparse
    # (e.g. early-cycle Swiss, no extra lenses passed in).
    effective_depth = min_depth
    universe = _ranked_universe(
        last_mains, last_stars, target_date, lottery,
        extra_lens_map, effective_depth,
    )
    test_pool = build_ghost_pool(
        last_mains, last_stars, target_date, lottery,
        extra_lens_map=extra_lens_map, min_depth=effective_depth,
    )
    if any(len(test_pool.get(f'P{s}', [])) == 0
           for s in range(1, cfg['n_slots'] + 1)) and effective_depth > 2:
        effective_depth = 2
        universe = _ranked_universe(
            last_mains, last_stars, target_date, lottery,
            extra_lens_map, effective_depth,
        )

    # Initial pool (batch 1)
    pool_1 = build_ghost_pool(
        last_mains, last_stars, target_date, lottery,
        extra_lens_map=extra_lens_map, min_depth=effective_depth,
    )
    pool_1 = apply_20_suspect_discipline(pool_1)
    pools: List[Dict[str, List[Dict]]] = [pool_1]

    n_batches = (n_total + batch_size - 1) // batch_size
    for b in range(1, n_batches):
        rotated = rotate_pool(
            pools[-1], universe, banned, pools[-3:], lottery,
        )
        rotated = apply_20_suspect_discipline(rotated)
        pools.append(rotated)

    tickets: List[Dict] = []
    wildcard_quota = max(1, int(n_total * wildcard_fraction))
    wildcard_count = 0

    for b in range(n_batches):
        pool = pools[b]
        n_in_batch = min(batch_size, n_total - len(tickets))
        if n_in_batch <= 0:
            break

        # Enumerate Cartesian tickets from this pool, ranked by depth
        enumerated = _enumerate_pool_tickets(
            pool, lottery, banned, max_tickets=batch_size,
        )
        # Skip tickets already emitted (cross-batch dedupe)
        emitted_keys = {tuple(t['mains']) for t in tickets}

        # Build wildcard list = top universe NOT in this pool
        pool_values = {e['n'] for entries in pool.values() for e in entries}
        wild_list = [e for e in universe if e['n'] not in pool_values]

        added_in_batch = 0
        for mains_sorted, depth_sum, drunk_count in enumerated:
            if added_in_batch >= n_in_batch:
                break
            if tuple(mains_sorted) in emitted_keys:
                continue

            global_idx = len(tickets)
            do_wildcard = (
                wildcard_count < wildcard_quota
                and (global_idx % 10 == 9)
                and wild_list
            )
            if do_wildcard:
                wild_entry = wild_list[wildcard_count % len(wild_list)]
                wild_slot = None
                for slot in range(1, cfg['n_slots'] + 1):
                    if _fits_band(wild_entry['n'], slot, lottery):
                        wild_slot = slot
                        break
                if wild_slot is not None and wild_entry['n'] not in mains_sorted:
                    wild_picks = list(mains_sorted)
                    wild_picks[wild_slot - 1] = wild_entry['n']
                    wild_sorted = sorted(set(wild_picks))
                    if (len(wild_sorted) == cfg['n_slots']
                            and tuple(wild_sorted) not in emitted_keys):
                        wildcard_count += 1
                        tickets.append({
                            'mains': wild_sorted,
                            'batch': b + 1,
                            'pool_id': b + 1,
                            'archetype': f'GhostPool-Wildcard-B{b+1}',
                            'story': (f"Batch {b+1} · cosmos surprise door "
                                      f"({wild_entry['n']} via "
                                      f"{wild_entry['lenses'][0] if wild_entry['lenses'] else 'wildcard'})"),
                            'laws_fired': ['Law70·ghost-pool',
                                           'Law71·20-suspect-wildcard',
                                           'Law72·rotation'],
                            'lens_count': depth_sum + wild_entry.get('depth', 0),
                            'drunk_anchors': drunk_count,
                            'is_wildcard': True,
                        })
                        emitted_keys.add(tuple(wild_sorted))
                        added_in_batch += 1
                        continue

            tickets.append({
                'mains': mains_sorted,
                'batch': b + 1,
                'pool_id': b + 1,
                'archetype': f'GhostPool-B{b+1}',
                'story': (f"Batch {b+1} · ghost-pool of last d "
                          f"(rotation #{b}) · "
                          f"{drunk_count} drunk-cosmos anchor{'s' if drunk_count!=1 else ''}"),
                'laws_fired': ['Law69·mirror-depth',
                               'Law70·ghost-pool',
                               'Law71·20-suspect-discipline',
                               'Law72·pool-rotation'],
                'lens_count': depth_sum,
                'drunk_anchors': drunk_count,
                'is_wildcard': False,
            })
            emitted_keys.add(tuple(mains_sorted))
            added_in_batch += 1

    # Final dedupe (defensive)
    seen_keys: set = set()
    unique: List[Dict] = []
    for t in tickets:
        key = tuple(t['mains'])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append(t)

    return {
        'tickets': unique,
        'pools': pools,
        'meta': {
            'n_total': n_total,
            'n_batches': n_batches,
            'batch_size': batch_size,
            'wildcards_emitted': wildcard_count,
            'wildcard_quota': wildcard_quota,
            'lottery': lottery,
            'last_mains': last_mains,
            'last_stars': last_stars,
            'universe_size': len(universe),
            'effective_min_depth': effective_depth,
        },
    }


# ════════════════════════════════════════════════════════════════════
# DIAGNOSTIC HELPERS
# ════════════════════════════════════════════════════════════════════
def pool_unique_count(pool: Dict[str, List[Dict]]) -> int:
    seen: set = set()
    for entries in pool.values():
        for e in entries:
            seen.add(e['n'])
    return len(seen)


def pool_summary(pool: Dict[str, List[Dict]]) -> Dict:
    return {
        slot_key: [{'n': e['n'], 'depth': e['depth'],
                    'drunk': bool(e.get('drunk'))} for e in entries]
        for slot_key, entries in pool.items()
    }
