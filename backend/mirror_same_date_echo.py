"""
🪞 Mirror-Date Same-Date Echo Analyzer

For tonight 02.06.2026 — find ALL "02.06" mirror precedents across history
and compute the inter-year cosmic grammar.

Special focus: 02.06.2020 (TRIPLE mirror M2+M3+M5) sat at Q2d18.
              02.06.2023 (M5 mirror) ALSO sat at Q2d18.
              → Same-d-position recurrence across mirror years.
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

    print("=" * 80)
    print("🪞 SAME-DATE ECHO — every 02.06 Euro draw in history")
    print("=" * 80)
    same_dm = [r for r in rows if r["dt"].day == 2 and r["dt"].month == 6]
    for r in same_dm:
        print(f"  {r['dt'].strftime('%d.%m.%Y')}  mains={r['mains']}  stars={r['stars']}")

    print()
    print("=" * 80)
    print("🔥 OVERLAP TALLY across all 02.06 draws")
    print("=" * 80)
    main_count = Counter()
    star_count = Counter()
    for r in same_dm:
        for n in r["mains"]:
            main_count[n] += 1
        for s in r["stars"]:
            star_count[s] += 1
    print("Mains repeating ≥2 times:")
    for n, c in sorted(main_count.items(), key=lambda x: (-x[1], x[0])):
        if c >= 2:
            print(f"  {n:>2}  fired {c}x")
    print("Stars repeating ≥2 times:")
    for s, c in sorted(star_count.items(), key=lambda x: (-x[1], x[0])):
        if c >= 2:
            print(f"  ⭐{s:>2}  fired {c}x")

    print()
    print("=" * 80)
    print("🎯 BD-29.05.2026 [5, 14, 18, 31, 35] ⭐(2, 12) vs 02.06 history")
    print("=" * 80)
    bd_mains = {5, 14, 18, 31, 35}
    bd_stars = {2, 12}
    for r in same_dm:
        ovrm = set(r["mains"]) & bd_mains
        ovrs = set(r["stars"]) & bd_stars
        # carrier discharge ±25
        carrier_hits = set()
        for m in r["mains"]:
            for b in bd_mains:
                if abs(m - b) == 25 or m == ((b + 25) % 50) or m == ((b - 25) % 50):
                    carrier_hits.add((m, b))
        # circle ±25 wrap including 50 = 0
        # mirror neighbor ±1, ±2
        neighbor_hits = set()
        for m in r["mains"]:
            for b in bd_mains:
                if abs(m - b) in (1, 2):
                    neighbor_hits.add((m, b))
        print(f"  {r['dt'].strftime('%d.%m.%Y')} → "
              f"raw_overlap_mains={sorted(ovrm)} "
              f"stars={sorted(ovrs)} "
              f"carrier(±25)={sorted(carrier_hits)} "
              f"neighbor(±1/2)={sorted(neighbor_hits)}")

    print()
    print("=" * 80)
    print("🎼 INTER-MIRROR-YEAR GRAMMAR — 02.06.2020 ↔ 02.06.2023 ↔ ...today 2026")
    print("=" * 80)
    # The "every 3 years" pattern (2020, 2023, 2026 = 3-yr arithmetic)
    triples = [
        (2020, 2023, 2026),
        (2014, 2017, 2020),
        (2011, 2014, 2017),
    ]
    for trio in triples:
        print(f"\n  Trio {trio}:")
        for y in trio:
            match = next((r for r in same_dm if r['dt'].year == y), None)
            if match:
                print(f"    02.06.{y}  mains={match['mains']}  stars={match['stars']}")
            elif y == 2026:
                print(f"    02.06.{y}  ← tonight (BD 29.05.26 [5,14,18,31,35] ⭐(2,12))")
            else:
                print(f"    02.06.{y}  — no draw found")

    print()
    print("=" * 80)
    print("✨ DIGIT-GRAMMAR — what digits 0,2,6 + year 26 do in each year's draw")
    print("=" * 80)
    for r in same_dm:
        digs_in_mains = []
        for m in r["mains"]:
            for d in str(m):
                digs_in_mains.append(d)
        c = Counter(digs_in_mains)
        focus = {d: c.get(d, 0) for d in "0246"}
        print(f"  {r['dt'].strftime('%d.%m.%Y')}  mains={r['mains']}  "
              f"digit-count(0,2,4,6)={focus}  total_mains_sum={sum(r['mains'])}")

    print()
    print("=" * 80)
    print("🌀 +25 CARRIER PROJECTION — apply +25/-25 to each historical 02.06 draw")
    print("=" * 80)
    for r in same_dm:
        carriers = []
        for m in r["mains"]:
            c1 = (m + 25 - 1) % 50 + 1  # +25 wrap inside 1-50
            c2 = (m - 25 - 1) % 50 + 1
            carriers.append((m, c1, c2))
        print(f"  {r['dt'].strftime('%d.%m.%Y')}  carriers (raw → +25 → -25): {carriers}")

    print()
    print("=" * 80)
    print("🎯 PURE-OPS POOL — apply Circle/Flip/Add to 02.06 history → check tonight")
    print("=" * 80)
    # For each historical 02.06 main, build its full op-fan:
    #   raw, +25 carrier, -25 carrier, digit-flip (10s↔1s swap), Swiss-circle (+21 mod 42 — not Euro but show)
    # Then intersect with BD 29.05.2026 to see what universe is replaying
    op_pool = defaultdict(set)  # target_num -> set of (year, source_num, op)
    for r in same_dm:
        if r["dt"].year >= 2026:
            continue
        for m in r["mains"]:
            ops = {
                "raw": m,
                "+25": ((m + 25 - 1) % 50) + 1,
                "-25": ((m - 25 - 1) % 50) + 1,
                "flip": int(str(m).zfill(2)[::-1]) if 1 <= int(str(m).zfill(2)[::-1]) <= 50 else None,
                "digit_sum": sum(int(d) for d in str(m)) if sum(int(d) for d in str(m)) <= 50 else None,
            }
            for op, target in ops.items():
                if target is not None and 1 <= target <= 50:
                    op_pool[target].add((r["dt"].year, m, op))

    # Rank candidates by appearance count
    ranked = sorted(op_pool.items(), key=lambda kv: -len(kv[1]))
    print("Top-25 numbers reachable via pure ops from past 02.06 mains:")
    for n, sources in ranked[:25]:
        srcs = list(sources)
        srcs.sort(key=lambda s: -s[0])
        sample = ", ".join(f"{y}.{m}/{o}" for y, m, o in srcs[:6])
        print(f"  n={n:>2}  ({len(sources):>2} paths)  {sample}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
