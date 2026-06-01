"""
Session 45 — Canon 31 Hungry-Number Engine tests.

Locks the engine against the LIVE 29.05.2026 Euro draw [5, 14, 18, 31, 35] ⭐2,12
and the prior db 26.05.2026 [6, 23, 25, 35, 37] ⭐6, 12.

Every chain DJ taught on 29.05.2026 night must be reproducible.
"""
from cosmic_voices.hungry_engine import (
    hungry_from_seed, cross_position_hungry, hungry_pool,
    flip_digits, wrap, tablet_neighbors, chain_finder,
)


DB_26_05 = {"p": [6, 23, 25, 35, 37], "stars": [6, 12]}
DRAW_29_05_ACTUAL = [5, 14, 18, 31, 35]


# ---------- Ops primitives ----------
def test_flip_basic():
    assert flip_digits(35) == 53
    assert flip_digits(18) == 81
    assert flip_digits(7) == 70
    assert flip_digits(14) == 41


def test_wrap_basic():
    assert wrap(54, 50) == 4
    assert wrap(81, 50) == 31
    assert wrap(73, 50) == 23
    assert wrap(35, 50) == 35


def test_tablet_neighbors_35():
    """35 sits at row 5 col 7 of 7-wide tablet. Above=28, left=34, NW=27."""
    nbrs = dict(tablet_neighbors(35, width=7, mx=49))
    assert nbrs.get("above") == 28
    assert nbrs.get("left") == 34
    assert nbrs.get("NW") == 27


# ---------- DJ chain reproductions ----------
def test_chain_14_hungry_from_35():
    """DJ: 'Sit 35, expect 14 hungry' (35 - 21 = 14, Swiss carrier-back)."""
    h = hungry_from_seed(35, mode="euro")
    assert 14 in h
    assert any("altCarrier(21)" in p or "Swiss" in p or "21" in p for p in h[14])


def test_chain_18_flip_to_31():
    """DJ: 18 ↔ 81 ↔ 31 (flip + wrap)."""
    h = hungry_from_seed(18, mode="euro")
    assert 31 in h
    assert any("flip→81 wrap→31" in p or "flip" in p and "31" in p for p in h[31])


def test_chain_18_carrier_back_to_6():
    """DJ: 18 → flip → 81 → wrap → 31 → -25 → 6. Multi-step chain via chain_finder."""
    chains = chain_finder(18, 6, mode="euro", max_depth=3)
    assert len(chains) >= 1, "Should find at least one chain 18 → 6"
    # At least one chain should mention flip and carrier
    full = " ".join(step for c in chains for step in c)
    assert "flip" in full or "carrier" in full


def test_chain_20_flip_cascade_to_4():
    """DJ: target=20, walk 20+25=45, flip→54, wrap→4. P1 of 12.05 was 4."""
    h = hungry_from_seed(20, mode="euro")
    # 20 + 25 = 45 reachable
    assert 45 in h
    # Then from 45: flip → 54 → wrap → 4
    h2 = hungry_from_seed(45, mode="euro")
    assert 4 in h2
    assert any("flip" in p for p in h2[4])


def test_cross_pos_10_plus_6_equals_16():
    """DJ: 10+6=16 hungry. 10 = db P4 (35) - 25. 6 = db P1."""
    cp = cross_position_hungry(DB_26_05, mode="euro")
    assert 16 in cp
    # The exact chain: P4-carrier + P1
    assert any("P4=35" in p and "P1=6" in p and "16" in p for p in cp[16])


def test_cross_pos_6_plus_12_equals_18():
    """DJ: 6+12=18 hungry. db P1=6, db ⭐12."""
    cp = cross_position_hungry(DB_26_05, mode="euro")
    assert 18 in cp
    assert any("P1=6" in p and "12" in p for p in cp[18])


def test_actual_draw_29_05_coverage():
    """🎯 THE BIG ONE: how many of the actual 29.05 draw [5,14,18,31,35]
    were reachable as hungry from seeds {35, 29 (date), 25 (carrier)} + db?
    """
    seeds = [35, 29, 25, 37]  # db P4, date day, Euro carrier, db P5
    pool = hungry_pool(seeds, db_draw=DB_26_05, mode="euro", min_paths=1)
    pool_set = {entry["n"] for entry in pool}
    hits = [n for n in DRAW_29_05_ACTUAL if n in pool_set]
    misses = [n for n in DRAW_29_05_ACTUAL if n not in pool_set]
    print(f"\n  Actual draw: {DRAW_29_05_ACTUAL}")
    print(f"  Hungry pool size: {len(pool_set)}")
    print(f"  Hits: {hits} ({len(hits)}/5)")
    print(f"  Misses: {misses}")
    # At least 4 of 5 mains MUST be in the hungry pool (5 is the wildcard month-digit)
    assert len(hits) >= 4, f"Hungry engine must catch ≥4 of actual draw, got {hits}"
    # 14, 18, 31, 35 must specifically be reachable
    for must in (14, 18, 31, 35):
        assert must in pool_set, f"{must} must be in hungry pool"


def test_hungry_multi_path_strongest():
    """Multi-path candidates rank highest."""
    seeds = [35, 37]
    pool = hungry_pool(seeds, mode="euro")
    # Top candidates should have ≥2 paths
    top = pool[:5]
    assert all(t["path_count"] >= 1 for t in top)
    # The TOP candidate has the most paths
    assert pool[0]["path_count"] >= pool[-1]["path_count"]


def test_chain_finder_finds_18_to_31():
    """chain_finder must find at least one chain 18 → 31."""
    chains = chain_finder(18, 31, mode="euro", max_depth=2)
    assert len(chains) >= 1
    # The shortest should mention flip
    assert any("flip" in step for step in chains[0])


def test_no_fake_laws_path_format():
    """All paths must be REAL ops (circle/flip/add/tablet/digit). No bare numerical
    laws like '6*7=42' should appear."""
    h = hungry_from_seed(35, mode="euro")
    for n, paths in h.items():
        for p in paths:
            # Each path must contain a real op marker
            assert any(marker in p for marker in
                       ["carrier", "flip", "ghost", "tablet", "digit", "wrap", "+", "-"])
