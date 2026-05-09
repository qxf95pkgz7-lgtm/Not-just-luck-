"""
🎻 SWISS POST-BD STATS for d10 09.05.2026 prep
================================================
DJ asks:
  1. Last draw 06.05 family sig = 2-3-1 (back-loaded, no 1-9/10s).
     What does ND historically look like after this signature?
  2. Last P1 = 22 (P1 > 21). What history says about ND when previous
     P1 was high (>21)?
"""
import asyncio
from collections import Counter, defaultdict
from year_d_ledger import load_draws


def family_of(n: int) -> str:
    if 1 <= n <= 9: return "1-9"
    if 10 <= n <= 19: return "10s"
    if 20 <= n <= 29: return "20s"
    if 30 <= n <= 39: return "30s"
    return "40-42"


def signature_inorder(p):
    """Return tuple (c1-9, c10s, c20s, c30s, c40-42)."""
    c = Counter(family_of(n) for n in p)
    return (c.get("1-9", 0), c.get("10s", 0), c.get("20s", 0),
            c.get("30s", 0), c.get("40-42", 0))


def signature_str(sig):
    parts = [str(c) for c in sig if c > 0]
    return "-".join(parts)


async def main():
    s = await load_draws("swiss")
    s.sort(key=lambda x: x["dt"])
    print(f"🍀 Swiss total draws: {len(s)}\n")

    # Q2 d9 = 06.05.2026
    target_bd = next(d for d in s if d["date"] == "06.05.2026")
    bd_sig = signature_inorder(target_bd["p"])
    print(f"BD (06.05.2026) mains: {target_bd['p']}")
    print(f"  in-order signature: {bd_sig}  → '{signature_str(bd_sig)}'")
    print(f"  P1 = {target_bd['p'][0]}  (>21 trigger)\n")

    # ── Q1: history of FAMILY SIG 0-0-2-3-1 (or simply (0,0,2,3,1)) ──
    print("="*78)
    print("📊 Q1 — ND after BD with sig (0,0,2,3,1) (back-loaded triple-30s)")
    print("="*78)
    matched = []
    for i, d in enumerate(s[:-1]):
        if signature_inorder(d["p"]) == bd_sig:
            matched.append((i, d, s[i+1]))
    print(f"Found {len(matched)} historical BDs with same in-order sig (0,0,2,3,1):\n")
    pos_freq = [Counter() for _ in range(6)]
    nd_sigs = Counter()
    nd_p1s = []
    for _, bd, nd in matched[-30:]:
        nd_sig = signature_inorder(nd["p"])
        print(f"  BD {bd['date']}({bd['wd'][:3]}) {bd['p']} → ND {nd['date']}({nd['wd'][:3]}) {nd['p']}  sig→'{signature_str(nd_sig)}'")
        nd_sigs[signature_str(nd_sig)] += 1
        if nd["p"]:
            nd_p1s.append(nd["p"][0])
        for k, val in enumerate(nd["p"][:6]):
            pos_freq[k][val] += 1
    if matched:
        print(f"\n  ND sig top 5:")
        for sig, c in nd_sigs.most_common(5):
            print(f"    '{sig}' × {c}  ({100*c/len(matched):.1f}%)")
        print(f"\n  ND P-position TOP-5:")
        for k in range(6):
            top = pos_freq[k].most_common(5)
            print(f"    P{k+1}: {top}")
        if nd_p1s:
            print(f"  ND P1 mean = {sum(nd_p1s)/len(nd_p1s):.1f}, min={min(nd_p1s)}, max={max(nd_p1s)}")

    # ── Q2: history of P1 > 21 → ND ──
    print("\n" + "="*78)
    print("📊 Q2 — ND when previous P1 > 21 (snap-back trigger)")
    print("="*78)
    snap = []
    for i, d in enumerate(s[:-1]):
        if d["p"][0] > 21:
            snap.append((i, d, s[i+1]))
    print(f"Found {len(snap)} cases of P1>21 → ND in {len(s)} Swiss draws "
          f"({100*len(snap)/len(s):.1f}%)\n")

    # Stats on next P1
    nd_p1_band = Counter()
    nd_p1s = []
    nd_p5s = []
    nd_p6s = []
    nd_sums = []
    nd_lucky = Counter()
    nd_replay = Counter()
    nd_has_9 = 0
    nd_has_38 = 0
    nd_has_27 = 0
    nd_has_16 = 0
    nd_has_10 = 0
    nd_has_39 = 0
    nd_p1_eq_9 = 0
    same_weekday = []
    nd_count = len(snap)
    for _, bd, nd in snap:
        p1 = nd["p"][0]
        nd_p1s.append(p1)
        if 1 <= p1 <= 5: nd_p1_band["1-5"] += 1
        elif 6 <= p1 <= 10: nd_p1_band["6-10"] += 1
        elif 11 <= p1 <= 15: nd_p1_band["11-15"] += 1
        elif 16 <= p1 <= 20: nd_p1_band["16-20"] += 1
        else: nd_p1_band["21+"] += 1
        if p1 == 9: nd_p1_eq_9 += 1
        if len(nd["p"]) >= 5: nd_p5s.append(nd["p"][4])
        if len(nd["p"]) >= 6: nd_p6s.append(nd["p"][5])
        nd_sums.append(sum(nd["p"]))
        if nd.get("lucky"): nd_lucky[nd["lucky"]] += 1
        if nd.get("replay"): nd_replay[nd["replay"]] += 1
        if 9 in nd["p"]: nd_has_9 += 1
        if 38 in nd["p"]: nd_has_38 += 1
        if 27 in nd["p"]: nd_has_27 += 1
        if 16 in nd["p"]: nd_has_16 += 1
        if 10 in nd["p"]: nd_has_10 += 1
        if 39 in nd["p"]: nd_has_39 += 1

    print(f"  ND P1 band distribution:")
    for band in ("1-5", "6-10", "11-15", "16-20", "21+"):
        c = nd_p1_band.get(band, 0)
        bar = "█" * int(40*c/nd_count) if nd_count else ""
        print(f"    {band:>6s}  {c:>4d}  ({100*c/nd_count:.1f}%)  {bar}")
    print(f"\n  ND P1 = 9 specifically: {nd_p1_eq_9}/{nd_count} = "
          f"{100*nd_p1_eq_9/nd_count:.1f}%  (vs baseline ~3.2%)")
    print(f"  ND P1 mean = {sum(nd_p1s)/nd_count:.1f}, median = "
          f"{sorted(nd_p1s)[nd_count//2]}")

    print(f"\n  ND main occurrences (DJ's headliner candidates):")
    print(f"    9 :  {nd_has_9 :>4d}/{nd_count} = {100*nd_has_9/nd_count:.1f}%  (baseline 14.3%)")
    print(f"    10:  {nd_has_10:>4d}/{nd_count} = {100*nd_has_10/nd_count:.1f}%")
    print(f"    16:  {nd_has_16:>4d}/{nd_count} = {100*nd_has_16/nd_count:.1f}%")
    print(f"    27:  {nd_has_27:>4d}/{nd_count} = {100*nd_has_27/nd_count:.1f}%")
    print(f"    38:  {nd_has_38:>4d}/{nd_count} = {100*nd_has_38/nd_count:.1f}%")
    print(f"    39:  {nd_has_39:>4d}/{nd_count} = {100*nd_has_39/nd_count:.1f}%")

    # ── Q2b: also restrict to BD on Wed (like 06.05) → next is Sat ──
    print(f"\n  Sub-filter: BD-Wed P1>21, ND-Sat:")
    sub = [(i, b, n) for i, b, n in snap if b["wd"] == "Wed" and n["wd"] == "Sat"]
    sub_n = len(sub)
    sub_has_9 = sum(1 for _, _, n in sub if 9 in n["p"])
    sub_p1_eq_9 = sum(1 for _, _, n in sub if n["p"][0] == 9)
    sub_has_38 = sum(1 for _, _, n in sub if 38 in n["p"])
    sub_has_27 = sum(1 for _, _, n in sub if 27 in n["p"])
    sub_has_16 = sum(1 for _, _, n in sub if 16 in n["p"])
    sub_has_10 = sum(1 for _, _, n in sub if 10 in n["p"])
    sub_has_39 = sum(1 for _, _, n in sub if 39 in n["p"])
    print(f"    {sub_n} cases (Wed→Sat with BD-P1>21)")
    print(f"      P1=9 specifically: {sub_p1_eq_9}/{sub_n} = "
          f"{100*sub_p1_eq_9/max(1,sub_n):.1f}%")
    print(f"      9  in mains: {sub_has_9}/{sub_n} = {100*sub_has_9/max(1,sub_n):.1f}%")
    print(f"      10 in mains: {sub_has_10}/{sub_n} = {100*sub_has_10/max(1,sub_n):.1f}%")
    print(f"      16 in mains: {sub_has_16}/{sub_n} = {100*sub_has_16/max(1,sub_n):.1f}%")
    print(f"      27 in mains: {sub_has_27}/{sub_n} = {100*sub_has_27/max(1,sub_n):.1f}%")
    print(f"      38 in mains: {sub_has_38}/{sub_n} = {100*sub_has_38/max(1,sub_n):.1f}%")
    print(f"      39 in mains: {sub_has_39}/{sub_n} = {100*sub_has_39/max(1,sub_n):.1f}%")

    # last 10 historical Wed→Sat with BD-P1>21
    print(f"\n  Last 10 Wed→Sat BD-P1>21 cases:")
    for i, b, n in sub[-10:]:
        print(f"    BD {b['date']} {b['p']} 🍀{b.get('lucky')}R:{b.get('replay')} "
              f"→ ND {n['date']} {n['p']} 🍀{n.get('lucky')}R:{n.get('replay')}")

    # P5/P6 distributions for Wed→Sat snap-back
    if sub:
        sub_p5 = Counter()
        sub_p6 = Counter()
        for _, _, n in sub:
            if len(n["p"]) >= 5: sub_p5[n["p"][4]] += 1
            if len(n["p"]) >= 6: sub_p6[n["p"][5]] += 1
        print(f"\n  ND P5 top: {sub_p5.most_common(8)}")
        print(f"  ND P6 top: {sub_p6.most_common(8)}")


if __name__ == "__main__":
    asyncio.run(main())
