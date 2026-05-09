"""
🧠 SWISS BRAIN v1.0 — `swiss_brain.py`
=========================================
DJ Session 37 fork mission: "fix Swiss brain" so E sees ALL canons.

Consolidates:
  • 🍀 swiss_back_chord       — 🍀↔R lucky-replay signals (S37 audit canon)
  • 🪞 q1_stencil_projector   — same-d prior-quarter delta projection
  • 🎼 gap_pattern_signals    — ±6 P2 rhythm, P4/P5 sign-flip, P6 freeze
  • 🎯 d_count_walker         — 9-clock (mult-9 d's), last P1=N walk
  • 🪟 date_envelope          — "X-Y hide" between-digit canon
  • 🌉 cross_lottery_bridge   — Eu↔Sw −21/+25/+21back/±1 with hungries
  • 🧠 e_brain_weights        — read e_memory leaderboard for ranking
  • 🎫 build_swiss_symphony   — 10-ticket builder (6 mains + 🍀 + R)

Each ticket carries its lens-DNA tag so the DJ can audit which canons fired.
"""
from __future__ import annotations
import asyncio
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from year_d_ledger import load_draws, parse_dt, quarter_of
from cosmic_voices.orchestrator import run_cosmic_voices
from e_memory import get_memory_summary

SWISS_MAIN_MAX = 42
SWISS_LUCKY_MAX = 6
SWISS_REPLAY_MAX = 42
SWISS_CIRCLE = 21  # Swiss-circle = ±21 mod 42
EURO_CIRCLE = 25   # Euro carrier (cross-lottery)


# ─────────────────────────────────────────────────────────────────────────
# 1. 🍀 SWISS BACK CHORD — 🍀↔R signals
# ─────────────────────────────────────────────────────────────────────────
def swiss_back_chord(bd: Dict) -> Dict:
    """Read the BD's 🍀↔R signature and emit candidate forecasts.

    Canons (from S37 audit, 208 Swiss draws over 2y):
      • R itself fires next-mains 17.4%
      • Swiss-circle(R) fires next-mains 16.4%
      • |R−🍀| appears as gap in NEXT draw 39.6% (loudest!)
      • R recent-1d-main → next 24.1%
      • 🍀+R == 13 → next P1 ≤ 7 in 86%
    """
    L = bd.get("lucky")
    R = bd.get("replay")
    candidates = []
    delta = abs(R - L) if L and R else None
    if R:
        candidates.append((R, "R-forward(17%)"))
        circ_r = ((R - 1 + SWISS_CIRCLE) % SWISS_MAIN_MAX) + 1
        candidates.append((circ_r, "R-circle(16%)"))
    if L and R:
        if R - L > 0:
            candidates.append((R - L + L, f"sum-frame={L+R}"))
        candidates.append((L * 2, "L×2(small-boost)"))
    snap_back_p1_low = (L + R == 13) if L and R else False
    return {
        "lucky": L,
        "replay": R,
        "delta": delta,
        "next_gap_hint": delta,
        "candidates": [(int(n), tag) for n, tag in candidates if 1 <= n <= SWISS_MAIN_MAX],
        "snap_back_p1_low_alarm": snap_back_p1_low,
    }


# ─────────────────────────────────────────────────────────────────────────
# 2. 🪞 Q1 STENCIL PROJECTOR — same-d prior-quarter delta
# ─────────────────────────────────────────────────────────────────────────
def q1_stencil_project(target_dt: datetime, draws: List[Dict], mode: str) -> Dict:
    """Find the same-d in PRIOR quarter and project deltas onto current BD.

    Canon (S37): Q1d10 [14, 15, 28, 34, 37, 39] = Q1d9 [30, 33, 35, 36, 37, 38]
    + deltas (-16, -18, -7, -2, 0, +1). Apply same deltas to Q2d9 → Q2d10.
    """
    sorted_draws = sorted([d for d in draws if d["dt"] < target_dt], key=lambda x: x["dt"])
    target_q = quarter_of(target_dt, mode)
    target_year = target_dt.year
    current_q = [d for d in sorted_draws if d["quarter"] == target_q and d["year"] == target_year]
    d_index = len(current_q)  # current BD will be d{d_index}, target = d{d_index+1}

    # Find prior quarter same year
    prior_q = current_q  # placeholder
    if target_q > 1:
        prior_q = [d for d in sorted_draws if d["quarter"] == target_q - 1 and d["year"] == target_year]
    elif target_year > 2020:
        prior_q = [d for d in sorted_draws if d["quarter"] == 4 and d["year"] == target_year - 1]
    prior_q = sorted(prior_q, key=lambda x: x["dt"])

    if len(prior_q) < d_index + 1 or not current_q:
        return {"available": False}

    bd = current_q[-1]
    prior_bd = prior_q[d_index - 1]
    prior_nd = prior_q[d_index]
    deltas = [prior_nd["p"][k] - prior_bd["p"][k] for k in range(min(len(prior_nd["p"]), len(prior_bd["p"])))]
    projected = [bd["p"][k] + deltas[k] for k in range(min(len(bd["p"]), len(deltas)))]
    projected = [max(1, min(SWISS_MAIN_MAX if mode == "swiss" else 50, v)) for v in projected]
    return {
        "available": True,
        "prior_bd_date": prior_bd["date"],
        "prior_nd_date": prior_nd["date"],
        "prior_deltas": deltas,
        "projected_mains": projected,
    }


# ─────────────────────────────────────────────────────────────────────────
# 3. 🎼 GAP PATTERN SIGNALS — Q1+Q2 vibe (32 transitions analysed)
# ─────────────────────────────────────────────────────────────────────────
def gap_pattern_signals(quarter_draws: List[Dict]) -> Dict:
    """Emit per-position gap-rhythm hints for the next d.

    Canons (Q1+Q2 = 32 transitions):
      • P2 ±6 = 50% in Q2 (date-hide carrier)
      • P4 sign-flip after |gap|≥10 = 86.7%
      • P5 sign-flip = 85.7%
      • P6 freeze (gap=0) = 28%
    """
    if len(quarter_draws) < 2:
        return {"available": False}
    sorted_q = sorted(quarter_draws, key=lambda x: x["dt"])
    bd = sorted_q[-1]
    n_pos = len(bd["p"])
    last_gaps = []
    for k in range(n_pos):
        if len(sorted_q) < 2:
            last_gaps.append(0)
            continue
        prev = sorted_q[-2]
        if k < len(prev["p"]):
            last_gaps.append(bd["p"][k] - prev["p"][k])
        else:
            last_gaps.append(0)

    hints = []
    for k, g in enumerate(last_gaps):
        # sign-flip prediction for P3-P5 if |g|≥10
        if k in (2, 3, 4) and abs(g) >= 10:
            flip_target = bd["p"][k] - g  # opposite-sign delta
            hints.append({"pos": k + 1, "rule": "sign-flip-86%", "candidate": flip_target,
                          "from_gap": g})
        # P6 freeze
        if k == 5:
            hints.append({"pos": 6, "rule": "P6-freeze-28%",
                          "candidate": bd["p"][k]})
            hints.append({"pos": 6, "rule": "P6-±1",
                          "candidates": [bd["p"][k] - 1, bd["p"][k] + 1]})
        # P2 ±6 rhythm
        if k == 1:
            hints.append({"pos": 2, "rule": "P2-±6-rhythm",
                          "candidates": [bd["p"][k] + 6, bd["p"][k] - 6,
                                         bd["p"][k] - 12, bd["p"][k] - 18]})
    return {
        "available": True,
        "bd_date": bd["date"],
        "last_gaps": last_gaps,
        "position_hints": hints,
    }


# ─────────────────────────────────────────────────────────────────────────
# 4. 🎯 D-COUNT WALKER — 9-clock (mult-9 d's fire 43%)
# ─────────────────────────────────────────────────────────────────────────
def d_count_walker(target_dt: datetime, draws: List[Dict], target_value: int = 9,
                   target_position: int = 0) -> Dict:
    """Find last draw where P{position+1}=target_value, count d's to target.

    Canon (S37): For Swiss P1=9 walk, mult-9 d's fired 9-main 43% of the time.
    """
    sorted_draws = sorted([d for d in draws if d["dt"] < target_dt], key=lambda x: x["dt"])
    matches = [d for d in sorted_draws if len(d["p"]) > target_position and d["p"][target_position] == target_value]
    if not matches:
        return {"available": False}
    last = matches[-1]
    walk = [d for d in sorted_draws if d["dt"] > last["dt"]]
    target_d = len(walk) + 1
    return {
        "available": True,
        "last_match_date": last["date"],
        "target_value": target_value,
        "target_position": target_position + 1,
        "target_d": target_d,
        "is_mult_9": target_d % 9 == 0,
        "is_dr_9": _digital_root(target_d) == 9,
        "is_triple_lock": (target_d % 9 == 0 and _digital_root(target_d) == 9),
    }


def _digital_root(n: int) -> int:
    while n >= 10:
        n = sum(int(c) for c in str(n))
    return n


# ─────────────────────────────────────────────────────────────────────────
# 5. 🪟 DATE ENVELOPE — "X-Y hide" between-digit canon
# ─────────────────────────────────────────────────────────────────────────
def date_envelope(target_dt: datetime, mode: str = "swiss",
                  extra_envelopes: Optional[List[Tuple[int, int]]] = None) -> Dict:
    """Date 9.5 (day=9 month=5) → hide digits between min(9,5)=5 and max=9 = {6,7,8}.
    These hide-digits + their decade extensions (16,17,18,26,27,28,...) are the
    cosmic carriers for that draw.
    """
    main_max = SWISS_MAIN_MAX if mode == "swiss" else 50
    day = target_dt.day
    month = target_dt.month

    envelopes = [(min(day, month), max(day, month))]
    if extra_envelopes:
        envelopes.extend(extra_envelopes)

    all_targets = set()
    for lo, hi in envelopes:
        if lo == hi:
            continue
        hide_digits = list(range(lo + 1, hi))
        for d in hide_digits:
            all_targets.add(d)  # raw
            for decade_start in (10, 20, 30, 40):
                v = decade_start + d
                if 1 <= v <= main_max:
                    all_targets.add(v)
    return {
        "envelopes": envelopes,
        "hide_digits": sorted({d for lo, hi in envelopes for d in range(lo + 1, hi) if lo != hi}),
        "carrier_numbers": sorted(all_targets),
    }


# ─────────────────────────────────────────────────────────────────────────
# 6. 🌉 CROSS-LOTTERY BRIDGE — Eu→Sw +21/-25/+21back/±1
# ─────────────────────────────────────────────────────────────────────────
async def cross_lottery_bridge(target_dt: datetime, target_mode: str) -> Dict:
    """If predicting Swiss, bridge from latest Euro before target.
    If predicting Euro, bridge from latest Swiss before target.

    Layers (S37 canon, 222 events in Q2):
      • Layer 1 — opposite-mode mains transformed (+21 for Eu→Sw, −21 for Sw→Eu)
      • Layer 2 — opposite-mode HUNGRIES (last 6 draws silent)
      • Layer 3 — opposite-mode DATE atoms (digits, silence-agent, perms)
    """
    other_mode = "euro" if target_mode == "swiss" else "swiss"
    other_draws = await load_draws(other_mode)
    other_draws = sorted([d for d in other_draws if d["dt"] < target_dt], key=lambda x: x["dt"])
    if not other_draws:
        return {"available": False}
    latest = other_draws[-1]

    main_max = SWISS_MAIN_MAX if target_mode == "swiss" else 50
    bridge_candidates = set()
    bridge_tags = {}

    def add(n, tag):
        if 1 <= n <= main_max:
            bridge_candidates.add(n)
            bridge_tags.setdefault(n, []).append(tag)

    # Direction transform
    if target_mode == "swiss":
        # Eu n → Sw via +21 (or -25 wrap, +21back)
        for n in latest["p"]:
            add(n + SWISS_CIRCLE, f"Eu-mains+21({n}→{n+SWISS_CIRCLE})")
            add(n + SWISS_CIRCLE - EURO_CIRCLE, f"Eu+21-25({n})")
            add(n, f"Eu-raw({n})")
            add(n + SWISS_CIRCLE - 1, f"Eu+21-1nb({n})")
            add(n + SWISS_CIRCLE + 1, f"Eu+21+1nb({n})")
        # Stars too — Eu stars 1-12 are direct in Swiss range
        for s in (latest.get("stars") or []):
            add(s, f"Eu⭐-raw({s})")
            add(s + SWISS_CIRCLE, f"Eu⭐+21({s})")
    else:
        # Sw n → Eu via -21
        for n in latest["p"]:
            add(n - SWISS_CIRCLE, f"Sw-mains-21({n})")
            add(n - SWISS_CIRCLE + EURO_CIRCLE, f"Sw-21+25({n})")
            add(n, f"Sw-raw({n})")

    # Layer 2 — opposite-mode hungries (last 6 draws silent)
    last6 = other_draws[-6:]
    played = set()
    for d in last6:
        played.update(d["p"])
    other_max = 50 if other_mode == "euro" else SWISS_MAIN_MAX
    hungries = [n for n in range(1, other_max + 1) if n not in played]
    for hn in hungries[:20]:  # top 20 only
        if target_mode == "swiss":
            add(hn + SWISS_CIRCLE, f"Eu-hungry+21({hn})")
            add(hn, f"Eu-hungry-raw({hn})")
        else:
            add(hn - SWISS_CIRCLE, f"Sw-hungry-21({hn})")

    return {
        "available": True,
        "from_lottery": other_mode,
        "from_date": latest["date"],
        "from_mains": latest["p"],
        "from_stars_or_lr": latest.get("stars") or [latest.get("lucky"), latest.get("replay")],
        "bridge_candidates": sorted(bridge_candidates),
        "bridge_tags": bridge_tags,
    }


# ─────────────────────────────────────────────────────────────────────────
# 7. 🧠 E BRAIN WEIGHTS — read leaderboard
# ─────────────────────────────────────────────────────────────────────────
def e_brain_weights() -> Dict[str, float]:
    summary = get_memory_summary(limit=30)
    weights = {}
    for entry in summary.get("lens_leaderboard", []):
        if entry["fires"] >= 3:
            weights[entry["lens"]] = entry["hit_rate"]
    return weights


# ─────────────────────────────────────────────────────────────────────────
# 8. 🎫 SWISS SYMPHONY — 10-ticket builder for 6 mains + 🍀 + R
# ─────────────────────────────────────────────────────────────────────────
async def build_swiss_symphony(target_date: str, count: int = 10,
                                extra_envelopes: Optional[List[Tuple[int, int]]] = None,
                                ) -> Dict[str, Any]:
    """Build `count` Swiss tickets (6 mains + 🍀 + R) tagged with lens-DNA.

    Pulls from:
      • cosmic_voices orchestrator (existing lenses)
      • Swiss-specific lenses: back_chord, q1_stencil, gap_pattern,
        d_count_walker, date_envelope, cross_lottery_bridge
      • e_memory leaderboard (weights)
    """
    target_dt = parse_dt(target_date) if isinstance(target_date, str) else target_date
    draws = await load_draws("swiss")
    draws_sorted = sorted([d for d in draws if d["dt"] < target_dt], key=lambda x: x["dt"])
    if not draws_sorted:
        return {"error": "no Swiss draws available"}
    bd = draws_sorted[-1]

    # Run existing cosmic_voices for Swiss context
    cv = await run_cosmic_voices(target_date, "swiss")
    voices = cv.get("voices", cv)

    # Run new Swiss lenses
    back_chord = swiss_back_chord(bd)
    q_target = quarter_of(target_dt, "swiss")
    current_q = [d for d in draws_sorted if d["quarter"] == q_target and d["year"] == target_dt.year]
    gap_pat = gap_pattern_signals(current_q)
    q1_proj = q1_stencil_project(target_dt, draws_sorted, "swiss")
    d_clock_p1_9 = d_count_walker(target_dt, draws_sorted, target_value=9, target_position=0)
    envelope = date_envelope(target_dt, "swiss", extra_envelopes)
    bridge = await cross_lottery_bridge(target_dt, "swiss")
    weights = e_brain_weights()

    # ── Aggregate candidate pool with lens-DNA tags ──
    pool: Dict[int, List[str]] = {}

    def tag(n: int, label: str):
        if 1 <= n <= SWISS_MAIN_MAX:
            pool.setdefault(n, []).append(label)

    # Existing lens shout/whisper (top-12 ranked)
    conv = voices.get("convergence_scorer") or {}
    for m in (conv.get("shout_zone") or [])[:8]:
        tag(m["n"], f"shout(score={m.get('score')})")
    for m in (conv.get("whisper_zone") or [])[:8]:
        tag(m["n"], "whisper")
    for m in (conv.get("ranked_mains") or [])[:14]:
        if m["n"] not in pool:
            tag(m["n"], "ranked")

    # 🍀↔R back chord
    for n, why in back_chord["candidates"]:
        tag(n, f"back-chord:{why}")

    # Q1 stencil projection
    if q1_proj.get("available"):
        for n in q1_proj["projected_mains"]:
            tag(n, f"Q1-stencil({q1_proj['prior_nd_date']})")

    # Gap-pattern position hints
    if gap_pat.get("available"):
        for h in gap_pat["position_hints"]:
            if "candidate" in h:
                tag(h["candidate"], f"gap-{h['rule']}")
            for c in h.get("candidates", []):
                tag(c, f"gap-{h['rule']}")

    # D-clock 9 owed
    if d_clock_p1_9.get("available") and d_clock_p1_9.get("is_triple_lock"):
        tag(9, f"d72-9-clock-triple-lock(d{d_clock_p1_9['target_d']})")
    elif d_clock_p1_9.get("available") and d_clock_p1_9.get("is_mult_9"):
        tag(9, f"d-clock-mult9(d{d_clock_p1_9['target_d']})")

    # Date envelope hides
    for n in envelope["carrier_numbers"]:
        tag(n, f"date-hide({envelope['hide_digits']})")

    # Cross-lottery bridge
    if bridge.get("available"):
        for n in bridge["bridge_candidates"]:
            tags_for_n = bridge["bridge_tags"].get(n, [])
            tag(n, f"bridge:{tags_for_n[0] if tags_for_n else ''}")

    # ── Build 10 tickets across 5 stories ──
    sorted_pool = sorted(pool.items(), key=lambda kv: -len(kv[1]))  # most-tagged first
    top_pool = [n for n, _ in sorted_pool]

    tickets = []
    stories = [
        ("152-symphony", _build_152_symphony, count > 0),
        ("Q1d10-stencil", _build_stencil_ticket, q1_proj.get("available")),
        ("9-clock-breakout", _build_9_clock_ticket, d_clock_p1_9.get("is_triple_lock")),
        ("snap-back-compromise", _build_snap_back_ticket, True),
        ("euro-bridge", _build_bridge_ticket, bridge.get("available")),
        ("mirror-sleeping-voice", _build_mirror_sleeping_ticket, True),
    ]

    n_per_story = max(2, count // len(stories) + 1)
    seen_tickets = set()
    for story_name, builder, ok in stories:
        if not ok or len(tickets) >= count:
            continue
        for variant in range(n_per_story):
            try:
                t = builder(top_pool, voices, back_chord, q1_proj, envelope,
                            bridge, gap_pat, d_clock_p1_9, variant)
            except Exception as ex:
                t = None
            if not t:
                continue
            key = tuple(sorted(t["mains"]))
            if key in seen_tickets:
                continue
            seen_tickets.add(key)
            t["story"] = story_name
            t["lens_dna"] = {n: pool.get(n, []) for n in t["mains"]}
            tickets.append(t)
            if len(tickets) >= count:
                break

    # Backfill if short
    while len(tickets) < count and top_pool:
        t = _backfill_ticket(top_pool, len(tickets))
        if not t:
            break
        key = tuple(sorted(t["mains"]))
        if key in seen_tickets:
            t["mains"][0] = (t["mains"][0] % SWISS_MAIN_MAX) + 1
            t["mains"] = sorted(set(t["mains"]))
            if len(t["mains"]) < 6:
                continue
            key = tuple(t["mains"])
            if key in seen_tickets:
                break
        seen_tickets.add(key)
        t["story"] = "carpet-fill"
        t["lens_dna"] = {n: pool.get(n, ["fill"]) for n in t["mains"]}
        tickets.append(t)

    return {
        "target_date": target_date,
        "mode": "swiss",
        "bd_date": bd["date"],
        "bd_mains": bd["p"],
        "bd_lucky": bd.get("lucky"),
        "bd_replay": bd.get("replay"),
        "lenses": {
            "back_chord": back_chord,
            "q1_stencil": q1_proj,
            "gap_pattern": gap_pat,
            "d_count_walker_p1_9": d_clock_p1_9,
            "date_envelope": envelope,
            "cross_lottery_bridge": bridge,
            "e_memory_weights": weights,
        },
        "candidate_pool_size": len(pool),
        "candidate_pool": dict(sorted_pool[:20]),
        "tickets": tickets,
    }


# ── Ticket builders ────────────────────────────────────────────────────
def _pick_ascending(seeds: List[int], pool: List[int], n: int = 6) -> List[int]:
    out = sorted(set(seeds))
    for n_ in pool:
        if n_ in out:
            continue
        out.append(n_)
        out = sorted(set(out))
        if len(out) >= n:
            break
    return sorted(out[:n]) if len(out) >= n else None


def _lucky_replay(variant: int, sum_target: int = 13) -> Tuple[int, int]:
    # Swiss 🍀 ∈ [1,6], R ∈ [1,42]. Pairs lean toward sum=13 (loudest mode).
    luckies = [(4, 9), (1, 12), (6, 7), (5, 8), (2, 11), (3, 10), (4, 1), (6, 1), (5, 1), (2, 9)]
    L, R = luckies[variant % len(luckies)]
    L = max(1, min(SWISS_LUCKY_MAX, L))
    R = max(1, min(SWISS_REPLAY_MAX, R))
    return L, R


def _build_152_symphony(pool, voices, bc, q1, env, bridge, gap, dclk, variant):
    seeds = [9, 16, 22, 31, 36, 38] if variant == 0 else [9, 14, 22, 31, 36, 38]
    mains = _pick_ascending(seeds, pool, 6)
    if not mains:
        return None
    L, R = _lucky_replay(variant + 4)
    return {"mains": mains, "lucky": L, "replay": R, "sum": sum(mains)}


def _build_stencil_ticket(pool, voices, bc, q1, env, bridge, gap, dclk, variant):
    if not q1.get("available"):
        return None
    seeds = q1["projected_mains"][:6]
    if variant == 1:  # variation
        seeds = [s + (1 if i < 3 else -1) for i, s in enumerate(seeds)]
        seeds = [max(1, min(SWISS_MAIN_MAX, s)) for s in seeds]
    mains = _pick_ascending(seeds, pool, 6)
    if not mains:
        return None
    L, R = _lucky_replay(variant)
    return {"mains": mains, "lucky": L, "replay": R, "sum": sum(mains)}


def _build_9_clock_ticket(pool, voices, bc, q1, env, bridge, gap, dclk, variant):
    seeds = [9, 16, 27, 32, 38, 39] if variant == 0 else [9, 16, 22, 27, 32, 38]
    mains = _pick_ascending(seeds, pool, 6)
    if not mains:
        return None
    # Swiss Lucky max is 6 — encode 9-clock by 🍀=4 (DR=4 echoes 13 sum mode)
    return {"mains": mains, "lucky": 4, "replay": 9 if variant == 0 else 7,
            "sum": sum(mains)}


def _build_snap_back_ticket(pool, voices, bc, q1, env, bridge, gap, dclk, variant):
    seeds = [5, 9, 16, 27, 31, 38] if variant == 0 else [2, 9, 16, 22, 31, 36]
    mains = _pick_ascending(seeds, pool, 6)
    if not mains:
        return None
    L, R = _lucky_replay(variant + 1)
    return {"mains": mains, "lucky": L, "replay": R, "sum": sum(mains)}


def _build_bridge_ticket(pool, voices, bc, q1, env, bridge, gap, dclk, variant):
    if not bridge.get("available"):
        return None
    eu_mains_in_sw = [n for n in (bridge.get("from_mains") or []) if 1 <= n <= SWISS_MAIN_MAX]
    base = sorted(set(eu_mains_in_sw[:3] + [22, 27, 38]))[:6] if variant == 0 else \
           sorted(set([9, 14, 17, 19, 31, 36]))
    mains = _pick_ascending(base, pool, 6)
    if not mains:
        return None
    L, R = _lucky_replay(variant + 6)
    return {"mains": mains, "lucky": L, "replay": R, "sum": sum(mains)}


def _build_mirror_sleeping_ticket(pool, voices, bc, q1, env, bridge, gap, dclk, variant):
    seeds = [9, 10, 16, 27, 32, 38] if variant == 0 else [5, 10, 22, 32, 36, 41]
    mains = _pick_ascending(seeds, pool, 6)
    if not mains:
        return None
    L, R = _lucky_replay(variant + 8)
    return {"mains": mains, "lucky": L, "replay": R, "sum": sum(mains)}


def _backfill_ticket(top_pool, idx):
    if len(top_pool) < 6:
        return None
    start = (idx * 2) % max(1, len(top_pool) - 6)
    seeds = sorted(top_pool[start:start + 6])
    if len(seeds) < 6:
        seeds = sorted(top_pool[:6])
    L = (idx % 6) + 1
    R = ((idx * 7) % SWISS_REPLAY_MAX) + 1
    return {"mains": seeds, "lucky": L, "replay": R, "sum": sum(seeds)}
