"""
🌉 SWISS↔EURO Q2 BRIDGE AUDIT (−21 transform + carriers)
=========================================================
DJ canon (Session 37, 09.05.2026):
  Swiss n − 21 = Euro twin
  If twin not in Euro raw, walk via +25 carrier OR +21 back-loop.
  34 = self-loop (only shared raw value).

Walk every Swiss Q2 draw → its −21 shadow → check the temporally
ADJACENT Euro draws (the closest Euro before & after) for matches:
   • RAW match (Swiss-21 in Euro)
   • +25 carrier (Swiss-21+25 in Euro = Swiss+4)
   • -25 carrier (Swiss-21-25 in Euro = Swiss-46)
   • +21 back (Swiss itself in Euro)
   • neighbor ±1 / ±2
"""
import asyncio
from datetime import datetime
from year_d_ledger import load_draws


def main():
    asyncio.run(_run())


async def _run():
    e = await load_draws("euro")
    s = await load_draws("swiss")
    e.sort(key=lambda x: x["dt"])
    s.sort(key=lambda x: x["dt"])

    # Q2 2026 only
    e_q2 = [d for d in e if d["year"] == 2026 and d["quarter"] == 2]
    s_q2 = [d for d in s if d["year"] == 2026 and d["quarter"] == 2]

    print("\n🎻 EURO Q2 2026:")
    for i, d in enumerate(e_q2, 1):
        print(f"  Eud{i:2d}  {d['date']}  {d['wd']:3s}  {d['p']}  ⭐{d.get('stars')}")
    print("\n🍀 SWISS Q2 2026:")
    for i, d in enumerate(s_q2, 1):
        print(f"  Swd{i:2d}  {d['date']}  {d['wd']:3s}  {d['p']}  🍀{d.get('lucky')} R:{d.get('replay')}")

    # ── BRIDGE ANALYSIS ──
    print("\n" + "="*78)
    print("🌉 −21 BRIDGE — every Swiss draw → Euro shadow + carriers")
    print("="*78)

    def find_adjacent_euro(swiss_dt):
        before = [d for d in e_q2 if d["dt"] <= swiss_dt]
        after = [d for d in e_q2 if d["dt"] > swiss_dt]
        return (before[-1] if before else None, after[0] if after else None)

    overall_raw = 0
    overall_25 = 0
    overall_21back = 0
    overall_neighbor = 0
    overall_total_swiss_mains = 0
    bridges_per_pair = []

    for sd in s_q2:
        adj_before, adj_after = find_adjacent_euro(sd["dt"])
        targets = []
        if adj_before:
            targets.append(("before", adj_before))
        if adj_after and adj_after != adj_before:
            targets.append(("after", adj_after))

        print(f"\n🍀 Swiss {sd['date']} ({sd['wd']}) {sd['p']}")
        s_minus = [(n, n - 21) for n in sd["p"]]
        print(f"   −21 shadow: { {p: m for p, m in s_minus} }")

        for tag, ed in targets:
            print(f"   ↔ Euro {tag.upper()}: {ed['date']} ({ed['wd']}) {ed['p']}  ⭐{ed['stars']}")
            hits = []
            for n in sd["p"]:
                shadow = n - 21
                e_set = set(ed["p"])
                e_stars = set(ed.get("stars") or [])
                tags = []
                # raw shadow in Euro mains
                if shadow in e_set:
                    tags.append(f"RAW({shadow})")
                # +25 carrier
                if 1 <= shadow + 25 <= 50 and (shadow + 25) in e_set:
                    tags.append(f"+25({shadow+25})")
                # -25 carrier
                if 1 <= shadow - 25 and (shadow - 25) in e_set:
                    tags.append(f"-25({shadow-25})")
                # +21 back-loop (Swiss n itself in Euro)
                if 1 <= n <= 50 and n in e_set:
                    tags.append(f"+21back({n})")
                # ±1 neighbor of shadow
                for delta in (1, -1):
                    nb = shadow + delta
                    if 1 <= nb <= 50 and nb in e_set:
                        tags.append(f"±1nb({nb})")
                        break
                # shadow in stars
                if 1 <= shadow <= 12 and shadow in e_stars:
                    tags.append(f"⭐({shadow})")
                if tags:
                    hits.append(f"{n}→{tags}")
            for h in hits:
                print(f"      {h}")
            if not hits:
                print("      (no bridge hits)")

            # tally on the AFTER pair only (forward bridge)
            if tag == "after":
                bridge_count = 0
                for n in sd["p"]:
                    shadow = n - 21
                    if shadow in set(ed["p"]):
                        overall_raw += 1; bridge_count += 1
                    elif 1 <= shadow + 25 <= 50 and (shadow + 25) in set(ed["p"]):
                        overall_25 += 1; bridge_count += 1
                    elif n in set(ed["p"]):
                        overall_21back += 1; bridge_count += 1
                    elif any(1 <= shadow + d <= 50 and (shadow + d) in set(ed["p"]) for d in (1, -1)):
                        overall_neighbor += 1; bridge_count += 1
                overall_total_swiss_mains += len(sd["p"])
                bridges_per_pair.append((sd["date"], ed["date"], bridge_count, len(sd["p"])))

    print("\n" + "="*78)
    print("📊 FORWARD BRIDGE STATS (Swiss → Next Euro):")
    print("="*78)
    print(f"  Total Swiss mains scanned: {overall_total_swiss_mains}")
    print(f"  RAW (-21) matches:         {overall_raw}")
    print(f"  +25 carrier matches:        {overall_25}")
    print(f"  +21 back-loop matches:     {overall_21back}")
    print(f"  ±1 neighbor matches:        {overall_neighbor}")
    total_hits = overall_raw + overall_25 + overall_21back + overall_neighbor
    print(f"  ──────────────────────────────────")
    print(f"  TOTAL bridge hits:          {total_hits}/{overall_total_swiss_mains} = "
          f"{100*total_hits/max(1,overall_total_swiss_mains):.1f}%")
    print(f"\n  Per-pair density:")
    for sd_date, ed_date, hits, total in bridges_per_pair:
        bar = "█" * hits + "·" * (total - hits)
        print(f"    {sd_date} → {ed_date}  {hits}/{total}  {bar}")


if __name__ == "__main__":
    main()
