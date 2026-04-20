"""
🎻🎧 BACKTEST HARNESS & MISS EXPLAINER

Philosophy (taught by the DJ, 20.04.2026):
  "You prepare to the last war — you never win the next one.
   When numbers enter the box of suspects, they're just suspects.
   LEARN from the ones who fired but were NOT in the box.
   Ask WHY they're not in the box. That's the next law."

Two modes:
  1. BACKTEST — run `lottery_simulator` across the last N known draws, aggregate
     hit rate in 3+ / 2+ lens pools + per-position accuracy.
  2. MISS EXPLAIN — for each actual winner that was NOT in the 2+ pool,
     probe ~20 candidate transforms against the recent context and suggest
     what hidden law could have surfaced it.

USAGE:
  python backtest_harness.py --mode euro --last 20
  python backtest_harness.py --mode euro --last 20 --explain-misses
"""
import argparse
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean

from dotenv import load_dotenv
from pymongo import MongoClient

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

sys.path.insert(0, str(ROOT))
from lottery_simulator import (
    run_simulator, parse_date, load_draws, circle, digits_of_date,
    date_perms, CFG, _is_rare_compact,
)


def _db():
    return MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]


def load_recent_draws(mode: str, last_n: int):
    col = "euromillions_draws" if mode == "euro" else "draws"
    raw = list(_db()[col].find({}, {"_id": 0}))
    out = []
    for d in raw:
        try:
            out.append({**d, "_dt": parse_date(d["date"])})
        except Exception:
            continue
    out.sort(key=lambda x: x["_dt"])
    return out[-last_n:]


# ─────────────────────────────────────────────────────────────
# MISS EXPLAINER — why was this winner NOT in our box?
# Probes a battery of transforms against recent context.
# ─────────────────────────────────────────────────────────────
def explain_miss(n: int, target_date: str, mode: str, draws_before: list) -> list:
    """
    Given a number n that fired on target_date but was NOT in the 2+ lens pool,
    return a list of candidate explanations (hypotheses for NEW laws).
    """
    hypotheses = []
    mx = CFG[mode]["max_main"]
    if not draws_before:
        return hypotheses

    last = draws_before[-1]
    prev_draws = draws_before[-10:]

    # --- Direct last-draw transforms ---
    for prev_n in last["numbers"]:
        for k, label in [(5, "+5"), (6, "+6"), (7, "+7"), (8, "+8"), (9, "+9"),
                         (11, "+11"), (13, "+13"), (17, "+17"),
                         (-5, "-5"), (-7, "-7"), (-11, "-11"), (-13, "-13")]:
            x = prev_n + k
            if 1 <= x <= mx and x == n:
                hypotheses.append(f"last-draw {prev_n} {label} = {n}")
        # Digit reverse
        rev = int(str(prev_n)[::-1]) if prev_n >= 10 else prev_n * 10
        if 1 <= rev <= mx and rev == n:
            hypotheses.append(f"reverse({prev_n}) = {n}")
        rev_wrap = rev - mx if rev > mx else None
        if rev_wrap and 1 <= rev_wrap <= mx and rev_wrap == n:
            hypotheses.append(f"reverse({prev_n}) wrap = {n}")
        # Digit-sum
        ds = sum(int(c) for c in str(prev_n))
        if ds == n:
            hypotheses.append(f"digit-sum({prev_n}) = {n}")

    # --- Multi-draw arithmetic ---
    if len(prev_draws) >= 2:
        d1_nums = sorted(prev_draws[-1]["numbers"])
        d2_nums = sorted(prev_draws[-2]["numbers"])
        # Position-wise sum / diff / avg
        for i in range(min(len(d1_nums), len(d2_nums))):
            for op, label in [
                (d1_nums[i] + d2_nums[i], f"P{i+1}_sum"),
                (abs(d1_nums[i] - d2_nums[i]), f"P{i+1}_diff"),
                ((d1_nums[i] + d2_nums[i]) // 2, f"P{i+1}_avg"),
            ]:
                if op == n:
                    hypotheses.append(f"last2 {label} = {n}")

    # --- P-position running sums (N=2..5) ---
    for N in [2, 3, 4, 5]:
        if len(prev_draws) >= N:
            for pos in range(min(5, len(prev_draws[-1]["numbers"]))):
                s = sum(sorted(d["numbers"])[pos] for d in prev_draws[-N:])
                if 1 <= s <= mx and s == n:
                    hypotheses.append(f"Σ(last {N} P{pos+1}s) = {n}")

    # --- Star math / rare echo extensions ---
    if mode == "euro":
        last_stars = last.get("stars", [])
        if len(last_stars) == 2:
            a, b = sorted(last_stars)
            for v, lbl in [(a * b, f"⭐{a}×⭐{b}"),
                           (a + b * 2, f"⭐{a}+2⭐{b}"),
                           (a * 10 + b, f"concat ⭐{a}|⭐{b}"),
                           (b * 10 + a, f"concat ⭐{b}|⭐{a}")]:
                if 1 <= v <= mx and v == n:
                    hypotheses.append(f"star-extended {lbl} = {n}")

    # --- Date-derived transforms ---
    dd, mm, yyyy = target_date.split(".")
    d, m, y = int(dd), int(mm), int(yyyy)
    y2 = y % 100
    date_candidates = {
        f"D+Y2={d+y2}": d + y2,
        f"M+Y2={m+y2}": m + y2,
        f"D*M={d*m}": d * m,
        f"D+M*2={d+m*2}": d + m * 2,
        f"D-M+Y2={d-m+y2}": d - m + y2,
        f"(D*10+M)%mx={(d*10+m)%mx}": (d * 10 + m) % mx or mx,
        f"(M*10+D)%mx={(m*10+d)%mx}": (m * 10 + d) % mx or mx,
        f"dsum={d+m+y2}": d + m + y2,
        f"D^2-M={d*d-m}": d * d - m,
    }
    for lbl, v in date_candidates.items():
        if v == n:
            hypotheses.append(f"date-math {lbl}")

    # --- Seed-adjacency (was n a ±1/±2 of a recent seed number?) ---
    recent_mains = set()
    for d_ in prev_draws:
        recent_mains.update(d_["numbers"])
    for delta in [-3, -2, 2, 3]:
        x = n + delta
        if x in recent_mains:
            hypotheses.append(f"±{abs(delta)} of recent {x}")

    # --- Gap echoes ---
    if len(last["numbers"]) >= 5:
        nums = sorted(last["numbers"])
        for i in range(len(nums) - 1):
            gap = nums[i+1] - nums[i]
            if gap == n:
                hypotheses.append(f"last draw gap({nums[i]}->{nums[i+1]}) = {n}")

    # --- Star→main concat/transform ---
    if mode == "euro" and last.get("stars"):
        for s in last["stars"]:
            for tgt, lbl in [(s * 10, f"⭐{s}×10"),
                             (s + 25, f"⭐{s}+25 (euro circle)"),
                             (s + 21, f"⭐{s}+21")]:
                if 1 <= tgt <= mx and tgt == n:
                    hypotheses.append(f"star-to-main {lbl} = {n}")

    # --- Rare-compact historical echo (any rare in last 30 draws?) ---
    for d_ in draws_before[-30:]:
        if _is_rare_compact(d_, mode):
            if n in d_["numbers"]:
                hypotheses.append(f"rare-compact seed {d_['date']} held {n}")

    # --- Absolute silence: how long since this n last appeared? ---
    gap = 0
    for d_ in reversed(draws_before):
        gap += 1
        if n in d_["numbers"]:
            break
    else:
        gap = 9999
    if gap > 15:
        hypotheses.append(f"deep silence: {gap} draws since last appearance")

    return hypotheses


# ─────────────────────────────────────────────────────────────
# BACKTEST
# ─────────────────────────────────────────────────────────────
def backtest(mode: str, last_n: int = 20, explain: bool = False,
             pool_threshold: int = 2) -> dict:
    target_draws = load_recent_draws(mode, last_n)
    if not target_draws:
        return {"error": "no draws"}

    results = []
    hit_3p = []
    hit_2p = []
    pool_size_3p = []
    pool_size_2p = []
    position_rank_hits = {"top3": 0, "top5": 0, "top12": 0, "missed": 0, "total": 0}
    miss_catalog = []  # (date, missed_n, hypotheses)

    all_miss_signals = Counter()

    for d in target_draws:
        target_date = d["date"]
        actual_mains = d["numbers"]
        actual_stars = d.get("stars", [])
        draws_before = load_draws(mode, target_date)
        if len(draws_before) < 30:
            continue
        sim = run_simulator(target_date, mode, actual_mains, actual_stars)
        v = sim.get("validation", {})
        results.append({
            "date": target_date,
            "actual": actual_mains,
            "hits_3p": v.get("hits_in_3plus_lens", []),
            "hits_2p": v.get("hits_in_2plus_lens", []),
            "pool_3p": v.get("total_3plus_pool", 0),
            "pool_2p": v.get("total_2plus_pool", 0),
            "position_hits": v.get("position_hits", []),
        })
        hit_3p.append(len(v.get("hits_in_3plus_lens", [])))
        hit_2p.append(len(v.get("hits_in_2plus_lens", [])))
        pool_size_3p.append(v.get("total_3plus_pool", 0))
        pool_size_2p.append(v.get("total_2plus_pool", 0))
        for ph in v.get("position_hits", []):
            position_rank_hits["total"] += 1
            if ph["in_top3"]:
                position_rank_hits["top3"] += 1
            elif ph["in_top5"]:
                position_rank_hits["top5"] += 1
            elif ph["in_top12"]:
                position_rank_hits["top12"] += 1
            else:
                position_rank_hits["missed"] += 1

        # Find misses: actual winners NOT in 2+ pool
        two_plus_set = set(v.get("hits_in_2plus_lens", []))
        actual_set = set(actual_mains)
        missed = sorted(actual_set - two_plus_set)
        if explain and missed:
            for miss_n in missed:
                hyps = explain_miss(miss_n, target_date, mode, draws_before)
                miss_catalog.append({
                    "date": target_date,
                    "n": miss_n,
                    "hypotheses": hyps,
                })
                # Track which signals show up across misses
                for h in hyps:
                    # Take first token as signal family
                    family = h.split(" ")[0] if " " in h else h
                    all_miss_signals[family] += 1

    out = {
        "mode": mode,
        "draws_tested": len(results),
        "pool_threshold": pool_threshold,
        "avg_hits_3plus_pool": round(mean(hit_3p), 2) if hit_3p else 0,
        "avg_hits_2plus_pool": round(mean(hit_2p), 2) if hit_2p else 0,
        "avg_pool_size_3plus": round(mean(pool_size_3p), 1) if pool_size_3p else 0,
        "avg_pool_size_2plus": round(mean(pool_size_2p), 1) if pool_size_2p else 0,
        "coverage_3plus_pct": round(100 * mean(hit_3p) / (5 if mode == "euro" else 6), 1) if hit_3p else 0,
        "coverage_2plus_pct": round(100 * mean(hit_2p) / (5 if mode == "euro" else 6), 1) if hit_2p else 0,
        "position_accuracy": position_rank_hits,
        "per_draw": results,
    }
    if explain:
        out["miss_catalog"] = miss_catalog
        out["miss_signal_frequency"] = dict(all_miss_signals.most_common(20))
    return out


def format_backtest(r: dict) -> str:
    if r.get("error"):
        return f"ERROR: {r['error']}"
    L = []
    L.append("🎻🎧 BACKTEST HARNESS")
    L.append("═" * 72)
    L.append(f"Mode: {r['mode'].upper()}  ·  Draws tested: {r['draws_tested']}")
    total_pos = 5 if r["mode"] == "euro" else 6
    L.append(f"Avg hits in 3+ pool: {r['avg_hits_3plus_pool']} / {total_pos}  ({r['coverage_3plus_pct']}% coverage)")
    L.append(f"Avg hits in 2+ pool: {r['avg_hits_2plus_pool']} / {total_pos}  ({r['coverage_2plus_pct']}% coverage)")
    L.append(f"Avg pool size — 3+: {r['avg_pool_size_3plus']}  ·  2+: {r['avg_pool_size_2plus']}")
    L.append("")
    pa = r["position_accuracy"]
    if pa["total"]:
        L.append("🎯 Position accuracy (out of all positions across all draws):")
        L.append(f"  TOP3: {pa['top3']}/{pa['total']} ({100*pa['top3']/pa['total']:.0f}%)")
        L.append(f"  TOP5: {pa['top3']+pa['top5']}/{pa['total']} ({100*(pa['top3']+pa['top5'])/pa['total']:.0f}%)")
        L.append(f"  TOP12: {pa['top3']+pa['top5']+pa['top12']}/{pa['total']} ({100*(pa['top3']+pa['top5']+pa['top12'])/pa['total']:.0f}%)")
        L.append(f"  MISSED entirely: {pa['missed']}/{pa['total']} ({100*pa['missed']/pa['total']:.0f}%)")
        L.append("")
    L.append("Per-draw summary:")
    L.append("-" * 72)
    for d in r["per_draw"]:
        L.append(f"  {d['date']}  actual={d['actual']}  3+hits={d['hits_3p']} ({len(d['hits_3p'])}/5)  2+hits={d['hits_2p']} ({len(d['hits_2p'])}/5)")

    if r.get("miss_catalog"):
        L.append("")
        L.append("🔍 MISS CATALOG — winners NOT in 2+ pool (where the NEXT laws hide)")
        L.append("═" * 72)
        # Group by date
        by_date = defaultdict(list)
        for m in r["miss_catalog"]:
            by_date[m["date"]].append(m)
        for date, items in sorted(by_date.items()):
            L.append(f"  📅 {date}:")
            for m in items:
                hyps = m["hypotheses"][:6]  # cap top 6 per miss
                if hyps:
                    L.append(f"    • {m['n']:>2}  could be: {' | '.join(hyps)}")
                else:
                    L.append(f"    • {m['n']:>2}  (no transform hypothesis found — TRULY hidden)")
        L.append("")
        L.append("🌟 SIGNAL FAMILIES appearing across misses (candidate new laws):")
        L.append("-" * 72)
        for family, count in list(r["miss_signal_frequency"].items())[:15]:
            L.append(f"  {count:>3} × {family}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["euro", "swiss"], required=True)
    ap.add_argument("--last", type=int, default=20)
    ap.add_argument("--explain-misses", action="store_true")
    args = ap.parse_args()

    r = backtest(args.mode, args.last, explain=args.explain_misses)
    print(format_backtest(r))


if __name__ == "__main__":
    main()
