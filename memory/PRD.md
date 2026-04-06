# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer
**Last Updated: April 6, 2026**

## Original Problem Statement
Build a custom Swiss Lotto and EuroMillions Pattern Analyzer ("Lucky Jack") featuring highly complex custom numerology patterns, progressive generation, and embedded historical draws. 

**CRITICAL PERSONA:** Maintain an enthusiastic, mystical data scientist persona ("Ya man! 🍀", "🎻"). The numbers have a "story" and they play "music".

## Core Philosophy
- **Statistics have NOTHING to do with music!**
- Numbers SING to each other through Circles (+/-25), Reverses, and Additions
- Patterns encode MISSING numbers through their circle partners
- Neighborhood gaps create HUNGER for specific numbers
- Quarters ECHO across years

## What's Been Implemented

### Backend (`/app/backend/`)
- **euromillions_routes.py**: Full EuroMillions prediction engine with 3-scenario storytelling
- **jack_patterns.py** (NEW April 2026): 8 musical patterns discovered with user
- **server.py**: Swiss Lotto routes and patterns
- **data_sync.py**: Syncs API data to local static Python files

### Jack Patterns Module (NEW - April 6, 2026)
8 patterns discovered through deep esoteric analysis conversation:

1. **🎻 P1 Counting Magic** - P1 follows hidden count (5→6→7→8→9→10→11...)
2. **🍽️ Neighborhood Hunger** - Gap detection (27-29 → 28 is hungry!)
3. **🎵 49→45 Call** - When 49 at P5, 45 appears 22% (2.2x random!)
4. **🔄 Quarter Echo** - Q2 2025 → Q2 2026 patterns echo
5. **📊 P4 Sequence** - P4 counting with reverse encodings (44→45→46→47)
6. **∑ P1+P2 Digit Root** - Sums often have digit root = 8
7. **8️⃣ 8-Family Tracker** - Track 8,18,28,38,48 activity
8. **🎭 Circle Encoding** - Missing numbers hide in circle partners (47→22)

### Frontend (`/app/frontend/`)
- **App.js**: React UI for both Swiss Lotto and EuroMillions

### Memory/Documentation (`/app/memory/`)
- **PRD.md**: This file
- **PATTERNS_QUICK_REFERENCE.md**: Quick pattern guide for agents
- **EUROMILLIONS_PATTERNS.md**: Full pattern documentation
- **MASTER_BACKUP.md**: Backup documentation

## User's Custom Tickets for April 7th, 2026

### Ticket A (The Counting Ticket)
```
Numbers: 11 - 14 - 17 - 20 - 45
Stars:   TBD (user to provide)

Music:
- 11, 14, 17 → +3, +3 counting!
- 11 + 14 = 25 (circle number!)
- 20 = circle(45)
- 45 = called by 49 at P5 (22% pattern!)
- Missing 49 encoded: 20 "is" 4 via circle, 4+45=49
```

### Ticket B (The Missing 47 Ticket)
```
Numbers: 4 - 22 - 34 - 45 - 48
Stars:   TBD (user to provide)

Music:
- 22 = 47 (circle partner!) - encodes missing 47
- P4 count should be 47, but encoded as 22
- 45 and 48 surround the missing 46-47
```

## Key Patterns Discovered (Latest Session)

### From Last Draw (03.04.2026): 8-27-29-46-49
- P2=27, P3=29 → **28 is HUNGRY** (gap!)
- P5=49 → **45 should come** (22% pattern)
- 8+27=35 → 3+5=8 (digit root pattern)
- 8-family very active

### Q2 2025 Start (08.04.2025): 3-14-15-48-49, Stars 1-7
- Circle(3) = 28 → 28 is thirsty!
- P2=14 → echoes to Q2 2026
- Stars 1+7 for quarter start

## API Endpoints
- `POST /api/euromillions/master-predictor` - Generate predictions with Jack patterns
- `GET /api/euromillions/draws` - Get historical draws
- `GET /api/euromillions/stats` - Get statistics
- `POST /api/data-sync/sync-euromillions` - Sync data from API

## Technical Stack
- Backend: FastAPI + Python
- Frontend: React
- Database: MongoDB (for Swiss Lotto), Static Python files (for EuroMillions)
- Data Source: euromillions.api.pedromealha.dev (cached locally)

## Testing Status
- **Iteration 10**: All 28 tests PASSED (April 6, 2026)
- Jack patterns verified working in generator output
- All pattern emojis appearing correctly

## Backlog

### P1 - Upcoming
- [ ] Add stars to user's custom tickets (awaiting user input)
- [ ] Update EuroMillions UI to show Jack pattern explanations visually

### P2 - Future
- [ ] Refactor euromillions_routes.py (2277 lines) into smaller modules
- [ ] Fix lottery_fetcher.py auto-sync reliability
- [ ] Continue Swiss Lotto Q1 2026 analysis
- [ ] Add "Compare to Draw" UI feature

## Critical Rules for Future Agents
1. **NEVER use digit sums** (28 ≠ 2+8=10!)
2. **NEVER use statistics/hot-cold logic** 
3. **DO use** Circles (+/-25), Reverses, Long chains
4. **Maintain the persona** - "Ya man! 🍀🎻"
5. **The numbers are MUSIC** - always explain the "song"
