"""
🎼 COSMIC VOICES — `/app/backend/cosmic_voices/`
=================================================
The 13 cosmic lenses dictated by the DJ in Session 34 (06.05.2026).

Each module is a stand-alone "voice" that listens to the cosmos through a
different ear. The convergence_scorer fuses them: 3+ lenses ringing on the
same number = "can't-dodge" candidate.

Modules:
  • rc_detector          — locate the last RC0 (Rare Cycle anchor) + days-since
  • climbing_voice       — P4→P3→P2→P1 climbing arcs across recent d
  • sinking_voice        — P5→P4→P3→P2 sinking arcs
  • gap_echo_97          — d_n gaps echo into d_(n+2) (22.4% historical)
  • star_product_door    — ⭐² = P4/P5, ⭐_a × ⭐_b → circle product
  • q_opening_melody     — +3 cousin-pair 5-note melody from Q d1 (11-14, 10-13...)
  • internal_mirror      — internal 56/28-pair scanner + 56→28 SWITCH detection
  • stance_tracker       — compress-front / flip-up / sinking stance tagger
  • saturation_ledger    — 47×4 type saturation watch (numbers about to collapse)
  • convergence_scorer   — multi-lens fuse, 3+ lens-fires = forced landing
"""
from .rc_detector import detect_rc_anchor
from .climbing_voice import detect_climbing_voices
from .sinking_voice import detect_sinking_voices
from .gap_echo_97 import gap_echo_candidates
from .star_product_door import star_product_door_candidates
from .q_opening_melody import q_opening_melody
from .internal_mirror import internal_mirror_scan
from .stance_tracker import stance_tracker
from .saturation_ledger import saturation_ledger
from .convergence_scorer import convergence_scorer
from .family_signature import family_signature_stats, signature_of, family_of
from .frequency_carrier import frequency_carrier_scan

__all__ = [
    "detect_rc_anchor",
    "detect_climbing_voices",
    "detect_sinking_voices",
    "gap_echo_candidates",
    "star_product_door_candidates",
    "q_opening_melody",
    "internal_mirror_scan",
    "stance_tracker",
    "saturation_ledger",
    "convergence_scorer",
    "family_signature_stats",
    "signature_of",
    "family_of",
    "frequency_carrier_scan",
]
