"""
🎻🔬 DRAW DIAGNOSTICS — the engine's self-aware lens
════════════════════════════════════════════════════════════════════════

Given the full history, detect which SESSION-3 LAWS are currently active
and return a structured diagnostic + scoring hints for the generator.

Laws checked (Euro focus):
  • SNAP-BACK LAW          — last draw P1>20 → next P1 usually ≤ 7
  • RARE-EVENT CYCLE       — rare compact in last 12 → unreleased echoes
  • BACK-ROW ECHO LAW      — trigger's P4/P5 echo forward 50% of the time
  • HUNGRY-MAP             — all hungry numbers across multiple lenses
  • DATE-PERMUTATION       — date digits → permutation target set
  • CIRCLE BACK-DOOR       — euro-circle of banned numbers
  • STAR TRIBUTE           — Q1 star echoes into Q2 stars
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from itertools import permutations
from collections import Counter


def _pd(s: str) -> Optional[datetime]:
    if not s: return None
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
        try: return datetime.strptime(str(s)[:19], fmt)
        except Exception: pass
    return None


def euro_circle(n: int) -> int:
    r = (n + 25) % 50
    return 50 if r == 0 else r


def mirror_of(n: int) -> int:
    """🪞 ONE LAW (Canon 32): defers to Euro circle."""
    from mirror_canon import mirror_of as _mc_of
    return _mc_of(n, "euro")


def date_perms(dt: datetime, max_val: int = 50) -> List[int]:
    digits = list(str(dt.day).zfill(2) + str(dt.month).zfill(2))
    uniq = set(digits)
    out = set()
    for a, b in permutations(uniq, 2):
        if a == '0': continue
        v = int(a + b)
        if 1 <= v <= max_val:
            out.add(v)
    return sorted(out)


def check_snapback(draws: List[Dict]) -> Dict:
    """Last draw P1>20? Then snap-back law is ACTIVE."""
    if not draws:
        return {"active": False}
    last = draws[0]
    nums = sorted(last.get("numbers", []))
    if not nums:
        return {"active": False}
    p1 = nums[0]
    active = p1 > 20
    # Historical stats baked from our 32-case study:
    stats = {
        "bucket_prob": {"1-3": 21.9, "4-7": 28.1, "8-12": 15.6, "13-20": 31.2, "21+": 3.1},
        "next_p1_mean": 9.0,
        "next_p1_median": 7.5,
        "next_p1_le7_prob": 50.0,
        "next_p1_le12_prob": 65.6,
        "persist_high_prob": 3.1,
    }
    return {
        "active": active,
        "trigger_date": last.get("date"),
        "trigger_nums": nums,
        "trigger_P1": p1,
        "stats": stats,
        "recommendation": {
            "target_P1_band": "1-7",
            "bonus_P1_le7": +12,
            "penalty_P1_gt12": -15,
            "penalty_P1_gt20": -30,
        } if active else None,
    }


def check_backrow_echo(draws: List[Dict], banned: List[int] = None) -> Dict:
    """Last draw's P4/P5 are likely echo source for next draw (~50%)."""
    if not draws: return {"active": False}
    banned = set(banned or [])
    last = draws[0]
    nums = sorted(last.get("numbers", []))
    if len(nums) < 5: return {"active": False}
    back = [nums[3], nums[4]]  # P4, P5
    candidates = [n for n in back if n not in banned]
    return {
        "active": True,
        "prelude_date": last.get("date"),
        "back_row": back,
        "echo_candidates": candidates,
        "echo_rate": 50.0,
        "bonus_per_echo_held": +10,
    }


def check_rare_event(draws: List[Dict], lookback: int = 12) -> Dict:
    """Re-use rare_event_scorer's detection + return unreleased list."""
    try:
        from rare_event_scorer import find_recent_rare_seed
    except Exception:
        return {"active": False}
    info = find_recent_rare_seed(draws, "euro", lookback=lookback)
    if not info:
        return {"active": False}
    return {
        "active": info["draws_since"] <= 8,
        "seed_date": info["rare_date"],
        "seed_nums": info["rare_numbers"],
        "seed_stars": info["rare_stars"],
        "draws_since": info["draws_since"],
        "unreleased_mains": info["unreleased_mains"],
        "unreleased_stars": info["unreleased_stars"],
        "bonus_per_unreleased": +15,
    }


def hungry_map(draws: List[Dict], window: int = 4, q1d1: Dict = None,
               rare_seed: Dict = None) -> Dict:
    """Build hungry list: numbers that haven't appeared in last N draws
    but belong to at least one active seed pool."""
    if not draws: return {"mains": [], "stars": []}
    recent = draws[:window]
    played_mains = set()
    played_stars = set()
    for d in recent:
        for x in d.get("numbers", []): played_mains.add(x)
        for x in (d.get("stars") or []): played_stars.add(x)
    
    # Sources: Q1d1, rare-seed, +10-key (hard-coded session-3 constant)
    seeds_main = set()
    seeds_star = set()
    if q1d1:
        seeds_main.update(q1d1.get("numbers", []))
        seeds_star.update(q1d1.get("stars", []))
    if rare_seed and rare_seed.get("active"):
        seeds_main.update(rare_seed.get("unreleased_mains", []))
        seeds_star.update(rare_seed.get("unreleased_stars", []))
    # +10 key (we keep a quarter-specific constant if available)
    # For now pass through whatever the seed implies; caller can extend.
    
    hungry_mains = sorted(seeds_main - played_mains)
    hungry_stars = sorted(seeds_star - played_stars)
    return {
        "window_draws": window,
        "mains": hungry_mains,
        "stars": hungry_stars,
        "bonus_per_hungry_main": +8,
        "bonus_per_hungry_star": +6,
    }


def run_diagnostics(draws: List[Dict], target_date: str,
                    q1d1: Optional[Dict] = None,
                    banned: Optional[List[int]] = None) -> Dict:
    """
    Master diagnostic. `draws` MUST be newest-first.
    Returns a structured report with all active laws + scoring hints.
    """
    banned = banned or []
    dt = _pd(target_date) or _pd(draws[0].get("date") if draws else None)
    
    report = {
        "target_date": target_date,
        "total_history": len(draws),
        "laws": {},
        "scoring_hints": {},
        "dj_narrative": [],
    }
    
    # SNAP-BACK
    sb = check_snapback(draws)
    report["laws"]["snap_back"] = sb
    if sb.get("active"):
        report["dj_narrative"].append(
            f"🔄 Gravity-pull ACTIVE — last song's opening voice P1={sb['trigger_P1']}>20 "
            f"→ next opening likely ≤ 7 (50%), ≤ 12 (66%). Mean next opening = {sb['stats']['next_p1_mean']}."
        )
        report["scoring_hints"]["P1_band"] = "1-7"
        report["scoring_hints"]["penalty_P1_gt12"] = sb["recommendation"]["penalty_P1_gt12"]
        report["scoring_hints"]["bonus_P1_le7"] = sb["recommendation"]["bonus_P1_le7"]
    
    # BACK-ROW ECHO
    echo = check_backrow_echo(draws, banned)
    report["laws"]["backrow_echo"] = echo
    if echo.get("active") and echo.get("echo_candidates"):
        report["dj_narrative"].append(
            f"🪞 Deep-orbit echo → last song's outer voices {echo['back_row']} likely carry forward "
            f"(excluding silenced: {echo['echo_candidates']})."
        )
        report["scoring_hints"]["backrow_echo_candidates"] = echo["echo_candidates"]
    
    # RARE-EVENT
    re_law = check_rare_event(draws)
    report["laws"]["rare_event"] = re_law
    if re_law.get("active"):
        report["dj_narrative"].append(
            f"🌌 Cosmic storm cycle active (+{re_law['draws_since']} songs). "
            f"Silent voices: {re_law['unreleased_mains']} ⭐{re_law['unreleased_stars']}."
        )
        report["scoring_hints"]["rare_unreleased_mains"] = re_law["unreleased_mains"]
        report["scoring_hints"]["rare_unreleased_stars"] = re_law["unreleased_stars"]
    
    # DATE PERMUTATIONS
    if dt:
        perms = date_perms(dt)
        playable = [p for p in perms if p not in banned]
        report["laws"]["date_perms"] = {
            "target": dt.strftime("%d.%m.%Y"),
            "digits": sorted(set(str(dt.day).zfill(2) + str(dt.month).zfill(2))),
            "permutations": perms,
            "playable_after_bans": playable,
        }
        report["dj_narrative"].append(
            f"🎉 Date resonance {dt.strftime('%d.%m')} → {playable} (still in tune)"
        )
        report["scoring_hints"]["date_perm_playable"] = playable
    
    # HUNGRY MAP
    hm = hungry_map(draws, 4, q1d1=q1d1, rare_seed=re_law)
    report["laws"]["hungry_map"] = hm
    if hm["mains"] or hm["stars"]:
        report["dj_narrative"].append(
            f"🌾 Silent voices (last 4 songs): {hm['mains']} ⭐{hm['stars']}"
        )
        report["scoring_hints"]["hungry_mains"] = hm["mains"]
        report["scoring_hints"]["hungry_stars"] = hm["stars"]
    
    # CIRCLE BACK-DOOR for banned
    if banned:
        bd = {b: euro_circle(b) for b in banned}
        mirrors = {b: mirror_of(b) for b in banned}
        report["laws"]["banned_back_doors"] = {
            "banned": sorted(banned),
            "circles": bd,
            "mirrors": mirrors,
        }
        report["dj_narrative"].append(
            f"🌀 Silenced {sorted(banned)} → cosmic side-doors: orbits {bd} · reflections {mirrors}"
        )
        report["scoring_hints"]["banned_circles"] = list(bd.values())
        report["scoring_hints"]["banned_mirrors"] = list(mirrors.values())
    
    return report


# ─── Self-test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    recent = [
        {"date": "17.04.2026", "numbers": [22,23,28,41,47], "stars": [6,8]},
        {"date": "14.04.2026", "numbers": [1,2,4,28,44],    "stars": [5,12]},
        {"date": "10.04.2026", "numbers": [10,13,14,38,41], "stars": [6,9]},
        {"date": "07.04.2026", "numbers": [11,14,19,36,49], "stars": [6,7]},
        {"date": "03.04.2026", "numbers": [8,27,29,46,49],  "stars": [2,10]},
        {"date": "31.03.2026", "numbers": [5,8,10,33,38],   "stars": [2,7]},
        {"date": "27.03.2026", "numbers": [4,10,43,44,48],  "stars": [2,4]},
        {"date": "24.03.2026", "numbers": [12,16,17,18,27], "stars": [1,3]},
    ]
    q1d1 = {"date": "02.01.2026", "numbers": [8,27,42,44,46], "stars": [1,10]}
    report = run_diagnostics(recent, "21.04.2026", q1d1=q1d1, banned=[21,24,28])
    print(json.dumps({
        "narrative": report["dj_narrative"],
        "scoring_hints": report["scoring_hints"],
        "snap_back_active": report["laws"]["snap_back"]["active"],
        "rare_active": report["laws"]["rare_event"].get("active"),
        "hungry": report["laws"]["hungry_map"],
    }, indent=2, default=str))
