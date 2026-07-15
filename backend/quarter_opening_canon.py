"""
🎻 QUARTER OPENING CANON — Canon 34 (DJ-taught 09.06.2026, from The Book)
=========================================================================

Q anchors are DJ-defined, not calendar quarters. Set from The Book:

    Q1 opens on 01.03.2026
    Q2 opens on 08.04.2026
    Q3 opens on 11.07.2026
    (Q4 pending)

The FIRST Swiss draw on-or-after each Q anchor is the "Q opener".
Its mains DANCE with the anchor date via the One Law (Swiss +21):

    day               ± carrier   (e.g. day 8  → 29)
    month             ± carrier   (e.g. month 7 → 28)
    day.month flat    carrier-back until in universe (e.g. 84 → 21)
    day×month         carrier-back (e.g. 77 → 35)
    date digit-sum    (e.g. 0+8+0+4+2+0+2+6 = 22)

Verified matches:
    Q2 opener (08.04 → [2,9,21,22,26,35]):  84→21 ✅  digit-sum 22 ✅
    Q3 opener (11.07 → [2,3,21,23,28,35]): month+21=28 ✅  day×month→35 ✅

Second law (history-echo): if a subset of mains from a Q-opener also appeared
together in a PAST draw, look at what came AFTER that past draw — same P1/P2/P6
often echo forward.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Set
from datetime import datetime


QUARTER_ANCHORS = {
    "Q1_2026": "01.03.2026",
    "Q2_2026": "08.04.2026",
    "Q3_2026": "11.07.2026",
}


def _wrap_carrier_back(n: int, carrier: int, max_n: int) -> int:
    while n > max_n:
        n -= carrier
    while n < 1:
        n += carrier
    return n


def compute_dance_seeds(date_str: str, mode: str = "swiss") -> Dict[str, int]:
    """Compute all date-derived cosmic seeds for a Q-opener date."""
    dd, mm, yy = date_str.split(".")
    d, m, y = int(dd), int(mm), int(yy)
    carrier = 21 if mode == "swiss" else 25
    max_n = 42 if mode == "swiss" else 50
    ddmm = int(f"{dd}{mm}")
    dxm = d * m
    ds = sum(int(c) for c in date_str.replace(".", ""))
    return {
        "day": _wrap_carrier_back(d, carrier, max_n),
        "day+carrier": _wrap_carrier_back(d + carrier, carrier, max_n),
        "month": _wrap_carrier_back(m, carrier, max_n),
        "month+carrier": _wrap_carrier_back(m + carrier, carrier, max_n),
        "day.month→carrier-back": _wrap_carrier_back(ddmm, carrier, max_n),
        "day×month→carrier-back": _wrap_carrier_back(dxm, carrier, max_n),
        "date-digit-sum": _wrap_carrier_back(ds, carrier, max_n),
    }


def find_dancers(date_str: str, mains: List[int], mode: str = "swiss") -> Dict:
    """Return the seeds that LANDED in the draw = the dancers."""
    seeds = compute_dance_seeds(date_str, mode)
    mains_set = set(mains)
    dancers = {label: v for label, v in seeds.items() if v in mains_set}
    return {
        "date": date_str,
        "mode": mode,
        "mains": sorted(mains),
        "seeds": seeds,
        "dancers": dancers,
        "dancer_count": len(dancers),
    }


async def find_q_opener_in_db(db, anchor_date: str, mode: str = "swiss") -> Optional[Dict]:
    """First draw on-or-after anchor_date. mode=swiss uses `draws`,
    euro would use `euromillions_draws`."""
    coll = db.draws if mode == "swiss" else db.euromillions_draws
    anchor_dt = datetime.strptime(anchor_date, "%d.%m.%Y")
    all_docs = await coll.find({}, {"_id": 0}).to_list(5000)
    candidates = []
    for d in all_docs:
        try:
            dt = datetime.strptime(d["date"], "%d.%m.%Y")
        except (KeyError, ValueError):
            continue
        if dt >= anchor_dt:
            candidates.append((dt, d))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    _, opener = candidates[0]
    return opener


async def history_echo(db, subset: List[int], mode: str = "swiss",
                        exclude_dates: Optional[Set[str]] = None) -> List[Dict]:
    """Find every past draw where ALL numbers in `subset` appeared together.
    Return each match with the NEXT draw's mains (what came after)."""
    coll = db.draws if mode == "swiss" else db.euromillions_draws
    all_docs = await coll.find({}, {"_id": 0}).to_list(5000)
    all_docs.sort(key=lambda d: datetime.strptime(d["date"], "%d.%m.%Y"))
    subset_s = set(subset)
    exclude = exclude_dates or set()
    matches = []
    for i, d in enumerate(all_docs):
        if d.get("date") in exclude:
            continue
        mains = set(d.get("numbers", []))
        if subset_s.issubset(mains):
            nxt = all_docs[i + 1] if i + 1 < len(all_docs) else None
            matches.append({
                "date": d["date"],
                "mains": sorted(d.get("numbers", [])),
                "next_date": nxt["date"] if nxt else None,
                "next_mains": sorted(nxt.get("numbers", [])) if nxt else None,
                "p1_p2_p6_next": (
                    (sorted(nxt.get("numbers", []))[0],
                     sorted(nxt.get("numbers", []))[1],
                     sorted(nxt.get("numbers", []))[-1]) if nxt and len(nxt.get("numbers", [])) >= 6 else None
                ),
            })
    return matches


async def analyze_quarter_opener(db, q_id: str, mode: str = "swiss") -> Dict:
    """End-to-end: pull the Q opener from DB, run dance analysis + history echo
    on 3-main subsets to see if any prior draw shared 3+ numbers."""
    if q_id not in QUARTER_ANCHORS:
        return {"error": f"Unknown quarter {q_id}. Known: {list(QUARTER_ANCHORS.keys())}"}
    anchor = QUARTER_ANCHORS[q_id]
    opener = await find_q_opener_in_db(db, anchor, mode)
    if not opener:
        return {"error": f"No draw found on/after {anchor}"}
    mains = sorted(opener.get("numbers", []))
    dance = find_dancers(opener["date"], mains, mode)
    # History echo — check all 3-number subsets that INCLUDE at least one dancer
    from itertools import combinations
    dancers = list(dance["dancers"].values())
    echoes = []
    if dancers and len(mains) >= 3:
        seen_subsets = set()
        for subset in combinations(mains, 3):
            # Require the subset to intersect the dancers OR just top-3 subset
            if not (set(subset) & set(dancers)):
                continue
            key = tuple(sorted(subset))
            if key in seen_subsets:
                continue
            seen_subsets.add(key)
            hits = await history_echo(db, list(subset), mode, exclude_dates={opener["date"]})
            if hits:
                echoes.append({"subset": list(subset), "matches": hits[:5]})
    return {
        "quarter": q_id,
        "anchor": anchor,
        "opener": {"date": opener["date"], "mains": mains, "lucky": opener.get("luckyNumbers", opener.get("lucky", []))},
        "dance": dance,
        "history_echoes": echoes,
    }
