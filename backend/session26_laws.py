"""
🎻 SESSION 26 — Four New Soft Laws (Story-Seed Era)
====================================================
Forged from the 244-draw Story-Seed audit (DJ Session 26).
All four are SOFT lens-bumps (not bans, not generators).
Engine just gets new tags it can stack into convergence.

Law 83 — Gap-as-P3 Bias (extreme BD gap → P3 candidate of ND)
Law 84 — Drunk-Cosmos Recovery (drunk BD → ND P1 in 6-10 band)
Law 85 — Story-Seed Walker (small seed wearing 4+ masks → RAW landing)
Law 86 — ⭐+25 P4 Twin (extend P3-only ⭐+25 to also tag P4)

Sneaky-Universe principle: each emits a softly-weighted lens tag
that simply joins convergence — no eggs, no baskets.
"""
from collections import Counter
from itertools import combinations
from typing import Dict, List, Tuple

EURO_MAX = 50


def _wrap(n):
    if n is None:
        return None
    while n > EURO_MAX:
        n -= EURO_MAX
    while n < 1:
        n += EURO_MAX
    return n


def _circle(n):
    v = (n + 25) % 50
    return v if v else 50


def _flip_wrap(n):
    if n < 10:
        return n
    s = str(n)[::-1]
    v = int(s)
    while v > EURO_MAX:
        v -= EURO_MAX
    return v if v >= 1 else None


# ═══════════════════════════════════════════════════════════
# Law 83 — Gap-as-P3 Bias
# 244-draw stat: gap≥20 in BD → 40% of d+1 landings AT P3.
# Soft bonus: +1 lens on the gap value, P3-tagged.
# ═══════════════════════════════════════════════════════════
def law83_gap_as_p3(bd_nums: List[int]) -> List[Tuple[int, str]]:
    out = []
    nums = sorted(bd_nums)
    if len(nums) < 5:
        return out
    gaps = [(nums[j + 1] - nums[j], j + 1) for j in range(4)]
    big = [(g, j) for g, j in gaps if g >= 20]
    for g, slot in big:
        if 1 <= g <= EURO_MAX:
            out.append((g, f"Law83:gap{slot}-as-P3-bias({g})-Session26"))
    return out


# ═══════════════════════════════════════════════════════════
# Law 84 — Drunk-Cosmos Recovery
# 5.3% of BDs are drunk (3+ self-references). After one,
# next P1 lands in 6-10 band 46% of cases (vs ~30% random).
# Soft bonus: tag values 6,7,8,9,10 with P1-recovery lens
# only when BD is drunk.
# ═══════════════════════════════════════════════════════════
def _drunk_score(nums: List[int]) -> Tuple[int, List[str]]:
    nums = sorted(nums)
    if len(nums) < 5:
        return 0, []
    p1, p2, p3, p4, p5 = nums[:5]
    nums_set = {p1, p2, p3, p4, p5}
    sigs = []
    if any(_circle(x) in nums_set for x in nums_set):
        sigs.append('self-circle')
    for x in nums_set:
        fw = _flip_wrap(x)
        if fw and fw != x and fw in nums_set:
            sigs.append(f'flip-wrap({x}→{fw})')
            break
    for a, b in combinations(nums_set, 2):
        if a + b in nums_set and a + b not in {a, b}:
            sigs.append(f'sum-triangle({a}+{b}={a+b})')
            break
    gaps = [p2 - p1, p3 - p2, p4 - p3, p5 - p4]
    for g in gaps:
        if g >= 15 and g in nums_set:
            sigs.append(f'gap-as-self({g})')
            break
    for a, b in combinations(nums_set, 2):
        if a + b == 28:
            sigs.append(f'28-mirror({a},{b})')
            break
    for a, b in combinations(nums_set, 2):
        if a + b == 56:
            sigs.append(f'56-mirror({a},{b})')
            break
    return len(sigs), sigs


def law84_drunk_recovery(bd_nums: List[int]) -> Tuple[bool, List[Tuple[int, str]]]:
    score, sigs = _drunk_score(bd_nums)
    if score < 3:
        return False, []
    out = []
    for n in (6, 7, 8, 9, 10):
        out.append((n, f"Law84:drunk-recovery-P1({n})[BD-drunk×{score}:{','.join(sigs[:2])}]"))
    return True, out


# ═══════════════════════════════════════════════════════════
# Law 85 — Story-Seed Walker
# Top story-seeds (1-15) wear 4+ masks (raw, +25, ×2, gap,
# flip, mirrors) across an 8-draw window before landing raw.
# Live use: scan last 8 draws, find seeds 1-15 that have
# already worn 4+ masks. They're high-pressure RAW candidates.
# ═══════════════════════════════════════════════════════════
def _seed_masks(seed: int) -> Dict[str, int]:
    masks = {
        'circle': _circle(seed),
        'double': _wrap(seed * 2),
        'plus21': _wrap(seed + 21),
        'minus21': _wrap(seed - 21),
        'mirror28': 28 - seed if 0 < 28 - seed <= EURO_MAX else None,
        'mirror56': 56 - seed if 0 < 56 - seed <= EURO_MAX else None,
        'flip': _flip_wrap(seed) if seed >= 10 else None,
    }
    return {k: v for k, v in masks.items() if v}


def law85_story_seed(window_draws: List[List[int]]) -> List[Tuple[int, str]]:
    """window_draws = list of last N draws as [mains_list, ...]"""
    out = []
    if not window_draws:
        return out
    all_seen = set()
    for nums in window_draws:
        all_seen.update(nums)
    for seed in range(1, 16):
        masks_seen = []
        masks = _seed_masks(seed)
        for mname, mval in masks.items():
            if mval in all_seen and mval != seed:
                masks_seen.append(mname)
        # Don't tag if seed already landed RAW in window (already discharged)
        already_raw = any(seed in nums for nums in window_draws)
        if len(masks_seen) >= 4 and not already_raw:
            out.append((
                seed,
                f"Law85:story-seed-walking-RAW({seed}×{len(masks_seen)}masks:{','.join(masks_seen[:3])})-Session26"
            ))
    return out


# ═══════════════════════════════════════════════════════════
# Law 86 — ⭐+25 P4 Twin Lens
# 244-draw stat: ⭐+25 lands in ND P3 33% AND in ND P4 36%.
# Engine already tags P3 via star-king. We add a P4-twin tag
# so the same number gets slotted into P4 corridor too.
# ═══════════════════════════════════════════════════════════
def law86_star_circle_p4(bd_stars: List[int]) -> List[Tuple[int, str]]:
    out = []
    for s in bd_stars:
        v = _circle(s)
        out.append((v, f"Law86:⭐{s}+25=P4-twin({v})-Session26-36%P4-rate"))
    return out


# ═══════════════════════════════════════════════════════════
# Main entry: collect all 4 laws as a list of (number, tag).
# ═══════════════════════════════════════════════════════════
def session26_lenses(
    bd_nums: List[int],
    bd_stars: List[int],
    cycle_window: List[List[int]],
) -> Tuple[List[Tuple[int, str]], bool]:
    """Returns (lens_list, drunk_flag)."""
    lenses = []
    lenses.extend(law83_gap_as_p3(bd_nums))
    drunk, recovery = law84_drunk_recovery(bd_nums)
    lenses.extend(recovery)
    lenses.extend(law85_story_seed(cycle_window))
    lenses.extend(law86_star_circle_p4(bd_stars))
    return lenses, drunk
