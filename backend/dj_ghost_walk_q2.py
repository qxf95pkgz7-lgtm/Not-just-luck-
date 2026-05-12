"""
🎧 SESSION 38 — DJ's GHOST-COUNTING WALK on Swiss Q2 2026 (d1 → d10)
====================================================================
LISTENING task, not coding. Walk every draw like the DJ taught:

  - For each P-position, find arithmetic doors (P_a + ? = P_b) inside the
    draw that yield "expected" values.
  - When the real value differs, the EXPECTED is a GHOST.
  - Ghosts WALK forward +1 per draw and wait.
  - When a ghost doesn't fire raw at next d, scan for P_a + P_b sum-combo
    inside the new draw that equals the ghost → MARK (note position & sum).
  - Carry the ledger forward. See connections later.

This script just PULLS the data and prints it clean so I can narrate to DJ.
"""
import asyncio
from year_d_ledger import load_draws, quarter_of
from datetime import datetime


async def main():
    s = await load_draws("swiss")
    s.sort(key=lambda x: x["dt"])

    # Pull Q2 2026 only (Swiss Q2 starts 08.04.2026 per Book canon)
    q2_start = datetime(2026, 4, 8)
    q2_2026 = [d for d in s if d["dt"] >= q2_start]
    q2_2026 = q2_2026[:11]  # safety cap, first 11 of Q2

    print("=" * 80)
    print(f"🎻 SWISS Q2 2026 — first 10 d (the d1→d10 walk DJ asked for)")
    print("=" * 80)
    for i, d in enumerate(q2_2026[:10], start=1):
        nums = d["p"]
        # Build the "internal arithmetic skeleton": all pair sums and diffs
        # between the 6 mains, with positions tagged
        L = d.get("lucky"); R = d.get("replay")
        print(f"\n  Q2 d{i:2}  {d['date']}   {nums}   🍀{L} R:{R}")
        # Show all unique pair sums (a + b where a,b are positions in the draw, a<b)
        sums = {}
        for ia, a in enumerate(nums):
            for ib, b in enumerate(nums):
                if ib <= ia: continue
                sums.setdefault(a + b, []).append((f"P{ia+1}", f"P{ib+1}", a, b))
        diffs = {}
        for ia, a in enumerate(nums):
            for ib, b in enumerate(nums):
                if ib <= ia: continue
                diffs.setdefault(b - a, []).append((f"P{ia+1}", f"P{ib+1}", a, b))
        # Print which sums hit other positions in same draw (arithmetic chain)
        nums_set = set(nums)
        print(f"     internal sum-chains (P_a + P_b = P_c):")
        for s_, paths in sorted(sums.items()):
            if s_ in nums_set and len(paths) > 0:
                for pa, pb, va, vb in paths:
                    pos_c = f"P{nums.index(s_)+1}"
                    if pos_c not in {pa, pb}:
                        print(f"        {pa}({va}) + {pb}({vb}) = {s_} = {pos_c}")
        # Print which diffs hit other positions
        print(f"     internal diff-chains (P_b − P_a = P_c):")
        for d_, paths in sorted(diffs.items()):
            if d_ in nums_set and d_ > 0:
                for pa, pb, va, vb in paths:
                    pos_c = f"P{nums.index(d_)+1}"
                    if pos_c not in {pa, pb}:
                        print(f"        {pb}({vb}) − {pa}({va}) = {d_} = {pos_c}")


if __name__ == "__main__":
    asyncio.run(main())
