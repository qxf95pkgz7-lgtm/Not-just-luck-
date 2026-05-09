"""
Q2 SWISS PER-POSITION GAP WALK
==================================
DJ: "Check gap q2 d all p with nd p. Check if gap has clues."

For each P-position (P1..P6), walk d1→d2→...→d9 and compute the
delta to the next d. Look for:
  • repeating gaps (rhythm)
  • cumulative drift
  • d-position signatures
  • the 67-bridge / 678-hide / 9-clock numbers in gaps
"""
import asyncio
from collections import Counter
from year_d_ledger import load_draws


async def main():
    s = await load_draws("swiss")
    s.sort(key=lambda x: x["dt"])
    q2 = [d for d in s if d["year"] == 2026 and d["quarter"] == 2]

    print("🍀 SWISS Q2 2026 — d-by-d ledger")
    print("="*82)
    for i, d in enumerate(q2, 1):
        L = d.get("lucky"); R = d.get("replay")
        print(f"  d{i:2d}  {d['date']}  {d['wd']:3s}  {d['p']}  🍀{L} R:{R}")

    # ── per-position gaps ──
    print("\n" + "="*82)
    print("📊 PER-POSITION GAP WALK (d→d+1 delta for each P-slot)")
    print("="*82)

    pos_series = [[] for _ in range(6)]  # P1..P6 raw value series
    for d in q2:
        for k in range(6):
            pos_series[k].append(d["p"][k] if k < len(d["p"]) else None)

    print("\n  d-by-d values per position:")
    print(f"  d#:  {'P1':>4} {'P2':>4} {'P3':>4} {'P4':>4} {'P5':>4} {'P6':>4}")
    for i in range(len(q2)):
        row = " ".join(f"{pos_series[k][i]:>4d}" for k in range(6))
        print(f"  d{i+1:>2}: {row}  ({q2[i]['date'][:5]} {q2[i]['wd'][:3]})")

    print(f"\n  GAPS (Δ = d_{{n+1}} − d_n):")
    print(f"  d#→d#+1:  {'ΔP1':>4} {'ΔP2':>4} {'ΔP3':>4} {'ΔP4':>4} {'ΔP5':>4} {'ΔP6':>4}")
    gap_per_pos = [[] for _ in range(6)]
    for i in range(len(q2) - 1):
        deltas = [pos_series[k][i+1] - pos_series[k][i] for k in range(6)]
        for k in range(6):
            gap_per_pos[k].append(deltas[k])
        print(f"  d{i+1:>2}→d{i+2:<2}:   {deltas[0]:>+4d} {deltas[1]:>+4d} {deltas[2]:>+4d} "
              f"{deltas[3]:>+4d} {deltas[4]:>+4d} {deltas[5]:>+4d}")

    # ── Look for clues ──
    print("\n" + "="*82)
    print("🔍 GAP CLUES")
    print("="*82)

    for k in range(6):
        gaps = gap_per_pos[k]
        gap_counter = Counter(gaps)
        top = gap_counter.most_common(3)
        cum = sum(gaps)
        avg = cum / len(gaps)
        run_max = max(gaps); run_min = min(gaps)
        print(f"\n  P{k+1}: gaps = {gaps}")
        print(f"       cumulative = {cum:+d}  ({pos_series[k][0]} → {pos_series[k][-1]})")
        print(f"       avg = {avg:+.1f}  range = [{run_min}, {run_max}]")
        print(f"       most common gaps: {top}")
        # special markers: ±9, ±21 (Sw-circle), ±25 (Eu-circle), ±7, ±6 (date hide)
        markers = []
        for g in gaps:
            if abs(g) == 9: markers.append(f"±9({g})")
            elif abs(g) == 21: markers.append(f"±21-circle({g})")
            elif abs(g) == 25: markers.append(f"±25({g})")
            elif abs(g) in (6, 7, 8): markers.append(f"678-hide({g})")
            elif g == 0: markers.append("0-FREEZE")
        if markers:
            print(f"       ⚡ markers: {markers}")

    # ── Project d10 from extrapolated gaps (cumulative + last-gap-repeat) ──
    print("\n" + "="*82)
    print("🎯 PROJECTING d10 (Sat 09.05.2026) — multiple methods")
    print("="*82)

    # Method 1: most-frequent gap repeat per position
    print("\n  Method A — Most frequent gap repeat:")
    proj_a = []
    for k in range(6):
        gaps = gap_per_pos[k]
        most = Counter(gaps).most_common(1)[0][0]
        proj_a.append(pos_series[k][-1] + most)
    print(f"    {proj_a}")

    # Method 2: average gap
    print("\n  Method B — Average gap:")
    proj_b = []
    for k in range(6):
        gaps = gap_per_pos[k]
        avg = sum(gaps) / len(gaps)
        proj_b.append(round(pos_series[k][-1] + avg))
    print(f"    {proj_b}")

    # Method 3: last gap repeat
    print("\n  Method C — Last gap repeat:")
    proj_c = []
    for k in range(6):
        last_g = gap_per_pos[k][-1]
        proj_c.append(pos_series[k][-1] + last_g)
    print(f"    {proj_c}")

    # Method 4: median gap
    print("\n  Method D — Median gap:")
    proj_d = []
    for k in range(6):
        gaps = sorted(gap_per_pos[k])
        med = gaps[len(gaps) // 2]
        proj_d.append(pos_series[k][-1] + med)
    print(f"    {proj_d}")

    # Method 5: d-walk pattern — at d9 we're at d#9, what was d8→d9 delta? d10 likely opposite-sign?
    print("\n  Method E — Sign-flip echo (if d8→d9 was +X, d9→d10 ≈ −X):")
    proj_e = []
    for k in range(6):
        last_g = gap_per_pos[k][-1]
        proj_e.append(pos_series[k][-1] - last_g)
    print(f"    {proj_e}")


if __name__ == "__main__":
    asyncio.run(main())
