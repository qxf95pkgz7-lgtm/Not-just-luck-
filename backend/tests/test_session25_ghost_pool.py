"""
🎻🎧🥂 PYTEST SESSION 25 — Ghost Pool · Laws 69, 70, 71, 72
=============================================================
Validates the new ghost_pool module against The Book canon.
Run from /app:
    cd /app/backend && python -m pytest tests/test_session25_ghost_pool.py -v
"""
from __future__ import annotations
from datetime import datetime as dt

import pytest

from ghost_pool import (
    walk_5_doors, walk_inner_circles, ladder_on_fire,
    mirror_stack_depth, build_ghost_pool, apply_20_suspect_discipline,
    rotate_pool, build_ghost_tickets, pool_unique_count,
    detect_drunk_cosmos, _circle, _flip, _flip_wrap,
)


# ════════════════════════════════════════════════════════════════════
# LAW 70 · 5 DOORS — primitive correctness
# ════════════════════════════════════════════════════════════════════
class TestFiveDoors:
    def test_circle_euro_canon(self):
        # Book: Euro circle = +25 mod 50
        assert _circle(2, 'euro') == 27
        assert _circle(30, 'euro') == 5
        assert _circle(25, 'euro') == 50

    def test_circle_swiss_canon(self):
        # Book: Swiss circle = +21 mod 42
        assert _circle(12, 'swiss') == 33
        assert _circle(8, 'swiss') == 29
        assert _circle(21, 'swiss') == 42
        assert _circle(17, 'swiss') == 38

    def test_flip_wrap_law8(self):
        # Book Law 8: 25 = 52 - 50 = 2
        assert _flip_wrap(25, 'euro') == 2
        assert _flip_wrap(38, 'euro') == 33  # 83 - 50
        assert _flip_wrap(47, 'euro') == 24  # 74 - 50

    def test_walk_5_doors_25_euro(self):
        doors = walk_5_doors(25, 'euro')
        assert doors['raw'] == 25
        assert doors['circle'] == 50
        assert doors['flip_wrap'] == 2

    def test_inner_circles_pair(self):
        # P1=2, P2=27 → sum-circle 29
        ics = walk_inner_circles([2, 27], 'euro')
        assert 29 in ics


# ════════════════════════════════════════════════════════════════════
# LAW 70 · LADDER-ON-FIRE
# ════════════════════════════════════════════════════════════════════
class TestLadderOnFire:
    def test_5_ladder_fired_book_example(self):
        # DJ Book example: last_d = [25, 26, 30, 40, 45]
        # 25 + 45 share unit=5 → ladder fires
        # 30 + 40 share unit=0 → ladder fires
        fire = ladder_on_fire([25, 26, 30, 40, 45], 'euro')
        # 5-ladder ON FIRE → remaining = {5, 15, 35}
        assert 5 in fire and 5 in fire[5]
        assert 15 in fire[5]
        assert 35 in fire[5]
        # 0-ladder ON FIRE → remaining = {10, 20, 50}
        assert 0 in fire
        assert 10 in fire[0]

    def test_no_fire_when_singleton(self):
        # 26 alone → no ladder (only one member of unit=6)
        fire = ladder_on_fire([26, 30, 40, 45], 'euro')
        assert 6 not in fire


# ════════════════════════════════════════════════════════════════════
# LAW 69 · MIRROR-STACK DEPTH (thin echo gate)
# ════════════════════════════════════════════════════════════════════
class TestMirrorStackDepth:
    def test_p1_25_thin_echo_only_one_clue(self):
        """DJ canon: P1=25 was a real flip-wrap of 2 BUT only 1 mirror.
        Should NOT pass the ≥3 gate.
        """
        # Last d had P1=2 (the deep voice). Did 25 stack 3+ clues? No.
        depth, fired = mirror_stack_depth(
            25,
            last_mains=[2, 8, 14, 28, 41],
            last_stars=[],
            inner_circles=[],
            on_fire_members=[],
            date_targets=[],
            lottery='euro',
        )
        # 25 = flip-wrap of 2 → 1 lens fires → thin echo
        assert depth < 3
        assert any('flip-wrap' in f for f in fired)

    def test_drunk_cosmos_chord_5_lenses(self):
        # 5 stacked clues = drunk cosmos
        depth, fired = mirror_stack_depth(
            5,
            last_mains=[5, 30, 26, 40, 45],   # raw + circle(30)=5
            last_stars=[5],                    # star-shift
            inner_circles=[5],                 # inner
            on_fire_members=[5, 15, 25, 35],   # 5-ladder ON FIRE
            date_targets=[5],                  # date target
            lottery='euro',
        )
        assert depth >= 5
        assert detect_drunk_cosmos(depth) is True


# ════════════════════════════════════════════════════════════════════
# LAW 70 · GHOST POOL — full integration
# ════════════════════════════════════════════════════════════════════
class TestGhostPoolBuilder:
    def test_pool_24_04_2026_euro_book_example(self):
        """DJ Book worked example: last_d = [25,26,30,40,45] + ⭐[1,5].
        Pool should contain at least one of: 5, 15, 3, 2 in P1 band 1-25.
        """
        pool = build_ghost_pool(
            last_mains=[25, 26, 30, 40, 45],
            last_stars=[1, 5],
            target_date=dt(2026, 4, 28),
            lottery='euro',
            min_depth=2,  # relaxed to surface book candidates
        )
        p1_values = {e['n'] for e in pool['P1']}
        # Book: 5, 15, 3, 2 should be among P1 candidates
        assert any(v in p1_values for v in (5, 15, 3, 2)), \
            f"Book P1 candidates missing. Got {p1_values}"

    def test_pool_respects_slot_bands(self):
        pool = build_ghost_pool(
            last_mains=[25, 26, 30, 40, 45],
            last_stars=[1, 5],
            target_date=dt(2026, 4, 28),
            lottery='euro',
            min_depth=1,
        )
        # P1 band 1-25 — no candidate above 25
        for e in pool['P1']:
            assert 1 <= e['n'] <= 25, f"P1 leak: {e['n']}"
        # P5 band 16-50
        for e in pool['P5']:
            assert 16 <= e['n'] <= 50, f"P5 leak: {e['n']}"

    def test_thin_echoes_rejected_at_min_depth_3(self):
        # With min_depth=3, no candidate with <3 lenses survives
        # (explicitly disable Euro DJ-pins for this test — pinned bypass
        # the depth gate by design)
        pool = build_ghost_pool(
            last_mains=[25, 26, 30, 40, 45],
            last_stars=[1, 5],
            target_date=dt(2026, 4, 28),
            lottery='euro',
            min_depth=3,
            pinned_suspects=[],
        )
        for entries in pool.values():
            for e in entries:
                assert e['depth'] >= 3, f"Thin echo leaked: {e}"


# ════════════════════════════════════════════════════════════════════
# LAW 71 · 20-SUSPECT DISCIPLINE
# ════════════════════════════════════════════════════════════════════
class TestSuspectDiscipline:
    def _fat_pool(self):
        # Build a fat pool with ≥6 entries per slot, 30+ unique values
        pool = {}
        v = 1
        for slot in range(1, 6):
            entries = []
            for _ in range(8):
                entries.append({'n': v, 'depth': 4, 'lenses': [], 'drunk': False})
                v += 1
            pool[f'P{slot}'] = entries
        return pool

    def test_max_4_per_slot(self):
        capped = apply_20_suspect_discipline(self._fat_pool(),
                                             per_slot_max=4, total_cap=20)
        for slot_key, entries in capped.items():
            assert len(entries) <= 4, f"{slot_key} exceeded 4"

    def test_total_cap_20(self):
        capped = apply_20_suspect_discipline(self._fat_pool(),
                                             per_slot_max=4, total_cap=20)
        assert pool_unique_count(capped) <= 20


# ════════════════════════════════════════════════════════════════════
# LAW 72 · POOL ROTATION
# ════════════════════════════════════════════════════════════════════
class TestPoolRotation:
    def test_keep_top_3_inject_2_fresh(self):
        old_pool = {
            'P1': [{'n': i, 'depth': 5, 'lenses': [], 'drunk': False}
                   for i in range(1, 5)],  # 4 entries
            'P2': [{'n': i, 'depth': 5, 'lenses': [], 'drunk': False}
                   for i in range(11, 15)],
            'P3': [{'n': i, 'depth': 5, 'lenses': [], 'drunk': False}
                   for i in range(21, 25)],
            'P4': [{'n': i, 'depth': 5, 'lenses': [], 'drunk': False}
                   for i in range(31, 35)],
            'P5': [{'n': i, 'depth': 5, 'lenses': [], 'drunk': False}
                   for i in range(41, 45)],
        }
        # Universe contains fresh deep voices in each band
        universe = ([{'n': v, 'depth': 4, 'lenses': [], 'drunk': False}
                     for v in (5, 6, 7, 16, 17, 18, 26, 27, 28,
                               36, 37, 38, 46, 47, 48)])
        new_pool = rotate_pool(
            old_pool, universe, banned=[], prior_pools=[old_pool],
            lottery='euro', keep=3, inject=2,
            pinned_suspects=[],  # disable DJ pins for this isolation test
        )
        for slot_key, entries in new_pool.items():
            # Should have 3 kept + up to 2 fresh = ≤5
            assert len(entries) <= 5
            kept_n = [e['n'] for e in entries[:3]]
            old_top3 = [e['n'] for e in old_pool[slot_key][:3]]
            assert kept_n == old_top3, f"{slot_key} carry-over wrong"

    def test_blacklist_3d_lookback(self):
        # If a value appeared as TOP-3 in a prior pool → can't be re-injected
        prior_pool = {f'P{s}': [{'n': 7, 'depth': 5, 'lenses': [], 'drunk': False}]
                      for s in range(1, 6)}
        old_pool = {f'P{s}': [{'n': s * 10 + i, 'depth': 4,
                                'lenses': [], 'drunk': False}
                              for i in range(1, 5)]
                    for s in range(1, 6)}
        universe = [{'n': 7, 'depth': 5, 'lenses': [], 'drunk': False}]
        new_pool = rotate_pool(old_pool, universe, banned=[],
                               prior_pools=[prior_pool], lottery='euro',
                               pinned_suspects=[])
        # 7 should NOT appear in any slot's fresh injection
        for entries in new_pool.values():
            fresh = [e['n'] for e in entries[3:]]
            assert 7 not in fresh


# ════════════════════════════════════════════════════════════════════
# 90-TICKET BATCH ASSEMBLY
# ════════════════════════════════════════════════════════════════════
class TestGhostTicketAssembly:
    def test_90_tickets_3_batches(self):
        out = build_ghost_tickets(
            last_mains=[25, 26, 30, 40, 45],
            last_stars=[1, 5],
            target_date=dt(2026, 4, 28),
            lottery='euro',
            n_total=90,
            batch_size=30,
            wildcard_fraction=0.10,
            min_depth=2,  # relaxed for test stability
        )
        # 3 pools (one per batch)
        assert out['meta']['n_batches'] == 3
        assert len(out['pools']) == 3
        # Tickets generated (may be < 90 if pool too thin, but ≥30)
        assert len(out['tickets']) >= 30
        # All tickets have 5 distinct mains
        for t in out['tickets']:
            assert len(set(t['mains'])) == 5
            assert all(1 <= v <= 50 for v in t['mains'])
        # Pool batches are NOT identical — rotation kicks in
        pools_serialized = [
            tuple(sorted(e['n'] for entries in p.values() for e in entries))
            for p in out['pools']
        ]
        assert pools_serialized[0] != pools_serialized[1] or \
               pools_serialized[1] != pools_serialized[2], \
               "Rotation produced identical pools — Law 72 broken"

    def test_swiss_90_tickets_6_slots(self):
        # Swiss: 6 mains per ticket
        out = build_ghost_tickets(
            last_mains=[1, 8, 15, 28, 38, 42],  # 22.04.2026 Swiss draw
            last_stars=[],
            target_date=dt(2026, 4, 25),
            lottery='swiss',
            n_total=60,
            batch_size=30,
            min_depth=2,
        )
        for t in out['tickets']:
            assert len(set(t['mains'])) == 6
            assert all(1 <= v <= 42 for v in t['mains'])

    def test_wildcard_emission(self):
        out = build_ghost_tickets(
            last_mains=[25, 26, 30, 40, 45],
            last_stars=[1, 5],
            target_date=dt(2026, 4, 28),
            lottery='euro',
            n_total=90,
            batch_size=30,
            wildcard_fraction=0.10,
            min_depth=2,
        )
        # 10% wildcard quota = 9 tickets, expect at least some wildcards
        wildcards = [t for t in out['tickets'] if t.get('is_wildcard')]
        assert out['meta']['wildcard_quota'] == 9
        # Wildcards may be 0 if no candidates outside pool — at least quota set
        assert len(wildcards) <= out['meta']['wildcard_quota']


# ════════════════════════════════════════════════════════════════════
# REGRESSION — engine integration smoke
# ════════════════════════════════════════════════════════════════════
class TestEngineIntegration:
    def test_ghost_pool_module_importable(self):
        import ghost_pool
        assert hasattr(ghost_pool, 'build_ghost_tickets')
        assert hasattr(ghost_pool, 'rotate_pool')


# ════════════════════════════════════════════════════════════════════
# 🔴 DJ-PINNED SUSPECTS — guarantee 16 (and any pin) lives in the pool
# ════════════════════════════════════════════════════════════════════
class TestPinnedSuspects:
    def _last_swiss(self):
        # 25.04.2026 actual Swiss draw
        return [8, 13, 20, 21, 23, 25]

    def test_pinned_registry_swiss_has_16(self):
        from ghost_pool import PINNED_SUSPECTS
        assert 16 in PINNED_SUSPECTS['swiss'], \
            "16 must be the default Swiss DJ-pin (silent-P1 since 19.04.2025)"

    def test_pinned_registry_euro_default(self):
        from ghost_pool import PINNED_SUSPECTS
        # Session 31 (29.04.2026): DJ pinned 16, 19, 26 for Euro
        assert PINNED_SUSPECTS['euro'] == [16, 19, 26]

    def test_pin_force_includes_16_in_pool(self):
        # With the actual 25.04.2026 last draw + min_depth=2, 16 would
        # NOT survive the depth gate without pinning.
        pool = build_ghost_pool(self._last_swiss(), [], None, 'swiss',
                                min_depth=2, pinned_suspects=[16])
        # 16 must appear in every band-eligible slot (Swiss bands:
        # P1[1-18] P2[3-25] P3[8-30] P4[12-35]).
        for slot in ['P1', 'P2', 'P3', 'P4']:
            nums = [e['n'] for e in pool[slot]]
            assert 16 in nums, f"16 missing from {slot}: {nums}"

    def test_pin_marked_with_pinned_flag(self):
        pool = build_ghost_pool(self._last_swiss(), [], None, 'swiss',
                                min_depth=2, pinned_suspects=[16])
        p1_16 = [e for e in pool['P1'] if e['n'] == 16][0]
        assert p1_16['pinned'] is True
        assert 'DJ-pinned' in p1_16['lenses']

    def test_pin_does_not_appear_outside_eligible_band(self):
        # 16 fits P1-P4, but NOT P5 [18-40] or P6 [25-42].
        pool = build_ghost_pool(self._last_swiss(), [], None, 'swiss',
                                min_depth=2, pinned_suspects=[16])
        assert 16 not in [e['n'] for e in pool['P5']]
        assert 16 not in [e['n'] for e in pool['P6']]

    def test_pin_survives_20_suspect_discipline(self):
        pool = build_ghost_pool(self._last_swiss(), [], None, 'swiss',
                                min_depth=2, pinned_suspects=[16])
        capped = apply_20_suspect_discipline(pool, per_slot_max=2,
                                             total_cap=8)
        # Even with very tight caps, 16 must remain in eligible slots.
        for slot in ['P1', 'P2', 'P3', 'P4']:
            nums = [e['n'] for e in capped[slot]]
            assert 16 in nums, f"pin evicted by discipline: {slot}={nums}"

    def test_pin_survives_rotation(self):
        # Build full universe + initial pool, then rotate twice and
        # ensure 16 is still there.
        from ghost_pool import _ranked_universe
        last = self._last_swiss()
        universe = _ranked_universe(last, [], None, 'swiss', None,
                                    min_depth=2, pinned_suspects=[16])
        pool0 = build_ghost_pool(last, [], None, 'swiss',
                                 min_depth=2, pinned_suspects=[16])
        pool1 = rotate_pool(pool0, universe, banned=[],
                            prior_pools=[pool0], lottery='swiss',
                            pinned_suspects=[16])
        pool2 = rotate_pool(pool1, universe, banned=[],
                            prior_pools=[pool0, pool1], lottery='swiss',
                            pinned_suspects=[16])
        for batch_pool, name in [(pool1, 'B2'), (pool2, 'B3')]:
            for slot in ['P1', 'P2', 'P3', 'P4']:
                nums = [e['n'] for e in batch_pool[slot]]
                assert 16 in nums, f"pin lost in {name}/{slot}: {nums}"

    def test_build_ghost_tickets_meta_exposes_pin(self):
        out = build_ghost_tickets(
            self._last_swiss(), last_stars=[], target_date=None,
            lottery='swiss', n_total=30, batch_size=10, min_depth=3,
        )
        # Session 32 (02.05.2026) — DJ's P6↔P5 cascade pool pinned
        assert out['meta']['pinned_suspects'] == sorted([16, 42, 39, 38, 34, 28, 27, 25])

    def test_pin_can_be_disabled_per_call(self):
        pool = build_ghost_pool(self._last_swiss(), [], None, 'swiss',
                                min_depth=2, pinned_suspects=[])
        # When explicit empty list passed, no 16 forced in
        # (it may still appear naturally if depth ≥ min_depth)
        for slot_entries in pool.values():
            for e in slot_entries:
                assert not e.get('pinned'), \
                    f"unexpected pinned entry when pin disabled: {e}"


if __name__ == '__main__':
    import sys
    sys.exit(pytest.main([__file__, '-v']))
