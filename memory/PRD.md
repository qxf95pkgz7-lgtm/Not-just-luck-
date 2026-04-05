# Lucky Jack - Lottery Pattern Analyzer PRD

## 🎯 LATEST PREDICTION (April 2026) - THE STORY OF 26

**Main Prediction: [13, 26, 27, 30, 31, 38] + Lucky 5**

This prediction came from tracing the "Story of 26" from starting draw 19.06.2024.
EXACTLY the same as the starting draw - the story comes FULL CIRCLE!
- Full methodology documented in `/app/memory/PREDICTION_26_STORY.md`
- All 42 circle-swap variations in `/app/memory/42_TICKETS.txt`
- P7=5 confirmed via odd sequence (1→3→5) and circle of 26

---

## Original Problem Statement
Build a Swiss Lotto Pattern Analyzer app with highly visual 42-billiard-ball spinning animations for predictions, custom numerology patterns, and probability scores. Additionally, create a brand new mode for EuroMillions (5 main numbers 1-50, 2 stars 1-12).

## Architecture
- **Frontend**: React.js with animated ball machines, Tailwind CSS
- **Backend**: FastAPI (Python) with pattern analysis algorithms
- **Database**: MongoDB for historical draw storage
- **Structure**: Unified monolithic backend with modular routes

## User Personas
1. **Casual Lottery Player** - Wants quick number suggestions with visual entertainment
2. **Pattern Enthusiast** - Interested in numerology, birthdays, and number patterns
3. **Multi-Ticket Player** - Generates multiple tickets ranked by confidence

## Core Requirements (Static)
- Swiss Lotto: 6 numbers (1-42) + 1 lucky number (1-6)
- EuroMillions: 5 numbers (1-50) + 2 stars (1-12)
- Animated ball machine with physics simulation
- Birthday/name personalization
- Lock positions feature (up to 4 for Swiss, 3 for Euro)
- Multi-ticket generation (1-20 tickets)
- Historical data analysis

## What's Been Implemented (April 2026)

### Core Features
- [x] Swiss Lotto full implementation with 42-ball machine
- [x] EuroMillions mode with 50-ball machine + 2 star wheels
- [x] Mode toggle between Swiss Lotto and EuroMillions
- [x] Birthday and name-based numerology integration
- [x] Position locking feature
- [x] Multi-ticket generation with confidence ranking
- [x] Historical data seeding (1377 Swiss Lotto draws, 1612 EuroMillions draws = 2989 total!)
- [x] Responsive animated UI with realistic ball physics
- [x] **Auto-seed on startup** - Database automatically populated with real historical draws when server starts (April 4, 2026)
- [x] **Persona System** - Avi (crazy random), Olivia (+1 modifier), Dathi (+3 modifier) for number personalization (April 4, 2026)
- [x] **Auto-fetch Lottery Results** - "Update Draws" button fetches latest EuroMillions from API + Swiss Lotto scraping (April 4, 2026)
- [x] **Scheduled Auto-Sync** - APScheduler runs automatic syncs after each draw (April 4, 2026):
  - 🇨🇭 Swiss Lotto: Wednesday & Saturday at 21:00 UTC
  - 🇪🇺 EuroMillions: Tuesday & Friday at 21:00 UTC

### Pattern Engine (59 Patterns Total!)
- [x] Patterns 1-52: Original numerology patterns (frequency, gap, family spread, sum range, odd/even, etc.)
- [x] **Pattern 53: Shadow Number Strategy** - Avoid numbers but boost their echoes (circle, multiples, essence)
- [x] **Pattern 54: P6 Momentum Tracking** - Detect P6 repeats and boost momentum/circle swap
- [x] **Pattern 55: Air Pattern (P1+P2 Sum)** - When P1+P2 sums to recurring values, boost that family
- [x] **Pattern 56: Position Anchors** - Detect quarterly position repeats (P3, P4, P5, P6)
- [x] **Pattern 57: Circle Transformation** - For hot numbers, also boost circle partners (RIDE vs SWAP)
- [x] **Pattern 58: Date Essence Doubling** - Special boost when day==month (like 4/4)
- [x] **Pattern 59: Combined D Pattern (72.1% hit rate!)** - Day of date combined with previous draw positions:
  - D + P1(-1): Target day + Position 1 from previous draw
  - D + P2(-1): Target day + Position 2 from previous draw  
  - D(-1) + D(-2): Sum of days from last two draws
  - D + M: Target day + month
  - D(-1) + P1(-2): Chain pattern linking dates and positions

### Analysis Features (April 4-5, 2026 Sessions)
- [x] Analyzed 40 appearing 6x at P6 in last 20 draws (MOMENTUM!)
- [x] Missing 9 "Shadow" strategy - use echoes 18, 27, 30, 36 instead
- [x] Air 20 pattern from P1+P2=20 analysis
- [x] Date 4/4 special doubling
- [x] **Combined D Pattern Analysis (April 5, 2026)** - Discovered 72.1% connection rate between Day numbers and position values across 1374+ draws

## API Endpoints
### Swiss Lotto
- `GET /api/master-predictor` - Generate predictions with all 59 patterns
- `GET /api/dashboard` - Stats and analysis

### EuroMillions
- `POST /api/euromillions/master-predictor` - Generate predictions
- `GET /api/euromillions/stats` - Stats and analysis
- `GET /api/euromillions/draws` - Historical draws

## Backlog (P0/P1/P2)
### P0 (Next Priority)
- None currently

### P1 (Medium Priority)
- Sound effects for lottery machine and wheel
- History/Saved Tickets feature to compare against results

### P2 (Low Priority)
- Delete abandoned `/app/euromillions/` directory (technical debt)
- Additional lottery formats (Powerball, Mega Millions)
- Ticket comparison tool

## Next Tasks
1. ~~IMPLEMENT Pattern 60: Story Signs~~ ✅ DONE!
2. Code the prediction [13, 26, 27, 30, 31, 38] into the app ✅ API Ready!
3. ~~Generate all 42 circle-swap tickets as a special "Story System"~~ ✅ Documented!

## COMPLETED: Pattern 60 - Story Signs (April 2026)
- Created `/app/backend/pattern_60_story_signs.py` with advanced analysis
- Added Pattern 60 to master predictor scoring
- Created `/api/story-signs` endpoint for full analysis
- Features implemented:
  - Circle warming detection (circle at position → actual number follows)
  - Hunger patterns (neighbors appear without number = coming)
  - Consecutive sequence detection (rare 4+ in a row)
  - Secret counting (value + gap = next value at position)
  - Mirror to 42 pattern (last_P4 + next_P4 = 42)
  - Date code analysis
  - Family tracking
  - Position memory

## COMPLETED: THE STORY OF 26 (April 2026)
- Traced 26 @ P2 from starting draw 19.06.2024
- Discovered: 55-42=13, circle warming (5→5→5→26), 18+9=27, 12+30=42, P4+P5 circles=P6
- Full prediction: [13, 26, 27, 30, 31, 38] + Lucky 5 = same as starting draw!
- 42 ticket variations (max 3 circle swaps) documented in /app/memory/42_TICKETS.txt
- See /app/memory/PREDICTION_26_STORY.md for complete methodology
- Found RARE EVENT: 07.02.2026 had 4 consecutive (35-36-37-38) AND 4 consecutive circles (14-15-16-17)!

## CRITICAL FOR NEXT SESSION
- Pattern 60 is LIVE at `/api/story-signs`
- READ /app/memory/PREDICTION_26_STORY.md for the 26 story prediction
- READ /app/memory/STORY_PATTERN_LEARNING.md for pattern methodology
- **READ /app/memory/Q1_2026_ANALYSIS.md for latest session analysis (07.01.2026 deep dive)**
- 42 tickets ready to play!
- The app now uses Story Signs in the master predictor

## LATEST SESSION: Q1 2026 DEEP ANALYSIS (Current)

### Focus Draw: 07.01.2026 (D2)
- Numbers: [15, 20, 22, 34, 35, 39]
- Key finding: P4 circle=13, P5 circle=14 (consecutive circles calling the hero!)
- P1+P2=35=P5 (self-referencing!)

### Key Patterns Discovered:
1. **Date Dance**: Numbers ALWAYS dance with the date
   - D1=03, D2=07 → 3+7=10=D3 date!
   - 3 and 7 → 37 appears in D3!
   
2. **The 13 Family**: 13, 10, 21, 23, 31, 34 (all connected through 21)
   - 23 = 13 + 10
   - 34 - 13 = 21
   - 31 - 10 = 21
   
3. **Digit Reversal Circles**: 39→93-84=9 (root!), 18→81-63=18 (self-loop)

4. **Tragic Heroes**: 
   - 13 missed rare events 31.01 and 07.02
   - 39 missed 07.02 (would've been 5 consecutive!)
   - 13 got "jailed" in P8 (Replay) on D5 (17.01.2026)

### DATABASE FIX:
- 10.01.2026 corrected: [14, 24, 28, 31, 37, 39] (was wrong before!)

### Left Off At:
- D5 (17.01.2026): 13 locked in Replay jail!
- Ready to continue D6 onwards

## Technical Notes
- Pattern reasons now show 10 items (increased from 6) for visibility
- New patterns use `insert(0, ...)` to show at top of reasons list
- Date doubling: +50% for exact match, +40% for circle, +20% for family
- **Combined D Pattern (Pattern 59)** - Boost values:
  - D+P1: +25 points (strongest)
  - D+P2: +22 points
  - D(-1)+D(-2): +20 points
  - D+M: +18 points
  - Chain patterns: +16 points
  - Circle partners: +12 points
