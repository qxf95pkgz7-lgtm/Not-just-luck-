# Lucky Jack - Swiss Lotto + EuroMillions Pattern Analyzer

## Overview
Dual lottery pattern analyzer system featuring physics-based number generators with comprehensive numerology patterns.

## What's Implemented (Updated: April 3, 2026)

### Swiss Lotto "Lucky Jack" (Main App)
- **Ball Machine**: 42 balls with gravity vs air jets physics, tube catching mechanism
- **Ball Fall Animation**: After draw, balls fall back into dome dramatically
- **Lucky Wheel**: Spinning wheel (1-6) with perspective angle
- **51 Pattern Algorithms**: Master Predictor with all user-validated numerology patterns
- **Lock Positions**: Lock 1-4 numbers at specific positions (P1-P6)
- **Multiple Tickets**: Generate 1-20 tickets ranked by confidence
- **Personalization**: Birthday and name-based predictions

### EuroMillions "Lucky Stars" (NEW - API Integration)
- **Format**: 5 main numbers (1-50) + 2 star numbers (1-12)
- **Historical Data**: 262 draws seeded from 2014-2016 (extracted from lotto24.ch images)
- **API Endpoints**:
  - `GET /api/euromillions/health` - Health check
  - `GET /api/euromillions/draws` - Historical draws
  - `GET /api/euromillions/stats` - Statistical analysis
  - `POST /api/euromillions/master-predictor` - Generate predictions
  - `GET /api/euromillions/analyze-ticket` - Analyze user tickets
- **Patterns Adapted**: Position Frequency, Gap Analysis, Family Spread, Consecutive Pairs, Odd/Even, High/Low, Star patterns
- **Price**: €2.50 per ticket

## Tech Stack
- React.js + Tailwind CSS (Frontend)
- FastAPI + Motor (Backend)
- MongoDB (Swiss Lotto: 1,380 draws, EuroMillions: 262 draws)

## Architecture
```
/app/
├── backend/
│   ├── server.py           # Main Swiss Lotto backend with 51 patterns
│   ├── euromillions_routes.py  # EuroMillions API routes with 262 draws
│   └── requirements.txt
├── frontend/
│   └── src/App.js          # Swiss Lotto UI
├── euromillions/           # Scaffolded standalone EuroMillions app (future)
│   ├── backend/
│   └── frontend/
└── memory/
    ├── PRD.md
    └── HANDOFF.md
```

## API Routes Summary

### Swiss Lotto (/api/*)
- `GET /api/` - Root info
- `GET /api/dashboard` - Dashboard stats
- `GET /api/master-predictor` - Generate predictions
- `GET /api/analyze-patterns` - Pattern analysis

### EuroMillions (/api/euromillions/*)
- `GET /api/euromillions/health` - Health check
- `GET /api/euromillions/draws` - Historical draws
- `GET /api/euromillions/stats` - Statistical analysis  
- `POST /api/euromillions/master-predictor` - Generate predictions
- `GET /api/euromillions/analyze-ticket` - Analyze tickets

## Next Tasks (P1)
- Build EuroMillions frontend UI with ball machine (5 main balls + 2 star balls)
- Add lottery selector to switch between Swiss Lotto and EuroMillions
- Add sound effects for catches/rolls

## Future Tasks (P2)
- History/Saved Tickets feature
- Compare generated vs actual results
- Mobile responsive improvements

## Known Limitations
- Preview URL API routing returns 404 (platform ingress issue)
- Test via localhost:8001 for backend, localhost:3000 for frontend
