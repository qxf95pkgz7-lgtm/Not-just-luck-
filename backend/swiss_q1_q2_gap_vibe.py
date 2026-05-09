"""
Swiss Q1 2026 PER-POSITION GAP WALK + Q1↔Q2 GAP VIBE PATTERN
==============================================================
DJ: "Check gap q1 learn the vibe, make let's have a gap pattern"

We compute the same per-position gaps for Q1 and lay them next to Q2.
Goal: find the per-position rhythm signature (the "vibe") of how the
cosmos moves each P-slot d-by-d, and codify it as a canon.
"""
import asyncio
from collections import Counter
from year_d_ledger import load_draws


async def main():
    s = await load_draws("swiss")
    s.sort(key=lambda x: x["dt"])

    # Swiss Q1 starts ~02.01 (no skip per Book canon for Swiss Q1?)
    q1 = [d for d in s if d["year"] == 2026 and d["quarter"] == 1]
    q2 = [d for d in s if d["year"] == 2026 and d["quarter"] == 2]

    print("🍀 SWISS Q1 2026 LEDGER:")
    print("="*82)
    for i, d in enumerate(q1, 1):
        print(f"  d{i:2d}  {d['date']}  {d['wd']:3s}  {d['p']}  🍀{d.get('lucky')} R:{d.get('replay')}")

    def gap_walk(quarter):
        pos = [[] for _ in range(6)]
        for d in quarter:
            for k in range(6):
                pos[k].append(d["p"][k] if k < len(d["p"]) else None)
        gaps = [[] for _ in range(6)]
        for k in range(6):
            for i in range(len(quarter) - 1):
                gaps[k].append(pos[k][i + 1] - pos[k][i])
        return pos, gaps

    q1_pos, q1_gaps = gap_walk(q1)
    q2_pos, q2_gaps = gap_walk(q2)

    print(f"\n  Q1 gaps per position ({len(q1)-1} transitions):")
    for k in range(6):
        print(f"    P{k+1}: {q1_gaps[k]}")

    print(f"\n  Q2 gaps per position ({len(q2)-1} transitions):")
    for k in range(6):
        print(f"    P{k+1}: {q2_gaps[k]}")

    # ── Vibe analysis ──
    print("\n" + "="*82)
    print("🎼 VIBE PATTERN — combined Q1 + Q2 stats per position")
    print("="*82)

    for k in range(6):
        all_gaps = q1_gaps[k] + q2_gaps[k]
        if not all_gaps:
            continue
        # ±6, ±7, ±8 (678 hide) tally
        h678 = sum(1 for g in all_gaps if abs(g) in (6, 7, 8))
        # ±9 tally
        h9 = sum(1 for g in all_gaps if abs(g) == 9)
        # 0 freeze
        h0 = sum(1 for g in all_gaps if g == 0)
        # sign distribution
        pos_n = sum(1 for g in all_gaps if g > 0)
        neg_n = sum(1 for g in all_gaps if g < 0)
        avg = sum(all_gaps) / len(all_gaps)
        # signature: most common 3
        top3 = Counter(all_gaps).most_common(3)
        # range
        mn, mx = min(all_gaps), max(all_gaps)
        # alternation count: how often does sign flip between consecutive transitions
        flips = sum(1 for i in range(1, len(all_gaps)) if all_gaps[i] * all_gaps[i-1] < 0)
        flip_pct = 100 * flips / max(1, len(all_gaps) - 1)

        print(f"\n  P{k+1}:  n={len(all_gaps)}  range=[{mn}, {mx}]  avg={avg:+.2f}")
        print(f"        678-hide gaps (±6,±7,±8): {h678}/{len(all_gaps)} = "
              f"{100*h678/len(all_gaps):.1f}%")
        print(f"        ±9 gaps: {h9}  · 0-freeze: {h0}")
        print(f"        sign distribution: + = {pos_n}, − = {neg_n}")
        print(f"        sign-FLIP rate: {flips}/{len(all_gaps)-1} = {flip_pct:.1f}%")
        print(f"        top 3 gaps: {top3}")

    # ── Sign-flip-after-large-jump rule test ──
    print("\n" + "="*82)
    print("🪞 SIGN-FLIP RULE: after a |gap| ≥ 10, does next gap flip sign?")
    print("="*82)
    for k in range(6):
        all_gaps = q1_gaps[k] + q2_gaps[k]
        big = []
        for i in range(len(all_gaps) - 1):
            if abs(all_gaps[i]) >= 10:
                big.append((all_gaps[i], all_gaps[i + 1],
                            all_gaps[i] * all_gaps[i + 1] < 0))
        if big:
            flipped = sum(1 for _, _, f in big if f)
            print(f"  P{k+1}: {len(big)} large jumps, "
                  f"flip-back rate = {flipped}/{len(big)} = "
                  f"{100*flipped/len(big):.1f}%")
            for prev, nxt, fl in big:
                tag = "✓ flipped" if fl else "✗ same-sign"
                print(f"     prev={prev:+d}  next={nxt:+d}  {tag}")

    # ── ±6 P2 rhythm test on Q1 ──
    print("\n" + "="*82)
    print("🎯 ±6 P2 RHYTHM TEST (Q1 + Q2)")
    print("="*82)
    p2_combined = q1_gaps[1] + q2_gaps[1]
    p2_6 = sum(1 for g in p2_combined if abs(g) == 6)
    print(f"  P2 ±6 hits: {p2_6}/{len(p2_combined)} = "
          f"{100*p2_6/max(1,len(p2_combined)):.1f}%")
    print(f"  Q1 P2 gaps: {q1_gaps[1]}")
    print(f"  Q2 P2 gaps: {q2_gaps[1]}")

    # ── Cumulative drift (Q1 vs Q2) ──
    print("\n" + "="*82)
    print("📈 CUMULATIVE DRIFT per position (Q1 vs Q2)")
    print("="*82)
    print(f"  {'Pos':3s} {'Q1 first→last':18s} {'Q1 cum':>7s}  {'Q2 first→last':18s} {'Q2 cum':>7s}")
    for k in range(6):
        if not q1_pos[k] or not q2_pos[k]:
            continue
        q1_first, q1_last = q1_pos[k][0], q1_pos[k][-1]
        q2_first, q2_last = q2_pos[k][0], q2_pos[k][-1]
        q1_cum = q1_last - q1_first
        q2_cum = q2_last - q2_first
        print(f"  P{k+1}  {q1_first:>2d}→{q1_last:>2d} (Δ{q1_cum:+d})       "
              f"{q1_cum:+>5d}    {q2_first:>2d}→{q2_last:>2d} (Δ{q2_cum:+d})       "
              f"{q2_cum:+>5d}")

    # ── d-by-d alignment Q1 vs Q2 (same d-position) ──
    print("\n" + "="*82)
    print("🪞 SAME-d PATTERN: Q1d_n vs Q2d_n positional comparison")
    print("="*82)
    print(f"  {'d#':3s}  {'Q1 P1':>5s}  {'Q2 P1':>5s} | {'Q1 P6':>5s}  {'Q2 P6':>5s}")
    for i in range(min(len(q1), len(q2))):
        print(f"  d{i+1:>2}  {q1_pos[0][i]:>5d}  {q2_pos[0][i]:>5d}  | "
              f"{q1_pos[5][i]:>5d}  {q2_pos[5][i]:>5d}")


if __name__ == "__main__":
    asyncio.run(main())
