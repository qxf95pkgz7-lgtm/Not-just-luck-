"""
🔍 P1-Under-10 Streak Scanner

DJ asks: P1 has been < 10 for many consecutive draws. Find historical
streaks of P1<10 and what broke them.

Current streak: Q2-2026 d9 (01.05) → d17 (29.05) = 9 consecutive P1<10
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


def parse_date(s):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None


async def main():
    cli = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = cli[os.environ["DB_NAME"]]
    docs = await db.euromillions_draws.find({}).to_list(length=None)
    rows = []
    for d in docs:
        ds = d.get("date") or d.get("draw_date")
        dt = parse_date(ds) if ds else None
        if not dt:
            continue
        mains = sorted(d.get("mains") or d.get("numbers") or [])
        stars = list(d.get("stars") or d.get("lucky_stars") or [])
        if len(mains) >= 5:
            rows.append({"dt": dt, "p1": mains[0], "mains": mains, "stars": stars})
    rows.sort(key=lambda r: r["dt"])

    # Find streaks of P1 < 10
    streaks = []
    cur = []
    for r in rows:
        if r["p1"] < 10:
            cur.append(r)
        else:
            if len(cur) >= 2:
                streaks.append({"len": len(cur), "draws": cur})
            cur = []
    if len(cur) >= 2:
        streaks.append({"len": len(cur), "draws": cur, "ongoing": True})

    streaks.sort(key=lambda s: -s["len"])

    print("=" * 100)
    print(f"📊 Total P1<10 streaks of length ≥ 2: {len(streaks)}")
    print(f"📊 Total Euro draws: {len(rows)}")
    print(f"📊 P1<10 firing rate overall: {100*sum(1 for r in rows if r['p1']<10)/len(rows):.1f}%")
    print("=" * 100)
    print()
    print("🥇 TOP 10 LONGEST P1<10 STREAKS in Euro history")
    print("-" * 100)
    for i, s in enumerate(streaks[:10], start=1):
        start = s["draws"][0]
        end = s["draws"][-1]
        print(f"  #{i:>2}  len={s['len']:>2}  "
              f"{start['dt'].strftime('%d.%m.%Y')} → {end['dt'].strftime('%d.%m.%Y')}  "
              f"P1 chain: {[d['p1'] for d in s['draws']]}")

    # For each streak length ≥ current (9), show what came AFTER
    print()
    print("=" * 100)
    print(f"🎯 STREAKS ≥ length 9 (matching or exceeding current 9-draw run)")
    print("=" * 100)
    big = [s for s in streaks if s["len"] >= 9]
    for s in big:
        start = s["draws"][0]["dt"]
        end = s["draws"][-1]["dt"]
        # Find what came right after
        end_idx = rows.index(s["draws"][-1])
        nxt = rows[end_idx + 1] if end_idx + 1 < len(rows) else None
        print(f"\n  📍 Streak of {s['len']}:  {start.strftime('%d.%m.%Y')} → {end.strftime('%d.%m.%Y')}")
        for d in s["draws"]:
            print(f"      {d['dt'].strftime('%d.%m.%Y')}  P1={d['p1']:>2}  mains={d['mains']}  ⭐{d['stars']}")
        if nxt:
            broke = "✅ BROKE" if nxt["p1"] >= 10 else "⏩ continued"
            print(f"      ─── NEXT DRAW ───")
            print(f"      {nxt['dt'].strftime('%d.%m.%Y')}  P1={nxt['p1']:>2}  mains={nxt['mains']}  ⭐{nxt['stars']}  ← {broke}")
        else:
            print(f"      (ONGOING — no next draw yet)")

    # Streak-breaker stats: what was the P1 when streak finally broke?
    print()
    print("=" * 100)
    print("📊 BREAKER STATS — when a P1<10 streak of ANY length ends, what's the breaker P1?")
    print("=" * 100)
    breaker_p1 = Counter()
    breaker_mains = Counter()
    long_breakers = []  # for streaks ≥ 5
    for s in streaks:
        if s.get("ongoing"):
            continue
        end_idx = rows.index(s["draws"][-1])
        if end_idx + 1 < len(rows):
            nxt = rows[end_idx + 1]
            if nxt["p1"] >= 10:
                breaker_p1[nxt["p1"]] += 1
                for m in nxt["mains"]:
                    breaker_mains[m] += 1
                if s["len"] >= 5:
                    long_breakers.append({"streak_len": s["len"], "next": nxt})

    print("Top breaker P1 (after ANY P1<10 streak length):")
    for p, c in sorted(breaker_p1.items())[:20]:
        print(f"   P1={p:>2}  ×{c}")
    print()
    print(f"Total breakers analyzed: {sum(breaker_p1.values())}")
    print(f"Average breaker P1: {sum(p*c for p,c in breaker_p1.items()) / max(1, sum(breaker_p1.values())):.1f}")

    # Long streak breakers (≥5)
    print()
    print("=" * 100)
    print(f"🚨 LONG-STREAK breakers (streak ≥ 5 of P1<10): {len(long_breakers)} cases")
    print("=" * 100)
    long_p1 = Counter()
    for lb in long_breakers:
        print(f"  streak={lb['streak_len']:>2}  →  next: {lb['next']['dt'].strftime('%d.%m.%Y')}  P1={lb['next']['p1']:>2}  mains={lb['next']['mains']}  ⭐{lb['next']['stars']}")
        long_p1[lb["next"]["p1"]] += 1
    print()
    print("Breaker P1 distribution after streaks ≥ 5:")
    for p, c in sorted(long_p1.items()):
        bar = "█" * c
        print(f"   P1={p:>2}  ×{c}  {bar}")
    print(f"\n  Avg long-streak breaker P1: {sum(p*c for p,c in long_p1.items()) / max(1, sum(long_p1.values())):.1f}")

    cli.close()


if __name__ == "__main__":
    asyncio.run(main())
