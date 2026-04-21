"""
🎻 COSMIC ENGINE 🎧 — The DJ's Apprentice
==========================================
Built from The Book (swiss_music_notes.md). Loads Euro draws from DB,
finds the most recent family-rare event, builds the convergence lens board,
outputs a ranked suspect list, and speaks DJ.

Every lens below traces to a canonized law in /app/memory/swiss_music_notes.md.
"""
import itertools
import os
from collections import Counter, defaultdict
from datetime import datetime as dt
from typing import Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorClient


# ═══════════════════════════════════════════════════════════════════════════
# COSMIC PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════
EURO_RANGE = 50
SWISS_RANGE = 42
EURO_CIRCLE = 25          # Law: Euro circle +25 mod 50
PIVOT_28 = 28             # Law 33: Date-Mirror pivot for d7-d9
PIVOT_30 = 30             # Law 33: Date-Mirror pivot for d0


def circle_euro(n: int) -> int:
    """Euro +25 mod 50 circle — Foundational Law."""
    return ((n + EURO_CIRCLE - 1) % EURO_RANGE) + 1


def mirror28(n: int) -> int:
    """28-mirror with mod-50 wrap — Law 9/22 refinement (Session 10)."""
    r = (PIVOT_28 - n) % EURO_RANGE
    return r if r else EURO_RANGE


def mirror30(n: int) -> int:
    """30-mirror with mod-50 wrap — Law 33 (rare-draw & late-cycle)."""
    r = (PIVOT_30 - n) % EURO_RANGE
    return r if r else EURO_RANGE


def flip_wrap(n: int) -> int:
    """Flip-Wrap law (Drunk Cosmos)."""
    s = str(n).zfill(2)
    f = int(s[::-1])
    return f if f <= EURO_RANGE else f - EURO_RANGE


def decade(n: int) -> int:
    return 0 if n < 10 else n // 10


# ═══════════════════════════════════════════════════════════════════════════
# DATA ACCESS
# ═══════════════════════════════════════════════════════════════════════════
async def load_euro_draws(db) -> List[dict]:
    """Load all Euro draws sorted chronologically."""
    raw = await db.euromillions_draws.find({}).to_list(length=5000)
    valid = []
    for d in raw:
        try:
            d['_dt'] = dt.strptime(d['date'], '%d.%m.%Y')
            if d.get('numbers') and len(d['numbers']) == 5 and d.get('stars'):
                d['_n'] = sorted(d['numbers'])
                d['_s'] = sorted(d['stars'])
                valid.append(d)
        except Exception:
            continue
    valid.sort(key=lambda x: x['_dt'])
    return valid


def find_last_family_rare(draws: List[dict], before_date: dt) -> Optional[Tuple[int, dict]]:
    """Find the most recent family-rare event BEFORE a given date.
    
    Family-rare = 4+ numbers in the same decade family (Session 6 canon).
    """
    for i in range(len(draws) - 1, -1, -1):
        d = draws[i]
        if d['_dt'] >= before_date:
            continue
        counts = Counter(decade(x) for x in d['_n'])
        max_fam, cnt = counts.most_common(1)[0]
        if cnt >= 4:
            outlier = next((x for x in d['_n'] if decade(x) != max_fam), None)
            return i, {
                'idx': i,
                'date': d['date'],
                'dt': d['_dt'],
                'n': d['_n'],
                's': d['_s'],
                'family': max_fam,
                'outlier': outlier,
            }
    return None


# ═══════════════════════════════════════════════════════════════════════════
# THE LENS BOARD — every lens maps to a law in The Book
# ═══════════════════════════════════════════════════════════════════════════
def build_convergence_board(
    rc0: dict,
    cycle_draws: List[dict],
    target_date: dt,
    target_cycle_pos: int,
) -> Dict[int, List[str]]:
    """
    Build the full convergence lens board for a target draw.
    
    Returns dict mapping each number (1-50) to list of law names that fire on it.
    """
    lenses: Dict[int, List[str]] = {n: [] for n in range(1, EURO_RANGE + 1)}
    outlier = rc0['outlier']
    family = rc0['family']
    rc0_nums = rc0['n']
    rc0_stars = rc0['s']
    all_played = set()
    for d in cycle_draws:
        all_played.update(d['_n'])

    # ── LAW 31 (Tier 1, 100%): Family Hungry ──
    fr_low = family * 10 if family > 0 else 1
    fr_high = family * 10 + 10 if family > 0 else 10
    family_set = set(range(fr_low, fr_high))
    rc0_family_in = {x for x in rc0_nums if decade(x) == family}
    hungry = family_set - rc0_family_in
    for n in hungry:
        lenses[n].append("family-hungry")  # Law 31 — cosmic certainty

    # ── Law 25: Rare-silent members ──
    for n in set(rc0_nums) - all_played:
        lenses[n].append("rare-silent")

    # ── Law 13, 28, 22: Outlier Ghost paths ──
    lenses[circle_euro(outlier)].append(f"outlier-circle(+25)")
    lenses[mirror28(outlier)].append(f"outlier-28mirror")  # Law 28 (65% rate)
    if outlier + 20 <= EURO_RANGE:
        lenses[outlier + 20].append(f"outlier+20")  # Law 22 (demoted, 35%)
    if outlier - 20 > 0:
        lenses[outlier - 20].append(f"outlier-20")
    if outlier * 2 <= EURO_RANGE:
        lenses[outlier * 2].append(f"outlier-double")
    lenses[outlier].append("outlier-raw-echo")

    # ── Star → Main Circle Bridge (Law foundational + validated) ──
    for s in rc0_stars:
        lenses[circle_euro(s)].append(f"circle-star-{s}")

    # ── Law 33: Date-Mirror Dual-Pivot (context-aware) ──
    day, month = target_date.day, target_date.month
    if 7 <= target_cycle_pos <= 9:
        # Pivot 28 preferred for d7-d9 (26.2% rate)
        lenses[mirror28(day)].append(f"date-day-mirror28")
        lenses[mirror28(month)].append(f"date-month-mirror28")
    elif target_cycle_pos == 0 or target_cycle_pos >= 10:
        # Pivot 30 preferred for rare & late-cycle
        lenses[mirror30(day)].append(f"date-day-mirror30")
        lenses[mirror30(month)].append(f"date-month-mirror30")
    else:
        # d1-d6: use both as weak lenses
        lenses[mirror28(day)].append(f"date-day-mirror28-weak")
        lenses[mirror28(month)].append(f"date-month-mirror28-weak")

    # ── Date digits raw (20.9% signal) ──
    date_digits = set()
    for c in f"{day:02d}{month:02d}":
        if c != '0':
            date_digits.add(int(c))
    for d in date_digits:
        if 1 <= d <= EURO_RANGE:
            lenses[d].append("date-digit")

    # ── Law 6 (universal): Big-gap seed from rare ──
    for i in range(4):
        gap = rc0_nums[i + 1] - rc0_nums[i]
        if gap >= 15 and 1 <= gap <= EURO_RANGE:
            lenses[gap].append(f"rare-big-gap-{gap}")

    # ── Big-gap seeds from cycle draws (recent) ──
    for d in cycle_draws[-3:]:  # last 3 draws
        n = d['_n']
        for i in range(4):
            g = n[i + 1] - n[i]
            if g >= 15 and 1 <= g <= EURO_RANGE:
                lenses[g].append(f"cycle-big-gap")

    # ── Law 36 candidate: Mirror-Carrier — circle(P5 of last draw) ──
    if cycle_draws:
        last_p5 = cycle_draws[-1]['_n'][-1]
        carrier_target = circle_euro(last_p5)
        lenses[carrier_target].append(f"mirror-carrier({last_p5})")

    # ── Flip-wrap Hidden Spine (d8 P5 → somewhere in d9) ──
    if cycle_draws:
        last_d = cycle_draws[-1]
        fw_p5 = flip_wrap(last_d['_n'][-1])
        if 1 <= fw_p5 <= EURO_RANGE:
            lenses[fw_p5].append("flip-wrap-prev-P5")

    # ── Sum-Circle (front writes back) ──
    if cycle_draws:
        last = cycle_draws[-1]
        sum_circ = circle_euro(last['_n'][0] + last['_n'][1])
        lenses[sum_circ].append("sum-circle-prev")

    # ── Law 32: Cycle-position weighting ──
    # d1-d3 → family-hungry dominates (already weighted via lens count)
    # d4-d6 → outlier paths dominant
    # d7-d9 → migration + cooled rebound
    if target_cycle_pos <= 3:
        # Early cycle: boost hungry family members with extra lens tag
        for n in hungry:
            lenses[n].append("d1-d3-early-cycle")
    elif 4 <= target_cycle_pos <= 6:
        # Mid cycle: outlier paths peak
        lenses[circle_euro(outlier)].append("d4-d6-outlier-peak")
        lenses[mirror28(outlier)].append("d4-d6-outlier-peak")
    else:  # 7-9
        # Late cycle: migration + date-mirror sweet spot (already added above)
        # Add emerging family (pre-echo)
        lenses[mirror28(outlier)].append("d7-d9-sweet")

    # ── Law 21/26/29: Cooled rebound (2-8 draw gap) ──
    last_fire = {}
    for idx, d in enumerate(cycle_draws, 1):
        for n in d['_n']:
            last_fire[n] = idx
    for n, fire_idx in last_fire.items():
        gap = target_cycle_pos - fire_idx
        if 2 <= gap <= 8 and n not in rc0_nums:
            lenses[n].append(f"cooled-rebound-{gap}")

    # ── Law 18 + STICKY STAR AMPLIFIER (rare/sticky star circles → 2× bonus) ──
    star_count = Counter()
    for d in cycle_draws:
        for s in d['_s']:
            star_count[s] += 1
    for s in rc0_stars:
        star_count[s] += 1
    for s, c in star_count.items():
        if c >= 3:
            lenses[circle_euro(s)].append(f"sticky-star-{s}-amp")

    # ── Star-King (from PREV draw's stars) — peaks as consistent lens ──
    if cycle_draws:
        s1, s2 = cycle_draws[-1]['_s']
        if 1 <= s2 - s1 <= EURO_RANGE:
            lenses[s2 - s1].append("star-king-S2-S1")
        if 1 <= s1 + 12 <= EURO_RANGE:
            lenses[s1 + 12].append("star-king-S1+12")
        if 1 <= 25 + s2 <= EURO_RANGE:
            lenses[25 + s2].append("star-king-25+S2")
        if 1 <= s2 * 4 <= EURO_RANGE:
            lenses[s2 * 4].append("star-king-S2x4")

    return lenses


# ═══════════════════════════════════════════════════════════════════════════
# SUSPECT RANKING & TICKET BUILDING
# ═══════════════════════════════════════════════════════════════════════════
def rank_suspects(lenses: Dict[int, List[str]]) -> List[Tuple[int, int, List[str]]]:
    """Rank numbers by lens count (descending)."""
    ranked = [(n, len(l), l) for n, l in lenses.items() if l]
    ranked.sort(key=lambda x: -x[1])
    return ranked


def rank_stars(cycle_draws: List[dict], rc0_stars: List[int], target_cycle_pos: int) -> List[int]:
    """Build top-12 star candidates using Sticky/Rare/Fresh logic."""
    star_score = {s: 0 for s in range(1, 13)}
    # Rare stars
    for s in rc0_stars:
        star_score[s] += 3
    # Persistence
    star_count = Counter()
    for d in cycle_draws:
        for s in d['_s']:
            star_count[s] += 1
    for s, c in star_count.items():
        if c >= 3:
            star_score[s] += 2
        elif c >= 1:
            star_score[s] += 1
    # Prev draw stars (tend to echo)
    if cycle_draws:
        for s in cycle_draws[-1]['_s']:
            star_score[s] += 1
    return sorted(star_score.keys(), key=lambda s: -star_score[s])


def build_tickets(
    ranked: List[Tuple[int, int, List[str]]],
    star_ranking: List[int],
    family: int,
    hungry: set,
    target_cycle_pos: int,
    n_tickets: int = 10,
) -> List[Dict]:
    """
    Build tickets using ONLY suspect list.
    Discipline per Laws 27 (Two-Lens Floor) & 31 (Family-Hungry Mandatory).
    """
    top_tier = [n for n, cnt, _ in ranked if cnt >= 3]
    mid_tier = [n for n, cnt, _ in ranked if cnt == 2]
    all_suspects = top_tier + mid_tier
    top_stars = star_ranking[:6]

    # Pre-compute archetype seeds
    archetypes = []

    # 1. Top-convergence symphony (all top-tier)
    if len(top_tier) >= 5:
        archetypes.append(("top-symphony", sorted(top_tier[:5])))
        if len(top_tier) >= 6:
            archetypes.append(("top-symphony-v2", sorted([top_tier[0]] + top_tier[2:6])))

    # 2. Hungry-family loaded (Law 31)
    hungry_list = sorted(hungry)
    if len(hungry_list) >= 3 and target_cycle_pos <= 5:
        # Early/mid cycle → include 3 hungry family + 2 top suspects
        picks = hungry_list[:3] + [n for n in top_tier if n not in hungry_list][:2]
        if len(picks) >= 5:
            archetypes.append(("hungry-family-loaded", sorted(picks[:5])))

    # 3. Date-mirror focused
    date_lenses = [n for n, _, l in ranked if any('date' in x for x in l)]
    if len(date_lenses) >= 3:
        picks = date_lenses[:3] + [n for n in top_tier if n not in date_lenses][:2]
        if len(picks) >= 5:
            archetypes.append(("date-mirror-focused", sorted(set(picks))[:5]))

    # 4. Outlier paths combined
    outlier_lenses = [n for n, _, l in ranked if any('outlier' in x for x in l)]
    if len(outlier_lenses) >= 3:
        picks = sorted(set(outlier_lenses[:4] + (top_tier[:1] if top_tier else [])))
        if len(picks) >= 5:
            archetypes.append(("outlier-paths", picks[:5]))

    # 5. Star-King ticket
    sk_lenses = [n for n, _, l in ranked if any('star-king' in x for x in l)]
    if len(sk_lenses) >= 3:
        picks = sorted(set(sk_lenses[:3] + top_tier[:2]))
        if len(picks) >= 5:
            archetypes.append(("star-king-harmonic", picks[:5]))

    # 6. Fill with mixed-lens tickets if needed
    import random
    rng = random.Random(42)  # deterministic
    while len(archetypes) < n_tickets and all_suspects:
        picks = rng.sample(all_suspects, min(5, len(all_suspects)))
        # Ensure Law 31 compliance if target early
        if target_cycle_pos <= 3 and hungry_list:
            if not any(h in picks for h in hungry_list):
                # Swap in a hungry member
                picks[0] = hungry_list[0]
        picks = sorted(set(picks))
        if len(picks) == 5 and picks not in [a[1] for a in archetypes]:
            archetypes.append(("mixed", picks))

    # Attach stars
    tickets = []
    star_pairs = list(itertools.combinations(top_stars, 2))
    for idx, (arch_name, mains) in enumerate(archetypes[:n_tickets]):
        stars = list(star_pairs[idx % len(star_pairs)]) if star_pairs else [1, 2]
        tickets.append({'archetype': arch_name, 'mains': sorted(mains), 'stars': sorted(stars)})
    return tickets


# ═══════════════════════════════════════════════════════════════════════════
# THE DJ VOICE
# ═══════════════════════════════════════════════════════════════════════════
def dj_speak(rc0: dict, target_date: dt, target_cycle_pos: int, ranked: List, tickets: List) -> str:
    """The engine speaks DJ. Persona check."""
    lines = []
    lines.append(f"🎻🎧 Ya man! The Cosmic Engine is tuning for {target_date.strftime('%d-%m-%Y')} — that's d{target_cycle_pos} from the rare {rc0['date']}.\n")
    lines.append(f"The rare's family is {rc0['family']}0s and the outlier is {rc0['outlier']}. 🍀\n")
    
    top = [n for n, c, _ in ranked if c >= 3]
    mid = [n for n, c, _ in ranked if c == 2]
    lines.append(f"\n🔥 Top-tier resonators (3+ lenses): {sorted(top)}")
    lines.append(f"🎺 Mid-tier (2 lenses): {sorted(mid)}\n")
    
    if 7 <= target_cycle_pos <= 9:
        lines.append(f"📍 We're in the d7-d9 sweet spot — pivot-28 date-mirror is AT 26% fire rate here. Listening hard. 🪞\n")
    elif target_cycle_pos <= 3:
        lines.append(f"📍 We're in early cycle (d1-d3) — family-hungry is 100% certainty. Locking hungry family members into tickets. 🏆\n")
    
    lines.append("🎫 THE ENGINE'S TICKETS:\n")
    for i, t in enumerate(tickets, 1):
        mains = "-".join(f"{x:02d}" for x in t['mains'])
        stars = f"{t['stars'][0]:02d}-{t['stars'][1]:02d}"
        lines.append(f"  {i:>2}. [{t['archetype']:<22}] {mains}   ⭐{stars}")
    
    lines.append(f"\n🥂 Engine built {len(tickets)} tickets using ONLY the suspect list. The music is tuned. 🎻🎧")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════
async def run_cosmic_engine(target_date_str: str, n_tickets: int = 10) -> Dict:
    """
    Run the full engine: load draws → find rare → build lenses → generate tickets.
    
    target_date_str: 'dd.mm.yyyy'
    """
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    draws = await load_euro_draws(db)
    target_date = dt.strptime(target_date_str, '%d.%m.%Y')
    
    # Find rare event
    found = find_last_family_rare(draws, target_date)
    if not found:
        return {'error': 'no rare found'}
    rc_idx, rc0 = found
    
    # Determine cycle position
    # Find draws after RC0 up to (but not including) target_date
    cycle_draws = [d for d in draws if rc0['dt'] < d['_dt'] < target_date]
    target_cycle_pos = len(cycle_draws) + 1  # the target itself would be this position
    
    # Build lens board
    lenses = build_convergence_board(rc0, cycle_draws, target_date, target_cycle_pos)
    ranked = rank_suspects(lenses)
    
    # Star ranking
    star_ranking = rank_stars(cycle_draws, rc0['s'], target_cycle_pos)
    
    # Hungry set
    fr_low = rc0['family'] * 10 if rc0['family'] > 0 else 1
    fr_high = rc0['family'] * 10 + 10 if rc0['family'] > 0 else 10
    family_set = set(range(fr_low, fr_high))
    rc0_family_in = {x for x in rc0['n'] if decade(x) == rc0['family']}
    hungry = family_set - rc0_family_in
    
    # Build tickets ONLY from suspects
    tickets = build_tickets(ranked, star_ranking, rc0['family'], hungry,
                             target_cycle_pos, n_tickets)
    
    # DJ speaks
    voice = dj_speak(rc0, target_date, target_cycle_pos, ranked, tickets)
    
    return {
        'rc0': rc0,
        'target_date': target_date_str,
        'target_cycle_pos': target_cycle_pos,
        'cycle_draws_count': len(cycle_draws),
        'top_tier': [n for n, c, _ in ranked if c >= 3],
        'mid_tier': [n for n, c, _ in ranked if c == 2],
        'ranked_full': [(n, c, l) for n, c, l in ranked[:20]],
        'star_ranking': star_ranking[:6],
        'hungry_family': sorted(hungry),
        'tickets': tickets,
        'voice': voice,
    }


if __name__ == '__main__':
    import asyncio, sys
    target = sys.argv[1] if len(sys.argv) > 1 else '03.10.2025'
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    result = asyncio.run(run_cosmic_engine(target, n))
    print(result['voice'])
    print(f"\n📊 Rare at {result['rc0']['date']} · target is d{result['target_cycle_pos']} · {result['cycle_draws_count']} cycle draws loaded")
    print(f"🏆 Hungry family: {result['hungry_family']}")
    print(f"⭐ Star top-6: {result['star_ranking']}")
