"""
🎼 COSMIC VOICES ORCHESTRATOR — single entry point
===================================================
Calls every voice for a target_date + mode, returns the structured prophecy.
Intended to be invoked from `dj_brain.cosmic_brain()` (lens #16) and from
the new `/api/cosmic-voices/{date}/{mode}?lens=all` endpoint.
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from year_d_ledger import (
    load_draws, parse_dt, quarter_of, current_quarter_stream, split_by_weekday,
)
from cosmic_voices.rc_detector import detect_rc_anchor
from cosmic_voices.climbing_voice import detect_climbing_voices
from cosmic_voices.sinking_voice import detect_sinking_voices
from cosmic_voices.gap_echo_97 import gap_echo_candidates
from cosmic_voices.star_product_door import star_product_door_candidates
from cosmic_voices.q_opening_melody import q_opening_melody
from cosmic_voices.internal_mirror import internal_mirror_scan
from cosmic_voices.stance_tracker import stance_tracker
from cosmic_voices.saturation_ledger import saturation_ledger
from cosmic_voices.convergence_scorer import convergence_scorer
from cosmic_voices.family_signature import family_signature_stats


def _quarter_draws_for(target_dt: datetime, draws: List[Dict], mode: str) -> List[Dict]:
    """Return draws of target's quarter+year (any weekday) BEFORE target_dt."""
    tq = quarter_of(target_dt, mode)
    return [d for d in draws if d["quarter"] == tq and d["year"] == target_dt.year
            and d["dt"] < target_dt]


def _opening_pair_for_quarter(quarter_draws: List[Dict]) -> Optional[Tuple[int, int]]:
    if not quarter_draws:
        return None
    sorted_q = sorted(quarter_draws, key=lambda x: x["dt"])
    first = sorted_q[0]
    if len(first["p"]) < 2:
        return None
    return (first["p"][0], first["p"][1])


async def run_cosmic_voices(
    target_date: str,
    mode: str = "euro",
    lens: str = "all",
    user_pins: Optional[List[int]] = None,
) -> Dict:
    """Execute every voice for the target_date. `lens="all"` returns full
    prophecy. Specific lens name returns only that voice.
    """
    mode = mode.lower().strip()
    if mode not in ("euro", "swiss"):
        return {"error": "mode must be 'euro' or 'swiss'"}

    target_dt = parse_dt(target_date)
    if not target_dt:
        return {"error": f"invalid target_date '{target_date}' (use dd.mm.yyyy)"}

    draws = await load_draws(mode)
    past = [d for d in draws if d["dt"] < target_dt]
    past.sort(key=lambda x: x["dt"])

    recent = past[-10:]  # last 10 draws regardless of weekday

    # BD = previous draw (overall); BD weekday is the target weekday's stream
    quarter_draws = _quarter_draws_for(target_dt, draws, mode)
    opening = _opening_pair_for_quarter(quarter_draws)

    # Each voice
    rc = detect_rc_anchor(target_dt, draws, mode)
    cv = detect_climbing_voices(recent, lookback=6)
    sv = detect_sinking_voices(recent, lookback=6)
    ge = gap_echo_candidates(recent, mode)
    bd_stars = recent[-1].get("stars") if (recent and mode == "euro") else None
    spd = star_product_door_candidates(bd_stars or [], mode) if bd_stars else {"available": False}
    qom = q_opening_melody(opening, quarter_draws) if opening else {"available": False}
    im = internal_mirror_scan(recent, lookback=10)
    st = stance_tracker(recent, mode, lookback=8)
    sat = saturation_ledger(recent, mode, window=5, threshold=3)
    fs = family_signature_stats(target_dt, draws, years_back=5) if mode == "euro" else None

    voices = {
        "rc_detector": rc,
        "climbing_voice": cv,
        "sinking_voice": sv,
        "gap_echo_97": ge,
        "star_product_door": spd,
        "q_opening_melody": qom,
        "internal_mirror": im,
        "stance_tracker": st,
        "saturation_ledger": sat,
        "family_signature": fs,
    }
    convergence = convergence_scorer(voices, mode=mode, user_pins=user_pins)
    voices["convergence_scorer"] = convergence

    # Filter to specific lens if requested
    if lens != "all" and lens in voices:
        return {
            "target_date": target_date,
            "mode": mode,
            "lens": lens,
            lens: voices[lens],
        }
    return {
        "target_date": target_date,
        "mode": mode,
        "lens": "all",
        "voices": voices,
    }
