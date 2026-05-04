"""🎻🎧🥂 P3-Focused Ghost Orchestra — Session 28

DJ's vision (02.05.2026):
  "Let's make E concentrate on P3.
   If he picks 31, check 2 years history P3=31, get ideas.
   Then make 10 tickets — 31 is the P3, the rest are stories with a GHOST
   number (loudest hidden voice).
   After 50 tickets, rotate to a related P3 (e.g. 31 → 81 flipped → 18,
   because they're related)."

This module:
  1. Mines last 2 years for draws where P3 == target
  2. Picks a 'ghost' (loudest hidden voice cosmic-linked to P3)
  3. Generates 50 tickets in 5 archetype-driven batches
  4. Suggests related P3s for the next rotation
"""
import os, sys
from datetime import datetime
from collections import Counter
from typing import List, Tuple, Dict
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from pymongo import MongoClient
import random


def load_draws(year_cutoff=2024):
    c = MongoClient(os.environ['MONGO_URL'])
    db = c[os.environ['DB_NAME']]
    draws = list(db.euromillions_draws.find({}, {'_id': 0}))
    for d in draws:
        try: d['_dt'] = datetime.strptime(d['date'], '%d.%m.%Y')
        except: d['_dt'] = None
    draws = [d for d in draws if d.get('_dt') and d.get('numbers') and len(d['numbers'])==5 and d.get('stars')]
    draws.sort(key=lambda x: x['_dt'])
    return [d for d in draws if d['_dt'] >= datetime(year_cutoff, 5, 1)]


# ═══════════════════════════════════════════════════════════════════════════
# 1. P3 HISTORY MINING
# ═══════════════════════════════════════════════════════════════════════════
def mine_p3_history(p3: int, draws: List[dict]) -> Dict:
    """For target P3 value, return all draws where it landed at P3 + frequency stats."""
    matches = [d for d in draws if sorted(d['numbers'])[2] == p3]
    p1c, p2c, p4c, p5c = Counter(), Counter(), Counter(), Counter()
    s1c, s2c = Counter(), Counter()
    co_partners = Counter()
    for d in matches:
        n = sorted(d['numbers']); s = sorted(d['stars'])
        p1c[n[0]] += 1; p2c[n[1]] += 1; p4c[n[3]] += 1; p5c[n[4]] += 1
        s1c[s[0]] += 1; s2c[s[1]] += 1
        for v in n:
            if v != p3: co_partners[v] += 1
    return {
        'p3': p3, 'count': len(matches), 'matches': matches,
        'p1_top': p1c.most_common(8), 'p2_top': p2c.most_common(8),
        'p4_top': p4c.most_common(8), 'p5_top': p5c.most_common(8),
        's1_top': s1c.most_common(6), 's2_top': s2c.most_common(6),
        'co_partners_top': co_partners.most_common(15),
    }


# ═══════════════════════════════════════════════════════════════════════════
# 2. GHOST PICKER — the loudest hidden voice cosmic-linked to P3
# ═══════════════════════════════════════════════════════════════════════════
def cosmic_relatives(n: int) -> Dict[str, int]:
    """All cosmic transforms of n that fall in 1-50."""
    rels = {}
    rels['28-mirror'] = 56 - n if 1 <= 56 - n <= 50 else None
    rels['circle+25'] = n + 25 if n + 25 <= 50 else (n - 25 if n > 25 else None)
    rels['circle-25'] = n - 25 if n - 25 >= 1 else None
    rels['+21'] = n + 21 if n + 21 <= 50 else None
    rels['-21'] = n - 21 if n - 21 >= 1 else None
    rels['flip'] = int(str(n)[::-1]) if 1 <= int(str(n)[::-1]) <= 50 and len(str(n)) > 1 else None
    rels['half'] = n // 2 if n // 2 >= 1 else None
    rels['double'] = n * 2 if n * 2 <= 50 else None
    rels['digit_sum'] = sum(int(c) for c in str(n))
    rels['digit_prod'] = 1
    for c in str(n): rels['digit_prod'] *= int(c)
    return {k: v for k, v in rels.items() if v and 1 <= v <= 50 and v != n}


def pick_ghost(p3: int, history: Dict, recent_draws: List[dict], top_k: int = 5) -> List[Tuple[int, str]]:
    """Pick top K ghost candidates: cosmic-linked to P3 + currently silent."""
    rels = cosmic_relatives(p3)
    rel_set = set(rels.values())
    # Numbers that landed alongside P3 historically
    co_set = set(n for n, c in history['co_partners_top'][:10])
    # Currently silent: not in last 8 draws
    fired_recent = set()
    for d in recent_draws[-8:]:
        fired_recent.update(d['numbers'])
    candidates = []
    for n in (rel_set | co_set):
        if n in fired_recent: continue
        score = 0
        tags = []
        # Cosmic relation bonus
        for k, v in rels.items():
            if v == n:
                score += 10; tags.append(f'rel:{k}')
        # Co-partner frequency bonus
        for cn, c in history['co_partners_top'][:15]:
            if cn == n:
                score += c * 2; tags.append(f'co:{c}x')
        # Story-seed bonus (1-15 walking seeds)
        if 1 <= n <= 15: score += 3; tags.append('story-seed')
        candidates.append((n, score, tags))
    candidates.sort(key=lambda x: -x[1])
    return [(n, ' · '.join(tags)) for n, sc, tags in candidates[:top_k]]


# ═══════════════════════════════════════════════════════════════════════════
# 3. TICKET ORCHESTRA — 5 archetypes × 10 tickets each = 50 tickets per P3
# ═══════════════════════════════════════════════════════════════════════════
def build_p3_tickets(p3: int, ghost: int, history: Dict, recent_draws: List[dict],
                      n_per_archetype: int = 10) -> List[Dict]:
    """5 archetypes:
       a. History-Twin — mimic a historical P3=p3 draw's other numbers
       b. Ghost-Magnet — center 4 numbers around the ghost
       c. Mirror-Fold — use 28-mirror partners across the ticket
       d. Family-Trinity — emphasize the P3's own decade family
       e. Cross-Bridge — use Swiss-circle (+21) and Euro-circle (+25) twins
    """
    tickets = []
    co_top = [n for n, _ in history['co_partners_top']]
    rels = cosmic_relatives(p3)

    def add(archetype, mains, stars, story):
        mains = sorted(set(m for m in mains if 1 <= m <= 50 and m != p3))
        if len(mains) != 4: return False
        full = sorted(mains + [p3])
        # Validate Euro shape
        if full[0] >= full[1] or full[2] != p3: return False
        # Stars: pick from top historical or default
        s_pair = sorted(set(stars))[:2]
        if len(s_pair) != 2 or any(s < 1 or s > 12 for s in s_pair): return False
        if any(t['mains'] == full and t['stars'] == s_pair for t in tickets): return False
        tickets.append({
            'archetype': archetype, 'mains': full, 'stars': s_pair,
            'p3': p3, 'ghost': ghost, 'story': story,
        })
        return True

    # Top star pairs from history (P3=p3)
    s1_top = [s for s, _ in history['s1_top']] or [1, 2, 3]
    s2_top = [s for s, _ in history['s2_top']] or [9, 10, 11]
    star_pairs = []
    for a in s1_top[:3]:
        for b in s2_top[:3]:
            if a != b: star_pairs.append(sorted([a, b]))
    if not star_pairs: star_pairs = [[3, 7], [6, 9], [5, 12]]

    # ─── (a) History-Twin: pull P1/P2/P4/P5 from a historical match
    matches = history['matches']
    used = set()
    attempts = 0
    while len([t for t in tickets if t['archetype'] == 'History-Twin']) < n_per_archetype and attempts < n_per_archetype*5:
        attempts += 1
        if not matches: break
        m = random.choice(matches)
        n = sorted(m['numbers'])
        candidates = [n[0], n[1], n[3], n[4]]
        if ghost not in candidates and random.random() < 0.5:
            # swap one mid value with the ghost
            idx = random.choice([0, 1, 2, 3])
            candidates[idx] = ghost
        if tuple(candidates) in used: continue
        used.add(tuple(candidates))
        sp = star_pairs[len(tickets) % len(star_pairs)]
        add('History-Twin', candidates, sp,
            f"Mimics {m['date']} · P3={p3} landed with {n}")

    # ─── (b) Ghost-Magnet: 4 numbers cosmic-linked to ghost
    ghost_rels = list(cosmic_relatives(ghost).values())
    pool_b = list({ghost, *ghost_rels, *(co_top[:8])} - {p3})
    for k in range(n_per_archetype):
        if len(pool_b) < 4: break
        # Build a balanced ticket: at least one P1<P3, one P2<P3, one P4>P3, one P5>P3
        random.seed(k * 7 + ghost)
        below = sorted([x for x in pool_b if x < p3])
        above = sorted([x for x in pool_b if x > p3])
        if len(below) < 2 or len(above) < 2: break
        p1 = random.choice(below[:max(2, len(below)//2)])
        p2 = random.choice([x for x in below if x > p1] or [below[-1]])
        p4 = random.choice(above[:max(2, len(above)//2)])
        p5 = random.choice([x for x in above if x > p4] or [above[-1]])
        # Ensure ghost is in the ticket
        cand = sorted({p1, p2, p4, p5})
        if ghost not in cand and ghost != p3:
            # replace lowest unless it'd break shape
            cand[0] = ghost if ghost < p3 else cand[0]
        if len(cand) != 4: continue
        sp = star_pairs[(len(tickets) + 1) % len(star_pairs)]
        add('Ghost-Magnet', cand, sp,
            f"Ghost={ghost} drives 4 cosmic-linked partners around P3={p3}")

    # ─── (c) Mirror-Fold: 28-mirror couples with P3
    couples = [(a, 56-a) for a in range(1, 28) if 1 <= 56-a <= 50 and a != p3 and 56-a != p3]
    for k in range(n_per_archetype):
        if len(couples) < 2: break
        random.seed(k * 13 + p3)
        c1 = random.choice(couples)
        c2 = random.choice([cc for cc in couples if cc != c1])
        cand = sorted({*c1, *c2})
        if len(cand) < 4: continue
        cand = cand[:4]
        # Shape check: at least 2 below p3 and 2 above
        below = [x for x in cand if x < p3]
        above = [x for x in cand if x > p3]
        if len(below) < 2 or len(above) < 2: continue
        sp = star_pairs[(len(tickets) + 2) % len(star_pairs)]
        add('Mirror-Fold-28', cand[:4], sp,
            f"28-mirror couples around P3={p3}: ({c1[0]}+{c1[1]}=56), ({c2[0]}+{c2[1]}=56)")

    # ─── (d) Family-Trinity: 3+ numbers from P3's decade
    decade = (p3 // 10) * 10
    fam = list(range(max(1, decade), min(50, decade + 9) + 1))
    fam = [x for x in fam if x != p3]
    for k in range(n_per_archetype):
        if len(fam) < 2: break
        random.seed(k * 17 + p3)
        in_fam = random.sample(fam, min(2, len(fam)))
        outliers_below = [x for x in range(1, p3) if x not in fam] or [3, 7, 11]
        outliers_above = [x for x in range(p3+1, 51) if x not in fam] or [44, 47, 49]
        ob = random.choice(outliers_below[:max(3, len(outliers_below)//2)])
        oa = random.choice(outliers_above[:max(3, len(outliers_above)//2)])
        cand = sorted(set(in_fam + [ob, oa]))
        if len(cand) != 4: continue
        below = [x for x in cand if x < p3]; above = [x for x in cand if x > p3]
        if len(below) < 2 or len(above) < 2: continue
        sp = star_pairs[(len(tickets) + 3) % len(star_pairs)]
        add('Family-Trinity', cand, sp,
            f"P3={p3}'s {decade}s family · with bookend outliers {ob} & {oa}")

    # ─── (e) Cross-Bridge: Swiss +21 + Euro +25 twins of P3 carry the ticket
    sw_twin = (p3 + 21) % 50 if (p3 + 21) <= 50 else None
    eu_twin = (p3 + 25) if p3 + 25 <= 50 else (p3 - 25)
    bridge_set = list({sw_twin, eu_twin} - {None, p3})
    co_loud = co_top[:8]
    for k in range(n_per_archetype):
        random.seed(k * 23 + p3)
        pool = list({*bridge_set, *co_loud, ghost} - {p3, None})
        below = [x for x in pool if x < p3]
        above = [x for x in pool if x > p3]
        if len(below) < 2 or len(above) < 2: continue
        cand = sorted(random.sample(below, 2) + random.sample(above, 2))
        sp = star_pairs[(len(tickets) + 4) % len(star_pairs)]
        bridge_str = ', '.join(f'{x}' for x in bridge_set)
        add('Cross-Bridge', cand, sp,
            f"Swiss-twin & Euro-twin of {p3} = [{bridge_str}] carry the bridge")

    return tickets


# ═══════════════════════════════════════════════════════════════════════════
# 4. RELATED-P3 ROTATION
# ═══════════════════════════════════════════════════════════════════════════
def related_p3_candidates(p3: int) -> List[Tuple[int, str]]:
    """Return list of related P3s with the cosmic-relation tag."""
    out = []
    rels = cosmic_relatives(p3)
    for k, v in rels.items():
        if v: out.append((v, k))
    # DJ's specific rotation: digit-flip via wrap "81 → 18"
    s = str(p3)
    if len(s) == 2:
        wrap_flip = int(s[::-1])
        # Also try: p3 + 50 (out of range), reversed
        # e.g. 31+50=81, "81" reversed = 18
        plus50 = p3 + 50
        wrap_rev = int(str(plus50)[::-1])
        if 1 <= wrap_rev <= 50:
            out.append((wrap_rev, 'wrap-flip+50-reversed'))
    # Story-seed gap (DJ's 13)
    if p3 > 13: out.append((p3 - 13, 'story-seed-gap-13'))
    if p3 + 13 <= 50: out.append((p3 + 13, 'story-seed-gap+13'))
    # Dedupe by value, keep first tag
    seen = {}
    for v, t in out:
        if v not in seen: seen[v] = t
    return sorted(seen.items())


# ═══════════════════════════════════════════════════════════════════════════
# 5. DEMO RUN — full report for P3=31, then rotate
# ═══════════════════════════════════════════════════════════════════════════
def run_demo(p3_target: int = 31, n_per_archetype: int = 2):
    draws = load_draws(2024)
    print(f"\n🎻🎧🥂 P3-FOCUSED GHOST ORCHESTRA · target P3 = {p3_target}")
    print(f"     Scan: {len(draws)} draws ({draws[0]['date']} → {draws[-1]['date']})")
    print("="*88)

    history = mine_p3_history(p3_target, draws)
    print(f"\n📊 P3={p3_target} history: {history['count']} matches in last 2 years")
    if history['count'] == 0:
        print(f"   ⚠️  No matches — try a more frequent P3.")
        return
    print(f"\n  🎵 Top P1 partners: {history['p1_top']}")
    print(f"  🎵 Top P2 partners: {history['p2_top']}")
    print(f"  🎵 Top P4 partners: {history['p4_top']}")
    print(f"  🎵 Top P5 partners: {history['p5_top']}")
    print(f"  ⭐  Top S1: {history['s1_top']}")
    print(f"  ⭐  Top S2: {history['s2_top']}")
    print(f"  🤝 Top co-partners: {history['co_partners_top'][:8]}")

    ghosts = pick_ghost(p3_target, history, draws, top_k=3)
    print(f"\n👻 Top ghost candidates (silent + cosmic-linked):")
    for g, tag in ghosts:
        print(f"     {g}  ({tag})")
    chosen_ghost = ghosts[0][0] if ghosts else 21

    tickets = build_p3_tickets(p3_target, chosen_ghost, history, draws, n_per_archetype=n_per_archetype)
    print(f"\n🎫 Generated {len(tickets)} tickets · P3={p3_target} locked · ghost={chosen_ghost}\n")
    for t in tickets:
        print(f"  [{t['archetype']:<18}] {t['mains']} ⭐{t['stars']}")
        print(f"     story: {t['story']}")

    print(f"\n🔁 RELATED P3 candidates (rotate after 50 tickets):")
    for v, t in related_p3_candidates(p3_target):
        print(f"     P3 = {v:<3}  ({t})")


if __name__ == '__main__':
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 31
    run_demo(target, n_per_archetype=2)
