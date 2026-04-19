"""
🚨🎻 CYCLE-CLOSE SIMULATOR for Q2d5 = 21.04.2026
══════════════════════════════════════════════════════════════════════════
Forced-seeds derived from Session-3 esoteric rules:
  • RARE-EVENT hungry (24-03 seed):   17, 18   + ⭐1, ⭐3
  • +10 KEY translation (Q1d5 → Q2d5): 10, 15, 27, 34, 39
  • STAR TRIBUTE hungry (Q1 ⭐ un-tributed): ⭐10, ⭐12
  • +3 BOOKEND (P1/P5 twin gap): 5+3=8 at P1, 50+3=3 at P5 (Euro wrap)
  
Generate 12 candidate tickets scored by:
  1. date_resonance (Session-3 Euro neighborhood)
  2. rare_event_echo (Session-3 cycle)
  3. cycle_close_lock (NEW — +10 key + forced seed)
"""
import sys
sys.path.insert(0, '/app/backend')
from euro_date_tuning import score_euro_date_resonance
from rare_event_scorer import score_rare_event_echo
import random

TARGET_DATE = "21.04.2026"

# Forced seed pools
TRIPLE_LOCK   = {17, 18}                  # Rare + seed + Q1d2 seed = MUST-HAVE candidates
PLUS10_KEY    = {10, 15, 27, 34, 39}       # +10 translation from Q1d5
STAR_HUNGRY   = {10, 12}                   # Q1 ⭐ un-tributed
STAR_RARE     = {1, 3}                     # rare-event ⭐ un-tributed
BOOKEND_FRONT = {8}                        # +3 gap from Q1d5 P1=5
BOOKEND_BACK  = {3, 44, 45, 46, 47}        # +3 bookend back-row candidates

# Recent Euro draws (for rare-event scorer context — newest first)
RECENT = [
    {"date": "17.04.2026", "numbers": [22,23,28,41,47], "stars": [6,8]},
    {"date": "14.04.2026", "numbers": [1,2,4,28,44],    "stars": [5,12]},
    {"date": "10.04.2026", "numbers": [10,13,14,38,41], "stars": [6,9]},
    {"date": "07.04.2026", "numbers": [11,14,19,36,49], "stars": [6,7]},
    {"date": "03.04.2026", "numbers": [8,27,29,46,49],  "stars": [2,10]},
    {"date": "31.03.2026", "numbers": [5,8,10,33,38],   "stars": [2,7]},
    {"date": "27.03.2026", "numbers": [4,10,43,44,48],  "stars": [2,4]},
    {"date": "24.03.2026", "numbers": [12,16,17,18,27], "stars": [1,3]},
]

def cycle_close_score(nums, stars):
    """Score a ticket against the cycle-close forced seeds."""
    s = 0
    signals = []
    ns = set(nums); ss = set(stars)
    
    # Triple-lock mains — massive bonus
    held_tl = ns & TRIPLE_LOCK
    if held_tl:
        s += 30 * len(held_tl)
        signals.append(f"triple-lock {sorted(held_tl)} (+{30*len(held_tl)})")
    
    # +10 key translations
    held_p10 = ns & PLUS10_KEY
    if held_p10:
        s += 15 * len(held_p10)
        signals.append(f"+10-key {sorted(held_p10)} (+{15*len(held_p10)})")
    
    # Star tribute
    held_st = ss & STAR_HUNGRY
    if held_st:
        s += 20 * len(held_st)
        signals.append(f"⭐ tribute {sorted(held_st)} (+{20*len(held_st)})")
    
    # Rare-event stars
    held_sr = ss & STAR_RARE
    if held_sr:
        s += 15 * len(held_sr)
        signals.append(f"⭐ rare-hungry {sorted(held_sr)} (+{15*len(held_sr)})")
    
    # Bookend +3 (front: 8, back: 44-47 ~ in vicinity)
    if 8 in ns:
        s += 10
        signals.append("bookend-front 8 (+10)")
    if any(x in ns for x in [44, 45, 46, 47]):
        bk = ns & {44,45,46,47}
        s += 8
        signals.append(f"bookend-back {sorted(bk)} (+8)")
    
    return s, signals


def make_ticket(force_mains, force_stars):
    """Construct a Euro ticket around forced seeds."""
    mains = set(force_mains)
    stars = set(force_stars)
    # fill mains to 5, stars to 2
    while len(mains) < 5:
        n = random.randint(1, 50)
        mains.add(n)
    while len(stars) < 2:
        st = random.randint(1, 12)
        stars.add(st)
    return sorted(list(mains)[:5]), sorted(list(stars)[:2])


def simulate(n_tickets=12, seed=42):
    random.seed(seed)
    tickets = []
    
    # Ticket 1 — max-lock (17, 18 + 2 from +10 key + bookend)
    m1, s1 = make_ticket([17, 18, 15, 39], [10, 3])
    tickets.append(("MAX-LOCK 1", m1, s1))
    
    # Ticket 2 — +10 key heavy
    m2, s2 = make_ticket([10, 15, 27, 34, 39], [12, 1])
    tickets.append(("+10-KEY", m2, s2))
    
    # Ticket 3 — triple-lock + bookend
    m3, s3 = make_ticket([8, 17, 18, 47], [10, 12])
    tickets.append(("TRIPLE+BOOK", m3, s3))
    
    # Ticket 4 — rare-echo stars + 17
    m4, s4 = make_ticket([17, 27, 41], [1, 3])
    tickets.append(("STAR-RARE", m4, s4))
    
    # Ticket 5 — 18 + 10 + 44 palindrome axis
    m5, s5 = make_ticket([18, 10, 44, 41], [10, 5])
    tickets.append(("PALINDROME", m5, s5))
    
    # Ticket 6-12 — weighted randoms leaning on pool
    weighted_pool = list(TRIPLE_LOCK) * 4 + list(PLUS10_KEY) * 3 + list(BOOKEND_BACK) * 2
    for i in range(7):
        core = set()
        while len(core) < 3:
            core.add(random.choice(weighted_pool))
        stars_core = set()
        while len(stars_core) < 2:
            stars_core.add(random.choice(list(STAR_HUNGRY | STAR_RARE | {5, 6})))
        m, s = make_ticket(list(core), list(stars_core))
        tickets.append((f"WEIGHTED-{i+1}", m, s))
    
    return tickets


def main():
    print(f"🎻🔥 CYCLE-CLOSE SIMULATION — target: {TARGET_DATE}")
    print(f"    Triple-lock: {sorted(TRIPLE_LOCK)}  +10-key: {sorted(PLUS10_KEY)}")
    print(f"    Star-hungry: {sorted(STAR_HUNGRY)} Star-rare: {sorted(STAR_RARE)}")
    print("=" * 80)
    
    tickets = simulate(12)
    ranked = []
    for label, nums, stars in tickets:
        # 3 scorers
        dr = score_euro_date_resonance(nums, stars, TARGET_DATE)
        rr = score_rare_event_echo(nums, stars, RECENT, mode="euro")
        cc, cc_sig = cycle_close_score(nums, stars)
        total = dr["score"] + rr["score"] + cc
        ranked.append({
            "label": label, "nums": nums, "stars": stars,
            "total": total, "date": dr["score"], "rare": rr["score"], "cycle": cc,
            "dr_badge": dr["badge"], "rare_held": rr["unreleased_held"],
            "cc_signals": cc_sig,
        })
    
    ranked.sort(key=lambda x: -x["total"])
    
    for i, t in enumerate(ranked):
        marker = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f" {i+1}"
        print(f"\n{marker} [{t['label']:<14}] {t['nums']} ⭐{t['stars']}  TOTAL: {t['total']}")
        print(f"       date-res: {t['date']:>+4} ({t['dr_badge']})   rare-echo: {t['rare']:>+4}   cycle-close: {t['cycle']:>+4}")
        if t['cc_signals']:
            print(f"       signals: {' | '.join(t['cc_signals'])}")
        if t['rare_held']['mains'] or t['rare_held']['stars']:
            print(f"       rare-held: mains {t['rare_held']['mains']} stars {t['rare_held']['stars']}")
    
    print("\n" + "=" * 80)
    print(f"🎻 Total tickets simulated: {len(ranked)}")
    print(f"🚨 FULL-ECHO or harmonic tier: {sum(1 for t in ranked if t['total']>=80)}")
    best = ranked[0]
    print(f"\n🥇 WINNER: {best['nums']} ⭐{best['stars']}  ({best['total']} pts)")

if __name__ == "__main__":
    main()
