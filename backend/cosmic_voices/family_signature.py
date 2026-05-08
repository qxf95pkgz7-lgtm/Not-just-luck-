"""
🍽️ FAMILY SIGNATURE LENS — `cosmic_voices/family_signature.py`
==============================================================
DJ canon (Session 35, 07.05.2026):

> "Every d has family numbers. Rare event = 4 in same family.
>  Stats can read it. d7 d8 d4 → 2-3.  First 3 d were 3-1-1. You got it?"

The decade-family signature of a draw classifies its 5 mains by decade:
  1-9, 10s, 20s, 30s, 40s — sorted by count desc → e.g. "3-1-1" or "2-2-1".

This lens feeds E with **pure dry historical statistics from the last 5
years of Q2 Euro draws**, so the engine can shape d-numbers by them.

⚠️  SNEAKY UNIVERSE CANON
A signature with 0% historical rate STILL requires a minimum of **3
tickets** in the symphony. The cosmos doesn't read its own record book.
0% in 5 yrs = "no chance" historically — but the universe is sneaky and
will fire it the moment we stop covering it.

Output structure:
  • current_q2_sequence  — this year's d-by-d signatures so far
  • base_rates           — % of each signature in the 5-yr window
  • position_bias        — for each d-pos, top signatures
  • transition_matrix    — after sig X, what comes next
  • family_feeding       — Q2 family imbalance so far (starved/overfed)
  • projected_tonight    — top 3 signatures for the upcoming d (by combining lenses)
  • min_tickets_per_sig  — 3 minimum (sneaky universe canon)
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def family_of(n: int) -> str:
    """Decade family of a Euro main (1..50)."""
    if 1 <= n <= 9:
        return "1-9"
    if 10 <= n <= 19:
        return "10s"
    if 20 <= n <= 29:
        return "20s"
    if 30 <= n <= 39:
        return "30s"
    return "40s"


def signature_of(mains: List[int]) -> Tuple[str, Dict[str, int]]:
    """Return ('3-1-1', {'10s': 3, '30s': 1, '40s': 1}) for a draw."""
    fams = Counter(family_of(n) for n in mains)
    counts = sorted(fams.values(), reverse=True)
    return "-".join(str(c) for c in counts), dict(fams)


# DJ canon: Euro Q2 starts 07.04 (03.04 transition skipped), no New-Year skip Q1
def _euro_quarter(dt: datetime) -> int:
    if (dt.month, dt.day) >= (10, 7):
        return 4
    if (dt.month, dt.day) >= (7, 7):
        return 3
    if (dt.month, dt.day) >= (4, 7):
        return 2
    if (dt.month, dt.day) >= (1, 2):
        return 1
    return 4


def _q2_draws_in_window(draws: List[Dict], target_dt: datetime,
                         years_back: int = 5) -> Dict[int, List[Dict]]:
    """Return {year: [draws...]} for Q2 of each year in the rolling 5-yr window."""
    target_year = target_dt.year
    by_year: Dict[int, List[Dict]] = defaultdict(list)
    for d in draws:
        if d["year"] in range(target_year - years_back, target_year + 1):
            if d["quarter"] == 2:
                by_year[d["year"]].append(d)
    for y in by_year:
        by_year[y].sort(key=lambda x: x["dt"])
    return by_year


def family_signature_stats(target_dt: datetime, draws: List[Dict],
                            years_back: int = 5) -> Dict:
    """Compute dry historical signature statistics for the 5-yr Q2 Euro window
    relative to `target_dt`. `draws` should come from year_d_ledger.load_draws.

    Args:
        target_dt: target draw date (used to anchor "current Q2" + position)
        draws: full chronological draw list with 'dt', 'p', 'year', 'quarter'
        years_back: how many years of Q2 data to include (default 5)
    """
    by_year_q2 = _q2_draws_in_window(draws, target_dt, years_back=years_back)

    # ── 1. Current year Q2 sequence + d-position of target
    current = by_year_q2.get(target_dt.year, [])
    current_seq = []
    for i, d in enumerate(current, 1):
        sig, fams = signature_of(d["p"])
        current_seq.append({
            "d_pos": i,
            "date": d["date"],
            "mains": d["p"],
            "signature": sig,
            "families": fams,
        })
    target_d_pos = len(current_seq) + 1  # the upcoming draw is d_(N+1)

    # ── 2. Base rates across the 5-yr window
    sig_counts = Counter()
    by_d_pos: Dict[int, Counter] = defaultdict(Counter)  # d_pos → Counter(sig)
    transitions: Dict[str, Counter] = defaultdict(Counter)
    for year, year_draws in by_year_q2.items():
        if year == target_dt.year:
            # Only use historical years' fully realized sequences for base rates
            year_draws_for_base = [d for d in year_draws if d["dt"] < target_dt]
        else:
            year_draws_for_base = year_draws
        sigs = [signature_of(d["p"])[0] for d in year_draws_for_base]
        for i, s in enumerate(sigs, 1):
            sig_counts[s] += 1
            if i <= 12:
                by_d_pos[i][s] += 1
        for i in range(len(sigs) - 1):
            transitions[sigs[i]][sigs[i + 1]] += 1
    total = sum(sig_counts.values())

    base_rates = []
    for s, c in sig_counts.most_common():
        base_rates.append({
            "signature": s,
            "count": c,
            "pct": round(100 * c / total, 1) if total else 0,
        })

    # ── 3. Position-d bias — for the target_d_pos, top signatures historically
    pos_top = []
    if target_d_pos in by_d_pos:
        pos_total = sum(by_d_pos[target_d_pos].values())
        for s, c in by_d_pos[target_d_pos].most_common():
            pos_top.append({
                "signature": s,
                "count": c,
                "pct": round(100 * c / pos_total, 1) if pos_total else 0,
            })

    # ── 4. Transition probability — from the last realized signature to next
    transition_top = []
    last_sig = current_seq[-1]["signature"] if current_seq else None
    if last_sig and last_sig in transitions:
        nxt = transitions[last_sig]
        nxt_total = sum(nxt.values())
        for s, c in nxt.most_common():
            transition_top.append({
                "signature": s,
                "count": c,
                "pct": round(100 * c / nxt_total, 1) if nxt_total else 0,
            })

    # ── 5. Family feeding — current Q2 imbalance
    feeding = Counter()
    for d in current:
        for n in d["p"]:
            feeding[family_of(n)] += 1
    feed_total = sum(feeding.values()) or 1
    fam_status = []
    for f in ["1-9", "10s", "20s", "30s", "40s"]:
        c = feeding[f]
        pct = round(100 * c / feed_total, 1)
        if c <= 4 and len(current) >= 6:
            tag = "STARVED"
        elif pct >= 30:
            tag = "OVERFED"
        else:
            tag = "balanced"
        fam_status.append({
            "family": f, "fed_count": c, "pct": pct, "status": tag,
        })
    starved = [f["family"] for f in fam_status if f["status"] == "STARVED"]
    overfed = [f["family"] for f in fam_status if f["status"] == "OVERFED"]

    # ── 6. Hot-streak alarm — has any rare signature been overfired this year?
    streak_alarm = []
    if current_seq:
        recent_sigs = [c["signature"] for c in current_seq[-5:]]
        streak_counts = Counter(recent_sigs)
        for s, hits in streak_counts.items():
            base = next((b["pct"] for b in base_rates if b["signature"] == s), 0)
            streak_pct = 100 * hits / len(recent_sigs)
            if base and streak_pct >= 3 * base and hits >= 3:
                streak_alarm.append({
                    "signature": s,
                    "hits_in_last_5": hits,
                    "streak_pct": round(streak_pct, 1),
                    "base_pct": base,
                    "ratio_x": round(streak_pct / base, 1) if base else None,
                })

    # ── 7. Project tonight — fuse position bias + transition
    proj = Counter()
    for entry in pos_top:
        proj[entry["signature"]] += entry["pct"]
    for entry in transition_top:
        proj[entry["signature"]] += entry["pct"]
    projected_tonight = []
    for s, total_score in proj.most_common():
        projected_tonight.append({
            "signature": s,
            "fused_score": round(total_score, 1),
        })

    return {
        "target_d_pos": target_d_pos,
        "years_in_window": list(sorted(by_year_q2.keys())),
        "current_q2_sequence": current_seq,
        "base_rates_5y": base_rates,
        "total_q2_draws_5y": total,
        "position_bias_d{}".format(target_d_pos): pos_top,
        "transition_after_{}".format(last_sig): transition_top if last_sig else [],
        "last_signature": last_sig,
        "family_feeding": fam_status,
        "starved_families": starved,
        "overfed_families": overfed,
        "hot_streak_alarm": streak_alarm,
        "projected_tonight": projected_tonight[:5],
        # ── SNEAKY UNIVERSE CANON ──
        "min_tickets_per_signature": 3,
        "sneaky_universe_canon": (
            "Even a 0% historical rate STILL requires a minimum of 3 tickets "
            "covering that signature. The cosmos doesn't read its own record "
            "book — 0% in 5 years means it will fire the moment we stop "
            "covering it. NEVER drop coverage below 3 tickets per shape."
        ),
        "rule": (
            "Signature stats — last {} years Q2 Euro. Read base rates + "
            "position bias + transition + family feeding TOGETHER. The "
            "cosmos owes the starved family. The hot-streak alarm marks "
            "exhausted signatures (rare-shapes overfired = mean reversion)."
        ).format(years_back),
    }
