"""
🪞 Swiss Month-Transition Canon — DJ Live (Session 45)

Canon (DJ-taught, 28.03.2026 → 01.04.2026 example):

  P1 = (BD_day − 21) + ND_day        ← Swiss-circle minus + day-step
  P2 = month_OLD × month_NEW          ← month-product
  P3 = month_OLD + year_prefix(20)    ← old-month shoulder
  P4 = month_NEW + year_prefix(20)    ← new-month shoulder
  P5 = BD_day + ND_day                ← day-sum head
  P6 = year_prefix × 2                ← year-cap

Goal: scan all month-transitions in Swiss history. For each:
  - identify last draw of month M
  - identify first draw of month M+1
  - compute the 6 canon predictions
  - count how many canon-predictions HIT in the ND
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
            mains = list(d.get("numbers") or [])
            if len(mains) == 6:
                rows.append({"dt": dt, "mains": sorted(mains),
                             "lucky": d.get("lucky_number"),
                             "replay": d.get("replay_number")})
        except Exception:
            pass
    rows.sort(key=lambda r: r["dt"])

    # Find month transitions: pair (BD, ND) where BD.month != ND.month and they are consecutive
    transitions = []
    for i in range(len(rows) - 1):
        if rows[i]["dt"].month != rows[i + 1]["dt"].month:
            transitions.append((rows[i], rows[i + 1]))

    print(f"📊 Total Swiss month-transitions: {len(transitions)}\n")

    def canon_pred(bd, nd):
        """Return the 6 canon-predicted numbers."""
        bd_day = bd["dt"].day
        nd_day = nd["dt"].day
        m_old = bd["dt"].month
        m_new = nd["dt"].month
        yp = bd["dt"].year // 100  # 20 for 2026, but year_prefix is the 2-digit prefix
        # DJ used 20 — that's the century-prefix (the first 2 digits of year)
        # 2026 → year_prefix = 20
        yp = bd["dt"].year // 100  # =20 for 21st century — works
        return {
            "P1": (bd_day - 21) + nd_day,
            "P2": m_old * m_new,
            "P3": m_old + yp,
            "P4": m_new + yp,
            "P5": bd_day + nd_day,
            "P6": yp * 2,
        }

    print("=" * 110)
    print("🎯 CANON vs REALITY — every Swiss month-transition")
    print("=" * 110)
    print(f"{'BD':<12} {'ND':<12} {'BD-mains':<25} {'ND-mains':<28} {'canon':<32}  hits")
    print("-" * 130)

    total_hits = Counter()  # count by # hits per ND
    canon_position_hits = Counter()  # which canon slot fires most
    hit_examples = []
    near_misses = 0

    for bd, nd in transitions:
        pred = canon_pred(bd, nd)
        nd_set = set(nd["mains"])
        # Check raw hits
        hits = [(k, v) for k, v in pred.items() if v in nd_set and 1 <= v <= 42]
        # Check ±1 ghost hits
        near_hits = [(k, v) for k, v in pred.items()
                     if (v in nd_set or v - 1 in nd_set or v + 1 in nd_set) and 1 <= v <= 42]
        total_hits[len(hits)] += 1
        for k, _ in hits:
            canon_position_hits[k] += 1
        canon_str = ",".join(f"{k}={v}" for k, v in pred.items())
        hit_str = f"{len(hits)}/6 hits: {','.join(f'{k}={v}' for k,v in hits)}"
        if len(hits) >= 3:
            hit_examples.append({"bd": bd, "nd": nd, "pred": pred, "hits": hits})
        # Print first 20 + any high-hit ones
        if len(transitions) <= 100 or len(hits) >= 3:
            print(f"{bd['dt'].strftime('%d.%m.%Y'):<12} {nd['dt'].strftime('%d.%m.%Y'):<12} "
                  f"{str(bd['mains']):<25} {str(nd['mains']):<28} {canon_str:<32}  {hit_str}")

    print()
    print("=" * 110)
    print("📊 HIT-RATE distribution across all transitions")
    print("=" * 110)
    total = sum(total_hits.values())
    for k in sorted(total_hits.keys()):
        c = total_hits[k]
        print(f"  {k}/6 canon-hits:  {c:>3} cases  ({100*c/total:.1f}%)")
    print()
    expected_random = 6 * 6 / 42  # 6 predictions, 6/42 hit prob each
    print(f"  → Random expectation (uniform): ≈ {expected_random:.2f} hits per ND")
    actual_avg = sum(k * c for k, c in total_hits.items()) / max(1, total)
    print(f"  → Actual average               : {actual_avg:.2f} hits per ND")
    print(f"  → Canon LIFT vs random         : {actual_avg / expected_random:.2f}x")

    print()
    print("📊 Per-position canon strength (which slot lands most often):")
    for k in sorted(canon_position_hits.keys()):
        c = canon_position_hits[k]
        print(f"   {k}  ×{c}  ({100*c/total:.1f}%)")

    # Show top 3+ hit examples
    print()
    print("=" * 110)
    print("🥇 TOP canon HITS (3+ predictions landed)")
    print("=" * 110)
    for ex in hit_examples[:20]:
        print(f"  {ex['bd']['dt'].strftime('%d.%m.%Y')} {ex['bd']['mains']}  →  "
              f"{ex['nd']['dt'].strftime('%d.%m.%Y')} {ex['nd']['mains']}  "
              f"canon: {ex['pred']}  hits: {ex['hits']}")

    # TOMORROW projection (30.05 → 03.06)
    print()
    print("=" * 110)
    print("🎯 TOMORROW PROJECTION — Wed 03.06.2026 Swiss")
    print("=" * 110)
    # Find 30.05.2026 + the expected next
    bd = next((r for r in rows if r["dt"].strftime("%d.%m.%Y") == "30.05.2026"), None)
    if bd:
        # Hypothetical ND on 03.06.2026
        import types
        nd_stub = {"dt": datetime(2026, 6, 3), "mains": []}
        pred = canon_pred(bd, nd_stub)
        print(f"  BD: 30.05.2026 [7, 9, 14, 17, 19, 39] 🍀2")
        print(f"  Canon → ND 03.06.2026 prediction:")
        for k, v in pred.items():
            print(f"     {k} = {v}")
        # Lucky predictor: BD-🍀 + month_OLD (mod 6)
        bd_lucky = bd["lucky"]
        if bd_lucky:
            pred_lucky = ((bd_lucky + bd["dt"].month - 1) % 6) + 1
            print(f"  🍀 prediction: ({bd_lucky} + {bd['dt'].month}) mod-6 = {pred_lucky}")
        print(f"  → 🎫 Predicted Wed 03.06.2026 Swiss: [12, 25, 26, 30, 33, 40] 🍀{pred_lucky if bd_lucky else '?'}")

    cli.close()


if __name__ == "__main__":
    asyncio.run(main())
