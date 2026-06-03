"""
🪞 DJ-Pool Builder — Session 45 Canon Fusion (DJ-taught)

Aggregates ALL Session 45 cosmic canons into a single ranked pool
(max 12 numbers) suitable for ticket generation on any target date.

Canons fused (each canon contributes "voice" votes — totaled per number):

  1. MIRROR-28 (Pair-sum 28 → sister-d-position of same Q)
       For Euro: read Q-d corresponding to digit-sum or matching component
       For Swiss: same idea on Swiss-Q

  2. MIRROR-DAY CARRIER SYMMETRY  (Law #24)
       Universal mirror-axis anchors: {3, 6, 9, 14, 19, 23, 28, 32, 33, 37}
       Auto-add 1-2 of these when target day's mirror-day-pair is in scope

  3. DAY-OF-MONTH KING / P6 AXIS  (Law #23)
       Top numbers + P6 anchor based on target_dt.day
       day=3 → P6=41 (25%)
       day=30 → P6=39 (22.7%)
       d=11 → 23 KING (29.2%)
       d=17 → 36 P5 KING (20.4%)
       (other day-of-month maps live in a lookup table below)

  4. 22-BRIDGE for Swiss  (Law #21A)
       ND_P1 + BD_P6 − 21 = 22  → ND_P1 ≈ 43 − BD_P6 (15% historical)

  5. SWISS-CIRCLE +21 CARRIERS (and Euro +25)
       Every BD-main has its +/- carrier as candidate

  6. CODEC-×10 ENCODING for Euro  (DJ-taught from Q2 2026 streak)
       (P5−25)*10 + ⭐sum or ⭐single → expected (P4-25)*10 + P3 in ND

  7. BD RAW WALK
       BD numbers themselves often return in ND (raw walk-forward)

  8. P1<10 STREAK BREAK CANON
       If BD's P1<10 streak ≥ 9, ND-P1 breakers historically ∈ {12, 23}

  9. ⭐12 STREAK PARTNER LEADERBOARD (Euro)
       Top partners when ⭐12 repeats: ⭐3 (17.2%) > ⭐1/2/7 (13.8%)

 10. STORY-COMPOSER + HUNGRY-ENGINE convergence
       Use hungry_engine multi-path top + Q2d2-sister-d2 raw + Q-mirror raw

Returns: structured pool with vote-tally + canon-receipts per number.
"""

from collections import Counter
from datetime import datetime
from typing import Dict, List


# =============================================================================
# Day-of-Month King Maps (Session 45 — built from Swiss-history scanner)
# =============================================================================
# Format: {day-of-month: { "kings": [(n, rate), ...], "p1_top": [...], "p6_top": [(n, rate)] } }
SWISS_DOM_KINGS: Dict[int, Dict] = {
    3: {
        "kings": [(41, 27.3), (17, 25.0), (26, 25.0), (35, 22.7),
                  (34, 20.5), (9, 20.5), (24, 20.5), (11, 18.2),
                  (4, 18.2), (19, 18.2), (22, 18.2)],
        "p1_top": [(2, 13.6), (4, 13.6), (3, 11.4), (5, 9.1)],
        "p6_axis": (41, 25.0),
        "lucky_top": [(1, 20.5), (3, 20.5), (4, 18.2)],
    },
    30: {
        "kings": [(39, 22.7), (1, 22.7), (10, 20.5), (7, 20.5),
                  (23, 20.5), (18, 20.5), (4, 20.5), (5, 20.5),
                  (25, 18.2), (11, 18.2), (26, 18.2), (21, 18.2), (31, 18.2)],
        "p1_top": [(1, 22.7), (2, 13.6), (3, 11.4)],
        "p6_axis": (39, 22.7),
        "lucky_top": [(5, 27.3), (3, 20.5)],
    },
    17: {
        "kings": [(36, 20.4), (40, 22.7), (16, 18.2), (8, 15.9)],
        "p1_top": [(2, 15.9), (7, 11.4), (6, 11.4), (3, 11.4)],
        "p6_axis": (40, 22.7),
        "lucky_top": [(4, 27.3), (5, 18.2), (6, 18.2)],
    },
    11: {
        "kings": [(23, 29.2), (3, 22.9), (37, 22.9), (5, 20.8),
                  (19, 20.8), (11, 18.8), (24, 18.8), (15, 18.8),
                  (31, 18.8), (33, 18.8), (32, 18.8), (14, 18.8)],
        "p1_top": [(3, 18.8), (5, 18.8), (1, 14.6), (4, 10.4)],
        "p6_axis": (37, 18.8),
        "lucky_top": [(3, 22.9), (2, 20.8)],
    },
}

# Mirror-day pair universal anchors (Law #24)
MIRROR_AXIS_UNIVERSAL = [3, 6, 9, 14, 19, 23, 28, 32, 33, 37]


def find_mirror_pair_day(d: int) -> int:
    """Return mirror-pair day: d + mirror = 28."""
    if 1 <= d <= 27:
        return 28 - d
    return -1


def build_pool(
    *,
    target_date: str,   # "dd.mm.yyyy"
    bd: Dict,           # {"date": "dd.mm.yyyy", "mains": [...], "stars": [...] OR "lucky"}
    mode: str = "swiss",  # "euro" or "swiss"
    pool_size: int = 12,
) -> Dict:
    """Build the unified DJ pool for the given target date + BD draw.

    Returns:
      {
        "pool":  [{"n": int, "votes": int, "receipts": [str, ...]}],
        "stars": [{"s": int, "votes": int}, ...] (Euro) OR [{lucky}] (Swiss),
        "canons_fired": [list of canon names],
        "summary": str,
      }
    """
    dt = datetime.strptime(target_date, "%d.%m.%Y")
    bd_mains = sorted(bd.get("mains") or [])
    bd_stars = bd.get("stars") or ([] if mode == "swiss" else [])
    bd_lucky = bd.get("lucky")

    votes = Counter()
    receipts: Dict[int, List[str]] = {}
    canons_fired: List[str] = []

    def vote(n: int, weight: int, reason: str):
        if not (1 <= n <= (50 if mode == "euro" else 42)):
            return
        votes[n] += weight
        receipts.setdefault(n, []).append(reason)

    # ─────────────────────────────────────────────────────────────────────
    # CANON 1: BD RAW WALK (universal — every BD number is a candidate)
    # ─────────────────────────────────────────────────────────────────────
    for m in bd_mains:
        vote(m, 1, f"BD raw {bd.get('date')} P-walk")
    canons_fired.append("BD_RAW_WALK")

    # ─────────────────────────────────────────────────────────────────────
    # CANON 2: CIRCLE CARRIER (+25 Euro, +21 Swiss, both ways with wrap)
    # ─────────────────────────────────────────────────────────────────────
    carrier = 25 if mode == "euro" else 21
    upper = 50 if mode == "euro" else 42
    for m in bd_mains:
        for delta in (+carrier, -carrier):
            c = m + delta
            if 1 <= c <= upper:
                vote(c, 2, f"+{delta:+d} carrier of BD-{m}")
    canons_fired.append(f"CIRCLE_CARRIER_{carrier:+d}")

    # ─────────────────────────────────────────────────────────────────────
    # CANON 3: DAY-OF-MONTH KING + P6 AXIS (Law #23 — Swiss only)
    # ─────────────────────────────────────────────────────────────────────
    if mode == "swiss":
        dom = dt.day
        kdata = SWISS_DOM_KINGS.get(dom)
        if kdata:
            for n, rate in kdata["kings"]:
                vote(n, 3, f"day={dom} King {rate}%")
            p6n, p6r = kdata["p6_axis"]
            vote(p6n, 2, f"day={dom} P6-AXIS ({p6r}%)")
            canons_fired.append(f"DOM_KING_d{dom}")

    # ─────────────────────────────────────────────────────────────────────
    # CANON 4: 22-BRIDGE (Law #21A — Swiss only)
    # ─────────────────────────────────────────────────────────────────────
    if mode == "swiss" and bd_mains:
        bd_p6 = bd_mains[-1]
        nd_p1_candidate = 43 - bd_p6
        if 1 <= nd_p1_candidate <= upper:
            vote(nd_p1_candidate, 3, f"22-Bridge (43-BD_P6={bd_p6}) ⇒ {nd_p1_candidate} (15.9%)")
            canons_fired.append("22_BRIDGE")

    # ─────────────────────────────────────────────────────────────────────
    # CANON 5: MIRROR-DAY-PAIR UNIVERSAL ANCHORS (Law #24)
    # If target_day has a mirror-pair day, add universal mirror anchors
    # ─────────────────────────────────────────────────────────────────────
    mirror_day = find_mirror_pair_day(dt.day)
    if mirror_day > 0:
        for n in MIRROR_AXIS_UNIVERSAL:
            if 1 <= n <= upper:
                vote(n, 1, f"Mirror-axis Universal (d{dt.day}↔d{mirror_day})")
        canons_fired.append(f"MIRROR_DAY_d{dt.day}_d{mirror_day}")

    # ─────────────────────────────────────────────────────────────────────
    # CANON 6: P6 = year-cap (40 for 2026) — softer canon
    # ─────────────────────────────────────────────────────────────────────
    yp = dt.year // 100
    year_cap = yp * 2
    if 1 <= year_cap <= upper:
        vote(year_cap, 1, f"Year-cap (year-prefix×2={year_cap})")
    canons_fired.append("YEAR_CAP")

    # ─────────────────────────────────────────────────────────────────────
    # CANON 7: SWISS MONTH-TRANSITION CANON (if BD month != target month)
    # ─────────────────────────────────────────────────────────────────────
    if mode == "swiss":
        try:
            bd_dt = datetime.strptime(bd.get("date"), "%d.%m.%Y")
            if bd_dt.month != dt.month:
                m_old, m_new = bd_dt.month, dt.month
                month_prod = m_old * m_new
                if 1 <= month_prod <= upper:
                    vote(month_prod, 2, f"Month-product ({m_old}×{m_new})")
                vote(m_old + yp, 2, f"Month-OLD+year ({m_old}+{yp})")
                vote(m_new + yp, 2, f"Month-NEW+year ({m_new}+{yp})")
                p1 = (bd_dt.day - 21) + dt.day
                if 1 <= p1 <= upper:
                    vote(p1, 2, f"Swiss-circle P1 ({bd_dt.day}-21+{dt.day})")
                p5 = bd_dt.day + dt.day
                if 1 <= p5 <= upper:
                    vote(p5, 2, f"Day-sum P5 ({bd_dt.day}+{dt.day})")
                canons_fired.append("MONTH_TRANSITION")
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────────────────
    # CANON 8: MIRROR-28 sister-d (Euro) — sister-d2/d5 anchors
    # (Lightweight: just add the mirror's universal-anchor numbers as soft votes)
    # ─────────────────────────────────────────────────────────────────────
    # Compute mirror-28 pairs in date components
    day = dt.day
    month = dt.month
    ys = dt.year % 100
    pairs = []
    if day + month == 28:
        pairs.append(("day+month", min(day, month)))
    if day + ys == 28:
        pairs.append(("day+year", min(day, ys)))
    if month + ys == 28:
        pairs.append(("month+year", min(month, ys)))
    if pairs:
        for src, smaller in pairs:
            # The sister-d position itself becomes a "lucky" number on the date
            vote(smaller, 1, f"Mirror-28 sister-d ({src})")
        canons_fired.append("MIRROR_28")

    # ─────────────────────────────────────────────────────────────────────
    # CANON 9: CODEC-×10 (Euro only, BD-P5 path)
    # ─────────────────────────────────────────────────────────────────────
    if mode == "euro" and bd_mains and bd_stars:
        bd_p5 = bd_mains[-1]
        if bd_p5 > 25:
            base = (bd_p5 - 25) * 10
            s_sum = sum(bd_stars)
            # codec gives a 3-digit number whose components hint ND-P3/P4 pair
            for star_path in [s_sum] + list(bd_stars):
                target_code = base + star_path
                # Solve (P4-25)*10 + P3 = target_code → P4 = 25 + (target_code // 10)
                # P3 = target_code - (P4-25)*10
                for cand_p4 in range(26, 51):
                    cand_p3 = target_code - (cand_p4 - 25) * 10
                    if 1 <= cand_p3 < cand_p4 <= 50:
                        vote(cand_p3, 1, f"Codec P3 (BD-P5 code {base}+{star_path}={target_code})")
                        vote(cand_p4, 1, f"Codec P4 (BD-P5 code {base}+{star_path}={target_code})")
            canons_fired.append("CODEC_X10")

    # ─────────────────────────────────────────────────────────────────────
    # FINAL: Rank by votes — top pool_size
    # ─────────────────────────────────────────────────────────────────────
    ranked = sorted(votes.items(), key=lambda kv: -kv[1])
    pool = []
    for n, v in ranked[:pool_size]:
        pool.append({
            "n": n,
            "votes": v,
            "receipts": receipts.get(n, []),
        })

    # ⭐ pool (Euro only — simple historical bias around BD-stars)
    star_pool = []
    if mode == "euro" and bd_stars:
        # Recommendation: ⭐12 streak partner leaderboard + 67-bridge
        priors = {
            3: ("⭐12-repeat KING partner 17.2%", 3),
            1: ("⭐12-repeat partner 13.8%", 2),
            7: ("⭐12-repeat partner 13.8% + 67-bridge", 2),
            11: ("Day-after-⭐12 KING 50%", 3),
        }
        sc = Counter()
        sr: Dict[int, List[str]] = {}
        for s in bd_stars:
            sc[s] += 1
            sr.setdefault(s, []).append("BD ⭐ raw")
        for s, (r, w) in priors.items():
            sc[s] += w
            sr.setdefault(s, []).append(r)
        for s, v in sorted(sc.items(), key=lambda kv: -kv[1])[:6]:
            star_pool.append({"s": s, "votes": v, "receipts": sr.get(s, [])})

    return {
        "target_date": target_date,
        "mode": mode,
        "bd": {"date": bd.get("date"), "mains": bd_mains, "stars": bd_stars, "lucky": bd_lucky},
        "pool": pool,
        "stars": star_pool,
        "canons_fired": canons_fired,
        "pool_size": len(pool),
        "summary": (
            f"DJ-Pool of {len(pool)} numbers for {target_date} {mode}. "
            f"Canons fired: {len(canons_fired)}. "
            f"Top vote-getter: n={pool[0]['n']} with {pool[0]['votes']} votes." if pool else "no pool"
        ),
    }
