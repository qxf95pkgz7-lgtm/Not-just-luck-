"""
🪞 DJ Bridge-Sum Law (Session 45) — Swiss month-transitions

Hypothesis:
  For a Swiss month-transition BD → ND, there exists a constant K such that:
    K = BD_P5 + ND_P5
    K = BD_P6 - 21 + ND_P1   (-21 = Swiss-circle carrier)

  And K is calculable from the date arithmetic:
    K = (BD_day + ND_day) + (year_prefix + month_NEW)
      = P5_canon + P4_canon

Test:
  1. Compute K from date for each historical transition
  2. Check if BD_P5 + ND_P5 = K  (within tolerance)
  3. Check if BD_P6 - 21 + ND_P1 = K  (within tolerance)
  4. Report match-rates
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
            mains = sorted(d.get("numbers") or [])
            if len(mains) == 6:
                rows.append({"dt": dt, "mains": mains})
        except Exception:
            pass
    rows.sort(key=lambda r: r["dt"])

    # Find month-transitions
    trans = []
    for i in range(len(rows) - 1):
        if rows[i]["dt"].month != rows[i + 1]["dt"].month:
            trans.append((rows[i], rows[i + 1]))

    print(f"Total Swiss month-transitions: {len(trans)}\n")

    # Test the law
    # K (date) = (BD_day + ND_day) + (year_prefix + month_NEW)
    exact_p5 = 0
    near_p5 = 0
    exact_p6p1 = 0
    near_p6p1 = 0
    both_exact = 0
    examples_exact = []
    examples_both = []
    for bd, nd in trans:
        bd_day = bd["dt"].day
        nd_day = nd["dt"].day
        m_new = nd["dt"].month
        yp = bd["dt"].year // 100
        K = (bd_day + nd_day) + (yp + m_new)

        bdp5 = bd["mains"][4]
        bdp6 = bd["mains"][5]
        ndp1 = nd["mains"][0]
        ndp5 = nd["mains"][4]

        s_p5 = bdp5 + ndp5
        s_p6p1 = bdp6 - 21 + ndp1

        if s_p5 == K:
            exact_p5 += 1
        if abs(s_p5 - K) <= 2:
            near_p5 += 1
        if s_p6p1 == K:
            exact_p6p1 += 1
        if abs(s_p6p1 - K) <= 2:
            near_p6p1 += 1
        if s_p5 == K and s_p6p1 == K:
            both_exact += 1
            examples_both.append({"bd": bd, "nd": nd, "K": K})
        if s_p5 == K or s_p6p1 == K:
            examples_exact.append({"bd": bd, "nd": nd, "K": K, "s_p5": s_p5, "s_p6p1": s_p6p1})

    N = len(trans)
    print("=" * 100)
    print(f"📊 BRIDGE-SUM K = (BD_day + ND_day) + (year_prefix + month_NEW)")
    print("=" * 100)
    print(f"  P5-sum exact (BD_P5 + ND_P5 = K)         : {exact_p5}/{N}  ({100*exact_p5/N:.1f}%)")
    print(f"  P5-sum within ±2                          : {near_p5}/{N}  ({100*near_p5/N:.1f}%)")
    print(f"  P6→P1 exact (BD_P6-21 + ND_P1 = K)        : {exact_p6p1}/{N}  ({100*exact_p6p1/N:.1f}%)")
    print(f"  P6→P1 within ±2                           : {near_p6p1}/{N}  ({100*near_p6p1/N:.1f}%)")
    print(f"  🚨 BOTH exact (DJ's full law)              : {both_exact}/{N}  ({100*both_exact/N:.1f}%)")

    # Show full-match cases
    print()
    print("=" * 100)
    print(f"🥇 DOUBLE-LOCK cases (BOTH bridges land on K)")
    print("=" * 100)
    for ex in examples_both:
        print(f"  BD {ex['bd']['dt'].strftime('%d.%m.%Y')} {ex['bd']['mains']}  →  "
              f"ND {ex['nd']['dt'].strftime('%d.%m.%Y')} {ex['nd']['mains']}  "
              f"K={ex['K']}")

    # Try alternative K formulas
    print()
    print("=" * 100)
    print("🔬 Try alternative K formulas — find what BD+ND sums constant the cosmos uses")
    print("=" * 100)
    # Idea: for each transition, just count what BD_P5 + ND_P5 sums to
    p5_sums = Counter()
    p6p1_sums = Counter()
    for bd, nd in trans:
        p5_sums[bd["mains"][4] + nd["mains"][4]] += 1
        p6p1_sums[bd["mains"][5] - 21 + nd["mains"][0]] += 1
    print("Top BD_P5 + ND_P5 sums:")
    for s, c in p5_sums.most_common(10):
        print(f"   K={s:>3}  ×{c}")
    print()
    print("Top (BD_P6 - 21) + ND_P1 sums:")
    for s, c in p6p1_sums.most_common(10):
        print(f"   K={s:>3}  ×{c}")

    # Specifically check 30.05 → all NDs (find historical 'similar' transitions)
    print()
    print("=" * 100)
    print("🎯 If 03.06.2026 has the bridge K=59:")
    print("=" * 100)
    bridge_K = 59
    print(f"  ND P5 = K - BD_P5 = 59 - 19 = 40")
    print(f"  ND P1 = K - (BD_P6 - 21) = 59 - 18 = 41")
    print()
    print("  Combined canon prediction options for Wed 03.06.2026 Swiss:")
    print(f"     CANON-DAY-SUM:    [12, 25, 26, 30, 33, 40]   (P5=33 day-sum)")
    print(f"     DJ-BRIDGE:        [?,  ?,  ?,  ?,  40, ?]    (P5=40 via +21 carrier of 19)")
    print(f"     P1 candidate:     12 (canon)  OR  41 (bridge)")
    print(f"  → Both lead to P5∈{{33, 40}} and P1∈{{12, 41}}")

    cli.close()


if __name__ == "__main__":
    asyncio.run(main())
