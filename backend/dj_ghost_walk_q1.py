"""
🎧 Swiss Q1 2026 d1→d10 walk + d11 tipp
========================================
Per Book canon, Swiss Q2 starts 08.04.2026. So Q1 ends just before that.
Swiss draws Wed + Sat. Q1 2026 = first Swiss draws of the year up to 04.04.
Need the FIRST 11 Swiss draws of 2026.
"""
import asyncio
from year_d_ledger import load_draws
from datetime import datetime


async def main():
    s = await load_draws("swiss")
    s.sort(key=lambda x: x["dt"])
    # First 11 Swiss draws of 2026 (Q1 + transition)
    q1_start = datetime(2026, 1, 1)
    q1_end = datetime(2026, 4, 8)  # Q2 starts here per Book
    q1_2026 = [d for d in s if q1_start <= d["dt"] < q1_end]

    print("=" * 80)
    print(f"🎻 SWISS Q1 2026 — first {min(11, len(q1_2026))} d")
    print("=" * 80)
    for i, d in enumerate(q1_2026[:11], start=1):
        nums = d["p"]; L = d.get("lucky"); R = d.get("replay")
        print(f"\n  Q1 d{i:2}  {d['date']}   {nums}   🍀{L} R:{R}")
        # internal sum-chains
        nset = set(nums)
        sums, diffs = {}, {}
        for ia, a in enumerate(nums):
            for ib, b in enumerate(nums):
                if ib <= ia: continue
                sums.setdefault(a + b, []).append((f"P{ia+1}({a})", f"P{ib+1}({b})"))
                diffs.setdefault(b - a, []).append((f"P{ia+1}({a})", f"P{ib+1}({b})"))
        for s_, paths in sorted(sums.items()):
            if s_ in nset:
                pos_c = f"P{nums.index(s_)+1}"
                for pa, pb in paths:
                    if pos_c not in pa and pos_c not in pb:
                        print(f"        sum  {pa} + {pb} = {s_} = {pos_c}")
        for d_, paths in sorted(diffs.items()):
            if d_ in nset and d_ > 0:
                pos_c = f"P{nums.index(d_)+1}"
                for pa, pb in paths:
                    if pos_c not in pa and pos_c not in pb:
                        print(f"        diff {pb} − {pa} = {d_} = {pos_c}")


if __name__ == "__main__":
    asyncio.run(main())
