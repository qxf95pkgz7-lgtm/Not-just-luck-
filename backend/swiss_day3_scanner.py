"""
Swiss Day=3 — every historical Swiss draw on day=3 of any month
with the BD (previous draw) for clue mining.

Tomorrow Wed 03.06.2026 is day=3 — look for grammar.
"""

import asyncio
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

ENV = {}
for line in Path("/app/backend/.env").read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        ENV[k.strip()] = v.strip().strip('"')
os.environ.setdefault("MONGO_URL", ENV["MONGO_URL"])
os.environ.setdefault("DB_NAME", ENV["DB_NAME"])
from motor.motor_asyncio import AsyncIOMotorClient


async def main():
    cli = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = cli[os.environ["DB_NAME"]]
    docs = await db.draws.find({}).to_list(length=None)
    rows = []
    for d in docs:
        try:
            dt = datetime.strptime(d.get("date", ""), "%d.%m.%Y")
            m = sorted(d.get("numbers") or [])
            if len(m) == 6:
                rows.append({"dt": dt, "mains": m, "lucky": d.get("lucky_number"), "replay": d.get("replay_number")})
        except Exception:
            pass
    rows.sort(key=lambda r: r["dt"])

    day3 = [(i, r) for i, r in enumerate(rows) if r["dt"].day == 3]
    print(f"📊 Total Swiss day=3 draws: {len(day3)}\n")
    print("=" * 110)
    print("🎯 EVERY Swiss day=3 + BD pair")
    print("=" * 110)
    print(f"{'BD':<13} {'BD-mains':<28} {'BD🍀':<6} → {'ND (day=3)':<13} {'ND-mains':<28} {'ND🍀':<6}")
    print("-" * 110)

    pairs = []
    nd_main = Counter()
    nd_star_lucky = Counter()
    bd_carrier_match = 0  # times ND_P1 = 43 - BD_P6 (22-bridge)
    p5_walk_match = 0    # times BD_P5 + ND_P5 within ±2 of K
    p6_year_cap = 0       # times ND_P6 = 40 (year-cap)
    same_month = 0       # ND day=3 + BD same month
    cross_month = 0      # cross-month

    for i, r in day3:
        if i == 0:
            continue
        bd = rows[i - 1]
        same_mo = bd["dt"].month == r["dt"].month
        if same_mo:
            same_month += 1
        else:
            cross_month += 1
        if 43 - bd["mains"][5] == r["mains"][0]:
            bd_carrier_match += 1
        if r["mains"][5] == 40:
            p6_year_cap += 1
        # K = (bd_day + nd_day) + (yp + month_NEW)
        K = (bd["dt"].day + r["dt"].day) + (bd["dt"].year // 100 + r["dt"].month)
        if abs((bd["mains"][4] + r["mains"][4]) - K) <= 2:
            p5_walk_match += 1
        print(f"  {bd['dt'].strftime('%d.%m.%Y'):<13} {str(bd['mains']):<28} 🍀{str(bd['lucky']):<3} → "
              f"{r['dt'].strftime('%d.%m.%Y'):<13} {str(r['mains']):<28} 🍀{str(r['lucky']):<3}")
        for n in r["mains"]:
            nd_main[n] += 1
        if r["lucky"] is not None:
            nd_star_lucky[r["lucky"]] += 1
        pairs.append((bd, r))

    N = len(pairs)
    print()
    print("=" * 110)
    print(f"📊 Day=3 NDs: {N} cases")
    print(f"  same-month (BD also same month): {same_month}")
    print(f"  cross-month (BD in prev month) : {cross_month}")
    print()
    print("Top 15 mains across day=3 NDs:")
    for n, c in nd_main.most_common(15):
        print(f"   n={n:>2}  ×{c:>2}  ({100*c/max(1,N):.1f}%)")
    print()
    print("🍀 distribution on day=3 NDs:")
    for lk, c in sorted(nd_star_lucky.items()):
        print(f"   🍀{lk}  ×{c}  ({100*c/max(1,N):.1f}%)")
    print()
    print(f"📐 22-Bridge (ND_P1 = 43 - BD_P6) hits: {bd_carrier_match}/{N}  ({100*bd_carrier_match/max(1,N):.1f}%)")
    print(f"📐 P6=40 year-cap hits:                  {p6_year_cap}/{N}  ({100*p6_year_cap/max(1,N):.1f}%)")
    print(f"📐 P5-walk (±2 of canon K):              {p5_walk_match}/{N}  ({100*p5_walk_match/max(1,N):.1f}%)")

    # Filter: cross-month day=3 only (matches tomorrow's situation)
    print()
    print("=" * 110)
    print("🎯 CROSS-MONTH DAY=3 ONLY (tomorrow matches this template)")
    print("=" * 110)
    cross_pairs = [(b, r) for b, r in pairs if b["dt"].month != r["dt"].month]
    print(f"Cross-month cases: {len(cross_pairs)}\n")
    nd_main_cross = Counter()
    p1_cross = Counter()
    p6_cross = Counter()
    p5_cross = Counter()
    p2_cross = Counter()
    p3_cross = Counter()
    p4_cross = Counter()
    for bd, r in cross_pairs:
        for n in r["mains"]:
            nd_main_cross[n] += 1
        p1_cross[r["mains"][0]] += 1
        p2_cross[r["mains"][1]] += 1
        p3_cross[r["mains"][2]] += 1
        p4_cross[r["mains"][3]] += 1
        p5_cross[r["mains"][4]] += 1
        p6_cross[r["mains"][5]] += 1
    print("Top-15 mains:")
    for n, c in nd_main_cross.most_common(15):
        print(f"   n={n:>2}  ×{c:>2}  ({100*c/max(1,len(cross_pairs)):.1f}%)")
    print()
    print("P1 distribution:")
    for v, c in sorted(p1_cross.items())[:20]:
        bar = "█" * c
        print(f"   P1={v:>2}  ×{c}  {bar}")
    print()
    print("P6 distribution:")
    for v, c in sorted(p6_cross.items())[-15:]:
        bar = "█" * c
        print(f"   P6={v:>2}  ×{c}  {bar}")

    cli.close()


if __name__ == "__main__":
    asyncio.run(main())
