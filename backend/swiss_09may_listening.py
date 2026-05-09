"""
🎻 09.05 LISTENING PASS — date envelope 678 hide + 10-18 mirror + 3-draw window
==============================================================================
DJ instruction (Session 37):
  "9-5, 678 hide. Check history the date, then check if d10 connection to
   mirror 10-18. Better look 3 d 2 bd one after. Find clues, let us improve E."

Window we listen to:
  • 09.05 history (both lotteries, all years) — date-day=9 month=5
  • 678 hide (digits between 5 and 9 = 6,7,8)
  • 10-18 mirror pair (sum=28 axis)
  • Recent 3-draw window: BD-2, BD-1, latest cross
       = 02.05.2026 Sw d8  +  06.05.2026 Sw d9  +  08.05.2026 Eu d10
"""
import asyncio
from collections import Counter
from datetime import datetime
from year_d_ledger import load_draws


async def main():
    e = await load_draws("euro")
    s = await load_draws("swiss")
    e.sort(key=lambda x: x["dt"]); s.sort(key=lambda x: x["dt"])

    # ── 1. HISTORY OF 09.05 (every year, both lotteries) ──
    print("="*82)
    print("📅 09.05 HISTORY — every year, both lotteries")
    print("="*82)
    e_905 = [d for d in e if d["dt"].day == 9 and d["dt"].month == 5]
    s_905 = [d for d in s if d["dt"].day == 9 and d["dt"].month == 5]
    print("\n🎻 Euro 09.05 history:")
    for d in e_905:
        wd = d["wd"]
        nums = d["p"]
        stars = d.get("stars")
        has678 = sorted(set(nums) & {6, 7, 8} | {x for x in nums if x % 10 in (6, 7, 8) or (x // 10) in (6, 7, 8)})
        print(f"  {d['date']}  {wd}  {nums}  ⭐{stars}  · 678-hide hits: {[x for x in nums if x in (6,7,8) or x%10 in (6,7,8) or 10<=x<=19 and x in (16,17,18) or 20<=x<=29 and x in (26,27,28) or 30<=x<=39 and x in (36,37,38) or 40<=x<=50 and x in (46,47,48)]}")

    print("\n🍀 Swiss 09.05 history:")
    for d in s_905:
        wd = d["wd"]
        nums = d["p"]
        L = d.get("lucky"); R = d.get("replay")
        print(f"  {d['date']}  {wd}  {nums}  🍀{L} R:{R}  · 678-hide hits: {[x for x in nums if x in (6,7,8) or x%10 in (6,7,8) or x in (16,17,18,26,27,28,36,37,38)]}")

    # ── 2. 678-HIDE SIGNATURE ANALYSIS ──
    print("\n" + "="*82)
    print("🔢 678-HIDE SIGNATURE — count of {6,7,8 + their decade-extensions} per draw")
    print("="*82)
    targets_678 = {6, 7, 8, 16, 17, 18, 26, 27, 28, 36, 37, 38, 46, 47, 48}

    print("\n🎻 Euro 09.05:")
    for d in e_905:
        hits = sorted(set(d["p"]) & targets_678)
        star_hits = sorted(set(d.get("stars") or []) & targets_678)
        print(f"  {d['date']}: mains-678 = {hits}  (count {len(hits)})  ⭐-678 = {star_hits}")
    if e_905:
        avg = sum(len(set(d["p"]) & targets_678) for d in e_905) / len(e_905)
        print(f"  → Euro 09.05 avg 678-hits / draw = {avg:.2f}  (5-mains baseline ~1.5)")

    print("\n🍀 Swiss 09.05:")
    for d in s_905:
        hits = sorted(set(d["p"]) & targets_678)
        print(f"  {d['date']}: mains-678 = {hits}  (count {len(hits)})  🍀{d.get('lucky')} R:{d.get('replay')}")
    if s_905:
        avg_s = sum(len(set(d["p"]) & targets_678) for d in s_905) / len(s_905)
        print(f"  → Swiss 09.05 avg 678-hits / draw = {avg_s:.2f}  (6-mains baseline ~2.1)")

    # ── 3. 10-18 MIRROR PAIR HISTORY ──
    print("\n" + "="*82)
    print("🪞 10-18 MIRROR PAIR (sum=28 axis) — history of CO-occurrence in same draw")
    print("="*82)

    print("\n🍀 Swiss draws holding BOTH 10 AND 18 (last 5 years):")
    cnt_swiss = 0
    cutoff_5y = datetime(2021, 5, 1)
    for d in s:
        if d["dt"] < cutoff_5y:
            continue
        if 10 in d["p"] and 18 in d["p"]:
            print(f"  {d['date']} {d['wd']} {d['p']} 🍀{d.get('lucky')} R:{d.get('replay')}")
            cnt_swiss += 1
    n5 = sum(1 for d in s if d["dt"] >= cutoff_5y)
    print(f"  TOTAL: {cnt_swiss}/{n5} = {100*cnt_swiss/max(1,n5):.1f}%  (5-yr Swiss baseline)")

    print("\n🎻 Euro draws holding BOTH 10 AND 18 (last 5 years):")
    cnt_euro = 0
    for d in e:
        if d["dt"] < cutoff_5y:
            continue
        if 10 in d["p"] and 18 in d["p"]:
            print(f"  {d['date']} {d['wd']} {d['p']} ⭐{d.get('stars')}")
            cnt_euro += 1
    n5e = sum(1 for d in e if d["dt"] >= cutoff_5y)
    print(f"  TOTAL: {cnt_euro}/{n5e} = {100*cnt_euro/max(1,n5e):.1f}%  (5-yr Euro baseline)")

    # ── 4. THE 3-DRAW WINDOW (BD-2, BD-1, latest cross) ──
    print("\n" + "="*82)
    print("🎯 3-DRAW WINDOW for d10 Sat 09.05.2026 Swiss target")
    print("="*82)
    # BD-2 Sw = 02.05 Sat
    # BD-1 Sw = 06.05 Wed
    # Latest cross = 08.05 Fri Eu
    bd2 = next((d for d in s if d["date"] == "02.05.2026"), None)
    bd1 = next((d for d in s if d["date"] == "06.05.2026"), None)
    cross = next((d for d in e if d["date"] == "08.05.2026"), None)
    win = []
    if bd2: win.append(("BD-2  Sw d8 ", bd2))
    if bd1: win.append(("BD-1  Sw d9 ", bd1))
    if cross: win.append(("Eu after Sw ", cross))

    for tag, d in win:
        nums = d["p"]
        family_678 = sorted(set(nums) & targets_678)
        has_10 = 10 in nums
        has_18 = 18 in nums
        gaps = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
        print(f"\n  {tag}  {d['date']}  {d['wd']}  {nums}")
        print(f"     678-hide hits: {family_678}  · has-10: {has_10}  has-18: {has_18}")
        print(f"     gaps: {gaps}")
        if "lucky" in d:
            print(f"     🍀{d.get('lucky')} R:{d.get('replay')}")
        if d.get("stars"):
            print(f"     ⭐{d['stars']}")

    # ── 5. AGGREGATE — 678-hits + 10/18 across the 3-draw window ──
    all_678 = []
    has_10_count = 0
    has_18_count = 0
    for tag, d in win:
        all_678.extend(set(d["p"]) & targets_678)
        if 10 in d["p"]: has_10_count += 1
        if 18 in d["p"]: has_18_count += 1
    print(f"\n  🔢 3-window 678-hide tally: {Counter(all_678)}")
    print(f"  🪞 10 appearances in window: {has_10_count}/3   18 appearances: {has_18_count}/3")

    # ── 6. RIDE: which 678-extensions are HUNGRY in Swiss right now? ──
    sw_recent6 = sorted(s, key=lambda x: x["dt"])[-6:]
    sw_played = set()
    for d in sw_recent6:
        sw_played.update(d["p"])
    silent_678 = sorted(targets_678 - sw_played)
    print(f"\n  💤 678-hide numbers SILENT in last 6 Swiss draws: {silent_678}")

    # ── 7. The bridge — Sw 06.05 d9 hungries' 678-shift via -21 carriers
    print("\n  🌉 Eu→Sw +21 bridge with 678 lens:")
    if cross:
        print(f"     Eu {cross['date']} mains: {cross['p']} ⭐{cross['stars']}")
        for n in cross["p"]:
            shadow = n + 21
            if shadow in targets_678 and 1 <= shadow <= 42:
                print(f"     Eu {n} +21 = {shadow} (in 678 family) → STRONG Sw candidate")
            elif n in targets_678:
                print(f"     Eu {n} (raw 678) — check Sw bridge")
        for s_e in (cross.get("stars") or []):
            if s_e in (6, 7, 8):
                print(f"     Eu ⭐{s_e} ∈ {{6,7,8}} hidden digits — DIRECT 678 hit")


if __name__ == "__main__":
    asyncio.run(main())
