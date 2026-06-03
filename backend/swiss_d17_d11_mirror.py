"""
Swiss Day=17 + Day=11 — Mirror-Pair Day Analysis
(Session 45 DJ canon: d17 + d11 = 28, the mirror-axis)

For each: scan all historical Swiss draws, look at:
  - mains tally + position bands
  - BD pair (the draw before)
  - ND pair (the draw after)
  - Swiss-circle carriers: 17 ↔ 38, 11 ↔ 32
  - cross-pattern between day=17 and day=11 (mirror pair)
"""

import asyncio
import os
from collections import Counter, defaultdict
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

    def analyze(target_day, name):
        days = [(i, r) for i, r in enumerate(rows) if r["dt"].day == target_day]
        print("=" * 110)
        print(f"🎯 Swiss day={target_day} ({name}) — {len(days)} cases")
        print("=" * 110)
        nd_main = Counter()
        p_bands = defaultdict(lambda: Counter())
        bd_mains_all = Counter()
        nd_mains_all = Counter()
        lucky_count = Counter()
        carrier_hits = Counter()  # mapping cosmic carrier raw hits
        for i, r in days:
            for n in r["mains"]:
                nd_main[n] += 1
            sm = sorted(r["mains"])
            for pi, v in enumerate(sm, start=1):
                p_bands[pi][v] += 1
            if r["lucky"] is not None:
                lucky_count[r["lucky"]] += 1
            # 17→38 / 11→32 carriers — track if both members fired
            if target_day == 17:
                if 17 in r["mains"]:
                    carrier_hits["17_raw"] += 1
                if 38 in r["mains"]:
                    carrier_hits["38_raw"] += 1
                if 17 in r["mains"] and 38 in r["mains"]:
                    carrier_hits["17_AND_38"] += 1
                if 11 in r["mains"]:
                    carrier_hits["11_raw"] += 1
                if 32 in r["mains"]:
                    carrier_hits["32_raw"] += 1
            else:  # 11
                if 11 in r["mains"]:
                    carrier_hits["11_raw"] += 1
                if 32 in r["mains"]:
                    carrier_hits["32_raw"] += 1
                if 11 in r["mains"] and 32 in r["mains"]:
                    carrier_hits["11_AND_32"] += 1
                if 17 in r["mains"]:
                    carrier_hits["17_raw"] += 1
                if 38 in r["mains"]:
                    carrier_hits["38_raw"] += 1
            # BD/ND
            if i > 0:
                for n in rows[i - 1]["mains"]:
                    bd_mains_all[n] += 1
            if i + 1 < len(rows):
                for n in rows[i + 1]["mains"]:
                    nd_mains_all[n] += 1

        N = len(days)
        print(f"\nTop-15 ND mains (the day={target_day} draw itself):")
        for n, c in nd_main.most_common(15):
            print(f"   n={n:>2}  ×{c:>2}  ({100*c/max(1,N):.1f}%)")

        print(f"\n📍 Position bands:")
        for pi in sorted(p_bands.keys()):
            top = p_bands[pi].most_common(5)
            avg = sum(v * cnt for v, cnt in p_bands[pi].items()) / max(1, sum(cnt for _, cnt in p_bands[pi].items()))
            print(f"   P{pi}  avg={avg:.1f}  top: " + " ".join(f"{v}({c})" for v, c in top))

        print(f"\n🍀 lucky distribution:")
        for lk, c in sorted(lucky_count.items()):
            print(f"   🍀{lk}  ×{c}  ({100*c/max(1,N):.1f}%)")

        print(f"\n🔄 Swiss-circle carrier raw-hits (mirror-pair {target_day}↔{17+11-target_day}):")
        for k, v in carrier_hits.items():
            print(f"   {k}: {v}/{N}  ({100*v/max(1,N):.1f}%)")

        print(f"\nTop-10 BD mains (day before day={target_day}):")
        for n, c in bd_mains_all.most_common(10):
            print(f"   n={n:>2}  ×{c:>2}  ({100*c/max(1,N):.1f}%)")

        print(f"\nTop-10 ND mains (day after day={target_day}):")
        for n, c in nd_mains_all.most_common(10):
            print(f"   n={n:>2}  ×{c:>2}  ({100*c/max(1,N):.1f}%)")

        return {"days": days, "nd_main": nd_main, "p_bands": p_bands, "lucky": lucky_count}

    d17 = analyze(17, "PRIMARY")
    print()
    d11 = analyze(11, "MIRROR")

    # CROSS-COMPARISON
    print()
    print("=" * 110)
    print("🪞 CROSS-MIRROR — shared kings between day=17 and day=11")
    print("=" * 110)
    top17 = set(n for n, _ in d17["nd_main"].most_common(20))
    top11 = set(n for n, _ in d11["nd_main"].most_common(20))
    shared = top17 & top11
    print(f"\nShared in top-20 between d17 and d11: {sorted(shared)}")
    only17 = top17 - top11
    only11 = top11 - top17
    print(f"Only in d17 top-20: {sorted(only17)}")
    print(f"Only in d11 top-20: {sorted(only11)}")

    # Carrier pair (17, 38) and (11, 32) presence in each
    print()
    print("🎯 Carrier pair raw-rates:")
    n17 = len(d17["days"])
    n11 = len(d11["days"])
    print(f"   d17: 17 raw = {d17['nd_main'][17]} ({100*d17['nd_main'][17]/max(1,n17):.1f}%)  · 38 raw = {d17['nd_main'][38]} ({100*d17['nd_main'][38]/max(1,n17):.1f}%)")
    print(f"   d17: 11 raw = {d17['nd_main'][11]} ({100*d17['nd_main'][11]/max(1,n17):.1f}%)  · 32 raw = {d17['nd_main'][32]} ({100*d17['nd_main'][32]/max(1,n17):.1f}%)")
    print(f"   d11: 11 raw = {d11['nd_main'][11]} ({100*d11['nd_main'][11]/max(1,n11):.1f}%)  · 32 raw = {d11['nd_main'][32]} ({100*d11['nd_main'][32]/max(1,n11):.1f}%)")
    print(f"   d11: 17 raw = {d11['nd_main'][17]} ({100*d11['nd_main'][17]/max(1,n11):.1f}%)  · 38 raw = {d11['nd_main'][38]} ({100*d11['nd_main'][38]/max(1,n11):.1f}%)")

    cli.close()


if __name__ == "__main__":
    asyncio.run(main())
