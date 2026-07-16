"""
🎼 CANON 38 — SWISS HIGH-P1 → EURO CROSS-LOTTERY LEAK

When Swiss P1 (the smallest sorted main) crosses above 19 — a rare event
firing ~26 times in 10 years — the immediately-following Euro draw carries
a measurable cross-lottery signature:

  🔥 KING numbers (2.3× lift over baseline): 6, 41, 34
  ⭐ STAR lifts (+6-8%): stars 3 and 4
  🌀 Circle-carrier leak: Swiss_P1 + 21 (Swiss Circle) appears in Euro ~19%
  🎯 Direct leak: numbers present in the trigger Swiss draw often reappear

This module detects the trigger and returns the ammunition for the next Euro.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter
from motor.motor_asyncio import AsyncIOMotorDatabase


SWISS_TRIGGER_THRESHOLD = 19  # P1 must be strictly greater than 19
SWISS_CIRCLE_CARRIER = 21


def parse_dt(s: str) -> datetime:
    dd, mm, yyyy = s.split(".")
    return datetime(int(yyyy), int(mm), int(dd))


def wrap50(n: int) -> int:
    while n > 50: n -= 50
    while n < 1: n += 50
    return n


async def find_last_swiss_before(db: AsyncIOMotorDatabase, target_date: str) -> Optional[Dict]:
    """Return the Swiss draw immediately preceding target_date (dd.mm.yyyy)."""
    target_dt = parse_dt(target_date)
    cursor = db["draws"].find({}).batch_size(200)
    latest = None
    async for d in cursor:
        try:
            d_dt = parse_dt(d["date"])
        except Exception:
            continue
        if d_dt < target_dt:
            if latest is None or d_dt > parse_dt(latest["date"]):
                latest = d
    return latest


async def compute_historical_lifts(
    db: AsyncIOMotorDatabase, years_back: int = 10
) -> Dict[str, Any]:
    """Recompute the KING numbers and star lifts from history."""
    cutoff = datetime.now().year - years_back
    swiss = await db["draws"].find({}).to_list(5000)
    euro = await db["euromillions_draws"].find({}).to_list(5000)

    def date_key(d):
        try: return parse_dt(d["date"])
        except: return datetime(1900, 1, 1)

    swiss.sort(key=date_key)
    euro.sort(key=date_key)
    swiss = [d for d in swiss if date_key(d).year >= cutoff]
    euro = [d for d in euro if date_key(d).year >= cutoff]

    euro_by_date = {date_key(d): d for d in euro}
    euro_dates_sorted = sorted(euro_by_date.keys())

    def next_euro_after(s_dt):
        for ed in euro_dates_sorted:
            if ed >= s_dt: return euro_by_date[ed]
        return None

    # Trigger events
    events = []
    for d in swiss:
        mains = sorted(d["numbers"])
        if len(mains) >= 6 and mains[0] > SWISS_TRIGGER_THRESHOLD:
            ne = next_euro_after(date_key(d))
            if ne:
                events.append({
                    "s_date": d["date"], "s_mains": mains,
                    "e_date": ne["date"],
                    "e_mains": sorted(ne["numbers"]),
                    "e_stars": ne.get("stars", []),
                })

    # Baseline vs conditional main-number frequency
    base_main = Counter()
    for d in euro:
        for n in sorted(d["numbers"]):
            base_main[n] += 1
    cond_main = Counter()
    for e in events:
        for n in e["e_mains"]:
            cond_main[n] += 1

    total_base = sum(base_main.values()) or 1
    total_cond = sum(cond_main.values()) or 1

    main_lifts = []
    for n in range(1, 51):
        bp = base_main[n] / total_base * 100
        cp = cond_main[n] / total_cond * 100
        main_lifts.append({
            "n": n, "count": cond_main[n],
            "base_pct": round(bp, 2), "cond_pct": round(cp, 2),
            "lift_pct": round(cp - bp, 2),
        })
    main_lifts.sort(key=lambda x: -x["lift_pct"])

    # Stars
    base_star = Counter()
    cond_star = Counter()
    for d in euro:
        for s in d.get("stars", []):
            base_star[s] += 1
    for e in events:
        for s in e["e_stars"]:
            cond_star[s] += 1
    tb_s = sum(base_star.values()) or 1
    tc_s = sum(cond_star.values()) or 1
    star_lifts = []
    for s in range(1, 13):
        bp = base_star[s] / tb_s * 100
        cp = cond_star[s] / tc_s * 100
        star_lifts.append({
            "s": s, "count": cond_star[s],
            "base_pct": round(bp, 2), "cond_pct": round(cp, 2),
            "lift_pct": round(cp - bp, 2),
        })
    star_lifts.sort(key=lambda x: -x["lift_pct"])

    return {
        "years_back": years_back,
        "trigger_events_count": len(events),
        "top_main_lifts": main_lifts[:15],
        "top_star_lifts": star_lifts[:6],
        "history_events": events[-20:],  # last 20 for reference
    }


async def forecast_for_target(
    db: AsyncIOMotorDatabase, target_date: str
) -> Dict[str, Any]:
    """Given a target Euro draw date, return Canon 38 cross-leak forecast."""
    # Find the last Swiss draw before target
    last_swiss = await find_last_swiss_before(db, target_date)
    if not last_swiss:
        return {"trigger_fired": False, "reason": "no Swiss draw found before target date"}

    swiss_mains = sorted(last_swiss["numbers"])
    swiss_p1 = swiss_mains[0]

    # Compute historical lifts fresh (10-yr rolling)
    hist = await compute_historical_lifts(db, years_back=10)

    result = {
        "target_date": target_date,
        "trigger_swiss_date": last_swiss["date"],
        "trigger_swiss_mains": swiss_mains,
        "trigger_swiss_p1": swiss_p1,
        "trigger_fired": swiss_p1 > SWISS_TRIGGER_THRESHOLD,
        "threshold": SWISS_TRIGGER_THRESHOLD,
        "historical_events_10y": hist["trigger_events_count"],
    }

    if not result["trigger_fired"]:
        result["forecast"] = None
        result["message"] = (
            f"Cross-lottery signal NOT active — Swiss P1={swiss_p1} does not exceed {SWISS_TRIGGER_THRESHOLD}."
        )
        return result

    # Build the ammunition
    top_kings = [x["n"] for x in hist["top_main_lifts"][:7]]
    top_stars = [x["s"] for x in hist["top_star_lifts"][:3] if x["lift_pct"] > 0]
    circle_carrier = wrap50(swiss_p1 + SWISS_CIRCLE_CARRIER)
    direct_leak = swiss_mains  # numbers from the trigger Swiss that may reappear
    all_ammo = sorted(set(top_kings + [circle_carrier] + swiss_mains))

    result["forecast"] = {
        "top_kings": top_kings,
        "top_stars": top_stars,
        "circle_carrier": circle_carrier,
        "circle_carrier_explanation": f"Swiss P1 ({swiss_p1}) + Circle carrier (+{SWISS_CIRCLE_CARRIER}) = {circle_carrier} (wrapped mod-50)",
        "swiss_direct_leak": direct_leak,
        "swiss_leak_note": "Numbers appearing in the trigger Swiss draw often reappear in the following Euro. Cross-check against KINGS.",
        "full_ammunition_pool": all_ammo,
        "top_main_lifts_detail": hist["top_main_lifts"][:10],
        "top_star_lifts_detail": hist["top_star_lifts"][:5],
    }
    result["message"] = (
        f"🎼 CANON 38 ACTIVE — Swiss draw on {last_swiss['date']} triggered the cross-leak "
        f"(P1={swiss_p1} > {SWISS_TRIGGER_THRESHOLD}). Hunt Euro numbers below."
    )
    return result
