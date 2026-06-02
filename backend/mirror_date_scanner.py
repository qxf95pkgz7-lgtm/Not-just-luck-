"""
🪞 Mirror-Date Scanner — Session 45 Canon Builder

Scans full Euro draw history for "mirror-date" patterns and reports
the draws + their same-quarter d-neighbours so the DJ can hear the
universe's mirror-grammar.

A "mirror date" is any draw date D-M-Y where the date itself carries
an internal palindrome/echo. We test 7 mirror predicates:

  M1 day == year-suffix          (23.05.2023 — DJ canonical example)
  M2 day == year-suffix flipped  (32.MM.2023 → impossible; 41.MM.2014 → also)
                                  practically: reverse(year-suffix) == day
                                  e.g. 32.MM.2023 — day 32 invalid, but
                                       21.MM.2012 → reverse(12)=21 ✓
  M3 day-flipped == year-suffix  (14.MM.2041 etc; 21.MM.2012 same as M2 mirror)
  M4 day == month*2              (02.06.2026 — DJ's tonight: day=2, day×... no)
                                  → DJ tonight 02.06 → 2 fits 26 via doubling 13
                                  practical interpretation: day appears INSIDE
                                  year-suffix digits  (day=2, year-suffix=26 → 2 in '26' ✓)
  M5 day in year-suffix digits   (the 02.06.2026 case)
  M6 year-suffix in date-pair    (year 26 appears as month=06 doubled? skip)
                                  PRACTICAL: month == half of year-suffix
                                            06 mirrors 26 if interpreted as 6 ↔ 6 of 26?
                                  We code: month_2digit_in (year-suffix as string)
  M7 palindrome whole date       e.g. 02.02.2020, 12.02.2021 reversed 1202.2021

We then for each mirror-date:
  - record its q-d position (which q + which draw-index inside that q)
  - sweep all OTHER draws in the same quarter
  - find which neighbor draws share P3 axis (same P3 ±0) OR same star pair

The output is The Book grammar.
"""

import asyncio
import os
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Load env directly
ENV = {}
for line in (Path(__file__).parent / ".env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    ENV[k.strip()] = v.strip().strip('"').strip("'")

os.environ.setdefault("MONGO_URL", ENV.get("MONGO_URL", "mongodb://localhost:27017"))
os.environ.setdefault("DB_NAME", ENV.get("DB_NAME", "test_database"))

from motor.motor_asyncio import AsyncIOMotorClient


def parse_date(s: str):
    """Try multiple formats — returns datetime or None."""
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None


def is_mirror_date(dt: datetime):
    """Return list of mirror predicates this date satisfies."""
    day = dt.day
    month = dt.month
    year = dt.year
    ys = year % 100  # year-suffix
    day_s = f"{day:02d}"
    ys_s = f"{ys:02d}"
    flip_day = int(day_s[::-1])
    flip_ys = int(ys_s[::-1])

    fires = []

    if day == ys:
        fires.append(("M1", f"day({day})==year-suffix({ys})"))
    if day == flip_ys:
        fires.append(("M2", f"day({day})==flip(year-suffix)({flip_ys})"))
    if flip_day == ys and day != ys:
        fires.append(("M3", f"flip(day)({flip_day})==year-suffix({ys})"))
    if month == ys:
        fires.append(("M4", f"month({month})==year-suffix({ys})"))
    if day_s in ys_s and len(day_s) == 2 and day > 0:
        # day's whole 2-digit string is substring of year-suffix
        fires.append(("M5d", f"day-string({day_s}) ⊂ year-suffix({ys_s})"))
    # Single-digit echo: tonight's 02.06.2026 case
    # day=02, year-suffix=26. day's ones-digit (2) appears in year-suffix.
    if 1 <= day <= 9 and str(day) in ys_s:
        fires.append(("M5", f"day-digit({day}) inside year-suffix({ys_s})"))
    if month == day:
        fires.append(("M6", f"month==day=({month}) — twin date"))
    # Palindrome: full ddmmyyyy reversed == itself
    full = f"{day:02d}{month:02d}{year:04d}"
    if full == full[::-1]:
        fires.append(("M7", f"full date palindrome {full}"))

    return fires


# Euro Q-d position per The Book canon
# Q1 d1 = 1st Tue of the year
# Q2 d1 = 1st Tue after April transition (typically ~04.04 or ~07.04)
# Q3 d1 = 1st Tue of July
# Q4 d1 = 1st Tue of October
# Simplified: quarter = ceil(month/3); d-position is rank inside that quarter

def q_for(dt: datetime) -> int:
    return (dt.month - 1) // 3 + 1


def get_qd(dt: datetime, all_dates_sorted_in_year: dict):
    """Given a date and a precomputed map year→quarter→[sorted_dates],
    return (q, d_index) where d_index is 1-based position in that quarter."""
    q = q_for(dt)
    bucket = all_dates_sorted_in_year.get((dt.year, q), [])
    for i, d in enumerate(bucket, start=1):
        if d.date() == dt.date():
            return q, i
    return q, None


async def run_scan():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    docs = await db.euromillions_draws.find({}).to_list(length=None)
    print(f"📦 Loaded {len(docs)} Euro draws from DB\n")

    # Normalize
    rows = []
    for d in docs:
        date_str = d.get("date") or d.get("draw_date") or d.get("Date")
        if not date_str:
            continue
        dt = parse_date(date_str)
        if not dt:
            continue
        mains = d.get("mains") or d.get("numbers") or d.get("main_numbers") or []
        stars = d.get("stars") or d.get("lucky_stars") or []
        rows.append({"dt": dt, "mains": list(mains), "stars": list(stars)})

    rows.sort(key=lambda x: x["dt"])
    print(f"✅ Parsed {len(rows)} draws ({rows[0]['dt'].date()} → {rows[-1]['dt'].date()})\n")

    # Build year+q → [sorted dates] map for qd lookup
    qd_map = defaultdict(list)
    for r in rows:
        qd_map[(r["dt"].year, q_for(r["dt"]))].append(r["dt"])
    for k in qd_map:
        qd_map[k].sort()

    # Scan mirror dates
    mirrors = []
    for r in rows:
        fires = is_mirror_date(r["dt"])
        if fires:
            q, di = get_qd(r["dt"], qd_map)
            mirrors.append({
                "date": r["dt"].strftime("%d.%m.%Y"),
                "year": r["dt"].year,
                "q": q,
                "d": di,
                "mains": r["mains"],
                "stars": r["stars"],
                "fires": [{"code": c, "desc": d} for c, d in fires],
            })

    print(f"🪞 Found {len(mirrors)} mirror-date Euro draws\n")

    # Group by mirror-code
    by_code = defaultdict(list)
    for m in mirrors:
        for f in m["fires"]:
            by_code[f["code"]].append(m)

    print("=" * 80)
    print("MIRROR-CODE TALLY")
    print("=" * 80)
    for code in sorted(by_code.keys()):
        print(f"  {code}: {len(by_code[code])} draws")
    print()

    # Show strong mirrors (M1, M2, M3, M7)
    strong_codes = {"M1", "M2", "M3", "M7"}
    print("=" * 80)
    print("🔥 STRONG MIRROR DATES (M1/M2/M3/M7)")
    print("=" * 80)
    seen = set()
    strong_list = []
    for m in mirrors:
        codes = {f["code"] for f in m["fires"]}
        if codes & strong_codes and m["date"] not in seen:
            seen.add(m["date"])
            strong_list.append(m)

    for m in strong_list:
        codes = "+".join(sorted(f["code"] for f in m["fires"]))
        mains = m["mains"]
        stars = m["stars"]
        p3 = mains[2] if len(mains) >= 3 else None
        print(f"  {m['date']}  Q{m['q']}d{m['d']:>2}  {codes:>10}  "
              f"mains={mains}  stars={stars}  P3={p3}")

    print()
    print("=" * 80)
    print("🎯 TONIGHT 02.06.2026 — same mirror-code precedents:")
    print("=" * 80)
    today_fires = is_mirror_date(datetime(2026, 6, 2))
    today_codes = [c for c, _ in today_fires]
    print(f"  Today fires: {today_fires}\n")

    sister = [m for m in mirrors
              if set(f["code"] for f in m["fires"]) & set(today_codes)]
    for m in sister[-25:]:
        codes = "+".join(sorted(f["code"] for f in m["fires"]))
        print(f"  {m['date']}  Q{m['q']}d{m['d']}  {codes:>8}  "
              f"mains={m['mains']}  stars={m['stars']}")

    # Save to JSON for further analysis
    out = {
        "scan_date": datetime.utcnow().isoformat(),
        "total_draws": len(rows),
        "mirror_count": len(mirrors),
        "by_code": {k: len(v) for k, v in by_code.items()},
        "strong_mirrors": strong_list,
        "today_fires": today_fires,
        "today_sisters": sister,
        "all_mirrors": mirrors,
    }
    Path("/app/backend/data").mkdir(exist_ok=True)
    Path("/app/backend/data/mirror_date_scan.json").write_text(json.dumps(out, indent=2, default=str))
    print(f"\n💾 Saved /app/backend/data/mirror_date_scan.json")

    client.close()


if __name__ == "__main__":
    asyncio.run(run_scan())
