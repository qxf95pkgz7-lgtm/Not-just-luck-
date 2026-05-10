"""
🌌 SAME-POSITION CROSS-DRAW GAP CANON
======================================
DJ S38: "did you find the 9 in the gap from p6 and p6 db?"

For Sw BD-1 06.05 → ND 09.05:
  P1:  22 → 11   gap = −11
  P2:  28 → 12   gap = −16
  P3:  33 → 24   gap = −9   ★
  P4:  34 → 25   gap = −9   ★
  P5:  38 → 29   gap = −9   ★
  P6:  40 → 31   gap = −9   ★

🚨 FOUR POSITIONS (P3-P6) ALL SHIFTED EXACTLY −9.
The 9-clock fired as a UNIFORM POSITIONAL SHIFT, not as a raw number!

Probe last 10 d for Sw and Eu — find canon stability + Eu↔Sw comparison.
"""
import asyncio
from collections import Counter
from year_d_ledger import load_draws


def per_pos_gaps(prev_p, next_p):
    n = min(len(prev_p), len(next_p))
    return [next_p[i] - prev_p[i] for i in range(n)]


async def main():
    e = await load_draws("euro")
    s = await load_draws("swiss")
    e.sort(key=lambda x: x["dt"]); s.sort(key=lambda x: x["dt"])

    print("="*82)
    print("🌌 SWISS — last 10 transitions, per-position cross-draw gaps")
    print("="*82)
    last_sw = s[-11:]
    print(f"  {'BD→ND':30s} {'ΔP1':>4s} {'ΔP2':>4s} {'ΔP3':>4s} {'ΔP4':>4s} {'ΔP5':>4s} {'ΔP6':>4s}  notes")
    sw_uniform_count = Counter()
    for i in range(len(last_sw) - 1):
        bd, nd = last_sw[i], last_sw[i + 1]
        gaps = per_pos_gaps(bd["p"], nd["p"])
        # uniform shift = 3+ positions with same gap
        c = Counter(gaps)
        most_common, freq = c.most_common(1)[0]
        notes = ""
        if freq >= 3:
            notes = f"UNIFORM-{most_common:+d} on {freq} positions"
            sw_uniform_count[(most_common, freq)] += 1
        # 9-signal scan
        nines = [g for g in gaps if abs(g) == 9]
        if nines:
            notes += f"  9-gap×{len(nines)}"
        bd_lbl = f"{bd['date']}→{nd['date']}"
        print(f"  {bd_lbl:30s} {gaps[0]:>+4d} {gaps[1]:>+4d} {gaps[2]:>+4d} {gaps[3]:>+4d} {gaps[4]:>+4d} {gaps[5]:>+4d}  {notes}")

    print(f"\n  📊 SW UNIFORM-SHIFT events (≥3 positions same gap): {dict(sw_uniform_count)}")

    print("\n" + "="*82)
    print("🌌 EURO — last 10 transitions, per-position cross-draw gaps")
    print("="*82)
    last_eu = e[-11:]
    print(f"  {'BD→ND':30s} {'ΔP1':>4s} {'ΔP2':>4s} {'ΔP3':>4s} {'ΔP4':>4s} {'ΔP5':>4s}  notes")
    eu_uniform_count = Counter()
    for i in range(len(last_eu) - 1):
        bd, nd = last_eu[i], last_eu[i + 1]
        gaps = per_pos_gaps(bd["p"], nd["p"])
        c = Counter(gaps)
        most_common, freq = c.most_common(1)[0]
        notes = ""
        if freq >= 3:
            notes = f"UNIFORM-{most_common:+d} on {freq}"
            eu_uniform_count[(most_common, freq)] += 1
        nines = [g for g in gaps if abs(g) == 9]
        if nines:
            notes += f"  9-gap×{len(nines)}"
        bd_lbl = f"{bd['date']}→{nd['date']}"
        print(f"  {bd_lbl:30s} {gaps[0]:>+4d} {gaps[1]:>+4d} {gaps[2]:>+4d} {gaps[3]:>+4d} {gaps[4]:>+4d}  {notes}")

    print(f"\n  📊 EU UNIFORM-SHIFT events: {dict(eu_uniform_count)}")

    # ── Eu LD position-by-position vs SW LD ──
    print("\n" + "="*82)
    print("🪞 LAST DRAW: Eu 08.05 vs Sw 09.05 — POSITIONAL CROSS-LOTTERY")
    print("="*82)
    eu_ld = next((d for d in e if d["date"] == "08.05.2026"), None)
    sw_ld = next((d for d in s if d["date"] == "09.05.2026"), None)
    if eu_ld and sw_ld:
        print(f"  Eu 08.05  P1=2  P2=17  P3=19  P4=34  P5=37   ⭐[8,11]")
        print(f"  Sw 09.05  P1=11 P2=12  P3=24  P4=25  P5=29  P6=31  🍀2 R:1")
        print()
        print(f"  Pos-by-pos Sw − Eu (Sw mains − 21 to align):")
        print(f"  P1: 11 − 2  = +9   ← THE 9!")
        print(f"  P2: 12 − 17 = −5")
        print(f"  P3: 24 − 19 = +5")
        print(f"  P4: 25 − 34 = −9   ← THE 9!")
        print(f"  P5: 29 − 37 = −8")
        print(f"  P6: 31 − ?  (no Eu P6)")
        print()
        print(f"  Sw 09.05 mains − 21 → Eu shadow: [{11-21}, {12-21}, {24-21}, {25-21}, {29-21}, {31-21}] = [-10, -9, 3, 4, 8, 10]")
        print(f"  Wraps: [32, 33, 3, 4, 8, 10]")
        print(f"  Compare to Eu 08.05 [2, 17, 19, 34, 37]:")
        print(f"    3  ↔ 2 (±1)         ★ 1-cousin")
        print(f"    8  ↔ ⭐8 RAW MATCH  ★★★")
        print(f"    10 ↔ 17 (-7)         family-7?")
        print(f"    32 ↔ 34 (-2)        ★")
        print(f"    33 ↔ 34 (-1)        ★")

    # ── 9-SIGNAL DENSITY in 1-yr historical Swiss ──
    print("\n" + "="*82)
    print("🎯 9-GAP DENSITY in same-position transitions (last 1 yr, Swiss)")
    print("="*82)
    yr_sw = [d for d in s if d["dt"].year >= 2025]
    nine_pos_counter = Counter()
    total = 0
    for i in range(len(yr_sw) - 1):
        bd, nd = yr_sw[i], yr_sw[i + 1]
        gaps = per_pos_gaps(bd["p"], nd["p"])
        for k, g in enumerate(gaps):
            total += 1
            if abs(g) == 9:
                nine_pos_counter[k + 1] += 1
    print(f"  9-gap occurrences per position (last yr Swiss):")
    for p in range(1, 7):
        print(f"    P{p}: {nine_pos_counter.get(p, 0)}")
    print(f"  Total transitions scanned: {total // 6}")
    print(f"  Total 9-gaps across all positions: {sum(nine_pos_counter.values())}")
    print(f"  Baseline (random): expected ~{total / 42:.1f} (assuming uniform gap distribution in -41..+41)")

    # ── Apply 9-uniform-shift forecast to next Eu (Tue 12.05) ──
    print("\n" + "="*82)
    print("🎯 PROJECTING Tue 12.05 EU using uniform-shift canons")
    print("="*82)
    if eu_ld:
        for shift in (-9, +9, -5, +5, -3, +3):
            shifted = [max(1, min(50, p + shift)) for p in eu_ld["p"]]
            print(f"  Eu 08.05 + ({shift:+d}) shift = {shifted}")
        # Apply Sw's just-played -9 uniform shift to Eu
        print()
        print(f"  Sw 09.05 carried a -9 uniform shift across P3-P6.")
        print(f"  If Eu mirrors this on its NEXT transition (12.05):")
        print(f"  Eu 08.05 [2, 17, 19, 34, 37] ⭐[8, 11]")
        print(f"  Apply -9 to all: [-7, 8, 10, 25, 28] (P1 wraps invalid)")
        print(f"  Apply mixed -9/-5: P1=2 stays, P2-P5: [12, 14, 25, 28] or [13, 14, 29, 32]")


if __name__ == "__main__":
    asyncio.run(main())
