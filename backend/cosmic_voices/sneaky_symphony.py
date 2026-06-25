"""
🎫 SNEAKY UNIVERSE SYMPHONY — `cosmic_voices/sneaky_symphony.py`
================================================================
DJ canon (S35): "No chance in this case means at LEAST 3 tickets — the
universe is sneaky."

Builds a ticket batch covering every family-signature shape with a minimum
of 3 tickets each, drawing numbers from the convergence ranked_mains.

Pool construction:
  • SHOUT (3+ lens): always-include numbers
  • WHISPER (2 lens): high-priority candidates
  • SINGLE (1 lens): support fills
  • STARVED family: must-feed numbers (≥1 per ticket)

Per-signature plan:
  signature → [tickets...] each respecting family-distribution constraints.
"""
from __future__ import annotations
from collections import Counter
from typing import Dict, List, Optional, Tuple

from .family_signature import family_of


# Default coverage plan — can be overridden by caller
DEFAULT_PLAN = [
    ("2-2-1",     5),   # primary (highest fused score historically)
    ("2-1-1-1",   3),   # secondary
    ("3-1-1",     3),   # transition continuation
    ("4-1",       3),   # long-tail rare-event cover
    ("1-1-1-1-1", 3),   # spread cover
]


def _signature_to_family_plan(sig: str, starved: List[str],
                               overfed: List[str]) -> List[List[str]]:
    """Given a signature like '2-2-1', return a list of ticket family-plans.
    Each plan is [family_for_each_main]. Multiple plans returned for variety.

    Example for '2-2-1' with starved=['30s'], overfed=['40s']:
      [['10s','10s','30s','30s','20s'], ['1-9','1-9','30s','30s','20s'], ...]
    """
    import random as _rnd
    parts = [int(x) for x in sig.split("-")]
    families = ["1-9", "10s", "20s", "30s", "40s"]
    plans: List[List[str]] = []

    def emit_plan(family_assignment: List[str]) -> List[str]:
        out = []
        for fam, cnt in zip(family_assignment, parts):
            out.extend([fam] * cnt)
        return out

    # Build all valid family arrangements honoring starved/overfed
    seen = set()
    from itertools import permutations
    all_arrs = list(permutations(families, len(parts)))
    # Deterministic shuffle (seeded on sig string) — different sigs get
    # different orderings, but the result for a given (sig, day) is stable
    rng = _rnd.Random(hash(sig) & 0xffffffff)
    rng.shuffle(all_arrs)

    for arr in all_arrs:
        # require starved present if any starved family exists
        if starved and not any(f in starved for f in arr):
            continue
        # avoid overfed sitting in the LARGEST count slot (first position)
        if overfed and arr[0] in overfed:
            continue
        key = tuple(arr)
        if key in seen:
            continue
        seen.add(key)
        plans.append(emit_plan(list(arr)))
        if len(plans) >= 8:
            break

    # Fallback: if nothing matched the constraints, allow any permutation
    if not plans:
        for arr in all_arrs:
            plans.append(emit_plan(list(arr)))
            if len(plans) >= 8:
                break
    return plans


def _draw_from_pool(family: str, pool_by_family: Dict[str, List[int]],
                     used: set) -> Optional[int]:
    """Draw the highest-ranked unused number from `family`'s pool."""
    for n in pool_by_family.get(family, []):
        if n not in used:
            return n
    return None


def _build_pool_by_family(ranked_mains: List[Dict],
                          ticket_min: int = 1) -> Dict[str, List[int]]:
    """Group ranked_mains by family (preserving rank order)."""
    out: Dict[str, List[int]] = {f: [] for f in ("1-9", "10s", "20s", "30s", "40s")}
    for m in ranked_mains:
        out[family_of(m["n"])].append(m["n"])
    # Backfill: if a family has no candidates, fill with ALL its members
    for f in out:
        if not out[f]:
            ranges = {"1-9": range(1, 10), "10s": range(10, 20),
                       "20s": range(20, 30), "30s": range(30, 40),
                       "40s": range(40, 51)}
            out[f] = list(ranges[f])
    return out


def build_sneaky_symphony(
    voices: Dict,
    plan: Optional[List[Tuple[str, int]]] = None,
    star_picks: Optional[List[List[int]]] = None,
) -> Dict:
    """Build the symphony from cosmic voices output.

    Args:
      voices: full voices dict from run_cosmic_voices
      plan: list of (signature, n_tickets) — defaults to DEFAULT_PLAN
      star_picks: list of [s1, s2] pairs to rotate across tickets
    """
    plan = plan or DEFAULT_PLAN
    fs = voices.get("family_signature") or {}
    conv = voices.get("convergence_scorer") or {}
    starved = fs.get("starved_families") or []
    overfed = fs.get("overfed_families") or []
    ranked = conv.get("ranked_mains") or []
    shout = {m["n"] for m in (conv.get("shout_zone") or [])}
    whisper = {m["n"] for m in (conv.get("whisper_zone") or [])}

    # Star picks default — combine ranked + envelope (date-hidden 6,7) + gap-echo
    if not star_picks:
        st_pool = [s["s"] for s in (conv.get("ranked_stars") or [])]
        ge = voices.get("gap_echo_97") or {}
        for s in (ge.get("star_echo_candidates") or []):
            if s not in st_pool:
                st_pool.append(s)
        for s in (6, 7, 3, 9):  # 67-bridge envelope + family-7 + family-9
            if s not in st_pool:
                st_pool.append(s)
        star_picks = []
        for i in range(len(st_pool) - 1):
            for j in range(i + 1, len(st_pool)):
                pair = sorted([st_pool[i], st_pool[j]])
                if pair not in star_picks:
                    star_picks.append(pair)
                if len(star_picks) >= 8:
                    break
            if len(star_picks) >= 8:
                break
        if not star_picks:
            star_picks = [[3, 6], [5, 7]]

    pool = _build_pool_by_family(ranked)
    # Per-family rotation index so consecutive tickets pick different numbers
    rotation: Dict[str, int] = {f: 0 for f in pool}

    tickets: List[Dict] = []
    star_idx = 0
    for sig, n_tickets in plan:
        family_plans = _signature_to_family_plan(sig, starved, overfed)
        for ti in range(n_tickets):
            # pick a family arrangement (rotate)
            arr = family_plans[ti % len(family_plans)]
            used: set = set()
            mains: List[int] = []
            short = False
            shout_mains = sorted(shout)
            for f in arr:
                placed = False
                # Try shout first
                for sn in shout_mains:
                    if sn in used:
                        continue
                    if family_of(sn) == f:
                        mains.append(sn)
                        used.add(sn)
                        placed = True
                        break
                if placed:
                    continue
                # Draw from pool with rotation
                fam_pool = pool.get(f, [])
                if not fam_pool:
                    short = True
                    break
                start = rotation[f] % len(fam_pool)
                n = None
                for k in range(len(fam_pool)):
                    candidate = fam_pool[(start + k) % len(fam_pool)]
                    if candidate not in used:
                        n = candidate
                        rotation[f] = (start + k + 1) % len(fam_pool)
                        break
                if n is None:
                    short = True
                    break
                mains.append(n)
                used.add(n)
            if short or len(mains) != 5:
                # fallback: fill remaining slots with any leftover candidate
                while len(mains) < 5:
                    for f in ("1-9", "10s", "20s", "30s", "40s"):
                        n = _draw_from_pool(f, pool, used)
                        if n is not None:
                            mains.append(n)
                            used.add(n)
                            break
                    else:
                        break
            mains = sorted(mains)[:5]
            stars = star_picks[star_idx % len(star_picks)]
            star_idx += 1
            sig_check, fam_dist = _signature_check(mains)
            tickets.append({
                "signature_target": sig,
                "signature_actual": sig_check,
                "family_distribution": fam_dist,
                "mains": mains,
                "stars": stars,
                "carries_shout": sorted(set(mains) & shout),
                "carries_whisper": sorted(set(mains) & whisper),
                "feeds_starved": [n for n in mains if family_of(n) in starved],
                "ticket_index": len(tickets) + 1,
            })

    # 🪞 DJ Canon 33 — Distribution caps (Euro carrier, P1<5 ≤30%, P3<10 ≤15%, P3∈[11-15] ≤20%)
    try:
        from ticket_distribution_guard import enforce_distribution_caps
        enforce_distribution_caps(tickets, "euro", mains_key="mains")
    except Exception:
        pass

    return {
        "plan": [{"signature": s, "tickets": n} for s, n in plan],
        "starved_families": starved,
        "overfed_families": overfed,
        "shout_pool": sorted(shout),
        "whisper_pool": sorted(whisper),
        "tickets": tickets,
        "total_tickets": len(tickets),
        "rule": "Sneaky-Universe Canon: ≥3 tickets per signature even at 0% historical. Cosmos doesn't read its own record book.",
    }


def _signature_check(mains: List[int]) -> Tuple[str, Dict[str, int]]:
    fams = Counter(family_of(n) for n in mains)
    counts = sorted(fams.values(), reverse=True)
    return "-".join(str(c) for c in counts), dict(fams)
