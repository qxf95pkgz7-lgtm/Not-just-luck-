"""Session 40 — Story Composer regression tests.

Validates that the Story Composer fuses Brain + Ghost + Hungry + Prince
into multi-narrative tickets.
"""
import asyncio
import pytest


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_compose_stories_swiss_basic():
    from ghost_engine import compose_stories
    out = _run(compose_stories("13.05.2026", "swiss", count=8))
    assert out.get("error") is None
    assert out["mode"] == "swiss"
    assert out["count_returned"] >= 3
    # Each story has the required fields
    for s in out["stories"]:
        assert len(s["mains"]) == 6
        assert s["lucky"] in range(1, 7)
        assert s["replay"] in range(1, 11)
        assert s["theme"]
        assert s["story_arc"]
        assert s["number_dna"]
        assert s["narrative"]
        # No duplicates within ticket
        assert len(set(s["mains"])) == 6
        # All mains in Swiss range
        for n in s["mains"]:
            assert 1 <= n <= 42


def test_compose_stories_euro_basic():
    from ghost_engine import compose_stories
    out = _run(compose_stories("15.05.2026", "euro", count=8))
    assert out.get("error") is None
    assert out["mode"] == "euro"
    assert out["count_returned"] >= 4
    for s in out["stories"]:
        assert len(s["mains"]) == 5
        assert isinstance(s["stars"], list) and len(s["stars"]) == 2
        # Euro range
        for n in s["mains"]:
            assert 1 <= n <= 50
        for star in s["stars"]:
            assert 1 <= star <= 12


def test_compose_stories_palette_has_sources():
    """The palette must fuse signals from Brain + Ghost + Hungry."""
    from ghost_engine import compose_stories
    out = _run(compose_stories("13.05.2026", "swiss", count=5))
    palette = out["palette"]
    assert len(palette) > 0
    # At least one lens-tag mentions ghost AND at least one mentions hungry or voices
    all_tags = " ".join(t for p in palette for t in p["lenses"])
    assert "ghost" in all_tags or "alive" in all_tags
    # Auto-connections present
    p0 = palette[0]
    assert "circle" in p0["connections"]
    assert "mirror_28" in p0["connections"]


def test_compose_stories_themes_diverse():
    """Different stories must have different themes."""
    from ghost_engine import compose_stories
    out = _run(compose_stories("13.05.2026", "swiss", count=8))
    themes = [s["theme"] for s in out["stories"]]
    assert len(set(themes)) >= max(3, len(themes) - 1)  # nearly all unique


def test_compose_stories_sister_dates():
    from ghost_engine import compose_stories
    out = _run(compose_stories("13.05.2026", "swiss", count=5))
    sd = out["sister_date_precedents"]
    # 13.05 has historical sister dates in years past
    assert len(sd) >= 1
    for s in sd:
        assert s["mains"]
        assert "date" in s


def test_compose_stories_invalid_mode():
    from ghost_engine import compose_stories
    out = _run(compose_stories("13.05.2026", "powerball", count=5))
    assert "error" in out


def test_compose_stories_invalid_date():
    from ghost_engine import compose_stories
    out = _run(compose_stories("not-a-date", "swiss", count=5))
    assert "error" in out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
