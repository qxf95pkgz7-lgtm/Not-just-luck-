"""
Star ⭐[1, 11] CLUE HUNT — Session 30
=====================================
DJ asked: when stars were [1, 11], what happened the next draw (nd)?
Pure detective mode — no laws, just clues. Look for patterns with the date.
"""
import os
import sys
from datetime import datetime
from collections import Counter, defaultdict

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")

TARGET = {1, 11}


def parse_date(s):
    return datetime.strptime(s, "%d.%m.%Y")


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    draws = await db.euromillions_draws.find({}, {"_id": 0}).to_list(length=10000)
    # sort by date asc
    draws = [d for d in draws if d.get("date") and d.get("numbers") and d.get("stars")]
    draws.sort(key=lambda d: parse_date(d["date"]))

    print(f"📚 Loaded {len(draws)} Euro draws from {draws[0]['date']} → {draws[-1]['date']}")
    print()

    # find every draw with stars == {1, 11}
    hits = []
    for i, d in enumerate(draws):
        s = set(d["stars"])
        if s == TARGET:
            nd = draws[i + 1] if i + 1 < len(draws) else None
            nd2 = draws[i + 2] if i + 2 < len(draws) else None
            hits.append({"i": i, "d": d, "nd": nd, "nd2": nd2})

    print(f"🎯 Found {len(hits)} draws with ⭐[1, 11]")
    print("=" * 100)

    # ---- 1. List every occurrence with full context ----
    for h in hits:
        d, nd, nd2 = h["d"], h["nd"], h["nd2"]
        date = d["date"]
        nums = d["numbers"]
        print(f"\n🔵 {date} → mains {nums} ⭐{d['stars']}")
        if nd:
            shared_mains = sorted(set(nums) & set(nd["numbers"]))
            shared_stars = sorted(set(d["stars"]) & set(nd["stars"]))
            print(f"   ➡️  ND  {nd['date']} → mains {nd['numbers']} ⭐{nd['stars']}"
                  f"   | repeats: mains={shared_mains} stars={shared_stars}")
        if nd2:
            print(f"   ➡️  ND2 {nd2['date']} → mains {nd2['numbers']} ⭐{nd2['stars']}")

    if not hits:
        return

    print()
    print("=" * 100)
    print("🔬 AGGREGATE CLUE BOARD")
    print("=" * 100)

    # ---- 2. Star clues: what stars appeared in nd ----
    nd_star_freq = Counter()
    nd_star_pairs = Counter()
    for h in hits:
        nd = h["nd"]
        if nd:
            for s in nd["stars"]:
                nd_star_freq[s] += 1
            nd_star_pairs[tuple(sorted(nd["stars"]))] += 1

    n = sum(1 for h in hits if h["nd"])
    print(f"\n⭐ NEXT-DRAW star single-frequency (n={n} ND draws):")
    for s, c in nd_star_freq.most_common():
        pct = 100 * c / n
        baseline = 100 * 2 / 12  # ~16.7% per single star (random)
        marker = "🔥" if pct >= baseline * 1.5 else ("📉" if pct < baseline * 0.5 else "")
        print(f"   ⭐{s:2d}: {c}/{n} = {pct:5.1f}%  (baseline {baseline:.1f}%) {marker}")

    print(f"\n⭐ NEXT-DRAW star PAIR frequency (top pairs):")
    for pair, c in nd_star_pairs.most_common(10):
        print(f"   ⭐{pair}: {c}/{n}")

    # how often does 1 or 11 reappear next draw?
    one_back = sum(1 for h in hits if h["nd"] and 1 in h["nd"]["stars"])
    eleven_back = sum(1 for h in hits if h["nd"] and 11 in h["nd"]["stars"])
    both_back = sum(1 for h in hits if h["nd"] and 1 in h["nd"]["stars"] and 11 in h["nd"]["stars"])
    neither = sum(1 for h in hits if h["nd"] and 1 not in h["nd"]["stars"] and 11 not in h["nd"]["stars"])
    print(f"\n♻️  Reappearance of seed stars next draw:")
    print(f"   ⭐1 alone back:     {one_back}/{n} = {100*one_back/n:.1f}%")
    print(f"   ⭐11 alone back:    {eleven_back}/{n} = {100*eleven_back/n:.1f}%")
    print(f"   ⭐BOTH back:        {both_back}/{n} = {100*both_back/n:.1f}%")
    print(f"   ⭐NEITHER (clean break): {neither}/{n} = {100*neither/n:.1f}%")

    # ---- 3. Star companions: what star pairs WITH 1 or 11 next time? ----
    one_companions = Counter()
    eleven_companions = Counter()
    for h in hits:
        nd = h["nd"]
        if nd:
            ss = nd["stars"]
            if 1 in ss:
                for s in ss:
                    if s != 1:
                        one_companions[s] += 1
            if 11 in ss:
                for s in ss:
                    if s != 11:
                        eleven_companions[s] += 1

    print(f"\n🤝 Companions of ⭐1 in ND (when 1 returned):")
    for s, c in one_companions.most_common():
        print(f"   ⭐1 + ⭐{s:2d}: {c}")
    print(f"\n🤝 Companions of ⭐11 in ND (when 11 returned):")
    for s, c in eleven_companions.most_common():
        print(f"   ⭐11 + ⭐{s:2d}: {c}")

    # ---- 4. Mains repeats: how many of seed mains came back ----
    main_repeat_count = Counter()
    for h in hits:
        nd = h["nd"]
        if nd:
            shared = len(set(h["d"]["numbers"]) & set(nd["numbers"]))
            main_repeat_count[shared] += 1
    print(f"\n🔁 Mains repeat count from seed→ND:")
    for cnt, c in sorted(main_repeat_count.items()):
        print(f"   {cnt} mains carried over: {c}/{n}")

    # ---- 5. Date clues: day-of-month + month patterns ----
    print(f"\n📅 Date signature of [1,11] events:")
    for h in hits:
        d = h["d"]
        nd = h["nd"]
        dt = parse_date(d["date"])
        nd_dt = parse_date(nd["date"]) if nd else None
        gap = (nd_dt - dt).days if nd_dt else None
        sum_d = dt.day + dt.month
        print(f"   {d['date']}  day={dt.day:2d} month={dt.month:2d} sum={sum_d:3d}  → gap to ND: {gap}d")

    # ---- 6. ND P1 / P5 distribution ----
    nd_p1 = Counter()
    nd_p5 = Counter()
    for h in hits:
        if h["nd"]:
            nd_p1[h["nd"]["numbers"][0]] += 1
            nd_p5[h["nd"]["numbers"][-1]] += 1
    print(f"\n🎯 ND P1 distribution: {dict(nd_p1)}")
    print(f"🎯 ND P5 distribution: {dict(nd_p5)}")

    p1_low = sum(c for v, c in nd_p1.items() if v <= 5)
    p1_2or3 = sum(c for v, c in nd_p1.items() if v in (2, 3))
    print(f"   ND P1 ≤ 5:        {p1_low}/{n} = {100*p1_low/n:.1f}%")
    print(f"   ND P1 ∈ {{2,3}}:   {p1_2or3}/{n} = {100*p1_2or3/n:.1f}%   (Law 90 zone)")

    # ---- 7. Did the next draw show a star drift? ----
    print(f"\n🌬️  Star DRIFT (seed=[1,11] vs ND stars, sorted):")
    drift_sums = Counter()
    for h in hits:
        if h["nd"]:
            seed_sum = sum(h["d"]["stars"])  # always 12
            nd_sum = sum(h["nd"]["stars"])
            drift_sums[nd_sum - seed_sum] += 1
    for diff, c in sorted(drift_sums.items()):
        print(f"   Δ star-sum = {diff:+d} → {c} times")

    # 1+11 = 12 (a full octave?). Did the cosmos echo 12 in mains?
    print(f"\n🎵 12-echo in ND mains (1+11=12):")
    twelve_in_mains = sum(1 for h in hits if h["nd"] and 12 in h["nd"]["numbers"])
    one_in_mains = sum(1 for h in hits if h["nd"] and 1 in h["nd"]["numbers"])
    eleven_in_mains = sum(1 for h in hits if h["nd"] and 11 in h["nd"]["numbers"])
    print(f"   12 in ND mains:   {twelve_in_mains}/{n} = {100*twelve_in_mains/n:.1f}%")
    print(f"   1  in ND mains:   {one_in_mains}/{n} = {100*one_in_mains/n:.1f}%")
    print(f"   11 in ND mains:   {eleven_in_mains}/{n} = {100*eleven_in_mains/n:.1f}%")

    # 51-mirror of stars: 1→50, 11→40 (51-mirror) — did 50 or 40 land in mains?
    print(f"\n🪞 51-mirror of seed stars in ND mains (1→50, 11→40):")
    fifty_in = sum(1 for h in hits if h["nd"] and 50 in h["nd"]["numbers"])
    forty_in = sum(1 for h in hits if h["nd"] and 40 in h["nd"]["numbers"])
    print(f"   50 in ND mains:   {fifty_in}/{n} = {100*fifty_in/n:.1f}%")
    print(f"   40 in ND mains:   {forty_in}/{n} = {100*forty_in/n:.1f}%")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
