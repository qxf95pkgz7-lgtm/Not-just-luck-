"""
🎻🎧🥂 RANDOM BASELINE — DJ's pure-math reality check (29.04.2026)
====================================================================
"If you do random 100 tickets, what chance you hit 4? 3? 2?"

Closed-form hypergeometric probabilities for both lotteries:
  • Euro:  5 of 50 mains + 2 of 12 stars
  • Swiss: 6 of 42 mains + 🍀1 of 6 lucky + R 1 of 35 replay

Each helper returns the per-ticket probability so the box can show:
  E_actual_hit_rate  ·  Random_baseline  ·  Multiplier (×)
"""
from __future__ import annotations
from math import comb
from typing import Dict


# ════════════════════════════════════════════════════════════════════
# EURO 5/50 + 2/12 stars
# ════════════════════════════════════════════════════════════════════
EURO_TOTAL_MAINS = comb(50, 5)        # 2_118_760
EURO_TOTAL_STARS = comb(12, 2)        # 66


def euro_main_prob(k: int) -> float:
    """P(exactly k mains hit out of 5) — random ticket, no constraints."""
    if k < 0 or k > 5:
        return 0.0
    return comb(5, k) * comb(45, 5 - k) / EURO_TOTAL_MAINS


def euro_star_prob(k: int) -> float:
    """P(exactly k stars hit out of 2)."""
    if k < 0 or k > 2:
        return 0.0
    return comb(2, k) * comb(10, 2 - k) / EURO_TOTAL_STARS


def euro_at_least_k_mains(k: int) -> float:
    return sum(euro_main_prob(i) for i in range(k, 6))


def euro_at_least_total(t: int) -> float:
    """P(mains + stars >= t) — combined prize-tier reality.
    `Money mode` cares about 3+ TOTAL (e.g. 2m+1s, 1m+2s, 3m+0s).
    """
    p = 0.0
    for m in range(6):
        for s in range(3):
            if m + s >= t:
                p += euro_main_prob(m) * euro_star_prob(s)
    return p


def euro_baseline() -> Dict[str, float]:
    """Per-ticket hit-rate baseline for Euro across the standard tiers."""
    return {
        # Mains-only tiers (Jackpot view)
        "p_2plus_mains":  euro_at_least_k_mains(2),
        "p_3plus_mains":  euro_at_least_k_mains(3),
        "p_4plus_mains":  euro_at_least_k_mains(4),
        "p_5_mains":      euro_main_prob(5),
        # Combined mains+stars tiers (Money view)
        "p_2plus_total":  euro_at_least_total(2),
        "p_3plus_total":  euro_at_least_total(3),
        "p_4plus_total":  euro_at_least_total(4),
        # Star-only sanity
        "p_1plus_stars":  euro_star_prob(1) + euro_star_prob(2),
        "p_2_stars":      euro_star_prob(2),
        # Convenience: per-100-tix expected count of >=k hitters
        "exp_per_100_2plus_mains": 100.0 * euro_at_least_k_mains(2),
        "exp_per_100_3plus_mains": 100.0 * euro_at_least_k_mains(3),
        "exp_per_100_4plus_mains": 100.0 * euro_at_least_k_mains(4),
    }


# ════════════════════════════════════════════════════════════════════
# SWISS 6/42 + lucky 1/6 + replay 1/35
# ════════════════════════════════════════════════════════════════════
SWISS_TOTAL_MAINS = comb(42, 6)       # 5_245_786


def swiss_main_prob(k: int) -> float:
    if k < 0 or k > 6:
        return 0.0
    return comb(6, k) * comb(36, 6 - k) / SWISS_TOTAL_MAINS


def swiss_at_least_k_mains(k: int) -> float:
    return sum(swiss_main_prob(i) for i in range(k, 7))


def swiss_lucky_prob() -> float:
    """P(🍀 lucky number hits) — 1 chosen out of 6."""
    return 1.0 / 6.0


def swiss_replay_prob() -> float:
    """P(replay number hits) — 1 chosen out of 35."""
    return 1.0 / 35.0


def swiss_at_least_total(t: int) -> float:
    """P(mains + lucky-flag >= t).
    Treats lucky-hit as a single "+1" point in the total — matches the
    `total_matches` field used in the hit tracker.
    """
    p = 0.0
    for m in range(7):
        for L in (0, 1):
            if m + L >= t:
                pL = swiss_lucky_prob() if L == 1 else (1 - swiss_lucky_prob())
                p += swiss_main_prob(m) * pL
    return p


def swiss_baseline() -> Dict[str, float]:
    """Per-ticket hit-rate baseline for Swiss across standard tiers."""
    return {
        # Mains-only tiers
        "p_2plus_mains":  swiss_at_least_k_mains(2),
        "p_3plus_mains":  swiss_at_least_k_mains(3),
        "p_4plus_mains":  swiss_at_least_k_mains(4),
        "p_5plus_mains":  swiss_at_least_k_mains(5),
        "p_6_mains":      swiss_main_prob(6),
        # Combined mains+lucky tiers
        "p_2plus_total":  swiss_at_least_total(2),
        "p_3plus_total":  swiss_at_least_total(3),
        "p_4plus_total":  swiss_at_least_total(4),
        # Lucky / Replay
        "p_lucky_hit":    swiss_lucky_prob(),
        "p_replay_hit":   swiss_replay_prob(),
        # Per-100-tix expectations
        "exp_per_100_2plus_mains": 100.0 * swiss_at_least_k_mains(2),
        "exp_per_100_3plus_mains": 100.0 * swiss_at_least_k_mains(3),
        "exp_per_100_4plus_mains": 100.0 * swiss_at_least_k_mains(4),
    }


# ════════════════════════════════════════════════════════════════════
# E ACTUAL VS RANDOM — comparison helpers
# ════════════════════════════════════════════════════════════════════
def compute_engine_rates_euro(tickets, hit_results) -> Dict[str, float]:
    """Given E's actual tickets + their hit_results for one draw,
    return the observed per-ticket rates.

    `hit_results[i]` shape (Euro): {hit_count, star_hit_count, ...}
    """
    n = max(1, len(hit_results))
    c2_main = c3_main = c4_main = c5_main = 0
    c2_total = c3_total = c4_total = 0
    c1_star = c2_star = 0
    for hr in hit_results:
        m = int(hr.get("hit_count", 0))
        s = int(hr.get("star_hit_count", 0))
        if m >= 2: c2_main += 1
        if m >= 3: c3_main += 1
        if m >= 4: c4_main += 1
        if m >= 5: c5_main += 1
        if m + s >= 2: c2_total += 1
        if m + s >= 3: c3_total += 1
        if m + s >= 4: c4_total += 1
        if s >= 1: c1_star += 1
        if s >= 2: c2_star += 1
    return {
        "n": len(hit_results),
        "p_2plus_mains":  c2_main / n,
        "p_3plus_mains":  c3_main / n,
        "p_4plus_mains":  c4_main / n,
        "p_5_mains":      c5_main / n,
        "p_2plus_total":  c2_total / n,
        "p_3plus_total":  c3_total / n,
        "p_4plus_total":  c4_total / n,
        "p_1plus_stars":  c1_star / n,
        "p_2_stars":      c2_star / n,
    }


def compute_engine_rates_swiss(tickets, hit_results) -> Dict[str, float]:
    """Given Swiss tickets + hit_results, return observed per-ticket rates.

    `hit_results[i]` shape (Swiss): {hit_count, lucky_hit, total_matches}
    """
    n = max(1, len(hit_results))
    c2_main = c3_main = c4_main = c5_main = c6_main = 0
    c2_total = c3_total = c4_total = 0
    c_lucky = 0
    for hr in hit_results:
        m = int(hr.get("hit_count", 0))
        L = int(bool(hr.get("lucky_hit", False)))
        total = int(hr.get("total_matches", m + L))
        if m >= 2: c2_main += 1
        if m >= 3: c3_main += 1
        if m >= 4: c4_main += 1
        if m >= 5: c5_main += 1
        if m >= 6: c6_main += 1
        if total >= 2: c2_total += 1
        if total >= 3: c3_total += 1
        if total >= 4: c4_total += 1
        if L: c_lucky += 1
    return {
        "n": len(hit_results),
        "p_2plus_mains":  c2_main / n,
        "p_3plus_mains":  c3_main / n,
        "p_4plus_mains":  c4_main / n,
        "p_5plus_mains":  c5_main / n,
        "p_6_mains":      c6_main / n,
        "p_2plus_total":  c2_total / n,
        "p_3plus_total":  c3_total / n,
        "p_4plus_total":  c4_total / n,
        "p_lucky_hit":    c_lucky / n,
    }
