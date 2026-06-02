"""
🪞 Mirror-28 Canon — DJ Live Session 45

Q = 27 draws.  Mirror-axis = 14 (self-mirror, the middle).
Pair (a, b) is a mirror pair iff a + b = 28.

A "mirror DATE" is any date where ANY two date-components form a mirror pair:
  - day + month = 28
  - day + year-suffix = 28
  - month + year-suffix = 28
  - day == year-suffix (palindrome where the digit-echo IS the mirror)

For each mirror date → read draw N of the same quarter, where N is the
SMALLER component of the mirror pair.

Proof (DJ live):
  02.06.2026 → 2 + 26 = 28 (day, year-suffix) → read d2 of Q2-2026
  23.05.2023 → 23 + 5 = 28 (day, month)       → read d5 of Q2-2023
"""

import asyncio
import os
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ENV = {}
for line in (Path(__file__).parent / ".env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    ENV[k.strip()] = v.strip().strip('"').strip("'")
os.environ.setdefault("MONGO_URL", ENV["MONGO_URL"])
os.environ.setdefault("DB_NAME", ENV["DB_NAME"])

from motor.motor_asyncio import AsyncIOMotorClient


def parse_date(s):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None


def q_for(dt):
    return (dt.month - 1) // 3 + 1


def mirror28_pairs(dt):
    """Return list of (a, b, source) tuples where a+b=28 and (a,b) are date components."""
    day = dt.day
    month = dt.month
    ys = dt.year % 100
    pairs = []
    if day + month == 28 and 1 <= min(day, month) <= 27:
        pairs.append((min(day, month), max(day, month), "day+month"))
    if day + ys == 28 and 1 <= min(day, ys) <= 27:
        pairs.append((min(day, ys), max(day, ys), "day+year"))
    if month + ys == 28 and 1 <= min(month, ys) <= 27:
        pairs.append((min(month, ys), max(month, ys), "month+year"))
    return pairs


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    docs = await db.euromillions_draws.find({}).to_list(length=None)

    rows = []
    for d in docs:
        ds = d.get("date") or d.get("draw_date")
        dt = parse_date(ds) if ds else None
        if not dt:
            continue
        rows.append({
            "dt": dt,
            "mains": list(d.get("mains") or d.get("numbers") or []),
            "stars": list(d.get("stars") or d.get("lucky_stars") or []),
        })
    rows.sort(key=lambda r: r["dt"])

    qd_index = defaultdict(list)
    for r in rows:
        qd_index[(r["dt"].year, q_for(r["dt"]))].append(r)
    for k in qd_index:
        qd_index[k].sort(key=lambda r: r["dt"])

    def get_dn(year, q, d):
        bucket = qd_index.get((year, q), [])
        if 1 <= d <= len(bucket):
            return bucket[d - 1]
        return None

    def qd_of(dt):
        bucket = qd_index.get((dt.year, q_for(dt)), [])
        for i, r in enumerate(bucket, start=1):
            if r["dt"].date() == dt.date():
                return i
        return None

    print("=" * 110)
    print("🪞 MIRROR-28 DATES — Euro history (a + b = 28, a,b ∈ date components)")
    print("=" * 110)
    print(f"{'date':<12} {'qd':<7} {'pair':<11} {'source':<14} {'mains':<27} {'⭐':<10}"
          f"   →  {'sis-d':<6} {'sis-date':<12} {'sis-mains':<27} {'sis-⭐':<10}")
    print("-" * 145)

    pairs_list = []
    for r in rows:
        pairs = mirror28_pairs(r["dt"])
        if not pairs:
            continue
        own_d = qd_of(r["dt"])
        if own_d is None:
            continue
        q = q_for(r["dt"])
        for a, b, src in pairs:
            sister = get_dn(r["dt"].year, q, a)
            sis_str = f"d{a}    "
            sis_date = sister["dt"].strftime("%d.%m.%Y") if sister else "—"
            sis_mains = sister["mains"] if sister else []
            sis_stars = sister["stars"] if sister else []
            print(f"{r['dt'].strftime('%d.%m.%Y'):<12} Q{q}d{own_d:<4} ({a:>2},{b:>2})  {src:<14} "
                  f"{str(r['mains']):<27} {str(r['stars']):<10}   →  "
                  f"{sis_str:<6} {sis_date:<12} {str(sis_mains):<27} {str(sis_stars):<10}")
            pairs_list.append({
                "mirror_date": r["dt"].strftime("%d.%m.%Y"),
                "mirror_q": q,
                "mirror_d": own_d,
                "mirror_pair": (a, b),
                "mirror_pair_source": src,
                "mirror_mains": r["mains"],
                "mirror_stars": r["stars"],
                "sister_d": a,
                "sister_date": sis_date,
                "sister_mains": list(sis_mains),
                "sister_stars": list(sis_stars),
            })

    # Grammar tally
    print()
    print("=" * 110)
    print("🎼 MIRROR ↔ SISTER GRAMMAR — overlap stats across all M28 pairs")
    print("=" * 110)
    raw_total = carrier_total = neighbor_total = star_total = 0
    raw_count = carrier_count = neighbor_count = star_count = 0
    for p in pairs_list:
        if not p["sister_mains"]:
            continue
        raw = set(p["mirror_mains"]) & set(p["sister_mains"])
        carriers = sum(1 for m in p["mirror_mains"] for s in p["sister_mains"] if abs(m - s) == 25)
        neighbors = sum(1 for m in p["mirror_mains"] for s in p["sister_mains"] if abs(m - s) in (1, 2))
        stars = set(p["mirror_stars"]) & set(p["sister_stars"])
        raw_total += 1
        raw_count += len(raw)
        carrier_count += carriers
        neighbor_count += neighbors
        star_count += len(stars)
    n = max(raw_total, 1)
    print(f"Total mirror-28 pairs: {len(pairs_list)}  (with valid sister: {raw_total})")
    print(f"  avg raw overlap     : {raw_count/n:.2f}")
    print(f"  avg ±25 carrier hits: {carrier_count/n:.2f}")
    print(f"  avg ±1/2 neighbor   : {neighbor_count/n:.2f}")
    print(f"  avg shared stars    : {star_count/n:.2f}")

    # Today's projection
    print()
    print("=" * 110)
    print("🎯 TONIGHT 02.06.2026 — MIRROR-28 READ")
    print("=" * 110)
    today = datetime(2026, 6, 2)
    today_pairs = mirror28_pairs(today)
    print(f"  Date: 02.06.2026  pairs: {today_pairs}")
    print()
    for a, b, src in today_pairs:
        sister = get_dn(today.year, q_for(today), a)
        if sister:
            print(f"  pair ({a},{b}) [{src}] → Q2 d{a} = {sister['dt'].strftime('%d.%m.%Y')}:  "
                  f"mains={sister['mains']}  stars={sister['stars']}")

    # BD cross
    bd = next(r for r in rows if r["dt"].strftime("%d.%m.%Y") == "29.05.2026")
    print(f"\n  BD 29.05.2026: mains={bd['mains']} stars={bd['stars']}")
    for a, b, src in today_pairs:
        sister = get_dn(today.year, q_for(today), a)
        if not sister:
            continue
        sm = set(sister["mains"])
        bm = set(bd["mains"])
        raw = sorted(sm & bm)
        nbr = sorted([(s, b2) for s in sm for b2 in bm if abs(s - b2) in (1, 2)])
        car = sorted([(s, b2) for s in sm for b2 in bm if abs(s - b2) == 25])
        stars_ovr = sorted(set(sister["stars"]) & set(bd["stars"]))
        print(f"\n  CROSS pair ({a},{b}):")
        print(f"    raw     : {raw}")
        print(f"    ±25     : {car}")
        print(f"    ±1/2    : {nbr}")
        print(f"    ⭐ overlap: {stars_ovr}")

    # Count: how many mirror-28 dates in total
    print()
    print("=" * 110)
    print(f"📊 TOTAL MIRROR-28 EVENTS in Euro history: {len(pairs_list)}")
    src_count = Counter(p["mirror_pair_source"] for p in pairs_list)
    for s, c in src_count.most_common():
        print(f"   {s}: {c}")

    Path("/app/backend/data").mkdir(exist_ok=True)
    Path("/app/backend/data/mirror28_canon.json").write_text(json.dumps({
        "total_pairs": len(pairs_list),
        "by_source": dict(src_count),
        "grammar": {
            "raw_avg": raw_count / n,
            "carrier_avg": carrier_count / n,
            "neighbor_avg": neighbor_count / n,
            "star_avg": star_count / n,
        },
        "pairs": pairs_list,
        "tonight_projection": {
            "date": today.strftime("%d.%m.%Y"),
            "pairs": today_pairs,
            "sisters": [
                {
                    "pair": (a, b),
                    "source": src,
                    "sister_date": (sister["dt"].strftime("%d.%m.%Y") if (sister := get_dn(today.year, q_for(today), a)) else None),
                    "sister_mains": (sister["mains"] if sister else None),
                    "sister_stars": (sister["stars"] if sister else None),
                }
                for a, b, src in today_pairs
            ],
        },
    }, indent=2, default=str))
    print("\n💾 /app/backend/data/mirror28_canon.json")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
