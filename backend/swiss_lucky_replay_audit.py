"""
🍀↔R AUDIT — Swiss 2-year listening scan
==========================================
DJ canon (Session 37, fork-fix): 'The Lucky itself is just a number that
helps with the Replay number — check last 2 years connection, you will find
the clues.'

Pure listening — no decisions yet. We dump every angle of 🍀↔R relationship
across the last 2 years of Swiss draws.
"""
import asyncio
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from year_d_ledger import load_draws


def main():
    asyncio.run(_run())


async def _run():
    draws = await load_draws("swiss")
    cutoff = datetime(2024, 5, 9)  # ~2 years back
    recent = [d for d in draws if d["dt"] >= cutoff]
    recent.sort(key=lambda d: d["dt"])
    n = len(recent)
    print(f"\n🎻 SWISS 🍀↔R AUDIT — {n} draws, {recent[0]['date']} → {recent[-1]['date']}\n")

    # ── 1. Sum, Diff, last-digit ────────────────────────────────────────────
    sum_counts = Counter()
    diff_counts = Counter()
    re_lock = 0          # 🍀 == R
    lucky_eq_p_n = Counter()  # 🍀 == position index (1-6) of replay-twin
    lucky_in_mains = 0
    replay_in_mains = 0
    re_lock_after_re_lock = 0
    last_digit_match = 0
    lucky_index_main_eq_replay = Counter()  # 🍀 = k → does P[k] == R?
    lucky_pluses_main = Counter()  # 🍀 + something = R hits

    pair_counter = Counter()  # (lucky, replay) frequency

    for i, d in enumerate(recent):
        L = d["lucky"]
        R = d["replay"]
        P = d["p"]
        if L is None or R is None:
            continue
        pair_counter[(L, R)] += 1
        sum_counts[L + R] += 1
        diff_counts[abs(R - L)] += 1
        if L == R:
            re_lock += 1
            if i + 1 < len(recent):
                nxt = recent[i + 1]
                if nxt.get("lucky") == nxt.get("replay"):
                    re_lock_after_re_lock += 1
        if L in P:
            lucky_in_mains += 1
        if R in P:
            replay_in_mains += 1
        if str(R)[-1] == str(L)[-1]:
            last_digit_match += 1
        # 🍀 as POSITION pointer (1-6 → P[L-1])
        if 1 <= L <= 6 and L - 1 < len(P):
            lucky_index_main_eq_replay[(L, P[L - 1] == R)] += 1

    print(f"📊 Total draws scanned: {n}")
    print(f"   🔁 RE-LOCK (🍀 == R): {re_lock}/{n} = {100*re_lock/n:.1f}%")
    print(f"   🪞 RE-LOCK after RE-LOCK: {re_lock_after_re_lock}")
    print(f"   🍀 lands as a MAIN: {lucky_in_mains}/{n} = {100*lucky_in_mains/n:.1f}%")
    print(f"   🎯 R lands as a MAIN: {replay_in_mains}/{n} = {100*replay_in_mains/n:.1f}%")
    print(f"   🔢 last digit match (🍀↔R): {last_digit_match}/{n} = {100*last_digit_match/n:.1f}%")

    # ── 2. 🍀 as POINTER index (1-6) → does P[🍀] == R? ─────────────────────
    print(f"\n🎯 🍀 AS POSITION POINTER (does P[🍀] == R?):")
    for (L, hit), c in sorted(lucky_index_main_eq_replay.items()):
        print(f"   🍀={L}  P{L} == R: {'✓' if hit else '✗'}  count={c}")
    # bucket: pointer hit overall
    pointer_hits = sum(c for (L, hit), c in lucky_index_main_eq_replay.items() if hit)
    pointer_total = sum(lucky_index_main_eq_replay.values())
    print(f"   ⇒ pointer-hit rate: {pointer_hits}/{pointer_total} = "
          f"{100*pointer_hits/max(1,pointer_total):.1f}%  (random baseline 1/6 ≈ 16.7%)")

    # ── 3. 🍀↔R difference distribution ─────────────────────────────────────
    print(f"\n📐 |R − 🍀| DISTRIBUTION (top 12):")
    for diff, c in diff_counts.most_common(12):
        print(f"   diff={diff:2d}  count={c:3d}  ({100*c/n:.1f}%)")

    # ── 4. 🍀 + R sum distribution ──────────────────────────────────────────
    print(f"\n➕ 🍀 + R SUM DISTRIBUTION (top 12):")
    for s, c in sum_counts.most_common(12):
        print(f"   sum={s:2d}  count={c:3d}  ({100*c/n:.1f}%)")

    # ── 5. ⚙️ Does L+R land in NEXT draw mains? ─────────────────────────────
    nxt_sum_in_mains = 0
    nxt_diff_in_mains = 0
    nxt_R_carries_forward = 0
    nxt_R_swisscircle_in_mains = 0
    swisscircle = lambda x: ((x - 1 + 21) % 42) + 1
    nxt_count = 0
    for i, d in enumerate(recent[:-1]):
        L = d["lucky"]; R = d["replay"]
        if L is None or R is None:
            continue
        nxt_count += 1
        nxt = recent[i + 1]
        m = nxt["p"]
        if (L + R) in m:
            nxt_sum_in_mains += 1
        if abs(R - L) in m:
            nxt_diff_in_mains += 1
        if R in m:
            nxt_R_carries_forward += 1
        if swisscircle(R) in m:
            nxt_R_swisscircle_in_mains += 1

    print(f"\n🔮 NEXT-DRAW PROJECTION ({nxt_count} consecutive pairs):")
    print(f"   (🍀+R) appears in NEXT mains: {nxt_sum_in_mains}/{nxt_count} "
          f"= {100*nxt_sum_in_mains/max(1,nxt_count):.1f}%")
    print(f"   |R−🍀| appears in NEXT mains: {nxt_diff_in_mains}/{nxt_count} "
          f"= {100*nxt_diff_in_mains/max(1,nxt_count):.1f}%")
    print(f"   R carries to NEXT mains:     {nxt_R_carries_forward}/{nxt_count} "
          f"= {100*nxt_R_carries_forward/max(1,nxt_count):.1f}%")
    print(f"   Swiss-circle(R) → NEXT main: {nxt_R_swisscircle_in_mains}/{nxt_count} "
          f"= {100*nxt_R_swisscircle_in_mains/max(1,nxt_count):.1f}%")

    # ── 6. 🍀 acts as a step/scaler? Test: R = P[🍀] OR R = P[🍀] ± 1 ────────
    R_eq_p_lucky = 0
    R_neighbor_p_lucky = 0
    for d in recent:
        L = d["lucky"]; R = d["replay"]
        P = d["p"]
        if L is None or R is None or not (1 <= L <= 6) or L - 1 >= len(P):
            continue
        if R == P[L - 1]:
            R_eq_p_lucky += 1
        if abs(R - P[L - 1]) <= 2:
            R_neighbor_p_lucky += 1

    valid = sum(1 for d in recent if d.get("lucky") and d.get("replay") and 1 <= d["lucky"] <= 6 and len(d["p"]) >= d["lucky"])
    print(f"\n🎯 R = P[🍀] (lucky as exact position pointer): "
          f"{R_eq_p_lucky}/{valid} = {100*R_eq_p_lucky/max(1,valid):.1f}%")
    print(f"🪞 R within ±2 of P[🍀]: {R_neighbor_p_lucky}/{valid} = "
          f"{100*R_neighbor_p_lucky/max(1,valid):.1f}%  (baseline ≈ 12%)")

    # ── 7. 🍀 helps R via Swiss-circle: R = circle(P[🍀])? ──────────────────
    R_eq_circle_p_lucky = 0
    for d in recent:
        L = d["lucky"]; R = d["replay"]
        P = d["p"]
        if L is None or R is None or not (1 <= L <= 6) or L - 1 >= len(P):
            continue
        if R == swisscircle(P[L - 1]):
            R_eq_circle_p_lucky += 1
    print(f"🔄 R == Swiss-circle(P[🍀]): {R_eq_circle_p_lucky}/{valid} = "
          f"{100*R_eq_circle_p_lucky/max(1,valid):.1f}%")

    # ── 8. 🍀 by itself fires often as digit of R? (e.g. 🍀=3, R=23 → '3' digit)
    digit_in_R = 0
    for d in recent:
        L = d["lucky"]; R = d["replay"]
        if L is None or R is None:
            continue
        if str(L) in str(R):
            digit_in_R += 1
    print(f"🔠 🍀 digit appears in R: {digit_in_R}/{n} = {100*digit_in_R/n:.1f}%")

    # ── 9. 🍀 + 🍀 = R or × 🍀 = R? ─────────────────────────────────────────
    twin_eq = 0
    six_times = 0
    seven_times = 0
    for d in recent:
        L = d["lucky"]; R = d["replay"]
        if L is None or R is None:
            continue
        if R == L * 2:
            twin_eq += 1
        if R == L * 6:
            six_times += 1
        if R == L * 7:
            seven_times += 1
    print(f"📦 R == 🍀 × 2: {twin_eq}/{n} = {100*twin_eq/n:.1f}%")
    print(f"📦 R == 🍀 × 6: {six_times}/{n} = {100*six_times/n:.1f}%")
    print(f"📦 R == 🍀 × 7: {seven_times}/{n} = {100*seven_times/n:.1f}%")

    # ── 10. Wed vs Sat split ───────────────────────────────────────────────
    print(f"\n🗓️ WED vs SAT split:")
    for wd in ("Wed", "Sat"):
        sub = [d for d in recent if d["wd"] == wd]
        sub_n = len(sub)
        relock = sum(1 for d in sub if d.get("lucky") == d.get("replay"))
        sub_pointer_hits = 0
        sub_valid = 0
        for d in sub:
            L = d.get("lucky"); R = d.get("replay")
            P = d["p"]
            if L is None or R is None or not (1 <= L <= 6) or L - 1 >= len(P):
                continue
            sub_valid += 1
            if R == P[L - 1]:
                sub_pointer_hits += 1
        print(f"   {wd}: n={sub_n}  RE-LOCK {relock}/{sub_n}={100*relock/max(1,sub_n):.1f}%  "
              f"P[🍀]==R {sub_pointer_hits}/{sub_valid}={100*sub_pointer_hits/max(1,sub_valid):.1f}%")

    # ── 11. Top (🍀, R) pairs ──────────────────────────────────────────────
    print(f"\n🥇 TOP (🍀, R) PAIRS in 2 yrs:")
    for (L, R), c in pair_counter.most_common(15):
        print(f"   🍀={L:2d}  R={R:2d}   ×{c}")


if __name__ == "__main__":
    main()
