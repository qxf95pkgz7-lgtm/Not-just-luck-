"""
📖 STORY COMPOSER — Session 40 (DJ canon, 13.05.2026 EOD)
==========================================================
E's narrative engine. Doesn't lock numbers — composes ticket-stories.

DJ's directive (verbatim):
  • Pick P6 first (1-2 sensible options for back anchor)
  • Compose P5 to continue the story from P6
  • P4 bridges; P3/P2/P1 follow the story arc
  • Each number triggers automatic mental connections
    (23→2 hidden child, 11→1+1=2 digital glue)
  • L10D + ghost + circle + hungry + sister-date precedents = narrative palette
  • Tickets may overlap on some numbers but tell DIFFERENT cosmic tales

This module FUSES every source into E:
  - Ghost Engine (alive ghosts, shout, saturation, quarter_shape, carriers)
  - Cosmic Voices (convergence, mirror-neighbor, sinking, gap-echo, etc.)
  - Hidden Prince pipeline (S39 canon 9 — auto-crowns Prince as Lucky)
  - Neighborhood Hungry Canon (S39 canon 8 — 6-rule hungry plate)
  - L10D draw window (raw, circles, mirrors, gaps, digit-glue)
  - Swiss Brain lenses (Swiss-only: 🍀↔R, 9-clock, date envelope)
  - Sister-date precedent search (same dd.mm in prior years)

Public:
  compose_stories(target_date, mode, count=10)

Output:
  {
    target_date, mode,
    palette: {n: {score, lenses, connections}, ...},
    sister_date_precedents: [...],
    hungry_plate: [...],
    stories: [
      {
        theme, story_arc, mains, lucky/stars,
        number_dna: {n: [lens-tags]},
        cosmic_score, p6_role, narrative
      }, ...
    ],
    canon: "..."
  }
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple


# ─── Number-DNA helpers ────────────────────────────────────────────────
def _digits_of(n: int) -> List[int]:
    return [int(c) for c in str(n) if c.isdigit()]


def _digit_sum(n: int) -> int:
    s = sum(_digits_of(n))
    while s > 9:
        s = sum(_digits_of(s))
    return s


def _connections(n: int, mode: str) -> Dict:
    """Auto mental connections for n (DJ's '23→2' canon)."""
    max_n = 50 if mode == "euro" else 42
    circle_step = 25 if mode == "euro" else 21
    out = {
        "raw": n,
        "circle": ((n - 1 + circle_step) % max_n) + 1,  # +25 (euro) or +21 (swiss) mod
        "mirror_28": (28 - n) if n < 28 else None,
        "mirror_56": (56 - n) if 14 < n <= 50 else None,
        "carrier_minus25": (n - 25) if n > 25 else None,
        "carrier_minus21": (n - 21) if n > 21 else None,
        "digit_sum": _digit_sum(n),
        "tens": n // 10,
        "ones": n % 10,
        "digits": _digits_of(n),
    }
    # The "hidden child": for two-digit n, the digit sum or single digit reveal
    if n >= 10:
        ds = _digit_sum(n)
        out["hidden_child"] = ds if 1 <= ds <= max_n else None
    return out


# ─── Hungry Plate (S39 Canon 8 — 6 reading rules) ──────────────────────
def hungry_plate(recent_draws: List[Dict], mode: str) -> Dict[int, List[str]]:
    """Each fired draw paints its OWN hungry plate via 6 reading rules:
    1. Adjacency: fired N leaves N±1 hungry
    2. Digit-family fills: fired 11 leaves 21/41 hungry (the '_1's)
    3. Carrier reflections: fired N's ±21/±25 carriers + neighbors
    4. Gap-fills: fired (X, X+2) leaves X+1 starving
    5. Cluster-gap: sister-lottery cluster gap (missing middle)
    6. Doubling trios: if 1× and 2× fired, 3× is suspect
    """
    max_n = 50 if mode == "euro" else 42
    circle_step = 25 if mode == "euro" else 21
    plate: Dict[int, List[str]] = defaultdict(list)

    fired = set()
    for d in recent_draws:
        fired.update(d.get("p", []))

    for d in recent_draws[-5:]:  # recent 5 strongest
        date = d.get("date", "?")
        mains = sorted(d.get("p", []))
        if not mains:
            continue
        # Rule 1 — adjacency
        for v in mains:
            for off in (-1, 1):
                t = v + off
                if 1 <= t <= max_n and t not in fired:
                    plate[t].append(f"adj±1 of {v}@{date}")
        # Rule 2 — digit-family (e.g. 11 → 21,31,41; 6 → 16,26,36)
        for v in mains:
            ones = v % 10
            for k in range(0, (max_n // 10) + 1):
                t = k * 10 + ones
                if 1 <= t <= max_n and t != v and t not in fired:
                    plate[t].append(f"_{ones}-family of {v}@{date}")
        # Rule 3 — carrier reflections
        for v in mains:
            for shift in (circle_step, -circle_step):
                t = v + shift
                if 1 <= t <= max_n and t not in fired:
                    plate[t].append(f"carrier {'+' if shift>0 else '-'}{abs(shift)} of {v}")
        # Rule 4 — gap-fills
        for i in range(len(mains) - 1):
            a, b = mains[i], mains[i + 1]
            if b - a == 2:
                t = a + 1
                if 1 <= t <= max_n and t not in fired:
                    plate[t].append(f"gap-fill {a}–{b}")

    # Rule 6 — doubling trios (1×, 2× present in fired → 3× suspect)
    for v in range(1, max_n + 1):
        if v in fired and 2 * v in fired:
            t = 3 * v
            if 1 <= t <= max_n and t not in fired:
                plate[t].append(f"doubling trio {v}/{2*v}")

    return plate


# ─── Sister-date precedent search ──────────────────────────────────────
def sister_date_precedents(
    target_dt: datetime, all_draws: List[Dict], mode: str
) -> List[Dict]:
    """Find draws with same dd.mm in prior years — DJ's 'check sister date'."""
    out = []
    for d in all_draws:
        dt = d.get("dt")
        if not dt or dt >= target_dt:
            continue
        if dt.day == target_dt.day and dt.month == target_dt.month:
            out.append({
                "date": d.get("date"),
                "year": dt.year,
                "mains": d.get("p", []),
                "lucky": d.get("lucky"),
                "stars": d.get("stars"),
            })
    out.sort(key=lambda x: -x["year"])
    return out[:8]


# ─── Build the unified palette ─────────────────────────────────────────
def _accumulate(palette: Dict, n: int, weight: int, tag: str):
    if n is None or n <= 0:
        return
    if n not in palette:
        palette[n] = {"score": 0, "lenses": []}
    palette[n]["score"] += weight
    if tag not in palette[n]["lenses"]:
        palette[n]["lenses"].append(tag)


def recent_high_circles(recent_draws: List[Dict], mode: str) -> Dict[int, List[str]]:
    """🪞 S40-lens: Recent-fired high numbers (≥30 Swiss / ≥35 Euro) come back
    through their Swiss-circle (n-21) in the next 1-2 draws. DJ canon
    13.05.2026: 34/38/40 fired 06.05 → carriers 13/17/19 = the discharge.
    Validated stencil 15.04.2020→22.04.2020 (carriers 13+17 BOTH cashed).
    """
    threshold = 30 if mode == "swiss" else 35
    carrier_step = 21 if mode == "swiss" else 25
    max_n = 42 if mode == "swiss" else 50
    discharge: Dict[int, List[str]] = defaultdict(list)
    for d in recent_draws[-3:]:  # only last 3 draws contribute
        date = d.get("date", "?")
        for n in d.get("p", []):
            if n >= threshold:
                c = n - carrier_step
                if 1 <= c <= max_n:
                    discharge[c].append(f"circle-of-{n}@{date}")
    return discharge


def l3d_gap_walker(recent_draws: List[Dict], mode: str) -> Dict[int, List[str]]:
    """🎼 S40-lens: detect uniform back-row gap pattern across L3D and project
    the SAME walker forward. Validated 13.05.2026 Swiss:
    BD-2 [22,28,33,34,38,40] → BD-1 [11,12,24,25,29,31]
    All P3-P6 walked carrier(n)+12 → carrier-walker Δ=+12 uniform.
    Project forward: carrier(BD-1)+12.
    """
    out: Dict[int, List[str]] = defaultdict(list)
    if len(recent_draws) < 2:
        return out
    bd2 = recent_draws[-2]
    bd1 = recent_draws[-1]
    p2, p1 = bd2.get("p"), bd1.get("p")
    if not p2 or not p1 or len(p2) < 6 or len(p1) < 6:
        return out
    carrier_step = 21 if mode == "swiss" else 25
    max_n = 42 if mode == "swiss" else 50

    # Detect carrier-walker delta across P3-P6 (back row)
    deltas = []
    for i in (2, 3, 4, 5):
        if i >= len(p2) or i >= len(p1):
            continue
        b2_carrier = p2[i] - carrier_step if p2[i] > carrier_step else p2[i] + carrier_step
        delta = p1[i] - b2_carrier
        deltas.append(delta)
    if not deltas:
        return out
    # If 3+ of 4 back positions share same delta → walker detected
    from collections import Counter as _C
    delta_count = _C(deltas)
    dominant, count = delta_count.most_common(1)[0]
    if count < 3:
        return out

    # Project: apply same dominant delta to BD-1's carriers (forward continuation)
    for i, p in enumerate(p1):
        c = p - carrier_step if p > carrier_step else p + carrier_step
        proj = c + dominant
        while proj > max_n:
            proj -= max_n
        if proj < 1:
            proj += max_n
        out[proj].append(f"l3d-walker Δ={dominant} from P{i+1}={p}")
    # Also project reverse-walker (carrier minus delta = "swing-back")
    for i, p in enumerate(p1):
        c = p - carrier_step if p > carrier_step else p + carrier_step
        proj = c - dominant
        while proj < 1:
            proj += max_n
        while proj > max_n:
            proj -= max_n
        out[proj].append(f"l3d-walker reverse Δ=-{dominant} from P{i+1}={p}")
    return out


async def _gather_signals(target_date: str, mode: str) -> Dict:
    """Run all engines in parallel-ish (asyncio sequential, all light)."""
    from year_d_ledger import load_draws, parse_dt
    from .ghost_orchestrator import build_ghost_ledger
    from .hidden_prince import hidden_prince_pipeline

    out = {"target_date": target_date, "mode": mode}

    target_dt = parse_dt(target_date)
    if not target_dt:
        out["error"] = f"invalid target_date '{target_date}'"
        return out

    # Ghost ledger
    gl = await build_ghost_ledger(target_date, mode, lookback=10)
    out["ghost_ledger"] = gl

    # Cosmic voices
    try:
        from cosmic_voices.orchestrator import run_cosmic_voices
        cv = await run_cosmic_voices(target_date=target_date, mode=mode, lens="all")
        out["cosmic_voices"] = cv
    except Exception as e:
        out["cosmic_voices"] = {"error": str(e)}

    # Swiss Brain extras (Swiss only)
    if mode == "swiss":
        try:
            from swiss_brain import build_swiss_symphony
            sb = await build_swiss_symphony(target_date, count=6)
            out["swiss_brain"] = sb
        except Exception as e:
            out["swiss_brain"] = {"error": str(e)}

    # Hungry plate from recent 10
    all_draws = await load_draws(mode)
    past = sorted(
        [d for d in all_draws if d["dt"] < target_dt], key=lambda x: x["dt"]
    )
    recent10 = past[-10:]
    out["recent_draws"] = recent10
    out["hungry_plate"] = dict(hungry_plate(recent10, mode))
    out["sister_dates"] = sister_date_precedents(target_dt, all_draws, mode)
    # 🪞 S40 new lenses
    out["circle_discharge"] = dict(recent_high_circles(recent10, mode))
    out["l3d_walker"] = dict(l3d_gap_walker(recent10, mode))

    # Hidden Prince pipeline
    max_main = 42 if mode == "swiss" else 50
    max_lucky = 6 if mode == "swiss" else 12
    last_euro_mains: List[int] = []
    if mode == "swiss":
        euros = await load_draws("euro")
        past_eu = sorted(
            [d for d in euros if d["dt"] < target_dt], key=lambda x: x["dt"]
        )
        if past_eu:
            last_euro_mains = past_eu[-1].get("p", [])

    hungry_pool: Set[int] = set(out["hungry_plate"].keys())
    for g in gl.get("alive_ghosts", []):
        hungry_pool.add(g["n"])
        hungry_pool.update(g.get("projected_hot_zone", []))
    for n in gl.get("convergence", {}).get("shout", []):
        hungry_pool.add(n)
    fugues = hidden_prince_pipeline(
        recent_draws=recent10,
        hungry_pool=hungry_pool,
        last_euro_mains=last_euro_mains,
        ghost_shout=gl.get("convergence", {}).get("shout", []),
        max_lucky=max_lucky,
        max_main=max_main,
        top_k=4,
    )
    out["princes"] = fugues
    return out


def build_palette(signals: Dict, mode: str) -> Dict[int, Dict]:
    """Score every candidate by counting how many lenses ring on it."""
    palette: Dict[int, Dict] = {}
    max_n = 50 if mode == "euro" else 42

    # Ghost ledger
    gl = signals.get("ghost_ledger", {})
    for r in gl.get("convergence", {}).get("ranked", [])[:30]:
        n = r["n"]
        # Cap to prevent low-band alive ghosts from dominating
        capped = min(r["score"], 12)
        _accumulate(palette, n, capped, f"ghost:{', '.join(r['tags'][:2])}")
    for g in gl.get("alive_ghosts", []):
        _accumulate(palette, g["n"], 3, f"alive-ghost(age={g['age']})")
        # Hot-zone weight reduced from 1 to 0.5 (rounded; given as 1 per)
        # Limit hot-zones to top 3 per ghost
        for v in g.get("projected_hot_zone", [])[:3]:
            _accumulate(palette, v, 1, f"hot-zone of g{g['n']}")
        for v in g.get("carriers", [])[:2]:
            _accumulate(palette, v, 1, f"carrier of g{g['n']}")
    for s in gl.get("saturation", {}).get("saturated", []):
        _accumulate(palette, s["n"], 2, f"sat×{s.get('count')}")

    # Cosmic voices convergence
    cv = signals.get("cosmic_voices", {}).get("voices", {})
    conv = cv.get("convergence_scorer", {}) if isinstance(cv, dict) else {}
    for r in (conv.get("ranked_mains_expanded") or conv.get("ranked_mains") or [])[:30]:
        if isinstance(r, dict):
            n = r.get("n")
            sc = r.get("score", 1)
            tags = r.get("tags", [])
        else:  # tuple fallback
            n = r[0] if r else None
            sc = 1
            tags = []
        if n:
            _accumulate(palette, int(n), int(sc) if isinstance(sc, (int, float)) else 1,
                        f"voices:{', '.join(tags[:2]) if tags else 'conv'}")

    # Hungry plate
    for n, reasons in signals.get("hungry_plate", {}).items():
        _accumulate(palette, int(n), min(len(reasons), 3), f"hungry:{reasons[0]}")

    # 🪞 S40-lens: recent-fired high numbers' circles (DJ canon 13.05.2026)
    # Strong weight — these are PROVEN historical discharge points
    for n, reasons in signals.get("circle_discharge", {}).items():
        _accumulate(palette, int(n), 10 + min(4, len(reasons) * 2),
                    f"🪞{reasons[0]}")

    # 🎼 S40-lens: L3D carrier-walker projection (forward + reverse)
    # Forward walker = continuation, reverse = swing-back (both relevant)
    for n, reasons in signals.get("l3d_walker", {}).items():
        # Count forward vs reverse
        fwd = sum(1 for r in reasons if "reverse" not in r)
        rev = sum(1 for r in reasons if "reverse" in r)
        # Forward Δ=8 each, reverse Δ=6 each (forward slightly louder)
        w = fwd * 8 + rev * 6
        _accumulate(palette, int(n), w, f"🎼{reasons[0]}")

    # Sister-date precedents — each precedent main gets weight
    for prec in signals.get("sister_dates", []):
        for m in prec.get("mains", []):
            _accumulate(palette, int(m), 2, f"sister-date {prec['year']}")

    # Princes — boost prince's pair members
    for p in signals.get("princes", []):
        for v in p.get("mains", []):
            _accumulate(palette, int(v), 3, f"prince-pair (X={p['prince']})")

    # Swiss-specific extras
    if mode == "swiss":
        sb = signals.get("swiss_brain", {})
        for tk in sb.get("tickets", [])[:6]:
            for v in tk.get("mains", []):
                _accumulate(palette, int(v), 1, f"swiss-symphony:{tk.get('story', '?')[:18]}")

    # Cap to range
    return {n: v for n, v in palette.items() if 1 <= n <= max_n}


# ─── Story Composition — backward from P6 ──────────────────────────────
def _pick_top(palette: Dict[int, Dict], k: int = 12, exclude: Optional[Set[int]] = None) -> List[int]:
    exclude = exclude or set()
    items = [
        (n, v["score"]) for n, v in palette.items() if n not in exclude
    ]
    items.sort(key=lambda x: (-x[1], x[0]))
    return [n for n, _ in items[:k]]


def _compose_one_story(
    theme: str,
    palette: Dict[int, Dict],
    signals: Dict,
    p6_seed: int,
    mode: str,
    used_globally: Set[int],
    diversity_idx: int = 0,
    freq: Optional[Counter] = None,
    freq_cap: int = 99,
) -> Optional[Dict]:
    """Compose a single ticket backward from P6 seed.

    `diversity_idx` rotates pick-priority for P5/P4/P3/P2 so different themes
    produce different mid-row picks even when palette overlaps heavily.
    `freq` tracks how often each n has been used; numbers near `freq_cap`
    get a strong score penalty to force diversity.

    Returns a ticket dict with mains, story_arc, number_dna.
    """
    freq = freq or Counter()

    def _adj_score(n: int, base: int) -> int:
        """Penalty for over-used numbers."""
        f = freq[n]
        if f >= freq_cap:
            return base - 100  # hard reject
        return base - (f * 8)  # soft penalty per prior use

    max_n = 42 if mode == "swiss" else 50
    n_mains = 6 if mode == "swiss" else 5
    if p6_seed is None or not (1 <= p6_seed <= max_n):
        return None

    mains: List[int] = [p6_seed]
    story_arc: List[str] = [f"P{n_mains}={p6_seed} · anchor: {theme}"]
    number_dna: Dict[int, List[str]] = {p6_seed: palette.get(p6_seed, {}).get("lenses", [])[:4]}

    seed_conn = _connections(p6_seed, mode)

    # P5: candidates score with seed-aware bonuses + freq penalty
    candidates_p5 = []
    for n, v in palette.items():
        if n in mains:
            continue
        bonus = 0
        if n == seed_conn.get("circle"):
            bonus += 6
        if n == seed_conn.get("carrier_minus25") or n == seed_conn.get("carrier_minus21"):
            bonus += 5
        if abs(n - p6_seed) == 10:
            bonus += 4
        if 1 <= p6_seed - n <= 8:
            bonus += 2
        candidates_p5.append((n, _adj_score(n, v["score"] + bonus)))
    candidates_p5.sort(key=lambda x: -x[1])
    sub_p5 = [n for n, _ in candidates_p5 if n < p6_seed and n not in mains]
    pick_idx = diversity_idx % max(1, min(3, len(sub_p5)))
    if sub_p5:
        p5 = sub_p5[pick_idx if pick_idx < len(sub_p5) else 0]
        mains.insert(0, p5)
        tags = []
        if p5 == seed_conn.get("circle"):
            tags.append("circle-twin of P6")
        if abs(p5 - p6_seed) == 10:
            tags.append("10-shift of P6")
        if not tags:
            tags.append(f"gap {p6_seed-p5}")
        story_arc.append(f"P{n_mains-1}={p5} · " + " · ".join(tags))
        number_dna[p5] = palette.get(p5, {}).get("lenses", [])[:4] + tags

    # P4 → P2: build by descending, varying mid-position picks by diversity
    while len(mains) < n_mains - 1:
        cur_pos = n_mains - len(mains)
        top_floor = mains[0]
        candidates = []
        for n, v in palette.items():
            if n in mains:
                continue
            if n >= top_floor:
                continue
            bonus = 0
            if cur_pos == n_mains - 2:
                gap = top_floor - n
                if 2 <= gap <= 12:
                    bonus += 3
                if n in signals.get("hungry_plate", {}):
                    bonus += 1
            if cur_pos == 3:
                if str(n).endswith(("0", "5")):
                    bonus += 1
            candidates.append((n, _adj_score(n, v["score"] + bonus)))
        candidates.sort(key=lambda x: -x[1])
        if not candidates:
            break
        offset = (diversity_idx + cur_pos) % max(1, min(4, len(candidates)))
        pick = candidates[offset if offset < len(candidates) else 0][0]
        mains.insert(0, pick)
        role = {n_mains - 2: "bridge", 3: "voice", 2: "pivot"}.get(cur_pos, "fill")
        story_arc.append(f"P{cur_pos}={pick} · {role}")
        number_dna[pick] = palette.get(pick, {}).get("lenses", [])[:4]

    # P1: snap-back 1-9, deep rotation per theme + freq penalty
    p1_pool = [n for n in palette if n <= 9 and n not in mains]
    p1_pool.sort(key=lambda n: -_adj_score(n, palette[n]["score"]))
    if p1_pool:
        p1_idx = diversity_idx % len(p1_pool)
        p1 = p1_pool[p1_idx]
    else:
        rem = sorted(
            [n for n in palette if n not in mains and n < mains[0]],
            key=lambda n: (-_adj_score(n, palette[n]["score"]), n),
        )
        p1 = rem[0] if rem else max(1, mains[0] - 3)
    mains.insert(0, p1)
    story_arc.append(f"P1={p1} · snap-back front")
    number_dna[p1] = palette.get(p1, {}).get("lenses", [])[:4]

    mains = sorted(set(mains))[:n_mains]
    if len(mains) < n_mains:
        rem = sorted(
            [n for n in palette if n not in mains],
            key=lambda n: -_adj_score(n, palette[n]["score"]),
        )
        for n in rem:
            mains.append(n)
            number_dna[n] = palette.get(n, {}).get("lenses", [])[:4]
            if len(mains) >= n_mains:
                break
        mains = sorted(set(mains))[:n_mains]

    cosmic_score = sum(palette.get(n, {}).get("score", 0) for n in mains)
    return {
        "theme": theme,
        "mains": mains,
        "p6": mains[-1],
        "story_arc": story_arc,
        "number_dna": {n: number_dna.get(n, []) for n in mains},
        "cosmic_score": cosmic_score,
    }


def _crown_companions(
    ticket: Dict, signals: Dict, mode: str
) -> Dict:
    """Crown Lucky (Swiss) or Stars (Euro) based on Prince + recent."""
    if mode == "swiss":
        # Prefer crowned prince Lucky from S39 pipeline
        princes = signals.get("princes", [])
        if princes:
            ticket["lucky"] = princes[0].get("lucky", 4)
            ticket["lucky_why"] = f"Hidden Prince X={princes[0].get('prince')} crowned"
        else:
            ticket["lucky"] = 4
            ticket["lucky_why"] = "Q2d11 canon default"
        # Replay: 1 dominant streak unless told otherwise
        ticket["replay"] = 1
        ticket["replay_why"] = "R=1 dominant streak"
    else:  # euro
        recent = signals.get("recent_draws", [])
        last_stars = recent[-1].get("stars", []) if recent else []
        # Star King formulas (S4): S2-S1 = P1 candidate (8.2%), S1+S2 small
        if len(last_stars) == 2:
            s1, s2 = sorted(last_stars)
            cand1 = max(1, min(12, s2 - s1)) if s2 > s1 else 1
            cand2 = max(1, min(12, s1 + s2 - 6))
            ticket["stars"] = sorted(set([cand1, cand2]))[:2]
            if len(ticket["stars"]) < 2:
                ticket["stars"] = sorted(set(ticket["stars"] + [3, 6]))[:2]
            ticket["stars_why"] = f"S2-S1={cand1} / S1+S2-6={cand2} (King-formulas)"
        else:
            ticket["stars"] = [3, 6]
            ticket["stars_why"] = "default DJ ⭐(3,6)"
    return ticket


# ─── Public entrypoint ─────────────────────────────────────────────────
def _p1_silent_state(signals: Dict, target_n: int = 9, lookback: int = 30) -> Dict:
    """Canon 28 + P1=9 INJECT MANDATE state-tracker.
    Returns {'p1_silent': bool, 'p1_fires': int, 'lookback': N} for `target_n`
    at the P1 (smallest-main) position across the last `lookback` Swiss draws.
    """
    recent = signals.get("recent_draws", []) or []
    if not recent:
        # fall back to gl saturation history if available
        gl = signals.get("ghost_ledger", {}) or {}
        recent = gl.get("recent", []) or []
    # Use most recent N draws
    window = recent[-lookback:] if len(recent) > lookback else recent
    fires = 0
    for d in window:
        mains = sorted(d.get("p") or d.get("mains") or [])
        if mains and mains[0] == target_n:
            fires += 1
    return {
        "target_n": target_n,
        "lookback": len(window),
        "p1_fires": fires,
        "p1_silent": fires == 0,
    }


def _inject_p1_9_swiss(
    stories: List[Dict],
    palette: Dict[int, Dict],
    signals: Dict,
    count: int,
) -> List[Dict]:
    """🎯 P1=9 INJECT MANDATE (DJ canon 26.05.2026 night):
        'every 10 gen at least 2 tickets p1-9 Until it happens'

    When 9 is still P1-silent in the active Swiss walk, FORCE at least
    ceil(count * 0.2) tickets in the batch to carry P1=9. Mandate releases
    automatically when 9 has fired at P1 in the recent window (Canon 28).

    The injected tickets keep their other mains intact: lowest non-9 main
    is dropped if 9 is already present in mid-row, else 9 replaces P1.
    """
    state = _p1_silent_state(signals, target_n=9, lookback=30)
    if not state["p1_silent"]:
        # Mandate released — 9 has fired at P1 recently
        for s in stories:
            s["p1_9_mandate"] = "released"
        return stories

    required = max(2, (count * 2 + 9) // 10)  # ceil(count/5), min 2
    already = sum(1 for s in stories if s.get("mains") and min(s["mains"]) == 9)
    need = max(0, required - already)

    if need == 0:
        for s in stories:
            if s.get("mains") and min(s["mains"]) == 9:
                s["p1_9_injected"] = True
                s["p1_9_mandate"] = "active"
        return stories

    # Sort stories by lowest cosmic score (modify weakest first), preserving order
    indexed = sorted(
        [(i, s) for i, s in enumerate(stories)],
        key=lambda kv: kv[1].get("cosmic_score", 0),
    )
    modified = 0
    n_mains = 6  # Swiss
    for i, story in indexed:
        if modified >= need:
            break
        mains = sorted(story.get("mains") or [])
        if not mains or mains[0] == 9:
            continue
        # Build new ticket: 9 at P1 + top mains > 9 from original (keep ≤5)
        top_others = sorted([n for n in mains if n > 9], reverse=True)[:n_mains - 1]
        new_mains = sorted([9] + top_others)
        # If still under n_mains, top up from palette (>9 only)
        while len(new_mains) < n_mains:
            candidates = sorted(
                [n for n in palette if n not in new_mains and n > 9],
                key=lambda n: -palette[n]["score"],
            )
            if not candidates:
                break
            new_mains = sorted(new_mains + [candidates[0]])
        if len(new_mains) != n_mains or min(new_mains) != 9:
            continue
        story["mains"] = new_mains
        story["p1_9_injected"] = True
        story["p1_9_mandate"] = "active"
        story["story_arc"] = (
            ["P1=9 · 🎯 DJ-MANDATE (Canon 28 silent debt — carrier of HUGE-P1=30)"]
            + [arc for arc in (story.get("story_arc") or []) if not arc.startswith("P1=")]
        )
        # Recompute cosmic score
        story["cosmic_score"] = sum(
            palette.get(n, {}).get("score", 0) for n in new_mains
        )
        modified += 1

    # Flag the rest with mandate-active
    for s in stories:
        s.setdefault("p1_9_mandate", "active")
        if s.get("mains") and min(s["mains"]) == 9:
            s["p1_9_injected"] = True

    return stories


def _enforce_p3_low_cap(stories: List[Dict], mode: str, count: int) -> List[Dict]:
    """🪞 DJ Canon (09.06.2026) — P3 < 10 cap.

    Of `count` tickets, at most `floor(count / 5)` (≈2 per 10) may have P3 < 10.
    Excess tickets get their offending low number lifted via the One Law circle
    (`mirror_canon.mirror_of` — Swiss +21, Euro +25).

    P3 = the 3rd-lowest main = mains[2] (0-indexed, sorted ascending).
    """
    try:
        from mirror_canon import mirror_of as _circle
    except Exception:
        return stories  # canon unavailable — skip silently

    max_n = 42 if mode == "swiss" else 50
    cap = max(1, count // 5)  # 2 of 10, 3 of 15, etc.

    # Tag offenders (P3<10) sorted by COSMIC score ascending —
    # weakest stories get lifted first, strongest keep their natural shape.
    offenders = [
        (i, s) for i, s in enumerate(stories)
        if len(s.get("mains") or []) >= 3 and sorted(s["mains"])[2] < 10
    ]
    if len(offenders) <= cap:
        return stories

    offenders.sort(key=lambda kv: kv[1].get("cosmic_score", 0))
    to_lift = offenders[:len(offenders) - cap]

    for idx, story in to_lift:
        mains_sorted = sorted(story["mains"])
        p3_old = mains_sorted[2]
        circle_partner = _circle(p3_old, mode)
        # Validate: must be in universe, not already present
        if not (1 <= circle_partner <= max_n) or circle_partner in mains_sorted:
            # fallback: try lifting P2 or P1 instead
            for back_pos in (1, 0):
                p_old = mains_sorted[back_pos]
                if p_old >= 10:
                    continue
                alt = _circle(p_old, mode)
                if 1 <= alt <= max_n and alt not in mains_sorted:
                    circle_partner = alt
                    p3_old = p_old
                    break
            else:
                continue  # can't safely lift — leave it
        new_mains = sorted(n for n in mains_sorted if n != p3_old) + [circle_partner]
        new_mains.sort()
        story["mains"] = new_mains
        # Annotate the lift for transparency
        lifts = story.setdefault("p3_low_lifts", [])
        lifts.append(f"{p3_old}→{circle_partner} (One Law circle)")
        # Stamp the narrative so the UI shows what happened
        arc = story.get("story_arc") or []
        arc.append(f"🪞 P3<10 cap → circled {p3_old}→{circle_partner}")
        story["story_arc"] = arc

    return stories




async def compose_stories(
    target_date: str,
    mode: str = "swiss",
    count: int = 10,
) -> Dict:
    """Compose N ticket-stories for the target date.

    Each story has its own narrative theme but draws from the UNIFIED palette
    that fuses Brain + Ghost Pool + Hungry + Prince + Sister-date + Swiss Brain.
    """
    mode = mode.lower().strip()
    if mode not in ("euro", "swiss"):
        return {"error": "mode must be 'euro' or 'swiss'"}

    signals = await _gather_signals(target_date, mode)
    if signals.get("error"):
        return signals

    palette = build_palette(signals, mode)
    if not palette:
        return {"error": "empty palette", "signals_keys": list(signals.keys())}

    # Pick P6 anchor candidates by theme
    gl = signals.get("ghost_ledger", {})
    sat_ns = [s["n"] for s in gl.get("saturation", {}).get("saturated", [])]
    shout = gl.get("convergence", {}).get("shout", [])

    max_n = 42 if mode == "swiss" else 50
    top_pool = _pick_top(palette, k=25)
    # High-band candidates: prefer top 25% of the range for P6 anchor
    high_band_threshold = max_n - 16  # 26 for swiss, 34 for euro
    high_pool_palette = [n for n in palette if n >= high_band_threshold]
    high_pool_palette.sort(key=lambda n: -palette[n]["score"])

    themes: List[Tuple[str, int]] = []
    seen_p6: Set[int] = set()

    def _add_theme(label: str, seed: Optional[int]):
        if seed is None or not (1 <= seed <= max_n):
            return
        if seed in seen_p6:
            return
        themes.append((label, seed))
        seen_p6.add(seed)

    # 1. HUGE-Tail / Saturation Anchor — high-band saturated
    if sat_ns:
        sat_high = [n for n in sat_ns if n >= high_band_threshold]
        if sat_high:
            _add_theme("Saturation Cascade", sat_high[0])

    # 1.5 🪞 Circle-Discharge Anchor — DJ canon 13.05.2026
    # High recent-fired numbers discharge through their carriers (n-21)
    # When this fires, the carriers usually cluster in mid-band
    circ = signals.get("circle_discharge", {})
    if circ:
        # Build anchor from the LOUDEST carriers (most reasons → most recent highs)
        circ_top = sorted(circ.items(), key=lambda kv: -len(kv[1]))
        for c, reasons in circ_top[:3]:
            # Pair the carrier with a high-band P6 that respects the discharge
            # Find a high palette anchor that's a +21 carrier of c (i.e. the source)
            source = c + (21 if mode == "swiss" else 25)
            if 1 <= source <= max_n and source in palette:
                _add_theme(f"Circle-Discharge {source}→{c}", source)
            else:
                _add_theme(f"Circle-Discharge anchor {c}",
                           high_pool_palette[0] if high_pool_palette else c)

    # 1.6 🎼 L3D Carrier-Walker Anchor — DJ canon 13.05.2026
    walker = signals.get("l3d_walker", {})
    if walker:
        # Loudest walker projection that's high-band
        walker_high = sorted(
            [(n, len(r)) for n, r in walker.items() if n >= high_band_threshold],
            key=lambda kv: -kv[1],
        )
        for n, _ in walker_high[:2]:
            _add_theme(f"L3D Walker P6={n}", n)
    # 2. Carrier Anchor — alive ghost's high-band carrier
    for g in gl.get("alive_ghosts", [])[:8]:
        for c in g.get("carriers", []):
            if c >= high_band_threshold and c <= max_n:
                _add_theme(f"Carrier Anchor ({g['n']}→{c})", c)
                break
        if len(themes) >= 2:
            break
    # 3. Sleeping-Voice Anchor — high-band shout numbers
    for n in shout:
        if n >= high_band_threshold:
            _add_theme(f"Sleeping High Voice {n}", n)
            if sum(1 for t in themes if "Sleeping" in t[0]) >= 2:
                break
    # 4. Sister-date Anchor — last year's same-date max + 2nd-max
    for prec in signals.get("sister_dates", [])[:4]:
        ms = sorted(prec.get("mains") or [])
        if ms:
            if ms[-1] >= high_band_threshold:
                _add_theme(f"Sister-Date {prec['year']} P6", ms[-1])
            if len(ms) >= 2 and ms[-2] >= high_band_threshold:
                _add_theme(f"Sister-Date {prec['year']} P5", ms[-2])
    # 5. Quarter-Shape Anchor — top high palette
    qs = gl.get("quarter_shape", {})
    if qs.get("dominant_shape") and high_pool_palette:
        _add_theme(
            f"Quarter Shape {qs['dominant_shape']}",
            high_pool_palette[0],
        )
    # 6. Mirror-Axis Anchor (28-pair high) — for each low n in top pool, get high mirror
    for n in top_pool[:10]:
        m = (56 - n) if n < 28 else None
        if m and m in palette and m >= high_band_threshold:
            _add_theme(f"28-Mirror Pair ({n}↔{m})", m)
            break
    # 7. Sneaky Dodge — top shout ±10 (S39 Canon 2)
    for sh in shout[:5]:
        for delta in (10, -10):
            sneaky = sh + delta
            if 1 <= sneaky <= max_n and sneaky >= high_band_threshold:
                _add_theme(f"Sneaky ±10 of {sh}", sneaky)
                break
        if any("Sneaky" in t[0] for t in themes):
            break
    # 8. Sinking-Voice trail → high-band landing
    sv_data = signals.get("cosmic_voices", {}).get("voices", {}).get("sinking_voice", {})
    sinks = sv_data.get("trails") if isinstance(sv_data, dict) else None
    if isinstance(sinks, list) and sinks:
        last_p2 = sinks[0].get("last_p2")
        if isinstance(last_p2, int):
            sink_p6 = last_p2 + 22
            if sink_p6 > max_n:
                sink_p6 = max_n - 1
            _add_theme(f"Sinking Voice→P6={sink_p6}", sink_p6)
    # 9. Hidden Prince theme — when high-scoring
    princes = signals.get("princes", [])
    if princes:
        top_prince = princes[0]
        if top_prince.get("score", 0) >= 8 and top_prince.get("mains"):
            mx = max(top_prince["mains"])
            if mx >= high_band_threshold:
                _add_theme(
                    f"Hidden Prince X={top_prince['prince']}",
                    mx,
                )
    # 10. Top-Palette High — pure score king (always-on)
    for n in high_pool_palette[:6]:
        _add_theme(f"Top-Palette High @{n}", n)
        if sum(1 for t in themes if "Top-Palette" in t[0]) >= 3:
            break
    # 11. Cosmic-Voices high band picks
    voices_ranked = (
        signals.get("cosmic_voices", {}).get("voices", {})
        .get("convergence_scorer", {})
        .get("ranked_mains_expanded")
        or []
    )
    for r in voices_ranked[:15]:
        n = r.get("n") if isinstance(r, dict) else r
        if isinstance(n, int) and n >= high_band_threshold:
            _add_theme(f"Voices high @{n}", n)
            if sum(1 for t in themes if "Voices high" in t[0]) >= 3:
                break

    # If still under count anchors, fill with descending palette high band
    fallback = [n for n in top_pool if n not in seen_p6]
    fallback.sort(key=lambda n: (-int(n >= high_band_threshold), -palette[n]["score"]))
    for n in fallback:
        if len(themes) >= count + 6:
            break
        _add_theme(f"Palette echo @{n}", n)

    # Compose
    stories: List[Dict] = []
    used_globally: Set[int] = set()
    dup_cap = 5 if mode == "swiss" else 4  # max overlap before reject
    soft_dup_cap = 6 if mode == "swiss" else 5
    # 🪞 S40: per-number frequency cap across all tickets (DJ critique — no carpet-bomb)
    max_freq = max(2, (count + 1) // 2)  # ≤ ceil(count/2)
    freq: Counter = Counter()

    def _is_carpet(story: Dict) -> bool:
        # Reject if 3+ numbers in this story already at max_freq
        over = sum(1 for n in story["mains"] if freq[n] >= max_freq)
        return over >= 3

    for theme_idx, (theme, p6) in enumerate(themes):
        if len(stories) >= count:
            break
        story = _compose_one_story(
            theme, palette, signals, p6, mode, used_globally,
            diversity_idx=theme_idx, freq=freq, freq_cap=max_freq,
        )
        if not story:
            continue
        is_dup = False
        for prior in stories:
            overlap = len(set(story["mains"]) & set(prior["mains"]))
            if overlap >= dup_cap:
                is_dup = True
                break
        if not is_dup and _is_carpet(story):
            is_dup = True
        if is_dup:
            for retry in range(1, 8):
                alt = _compose_one_story(
                    theme, palette, signals, p6, mode, used_globally,
                    diversity_idx=theme_idx + retry * 5,
                    freq=freq, freq_cap=max_freq,
                )
                if not alt:
                    continue
                clash = any(
                    len(set(alt["mains"]) & set(p["mains"])) >= dup_cap
                    for p in stories
                ) or _is_carpet(alt)
                if not clash:
                    story = alt
                    is_dup = False
                    break
            if is_dup and len(stories) < count // 2:
                soft_alt = _compose_one_story(
                    theme, palette, signals, p6, mode, used_globally,
                    diversity_idx=theme_idx, freq=freq, freq_cap=max_freq + 1,
                )
                if soft_alt and not any(
                    len(set(soft_alt["mains"]) & set(p["mains"])) >= soft_dup_cap
                    for p in stories
                ):
                    story = soft_alt
                    is_dup = False
        if is_dup:
            continue
        _crown_companions(story, signals, mode)
        story["narrative"] = " → ".join(story["story_arc"])
        stories.append(story)
        used_globally.update(story["mains"])
        for n in story["mains"]:
            freq[n] += 1

    # 🎯 P1=9 INJECT MANDATE (Swiss only — Canon 28 silent debt enforcement)
    if mode == "swiss":
        stories = _inject_p1_9_swiss(stories, palette, signals, count)

    # 🪞 P3<10 CAP (DJ Canon 33, 09.06.2026 PM) — universal distribution guard
    # Caps: P1<5 ≤30%, P3<10 ≤15%, P3∈[11-15] ≤20%. Lifts via One Law circle.
    try:
        from ticket_distribution_guard import enforce_distribution_caps
        enforce_distribution_caps(stories, mode, mains_key="mains")
    except Exception:
        # Fallback to legacy P3<10 cap if the guard module is missing
        stories = _enforce_p3_low_cap(stories, mode, count)

    # Sort: highest cosmic_score first
    stories.sort(key=lambda s: -s.get("cosmic_score", 0))

    # Final palette for UI
    palette_view = sorted(
        [
            {"n": n, "score": v["score"], "lenses": v["lenses"][:5],
             "connections": _connections(n, mode)}
            for n, v in palette.items()
        ],
        key=lambda x: (-x["score"], x["n"]),
    )[:30]

    return {
        "target_date": target_date,
        "mode": mode,
        "count_requested": count,
        "count_returned": len(stories),
        "palette": palette_view,
        "hungry_plate": [
            {"n": int(n), "reasons": list(reasons)[:4]}
            for n, reasons in sorted(
                signals.get("hungry_plate", {}).items(),
                key=lambda kv: -len(kv[1]),
            )[:18]
        ],
        "sister_date_precedents": signals.get("sister_dates", []),
        "princes": [
            {
                "prince": p.get("prince"),
                "score": p.get("score"),
                "why": p.get("why", []),
                "mains": p.get("mains", []),
                "lucky": p.get("lucky"),
            }
            for p in signals.get("princes", [])[:3]
        ],
        "ghost_shout": gl.get("convergence", {}).get("shout", []),
        "voices_shout": (
            signals.get("cosmic_voices", {})
            .get("voices", {})
            .get("convergence_scorer", {})
            .get("shout_zone_expanded")
            or signals.get("cosmic_voices", {})
            .get("voices", {})
            .get("convergence_scorer", {})
            .get("shout_zone")
            or []
        ),
        "stories": stories,
        "canon": (
            "S40 Story Composer — E fuses Brain (cosmic_voices) + Ghost Pool + "
            "Hungry Plate (S39 Canon 8) + Hidden Prince (S39 Canon 9) + "
            "Sister-Date Precedents + Swiss Brain into ONE narrative palette. "
            "Tickets compose backward (P6→P1) along themed story arcs; "
            "each number wears its lens-DNA."
        ),
    }
