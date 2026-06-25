"""
🪞 ONE MIRROR ONE LAW — Canon 32 (Session 49, DJ-taught 09.06.2026)
====================================================================

For LOTTO NUMBERS, the mirror IS the circle (carrier shift).

  Swiss:  mirror(n) = { n+21 wrap, n-21 wrap }   carrier=21
  Euro:   mirror(n) = { n+25 wrap, n-25 wrap }   carrier=25

Examples taught by the DJ on 09.06.2026:
  EURO   19 → 44   ( 19+25 )         9 → 34  ( 9+25 )       1 → 26  ( 1+25 )
  SWISS  24 → 3    ( 24-21 )         4 → 25  ( 4+21 )       1 → 22  ( 1+21 )

The CALENDAR mirror (mirror(d) = 28-d, self-mirror at d=14 in Q=27 days)
is a DIFFERENT law in a DIFFERENT domain. It is NOT applied to lotto numbers.
See `quarter_mirror_day()` for the calendar version.

The OLD wrong mirrors that this law replaces:
  • 28 - n          (treated quarter-day formula as number-mirror — WRONG)
  • 43 - n / 51 - n / 56 - n / 100 - n   (arbitrary folding — WRONG)
  • mirror_low/mirror_high hybrid        (WRONG)
"""
from __future__ import annotations
from typing import Iterable, List, Set


SWISS_CARRIER = 21
EURO_CARRIER = 25
SWISS_MAX = 42
EURO_MAX = 50


def _carriers(mode: str) -> tuple[int, int]:
    return (SWISS_CARRIER, SWISS_MAX) if mode == "swiss" else (EURO_CARRIER, EURO_MAX)


def wrap_in_universe(n: int, mx: int) -> int:
    """Wrap n into [1, mx] (1-indexed)."""
    return ((n - 1) % mx) + 1


def mirror_pair(n: int, mode: str = "swiss") -> List[int]:
    """🪞 ONE LAW: mirror = circle. Returns the unique mirror partners of n.

    Returns at most 2 numbers: {n+carrier wrapped, n-carrier wrapped}.
    If both wrap to the same value (only possible at universe boundaries),
    returns a single element.
    """
    carrier, mx = _carriers(mode)
    up = wrap_in_universe(n + carrier, mx)
    dn = wrap_in_universe(n - carrier, mx)
    return [up] if up == dn else [up, dn]


def mirror_of(n: int, mode: str = "swiss") -> int:
    """Single-mirror form (chooses the +carrier side). Use when callers
    expect ONE partner per n (for back-compat with code expecting an int).

    For symmetric scoring, prefer `mirror_pair`.
    """
    pair = mirror_pair(n, mode)
    return pair[0]


def expand_with_mirrors(seeds: Iterable[int], mode: str = "swiss") -> Set[int]:
    """Take a seed set, add every seed's mirror pair to it. Returns the union."""
    out: Set[int] = set(seeds)
    for s in list(out):
        out.update(mirror_pair(s, mode))
    return out


def quarter_mirror_day(day_in_quarter: int) -> int:
    """🗓️ CALENDAR mirror (separate domain). Q=27 days; self-mirror at day=14.

      d  1 ↔ 27   (1 + 27 = 28)
      d  2 ↔ 26
      ...
      d 13 ↔ 15
      d 14 ↔ 14   ← only self-mirror

    NOT for lotto numbers. For lotto numbers use `mirror_pair()`.
    """
    if 1 <= day_in_quarter <= 27:
        return 28 - day_in_quarter
    raise ValueError(f"day_in_quarter must be in 1..27, got {day_in_quarter}")
