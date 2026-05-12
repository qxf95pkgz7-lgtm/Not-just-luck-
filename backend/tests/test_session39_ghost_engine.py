"""Session 39 — Ghost Engine (S38/S39 Ghost-Counting Canon) backend tests.

Validates GET /api/ghost-ledger/{target_date}/{mode}?lookback=10 for both
EuroMillions and Swiss Lotto modes. Confirms the 8 modules (arithmetic
ledger, ghost walk, closures, chainless windows, saturation, quarter
shape, carrier expansion, convergence) all return their expected keys.
"""
import os
import pytest
import requests

_url = os.environ.get("REACT_APP_BACKEND_URL")
if not _url:
    # fallback — load from frontend/.env (testing context)
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    _url = line.split("=", 1)[1].strip()
                    break
    except Exception:
        pass
BASE_URL = (_url or "").rstrip("/")


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ─── Ghost Ledger — Swiss mode ──────────────────────────────────────────
class TestGhostLedgerSwiss:
    URL = f"{BASE_URL}/api/ghost-ledger/13.05.2026/swiss"

    def test_status_200(self, api):
        r = api.get(self.URL, params={"lookback": 10}, timeout=60)
        assert r.status_code == 200, r.text

    def test_top_level_keys(self, api):
        r = api.get(self.URL, params={"lookback": 10}, timeout=60)
        data = r.json()
        assert "error" not in data, f"unexpected error: {data.get('error')}"
        for k in (
            "target_date", "mode", "lookback", "draws_window",
            "arithmetic_ledger", "alive_ghosts", "chainless_windows",
            "saturation", "quarter_shape", "carrier_pool", "convergence",
        ):
            assert k in data, f"missing key {k}"
        assert data["mode"] == "swiss"
        assert data["target_date"] == "13.05.2026"

    def test_convergence_shape(self, api):
        data = api.get(self.URL, params={"lookback": 10}, timeout=60).json()
        conv = data["convergence"]
        for k in ("ranked", "shout", "whisper"):
            assert k in conv, f"convergence missing {k}"
        assert isinstance(conv["shout"], list)
        assert isinstance(conv["whisper"], list)
        # all shout/whisper numbers must be valid Swiss main (1..42)
        for n in conv["shout"] + conv["whisper"]:
            assert 1 <= n <= 42, f"out-of-range swiss n={n}"

    def test_alive_ghosts_shape(self, api):
        data = api.get(self.URL, params={"lookback": 10}, timeout=60).json()
        for g in data["alive_ghosts"]:
            for k in ("n", "born_date", "age", "projected_hot_zone", "carriers"):
                assert k in g, f"alive ghost missing {k}"
            assert 1 <= g["n"] <= 42

    def test_arithmetic_ledger_has_births(self, api):
        data = api.get(self.URL, params={"lookback": 10}, timeout=60).json()
        ledger = data["arithmetic_ledger"]
        assert isinstance(ledger, list)
        assert len(ledger) > 0
        total_ghosts = sum(e.get("ghost_count", 0) for e in ledger)
        # Ledger should produce at least one ghost across 10 draws
        assert total_ghosts >= 1, "no ghosts born across 10 swiss draws"

    def test_quarter_shape_present(self, api):
        data = api.get(self.URL, params={"lookback": 10}, timeout=60).json()
        qs = data["quarter_shape"]
        assert isinstance(qs, dict)
        # Schema may differ but it must be a non-error dict
        assert "error" not in qs


# ─── Ghost Ledger — Euro mode ───────────────────────────────────────────
class TestGhostLedgerEuro:
    URL = f"{BASE_URL}/api/ghost-ledger/15.05.2026/euro"

    def test_status_200(self, api):
        r = api.get(self.URL, params={"lookback": 10}, timeout=60)
        assert r.status_code == 200, r.text

    def test_top_level_keys(self, api):
        data = api.get(self.URL, params={"lookback": 10}, timeout=60).json()
        assert "error" not in data, f"unexpected error: {data.get('error')}"
        for k in (
            "target_date", "mode", "lookback", "draws_window",
            "arithmetic_ledger", "alive_ghosts", "chainless_windows",
            "saturation", "quarter_shape", "carrier_pool", "convergence",
        ):
            assert k in data, f"missing key {k}"
        assert data["mode"] == "euro"

    def test_euro_range(self, api):
        data = api.get(self.URL, params={"lookback": 10}, timeout=60).json()
        for n in data["convergence"]["shout"] + data["convergence"]["whisper"]:
            assert 1 <= n <= 50, f"out-of-range euro n={n}"

    def test_different_from_swiss(self, api):
        euro = api.get(self.URL, params={"lookback": 10}, timeout=60).json()
        swiss = api.get(
            f"{BASE_URL}/api/ghost-ledger/13.05.2026/swiss",
            params={"lookback": 10}, timeout=60,
        ).json()
        # Different modes → different draws_window dates (or different
        # convergence shout)
        assert euro.get("draws_window") != swiss.get("draws_window"), \
            "Euro and Swiss returned identical draws_window"


# ─── Edge cases ─────────────────────────────────────────────────────────
class TestGhostLedgerEdge:
    def test_invalid_mode_no_500(self, api):
        r = api.get(f"{BASE_URL}/api/ghost-ledger/15.05.2026/foobar",
                    params={"lookback": 10}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        # Endpoint pattern: returns 200 with {error: ...}
        assert "error" in data

    def test_invalid_date_no_500(self, api):
        r = api.get(f"{BASE_URL}/api/ghost-ledger/bad-date/euro",
                    params={"lookback": 10}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "error" in data

    def test_lookback_param_respected(self, api):
        r = api.get(f"{BASE_URL}/api/ghost-ledger/15.05.2026/euro",
                    params={"lookback": 5}, timeout=60)
        data = r.json()
        assert data.get("lookback") == 5
        assert len(data.get("draws_window", [])) <= 5


# ─── Regression — older endpoints still alive ───────────────────────────
class TestRegressions:
    def test_cosmic_voices_still_works(self, api):
        r = api.get(f"{BASE_URL}/api/cosmic-voices/15.05.2026/euro",
                    params={"lens": "all"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "error" not in data or "voices" in data

    def test_ghost_counter_swiss_still_works(self, api):
        r = api.get(f"{BASE_URL}/api/ghost-counter/13.05.2026/swiss", timeout=30)
        assert r.status_code == 200
