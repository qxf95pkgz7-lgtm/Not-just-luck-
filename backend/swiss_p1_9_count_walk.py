"""
🎯 SWISS P1=9 d-COUNT WALK (DJ Session 37, 09.05.2026 prep)
============================================================
DJ: "P1-9. Last time count d by d see if count has connections to the 9.
     I think last time was on 30-8-2025. Keep counting we meet at l d."

We:
  1. Find the most recent Swiss draw with P1=9 (verify DJ's memory of 30.08.2025).
  2. From that draw to today's BD (06.05.2026 d9), walk every draw d by d.
  3. For each d-count, check connections to '9':
       • 9 in mains
       • 9 in gaps
       • digit-sum / digital root = 9
       • date-day or month or sum = 9 / contains 9 / multiple of 9
       • 9-th position, 9-th anniversary, etc.
       • d-count-mod-9 == 0
"""
import asyncio
from datetime import datetime
from year_d_ledger import load_draws


def digital_root(n: int) -> int:
    while n >= 10:
        n = sum(int(c) for c in str(n))
    return n


async def main():
    s = await load_draws("swiss")
    s.sort(key=lambda x: x["dt"])

    # Find last P1=9 in Swiss history
    p1_9 = [d for d in s if d["p"][0] == 9]
    print("="*82)
    print("🔍 ALL SWISS P1=9 EVENTS (history)")
    print("="*82)
    for d in p1_9[-12:]:
        print(f"  {d['date']}  {d['wd']}  {d['p']}  🍀{d.get('lucky')} R:{d.get('replay')}")

    if not p1_9:
        print("  ⚠️ No P1=9 events found")
        return

    last_p1_9 = p1_9[-1]
    print(f"\n🎯 LAST P1=9 EVENT: {last_p1_9['date']} {last_p1_9['wd']} "
          f"{last_p1_9['p']} 🍀{last_p1_9['lucky']} R:{last_p1_9['replay']}")

    # Walk every Swiss draw from the day AFTER last P1=9 → up to most recent
    cutoff = last_p1_9["dt"]
    walk = [d for d in s if d["dt"] > cutoff]
    walk.sort(key=lambda x: x["dt"])

    target_dt = datetime(2026, 5, 9)  # the last d before our target Sat

    print(f"\n{'='*82}")
    print(f"🚶 d-by-d walk from {cutoff.strftime('%d.%m.%Y')} → 09.05.2026 Sat (target d10)")
    print(f"{'='*82}")
    print(f"{'#':>3}  {'date':10s} {'wd':3s}  {'mains':35s}  9-conn signals")
    print(f"{'-'*82}")

    nine_score_per_d = []
    cumulative_signals = []

    for i, d in enumerate(walk, 1):
        signals = []
        nums = d["p"]
        gaps = [nums[k+1] - nums[k] for k in range(len(nums)-1)]
        date = d["dt"]

        # 1. 9 in mains
        if 9 in nums:
            signals.append("9-main")
        # 2. 9 in gaps
        nine_in_gaps = [g for g in gaps if g == 9]
        if nine_in_gaps:
            signals.append(f"gap-9×{len(nine_in_gaps)}")
        # 3. multiples of 9 in mains
        multi9 = [n for n in nums if n != 9 and n % 9 == 0]
        if multi9:
            signals.append(f"×9:{multi9}")
        # 4. digital root of sum = 9
        sum_val = sum(nums)
        if digital_root(sum_val) == 9:
            signals.append(f"DR-sum=9({sum_val})")
        # 5. date-day = 9, mo = 9, day*month = mult of 9
        if date.day == 9 or date.month == 9:
            signals.append(f"date-9")
        if (date.day + date.month) == 9:
            signals.append(f"d+m=9")
        if (date.day * date.month) % 9 == 0:
            signals.append(f"d×m%9=0")
        # 6. d-count mod 9
        if i % 9 == 0:
            signals.append(f"d#{i}=mult9")
        # 7. d-count itself or i mirror
        if i in nums:
            signals.append(f"d#{i}-in-mains")
        # 8. 9-th member of family (decades) — e.g. 9, 19, 29, 39
        nine_decade = [n for n in nums if n in (9, 19, 29, 39)]
        if nine_decade:
            signals.append(f"decade-9:{nine_decade}")
        # 9. lucky / replay = 9
        if d.get("lucky") == 9:
            signals.append("🍀=9")
        if d.get("replay") == 9:
            signals.append("R=9")
        # 10. P1 itself = 9 (would close the cycle)
        if nums[0] == 9:
            signals.append("P1=9!")

        nine_score_per_d.append(len(signals))
        flag = ""
        if i % 9 == 0:
            flag = "  ◀ 9-th"
        if d["dt"].day == 9 or d["dt"].month == 9:
            flag += "  ◀ date-9"

        cumulative_signals.extend(signals)

        print(f"  d{i:>2}  {d['date']}  {d['wd']:3s}  {str(nums):35s}  "
              f"{', '.join(signals) if signals else '·'}{flag}")

    # Total walk length
    print(f"\n  Total d's between last P1=9 and BD-1 (06.05.2026 Sat = d{len(walk)}): {len(walk)}")
    target_d = len(walk) + 1
    print(f"  → Sat 09.05.2026 will be d{target_d} since last P1=9")
    print(f"  d{target_d} mod 9 = {target_d % 9}")
    print(f"  d{target_d} digital root = {digital_root(target_d)}")

    # Summary stats
    from collections import Counter
    sig_counter = Counter(cumulative_signals)
    print(f"\n📊 9-CONNECTION DENSITY (cumulative across {len(walk)} draws):")
    for sig, c in sig_counter.most_common(20):
        print(f"   {sig}: {c}")

    # Compare to baseline 9-density
    total_signals = sum(nine_score_per_d)
    print(f"\n  Total 9-connection signals: {total_signals}")
    print(f"  Avg signals / d: {total_signals/max(1,len(walk)):.2f}")

    # Hot streaks: where did the count fire 3+ signals in a single draw?
    print(f"\n  🔥 9-LOUD draws (≥3 signals):")
    for i, score in enumerate(nine_score_per_d, 1):
        if score >= 3:
            d = walk[i-1]
            print(f"    d{i:>2}  {d['date']}  {d['wd']}  score={score}")


if __name__ == "__main__":
    asyncio.run(main())
