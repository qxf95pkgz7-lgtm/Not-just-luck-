"""
🚫 Anti-Tunnel Throttle (Session 31, DJ canon — 29.04.2026)

Diagnosis: legacy ticket builders (Top-Symphony, RC0-Closing,
Hungry-Family-Loaded, Outlier-Orchestra, etc.) produce tickets where one
"hot" lens-rich number (e.g. 29 on 01.05.2026 Euro) ends up in >90% of
the saved tickets. This is the same tunnel-vision Session 24 diagnosed.

Fix: post-process any list of tickets to enforce a per-non-pinned-number
cap of `max_share` of the batch. Pinned suspects (DJ-pin) bypass the
cap so they always survive.

Usage:
    from anti_tunnel import filter_anti_tunnel
    kept = filter_anti_tunnel(tickets, pinned=[16, 19, 26], max_share=0.65)
"""
from typing import List, Dict, Iterable, Optional


def _ticket_mains(t: Dict) -> List[int]:
    """Extract mains list regardless of whether the dict uses 'numbers'
    or 'mains' as the key (different builders use different conventions).
    """
    if not isinstance(t, dict):
        return []
    if 'mains' in t and isinstance(t['mains'], (list, tuple)):
        return list(t['mains'])
    if 'numbers' in t and isinstance(t['numbers'], (list, tuple)):
        return list(t['numbers'])
    return []


def filter_anti_tunnel(
    tickets: List[Dict],
    pinned: Optional[Iterable[int]] = None,
    max_share: float = 0.65,
    min_keep: int = 3,
    swap_universe: Optional[List[int]] = None,
) -> List[Dict]:
    """Walk tickets in given order; for any non-pinned number exceeding
    `max_share * len(tickets)`, SWAP that number out of the over-cap
    tickets with a value from `swap_universe` (or pinned itself) that
    fits the same slot.

    - `pinned` values bypass the cap (DJ-pin must always survive)
    - When `swap_universe` is None, defaults to using `pinned` values for
      the swap target (so over-used number is replaced by a DJ pin)
    - If no valid swap target exists for a slot, the ticket is dropped
      (subject to `min_keep` floor)
    """
    pinned_set = set(pinned or [])
    # Build a broad swap pool: pinned first (DJ priority), then fallback to
    # any value in the universe of currently-used numbers (encourages
    # cross-pollination across the kept tickets) PLUS the safe defaults.
    used_in_input = set()
    for t in tickets:
        for v in _ticket_mains(t):
            used_in_input.add(v)
    if swap_universe:
        swap_pool = list(swap_universe)
    else:
        # Prioritise pins, then alternate values seen in the batch
        swap_pool = list(pinned_set) + sorted(used_in_input - pinned_set)
    n = len(tickets)
    if n <= min_keep:
        return list(tickets)
    cap = max(min_keep, int(n * max_share))
    use: Dict[int, int] = {}
    out: List[Dict] = []

    def _under_cap(v: int) -> bool:
        if v in pinned_set:
            return True
        return use.get(v, 0) < cap

    for t in tickets:
        nums = list(_ticket_mains(t))
        if not nums:
            out.append(t)
            continue

        # Identify which numbers in this ticket would push past cap
        over_targets: List[int] = [n_v for n_v in nums
                                   if n_v not in pinned_set
                                   and use.get(n_v, 0) >= cap]

        if over_targets:
            new_nums = list(nums)
            for bad in over_targets:
                bad_idx = new_nums.index(bad)
                lo = new_nums[bad_idx - 1] if bad_idx > 0 else 0
                hi = (new_nums[bad_idx + 1]
                      if bad_idx < len(new_nums) - 1 else 999)
                replaced = False
                for cand in swap_pool:
                    if cand in new_nums or cand == bad:
                        continue
                    if not _under_cap(cand):
                        continue
                    if lo < cand < hi:
                        new_nums[bad_idx] = cand
                        replaced = True
                        break
                if not replaced:
                    new_nums = None
                    break
            if new_nums is None:
                continue
            t = dict(t)
            if 'mains' in t:
                t['mains'] = new_nums
            if 'numbers' in t:
                t['numbers'] = new_nums
            nums = new_nums

        out.append(t)
        for n_v in nums:
            use[n_v] = use.get(n_v, 0) + 1

    if len(out) < min_keep:
        return list(tickets)
    return out


def tunnel_diagnostics(
    tickets: List[Dict],
    pinned: Optional[Iterable[int]] = None,
) -> Dict:
    """Return per-number frequency + the worst-offender for diagnostics."""
    pinned_set = set(pinned or [])
    n = len(tickets)
    if n == 0:
        return {'total': 0, 'frequency': {}, 'worst': None}
    freq: Dict[int, int] = {}
    for t in tickets:
        for v in _ticket_mains(t):
            freq[v] = freq.get(v, 0) + 1
    non_pinned = [(v, c) for v, c in freq.items() if v not in pinned_set]
    worst = max(non_pinned, key=lambda x: x[1]) if non_pinned else None
    return {
        'total': n,
        'frequency': freq,
        'worst': worst,
        'worst_share': (worst[1] / n) if worst else 0,
    }
