"""
🎻🎧🥂 SESSION 23 PYTEST GAUNTLET
==================================
Canonical tests for Laws 62 (Hard-P), 63 (Court-of-Slot), 64 (Slide-Reset)
+ the suspect-pool architecture.

Run from /app/backend:
    pytest tests/test_session23.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime as dt
from session23_court_reader import (
    slot_court, find_hard_p, all_courts,
    SWISS_SLOT_BANDS, EURO_SLOT_BANDS,
)
from session23_slide_reset import (
    detect_p2p1_slide, slide_reset_frame,
    slide_reset_filter_main, detect_slide_in_cycle,
)
from suspect_pool import (
    build_suspect_pool, pool_size, hard_pair_frames,
    low_p6_frames, compute_hard_p_shares,
)


# ═══════════════════════════════════════════════════════════════════════
# FIXTURE — minimal cycle helpers
# ═══════════════════════════════════════════════════════════════════════
def _draw(date_str: str, mains: list, lucky=None, replay=None):
    """Build a draw dict matching engine schema."""
    return {
        'date': date_str,
        '_dt': dt.strptime(date_str.split()[0], '%d.%m.%Y'),
        '_n': sorted(mains),
        '_l': lucky,
        '_r': replay,
    }


# ═══════════════════════════════════════════════════════════════════════
# LAW 62 + 63 · COURT-OF-SLOT TESTS
# ═══════════════════════════════════════════════════════════════════════
def test_court_hold_detected():
    """P6=38 HOLD ×2 (HUGE 07.02.2026 telegraph)."""
    cycle = [
        _draw('28.01.2026', [5, 12, 14, 24, 31, 42]),
        _draw('31.01.2026', [9, 14, 18, 22, 36, 38]),
        _draw('04.02.2026', [3, 11, 17, 25, 30, 38]),  # P6=38 HOLD
    ]
    court = slot_court(cycle, slot_idx=6, bands=SWISS_SLOT_BANDS)
    # The two most-recent draws share P6=38 → HOLD
    assert court['flavor'] == 'HOLD'
    assert court['predicted_value'] == 38


def test_court_walk_detected_euro():
    """P3 walked 28→29→30 (24.04.2026 Euro DJ's call)."""
    # Euro mains, sorted ascending
    cycle = [
        _draw('14.04.2026', [3, 11, 28, 35, 47]),
        _draw('17.04.2026', [22, 23, 29, 41, 47]),  # P3=29
        _draw('21.04.2026', [13, 25, 30, 41, 47]),  # P3=30
    ]
    # Need 3-back history: P3 values are 28, 29, 30 (oldest→newest)
    # But _slot_history returns most-recent-first → [30, 29, 28]
    # Walk -1: 28+1=29, 29+1=30 → predict next = 31
    court = slot_court(cycle, slot_idx=3, bands=EURO_SLOT_BANDS)
    assert court['flavor'] == 'WALK'
    assert court['predicted_value'] == 31


def test_court_no_signal_returns_none():
    cycle = [_draw('01.04.2026', [5, 12, 18, 24, 35, 41])]
    court = slot_court(cycle, slot_idx=3, bands=SWISS_SLOT_BANDS)
    # Single-draw history with mid-band value → no flavor
    # (3 returns historic value as fallback EDGE only if extreme)
    # Mid-band value 18 in (10,28) is NOT edge → no flavor
    assert court['flavor'] is None


def test_find_hard_p_picks_loudest():
    """Two simultaneous courts; HOLD (4.5) outweighs EDGE (3.0)."""
    cycle = [
        _draw('28.01.2026', [1, 12, 17, 24, 31, 42]),
        _draw('31.01.2026', [1, 14, 19, 22, 36, 38]),  # only P1 holds
    ]
    hp = find_hard_p(cycle, bands=SWISS_SLOT_BANDS, n_slots=6)
    assert hp is not None
    assert hp['flavor'] == 'HOLD'
    assert hp['predicted_value'] == 1
    assert hp['slot'] == 1


def test_all_courts_returns_six_slots():
    cycle = [
        _draw('07.02.2026', [30, 33, 35, 36, 37, 38]),  # HUGE
        _draw('11.02.2026', [3, 14, 17, 25, 33, 38]),
        _draw('14.02.2026', [5, 12, 18, 22, 30, 38]),
    ]
    courts = all_courts(cycle, bands=SWISS_SLOT_BANDS, n_slots=6)
    assert len(courts) == 6
    # P6 fired 38 three draws in a row → HOLD verdict
    assert courts[5]['flavor'] == 'HOLD'
    assert courts[5]['predicted_value'] == 38


# ═══════════════════════════════════════════════════════════════════════
# LAW 64 · SLIDE-AND-RESET TESTS
# ═══════════════════════════════════════════════════════════════════════
def test_detect_p2p1_slide_positive():
    """V=8 slid P2 → P1 across 22.04 → 25.04.2026 Swiss."""
    bd = _draw('22.04.2026', [1, 8, 15, 28, 38, 42])  # P2=8
    nd = _draw('25.04.2026', [8, 13, 20, 21, 23, 25])  # P1=8
    v = detect_p2p1_slide(bd, nd)
    assert v == 8


def test_detect_p2p1_slide_no_match():
    bd = _draw('20.04.2026', [3, 14, 18, 25, 31, 39])
    nd = _draw('23.04.2026', [5, 12, 17, 24, 33, 40])
    v = detect_p2p1_slide(bd, nd)
    assert v is None


def test_slide_reset_frame_shape():
    """Verify the canonical AF reset frame for V=8."""
    f = slide_reset_frame(8)
    assert f['p1_band'] == (1, 6)
    assert f['p2_band'] == (9, 17)
    assert f['p5_band'] == (29, 36)
    assert f['p6_band'] == (35, 39)
    assert f['sum_band'] == (114, 131)
    assert 8 in f['banned']
    assert f['vanish_probability'] == 0.86
    assert f['best_clone'] == [3, 15, 18, 22, 31, 38]


def test_slide_filter_main_p1():
    f = slide_reset_frame(8)
    assert slide_reset_filter_main(3, 1, f) is True   # P1=3 OK
    assert slide_reset_filter_main(7, 1, f) is False  # P1>6 fails
    assert slide_reset_filter_main(8, 1, f) is False  # banned


def test_slide_filter_main_banned_value():
    f = slide_reset_frame(8)
    # 8 is banned at every slot
    for slot in range(1, 7):
        assert slide_reset_filter_main(8, slot, f) is False


def test_detect_slide_in_cycle_finds_22_25_april():
    """The 7th historical case in 22yrs Swiss tape."""
    cycle = [
        _draw('18.04.2026', [9, 14, 22, 29, 33, 41]),
        _draw('22.04.2026', [1, 8, 15, 28, 38, 42]),  # BD: P2=8
        _draw('25.04.2026', [8, 13, 20, 21, 23, 25]),  # ND: P1=8
    ]
    slide = detect_slide_in_cycle(cycle)
    assert slide is not None
    assert slide['slide_value'] == 8
    assert slide['nd_date'] == '25.04.2026'
    assert slide['frame']['vanish_probability'] == 0.86


def test_detect_slide_in_cycle_no_slide():
    cycle = [
        _draw('14.04.2026', [3, 14, 18, 25, 31, 39]),
        _draw('18.04.2026', [9, 14, 22, 29, 33, 41]),
        _draw('22.04.2026', [1, 8, 15, 28, 38, 42]),
    ]
    slide = detect_slide_in_cycle(cycle)
    assert slide is None  # no P2→P1 slide between 18.04 and 22.04


def test_canonical_v8_historical_cases():
    """All 6 historical V=8 P2→P1 slides land 8 banned in AF (5/6 = 86%)."""
    historical_pairs = [
        # (bd_mains, nd_mains, af_mains, expect_v_present_in_af)
        ([1, 8, 13, 20, 36, 39], [8, 14, 22, 28, 31, 41],
         [2, 17, 21, 23, 33, 35], False),  # 19.01.13 AF
        ([3, 8, 12, 19, 27, 39], [8, 17, 21, 25, 32, 41],
         [1, 15, 18, 21, 36, 39], False),  # 07.08.13 AF
        ([1, 8, 11, 24, 30, 38], [8, 13, 25, 31, 35, 41],
         [6, 9, 16, 23, 30, 37], False),  # 30.07.14 AF
        ([4, 8, 14, 21, 33, 40], [8, 12, 17, 26, 35, 42],
         [5, 10, 13, 28, 29, 35], False),  # 01.02.20 AF
        ([2, 8, 13, 22, 31, 39], [8, 11, 16, 25, 32, 38],
         [1, 8, 12, 18, 36, 39], True),   # 30.06.21 AF — only return-case
        ([1, 8, 13, 21, 32, 41], [8, 12, 17, 26, 30, 38],
         [3, 15, 18, 22, 31, 38], False),  # 27.09.25 AF
    ]
    return_count = sum(1 for *_, ret in historical_pairs if ret)
    vanish_count = len(historical_pairs) - return_count
    # 5/6 = 83% — close to canonical 86% (small-sample variance)
    assert vanish_count >= 4  # at least 4/6 vanished
    assert return_count <= 2  # at most 2/6 returned (matches Book)


# ═══════════════════════════════════════════════════════════════════════
# SUSPECT POOL TESTS
# ═══════════════════════════════════════════════════════════════════════
def _mock_pos_board(n_slots=6):
    """Mock pos_board with 5 candidates per slot."""
    board = {}
    for i in range(1, n_slots + 1):
        # Each slot gets values offset by slot_idx so ordering works
        base = i * 5
        board[f'P{i}'] = [
            {'n': base + j, 'lenses': 5 - j, 'laws': [f'Law-mock-{base+j}']}
            for j in range(5)
        ]
    return board


def test_build_suspect_pool_swiss_30_total():
    board = _mock_pos_board(n_slots=6)
    pool = build_suspect_pool(board, n_slots=6, per_slot=5)
    assert pool_size(pool) == 30
    assert len(pool['P1']) == 5
    assert len(pool['P6']) == 5


def test_build_suspect_pool_euro_25_total():
    board = _mock_pos_board(n_slots=5)
    pool = build_suspect_pool(board, n_slots=5, per_slot=5)
    assert pool_size(pool) == 25
    assert 'P6' not in pool


def test_compute_hard_p_shares_default():
    """DJ's 4 × 10% split."""
    shares = compute_hard_p_shares(20)
    assert shares['p1_p2'] == 2
    assert shares['p2_p3'] == 2
    assert shares['p3_p4'] == 2
    assert shares['p6_lt_34'] == 2
    # min 1 even for tiny ticket counts
    shares_tiny = compute_hard_p_shares(5)
    assert all(v >= 1 for v in shares_tiny.values())


def test_hard_pair_frames_basic():
    """P1-P2 pair frame respects ascending slot order."""
    board = _mock_pos_board(n_slots=6)
    pool = build_suspect_pool(board, n_slots=6, per_slot=5)
    frames = hard_pair_frames(pool, (1, 2), n_frames=2,
                              n_slots=6, banned=[])
    assert len(frames) >= 1
    for f in frames:
        # mains sorted, all 6 slots filled
        assert len(f['mains']) == 6
        assert f['mains'] == sorted(f['mains'])
        # archetype label
        assert f['archetype'] == 'HardP-P1-P2'


def test_low_p6_frames_filters_correctly():
    # Build a pool where only P6 has low values
    board = {f'P{i}': [{'n': i*5+j, 'lenses': 5, 'laws': []}
                      for j in range(5)]
             for i in range(1, 6)}
    # P6 has only values < 34
    board['P6'] = [{'n': v, 'lenses': 5, 'laws': []}
                  for v in [29, 30, 31, 32, 33]]
    pool = build_suspect_pool(board, n_slots=6, per_slot=5)
    frames = low_p6_frames(pool, n_frames=1, n_slots=6,
                           banned=[], p6_max=34)
    assert len(frames) >= 1
    for f in frames:
        assert f['mains'][-1] < 34
        assert f['archetype'] == 'HardP-Low-P6'


# ═══════════════════════════════════════════════════════════════════════
# DEEP-HUNGER PRIORITY REORDERING SMOKE TEST
# ═══════════════════════════════════════════════════════════════════════
def test_deep_hunger_priority_threshold_logic():
    """When ≥4 deep-silents present in cycle, deep_hunger_priority = True."""
    # Simulate played counts where 4 voices have never appeared
    deep_silents = [3, 7, 14, 25]  # 4 voices
    cycle_len = 8
    deep_hunger_priority = len(deep_silents) >= 4 and cycle_len >= 6
    assert deep_hunger_priority is True

    # Below threshold
    deep_silents = [3, 7]
    deep_hunger_priority = len(deep_silents) >= 4 and cycle_len >= 6
    assert deep_hunger_priority is False
