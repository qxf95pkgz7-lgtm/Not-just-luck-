"""
🍀↔R DEEP PROBE — does R point to a SILENT/HUNGRY main? Does 🍀 indicate
                   discharge through a position-class?

We test:
 1. R hot/cold context — was R silent (no mains hit) in the previous 6/12 draws?
 2. R-fired-then-silent: when R was a recent main and now silent, is it more
    likely to fire as a NEXT main?
 3. Does 🍀 cluster with the ABSENT family at draw time?
 4. 🍀 as position-class hint: when 🍀 is small (1-2), does ND get a low-band
    P1? When 🍀 is large (5-6), does ND get a high-band P5/P6?
 5. R + 🍀 "story sum" — when sum is 13, does 13 (or n=13 family) land?
"""
import asyncio
from collections import Counter, defaultdict
from datetime import datetime

from year_d_ledger import load_draws


def family_of_swiss(n: int) -> str:
    if 1 <= n <= 9: return "1-9"
    if 10 <= n <= 19: return "10s"
    if 20 <= n <= 29: return "20s"
    if 30 <= n <= 39: return "30s"
    return "40-42"


def main():
    asyncio.run(_run())


async def _run():
    draws = await load_draws("swiss")
    cutoff = datetime(2024, 5, 9)
    recent = [d for d in draws if d["dt"] >= cutoff]
    recent.sort(key=lambda d: d["dt"])
    n = len(recent)
    print(f"\n🎻 SWISS 🍀↔R DEEP PROBE — {n} draws\n")

    # 1️⃣  Was R silent (not a main) in the previous 6 / 12 draws?
    r_silent_6 = 0
    r_silent_12 = 0
    r_silent_then_in_next = 0
    r_silent_total = 0
    valid = 0
    for i, d in enumerate(recent):
        R = d.get("replay")
        if R is None:
            continue
        if i < 12: continue
        valid += 1
        prev6 = recent[i-6:i]
        prev12 = recent[i-12:i]
        in_prev6 = any(R in p["p"] for p in prev6)
        in_prev12 = any(R in p["p"] for p in prev12)
        if not in_prev6:
            r_silent_6 += 1
        if not in_prev12:
            r_silent_12 += 1
            r_silent_total += 1
            if i + 1 < len(recent) and R in recent[i+1]["p"]:
                r_silent_then_in_next += 1

    print(f"1️⃣ R SILENT-CONTEXT (R was NOT a main in prev N draws):")
    print(f"   prev-6 silent:  {r_silent_6}/{valid}  = {100*r_silent_6/max(1,valid):.1f}%")
    print(f"   prev-12 silent: {r_silent_12}/{valid} = {100*r_silent_12/max(1,valid):.1f}%")
    print(f"   ⇒ When R was 12-silent, R fires in NEXT mains: "
          f"{r_silent_then_in_next}/{r_silent_total} = "
          f"{100*r_silent_then_in_next/max(1,r_silent_total):.1f}%")

    # 2️⃣  Did 🍀 anticipate the absent family?
    print(f"\n2️⃣ DOES 🍀 CLUSTER WITH ABSENT FAMILY?")
    lucky_to_family_starved = Counter()
    lucky_to_family_overfed = Counter()
    for d in recent:
        L = d.get("lucky"); P = d["p"]
        if L is None: continue
        fams = Counter(family_of_swiss(x) for x in P)
        starved = [f for f in ("1-9", "10s", "20s", "30s", "40-42") if fams.get(f, 0) == 0]
        most_fed = max(fams.items(), key=lambda x: x[1])[0] if fams else None
        for s in starved:
            lucky_to_family_starved[(L, s)] += 1
        if most_fed:
            lucky_to_family_overfed[(L, most_fed)] += 1
    # bucket: most common 🍀↔starved-family pair
    print(f"   Top 🍀↔STARVED family pairs:")
    for (L, fam), c in lucky_to_family_starved.most_common(8):
        print(f"     🍀={L} starved={fam}  ×{c}")

    # 3️⃣  🍀 size → ND P1/P5 size?
    print(f"\n3️⃣ 🍀 SIZE → NEXT-DRAW POSITION SIZE:")
    nd_p1_by_lucky = defaultdict(list)
    nd_p6_by_lucky = defaultdict(list)
    for i in range(len(recent) - 1):
        L = recent[i].get("lucky")
        if L is None: continue
        nd = recent[i + 1]["p"]
        if len(nd) >= 1:
            nd_p1_by_lucky[L].append(nd[0])
        if len(nd) >= 6:
            nd_p6_by_lucky[L].append(nd[5])
    for L in range(1, 7):
        p1s = nd_p1_by_lucky.get(L, [])
        p6s = nd_p6_by_lucky.get(L, [])
        if p1s:
            print(f"   🍀={L}: ND P1 mean={sum(p1s)/len(p1s):.1f}, "
                  f"P6 mean={sum(p6s)/max(1,len(p6s)):.1f}, n={len(p1s)}")

    # 4️⃣ Sum=13 — does n=13 (or its family) land in the SAME draw or NEXT?
    print(f"\n4️⃣ SUM=13 STORY (🍀+R = 13):")
    sum13_n = 0
    sum13_13_in_same = 0
    sum13_13_in_next = 0
    sum13_low_band_p1 = 0  # P1 ≤ 7 (the snap-back zone)
    for i, d in enumerate(recent):
        L = d.get("lucky"); R = d.get("replay")
        if L is None or R is None: continue
        if L + R != 13: continue
        sum13_n += 1
        if 13 in d["p"]: sum13_13_in_same += 1
        if i + 1 < len(recent) and 13 in recent[i + 1]["p"]:
            sum13_13_in_next += 1
        if d["p"][0] <= 7:
            sum13_low_band_p1 += 1
    print(f"   sum=13 cases: {sum13_n}")
    print(f"   13 in SAME mains:  {sum13_13_in_same}/{sum13_n} = "
          f"{100*sum13_13_in_same/max(1,sum13_n):.1f}%")
    print(f"   13 in NEXT mains:  {sum13_13_in_next}/{sum13_n} = "
          f"{100*sum13_13_in_next/max(1,sum13_n):.1f}%")
    print(f"   P1 ≤ 7 in same:    {sum13_low_band_p1}/{sum13_n} = "
          f"{100*sum13_low_band_p1/max(1,sum13_n):.1f}%")

    # 5️⃣ When R was a main 1-2 draws ago, does it RE-fire next?
    print(f"\n5️⃣ R RECENT-MAIN ECHO:")
    r_main_1d_ago = 0
    r_main_1d_ago_then_next = 0
    r_main_2d_ago = 0
    r_main_2d_ago_then_next = 0
    for i in range(2, len(recent) - 1):
        R = recent[i].get("replay")
        if R is None: continue
        if R in recent[i-1]["p"]:
            r_main_1d_ago += 1
            if R in recent[i+1]["p"]:
                r_main_1d_ago_then_next += 1
        if R in recent[i-2]["p"]:
            r_main_2d_ago += 1
            if R in recent[i+1]["p"]:
                r_main_2d_ago_then_next += 1
    print(f"   R was main 1d ago: {r_main_1d_ago}, then ND: "
          f"{r_main_1d_ago_then_next}/{r_main_1d_ago} = "
          f"{100*r_main_1d_ago_then_next/max(1,r_main_1d_ago):.1f}%")
    print(f"   R was main 2d ago: {r_main_2d_ago}, then ND: "
          f"{r_main_2d_ago_then_next}/{r_main_2d_ago} = "
          f"{100*r_main_2d_ago_then_next/max(1,r_main_2d_ago):.1f}%")

    # 6️⃣ |R−🍀| as next-draw GAP! (gap-rhythm carrier)
    print(f"\n6️⃣ |R−🍀| AS NEXT-DRAW GAP:")
    gap_match = 0
    valid_gap = 0
    for i in range(len(recent) - 1):
        L = recent[i].get("lucky"); R = recent[i].get("replay")
        if L is None or R is None: continue
        valid_gap += 1
        delta = abs(R - L)
        nd = recent[i+1]["p"]
        gaps = [nd[k+1] - nd[k] for k in range(len(nd)-1)]
        if delta in gaps:
            gap_match += 1
    print(f"   |R−🍀| appears as gap in NEXT draw: {gap_match}/{valid_gap} = "
          f"{100*gap_match/max(1,valid_gap):.1f}%")


if __name__ == "__main__":
    main()
