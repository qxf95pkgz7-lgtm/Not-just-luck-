"""
🔐 RC-WALKS ENCRYPTION LENS — Session 43 (26.05.2026 LIVE)
==========================================================
DJ taught this canon LIVE during the Euro Q2 d+1..d+17 walk from RC0
(24.03.2026 Euro). E now learns to:

1. Anchor on the last RC0 (5 positions = 5 walks, Euro)
2. Brute-fit each position's GHOST against training d's (d+1..d+15)
3. For each target d, compute all 5 walk targets (target = ghost + step)
4. Find PRE-IMAGES (Px values 1-50) that satisfy hide-paths:
   • Px ± anchor = target  (anchor path, the clean door)
   • Px ± 25 = target      (Euro carrier mask)
   • Px ± ghost = target   (ghost-key path)
   • Px = target (raw landing)
5. MULTI-WALK CONVERGENCE — numbers satisfying 2+ walks = LOCK
6. Quintuple-lock detection (5 of 5 walks point to one n)
7. P3-chain walk (gap reading + reverse-wrap canon)
8. Date encryption signals (mirror dates, D+M, sums, digit decomp)
9. Silent voices of the quarter (deepest debt)
10. Q-meta-anchor (most-fired number across the Q = heartbeat)
11. L3D neighbor overlap (DJ's strict "neighbors" canon)
12. Sum-echo flag (current target sum matches earlier d sum)

Each insight is a SHOUT (3+ paths) / WHISPER (2 paths) / NOTE (1 path).
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import Counter

EURO_CARRIER = 25
EURO_MAX = 50
SWISS_CARRIER = 21
SWISS_MAX = 42


def _reverse_wrap(n: int, base: int = EURO_MAX) -> int:
    """Reverse digits, wrap modulo base into [1, base]."""
    rev = int(str(n)[::-1].lstrip("0") or "0")
    return ((rev - 1) % base) + 1 if rev else 0


def fit_best_ghost(
    anchor: int,
    training_draws: List[List[int]],
    carrier: int = EURO_CARRIER,
    main_max: int = EURO_MAX,
    candidate_range: Tuple[int, int] = (1, 49),
) -> Dict:
    """For an anchor value, brute-search ghost ∈ candidate_range and pick the
    one with the most hide-path fires across training_draws. Linear walk:
    target_at_step_i = ghost + i  (clamped to mod main_max).
    """
    best = {"ghost": None, "fires": -1, "raws": 0}
    for g in range(candidate_range[0], candidate_range[1] + 1):
        fires = 0
        raws = 0
        for i, draw in enumerate(training_draws):
            target = g + i
            if target > main_max:
                target = ((target - 1) % main_max) + 1
            nums = sorted(draw)
            if target in nums:
                fires += 1
                raws += 1
                continue
            for p in nums:
                if (p + anchor == target or p - anchor == target or
                    p + carrier == target or p - carrier == target or
                    p + g == target or p - g == target):
                    fires += 1
                    break
        if (fires > best["fires"]) or (fires == best["fires"] and raws > best["raws"]):
            best = {"ghost": g, "fires": fires, "raws": raws,
                    "train_size": len(training_draws)}
    return best


def find_preimages(
    target: int, anchor: int, ghost: int,
    carrier: int = EURO_CARRIER, main_max: int = EURO_MAX,
) -> List[int]:
    """Return n ∈ [1, main_max] such that n satisfies a hide-path for target."""
    preimg = set()
    if 1 <= target <= main_max:
        preimg.add(target)  # raw landing
    for n in range(1, main_max + 1):
        if (n + anchor == target or n - anchor == target or
            n + carrier == target or n - carrier == target or
            n + ghost == target or n - ghost == target):
            preimg.add(n)
    return sorted(preimg)


def multi_walk_convergence(
    walks: Dict[str, Dict], target_step: int,
    carrier: int = EURO_CARRIER, main_max: int = EURO_MAX,
) -> Dict:
    """Run all walks for target_step, gather per-number multi-walk hits."""
    per_walk_targets = {}
    n_walks_hit = {}
    for wname, w in walks.items():
        anc = w["anchor"]
        g = w["ghost"]
        t = g + target_step
        if t > main_max:
            t = ((t - 1) % main_max) + 1
        per_walk_targets[wname] = {"anchor": anc, "ghost": g, "target": t}
        preimg = find_preimages(t, anc, g, carrier, main_max)
        for n in preimg:
            n_walks_hit.setdefault(n, []).append(f"{wname}→{t}")
    # categorize
    quintuple = [n for n, hits in n_walks_hit.items() if len(hits) >= 5]
    quad = [n for n, hits in n_walks_hit.items() if len(hits) == 4]
    triple = [n for n, hits in n_walks_hit.items() if len(hits) == 3]
    double = [n for n, hits in n_walks_hit.items() if len(hits) == 2]
    return {
        "walks": per_walk_targets,
        "by_walk_count": {n: hits for n, hits in n_walks_hit.items()},
        "quintuple_lock": sorted(quintuple),
        "quad_lock": sorted(quad),
        "triple_lock": sorted(triple),
        "double_lock": sorted(double),
    }


def track_p3_chain(recent_draws: List[Dict], depth: int = 6) -> Dict:
    """Read the P3 trail of the last `depth` draws, with gaps + reverse-wraps."""
    chain = []
    last = sorted(recent_draws, key=lambda x: x["dt"])[-depth:]
    for d in last:
        nums = sorted(d["p"])
        if len(nums) >= 3:
            p3 = nums[2]
            chain.append({
                "date": d["date"], "p3": p3,
                "reverse_wrap": _reverse_wrap(p3),
                "digit_sum": sum(int(c) for c in str(p3)),
            })
    # compute gaps
    for i in range(1, len(chain)):
        chain[i]["gap_from_prev"] = chain[i]["p3"] - chain[i-1]["p3"]
    # cumulative
    cum = 0
    for c in chain[1:]:
        cum += c["gap_from_prev"]
        c["cum_gap"] = cum
    return {"chain": chain, "cumulative_net_gap": cum if chain else 0}


def predict_next_p3(p3_chain: Dict, rc0_p3: Optional[int],
                    inner_gap: Optional[int] = None) -> Dict:
    """Multi-angle next-P3 prediction.
    inner_gap = RC0_P5 - RC0_P4 (DJ's '9-gap closure' canon).
    """
    chain = p3_chain.get("chain") or []
    if not chain:
        return {"available": False}
    last = chain[-1]["p3"]
    candidates = {}
    # path 1: gap-closure (last - inner_gap)
    if inner_gap:
        n = last - inner_gap
        if 1 <= n <= 50:
            candidates.setdefault(n, []).append(f"last({last})−inner_gap({inner_gap})")
    # path 2: RC0-P3 return (loop closure)
    if rc0_p3 and 1 <= rc0_p3 <= 50:
        candidates.setdefault(rc0_p3, []).append(f"RC0-P3 anchor return ({rc0_p3})")
    # path 3: reverse-wrap chain (rev(last) + 1) — symbolic
    rw = _reverse_wrap(last)
    if 1 <= rw <= 50:
        candidates.setdefault(rw, []).append(f"reverse-wrap({last}) → {rw}")
    # path 4: cumulative-net-back-to-origin
    cum = p3_chain.get("cumulative_net_gap", 0)
    origin = chain[0]["p3"]
    # if cum returned to ~0 → next step expected to slightly overshoot or undershoot
    candidates.setdefault(origin, []).append(f"origin return ({origin}, cum={cum})")
    # path 5: small step ±1, ±6 (DJ's gap-6 + gap-13 grammar)
    for delta in (-9, -6, -1, 1, 6, 9, 13, -13):
        n = last + delta
        if 1 <= n <= 50 and delta:
            candidates.setdefault(n, []).append(f"step Δ={delta:+d}")
    # rank by number of paths
    ranked = sorted([(n, paths) for n, paths in candidates.items()],
                    key=lambda x: (-len(x[1]), abs(x[0] - last)))
    return {
        "last_p3": last, "rc0_p3": rc0_p3, "inner_gap": inner_gap,
        "cumulative_net_gap": cum,
        "candidates": [
            {"n": n, "paths": paths, "weight": len(paths)}
            for n, paths in ranked[:8]
        ],
        "top_pick": ranked[0][0] if ranked else None,
    }


def date_encryption_signals(target_date_str: str) -> Dict:
    """Decode the calendar voice: D, M, Y-suffix, mirrors, sums, digit-decomp."""
    try:
        dt = datetime.strptime(target_date_str, "%d.%m.%Y")
    except ValueError:
        return {"available": False}
    D = dt.day
    M = dt.month
    Y = dt.year
    Ys = Y % 100
    digits = [int(c) for c in target_date_str.replace(".", "")]
    sum_d = sum(digits)
    return {
        "D": D, "M": M, "Y": Y, "Y_suffix": Ys,
        "D_plus_M": D + M,
        "D_times_M_mod50": (D * M) if (D * M) <= 50 else ((D * M - 1) % 50) + 1,
        "digit_sum": sum_d,
        "digit_decomp": sorted(set(d for d in digits if d > 0)),
        "DM_mirror": D == M,             # 3-3, 5-5 — low-double front canon
        "DY_mirror": D == Ys,            # 26-Y26 — DOUBLE-26 mirror date
        "MY_mirror": M == Ys,            # rare
        "D_reverse_wrap": _reverse_wrap(D) if D >= 10 else None,
        "carrier_discharges_of_D": [
            v for v in (D + 25, D - 25, _reverse_wrap(D) if D >= 10 else None,
                        D + 18, D - 18)
            if v is not None and 1 <= v <= 50
        ],
    }


def silent_voices(quarter_draws: List[Dict], main_max: int = EURO_MAX) -> Dict:
    """Numbers never played raw across the quarter's draws so far."""
    played = set()
    for d in quarter_draws:
        played.update(d.get("p", []))
    silent = [n for n in range(1, main_max + 1) if n not in played]
    return {
        "silent_count": len(silent),
        "silent_list": silent,
        "played_count": main_max - len(silent),
    }


def q_meta_heartbeat(quarter_draws: List[Dict], top_k: int = 8) -> Dict:
    """Most-fired numbers in the quarter = the Q heartbeat candidates."""
    counter = Counter()
    for d in quarter_draws:
        counter.update(d.get("p", []))
    return {
        "top_by_freq": [{"n": n, "fires": c} for n, c in counter.most_common(top_k)],
    }


def l3d_overlap_pool(recent_draws: List[Dict]) -> Dict:
    """DJ canon: Last 3 Draws define 'neighbors'. Returns the L3D pool."""
    last3 = sorted(recent_draws, key=lambda x: x["dt"])[-3:]
    pool = set()
    for d in last3:
        pool.update(d.get("p", []))
    return {
        "l3d_pool": sorted(pool),
        "l3d_dates": [d["date"] for d in last3],
        "pool_size": len(pool),
    }


def sum_echo_check(quarter_draws: List[Dict], target_step: int) -> Dict:
    """If the predicted target-sum matches a prior d sum, flag echo-night."""
    sums = []
    for i, d in enumerate(quarter_draws):
        sums.append({"d": i + 1, "date": d["date"], "sum": sum(d.get("p", []))})
    return {"history": sums}


def compose_encryption_reading(
    target_date: str,
    mode: str,
    rc0: Dict,
    all_quarter_draws: List[Dict],
    recent_draws: List[Dict],
    post_rc_draws: Optional[List[Dict]] = None,
) -> Dict:
    """Master entry. Builds the full encryption prophecy for target_date.

    Args:
      all_quarter_draws: draws of target's quarter (used for silent/heartbeat).
      recent_draws:      last ~10 draws (used for L3D).
      post_rc_draws:     ALL draws strictly between RC0 and target (any quarter),
                         used for walk training + P3 chain. If None, falls back
                         to all_quarter_draws.
    """
    if mode != "euro":
        return {"available": False, "reason": "encryption walks canon currently Euro-only"}
    if not rc0 or "mains" not in rc0:
        return {"available": False, "reason": "no RC0 anchor in window"}

    rc_mains = rc0["mains"]
    rc_stars = rc0.get("stars") or []
    if len(rc_mains) < 5:
        return {"available": False, "reason": "RC0 mains < 5"}

    try:
        target_dt = datetime.strptime(target_date, "%d.%m.%Y")
    except ValueError:
        return {"available": False, "reason": "bad date"}

    rc_dt = datetime.strptime(rc0["date"], "%d.%m.%Y")
    # Prefer caller-supplied post_rc_draws (includes transition between quarters)
    if post_rc_draws is None:
        post_rc = [d for d in all_quarter_draws if d["dt"] > rc_dt and d["dt"] < target_dt]
    else:
        post_rc = [d for d in post_rc_draws if d["dt"] > rc_dt and d["dt"] < target_dt]
    post_rc.sort(key=lambda x: x["dt"])
    target_step = len(post_rc) + 1  # d+1 = step 1, target = step (post_rc+1)
    training = [d["p"] for d in post_rc[:15]]

    # Fit each position's ghost
    walks = {}
    for i, anc in enumerate(rc_mains[:5], 1):
        if not training:
            walks[f"P{i}={anc}"] = {"anchor": anc, "ghost": anc, "fires": 0, "raws": 0}
        else:
            best = fit_best_ghost(anc, training)
            walks[f"P{i}={anc}"] = {"anchor": anc, **best}

    # Convergence at target_step
    conv = multi_walk_convergence(walks, target_step - 1)

    # P3 chain
    p3_chain_data = track_p3_chain(post_rc, depth=6)
    inner_gap = rc_mains[4] - rc_mains[3] if len(rc_mains) >= 5 else None
    p3_pred = predict_next_p3(p3_chain_data, rc_mains[2] if len(rc_mains) >= 3 else None,
                              inner_gap=inner_gap)

    # Date signals
    date_sig = date_encryption_signals(target_date)

    # Silent + meta + L3D + sum-echo
    silent = silent_voices(all_quarter_draws)
    meta = q_meta_heartbeat(all_quarter_draws)
    l3d = l3d_overlap_pool(recent_draws)
    sum_h = sum_echo_check(all_quarter_draws, target_step)

    # Compose shout zone: numbers in (3+ walk) ∪ (silent ∩ date-sum) ∪ (l3d ∩ heartbeat)
    triple_plus = set(conv["quintuple_lock"]) | set(conv["quad_lock"]) | set(conv["triple_lock"])
    silent_set = set(silent["silent_list"])
    l3d_set = set(l3d["l3d_pool"])
    heartbeat = {x["n"] for x in meta["top_by_freq"][:5]}

    shout = []
    for n in sorted(triple_plus):
        reasons = []
        walk_count = len(conv["by_walk_count"].get(n, []))
        reasons.append(f"{walk_count}-walk lock")
        if n in silent_set:
            reasons.append("silent-all-Q")
        if n == date_sig.get("digit_sum"):
            reasons.append("date-sum match")
        if n in l3d_set:
            reasons.append("L3D neighbor")
        if n in heartbeat:
            reasons.append("Q-heartbeat")
        shout.append({"n": n, "weight": len(reasons), "reasons": reasons})
    shout.sort(key=lambda x: -x["weight"])

    return {
        "available": True,
        "target_date": target_date,
        "rc0": {
            "date": rc0["date"], "mains": rc_mains, "stars": rc_stars,
            "inner_gap_P5_P4": inner_gap,
        },
        "target_step": target_step,
        "walks": walks,
        "convergence": conv,
        "p3_walk": {**p3_chain_data, "prediction": p3_pred},
        "date_signals": date_sig,
        "silent_voices": silent,
        "q_heartbeat": meta,
        "l3d_neighbors": l3d,
        "sum_history": sum_h,
        "shout_zone": shout[:12],
        "verdict_line": (
            f"d+{target_step} after RC0 {rc0['date']}. "
            f"{len(conv['quintuple_lock'])} quintuple, "
            f"{len(conv['quad_lock'])} quad, {len(conv['triple_lock'])} triple locks. "
            f"P3-pred {p3_pred.get('top_pick')}. "
            f"Date signals D={date_sig.get('D')}, sum={date_sig.get('digit_sum')}."
        ),
    }
