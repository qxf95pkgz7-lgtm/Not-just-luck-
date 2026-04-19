"""
🚨 RARE-EVENT CYCLE SCORER — Universal Swiss + Euro
════════════════════════════════════════════════════════════════════════

Detects the most recent "Rare Compact" draw within a lookback window
and rewards pending tickets that hold UNRELEASED seed numbers (mains
and stars that haven't re-emerged since the rare event).

Law (see /app/memory/swiss_music_notes.md SESSION 3):
    • Euro rare = P1-P4 span ≤ 7 AND P5 jump ≥ 6
    • Swiss rare = P1-P5 span ≤ 10 AND P6 jump ≥ 8
    • After a rare event the machine enters an 8-draw correction cycle
      where UNRELEASED seed numbers have elevated pressure.

Usage:
    from rare_event_scorer import score_rare_event_echo
    res = score_rare_event_echo(
        ticket_numbers=[...], ticket_stars=[...],
        recent_draws=[{"date":..., "numbers":[...], "stars":[...]}, ...],  # newest first
        mode="euro"  # or "swiss"
    )
"""
from typing import List, Dict, Optional
from datetime import datetime


def _is_rare_compact(numbers: List[int], mode: str) -> bool:
    n = sorted(numbers)
    if mode == "euro" and len(n) >= 5:
        return (n[3] - n[0]) <= 7 and (n[4] - n[3]) >= 6
    if mode == "swiss" and len(n) >= 6:
        return (n[4] - n[0]) <= 10 and (n[5] - n[4]) >= 8
    return False


def find_recent_rare_seed(recent_draws: List[Dict], mode: str,
                          lookback: int = 12) -> Optional[Dict]:
    """
    Find the most recent Rare Compact draw within the lookback window.
    `recent_draws` is newest-first.
    Returns:
        {
            "rare_date": str,
            "rare_numbers": List[int],
            "rare_stars": List[int],
            "draws_since": int,     # 1 means the rare event was the LAST draw
            "unreleased_mains": List[int],
            "unreleased_stars": List[int],
        }
        or None if no rare event in window.
    """
    if not recent_draws:
        return None
    
    rare_i = None
    for idx, dr in enumerate(recent_draws[:lookback]):
        nums = dr.get("numbers", [])
        if _is_rare_compact(nums, mode):
            rare_i = idx
            break
    
    if rare_i is None:
        return None
    
    rare = recent_draws[rare_i]
    seed_mains = set(rare.get("numbers", []))
    seed_stars = set(rare.get("stars", []) or [])
    
    # Everything drawn AFTER the rare event (indices 0..rare_i-1, newest first)
    drawn_since_mains = set()
    drawn_since_stars = set()
    for dr in recent_draws[:rare_i]:
        for x in dr.get("numbers", []):
            drawn_since_mains.add(x)
        for x in (dr.get("stars") or []):
            drawn_since_stars.add(x)
    
    unreleased_mains = sorted(seed_mains - drawn_since_mains)
    unreleased_stars = sorted(seed_stars - drawn_since_stars)
    
    return {
        "rare_date": rare.get("date"),
        "rare_numbers": sorted(seed_mains),
        "rare_stars": sorted(seed_stars),
        "draws_since": rare_i,  # 0 = rare was most recent draw
        "unreleased_mains": unreleased_mains,
        "unreleased_stars": unreleased_stars,
    }


def score_rare_event_echo(ticket_numbers: List[int],
                           ticket_stars: Optional[List[int]],
                           recent_draws: List[Dict],
                           mode: str = "euro") -> Dict:
    """
    Score a ticket for carrying UNRELEASED echoes from the most
    recent Rare Compact seed.
    
    Returns:
        {
            "score": int,            # bonus points
            "signals": [str, ...],
            "rare_seed": Dict or None,
            "unreleased_held": {"mains": [...], "stars": [...]},
            "active": bool,          # True if within 8-draw cycle window
        }
    """
    seed_info = find_recent_rare_seed(recent_draws, mode, lookback=12)
    if not seed_info:
        return {"score": 0, "signals": [], "rare_seed": None,
                "unreleased_held": {"mains": [], "stars": []}, "active": False}
    
    unrel_mains = set(seed_info["unreleased_mains"])
    unrel_stars = set(seed_info["unreleased_stars"])
    t_mains = set(ticket_numbers or [])
    t_stars = set(ticket_stars or [])
    
    held_mains = sorted(unrel_mains & t_mains)
    held_stars = sorted(unrel_stars & t_stars)
    
    score = 0
    signals: List[str] = []
    
    for n in held_mains:
        score += 15
        signals.append(f"unreleased seed echo {n} held")
    for s in held_stars:
        score += 10
        signals.append(f"unreleased ⭐ seed echo {s} held")
    
    # Cycle-close bonus: if we're within draws +1..+8 of the rare event
    draws_after = seed_info["draws_since"] + 1  # 1 = draw right after rare
    active = 1 <= draws_after <= 8
    if active and (held_mains or held_stars):
        score += 20
        signals.append(f"🚨 RARE-EVENT CYCLE active (+{draws_after} draws)")
    
    return {
        "score": score,
        "signals": signals,
        "rare_seed": {
            "date": seed_info["rare_date"],
            "numbers": seed_info["rare_numbers"],
            "stars": seed_info["rare_stars"],
            "unreleased_mains": seed_info["unreleased_mains"],
            "unreleased_stars": seed_info["unreleased_stars"],
            "draws_since": seed_info["draws_since"],
        },
        "unreleased_held": {"mains": held_mains, "stars": held_stars},
        "active": active,
    }


# ─── Self-test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Simulated: most recent draw first
    euro_recent = [
        {"date": "17.04.2026", "numbers": [22,23,28,41,47], "stars": [6,8]},
        {"date": "14.04.2026", "numbers": [1,2,4,28,44],    "stars": [5,12]},
        {"date": "10.04.2026", "numbers": [10,13,14,38,41], "stars": [6,9]},
        {"date": "07.04.2026", "numbers": [11,14,19,36,49], "stars": [6,7]},
        {"date": "03.04.2026", "numbers": [8,27,29,46,49],  "stars": [2,10]},
        {"date": "31.03.2026", "numbers": [5,8,10,33,38],   "stars": [2,7]},
        {"date": "27.03.2026", "numbers": [4,10,43,44,48],  "stars": [2,4]},
        {"date": "24.03.2026", "numbers": [12,16,17,18,27], "stars": [1,3]},  # RARE
        {"date": "20.03.2026", "numbers": [5,12,16,37,46],  "stars": [3,8]},
    ]
    seed = find_recent_rare_seed(euro_recent, "euro")
    print("🚨 Detected rare seed:", seed)
    print()
    
    test_tickets = [
        ([12, 17, 18, 29, 41], [3, 5]),   # grabs 3 unreleased mains + star 3
        ([9, 16, 22, 29, 44],  [1, 4]),   # grabs 16 + star 1
        ([1, 5, 9, 25, 47],    [6, 10]),  # carries nothing
    ]
    for nums, stars in test_tickets:
        r = score_rare_event_echo(nums, stars, euro_recent, mode="euro")
        print(f"🎫 {nums} ⭐{stars}  →  +{r['score']} points, active={r['active']}")
        for s in r['signals']:
            print(f"   • {s}")
        print()
