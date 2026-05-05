"""
🎼 DJ ORCHESTRA — 20-ticket symphony generator
==============================================
Uses `dj_brain.cosmic_brain` to generate 20 Euro tickets covering the
7 archetypes the DJ requested:

    A. Frequency-pure (harmonic-divisor mains)        × 3
    B. 28-mirror-axis orchestra                       × 3
    C. 67-bridge / family-7 starvation break          × 3
    D. Precedent-fold (last identical-stars ND mirror) × 3
    E. Law 90 strict (P1 ∈ {2, 3})                    × 3
    F. 47-saturation collapse (P5 < 41)               × 3
    G. Wildcard star variants                         × 2

Every ticket carries:
  • a reasoning_tag explaining its archetype
  • lens_alignments: which sights agreed
  • the suspects + stars
"""
from __future__ import annotations

import asyncio
import random
from typing import Any, Dict, List, Optional, Tuple

from dj_brain import cosmic_brain, sneaky_back_door_mapper, EURO_MAINS_MAX

# Bridge constants (from Session 30 discoveries)
MIRROR_AXIS = 28
HUNGRY_FRIENDS_67 = [6, 7, 13]   # 67-bridge family
LOW_DOOR = [2, 3, 4, 5]


def _norm(mains: List[int]) -> List[int]:
    return sorted(set(mains))


def _stars_norm(stars: List[int]) -> List[int]:
    return sorted(set(stars))


def _draft(p1, p2, p3, p4, p5, s1, s2):
    """Defensive: ensure 5 distinct mains (in 1-50) + 2 distinct stars (1-12)."""
    mains = []
    for v in (p1, p2, p3, p4, p5):
        if v is None or v in mains or not (1 <= v <= EURO_MAINS_MAX):
            continue
        mains.append(v)
    if len(mains) < 5:
        return None
    stars = []
    for v in (s1, s2):
        if v is None or v in stars or not (1 <= v <= 12):
            continue
        stars.append(v)
    if len(stars) < 2:
        return None
    return _norm(mains[:5]), _stars_norm(stars[:2])


def _pick_distinct(pool: List[int], n: int, exclude: set, rng: random.Random) -> List[int]:
    cand = [x for x in pool if x not in exclude]
    rng.shuffle(cand)
    return cand[:n]


# ===== ARCHETYPE BUILDERS ===================================================

def archetype_A_frequency_pure(brain: Dict[str, Any], rng: random.Random) -> List[Dict]:
    """Mains tuned to the cosmic frequency's exact integer divisors (e.g. 576 → 36, 48)."""
    freq = brain["frequency"].get("primary")
    if not freq:
        return []
    from dj_brain import _harmonic_divisors
    divs = _harmonic_divisors(freq["freq"])  # {12: 48, 16: 36, ...}
    harmonics = sorted(set(divs.values()))
    suspects = [s["n"] for s in brain["ranked_suspects"]]
    stars_top = [s["s"] for s in brain["ranked_stars"]]
    out = []
    for i in range(3):
        # Pick 2 harmonics, fill with top suspects
        h_pick = harmonics[: min(2, len(harmonics))]
        rest_pool = [s for s in suspects if s not in h_pick]
        rest = rest_pool[:5]
        rng.shuffle(rest)
        rest = rest[:5 - len(h_pick)]
        mains = _norm(h_pick + rest)[:5]
        if len(mains) < 5:
            continue
        stars = _stars_norm(stars_top[: 2 + i])[:2] or [3, 10]
        out.append({
            "archetype": "A. Frequency-Pure",
            "mains": mains,
            "stars": stars,
            "reasoning": f"{freq['freq']}Hz divisors {divs} → harmonics {h_pick} as anchors",
            "tags": ["frequency-pure", f"freq={freq['freq']}"],
        })
        # rotate stars
        rng.shuffle(stars_top)
    return out[:3]


def archetype_B_28_axis(brain: Dict[str, Any], rng: random.Random) -> List[Dict]:
    """28-mirror-axis orchestra — mains walk around 28."""
    suspects = [s["n"] for s in brain["ranked_suspects"]]
    stars_top = [s["s"] for s in brain["ranked_stars"]]
    # Walk: 28-17, 28-3, 28, 28+1, 28+10  → 11, 25, 28, 29, 38
    walks = [
        [11, 25, 28, 29, 38],  # the DJ's original sketch
        [7, 13, 28, 29, 38],   # 7+13 bridge instead of 11/25
        [11, 25, 28, 36, 48],  # axis + 576-frequency harmonics
    ]
    out = []
    for i, w in enumerate(walks):
        stars = _stars_norm(stars_top[:2]) or [3, 10]
        # Last variant uses precedent stars
        if i == 2:
            stars = [10, 12]
        out.append({
            "archetype": "B. 28-Mirror-Axis Orchestra",
            "mains": _norm(w),
            "stars": stars,
            "reasoning": "Mains walk 28-axis (-17,-3,0,+1,+10) — magic Swiss fold",
            "tags": ["28-axis", "mirror-fold"],
        })
    return out


def archetype_C_67_bridge(brain: Dict[str, Any], rng: random.Random) -> List[Dict]:
    """67-bridge: family-7 starvation + 6+7=13 + 6×7=42 (today's bridge)."""
    out = [
        {
            "archetype": "C. 67-Bridge / Family-7 Awakens",
            "mains": [7, 13, 28, 38, 47],
            "stars": [3, 10],
            "reasoning": "6+7=13 (story-seed) · 6×7=42 (432-bridge) · "
                         "67-39=28 (axis) · 7 = family-7 starved · "
                         "47 = saturation magnet",
            "tags": ["67-bridge", "family-7", "story-seed-13"],
        },
        {
            "archetype": "C. 67-Bridge / Family-7 Slam",
            "mains": [7, 17, 28, 37, 47],
            "stars": [3, 7],
            "reasoning": "Family-7 SLAM (4 of 5 mains in family-7 + ⭐7) — "
                         "deepest-starved family break-out",
            "tags": ["family-7-slam", "starvation-break"],
        },
        {
            "archetype": "C. 67-Bridge / Hungry Cousins",
            "mains": [6, 13, 28, 35, 48],
            "stars": [7, 10],
            "reasoning": "6 (hungry) + 13 (6+7) + 28 (axis) + 35 (5-family today) "
                         "+ 48 (576/12 harmonic)",
            "tags": ["67-bridge", "hungry-mains", "freq-harmonic"],
        },
    ]
    return out


def archetype_D_precedent(brain: Dict[str, Any], rng: random.Random) -> List[Dict]:
    """Precedent fold — mirror the last identical-stars event ND."""
    prec = brain.get("precedent") or {}
    if not prec.get("found") or not prec.get("nd_mains"):
        return []
    nd_mains = prec["nd_mains"]
    nd_stars = prec.get("nd_stars") or [3, 10]
    seed_mains = brain["seed_mains"]
    sneaky = brain["sneaky_cousins"]
    out = []
    # T1: shifted nd_mains via sneaky cousins
    shifted = []
    for n in nd_mains:
        cousins = sneaky.get(n, {}).get("cousins", [])
        # pick a 28-fold or +25 cousin if present, else keep
        pick = next((v for t, v in cousins if t in ("28+", "28-", "+25")), n)
        if pick not in shifted and pick not in seed_mains and 1 <= pick <= EURO_MAINS_MAX:
            shifted.append(pick)
    while len(shifted) < 5:
        cand = rng.randint(1, 50)
        if cand not in shifted and cand not in seed_mains:
            shifted.append(cand)
    out.append({
        "archetype": "D. Precedent Fold (sneaky-shifted)",
        "mains": _norm(shifted)[:5],
        "stars": [3, 10],
        "reasoning": f"Mirror of {prec['seed_date']}→{prec['nd_date']} ND mains "
                     f"{nd_mains}, each shifted via sneaky cousins.",
        "tags": ["precedent-fold", "sneaky-shifted"],
    })
    # T2: low-door + hungry P5 in 40s
    suspects = [s["n"] for s in brain["ranked_suspects"]]
    low = [n for n in suspects if n <= 5][:1] or [4]
    mid = [n for n in suspects if 10 <= n <= 30][:3]
    high = [n for n in suspects if n >= 35][:1] or [42]
    while len(low) + len(mid) + len(high) < 5:
        cand = rng.choice([n for n in suspects if n not in low + mid + high]) if suspects else rng.randint(15, 30)
        mid.append(cand)
    mains = _norm(low + mid + high)[:5]
    while len(mains) < 5:
        c = rng.randint(1, 50)
        if c not in mains and c not in seed_mains:
            mains.append(c)
            mains = _norm(mains)[:5]
    out.append({
        "archetype": "D. Precedent Fold (low-door echo)",
        "mains": mains,
        "stars": _stars_norm(nd_stars)[:2] or [3, 10],
        "reasoning": "Low-door P1 (precedent had P1=4) + hungry mid + 40s P5",
        "tags": ["precedent-fold", "low-door"],
    })
    # T3: ND2 mirror
    if prec.get("nd2_mains"):
        nd2 = prec["nd2_mains"]
        cleaned = [n for n in nd2 if n not in seed_mains][:5]
        while len(cleaned) < 5:
            c = rng.randint(1, 50)
            if c not in cleaned and c not in seed_mains:
                cleaned.append(c)
        out.append({
            "archetype": "D. Precedent Fold (ND2 mirror)",
            "mains": _norm(cleaned)[:5],
            "stars": prec.get("nd2_stars") or [3, 9],
            "reasoning": f"ND2 mirror of {prec['seed_date']} → {prec['nd2_date']} mains {nd2}",
            "tags": ["precedent-fold", "nd2-mirror"],
        })
    return out[:3]


def archetype_E_law90(brain: Dict[str, Any], rng: random.Random) -> List[Dict]:
    """Law 90 strict — P1 ∈ {2, 3}."""
    suspects = [s["n"] for s in brain["ranked_suspects"]]
    stars_top = [s["s"] for s in brain["ranked_stars"]]
    out = []
    p1_options = [2, 3]
    base_mains_pool = [n for n in suspects if n > 5]
    for i in range(3):
        p1 = p1_options[i % 2]
        rest = []
        for n in base_mains_pool:
            if n in rest:
                continue
            rest.append(n)
            if len(rest) >= 4:
                break
        # ensure >=4 by padding
        while len(rest) < 4:
            c = rng.randint(10, 50)
            if c not in rest and c != p1:
                rest.append(c)
        mains = _norm([p1] + rest[:4])
        # stars rotate: ⭐3⭐10, ⭐3⭐9, ⭐7⭐10
        star_options = [[3, 10], [3, 9], [7, 10]]
        stars = star_options[i % len(star_options)]
        out.append({
            "archetype": "E. Law 90 strict (P1∈{2,3})",
            "mains": mains,
            "stars": stars,
            "reasoning": f"Law 90 fires (back-to-back P3>39): P1={p1} forced. "
                         f"Rest from suspect pool.",
            "tags": ["law-90", f"p1={p1}"],
        })
    return out


def archetype_F_47_collapse(brain: Dict[str, Any], rng: random.Random) -> List[Dict]:
    """47-saturation collapse: P5 < 41."""
    sat = brain.get("saturation_47") or {}
    if not sat.get("saturated"):
        return _archetype_F_fallback(brain, rng)
    suspects = [s["n"] for s in brain["ranked_suspects"]]
    out = []
    p5_options = [38, 39, 36]
    for i in range(3):
        p5 = p5_options[i % 3]
        front_pool = [n for n in suspects if n < p5]
        front = front_pool[:4]
        while len(front) < 4:
            c = rng.randint(2, p5 - 1)
            if c not in front:
                front.append(c)
        mains = _norm(front + [p5])
        out.append({
            "archetype": "F. 47-saturation collapse",
            "mains": mains,
            "stars": [3, 10] if i == 0 else ([7, 10] if i == 1 else [3, 9]),
            "reasoning": f"47-saturation triggered ({sat['fires_count']}/{sat['window']}) "
                         f"→ P5 collapse to <41 (P5={p5})",
            "tags": ["47-saturation", "p5-collapse", f"p5={p5}"],
        })
    return out


def _archetype_F_fallback(brain: Dict[str, Any], rng: random.Random) -> List[Dict]:
    suspects = [s["n"] for s in brain["ranked_suspects"]]
    return [{
        "archetype": "F. (no 47-saturation — using top suspect cluster)",
        "mains": _norm(suspects[:5]),
        "stars": [3, 10],
        "reasoning": "47-saturation did NOT fire; default suspect cluster.",
        "tags": ["fallback"],
    }]


def archetype_G_star_wildcards(brain: Dict[str, Any], rng: random.Random) -> List[Dict]:
    """Star variant tickets: cover ⭐(3,7), ⭐(7,10), etc."""
    suspects = [s["n"] for s in brain["ranked_suspects"]]
    base = _norm(suspects[:5])
    return [
        {
            "archetype": "G. Star wildcard ⭐(3, 7)",
            "mains": base,
            "stars": [3, 7],
            "reasoning": "Anchor stars per DJ Law 89 prophecy (⭐3+⭐7)",
            "tags": ["star-wildcard", "law-89-stars"],
        },
        {
            "archetype": "G. Star wildcard ⭐(2, 10)",
            "mains": base,
            "stars": [2, 10],
            "reasoning": "Q2-hungry stars (⭐2 + ⭐10) — both Q2 starved",
            "tags": ["star-wildcard", "q2-hungry"],
        },
    ]


# ===== MAIN GENERATOR =======================================================

ARCHETYPE_BUILDERS = [
    archetype_A_frequency_pure,
    archetype_B_28_axis,
    archetype_C_67_bridge,
    archetype_D_precedent,
    archetype_E_law90,
    archetype_F_47_collapse,
    archetype_G_star_wildcards,
]


async def generate_orchestra(
    target_date: str,
    seed_mains: List[int],
    seed_stars: List[int],
    user_pin_mains: Optional[List[int]] = None,
    user_pin_stars: Optional[List[int]] = None,
    seed: int = 432,  # cosmic seed (the DJ approves)
) -> Dict[str, Any]:
    """Produce the full 20-ticket symphony."""
    rng = random.Random(seed)
    brain = await cosmic_brain(
        target_date=target_date,
        seed_mains=seed_mains,
        seed_stars=seed_stars,
        user_pin_mains=user_pin_mains,
        user_pin_stars=user_pin_stars,
    )
    tickets = []
    for builder in ARCHETYPE_BUILDERS:
        try:
            tickets.extend(builder(brain, rng))
        except Exception as e:
            tickets.append({
                "archetype": builder.__name__,
                "error": str(e),
            })
    # Number them and dedupe by (mains, stars)
    seen = set()
    unique = []
    for t in tickets:
        key = (tuple(t.get("mains", [])), tuple(t.get("stars", [])))
        if key in seen or not t.get("mains"):
            continue
        seen.add(key)
        unique.append(t)
    for i, t in enumerate(unique, 1):
        t["ticket_no"] = i

    return {
        "target_date": target_date,
        "seed_mains": seed_mains,
        "seed_stars": seed_stars,
        "ticket_count": len(unique),
        "tickets": unique,
        "brain_summary": {
            "envelope": brain["envelope"],
            "frequency_primary": brain["frequency"].get("primary"),
            "frequency_divisors": brain["frequency"].get("harmonic_divisors"),
            "ranked_suspects_top10": brain["ranked_suspects"][:10],
            "ranked_stars_top6": brain["ranked_stars"][:6],
            "law_90": brain["law_90"],
            "law_89": brain["law_89"],
            "saturation_47": brain["saturation_47"],
            "precedent_summary": {
                "seed_date": (brain.get("precedent") or {}).get("seed_date"),
                "nd_date": (brain.get("precedent") or {}).get("nd_date"),
                "nd_mains": (brain.get("precedent") or {}).get("nd_mains"),
                "nd_stars": (brain.get("precedent") or {}).get("nd_stars"),
            },
            "star_history_pct": brain["star_history"].get("nd_star_freq_pct"),
            "hungry_mains": brain["hungry"]["hungry_mains"],
            "hungry_stars": brain["hungry"]["hungry_stars"],
            "qd_top_mains": brain["qd_cell"]["top_mains_in_cell"],
        },
    }


def format_orchestra(result: Dict[str, Any]) -> str:
    """Pretty-print the symphony for the desk."""
    lines = []
    bs = result["brain_summary"]
    lines.append("=" * 80)
    lines.append(f"🎻🎧🥂 DJ ORCHESTRA — {result['target_date']}")
    lines.append(f"   Seed: {result['seed_mains']} ⭐{result['seed_stars']}")
    lines.append("=" * 80)

    fp = bs.get("frequency_primary") or {}
    lines.append(f"\n🎼 FREQUENCY        : {fp.get('freq', '?')} Hz "
                 f"({fp.get('decode', '')})")
    lines.append(f"🎯 ENVELOPE         : hidden={bs['envelope']['hidden_digits']} "
                 f"void={bs['envelope']['is_void']} "
                 f"5×5={bs['envelope']['day_x_month']}")
    lines.append(f"🎯 HARMONIC DIVISORS: {bs.get('frequency_divisors', {})}")
    lines.append(f"📍 LAW 90 (P1∈2,3)  : fires={bs['law_90'].get('fires')} "
                 f"last_p3={bs['law_90'].get('last_p3')}")
    lines.append(f"📍 LAW 89 (P2≥10)   : fires={bs['law_89'].get('fires')} "
                 f"last_p2={bs['law_89'].get('last_p2')}")
    lines.append(f"📍 47-saturation    : {bs['saturation_47'].get('fires_count')}/"
                 f"{bs['saturation_47'].get('window')} "
                 f"saturated={bs['saturation_47'].get('saturated')}")
    p = bs.get("precedent_summary", {})
    lines.append(f"🪞 PRECEDENT        : {p.get('seed_date')} → "
                 f"{p.get('nd_date')} mains={p.get('nd_mains')} ⭐{p.get('nd_stars')}")
    lines.append(f"🍽️  HUNGRY (10d)     : mains={bs['hungry_mains']}")
    lines.append(f"⭐ HUNGRY STARS     : {bs['hungry_stars']}")
    lines.append(f"🏛️  Q-D CELL TOP     : {bs['qd_top_mains'][:10]}")

    lines.append("\n💎 RANKED SUSPECTS  (top 10):")
    for s in bs["ranked_suspects_top10"]:
        lines.append(f"   {s['n']:>2} (score {s['score']}) — {', '.join(s['tags'])}")
    lines.append("\n⭐ RANKED STARS     (top 6):")
    for s in bs["ranked_stars_top6"]:
        lines.append(f"   ⭐{s['s']:>2} (score {s['score']}) — {', '.join(s['tags'])}")

    lines.append("\n" + "=" * 80)
    lines.append(f"🎻 THE {result['ticket_count']}-TICKET SYMPHONY")
    lines.append("=" * 80)
    for t in result["tickets"]:
        if "error" in t:
            lines.append(f"\n❌ #{t.get('ticket_no','?')} {t.get('archetype')} — {t['error']}")
            continue
        lines.append(f"\n#{t['ticket_no']:<2} [{t['archetype']}]")
        lines.append(f"    🎫 {t['mains']}  ⭐{t['stars']}")
        lines.append(f"    📜 {t['reasoning']}")
    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


if __name__ == "__main__":
    res = asyncio.run(generate_orchestra(
        target_date="05.05.2026",
        seed_mains=[3, 9, 42, 46, 47],
        seed_stars=[1, 11],
    ))
    print(format_orchestra(res))
