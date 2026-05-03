"""
🎻 SWISS COSMIC ENGINE 🎧 — The DJ's Apprentice (Swiss Lotto Native Build)
=========================================================================
Sibling of /app/backend/cosmic_engine.py (Euro). Same architecture, but
native to Swiss Lotto: 6 mains (1-42), 🍀 Lucky (1-6), R Replay.

Canonical laws baked in:
  · Session 14 — Swiss Cosmic Trinity (+21 circle 100%, seed-return 100%,
    28-mirror 100%), RE-LOCK detector, d-count walking method, 4 family
    clocks, bridge-number law, family-amplification twin-pulse.
  · Session 15 — Silent P1 Compass (5 King Clues + amplifiers via
    /app/backend/silent_p1_compass.py module).
  · Session 16 — Determination piece, welcome-companion reinforcement,
    72 magic flip operator (date-sum), hidden anchor d-walks.

Every lens traces to a specific session in /app/memory/swiss_music_notes.md.
"""
from __future__ import annotations
import os
import itertools
import random
from collections import Counter
from datetime import datetime as dt
from typing import Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorClient

# ═══════════════════════════════════════════════════════════════════
# COSMIC PRIMITIVES (Swiss range 1-42)
# ═══════════════════════════════════════════════════════════════════
SWISS_RANGE = 42
SWISS_CIRCLE = 21       # +21 mod 42
PIVOT_28 = 28           # 28-mirror axis
LUCKY_MAX = 6           # 🍀 range 1-6
FAMILY_RARE_THRESHOLD = 4   # Session 14: 4+ in same decade = rare
HUGE_DRAW = [30, 33, 35, 36, 37, 38]   # 07-02-2026 once-in-history


def circle_swiss(n: int) -> int:
    """+21 mod 42, 1-indexed."""
    return ((n + SWISS_CIRCLE - 1) % SWISS_RANGE) + 1


def mirror28(n: int) -> int:
    """28 - n, wrap into 1..42."""
    r = (PIVOT_28 - n) % SWISS_RANGE
    return r if r else SWISS_RANGE


def flip_wrap_swiss(n: int) -> int:
    """Two-digit flip with Swiss wrap."""
    s = str(n).zfill(2)
    f = int(s[::-1])
    return f if f <= SWISS_RANGE else f - SWISS_RANGE


def decade_swiss(n: int) -> int:
    """Decade family: 0s=1-9, 10s=10-19, 20s=20-29, 30s=30-39, 40s=40-42."""
    if n < 10:
        return 0
    return n // 10


def date_sum(target: dt) -> int:
    """DJ's date-sum: day + month + YYYY split (22+4+20+26=72 for 22.04.2026)."""
    y = target.year
    return target.day + target.month + (y // 100) + (y % 100)


def digit_sum(n: int) -> int:
    return sum(int(c) for c in str(n))


# ═══════════════════════════════════════════════════════════════════
# DATA ACCESS
# ═══════════════════════════════════════════════════════════════════
async def load_swiss_draws(db) -> List[dict]:
    raw = await db.draws.find({}, {"_id": 0}).to_list(length=20000)
    valid = []
    for d in raw:
        try:
            d['_dt'] = dt.strptime(d['date'], '%d.%m.%Y')
            nums = d.get('numbers')
            if nums and len(nums) == 6:
                d['_n'] = sorted(nums)
                d['_l'] = d.get('lucky_number')
                d['_r'] = d.get('replay_number')
                valid.append(d)
        except Exception:
            continue
    valid.sort(key=lambda x: x['_dt'])
    return valid


def find_last_family_rare(draws: List[dict],
                          before_date: dt) -> Optional[Tuple[int, dict]]:
    """Family-rare = 4+ in same decade (Session 14 canon)."""
    for i in range(len(draws) - 1, -1, -1):
        d = draws[i]
        if d['_dt'] >= before_date:
            continue
        counts = Counter(decade_swiss(x) for x in d['_n'])
        max_fam, cnt = counts.most_common(1)[0]
        if cnt >= FAMILY_RARE_THRESHOLD:
            outliers = [x for x in d['_n'] if decade_swiss(x) != max_fam]
            outlier = outliers[0] if outliers else None
            return i, {
                'idx': i, 'date': d['date'], 'dt': d['_dt'],
                'n': d['_n'], 'lucky': d['_l'], 'replay': d['_r'],
                'family': max_fam, 'outlier': outlier,
                'family_count': cnt, 'tier': 'HUGE' if cnt == 6 else
                                             ('BIG' if cnt == 5 else 'SMALL'),
            }
    return None


def find_last_re_lock(draws: List[dict], before_date: dt) -> Optional[dict]:
    """🍀 == R signature (Session 14)."""
    for i in range(len(draws) - 1, -1, -1):
        d = draws[i]
        if d['_dt'] >= before_date:
            continue
        if d['_l'] is not None and d['_l'] == d['_r']:
            return {'idx': i, 'date': d['date'], 'dt': d['_dt'],
                    'n': d['_n'], 'lucky': d['_l'], 'replay': d['_r']}
    return None


# ═══════════════════════════════════════════════════════════════════
# CONVERGENCE BOARD — all Swiss laws fire against every 1-42
# ═══════════════════════════════════════════════════════════════════
def build_swiss_convergence(
    rc0: dict,
    re_lock_anchor: Optional[dict],
    cycle: List[dict],
    target_date: dt,
    target_d: int,
    banned: List[int],
) -> Dict[int, List[str]]:
    """Fire every Swiss law against numbers 1-42. Returns {n: [law tags]}."""
    lenses: Dict[int, List[str]] = {n: [] for n in range(1, SWISS_RANGE + 1)}
    family = rc0['family']
    outlier = rc0.get('outlier')
    rc0_nums = rc0['n']

    played = Counter()
    last_fire: Dict[int, int] = {}
    for i, d in enumerate(cycle, 1):
        for n in d['_n']:
            played[n] += 1
            last_fire[n] = i

    def L(n: int, tag: str):
        if 1 <= n <= SWISS_RANGE and n not in banned:
            lenses[n].append(tag)

    # ── Session 14 Law A — FAMILY HUNGRY (100% cycle rate) ──
    if family == 0:
        fr_lo, fr_hi = 1, 10
    elif family == 4:
        fr_lo, fr_hi = 40, 43
    else:
        fr_lo, fr_hi = family * 10, family * 10 + 10
    fam_set = set(range(fr_lo, fr_hi)) & set(range(1, SWISS_RANGE + 1))
    rc0_in_fam = {x for x in rc0_nums if decade_swiss(x) == family}
    hungry_fam = fam_set - rc0_in_fam
    for n in hungry_fam:
        if played.get(n, 0) == 0:
            L(n, f"HUNGRY-{family}0s-UNFIRED(Session14)")
        else:
            L(n, f"hungry-{family}0s-fired-d{last_fire[n]}")

    # ── Session 14 Law B — SWISS COSMIC TRINITY ──
    # (1) Seed circle+21 discharge — 100% across 14 storms
    for n in rc0_nums:
        c = circle_swiss(n)
        L(c, f"Trinity:seed-circle+21({n})={c}(100%)")
    # (2) Seed 28-mirror — 100% across 14 storms
    for n in rc0_nums:
        m = mirror28(n)
        if 1 <= m <= SWISS_RANGE:
            L(m, f"Trinity:seed-28mirror({n})={m}(100%)")
    # (3) Seed raw return — 100% across 14 storms
    for n in rc0_nums:
        if n not in played:
            L(n, f"Trinity:seed-raw-return({n})-silent(Session14)")
        else:
            L(n, f"seed-fired-d{last_fire[n]}")

    # ── Session 14 — OUTLIER BRIDGE (walks forward across cycle) ──
    if outlier is not None:
        L(outlier, f"bridge-outlier({outlier})-Session14")
        L(circle_swiss(outlier), f"bridge-outlier-circle+21={circle_swiss(outlier)}")
        L(mirror28(outlier), f"bridge-outlier-28mirror={mirror28(outlier)}")

    # ── Session 14 — HUGE TWIN LOCK (structural, always active post-HUGE) ──
    # Silent P1 1-17 = +21 twin of a HUGE main
    HUGE_SET = set(HUGE_DRAW)
    for n in range(1, 18):
        if circle_swiss(n) in HUGE_SET:
            L(n, f"HUGE-twin-lock({n}↔{circle_swiss(n)})")

    # ── Session 14 — d-COUNT WALKING METHOD ──
    # At target_d, fire signs for the d-count value.
    d_raw = target_d % SWISS_RANGE or SWISS_RANGE
    L(d_raw, f"d-count-raw(d={target_d})")
    L(circle_swiss(d_raw), f"d-count-circle+21(d={target_d})")
    # Digit ladder
    for c in str(target_d):
        try:
            di = int(c)
            if 1 <= di <= SWISS_RANGE:
                L(di, f"d-count-digit({target_d}→{di})")
        except Exception:
            pass
    # d-count walk from HUGE P6=38 closes on Swiss-wrap(38+d)
    huge_walk = (38 + target_d)
    while huge_walk > SWISS_RANGE:
        huge_walk -= SWISS_RANGE
    L(huge_walk, f"HUGE-walk-close(38+{target_d}→{huge_walk})(Session14)")

    # ── Session 14 — RE-LOCK PRE-ECHO / AMPLIFIER ──
    if cycle and cycle[-1]['_l'] == cycle[-1]['_r']:
        L(cycle[-1]['_l'], f"BD-RE-LOCK-lucky={cycle[-1]['_l']}")
        L(circle_swiss(cycle[-1]['_l']), f"BD-RE-LOCK-circle-twin")
    if re_lock_anchor is not None:
        days_since = (target_date - re_lock_anchor['dt']).days
        if days_since <= 14:
            for n in re_lock_anchor['n']:
                L(n, f"recent-RE-LOCK-seed({n})-{days_since}d-ago")

    # ── Session 14 — ~90-DRAW RARE DRUM ──
    if 80 <= target_d <= 95:
        for n in fam_set:
            L(n, f"90d-rare-drum-window(d={target_d})")

    # ── Session 14 — FAMILY AMPLIFICATION (twin-pulse 1-3 draws) ──
    if target_d <= 3 and family is not None:
        for n in fam_set:
            if n not in played:
                L(n, f"family-amp-watch-d{target_d}(Session14)")

    # ── Session 15 — SILENT P1 COMPASS ──
    SILENT_FAMILY = {7, 9, 11, 12, 15, 16, 17}
    for v in SILENT_FAMILY:
        depth = (len(cycle) - last_fire.get(v, -999_999)) \
            if v in last_fire else len(cycle) + 50
        # Only flag as deep-silent when we have proper history
        if depth >= 20 or v not in last_fire:
            L(v, f"silent-P1-candidate({v})")
        # Twin-pulse: BD P2 == silent X → next P1
        if cycle and len(cycle[-1]['_n']) >= 2:
            if cycle[-1]['_n'][1] == v:
                L(v, f"silent-twin-pulse(BD P2={v})(Clue-E)")
        # Raw self-echo: silent X raw in BD → may break next
        if cycle and v in cycle[-1]['_n']:
            bonus = "-16-KING" if v == 16 else ""
            L(v, f"silent-raw-self-echo({v}){bonus}(Clue-D)")

    # BD L+R silent-family pre-echo (CLUE B)
    if cycle:
        L_val = cycle[-1]['_l'] or 0
        R_val = cycle[-1]['_r'] or 0
        lr_sum = L_val + R_val
        if lr_sum in SILENT_FAMILY:
            for v in SILENT_FAMILY:
                L(v, f"BD-L+R={lr_sum}-silent-pre-echo(Clue-B)")

    # Silent-pair BD cascade (CLUE C)
    if cycle:
        bd_front = set(cycle[-1]['_n'][:3])
        sp_hits = bd_front & SILENT_FAMILY
        if len(sp_hits) >= 2:
            for v in SILENT_FAMILY:
                L(v, f"BD-silent-pair-cascade({sorted(sp_hits)})(Clue-C)")

    # ── Session 15 — 28-MIRROR COUPLES ──
    MIRROR_28 = [(16, 12), (17, 11), (15, 13), (7, 21), (10, 18), (8, 20)]
    for a, b in MIRROR_28:
        if a not in played:
            L(a, f"28-mirror-couple({a}↔{b})-silent-half")
        if b not in played:
            L(b, f"28-mirror-couple({a}↔{b})-silent-half")

    # ── Session 16 — DETERMINATION PIECE (22.04.2026 specific echoes) ──
    # When we're close to the 4-4 hidden anchor walk
    # 4-4 P6=24 walks: d=3→27, d=5→29. 24 flip=42.
    # Generalize: if cycle holds 4-4 recently, fire anchor signals.
    four_four = next((d for d in cycle[-10:] if d['date'].startswith('04.04.')), None)
    if four_four is None:
        four_four_draws = [d for d in cycle if d['date'].startswith('04.04.')]
        four_four = four_four_draws[-1] if four_four_draws else None
    if four_four is not None:
        anchor_val = four_four['_n'][5]  # P6
        days_to = (target_date - four_four['_dt']).days
        # Find draw index distance
        try:
            anchor_idx = cycle.index(four_four)
            d_since_anchor = target_d - (anchor_idx + 1)
            walk_val = anchor_val + d_since_anchor
            if 1 <= walk_val <= SWISS_RANGE:
                L(walk_val, f"4-4-anchor-walk(d={d_since_anchor}, {anchor_val}+{d_since_anchor})")
            L(flip_wrap_swiss(anchor_val), f"4-4-anchor-flip({anchor_val})")
        except ValueError:
            pass

    # ── Session 16 — 72 MAGIC FLIP OPERATOR ──
    ds = date_sum(target_date)
    if ds == 72:
        # Date-sum 72 is the flip day — boost all flip-wrap relationships
        if cycle:
            for n in cycle[-1]['_n']:
                fw = flip_wrap_swiss(n)
                if fw != n and 1 <= fw <= SWISS_RANGE:
                    L(fw, f"72-flip-operator-day({n}→{fw})")
    else:
        # Regular date-sum: wrap it into range as a weak signal
        wrap = ds
        while wrap > SWISS_RANGE:
            wrap -= SWISS_RANGE
        L(wrap, f"date-sum({ds})wrap={wrap}")

    # ── Session 16 — RUNNING P2 SUM COMPASS ──
    if len(cycle) >= 3:
        p2_sum = sum(d['_n'][1] for d in cycle[-3:])
        while p2_sum > SWISS_RANGE:
            p2_sum -= SWISS_RANGE
        L(p2_sum, f"running-P2-sum-compass(last3)={p2_sum}")

    # ── Date-Mirror-28 (Law 33 partial, weak on Swiss per Session 14) ──
    L(mirror28(target_date.day), f"date-day-mirror28({target_date.day})")
    L(mirror28(target_date.month), f"date-mo-mirror28({target_date.month})")

    # ── Date permutations & digits ──
    dstr = f"{target_date.day:02d}{target_date.month:02d}"
    seen_p = set()
    for a, b in itertools.permutations(dstr, 2):
        v = int(a + b)
        if 1 <= v <= SWISS_RANGE and v not in seen_p:
            seen_p.add(v)
            L(v, f"date-perm({a}{b})")

    # ── Flip-wrap back-door (from last draw) ──
    if cycle:
        for n in cycle[-1]['_n']:
            fw = flip_wrap_swiss(n)
            if fw != n:
                L(fw, f"flipwrap-BD({n}→{fw})")

    # ── Sum-circle (Session 5 Law 9, works on Swiss too) ──
    if cycle:
        last = cycle[-1]['_n']
        sc = circle_swiss(last[0] + last[1])
        L(sc, f"sum-circle(P1+P2={last[0]+last[1]})={sc}")

    # ── Cooled rebound (2-8 gap) ──
    for n, fire in last_fire.items():
        gap = target_d - fire
        if n in hungry_fam or n == outlier:
            if 2 <= gap <= 8:
                L(n, f"cooled-rebound-{gap}d(hungry/outlier)")
        elif 4 <= gap <= 8:
            L(n, f"cooled-rebound-{gap}d")

    # ── Big-gap seed (Session 4 Law 6) ──
    for d in cycle[-3:]:
        n = d['_n']
        for i in range(5):
            g = n[i + 1] - n[i]
            if g >= 15 and 1 <= g <= SWISS_RANGE:
                L(g, f"big-gap-seed({n[i]}→{n[i+1]}=gap{g})")
                L(circle_swiss(g), f"big-gap-circle-release({g})")

    # ── P1 running sum (Session 4) ──
    p1s = [d['_n'][0] for d in cycle]
    for win in [2, 3, 4]:
        if len(p1s) >= win:
            s = sum(p1s[-win:])
            wrap_s = s
            while wrap_s > SWISS_RANGE:
                wrap_s -= SWISS_RANGE
            L(wrap_s, f"P1-running-sum({win})={s}→wrap{wrap_s}")

    # ── P1 snap-back (if last P1 > 20) ──
    if cycle and cycle[-1]['_n'][0] > 20:
        for n in range(1, 8):
            L(n, f"snap-back-sweet(P1>20, 50%)")

    # ── Session 19 · DIALECT LADDER + GHOST-ECHO + SLOT-REINCARNATION ──
    # Anchor = 5 draws back (or as far back as we have, min 2). Walks forward
    # to the target. Injects Law 38/39/40/41/42 signals into the convergence.
    try:
        from session19_dialect_ladder import compute_session19_ledger
        if len(cycle) >= 2:
            window = cycle[-5:] if len(cycle) >= 5 else cycle[:]
            s19_anchor = sorted(window[0]['_n'])
            s19_recent = [sorted(d['_n']) for d in window]
            s19_ledger = compute_session19_ledger(s19_anchor, s19_recent, 'swiss')
            # Law 39: unresolved ghosts are hungry for the next draw
            for n in s19_ledger.get('unresolved_ghosts', []):
                L(n, f"Law39:unresolved-ghost-hungry(Session19)")
            # Law 40: sum-ladder next target (P3 specialist in Swiss)
            st = s19_ledger.get('next_step_sum_target')
            if st is not None:
                L(st, f"Law40:sum-ladder-P3-king(Session19)")
            # Law 41: ghost-echo candidates (P1 specialist)
            for n in s19_ledger.get('echo_candidates', []):
                L(n, f"Law41:ghost-echo-candidate(Session19)")
            # Law 42: slot-reincarnation fires
            for fire in s19_ledger.get('reincarnation_fires', []):
                L(fire['flip_wrap_target'],
                  f"Law42:slot-reincarnation(P{fire['slot']}, flip={fire['flip']})(Session19)")
            # Law 38: dialect per-slot next-step targets
            for slot, info in s19_ledger.get('next_step_targets', {}).items():
                L(info['dialect_target'],
                  f"Law38:dialect-ladder(P{slot} next={info['dialect_target']})(Session19)")
    except Exception:
        pass

    return lenses


# ═══════════════════════════════════════════════════════════════════
# RANKING
# ═══════════════════════════════════════════════════════════════════
def rank_suspects(lenses: Dict[int, List[str]]) -> List[Tuple[int, int, List[str]]]:
    ranked = [(n, len(l), l) for n, l in lenses.items() if l]
    ranked.sort(key=lambda x: -x[1])
    return ranked


def apply_hold_fatigue(
    ranked: List[Tuple[int, int, List[str]]],
    cycle: List[dict],
    last_n_draws: int = 3,
) -> List[Tuple[int, int, List[str]]]:
    """🎼 Law 77 · Hold-Fatigue Compass · Swiss (Session 32 decay update).
    DJ's correction: decay not ban. 2-of-3 × 0.85, 3-of-3 × 0.60."""
    fire_count: Dict[int, int] = {}
    recent = cycle[-last_n_draws:] if len(cycle) >= last_n_draws else cycle
    for d in recent:
        for n in (d.get('_n') or []):
            fire_count[n] = fire_count.get(n, 0) + 1
    new_ranked = []
    for (n, score, lenses) in ranked:
        fc = fire_count.get(n, 0)
        if fc >= 3:
            new_score = max(1, int(score * 0.60))
        elif fc >= 2:
            new_score = max(1, int(score * 0.85))
        else:
            new_score = score
        new_ranked.append((n, new_score, lenses))
    new_ranked.sort(key=lambda x: -x[1])
    return new_ranked


def rank_lucky(cycle: List[dict]) -> List[int]:
    """🍀 ranking: prefer sticky (repeat in cycle) + recent."""
    if not cycle:
        return list(range(1, LUCKY_MAX + 1))
    cnt = Counter(d['_l'] for d in cycle if d['_l'] is not None)
    # Swap-code amplification: if recent 🍀 = 1, 2 amplifies; 3↔4
    ranked = sorted(range(1, LUCKY_MAX + 1),
                    key=lambda l: (-cnt.get(l, 0), l))
    return ranked


def rank_replay(cycle: List[dict]) -> List[int]:
    """Replay ranking: sticky + recent."""
    if not cycle:
        return [1, 2, 3, 4, 5, 6]
    cnt = Counter(d['_r'] for d in cycle if d['_r'] is not None)
    # If BD R=1 streak, prefer 1 then 2 (swap)
    recent = [d['_r'] for d in cycle[-4:] if d['_r'] is not None]
    ranked = sorted(cnt.keys(), key=lambda r: (-cnt[r], r))
    # Ensure 1-10 covered
    for r in range(1, 11):
        if r not in ranked:
            ranked.append(r)
    return ranked[:10]


# ═══════════════════════════════════════════════════════════════════
# TICKET BUILDER
# ═══════════════════════════════════════════════════════════════════
def build_swiss_tickets(
    ranked: List[Tuple[int, int, List[str]]],
    lenses: Dict[int, List[str]],
    lucky_rank: List[int],
    replay_rank: List[int],
    rc0: dict,
    cycle: List[dict],
    hungry_fam: set,
    target_d: int,
    target_date: dt,
    n_tickets: int = 12,
    banned: List[int] = None,
) -> List[Dict]:
    """Build 6-main tickets + 🍀 + R honouring Swiss laws & Session 16 core."""
    banned = banned or []
    played = set()
    for d in cycle:
        played.update(d['_n'])
    rc0_silent = [n for n in rc0['n'] if n not in played]
    unfired_hungry = sorted([h for h in hungry_fam if h not in played])

    top = [n for n, c, _ in ranked if c >= 4 and n not in banned]
    mid = [n for n, c, _ in ranked if c == 3 and n not in banned]
    low = [n for n, c, _ in ranked if c == 2 and n not in banned]
    suspects = top + mid + low

    # Session 16 core lock for 22.04.2026
    SESSION16_CORE = [27, 29, 38, 42]
    SESSION16_ACTIVE = target_date.strftime('%d.%m.%Y') == '22.04.2026'

    tickets = []

    def add(name, mains, lucky=None, replay=None):
        mains = sorted(set(m for m in mains
                           if 1 <= m <= SWISS_RANGE and m not in banned))
        if len(mains) != 6:
            return
        key = tuple(mains)
        for t in tickets:
            if tuple(t['mains']) == key:
                return
        if lucky is None:
            lucky = lucky_rank[len(tickets) % len(lucky_rank)]
        if replay is None:
            replay = replay_rank[len(tickets) % len(replay_rank)]
        lens_sample = []
        for m in mains:
            lens_sample.extend(lenses.get(m, [])[:2])
        tickets.append({
            'archetype': name,
            'mains': mains,
            'lucky': int(lucky),
            'replay': int(replay),
            'lens_sample': lens_sample[:8],
            'lens_count': sum(len(lenses.get(m, [])) for m in mains),
        })

    rank_of = {n: i for i, (n, _, _) in enumerate(ranked)}
    by_lens = lambda xs: sorted(xs, key=lambda x: rank_of.get(x, 9999))

    # 1. Top Swiss-Trinity Spine
    if len(top) >= 6:
        add("Top-Swiss-Trinity", top[:6])
    if len(top) >= 7:
        add("Top-Swiss-Trinity-v2", [top[0]] + top[2:7])

    # 2. Session 16 — DETERMINATION CORE (22.04.2026 only)
    if SESSION16_ACTIVE:
        p1_opts = [12, 15, 17, 9]
        p2_opts = [20, 22, 21, 14]
        for p1 in p1_opts:
            for p2 in p2_opts:
                if p1 < p2 and p2 < min(SESSION16_CORE):
                    add(f"S16-Core-Lock-P1={p1}-P2={p2}",
                        [p1, p2] + SESSION16_CORE)

    # 3. Silent-Compass Break
    SILENT_FAMILY = [7, 9, 11, 12, 15, 16, 17]
    sc_break = [n for n in SILENT_FAMILY if n in top + mid]
    if sc_break:
        for p1 in sc_break[:3]:
            fill = by_lens([n for n in top + mid if n > p1 and n not in sc_break])[:5]
            if len(fill) >= 5:
                add(f"Silent-Compass-Break-P1={p1}", [p1] + fill)

    # 4. HUGE-Twin Lock (P1=silent whose +21 is HUGE member)
    HUGE_TWIN = {9: 30, 12: 33, 15: 36, 16: 37, 17: 38}
    for silent, twin in HUGE_TWIN.items():
        if silent in top + mid and twin in top + mid + low:
            fill = by_lens([n for n in top + mid
                           if n not in {silent, twin}])[:4]
            if len(fill) >= 4:
                add(f"HUGE-Twin-Lock({silent}↔{twin})",
                    [silent, twin] + fill)

    # 5. Family-Hungry Spine
    if len(unfired_hungry) >= 3:
        picks = unfired_hungry[:4] + by_lens([n for n in top
                                              if n not in unfired_hungry])[:2]
        add("Family-Hungry-Spine", picks[:6])

    # 6. RC0 Closing Ceremony (cycle-close)
    if target_d >= 7 and len(rc0_silent) >= 4:
        fill = by_lens([n for n in top if n not in rc0_silent])[:max(0, 6 - len(rc0_silent))]
        add("RC0-Closing-Ceremony", rc0_silent[:6] + fill)

    # 7. Bridge-Number Orchestra (outlier walks)
    outlier = rc0.get('outlier')
    if outlier:
        op = [outlier, circle_swiss(outlier), mirror28(outlier),
              flip_wrap_swiss(outlier)]
        op = [x for x in op if 1 <= x <= SWISS_RANGE and x not in banned]
        op = list(dict.fromkeys(op))
        if len(op) >= 3:
            fill = by_lens([n for n in top + mid if n not in op])[:max(0, 6 - len(op))]
            add("Bridge-Number-Orchestra", op + fill)

    # 8. RE-LOCK Echo (if BD was RE-lock)
    if cycle and cycle[-1]['_l'] == cycle[-1]['_r']:
        re_l = cycle[-1]['_l']
        seed = [re_l, circle_swiss(re_l)] + cycle[-1]['_n'][:4]
        seed = [x for x in seed if 1 <= x <= SWISS_RANGE]
        if len(seed) >= 4:
            fill = by_lens([n for n in top if n not in seed])[:max(0, 6 - len(seed))]
            add(f"RE-LOCK-Echo(🍀{re_l}=R{re_l})", seed + fill)

    # 9. 28-Mirror Couple Magic
    couples = [(16, 12), (17, 11), (15, 13), (7, 21), (10, 18), (8, 20)]
    for a, b in couples:
        if a in top + mid and b in top + mid:
            fill = by_lens([n for n in top if n not in {a, b}])[:4]
            if len(fill) >= 4:
                add(f"28-Mirror-Couple({a}+{b})", [a, b] + fill)
                break

    # 10-N: Symphony mixes (random sample from top+mid)
    rng = random.Random(hash(target_date.strftime('%Y%m%d')))
    pool = [n for n, c, _ in ranked if c >= 2 and n not in banned]
    attempts = 0
    while len(tickets) < n_tickets and len(pool) >= 6 and attempts < 200:
        attempts += 1
        picks = rng.sample(pool, 6)
        # Discipline — must carry ≥1 hungry family member in early d
        if target_d <= 5 and unfired_hungry and \
                not any(h in picks for h in unfired_hungry):
            picks[0] = unfired_hungry[rng.randrange(len(unfired_hungry))]
        add(f"Symphony-Mix-{len(tickets)+1:02d}", picks)

    return tickets[:n_tickets]


# ═══════════════════════════════════════════════════════════════════
# SESSION 23 SWISS POSITION-BAND HELPER (DJ's pool grammar 28.04.2026)
# ═══════════════════════════════════════════════════════════════════
# DJ-canonized bands per slot. Hard min/max + soft rare-zone exceptions.
SWISS_BANDS = {1: (1, 29),  2: (2, 30),  3: (4, 33),
               4: (7, 40),  5: (10, 42), 6: (20, 42)}

# Rare-zone gates — values inside these zones are tagged "rare" and
# capped at the share listed. The pool may surface them but the ticket
# generator only commits them in `share_pct` of the n_tickets pass.
SWISS_RARE_ZONES = {
    'P2_high':  {'slot': 2, 'lo': 30, 'hi': 30, 'share_pct': 0.05},  # P2≥30
    'P3_low':   {'slot': 3, 'lo': 4,  'hi': 4,  'share_pct': 0.05},  # P3=4
    'P4_low':   {'slot': 4, 'lo': 1,  'hi': 6,  'share_pct': 0.05},  # P4<7
    'P6_low':   {'slot': 6, 'lo': 1,  'hi': 19, 'share_pct': 0.02},  # P6<20
}


def _fits_slot(value: int, slot_idx: int) -> bool:
    lo, hi = SWISS_BANDS.get(slot_idx, (1, SWISS_RANGE))
    return lo <= value <= hi


def _is_rare_zone(value: int, slot_idx: int) -> bool:
    """True if (value, slot) lands in a rare-zone gate (DJ's exceptions)."""
    for zone in SWISS_RARE_ZONES.values():
        if zone['slot'] == slot_idx and zone['lo'] <= value <= zone['hi']:
            return True
    return False


def _build_swiss_pos_pool(ranked: List[Tuple[int, int, List[str]]],
                          banned: List[int],
                          per_slot: int = 5,
                          slot_history_rates: Optional[Dict[int, Dict[int, float]]] = None) -> Dict[str, List[Dict]]:
    """Build a 6×5 Swiss suspect pool from `ranked` filtered by slot band.

    When `slot_history_rates` is provided, candidates are scored as
    (lens_count × 1.0) + (slot_rate% × 0.4) so each slot prefers its
    natural zone (P1 → low values, P6 → high values) instead of every
    slot grabbing the same top-lens picks.
    """
    pool: Dict[str, List[Dict]] = {}
    for slot_idx in range(1, 7):
        slot_label = f'P{slot_idx}'
        candidates = []
        for n, c, l in ranked:
            if n in banned:
                continue
            if c < 1:
                continue
            if not _fits_slot(n, slot_idx):
                continue
            slot_rate = 0.0
            if slot_history_rates and slot_idx in slot_history_rates:
                slot_rate = slot_history_rates[slot_idx].get(n, 0.0)
            # DJ's grammar: walk every value in band, score by Book clues
            # AT THAT SLOT. Slot-fit (historical landing rate %) leads the
            # score so each slot's pool reflects its native zone. Lens
            # count is secondary — voices must EARN the slot.
            score = slot_rate * 2.0 + float(c) * 0.5
            candidates.append({
                'n': n, 'lenses': c, 'laws': l,
                'slot': slot_label,
                'slot_rate': round(slot_rate, 2),
                'score': round(score, 2),
            })
        candidates.sort(key=lambda e: (e['score'], e['lenses']), reverse=True)
        pool[slot_label] = candidates[:per_slot]
    return pool


def compute_swiss_slot_history_rates(draws: List[Dict]) -> Dict[int, Dict[int, float]]:
    """For each (slot 1-6, value 1-42), return the historical % of draws
    in which that value landed at that slot.

    Used to weight the pool — P1 prefers 1-8, P6 prefers 35-42, etc.
    """
    counts = {i: {n: 0 for n in range(1, SWISS_RANGE + 1)} for i in range(1, 7)}
    total = 0
    for d in draws:
        mains = sorted(d.get('_n', d.get('numbers', [])))
        if len(mains) < 6:
            continue
        for i, v in enumerate(mains[:6], 1):
            counts[i][v] += 1
        total += 1
    if total == 0:
        return {}
    rates = {i: {n: counts[i][n] / total * 100 for n in counts[i]}
             for i in counts}
    return rates


def build_session23_swiss_tickets(
    ranked: List[Tuple[int, int, List[str]]],
    lenses: Dict[int, List[str]],
    lucky_rank: List[int],
    replay_rank: List[int],
    rc0: dict,
    cycle: List[dict],
    target_date: dt,
    target_d: int,
    n_tickets: int = 10,
    banned: Optional[List[int]] = None,
    recent_draws: Optional[List[dict]] = None,
    slot_history_rates: Optional[Dict[int, Dict[int, float]]] = None,
) -> Tuple[List[Dict], Dict[str, List[Dict]], List[int]]:
    """Generate Session 23 Swiss story tickets.

    Returns (tickets, final_pool, final_banned). Final pool & banned reflect
    Slide-Reset auto-bans so the caller can persist the post-ban pool.
    """
    banned = banned or []
    tickets: List[Dict] = []
    seen: set = set()
    pool = _build_swiss_pos_pool(ranked, banned, per_slot=5,
                                 slot_history_rates=slot_history_rates)
    # Use recent_draws if provided (cross-cycle court reading); fallback
    # to in-cycle draws.
    history = recent_draws if recent_draws else cycle

    rng_lucky = lucky_rank[:] or [1, 2, 3, 4, 5, 6]
    rng_replay = replay_rank[:] or [1, 2, 3, 12, 21, 33]

    def _commit(name: str, mains: List[int], story: str,
                laws: List[str]) -> bool:
        mains_sorted = sorted(set(mains))
        if len(mains_sorted) != 6:
            return False
        if any(not (1 <= m <= SWISS_RANGE) for m in mains_sorted):
            return False
        if any(m in banned for m in mains_sorted):
            return False
        key = tuple(mains_sorted)
        if key in seen:
            return False
        seen.add(key)
        tickets.append({
            'archetype': name,
            'mains': mains_sorted,
            'lucky': int(rng_lucky[len(tickets) % len(rng_lucky)]),
            'replay': int(rng_replay[len(tickets) % len(rng_replay)]),
            'story': story,
            'laws_fired': laws,
            'lens_sample': sum(([str(l)[:18] for l in lenses.get(m, [])[:1]]
                                for m in mains_sorted), []),
            'lens_count': sum(len(lenses.get(m, [])) for m in mains_sorted),
        })
        return True

    def _fill_other_slots(pinned: Dict[int, int]) -> Optional[List[int]]:
        used = set(pinned.values())
        result: Dict[int, int] = dict(pinned)
        # Law 65 — when P5 is pinned, filter P6 candidates by gap-band first.
        # When P6 is pinned, filter P5 candidates by reverse gap-band.
        try:
            from session23_p5p6_gap import p6_fits_p5
        except Exception:
            p6_fits_p5 = None
        for slot_idx in range(1, 7):
            if slot_idx in result:
                continue
            for entry in pool.get(f'P{slot_idx}', []):
                v = entry['n']
                if v in used:
                    continue
                ok = True
                for s2, v2 in result.items():
                    if s2 < slot_idx and v <= v2:
                        ok = False; break
                    if s2 > slot_idx and v >= v2:
                        ok = False; break
                if ok and p6_fits_p5 is not None:
                    # Law 65 gap-band check
                    if slot_idx == 6 and 5 in result:
                        if not p6_fits_p5(result[5], v):
                            ok = False
                    elif slot_idx == 5 and 6 in result:
                        if not p6_fits_p5(v, result[6]):
                            ok = False
                if ok:
                    result[slot_idx] = v
                    used.add(v)
                    break
            if slot_idx not in result:
                return None
        return sorted(result.values())

    # ── 1 · COURT-HARD-P-ANCHOR ──
    try:
        from session23_court_reader import find_hard_p, SWISS_SLOT_BANDS
        hp = find_hard_p(history, bands=SWISS_SLOT_BANDS, n_slots=6)
    except Exception:
        hp = None
    if hp and hp.get('predicted_value'):
        v = hp['predicted_value']
        s = hp['slot']
        if 1 <= v <= SWISS_RANGE and v not in banned and _fits_slot(v, s):
            mains = _fill_other_slots({s: v})
            if mains:
                _commit('Court-Hard-P-Anchor',
                        mains,
                        f"Hard P{s}={v} ({hp['flavor']}) — court speaks loudest",
                        [f'Law62·hard-P', f"Law63·court-{hp['flavor']}"])

    # ── 2 · LAW 64 SLIDE-RESET ──
    try:
        from session23_slide_reset import detect_slide_in_cycle
        slide = detect_slide_in_cycle(history)
    except Exception:
        slide = None
    if slide:
        v_slide = slide['slide_value']
        # Auto-ban the slide value across ALL Session 23 archetypes (86%
        # vanish probability — DJ's Sneaky Universe at slot-shift level).
        if v_slide not in banned:
            banned = list(banned) + [v_slide]
        # Rebuild pool with the new ban so subsequent archetypes filter V.
        pool = _build_swiss_pos_pool(ranked, banned, per_slot=5,
                                     slot_history_rates=slot_history_rates)
        clone = list(slide['frame']['best_clone'])
        clone_set = set(clone) | {v_slide}
        for entry in pool.get('P3', []):
            if entry['n'] not in clone_set and 14 <= entry['n'] <= 26:
                clone[2] = entry['n']
                break
        clone = [c for c in clone if c != v_slide]
        if len(clone) == 6:
            _commit('Law64-Slide-Reset',
                    clone,
                    f"V={v_slide} slid P2→P1 across {slide['bd_date']}→{slide['nd_date']} "
                    f"— AF reset: P1≤6, P2 9-17, V banned, 30s back-stretch",
                    ['Law64·slide-reset', f'V={v_slide}-banned-86%',
                     'Sneaky-Universe·slot-shift'])

    # ── 3 · HARD-P PAIR GUESSES ──
    for (a, b) in [(1, 2), (2, 3), (3, 4)]:
        a_top = pool.get(f'P{a}', [])[:3]
        b_top = pool.get(f'P{b}', [])[:3]
        added = False
        for ea in a_top:
            if added:
                break
            for eb in b_top:
                if ea['n'] >= eb['n']:
                    continue
                mains = _fill_other_slots({a: ea['n'], b: eb['n']})
                if mains and _commit(
                        f'HardP-Pair-P{a}P{b}',
                        mains,
                        f"E suspects P{a}-P{b} is the hard P of d "
                        f"({ea['n']}·{eb['n']})",
                        [f'Law62·hard-P-pair', f"Court-of-P{a}+P{b}"]):
                    added = True
                    break

    # ── 4 · LOW P6 SEAL (P6 < 20 — only ≤2% of tickets per DJ) ──
    p6_low = [e for e in pool.get('P6', [])
              if e['n'] < 20 and e['n'] not in banned]
    # share gate: only 1 ticket max if n_tickets≥10, else skip
    if n_tickets >= 10 and p6_low:
        ep6 = p6_low[0]
        mains = _fill_other_slots({6: ep6['n']})
        if mains:
            _commit('HardP-Low-P6',
                    mains,
                    f"P6={ep6['n']} < 20 — ultra-rare low back-seal (≤2% historical)",
                    ['Law62·hard-P-edge', 'P6<20·rare-low-seal'])

    # ── 5 · LAW 65 · P5-P6 KING-PAIR (the gap-collapse signature) ──
    try:
        from session23_p5p6_gap import P5_P6_KING_PAIRS, expected_p6_band
        for p5_v, p6_v in P5_P6_KING_PAIRS[:6]:
            if p5_v in banned or p6_v in banned:
                continue
            mains = _fill_other_slots({5: p5_v, 6: p6_v})
            if mains and _commit(
                    f'Law65-KingPair-{p5_v}-{p6_v}',
                    mains,
                    f"P5={p5_v}+P6={p6_v} king pair (gap={p6_v-p5_v}, top-12 historical)",
                    ['Law65·P5-P6-gap-collapse', 'King-pair-historical-top12']):
                break  # only one king-pair ticket per d
    except Exception:
        pass

    return tickets[:n_tickets], pool, banned


# ═══════════════════════════════════════════════════════════════════
# DJ VOICE
# ═══════════════════════════════════════════════════════════════════
def dj_speak_swiss(rc0: dict, re_lock_anchor: Optional[dict],
                   target_date: dt, target_d: int,
                   ranked: List, tickets: List,
                   hungry_fam: set, rc0_silent: List[int]) -> str:
    lines = []
    lines.append(
        f"🎻🎧 Ya man! Swiss engine tuned for "
        f"{target_date.strftime('%d-%m-%Y')} = d{target_d} from "
        f"{rc0['tier']} rare {rc0['date']} (family {rc0['family']}0s).\n"
    )
    if rc0.get('outlier'):
        lines.append(f"Family {rc0['family']}0s · outlier {rc0['outlier']} · "
                     f"hungry {sorted(hungry_fam)}")
    if rc0_silent:
        lines.append(f"🔴 RC0 rare-silent: {rc0_silent}")
    if re_lock_anchor:
        days = (target_date - re_lock_anchor['dt']).days
        lines.append(f"🔁 Last RE-LOCK: {re_lock_anchor['date']} "
                     f"🍀{re_lock_anchor['lucky']}=R{re_lock_anchor['replay']} "
                     f"({days}d ago)")
    top = [n for n, c, _ in ranked if c >= 4]
    mid = [n for n, c, _ in ranked if c == 3]
    lines.append(f"\n🏆 TOP resonators ({len(top)}): {sorted(top)}")
    lines.append(f"🎺 MID resonators ({len(mid)}): {sorted(mid)}")
    # d-count compass hint
    huge_walk = (38 + target_d)
    while huge_walk > SWISS_RANGE:
        huge_walk -= SWISS_RANGE
    lines.append(f"\n🧭 d-count walk from HUGE P6=38: closes at "
                 f"{huge_walk} (Session 14)")
    if date_sum(target_date) == 72:
        lines.append(f"🔥 Date-sum = 72 — magic flip operator day (Session 16)")
    lines.append("\n🎫 THE ENGINE'S TICKETS:")
    for i, t in enumerate(tickets, 1):
        m = "-".join(f"{x:02d}" for x in t['mains'])
        lines.append(f"  {i:>2}. [{t['archetype']:<34}] {m}  "
                     f"🍀{t['lucky']} R:{t['replay']:02d}  "
                     f"(lens={t['lens_count']})")
    lines.append(f"\n🥂 {len(tickets)} Swiss tickets built. Music tuned 🎻🎧")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════
async def run_swiss_cosmic_engine(
    target_date_str: str,
    n_tickets: int = 12,
    banned: Optional[List[int]] = None,
    db=None,
) -> Dict:
    banned = banned or []
    owns_client = False
    if db is None:
        client = AsyncIOMotorClient(os.environ['MONGO_URL'])
        db = client[os.environ['DB_NAME']]
        owns_client = True
    try:
        draws = await load_swiss_draws(db)
        target_date = dt.strptime(target_date_str, '%d.%m.%Y')

        found = find_last_family_rare(draws, target_date)
        if not found:
            return {'error': 'no family-rare anchor found'}
        _, rc0 = found

        re_lock_anchor = find_last_re_lock(draws, target_date)

        cycle = [d for d in draws if rc0['dt'] < d['_dt'] < target_date]
        target_d = len(cycle) + 1

        lenses = build_swiss_convergence(
            rc0, re_lock_anchor, cycle, target_date, target_d, banned
        )
        ranked = rank_suspects(lenses)
        # 🎼 Law 77 · Hold-Fatigue Compass — Swiss
        ranked = apply_hold_fatigue(ranked, cycle, last_n_draws=3)
        lucky_rank = rank_lucky(cycle)
        replay_rank = rank_replay(cycle)

        # Hungry
        family = rc0['family']
        if family == 0:
            fr_lo, fr_hi = 1, 10
        elif family == 4:
            fr_lo, fr_hi = 40, 43
        else:
            fr_lo, fr_hi = family * 10, family * 10 + 10
        fam_set = set(range(fr_lo, fr_hi)) & set(range(1, SWISS_RANGE + 1))
        rc0_in_fam = {x for x in rc0['n'] if decade_swiss(x) == family}
        hungry = fam_set - rc0_in_fam

        played = set()
        for d in cycle:
            played.update(d['_n'])
        rc0_silent = [n for n in rc0['n'] if n not in played]

        tickets = build_swiss_tickets(
            ranked, lenses, lucky_rank, replay_rank,
            rc0, cycle, hungry, target_d, target_date, n_tickets, banned
        )

        # Session 23 — Court-Hard-P + Slide-Reset + 4 hard-P guesses.
        # Pass the LAST 6 draws regardless of rc0 boundary (slides + courts
        # often span cycles). Slot-history rates weight the per-slot pool.
        recent = draws[-6:] if len(draws) >= 6 else draws
        slot_rates = compute_swiss_slot_history_rates(draws)
        story_tickets, _swiss_pool, _post_ban = build_session23_swiss_tickets(
            ranked, lenses, lucky_rank, replay_rank,
            rc0, cycle, target_date, target_d,
            n_tickets=10, banned=banned,
            recent_draws=recent,
            slot_history_rates=slot_rates,
        )

        # Session 23 — persist suspect pool for next-d carry-over
        try:
            from suspect_pool import save_pool_snapshot
            await save_pool_snapshot(db, 'swiss', target_date,
                                     _swiss_pool, target_d=target_d)
        except Exception:
            pass

        # 🎻 SESSION 25 — GHOST POOL TICKETS (Laws 69-72) for Swiss
        ghost_tickets: List[Dict] = []
        ghost_meta: Dict = {}
        try:
            from ghost_pool import build_ghost_tickets
            # Source last-draw from the full draws array (Swiss family-rare
            # anchors can be sparse, so cycle may be empty even when many
            # recent draws exist).
            last_d = None
            for d in reversed(draws):
                if d['_dt'] < target_date:
                    last_d = d
                    break
            if last_d is not None:
                extra_lens_map: Dict[int, List[str]] = {}
                for n_, c_, l_ in ranked[:30]:
                    if l_:
                        extra_lens_map[n_] = [str(x)[:24] for x in l_[:3]]
                gp_out = build_ghost_tickets(
                    last_mains=last_d['_n'],
                    last_stars=[],  # Swiss has 🍀+R, not stars
                    target_date=target_date,
                    lottery='swiss',
                    extra_lens_map=extra_lens_map,
                    n_total=90,
                    batch_size=30,
                    banned=banned,
                    wildcard_fraction=0.10,
                    min_depth=3,
                )
                rng_lucky = lucky_rank[:] or [1, 2, 3, 4, 5, 6]
                rng_replay = replay_rank[:] or [1, 2, 3, 12, 21, 33]
                for i, t in enumerate(gp_out['tickets']):
                    t['lucky'] = int(rng_lucky[i % len(rng_lucky)])
                    t['replay'] = int(rng_replay[i % len(rng_replay)])
                    ghost_tickets.append(t)
                ghost_meta = gp_out.get('meta', {})
        except Exception as e:
            ghost_tickets = []
            ghost_meta = {'error': str(e)}

        voice = dj_speak_swiss(rc0, re_lock_anchor, target_date, target_d,
                               ranked, tickets, hungry, rc0_silent)

        # Tablet
        tablet = [{
            'd': 'd0', 'date': rc0['date'][:5],
            'mains': rc0['n'], 'lucky': rc0.get('lucky'),
            'replay': rc0.get('replay'),
            'tier': rc0['tier'], 'family': f"{rc0['family']}0s",
        }]
        for i, d in enumerate(cycle, 1):
            tablet.append({
                'd': f'd{i}', 'date': d['date'][:5],
                'mains': d['_n'], 'lucky': d['_l'], 'replay': d['_r'],
                'is_re_lock': d['_l'] is not None and d['_l'] == d['_r'],
            })

        return {
            'mode': 'swiss',
            'rc0': {
                'date': rc0['date'], 'mains': rc0['n'],
                'lucky': rc0.get('lucky'), 'replay': rc0.get('replay'),
                'family': family, 'outlier': rc0.get('outlier'),
                'tier': rc0['tier'], 'family_count': rc0['family_count'],
            },
            're_lock_anchor': ({
                'date': re_lock_anchor['date'],
                'mains': re_lock_anchor['n'],
                'lucky': re_lock_anchor['lucky'],
                'replay': re_lock_anchor['replay'],
                'days_since': (target_date - re_lock_anchor['dt']).days,
            } if re_lock_anchor else None),
            'target_date': target_date_str,
            'target_d': target_d,
            'date_sum': date_sum(target_date),
            'is_72_flip_day': date_sum(target_date) == 72,
            'tablet': tablet[-10:],
            'cycle_count': len(cycle),
            'hungry_family': sorted(hungry),
            'hungry_unfired': sorted([h for h in hungry if h not in played]),
            'rc0_silent': rc0_silent,
            'top_tier': sorted([n for n, c, _ in ranked if c >= 4]),
            'mid_tier': sorted([n for n, c, _ in ranked if c == 3]),
            'support_tier': sorted([n for n, c, _ in ranked if c == 2]),
            'suspect_board': [
                {'n': n, 'lenses': c, 'laws': l}
                for n, c, l in ranked[:40]
            ],
            'lucky_ranking': lucky_rank,
            'replay_ranking': replay_rank,
            'tickets': tickets,
            'story_tickets': story_tickets,
            'ghost_tickets': ghost_tickets,
            'ghost_meta': ghost_meta,
            'suspect_pool': _swiss_pool,
            'banned': banned,
            'voice': voice,
        }
    finally:
        if owns_client:
            client.close()


if __name__ == '__main__':
    import asyncio, sys
    target = sys.argv[1] if len(sys.argv) > 1 else '22.04.2026'
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    result = asyncio.run(run_swiss_cosmic_engine(target, n))
    if 'voice' in result:
        print(result['voice'])
    else:
        print(result)
