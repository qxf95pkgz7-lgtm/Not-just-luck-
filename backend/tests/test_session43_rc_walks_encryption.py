"""Session 43 — RC-Walks Encryption Lens tests.

Verifies the encryption decoder produces the right output on the live
26.05.2026 d+18 reading: 17 = quintuple lock + P3 prediction, 39 silent,
DY-mirror date detection, RC0 anchor 24.03.2026 with inner_gap=9.
"""
from datetime import datetime
import pytest

from cosmic_voices.rc_walks_encryption import (
    compose_encryption_reading,
    date_encryption_signals,
    fit_best_ghost,
    find_preimages,
    multi_walk_convergence,
    track_p3_chain,
    predict_next_p3,
    _reverse_wrap,
)


def _draw(date_str: str, mains, stars=None):
    return {
        "date": date_str,
        "dt": datetime.strptime(date_str, "%d.%m.%Y"),
        "p": sorted(mains),
        "stars": stars,
    }


RC0 = {
    "date": "24.03.2026",
    "mains": [12, 16, 17, 18, 27],
    "stars": [1, 3],
}

# Real Euro draws RC0 → 22.05.2026 (d+1 .. d+17)
POST_RC = [
    _draw("27.03.2026", [4, 10, 43, 44, 48], [2, 4]),
    _draw("31.03.2026", [5, 8, 10, 33, 38], [2, 7]),
    _draw("03.04.2026", [8, 27, 29, 46, 49], [2, 10]),
    _draw("07.04.2026", [11, 14, 19, 36, 49], [6, 7]),
    _draw("10.04.2026", [10, 13, 14, 38, 41], [6, 9]),
    _draw("14.04.2026", [1, 2, 4, 28, 44], [5, 12]),
    _draw("17.04.2026", [22, 23, 28, 41, 47], [6, 8]),
    _draw("21.04.2026", [13, 16, 29, 40, 47], [3, 4]),
    _draw("24.04.2026", [25, 26, 30, 40, 45], [1, 5]),
    _draw("28.04.2026", [26, 29, 41, 46, 47], [8, 9]),
    _draw("01.05.2026", [3, 9, 42, 46, 47], [1, 11]),
    _draw("05.05.2026", [3, 4, 8, 20, 31], [6, 8]),
    _draw("08.05.2026", [2, 17, 19, 34, 37], [8, 11]),
    _draw("12.05.2026", [4, 26, 32, 35, 36], [5, 7]),
    _draw("15.05.2026", [3, 10, 38, 41, 43], [2, 9]),
    _draw("19.05.2026", [2, 12, 20, 38, 45], [2, 5]),
    _draw("22.05.2026", [6, 22, 26, 31, 37], [5, 8]),
]


def test_reverse_wrap():
    assert _reverse_wrap(26) == 12   # 62 -> 12 (DJ's "26=62=12")
    assert _reverse_wrap(17) == 21   # 71 -> 21 (the silent twin)
    assert _reverse_wrap(8) == 8     # single digit


def test_fit_best_ghost_finds_22_for_P4():
    """DJ's canonical ghost for P4=18 is 22. The brute-fit should agree."""
    training = [d["p"] for d in POST_RC[:15]]
    res = fit_best_ghost(anchor=18, training_draws=training)
    assert res["ghost"] == 22, f"expected ghost 22 (DJ canon), got {res['ghost']}"
    assert res["fires"] >= 10


def test_find_preimages_includes_raw_and_anchor():
    """target=22 with anchor=18, ghost=22 → preimages include 22 raw + 47 carrier."""
    pre = find_preimages(target=22, anchor=18, ghost=22)
    assert 22 in pre              # raw
    assert 47 in pre              # 47 - 25 carrier = 22
    assert 4 in pre               # 4 + 18 anchor = 22


def test_p3_chain_tracks_real_walk():
    """The P3 trail across d+13..d+17 must match Euro draws."""
    chain = track_p3_chain(POST_RC[-6:], depth=6)
    p3s = [c["p3"] for c in chain["chain"]]
    assert p3s == [8, 19, 32, 38, 20, 26], f"p3 chain {p3s}"
    # Reverse-wrap of 26 must be 12 (DJ canon)
    last = chain["chain"][-1]
    assert last["reverse_wrap"] == 12


def test_predict_next_p3_returns_17():
    """The next P3 prediction must include 17 (DJ's call) as top pick via
    gap-9 closure + RC0-P3 anchor return."""
    chain = track_p3_chain(POST_RC[-6:], depth=6)
    pred = predict_next_p3(chain, rc0_p3=17, inner_gap=9)
    assert pred["top_pick"] == 17
    paths_17 = [c for c in pred["candidates"] if c["n"] == 17][0]
    assert paths_17["weight"] >= 3


def test_multi_walk_convergence_quintuple_at_step18():
    """All 5 RC0 walks fit ghost=22, so target at step 18 = 22+17 = 39.
    The quintuple_lock must include numbers that satisfy ALL 5 walks."""
    training = [d["p"] for d in POST_RC[:15]]
    walks = {}
    for i, anc in enumerate(RC0["mains"], 1):
        best = fit_best_ghost(anc, training)
        walks[f"P{i}={anc}"] = {"anchor": anc, **best}
    conv = multi_walk_convergence(walks, target_step=17)  # 0-indexed step 17 = d+18
    assert 17 in conv["quintuple_lock"], f"17 must be quintuple lock, got {conv['quintuple_lock']}"


def test_date_signals_detects_DY_mirror_26():
    """26.05.2026 has D=26 and Y_suffix=26 → DY_mirror = True."""
    sig = date_encryption_signals("26.05.2026")
    assert sig["DY_mirror"] is True
    assert sig["D"] == 26 and sig["Y_suffix"] == 26
    # carrier discharges must include the 26+18=44 and 26-25=1
    assert 44 in sig["carrier_discharges_of_D"]
    assert 1 in sig["carrier_discharges_of_D"]
    # D reverse-wrap must be 12 (62 wrap)
    assert sig["D_reverse_wrap"] == 12


def test_compose_encryption_reading_live_call():
    """End-to-end live call for 26.05.2026 Euro must produce shout zone
    with 39 (5-walk + silent), and target_step=18."""
    reading = compose_encryption_reading(
        target_date="26.05.2026",
        mode="euro",
        rc0=RC0,
        all_quarter_draws=POST_RC,
        recent_draws=POST_RC[-3:],
        post_rc_draws=POST_RC,
    )
    assert reading["available"] is True
    assert reading["target_step"] == 18
    assert reading["rc0"]["inner_gap_P5_P4"] == 9
    # Shout zone must contain 17 OR 39 OR 14
    shout_ns = [s["n"] for s in reading["shout_zone"]]
    assert any(n in shout_ns for n in (14, 17, 39)), f"shout_zone {shout_ns}"
    # P3 prediction top pick = 17
    assert reading["p3_walk"]["prediction"]["top_pick"] == 17
    # Date signals: DY-mirror detected
    assert reading["date_signals"]["DY_mirror"] is True
