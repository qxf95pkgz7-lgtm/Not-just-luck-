"""
🎻 TIGHT-SIGNAL PROBE — under WHAT conditions does the cross-mirror-28
   half-fired completion BEAT baseline?

   Hypothesis: lens is CONFIRMATION not discovery. Strong when:
     a) pool is almost-discharged (≤ 2 owed pairs)
     b) the present half is multi-source (raw on BOTH lotteries, OR raw+carrier)
     c) the missing half is in a STARVED ones-digit family (Q-tablet hungry)
     d) the present half itself JUST fired (gap=1 from one of the windowed draws)
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
    if c == 0: c = 50
    forms.add(c)
    return forms


def expand_sw(m):
    forms = {m}
    if m > 21:
        forms.add(m - 21)
    return forms


def expand_pool(eu_draws, sw_draws):
    pool = set()
    sources = {}  # number → set of (mode, type) tags
    for d in eu_draws:
        for n in d["p"]:
            pool.add(n)
            sources.setdefault(n, set()).add(("eu", "raw"))
            c = (n - 25) % 50 or 50
            pool.add(c)
            sources.setdefault(c, set()).add(("eu", "carrier"))
    for d in sw_draws:
        for n in d["p"]:
            pool.add(n)
            sources.setdefault(n, set()).add(("sw", "raw"))
            if n > 21:
                pool.add(n - 21)
                sources.setdefault(n - 21, set()).add(("sw", "carrier"))
    return pool, sources


def half_fired(pool, sources):
    out = []
    for a, b in PAIRS_28:
        a_in = a in pool; b_in = b in pool
        if a_in != b_in:
            present = a if a_in else b
            missing = b if a_in else a
            out.append((a, b, missing, present, sources[present]))
    return out


def merge_chrono(e, s):
    merged = []
    for d in e: merged.append({"mode": "eu", **d})
    for d in s: merged.append({"mode": "sw", **d})
    merged.sort(key=lambda x: x["dt"])
    return merged


async def main():
    e = await load_draws("euro"); s = await load_draws("swiss")
    e.sort(key=lambda x: x["dt"]); s.sort(key=lambda x: x["dt"])
    merged = merge_chrono(e, s)
    cutoff = merged[-1]["dt"].replace(year=merged[-1]["dt"].year - 2)
    merged = [d for d in merged if d["dt"] >= cutoff]

    # Categories to test
    cats = {
        "all":                   {"obs": 0, "hit_d12": 0},
        "tight_pool (≤2 owed)":  {"obs": 0, "hit_d12": 0},
        "tight_pool (≤3 owed)":  {"obs": 0, "hit_d12": 0},
        "present_multi_src (≥2 sources)": {"obs": 0, "hit_d12": 0},
        "present_3_sources":     {"obs": 0, "hit_d12": 0},
        "present_eu_AND_sw":     {"obs": 0, "hit_d12": 0},
        "present_raw_AND_carrier": {"obs": 0, "hit_d12": 0},
        "missing_in_starved_family": {"obs": 0, "hit_d12": 0},
    }

    # baseline
    baseline_obs = 0
    baseline_hit = 0

    for i in range(0, len(merged) - 2):
        prior = merged[: i + 1]
        prior_eu = [d for d in prior if d["mode"] == "eu"][-3:]
        prior_sw = [d for d in prior if d["mode"] == "sw"][-3:]
        if len(prior_eu) < 3 or len(prior_sw) < 3: continue
        pool, sources = expand_pool(prior_eu, prior_sw)
        half = half_fired(pool, sources)
        next2 = merged[i + 1 : i + 3]
        if len(next2) < 1: continue

        # ones-digit hunger detection (rough): which ones-digits are silent in last 6 draws?
        played = set()
        for d in prior_eu + prior_sw:
            for n in d["p"]: played.add(n)
        family_starvation = {}
        for ones in range(10):
            members = [x for x in range(1, 28) if x % 10 == ones]
            missed = [m for m in members if m not in played]
            family_starvation[ones] = len(missed) / max(len(members), 1)

        # Ladders (5+ in same decade in 1-27)
        n_owed = len(half)

        for a, b, missing, present, src in half:
            # check landing in next 1-2 draws
            landed = False
            for nd in next2:
                if missing in nd["p"]:
                    landed = True; break
                if nd["mode"] == "eu" and (missing + 25) % 50 in nd["p"]:
                    landed = True; break
                if nd["mode"] == "sw" and (missing + 21) in nd["p"]:
                    landed = True; break

            cats["all"]["obs"] += 1
            if landed: cats["all"]["hit_d12"] += 1

            if n_owed <= 2:
                cats["tight_pool (≤2 owed)"]["obs"] += 1
                if landed: cats["tight_pool (≤2 owed)"]["hit_d12"] += 1
            if n_owed <= 3:
                cats["tight_pool (≤3 owed)"]["obs"] += 1
                if landed: cats["tight_pool (≤3 owed)"]["hit_d12"] += 1

            if len(src) >= 2:
                cats["present_multi_src (≥2 sources)"]["obs"] += 1
                if landed: cats["present_multi_src (≥2 sources)"]["hit_d12"] += 1
            if len(src) >= 3:
                cats["present_3_sources"]["obs"] += 1
                if landed: cats["present_3_sources"]["hit_d12"] += 1

            modes = {x[0] for x in src}
            types = {x[1] for x in src}
            if "eu" in modes and "sw" in modes:
                cats["present_eu_AND_sw"]["obs"] += 1
                if landed: cats["present_eu_AND_sw"]["hit_d12"] += 1
            if "raw" in types and "carrier" in types:
                cats["present_raw_AND_carrier"]["obs"] += 1
                if landed: cats["present_raw_AND_carrier"]["hit_d12"] += 1

            ones = missing % 10
            if family_starvation[ones] >= 0.6:
                cats["missing_in_starved_family"]["obs"] += 1
                if landed: cats["missing_in_starved_family"]["hit_d12"] += 1

        # baseline: random 1..27 land rate in next 1-2 draws
        for tgt in range(1, 28):
            baseline_obs += 1
            for nd in next2:
                if tgt in nd["p"] or \
                   (nd["mode"]=="eu" and (tgt+25)%50 in nd["p"]) or \
                   (nd["mode"]=="sw" and (tgt+21) in nd["p"]):
                    baseline_hit += 1; break

    base_rate = 100 * baseline_hit / max(baseline_obs, 1)
    print("=" * 86)
    print(f"🪞 TIGHT-SIGNAL PROBE — landing rate in next 1-2 draws by lens condition")
    print("=" * 86)
    print(f"  ⚖ BASELINE rate (any # 1..27 in next 1-2 draws): {base_rate:.1f}%")
    print()
    print(f"  {'CONDITION':45} {'N':>6}  {'HIT':>5}  {'RATE':>6}  {'LIFT':>5}")
    print("  " + "-" * 80)
    for name, c in cats.items():
        rate = 100 * c["hit_d12"] / max(c["obs"], 1)
        lift = rate / base_rate if base_rate > 0 else 0
        marker = " 🔥" if lift >= 1.20 else (" 🟡" if lift >= 1.05 else "")
        print(f"  {name:45} {c['obs']:6}  {c['hit_d12']:5}  {rate:5.1f}%  {lift:5.2f}×{marker}")


if __name__ == "__main__":
    asyncio.run(main())
