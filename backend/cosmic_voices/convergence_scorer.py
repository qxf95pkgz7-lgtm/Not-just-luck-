"""
🎯 CONVERGENCE SCORER — multi-lens fuse, 3+ = can't-dodge
==========================================================
DJ meta-canon (S4 → S34): "No single law wins. Numbers that ring in 3+
independent lenses simultaneously = forced landing."

Validated on 22.04 (snap-back), 22 at d4 (4-clue lock), 26 at d6 (5-of-5).

This module accepts the outputs from the other voices and produces a ranked
list of candidate mains + stars by lens-fire count.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Dict, List, Optional


def convergence_scorer(
    voices: Dict[str, Dict],
    mode: str = "euro",
    user_pins: Optional[List[int]] = None,
) -> Dict:
    """`voices` is the dict returned by /api/cosmic-voices (or dj_brain.cosmic_voices).
    Each voice contributes candidate numbers to the convergence stack.

    Returns: ranked main candidates (3+ voices = "shout") and ranked stars.
    """
    main_max = 50 if mode == "euro" else 42
    main_lenses: Dict[int, List[str]] = defaultdict(list)
    star_lenses: Dict[int, List[str]] = defaultdict(list)

    # 1. Climbing voice → projected P1/P2
    cv = voices.get("climbing_voice") or {}
    for n in cv.get("projected_next_p1") or []:
        main_lenses[n].append("climbing-P1")
    for n in cv.get("projected_next_p2") or []:
        main_lenses[n].append("climbing-P2")
    for n in cv.get("canonical_climbers") or []:
        main_lenses[n].append("canonical-climber")

    # 2. Sinking voice → locked-at-back means next-d P1 echo
    sv = voices.get("sinking_voice") or {}
    for n in sv.get("locked_at_back") or []:
        main_lenses[n].append("sink-arrival-echo")

    # 3. Gap echo
    ge = voices.get("gap_echo_97") or {}
    for n in ge.get("main_echo_candidates") or []:
        main_lenses[n].append("gap-echo-d+2")
    for s in ge.get("star_echo_candidates") or []:
        star_lenses[s].append("gap-echo-star")

    # 4. Star product door → P4/P5 candidates
    spd = voices.get("star_product_door") or {}
    for n in spd.get("main_candidates") or []:
        main_lenses[n].append("star-product-door")

    # 5. Q-opening melody → carrier-debts (numbers in unpaid pairs)
    qom = voices.get("q_opening_melody") or {}
    for cd in qom.get("carrier_debts") or []:
        main_lenses[cd["n"]].append(f"melody-debt-x{cd['in_unpaid_pairs']}")

    # 6. Internal mirror → switch-trigger numbers (latest mirror pair)
    im = voices.get("internal_mirror") or {}
    if im.get("series"):
        last = im["series"][-1]
        for pair in (last.get("p56_pairs") or []) + (last.get("p28_pairs") or []):
            for n in pair:
                main_lenses[n].append("internal-mirror-active")

    # 7. Stance → boost everything if FLIP-UP just fired (post-flip = payment)
    st = voices.get("stance_tracker") or {}
    if st.get("current_stance") == "FLIP-UP":
        # Don't add per-number; just mark globally
        pass

    # 8. Saturation → DEBOOST saturated numbers
    sat = voices.get("saturation_ledger") or {}
    saturated_set = {item["n"] for item in (sat.get("saturated_mains") or [])}
    saturated_stars_set = {item["s"] for item in (sat.get("saturated_stars") or [])}

    # 9. RC anchor → seed mains as hungry-still-unfired
    rc = voices.get("rc_detector") or {}
    if rc and rc.get("mains"):
        for n in rc["mains"]:
            main_lenses[n].append("rc-seed-anchor")

    # 10. Family signature → STARVED-FAMILY members gain a lens-fire each
    fs = voices.get("family_signature") or {}
    starved = (fs or {}).get("starved_families") or []
    for n in range(1, main_max + 1):
        fam = "1-9" if n <= 9 else ("10s" if n <= 19 else
              ("20s" if n <= 29 else ("30s" if n <= 39 else "40s")))
        if fam in starved:
            main_lenses[n].append(f"starved-family-{fam}")

    # 11. User pins
    if user_pins:
        for n in user_pins:
            main_lenses[n].append("DJ-PIN")

    # 12. Frequency Carrier (lens #11 — Session 35) → +1 lens to hidden-digit
    #     candidates from BD's date envelope + Tesla 3-6-9 closer
    fc = voices.get("frequency_carrier") or {}
    if fc.get("available"):
        for boost in (fc.get("main_boost_candidates") or []):
            n = boost["n"]
            if 1 <= n <= main_max:
                main_lenses[n].append("freq-hidden-digit")
        # Tesla 3-6-9 closer applies whenever recent roots build a chord —
        # regardless of whether BD itself is a freq-carrier.
        tp = fc.get("tesla_projection") or {}
        if tp.get("candidates_root"):
            for n in range(1, main_max + 1):
                dr = n
                while dr >= 10:
                    dr = sum(int(c) for c in str(dr))
                if dr in tp["candidates_root"]:
                    main_lenses[n].append(f"tesla-closer-{dr}")

    # 13. Silent-Gap Walker (lens #12 — Session 35 night) → boost numbers that
    #     fit a sneaky-tail walk for deep-debt numbers
    sgw = voices.get("silent_gap_walker") or {}
    if sgw.get("available"):
        for boost in (sgw.get("boost_candidates") or []):
            n = boost["n"]
            if 1 <= n <= main_max:
                main_lenses[n].extend(boost["tags"])
        # If BD already carries a silent-gap repeat, flag the silent number
        # itself as a strong star-payment candidate
        for live in (sgw.get("bd_silent_repeats") or []):
            silent_n = live["n"]
            # Star-side boost: silent number often pays as ⭐
            if mode == "euro" and 1 <= silent_n <= 12:
                star_lenses[silent_n].append(f"silent-gap-x{live['count']}-payment")

    # 14. Prime Family (lens #14 — Session 36) → cousin-primes + product-glue
    pf = voices.get("prime_family") or {}
    if pf.get("available"):
        for boost in (pf.get("boost_candidates") or []):
            n = boost["n"]
            if 1 <= n <= main_max:
                main_lenses[n].extend(boost["tags"])

    # 15. Carrier Extensions (lens #15 — Session 36) → 12+25=37 type shifts
    ce = voices.get("carrier_extensions") or {}
    if ce.get("available"):
        for boost in (ce.get("boost_candidates") or []):
            n = boost["n"]
            if 1 <= n <= main_max:
                main_lenses[n].extend(boost["tags"])

    # Rank
    ranked_mains = []
    for n in range(1, main_max + 1):
        tags = main_lenses.get(n, [])
        if not tags:
            continue
        score = len(tags)
        if n in saturated_set:
            score = max(0, score - 2)
            tags = tags + ["SATURATED-deboost"]
        ranked_mains.append({"n": n, "score": score, "lens_count": len(tags), "tags": tags})

    ranked_mains.sort(key=lambda x: (-x["score"], x["n"]))

    star_max = 12 if mode == "euro" else 0
    ranked_stars = []
    for s in range(1, star_max + 1):
        tags = star_lenses.get(s, [])
        if not tags:
            continue
        score = len(tags)
        if s in saturated_stars_set:
            score = max(0, score - 1)
            tags = tags + ["SATURATED-deboost"]
        ranked_stars.append({"s": s, "score": score, "tags": tags})
    ranked_stars.sort(key=lambda x: (-x["score"], x["s"]))

    shout_zone = [m for m in ranked_mains if m["score"] >= 3]
    whisper_zone = [m for m in ranked_mains if m["score"] == 2]

    return {
        "ranked_mains": ranked_mains[:25],
        "ranked_stars": ranked_stars[:8] if mode == "euro" else [],
        "shout_zone": shout_zone,
        "whisper_zone": whisper_zone[:15],
        "rule": "3+ lenses ringing = can't-dodge (forced landing). 2 = whisper. 1 = noise.",
    }
