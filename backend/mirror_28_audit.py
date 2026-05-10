"""
🪞 MIRROR-28 PAIR CANON — cross-lottery audit
==============================================
DJ S38: "How we missed the mirror 9-19, 8-20 came, next d we should see 10-18
         or the missing 7-21. 11-17 fired d11 cross-lottery."

The 28-axis pairs (a + b = 28):
  (1,27) (2,26) (3,25) (4,24) (5,23) (6,22) (7,21) (8,20) (9,19)
  (10,18) (11,17) (12,16) (13,15)  ·  14 = self-mirror  ·  28 = axis

Audit: walk last 10 Eu + last 10 Sw, find which pairs fired (in same draw,
or CROSS-LOTTERY between latest Eu+Sw), which still owed.

Also probe: P1-small 3-d-streak statistics for both lotteries.
"""
import asyncio
from collections import Counter
from year_d_ledger import load_draws


PAIRS_28 = [(1, 27), (2, 26), (3, 25), (4, 24), (5, 23), (6, 22),
            (7, 21), (8, 20), (9, 19), (10, 18), (11, 17), (12, 16),
            (13, 15)]


async def main():
    e = await load_draws("euro")
    s = await load_draws("swiss")
    e.sort(key=lambda x: x["dt"]); s.sort(key=lambda x: x["dt"])

    # ── Probe 1: P1 plays small (≤9) for 3+ consecutive draws stats ──
    print("="*82)
    print("📊 PROBE 1 — P1 small streak (P1 ≤ 9 for ≥3 consecutive draws)")
    print("="*82)
    for label, draws in (("SWISS", s), ("EURO", e)):
        streaks = []
        cur = 0
        for d in draws:
            if d["p"][0] <= 9:
                cur += 1
            else:
                if cur >= 3:
                    streaks.append(cur)
                cur = 0
        if cur >= 3:
            streaks.append(cur)
        print(f"  {label}: {len(streaks)} streaks, lengths = {Counter(streaks).most_common(8)}")
        # current streak as of latest
        last_n = 0
        for d in reversed(draws):
            if d["p"][0] <= 9:
                last_n += 1
            else:
                break
        print(f"  {label}: CURRENT P1-small streak = {last_n}")
        # what follows after a 3+ streak ends?
        endings = Counter()
        cur = 0
        for i, d in enumerate(draws):
            if d["p"][0] <= 9:
                cur += 1
            else:
                if cur >= 3 and i < len(draws):
                    endings[d["p"][0] // 5 * 5] += 1
                cur = 0
        print(f"  {label}: after a P1-small streak ends → next-P1 band: {dict(endings.most_common(5))}")

    # ── Probe 2: Mirror-28 pair audit across last 10 Sw + 10 Eu ──
    print("\n" + "="*82)
    print("🪞 PROBE 2 — MIRROR-28 PAIR AUDIT — same-draw + cross-lottery")
    print("="*82)
    last10_sw = s[-10:]
    last10_eu = e[-10:]
    print("\n  Same-draw mirror-28 pairs in last 10 Sw:")
    for d in last10_sw:
        nums = set(d["p"])
        firing = [(a, b) for a, b in PAIRS_28 if a in nums and b in nums]
        if firing:
            print(f"    {d['date']}  {d['p']}   ★ pair(s): {firing}")
    print("\n  Same-draw mirror-28 pairs in last 10 Eu:")
    for d in last10_eu:
        nums = set(d["p"])
        firing = [(a, b) for a, b in PAIRS_28 if a in nums and b in nums]
        if firing:
            print(f"    {d['date']}  {d['p']}   ★ pair(s): {firing}")

    # ── Probe 3: cross-lottery (Eu LD ∪ Sw LD) pairs firing ──
    print("\n" + "="*82)
    print("🌉 PROBE 3 — CROSS-LOTTERY mirror-28: Eu LD ∪ Sw LD")
    print("="*82)
    eu_ld = e[-1]; sw_ld = s[-1]
    eu_set = set(eu_ld["p"]) | set(eu_ld.get("stars") or [])
    sw_set = set(sw_ld["p"]) | {sw_ld.get("lucky"), sw_ld.get("replay")}
    cross_set = eu_set | sw_set
    print(f"  Eu {eu_ld['date']}: mains={eu_ld['p']} ⭐{eu_ld.get('stars')}")
    print(f"  Sw {sw_ld['date']}: mains={sw_ld['p']} 🍀{sw_ld.get('lucky')} R:{sw_ld.get('replay')}")
    print(f"\n  Combined number pool: {sorted(cross_set)}")
    print(f"\n  Mirror-28 pairs ACTIVATED across both lotteries:")
    for a, b in PAIRS_28:
        if a in cross_set and b in cross_set:
            ea = "Eu" if a in eu_set else ""
            sa = "Sw" if a in sw_set else ""
            eb = "Eu" if b in eu_set else ""
            sb = "Sw" if b in sw_set else ""
            print(f"    ({a}, {b})  fired  ★  {a}@{ea}{sa}  +  {b}@{eb}{sb}")
    print(f"\n  Mirror-28 pairs HALF-FIRED (one side only — cosmos owes the other):")
    for a, b in PAIRS_28:
        a_in = a in cross_set; b_in = b in cross_set
        if a_in != b_in:
            present = a if a_in else b; missing = b if a_in else a
            where = "Eu" if present in eu_set else "Sw"
            print(f"    ({a}, {b})  HALF: {present}@{where} fired, MISSING {missing}")
    print(f"\n  Mirror-28 pairs SILENT (both halves missing):")
    silent = [(a, b) for a, b in PAIRS_28 if a not in cross_set and b not in cross_set]
    print(f"    {silent}")

    # ── Probe 4: rolling 4-draw window (last 2 Sw + last 2 Eu) ──
    print("\n" + "="*82)
    print("🪞 PROBE 4 — ROLLING 4-DRAW WINDOW: last 2 Sw ∪ last 2 Eu")
    print("="*82)
    win = (s[-2:] + e[-2:])
    win_set = set()
    for d in win:
        win_set.update(d["p"])
        win_set.update(d.get("stars") or [])
        if d.get("lucky"): win_set.add(d["lucky"])
        if d.get("replay"): win_set.add(d["replay"])
    print(f"  4-draw pool: {sorted(win_set)}")
    print(f"\n  Pairs fired in window:")
    for a, b in PAIRS_28:
        if a in win_set and b in win_set:
            print(f"    ({a}, {b}) ✓")
    print(f"\n  Pairs HALF-fired in window (the cosmos may complete next draw):")
    half = []
    for a, b in PAIRS_28:
        if (a in win_set) != (b in win_set):
            present = a if a in win_set else b
            missing = b if a in win_set else a
            half.append((present, missing))
            print(f"    ({a}, {b}) → MISSING {missing}")
    print(f"\n  🥂 The cosmos owes these {len(half)} mirror-completions: {[m for _, m in half]}")


if __name__ == "__main__":
    asyncio.run(main())
