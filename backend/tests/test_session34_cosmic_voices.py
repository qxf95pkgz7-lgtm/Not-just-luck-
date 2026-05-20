"""
Session 34 — Cosmic Voices (Lens #16) test suite.
Validates /api/cosmic-voices/{date}/{mode} and dj-brain integration.
"""
import os
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consensus-secret.preview.emergentagent.com").rstrip("/")
EP = f"{BASE_URL}/api/cosmic-voices"

EXPECTED_LENSES = {
    "rc_detector", "climbing_voice", "sinking_voice", "gap_echo_97",
    "star_product_door", "q_opening_melody", "internal_mirror",
    "stance_tracker", "saturation_ledger", "convergence_scorer",
}


# --- Cosmic Voices: all-lens Euro ---
class TestCosmicVoicesEuroAll:
    def test_all_lenses_present(self):
        r = requests.get(f"{EP}/08.05.2026/euro?lens=all", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("target_date") == "08.05.2026"
        assert data.get("mode") == "euro"
        assert data.get("lens") == "all"
        voices = data.get("voices", {})
        missing = EXPECTED_LENSES - set(voices.keys())
        assert not missing, f"Missing lenses: {missing}"

    def test_rc_detector_anchor(self):
        r = requests.get(f"{EP}/08.05.2026/euro?lens=all", timeout=30)
        rc = r.json()["voices"]["rc_detector"]
        assert rc.get("date") == "24.03.2026", f"RC0 anchor wrong: {rc.get('date')}"
        assert rc.get("days_since") == 45, f"days_since={rc.get('days_since')}"

    def test_internal_mirror_current_tune_28(self):
        r = requests.get(f"{EP}/08.05.2026/euro?lens=all", timeout=30)
        im = r.json()["voices"]["internal_mirror"]
        assert im.get("current_tune") == "28", f"current_tune={im.get('current_tune')}"

    def test_saturation_ledger_includes_47(self):
        r = requests.get(f"{EP}/08.05.2026/euro?lens=all", timeout=30)
        sl = r.json()["voices"]["saturation_ledger"]
        sat = sl.get("saturated_mains") or []
        # sat may be list[int] or list[dict]
        ns = []
        for x in sat:
            if isinstance(x, dict):
                ns.append(x.get("n"))
            else:
                ns.append(x)
        assert 47 in ns, f"saturated_mains missing 47: {sat}"


# --- Cosmic Voices: single lens (q_opening_melody) ---
class TestQOpeningMelody:
    def _q(self):
        r = requests.get(f"{EP}/08.05.2026/euro?lens=q_opening_melody", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        # Single-lens mode returns lens key at top-level OR nested under voices
        q = data.get("q_opening_melody") or data.get("voices", {}).get("q_opening_melody")
        assert q is not None, f"q_opening_melody missing in: {data}"
        return q

    def test_single_lens_q_melody(self):
        q = self._q()
        assert q.get("opening_pair") == [11, 14], f"opening_pair={q.get('opening_pair')}"
        assert (q.get("fired_count") or 0) >= 3, f"fired_count={q.get('fired_count')}"

    def test_unpaid_pairs_canonical(self):
        q = self._q()
        unpaid = q.get("unpaid_pairs") or []
        # normalise (each pair is list of two ints; orderless contains)
        unpaid_sets = [set(p) for p in unpaid]
        assert {12, 15} in unpaid_sets, f"unpaid_pairs missing [12,15]: {unpaid}"
        assert {9, 12} in unpaid_sets, f"unpaid_pairs missing [9,12]: {unpaid}"


# --- Cosmic Voices: Swiss mode ---
class TestCosmicVoicesSwiss:
    def test_swiss_all_lenses(self):
        r = requests.get(f"{EP}/06.05.2026/swiss?lens=all", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("mode") == "swiss"
        voices = data.get("voices", {})
        missing = EXPECTED_LENSES - set(voices.keys())
        assert not missing, f"Swiss missing lenses: {missing}"


# --- Cosmic Voices: pin_mains DJ override ---
class TestPinMains:
    def test_dj_pin_tag_on_n12(self):
        r = requests.get(f"{EP}/08.05.2026/euro?pin_mains=12,18", timeout=30)
        assert r.status_code == 200, r.text
        cs = r.json()["voices"].get("convergence_scorer", {})
        # Find n=12 entry, verify it carries DJ-PIN tag somewhere
        found = False
        # convergence_scorer may have shouts/whispers/scores list
        candidates = []
        for key in ("shouts", "whispers", "scores", "ranked", "convergence", "rows"):
            v = cs.get(key)
            if isinstance(v, list):
                candidates.extend(v)
        # Also walk shallow values
        if not candidates and isinstance(cs, dict):
            for v in cs.values():
                if isinstance(v, list):
                    candidates.extend(v)
        for row in candidates:
            if not isinstance(row, dict):
                continue
            if row.get("n") == 12:
                tags = row.get("tags") or row.get("lenses") or []
                # tags can be list of str or list of dict
                tag_strs = [t if isinstance(t, str) else str(t) for t in tags]
                joined = " ".join(tag_strs) + " " + str(row)
                if "DJ-PIN" in joined or "dj_pin" in joined.lower() or "pin" in joined.lower():
                    found = True
                    break
        assert found, f"n=12 with DJ-PIN tag not found in convergence_scorer: {cs}"


# --- Invalid mode ---
class TestInvalidMode:
    def test_bad_mode_no_500(self):
        r = requests.get(f"{EP}/08.05.2026/badmode?lens=all", timeout=30)
        assert r.status_code != 500, f"Got 500: {r.text[:200]}"
        # Accept either 4xx error OR 200 with {error: ...}
        if r.status_code == 200:
            assert "error" in r.json(), f"No error key: {r.json()}"


# --- DJ Brain integration (lens #16 wired) ---
class TestDjBrainCosmicVoices:
    def test_dj_brain_includes_cosmic_voices(self):
        r = requests.get(
            f"{BASE_URL}/api/dj-brain/05.05.2026?seed_mains=3,9,42,46,47&seed_stars=1,11",
            timeout=60,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "cosmic_voices" in data, f"cosmic_voices missing in dj-brain keys: {list(data.keys())}"
        assert data["cosmic_voices"] is not None


# --- Regressions: Session 33 (ghost-counter) and Session 31 (dj-suspects) ---
class TestRegressions:
    def test_ghost_counter_swiss_still_works(self):
        r = requests.get(
            f"{BASE_URL}/api/ghost-counter/06.05.2026/swiss?weekday_split=true",
            timeout=30,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        # should not be an error
        assert "error" not in d or d.get("error") in (None, "")

    def test_dj_suspects_euro_still_works(self):
        r = requests.get(f"{BASE_URL}/api/dj-suspects?mode=euro", timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert isinstance(d, (dict, list))
