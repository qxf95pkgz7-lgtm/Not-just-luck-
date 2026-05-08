"""
🎼 FREQUENCY CARRIER LENS — `cosmic_voices/frequency_carrier.py`
================================================================
DJ canon (Session 35, 07.05.2026 evening):

When a draw's P2 < 10, the front pair P1P2 concatenates cleanly. Combined
with P3 it can produce a COSMIC FREQUENCY (Solfeggio + 432-tuning + harmonic
ratios). 5-year scan validated 42 such hits across multiple formulas.

THE KEY DISCOVERIES:
  • 14.06.2022 [2,7,27,34,40] → 297 fires through 5 formulas (mega-carrier)
  • 01.05.2026 [3,9,42,46,47] → 432 fires through 3 formulas (recent)
  • After a freq-carrier BD, ND signature `3-1-1` DOUBLES (26% vs 13% base)
  • 432-BD → ND carries hungry-digits {2,3,4} 100% of the time (3/3)
  • Tesla 3-6-9: every cosmic freq reduces to digital-root 3, 6, or 9

This lens scans BD + recent draws and returns:
  • freq_hits: list of formula matches in the BD (and BD-1, BD-2)
  • hidden_digit_echo_targets: digits 1-9 likely to appear in target ND
  • tesla_root_projection: which root closes the recent chord (3,6,9)
  • signature_bias_post_freq: '3-1-1 cluster' alarm if BD fired any freq
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional


# Cosmic frequency table — Solfeggio + 432-tuning + harmonics
COSMIC_FREQUENCIES = {
    174: "solf-relief", 285: "solf-restore", 396: "solf-liberation",
    417: "solf-change", 432: "natural-A", 528: "solf-DNA", 540: "E♭",
    576: "432×4/3", 639: "solf-relations", 648: "432×3/2",
    741: "solf-expression", 852: "solf-intuition", 963: "solf-divine",
    864: "432×2", 234: "432-reverse", 216: "432/2", 144: "432/3",
    324: "432×3/4", 297: "reverse-792", 468: "234×2",
}


def _digital_root(n: int) -> int:
    """Reduce a positive integer to its digital root (Tesla 3-6-9 cycle)."""
    while n >= 10:
        n = sum(int(c) for c in str(n))
    return n


def _formula_derivatives(p: List[int]) -> List[Dict]:
    """For a draw with P2<10, compute every concat-derivative and check freq."""
    if len(p) < 3 or p[1] >= 10:
        return []
    p1, p2, p3 = p[0], p[1], p[2]
    p4 = p[3] if len(p) > 3 else 0
    p5 = p[4] if len(p) > 4 else 0
    c12 = int(f"{p1}{p2}")
    c21 = int(f"{p2}{p1}")
    forms = [
        (c12 + p3, "P1P2 + P3"),
        (c12 * 10 + p3, "P1P2×10 + P3"),
        (c12 * 10 + p4, "P1P2×10 + P4"),
        (c12 * 10 + p5, "P1P2×10 + P5"),
        (c12 * p3, "P1P2 × P3"),
        (c12 + p3 * 10, "P1P2 + P3×10"),
        (c21 * 10 + p3, "P2P1×10 + P3"),
        (c21 + p3 * 10, "P2P1 + P3×10"),
        (int(f"{p3}0") + c12, "P30 + P1P2"),
        (int(f"{p3}0") + c21, "P30 + P2P1"),
        (int(f"{p1}{p2}{p3}"), "P1P2P3"),
        (p1 * 100 + p2 * 10 + p3, "100·P1+10·P2+P3"),
    ]
    hits = []
    for v, name in forms:
        if v in COSMIC_FREQUENCIES:
            hits.append({
                "formula": name,
                "value": v,
                "name": COSMIC_FREQUENCIES[v],
                "digital_root": _digital_root(v),
            })
    return hits


def _hidden_digits_for_date(dt: datetime) -> List[int]:
    """Digits BETWEEN dd and mm (exclusive) — the date-envelope hidden trio."""
    lo, hi = sorted([dt.day, dt.month])
    return list(range(lo + 1, hi))


def frequency_carrier_scan(target_dt: datetime, recent_draws: List[Dict]) -> Dict:
    """Scan the last 3 draws for cosmic-frequency formula hits and produce
    target-ND projections.

    `recent_draws` should be chronologically ascending with 'p', 'date', 'dt'.
    """
    if not recent_draws:
        return {"available": False, "reason": "no recent draws"}

    # Look at last 3 draws (BD, BD-1, BD-2)
    window = recent_draws[-3:]
    scan = []
    all_hits: List[Dict] = []
    for d in window:
        hits = _formula_derivatives(d["p"])
        scan.append({
            "date": d["date"],
            "mains": d["p"],
            "p2_lt_10": len(d["p"]) >= 2 and d["p"][1] < 10,
            "hits": hits,
            "draw_sum": sum(d["p"]),
            "draw_root": _digital_root(sum(d["p"])),
        })
        for h in hits:
            all_hits.append({**h, "date": d["date"], "mains": d["p"]})

    bd = window[-1]
    bd_hits = scan[-1]["hits"] if scan else []
    bd_fires_freq = len(bd_hits) > 0

    # Hidden-digit echo targets (from BD's date envelope)
    bd_hidden = _hidden_digits_for_date(bd["dt"])

    # Tesla 3-6-9 chord — read recent roots, project closer
    recent_roots = [s["draw_root"] for s in scan]
    tesla_projection = None
    if len(recent_roots) >= 2 and recent_roots[-1] == recent_roots[-2]:
        # Two same roots in a row → cosmos wants 6 or 9 to close
        last = recent_roots[-1]
        if last == 3:
            tesla_projection = {
                "rule": "After two 3-roots, cosmos closes with 6 or 9 (Tesla 3-6-9)",
                "candidates_root": [6, 9],
                "recent_roots": recent_roots,
            }
        elif last == 6:
            tesla_projection = {
                "rule": "After two 6-roots, cosmos closes with 3 or 9",
                "candidates_root": [3, 9],
                "recent_roots": recent_roots,
            }
        elif last == 9:
            tesla_projection = {
                "rule": "After two 9-roots, cosmos closes with 3 or 6",
                "candidates_root": [3, 6],
                "recent_roots": recent_roots,
            }

    # Signature bias — if BD fired freq, 3-1-1 ND signature DOUBLES
    signature_bias = None
    if bd_fires_freq:
        signature_bias = {
            "alarm": "FREQ-BD fired → ND signature 3-1-1 weight DOUBLES (26% vs 13% base)",
            "preferred_signatures": ["3-1-1", "2-2-1"],
            "deboosted_signatures": ["2-1-1-1"],
        }

    # Echo strength — sum of formulas that fired across the window
    echo_strength = len(all_hits)
    multi_formula_carrier = None
    if scan and scan[-1].get("hits"):
        # Count distinct values in BD hits
        vals = Counter(h["value"] for h in scan[-1]["hits"])
        amplified = [v for v, c in vals.items() if c >= 2]
        if amplified:
            multi_formula_carrier = {
                "amplified_values": amplified,
                "warning": "Multi-formula amplification = MEGA cosmic carrier (rare).",
            }

    # Build candidate boost list — hidden-digit numbers from BD + Tesla closers
    main_boosts: Dict[int, List[str]] = {}
    for h in bd_hidden:
        # Each hidden digit (1-9) is itself a main candidate
        if 1 <= h <= 9:
            main_boosts.setdefault(h, []).append(f"hidden-digit-{h}")
        # Plus its decade-extensions (h+10, h+20, h+30, h+40)
        for offset in (10, 20, 30, 40):
            n = h + offset
            if 1 <= n <= 50:
                main_boosts.setdefault(n, []).append(f"hidden-digit-decade-{h}")

    return {
        "available": True,
        "scan_window": scan,
        "bd_fires_freq": bd_fires_freq,
        "bd_hits": bd_hits,
        "bd_hidden_digits": bd_hidden,
        "all_hits_in_window": all_hits,
        "echo_strength": echo_strength,
        "multi_formula_carrier": multi_formula_carrier,
        "tesla_projection": tesla_projection,
        "signature_bias": signature_bias,
        "main_boost_candidates": [
            {"n": n, "tags": tags} for n, tags in sorted(main_boosts.items())
        ],
        "rule": ("Frequency Carrier Lens — when P2<10, BD's P1P2/P3 concat "
                  "can resolve to a Solfeggio/432-tuning. After such a BD, "
                  "ND's hidden-digit carriers + Tesla 3-6-9 closer carry +1 "
                  "lens-fire each in convergence."),
    }
