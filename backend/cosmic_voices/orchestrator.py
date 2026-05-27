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
from cosmic_voices.frequency_carrier import frequency_carrier_scan
from cosmic_voices.silent_gap_walker import silent_gap_walker
from cosmic_voices.prime_family import prime_family_scan
from cosmic_voices.carrier_extensions import carrier_extensions
from cosmic_voices.mirror_neighbor import mirror_neighbor_expand
from cosmic_voices.rc_walks_encryption import compose_encryption_reading


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


def _detect_swiss_huge(past_draws: List[Dict]) -> Optional[Dict]:
    """Detect the most-recent Swiss HUGE (6-in-decade family-rare draw).
    A HUGE = 6 mains where 5+ share the same decade-family (30s, 20s, 10s, 0s).
    Returns dict with date/mains/lucky or None.
    """
    for d in sorted(past_draws, key=lambda x: x["dt"], reverse=True):
        mains = sorted(d.get("p", []))
        if len(mains) != 6:
            continue
        # decade-family: floor(n / 10) — 30s = 3, 20s = 2, etc.
        # 40-42 considered 30s-extension (4 with 0/1/2 fold-in)
        fams = []
        for n in mains:
            if 30 <= n <= 42:
                fams.append(3)
            elif 1 <= n <= 9:
                fams.append(0)
            else:
                fams.append(n // 10)
        from collections import Counter as _C
        top_count = _C(fams).most_common(1)[0][1]
        if top_count >= 5:
            return {
                "date": d["date"],
                "mains": mains,
                "lucky": d.get("lucky"),
                "stars": [d["lucky"]] if d.get("lucky") else [],
            }
    return None


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
    fc = frequency_carrier_scan(target_dt, recent) if mode == "euro" else None
    # Lens #12: feed deep-debt numbers from RC + melody for sneaky-gap projection
    deep_debt: list = []
    if rc and rc.get("mains"):
        deep_debt.extend(rc["mains"])
    if qom and qom.get("carrier_debts"):
        for cd in qom["carrier_debts"]:
            if cd.get("in_unpaid_pairs", 0) >= 2 and cd["n"] not in deep_debt:
                deep_debt.append(cd["n"])
    sgw = silent_gap_walker(recent, deep_debt_numbers=deep_debt) if mode == "euro" else None
    pf = prime_family_scan(recent) if mode == "euro" else None
    ce = carrier_extensions(deep_debt) if (mode == "euro" and deep_debt) else None

    # Lens #17 (Session 43 Euro / Session 44 Swiss) — RC-Walks Encryption Decoder
    rc_walks_enc = None
    if mode == "euro" and rc and rc.get("mains"):
        from year_d_ledger import parse_dt as _pd
        rc_dt = _pd(rc["date"])
        post_rc = [d for d in past if d["dt"] > rc_dt] if rc_dt else []
        rc_walks_enc = compose_encryption_reading(
            target_date=target_date, mode=mode, rc0=rc,
            all_quarter_draws=quarter_draws,
            recent_draws=recent,
            post_rc_draws=post_rc,
        )
    elif mode == "swiss":
        # HUGE anchor for Swiss = the family-rare 6-in-decade. Currently the
        # ONLY HUGE in history: 07.02.2026 [30, 33, 35, 36, 37, 38] 🍀6.
        # Build it from past draws (auto-detect: 6 mains in same decade-family).
        huge = _detect_swiss_huge(past)
        if huge:
            from year_d_ledger import parse_dt as _pd
            huge_dt = _pd(huge["date"])
            post_huge = [d for d in past if d["dt"] > huge_dt] if huge_dt else []
            rc_walks_enc = compose_encryption_reading(
                target_date=target_date, mode="swiss", rc0=huge,
                all_quarter_draws=quarter_draws,
                recent_draws=recent,
                post_rc_draws=post_huge,
            )

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
        "frequency_carrier": fc,
        "silent_gap_walker": sgw,
        "prime_family": pf,
        "carrier_extensions": ce,
        "rc_walks_encryption": rc_walks_enc,
    }
    convergence = convergence_scorer(voices, mode=mode, user_pins=user_pins)
    # Brain v0.1: mirror-neighbor expansion AFTER convergence
    if mode == "euro" and convergence.get("ranked_mains"):
        mn = mirror_neighbor_expand(convergence["ranked_mains"])
        convergence["mirror_neighbor"] = mn
        # Replace ranked_mains with expanded list (keeps original tags + neighbor tags)
        convergence["ranked_mains_expanded"] = mn["expanded_ranked"]
        convergence["shout_zone_expanded"] = mn["shout_expanded"]
        convergence["whisper_zone_expanded"] = mn["whisper_expanded"]
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
