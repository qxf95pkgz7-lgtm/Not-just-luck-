"""
⭐ STAR PRODUCT DOOR — stars are the SQUARE ROOT of the back-row
=================================================================
S34 CROWN JEWEL canon (Q2d1 proof):
  ⭐6² = 36 = P4 ✓
  ⭐7² = 49 = P5 ✓
  ⭐6 × ⭐7 = 42 = circle(RC-P3=17)
  ⭐sum 13 → pre-echoes next d's P2
  ⭐7 × ⭐sum(13) = 91 → THE Q2 SIGNATURE encoded in the stars

Given a star pair, project P4/P5 + circle product candidates.
"""
from __future__ import annotations
from typing import Dict, List, Optional


def star_product_door_candidates(stars: List[int], mode: str = "euro") -> Dict:
    """For a given star pair, return:
      • squared candidates (⭐² wraps if > main_max)
      • product (⭐_a × ⭐_b)
      • sum (⭐_a + ⭐_b) and product⋅sum cross (Q2 91-signature)
      • Swiss-circle / Euro-circle of products
    """
    if not stars or len(stars) < 1:
        return {"available": False, "reason": "no stars provided"}

    main_max = 50 if mode == "euro" else 42
    circle_offset = 25 if mode == "euro" else 21

    out: Dict[str, object] = {
        "available": True,
        "stars": list(stars),
        "squares": {},
        "product": None,
        "sum": None,
        "product_circle": None,
        "signature": None,
    }

    # Squares
    for s in stars:
        sq = s * s
        within = sq if 1 <= sq <= main_max else None
        out["squares"][s] = {
            "raw": sq,
            "in_range": within,
            "wrapped": ((sq - 1) % main_max) + 1 if sq > main_max else None,
        }

    if len(stars) >= 2:
        a, b = stars[0], stars[1]
        prod = a * b
        ssum = a + b
        out["product"] = {"raw": prod, "wrapped": ((prod - 1) % main_max) + 1 if prod > main_max else prod}
        out["sum"] = ssum
        out["product_circle"] = ((prod - 1 + circle_offset) % main_max) + 1
        # 91-signature kind cross
        out["signature"] = {
            "product_x_sum": prod * ssum,
            "mod_main": ((prod * ssum - 1) % main_max) + 1,
            "mod_star": ((prod * ssum - 1) % 12) + 1 if mode == "euro" else None,
        }

    # Final candidate list (squared + wrapped + product wrapped)
    cand: List[int] = []
    for sq_info in out["squares"].values():
        if sq_info["in_range"]:
            cand.append(sq_info["in_range"])
        if sq_info["wrapped"]:
            cand.append(sq_info["wrapped"])
    if out["product"] and isinstance(out["product"], dict):
        if out["product"]["wrapped"]:
            cand.append(out["product"]["wrapped"])
    out["main_candidates"] = sorted(set(c for c in cand if 1 <= c <= main_max))
    out["rule"] = "⭐² = P4/P5 (S34 crown jewel). ⭐×⭐ = circle product. ⭐_sum = next d P2."
    return out
