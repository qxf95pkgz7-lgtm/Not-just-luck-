"""
🪞 CROSS-LOTTERY MIRROR-28 BACKTEST
====================================
Validates: when the rolling 6-draw window (last 3 Eu + last 3 Sw, CARRIER-
EXPANDED) has a half-fired mirror-28 pair, how often does the missing half
land at ANY position in the next 1-2 draws (Eu OR Sw)?

If "owed completions" land >> baseline, the lens has signal worth coding.

Carrier rules:
  Euro n → forms = {n, (n-25) mod 50}
  Swiss m → forms = {m, m-21 if m>21}
"""
import asyncio
from collections import Counter
from year_d_ledger import load_draws


PAIRS_28 = [(1, 27), (2, 26), (3, 25), (4, 24), (5, 23), (6, 22),
            (7, 21), (8, 20), (9, 19), (10, 18), (11, 17), (12, 16),
            (13, 15)]


def expand_eu(n):
    forms = {n}
    c = (n - 25) % 50
    if c == 0:
        c = 50
    forms.add(c)
    return forms


def expand_sw(m):
    forms = {m}
    if m > 21:
        forms.add(m - 21)
    return forms


def expand_pool(eu_draws, sw_draws):
    pool = set()
    for d in eu_draws:
        for n in d["p"]:
            pool |= expand_eu(n)
    for d in sw_draws:
        for n in d["p"]:
            pool |= expand_sw(n)
    return pool


def half_fired(pool):
    """Return list of (a, b, missing) for pairs where exactly one half present."""
    out = []
    for a, b in PAIRS_28:
        a_in = a in pool
        b_in = b in pool
        if a_in != b_in:
            present = a if a_in else b
            missing = b if a_in else a
            out.append((a, b, missing, present))
    return out


def chronological_merge(eu, sw):
    """Merge euro+swiss draws sorted by date with mode tag."""
    merged = []
    for d in eu:
        merged.append({"mode": "eu", **d})
    for d in sw:
        merged.append({"mode": "sw", **d})
    merged.sort(key=lambda x: x["dt"])
    return merged


async def main():
    e = await load_draws("euro")
    s = await load_draws("swiss")
    e.sort(key=lambda x: x["dt"])
    s.sort(key=lambda x: x["dt"])
    merged = chronological_merge(e, s)

    # Restrict to last 2 years for backtest
    cutoff = merged[-1]["dt"].replace(year=merged[-1]["dt"].year - 2)
    merged_2y = [d for d in merged if d["dt"] >= cutoff]
    print(f"Backtest: {len(merged_2y)} draws (last 2 years)")
    print(f"From {merged_2y[0]['date']} to {merged_2y[-1]['date']}")
    print()

    # Walk forward — at each draw_idx, look at last 3 Eu + last 3 Sw before it
    # then check if any half-fired completion lands in next 1 or next 1-2 draws
    n_windows = 0
    n_owed_observations = 0
    n_landed_d1 = 0          # missing fired in next draw
    n_landed_d12 = 0         # missing fired in next 1 OR 2 draws
    n_landed_d3 = 0          # next 3
    landed_breakdown_by_pair = Counter()
    landed_at_eu = 0
    landed_at_sw = 0

    # baseline: pick a random number 1..27 and check if it lands in next 1-2 draws
    # We approximate baseline by scanning rate of any specific 1-27 number landing in next 1-2 draws
    baseline_landed_d12 = 0
    baseline_observations = 0

    # Iterate from draw index 6 forward (need at least 3 of each for window)
    for i in range(0, len(merged_2y) - 2):
        # Build window: last 3 Eu and last 3 Sw BEFORE & up to merged_2y[i]
        prior = merged_2y[: i + 1]
        prior_eu = [d for d in prior if d["mode"] == "eu"][-3:]
        prior_sw = [d for d in prior if d["mode"] == "sw"][-3:]
        if len(prior_eu) < 3 or len(prior_sw) < 3:
            continue
        pool = expand_pool(prior_eu, prior_sw)
        half = half_fired(pool)
        if not half:
            continue
        n_windows += 1

        # Next 1, 2, 3 draws (mode-agnostic chronological)
        next_draws = merged_2y[i + 1 : i + 4]
        if len(next_draws) < 1:
            continue

        # For each missing number, did it land at any pos in next k draws?
        for a, b, missing, present in half:
            n_owed_observations += 1
            # Check d+1
            d1 = next_draws[0]
            d1_pool = expand_eu(missing) if d1["mode"] == "eu" else expand_sw(missing)
            # Wait — check if MISSING (raw) appears in next-draw mains;
            # carrier-form too: e.g. missing=18 in Sw next, also check 18+21=39 OR Eu missing+25
            # Actually the symmetric check: missing landed if missing ∈ next_draw raw mains
            if missing in d1["p"]:
                n_landed_d1 += 1
                n_landed_d12 += 1
                landed_breakdown_by_pair[(a, b)] += 1
                if d1["mode"] == "eu": landed_at_eu += 1
                else: landed_at_sw += 1
                continue
            # carrier echo: if missing+25 ∈ Eu next, OR missing+21 ∈ Sw next, count as carrier-landing
            if d1["mode"] == "eu":
                if (missing + 25) % 50 in d1["p"] or missing in d1["p"]:
                    n_landed_d1 += 1
                    n_landed_d12 += 1
                    landed_breakdown_by_pair[(a, b)] += 1
                    landed_at_eu += 1
                    continue
            else:
                if (missing + 21) in d1["p"]:
                    n_landed_d1 += 1
                    n_landed_d12 += 1
                    landed_breakdown_by_pair[(a, b)] += 1
                    landed_at_sw += 1
                    continue
            # Check d+2 (if exists)
            if len(next_draws) >= 2:
                d2 = next_draws[1]
                if missing in d2["p"]:
                    n_landed_d12 += 1
                    landed_breakdown_by_pair[(a, b)] += 1
                    if d2["mode"] == "eu": landed_at_eu += 1
                    else: landed_at_sw += 1
                    continue
                if d2["mode"] == "eu" and (missing + 25) % 50 in d2["p"]:
                    n_landed_d12 += 1
                    landed_breakdown_by_pair[(a, b)] += 1
                    landed_at_eu += 1
                    continue
                if d2["mode"] == "sw" and (missing + 21) in d2["p"]:
                    n_landed_d12 += 1
                    landed_breakdown_by_pair[(a, b)] += 1
                    landed_at_sw += 1
                    continue
            # d+3 supplement (track separately)
            if len(next_draws) >= 3:
                d3 = next_draws[2]
                if missing in d3["p"] or \
                   (d3["mode"] == "eu" and (missing + 25) % 50 in d3["p"]) or \
                   (d3["mode"] == "sw" and (missing + 21) in d3["p"]):
                    n_landed_d3 += 1

    # ── BASELINE: pick a fixed number (say each 1..27), measure rate it lands in any next 1-2 draws ──
    # Sample baseline: average rate that ANY number in 1..27 lands (raw or carrier-equivalent)
    # in next 1-2 draws taken across all positions in the timeline
    for i in range(0, len(merged_2y) - 2):
        next2 = merged_2y[i + 1 : i + 3]
        if len(next2) < 2:
            continue
        for tgt in range(1, 28):
            baseline_observations += 1
            for nd in next2:
                hit = False
                if tgt in nd["p"]:
                    hit = True
                elif nd["mode"] == "eu" and (tgt + 25) % 50 in nd["p"]:
                    hit = True
                elif nd["mode"] == "sw" and (tgt + 21) in nd["p"]:
                    hit = True
                if hit:
                    baseline_landed_d12 += 1
                    break

    print("=" * 80)
    print(f"📊 BACKTEST RESULTS")
    print("=" * 80)
    print(f"  Windows scanned (had ≥1 half-fired pair):  {n_windows}")
    print(f"  Total owed-completion observations:        {n_owed_observations}")
    print(f"\n  Landed in NEXT draw (raw or carrier):       {n_landed_d1}  ({100*n_landed_d1/max(n_owed_observations,1):.1f}%)")
    print(f"  Landed in NEXT 1-2 draws:                   {n_landed_d12}  ({100*n_landed_d12/max(n_owed_observations,1):.1f}%)")
    print(f"  Additional landings in d+3:                 {n_landed_d3}")
    print(f"\n  ⚖ BASELINE (any 1..27 # in next 1-2 draws): {100*baseline_landed_d12/max(baseline_observations,1):.1f}%")
    print(f"\n  🚨 LIFT vs baseline:                        {(100*n_landed_d12/max(n_owed_observations,1)) / (100*baseline_landed_d12/max(baseline_observations,1)):.2f}×")
    print()
    print(f"  Distribution of landings (Eu vs Sw):")
    print(f"    landed at Eu next: {landed_at_eu}")
    print(f"    landed at Sw next: {landed_at_sw}")
    print()
    print(f"  Pairs with most owed-→-landed events (top 10):")
    for pair, ct in landed_breakdown_by_pair.most_common(10):
        print(f"    ({pair[0]:2}, {pair[1]:2})  →  {ct} landings")


if __name__ == "__main__":
    asyncio.run(main())
