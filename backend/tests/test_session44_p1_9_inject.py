"""Session 44 — P1=9 INJECT MANDATE tests.

DJ canon 26.05.2026 night: 'every 10 gen at least 2 tickets p1-9 Until it happens'
Force ≥20% of Swiss tickets per batch to carry P1=9 while 9 is P1-silent.
"""
from ghost_engine.story_composer import _inject_p1_9_swiss, _p1_silent_state


def test_p1_silent_state_detects_silence():
    """If 9 has 0 fires at P1 in recent draws, state must say p1_silent=True."""
    signals = {
        "recent_draws": [
            {"p": [1, 6, 8, 14, 22, 34]},
            {"p": [2, 9, 21, 22, 26, 35]},   # 9 at P2, NOT P1
            {"p": [4, 12, 34, 38, 39, 40]},
        ]
    }
    state = _p1_silent_state(signals, target_n=9, lookback=30)
    assert state["p1_silent"] is True
    assert state["p1_fires"] == 0


def test_p1_silent_state_detects_release():
    """When 9 fires at P1, mandate releases (p1_silent=False)."""
    signals = {
        "recent_draws": [
            {"p": [9, 15, 22, 25, 29, 32]},  # 9 at P1
            {"p": [4, 12, 34, 38, 39, 40]},
        ]
    }
    state = _p1_silent_state(signals, target_n=9, lookback=30)
    assert state["p1_silent"] is False
    assert state["p1_fires"] == 1


def test_inject_p1_9_swiss_forces_2_of_10_tickets():
    """Batch of 10 stories with no P1=9 → ≥2 must be modified to start with 9."""
    signals = {
        "recent_draws": [
            {"p": [1, 6, 8, 14, 22, 34]},
            {"p": [4, 12, 34, 38, 39, 40]},
        ]
    }
    palette = {n: {"score": 10, "lenses": []} for n in range(1, 43)}
    stories = [
        {
            "theme": f"T{i}", "mains": sorted([2 + i % 5, 12, 18, 24, 30, 35]),
            "story_arc": [f"P1={2 + i % 5} · snap-back front"],
            "cosmic_score": 50, "number_dna": {},
        }
        for i in range(10)
    ]
    result = _inject_p1_9_swiss(stories, palette, signals, count=10)
    p1_9_count = sum(1 for s in result if s.get("mains") and min(s["mains"]) == 9)
    assert p1_9_count >= 2, f"Expected ≥2 P1=9 tickets, got {p1_9_count}"
    injected = [s for s in result if s.get("p1_9_injected")]
    assert len(injected) >= 2
    for s in injected:
        assert 9 in s["mains"]
        assert min(s["mains"]) == 9
        assert s.get("p1_9_mandate") == "active"


def test_inject_p1_9_swiss_releases_when_9_fired():
    """When 9 has fired at P1 recently, no injection happens."""
    signals = {
        "recent_draws": [
            {"p": [9, 15, 22, 25, 29, 32]},
        ]
    }
    palette = {n: {"score": 10, "lenses": []} for n in range(1, 43)}
    stories = [
        {"theme": "T1", "mains": [2, 12, 18, 24, 30, 35],
         "story_arc": [], "cosmic_score": 50, "number_dna": {}}
    ]
    result = _inject_p1_9_swiss(stories, palette, signals, count=10)
    assert result[0]["mains"] == [2, 12, 18, 24, 30, 35]  # unchanged
    assert result[0]["p1_9_mandate"] == "released"


def test_inject_preserves_ticket_count():
    """Injection must not add/remove tickets."""
    signals = {"recent_draws": [{"p": [1, 6, 8, 14, 22, 34]}]}
    palette = {n: {"score": 5, "lenses": []} for n in range(1, 43)}
    stories = [
        {"theme": f"T{i}", "mains": sorted([3, 12, 18, 24, 30, 35]),
         "story_arc": [], "cosmic_score": 30, "number_dna": {}}
        for i in range(10)
    ]
    result = _inject_p1_9_swiss(stories, palette, signals, count=10)
    assert len(result) == 10
