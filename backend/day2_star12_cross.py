"""
🪞 DAY=2 + ⭐12 Cross-Scanner — DJ Live Session 45

Two layers:
  Layer 1: ALL Euro draws where day=2 (regardless of month)
  Layer 2: subset where ⭐12 fires (raw or in BD/ND)

Tonight 02.06.2026 sits at intersection: day=2 + ⭐12 streak active.
"""

import asyncio
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ENV = {}
for line in (Path(__file__).parent / ".env").read_text().splitlines():
    if "=" not in line or line.strip().startswith("#"):
        continue
    k, v = line.split("=", 1)
    ENV[k.strip()] = v.strip().strip('"')
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
    c = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = c[os.environ["DB_NAME"]]
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

    # Layer 1 — all day=2 draws
    day2 = [r for r in rows if r["dt"].day == 2]
    print(f"📊 ALL day=2 Euro draws: {len(day2)}")
    print()
    print("=" * 100)
    print("🪞 LAYER 1 — every day=2 draw in history")
    print("=" * 100)
    print(f"{'date':<12} {'wd':<3} {'mains':<27} {'⭐':<10}  notes")
    print("-" * 90)
    for r in day2:
        wd = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][r["dt"].weekday()]
        has12 = "★12" if 12 in r["stars"] else ""
        print(f"  {r['dt'].strftime('%d.%m.%Y'):<10} {wd:<3} {str(r['mains']):<27} {str(r['stars']):<10}  {has12}")

    # Layer 1 main-number tally
    print()
    print("=" * 100)
    print("🔥 LAYER 1 TALLY — mains frequency across all day=2 draws")
    print("=" * 100)
    main_count = Counter()
    star_count = Counter()
    for r in day2:
        for n in r["mains"]:
            main_count[n] += 1
        for s in r["stars"]:
            star_count[s] += 1
    print("Top-20 mains:")
    for n, c in main_count.most_common(20):
        rate = 100 * c / max(1, len(day2))
        print(f"   n={n:>2}  fired {c:>2}x  ({rate:.1f}%)")
    print()
    print("Top-12 stars:")
    for s, cnt in sorted(star_count.items(), key=lambda x: -x[1])[:12]:
        rate = 100 * cnt / max(1, len(day2))
        print(f"   ⭐{s:>2}  fired {cnt:>2}x  ({rate:.1f}%)")

    # Layer 2 — day=2 AND ⭐12 active in that draw
    day2_star12 = [r for r in day2 if 12 in r["stars"]]
    print()
    print("=" * 100)
    print(f"🚨 LAYER 2 — day=2 AND ⭐12 fired in same draw: {len(day2_star12)} cases")
    print("=" * 100)
    for r in day2_star12:
        wd = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][r["dt"].weekday()]
        print(f"  {r['dt'].strftime('%d.%m.%Y'):<12} {wd:<3} mains={r['mains']} ⭐{r['stars']}")

    # Layer 2 tally
    print()
    if day2_star12:
        print("Tally (day=2 + ⭐12 active):")
        d2s12_count = Counter()
        for r in day2_star12:
            for n in r["mains"]:
                d2s12_count[n] += 1
        for n, c in d2s12_count.most_common(15):
            rate = 100 * c / max(1, len(day2_star12))
            print(f"   n={n:>2}  fired {c:>2}x  ({rate:.1f}%)")

    # Layer 3 — day=2 where ⭐12 fired in BD (day before) — tonight's actual case!
    print()
    print("=" * 100)
    print("🎯 LAYER 3 — day=2 draws where the PRIOR draw (BD) had ⭐12")
    print("=" * 100)
    print("(THIS is our exact tonight setup: BD 29.05.2026 had ⭐12, tonight 02.06 is day=2)")
    print()
    day2_bd_star12 = []
    for i, r in enumerate(rows):
        if r["dt"].day != 2:
            continue
        if i > 0 and 12 in rows[i - 1]["stars"]:
            day2_bd_star12.append((rows[i - 1], r))
    for bd, nd in day2_bd_star12:
        bd_repeats = "🔥 ⭐12-REPEAT" if 12 in nd["stars"] else ""
        print(f"  BD {bd['dt'].strftime('%d.%m.%Y')} mains={bd['mains']} ⭐{bd['stars']}")
        print(f"  ND {nd['dt'].strftime('%d.%m.%Y')} mains={nd['mains']} ⭐{nd['stars']}  {bd_repeats}")
        print()
    print(f"Total: {len(day2_bd_star12)} cases")
    repeat_count = sum(1 for _, nd in day2_bd_star12 if 12 in nd["stars"])
    print(f"⭐12 repeated on day=2 ND: {repeat_count} times ({100*repeat_count/max(1,len(day2_bd_star12)):.1f}%)")

    # Tally for day=2 BD-⭐12 draws
    print()
    print("📊 Mains tally on day=2 draws AFTER ⭐12 BD:")
    nd_count = Counter()
    nd_star_count = Counter()
    for _, nd in day2_bd_star12:
        for n in nd["mains"]:
            nd_count[n] += 1
        for s in nd["stars"]:
            nd_star_count[s] += 1
    for n, c in nd_count.most_common(15):
        rate = 100 * c / max(1, len(day2_bd_star12))
        print(f"   n={n:>2}  fired {c:>2}x  ({rate:.1f}%)")
    print()
    print("📊 ⭐ tally on day=2 draws AFTER ⭐12 BD:")
    for s, cnt in sorted(nd_star_count.items(), key=lambda x: -x[1])[:12]:
        rate = 100 * cnt / max(1, len(day2_bd_star12))
        print(f"   ⭐{s:>2}  fired {cnt:>2}x  ({rate:.1f}%)")

    # Layer 4: BD has ⭐12 AND ND day=2 AND ND ALSO has ⭐12 (the streak case = our tonight if 12 repeats)
    streak_cases = [(b, n) for b, n in day2_bd_star12 if 12 in n["stars"]]
    if streak_cases:
        print()
        print("=" * 100)
        print(f"🚨🚨 LAYER 4 — TONIGHT-MATCHING (BD ⭐12 + ND day=2 + ND ⭐12 repeats) = {len(streak_cases)}")
        print("=" * 100)
        for b, n in streak_cases:
            print(f"  BD {b['dt'].strftime('%d.%m.%Y')} ⭐{b['stars']} → ND {n['dt'].strftime('%d.%m.%Y')} mains={n['mains']} ⭐{n['stars']}")

    # Position bands for day=2 BD-⭐12 case
    print()
    print("=" * 100)
    print("📍 POSITION BANDS — day=2 ND after ⭐12 BD")
    print("=" * 100)
    p_bands = defaultdict(lambda: Counter())
    for _, nd in day2_bd_star12:
        if len(nd["mains"]) >= 5:
            sm = sorted(nd["mains"])
            for pi, v in enumerate(sm, start=1):
                p_bands[pi][v] += 1
    for pi in sorted(p_bands):
        top = p_bands[pi].most_common(5)
        avg = sum(v * cnt for v, cnt in p_bands[pi].items()) / max(1, sum(cnt for _, cnt in p_bands[pi].items()))
        top_str = " ".join(f"{v}({cnt})" for v, cnt in top)
        print(f"   P{pi}  avg={avg:.1f}  top: {top_str}")

    c.close()


if __name__ == "__main__":
    asyncio.run(main())
