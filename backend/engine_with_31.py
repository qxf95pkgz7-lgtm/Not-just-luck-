"""
🎻 Engine run with 31 LOCKED as anchor — all 34 book laws fire.
Target = next Euro draw after today.
"""
import asyncio
import sys
from datetime import datetime as dt, timedelta
from cosmic_engine import (
    load_euro_draws, find_last_family_rare, build_convergence_board,
    rank_suspects, rank_stars, decade, EURO_RANGE,
)
from motor.motor_asyncio import AsyncIOMotorClient
import os
import itertools
from collections import Counter


def next_euro_draw(today: dt) -> dt:
    """Euro draws are Tuesday(1) and Friday(4). Find next."""
    wd = today.weekday()
    if wd < 1:
        delta = 1 - wd
    elif wd < 4:
        delta = 4 - wd
    elif wd == 4:
        delta = 4  # today is Fri, go to next Tue
    else:  # Sat/Sun
        delta = (1 - wd) % 7
    return today + timedelta(days=delta) if delta else today + timedelta(days=1)


async def main(target_str=None):
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    draws = await load_euro_draws(db)

    if target_str:
        target_date = dt.strptime(target_str, '%d.%m.%Y')
    else:
        target_date = next_euro_draw(dt.now())

    found = find_last_family_rare(draws, target_date)
    if not found:
        print("No rare found before target."); return
    _, rc0 = found

    cycle_draws = [d for d in draws if rc0['dt'] < d['_dt'] < target_date]
    target_cycle_pos = len(cycle_draws) + 1

    lenses = build_convergence_board(rc0, cycle_draws, target_date, target_cycle_pos)
    ranked = rank_suspects(lenses)
    star_ranking = rank_stars(cycle_draws, rc0['s'], target_cycle_pos)

    fr_low = rc0['family'] * 10 if rc0['family'] > 0 else 1
    fr_high = rc0['family'] * 10 + 10 if rc0['family'] > 0 else 10
    family_set = set(range(fr_low, fr_high))
    rc0_family_in = {x for x in rc0['n'] if decade(x) == rc0['family']}
    hungry = family_set - rc0_family_in

    print("="*78)
    print(f"🎻🎧 COSMIC ENGINE — TARGET {target_date.strftime('%d-%m-%Y (%A)')}")
    print("="*78)
    print(f"Rare anchor RC0: {rc0['date']} · mains={rc0['n']} · stars={rc0['s']}")
    print(f"Family: decade-{rc0['family']}0s · Outlier: {rc0['outlier']}")
    print(f"Target is d{target_cycle_pos} since RC0 · {len(cycle_draws)} cycle draws")
    print(f"Hungry family ({rc0['family']}0s): {sorted(hungry)}")
    print(f"Star top-6: {star_ranking[:6]}")
    print()

    # ── 31's lens readout ──
    l31 = lenses[31]
    count31 = len(l31)
    rank_of_31 = next((i+1 for i, (n, c, _) in enumerate(ranked) if n == 31), None)
    print("─"*78)
    print(f"🎯 NUMBER 31 — THE ANCHOR · {count31} lenses · rank #{rank_of_31} in suspect list")
    print("─"*78)
    if l31:
        for law in l31:
            print(f"   🔸 {law}")
    else:
        print("   (no lens fires on 31 in current cycle — pure wild card)")

    # Is 31 in hungry set?
    if 31 in hungry:
        print(f"   ✅ 31 is in the HUNGRY FAMILY (Law 31 → cosmic certainty)")
    # Decade 3 family analysis
    d30s = [n for n in range(30, 40) if lenses[n]]
    print(f"   📊 30s decade lenses firing on: {d30s}")

    # ── TOP SUSPECTS WITHOUT 31 CONSTRAINT ──
    print()
    print("─"*78)
    print("🏆 TOP SUSPECTS (all laws, ranked)")
    print("─"*78)
    for i, (n, c, laws) in enumerate(ranked[:25], 1):
        laws_str = ", ".join(laws[:4]) + (f" +{len(laws)-4}" if len(laws) > 4 else "")
        marker = "⭐" if n == 31 else "  "
        print(f"   {marker} #{i:>2}  {n:>2}  ({c} lenses)  {laws_str}")

    # ── TICKETS WITH 31 LOCKED ──
    print()
    print("─"*78)
    print("🎫 TICKETS — 31 LOCKED AS ANCHOR")
    print("─"*78)

    top_tier = [n for n, c, _ in ranked if c >= 3 and n != 31]
    mid_tier = [n for n, c, _ in ranked if c == 2 and n != 31]
    # prioritize decade-30s family (natural friends of 31)
    d30s_friends = sorted([n for n in range(30, 40) if n != 31 and lenses[n]],
                          key=lambda x: -len(lenses[x]))
    hungry_no31 = sorted([n for n in hungry if n != 31], key=lambda x: -len(lenses[x]))
    date_lenses = [n for n, _, l in ranked if n != 31 and any('date' in x for x in l)]
    outlier_lenses = [n for n, _, l in ranked if n != 31 and any('outlier' in x for x in l)]
    sk_lenses = [n for n, _, l in ranked if n != 31 and any('star-king' in x for x in l)]

    top_stars = star_ranking[:6]
    star_pairs = list(itertools.combinations(top_stars, 2))

    archetypes = []

    # 1. 31 + top symphony
    if len(top_tier) >= 4:
        archetypes.append(("31+top-symphony", sorted([31] + top_tier[:4])))

    # 2. 31 + decade-30s family (anchor the Outlier-P2 read)
    if len(d30s_friends) >= 4:
        archetypes.append(("31+30s-family-lock", sorted([31] + d30s_friends[:4])))

    # 3. 31 + hungry family
    if len(hungry_no31) >= 4:
        archetypes.append(("31+hungry-loaded", sorted([31] + hungry_no31[:4])))

    # 4. 31 + date-mirrors
    if len(date_lenses) >= 3:
        pool = list(dict.fromkeys([31] + date_lenses[:5] + top_tier + mid_tier))
        picks = sorted(pool[:5])
        if len(picks) == 5:
            archetypes.append(("31+date-mirror", picks))

    # 5. 31 + outlier paths
    if len(outlier_lenses) >= 4:
        archetypes.append(("31+outlier-paths", sorted(set([31] + outlier_lenses[:4]))[:5]))

    # 6. 31 + star-king harmonic
    if len(sk_lenses) >= 3:
        pool = list(dict.fromkeys([31] + sk_lenses[:5] + top_tier + mid_tier))
        picks = sorted(pool[:5])
        if len(picks) == 5:
            archetypes.append(("31+star-king", picks))

    # 7. 31 + P2-outlier signature (decade-30s + low-anchor)
    # When P2=31, the "30s decade-family + one sub-25 bridge" shape
    lows = [n for n, c, _ in ranked if n < 25 and c >= 2 and n != 31][:2]
    if len(d30s_friends) >= 2 and len(lows) >= 1:
        picks = sorted(set([31] + d30s_friends[:2] + lows + top_tier[:1]))[:5]
        if len(picks) == 5:
            archetypes.append(("31+P2-outlier-signature", picks))

    # 8. 31 + mirror-carrier / flip-wrap bridge
    bridge = [n for n, _, l in ranked if n != 31 and any('carrier' in x or 'flip-wrap' in x or 'sum-circle' in x for x in l)]
    if len(bridge) >= 3:
        picks = sorted(set([31] + bridge[:3] + top_tier[:1]))[:5]
        if len(picks) == 5:
            archetypes.append(("31+cosmic-bridge", picks))

    # Fill with random mixed tickets (deterministic seed)
    import random
    rng = random.Random(31)
    all_pool = list(set(top_tier + mid_tier + list(hungry_no31)[:8]))
    while len(archetypes) < 10 and len(all_pool) >= 4:
        picks = rng.sample(all_pool, 4)
        picks = sorted(set([31] + picks))[:5]
        if len(picks) == 5 and picks not in [a[1] for a in archetypes]:
            archetypes.append(("31+mixed-symphony", picks))

    for i, (name, mains) in enumerate(archetypes[:10], 1):
        stars = list(star_pairs[(i-1) % len(star_pairs)]) if star_pairs else [1, 2]
        m = "-".join(f"{x:02d}" for x in mains)
        s = f"{stars[0]:02d}-{stars[1]:02d}"
        print(f"  {i:>2}. [{name:<26}] {m}   ⭐{s}")

    # ── THE DJ'S VERDICT ──
    print()
    print("─"*78)
    print("🍀 THE DJ'S VERDICT")
    print("─"*78)
    if count31 == 0:
        print("   ⚠️ 31 has ZERO lens support this cycle — forcing it is a pure hunch play.")
        print(f"   The engine's natural top-tier is {sorted([n for n,c,_ in ranked if c>=3])[:8]}.")
    elif count31 == 1:
        print(f"   ⚠️ 31 has only 1 lens ({l31[0]}) — weak signal, risky anchor.")
    elif count31 == 2:
        print(f"   🎺 31 passes the Two-Lens Floor (Law 27). Mid-tier anchor — playable.")
    else:
        print(f"   🔥 31 is RESONATING HARD — {count31} lenses. Top-tier anchor — strong play.")

    if 31 in hungry:
        print(f"   ✅ 31 is hungry-family (Law 31, early-cycle cosmic certainty).")
    if target_cycle_pos <= 3 and 31 in hungry:
        print(f"   🏆 d{target_cycle_pos} + hungry-31 = MAXIMUM cosmic weight.")
    if 7 <= target_cycle_pos <= 9:
        print(f"   📍 d{target_cycle_pos} sweet spot — date-mirror28 dominates.")

    print()


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(target))
