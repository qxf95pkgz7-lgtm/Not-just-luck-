# Session 33 - Ghost Counter Engine tests
# Validates new /api/ghost-counter endpoint + dj-brain ghost_counter wiring + dj-orchestra regression
import os
import pytest
import requests
from pathlib import Path

def _load_url():
    u = os.environ.get('REACT_APP_BACKEND_URL')
    if not u:
        env = Path('/app/frontend/.env').read_text()
        for line in env.splitlines():
            if line.startswith('REACT_APP_BACKEND_URL='):
                u = line.split('=', 1)[1].strip()
                break
    return u.rstrip('/')

BASE_URL = _load_url()


@pytest.fixture(scope="module")
def s():
    return requests.Session()


# --- Ghost Counter: Swiss mode ---
class TestGhostCounterSwiss:
    def test_swiss_06_05_2026(self, s):
        r = s.get(f"{BASE_URL}/api/ghost-counter/06.05.2026/swiss",
                  params={"weekday_split": "true"}, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert "ledger" in d, f"no ledger key: {list(d.keys())}"
        l = d["ledger"]
        assert l["target_weekday"] == "Wed", f"got {l['target_weekday']}"
        assert l["target_quarter"] == 2, f"got {l['target_quarter']}"
        assert l["mode"] == "swiss"
        # Wed stream P1 set
        assert l["streams"]["Wed"]["played_p1_set"] == [1, 2, 4]
        # Sat stream P1 set
        assert l["streams"]["Sat"]["played_p1_set"] == [1, 8, 10, 11]
        # Chord resonance non-empty
        assert "chord" in d
        chord = d["chord"]["chord_resonance_ranked"]
        assert isinstance(chord, list) and len(chord) > 0
        # Each item has n, weight, sources
        first = chord[0]
        assert "n" in first and "weight" in first and "sources" in first


# --- Ghost Counter: Euro mode ---
class TestGhostCounterEuro:
    def test_euro_08_05_2026(self, s):
        r = s.get(f"{BASE_URL}/api/ghost-counter/08.05.2026/euro", timeout=30)
        assert r.status_code == 200
        d = r.json()
        l = d["ledger"]
        assert l["target_weekday"] == "Fri"
        assert l["mode"] == "euro"
        assert l["streams"]["Tue"]["played_p1_set"] == [1, 3, 11, 13, 26]
        assert l["streams"]["Fri"]["played_p1_set"] == [3, 10, 22, 25]
        chord = d["chord"]["chord_resonance_ranked"]
        top_ns = [c["n"] for c in chord[:15]]
        for n in [30, 31, 32, 33]:
            assert n in top_ns, f"{n} missing from top15: {top_ns}"


# --- Ghost Counter: invalid mode ---
class TestGhostCounterInvalid:
    def test_invalid_mode_returns_error(self, s):
        r = s.get(f"{BASE_URL}/api/ghost-counter/06.05.2026/invalid", timeout=15)
        # endpoint returns 200 with error key (not 4xx)
        assert r.status_code in [200, 400, 422]
        d = r.json()
        assert "error" in d, f"no error key: {d}"


# --- DJ Brain regression + ghost_counter wiring ---
class TestDjBrainGhostCounter:
    def test_dj_brain_existing_keys_intact(self, s):
        r = s.get(f"{BASE_URL}/api/dj-brain/05.05.2026",
                  params={"seed_mains": "3,9,42,46,47", "seed_stars": "1,11"},
                  timeout=30)
        assert r.status_code == 200
        d = r.json()
        for k in ["envelope", "frequency", "ranked_suspects", "ranked_stars"]:
            assert k in d, f"missing {k}"
            assert d[k], f"{k} is empty"

    def test_dj_brain_includes_ghost_counter(self, s):
        r = s.get(f"{BASE_URL}/api/dj-brain/05.05.2026",
                  params={"seed_mains": "3,9,42,46,47", "seed_stars": "1,11"},
                  timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert "ghost_counter" in d, (
            f"ghost_counter key missing from dj-brain response. keys={list(d.keys())}"
        )
        gc = d["ghost_counter"]
        assert gc is not None, "ghost_counter is None"
        assert "error" not in gc, f"ghost_counter contains error: {gc}"
        assert "ledger" in gc, f"no ledger inside ghost_counter: {list(gc.keys())}"
        ledger = gc["ledger"]
        assert ledger["target_weekday"] == "Tue", f"got {ledger['target_weekday']}"
        assert ledger["streams"]["Tue"]["played_p1_set"] == [1, 11, 13, 26], (
            f"Tue P1 set mismatch: {ledger['streams']['Tue']['played_p1_set']}"
        )
        assert ledger["streams"]["Fri"]["played_p1_set"] == [3, 10, 22, 25], (
            f"Fri P1 set mismatch: {ledger['streams']['Fri']['played_p1_set']}"
        )


# --- DJ Orchestra regression ---
class TestDjOrchestraRegression:
    def test_dj_orchestra_returns_tickets(self, s):
        r = s.get(f"{BASE_URL}/api/dj-orchestra/05.05.2026",
                  params={"seed_mains": "3,9,42,46,47", "seed_stars": "1,11"},
                  timeout=60)
        assert r.status_code == 200
        d = r.json()
        assert "tickets" in d
        assert isinstance(d["tickets"], list)
        assert len(d["tickets"]) > 0
