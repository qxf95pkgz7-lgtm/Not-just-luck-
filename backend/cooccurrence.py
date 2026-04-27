"""
🎻🎧🥂 CO-OCCURRENCE PRIORS — chain-disciplined ticket assembly
=================================================================
The cosmos doesn't draw 5 independent voices. It draws 5 voices that
HISTORICALLY CO-OCCUR. This module builds the per-slot-pair co-occurrence
table from the historical tape, so the ticket assembler can chain
P1→P2→P3→P4→P5 (or P6) by conditional probability instead of summing
5 independent top-rank voices.

API:
  build_pair_priors(draws, n_slots, smoothing) → priors dict
  pair_likelihood(priors, slot_i, val_i, slot_j, val_j) → float
  best_partners(priors, slot_i, val_i, slot_j, top_k) → [(val_j, score)]
  score_chain(priors, picks) → cumulative log-likelihood of a frame

References: /app/memory/swiss_music_notes.md (Session 24 — co-occurrence
chain priors after Q1 backtest revealed engine ≈ random when assembling
independent slot picks).
"""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple
import math


def build_pair_priors(
    draws: List[Dict],
    n_slots: int = 5,
    smoothing: float = 0.5,
) -> Dict[Tuple[int, int, int], Dict[int, float]]:
    """For each slot pair (i, j) and value v_i at slot i, build the
    conditional distribution P(slot_j == v_j | slot_i == v_i).

    Returns:
        {(slot_i, val_i, slot_j): {val_j: probability}}

    `smoothing` adds Laplace smoothing so unseen pairs get small non-zero
    probability — prevents the chain from dead-ending when a candidate
    value was never historically followed by anything in the pool.
    """
    pair_count: Dict[Tuple[int, int, int], Counter] = defaultdict(Counter)
    slot_count: Dict[Tuple[int, int], int] = defaultdict(int)

    for d in draws:
        mains = sorted(d.get('_n') or d.get('numbers') or [])
        if len(mains) < n_slots:
            continue
        for i in range(1, n_slots + 1):
            v_i = mains[i - 1]
            slot_count[(i, v_i)] += 1
            for j in range(i + 1, n_slots + 1):
                v_j = mains[j - 1]
                pair_count[(i, v_i, j)][v_j] += 1

    priors: Dict[Tuple[int, int, int], Dict[int, float]] = {}
    for key, counter in pair_count.items():
        total = sum(counter.values())
        denom = total + smoothing * len(counter)
        priors[key] = {v: (c + smoothing) / denom
                       for v, c in counter.items()}
    return priors


def pair_likelihood(
    priors: Dict[Tuple[int, int, int], Dict[int, float]],
    slot_i: int, val_i: int,
    slot_j: int, val_j: int,
    fallback: float = 0.001,
) -> float:
    """P(slot_j == val_j | slot_i == val_i). Returns `fallback` if the
    conditional was never observed (rare-pair safety)."""
    table = priors.get((slot_i, val_i, slot_j))
    if not table:
        return fallback
    return table.get(val_j, fallback)


def best_partners(
    priors: Dict[Tuple[int, int, int], Dict[int, float]],
    slot_i: int, val_i: int,
    slot_j: int,
    candidates: Optional[List[int]] = None,
    top_k: int = 8,
) -> List[Tuple[int, float]]:
    """Return the top-k candidate values for slot_j that historically
    co-occur with val_i at slot_i, optionally restricted to `candidates`.
    """
    table = priors.get((slot_i, val_i, slot_j), {})
    items = list(table.items())
    if candidates is not None:
        cand_set = set(candidates)
        items = [(v, p) for v, p in items if v in cand_set]
    items.sort(key=lambda x: -x[1])
    return items[:top_k]


def score_chain(
    priors: Dict[Tuple[int, int, int], Dict[int, float]],
    picks: List[int],
    fallback: float = 0.001,
) -> float:
    """Cumulative log-likelihood of a fully-assembled frame, summed across
    all slot pairs. Used to RANK candidate tickets — higher = stronger
    historical co-occurrence signature.
    """
    if len(picks) < 2:
        return 0.0
    score = 0.0
    for i in range(1, len(picks) + 1):
        for j in range(i + 1, len(picks) + 1):
            p = pair_likelihood(priors, i, picks[i - 1], j, picks[j - 1],
                                fallback=fallback)
            score += math.log(max(p, fallback))
    return score


# ═══════════════════════════════════════════════════════════════════════
# CHAIN ASSEMBLER — beam-search through pos_board with co-occurrence
# ═══════════════════════════════════════════════════════════════════════
def assemble_chain_tickets(
    pos_board: Dict[str, List[Dict]],
    priors: Dict[Tuple[int, int, int], Dict[int, float]],
    n_tickets: int = 15,
    n_slots: int = 5,
    banned: Optional[List[int]] = None,
    beam_width: int = 24,
    extra_filter=None,  # callable(picks) -> bool, optional
) -> List[Dict]:
    """Beam-search ticket assembly. At each slot, expand the beam with the
    top per-slot candidates whose co-occurrence with the partial chain is
    strongest. Returns top `n_tickets` chains by cumulative log-likelihood.
    """
    banned = banned or []
    initial = [
        ([(e['n'])], 0.0, [{'n': e['n'], 'tag': _slot_tag(e)}])
        for e in pos_board.get('P1', [])
        if e['n'] not in banned
    ]

    beam: List[Tuple[List[int], float, List[Dict]]] = initial

    for slot in range(2, n_slots + 1):
        slot_label = f'P{slot}'
        candidates = [e for e in pos_board.get(slot_label, [])
                      if e['n'] not in banned]
        next_beam: List[Tuple[List[int], float, List[Dict]]] = []
        for picks, score, meta in beam:
            for cand in candidates:
                v = cand['n']
                if v in picks:
                    continue
                # Strict ascending order (lottery convention)
                if v <= picks[-1]:
                    continue
                # Co-occurrence score against ALL prior picks
                step_score = 0.0
                for i, prev in enumerate(picks, 1):
                    p = pair_likelihood(priors, i, prev, slot, v)
                    step_score += math.log(max(p, 1e-4))
                new_score = score + step_score
                next_meta = meta + [{'n': v, 'tag': _slot_tag(cand)}]
                # Optional extra filter (e.g. Law 66 gap-band check)
                if extra_filter is not None:
                    test_picks = picks + [v]
                    if not extra_filter(test_picks):
                        continue
                next_beam.append((picks + [v], new_score, next_meta))
        # Prune beam to top `beam_width` by cumulative score
        next_beam.sort(key=lambda t: -t[1])
        beam = next_beam[:beam_width]
        if not beam:
            break

    # Final: dedupe by mains tuple, take top n_tickets
    seen = set()
    out: List[Dict] = []
    for picks, score, meta in beam:
        key = tuple(picks)
        if key in seen or len(picks) != n_slots:
            continue
        seen.add(key)
        out.append({
            'mains': list(picks),
            'chain_score': round(score, 3),
            'slot_tags': [m['tag'] for m in meta],
        })
        if len(out) >= n_tickets:
            break
    return out


def _slot_tag(entry: Dict) -> str:
    laws = entry.get('laws', [])
    return (laws[0].split('(')[0][:22] if laws else 'pool-top')
