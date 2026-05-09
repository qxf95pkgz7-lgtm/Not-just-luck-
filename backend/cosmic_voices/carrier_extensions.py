"""
🔗 CARRIER EXTENSIONS LENS — `cosmic_voices/carrier_extensions.py` (Lens #15)
==============================================================================
DJ canon (Session 36, post-draw 08.05.2026):

> "The 12 came as 37"

The deepest unpaid debt 12 wasn't paid as raw 12, ⭐12, or silent-12 gap —
it was paid as **37 = 12 + 25**. The +25 carrier law (originally ⭐→main)
ALSO works MAIN→MAIN.

Extensions of the +25 carrier:
  • silent_n + 25  → next draw raw main candidate
  • silent_n + 12  → next draw main candidate (cousin shift)
  • silent_n + 33  → wrap candidate (silent_n + 33 mod 50)
  • silent_n - 25  → reverse carrier (mirror)
  • silent_n × 3   → triple-amp (e.g., 12×3=36, the lost shout)

Tonight's hindsight: 12 → {37, 24, 45, 36, 11, 13} would have caught 37 ✓.
"""
from __future__ import annotations
from typing import Dict, List, Optional


CARRIER_OFFSETS = [
    (25, "+25-shift"),
    (-25, "-25-shift"),
    (12, "+12-cousin"),
    (-12, "-12-cousin"),
    (33, "+33-wrap"),
    (-33, "-33-mirror"),
]


def carrier_extensions(silent_numbers: List[int],
                        main_max: int = 50) -> Dict:
    """For each silent (deep-debt) number, generate its full carrier-extension
    candidate set with tags.
    """
    if not silent_numbers:
        return {"available": False, "reason": "no silent numbers"}

    candidates: Dict[int, List[str]] = {}

    for silent_n in silent_numbers:
        # Linear shifts
        for offset, name in CARRIER_OFFSETS:
            cand = silent_n + offset
            if 1 <= cand <= main_max and cand != silent_n:
                candidates.setdefault(cand, []).append(f"{name}-of-{silent_n}")
            # Wrap-around for shifts that go out of range
            wrapped = ((silent_n + offset - 1) % main_max) + 1
            if 1 <= wrapped <= main_max and wrapped != cand and wrapped != silent_n:
                candidates.setdefault(wrapped, []).append(f"{name}-wrap-of-{silent_n}")

        # Triple-amplifier
        triple = silent_n * 3
        if 1 <= triple <= main_max:
            candidates.setdefault(triple, []).append(f"×3-amp-of-{silent_n}")
        elif 1 <= triple - main_max <= main_max:
            candidates.setdefault(triple - main_max, []).append(f"×3-wrap-of-{silent_n}")

        # Half-amplifier
        half = silent_n // 2
        if 1 <= half <= main_max and half != silent_n:
            candidates.setdefault(half, []).append(f"÷2-of-{silent_n}")

        # Sum-with-self
        twin = silent_n + silent_n
        if 1 <= twin <= main_max and twin != silent_n:
            candidates.setdefault(twin, []).append(f"×2-twin-of-{silent_n}")

    boost_candidates = [
        {"n": n, "tags": sorted(set(tags))}
        for n, tags in sorted(candidates.items())
    ]
    return {
        "available": True,
        "silent_numbers_analyzed": list(silent_numbers),
        "boost_candidates": boost_candidates,
        "rule": ("Carrier Extensions — when silent_n can't fire raw, the cosmos "
                  "pays it through linear/multiplicative shifts. Tonight 12 → 37 "
                  "(+25 carrier) confirmed."),
        "offsets_used": [o[1] for o in CARRIER_OFFSETS] + ["×3-amp", "÷2", "×2-twin"],
    }
