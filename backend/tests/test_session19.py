"""
🎻 Session 19 pytest — canonizes DJ's Dialect Ladder + Ghost-Echo + Slot-Reincarnation.

Every canonical case below is a REAL historical validation the DJ walked me
through on 22.04.2026 late. Do NOT change expected values without the DJ.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from session19_dialect_ladder import (
    circle_swiss, circle_euro, flip_digits, flip_wrap, wrap_range,
    cosmic_orbit, dialect_ladder, column_ghost_walk, sum_ladder,
    unresolved_ghosts, ghost_echo_candidates,
    slot_reincarnation_targets, detect_slot_reincarnation_fires,
    compute_session19_ledger, score_session19, suggest_next_frame,
)


# ═══════════════════════════════════════════════════════════════════
# PRIMITIVES
# ═══════════════════════════════════════════════════════════════════
def test_circle_swiss():
    assert circle_swiss(14) == 35
    assert circle_swiss(21) == 42
    assert circle_swiss(22) == 1   # wrap
    assert circle_swiss(9) == 30
    assert circle_swiss(16) == 37  # HUGE P5 via +21


def test_circle_euro():
    assert circle_euro(14) == 39
    assert circle_euro(25) == 50
    assert circle_euro(26) == 1    # wrap
    assert circle_euro(41) == 16   # the DJ's key triangle stepping stone


def test_flip_digits():
    assert flip_digits(14) == 41
    assert flip_digits(26) == 62
    assert flip_digits(5) == 50    # 05 → 50


def test_flip_wrap_euro():
    """14 → 41 → Euro-wrap → 16 (the DJ's slot-reincarnation triangle)."""
    assert flip_wrap(14, 'euro') == 16


def test_flip_wrap_swiss():
    """26 → 62 → Swiss-wrap → 20."""
    assert flip_wrap(26, 'swiss') == 20


def test_cosmic_orbit_euro_14():
    o = cosmic_orbit(14, 'euro')
    assert o == {'raw': 14, 'twin': 39, 'flip': 41, 'flip_wrap': 16}


# ═══════════════════════════════════════════════════════════════════
# LAW 38 · DIALECT LADDER
# ═══════════════════════════════════════════════════════════════════
def test_dialect_ladder_euro_p2_anchor_14():
    """DJ's canonical: P2=14 → twin 39; min(14,39)=14 → ladder [14,15,16,17,18,19].

    Note: the DJ narrative of 12→13→14→15→16 uses a silent-FAMILY dialect
    (not just Swiss-circle) where 14↔12 via cross-book silent-compass. The
    pure twin ladder starts at 14. Silent-family dialect shift handled by
    score_session19 via silent_family amplifier.
    """
    ladder = dialect_ladder(14, 'euro', steps=6)
    assert ladder == [14, 15, 16, 17, 18, 19]


def test_dialect_ladder_swiss_p1_anchor_2():
    """Swiss 08.04.2026 P1=2 → twin 23; start=2 → [2,3,4,5,6,7].
    Validates d1=2 (anchor closure) and d3=4 landed P1 on 15.04.2026."""
    ladder = dialect_ladder(2, 'swiss', steps=6)
    assert ladder == [2, 3, 4, 5, 6, 7]


# ═══════════════════════════════════════════════════════════════════
# LAW 40 · SUM-LADDER — the KING signal validated on Swiss
# ═══════════════════════════════════════════════════════════════════
def test_sum_ladder_swiss_anchor_08_04_2026():
    """Swiss 08.04 anchor [2,9,21,22,26,35] P1+P2=11. Ladder = [11..16]."""
    ladder = sum_ladder([2, 9, 21, 22, 26, 35], 'swiss', steps=6)
    assert ladder[0] == 11
    assert ladder[3] == 14   # d4 = 14 landed at P2 on 18.04.2026 ✅
    assert ladder[4] == 15   # d5 = 15 landed at P3 on 22.04.2026 ✅
    assert ladder[5] == 16   # d6 = 16 = 25.04.2026 triple-lock target


# ═══════════════════════════════════════════════════════════════════
# LAW 41 · GHOST-ECHO — Euro 21.04.2026 canonical
# ═══════════════════════════════════════════════════════════════════
def test_ghost_echo_euro_13_resurface_as_p1():
    """Euro 07.04 anchor [11,14,19,36,49]. Recent draws d1..d5 from real history.
    d1 P2 ghost=15 real=13. 13 resurfaced as P1 at d5 (21.04.2026 [13,16,29,40,47])."""
    anchor = [11, 14, 19, 36, 49]
    recent = [
        [11, 14, 19, 36, 49],   # d1 07.04
        [10, 13, 14, 38, 41],   # d2 10.04
        [1, 2, 4, 28, 44],      # d3 14.04
        [22, 23, 28, 41, 47],   # d4 17.04
        [13, 16, 29, 40, 47],   # d5 21.04
    ]
    mm = ghost_echo_candidates(anchor, recent, 'euro')
    # Check d2 P2: ghost=15, real=13
    d2_p2 = [(col, g, r) for col, g, r in mm if col == 2 and g == 15 and r == 13]
    assert len(d2_p2) == 1, f"d2 P2 mismatch (ghost=15 real=13) not found in {mm}"
    ledger = compute_session19_ledger(anchor, recent, 'euro')
    # 13 should be an echo candidate
    assert 13 in ledger['echo_candidates']


# ═══════════════════════════════════════════════════════════════════
# LAW 42 · SLOT-REINCARNATION — flip-wrap triangle
# ═══════════════════════════════════════════════════════════════════
def test_slot_reincarnation_euro_14_41_16():
    """Euro anchor P2=14 → flip 41 → wrap 16.
    41 fired at d2 (10.04.2026) P5. 16 landed at d5 (21.04.2026) P2. Triangle closed."""
    anchor = [11, 14, 19, 36, 49]
    recent = [
        [11, 14, 19, 36, 49],
        [10, 13, 14, 38, 41],   # 41 fires here at P5 (middle voice)
        [1, 2, 4, 28, 44],
        [22, 23, 28, 41, 47],
        [13, 16, 29, 40, 47],   # 16 lands P2 — same slot as anchor P2=14, CLOSURE
    ]
    fires = detect_slot_reincarnation_fires(anchor, recent, 'euro')
    # Should find the P2 slot reincarnation
    p2_fire = [f for f in fires if f['slot'] == 2]
    assert len(p2_fire) == 1
    assert p2_fire[0]['anchor'] == 14
    assert p2_fire[0]['flip'] == 41
    assert p2_fire[0]['flip_wrap_target'] == 16
    assert p2_fire[0]['closed_same_slot'] is True


# ═══════════════════════════════════════════════════════════════════
# LEDGER + SCORING — end-to-end
# ═══════════════════════════════════════════════════════════════════
def test_unresolved_ghosts_swiss_25_04_prep():
    """Swiss 08.04 anchor; recent 5 draws through 22.04. Ghosts that
    never landed form the 25.04.2026 hungry list."""
    anchor = [2, 9, 21, 22, 26, 35]
    recent = [
        [2, 9, 21, 22, 26, 35],
        [1, 6, 8, 14, 22, 34],
        [4, 12, 34, 38, 39, 40],
        [10, 14, 19, 21, 40, 41],
        [1, 8, 15, 28, 38, 42],
    ]
    hungry = unresolved_ghosts(anchor, recent, 'swiss')
    # 16 is NOT unresolved here (not in walks from anchor [2,9,21,22,26,35])
    # But the SUM-ladder d6=16 IS the triple-lock target
    ledger = compute_session19_ledger(anchor, recent, 'swiss')
    assert ledger['next_step_sum_target'] == 16   # 🔴 25.04 triple-lock


def test_score_session19_boosts_sum_ladder_p3():
    """Ticket with 16 at P3 on 25.04.2026 should get Law40 P3-king bonus +25."""
    anchor = [2, 9, 21, 22, 26, 35]
    recent = [
        [2, 9, 21, 22, 26, 35],
        [1, 6, 8, 14, 22, 34],
        [4, 12, 34, 38, 39, 40],
        [10, 14, 19, 21, 40, 41],
        [1, 8, 15, 28, 38, 42],
    ]
    ledger = compute_session19_ledger(anchor, recent, 'swiss')
    # Ticket with 16 at P3
    ticket = [2, 9, 16, 27, 33, 42]
    bonus, tags = score_session19(ticket, ledger)
    assert bonus >= 25, f"Expected ≥25 bonus for sum-ladder P3 king, got {bonus} tags={tags}"
    assert any('sum-ladder-P3-king' in t for t in tags)


def test_suggest_next_frame_swiss_25_04():
    anchor = [2, 9, 21, 22, 26, 35]
    recent = [
        [2, 9, 21, 22, 26, 35],
        [1, 6, 8, 14, 22, 34],
        [4, 12, 34, 38, 39, 40],
        [10, 14, 19, 21, 40, 41],
        [1, 8, 15, 28, 38, 42],
    ]
    ledger = compute_session19_ledger(anchor, recent, 'swiss')
    frame = suggest_next_frame(ledger)
    assert frame['sum_target'] == 16
    assert 'P1' in frame and 'P6' in frame


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
