"""
🔗 INTERNAL CHAIN DETECTOR — chainless = cash-window
====================================================
S38 canon: a draw has an INTERNAL CHAIN if it contains any 3-position equation:
  • Pa + Pb = Pc  (sum chain)
  • Pb − Pa = Pc  (diff chain)

Draws with NO internal chain are CASH-WINDOWS — that's where deep ghosts
pay raw (validated on Q1 HUGE 07.02.2026 + Q2d10).
"""
from __future__ import annotations
from itertools import combinations
from typing import Dict, List, Tuple


def scan_internal_chains(draw: Dict) -> List[Dict]:
    """Return all internal chains in a single draw."""
    p = draw.get("p") or []
    in_p = set(p)
    chains: List[Dict] = []
    for i, j in combinations(range(len(p)), 2):
        a, b = p[i], p[j]
        # sum chain: a + b in draw
        s = a + b
        if s in in_p:
            chains.append({"type": "sum", "eq": f"P{i+1}+P{j+1}=P?", "src": [a, b], "result": s})
        # diff chain
        d = b - a
        if d in in_p and d != a and d != b:
            chains.append({"type": "diff", "eq": f"P{j+1}-P{i+1}=P?", "src": [a, b], "result": d})
    return chains


def detect_chainless_windows(draws: List[Dict]) -> List[Dict]:
    """Per draw, classify as chainless (cash-window) or chain-bound."""
    out: List[Dict] = []
    for d in draws:
        chains = scan_internal_chains(d)
        out.append({
            "date": d.get("date"),
            "p": d.get("p"),
            "chain_count": len(chains),
            "chains": chains,
            "is_cash_window": len(chains) == 0,
        })
    return out
