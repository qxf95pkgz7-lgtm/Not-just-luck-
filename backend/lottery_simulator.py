"""
🎻🎧 LOTTERY MUSIC SIMULATOR — The Cosmos Convergence Engine

Pick any date (Euro or Swiss). The simulator runs EVERY law from The Book
(`/app/memory/swiss_music_notes.md`) against the draws BEFORE that date,
then builds:

  1. A CONVERGENCE RADAR — for every number 1-50 (and stars 1-12), list
     which laws are vibrating. Numbers ringing in 3+ lenses = cosmos shout.
  2. A per-POSITION SUSPECT LIST — P1 / P2 / P3 / P4 / P5 (+stars) ranked
     by lens count × position-fitness.
  3. A VALIDATION BLOCK — if the actual draw is known, print hit rate.

USAGE:
  python lottery_simulator.py --date 17.04.2026 --mode euro
  python lottery_simulator.py --date 18.04.2026 --mode swiss
  python lottery_simulator.py --date 17.04.2026 --mode euro --actual "22,23,28,41,47" --stars "6,8"

No external deps beyond pymongo + dotenv. Self-contained law engine.
"""
import argparse
import json
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from dotenv import load_dotenv
from pymongo import MongoClient

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

# ─────────────────────────────────────────────────────────────
# DB + date helpers
# ─────────────────────────────────────────────────────────────
def _db():
    return MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]

def parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%d.%m.%Y")

def load_draws(mode: str, before: str) -> List[dict]:
    """Return all draws strictly BEFORE `before`, sorted by true date asc."""
    col = "euromillions_draws" if mode == "euro" else "draws"
    raw = list(_db()[col].find({}, {"_id": 0}))
    cutoff = parse_date(before)
    out = []
    for d in raw:
        try:
            dt = parse_date(d["date"])
            if dt < cutoff:
                out.append({**d, "_dt": dt})
        except Exception:
            continue
    out.sort(key=lambda x: x["_dt"])
    return out

# ─────────────────────────────────────────────────────────────
# Range helpers per lottery
# ─────────────────────────────────────────────────────────────
CFG = {
    "euro":  {"max_main": 50, "circle": 25, "npos": 5, "max_star": 12},
    "swiss": {"max_main": 42, "circle": 21, "npos": 6, "max_star": None},
}

def circle(n: int, mode: str) -> int:
    m = CFG[mode]["max_main"]
    c = CFG[mode]["circle"]
    return ((n - 1 + c) % m) + 1

def mirror_low(n: int) -> int:
    """🪞 ONE LAW (Canon 32): defers to circle (Euro)."""
    from mirror_canon import mirror_of as _mc_of
    return _mc_of(n, "euro")

def mirror_high(n: int) -> int:
    """🪞 ONE LAW (Canon 32): same as mirror_low — both fold to the One Law."""
    from mirror_canon import mirror_of as _mc_of
    return _mc_of(n, "euro")

def digits_of_date(date_str: str) -> List[int]:
    """17.04 → [1,7,0,4]  (ignore year)."""
    dd, mm, _ = date_str.split(".")
    return [int(c) for c in dd + mm]

def date_perms(date_str: str, max_main: int) -> List[int]:
    ds = digits_of_date(date_str)
    out = set()
    for a in ds:
        for b in ds:
            n = a * 10 + b
            if 1 <= n <= max_main:
                out.add(n)
    return sorted(out)

# ─────────────────────────────────────────────────────────────
# Law engine — each law adds (number → reason) to `rings`
# ─────────────────────────────────────────────────────────────
def law_snap_back(rings, draws, mode):
    """If prev draw P1>20, next P1 ≤ 7 @50%, ≤12 @66%. (Euro-documented)"""
    if not draws:
        return
    last = draws[-1]
    nums = sorted(last["numbers"])
    if nums[0] > 20:
        for n in range(1, 8):
            rings[n].append(("snap-back-sweet", f"prev P1={nums[0]} >20 → sweet P1≤7"))
        for n in range(8, 13):
            rings[n].append(("snap-back-band", f"prev P1={nums[0]} → band P1 8-12"))

def law_date_perm(rings, target_date, mode):
    mx = CFG[mode]["max_main"]
    for n in date_perms(target_date, mx):
        rings[n].append(("date-perm", f"recomposition of digits of {target_date}"))

def law_raw_date_echo(rings, target_date, mode):
    dd, mm, _ = target_date.split(".")
    d, m = int(dd), int(mm)
    mx = CFG[mode]["max_main"]
    if 1 <= d <= mx:
        rings[d].append(("raw-D", f"day({d}) direct"))
    if 1 <= m <= mx:
        rings[m].append(("raw-M", f"month({m}) direct"))

def law_circle_date_echo(rings, target_date, mode):
    dd, mm, _ = target_date.split(".")
    d, m = int(dd), int(mm)
    mx = CFG[mode]["max_main"]
    cD = circle(d, mode) if d <= mx else None
    cM = circle(m, mode) if m <= mx else None
    for (label, target) in [("circle(D)", cD), ("circle(M)", cM)]:
        if target is None:
            continue
        for delta in [-2, -1, 0, 1, 2]:
            n = target + delta
            if 1 <= n <= mx:
                tag = f"{label}±{abs(delta)}" if delta else f"{label} EXACT"
                rings[n].append(("date-circle", f"{tag}={target}"))

def _is_rare_compact(d, mode):
    nums = sorted(d["numbers"])
    if mode == "euro":
        return (nums[3] - nums[0]) <= 7 and (nums[4] - nums[3]) >= 6
    else:
        return (nums[4] - nums[0]) <= 10 and (nums[5] - nums[4]) >= 8

def law_rare_event(rings, draws, mode):
    """Find most recent rare-compact in last 10 draws → unreleased mains/stars echo."""
    window = draws[-10:]
    rare = None
    for d in reversed(window):
        if _is_rare_compact(d, mode):
            rare = d
            break
    if not rare:
        return
    post = [d for d in draws if d["_dt"] > rare["_dt"]]
    played_mains = set()
    played_stars = set()
    for d in post:
        played_mains.update(d["numbers"])
        if mode == "euro":
            played_stars.update(d.get("stars", []))
    draws_since = len(post)
    if draws_since <= 8:
        for n in rare["numbers"]:
            if n not in played_mains:
                rings[n].append(("rare-echo", f"rare seed {rare['date']} +{draws_since}"))
        if mode == "euro":
            for s in rare.get("stars", []):
                rings[f"S{s}"].append(("rare-star-echo", f"rare ⭐ seed {rare['date']} +{draws_since}"))

def law_high_sum_rebound(rings, draws, mode):
    """After P1+P2 ≥ 40 (Euro): next P1 bucket weighted 8-15 (33%), 1-3 (28%), 4-7 (20%)."""
    if mode != "euro" or not draws:
        return
    last = sorted(draws[-1]["numbers"])
    if last[0] + last[1] >= 40:
        for n in range(8, 16):
            rings[n].append(("high-sum-rebound", f"prev P1+P2={last[0]+last[1]} → P1 bucket 8-15"))
        for n in range(1, 4):
            rings[n].append(("high-sum-rebound-low", "rebound low bucket 1-3"))

def law_ladder_fill(rings, draws, target_date, mode, banned: List[int]):
    """
    LADDER-FILL LAW (DJ discovery 20.04.2026):
    Take last draw's front trio digit permutations IN RANGE. Any perm that is
    BANNED / just-played / cooling = ladder anchor. Integers BETWEEN consecutive
    anchors become hungry landing candidates.
    """
    if not draws:
        return
    last_nums = sorted(draws[-1]["numbers"])
    front_digits = []
    for n in last_nums[:3]:
        front_digits += [int(c) for c in str(n)]
    mx = CFG[mode]["max_main"]
    perms = set()
    for a in front_digits:
        for b in front_digits:
            n = a * 10 + b
            if 1 <= n <= mx:
                perms.add(n)
    just_played = set(draws[-1]["numbers"]) | set(banned or [])
    anchors = sorted(p for p in perms if p in just_played)
    # look for consecutive-zone anchor pairs (gap ≤ 5)
    for i in range(len(anchors) - 1):
        a, b = anchors[i], anchors[i+1]
        if 2 <= b - a <= 5:
            for mid in range(a + 1, b):
                if 1 <= mid <= mx:
                    rings[mid].append(
                        ("ladder-fill", f"{a}↔{b} anchors (from last-draw digit perms) → middle")
                    )

def law_self_circle_21(rings, draws, mode):
    """
    SELF-CIRCLE +21 BRIDGE (DJ discovery 20.04.2026):
    Within a single lottery, numbers of the last draw also reappear transformed
    by +21 (the Swiss-circle formula applied inside Euro too).
    Euro example: last Euro had 1, 2 in P1-P2 → next Euro landed 22, 23.
    """
    if not draws:
        return
    mx = CFG[mode]["max_main"]
    for n in draws[-1]["numbers"]:
        x = n + 21
        if 1 <= x <= mx:
            rings[x].append(("self-circle-21", f"last {mode} {n}+21 inside own range"))
        x2 = n - 21
        if 1 <= x2 <= mx:
            rings[x2].append(("self-circle-21-down", f"last {mode} {n}-21 inside own range"))


def law_silent_band_hunger(rings, draws, mode, window: int = 6):
    """
    SILENT-BAND HUNGER (DJ discovery 20.04.2026):
    Scan the last N draws; any integer whose ±2 neighborhood had ZERO activity
    in the window has pressure building. Tag it as silent-band hungry.
    """
    if not draws:
        return
    mx = CFG[mode]["max_main"]
    recent = set()
    for d in draws[-window:]:
        recent.update(d["numbers"])
    for n in range(1, mx + 1):
        neighborhood = set(range(max(1, n - 2), min(mx, n + 2) + 1))
        if not (neighborhood & recent):
            rings[n].append(("silent-band", f"±2 zone empty in last {window} draws"))


def law_cross_lottery_bridge(rings, target_date, mode):
    """
    Swiss ⇄ Euro digit-roll / circle-bridge:
    - Euro → Swiss: n mod 21 (i.e., n - 21 or n - 42) lives in Swiss voice.
    - Swiss → Euro: n + 21 lives in Euro voice.
    Also Δ±2 (the loudest king bridge).
    """
    cutoff = parse_date(target_date)
    # Find the most recent draw of the OTHER lottery before target
    other_mode = "swiss" if mode == "euro" else "euro"
    other_col = "draws" if other_mode == "swiss" else "euromillions_draws"
    raw = list(_db()[other_col].find({}, {"_id": 0}))
    candidates = []
    for d in raw:
        try:
            dt = parse_date(d["date"])
            if dt < cutoff:
                candidates.append((dt, d))
        except Exception:
            continue
    if not candidates:
        return
    candidates.sort(key=lambda x: x[0])
    last_other = candidates[-1][1]
    mx = CFG[mode]["max_main"]
    for n in last_other["numbers"]:
        # Delta ±2 king bridge (Euro→Swiss validated king)
        for d in [-2, -1, 1, 2]:
            x = n + d
            if 1 <= x <= mx:
                rings[x].append(("cross-Δ", f"{other_mode} {n} Δ{d}"))
        # Circle bridge
        if mode == "swiss":
            # Swiss voice of Euro n = ((n-1) mod 42)+1
            x = ((n - 1) % mx) + 1
            rings[x].append(("cross-circle", f"Swiss voice of Euro {n}"))
        else:
            x = n + 21
            if 1 <= x <= mx:
                rings[x].append(("cross-circle", f"Euro voice of Swiss {n} (+21)"))

def law_p1_running_sum(rings, draws, mode, quarter_days: int = 4):
    """
    P1 RUNNING SUM LAW (DJ discovery 20.04.2026):
    Sum of last N P1 values often equals next draw's P1 (or a close slot).
    Use N=3 as primary, N=2 as secondary.
    """
    mx = CFG[mode]["max_main"]
    if len(draws) < 2:
        return
    for N in [2, 3, 4]:
        if len(draws) < N:
            continue
        s = sum(sorted(d["numbers"])[0] for d in draws[-N:])
        if 1 <= s <= mx:
            rings[s].append(("p1-running-sum", f"Σ(last {N} P1s)={s}"))

def law_plus10_key(rings, mode):
    """Q1→Q2 +10 KEY applied to Q1d5 (Euro 2026 documented)."""
    if mode != "euro":
        return
    q1d5 = [5, 17, 24, 29, 50]  # 16.01.2026
    for n in q1d5:
        x = n + 10
        if x > 50:
            x -= 50
        if 1 <= x <= 50:
            rings[x].append(("+10-key", f"Q1d5 {n}+10 translation"))

def law_banned_backdoor(rings, banned: List[int], mode):
    if not banned:
        return
    for b in banned:
        c = circle(b, mode)
        rings[c].append(("back-door", f"circle({b})={c}"))
        lo = mirror_low(b)
        if lo and 1 <= lo <= CFG[mode]["max_main"]:
            rings[lo].append(("mirror-low", f"mirror-low({b})={lo} (pair-sum 28)"))
        hi = mirror_high(b)
        if hi and 1 <= hi <= CFG[mode]["max_main"]:
            rings[hi].append(("mirror-high", f"mirror-high({b})={hi} (pair-sum 56)"))

def law_hungry_seed(rings, draws, mode, seeds: Dict[str, list]):
    """Seed-hungry: numbers in seed sets not yet played in the reference window."""
    played = set()
    for d in draws[-30:]:  # last 30 draws window
        played.update(d["numbers"])
    for seed_name, seed_nums in seeds.items():
        for n in seed_nums:
            if n not in played:
                rings[n].append(("seed-hungry", f"{seed_name} un-played in last 30"))

def law_column_memory(rings, draws, mode):
    """Column-Memory nudges (Swiss-documented, Euro used lightly)."""
    if not draws:
        return
    last = sorted(draws[-1]["numbers"])
    # P1 transitions (Swiss-documented but applied both)
    p1 = last[0]
    deltas = {
        4: [4], 2: [2, 3], 1: [0, 1], 10: [-7, -8],
    }
    if p1 in deltas:
        for dlt in deltas[p1]:
            tgt = p1 + dlt
            if 1 <= tgt <= CFG[mode]["max_main"]:
                rings[tgt].append(("col-memory-P1", f"last P1={p1} → +{dlt}"))
    # P4 documented jumps (Swiss)
    if mode == "swiss" and len(last) >= 4:
        p4 = last[3]
        if p4 == 21:
            rings[28].append(("col-memory-P4", "last P4=21 → +7"))
        if p4 == 14:
            rings[35].append(("col-memory-P4", "last P4=14 → +21 wrap"))

def law_backrow_echo(rings, draws, mode):
    """After a trigger (P1>20 Euro), back-row of trigger carries ~50% forward."""
    if mode != "euro" or not draws:
        return
    last = sorted(draws[-1]["numbers"])
    if last[0] > 20:
        for n in last[-2:]:
            rings[n].append(("back-row-echo", f"prev P4/P5={n} echo forward"))

def law_consecutive_pair(rings, draws, mode):
    """If last draw had a consecutive pair, next draw often carries one too."""
    if not draws:
        return
    nums = sorted(draws[-1]["numbers"])
    for i in range(len(nums) - 1):
        if nums[i+1] - nums[i] == 1:
            # boost pair-friendly band (20s and 40s stack historically)
            for base in [nums[i] + 5, nums[i] + 10]:
                if 1 <= base <= CFG[mode]["max_main"]:
                    rings[base].append(("cons-pair-band", f"last pair {nums[i]}-{nums[i+1]}"))
            break

def law_dj_calls(rings, dj_call: dict, mode):
    """Apply DJ locks / expanded back row / triple-lock / hungry list."""
    if mode != "euro" or not dj_call:
        return
    c = dj_call.get("euro", {})
    if c.get("p1_lock"):
        rings[c["p1_lock"]].append(("dj-P1-lock", f"user P1={c['p1_lock']}"))
    if c.get("p2_lock"):
        rings[c["p2_lock"]].append(("dj-P2-lock", f"user P2={c['p2_lock']}"))
    for s in c.get("star_locks", []):
        rings[f"S{s}"].append(("dj-star-lock", f"user star={s}"))
    for n in c.get("triple_lock_mains", []):
        rings[n].append(("dj-triple-lock", "triple-lock main"))
    for n in c.get("expanded_back_row", []):
        rings[n].append(("dj-back-row", "expanded back-row"))
    for n in c.get("user_hungry_list_next_3d", []):
        rings[n].append(("dj-hungry", "DJ hungry list"))
    for n in c.get("plus10_key", []):
        rings[n].append(("dj-plus10", "+10 key list"))
    for n in c.get("date_perms", []):
        rings[n].append(("dj-date-perm", "DJ date-perm list"))

def law_star_math(rings, draws, mode):
    """
    EURO STAR KING FORMULAS (DJ discovery 20.04.2026, validated over 1,617 draws):
    The stars pre-echo the mains via specific arithmetic bridges.
    Discovered rates vs 2% random baseline:
      • S2 - S1 = P1          8.2%  🔥🔥  (4× baseline — P1 KING)
      • S1 + S2 = P1 or P2    4.1% / 3.8%
      • S1 + 12 = P2          4.3%  🔥
      • 25 + S1 = P3          3.7%  (circle-lift)
      • S1 + 21 = P3/P4       3.5%  (bridge)
      • 25 + S2 = P4          4.3%  🔥  (back-row ladder)
      • S2 × 4 = P5           3.3%  🔥  (quadruple expansion)
      • 50 - S1 - S2 = P5     3.2%  (mirror-back)
      • S1 × 3 = P1           4.0%
    """
    if mode != "euro" or not draws:
        return
    last = draws[-1]
    stars = last.get("stars", [])
    if len(stars) != 2:
        return
    s1, s2 = sorted(stars)
    formulas = [
        (s2 - s1,     f"S2-S1 king (8.2% → P1)"),
        (s1 + s2,     f"S1+S2 pivot (4.1% → P1/P2)"),
        (s1 * 3,      f"S1×3 (4.0% → P1)"),
        (s1 * 4,      f"S1×4 (3.2% → P1)"),
        (s1 + 12,     f"S1+12 (4.3% → P2)"),
        (s2 + 12,     f"S2+12 (2.5% → P2)"),
        (2 * s1 + s2, f"2·S1+S2 (4.0% → P2)"),
        (25 + s1,     f"25+S1 circle-lift (3.7% → P3)"),
        (s1 + 21,     f"S1+21 bridge (3.5% → P3)"),
        (s2 + 21,     f"S2+21 bridge (3.3% → P3/P4)"),
        (25 + s2,     f"25+S2 circle-lift (4.3% → P4)"),
        (s2 * 4,      f"S2×4 quad-expand (3.3% → P5)"),
        (50 - s1 - s2, f"50-S1-S2 mirror-back (3.2% → P5)"),
        (s1 * s2,     f"S1×S2 product ({s1}×{s2})"),
        (s1 * 10 + s2, f"concat S1|S2 (6.4% in mains)"),
        (s2 * 10 + s1, f"concat S2|S1 (0.9% in mains)"),
    ]
    for val, why in formulas:
        if 1 <= val <= 50:
            rings[val].append(("star-king-formula", why))
    # Also star-to-star forward hints for star suspects
    for x, why in [
        (s1 + s2,  f"⭐{s1}+⭐{s2}"),
        (s2 - s1,  f"⭐{s2}-⭐{s1}"),
        ((s1 * s2) % 12 or 12, f"⭐{s1}×⭐{s2} mod 12"),
    ]:
        if 1 <= x <= 12:
            rings[f"S{x}"].append(("star-math", why))

    # Cross-draw: previous S1+25, S2+25, S1+12, S2+12 can still echo
    # (Note: already baked into formulas above since we only track last draw)


def law_prev_star_forward_echo(rings, draws, mode, window=3):
    """
    Prev draw stars → next P1 ±3 fires at 44.7% (strongest cross-draw signal).
    Add soft bonuses for numbers in the ±3 neighborhood of last draw's stars.
    """
    if mode != "euro" or not draws:
        return
    last = draws[-1]
    stars = last.get("stars", [])
    if len(stars) != 2:
        return
    s1, s2 = sorted(stars)
    mx = 50
    for star, label in [(s1, "S1"), (s2, "S2")]:
        for delta in [-3, -2, -1, 0, 1, 2, 3]:
            n = star + delta
            if 1 <= n <= mx and delta != 0:
                tag_name = f"star-forward-echo"
                rings[n].append((tag_name, f"prev ⭐{label}={star} ±{abs(delta)} → P1/P2 zone (44.7% ±3)"))

# ─────────────────────────────────────────────────────────────
# Position fitness — documented bias tables
# ─────────────────────────────────────────────────────────────
# Very rough Euro priors (from 2-yr analysis)
EURO_POS_BANDS = {
    0: range(1, 15),   # P1 ≤ 14
    1: range(3, 22),   # P2
    2: range(10, 35),  # P3
    3: range(22, 45),  # P4
    4: range(30, 51),  # P5
}
SWISS_POS_BANDS = {
    0: range(1, 10),
    1: range(3, 18),
    2: range(8, 25),
    3: range(15, 32),
    4: range(22, 38),
    5: range(30, 43),
}

def position_fit(n: int, pos: int, mode: str) -> bool:
    bands = EURO_POS_BANDS if mode == "euro" else SWISS_POS_BANDS
    return n in bands.get(pos, range(1, 51))

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def run_simulator(target_date: str, mode: str,
                  actual_mains: Optional[List[int]] = None,
                  actual_stars: Optional[List[int]] = None,
                  dj_call: Optional[dict] = None) -> dict:
    draws = load_draws(mode, target_date)
    if not draws:
        return {"error": "no historical draws before target date"}

    # Seeds (Euro-documented reference anchors for 2026) — date-gated to avoid hindsight
    seeds = {}
    if mode == "euro":
        target_dt = parse_date(target_date)
        SEED_DATES = {
            "Q1d1-yearly":  ("02.01.2026", [8, 27, 42, 44, 46]),
            "Q1d2":         ("06.01.2026", [5, 14, 17, 18, 31]),
            "Q1d3":         ("09.01.2026", [1, 7, 10, 26, 34]),
            "Q1d4":         ("13.01.2026", [6, 10, 18, 44, 47]),
            "Q1d5-+10":     ("16.01.2026", [5, 17, 24, 29, 50]),
            "rare-24.03":   ("24.03.2026", [12, 16, 17, 18, 27]),
        }
        for name, (seed_date, nums) in SEED_DATES.items():
            try:
                if parse_date(seed_date) < target_dt:
                    seeds[name] = nums
            except Exception:
                pass

    rings: Dict = defaultdict(list)
    banned = (dj_call or {}).get(mode, {}).get("banned_mains", []) if dj_call else []

    # Fire every law
    law_snap_back(rings, draws, mode)
    law_date_perm(rings, target_date, mode)
    law_raw_date_echo(rings, target_date, mode)
    law_circle_date_echo(rings, target_date, mode)
    law_rare_event(rings, draws, mode)
    law_high_sum_rebound(rings, draws, mode)
    law_ladder_fill(rings, draws, target_date, mode, banned)
    law_cross_lottery_bridge(rings, target_date, mode)
    law_self_circle_21(rings, draws, mode)
    law_silent_band_hunger(rings, draws, mode)
    law_p1_running_sum(rings, draws, mode)
    law_plus10_key(rings, mode)
    law_banned_backdoor(rings, banned, mode)
    law_hungry_seed(rings, draws, mode, seeds)
    law_column_memory(rings, draws, mode)
    law_backrow_echo(rings, draws, mode)
    law_consecutive_pair(rings, draws, mode)
    law_star_math(rings, draws, mode)
    law_prev_star_forward_echo(rings, draws, mode)
    if dj_call:
        law_dj_calls(rings, dj_call, mode)

    # Build convergence table
    mx = CFG[mode]["max_main"]
    convergence = []
    for n in range(1, mx + 1):
        entries = rings.get(n, [])
        if entries:
            laws_hit = sorted(set(tag for tag, _ in entries))
            convergence.append({
                "n": n,
                "lens_count": len(laws_hit),
                "laws": laws_hit,
                "reasons": [f"{tag}: {why}" for tag, why in entries],
            })
    convergence.sort(key=lambda x: (-x["lens_count"], x["n"]))

    # Per-position suspects — show ALL numbers ranked by lens count; flag band fit
    npos = CFG[mode]["npos"]
    position_suspects = []
    for p in range(npos):
        cands = []
        for c in convergence:
            if c["n"] in banned:
                continue
            fit = position_fit(c["n"], p, mode)
            cands.append({**c, "band_fit": fit})
        # Primary sort: lens count first (cosmos loudness), band fit as tiebreaker
        cands.sort(key=lambda x: (-x["lens_count"], 0 if x["band_fit"] else 1, x["n"]))
        position_suspects.append({
            "pos": f"P{p+1}",
            "top": cands[:15],
        })

    # Stars (Euro only)
    star_suspects = []
    if mode == "euro":
        for s in range(1, 13):
            key = f"S{s}"
            entries = rings.get(key, [])
            if entries:
                laws_hit = sorted(set(tag for tag, _ in entries))
                star_suspects.append({
                    "s": s,
                    "lens_count": len(laws_hit),
                    "laws": laws_hit,
                    "reasons": [f"{tag}: {why}" for tag, why in entries],
                })
        star_suspects.sort(key=lambda x: (-x["lens_count"], x["s"]))

    out = {
        "target_date": target_date,
        "mode": mode,
        "draws_scanned": len(draws),
        "convergence": convergence,
        "position_suspects": position_suspects,
        "star_suspects": star_suspects,
        "banned": banned,
    }

    # Validation
    if actual_mains:
        top_by_lens = set(c["n"] for c in convergence if c["lens_count"] >= 3)
        top_by_lens_any = set(c["n"] for c in convergence if c["lens_count"] >= 2)
        out["validation"] = {
            "actual_mains": sorted(actual_mains),
            "actual_stars": sorted(actual_stars or []),
            "hits_in_3plus_lens": sorted(set(actual_mains) & top_by_lens),
            "hits_in_2plus_lens": sorted(set(actual_mains) & top_by_lens_any),
            "total_3plus_pool": len(top_by_lens),
            "total_2plus_pool": len(top_by_lens_any),
        }
        # Per-position hit check
        pos_hits = []
        actual_sorted = sorted(actual_mains)
        for idx, ps in enumerate(position_suspects):
            if idx >= len(actual_sorted):
                break
            actual_n = actual_sorted[idx]
            top_ns = [c["n"] for c in ps["top"]]
            pos_hits.append({
                "pos": ps["pos"],
                "actual": actual_n,
                "in_top3": actual_n in top_ns[:3],
                "in_top5": actual_n in top_ns[:5],
                "in_top12": actual_n in top_ns[:12],
                "rank": top_ns.index(actual_n) + 1 if actual_n in top_ns else None,
            })
        out["validation"]["position_hits"] = pos_hits

    return out


def format_report(result: dict) -> str:
    if result.get("error"):
        return f"ERROR: {result['error']}"
    r = result
    out = []
    out.append(f"🎻🎧 LOTTERY MUSIC SIMULATOR")
    out.append(f"Target: {r['target_date']}  ·  Mode: {r['mode'].upper()}  ·  Draws scanned: {r['draws_scanned']}")
    if r.get("banned"):
        out.append(f"🚫 Banned: {r['banned']}")
    out.append("═" * 72)
    out.append("")
    # Convergence 3+
    strong = [c for c in r["convergence"] if c["lens_count"] >= 3]
    out.append(f"🔔 CONVERGENCE RADAR — numbers ringing in 3+ lenses ({len(strong)})")
    out.append("-" * 72)
    for c in strong[:25]:
        out.append(f"  {c['n']:>3}  ({c['lens_count']:>2} lenses)  {' · '.join(c['laws'])}")
    out.append("")
    # Position suspects
    out.append(f"🎯 POSITION SUSPECTS")
    out.append("-" * 72)
    for ps in r["position_suspects"]:
        line = f"  {ps['pos']}:  "
        parts = []
        for c in ps["top"][:10]:
            mark = "" if c.get("band_fit") else "~"
            parts.append(f"{mark}{c['n']}({c['lens_count']})")
        out.append(line + " · ".join(parts))
    out.append("  (~ = off typical band, but ringing loud)")
    out.append("")
    # Stars
    if r.get("star_suspects"):
        out.append(f"⭐ STAR SUSPECTS (Euro)")
        out.append("-" * 72)
        for s in r["star_suspects"][:8]:
            out.append(f"  ⭐{s['s']:>2} ({s['lens_count']})  {' · '.join(s['laws'])}")
        out.append("")
    # Validation
    if r.get("validation"):
        v = r["validation"]
        out.append("🧪 VALIDATION")
        out.append("-" * 72)
        out.append(f"  Actual: {v['actual_mains']}  ⭐{v['actual_stars']}")
        out.append(f"  Hits in 3+ lens pool ({v['total_3plus_pool']}): "
                   f"{v['hits_in_3plus_lens']}  ({len(v['hits_in_3plus_lens'])}/{len(v['actual_mains'])})")
        out.append(f"  Hits in 2+ lens pool ({v['total_2plus_pool']}): "
                   f"{v['hits_in_2plus_lens']}  ({len(v['hits_in_2plus_lens'])}/{len(v['actual_mains'])})")
        out.append(f"  Per-position:")
        for h in v["position_hits"]:
            badge = "🎯 TOP3" if h["in_top3"] else ("🎻 TOP5" if h["in_top5"] else ("🎧 TOP12" if h["in_top12"] else "❌ miss"))
            rank = f"#{h['rank']}" if h["rank"] else "—"
            out.append(f"    {h['pos']}: actual={h['actual']:>2}  rank={rank:>3}  {badge}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="Target date DD.MM.YYYY")
    ap.add_argument("--mode", choices=["euro", "swiss"], required=True)
    ap.add_argument("--actual", help="Actual mains, comma separated (for validation)")
    ap.add_argument("--stars", help="Actual stars, comma separated")
    ap.add_argument("--no-dj", action="store_true", help="Ignore dj_calls.json")
    ap.add_argument("--banned", help="Override banned mains, comma separated")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args()

    dj_call = None
    if not args.no_dj:
        dj_path = ROOT / "dj_calls.json"
        if dj_path.exists():
            dj_call = json.loads(dj_path.read_text())

    actual_mains = [int(x) for x in args.actual.split(",")] if args.actual else None
    actual_stars = [int(x) for x in args.stars.split(",")] if args.stars else None

    if args.banned:
        banned_list = [int(x) for x in args.banned.split(",")]
        if dj_call is None:
            dj_call = {"euro": {}, "swiss": {}}
        dj_call.setdefault(args.mode, {})["banned_mains"] = banned_list

    result = run_simulator(args.date, args.mode, actual_mains, actual_stars, dj_call)

    if args.json:
        # strip _dt, Counter, etc for JSON serialization
        print(json.dumps(result, default=str, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
