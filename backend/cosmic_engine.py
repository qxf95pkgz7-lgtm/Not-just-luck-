"""
🎻 COSMIC ENGINE 🎧 — The DJ's Apprentice (Production Build)
=============================================================
Built from The Book (swiss_music_notes.md). 34+ canonized laws fire natively.

Output: tablet, hunger scan, suspect board (lens-counted), star ranking,
        narrative ticket orchestra (30 archetypes max), DJ voice.

Every lens below traces to a specific law in /app/memory/swiss_music_notes.md.
"""
import itertools
import os
from collections import Counter
from datetime import datetime as dt
from typing import Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorClient


# ═══════════════════════════════════════════════════════════════════════════
# COSMIC PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════
EURO_RANGE = 50
SWISS_RANGE = 42
EURO_CIRCLE = 25          # Foundational — Euro +25 mod 50
SWISS_CIRCLE = 21         # Foundational — Swiss +21 mod 42
PIVOT_28 = 28             # Law 33 — date-mirror pivot (d7-d9 sweet)
PIVOT_30 = 30             # Law 33 — date-mirror pivot (rare & late-cycle)

BANNED_DEFAULT: List[int] = []  # DJ can override via kwarg


def circle_euro(n: int) -> int:
    return ((n + EURO_CIRCLE - 1) % EURO_RANGE) + 1


def mirror28(n: int) -> int:
    r = (PIVOT_28 - n) % EURO_RANGE
    return r if r else EURO_RANGE


def mirror30(n: int) -> int:
    r = (PIVOT_30 - n) % EURO_RANGE
    return r if r else EURO_RANGE


def flip_wrap(n: int) -> int:
    s = str(n).zfill(2)
    f = int(s[::-1])
    return f if f <= EURO_RANGE else f - EURO_RANGE


def decade(n: int) -> int:
    return 0 if n < 10 else n // 10


def star_king_13(s1: int, s2: int) -> List[Tuple[int, str]]:
    """The 13 Star-King formulas from The Book Session 4."""
    out = []
    def add(v, nm):
        if 1 <= v <= EURO_RANGE:
            out.append((v, nm))
    add(s2 - s1,      "SK: S2-S1 (P1 8.2%)")
    add(25 + s2,      "SK: 25+S2 (P4 4.3%)")
    add(s1 + 12,      "SK: S1+12 (P2 4.3%)")
    add(s1 + s2,      "SK: S1+S2 (3.8%)")
    add(s1 * 3,       "SK: S1x3 (4.0%)")
    add(2*s1 + s2,    "SK: 2S1+S2 (4.0%)")
    add(25 + s1,      "SK: 25+S1 (P3 3.7%)")
    add(s1 + 21,      "SK: S1+21 (P3 3.5%)")
    add(s1 * 4,       "SK: S1x4 (3.2%)")
    add(50 - s1 - s2, "SK: 50-S1-S2 (P5 3.2%)")
    add(s2 * 4,       "SK: S2x4 (P5 3.3%)")
    add(s2 + 21,      "SK: S2+21 (3.3%)")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# DATA ACCESS
# ═══════════════════════════════════════════════════════════════════════════
async def load_euro_draws(db) -> List[dict]:
    raw = await db.euromillions_draws.find({}, {"_id": 0}).to_list(length=5000)
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


def compute_slot_history_rates(all_draws: List[dict]) -> Dict[int, Dict[int, float]]:
    """Returns {slot(1-5): {n: percentage-rate-at-this-slot}}."""
    total = len(all_draws)
    if total == 0:
        return {i: {} for i in range(1, 6)}
    counts: Dict[int, Counter] = {i: Counter() for i in range(1, 6)}
    for d in all_draws:
        for i, v in enumerate(sorted(d['_n'])):
            if i < 5:
                counts[i+1][v] += 1
    return {
        slot: {n: 100.0 * c / total for n, c in cnt.items()}
        for slot, cnt in counts.items()
    }


def find_last_family_rare(draws: List[dict], before_date: dt) -> Optional[Tuple[int, dict]]:
    """Family-rare = 4+ numbers in same decade family (Session 6 canon)."""
    for i in range(len(draws) - 1, -1, -1):
        d = draws[i]
        if d['_dt'] >= before_date:
            continue
        counts = Counter(decade(x) for x in d['_n'])
        max_fam, cnt = counts.most_common(1)[0]
        if cnt >= 4:
            outlier = next((x for x in d['_n'] if decade(x) != max_fam), None)
            return i, {
                'idx': i, 'date': d['date'], 'dt': d['_dt'],
                'n': d['_n'], 's': d['_s'],
                'family': max_fam, 'outlier': outlier,
            }
    return None


# ═══════════════════════════════════════════════════════════════════════════
# THE LENS BOARD — every lens maps to a law in The Book
# ═══════════════════════════════════════════════════════════════════════════
def build_convergence_board(
    rc0: dict,
    cycle: List[dict],
    target_date: dt,
    target_d: int,
    banned: List[int],
) -> Dict[int, List[str]]:
    """Run every law against every number 1-50. Returns {n: [law tags]}."""
    lenses: Dict[int, List[str]] = {n: [] for n in range(1, EURO_RANGE + 1)}
    outlier = rc0['outlier']; family = rc0['family']
    rc0_nums = rc0['n']; rc0_stars = rc0['s']

    # Track played
    played = Counter(); last_fire: Dict[int, int] = {}
    for i, d in enumerate(cycle, 1):
        for n in d['_n']:
            played[n] += 1; last_fire[n] = i

    def L(n: int, tag: str):
        if 1 <= n <= EURO_RANGE and n not in banned:
            lenses[n].append(tag)

    # ── Law 31 — FAMILY HUNGRY (100% cycle rate, peak d1) ──
    fr_lo = family*10 if family > 0 else 1
    fr_hi = family*10 + 10 if family > 0 else 10
    fam_set = set(range(fr_lo, fr_hi))
    rc0_in_fam = {x for x in rc0_nums if decade(x) == family}
    hungry_fam = fam_set - rc0_in_fam
    for n in hungry_fam:
        if played.get(n, 0) == 0:
            L(n, f"HUNGRY-{family}0s-UNFIRED(Law31)")
        else:
            L(n, f"hungry-{family}0s-fired-d{last_fire[n]}")

    # ── Law 25 — RC0 rare-silent ──
    for n in rc0_nums:
        if n not in played:
            L(n, f"RC0-rare-silent({n})-Law25")

    # ── Law 12 — EXACT-POSITION REPEAT from RC0 (cycle-close sweet) ──
    if target_d >= 7:
        for pos, n in enumerate(rc0_nums, 1):
            if n not in played:
                L(n, f"RC0-P{pos}-exact-pos-repeat(Law12)")

    # ── Law 13 — OUTLIER GHOST paths ──
    ghost_count = sum(1 for d in cycle if outlier in d['_n'])
    ghost_active = ghost_count < 4  # Law 24 saturation cap
    if ghost_active:
        L(outlier, f"outlier-{outlier}-raw-echo(Law13)")
    L(circle_euro(outlier), f"outlier-circle+25(73.9%-Tier1)")
    L(mirror28(outlier), f"outlier-28mirror(Law28-65.2%-Tier1)")

    # Law 17 — Outlier double twin
    if outlier*2 <= EURO_RANGE:
        L(outlier*2, f"outlier-DOUBLE(Law17)")
    elif outlier*2 - EURO_RANGE > 0:
        L(outlier*2 - EURO_RANGE, f"outlier-DOUBLE-wrap")

    # Law 22 — Mirror-20 (once per cycle, Law 23)
    if outlier+20 <= EURO_RANGE:
        if (outlier+20) in played:
            L(outlier+20, f"outlier+20-EXHAUSTED(Law23)")
        else:
            L(outlier+20, f"outlier+20(Law22-Tier2)")
    if outlier-20 > 0:
        if (outlier-20) not in played:
            L(outlier-20, f"outlier-20-UNFIRED(Law22)")
        else:
            L(outlier-20, f"outlier-20-fired-d{last_fire[outlier-20]}")

    # ── Foundational Star→Main Circle Bridge ──
    for s in rc0_stars:
        L(circle_euro(s), f"RC0-⭐{s}-circle={circle_euro(s)}")

    # ── Session 4 — 13 STAR KING formulas from d(last) stars ──
    if cycle:
        s1, s2 = cycle[-1]['_s']
        for v, name in star_king_13(s1, s2):
            L(v, f"[d{len(cycle)} ⭐{s1},{s2}] {name}={v}")
        # Prev-star forward echo ±3 (44.7% → next P1)
        for s in cycle[-1]['_s']:
            for delta in range(-3, 4):
                v = s + delta
                if 1 <= v <= EURO_RANGE:
                    L(v, f"prev-star-{s}±{delta}")

    # ── Law 18 — STICKY STAR AMPLIFIER (circle of sticky star) ──
    star_cnt = Counter()
    for d in cycle:
        for s in d['_s']: star_cnt[s] += 1
    for s in rc0_stars: star_cnt[s] += 1
    for s, c in star_cnt.items():
        if c >= 3:
            L(circle_euro(s), f"sticky-⭐{s}×{c}-circle-AMP(Law18)")

    # ── Law 30 — STICKY STAR LONG-COOLED (early d1-d3 then silent → d7-d9 fire) ──
    early = Counter(); mid = Counter()
    for i, d in enumerate(cycle, 1):
        for s in d['_s']:
            if i <= 3: early[s] += 1
            elif 4 <= i <= 6: mid[s] += 1
    for s, c in early.items():
        if c >= 2 and mid.get(s, 0) == 0 and target_d >= 7:
            L(s, f"sticky-star-long-cooled-⭐{s}(Law30)")
            L(circle_euro(s), f"sticky-long-cooled-circle({s})")

    # ── Law 33 — DATE-MIRROR DUAL-PIVOT ──
    day, month = target_date.day, target_date.month
    if 7 <= target_d <= 9:
        L(mirror28(day), f"DATE-day{day}→mirror28={mirror28(day)}[d7-d9-26%sweet]")
        L(mirror28(month), f"DATE-mo{month}→mirror28={mirror28(month)}")
    elif target_d == 0 or target_d >= 10:
        L(mirror30(day), f"DATE-day{day}→mirror30={mirror30(day)}[pivot30-sweet]")
        L(mirror30(month), f"DATE-mo{month}→mirror30={mirror30(month)}")
    else:
        L(mirror28(day), f"date-day-mirror28(weak)")
        L(mirror28(month), f"date-mo-mirror28(weak)")
    # Pivot-30 always as secondary
    L(mirror30(day), f"date-day-mirror30={mirror30(day)}")
    L(mirror30(month), f"date-mo-mirror30={mirror30(month)}")

    # ── Law 11 — Date permutations (2-digit recombinations of DD.MM digits) ──
    dstr = f"{day:02d}{month:02d}"
    perms_seen = set()
    for a, b in itertools.permutations(dstr, 2):
        v = int(a + b)
        if 1 <= v <= EURO_RANGE and v not in perms_seen:
            perms_seen.add(v)
            L(v, f"date-perm({a}{b})")
    # Raw date digits (Session 3)
    for c in dstr:
        d_int = int(c)
        if 1 <= d_int <= EURO_RANGE:
            L(d_int, f"date-digit-{d_int}")

    # ── Silence Agent — circle(month) ──
    L(circle_euro(month), f"silence-agent=circle(mo{month})={circle_euro(month)}")

    # ── Law 8 — FLIP-WRAP back-door (from last draw) ──
    if cycle:
        for n in cycle[-1]['_n']:
            fw = flip_wrap(n)
            if fw != n:
                L(fw, f"flipwrap({n})={fw}(Law8)")

    # ── Law 9 — SUM-CIRCLE (front writes back) ──
    if cycle:
        last = cycle[-1]
        sc = circle_euro(last['_n'][0] + last['_n'][1])
        L(sc, f"sum-circle(P1+P2 d{len(cycle)})={sc}(Law9)")

    # ── Self-Circle +21 (Session 4, Euro-internal) ──
    if cycle:
        for n in cycle[-1]['_n']:
            v = ((n-1+21) % EURO_RANGE) + 1
            if v != n:
                L(v, f"self-circle+21({n})={v}")

    # ── Laws 21/26/29 — COOLED REBOUND (2-8 gap, widened for hungry) ──
    for n, fire in last_fire.items():
        gap = target_d - fire
        if n in hungry_fam or n == outlier:
            if 2 <= gap <= 8:
                L(n, f"cooled-rebound-{gap}d(hungry-Law29)")
        elif 4 <= gap <= 8:
            L(n, f"cooled-rebound-{gap}d(Law26)")

    # ── Law 6 + Law 19 — BIG-GAP SEED (raw or circle release) ──
    for d in cycle[-3:]:
        n = d['_n']
        for i in range(4):
            g = n[i+1] - n[i]
            if g >= 15 and 1 <= g <= EURO_RANGE:
                L(g, f"big-gap-seed({n[i]}→{n[i+1]}=gap{g})")
                L(circle_euro(g), f"big-gap-circle-release(Law19)")
    # RC0 gaps
    for i in range(4):
        g = rc0_nums[i+1] - rc0_nums[i]
        if g >= 15:
            L(g, f"RC0-big-gap={g}")

    # ── Session 4 — LADDER-FILL (last draw's front trio digits) ──
    if cycle:
        last = cycle[-1]
        digs = []
        for x in last['_n'][:3]:
            for c in f"{x:02d}":
                if c != '0': digs.append(int(c))
        for a, b in itertools.permutations(digs, 2):
            v = int(f"{a}{b}")
            if 1 <= v <= EURO_RANGE:
                L(v, f"ladder-fill-digit({a}{b})")

    # ── Session 4 — P1 RUNNING SUM ──
    p1s = [d['_n'][0] for d in cycle]
    for win in [2, 3, 4]:
        if len(p1s) >= win:
            s = sum(p1s[-win:])
            L(s, f"P1-running-sum({win})={s}")

    # ── Law 18 / Law 37 — MIRROR-SPLIT 28-COUPLE silent-pair ──
    silent_all = {n for n in range(1, EURO_RANGE+1) if n not in played and n not in rc0_nums}
    silent_with_rc0 = {n for n in range(1, EURO_RANGE+1) if n not in played}
    for a in range(1, 14):
        b = 28 - a
        if b > 0 and a in silent_with_rc0 and b in silent_with_rc0:
            tag = "silent-28-couple-pair-magic(Law37-cand)"
            if a in rc0_nums and a not in played:
                tag += "-RC0"
            L(a, tag); L(b, tag.replace("RC0", ""))

    # ── Law 5 — P1 SNAP-BACK (if last P1 > 20) ──
    if cycle and cycle[-1]['_n'][0] > 20:
        for n in range(1, 8):
            L(n, f"snap-back-sweet(Law5 50%)")
        for n in range(8, 13):
            L(n, f"snap-back-band(Law5 65.6%)")

    # ── Delta math — DJ's teaching: last P1 − target_d (cycle-position) ──
    if cycle:
        delta = cycle[-1]['_n'][0] - target_d
        if 1 <= delta <= EURO_RANGE:
            L(delta, f"DJ-delta: d{len(cycle)}-P1({cycle[-1]['_n'][0]})−target_d({target_d})={delta}")

    # ── Law 52 — DUAL-CLOCK RESONANCE (anchor-window d-digit fires) ──
    # E was only listening on the RC0 clock. The DJ teaches a parallel
    # Session 19/20 anchor-window clock (last 5 draws + target = d6).
    # When the anchor-d digit matches a main, amplify.
    if cycle:
        window_len = min(5, len(cycle))
        anchor_d = window_len + 1  # target is one beyond the window anchor
        # Raw d-digit family: d, d+10, d+20, d+30, d+40 (date-grammar)
        for k in range(0, 5):
            v = anchor_d + 10*k
            if 1 <= v <= EURO_RANGE:
                L(v, f"Law52:anchor-d{anchor_d}-tens({v})")
        # Mirror28 & ceiling shadows of the anchor-d
        mir = 28 - anchor_d
        if 1 <= mir <= EURO_RANGE:
            L(mir, f"Law52:anchor-d{anchor_d}-mirror28({mir})")
        if 50 - anchor_d >= 1:
            L(50 - anchor_d, f"Law52:anchor-d{anchor_d}-ceiling({50-anchor_d})")
        # Δ of last P1 ± anchor_d (the "run" math from Swiss→Euro shift)
        last_p1 = cycle[-1]['_n'][0]
        for sign in (+1, -1):
            v = last_p1 + sign*anchor_d
            if 1 <= v <= EURO_RANGE:
                sym = '+' if sign>0 else '-'
                L(v, f"Law52:P1-Δ-d{anchor_d}(last-P1={last_p1}{sym}d)={v}")
        # Anchor-P1 ± anchor_d (cycle-close mirror from Session 20)
        anchor_p1 = cycle[-window_len]['_n'][0]
        for sign in (+1, -1):
            v = anchor_p1 + sign*anchor_d
            if 1 <= v <= EURO_RANGE:
                sym = '+' if sign>0 else '-'
                L(v, f"Law52:P1-anchor-cycle-close(anchor-P1={anchor_p1}{sym}d)={v}")
        # Boost the raw d-digit itself with multiple echoes (DJ's "must be suspicious")
        if 1 <= anchor_d <= EURO_RANGE:
            L(anchor_d, f"Law52:d{anchor_d}-raw-cycle-position-P1")
            L(anchor_d, f"Law52:d{anchor_d}-year-root-echo")
            # anchor_d flip shadow (6→60 wrap=10, 7→70 wrap=20)
            flip = int(str(anchor_d*10).rjust(2,'0')[::-1]) if anchor_d < 10 else anchor_d
            if 1 <= flip <= EURO_RANGE and flip != anchor_d:
                L(flip, f"Law52:d{anchor_d}-flip-shadow({flip})")

    # ── Law 35 CANDIDATE — Intra-draw P3→P4 shrinking gap ──
    if len(cycle) >= 3:
        gaps34 = [d['_n'][3] - d['_n'][2] for d in cycle[-3:]]
        if gaps34[0] >= gaps34[1] >= gaps34[2]:
            # Shrinking — project gap continues
            proj_gap = max(1, gaps34[2] - 3)
            L(proj_gap, f"intra-P3-P4-shrink-projection(Law35-cand) gap={proj_gap}")

    # ── Session 19 · DIALECT LADDER + GHOST-ECHO + SLOT-REINCARNATION ──
    # Euro variant — 5 mains, +25 Euro-circle. Teaches E the ladder from the
    # last 5 draws of the cycle window.
    try:
        from session19_dialect_ladder import compute_session19_ledger
        if len(cycle) >= 2:
            window = cycle[-5:] if len(cycle) >= 5 else cycle[:]
            s19_anchor = sorted(window[0]['_n'])
            s19_recent = [sorted(d['_n']) for d in window]
            s19_ledger = compute_session19_ledger(s19_anchor, s19_recent, 'euro')
            # Law 39: unresolved ghosts hungry for next draw
            for n in s19_ledger.get('unresolved_ghosts', []):
                L(n, f"Law39:unresolved-ghost-hungry(Session19)")
            # Law 40: sum-ladder next target (P3 specialist in Euro)
            st = s19_ledger.get('next_step_sum_target')
            if st is not None:
                L(st, f"Law40:sum-ladder-P3-king(Session19)")
            # Law 41: ghost-echo candidates (P1 specialist)
            for n in s19_ledger.get('echo_candidates', []):
                L(n, f"Law41:ghost-echo-candidate(Session19)")
            # Law 42: slot-reincarnation fires
            for fire in s19_ledger.get('reincarnation_fires', []):
                L(fire['flip_wrap_target'],
                  f"Law42:slot-reincarnation(P{fire['slot']}, flip={fire['flip']})(Session19)")
            # Law 38: dialect per-slot next-step targets
            for slot, info in s19_ledger.get('next_step_targets', {}).items():
                L(info['dialect_target'],
                  f"Law38:dialect-ladder(P{slot} next={info['dialect_target']})(Session19)")
    except Exception:
        pass

    return lenses


# ═══════════════════════════════════════════════════════════════════════════
# RANKING & STAR-SCORING
# ═══════════════════════════════════════════════════════════════════════════
def rank_suspects(lenses: Dict[int, List[str]]) -> List[Tuple[int, int, List[str]]]:
    ranked = [(n, len(l), l) for n, l in lenses.items() if l]
    ranked.sort(key=lambda x: -x[1])
    return ranked


# ═══════════════════════════════════════════════════════════════════════════
# PER-POSITION SUSPECT BOARD — each slot gets its own top voices
# ═══════════════════════════════════════════════════════════════════════════
def build_per_position_board(
    lenses: Dict[int, List[str]],
    ranked: List[Tuple[int, int, List[str]]],
    banned: List[int],
    top_n: int = 5,
    cycle: Optional[List[dict]] = None,
    slot_history_rates: Optional[Dict[int, Dict[int, float]]] = None,
) -> Dict[str, List[Dict]]:
    """Per-slot suspect board with FOUR filters:
    1. Explicit-position-law count × 3
    2. Structural slot-fit (overlapping bands)
    3. Historical slot-fit penalty (kill sub-0.5% candidates at that slot)
    4. Just-fired cool-down (penalize voices that fired this slot in last 3 draws)
    """
    import re
    slot_re = re.compile(r'P([1-5])')

    slot_ranges = {
        1: (1, 18), 2: (6, 26), 3: (14, 36), 4: (22, 44), 5: (30, 50),
    }
    p1_kw = ('snap-back', 'dialect-ladder(P1', 'ghost-echo', 'DJ-delta', 'outlier-circle+25',
             'outlier-28mirror', 'P1-exact-pos-repeat', 'anchor-d', 'anchor-clock',
             'SK: S2-S1', 'cycle-position-P1', 'year-root-echo', 'snap-back-sweet',
             'snap-back-band', 'd6-raw', 'd-flip-shadow', 'Δlast-P1', 'S1-', 'P1-anchor')
    p2_kw = ('dialect-ladder(P2', 'hungry-', 'RC0-P2-exact')
    p3_kw = ('dialect-ladder(P3', 'RC0-P3-exact', 'sum-ladder-P3-king', 'SK: S2x', 'S1+21')
    p4_kw = ('dialect-ladder(P4', 'RC0-P4-exact', 'mirror28', 'DATE-mo')
    p5_kw = ('dialect-ladder(P5', 'RC0-P5-exact', 'ceiling', 'outlier-DOUBLE', 'outlier+20',
             'outlier-20', 'cooled-rebound', 'SK: S2x4 (P5')
    pos_kw = {1: p1_kw, 2: p2_kw, 3: p3_kw, 4: p4_kw, 5: p5_kw}

    # Just-fired penalty — last 3 cycle draws at same slot
    recent_same_slot: Dict[int, set] = {s: set() for s in range(1, 6)}
    if cycle:
        for d in cycle[-3:]:
            nums_sorted = sorted(d.get('_n', []))
            for i, v in enumerate(nums_sorted):
                if i < 5:
                    recent_same_slot[i+1].add(v)

    pos_scored: Dict[int, Dict[int, Tuple[float, List[str]]]] = {i: {} for i in range(1, 6)}

    for n, cnt, laws in ranked:
        if n in banned:
            continue
        for slot in range(1, 6):
            explicit_laws = []
            struct_fit = 1.0 if (slot_ranges[slot][0] <= n <= slot_ranges[slot][1]) else 0.0
            for law in laws:
                if any(k in law for k in pos_kw[slot]):
                    explicit_laws.append(law)
                else:
                    m = slot_re.search(law)
                    if m and int(m.group(1)) == slot:
                        explicit_laws.append(law)

            # Historical-fit penalty: kill if < 0.5% at this slot
            hist_rate = 0.0
            if slot_history_rates:
                hist_rate = slot_history_rates.get(slot, {}).get(n, 0.0)
            # Skip voices that have < 0.3% historical rate at this slot
            # UNLESS they have 2+ explicit-position laws (cosmic override)
            if slot_history_rates is not None and hist_rate < 0.3 and len(explicit_laws) < 2:
                continue

            score = len(explicit_laws) * 3 + struct_fit + cnt * 0.3
            # Historical rate bonus (up to +3 at 7% rate)
            score += min(hist_rate * 0.4, 3.0)
            # Just-fired cool-down penalty (−2 if voice fired this slot in last 3 draws)
            if n in recent_same_slot.get(slot, set()):
                score -= 2.0

            if struct_fit > 0 or explicit_laws:
                other_laws = [l for l in laws if l not in explicit_laws]
                ordered_laws = explicit_laws + other_laws
                pos_scored[slot][n] = (score, ordered_laws)

    out: Dict[str, List[Dict]] = {}
    for slot in range(1, 6):
        scored_list = sorted(
            pos_scored[slot].items(),
            key=lambda kv: -kv[1][0]
        )
        out[f"P{slot}"] = [
            {"n": n, "lenses": len(lenses.get(n, [])),
             "score": round(data[0], 2),
             "laws": data[1][:8]}
            for n, data in scored_list[:top_n]
        ]
    return out


def rank_stars(cycle: List[dict], rc0_stars: List[int], target_d: int) -> List[int]:
    score = {s: 0 for s in range(1, 13)}
    for s in rc0_stars: score[s] += 3
    cnt = Counter()
    for d in cycle:
        for s in d['_s']: cnt[s] += 1
    for s, c in cnt.items():
        if c >= 3: score[s] += 2
        elif c >= 1: score[s] += 1
    if cycle:
        for s in cycle[-1]['_s']: score[s] += 1
    # Sticky-Star Long-Cooled (Law 30)
    early = Counter(); mid = Counter()
    for i, d in enumerate(cycle, 1):
        for s in d['_s']:
            if i <= 3: early[s] += 1
            elif 4 <= i <= 6: mid[s] += 1
    if target_d >= 7:
        for s, c in early.items():
            if c >= 2 and mid.get(s, 0) == 0: score[s] += 2
    return sorted(score.keys(), key=lambda s: -score[s])


# ═══════════════════════════════════════════════════════════════════════════
# TICKET ORCHESTRA — narrative archetypes from The Book
# ═══════════════════════════════════════════════════════════════════════════
def build_tickets(
    ranked: List[Tuple[int, int, List[str]]],
    lenses: Dict[int, List[str]],
    star_ranking: List[int],
    rc0: dict,
    cycle: List[dict],
    hungry_fam: set,
    target_d: int,
    n_tickets: int = 30,
    banned: List[int] = None,
) -> List[Dict]:
    banned = banned or []
    rc0_nums = rc0['n']
    played = set()
    for d in cycle:
        played.update(d['_n'])
    rc0_silent = [n for n in rc0_nums if n not in played]
    unfired_hungry = sorted([h for h in hungry_fam if h not in played])

    top = [n for n,c,_ in ranked if c >= 4 and n not in banned]
    mid = [n for n,c,_ in ranked if c == 3 and n not in banned]
    low = [n for n,c,_ in ranked if c == 2 and n not in banned]
    suspects = top + mid + low

    star_pairs = list(itertools.combinations(star_ranking[:6], 2))
    tickets = []

    def add(name, mains, stars=None):
        mains = sorted(set(m for m in mains if 1 <= m <= EURO_RANGE and m not in banned))
        if len(mains) != 5: return
        if mains in [t['mains'] for t in tickets]: return
        if stars is None:
            stars = list(star_pairs[len(tickets) % len(star_pairs)]) if star_pairs else [1, 2]
        tickets.append({'archetype': name, 'mains': mains, 'stars': sorted(stars)})

    rank_of = {n: i for i, (n, _, _) in enumerate(ranked)}
    by_lens = lambda xs: sorted(xs, key=lambda x: rank_of.get(x, 9999))

    # 1. Top Symphony
    if len(top) >= 5: add("Top-Symphony", top[:5])
    if len(top) >= 6: add("Top-Symphony-v2", [top[0]]+top[2:6])

    # 2. RC0 Closing Ceremony (Law 12 exact-pos repeat for d7+)
    if target_d >= 7 and len(rc0_silent) >= 3:
        fill = by_lens([n for n in suspects if n not in rc0_silent])[:max(0, 5-len(rc0_silent))]
        add("RC0-Closing-Ceremony", rc0_silent[:5] + fill)

    # 3. Family-Hungry Loaded (Law 31)
    if len(unfired_hungry) >= 2:
        picks = unfired_hungry[:3] + by_lens([n for n in top if n not in unfired_hungry])[:2]
        add("Hungry-Family-Loaded", picks[:5])

    # 4. Outlier Orchestra
    outlier = rc0['outlier']
    op = [mirror28(outlier), circle_euro(outlier), outlier,
          outlier*2 if outlier*2 <= EURO_RANGE else 0,
          outlier-20 if outlier-20 > 0 else 0]
    op = [x for x in op if x > 0 and x not in banned]
    if len(op) >= 4:
        fill = by_lens([n for n in top if n not in op])[:1]
        add("Outlier-Orchestra", by_lens(op)[:4] + fill)

    # 5. Date-Mirror Dance (Law 33)
    day, month = None, None
    if cycle:  # derive from target via lenses (we infer)
        pass
    dm = []
    for n, _, l in ranked:
        if any('DATE' in t or 'date-day' in t or 'date-mo' in t for t in l):
            dm.append(n)
    if len(dm) >= 3:
        picks = dm[:3] + by_lens([n for n in top if n not in dm])[:2]
        add("Date-Mirror-Dance", picks[:5])

    # 6. Star-King Symphony
    sk_nums = []
    for n, _, l in ranked:
        if any('SK:' in t for t in l):
            sk_nums.append(n)
    if len(sk_nums) >= 5:
        add("Star-King-Symphony", sk_nums[:5])

    # 7. Silent-Pair Mirror-Split (Law 37 candidate)
    sp = []
    for n, _, l in ranked:
        if any('silent-28-couple' in t for t in l):
            sp.append(n)
    if len(sp) >= 4:
        fill = by_lens([n for n in top if n not in sp])[:1]
        add("Silent-28-Couple-Magic", sp[:4] + fill)

    # 8. Cooled-Rebound
    rb = [n for n,_,l in ranked if any('cooled-rebound' in t for t in l) and len(l) >= 2]
    if len(rb) >= 4:
        add("Cooled-Rebound", rb[:5])

    # 9. Ladder-Fill
    lf = [n for n,_,l in ranked if any('ladder-fill' in t for t in l) and len(l) >= 2]
    if len(lf) >= 5:
        add("Ladder-Fill", lf[:5])

    # 10. Sum-Circle + Flip-Wrap
    scfw = [n for n,_,l in ranked if any('sum-circle' in t or 'flipwrap' in t for t in l) and len(l) >= 2]
    if len(scfw) >= 4:
        fill = by_lens([n for n in top if n not in scfw])[:1]
        add("Sum-Circle-Flip-Wrap", scfw[:4] + fill)

    # 11. Self-Circle +21 Spine
    sc21 = [n for n,_,l in ranked if any('self-circle+21' in t for t in l) and len(l) >= 2]
    if len(sc21) >= 4:
        fill = by_lens([n for n in top if n not in sc21])[:1]
        add("Self-Circle-21-Spine", sc21[:4] + fill)

    # 12. Sticky-Star Harmonics
    ss = [n for n,_,l in ranked if any('sticky' in t for t in l) and len(l) >= 2]
    if len(ss) >= 4:
        fill = by_lens([n for n in top if n not in ss])[:1]
        add("Sticky-Star-Harmonics", ss[:4] + fill)

    # 13. Date-Permutation
    dp = [n for n,_,l in ranked if any('date-perm' in t or 'date-digit' in t for t in l) and len(l) >= 2]
    if len(dp) >= 4:
        add("Date-Permutation", dp[:5])

    # 14. Big-Gap Seeds
    bg = [n for n,_,l in ranked if any('big-gap' in t for t in l) and len(l) >= 2]
    if len(bg) >= 3:
        fill = by_lens([n for n in top if n not in bg])[:2]
        add("Big-Gap-Seeds", bg[:3] + fill)

    # 15. Mid-Tier Deep Dive (Law 27 Two-Lens Floor)
    if len(mid) >= 5: add("Mid-Tier-Deep-Dive", mid[:5])

    # 16. Delta-Math Lock
    dm2 = [n for n,_,l in ranked if any('DJ-delta' in t for t in l)]
    if dm2 and len(top) >= 4:
        add("Delta-Math-Lock", dm2[:1] + [n for n in top if n not in dm2][:4])

    # 17. Snap-Back Shape
    sb_lows = [n for n,_,l in ranked if n <= 7 and any('snap-back' in t for t in l)]
    if len(sb_lows) >= 2 and len(top) >= 3:
        picks = sb_lows[:2] + [n for n in top if n not in sb_lows][:3]
        add("Snap-Back-Shape", picks[:5])

    # 18-30. Symphony mixes — Law 27 Two-Lens Floor spreads
    import random
    rng = random.Random(42)
    pool = [n for n,c,_ in ranked if c >= 2 and n not in banned]
    while len(tickets) < n_tickets and len(pool) >= 5:
        picks = rng.sample(pool, 5)
        # Law 31 discipline — must carry ≥1 hungry family member in early cycle
        if target_d <= 5 and unfired_hungry and not any(h in picks for h in unfired_hungry):
            picks[0] = unfired_hungry[rng.randrange(len(unfired_hungry))]
        add(f"Symphony-Mix-{len(tickets)+1:02d}", picks)

    return tickets[:n_tickets]


# ═══════════════════════════════════════════════════════════════════════════
# DISCIPLINED BUILDER — Per-slot top-6, max 1 suspect per slot, music story
# ═══════════════════════════════════════════════════════════════════════════
def build_disciplined_tickets(
    pos_board: Dict[str, List[Dict]],
    ranked: List[Tuple[int, int, List[str]]],
    star_ranking: List[int],
    rc0: dict,
    cycle: List[dict],
    hungry_fam: set,
    target_d: int,
    n_tickets: int = 12,
    banned: List[int] = None,
) -> List[Dict]:
    """DJ's discipline: pick EXACTLY one voice per slot from its top-6 suspect
    board, assemble narrative tickets telling a music story. No floods.
    Max 1 suspect per slot = 5 suspicious voices per ticket, ascending sorted."""
    banned = banned or []
    tickets: List[Dict] = []
    star_pairs = list(itertools.combinations(star_ranking[:4], 2))

    # Helper: top-k voices per slot with their primary law tag
    def slot_pick(slot: int, k: int = 3) -> List[Tuple[int, str]]:
        entries = pos_board.get(f"P{slot}", [])[:k]
        out = []
        for e in entries:
            primary = (e['laws'][0] if e['laws'] else 'raw')
            # Compact the law tag for narrative
            tag = primary.split('(')[0].replace('Law', 'L').strip()
            if len(tag) > 28:
                tag = tag[:28] + '…'
            out.append((e['n'], tag))
        return out

    slots = {i: slot_pick(i, 5) for i in range(1, 6)}

    # Per-slot voice-usage cap: no voice may appear at the SAME SLOT in more
    # than 40% of tickets (e.g. max 4 of 10). This is the DJ's "don't let 1
    # land P1 in 10/20 tickets" discipline.
    max_slot_reuse = max(2, int(n_tickets * 0.4))
    slot_usage: Dict[Tuple[int, int], int] = {}  # (slot, voice) -> count

    def weave(name: str, slot_choices: List[Tuple[int, str]], theme: str) -> bool:
        """Assemble a ticket from per-slot choices with duplicate-safe fallback
        AND per-slot voice-cap. If a chosen voice already hit its cap at that
        slot, fall through the top-5 for a cooler alternative."""
        final: List[Tuple[int, str]] = []
        seen: set = set()
        slot_full = [slots[i] for i in range(1, 6)]
        for slot_idx, (n, tag) in enumerate(slot_choices):
            slot_num = slot_idx + 1
            # Try primary pick first
            pick: Optional[Tuple[int, str]] = None
            if (n not in seen and (1 <= n <= EURO_RANGE) and n not in banned
                and slot_usage.get((slot_num, n), 0) < max_slot_reuse):
                pick = (n, tag)
            if pick is None:
                # Scan slot's top-5 for alternative
                for cand_n, cand_tag in slot_full[slot_idx]:
                    if (cand_n not in seen and cand_n not in banned
                        and 1 <= cand_n <= EURO_RANGE
                        and slot_usage.get((slot_num, cand_n), 0) < max_slot_reuse):
                        pick = (cand_n, cand_tag)
                        break
            if pick is None:
                # Last resort: accept any non-duplicate from slot top-5
                for cand_n, cand_tag in slot_full[slot_idx]:
                    if (cand_n not in seen and cand_n not in banned
                        and 1 <= cand_n <= EURO_RANGE):
                        pick = (cand_n, cand_tag)
                        break
            if pick is None:
                return False
            final.append(pick)
            seen.add(pick[0])

        if len(final) != 5:
            return False
        mains_sorted = sorted(n for n, _ in final)
        if any(t['mains'] == mains_sorted for t in tickets):
            return False
        # Commit slot-usage
        for slot_idx, (n, _) in enumerate(final):
            slot_usage[(slot_idx+1, n)] = slot_usage.get((slot_idx+1, n), 0) + 1
        story_parts = [f"P{i+1}={n:02d}·{tag}" for i, (n, tag) in enumerate(final)]
        stars = list(star_pairs[len(tickets) % len(star_pairs)]) if star_pairs else [1, 2]
        tickets.append({
            'archetype': name,
            'theme': theme,
            'mains': mains_sorted,
            'stars': sorted(stars),
            'music_story': " · ".join(story_parts),
        })
        return True

    # T1: Top-voice-per-slot (E's purest reading)
    if all(slots[i] for i in range(1, 6)):
        weave("Pure-Top-Voice", [slots[i][0] for i in range(1, 6)],
              "E's loudest voice at every slot")

    # T2: Second-voice-per-slot (alternative harmony)
    if all(len(slots[i]) >= 2 for i in range(1, 6)):
        weave("Alt-Harmony", [slots[i][1] for i in range(1, 6)],
              "The alternative voice — if the top decoys")

    # T3: Back-heavy — front top-1, back second-voice
    if all(slots[i] for i in range(1, 6)) and len(slots[4]) >= 2 and len(slots[5]) >= 2:
        weave("Back-Heavy",
              [slots[1][0], slots[2][0], slots[3][0], slots[4][1], slots[5][1]],
              "Front-raw, back-shadow")

    # T4: Front-shadow — P1-P2 second-voice, back top-1
    if len(slots[1]) >= 2 and len(slots[2]) >= 2 and all(slots[i] for i in range(3, 6)):
        weave("Front-Shadow",
              [slots[1][1], slots[2][1], slots[3][0], slots[4][0], slots[5][0]],
              "P1-P2 hidden voices, back kings")

    # T5: Deep-hunger — prefer RC0-silent or hungry-family voices per slot
    rc0_nums = rc0['n']
    played = set()
    for d in cycle: played.update(d['_n'])
    rc0_silent = [n for n in rc0_nums if n not in played]
    hungry_unfired = sorted([h for h in hungry_fam if h not in played])
    deep_picks: List[Tuple[int, str]] = []
    for i in range(1, 6):
        preferred = None
        for entry in pos_board.get(f"P{i}", []):
            if entry['n'] in rc0_silent or entry['n'] in hungry_unfired:
                tag = (entry['laws'][0].split('(')[0] if entry['laws'] else 'hungry')
                preferred = (entry['n'], tag)
                break
        if not preferred and slots[i]:
            preferred = slots[i][0]
        if preferred:
            deep_picks.append(preferred)
    if len(deep_picks) == 5:
        weave("Deep-Hunger", deep_picks, "Every slot pays the unpaid bill")

    # T6: d-Clock echo — prefer voices that fire Law52 (d-digit family)
    dclock_picks: List[Tuple[int, str]] = []
    for i in range(1, 6):
        preferred = None
        for entry in pos_board.get(f"P{i}", []):
            if any('Law52' in l for l in entry['laws']):
                tag = next((l.split('(')[0] for l in entry['laws'] if 'Law52' in l), 'Law52')
                preferred = (entry['n'], tag)
                break
        if not preferred and slots[i]:
            preferred = slots[i][0]
        if preferred:
            dclock_picks.append(preferred)
    if len(dclock_picks) == 5:
        weave("d-Clock-Echo", dclock_picks, "Every voice answers the anchor clock")

    # T7-T12: Rotation through per-slot voice combinations (deterministic)
    import itertools as _it
    combos = list(_it.product(
        range(min(3, len(slots[1]))) if slots[1] else [0],
        range(min(3, len(slots[2]))) if slots[2] else [0],
        range(min(3, len(slots[3]))) if slots[3] else [0],
        range(min(2, len(slots[4]))) if slots[4] else [0],
        range(min(2, len(slots[5]))) if slots[5] else [0],
    ))
    for idx, combo in enumerate(combos):
        if len(tickets) >= n_tickets:
            break
        try:
            picks = [slots[i+1][combo[i]] for i in range(5)]
            weave(f"Rotation-{idx+1:02d}", picks, f"Combo {combo}")
        except IndexError:
            continue

    return tickets[:n_tickets]


# ═══════════════════════════════════════════════════════════════════════════
# DJ VOICE
# ═══════════════════════════════════════════════════════════════════════════
def dj_speak(rc0: dict, target_date: dt, target_d: int,
             ranked: List, tickets: List, hungry_fam: set,
             rc0_silent: List[int]) -> str:
    lines = []
    lines.append(f"🎻🎧 Ya man! Engine tuned for {target_date.strftime('%d-%m-%Y')} = d{target_d} from rare {rc0['date']}.\n")
    lines.append(f"Rare {rc0['family']}0s · outlier {rc0['outlier']} · hungry-family {sorted(hungry_fam)}")
    if rc0_silent:
        lines.append(f"🔴 RC0 rare-silent: {rc0_silent}")
    top = [n for n,c,_ in ranked if c >= 4]
    mid = [n for n,c,_ in ranked if c == 3]
    lines.append(f"\n🏆 TOP resonators ({len(top)}): {sorted(top)}")
    lines.append(f"🎺 MID resonators ({len(mid)}): {sorted(mid)}")
    if 7 <= target_d <= 9:
        lines.append(f"\n📍 d{target_d} — date-mirror28 SWEET SPOT (26% fire rate, Law 33) 🪞")
    elif target_d <= 3:
        lines.append(f"\n📍 d{target_d} — family-hungry DOMINANCE (Law 31, 100% cycle rate) 🌾")
    lines.append("\n🎫 THE ENGINE'S TICKETS:")
    for i, t in enumerate(tickets, 1):
        m = "-".join(f"{x:02d}" for x in t['mains'])
        s = f"{t['stars'][0]:02d}-{t['stars'][1]:02d}"
        lines.append(f"  {i:>2}. [{t['archetype']:<26}] {m}   ⭐{s}")
    lines.append(f"\n🥂 {len(tickets)} tickets built from the suspect list. Music tuned 🎻🎧")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════
async def run_cosmic_engine(
    target_date_str: str,
    n_tickets: int = 30,
    banned: Optional[List[int]] = None,
) -> Dict:
    banned = banned or []
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    draws = await load_euro_draws(db)
    target_date = dt.strptime(target_date_str, '%d.%m.%Y')

    found = find_last_family_rare(draws, target_date)
    if not found:
        return {'error': 'no rare found'}
    _, rc0 = found

    cycle = [d for d in draws if rc0['dt'] < d['_dt'] < target_date]
    target_d = len(cycle) + 1

    lenses = build_convergence_board(rc0, cycle, target_date, target_d, banned)
    ranked = rank_suspects(lenses)
    # Historical slot rates for structural-fit + cool-down penalties
    slot_rates = compute_slot_history_rates(draws)
    pos_board = build_per_position_board(
        lenses, ranked, banned, top_n=5,
        cycle=cycle, slot_history_rates=slot_rates,
    )
    star_ranking = rank_stars(cycle, rc0['s'], target_d)

    # hungry
    family = rc0['family']
    fr_lo = family*10 if family > 0 else 1
    fr_hi = family*10 + 10 if family > 0 else 10
    fam_set = set(range(fr_lo, fr_hi))
    rc0_in_fam = {x for x in rc0['n'] if decade(x) == family}
    hungry = fam_set - rc0_in_fam

    played = set()
    for d in cycle: played.update(d['_n'])
    rc0_silent = [n for n in rc0['n'] if n not in played]

    tickets = build_tickets(ranked, lenses, star_ranking, rc0, cycle,
                            hungry, target_d, n_tickets, banned)
    # DJ's disciplined tickets — 1 suspect per slot, each ticket a music story
    disciplined = build_disciplined_tickets(
        pos_board, ranked, star_ranking, rc0, cycle, hungry, target_d,
        n_tickets=12, banned=banned,
    )

    voice = dj_speak(rc0, target_date, target_d, ranked, tickets, hungry, rc0_silent)

    # Tablet for response
    tablet = []
    tablet.append({
        'd': 'd0', 'date': rc0['date'][:5],
        'mains': rc0['n'], 'stars': rc0['s'],
    })
    for i, d in enumerate(cycle, 1):
        tablet.append({
            'd': f'd{i}', 'date': d['date'][:5],
            'mains': d['_n'], 'stars': d['_s'],
        })

    return {
        'rc0': {'date': rc0['date'], 'mains': rc0['n'], 'stars': rc0['s'],
                'family': family, 'outlier': rc0['outlier']},
        'target_date': target_date_str,
        'target_d': target_d,
        'tablet': tablet,
        'cycle_count': len(cycle),
        'hungry_family': sorted(hungry),
        'hungry_unfired': sorted([h for h in hungry if h not in played]),
        'rc0_silent': rc0_silent,
        'top_tier': sorted([n for n,c,_ in ranked if c >= 4]),
        'mid_tier': sorted([n for n,c,_ in ranked if c == 3]),
        'support_tier': sorted([n for n,c,_ in ranked if c == 2]),
        'suspect_board': [{'n': n, 'lenses': c, 'laws': l} for n,c,l in ranked[:30]],
        'pos_board': pos_board,
        'anchor_d': min(5, len(cycle)) + 1,
        'star_ranking': star_ranking[:6],
        'tickets': tickets,
        'disciplined_tickets': disciplined,
        'banned': banned,
        'voice': voice,
    }


if __name__ == '__main__':
    import asyncio, sys
    target = sys.argv[1] if len(sys.argv) > 1 else '21.04.2026'
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    result = asyncio.run(run_cosmic_engine(target, n, banned=[21, 24, 28]))
    print(result['voice'])
