"""
🎻🎭 STORY TICKET ORCHESTRA

Takes the convergence radar output from `lottery_simulator` and builds
THEMED TICKETS — each ticket tells a coherent narrative using a specific
subset of laws. Then reports coverage:

  "With N tickets, we hold X% of the 2+ pool and Y% of the 3+ pool."

Each archetype has a priority rule for selecting 5 mains + 2 stars so that
the ticket's STORY is legible (not just random sampling).
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

from lottery_simulator import run_simulator, CFG


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _has_law(entry, law_prefix):
    return any(l.startswith(law_prefix) for l in entry["laws"])


def _filter(conv, predicate):
    return [c for c in conv if predicate(c)]


def _pick(numbers, seen, n):
    """Pick up to n new numbers from list, skipping already chosen."""
    out = []
    for x in numbers:
        if len(out) >= n:
            break
        if x not in seen and x not in out:
            out.append(x)
    return out


def _complete_ticket(chosen, pool_by_lens, banned, size=5):
    """If ticket is short, fill from top-convergence pool."""
    if len(chosen) >= size:
        return sorted(chosen[:size])
    needed = size - len(chosen)
    fill = _pick(pool_by_lens, set(chosen) | set(banned), needed)
    return sorted(chosen + fill)


def _pick_stars(conv_stars, seen_stars=None, n=2):
    if seen_stars is None:
        seen_stars = set()
    out = []
    for s in conv_stars:
        if len(out) >= n:
            break
        if s["s"] not in seen_stars and s["s"] not in out:
            out.append(s["s"])
    # pad with cosmic default 3, 6 if still short
    for d in [3, 6, 1, 10, 7, 8]:
        if len(out) >= n:
            break
        if d not in out:
            out.append(d)
    return sorted(out[:n])


# ─────────────────────────────────────────────────────────────
# Archetypes — each returns (ticket_mains, stars, narrative, laws_used)
# ─────────────────────────────────────────────────────────────
def archetype_ladder_fill(conv, stars, banned):
    ladder = [c["n"] for c in conv if _has_law(c, "ladder-fill")]
    date_perm = [c["n"] for c in conv if _has_law(c, "date-perm")]
    back_row = [c["n"] for c in conv if _has_law(c, "dj-back-row") or _has_law(c, "back-row-echo")]
    mains = _pick(ladder, set(banned), 2) + _pick(date_perm, set(banned), 2) + _pick(back_row, set(banned), 2)
    mains = list(dict.fromkeys(mains))
    return ("🪜 Ladder-Fill Symphony",
            "Rides the banned-anchor ladder plus date-perms plus back-row echo",
            mains, _pick_stars(stars))


def archetype_plus10_key(conv, stars, banned):
    p10 = [c["n"] for c in conv if _has_law(c, "+10-key") or _has_law(c, "dj-plus10")]
    hungry = [c["n"] for c in conv if _has_law(c, "dj-hungry")]
    mains = _pick(p10, set(banned), 4) + _pick(hungry, set(banned) | set(p10[:4]), 2)
    return ("🔑 +10 Key Translation",
            "Q1d5 seed+10 numbers dominate — Q-signature constant echo",
            mains, _pick_stars(stars))


def archetype_rare_cycle_close(conv, stars, banned):
    rare = [c["n"] for c in conv if _has_law(c, "rare-echo")]
    triple = [c["n"] for c in conv if _has_law(c, "dj-triple-lock")]
    mains = _pick(rare, set(banned), 4) + _pick(triple, set(banned) | set(rare[:4]), 3)
    rare_stars = [s["s"] for s in stars if any(l.startswith("rare") for l in s["laws"])]
    return ("🚨 Rare-Cycle Close",
            "Unreleased rare seed mains + rare-echo stars — the +8 cycle-close release",
            mains, sorted((rare_stars + _pick_stars(stars, set(rare_stars)))[:2]))


def archetype_snap_back_combo(conv, stars, banned):
    snap_sweet = [c["n"] for c in conv if _has_law(c, "snap-back-sweet")]
    snap_band = [c["n"] for c in conv if _has_law(c, "snap-back-band")]
    dj_lock = [c["n"] for c in conv if _has_law(c, "dj-P")]  # P1 or P2 lock
    mains = _pick(snap_sweet, set(banned), 2) + _pick(snap_band, set(banned), 2) + _pick(dj_lock, set(banned), 2)
    return ("🔄 Snap-Back Combo",
            "Low P1 sweet zone + DJ lock frame + rebound mid-band",
            mains, _pick_stars(stars))


def archetype_silent_band(conv, stars, banned):
    silent = [c["n"] for c in conv if _has_law(c, "silent-band")]
    self21 = [c["n"] for c in conv if _has_law(c, "self-circle-21")]
    mains = _pick(silent, set(banned), 3) + _pick(self21, set(banned), 3)
    return ("💤 Silent-Band Release",
            "Numbers whose ±2 zone was deep-silent + self +21 echoes",
            mains, _pick_stars(stars))


def archetype_double_resonance(conv, stars, banned):
    date_circle = [c["n"] for c in conv if _has_law(c, "date-circle")]
    date_perm = [c["n"] for c in conv if _has_law(c, "date-perm") and not _has_law(c, "dj-")]
    both = [c["n"] for c in conv if _has_law(c, "date-circle") and _has_law(c, "date-perm")]
    mains = _pick(both, set(banned), 3) + _pick(date_circle, set(banned), 2) + _pick(date_perm, set(banned), 2)
    return ("🌀 Double-Resonance Date",
            "Numbers that ring in BOTH raw-date and circle-date lenses",
            mains, _pick_stars(stars))


def archetype_mirror_orchestra(conv, stars, banned):
    mirror = [c["n"] for c in conv if _has_law(c, "mirror")]
    back_door = [c["n"] for c in conv if _has_law(c, "back-door")]
    mains = _pick(mirror, set(banned), 3) + _pick(back_door, set(banned), 3)
    return ("🪞 Mirror Orchestra",
            "Mirror twins (pair-sum 28 or 56) + banned back-doors",
            mains, _pick_stars(stars))


def archetype_pivot_band(conv, stars, banned):
    # 14 zone (±3) and 28 zone (±3)
    pivot_zone = [c["n"] for c in conv if 11 <= c["n"] <= 17 or 25 <= c["n"] <= 31]
    mains = _pick(sorted(pivot_zone, key=lambda n: -next(c["lens_count"] for c in conv if c["n"] == n)),
                  set(banned), 6)
    return ("🎯 Pivot Band",
            "Numbers clustered at ±3 of pivots 14 & 28",
            mains, _pick_stars(stars))


def archetype_cross_bridge(conv, stars, banned):
    cross = [c["n"] for c in conv if _has_law(c, "cross-Δ") or _has_law(c, "cross-circle")]
    mains = _pick(cross, set(banned), 6)
    return ("🌉 Cross-Lottery Bridge",
            "Euro↔Swiss Δ±2 and +21 circle candidates",
            mains, _pick_stars(stars))


def archetype_dj_signature(conv, stars, banned, dj_call=None):
    if not dj_call:
        return None
    c = dj_call.get("euro", {})
    chosen = []
    if c.get("p1_lock"):
        chosen.append(c["p1_lock"])
    if c.get("p2_lock"):
        chosen.append(c["p2_lock"])
    for n in c.get("triple_lock_mains", []):
        if n not in chosen and n not in banned:
            chosen.append(n)
    for n in c.get("user_hungry_list_next_3d", []):
        if len(chosen) >= 5:
            break
        if n not in chosen and n not in banned:
            chosen.append(n)
    return ("🎻🎻 DJ Signature",
            "User-locked P1/P2 + triple-lock + hungry list",
            chosen[:5], c.get("star_locks", _pick_stars(stars)))


def archetype_symphony_top(conv, stars, banned):
    """Pure top-5 by lens count."""
    top = [c["n"] for c in conv if c["n"] not in banned][:5]
    return ("🎻🎻🎻 Full Symphony (pure top-5)",
            "The 5 loudest numbers across all laws",
            top, _pick_stars(stars))


def archetype_hungry_heavy(conv, stars, banned):
    hungry = [c["n"] for c in conv if _has_law(c, "dj-hungry") or _has_law(c, "seed-hungry")]
    mains = _pick(hungry, set(banned), 6)
    return ("🌾 Hungry Heavy",
            "Ticket built entirely from hungry / seed-unplayed numbers",
            mains, _pick_stars(stars))


def archetype_running_sum_mirror(conv, stars, banned):
    """Running-sum + self-circle-21 + rebound."""
    rs = [c["n"] for c in conv if _has_law(c, "p1-running-sum")]
    hsr = [c["n"] for c in conv if _has_law(c, "high-sum-rebound")]
    scir = [c["n"] for c in conv if _has_law(c, "self-circle-21")]
    mains = _pick(rs, set(banned), 2) + _pick(hsr, set(banned), 2) + _pick(scir, set(banned), 2)
    return ("🔢 Running-Sum Mirror",
            "P1-running-sum + rebound band + self-circle echoes",
            mains, _pick_stars(stars))


ARCHETYPES = [
    archetype_symphony_top,
    archetype_dj_signature,
    archetype_ladder_fill,
    archetype_plus10_key,
    archetype_rare_cycle_close,
    archetype_snap_back_combo,
    archetype_silent_band,
    archetype_double_resonance,
    archetype_mirror_orchestra,
    archetype_pivot_band,
    archetype_cross_bridge,
    archetype_hungry_heavy,
    archetype_running_sum_mirror,
]


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def build_orchestra(target_date: str, mode: str, dj_call=None,
                    actual_mains=None, actual_stars=None):
    sim = run_simulator(target_date, mode, actual_mains, actual_stars, dj_call)
    conv = sim["convergence"]
    star_suspects = sim.get("star_suspects", [])
    banned = sim.get("banned", [])
    mx = CFG[mode]["max_main"]

    pool_3p = [c["n"] for c in conv if c["lens_count"] >= 3]
    pool_2p = [c["n"] for c in conv if c["lens_count"] >= 2]

    tickets = []
    for arch in ARCHETYPES:
        try:
            if arch.__name__ == "archetype_dj_signature":
                result = arch(conv, star_suspects, banned, dj_call)
            else:
                result = arch(conv, star_suspects, banned)
            if not result:
                continue
            name, story, mains, chosen_stars = result
            # Ensure 5 mains by filling from top-convergence
            mains = _complete_ticket(mains, [c["n"] for c in conv], banned, size=5)
            if len(set(mains)) < 5:
                continue
            # Score ticket
            score = sum(c["lens_count"] for c in conv if c["n"] in mains)
            laws_held = set()
            for c in conv:
                if c["n"] in mains:
                    laws_held.update(c["laws"])
            tickets.append({
                "archetype": name,
                "story": story,
                "mains": mains,
                "stars": chosen_stars,
                "lens_score": score,
                "laws_count": len(laws_held),
                "covered_in_3plus": sorted(set(mains) & set(pool_3p)),
                "covered_in_2plus": sorted(set(mains) & set(pool_2p)),
            })
        except Exception as e:
            print(f"skip {arch.__name__}: {e}", file=sys.stderr)

    # De-dup identical main-combos, prefer higher lens score
    dedup = {}
    for t in tickets:
        k = tuple(t["mains"])
        if k not in dedup or t["lens_score"] > dedup[k]["lens_score"]:
            dedup[k] = t
    tickets = sorted(dedup.values(), key=lambda t: -t["lens_score"])

    # Coverage stats
    all_mains = set()
    for t in tickets:
        all_mains.update(t["mains"])
    coverage = {
        "num_tickets": len(tickets),
        "unique_mains_covered": len(all_mains),
        "pool_3plus_size": len(pool_3p),
        "pool_3plus_covered": len(all_mains & set(pool_3p)),
        "pool_3plus_pct": round(100 * len(all_mains & set(pool_3p)) / max(1, len(pool_3p)), 1),
        "pool_2plus_size": len(pool_2p),
        "pool_2plus_covered": len(all_mains & set(pool_2p)),
        "pool_2plus_pct": round(100 * len(all_mains & set(pool_2p)) / max(1, len(pool_2p)), 1),
    }

    validation = sim.get("validation")
    if validation:
        actual_set = set(actual_mains)
        # How many tickets hit ≥3 of actual winners?
        ticket_hits = []
        for t in tickets:
            hits = len(set(t["mains"]) & actual_set)
            ticket_hits.append({
                "archetype": t["archetype"],
                "hits": hits,
                "matched": sorted(set(t["mains"]) & actual_set),
            })
        validation["tickets_with_3plus_hits"] = sum(1 for t in ticket_hits if t["hits"] >= 3)
        validation["tickets_with_2plus_hits"] = sum(1 for t in ticket_hits if t["hits"] >= 2)
        validation["ticket_hit_detail"] = ticket_hits

    return {
        "target_date": target_date,
        "mode": mode,
        "convergence_pool_3plus": pool_3p,
        "convergence_pool_2plus": pool_2p,
        "banned": banned,
        "tickets": tickets,
        "coverage": coverage,
        "validation": validation,
    }


def format_orchestra(r: dict) -> str:
    L = []
    L.append("🎻🎭 STORY TICKET ORCHESTRA")
    L.append("═" * 78)
    L.append(f"Target: {r['target_date']}  ·  Mode: {r['mode'].upper()}")
    if r.get("banned"):
        L.append(f"🚫 Banned: {r['banned']}")
    cov = r["coverage"]
    L.append(f"📊 {cov['num_tickets']} story tickets · "
             f"unique mains covered: {cov['unique_mains_covered']}")
    L.append(f"    3+ pool: {cov['pool_3plus_covered']}/{cov['pool_3plus_size']} ({cov['pool_3plus_pct']}%)")
    L.append(f"    2+ pool: {cov['pool_2plus_covered']}/{cov['pool_2plus_size']} ({cov['pool_2plus_pct']}%)")
    L.append("")
    L.append(f"🔔 3+ pool: {r['convergence_pool_3plus']}")
    L.append(f"🎧 2+ pool: {r['convergence_pool_2plus']}")
    L.append("")
    L.append("🎫 TICKETS (ranked by lens score)")
    L.append("-" * 78)
    for i, t in enumerate(r["tickets"], 1):
        L.append(f"  #{i:>2}  {t['archetype']}  ·  lens-score {t['lens_score']}")
        L.append(f"       mains: {t['mains']}  ⭐ {t['stars']}")
        L.append(f"       story: {t['story']}")
        L.append(f"       in 3+ pool: {t['covered_in_3plus']}  ·  in 2+ pool: {t['covered_in_2plus']}")
        L.append("")
    if r.get("validation"):
        v = r["validation"]
        L.append("🧪 VALIDATION")
        L.append("-" * 78)
        L.append(f"  Actual: {v['actual_mains']}  ⭐ {v['actual_stars']}")
        L.append(f"  Tickets with ≥2 hits: {v.get('tickets_with_2plus_hits', 0)}")
        L.append(f"  Tickets with ≥3 hits: {v.get('tickets_with_3plus_hits', 0)}")
        L.append(f"  Per-ticket hits:")
        for h in v.get("ticket_hit_detail", []):
            badge = "🎯" if h["hits"] >= 3 else ("🎻" if h["hits"] >= 2 else "🎧" if h["hits"] == 1 else "❌")
            L.append(f"    {badge} {h['hits']}/5  {h['matched']}  ← {h['archetype']}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--mode", choices=["euro", "swiss"], required=True)
    ap.add_argument("--actual")
    ap.add_argument("--stars")
    ap.add_argument("--no-dj", action="store_true")
    args = ap.parse_args()

    dj_call = None
    if not args.no_dj:
        p = ROOT / "dj_calls.json"
        if p.exists():
            dj_call = json.loads(p.read_text())

    actual_mains = [int(x) for x in args.actual.split(",")] if args.actual else None
    actual_stars = [int(x) for x in args.stars.split(",")] if args.stars else None

    r = build_orchestra(args.date, args.mode, dj_call, actual_mains, actual_stars)
    print(format_orchestra(r))


if __name__ == "__main__":
    main()
