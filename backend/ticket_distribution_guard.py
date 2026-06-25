"""
🪞 TICKET DISTRIBUTION GUARD — Canon 33 (DJ-taught 09.06.2026 PM)
==================================================================

Universal post-processing that enforces the DJ's cosmic-wave caps on
every ticket batch coming out of every generator:

  • P1 (lowest main) ∈ [1, 4]:    max 30%  of tickets
  • P3 (3rd lowest)  ∈ [1, 9]:    max 15%  of tickets
  • P3 (3rd lowest)  ∈ [11, 15]:  max 20%  of tickets

These are calibrated against the last 3 years of real Swiss + Euro
draws (DJ verified the cosmos honors these rates in the wild).

Whenever a batch exceeds a cap, the OFFENDING tickets are lifted by
the **One Law** (`mirror_canon.mirror_of` — Swiss +21, Euro +25).
The weakest tickets (lowest cosmic_score) are lifted first; the
strongest keep their natural shape.

Public API:
  enforce_distribution_caps(tickets, mode, mains_key="mains")
"""
from __future__ import annotations
from typing import List, Dict, Optional


# DJ caps — Canon 33
CAP_P1_LOW = 0.30  # P1 in [1..4] :   ≤ 30%
CAP_P3_LOW = 0.15  # P3 in [1..9] :   ≤ 15%
CAP_P3_MID = 0.20  # P3 in [11..15] : ≤ 20%

MAIN_MAX = {"swiss": 42, "euro": 50}


def _get_mains(ticket: Dict, mains_key: str) -> List[int]:
    raw = ticket.get(mains_key) or ticket.get("mains") or ticket.get("numbers") or []
    return [int(n) for n in raw]


def _set_mains(ticket: Dict, mains_key: str, new_mains: List[int]) -> None:
    new_mains = sorted(new_mains)
    ticket[mains_key] = new_mains
    # Mirror to the common alt key if present so downstream consumers stay coherent
    for alt in ("mains", "numbers"):
        if alt in ticket and alt != mains_key:
            ticket[alt] = new_mains


def _lift_one(mains: List[int], offender: int, mode: str, max_n: int) -> Optional[List[int]]:
    """Return new sorted mains with `offender` replaced by its One Law circle partner.
    If circle collides or wraps invalid, falls back to a +decade nudge.
    Returns None if no valid lift is possible.
    """
    try:
        from mirror_canon import mirror_of as _circle
    except Exception:
        return None
    cand = _circle(offender, mode)
    if 1 <= cand <= max_n and cand not in mains:
        new = [n for n in mains if n != offender] + [cand]
        return sorted(new)
    # Fallback: +10 nudge (decade shift) — preserves family band
    alt = offender + 10
    while alt in mains or alt > max_n:
        alt -= 1
        if alt <= offender:
            break
    if alt > offender and 1 <= alt <= max_n and alt not in mains:
        new = [n for n in mains if n != offender] + [alt]
        return sorted(new)
    return None


def _score_of(t: Dict) -> float:
    for k in ("cosmic_score", "score", "confidence"):
        if k in t and isinstance(t[k], (int, float)):
            return float(t[k])
    return 0.0


def _audit_band(tickets: List[Dict], mains_key: str,
                p_idx: int, lo: int, hi: int) -> List[int]:
    """Return indices of tickets whose P_{p_idx+1} is in [lo, hi]."""
    out = []
    for i, t in enumerate(tickets):
        ms = sorted(_get_mains(t, mains_key))
        if len(ms) > p_idx and lo <= ms[p_idx] <= hi:
            out.append(i)
    return out


def _annotate_lift(ticket: Dict, p_old: int, p_new: int, reason: str) -> None:
    lifts = ticket.setdefault("distribution_lifts", [])
    lifts.append(f"{p_old}→{p_new} ({reason})")


def enforce_distribution_caps(
    tickets: List[Dict],
    mode: str,
    mains_key: str = "mains",
) -> List[Dict]:
    """Apply the DJ's three cosmic-wave caps to a ticket batch (in-place).

    Operates as 3 sequential passes (P1<5, then P3<10, then P3∈[11-15]).
    Each pass identifies offenders, sorts by ascending cosmic_score, and
    lifts the weakest until the cap is met.

    Returns the mutated tickets list (for fluent chaining).
    """
    if not tickets:
        return tickets

    mode = mode.lower()
    if mode not in MAIN_MAX:
        return tickets
    max_n = MAIN_MAX[mode]
    n = len(tickets)
    if n == 0:
        return tickets

    passes = [
        ("P1<5",     0, 1, 4,  CAP_P1_LOW),
        ("P3<10",    2, 1, 9,  CAP_P3_LOW),
        ("P3∈11-15", 2, 11, 15, CAP_P3_MID),
    ]

    for label, p_idx, lo, hi, cap_frac in passes:
        cap_n = int(n * cap_frac)  # floor of N×cap (e.g., 10×0.15 = 1)
        # If cap is fractional and we have >0 offenders, at least allow 1.
        # 30% × 10 = 3.0 → cap_n=3. 15% × 10 = 1.5 → cap_n=1.
        # We want "no more than 15%" which means cap_n = floor.
        offender_idxs = _audit_band(tickets, mains_key, p_idx, lo, hi)
        if len(offender_idxs) <= cap_n:
            continue
        # Sort offenders by ascending cosmic_score (lift the weakest first)
        offender_idxs.sort(key=lambda i: _score_of(tickets[i]))
        to_lift = offender_idxs[: len(offender_idxs) - cap_n]
        for i in to_lift:
            t = tickets[i]
            # Iteratively lift until the ticket escapes this band (or max 3 attempts)
            for _attempt in range(3):
                ms = sorted(_get_mains(t, mains_key))
                if len(ms) <= p_idx or not (lo <= ms[p_idx] <= hi):
                    break  # already out of band
                p_old = ms[p_idx]
                new_ms = _lift_one(ms, p_old, mode, max_n)
                if new_ms is None:
                    break  # no valid lift
                _set_mains(t, mains_key, new_ms)
                _annotate_lift(
                    t, p_old,
                    new_ms[p_idx] if p_idx < len(new_ms) else new_ms[-1],
                    f"{label} cap (Canon 33)",
                )

    return tickets


def historical_distribution_audit(draws: List[Dict]) -> Dict:
    """Audit a list of historical draws against the same cap bands.
    Returns the % of draws that fall into each band (for verification UI).
    """
    p1_low = p3_low = p3_mid = 0
    valid = 0
    for d in draws:
        ms = sorted(d.get("numbers", []))
        if len(ms) < 3:
            continue
        valid += 1
        if 1 <= ms[0] <= 4:
            p1_low += 1
        if 1 <= ms[2] <= 9:
            p3_low += 1
        if 11 <= ms[2] <= 15:
            p3_mid += 1
    if valid == 0:
        return {"draws": 0}
    return {
        "draws": valid,
        "p1_lt_5_pct":      round(100 * p1_low / valid, 1),
        "p3_lt_10_pct":     round(100 * p3_low / valid, 1),
        "p3_in_11_15_pct":  round(100 * p3_mid / valid, 1),
        "caps": {"p1_lt_5": 30, "p3_lt_10": 15, "p3_in_11_15": 20},
    }
