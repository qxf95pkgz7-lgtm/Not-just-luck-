"""
🪞🌱 DJ CALL SCORER — the engine's new senses
════════════════════════════════════════════════════════════════════════

Three rule families derived from DJ Session-3:
  1. MIRROR-OF-BANNED  — when the DJ bans a number, its mirror (28−n for n≤27,
     56−n for n≥29) becomes the back-door twin. Reward tickets that hold it.
  2. CIRCLE-BACK-DOOR — reward the euro-circle of any banned number when it
     lands at P4 or P5.
  3. Q1-SEED-ECHO UNPLAYED — Q1 mains that haven't yet appeared as mains in
     Q2 carry a hunger bonus.
  4. DJ-LOCK MATCHES    — the P1 / P2 / Stars the DJ has specifically locked.
"""
import json
import os
from typing import List, Dict, Optional


def mirror_of(n: int) -> int:
    """Pair-sum 28 mirror for n≤27 (pivot 14); pair-sum 56 mirror for n≥29
    (pivot 28). n=28 is self-mirror."""
    if n <= 27:
        return 28 - n
    if n >= 29:
        return 56 - n
    return 28  # n == 28


def euro_circle(n: int) -> int:
    r = (n + 25) % 50
    return 50 if r == 0 else r


def load_dj_calls(path: str = "/app/backend/dj_calls.json") -> Dict:
    """Load the DJ's current session calls (bans + locks).
    Returns empty shell if missing so the scorer stays harmless."""
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"euro": {}, "swiss": {}}


def score_dj_calls(numbers: List[int],
                    stars: Optional[List[int]],
                    mode: str = "euro",
                    q2_played_mains: Optional[set] = None) -> Dict:
    """
    Score a ticket against the DJ's session calls.
    Returns:
        {
            "score": int,
            "signals": [str],
            "badge": "🎻 dj-tuned" | "🎧 neutral" | "💀 anti-dj",
            "lock_matches": {...},
            "back_door_hits": [...],
            "mirror_of_banned": [...],
            "seed_echoes": [...],
        }
    """
    calls = load_dj_calls()
    cfg = calls.get(mode, {}) or {}
    score = 0
    signals: List[str] = []
    
    banned = set(cfg.get("banned_mains", []) or [])
    p1_lock = cfg.get("p1_lock")
    p2_lock = cfg.get("p2_lock")
    star_locks = set(cfg.get("star_locks", []) or [])
    star_extensions = set(cfg.get("star_extensions", []) or [])
    triple_lock = set(cfg.get("triple_lock_mains", []) or [])
    back_row_pool = set(cfg.get("expanded_back_row", []) or [])
    q1_unplayed = set(cfg.get("q1_seeds_unplayed_in_q2_mains", []) or [])
    back_door = cfg.get("back_door_circles", {}) or {}
    
    t_mains = list(numbers or [])
    t_mains_sorted = sorted(t_mains)
    t_stars = set(stars or [])
    
    # 🚫 BAN penalty — carrying a banned number kills the ticket
    ban_hits = set(t_mains) & banned
    if ban_hits:
        score -= 25 * len(ban_hits)
        signals.append(f"💀 banned hit {sorted(ban_hits)} (−{25*len(ban_hits)})")
    
    # 🎯 DJ P1 / P2 / STAR locks
    lock_matches = {}
    if p1_lock is not None and len(t_mains_sorted) >= 1 and t_mains_sorted[0] == p1_lock:
        score += 25
        lock_matches["p1"] = p1_lock
        signals.append(f"🎯 P1={p1_lock} DJ-locked (+25)")
    if p2_lock is not None and len(t_mains_sorted) >= 2 and t_mains_sorted[1] == p2_lock:
        score += 25
        lock_matches["p2"] = p2_lock
        signals.append(f"🎯 P2={p2_lock} DJ-locked (+25)")
    
    # ⭐ Star locks — reward BOTH stars matching
    held_star_locks = t_stars & star_locks
    if len(held_star_locks) >= 2:
        score += 30
        lock_matches["stars_full"] = sorted(held_star_locks)
        signals.append(f"⭐⭐ both stars DJ-locked {sorted(held_star_locks)} (+30)")
    elif len(held_star_locks) == 1:
        score += 12
        lock_matches["star_half"] = sorted(held_star_locks)
        signals.append(f"⭐ partial star lock {sorted(held_star_locks)} (+12)")
    # Star extensions (e.g. 9 from "479")
    held_ext = t_stars & star_extensions
    if held_ext:
        score += 6 * len(held_ext)
        signals.append(f"⭐ star-extension {sorted(held_ext)} (+{6*len(held_ext)})")
    
    # 🔒 Triple-lock mains (rare-event + seed + Q1d2 hungry)
    held_triple = set(t_mains) & triple_lock
    if held_triple:
        score += 25 * len(held_triple)
        signals.append(f"🔒 triple-lock {sorted(held_triple)} (+{25*len(held_triple)})")
    
    # 🪞 Mirror of banned numbers held
    mirrors_held = []
    for b in banned:
        m = mirror_of(b)
        if m in set(t_mains):
            mirrors_held.append((b, m))
    if mirrors_held:
        score += 20 * len(mirrors_held)
        sig = ", ".join(f"{m} = mirror({b})" for b, m in mirrors_held)
        signals.append(f"🪞 mirror-of-banned: {sig} (+{20*len(mirrors_held)})")
    
    # 🌀 Back-door circles (e.g., circle(21)=46) at P4 or P5
    back_door_hits = []
    p4 = t_mains_sorted[3] if len(t_mains_sorted) >= 4 else None
    p5 = t_mains_sorted[4] if len(t_mains_sorted) >= 5 else None
    for k, v in back_door.items():
        if v in (p4, p5):
            back_door_hits.append({"banned": int(k), "circle": v, "pos": "P5" if v == p5 else "P4"})
            score += 18
            signals.append(f"🌀 back-door circle({k})={v} at {'P5' if v==p5 else 'P4'} (+18)")
    
    # 🌱 Back-row pool (expanded target set for P4/P5)
    backrow_hits = set([p4, p5]) & back_row_pool if p4 or p5 else set()
    backrow_hits.discard(None)
    if backrow_hits:
        score += 10 * len(backrow_hits)
        signals.append(f"🌱 expanded back-row {sorted(backrow_hits)} (+{10*len(backrow_hits)})")
    
    # 🌾 Q1 seed echoes un-played in Q2 mains
    seed_echoes = sorted(set(t_mains) & q1_unplayed)
    if seed_echoes:
        score += 15 * len(seed_echoes)
        signals.append(f"🌾 Q1-seed-echo un-played {seed_echoes} (+{15*len(seed_echoes)})")
    
    # 🎯 USER HUNGRY LIST (DJ-curated, active for next N draws)
    user_hungry = set(cfg.get("user_hungry_list_next_3d", []) or [])
    user_hungry_hits = sorted(set(t_mains) & user_hungry)
    if user_hungry_hits:
        score += 12 * len(user_hungry_hits)
        signals.append(f"🌾 DJ hungry-list {user_hungry_hits} (+{12*len(user_hungry_hits)})")
    
    # Badge tier
    if score >= 80:
        badge = "🎻🎻 dj-symphony"
    elif score >= 40:
        badge = "🎻 dj-tuned"
    elif score >= 10:
        badge = "🎧 partial-tune"
    elif score <= -10:
        badge = "💀 anti-dj"
    else:
        badge = "🎧 neutral"
    
    return {
        "score": score,
        "signals": signals,
        "badge": badge,
        "lock_matches": lock_matches,
        "back_door_hits": back_door_hits,
        "mirror_of_banned": [{"banned": b, "mirror": m} for b, m in mirrors_held],
        "seed_echoes": seed_echoes,
        "ban_hits": sorted(ban_hits),
    }


# ─── Self-test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    cases = [
        ("DJ's top pick",     [7, 14, 17, 41, 47], [3, 6]),
        ("Alt: seed 42",      [7, 14, 18, 42, 47], [3, 6]),
        ("Back-door 46",      [7, 14, 17, 41, 46], [3, 6]),
        ("High mirror 49",    [7, 14, 17, 42, 49], [3, 9]),
        ("Anti-DJ (has 21)",  [21, 24, 28, 33, 47], [1, 2]),
        ("Random neutral",    [3, 16, 22, 35, 44], [7, 11]),
    ]
    for label, nums, stars in cases:
        r = score_dj_calls(nums, stars, mode="euro")
        print(f"{label}: {nums} ⭐{stars}")
        print(f"  → {r['badge']}  {r['score']:+d} pts")
        for s in r['signals']:
            print(f"    {s}")
        print()
