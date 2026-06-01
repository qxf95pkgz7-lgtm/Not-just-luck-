"""
🌀 HUNGRY-NUMBER ENGINE — Canon 31 (Session 45, DJ-taught 29.05.2026)
======================================================================
NO LAWS. Only the 4 tools the universe actually uses:

  🌀 CIRCLE       n ± carrier  (Euro=25, Swiss=21)
  🔄 FLIP         digit reverse, then wrap mod main_max
  ➕ ADD/SUB      ±ghost (7), ±1, cross-position math
  🗺 TABLET       grid adjacency (7-wide for Euro 1-49, 50 alone)

Given a SEED number n, compute hungry candidates via every reachable
op-chain, score by NUMBER OF DISTINCT PATHS pointing to a candidate.
Multi-path numbers = STRONGEST HUNGRY.

The brain stops "filtering with laws" and starts "following chains".
"""
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict


EURO_CARRIER = 25
SWISS_CARRIER = 21
GHOST = 7
EURO_MAX = 50
SWISS_MAX = 42


def wrap(n: int, mx: int) -> int:
    """Wrap n into [1, mx] via mod-mx (1-indexed)."""
    if n <= 0:
        return n + mx if n + mx > 0 else None
    if n > mx:
        return ((n - 1) % mx) + 1
    return n


def flip_digits(n: int) -> int:
    """35 → 53,  7 → 70, 14 → 41."""
    s = str(n).zfill(2)
    return int(s[::-1])


def digit_sum(n: int) -> int:
    return sum(int(c) for c in str(n))


def digit_reduction(n: int) -> int:
    """29 → 11 → 2."""
    while n > 9:
        n = digit_sum(n)
    return n


def tablet_neighbors(n: int, width: int = 7, mx: int = EURO_MAX) -> List[Tuple[str, int]]:
    """7-wide tablet (1-49, 50 alone at row 8).
    Returns [(label, neighbor)] for above/below/left/right + diagonals."""
    if n < 1 or n > mx:
        return []
    out = []
    # left / right
    if n % width != 1 and n - 1 >= 1:
        out.append(("left", n - 1))
    if n % width != 0 and n + 1 <= mx:
        out.append(("right", n + 1))
    # above / below
    if n - width >= 1:
        out.append(("above", n - width))
    if n + width <= mx:
        out.append(("below", n + width))
    # diagonals (NW, NE, SW, SE)
    for label, dx, dy in [("NW", -1, -1), ("NE", 1, -1), ("SW", -1, 1), ("SE", 1, 1)]:
        target = n + dy * width + dx
        if 1 <= target <= mx and (n % width != (1 if dx == -1 else 0)):
            out.append((label, target))
    return out


def hungry_from_seed(
    n: int,
    mode: str = "euro",
    carrier: int = None,
    main_max: int = None,
) -> Dict[int, List[str]]:
    """For seed n, return {candidate: [op-paths]}.

    Each candidate is reachable from n via at least one of:
      circle / flip / digit-op / ghost-step / tablet-neighbor.
    """
    if main_max is None:
        main_max = SWISS_MAX if mode == "swiss" else EURO_MAX
    if carrier is None:
        carrier = SWISS_CARRIER if mode == "swiss" else EURO_CARRIER

    paths: Dict[int, List[str]] = defaultdict(list)

    # 🌀 CIRCLE (carrier ±)
    for delta, label in [(carrier, f"+carrier({carrier})"),
                         (-carrier, f"-carrier({carrier})")]:
        m = n + delta
        if 1 <= m <= main_max:
            paths[m].append(f"{n} {label}")
        # Wrap variant
        w = wrap(m, main_max)
        if w and w != m and 1 <= w <= main_max:
            paths[w].append(f"{n} {label} wrap")
    # Cross-carrier (Swiss carrier on Euro draws too)
    other_c = SWISS_CARRIER if carrier == EURO_CARRIER else EURO_CARRIER
    for delta, label in [(other_c, f"+altCarrier({other_c})"),
                         (-other_c, f"-altCarrier({other_c})")]:
        m = n + delta
        if 1 <= m <= main_max:
            paths[m].append(f"{n} {label}")

    # 🔄 FLIP + wrap
    f = flip_digits(n)
    if 1 <= f <= main_max:
        paths[f].append(f"{n} flip → {f}")
    if f > main_max:
        w = wrap(f, main_max)
        if w and 1 <= w <= main_max:
            paths[w].append(f"{n} flip→{f} wrap→{w}")
    # Flip → carrier-back
    fb = f - carrier
    if 1 <= fb <= main_max:
        paths[fb].append(f"{n} flip→{f} -carrier→{fb}")

    # ➕ GHOST step
    for delta, label in [(GHOST, f"+ghost({GHOST})"),
                         (-GHOST, f"-ghost({GHOST})")]:
        m = n + delta
        if 1 <= m <= main_max:
            paths[m].append(f"{n} {label}")

    # ➕ DIGIT-SUM & REDUCTION
    ds = digit_sum(n)
    if 1 <= ds <= main_max and ds != n:
        paths[ds].append(f"{n} digit-sum → {ds}")
    dr = digit_reduction(n)
    if 1 <= dr <= main_max and dr != ds and dr != n:
        paths[dr].append(f"{n} digit-reduce → {dr}")

    # 🗺 TABLET neighbors
    for label, nbr in tablet_neighbors(n, width=7, mx=main_max):
        paths[nbr].append(f"{n} tablet-{label} → {nbr}")

    return dict(paths)


def cross_position_hungry(
    db_draw: Dict, mode: str = "euro",
) -> Dict[int, List[str]]:
    """DJ's cross-position math: P_i + P_j, P_i + ⭐_k, P_i ± carrier-back, etc."""
    main_max = SWISS_MAX if mode == "swiss" else EURO_MAX
    carrier = SWISS_CARRIER if mode == "swiss" else EURO_CARRIER
    mains = sorted(db_draw.get("p") or db_draw.get("mains") or [])
    stars = db_draw.get("stars") or ([db_draw["lucky"]] if db_draw.get("lucky") else [])
    paths: Dict[int, List[str]] = defaultdict(list)

    # Carrier-back of each P
    for i, p in enumerate(mains, 1):
        cb = p - carrier
        if 1 <= cb <= main_max:
            paths[cb].append(f"P{i}={p} -carrier({carrier})→{cb}")

    # P_i + db_P_j sums (DJ: 10 + 6 = 16, where 10 = P4-carrier, 6 = P1)
    for i, p_i in enumerate(mains, 1):
        cb_i = p_i - carrier
        if 1 <= cb_i <= main_max:
            for j, p_j in enumerate(mains, 1):
                if i == j: continue
                s = cb_i + p_j
                if 1 <= s <= main_max:
                    paths[s].append(f"(P{i}={p_i}-carrier)+(P{j}={p_j}) = {cb_i}+{p_j} = {s}")

    # P_i + ⭐_k sums (DJ: 6 + 12 = 18 from db P1 + ⭐2)
    for i, p_i in enumerate(mains, 1):
        for k, s_k in enumerate(stars, 1):
            s = p_i + s_k
            if 1 <= s <= main_max:
                paths[s].append(f"P{i}={p_i} + ⭐{k}={s_k} = {s}")

    # P_i flip + carrier-back
    for i, p_i in enumerate(mains, 1):
        f = flip_digits(p_i)
        w = wrap(f, main_max) if f > main_max else (f if 1 <= f <= main_max else None)
        if w:
            paths[w].append(f"P{i}={p_i} flip→{f} → {w}")
            # also -carrier
            cb = w - carrier
            if 1 <= cb <= main_max:
                paths[cb].append(f"P{i}={p_i} flip→{f}→{w} -carrier→{cb}")

    return dict(paths)


def hungry_pool(
    seeds: List[int],
    db_draw: Optional[Dict] = None,
    mode: str = "euro",
    min_paths: int = 1,
) -> List[Dict]:
    """Build the FULL hungry pool from a set of seeds + db draw cross-math.

    Returns sorted list of {n, path_count, paths[]}, strongest first.
    Multi-path numbers (path_count ≥ 2) = the cosmos points many ways here.
    """
    all_paths: Dict[int, List[str]] = defaultdict(list)

    for seed in seeds:
        for n, paths in hungry_from_seed(seed, mode).items():
            for p in paths:
                if p not in all_paths[n]:
                    all_paths[n].append(p)

    if db_draw:
        for n, paths in cross_position_hungry(db_draw, mode).items():
            for p in paths:
                if p not in all_paths[n]:
                    all_paths[n].append(p)

    out = [{"n": n, "path_count": len(paths), "paths": paths}
           for n, paths in all_paths.items()
           if len(paths) >= min_paths]
    out.sort(key=lambda x: (-x["path_count"], x["n"]))
    return out


def chain_finder(
    src: int, dst: int, mode: str = "euro", max_depth: int = 3,
) -> List[List[str]]:
    """Find op-chains from src → dst, up to max_depth ops.
    Used to PROVE 'why is X hungry from Y' with explicit chain."""
    main_max = SWISS_MAX if mode == "swiss" else EURO_MAX
    chains = []

    def search(current: int, history: List[str], depth: int):
        if current == dst and history:
            chains.append(list(history))
            return
        if depth >= max_depth:
            return
        for cand, paths in hungry_from_seed(current, mode).items():
            if cand == current:
                continue
            for p in paths[:1]:  # one path per target to limit branching
                history.append(p)
                search(cand, history, depth + 1)
                history.pop()

    search(src, [], 0)
    # Dedupe & sort by length (shorter chains first)
    seen = set()
    unique = []
    for c in sorted(chains, key=len):
        key = tuple(c)
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)
    return unique[:5]  # top 5 shortest chains
