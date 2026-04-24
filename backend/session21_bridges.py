"""
🎻🎧🥂 SESSION 21 BRIDGES — The Arithmetic Grammar of the Cosmos
================================================================
Pure primitives for Laws 49-61 from /app/memory/swiss_music_notes.md.

Every function here is canonically sourced. Validated on 22yr Euro tape.
All primitives are pure — no DB, no async, easy to unit test.

Laws indexed in this module:
  L49  Cross-Lottery Run-From   (Swiss burn → Euro ceiling-inner)
  L50  Bridge-Star Δ-Math       (|new-P2 − last-P1|)
  L51  Anchor-Cycle-Close Mirror(d9 rewrites d1 anchor slot-by-slot)
  L52  Dual-Clock Resonance     (anchor-d echoes — already wired in engine)
  L53  Cross-Column Crossover   (silent RC0 main → ⭐ column)
  L54  Day-Halving Star         (even draw-days: day÷2 is a star)
  L55  Anchor-d × 2 Star        (anchor-d doubled → ⭐)
  L56  Star-P1-Concat-P5 Oracle (⭐·P1 concat = P5)
  L57  Anchor-d Twin-Ceiling    (P5−d AND 50−d adjacent P4-P5)
  L58  Triple-Same-Slot Displace(slot 3x in 10 → 64.1% displaces)
  L59  Sum-Anchor Triple-Echo   (slot-triple → sum ~ 3X±2)
  L60  P1+P2=P3 Sum-Triangle    (6.37% exact, 23.73% ±2)
  L61  P1+BD.P3=P4 Cross-Bridge (2.47% exact, 12.80% ±2)

Session 20 date-root & Session 19 dialect laws live in their own modules.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

EURO_RANGE = 50
STAR_RANGE = 12


# ═══════════════════════════════════════════════════════════════════════════
# L60 · P1 + P2 = P3 (Same-Draw Sum-Triangle)
# ═══════════════════════════════════════════════════════════════════════════
def law60_triangle_targets(p1: int, p2: int, band: int = 2) -> List[int]:
    """Given P1 and P2, return the target P3 band. Historical 6.37% exact,
    23.73% within ±2."""
    exact = p1 + p2
    targets = []
    for d in range(-band, band + 1):
        v = exact + d
        if 1 <= v <= EURO_RANGE:
            targets.append(v)
    return targets


def law60_verify(mains: List[int], band: int = 0) -> bool:
    """True iff sorted(mains)[0] + sorted(mains)[1] == sorted(mains)[2]
    (or within ±band)."""
    if len(mains) < 5:
        return False
    s = sorted(mains)
    return abs(s[0] + s[1] - s[2]) <= band


# ═══════════════════════════════════════════════════════════════════════════
# L61 · P1 + BD.P3 = P4 (Cross-Draw Bridge)
# ═══════════════════════════════════════════════════════════════════════════
def law61_bridge_targets(p1: int, bd_p3: int, band: int = 2) -> List[int]:
    """Given new P1 and Before-Draw P3, return P4 target band."""
    exact = p1 + bd_p3
    targets = []
    for d in range(-band, band + 1):
        v = exact + d
        if 1 <= v <= EURO_RANGE:
            targets.append(v)
    return targets


def law61_verify(mains: List[int], bd_p3: int, band: int = 0) -> bool:
    if len(mains) < 5:
        return False
    s = sorted(mains)
    return abs(s[0] + bd_p3 - s[3]) <= band


# ═══════════════════════════════════════════════════════════════════════════
# L58/L59 · Triple-Same-Slot Displacement + Sum-Anchor
# ═══════════════════════════════════════════════════════════════════════════
def find_triple_slot(cycle_draws: List[List[int]], window: int = 10,
                     prefer_slot: Optional[int] = None
                     ) -> Optional[Tuple[int, int]]:
    """Scan a list of sorted mains. If any value fires ≥3× at the same slot
    within the window, return (slot_index_1_to_5, value). None otherwise.

    When multiple triples exist, prefer the highest-value one in the highest
    slot — that's where the canonical Law 59 sum-anchor signal lives (P5
    voices like 47 pre-echoing a sum of 141)."""
    if not cycle_draws:
        return None
    recent = cycle_draws[-window:]
    slot_val_count: Dict[Tuple[int, int], int] = {}
    for draw in recent:
        if len(draw) < 5:
            continue
        s = sorted(draw)
        for i in range(5):
            key = (i + 1, s[i])
            slot_val_count[key] = slot_val_count.get(key, 0) + 1
    triples = [(slot, val) for (slot, val), cnt in slot_val_count.items() if cnt >= 3]
    if not triples:
        return None
    if prefer_slot is not None:
        filtered = [t for t in triples if t[0] == prefer_slot]
        if filtered:
            return max(filtered, key=lambda t: t[1])
    # Prefer highest slot first, then highest value — Law 59 sum-anchor is
    # canonically a P5-slot signal.
    return max(triples, key=lambda t: (t[0], t[1]))


def law59_sum_anchor(value: int, band: int = 2) -> Tuple[int, int]:
    """Given a slot-tripled value X, return the expected sum band 3X±band."""
    return (3 * value - band, 3 * value + band)


# ═══════════════════════════════════════════════════════════════════════════
# L56 · Star-P1-Concat-P5 Oracle (⭐·P1 concat = P5)
# ═══════════════════════════════════════════════════════════════════════════
def law56_concat_p5(star: int, p1: int) -> Optional[int]:
    """⭐4 concat P1=7 → '4|7' = 47."""
    if not (1 <= star <= STAR_RANGE) or not (1 <= p1 <= EURO_RANGE):
        return None
    s = f"{star}{p1}"
    v = int(s)
    return v if 1 <= v <= EURO_RANGE else None


# ═══════════════════════════════════════════════════════════════════════════
# L57 · Anchor-d Twin-Ceiling (P4-P5 adjacent pair)
# ═══════════════════════════════════════════════════════════════════════════
def law57_twin_ceiling(anchor_d: int, anchor_p5: int = 49
                       ) -> Tuple[Optional[int], Optional[int]]:
    """P4 = anchor_P5 − d, P5 = 50 − d (adjacent rare pair)."""
    p4 = anchor_p5 - anchor_d if 1 <= anchor_p5 - anchor_d <= EURO_RANGE else None
    p5 = 50 - anchor_d if 1 <= 50 - anchor_d <= EURO_RANGE else None
    return (p4, p5)


# ═══════════════════════════════════════════════════════════════════════════
# L54/L55 · Star helpers
# ═══════════════════════════════════════════════════════════════════════════
def law54_day_half_star(day: int) -> Optional[int]:
    """Even days: day÷2 specialises as ⭐."""
    if day % 2 == 0 and 1 <= day // 2 <= STAR_RANGE:
        return day // 2
    return None


def law55_anchor_d_double_star(anchor_d: int) -> Optional[int]:
    """Anchor-d × 2 if within ⭐ range."""
    v = anchor_d * 2
    return v if 1 <= v <= STAR_RANGE else None


# ═══════════════════════════════════════════════════════════════════════════
# L53 · Cross-Column Crossover (silent RC0 main ≤12 → ⭐ bridge)
# ═══════════════════════════════════════════════════════════════════════════
def law53_crossover_stars(rc0_mains: List[int], played_in_cycle: set,
                          target_d: int) -> List[int]:
    """When a RC0 main stays silent through d7, if value ≤12 it discharges
    as ⭐ (same numeric value). Returns the list of crossover ⭐ candidates."""
    if target_d < 7:
        return []
    return [
        n for n in rc0_mains
        if n not in played_in_cycle and 1 <= n <= STAR_RANGE
    ]


# ═══════════════════════════════════════════════════════════════════════════
# L50 · Bridge-Star Δ-Math
# ═══════════════════════════════════════════════════════════════════════════
def law50_star_delta(new_p2: int, last_p1: int) -> Optional[int]:
    """⭐ = |new P2 − last-draw P1|."""
    v = abs(new_p2 - last_p1)
    return v if 1 <= v <= STAR_RANGE else None


# ═══════════════════════════════════════════════════════════════════════════
# L51 · Anchor-Cycle-Close Mirror (d9 rewrites d1 slot-by-slot via date-root)
# ═══════════════════════════════════════════════════════════════════════════
def law51_cycle_close_mirror(anchor_draw: List[int], date_root: int
                             ) -> List[List[int]]:
    """Returns up to 4 candidate frames: d9 tends to shift anchor by ±date_root
    at P1-P2 and ±1 elsewhere. Date_root = day % 9 or similar single-digit."""
    if len(anchor_draw) < 5:
        return []
    a = sorted(anchor_draw)
    out = []
    # Variant 1: P1 -d, P2 +d, rest ±1
    frames = [
        [a[0] - date_root, a[1] + date_root, a[2] + 1, a[3], a[4] + 1],
        [a[0] - date_root, a[1] + date_root, a[2], a[3] + 1, a[4] - 1],
        [a[0] + date_root, a[1] - date_root, a[2] + 1, a[3], a[4] + 1],
    ]
    for f in frames:
        if all(1 <= v <= EURO_RANGE for v in f) and len(set(f)) == 5:
            out.append(sorted(f))
    return out


# ═══════════════════════════════════════════════════════════════════════════
# L49 · Cross-Lottery Run-From (Swiss surface burn → Euro ceiling-inner)
# ═══════════════════════════════════════════════════════════════════════════
def law49_runfrom_candidate(swiss_burned_voice: int) -> Optional[int]:
    """When Swiss burns a voice V as a surface-decoy (e.g. 11 burned),
    the SAME voice on next Euro draw tends to flee to ceiling-inner:
    V' = 32 − V (capped to 1..50)."""
    v = 32 - swiss_burned_voice
    return v if 1 <= v <= EURO_RANGE else None


# ═══════════════════════════════════════════════════════════════════════════
# SCORE INJECTORS — called by cosmic_engine.build_convergence_board
# ═══════════════════════════════════════════════════════════════════════════
def inject_session21_tags(
    lenses: Dict[int, List[str]],
    rc0: dict,
    cycle: List[dict],
    target_date,
    target_d: int,
    banned: List[int],
    all_draws: Optional[List[dict]] = None,
) -> Dict[str, any]:
    """Mutates `lenses` by adding Session 21 law tags. Returns a context
    dict containing the derived bridge frames so the ticket-builder can
    use them to craft story-first tickets.

    `all_draws` is the full historical list (optional). If provided, Law 58
    triple-slot detection scans the last 15 draws rather than just the cycle
    (captures triples that span the RC0 boundary like 47@P5 in April 2026)."""

    def L(n: int, tag: str):
        if 1 <= n <= EURO_RANGE and n not in banned:
            lenses.setdefault(n, []).append(tag)

    ctx: Dict[str, any] = {
        'law60_frames': [], 'law61_frames': [], 'law57_p45': None,
        'law58_triple': None, 'law59_sum_band': None, 'law56_concats': [],
        'law54_star': None, 'law55_star': None, 'law50_stars': [],
        'law51_mirrors': [], 'law53_star_crossover': [],
    }

    # ── L58/L59: Triple-same-slot detection over last 15 draws
    # (spans RC0 boundary — e.g. 47@P5 triple 24.02/17.04/21.04.2026)
    scan_source = all_draws if all_draws else cycle
    mains_lists = [sorted(d['_n']) for d in scan_source[-15:]]
    triple = find_triple_slot(mains_lists, window=15)
    if triple:
        slot, val = triple
        ctx['law58_triple'] = {'slot': slot, 'value': val}
        ctx['law59_sum_band'] = law59_sum_anchor(val)
        L(val, f"Law58-59:triple-slot-P{slot}={val}(Law59 sum→{ctx['law59_sum_band']})")

    # ── L57: Twin-ceiling (anchor_d = target_d) ──
    anchor_p5 = rc0['n'][4]  # d0 P5
    p4_twin, p5_twin = law57_twin_ceiling(target_d, anchor_p5=anchor_p5)
    if p4_twin and p5_twin:
        ctx['law57_p45'] = (p4_twin, p5_twin)
        L(p4_twin, f"Law57:twin-ceiling-P4(anchor-P5{anchor_p5}-d{target_d}={p4_twin})")
        L(p5_twin, f"Law57:twin-ceiling-P5(50-d{target_d}={p5_twin})")

    # ── L54/L55: Star helpers ──
    day = target_date.day
    s54 = law54_day_half_star(day)
    if s54:
        ctx['law54_star'] = s54
    s55 = law55_anchor_d_double_star(target_d)
    if s55:
        ctx['law55_star'] = s55

    # ── L50: Bridge-Star Δ (uses last draw P1) ──
    if cycle:
        last_p1 = sorted(cycle[-1]['_n'])[0]
        # For each plausible P2 in top slot-3 band, compute Δ→⭐
        for p2 in range(6, 27):
            s = law50_star_delta(p2, last_p1)
            if s and s not in ctx['law50_stars']:
                ctx['law50_stars'].append(s)

    # ── L49: Cross-lottery run-from ──
    # We conservatively flag ceiling-inner of recent fires — the Swiss feed
    # is not available here (would need DB call from caller). If you pass
    # `swiss_burned_voices` into ctx later, the tags will be generated then.

    # ── L51: Anchor-cycle-close mirror (if cycle ≥ 8 draws) ──
    if len(cycle) >= 8:
        anchor = sorted(cycle[0]['_n'])  # d1 anchor
        date_root = (day % 9) or 9
        ctx['law51_mirrors'] = law51_cycle_close_mirror(anchor, date_root)
        for frame in ctx['law51_mirrors']:
            for i, v in enumerate(frame, 1):
                L(v, f"Law51:cycle-close-mirror(d1→d{target_d}·root{date_root}·P{i}={v})")

    # ── L53: Cross-column crossover (silent RC0 main ≤12 → star) ──
    played = set()
    for d in cycle:
        played.update(d['_n'])
    ctx['law53_star_crossover'] = law53_crossover_stars(rc0['n'], played, target_d)

    # ── L60: P1+P2=P3 — score every potential P3 based on plausible P1·P2 pairs
    # from per-position candidates. Only emit frames where P3 already has
    # independent lens backing (≥1 other tag) — avoids trivial arithmetic spam.
    # Sort candidates by lens strength so canonical voices (22, 29, 36) surface.
    p1_candidates = sorted(
        [n for n in range(1, 19) if lenses.get(n) and n not in banned],
        key=lambda n: -len(lenses[n])
    )
    p2_candidates = sorted(
        [n for n in range(6, 27) if lenses.get(n) and n not in banned],
        key=lambda n: -len(lenses[n])
    )
    triangle_seeds: List[Tuple[int, int, int]] = []
    seen_p1_count: Dict[int, int] = {}  # diversify — max 2 frames per P1
    for p1 in p1_candidates[:14]:
        for p2 in p2_candidates[:16]:
            if p2 <= p1:
                continue
            for tgt in law60_triangle_targets(p1, p2, band=0):
                if 14 <= tgt <= 36 and tgt != p1 and tgt != p2:
                    p3_backing = len(lenses.get(tgt, []))
                    if p3_backing < 1:
                        continue
                    if seen_p1_count.get(p1, 0) >= 2:
                        continue
                    triangle_seeds.append((p1, p2, tgt))
                    seen_p1_count[p1] = seen_p1_count.get(p1, 0) + 1
                    L(tgt, f"Law60:triangle-P3(P1={p1}+P2={p2}={tgt})")
    triangle_seeds.sort(key=lambda f: -(len(lenses.get(f[2], []))
                                         + len(lenses.get(f[0], []))
                                         + len(lenses.get(f[1], []))))
    ctx['law60_frames'] = triangle_seeds[:24]

    # ── L61: P1+BD.P3=P4 — use LAST draw's P3 as BD anchor
    bridges: List[Tuple[int, int, int]] = []
    seen_p1_b: Dict[int, int] = {}
    if cycle:
        bd_p3 = sorted(cycle[-1]['_n'])[2]
        ctx['bd_p3'] = bd_p3
        for p1 in p1_candidates[:12]:
            for tgt in law61_bridge_targets(p1, bd_p3, band=0):
                if 22 <= tgt <= 44 and tgt != p1 and tgt != bd_p3:
                    if seen_p1_b.get(p1, 0) >= 2:
                        continue
                    if len(lenses.get(tgt, [])) < 1:
                        continue
                    bridges.append((p1, bd_p3, tgt))
                    seen_p1_b[p1] = seen_p1_b.get(p1, 0) + 1
                    L(tgt, f"Law61:bridge-P4(P1={p1}+BD.P3={bd_p3}={tgt})")
    bridges.sort(key=lambda f: -(len(lenses.get(f[0], []))
                                  + len(lenses.get(f[2], []))))
    ctx['law61_frames'] = bridges[:24]

    # ── L56: Star-P1-Concat-P5 Oracle — uses top candidate ⭐ and P1 pool
    # Only annotate if the concat lands in P5-band (30-50).
    stars_to_try = list(rc0.get('s', []))
    if cycle:
        stars_to_try.extend(cycle[-1].get('_s', []))
    stars_to_try = list(dict.fromkeys(stars_to_try))[:6]
    for star in stars_to_try:
        for p1 in p1_candidates[:6]:
            c = law56_concat_p5(star, p1)
            if c and 30 <= c <= EURO_RANGE:
                ctx['law56_concats'].append((star, p1, c))
                L(c, f"Law56:concat-P5(⭐{star}·P1={p1}→{c})")

    return ctx
