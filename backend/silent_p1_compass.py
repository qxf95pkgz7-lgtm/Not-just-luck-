"""
🎻🎧 SILENT P1 COMPASS — Swiss Lotto engine module (Session 15 canon)
─────────────────────────────────────────────────────────────────────
Tracks P1-silence for values 1-17 and scores tickets against the
FIVE KING CLUES + cross-book amplifiers the DJ taught on 21.04.2026.

"When a number has been silent at P1 for a long stretch, it doesn't
stay silent quietly. It plays at P2 first (the pre-echo), then escorts
its cosmic partners into the prior draw's 🍀+R sum. Then it breaks at
P1 — always with a specific WELCOME COMPANION at P2."

Canon source: /app/memory/swiss_music_notes.md (Session 15, L2680+)
"""
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ─── CANONICAL CONSTANTS ─────────────────────────────────────────────

SILENT_FAMILY = {7, 9, 11, 12, 15, 16, 17}

# P2 distributions observed when a silent X breaks at P1 (5-year scan)
WELCOME_COMPANION: Dict[int, Dict[int, int]] = {
    12: {14: 6, 15: 3, 17: 3, 13: 2, 22: 1, 25: 1},
    9:  {14: 4, 17: 3, 10: 2, 11: 1, 12: 1, 15: 1, 21: 1},
    16: {17: 3, 19: 2, 21: 1, 22: 1, 23: 1, 24: 1},
    17: {21: 3, 22: 3, 18: 2, 23: 2, 28: 2},
    11: {13: 4, 15: 3, 12: 2, 17: 2, 18: 2},
    15: {16: 3, 18: 3, 19: 2, 20: 2},
    7:  {9: 5, 8: 3, 12: 3, 10: 2, 11: 2},
}

# 28-mirror couples among silents (n1 + n2 = 28)
MIRROR_COUPLES_28 = [(16, 12), (17, 11), (15, 13), (7, 21)]

# HUGE-twin lock: each silent's +21 Swiss-circle is a HUGE 07.02.2026 member
# HUGE = [30, 33, 35, 36, 37, 38]
HUGE_TWIN_LOCK = {16: 37, 12: 33, 9: 30, 17: 38, 15: 36}


# ─── CORE HELPERS ────────────────────────────────────────────────────

def swiss_circle(n: int) -> int:
    """+21 mod 42 (Swiss-circle)"""
    r = n + 21
    return r - 42 if r > 42 else r


def re_lock(draw: dict) -> bool:
    """True when 🍀 == Replay (Swiss-only RE-lock signature)."""
    return draw.get('lucky_number') is not None and \
        draw.get('lucky_number') == draw.get('replay_number')


def compute_p1_silence_state(history: List[dict]) -> Dict[int, dict]:
    """
    Scan history (chronologically oldest→newest), return per-value state:
      { value: {silence_depth, last_p2_age, break_watch_active, is_deep_silent} }
    """
    state: Dict[int, dict] = {}
    n = len(history)
    for v in range(1, 18):
        last_p1_idx = None
        last_p2_idx = None
        for i, d in enumerate(history):
            nums = sorted(d.get('numbers', []))
            if not nums:
                continue
            if nums[0] == v:
                last_p1_idx = i
            if len(nums) > 1 and nums[1] == v:
                last_p2_idx = i
        silence = n - 1 - last_p1_idx if last_p1_idx is not None else n
        p2_age = n - 1 - last_p2_idx if last_p2_idx is not None else None
        break_watch = p2_age is not None and p2_age <= 10
        state[v] = {
            'silence_depth': silence,
            'last_p2_age': p2_age,
            'break_watch_active': break_watch,
            'is_deep_silent': silence >= 20,
            'is_silent_family': v in SILENT_FAMILY,
            'huge_twin': HUGE_TWIN_LOCK.get(v),
        }
    return state


def _ticket_mains(ticket: dict) -> List[int]:
    return sorted(ticket.get('mains') or ticket.get('numbers') or [])


# ─── FIVE KING CLUES ─────────────────────────────────────────────────

def score_welcome_companion(ticket: dict, last_draw: dict) -> Tuple[int, Optional[str]]:
    """CLUE A: +15 if P1=silent AND P2 ∈ WELCOME_COMPANION[P1]; +7 if top bucket."""
    mains = _ticket_mains(ticket)
    if len(mains) < 2:
        return 0, None
    p1, p2 = mains[0], mains[1]
    if p1 not in SILENT_FAMILY:
        return 0, None
    table = WELCOME_COMPANION.get(p1, {})
    if p2 not in table:
        return 0, None
    bonus = 15
    top = max(table.values())
    if table[p2] == top:
        bonus += 7
    if p2 in SILENT_FAMILY:
        bonus += 5  # double-silent welcome
    return bonus, f'welcome-companion(P1={p1},P2={p2})'


def score_bd_lr_pre_echo(ticket: dict, last_draw: dict) -> Tuple[int, Optional[str]]:
    """CLUE B: +12 if BD L+R ∈ SILENT_FAMILY AND ticket P1 ∈ SILENT_FAMILY."""
    mains = _ticket_mains(ticket)
    if not mains:
        return 0, None
    p1 = mains[0]
    if p1 not in SILENT_FAMILY:
        return 0, None
    L = last_draw.get('lucky_number')
    R = last_draw.get('replay_number')
    if L is None or R is None:
        return 0, None
    lr_sum = L + R
    if lr_sum in SILENT_FAMILY:
        return 12, f'BD-L+R={lr_sum}-silent-pre-echo'
    return 0, None


def score_silent_pair_bd_cascade(ticket: dict, last_draw: dict) -> Tuple[int, Optional[str]]:
    """CLUE C: +20 if BD has ≥2 silents in {P1,P2,P3} AND ticket P1 ∈ silent."""
    mains = _ticket_mains(ticket)
    if not mains or mains[0] not in SILENT_FAMILY:
        return 0, None
    bd = sorted(last_draw.get('numbers', []))
    if len(bd) < 3:
        return 0, None
    front = set(bd[:3])
    silent_hits = front & SILENT_FAMILY
    if len(silent_hits) >= 2:
        return 20, f'BD-silent-pair-cascade({sorted(silent_hits)})'
    return 0, None


def score_raw_self_echo(ticket: dict, last_draw: dict, state: dict) -> Tuple[int, Optional[str]]:
    """CLUE D: +25 if silent X raw ∈ BD AND ticket P1 == X (2× for X=16)."""
    mains = _ticket_mains(ticket)
    if not mains:
        return 0, None
    p1 = mains[0]
    if p1 not in SILENT_FAMILY:
        return 0, None
    if p1 in (last_draw.get('numbers') or []):
        bonus = 50 if p1 == 16 else 25
        return bonus, f'raw-self-echo({p1})'
    return 0, None


def score_twin_pulse(ticket: dict, last_draw: dict) -> Tuple[int, Optional[str]]:
    """CLUE E: +30 if BD P2 == silent X AND ticket P1 == X (lead-time = 1 draw)."""
    mains = _ticket_mains(ticket)
    if not mains:
        return 0, None
    bd = sorted(last_draw.get('numbers', []))
    if len(bd) < 2:
        return 0, None
    if mains[0] == bd[1] and mains[0] in SILENT_FAMILY:
        return 30, f'twin-pulse(P2={bd[1]}→P1)'
    return 0, None


# ─── CROSS-BOOK AMPLIFIERS ───────────────────────────────────────────

def score_circle21_companion(ticket: dict, state: dict) -> Tuple[int, Optional[str]]:
    """Session 14: +15 if ticket P1=silent AND ticket carries circle(P1) too."""
    mains = set(_ticket_mains(ticket))
    if not mains:
        return 0, None
    p1 = min(mains)
    if p1 not in SILENT_FAMILY:
        return 0, None
    circ = swiss_circle(p1)
    if circ in mains:
        return 15, f'circle21-companion({p1}↔{circ})'
    return 0, None


def score_28_mirror_couple(ticket: dict) -> Tuple[int, Optional[str]]:
    """Law 22/28: +30 if ticket holds BOTH halves of a silent 28-mirror couple."""
    mains = set(_ticket_mains(ticket))
    for a, b in MIRROR_COUPLES_28:
        if a in mains and b in mains:
            return 30, f'28-mirror-couple({a}+{b})'
    return 0, None


def score_huge_twin_lock(ticket: dict, state: dict) -> Tuple[int, Optional[str]]:
    """Trinity: +20 if ticket P1 ∈ HUGE_TWIN_LOCK keys (16,12,9,17,15)."""
    mains = _ticket_mains(ticket)
    if not mains:
        return 0, None
    p1 = mains[0]
    if p1 in HUGE_TWIN_LOCK:
        return 20, f'HUGE-twin-lock(P1={p1}↔{HUGE_TWIN_LOCK[p1]})'
    return 0, None


# ─── MASTER SCORER ───────────────────────────────────────────────────

def score_silent_compass(
    ticket: dict, last_draw: dict, history: List[dict]
) -> Tuple[int, List[str]]:
    """Score a ticket against all 5 king clues + 3 amplifiers.
    If BD is RE-LOCK, multiply final total by 1.5."""
    state = compute_p1_silence_state(history)
    total = 0
    lenses: List[str] = []

    for fn in (score_welcome_companion, score_bd_lr_pre_echo,
               score_silent_pair_bd_cascade, score_twin_pulse):
        b, name = fn(ticket, last_draw)
        if b:
            total += b
            if name:
                lenses.append(name)

    for fn in (score_raw_self_echo,):
        b, name = fn(ticket, last_draw, state)
        if b:
            total += b
            if name:
                lenses.append(name)

    for fn in (score_circle21_companion, score_huge_twin_lock):
        b, name = fn(ticket, state)
        if b:
            total += b
            if name:
                lenses.append(name)

    b, name = score_28_mirror_couple(ticket)
    if b:
        total += b
        if name:
            lenses.append(name)

    if re_lock(last_draw):
        total = int(total * 1.5)
        lenses.append('RE-LOCK-amplified')

    return total, lenses


# ─── LIVE FRAME SUGGESTER ────────────────────────────────────────────

def suggest_silent_frame(state: dict, last_draw: dict) -> dict:
    """Return break-watch flags, top P1 candidates, P2 welcome hints."""
    ranked = sorted(
        ((v, s) for v, s in state.items() if s['is_silent_family']),
        key=lambda x: -x[1]['silence_depth'],
    )
    top = [v for v, _ in ranked[:5]]
    warm = [v for v, s in ranked if s['break_watch_active']]
    bd = sorted(last_draw.get('numbers', []))
    bd_front = set(bd[:3])
    lr_sum = (last_draw.get('lucky_number') or 0) + (last_draw.get('replay_number') or 0)

    frame = {
        'p1_candidates': top,
        'p1_warm': warm,
        'p2_welcome_for_each': {v: sorted(WELCOME_COMPANION.get(v, {}).keys()) for v in top},
        'bd_silent_front': sorted(bd_front & SILENT_FAMILY),
        'bd_lr_sum': lr_sum,
        'bd_lr_is_silent': lr_sum in SILENT_FAMILY,
        'bd_is_re_lock': re_lock(last_draw),
        'huge_twin_lock': {v: HUGE_TWIN_LOCK.get(v) for v in top if v in HUGE_TWIN_LOCK},
    }
    return frame
