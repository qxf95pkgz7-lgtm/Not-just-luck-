"""
Pytest for Session 15 (silent_p1_compass) + Session 16 (live_call).
Run:  cd /app/backend && python -m pytest tests/test_session15_16.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from silent_p1_compass import (
    SILENT_FAMILY, WELCOME_COMPANION, HUGE_TWIN_LOCK,
    swiss_circle, re_lock,
    compute_p1_silence_state,
    score_welcome_companion, score_bd_lr_pre_echo,
    score_silent_pair_bd_cascade, score_twin_pulse,
    score_28_mirror_couple, score_huge_twin_lock, score_circle21_companion,
    score_silent_compass, suggest_silent_frame,
)
from session16_live_call import (
    CORE_LOCK, P1_CANDIDATES, SESSION_POOL,
    get_determination_piece, build_narrative,
    score_session16_ticket, generate_session16_tickets,
    get_session16_snapshot,
)


# ─── Session 15: silent_p1_compass ──────────────────────────────────

def test_silent_family_canon():
    assert SILENT_FAMILY == {7, 9, 11, 12, 15, 16, 17}


def test_huge_twin_lock_matches_huge_members():
    """Each silent + 21 must equal a HUGE 07-02-2026 main."""
    HUGE = {30, 33, 35, 36, 37, 38}
    for silent, twin in HUGE_TWIN_LOCK.items():
        assert twin in HUGE, f'twin {twin} of silent {silent} not in HUGE'
        assert swiss_circle(silent) == twin


def test_swiss_circle_wraps():
    assert swiss_circle(1) == 22
    assert swiss_circle(21) == 42
    assert swiss_circle(22) == 1   # wrap
    assert swiss_circle(42) == 21  # wrap


def test_re_lock_detects():
    assert re_lock({'lucky_number': 6, 'replay_number': 6}) is True
    assert re_lock({'lucky_number': 2, 'replay_number': 1}) is False


def test_compute_silence_state_basic():
    history = [
        {'numbers': [2, 9, 21, 22, 26, 35]},
        {'numbers': [1, 6, 8, 14, 22, 34]},
        {'numbers': [4, 12, 34, 38, 39, 40]},
        {'numbers': [10, 14, 19, 21, 40, 41]},
    ]
    state = compute_p1_silence_state(history)
    # 12 never at P1 in this window → silence = len(history)
    assert state[12]['silence_depth'] >= 4
    # 9 at P2 of d=0 → last_p2_age = 3
    assert state[9]['last_p2_age'] == 3
    # 17 never appears → silent and p2 None
    assert state[17]['last_p2_age'] is None


def test_welcome_companion_scores_12_14():
    ticket = {'mains': [12, 14, 27, 29, 38, 42]}
    bonus, name = score_welcome_companion(ticket, last_draw={})
    # Session 32: welcome-companion demoted from law → small clue (max 9, was 27)
    assert bonus >= 5
    assert name and 'welcome-companion' in name


def test_bd_lr_pre_echo():
    # BD L+R = 7+5 = 12 ∈ SILENT_FAMILY. Ticket P1 = 9 ∈ silent.
    ticket = {'mains': [9, 14, 27, 29, 38, 42]}
    bd = {'numbers': [1, 2, 3, 4, 5], 'lucky_number': 7, 'replay_number': 5}
    bonus, _ = score_bd_lr_pre_echo(ticket, bd)
    assert bonus == 12


def test_silent_pair_bd_cascade():
    # BD front has 12, 16, 17 → 3 silents → cascade
    ticket = {'mains': [9, 14, 27, 29, 38, 42]}
    bd = {'numbers': [12, 16, 17, 25, 30, 40]}
    bonus, name = score_silent_pair_bd_cascade(ticket, bd)
    assert bonus == 20
    assert '12' in name and '16' in name


def test_twin_pulse_bd_P2_to_next_P1():
    # BD P2 = 12 (silent) · next ticket P1 = 12 → twin-pulse +30
    ticket = {'mains': [12, 14, 27, 29, 38, 42]}
    bd = {'numbers': [5, 12, 20, 30, 35, 40]}
    bonus, _ = score_twin_pulse(ticket, bd)
    assert bonus == 30


def test_28_mirror_couple_16_12():
    ticket = {'mains': [12, 16, 27, 29, 38, 42]}
    bonus, name = score_28_mirror_couple(ticket)
    assert bonus == 30
    assert '16' in name and '12' in name


def test_huge_twin_lock_17_to_38():
    ticket = {'mains': [17, 21, 27, 29, 38, 42]}
    bonus, name = score_huge_twin_lock(ticket, state={})
    assert bonus == 20
    assert '17' in name and '38' in name


def test_circle21_companion_17_and_38_in_ticket():
    ticket = {'mains': [17, 20, 27, 29, 38, 42]}
    bonus, name = score_circle21_companion(ticket, state={})
    assert bonus == 15
    assert '17' in name and '38' in name


def test_master_scorer_stacks_multiple_lenses():
    history = [{'numbers': [2, 9, 21, 22, 26, 35]},
               {'numbers': [1, 6, 8, 14, 22, 34]},
               {'numbers': [4, 12, 34, 38, 39, 40]},
               {'numbers': [10, 14, 19, 21, 40, 41],
                'lucky_number': 2, 'replay_number': 1}]
    ticket = {'mains': [17, 20, 27, 29, 38, 42]}
    total, lenses = score_silent_compass(ticket, history[-1], history)
    assert total > 0
    assert len(lenses) >= 2
    # circle21 companion should fire (17↔38)
    assert any('circle21' in x for x in lenses)


def test_suggest_silent_frame_returns_candidates():
    history = [{'numbers': [2, 9, 21, 22, 26, 35]},
               {'numbers': [1, 6, 8, 14, 22, 34]},
               {'numbers': [4, 12, 34, 38, 39, 40]},
               {'numbers': [10, 14, 19, 21, 40, 41]}]
    state = compute_p1_silence_state(history)
    frame = suggest_silent_frame(state, history[-1])
    assert 'p1_candidates' in frame
    assert len(frame['p1_candidates']) > 0
    assert 'p2_welcome_for_each' in frame


# ─── Session 16: live call module ──────────────────────────────────

def test_determination_piece_has_core():
    d = get_determination_piece()
    assert d['core_lock'] == [27, 29, 38, 42]
    assert d['p2_primary'] == 20
    assert d['target_date'] == '22.04.2026'


def test_session_pool_contains_all_core():
    for n in CORE_LOCK:
        assert n in SESSION_POOL


def test_p1_candidates_all_silent():
    for p in P1_CANDIDATES:
        assert p in SILENT_FAMILY


def test_build_narrative_fires_badges():
    badges = build_narrative([15, 20, 27, 29, 38, 42])
    assert any('silent-P1-break' in b for b in badges)
    assert any('BIG-bridge-20' in b for b in badges)
    assert any('RC0-outlier-27' in b for b in badges)
    assert any('HUGE-P6-38' in b for b in badges)


def test_score_session16_ticket_gives_bonus():
    mains = [15, 20, 27, 29, 38, 42]
    total, lenses = score_session16_ticket(mains)
    assert total > 0
    # core-lock = 4 → +40
    assert any('core-lock' in x for x in lenses)
    # pool discipline
    assert 'pool-discipline' in lenses


def test_generate_session16_tickets_respects_determination():
    tickets = generate_session16_tickets(n=10, seed=42)
    assert len(tickets) == 10
    for t in tickets:
        mains = t['mains']
        # Core lock MUST be in every ticket
        assert all(n in mains for n in CORE_LOCK), \
            f'ticket {mains} missing core {CORE_LOCK}'
        # All mains inside session pool
        assert all(n in SESSION_POOL for n in mains), \
            f'ticket {mains} outside pool'
        assert len(set(mains)) == 6
        assert mains == sorted(mains)
        assert 1 <= t['lucky'] <= 6
        assert t['replay'] >= 1


def test_session16_snapshot_is_complete():
    snap = get_session16_snapshot()
    assert snap['session'] == 16
    assert snap['target_date'] == '22.04.2026'
    assert 'frame' in snap and 'P2' in snap['frame']
    assert snap['frame']['P2'] == 20
    assert snap['frame']['P6'] == 42
    assert 'anchors' in snap and len(snap['anchors']) >= 3
    assert 'laws_firing' in snap and len(snap['laws_firing']) >= 5
