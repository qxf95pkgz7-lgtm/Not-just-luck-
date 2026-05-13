"""
👻 GHOST ENGINE — Session 38 build (10.05.2026)
==================================================
The Ghost-Counting Canon codified.

DJ canon (S38):
  • GHOST DOOR — each draw, scan position pairs (Pa, Pb): expected = Pb - Pa.
    If expected ∈ [1, max_n] AND expected ∉ draw → expected is a GHOST.
  • GHOST WALK — +1 forward per draw, with ±1 mirror-neighbor / digit-swap /
    carrier-form (n−25 Euro, m−21 Swiss) probes.
  • CASH WINDOWS — validated on Q1 (HUGE 07.02.2026) + Q2 (12@Sw-d10):
      1. 4-DRAW LATE raw closure (mid-Q sweet spot)
      2. 9-10 DAY DEEP-SLEEP closure (Q-anchor → HUGE)
  • CHAINLESS = CASH-WINDOW — draws where no `Pa+Pb=Pc` AND no `Pb-Pa=Pc`
    exist are where deep ghosts pay raw.
  • QUARTER-SHAPE SIGNATURE — each Q sings its own internal chord-shape
    (Q1 Swiss `P1+P5=P6`, Q2 Swiss `P1+P2=P5/P4`).
  • SATURATION → FAMILY-RARE CASCADE — number ≥5× in 9d dethrones into a
    decade-cluster (Q1: 20 sat → 5-in-30s → HUGE 6-in-30s).
  • CARRIER-EXPANSION — Eu n → {n, n−25}; Sw m → {m, m−21}.

Modules:
  • ghost_arithmetic_ledger  — `?+Pa=Pb` door extractor (ghost birth)
  • ghost_walk_tracker       — +1 walk + neighbor / digit / carrier probes
  • ghost_close_detector     — closure detection across windows
  • internal_chain_detector  — chainless flag = cash-window
  • saturation_to_rare       — 5×-in-9d → decade-cluster predictor
  • quarter_shape_signature  — d1-d3 chord-shape detector
  • carrier_expansion        — unified Eu/Sw + cross-lottery pool
  • ghost_orchestrator       — single entry fusing 1-7
"""
from .ghost_arithmetic_ledger import build_arithmetic_ledger, extract_ghosts_for_draw
from .ghost_walk_tracker import walk_ghosts_forward
from .ghost_close_detector import detect_closures
from .internal_chain_detector import detect_chainless_windows, scan_internal_chains
from .saturation_to_rare import saturation_watch
from .quarter_shape_signature import detect_quarter_shape
from .carrier_expansion import expand_carriers, unified_pool
from .ghost_orchestrator import build_ghost_ledger
from .hidden_prince import (
    hidden_prince_pipeline, score_prince, build_fugue,
)
from .story_composer import compose_stories, build_palette, hungry_plate

__all__ = [
    "build_arithmetic_ledger",
    "extract_ghosts_for_draw",
    "walk_ghosts_forward",
    "detect_closures",
    "detect_chainless_windows",
    "scan_internal_chains",
    "saturation_watch",
    "detect_quarter_shape",
    "expand_carriers",
    "unified_pool",
    "build_ghost_ledger",
    "hidden_prince_pipeline",
    "score_prince",
    "build_fugue",
    "compose_stories",
    "build_palette",
    "hungry_plate",
]
