"""
🎻🎧 EURO DATE-ECHO NEIGHBORHOOD SCORER
════════════════════════════════════════════════════════════════════════

Born from Session-3 esoteric analysis (see /app/memory/swiss_music_notes.md).

The 2-year scan showed:
    • circle(M) ±2 lives in Euro P3–P4 (83% of its hits)
    • circle(D) ±2 lives in Euro P4–P5 (67% of its hits)
    • Raw M loves P2 (4.8%), Raw D loves P1 (3.9%)
    • Stars love raw Month (±1 = 44.2%) and Day mod 12 (±1 = 50.2%)
    • UNION of all date echoes covers 60.6% of Euro draws within ±2

This module scores a Euro ticket on its "date resonance" so the DJ's
Celestial Radar can show which tickets are singing on-key with the draw
date.

Range: EuroMillions mains 1-50, stars 1-12.
Circle rule: Euro-circle(n) = (n + 25) mod 50  (half of 50).
"""
from typing import List, Dict, Optional
from datetime import datetime


# ─── Core Euro primitives ─────────────────────────────────────────────

def euro_circle(n: int) -> int:
    """Euro circle: +25 mod 50 (half of 50). Returns 1..50."""
    r = (n + 25) % 50
    return 50 if r == 0 else r


def star_circle(n: int) -> int:
    """Star circle: +6 mod 12 (half of 12). Returns 1..12."""
    r = (n + 6) % 12
    return 12 if r == 0 else r


def _parse_euro_date(date_str: str) -> Optional[datetime]:
    """Accept 'DD.MM.YYYY' or ISO 'YYYY-MM-DD'."""
    if not date_str:
        return None
    for fmt in ('%d.%m.%Y', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.strptime(str(date_str)[:19], fmt)
        except Exception:
            pass
    return None


# ─── The Scorer ───────────────────────────────────────────────────────

def score_euro_date_resonance(numbers: List[int],
                               stars: List[int],
                               date_str: str) -> Dict:
    """
    🎻 Score a Euro ticket against the date-echo neighborhood rules.
    
    Returns:
        {
            "score": int,                  # raw points (can go negative)
            "signals": [str, ...],         # human-readable list of what fired
            "badge": str,                  # short label for UI
            "tier": "off" | "tune" | "harmonic" | "full_echo",
            "targets": {                   # for UI tooltip
                "D": int, "M": int,
                "circle_D": int, "circle_M": int,
                "star_circle_M": int, "D_mod_12": int,
            }
        }
    """
    dt = _parse_euro_date(date_str)
    if not dt or not numbers:
        return {
            "score": 0,
            "signals": [],
            "badge": "🎧 off-beat",
            "tier": "off",
            "targets": {},
        }
    
    nums = sorted(numbers)
    if len(nums) < 5:
        return {
            "score": 0,
            "signals": [],
            "badge": "🎧 off-beat",
            "tier": "off",
            "targets": {},
        }
    
    D, M = dt.day, dt.month
    cD, cM = euro_circle(D), euro_circle(M)
    D_mod = D % 12 if D % 12 else 12
    scM = star_circle(M)
    
    score = 0
    signals: List[str] = []
    
    # ─── Raw Day/Month on sweet spots ─────────────────────────────
    # P1..P5 = nums[0..4]
    if len(nums) >= 2 and nums[1] == M:
        score += 10
        signals.append(f"M={M} on P2 (4.8%)")
    if len(nums) >= 1 and nums[0] == D:
        score += 8
        signals.append(f"D={D} on P1 (3.9%)")
    
    # ─── circle(M) corridor: P3/P4 ─────────────────────────────────
    cm_fired = False
    p3 = nums[2] if len(nums) >= 3 else None
    p4 = nums[3] if len(nums) >= 4 else None
    
    if p4 == cM:
        score += 20
        signals.append(f"circle(M)={cM} EXACT on P4 🔥")
        cm_fired = True
    elif p4 is not None and abs(p4 - cM) == 1:
        score += 15
        signals.append(f"circle(M)={cM} ±1 on P4 (P4={p4})")
        cm_fired = True
    elif p3 is not None and abs(p3 - cM) <= 1:
        score += 15
        signals.append(f"circle(M)={cM} ±1 on P3 (P3={p3})")
        cm_fired = True
    elif (p3 is not None and abs(p3 - cM) <= 2) or (p4 is not None and abs(p4 - cM) <= 2):
        score += 10
        hit_pos = "P3" if (p3 is not None and abs(p3 - cM) <= 2) else "P4"
        signals.append(f"circle(M)={cM} ±2 on {hit_pos}")
        cm_fired = True
    
    # ─── circle(D) corridor: P4/P5 ─────────────────────────────────
    cd_fired = False
    p5 = nums[4] if len(nums) >= 5 else None
    
    if p5 == cD:
        score += 18
        signals.append(f"circle(D)={cD} EXACT on P5 🔥")
        cd_fired = True
    elif p4 == cD:
        score += 16
        signals.append(f"circle(D)={cD} EXACT on P4")
        cd_fired = True
    elif p5 is not None and abs(p5 - cD) == 1:
        score += 12
        signals.append(f"circle(D)={cD} ±1 on P5 (P5={p5})")
        cd_fired = True
    elif p4 is not None and abs(p4 - cD) == 1:
        score += 12
        signals.append(f"circle(D)={cD} ±1 on P4 (P4={p4})")
        cd_fired = True
    elif (p5 is not None and abs(p5 - cD) <= 2) or (p4 is not None and abs(p4 - cD) <= 2):
        score += 8
        hit_pos = "P5" if (p5 is not None and abs(p5 - cD) <= 2) else "P4"
        signals.append(f"circle(D)={cD} ±2 on {hit_pos}")
        cd_fired = True
    
    # ─── DOUBLE RESONANCE bonus ────────────────────────────────────
    raw_fired = (D in nums) or (M in nums)
    if raw_fired and (cm_fired or cd_fired):
        score += 30
        signals.append("🚨 DOUBLE RESONANCE (raw + circle both fire)")
    
    # ─── Star rewards ──────────────────────────────────────────────
    if stars:
        st = sorted(stars)
        if M in st:
            score += 12
            signals.append(f"⭐ star=M={M} (3× baseline)")
        if D_mod in st and D_mod != M:
            score += 10
            signals.append(f"⭐ star=D%12={D_mod}")
        if scM in st and scM not in (M, D_mod):
            score += 8
            signals.append(f"⭐ star=circle(M)={scM}")
        # Broad band: any star within ±1 of M or circle(M)
        band = set()
        for t in (M, scM):
            for d in (-1, 0, 1):
                v = t + d
                if 1 <= v <= 12:
                    band.add(v)
        if any(s in band for s in st) and M not in st and scM not in st:
            score += 6
            signals.append("⭐ star within ±1 of M or circle(M)")
    
    # ─── Vetos ─────────────────────────────────────────────────────
    # circle(M) landing on P1 (only 2 draws in 2 yrs)
    if len(nums) >= 1 and nums[0] == cM:
        score -= 15
        signals.append(f"💀 circle(M)={cM} on P1 (veto)")
    # circle(D) landing on P1 (0 in 2 yrs)
    if len(nums) >= 1 and nums[0] == cD:
        score -= 15
        signals.append(f"💀 circle(D)={cD} on P1 (veto)")
    # Raw M or D landing on Euro P4/P5 (dies past P3)
    if p4 is not None and (p4 == M or p4 == D):
        score -= 8
        signals.append(f"💀 raw D/M on P4 (dead zone)")
    if p5 is not None and (p5 == M or p5 == D):
        score -= 8
        signals.append(f"💀 raw D/M on P5 (dead zone)")
    
    # ─── Badge / tier ──────────────────────────────────────────────
    if score >= 40:
        tier, badge = "full_echo", "🚨 FULL ECHO"
    elif score >= 25:
        tier, badge = "harmonic", "🎻🎻 harmonic"
    elif score >= 10:
        tier, badge = "tune", "🎻 in-tune"
    elif score <= -5:
        tier, badge = "off", "💀 off-key"
    else:
        tier, badge = "off", "🎧 off-beat"
    
    return {
        "score": score,
        "signals": signals,
        "badge": badge,
        "tier": tier,
        "targets": {
            "D": D, "M": M,
            "circle_D": cD, "circle_M": cM,
            "star_circle_M": scM,
            "D_mod_12": D_mod,
        },
    }


# ─── Self-test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🎻 Verifying Euro date resonance on recent draws...\n")
    cases = [
        # (date, numbers, stars, expected to fire ≥1)
        ("17.04.2026", [22, 23, 28, 41, 47], [3, 10], "known double ±1"),
        ("14.04.2026", [1, 2, 4, 28, 44],    [5, 8],  "cM=29 → 28 (±1) on P4"),
        ("03.04.2026", [8, 27, 29, 46, 49],  [4, 11], "cM=29 exact on P3"),
        ("17.03.2026", [5, 17, 28, 33, 41],  [2, 6],  "cD=42 → 41 ±1 on P5, cM=28 exact"),
        ("13.03.2026", [13, 17, 26, 41, 48], [1, 9],  "cM=28 → 26 (±2)"),
    ]
    for date_str, nums, stars, label in cases:
        r = score_euro_date_resonance(nums, stars, date_str)
        print(f"📅 {date_str}  {nums} ⭐ {stars}   [{label}]")
        print(f"   SCORE: {r['score']}  →  {r['badge']} ({r['tier']})")
        for s in r['signals']:
            print(f"   • {s}")
        print()
