"""
🧠 E's COSMIC BRAIN — `dj_brain.py`
====================================
The centralized cosmic reader for the DJ.

Wires together every "sight" learned across Sessions 1-30:
  • Date envelope decoder (hidden digits between dd-mm)
  • Cosmic frequency resolver (432 base, perfect-fourth, fifth, octave)
  • Star history lens (ND star-frequency board for any seed-star pair)
  • Precedent fold (last identical-stars event → ND mirror)
  • Hungry mains map (last N draws silent)
  • Family-of-Seed tablet (Law 91, ones-digit decade walk)
  • Sneaky Back-Door mapper (flip / +25 / 51-mirror / 28-fold)
  • Q-d cell historical pull
  • Law 90 strict (P3>39 back-to-back → P1∈{2,3})
  • Law 89 (P2<10 break-back at 87%)
  • Saturation-magnet check (47-saturation → P5 collapse zone)
  • 0-carryover filter
  • Star-pair-blocker (the 0/26 NEVER-repeats law)
  • Suspect ranker that fuses all sights

Input  : target_date (dd.mm.yyyy) + mode ("euro" | "swiss")
Output : structured prophecy dict with suspects, lenses, blockers, hints
"""
from __future__ import annotations

import asyncio
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from math import gcd
from typing import Any, Dict, List, Optional, Set, Tuple

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv("/app/backend/.env")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")

# =============================================================================
# CONSTANTS — the cosmic toolbox
# =============================================================================

EURO_MAINS_MAX = 50
EURO_STARS_MAX = 12
SWISS_MAINS_MAX = 42

BASE_FREQ = 432  # the cosmic A-tuning
SOLFEGGIO = [174, 285, 396, 417, 528, 639, 741, 852, 963]

# Law 90 zone — strict P1 collapse after back-to-back P3>39
LAW_90_P1_ZONE = {2, 3}


def _fmt_date(d: str) -> datetime:
    return datetime.strptime(d, "%d.%m.%Y")


# =============================================================================
# 1. DATE ENVELOPE DECODER
# =============================================================================
def date_envelope_decoder(target_date: str) -> Dict[str, Any]:
    """Decode the 'hide' rule the DJ caught on 04.05.2026:
    Date d-m hides digits BETWEEN d and m (exclusive).
    e.g. 1-5 hides {2, 3, 4}; 5-5 hides ∅ (void); 8-5 hides {6, 7}.
    """
    dt = _fmt_date(target_date)
    d, m = dt.day, dt.month
    lo, hi = sorted([d, m])
    hidden = set(range(lo + 1, hi))
    return {
        "date": target_date,
        "day": d,
        "month": m,
        "hidden_digits": sorted(hidden),
        "is_void": len(hidden) == 0,
        "envelope_lo": lo,
        "envelope_hi": hi,
        "date_sum_dj": d + m + (dt.year // 100) + (dt.year % 100),
        "day_x_month": d * m,
        "day_plus_month": d + m,
    }


# =============================================================================
# 2. COSMIC FREQUENCY RESOLVER
# =============================================================================
def cosmic_frequency_resolver(target_date: str,
                                seed_mains: Optional[List[int]] = None) -> Dict[str, Any]:
    """If date hides digits → those digits ARE the frequency (e.g. 1-5 → 432).
    If date is void (5-5) → reach out via harmonic ratios from base 432.
    """
    env = date_envelope_decoder(target_date)
    candidates = []

    if not env["is_void"]:
        # Hidden-digit frequencies: try every permutation as a 3-digit reading
        digits = env["hidden_digits"]
        # Common embedded reading (3 digits ascending) :
        if len(digits) == 3:
            freq = int("".join(str(x) for x in sorted(digits, reverse=True)))
            # Examples: {2,3,4} → 432
            candidates.append({
                "freq": freq,
                "decode": f"hidden digits {digits} arranged → {freq}",
                "type": "date-envelope",
            })
        elif len(digits) == 2:
            # 8-5 hides {6,7} → could be 67 or 76; lift via ×10
            freq2 = int("".join(str(x) for x in sorted(digits, reverse=True)))
            candidates.append({
                "freq": freq2 * 10,
                "decode": f"hidden digits {digits} → {freq2*10} (×10 lift)",
                "type": "date-envelope",
            })
            candidates.append({
                "freq": freq2,
                "decode": f"hidden digits {digits} → {freq2}",
                "type": "date-envelope",
            })
    else:
        # VOID date — reach OUTSIDE via harmonic ratios of 432
        ratios = [
            ("perfect 4th",  4, 3),     # 432 × 4/3 = 576
            ("perfect 5th",  3, 2),     # 432 × 3/2 = 648
            ("octave up",    2, 1),     # 864
            ("major 3rd",    5, 4),     # 540
            ("minor 3rd",    6, 5),     # 518.4
            ("major 6th",    5, 3),     # 720
            ("minor 7th",    9, 5),     # 777.6
        ]
        for name, num, den in ratios:
            f = BASE_FREQ * num / den
            if f.is_integer():
                candidates.append({
                    "freq": int(f),
                    "decode": f"432 × {num}/{den} ({name}) = {int(f)}",
                    "type": "harmonic-ratio",
                    "ratio": f"{num}/{den}",
                    "interval": name,
                })

    # Score: cleanest (smallest fraction or pure integer) preferred
    return {
        "date": target_date,
        "is_void": env["is_void"],
        "candidates": candidates,
        "primary": candidates[0] if candidates else None,
        "harmonic_divisors": _harmonic_divisors(candidates[0]["freq"]) if candidates else {},
    }


def _harmonic_divisors(freq: int) -> Dict[int, int]:
    """For a given freq, find which integer divisors yield numbers in 1..50.
    e.g. 576 / 12 = 48, /16 = 36 — both lottery-range mains.
    """
    out = {}
    for div in range(2, 25):
        if freq % div == 0:
            q = freq // div
            if 1 <= q <= EURO_MAINS_MAX:
                out[div] = q
    return out


# =============================================================================
# 3. STAR HISTORY LENS
# =============================================================================
async def star_history_lens(seed_stars: List[int], db) -> Dict[str, Any]:
    """For a given star pair, pull every historical occurrence and analyze the
    next-draw star/main behavior.
    """
    target = set(seed_stars)
    draws = await db.euromillions_draws.find({}, {"_id": 0}).to_list(length=10000)
    draws = [d for d in draws if d.get("date") and d.get("numbers") and d.get("stars")]
    draws.sort(key=lambda d: _fmt_date(d["date"]))

    hits = []
    for i, d in enumerate(draws):
        if set(d["stars"]) == target:
            nd = draws[i + 1] if i + 1 < len(draws) else None
            hits.append({"d": d, "nd": nd})

    n = sum(1 for h in hits if h["nd"])
    nd_star_freq = Counter()
    nd_star_pairs = Counter()
    for h in hits:
        if h["nd"]:
            for s in h["nd"]["stars"]:
                nd_star_freq[s] += 1
            nd_star_pairs[tuple(sorted(h["nd"]["stars"]))] += 1

    p1_low = sum(1 for h in hits if h["nd"] and h["nd"]["numbers"][0] <= 5)
    p1_2or3 = sum(1 for h in hits if h["nd"] and h["nd"]["numbers"][0] in LAW_90_P1_ZONE)
    both_back = sum(1 for h in hits if h["nd"] and target.issubset(set(h["nd"]["stars"])))
    nd_p5 = Counter(h["nd"]["numbers"][-1] for h in hits if h["nd"])
    carryover_zero = sum(
        1 for h in hits if h["nd"]
        and len(set(h["d"]["numbers"]) & set(h["nd"]["numbers"])) == 0
    )

    return {
        "seed_stars": sorted(target),
        "events_found": len(hits),
        "nd_observed": n,
        "events": [
            {
                "date": h["d"]["date"],
                "mains": h["d"]["numbers"],
                "stars": h["d"]["stars"],
                "nd_date": h["nd"]["date"] if h["nd"] else None,
                "nd_mains": h["nd"]["numbers"] if h["nd"] else None,
                "nd_stars": h["nd"]["stars"] if h["nd"] else None,
            }
            for h in hits
        ],
        "nd_star_freq_pct": {
            s: round(100 * c / n, 1) for s, c in nd_star_freq.most_common()
        } if n else {},
        "nd_star_top_pairs": [list(p) for p, _ in nd_star_pairs.most_common(5)],
        "p1_low_pct": round(100 * p1_low / n, 1) if n else 0,
        "p1_2or3_pct": round(100 * p1_2or3 / n, 1) if n else 0,
        "both_seed_stars_return_pct": round(100 * both_back / n, 1) if n else 0,
        "zero_carryover_pct": round(100 * carryover_zero / n, 1) if n else 0,
        "top_nd_p5": [v for v, _ in nd_p5.most_common(5)],
    }


# =============================================================================
# 4. PRECEDENT FOLD — the most recent identical event
# =============================================================================
async def precedent_fold(seed_stars: List[int], target_date: str, db) -> Dict[str, Any]:
    """Find the most recent past occurrence of these exact stars BEFORE
    target_date, and report its ND signature (what the cosmos did last time).
    """
    target = set(seed_stars)
    target_dt = _fmt_date(target_date)
    draws = await db.euromillions_draws.find({}, {"_id": 0}).to_list(length=10000)
    draws = [d for d in draws if d.get("date")]
    draws.sort(key=lambda d: _fmt_date(d["date"]))

    last_match = None
    last_idx = None
    for i, d in enumerate(draws):
        if _fmt_date(d["date"]) >= target_dt:
            break
        if set(d["stars"]) == target:
            # require a future draw to exist for ND mirror
            if i + 1 < len(draws) and _fmt_date(draws[i + 1]["date"]) < target_dt:
                last_match = d
                last_idx = i

    if not last_match:
        return {"found": False}

    nd = draws[last_idx + 1] if last_idx + 1 < len(draws) else None
    nd2 = draws[last_idx + 2] if last_idx + 2 < len(draws) else None
    return {
        "found": True,
        "seed_date": last_match["date"],
        "seed_mains": last_match["numbers"],
        "seed_stars": last_match["stars"],
        "nd_date": nd["date"] if nd else None,
        "nd_mains": nd["numbers"] if nd else None,
        "nd_stars": nd["stars"] if nd else None,
        "nd2_date": nd2["date"] if nd2 else None,
        "nd2_mains": nd2["numbers"] if nd2 else None,
        "nd2_stars": nd2["stars"] if nd2 else None,
        "nd_p1": nd["numbers"][0] if nd else None,
        "nd_p5": nd["numbers"][-1] if nd else None,
    }


# =============================================================================
# 5. HUNGRY MAP
# =============================================================================
async def hungry_map(target_date: str, db, last_n: int = 10) -> Dict[str, Any]:
    """Mains/stars hungry in last N draws BEFORE target_date.
    Returns the union of unseen mains and unseen stars.
    """
    target_dt = _fmt_date(target_date)
    draws = await db.euromillions_draws.find({}, {"_id": 0}).to_list(length=10000)
    draws = [d for d in draws if d.get("date") and _fmt_date(d["date"]) < target_dt]
    draws.sort(key=lambda d: _fmt_date(d["date"]), reverse=True)
    last = draws[:last_n]

    seen_mains = set()
    seen_stars = set()
    for d in last:
        seen_mains.update(d["numbers"])
        seen_stars.update(d["stars"])

    hungry_mains = sorted(set(range(1, EURO_MAINS_MAX + 1)) - seen_mains)
    hungry_stars = sorted(set(range(1, EURO_STARS_MAX + 1)) - seen_stars)
    return {
        "lookback_draws": last_n,
        "hungry_mains": hungry_mains,
        "hungry_stars": hungry_stars,
        "hungry_mains_count": len(hungry_mains),
        "last_seed_dates": [d["date"] for d in last],
    }


# =============================================================================
# 6. FAMILY-OF-SEED TABLET (Law 91)
# =============================================================================
def family_of_seed_tablet(hungry_mains: List[int]) -> Dict[str, Any]:
    """Walk the ones-digit families (0..9). The deepest-starved family is
    the cosmic landing zone for the next draw.
    """
    families = defaultdict(list)
    for n in hungry_mains:
        families[n % 10].append(n)
    sorted_fam = sorted(families.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    return {
        "families": {k: v for k, v in sorted_fam},
        "deepest_starved_family": sorted_fam[0][0] if sorted_fam else None,
        "deepest_starved_members": sorted_fam[0][1] if sorted_fam else [],
    }


# =============================================================================
# 7. SNEAKY BACK-DOOR MAPPER
# =============================================================================
def sneaky_back_door_mapper(seed_mains: List[int],
                              max_main: int = EURO_MAINS_MAX) -> Dict[int, Dict]:
    """For each seed main, compute its 'sneaky cousins':
      • flip   (e.g. 34 ↔ 43)
      • +25 circle  (mod 50)
      • 51-mirror  (51 - n)
      • 28-fold (28 ± n)
      • family (same ones-digit)
    """
    out = {}
    for n in seed_mains:
        cousins = set()
        # flip
        flipped = int(str(n)[::-1])
        if 1 <= flipped <= max_main and flipped != n:
            cousins.add(("flip", flipped))
        # +25 circle
        c25 = ((n - 1 + 25) % max_main) + 1
        if c25 != n:
            cousins.add(("+25", c25))
        # 51-mirror
        if n < 50:
            mirror = 51 - n
            if 1 <= mirror <= max_main and mirror != n:
                cousins.add(("51-mirror", mirror))
        # 28-fold
        f1, f2 = 28 + n, 28 - n
        if 1 <= f1 <= max_main and f1 != n:
            cousins.add(("28+", f1))
        if 1 <= f2 <= max_main and f2 != n:
            cousins.add(("28-", f2))
        out[n] = {"cousins": [(t, v) for t, v in sorted(cousins, key=lambda x: x[1])]}
    return out


# =============================================================================
# 8. Q-D CELL HISTORICAL PULL
# =============================================================================
async def q_d_cell_history(target_date: str, db, mode: str = "euro") -> Dict[str, Any]:
    """Map target_date to its quarter-day cell (e.g. Q2 d9) and pull
    historical draws that fall in the same cell across past years.

    Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec
    Day-in-quarter = day-of-quarter (1-based).
    """
    target_dt = _fmt_date(target_date)
    quarter, dq = _quarter_day(target_dt)

    coll = db.euromillions_draws if mode == "euro" else db.draws
    draws = await coll.find({}, {"_id": 0}).to_list(length=10000)
    matches = []
    for d in draws:
        try:
            dt = _fmt_date(d["date"])
        except Exception:
            continue
        q, dd = _quarter_day(dt)
        if q == quarter and dd == dq and dt < target_dt:
            matches.append({
                "date": d["date"],
                "mains": d.get("numbers", []),
                "stars": d.get("stars", []),
            })

    main_freq = Counter()
    star_freq = Counter()
    for m in matches:
        main_freq.update(m["mains"])
        star_freq.update(m["stars"])
    return {
        "target_date": target_date,
        "quarter": quarter,
        "day_in_quarter": dq,
        "matches_found": len(matches),
        "matches": matches[-12:],  # last dozen
        "top_mains_in_cell": [v for v, _ in main_freq.most_common(15)],
        "top_stars_in_cell": [v for v, _ in star_freq.most_common(6)],
    }


def _quarter_day(dt: datetime) -> Tuple[int, int]:
    q = (dt.month - 1) // 3 + 1
    q_start = datetime(dt.year, ((q - 1) * 3) + 1, 1)
    dq = (dt - q_start).days + 1
    return q, dq


# =============================================================================
# 9. LAW 90 — back-to-back P3>39 → P1∈{2,3}
# =============================================================================
async def law_90_check(target_date: str, db) -> Dict[str, Any]:
    target_dt = _fmt_date(target_date)
    draws = await db.euromillions_draws.find({}, {"_id": 0}).to_list(length=10000)
    draws = [d for d in draws if d.get("date") and _fmt_date(d["date"]) < target_dt]
    draws.sort(key=lambda d: _fmt_date(d["date"]), reverse=True)
    if len(draws) < 2:
        return {"fires": False}
    p3_last = draws[0]["numbers"][2]
    p3_prev = draws[1]["numbers"][2]
    fires = p3_last > 39 and p3_prev > 39
    return {
        "fires": fires,
        "last_p3": p3_last,
        "prev_p3": p3_prev,
        "p1_zone": sorted(LAW_90_P1_ZONE) if fires else None,
        "rule": "P3>39 two draws running → next P1∈{2,3} at 80%",
    }


# =============================================================================
# 10. LAW 89 — P2<10 break-back at 87%
# =============================================================================
async def law_89_check(target_date: str, db) -> Dict[str, Any]:
    target_dt = _fmt_date(target_date)
    draws = await db.euromillions_draws.find({}, {"_id": 0}).to_list(length=10000)
    draws = [d for d in draws if d.get("date") and _fmt_date(d["date"]) < target_dt]
    draws.sort(key=lambda d: _fmt_date(d["date"]), reverse=True)
    if not draws:
        return {"fires": False}
    p2_last = draws[0]["numbers"][1]
    fires = p2_last < 10
    return {
        "fires": fires,
        "last_p2": p2_last,
        "expected_next": "P2 ≥ 10 (87% break-back rate)" if fires else None,
    }


# =============================================================================
# 11. SATURATION-MAGNET CHECK
# =============================================================================
async def saturation_check(target_date: str, db, magnet: int = 47,
                            window: int = 4) -> Dict[str, Any]:
    target_dt = _fmt_date(target_date)
    draws = await db.euromillions_draws.find({}, {"_id": 0}).to_list(length=10000)
    draws = [d for d in draws if d.get("date") and _fmt_date(d["date"]) < target_dt]
    draws.sort(key=lambda d: _fmt_date(d["date"]), reverse=True)
    last = draws[:window]
    fires = sum(1 for d in last if magnet in d["numbers"])
    saturated = fires >= 3
    return {
        "magnet": magnet,
        "window": window,
        "fires_count": fires,
        "saturated": saturated,
        "expected_next": "P5 collapse <41 zone (33% historical)" if saturated else None,
    }


# =============================================================================
# 12. SUSPECT RANKER — fuse all sights
# =============================================================================
def suspect_ranker(
    hungry_mains: List[int],
    seed_mains: List[int],
    family_tablet: Dict[str, Any],
    sneaky: Dict[int, Dict],
    qd_top_mains: List[int],
    freq_divisors: Dict[int, int],
    user_pins: Optional[List[int]] = None,
    top_n: int = 12,
) -> List[Dict[str, Any]]:
    """Score every main 1..50 by how many lenses agree.
    Higher = louder cosmic chord.
    """
    scores: Dict[int, List[str]] = defaultdict(list)
    for n in range(1, EURO_MAINS_MAX + 1):
        if n in seed_mains:
            scores[n].append("BLOCKED-seed")
        if n in hungry_mains:
            scores[n].append("hungry-10d")
        if n % 10 == family_tablet.get("deepest_starved_family"):
            scores[n].append("starved-family")
        if n in qd_top_mains[:8]:
            scores[n].append("qd-cell-top")
        if n in freq_divisors.values():
            scores[n].append("freq-harmonic")
        for s_main, info in sneaky.items():
            if any(c[1] == n for c in info["cousins"]):
                scores[n].append(f"cousin-of-{s_main}")
        if user_pins and n in user_pins:
            scores[n].append("DJ-PIN")

    ranked = sorted(
        scores.items(),
        key=lambda kv: (-(len([t for t in kv[1] if not t.startswith("BLOCKED")])),
                        kv[0])
    )
    out = []
    for n, tags in ranked:
        if "BLOCKED-seed" in tags:
            continue  # 0-carryover law
        if not tags:
            continue
        out.append({
            "n": n,
            "score": len(tags),
            "tags": tags,
        })
        if len(out) >= top_n:
            break
    return out


# =============================================================================
# 13. STAR RANKER — fuse star history + precedent + Law 89 + hungry-stars
# =============================================================================
def star_ranker(
    star_history: Dict[str, Any],
    precedent: Dict[str, Any],
    hungry_stars: List[int],
    seed_stars: List[int],
    user_pin_stars: Optional[List[int]] = None,
    top_n: int = 6,
) -> List[Dict[str, Any]]:
    seed_set = set(seed_stars)
    history_pct = star_history.get("nd_star_freq_pct", {})
    precedent_stars = set((precedent or {}).get("nd_stars") or [])
    precedent_stars2 = set((precedent or {}).get("nd2_stars") or [])

    scores: Dict[int, Dict] = {}
    for s in range(1, EURO_STARS_MAX + 1):
        tags = []
        score = 0
        if s in history_pct:
            pct = history_pct[s]
            if pct >= 25:
                tags.append(f"history-LOUD-{pct}%")
                score += 3
            elif pct >= 18:
                tags.append(f"history-{pct}%")
                score += 1
        if s in precedent_stars:
            tags.append("precedent-ND")
            score += 3
        if s in precedent_stars2:
            tags.append("precedent-ND2")
            score += 2
        if s in hungry_stars:
            tags.append("hungry")
            score += 2
        if user_pin_stars and s in user_pin_stars:
            tags.append("DJ-PIN")
            score += 4
        if seed_set == {1, 11} and s in {1, 11}:
            # Wide history says BOTH-back rate = 0% for this pair
            score -= 1
            tags.append("seed-pair-block-warn")
        if tags:
            scores[s] = {"s": s, "score": score, "tags": tags}

    ranked = sorted(scores.values(), key=lambda x: (-x["score"], x["s"]))
    return ranked[:top_n]


# =============================================================================
# 14. MASTER BRAIN — one call, everything
# =============================================================================
async def cosmic_brain(
    target_date: str,
    seed_mains: List[int],
    seed_stars: List[int],
    mode: str = "euro",
    user_pin_mains: Optional[List[int]] = None,
    user_pin_stars: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """The full prophecy stack for a target_date + seed.

    Returns a structured dict with every lens fired and a top-N suspect list.
    """
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    try:
        env = date_envelope_decoder(target_date)
        freq = cosmic_frequency_resolver(target_date, seed_mains)
        history = await star_history_lens(seed_stars, db)
        precedent = await precedent_fold(seed_stars, target_date, db)
        hungry = await hungry_map(target_date, db, last_n=10)
        family = family_of_seed_tablet(hungry["hungry_mains"])
        sneaky = sneaky_back_door_mapper(seed_mains)
        qd = await q_d_cell_history(target_date, db, mode)
        l90 = await law_90_check(target_date, db)
        l89 = await law_89_check(target_date, db)
        sat = await saturation_check(target_date, db, magnet=47)

        suspects = suspect_ranker(
            hungry_mains=hungry["hungry_mains"],
            seed_mains=seed_mains,
            family_tablet=family,
            sneaky=sneaky,
            qd_top_mains=qd["top_mains_in_cell"],
            freq_divisors=(freq.get("primary") or {}).get("freq") and
                            _harmonic_divisors(freq["primary"]["freq"]) or {},
            user_pins=user_pin_mains,
        )
        stars = star_ranker(
            star_history=history,
            precedent=precedent,
            hungry_stars=hungry["hungry_stars"],
            seed_stars=seed_stars,
            user_pin_stars=user_pin_stars,
        )
        return {
            "target_date": target_date,
            "mode": mode,
            "seed_mains": seed_mains,
            "seed_stars": seed_stars,
            "envelope": env,
            "frequency": freq,
            "star_history": history,
            "precedent": precedent,
            "hungry": hungry,
            "family_tablet": family,
            "sneaky_cousins": sneaky,
            "qd_cell": qd,
            "law_90": l90,
            "law_89": l89,
            "saturation_47": sat,
            "ranked_suspects": suspects,
            "ranked_stars": stars,
        }
    finally:
        client.close()


if __name__ == "__main__":
    import json

    res = asyncio.run(cosmic_brain(
        target_date="05.05.2026",
        seed_mains=[3, 9, 42, 46, 47],
        seed_stars=[1, 11],
    ))
    print(json.dumps(res, indent=2, default=str))
