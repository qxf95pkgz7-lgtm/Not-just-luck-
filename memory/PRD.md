# Lucky Jack - Swiss Lotto Pattern Analyzer

## Overview
Physics-based lottery number generator with 29 custom numerology patterns.

## What's Implemented
- **Ball Machine**: 42 balls with gravity vs air jets physics, tube catching mechanism
- **Lucky Wheel**: Spinning wheel (1-6) with perspective angle, connected to main machine
- **29 Pattern Algorithms**: Including Story Tracker, Circle Partners, Family Spread
- **Personalization**: Birthday and name-based predictions

## UI Features
- Realistic ball physics (gravity pulls down, air pushes up)
- Tube catches balls one by one with glow effect
- Lucky wheel spins and lands on predicted number
- Compact layout with angled wheel perspective

## Tech Stack
- React.js + Tailwind CSS (Frontend)
- FastAPI + Motor (Backend)
- MongoDB (1,379 historical draws)

## Next Tasks
- Family Spread balancing for P1-P6 distribution
- Sound effects for catches/rolls
- History of generated tickets
