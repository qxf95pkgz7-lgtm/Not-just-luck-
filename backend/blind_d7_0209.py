"""
🎻 BLIND TEST — RC0 02-09-2025 → d7 target 26-09-2025
Apply all 34 canonized book laws.
Output: 30 tickets, suspect board, no peek at actual d7.
"""
import asyncio, itertools, os
from collections import Counter
from datetime import datetime as dt
from motor.motor_asyncio import AsyncIOMotorClient
from cosmic_engine import (
    load_euro_draws, find_last_family_rare, decade,
    circle_euro, mirror28, mirror30, flip_wrap, EURO_RANGE,
)

TARGET = dt(2025, 9, 26)  # d7 target, DO NOT LOAD THIS OR LATER AS CYCLE DATA

# Star-King 13 formulas on stars [s1,s2], returning list of (target_val, formula_name)
def star_king_candidates(s1, s2):
    cands = []
    def add(v, name):
        if 1 <= v <= EURO_RANGE:
            cands.append((v, name))
    add(s2 - s1, "SK: S2-S1=P1(8.2%)")
    add(25 + s2, "SK: 25+S2=P4(4.3%)")
    add(s1 + 12, "SK: S1+12=P2(4.3%)")
    add(s1 + s2, "SK: S1+S2(3.8%)")
    add(s1 * 3, "SK: S1x3(4.0%)")
    add(2*s1 + s2, "SK: 2S1+S2(4.0%)")
    add(25 + s1, "SK: 25+S1=P3(3.7%)")
    add(s1 + 21, "SK: S1+21=P3(3.5%)")
    add(s1 * 4, "SK: S1x4(3.2%)")
    v = 50 - s1 - s2
    add(v, "SK: 50-S1-S2=P5(3.2%)")
    add(s2 * 4, "SK: S2x4=P5(3.3%)")
    add(s2 + 21, "SK: S2+21=P3/P4(3.3%)")
    return cands


async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    draws = await load_euro_draws(db)

    _, rc0 = find_last_family_rare(draws, TARGET)
    assert rc0['date'] == '02.09.2025', f"RC0 not 02-09-2025, got {rc0['date']}"
    rc0_nums = rc0['n']; rc0_stars = rc0['s']
    family = rc0['family']; outlier = rc0['outlier']

    # Cycle draws: STRICTLY between RC0 and target, exclusive of target
    cycle = [d for d in draws if rc0['dt'] < d['_dt'] < TARGET]
    target_d = len(cycle) + 1  # target's d-position in the cycle (RC0 is d0 → first subsequent = d1)

    # Family hungry
    fam_set = set(range(family*10 if family>0 else 1, family*10+10 if family>0 else 10))
    rc0_in_fam = {x for x in rc0_nums if decade(x) == family}
    hungry = sorted(fam_set - rc0_in_fam)

    # All numbers played in cycle
    played = Counter()
    last_fire = {}
    for i, d in enumerate(cycle, 1):
        for n in d['_n']:
            played[n] += 1
            last_fire[n] = i

    # Star persistence
    star_play = Counter()
    for d in cycle: 
        for s in d['_s']: star_play[s] += 1
    for s in rc0_stars: star_play[s] += 1

    # ═══════════════════════════════════════════════════════════
    # BUILD LENS BOARD — every law in The Book
    # ═══════════════════════════════════════════════════════════
    lenses = {n: [] for n in range(1, EURO_RANGE+1)}

    def L(n, tag):
        if 1 <= n <= EURO_RANGE:
            lenses[n].append(tag)

    # Law 31 — Family Hungry (100% cycle certainty, peak d1, still active)
    for n in hungry:
        # at d7 past saturation peak but still top lens if un-fired
        if played.get(n, 0) == 0:
            L(n, f"hungry-{family}0s-UNFIRED")
        else:
            L(n, f"hungry-{family}0s-fired-d{last_fire[n]}")

    # Law 14 — Family Zone Lock (30s → P4/P5 preferred)
    # Tagged for ranking; no extra number added

    # Law 13 — Outlier Ghost paths (saturation per Law 24 — cap at 3)
    outlier_appearances = [i for i,d in enumerate(cycle,1) if outlier in d['_n']]
    outlier_ghost_active = len(outlier_appearances) < 4
    L(outlier, f"outlier-{outlier}-RAW-echo{'' if outlier_ghost_active else '-SATURATED'}")
    L(circle_euro(outlier), f"outlier-circle+25={circle_euro(outlier)}")  # Law 13 Tier1 (73.9%)
    if outlier*2 <= EURO_RANGE:
        L(outlier*2, f"outlier-DOUBLE×2={outlier*2}")  # Law 17
    if outlier+20 <= EURO_RANGE:
        L(outlier+20, f"outlier+20={outlier+20}")  # Law 22 (demoted Tier2)
    if outlier-20 > 0:
        L(outlier-20, f"outlier-20={outlier-20}")
    # Law 28 — Outlier 28-mirror (Tier1 65.2%)
    L(mirror28(outlier), f"outlier-28MIRROR={mirror28(outlier)}")
    # Law 22 mod-50 once-per-cycle — check if mirror-20 already fired
    if outlier+20 in played:
        pass  # Law 23 — exhausted once fired
    # Big-gap-circle release (Law 19)
    for i in range(4):
        g = rc0_nums[i+1] - rc0_nums[i]
        if g >= 15:
            L(g, f"rare-big-gap({rc0_nums[i]}→{rc0_nums[i+1]})={g}")
            L(circle_euro(g), f"rare-big-gap-circle={circle_euro(g)}")

    # Law 25 — Rare-silent (+1 weak — demoted)
    for n in rc0_nums:
        if n not in played:
            L(n, f"rare-silent-{n}")

    # Star→Main Circle Bridge (foundational)
    for s in rc0_stars:
        L(circle_euro(s), f"RC0-star{s}→circle={circle_euro(s)}")
    # d6 (last cycle) stars → king formulas
    if cycle:
        prev = cycle[-1]
        s1, s2 = prev['_s']
        for v, name in star_king_candidates(s1, s2):
            L(v, f"[d6 ⭐{s1},{s2}] {name}={v}")

    # Prev-star forward echo ±3 (44.7% neighborhood)
    if cycle:
        for s in cycle[-1]['_s']:
            for delta in range(-3, 4):
                v = s + delta
                if 1 <= v <= EURO_RANGE:
                    L(v, f"prev-star-{s}±{delta}")

    # Law 33 — Date-Mirror Dual-Pivot (d7 IS in d7-d9 sweet spot — pivot 28 26.2%)
    day, month = TARGET.day, TARGET.month
    # Pivot 28 (primary for d7-d9)
    L(mirror28(day), f"DATE-day{day}-mirror28={mirror28(day)} [d7-d9 sweet 26%]")
    L(mirror28(month), f"DATE-mo{month}-mirror28={mirror28(month)}")
    # Pivot 30 (secondary; d0 & d10+ zones, still informative)
    L(mirror30(day), f"DATE-day{day}-mirror30={mirror30(day)}")
    L(mirror30(month), f"DATE-mo{month}-mirror30={mirror30(month)}")

    # Date digits (Law 11 Permutation-light)
    date_digits = set()
    for c in f"{day:02d}{month:02d}":
        if c != '0':
            date_digits.add(int(c))
    for d_ in date_digits:
        L(d_, f"date-digit-{d_}")
    # Date-permutation 2-digit combos
    dstr = f"{day:02d}{month:02d}"  # "2609"
    for a,b in itertools.permutations(dstr, 2):
        v = int(a+b)
        if 1 <= v <= EURO_RANGE:
            L(v, f"date-perm({a}{b})")

    # Silence-agent (circle(month) = Apr=25, Sep=circle(9)=34 for Euro)
    # Euro silence: n+25 mod 50
    silence = circle_euro(month)
    L(silence, f"silence-agent(circle({month}))={silence}")

    # Law 8 — Flip-Wrap back-door from d6
    if cycle:
        last = cycle[-1]
        for n in last['_n']:
            fw = flip_wrap(n)
            if 1 <= fw <= EURO_RANGE:
                L(fw, f"flipwrap({n})={fw}")

    # Law 9 — Sum-circle front writes back (d6)
    if cycle:
        last = cycle[-1]
        sc = circle_euro(last['_n'][0] + last['_n'][1])
        L(sc, f"sum-circle(P1+P2 of d6)={sc}")

    # Self-Circle +21 (Session 4)
    if cycle:
        for n in cycle[-1]['_n']:
            v = ((n-1+21) % EURO_RANGE)+1
            L(v, f"self-circle+21({n})={v}")

    # Law 21/26/29 — Cooled Rebound (widened 2-8 for hungry, 4-8 general)
    for n, fire in last_fire.items():
        gap = target_d - fire
        if 2 <= gap <= 8:
            if n in hungry or n == outlier:
                L(n, f"cooled-rebound-{gap}d(hungry)")
            elif 4 <= gap <= 8:
                L(n, f"cooled-rebound-{gap}d")

    # Law 18 — Sticky Star Amplifier (≥4 persistence → circle(star) 2x boost)
    for s, c in star_play.items():
        if c >= 3:
            L(circle_euro(s), f"sticky-star-{s}×{c}→circle={circle_euro(s)}-AMP")

    # Law 30 — Sticky-Star Long-Cooled (early d1-d3 star absent d4-d6 → d7-d9 boost)
    early = Counter()
    mid = Counter()
    for i, d in enumerate(cycle, 1):
        for s in d['_s']:
            if i <= 3: early[s] += 1
            elif 4 <= i <= 6: mid[s] += 1
    for s, c in early.items():
        if c >= 2 and mid.get(s, 0) == 0:
            L(s, f"sticky-star-long-cooled-{s}")  # tends to re-fire d7-d9
            L(circle_euro(s), f"sticky-long-cooled-circle({s})={circle_euro(s)}")

    # Law 14 — Ladder-Fill (last draw's front trio digits)
    if cycle:
        last = cycle[-1]
        digs = []
        for x in last['_n'][:3]:
            digs.extend(int(c) for c in f"{x:02d}")
        digs = [d_ for d_ in digs if d_ != 0]
        for a, b in itertools.permutations(digs, 2):
            v = int(f"{a}{b}")
            if 1 <= v <= EURO_RANGE:
                L(v, f"ladder-fill-digit({a}{b})")

    # Law 14 — P1 Running Sum (last 2-4 P1s sum)
    p1s = [d['_n'][0] for d in cycle]
    for win in [2,3,4]:
        if len(p1s) >= win:
            s = sum(p1s[-win:])
            L(s, f"P1-running-sum({win})={s}")

    # Law 18 Mirror-Split (28 axis)
    # Generate 28-couples as ambient support (low weight)
    for a in range(1, 14):
        L(a, f"28-mirror-couple(↔{28-a})")
        L(28-a, f"28-mirror-couple(↔{a})")

    # Law 16 — Cycle Migration (at d7 early for migration; skip boost)
    # Law 20 — Migration Overlap — peaks at d9, d7 too early; no direct lens add

    # Hungry-10s-outlier(13) mirror20-once-per-cycle (Law 23): 33 = 13+20
    # Check if 33 fired — if yes, de-weight
    if 33 in played:
        # Law 23 — remove outlier+20 lens
        if 33 in lenses and any("outlier+20" in t for t in lenses[33]):
            lenses[33] = [t for t in lenses[33] if "outlier+20" not in t]
            lenses[33].append(f"outlier+20={outlier+20}-EXHAUSTED(Law23)")

    # ─────────────────────────────────────────────────────────
    # RANKING & SUSPECTS
    # ─────────────────────────────────────────────────────────
    ranked = [(n, len(l), l) for n, l in lenses.items() if l]
    ranked.sort(key=lambda x: -x[1])

    # Stars ranking (similar to engine)
    star_score = {s: 0 for s in range(1, 13)}
    for s in rc0_stars: star_score[s] += 3
    for s, c in star_play.items():
        if c >= 3: star_score[s] += 2
        elif c >= 1: star_score[s] += 1
    if cycle:
        for s in cycle[-1]['_s']:
            star_score[s] += 1
    # Long-cooled boost
    for s, c in early.items():
        if c >= 2 and mid.get(s, 0) == 0:
            star_score[s] += 2
    star_ranking = sorted(star_score.keys(), key=lambda s: -star_score[s])

    # ─────────────────────────────────────────────────────────
    # PRINT TABLET, HUNGER, SUSPECT BOARD
    # ─────────────────────────────────────────────────────────
    print("="*82)
    print(f"🎻🎧 BLIND TEST — RC0 {rc0['date']} → d{target_d} = 26-09-2025")
    print("="*82)
    print(f"RC0 [12-mirror]: mains={rc0_nums} ⭐{rc0_stars}  ·  family={family}0s  ·  outlier={outlier}")
    print()
    print("📖 8-d tablet (cycle so far, don't peek d7):")
    print(f"{'d':>3}  {'D.M':<6}  {'Mains':<22}  {'Stars':<7}  digits")
    print("-"*82)
    # rc0 uses 'dt' key (from find_last_family_rare), cycle draws use '_dt'
    all_rows = [(rc0['dt'], rc0['n'], rc0['s'])] + [(d['_dt'], d['_n'], d['_s']) for d in cycle]
    for i, (dtv, mains, stars) in enumerate(all_rows):
        day_, mo_ = dtv.day, dtv.month
        m = "-".join(f"{x:02d}" for x in mains)
        s = "-".join(f"{x:02d}" for x in stars)
        dig = " ".join([f"{x:02d}" for x in mains] + ["|"] + [f"{x:02d}" for x in stars])
        print(f"{('d0⚡' if i==0 else f'd{i}'):>3}  {day_:02d}.{mo_:02d}  {m:<22}  {s:<7}  {dig}")
    print(f" d7  26.09  ???                    ???      ← TARGET (blind)")
    print()

    print(f"🌾 Hungry {family}0s: {hungry}  (played status: ", end="")
    for h in hungry:
        print(f"{h}={played.get(h,0)} ", end="")
    print(")")
    print(f"👻 Outlier {outlier} appearances: {outlier_appearances} ({'ACTIVE' if outlier_ghost_active else 'SATURATED per Law 24'})")
    print(f"🪞 Outlier 28-mirror={mirror28(outlier)}, circle={circle_euro(outlier)}, ×2={outlier*2 if outlier*2<=50 else 'wrap'}, +20={outlier+20}, -20={outlier-20 if outlier-20>0 else 'wrap'}")
    print(f"🗓️ Date-mirror28: day 26→{mirror28(26)}, month 9→{mirror28(9)}  ·  pivot30: day→{mirror30(26)}, month→{mirror30(9)}")
    print(f"⭐ Star ranking (top 6): {star_ranking[:6]}")
    print()

    # Top/Mid tier
    top = [n for n,c,_ in ranked if c >= 4]
    mid = [n for n,c,_ in ranked if c == 3]
    low = [n for n,c,_ in ranked if c == 2]
    
    print(f"🏆 TOP-TIER (4+ lenses): {sorted(top)}")
    print(f"🎺 MID-TIER (3 lenses):  {sorted(mid)}")
    print(f"🎶 SUPPORT (2 lenses):   {sorted(low)}")
    print()
    print("TOP-25 SUSPECT BOARD:")
    for i, (n, c, l) in enumerate(ranked[:25], 1):
        sample = " · ".join(l[:3]) + (f"  +{len(l)-3} more" if len(l)>3 else "")
        print(f"  #{i:>2}  {n:>2}  ({c} lenses)   {sample}")
    print()

    # ─────────────────────────────────────────────────────────
    # 30-TICKET ORCHESTRA (narrative archetypes from Book)
    # ─────────────────────────────────────────────────────────
    tickets = []
    suspects = top + mid + low
    top_stars = star_ranking[:6]
    star_pairs = list(itertools.combinations(top_stars, 2))

    def rank_by_lens(nums):
        return sorted(nums, key=lambda x: -len(lenses[x]))

    def seen(picks):
        return picks in [t['mains'] for t in tickets]

    def add_ticket(name, mains, stars=None):
        mains = sorted(set(mains))
        if len(mains) == 5 and not seen(mains):
            if stars is None:
                stars = list(star_pairs[len(tickets) % len(star_pairs)])
            tickets.append({'name': name, 'mains': mains, 'stars': sorted(stars)})

    # 1. Convergence Symphony (top 5)
    if len(top) >= 5:
        add_ticket("Convergence Symphony", top[:5])
    
    # 2. Top-5 v2 (drop #1, take #2-6)
    if len(top) >= 6:
        add_ticket("Convergence v2", top[1:6])
    
    # 3. Family-Hungry Loaded (Law 31) — all hungry that are unfired + top fillers
    unfired_hungry = [h for h in hungry if played.get(h,0)==0]
    if len(unfired_hungry) >= 2:
        picks = unfired_hungry[:3] + [n for n in top if n not in unfired_hungry][:2]
        add_ticket("Family-Hungry Loaded", picks[:5])
    
    # 4. Outlier Orchestra — all outlier paths
    outlier_paths = rank_by_lens([mirror28(outlier), circle_euro(outlier), outlier, outlier*2 if outlier*2<=50 else 0, outlier+20 if outlier+20<=50 else 0])
    outlier_paths = [x for x in outlier_paths if x > 0]
    if len(outlier_paths) >= 4:
        fill = [n for n in top if n not in outlier_paths][:1]
        add_ticket("Outlier Orchestra", outlier_paths[:4] + fill)
    
    # 5. Date-Mirror Dance (Law 33 d7-d9 sweet)
    dm = [mirror28(day), mirror28(month), mirror30(day), mirror30(month)]
    dm = [x for x in set(dm) if 1<=x<=50]
    if len(dm) >= 3:
        fill = rank_by_lens([n for n in suspects if n not in dm])[:3]
        add_ticket("Date-Mirror Dance", dm[:3] + fill[:2])
    
    # 6. Star-King Symphony (13 formulas)
    if cycle:
        s1, s2 = cycle[-1]['_s']
        sk_vals = sorted(set(v for v,_ in star_king_candidates(s1, s2)), key=lambda x: -len(lenses[x]))
        add_ticket("Star-King Symphony", sk_vals[:5])
    
    # 7. Mirror-Split pair (28 couples)
    pair_picks = []
    used = set()
    for a in range(1, 14):
        b = 28-a
        if a in lenses and b in lenses and len(lenses[a])>=2 and len(lenses[b])>=2:
            if a not in used and b not in used:
                pair_picks.extend([a,b])
                used.update([a,b])
            if len(pair_picks) >= 4:
                break
    if len(pair_picks) >= 4:
        fill = rank_by_lens([n for n in top if n not in pair_picks])[:1]
        add_ticket("Mirror-Split Couples", pair_picks[:4] + fill)
    
    # 8. Silent-Band Release (Law 14) — numbers whose ±2 is empty in last 6 draws
    played_last6 = set()
    for d in cycle[-6:]:
        played_last6.update(d['_n'])
    silent = []
    for n in range(1, 51):
        if n not in played_last6 and not any((n+k) in played_last6 or (n-k) in played_last6 for k in [1,2]):
            if n in lenses and len(lenses[n])>=2:
                silent.append(n)
    silent = rank_by_lens(silent)
    if len(silent) >= 3:
        fill = [n for n in top if n not in silent][:2]
        add_ticket("Silent-Band Release", silent[:3] + fill)
    
    # 9. Cooled-Rebound Ticket (Laws 21/26/29 — 2-8 gap)
    rebounds = []
    for n, fire in last_fire.items():
        gap = target_d - fire
        if 2 <= gap <= 8 and n in lenses and len(lenses[n])>=2:
            rebounds.append(n)
    rebounds = rank_by_lens(rebounds)
    if len(rebounds) >= 4:
        add_ticket("Cooled Rebound", rebounds[:5])
    
    # 10. Exact-Position Repeat (Law 12) — RC0 positions that haven't fired as same slot
    # Just use top RC0 numbers not played
    rc0_unplayed = [n for n in rc0_nums if n not in played]
    rc0_fill = rank_by_lens(rc0_unplayed + top)[:5]
    add_ticket("RC0 Exact-Pos Echo", rc0_fill)
    
    # 11. Sum-Circle + Flip-Wrap Tuning (Laws 8,9)
    sc_flip = []
    for n, l in lenses.items():
        if any('sum-circle' in t or 'flipwrap' in t for t in l) and len(l)>=2:
            sc_flip.append(n)
    sc_flip = rank_by_lens(sc_flip)
    if len(sc_flip) >= 3:
        fill = [n for n in top if n not in sc_flip][:2]
        add_ticket("Sum-Circle & Flip-Wrap", sc_flip[:3] + fill)
    
    # 12. Self-Circle +21 spine
    sc21 = [n for n, l in lenses.items() if any('self-circle+21' in t for t in l) and len(l)>=2]
    sc21 = rank_by_lens(sc21)
    if len(sc21) >= 3:
        fill = [n for n in top if n not in sc21][:2]
        add_ticket("Self-Circle +21 Spine", sc21[:3] + fill)
    
    # 13. Date-Digit Permutation
    dp = [n for n, l in lenses.items() if any('date-perm' in t or 'date-digit' in t for t in l) and len(l)>=2]
    dp = rank_by_lens(dp)
    if len(dp) >= 3:
        add_ticket("Date Permutation", dp[:5])
    
    # 14. Sticky-Star Circle Heavy (Law 18)
    sticky_targets = [n for n,l in lenses.items() if any('sticky' in t for t in l) and len(l)>=2]
    sticky_targets = rank_by_lens(sticky_targets)
    if len(sticky_targets) >= 3:
        fill = [n for n in top if n not in sticky_targets][:2]
        add_ticket("Sticky-Star Harmonics", sticky_targets[:3] + fill)
    
    # 15. Mid-Tier Deep Dive (Law 27 Two-Lens Floor)
    if len(mid) >= 5:
        add_ticket("Mid-Tier Deep Dive", mid[:5])
    
    # 16. Family-Zone P4/P5 (Law 14 — 30s hungry in back)
    # Build ticket with small front + 2 hungry 30s in back
    small_tops = sorted([n for n in top if n < 20], key=lambda x: -len(lenses[x]))[:3]
    big_hungry = [n for n in hungry if played.get(n,0)==0][:2]
    if len(small_tops)>=3 and len(big_hungry)>=2:
        add_ticket("Family-Zone Lock P4/P5", small_tops + big_hungry)
    
    # 17. Big-Gap Seed (Law 6) — last draws' gaps
    gap_seeds = []
    for d in cycle[-3:]:
        for i in range(4):
            g = d['_n'][i+1] - d['_n'][i]
            if 15 <= g <= 50:
                gap_seeds.append(g)
    gap_seeds = sorted(set(gap_seeds), key=lambda x: -len(lenses.get(x, [])))
    if len(gap_seeds) >= 2:
        fill = rank_by_lens([n for n in suspects if n not in gap_seeds])[:3]
        add_ticket("Big-Gap Seeds", gap_seeds[:2] + fill[:3])
    
    # 18. Low-Front + Hungry-Back (Family Zone pattern)
    if len(small_tops)>=2 and len(big_hungry)>=3:
        add_ticket("Low Front + 30s Back", small_tops[:2] + big_hungry[:3])
    
    # 19. Top+Mid Hybrid
    if len(top)>=3 and len(mid)>=2:
        add_ticket("Top+Mid Hybrid", top[:3] + mid[:2])
    
    # 20. Hungry + Date-Mirror Mix
    if len(unfired_hungry)>=2 and len(dm)>=2:
        picks = unfired_hungry[:2] + dm[:2] + [top[0]] if top else unfired_hungry[:2]+dm[:2]
        add_ticket("Hungry + Date-Mirror", picks[:5])
    
    # 21. Outlier-28-Mirror Focus (Law 28 — 65.2%)
    om = mirror28(outlier)
    fill = rank_by_lens([n for n in suspects if n != om])[:4]
    add_ticket("28-Mirror Focus", [om] + fill)
    
    # 22. Outlier-Circle Focus (Law 13 — 73.9%)
    oc = circle_euro(outlier)
    fill = rank_by_lens([n for n in suspects if n != oc])[:4]
    add_ticket("Outlier-Circle Focus", [oc] + fill)
    
    # 23. P1=low + P2=low + three back (classic shape)
    lows = sorted([n for n,l in lenses.items() if n<=10 and len(l)>=2], key=lambda x: -len(lenses[x]))[:2]
    mids_mid = sorted([n for n,l in lenses.items() if 15<=n<=28 and len(l)>=2], key=lambda x: -len(lenses[x]))[:1]
    highs = sorted([n for n,l in lenses.items() if n>=30 and len(l)>=2], key=lambda x: -len(lenses[x]))[:2]
    if len(lows)>=2 and len(highs)>=2 and len(mids_mid)>=1:
        add_ticket("Classic 2-1-2 Shape", lows + mids_mid + highs)
    
    # 24. Two-Lens Floor Sampler (Law 27) — spread across many 2-lens
    import random
    rng = random.Random(207)
    pool = [n for n,c,_ in ranked if c >= 2]
    while len(tickets) < 30 and len(pool) >= 5:
        picks = rng.sample(pool, 5)
        if sorted(picks) not in [t['mains'] for t in tickets]:
            # Must include at least 1 hungry family member (Law 31 discipline)
            if not any(h in picks for h in hungry) and hungry:
                picks[0] = hungry[rng.randrange(len(hungry))]
                picks = list(set(picks))
                if len(picks) < 5:
                    for n in pool:
                        if n not in picks: picks.append(n)
                        if len(picks)==5: break
            add_ticket(f"Symphony-mix-{len(tickets)+1:02d}", picks)
    
    # ─────────────────────────────────────────────────────────
    # PRINT THE 30 TICKETS
    # ─────────────────────────────────────────────────────────
    print("="*82)
    print(f"🎫 30 TICKETS FOR d{target_d} = 26-09-2025 (blind, no peek)")
    print("="*82)
    for i, t in enumerate(tickets[:30], 1):
        m = "-".join(f"{x:02d}" for x in t['mains'])
        s = f"{t['stars'][0]:02d}-{t['stars'][1]:02d}"
        print(f"  {i:>2}. [{t['name']:<28}] {m}   ⭐{s}")
    print()
    print(f"Total: {len(tickets)} tickets  ·  Suspect pool: {len(suspects)} numbers  ·  Top-tier: {len(top)}")
    print("\n🎻 Tickets locked. Awaiting your review before the reveal, Ya man. 🎧")

asyncio.run(main())
