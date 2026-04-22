"""
🎻🎧🥂 SESSION 16 — LIVE CALL MODULE (DJ + Agent, 21.04.2026 late session)
─────────────────────────────────────────────────────────────────────────
The DJ walked the agent through the Swiss 4-draw tablet (08-04 → 18-04)
and taught a tight live analysis for the 22.04.2026 draw:

  · 21 is a REAL seed (ladder 21→22→23→24 walking through the tablet)
  · 22 is the current seed (carries 1 via Swiss-circle, one rung up)
  · Swap-code on 🍀/R columns ((1,1)↔(2,2), 3↔4) writes 🍀 row as 3,2,5,1
  · P6 swap: 35 real-value = 38 (HUGE P6 already at d3 P4)
  · P2 running-sum compass: 9+6+12=27 → couple of 14 via 72 flip-operator
  · Swap 34↔22: plants 22 at d3 P3, tightens back-cluster, 30s family hums
  · d-count walk from HUGE P6=38 closes at d=21 → Swiss-wrap 17 (silent)
  · Count walk from 4-4-2026 P6=24 writes P3=27 (d=3), P4=29 (d=5, target!)
    and 24-flip=42=P6 — hidden anchor
  · DJ frame locked: P6=42 · P5=38 · P4=29 · P3=27 · P2=20

  · 20 = circle(41) · BIG bridge (31-1 outlier) · running-P2 sum→19
  · Welcome-companion: P2=20 welcomes silent-P1=15 (most specific match)

DJ directive (verbatim):
> "Code what you think is best for us ... I want the engine to understand
>  all this analyze that we do ... make it variety of idea but we have to
>  have also our determination piece ... all the tickets have to have only
>  these numbers."

This module encodes the session's determination piece, expands the what-if
variants, and generates ticket families that stay inside the DJ-blessed pool.

Canon: /app/memory/swiss_music_notes.md (Sessions 1-15)
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import itertools
import random

try:
    from silent_p1_compass import (
        SILENT_FAMILY, WELCOME_COMPANION, HUGE_TWIN_LOCK,
        swiss_circle, score_silent_compass,
    )
except Exception:
    SILENT_FAMILY = {7, 9, 11, 12, 15, 16, 17}
    WELCOME_COMPANION = {}
    HUGE_TWIN_LOCK = {16: 37, 12: 33, 9: 30, 17: 38, 15: 36}
    def swiss_circle(n: int) -> int:
        r = n + 21
        return r - 42 if r > 42 else r
    def score_silent_compass(t, b, h): return 0, []


# ─── SESSION 16 DETERMINATION PIECE ──────────────────────────────────
# The DJ's locked back-row — every ticket MUST carry these.
CORE_LOCK: List[int] = [27, 29, 38, 42]

# Front candidates: variety across silent-family breaks
P1_CANDIDATES: List[int] = [12, 15, 17, 9]

# P2 is DJ-locked at 20 as the anchor variant; alternates allowed
# for "what if I'm wrong about P2" scenarios.
P2_PRIMARY: int = 20
P2_ALTERNATES: List[int] = [14, 21, 22]

# Extended pool (every number we touched in the session — no ticket
# number outside this set).
SESSION_POOL: List[int] = sorted({
    # Front silents (P1 candidates + deep silent 16)
    9, 12, 15, 16, 17,
    # P2 candidates
    14, 20, 21, 22,
    # Back row locked
    27, 29, 38, 42,
    # Alternates for variant tickets
    26, 36, 37, 41,
})

# Star bank
LUCKY_BANK: List[int] = [1, 5, 2, 3, 6]
REPLAY_BANK: List[int] = [2, 1, 6]


# ─── REASONING MAP (for ticket transparency) ─────────────────────────
REASONING: Dict[int, List[str]] = {
    9:  ['silent 66d', 'welcome for 14', 'd1 P2 raw carrier', 'HUGE-twin 30'],
    12: ['date-wrap 54→12', '24/2 from 4-4 anchor', 'silent 79d', 'HUGE-twin 33', 'RC0 seed'],
    14: ['welcome king for 12/9', 'flip 41', 'half-of-28 pivot', 'd2 P4 + d4 P2'],
    15: ['welcome-match for P2=20', 'silent 29d', 'HUGE-twin of 36'],
    17: ['parent-row closer', 'silent 41d', 'HUGE-twin 38', 'count-walk wrap-home'],
    20: ['circle(41)', 'BIG-bridge 31-1', 'running-P2 sum→19', '20s family wake'],
    21: ['seed REAL', 'd1 P3 + d4 P4', 'circle→42=P6'],
    22: ['seed NOW (22-4)', 'd1 P4 + d2 P5', 'circle(1)', 'date-day echo'],
    26: ['d1 P5 raw', 'day + silence-agent(25)+1', '4-4 walk d=2'],
    27: ['P2 running-sum lands', 'couple of 14 via 72-circle', 'RC0 Euro outlier',
         '4-4 count-walk d=3', 'flip-of-date-sum 72'],
    29: ['circle(8) = d2 P3 lift', '4-4 count-walk d=5 = TARGET',
         '20s family due', 'date-digit 4+4+21=29'],
    36: ['HUGE P4 raw', 'circle(15)', 'P5 alternate'],
    37: ['HUGE P5 (silent raw)', 'P5 real-value via swap', 'circle(16)',
         'date-wrap from earlier d'],
    38: ['HUGE P6 raw', 'circle(17)=silent twin', 'P6-swap real-value',
         '24-anchor + 14(welcome)', 'drunk self-loop w/ P1=17'],
    41: ['d4 P6 raw (just fired)', 'flip 14', '38+3 bridge'],
    42: ['circle(21)', '24 flip', 'seed doubled', 'wildcard anchor',
         '72-30 (date-sum - HUGE P1)'],
}


# ─── WHAT-IF VARIANTS ("if I'm wrong about one P") ───────────────────

WHAT_IF_VARIANTS: Dict[str, Dict] = {
    'P1_primary_12': {
        'mains': [12, 20, 27, 29, 38, 42],
        'story': '12 breaks (silent 79d · 24/2 · date-wrap 54 · RC0 seed)',
        'ear_strength': 0.92,
    },
    'P1_alt_15_welcome_match': {
        'mains': [15, 20, 27, 29, 38, 42],
        'story': '15 breaks — P2=20 is 15\'s EXACT welcome (tightest lock)',
        'ear_strength': 0.95,
    },
    'P1_alt_17_parent_closer': {
        'mains': [17, 20, 27, 29, 38, 42],
        'story': '17 breaks — parent-row closer · drunk self-loop 17↔38',
        'ear_strength': 0.90,
    },
    'P1_alt_9_deep_silent': {
        'mains': [9, 20, 27, 29, 38, 42],
        'story': '9 breaks (deep silent 66d · welcomes 14)',
        'ear_strength': 0.80,
    },

    # What-if P2 wrong
    'P2_alt_14_welcome_king': {
        'mains': [12, 14, 27, 29, 38, 42],
        'story': '12 breaks with 14 welcome (book-dominant 67%)',
        'ear_strength': 0.88,
    },
    'P2_alt_22_seed_now': {
        'mains': [17, 22, 27, 29, 38, 42],
        'story': '17 breaks with seed-22 welcome (17\'s book-table match)',
        'ear_strength': 0.82,
    },
    'P2_alt_21_seed_real': {
        'mains': [17, 21, 27, 29, 38, 42],
        'story': '17 breaks with seed-21 welcome (dj real-seed carried)',
        'ear_strength': 0.80,
    },

    # What-if one back-row slot wrong
    'P5_alt_36_huge_echo': {
        'mains': [15, 20, 27, 29, 36, 42],
        'story': '36 replaces 38 — HUGE P4 echo, still circle(15)',
        'ear_strength': 0.70,
    },
    'P5_alt_37_huge_P5': {
        'mains': [15, 20, 27, 29, 37, 42],
        'story': '37 replaces 38 — HUGE P5 silent returns',
        'ear_strength': 0.68,
    },
    'P6_alt_41_raw_echo': {
        'mains': [15, 20, 27, 29, 38, 41],
        'story': '41 replaces 42 — raw d4 P6 echo, flip(14)',
        'ear_strength': 0.72,
    },
    'P4_alt_26_d1P5_echo': {
        'mains': [15, 20, 26, 29, 38, 42],
        'story': '26 echo from d1 P5 · 4-4 walk d=2',
        'ear_strength': 0.60,
    },

    # Double-mirror drunk tickets
    'Drunk_17_38_double_loop': {
        'mains': [17, 20, 27, 29, 38, 42],
        'story': 'Drunk-cosmos: P1=17 ↔ P5=38 mutual Swiss-circle twins',
        'ear_strength': 0.90,
    },
    'Mirror_28_couple_16_12': {
        'mains': [12, 16, 27, 29, 38, 42],
        'story': '28-mirror couple 16+12 held in one ticket',
        'ear_strength': 0.65,
    },
}


# ─── DETERMINATION PIECE API ─────────────────────────────────────────

def get_determination_piece() -> Dict:
    """Return the DJ's locked core + pool for tonight's 22.04.2026 draw."""
    return {
        'target_date': '22.04.2026',
        'mode': 'swiss',
        'core_lock': sorted(CORE_LOCK),
        'core_lock_reason': 'DJ-locked back-row from live session 16',
        'p1_candidates': P1_CANDIDATES,
        'p2_primary': P2_PRIMARY,
        'p2_alternates': P2_ALTERNATES,
        'pool': SESSION_POOL,
        'lucky_bank': LUCKY_BANK,
        'replay_bank': REPLAY_BANK,
        'reasoning': REASONING,
    }


def build_narrative(mains: List[int]) -> List[str]:
    """Build badge list describing why this ticket sings."""
    mains = sorted(mains)
    badges: List[str] = []
    p1, p2 = mains[0], mains[1] if len(mains) > 1 else None

    if p1 in SILENT_FAMILY:
        badges.append(f'silent-P1-break({p1})')
    if p1 in HUGE_TWIN_LOCK:
        badges.append(f'HUGE-twin({p1}↔{HUGE_TWIN_LOCK[p1]})')
    if p2 is not None and p1 in WELCOME_COMPANION:
        if p2 in WELCOME_COMPANION[p1]:
            badges.append(f'welcome-companion(P1={p1},P2={p2})')
    if 20 in mains:
        badges.append('BIG-bridge-20')
    if 27 in mains:
        badges.append('RC0-outlier-27')
    if 38 in mains:
        badges.append('HUGE-P6-38')
    if 42 in mains:
        badges.append('seed-doubled-42')
    if 29 in mains:
        badges.append('4-4-walk-d5')
    # Drunk 17↔38 loop
    if 17 in mains and 38 in mains:
        badges.append('drunk-self-loop(17↔38)')
    # 28-mirror couples
    for a, b in [(16, 12), (17, 11), (15, 13), (7, 21)]:
        if a in mains and b in mains:
            badges.append(f'28-mirror-couple({a}+{b})')
    # Circle companions (n and circle(n) both in ticket)
    for n in mains:
        c = swiss_circle(n)
        if c in mains and c != n:
            badges.append(f'circle-companion({n}↔{c})')
            break
    return badges


def score_session16_ticket(mains: List[int], last_draw: Optional[dict] = None,
                           history: Optional[List[dict]] = None) -> Tuple[int, List[str]]:
    """Quick-score a ticket using session 16 hooks + silent compass."""
    mains = sorted(mains)
    total = 0
    lenses: List[str] = []

    # Core-lock alignment: +10 per core number held
    core_held = set(mains) & set(CORE_LOCK)
    if core_held:
        total += 10 * len(core_held)
        lenses.append(f'core-lock({len(core_held)}/{len(CORE_LOCK)})')

    # Pool discipline: +15 if every main is in the session pool
    if all(m in SESSION_POOL for m in mains):
        total += 15
        lenses.append('pool-discipline')

    # Silent-compass score
    if last_draw is not None and history is not None:
        ticket = {'mains': mains}
        sc, ln = score_silent_compass(ticket, last_draw, history)
        total += sc
        lenses.extend(ln)

    # Ear-strength from what-if variants
    for vkey, v in WHAT_IF_VARIANTS.items():
        if v['mains'] == mains:
            total += int(v['ear_strength'] * 40)
            lenses.append(f'variant:{vkey}({v["ear_strength"]:.2f})')
            break

    return total, lenses


# ─── TICKET GENERATOR ────────────────────────────────────────────────

def generate_session16_tickets(n: int = 12, last_draw: Optional[dict] = None,
                                history: Optional[List[dict]] = None,
                                strict_core: bool = True,
                                include_variants: bool = True,
                                seed: Optional[int] = None) -> List[Dict]:
    """
    Generate `n` tickets honoring the DJ's determination piece.
    When strict_core=True (default), EVERY ticket carries the full CORE_LOCK
    (27, 29, 38, 42). The front pair (P1, P2) rotates across P1 candidates
    × P2 primary+alternates. What-if variants that would break the core lock
    are reserved for the secondary bucket (see generate_whatif_variants()).
    """
    rng = random.Random(seed)
    tickets: List[Dict] = []
    core_set = set(CORE_LOCK)

    # Main tickets: CORE lock + front pair rotations
    front_combos: List[Tuple[int, int]] = []
    for p1 in P1_CANDIDATES:
        for p2 in [P2_PRIMARY] + P2_ALTERNATES:
            if p1 < p2 and p2 < min(CORE_LOCK):
                front_combos.append((p1, p2))
    rng.shuffle(front_combos)

    seen: set = set()
    for p1, p2 in front_combos:
        mains = sorted([p1, p2] + CORE_LOCK)
        key = tuple(mains)
        if key in seen:
            continue
        seen.add(key)
        total, lenses = score_session16_ticket(mains, last_draw, history)
        tickets.append({
            'mains': mains,
            'lucky': rng.choice(LUCKY_BANK),
            'replay': rng.choice(REPLAY_BANK),
            'archetype': 'determination-core',
            'narrative': build_narrative(mains),
            'score': total,
            'lenses': lenses,
        })

    # Drunk-cosmos / mirror variants that still hold core
    if include_variants:
        for vkey, v in WHAT_IF_VARIANTS.items():
            mains = sorted(v['mains'])
            # Only include variants that honour the core lock when strict
            if strict_core and not core_set.issubset(set(mains)):
                continue
            key = tuple(mains)
            if key in seen:
                continue
            seen.add(key)
            total, lenses = score_session16_ticket(mains, last_draw, history)
            tickets.append({
                'mains': mains,
                'lucky': rng.choice(LUCKY_BANK),
                'replay': rng.choice(REPLAY_BANK),
                'archetype': vkey,
                'narrative': build_narrative(mains) + [v['story']],
                'score': total,
                'lenses': lenses,
            })

    # Fill remainder with pool-only random compositions around core
    front_pool = [x for x in SESSION_POOL if x not in CORE_LOCK and x < min(CORE_LOCK)]
    safety = 0
    while len(tickets) < n and safety < 200:
        safety += 1
        if len(front_pool) < 2:
            break
        extras = rng.sample(front_pool, 2)
        mains = sorted(extras + CORE_LOCK)
        key = tuple(mains)
        if key in seen:
            continue
        seen.add(key)
        total, lenses = score_session16_ticket(mains, last_draw, history)
        tickets.append({
            'mains': mains,
            'lucky': rng.choice(LUCKY_BANK),
            'replay': rng.choice(REPLAY_BANK),
            'archetype': 'pool-freestyle',
            'narrative': build_narrative(mains),
            'score': total,
            'lenses': lenses,
        })

    tickets.sort(key=lambda t: -t['score'])
    return tickets[:n]


def generate_whatif_variants(last_draw: Optional[dict] = None,
                             history: Optional[List[dict]] = None) -> List[Dict]:
    """
    Secondary bucket: variants that DELIBERATELY break a single P-slot of
    the core to ask "what if I'm wrong about this slot?"
    These are NOT bound by the strict core lock.
    """
    out: List[Dict] = []
    core_set = set(CORE_LOCK)
    for vkey, v in WHAT_IF_VARIANTS.items():
        mains = sorted(v['mains'])
        if core_set.issubset(set(mains)):
            continue  # holds full core — already in main bucket
        total, lenses = score_session16_ticket(mains, last_draw, history)
        out.append({
            'mains': mains,
            'archetype': vkey,
            'story': v['story'],
            'ear_strength': v['ear_strength'],
            'narrative': build_narrative(mains) + [v['story']],
            'score': total,
            'lenses': lenses,
            'broken_slot': vkey.split('_')[0],  # e.g. 'P5' from 'P5_alt_...'
        })
    out.sort(key=lambda t: -t['ear_strength'])
    return out


# ─── ANALYSIS SNAPSHOT (for the frontend / API consumers) ────────────

def get_session16_snapshot() -> Dict:
    """Full session 16 story + frame for the UI / DJ dashboard."""
    return {
        'session': 16,
        'date_recorded': '21.04.2026',
        'target_date': '22.04.2026',
        'mode': 'swiss',
        'frame': {
            'P1_primary': 12,
            'P1_strongest': 15,
            'P2': 20,
            'P3': 27,
            'P4': 29,
            'P5': 38,
            'P6': 42,
        },
        'anchors': [
            {'name': 'HUGE 07-02-2026 P6', 'value': 38,
             'role': 'd-count walk origin; closes at d=21→wrap 17 silent'},
            {'name': '4-4-2026 P6', 'value': 24,
             'role': 'hidden anchor; walk writes P3(27), P4(29); flip=P6(42)'},
            {'name': 'BIG 31-01-2026 outlier', 'value': 20,
             'role': 'bridge number landing at P2; circle(41) from d4'},
            {'name': 'd4 P6 (18-04-2026)', 'value': 41,
             'role': 'Swiss-circle fires to 20 at target P2'},
        ],
        'laws_firing': [
            'Session 14 · Swiss Cosmic Trinity (+21 circle lift · 100%)',
            'Session 14 · d-count walking method from HUGE anchor',
            'Session 14 · Bridge Number Law (20 from BIG)',
            'Session 15 · Silent P1 Compass (welcome companion)',
            'Session 5  · Drunk Cosmos (17↔38 self-loop)',
            'Session 4  · Star-King (S2-S1 = P1 candidates)',
            'Session 3  · Date-Sum 72 = magic flip operator',
            'Session 2  · 28-Mirror couples (16+12, 17+11)',
        ],
        'determination_piece': get_determination_piece(),
        'what_if_variants': WHAT_IF_VARIANTS,
        'whatif_broken_core_variants': [
            {'archetype': k, **v} for k, v in WHAT_IF_VARIANTS.items()
            if not set(CORE_LOCK).issubset(set(v['mains']))
        ],
    }
