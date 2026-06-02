"""
⭐12 Twice — when ⭐12 fires in two consecutive Euro draws

DJ question: tonight's BD 29.05.2026 ⭐(2, 12) — if ⭐12 comes again tonight,
what's the cosmic grammar of consecutive ⭐12 events?

Scan all consecutive-pair Euro draws for star-repeat patterns.
"""

import asyncio
import os
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
        stars = list(d.get("stars") or d.get("lucky_stars") or [])
        mains = list(d.get("mains") or d.get("numbers") or [])
        rows.append({"dt": dt, "mains": mains, "stars": stars})
    rows.sort(key=lambda r: r["dt"])

    # ⭐12 LIFETIME stats
    fire_count = sum(1 for r in rows if 12 in r["stars"])
    print(f"📊 ⭐12 fired {fire_count} times in {len(rows)} Euro draws "
          f"({100*fire_count/len(rows):.2f}%)\n")

    # Consecutive ⭐12 cases
    print("=" * 100)
    print("🚨 CONSECUTIVE ⭐12 — draw N has ⭐12 AND draw N+1 also has ⭐12")
    print("=" * 100)
    runs = []  # list of (date_prev, prev_mains, prev_stars, date_next, next_mains, next_stars)
    for i in range(len(rows) - 1):
        if 12 in rows[i]["stars"] and 12 in rows[i + 1]["stars"]:
            runs.append((rows[i], rows[i + 1]))

    print(f"Total consecutive ⭐12 pairs: {len(runs)}\n")
    print(f"{'BD':<12} {'BD-mains':<27} {'BD-⭐':<8}  →  {'ND':<12} {'ND-mains':<27} {'ND-⭐':<8}  partner ⭐")
    print("-" * 130)
    partner_count = Counter()
    pos_count = Counter()  # which P-position holds the repeat star
    nd_main_count = Counter()
    bd_main_count = Counter()
    for prev, nxt in runs:
        partner = [s for s in nxt["stars"] if s != 12]
        partner_count[partner[0] if partner else None] += 1
        print(f"{prev['dt'].strftime('%d.%m.%Y'):<12} {str(prev['mains']):<27} {str(prev['stars']):<8}  →  "
              f"{nxt['dt'].strftime('%d.%m.%Y'):<12} {str(nxt['mains']):<27} {str(nxt['stars']):<8}  ⭐{partner}")
        for n in nxt["mains"]:
            nd_main_count[n] += 1
        for n in prev["mains"]:
            bd_main_count[n] += 1

    print()
    print("=" * 100)
    print("⭐ PARTNER STAR LEADERBOARD (who joins ⭐12 in the ND)")
    print("=" * 100)
    for s, c in partner_count.most_common():
        rate = 100 * c / max(1, len(runs))
        print(f"   ⭐{s:>2}  fired {c:>2}x  ({rate:.1f}%)")

    print()
    print("=" * 100)
    print("🎯 ND MAINS TALLY when ⭐12 repeats")
    print("=" * 100)
    for n, c in nd_main_count.most_common(20):
        rate = 100 * c / max(1, len(runs))
        print(f"   n={n:>2}  fired {c:>2}x  ({rate:.1f}%)")

    print()
    print("=" * 100)
    print("📍 Position bands in ND when ⭐12 repeats")
    print("=" * 100)
    p_bands = defaultdict(lambda: Counter())
    for prev, nxt in runs:
        if len(nxt["mains"]) >= 5:
            sorted_m = sorted(nxt["mains"])
            for pi, val in enumerate(sorted_m, start=1):
                p_bands[pi][val] += 1
    for pi in sorted(p_bands.keys()):
        top = p_bands[pi].most_common(5)
        avg = sum(v * c for v, c in p_bands[pi].items()) / max(1, sum(c for _, c in p_bands[pi].items()))
        top_str = " ".join(f"{v}({c})" for v, c in top)
        print(f"   P{pi}  avg={avg:.1f}  top: {top_str}")

    # ⭐12 with ⭐2 specifically (our BD has ⭐(2, 12))
    print()
    print("=" * 100)
    print("🎼 SPECIAL: when BD has ⭐(2, 12) — what happens next?")
    print("=" * 100)
    for i in range(len(rows) - 1):
        if 2 in rows[i]["stars"] and 12 in rows[i]["stars"]:
            print(f"  BD  {rows[i]['dt'].strftime('%d.%m.%Y'):<12} mains={rows[i]['mains']} ⭐{rows[i]['stars']}")
            print(f"  ND  {rows[i+1]['dt'].strftime('%d.%m.%Y'):<12} mains={rows[i+1]['mains']} ⭐{rows[i+1]['stars']}")
            print()

    # Q2 specifically
    print("=" * 100)
    print("🌿 Q2-only: ⭐12 repeats in Q2 (our current quarter)")
    print("=" * 100)
    q2_runs = [(p, n) for p, n in runs
               if (p["dt"].month - 1) // 3 + 1 == 2 and (n["dt"].month - 1) // 3 + 1 == 2]
    print(f"  Q2 consecutive-⭐12: {len(q2_runs)}")
    for p, n in q2_runs:
        print(f"   {p['dt'].strftime('%d.%m.%Y')} ⭐{p['stars']} → "
              f"{n['dt'].strftime('%d.%m.%Y')} mains={n['mains']} ⭐{n['stars']}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
