# Lucky Jack - Swiss Lotto Pattern Analyzer

## Overview
Physics-based lottery number generator with **42 custom numerology patterns** - the most comprehensive pattern algorithm system.

## What's Implemented (Updated: April 2, 2026)
- **Ball Machine**: 42 balls with gravity vs air jets physics, tube catching mechanism
- **Ball Fall Animation**: After draw, balls fall back into dome dramatically
- **Lucky Wheel**: Spinning wheel (1-6) with perspective angle
- **42 Pattern Algorithms**: Master Predictor with all user-validated numerology patterns
- **Lock Positions**: Lock 1-4 numbers at specific positions (P1-P6)
- **Multiple Tickets**: Generate 1-20 tickets ranked by confidence
- **Personalization**: Birthday and name-based predictions

### Pattern System (42 Algorithms)
1-29: Core patterns (Story Tracker, Circle Partners, Family Spread, etc.)
30: P1/P2 Position Analysis (historical frequency at positions)
31: P1/P2 Transform (|P1-P2| → next P1/P2 prediction)
32: Family Hunger (chain building when family members appear)
33: Mirror/Reverse (15% hit rate)
34: Consecutive Pairs (54.3% draw rate)
35: Lucky Number Connection (Lucky × 7)
36-37: P3/P4 Position Analysis & Transforms
38-39: Date Story patterns (prev draw date, today's date)
40: 9@P1 Predictor (Family 9 trigger signals)
41: 9↔19 Connection (18.8%/15.9% oscillation)
42: **Gap Digits Pattern** (Last Time Position Count) - 25% hit rate!

## UI Features
- Realistic ball physics (gravity pulls down, air pushes up)
- Tube catches balls one by one with glow effect
- **Balls fall back into dome** after draw completes (3s delay, staggered)
- Lucky wheel spins and lands on predicted number
- Lock Positions panel with P1-P6 inputs
- Multiple Tickets panel with generate button inside

## Tech Stack
- React.js + Tailwind CSS (Frontend)
- FastAPI + Motor (Backend)
- MongoDB (1,380 historical draws)

## Next Tasks (P1)
- P5/P6 Position Analysis & Transforms
- Family Spread balancing for organic P1-P6 distribution
- Circle Partner (+21) balancing in ticket generation

## Future Tasks (P2)
- Sound effects for catches/rolls
- History/Saved Tickets feature
- Compare generated vs actual results

## Known Limitations
- Preview URL API routing returns 404 (platform ingress issue)
- Test via localhost:8001 for backend, localhost:3000 for frontend
