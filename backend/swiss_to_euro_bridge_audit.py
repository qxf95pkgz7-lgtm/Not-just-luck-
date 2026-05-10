"""
🌉 SW LD → NEXT EURO BRIDGE
============================
DJ S38: "now we look at euro bridge, what ld swiss can tell us about n euro d.
         look again last 10 d v l 10d euro, find new clues"

Sw LD = 09.05.2026 Sat [11, 12, 24, 25, 29, 31] 🍀2
Next Eu = 12.05.2026 Tue (3 days later)

Layers to analyse:
  1. Sw mains − 21 → Eu shadow (raw + carriers)
  2. Sw HUNGRIES (last 6 Sw draws silent) − 21
  3. Sw 🍀+R atoms — what do they bridge to?
  4. Last 10 Sw vs Last 10 Eu — full bridge density map

Fresh hunt: things we missed in Q2 audit — Sw → Eu  carrier with the
new family-shift lens applied. The 09.05 draw was −1-decade-shift of BD;
maybe the BRIDGE direction also carries this canon.
"""
import asyncio
from collections import Counter
from year_d_ledger import load_draws


async def main():
    e = await load_draws("euro")
    s = await load_draws("swiss")
    e.sort(key=lambda x: x["dt"]); s.sort(key=lambda x: x["dt"])

    sw_ld = next((d for d in s if d["date"] == "09.05.2026"), None)
    if not sw_ld:
        print("⚠️ Sw LD 09.05.2026 not found")
        sw_ld = s[-1]
    print(f"🍀 Sw LD: {sw_ld['date']} {sw_ld['p']} 🍀{sw_ld.get('lucky')} R:{sw_ld.get('replay')}")

    next_eu_candidate = next((d for d in e if d["dt"] > sw_ld["dt"]), None)
    print(f"🎻 Next Eu: {next_eu_candidate['date']} (target)" if next_eu_candidate else "🎻 Next Eu: not yet drawn")
    print()

    # ── 1. Sw mains -21 shadow + carriers ──
    print("="*82)
    print("🌉 LAYER 1 — Sw LD −21 SHADOW + CARRIERS → Eu candidates")
    print("="*82)
    sw_mains = sw_ld["p"]
    eu_candidates = {}
    def add(v, why):
        if 1 <= v <= 50:
            eu_candidates.setdefault(v, []).append(why)
    for n in sw_mains:
        add(n, f"Sw-raw({n})")           # +21back: Sw n itself in Eu
        add(n - 21, f"Sw{n}−21")          # raw shadow
        add(n - 21 + 25, f"Sw{n}−21+25(Eu-circle)")
        add(n - 21 - 25, f"Sw{n}−21−25")
        add(n - 21 + 1, f"Sw{n}−21+1nb")
        add(n - 21 - 1, f"Sw{n}−21−1nb")

    # 🍀 + R bridge
    L = sw_ld.get("lucky"); R = sw_ld.get("replay")
    if L: add(L, f"🍀={L} raw")
    if R:
        add(R, f"R={R} raw")
        add(R + 25, f"R+25")
        if R - 21 > 0: add(R - 21, f"R−21")

    print(f"Eu candidates from Sw LD ({len(eu_candidates)} unique values):")
    for v in sorted(eu_candidates.keys()):
        tags = eu_candidates[v]
        marker = "★" if len(tags) >= 2 else " "
        print(f"  {v:>3d} {marker} {tags[:3]}")

    high_conv = [v for v, tags in eu_candidates.items() if len(tags) >= 2]
    print(f"\n  🚨 HIGH-CONVERGENCE (≥2 paths from Sw LD): {sorted(high_conv)}")

    # ── 2. Sw hungries (last 6 Sw draws silent) − 21 ──
    print("\n" + "="*82)
    print("🌉 LAYER 2 — Sw HUNGRY (last 6 Sw silent) → Eu via −21")
    print("="*82)
    last6_sw = s[-6:]
    sw_played = set()
    for d in last6_sw:
        sw_played.update(d["p"])
    sw_hungries = sorted([n for n in range(1, 43) if n not in sw_played])
    print(f"Sw hungries (last 6 draws): {sw_hungries}")
    hungry_bridge = {}
    for hn in sw_hungries:
        for v, tag in [(hn, f"Sw-hungry-raw({hn})"),
                       (hn - 21, f"Sw-hungry−21({hn})"),
                       (hn + 25 - 21, f"Sw-hungry−21+25({hn})")]:
            if 1 <= v <= 50:
                hungry_bridge.setdefault(v, []).append(tag)
    # filter to high
    print(f"\nHungry-bridged Eu candidates (top 12 most-pathways):")
    sorted_h = sorted(hungry_bridge.items(), key=lambda kv: -len(kv[1]))
    for v, tags in sorted_h[:12]:
        print(f"  {v:>3d} ({len(tags)} paths) {tags[:2]}")

    # ── 3. Last 10 Sw vs Last 10 Eu — density map ──
    print("\n" + "="*82)
    print("🌉 LAYER 3 — LAST 10 Sw ↔ LAST 10 Eu BRIDGE-DENSITY")
    print("="*82)
    last10_sw = s[-10:]
    last10_eu = e[-10:]
    print("\nLast 10 Sw:")
    for d in last10_sw:
        print(f"  {d['date']} {d['wd']:3s} {d['p']} 🍀{d.get('lucky')} R:{d.get('replay')}")
    print("\nLast 10 Eu:")
    for d in last10_eu:
        print(f"  {d['date']} {d['wd']:3s} {d['p']} ⭐{d.get('stars')}")

    # For each Sw draw, find the NEXT Eu draw temporally and tally bridge hits
    print("\n  Forward bridge density (each Sw → its NEXT Eu):")
    print(f"  {'Sw date':10s} {'next Eu':10s} {'hits-mains':>10s} {'hits-hungry':>11s} {'⭐ hits':>8s}")
    print("  " + "-"*54)
    for sd in last10_sw:
        nxt = next((ed for ed in e if ed["dt"] > sd["dt"]), None)
        if not nxt: continue
        if nxt["dt"] > sd["dt"] + (last10_eu[-1]["dt"] - last10_eu[0]["dt"]):
            continue
        sw_set = set()
        for n in sd["p"]:
            sw_set.add(n)              # raw
            sw_set.add(n - 21)         # -21
            sw_set.add(n + 4)          # -21+25 effectively
        eu_main_hits = len(sw_set & set(nxt["p"]))
        # hungry hits
        sw_hungries_at_t = [n for n in range(1, 43) if n not in {x for d in s if d["dt"] < sd["dt"] for x in d["p"][-6:]}]
        # simpler: hungries from previous 6 of THIS sd
        idx = next(i for i, d in enumerate(s) if d["dt"] == sd["dt"])
        prev6 = s[max(0, idx-6):idx]
        sw_hungry_set = set(range(1, 43)) - set(x for d in prev6 for x in d["p"])
        hungry_set = set()
        for hn in sw_hungry_set:
            hungry_set.add(hn)
            hungry_set.add(hn - 21)
        h_hits = len(hungry_set & set(nxt["p"]))
        # star bridge: ⭐n related to Sw 🍀+R?
        s_lr = [sd.get("lucky"), sd.get("replay")]
        star_hits = len([s_v for s_v in (nxt.get("stars") or []) if s_v in s_lr])
        print(f"  {sd['date']:10s} {nxt['date']:10s} {eu_main_hits:>10d} {h_hits:>11d} {star_hits:>8d}")

    # ── 4. NEW CLUE HUNT — does Sw P1 anticipate Eu P1?
    print("\n" + "="*82)
    print("🔍 NEW-CLUE PROBES")
    print("="*82)
    # Probe A: Sw P1 vs next-Eu P1
    pairs = []
    for sd in s[-30:]:
        nxt = next((ed for ed in e if ed["dt"] > sd["dt"]), None)
        if nxt:
            pairs.append((sd["p"][0], nxt["p"][0]))
    if pairs:
        avg_diff = sum(abs(a-b) for a, b in pairs) / len(pairs)
        same_band = sum(1 for a, b in pairs if abs(a - b) <= 5)
        print(f"\nA. Sw P1 → Eu P1 (last 30 pairs):")
        print(f"   avg |Sw P1 − Eu P1| = {avg_diff:.1f}")
        print(f"   |Δ| ≤ 5 (same band): {same_band}/{len(pairs)} = {100*same_band/len(pairs):.1f}%")

    # Probe B: Sw twin-pair sums → Eu draw architecture
    print(f"\nB. Sw twin-pair detection: any consecutive in last 10 Sw?")
    for sd in last10_sw:
        ps = sd["p"]
        twins = [(ps[i], ps[i+1]) for i in range(len(ps)-1) if ps[i+1] - ps[i] == 1]
        if twins:
            print(f"   {sd['date']} twins: {twins}")

    # Probe C: |R − 🍀| = next Eu gap?
    print(f"\nC. |R − 🍀| as next-Eu GAP rhythm (last 10 Sw → next Eu):")
    for sd in last10_sw:
        L, R = sd.get("lucky"), sd.get("replay")
        if not (L and R): continue
        nxt = next((ed for ed in e if ed["dt"] > sd["dt"]), None)
        if not nxt: continue
        delta = abs(R - L)
        gaps = [nxt["p"][i+1] - nxt["p"][i] for i in range(len(nxt["p"])-1)]
        hit = delta in gaps
        print(f"   Sw {sd['date']} 🍀{L}R{R} delta={delta:>2}  → Eu {nxt['date']} gaps={gaps}  {'✓' if hit else '·'}")

    # Probe D: Sw sum vs Eu sum
    print(f"\nD. Sw sum → Eu sum (delta tracking, last 10):")
    for sd in last10_sw:
        nxt = next((ed for ed in e if ed["dt"] > sd["dt"]), None)
        if not nxt: continue
        ssum = sum(sd["p"]); esum = sum(nxt["p"])
        print(f"   Sw {sd['date']} sum={ssum}  → Eu {nxt['date']} sum={esum}  diff={esum-ssum:+d}")


if __name__ == "__main__":
    asyncio.run(main())
