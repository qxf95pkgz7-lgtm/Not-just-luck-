"""
🔐 RC-WALKS ENCRYPTION LENS — Session 43 + 44 (Euro + Swiss)
=============================================================
EURO (Session 43, 26.05.2026): 5-walk RC0 (24.03.2026) encryption.
SWISS (Session 44, 27.05.2026): 6-walk HUGE (07.02.2026) encryption,
   family-rare ghost-collapse, mod-42 wrap, Canons 21-29.

Canons coded:
   17  5-walk encryption (Euro)
   18  P3 walk-chain + reverse-wrap
   19  Q1 sum-echo + Q-loop closure
   20  Date-encryption signals
   21  6-walk from HUGE (Swiss)  [family-rare ghost collapse]
   22  mod-42 wrap RAW landing detector
   23  Time-cross identity (prev_P3 + cur_P2 = T - cur_P3)
   24  Ghost-as-P1+P2 post-closure rebirth signature
   25  P2-P1 digit signature (T + cur_P3 = "P2|P1"; single-digit front only)
        + the OPENING twin: carrier(HUGE-Pn) + k = "P1|P2"
   26  Silent carrier detection (n + 21 = anchor)
   27  R is NOT predictive (drop from scoring)
   28  Position-silent depth tracker (per-position 0-fires)
   29  Carrier-chord detection — find P-subset that sums to T / wrap / carrier
        (NEW DJ canon 27.05.2026 — "show me the ghost via the chord")
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
    if mode == "swiss":
        return compose_swiss_encryption_reading(
            target_date=target_date, huge=rc0,
            all_quarter_draws=all_quarter_draws,
            recent_draws=recent_draws,
            post_rc_draws=post_rc_draws,
        )
    if mode != "euro":
        return {"available": False, "reason": "encryption walks canon currently Euro/Swiss only"}
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


# ============================================================
# SWISS ENCRYPTION — Session 44 / Canons 21-29
# ============================================================
# HUGE 07.02.2026 [30, 33, 35, 36, 37, 38] 🍀6 R6 — the family-rare anchor.
# Family-rare collapse: all 6 anchors SHARE one ghost.
# DJ-canonical ghost = 7 (derived from P1-family ladder 11→13→30).
# Walk: T_a(k) = a + k. Wrap mod 42 when > 42 (Canon 22, RAW landing).
# ============================================================

SWISS_GHOST_DJ_CANONICAL = 7


def fit_family_ghost(
    anchors: List[int],
    training_draws: List[List[int]],
    carrier: int = SWISS_CARRIER,
    main_max: int = SWISS_MAX,
    candidate_range: Tuple[int, int] = (1, 41),
) -> Dict:
    """Family-rare collapse (Canon 21): ALL anchors share ONE ghost.
    Brute-search g; score = total hide-path fires summed across anchors.
    Returns DJ-canonical 7 if found in top-2 by fires (tie-break preference).
    """
    best = {"ghost": None, "fires": -1, "raws": 0}
    scoreboard = []
    for g in range(candidate_range[0], candidate_range[1] + 1):
        fires = 0
        raws = 0
        for anc in anchors:
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
                    if (p + anc == target or p - anc == target or
                        p + carrier == target or p - carrier == target or
                        p + g == target or p - g == target):
                        fires += 1
                        break
        scoreboard.append({"ghost": g, "fires": fires, "raws": raws})
        if (fires > best["fires"]) or (fires == best["fires"] and raws > best["raws"]):
            best = {"ghost": g, "fires": fires, "raws": raws,
                    "train_size": len(training_draws)}
    # DJ-canonical tie-break: if ghost=7 is within 10% of best, prefer 7
    if best["ghost"] != SWISS_GHOST_DJ_CANONICAL:
        dj_entry = next((s for s in scoreboard if s["ghost"] == SWISS_GHOST_DJ_CANONICAL), None)
        if dj_entry and best["fires"] > 0 and dj_entry["fires"] >= 0.85 * best["fires"]:
            return {
                "ghost": SWISS_GHOST_DJ_CANONICAL,
                "fires": dj_entry["fires"],
                "raws": dj_entry["raws"],
                "train_size": len(training_draws),
                "brute_best_ghost": best["ghost"],
                "brute_best_fires": best["fires"],
                "dj_canonical_used": True,
            }
    best["dj_canonical_used"] = False
    return best


def find_carrier_chord(
    draw_mains: List[int], lucky: Optional[int], target: int,
    carrier: int = SWISS_CARRIER, main_max: int = SWISS_MAX,
    max_size: int = 4,
) -> List[Dict]:
    """Canon 29 — CARRIER-CHORD DETECTION.

    Search subsets of {P1..P6, 🍀} (excluding R per Canon 27) for sums that
    equal target / target mod main_max (wrap) / wrap + carrier.

    Returns list of {kind, sum, group, group_names} for each chord hit.
    """
    nums = sorted(draw_mains)
    elements = []  # (label, value)
    for i, p in enumerate(nums, 1):
        elements.append((f"P{i}", p))
    if lucky is not None:
        elements.append(("🍀", lucky))

    # Targets: T raw, T mod max, (T mod max) + carrier
    wrap = ((target - 1) % main_max) + 1 if target > main_max else target
    targets = {target: "T_raw"}
    if wrap != target:
        targets[wrap] = "T_wrap"
    carrier_back = wrap + carrier
    if 1 <= carrier_back <= 2 * main_max:
        targets[carrier_back] = "T_carrier"

    from itertools import combinations
    hits = []
    for r in range(1, max_size + 1):
        for combo in combinations(elements, r):
            s = sum(v for _, v in combo)
            if s in targets:
                hits.append({
                    "kind": targets[s], "sum": s, "size": r,
                    "group_names": [lbl for lbl, _ in combo],
                    "group_values": [v for _, v in combo],
                })
    # Dedupe by (kind, sum, group_names tuple) and prefer smallest size first
    seen = set()
    uniq = []
    for h in sorted(hits, key=lambda x: (x["size"], x["sum"])):
        key = (h["kind"], h["sum"], tuple(h["group_names"]))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(h)
    return uniq


def detect_wrap_raw_cash(
    walks_targets: Dict[int, int], draw_mains: List[int],
    main_max: int = SWISS_MAX,
) -> List[Dict]:
    """Canon 22 — mod-42 WRAP RAW LANDING DETECTOR.
    walks_targets: {anchor: T(k)} computed for the current k.
    """
    nums = sorted(draw_mains)
    pos_map = {n: f"P{i}" for i, n in enumerate(nums, 1)}
    cashes = []
    for anc, t in walks_targets.items():
        if t > main_max:
            wrap = ((t - 1) % main_max) + 1
            if wrap in pos_map:
                cashes.append({
                    "anchor": anc, "T": t, "wrap": wrap,
                    "position": pos_map[wrap], "kind": "wrap_raw",
                })
        elif t in pos_map:
            cashes.append({
                "anchor": anc, "T": t, "wrap": t,
                "position": pos_map[t], "kind": "raw",
            })
    return cashes


def time_cross_identity(
    prev_draw_mains: List[int], cur_draw_mains: List[int],
    cur_k: int, anchor_for_p3: int,
    main_max: int = SWISS_MAX,
) -> Dict:
    """Canon 23 — TIME-CROSS IDENTITY:
        prev_P3 + cur_P2 = T(cur_k) - cur_P3
    where T(cur_k) = anchor_for_p3 + cur_k (wrapped mod main_max if > max).
    """
    if len(prev_draw_mains) < 3 or len(cur_draw_mains) < 3:
        return {"available": False}
    prev = sorted(prev_draw_mains)
    cur = sorted(cur_draw_mains)
    t = anchor_for_p3 + cur_k
    t_used = t  # NOTE: identity uses raw T (not wrapped) per DJ proof (k=19, T=54)
    lhs = prev[2] + cur[1]   # prev_P3 + cur_P2
    rhs = t_used - cur[2]    # T - cur_P3
    return {
        "available": True,
        "prev_P3": prev[2], "cur_P2": cur[1], "cur_P3": cur[2],
        "T": t_used, "anchor_for_p3": anchor_for_p3, "k": cur_k,
        "lhs": lhs, "rhs": rhs, "match": lhs == rhs,
    }


def post_closure_ghost_signature(
    closure_draw_mains: List[int], next_draw_mains: List[int],
    anchor: int, closure_k: int, ghost: int,
    main_max: int = SWISS_MAX,
) -> Dict:
    """Canon 24 — GHOST-AS-P1+P2 POST-CLOSURE.
    When closure_draw's last position == anchor RAW (Q-closure), the NEXT
    draw plays P1 + P2 = ghost.
    """
    if not closure_draw_mains or not next_draw_mains or len(next_draw_mains) < 2:
        return {"available": False}
    cmains = sorted(closure_draw_mains)
    nmains = sorted(next_draw_mains)
    closed = anchor in cmains  # anchor self-return RAW
    pair_sum = nmains[0] + nmains[1]
    return {
        "available": True,
        "anchor": anchor, "closure_k": closure_k, "ghost": ghost,
        "closure_anchor_returned_raw": closed,
        "next_P1": nmains[0], "next_P2": nmains[1],
        "P1_plus_P2": pair_sum,
        "ghost_match": closed and (pair_sum == ghost),
    }


def p2_p1_digit_signature(
    cur_draw_mains: List[int], T_value: int, cur_p3: int,
) -> Dict:
    """Canon 25 — P2-P1 DIGIT SIGNATURE.
    Requires P1, P2 ∈ 1..9 (single-digit front).
    Check T + cur_P3 reads as P2|P1 (tens=P2, units=P1) or P1|P2.
    """
    if len(cur_draw_mains) < 3:
        return {"available": False}
    cur = sorted(cur_draw_mains)
    p1, p2 = cur[0], cur[1]
    if not (1 <= p1 <= 9 and 1 <= p2 <= 9):
        return {"available": False, "reason": "front pair not single-digit"}
    expected = T_value + cur_p3
    p2p1 = p2 * 10 + p1
    p1p2 = p1 * 10 + p2
    return {
        "available": True,
        "T": T_value, "cur_P3": cur_p3, "sum": expected,
        "P1": p1, "P2": p2,
        "P2_P1_read": p2p1, "P1_P2_read": p1p2,
        "match_P2_P1": expected == p2p1,
        "match_P1_P2": expected == p1p2,
        "match_any": expected in (p2p1, p1p2),
    }


def opening_carrier_digit_signature(
    cur_draw_mains: List[int], anchor: int, k: int,
    carrier: int = SWISS_CARRIER,
) -> Dict:
    """Canon 25 OPENING TWIN (DJ's 27.05.2026 teaching):
        carrier_of(HUGE-Pn) + k = "P1|P2" (or "P2|P1")
    where carrier_of(anchor) = anchor - carrier (if > 0) or anchor + carrier.
    Validated: HUGE_P2=33, carrier=12, k=17 → 29 = P1|P2 of Q2d1 (2,9). ✓
    """
    if len(cur_draw_mains) < 2:
        return {"available": False}
    cur = sorted(cur_draw_mains)
    p1, p2 = cur[0], cur[1]
    carrier_of = anchor - carrier if anchor - carrier > 0 else anchor + carrier
    expected = carrier_of + k
    p1p2 = p1 * 10 + p2 if (1 <= p1 <= 9 and 1 <= p2 <= 9) else None
    p2p1 = p2 * 10 + p1 if (1 <= p1 <= 9 and 1 <= p2 <= 9) else None
    return {
        "available": True,
        "anchor": anchor, "carrier_of_anchor": carrier_of, "k": k,
        "sum": expected,
        "P1_P2_read": p1p2, "P2_P1_read": p2p1,
        "match_P1_P2": expected == p1p2,
        "match_P2_P1": expected == p2p1,
        "match_any": expected in (p1p2, p2p1),
    }


def silent_carriers(anchors: List[int], post_rc_draws: List[Dict],
                    carrier: int = SWISS_CARRIER, main_max: int = SWISS_MAX) -> List[Dict]:
    """Canon 26 — SILENT CARRIERS: for each anchor a, its carrier-twin
    c = a - carrier (Swiss back-door). Report carriers that are silent
    or rare across post-RC draws.
    """
    fired = Counter()
    p1_fires = Counter()
    for d in post_rc_draws:
        mains = sorted(d.get("p", []))
        for n in mains:
            fired[n] += 1
        if mains:
            p1_fires[mains[0]] += 1
    out = []
    for a in anchors:
        c = a - carrier
        if c < 1:
            c = a + carrier
            if c > main_max:
                continue
        out.append({
            "anchor": a, "carrier_twin": c,
            "carrier_fires_total": fired.get(c, 0),
            "carrier_fires_at_P1": p1_fires.get(c, 0),
            "is_silent_at_P1": p1_fires.get(c, 0) == 0,
        })
    return out


def position_silent_depth(post_rc_draws: List[Dict], main_max: int = SWISS_MAX,
                          positions: int = 6) -> Dict:
    """Canon 28 — POSITION-SILENT DEPTH TRACKER.
    For each position P1..P{positions}, list numbers with 0 fires in that
    position across the post-RC walk.
    """
    pos_fires: Dict[int, Counter] = {p: Counter() for p in range(1, positions + 1)}
    total = len(post_rc_draws)
    for d in post_rc_draws:
        mains = sorted(d.get("p", []))
        for i, n in enumerate(mains, 1):
            if i <= positions:
                pos_fires[i][n] += 1
    result = {}
    for p, c in pos_fires.items():
        silent_list = [n for n in range(1, main_max + 1) if c.get(n, 0) == 0]
        result[f"P{p}"] = {
            "silent": silent_list, "silent_count": len(silent_list),
            "total_draws": total,
        }
    return result


def compose_swiss_encryption_reading(
    target_date: str,
    huge: Dict,
    all_quarter_draws: List[Dict],
    recent_draws: List[Dict],
    post_rc_draws: Optional[List[Dict]] = None,
) -> Dict:
    """Master Swiss reading — implements Canons 21-29 on the HUGE walk.

    Args:
      huge: {"date": "07.02.2026", "mains": [30,33,35,36,37,38], "stars": [6]}
            (stars used loosely for Swiss 🍀)
    """
    if not huge or "mains" not in huge:
        return {"available": False, "reason": "no HUGE anchor for Swiss walk"}
    anchors = huge["mains"]
    if len(anchors) < 6:
        return {"available": False, "reason": "Swiss HUGE requires 6 mains"}

    try:
        target_dt = datetime.strptime(target_date, "%d.%m.%Y")
    except ValueError:
        return {"available": False, "reason": "bad date"}

    huge_dt = datetime.strptime(huge["date"], "%d.%m.%Y")
    if post_rc_draws is None:
        post_rc = [d for d in all_quarter_draws if d["dt"] > huge_dt and d["dt"] < target_dt]
    else:
        post_rc = [d for d in post_rc_draws if d["dt"] > huge_dt and d["dt"] < target_dt]
    post_rc.sort(key=lambda x: x["dt"])
    target_k = len(post_rc) + 1  # k for the target draw (d+k from HUGE)

    training = [d["p"] for d in post_rc[:18]]

    # Canon 21: family-rare ghost collapse (one ghost for all 6)
    family = fit_family_ghost(anchors, training) if training else {
        "ghost": SWISS_GHOST_DJ_CANONICAL, "fires": 0, "raws": 0,
        "dj_canonical_used": True, "train_size": 0,
    }
    ghost = family["ghost"]

    # Compute walks T_a(target_k) for each anchor
    walks_targets = {a: a + target_k for a in anchors}
    walks = {}
    for i, a in enumerate(anchors, 1):
        t = walks_targets[a]
        wrap = ((t - 1) % SWISS_MAX) + 1 if t > SWISS_MAX else t
        carrier_back = wrap + SWISS_CARRIER if wrap + SWISS_CARRIER <= SWISS_MAX else None
        walks[f"P{i}={a}"] = {
            "anchor": a, "T": t, "wrap": wrap,
            "carrier_back": carrier_back,
            "ghost": ghost,
        }

    # Canon 22 wrap-raw history (across post_rc draws)
    wrap_cash_history = []
    for idx, d in enumerate(post_rc):
        k = idx + 1
        targets_k = {a: a + k for a in anchors}
        cashes = detect_wrap_raw_cash(targets_k, d["p"])
        for c in cashes:
            wrap_cash_history.append({
                "date": d["date"], "k": k, **c,
            })

    # Canon 29: carrier-chord scan on LAST post-RC draw (most recent) — these
    # show the carrier-chord vocabulary the cosmos used just before target.
    chord_scan = []
    if post_rc:
        last_d = post_rc[-1]
        last_k = len(post_rc)
        for a in anchors:
            t = a + last_k
            chords = find_carrier_chord(
                last_d["p"], last_d.get("lucky") or last_d.get("luck"),
                t, max_size=4,
            )
            if chords:
                chord_scan.append({
                    "anchor": a, "k": last_k, "T": t,
                    "date": last_d["date"], "chords": chords[:4],
                })

    # Canon 23: time-cross identity between last two post-RC draws + projection
    time_cross = None
    if len(post_rc) >= 2:
        prev_d = post_rc[-2]
        cur_d = post_rc[-1]
        cur_k = len(post_rc)
        # Use P3-king anchor=35 by default for the identity
        anchor_p3 = anchors[2] if len(anchors) >= 3 else 35
        time_cross = time_cross_identity(
            prev_d["p"], cur_d["p"], cur_k, anchor_p3,
        )

    # Canon 24: post-closure ghost signature scan
    post_closure_events = []
    for i in range(len(post_rc) - 1):
        cur, nxt = post_rc[i], post_rc[i + 1]
        for a in anchors:
            k = i + 1
            if a + k == a + k:  # walk target raw
                # Closure means the walk-target landed RAW or anchor self-return
                if a in cur["p"]:
                    sig = post_closure_ghost_signature(
                        cur["p"], nxt["p"], a, k, ghost,
                    )
                    if sig.get("ghost_match"):
                        post_closure_events.append({
                            "closure_date": cur["date"],
                            "next_date": nxt["date"],
                            **sig,
                        })

    # Canon 25: P2-P1 digit signature scan on post-RC draws
    p2p1_signatures = []
    anchor_p3 = anchors[2] if len(anchors) >= 3 else 35
    for idx, d in enumerate(post_rc):
        k = idx + 1
        T = anchor_p3 + k
        cur = sorted(d["p"])
        if len(cur) >= 3:
            sig = p2_p1_digit_signature(cur, T, cur[2])
            if sig.get("available") and sig.get("match_any"):
                p2p1_signatures.append({
                    "date": d["date"], "k": k, "T": T, **sig,
                })

    # Canon 25 OPENING twin: scan all anchors as carrier-source
    opening_signatures = []
    for idx, d in enumerate(post_rc):
        k = idx + 1
        for a in anchors:
            sig = opening_carrier_digit_signature(d["p"], a, k)
            if sig.get("available") and sig.get("match_any"):
                opening_signatures.append({
                    "date": d["date"], "k": k, **sig,
                })

    # Canon 26: silent carriers
    sc = silent_carriers(anchors, post_rc)

    # Canon 28: position-silent depth
    pos_silent = position_silent_depth(post_rc, positions=6)

    # Date signals (reuse Euro fn)
    date_sig = date_encryption_signals(target_date)

    # Silent voices (range 1-42)
    silent = silent_voices(all_quarter_draws, main_max=SWISS_MAX)

    # Compose shout zone for target_k:
    # numbers that are (wrap of any walk) OR (carrier-back of any walk) OR
    # (P1-silent + carrier of an anchor) OR (in carrier-chord groups)
    shout_candidates: Dict[int, List[str]] = {}
    for a, info in walks.items():
        wrap = info["wrap"]
        if 1 <= wrap <= SWISS_MAX:
            shout_candidates.setdefault(wrap, []).append(f"wrap of {a}")
        cb = info["carrier_back"]
        if cb and 1 <= cb <= SWISS_MAX:
            shout_candidates.setdefault(cb, []).append(f"carrier-back of {a}")
    # carrier twins that are deep P1-silent
    for sc_entry in sc:
        if sc_entry["is_silent_at_P1"]:
            shout_candidates.setdefault(sc_entry["carrier_twin"], []).append(
                f"P1-silent carrier of anchor {sc_entry['anchor']}"
            )
    shout = [
        {"n": n, "weight": len(reasons), "reasons": reasons}
        for n, reasons in sorted(shout_candidates.items())
    ]
    shout.sort(key=lambda x: -x["weight"])

    return {
        "available": True,
        "mode": "swiss",
        "target_date": target_date,
        "huge": {
            "date": huge["date"], "mains": anchors,
            "lucky": huge.get("lucky") or (huge.get("stars") or [None])[0],
        },
        "target_k": target_k,
        "family_ghost": family,
        "walks": walks,
        "canon_22_wrap_cash_history": wrap_cash_history,
        "canon_23_time_cross": time_cross,
        "canon_24_post_closure_events": post_closure_events,
        "canon_25_p2p1_signatures": p2p1_signatures,
        "canon_25_opening_signatures": opening_signatures,
        "canon_26_silent_carriers": sc,
        "canon_28_position_silent": pos_silent,
        "canon_29_chord_scan_last_d": chord_scan,
        "date_signals": date_sig,
        "silent_voices_Q": silent,
        "shout_zone": shout[:12],
        "verdict_line": (
            f"Swiss d+{target_k} after HUGE {huge['date']}. "
            f"Family ghost={ghost} (DJ-canonical={family.get('dj_canonical_used')}). "
            f"{len(wrap_cash_history)} wrap-cashes in walk. "
            f"{len(p2p1_signatures)} Canon-25 firings. "
            f"R is DROPPED from scoring (Canon 27)."
        ),
    }
