# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
Build a custom Swiss Lotto and EuroMillions Pattern Analyzer ("Lucky Jack") featuring highly complex custom numerology patterns, progressive generation, and embedded historical draws. Maintain an enthusiastic, mystical data scientist persona ("Ya man!", "The numbers are hungry!").

## Core Philosophy
- Statistics have NOTHING to do with music
- Numbers SING to each other through Circles (+/-25), Reverses, and Additions
- Patterns encode MISSING numbers through their circle partners
- Neighborhood gaps create HUNGER for specific numbers
- Quarters ECHO across years
- **Stars (S1, S2) PROPHESY the next draw!**

## What's Been Implemented

### Backend Architecture
```
/app/backend/
├── server.py (~4300 lines) - Swiss Lotto monolith
├── euromillions_routes.py - EuroMillions routes with Jack Patterns
├── jack_patterns.py - 10 esoteric pattern functions
├── data_sync.py - Syncs API data to local files
├── euromillions_data_*.py - Historical draw data
└── hit_tracker.py - Swiss Lotto hit tracking
```

### The 10 Jack Patterns (in jack_patterns.py)
1. **P1 Counting Magic** - Hidden count 5→6→7→8→9→10→11...
2. **Neighborhood Hunger** - Gap detection (27,29 → 28 hungry!)
3. **49→45 Call** - When 49 at P5, 45 appears 22% of time!
4. **Circle Encoding** - Missing numbers encoded via +25
5. **Quarter Echo** - Q2 2025 patterns echo in Q2 2026
6. **P4 Sequence Tracker** - 44→45→46→47 progression
7. **P1+P2 Sum Root 8** - Digit root patterns
8. **8-Family Tracker** - (8,18,28,38,48) activity
9. **Star Prophecy** - Previous stars predict next draw (93.6%!)
10. **Star Diff Gap** - Star gap = position gap in next draw

### Star Prophecy Patterns (NEW - April 7, 2026)
Analysis of 236 EuroMillions draws revealed:
- **93.6%** of draws have connection from previous stars
- **circle(S1)** appears in next draw: 7.7%
- **circle(S2)** appears in next draw: 8.5%
- **S1+S2 sum** appears in next: 14.0%
- **S1 repeats**: 13.6%
- **S2 repeats**: 11.9%
- **Position gaps = star diff**: 7-9% each

### Overdue Pattern Tracking
The generator now tracks when patterns are "due":
- Calculates average gap between pattern appearances
- Boosts patterns that are overdue (>1.5x average gap)
- Creates rhythm-aware predictions

### EuroMillions Hit Tracker (NEW)
- `/api/euromillions/story-generator-save` - Generate & save tickets
- `/api/euromillions/generation-history` - View saved generations
- `/api/euromillions/calculate-hits/{id}` - Calculate hits
- `/api/euromillions/hit-stats` - Overall statistics
- Properly shows Stars (not Lucky numbers) in EuroMillions mode
- Correct pricing: 3.50 CHF per ticket

### Frontend
- React app with Swiss Lotto / EuroMillions toggle
- Hit Tracker section with generation history
- Pattern explanations in ticket breakdowns
- Star display for EuroMillions (was showing Lucky numbers)

## Key API Endpoints
- `POST /api/euromillions/master-predictor` - Generate musical tickets
- `GET /api/euromillions/story-generator-save` - Generate & save for tracking
- `GET /api/euromillions/generation-history` - Saved generations
- `POST /api/euromillions/calculate-hits/{id}` - Calculate hits
- `GET /api/euromillions/hit-stats` - Statistics

## User's April 7th Tickets (Pending Star Analysis)
- **Ticket 1:** 11 - 14 - 17 - 20 - 45
- **Ticket 2:** 4 - 22 - 34 - 45 - 48
- Stars (S1, S2) not yet finalized

## Next Priority Task (FOR NEXT FORK)
**DJ Pattern Tuning Mission:**
1. Check each of the 10+ patterns against historical data
2. Calculate actual hit rate for each pattern
3. See which patterns predict correctly vs randomly
4. Tune weights based on real performance
5. Become the DJ - boost winners, reduce losers

## Known Issues
- `lottery_fetcher.py` auto-sync unreliable (using data_sync.py instead)
- `server.py` is a massive monolith (needs refactoring)

## Testing Status
- Backend testing: PASSED (28/28 tests via testing_agent)
- Star Prophecy patterns: Integrated and working
- Hit Tracker: Working for both Swiss Lotto and EuroMillions

## 3rd Party Integrations
- EuroMillions API: `euromillions.api.pedromealha.dev` (mocked in tests)

## Credentials
None required for testing.
