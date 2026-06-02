"""
🪞 DJ Live Canon — Concatenation + Carrier-×10 Encoding

Two angles DJ taught (Session 45):

ANGLE A — Concatenation read:
  P1+P2 concat read as 3-digit number (5,14 → "514", 6,23 → "623")
  Look around each occurrence in history.

ANGLE B — Carrier×10 + Star encoding:
  Take BD's P5 → subtract 25 (the -25 carrier) → multiply by 10
  → add SUM of stars (or one star)
  → resulting number encodes ND's signature digits

  DJ verified: 22.05.2026 P5=37, ⭐5 → 37-25=12 → 120+5 = 125
               ND 26.05.2026 P4=35, P3=25 → 35-25=10 → 100+25 = 125 ✓ MATCH

  Apply to BD 29.05.2026 [5,14,18,31,35] ⭐(2,12):
    P5=35 → 35-25=10 → 100 + ⭐sum(14) = 114
    → tonight's signature should contain digits {1, 1, 4}
"""

import asyncio
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ENV = {}
for line in Path("/app/backend/.env").read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        ENV[k.strip()] = v.strip().strip('"')
os.environ.setdefault("MONGO_URL", ENV["MONGO_URL"])
os.environ.setdefault("DB_NAME", ENV["DB_NAME"])

from motor.motor_asyncio import AsyncIOMotorClient


def parse_date(s):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None


async def main():
    cli = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = cli[os.environ["DB_NAME"]]
    docs = await db.euromillions_draws.find({}).to_list(length=None)
    rows = []
    for d in docs:
        ds = d.get("date") or d.get("draw_date")
        dt = parse_date(ds) if ds else None
        if not dt:
            continue
        m = sorted(d.get("mains") or d.get("numbers") or [])
        s = list(d.get("stars") or d.get("lucky_stars") or [])
        if len(m) == 5:
            rows.append({"dt": dt, "mains": m, "stars": s})
    rows.sort(key=lambda r: r["dt"])

    # ANGLE A — P1=5 P2=14 historical lookup
    print("=" * 100)
    print("🎯 ANGLE A — Historical cases P1=5, P2=14 (matching BD 29.05.2026)")
    print("=" * 100)
    matches = []
    for i, r in enumerate(rows):
        if r["mains"][0] == 5 and r["mains"][1] == 14:
            matches.append((i, r))
    for i, r in matches:
        prev = rows[i - 1] if i > 0 else None
        nxt = rows[i + 1] if i + 1 < len(rows) else None
        print(f"\n  📍 {r['dt'].strftime('%d.%m.%Y')}  mains={r['mains']}  ⭐{r['stars']}")
        if prev:
            print(f"     BD  {prev['dt'].strftime('%d.%m.%Y')}  mains={prev['mains']}  ⭐{prev['stars']}")
        if nxt:
            print(f"     ND  {nxt['dt'].strftime('%d.%m.%Y')}  mains={nxt['mains']}  ⭐{nxt['stars']}")
    print(f"\n  Total P1=5,P2=14 cases: {len(matches)}")

    # P1=5 (broader)
    print()
    print("=" * 100)
    print("🎯 ANGLE A wider — All draws with P1=5 — what's the ND signature?")
    print("=" * 100)
    p1_5 = [(i, r) for i, r in enumerate(rows) if r["mains"][0] == 5]
    print(f"Total P1=5 cases: {len(p1_5)}")
    nd_main = Counter()
    nd_star = Counter()
    for i, r in p1_5:
        if i + 1 < len(rows):
            nd = rows[i + 1]
            for n in nd["mains"]:
                nd_main[n] += 1
            for s in nd["stars"]:
                nd_star[s] += 1
    print("Top-15 ND mains after P1=5:")
    for n, c in nd_main.most_common(15):
        print(f"   n={n:>2}  ×{c}  ({100*c/max(1,len(p1_5)):.1f}%)")
    print("Top stars after P1=5:")
    for s, c in sorted(nd_star.items(), key=lambda x: -x[1])[:10]:
        print(f"   ⭐{s:>2}  ×{c}  ({100*c/max(1,len(p1_5)):.1f}%)")

    # ANGLE B — Carrier×10 + Star encoding verification & projection
    print()
    print("=" * 100)
    print("🎯 ANGLE B — Carrier×10 codec verification")
    print("=" * 100)

    def codec_bd(bd):
        """Compute BD encoded numbers: (P5-25)*10 + star options."""
        p5 = bd["mains"][4]
        carrier = (p5 - 25)
        base = carrier * 10
        s_sum = sum(bd["stars"])
        return {
            "p5": p5,
            "carrier_minus25": carrier,
            "base": base,
            "plus_star_sum": base + s_sum,
            "plus_star_each": [base + s for s in bd["stars"]],
        }

    def codec_nd(nd):
        """Compute ND signature: (P4-25)*10 + P3."""
        p3, p4 = nd["mains"][2], nd["mains"][3]
        return {
            "p4_minus_25": (p4 - 25),
            "base": (p4 - 25) * 10,
            "plus_p3": (p4 - 25) * 10 + p3,
            "p3": p3,
            "p4": p4,
        }

    # Verify DJ's two examples
    print("\n🧪 Verifying DJ's examples:")
    # Example 1: BD 26.05 → ND 29.05
    bd1 = next(r for r in rows if r["dt"].strftime("%d.%m.%Y") == "26.05.2026")
    nd1 = next(r for r in rows if r["dt"].strftime("%d.%m.%Y") == "29.05.2026")
    print(f"\nEx1: BD 26.05.2026 {bd1['mains']} ⭐{bd1['stars']}")
    e1 = codec_bd(bd1)
    print(f"   BD encoded: P5={e1['p5']} → {e1['p5']}-25={e1['carrier_minus25']} ×10 = {e1['base']} + ⭐sum({sum(bd1['stars'])}) = {e1['plus_star_sum']}")
    print(f"   BD with each star: {e1['plus_star_each']}")
    print(f"     ND 29.05.2026 {nd1['mains']} ⭐{nd1['stars']}")
    n1 = codec_nd(nd1)
    print(f"   ND signature: P3={n1['p3']}, P4={n1['p4']} → (P4-25)*10+P3 = {n1['plus_p3']}")
    print(f"   DJ noted: BD encoded → 138, ND digits P4+P3 = 1831 (containing 138 in some form)")

    # Example 2: BD 22.05 → ND 26.05
    bd2 = next(r for r in rows if r["dt"].strftime("%d.%m.%Y") == "22.05.2026")
    nd2 = bd1  # = 26.05
    print(f"\nEx2: BD 22.05.2026 {bd2['mains']} ⭐{bd2['stars']}")
    e2 = codec_bd(bd2)
    print(f"   BD encoded: P5={e2['p5']} → {e2['p5']}-25={e2['carrier_minus25']} ×10 = {e2['base']} + star = {e2['plus_star_each']}")
    n2 = codec_nd(nd2)
    print(f"     ND 26.05.2026 {nd2['mains']} ⭐{nd2['stars']}")
    print(f"   ND signature: P3={n2['p3']}, P4={n2['p4']} → (P4-25)*10+P3 = {n2['plus_p3']} ✓ MATCH BD+⭐5=125")

    # TONIGHT projection
    print()
    print("=" * 100)
    print("🎯 TONIGHT 02.06.2026 — codec projection from BD 29.05.2026")
    print("=" * 100)
    bd_today = nd1  # 29.05
    e_today = codec_bd(bd_today)
    print(f"  BD 29.05.2026 [5,14,18,31,35] ⭐(2,12)")
    print(f"  P5=35 → 35-25=10 → ×10 = 100")
    print(f"  + ⭐sum(2+12=14) = 100+14 = 114")
    print(f"  + ⭐2 alone = 102")
    print(f"  + ⭐12 alone = 112")
    print()
    print(f"  → Tonight's ND signature should encode one of: 114, 102, 112")
    print()
    print(f"  Solve (P4-25)*10 + P3 = 114:")
    print(f"    Try P4 values 26..50, P3 must equal 114 - (P4-25)*10")
    for p4 in range(26, 51):
        target = 114 - (p4 - 25) * 10
        if 1 <= target < p4:
            print(f"      P4={p4}, P3={target}  → ND-P3-P4 = {target},{p4}")
    print()
    print(f"  Solve (P4-25)*10 + P3 = 102:")
    for p4 in range(26, 51):
        target = 102 - (p4 - 25) * 10
        if 1 <= target < p4:
            print(f"      P4={p4}, P3={target}  → ND-P3-P4 = {target},{p4}")
    print()
    print(f"  Solve (P4-25)*10 + P3 = 112:")
    for p4 in range(26, 51):
        target = 112 - (p4 - 25) * 10
        if 1 <= target < p4:
            print(f"      P4={p4}, P3={target}  → ND-P3-P4 = {target},{p4}")

    # SCAN history for the codec match
    print()
    print("=" * 100)
    print("📊 HISTORIC RATE — How often does (BD P5-25)*10 + ⭐sum = (ND P4-25)*10 + P3 ?")
    print("=" * 100)
    hits = 0
    near_hits = 0
    total = 0
    for i in range(len(rows) - 1):
        bd = rows[i]
        nd = rows[i + 1]
        if bd["mains"][4] <= 25:
            continue
        if nd["mains"][3] <= 25:
            continue
        bd_code_sum = (bd["mains"][4] - 25) * 10 + sum(bd["stars"])
        nd_sig = (nd["mains"][3] - 25) * 10 + nd["mains"][2]
        bd_codes_each = [(bd["mains"][4] - 25) * 10 + s for s in bd["stars"]]
        total += 1
        if bd_code_sum == nd_sig or nd_sig in bd_codes_each:
            hits += 1
        if abs(bd_code_sum - nd_sig) <= 5 or any(abs(c - nd_sig) <= 5 for c in bd_codes_each):
            near_hits += 1
    print(f"  Tested {total} consecutive draw pairs (where P5>25 and ND-P4>25)")
    print(f"  EXACT codec matches: {hits} ({100*hits/max(1,total):.2f}%)")
    print(f"  NEAR matches (±5):   {near_hits} ({100*near_hits/max(1,total):.2f}%)")

    cli.close()


if __name__ == "__main__":
    asyncio.run(main())
