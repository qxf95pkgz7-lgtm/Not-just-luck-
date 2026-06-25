"""
🎻 GHOST CHORD ENGINE — `ghost_chord_engine.py`
================================================
Fuses ghost-debt + Swiss-circle(+21) + pair-lock + +10 KEY into a chord
projection: given the unpaid ghosts, what back-trio is the cosmos likely
to play to discharge them?

DJ canon (Session 33):
  • "If P1=2 then 23"  → swiss_circle(2) = 23 (back-closer of 2-debt)
  • "If P1=5 then 27"  → swiss_circle(6) = 27 (the 5-6 pair-lock)
  • The deepest unpaid ghost projects the strongest back-closer
  • Pair-lock: numbers travel in {a, a+10}, {a, swiss_circle(a)}, {a, mirror(a)}
"""
from __future__ import annotations

from typing import Dict, List

SWISS_MAINS_MAX = 42
EURO_MAINS_MAX = 50

# Mirror-axis (Swiss=21.5 between 1-42 → pair-sum 43; Euro=25.5 → pair-sum 51)
SWISS_PAIR_SUM = 43
EURO_PAIR_SUM = 51


def swiss_circle(n: int) -> int:
    """+21 mod 42 (Swiss circle). 1..42 → 22..21."""
    v = n + 21
    if v > 42:
        v -= 42
    return v


def euro_circle(n: int) -> int:
    """+25 mod 50 (Euro circle)."""
    v = n + 25
    if v > 50:
        v -= 50
    return v


def swiss_mirror(n: int) -> int:
    """🪞 ONE LAW (Canon 32): mirror = circle. Swiss n → n+21 wrap."""
    from mirror_canon import mirror_of as _mc_of
    return _mc_of(n, "swiss")


def euro_mirror(n: int) -> int:
    """🪞 ONE LAW (Canon 32): mirror = circle. Euro n → n+25 wrap."""
    from mirror_canon import mirror_of as _mc_of
    return _mc_of(n, "euro")


def project_back_closer(p1_candidate: int, mode: str) -> Dict:
    """Given a candidate next-P1 value, project back-closer suspects via:
      • circle(P1)
      • circle(P1 + 1)  (the pair-lock twin)
      • mirror(P1)
      • +10 KEY
    """
    if mode == "swiss":
        circ = swiss_circle
        mirr = swiss_mirror
        max_n = SWISS_MAINS_MAX
    else:
        circ = euro_circle
        mirr = euro_mirror
        max_n = EURO_MAINS_MAX

    candidates = []
    candidates.append({"n": circ(p1_candidate),
                       "source": f"circle({p1_candidate})"})
    if p1_candidate + 1 <= max_n:
        candidates.append({"n": circ(p1_candidate + 1),
                           "source": f"circle(pair-twin {p1_candidate}+1)"})
    candidates.append({"n": mirr(p1_candidate),
                       "source": f"mirror({p1_candidate})"})
    plus10 = p1_candidate + 10
    if 1 <= plus10 <= max_n:
        candidates.append({"n": plus10, "source": "+10 KEY"})

    # Dedupe preserving first source
    seen: Dict[int, Dict] = {}
    for c in candidates:
        if c["n"] not in seen:
            seen[c["n"]] = c
    return {
        "p1": p1_candidate,
        "back_closer_candidates": list(seen.values()),
    }


def build_ghost_chord(ghost_ledger: Dict, mode: str, top_p1: int = 5) -> Dict:
    """Take a ghost-ledger output and emit a full chord projection.

    Picks top N ghost P1 candidates (by score), projects back-closer for each,
    and aggregates the most-resonant numbers (those hit by multiple projections).
    """
    target_stream = ghost_ledger.get("target_stream", {})
    ghosts = target_stream.get("ghost_p1_ranked", [])[:top_p1]

    projections = []
    resonance: Dict[int, List[str]] = {}
    for g in ghosts:
        proj = project_back_closer(g["n"], mode)
        proj["ghost_score"] = g["score"]
        proj["ghost_age_d"] = g["age_d"]
        projections.append(proj)
        for c in proj["back_closer_candidates"]:
            resonance.setdefault(c["n"], []).append(
                f"{c['source']} from ghost-P1={g['n']} (age {g['age_d']})"
            )

    chord = sorted(
        [{"n": n, "weight": len(srcs), "sources": srcs} for n, srcs in resonance.items()],
        key=lambda x: (-x["weight"], x["n"]),
    )

    return {
        "mode": mode,
        "top_ghost_p1_candidates": [{"n": g["n"], "score": g["score"],
                                      "age_d": g["age_d"], "reason": g["reason"]}
                                     for g in ghosts],
        "back_closer_projections": projections,
        "chord_resonance_ranked": chord,
        "chord_top_3": chord[:3] if len(chord) >= 3 else chord,
    }
