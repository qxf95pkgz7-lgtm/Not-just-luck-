# Lucky Jack - Lottery Pattern Analyzer PRD

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

### Pattern Engine (58 Patterns Total!)
- [x] Patterns 1-52: Original numerology patterns (frequency, gap, family spread, sum range, odd/even, etc.)
- [x] **Pattern 53: Shadow Number Strategy** - Avoid numbers but boost their echoes (circle, multiples, essence)
- [x] **Pattern 54: P6 Momentum Tracking** - Detect P6 repeats and boost momentum/circle swap
- [x] **Pattern 55: Air Pattern (P1+P2 Sum)** - When P1+P2 sums to recurring values, boost that family
- [x] **Pattern 56: Position Anchors** - Detect quarterly position repeats (P3, P4, P5, P6)
- [x] **Pattern 57: Circle Transformation** - For hot numbers, also boost circle partners (RIDE vs SWAP)
- [x] **Pattern 58: Date Essence Doubling** - Special boost when day==month (like 4/4)

### Analysis Features (April 4, 2026 Session)
- [x] Analyzed 40 appearing 6x at P6 in last 20 draws (MOMENTUM!)
- [x] Missing 9 "Shadow" strategy - use echoes 18, 27, 30, 36 instead
- [x] Air 20 pattern from P1+P2=20 analysis
- [x] Date 4/4 special doubling

## API Endpoints
### Swiss Lotto
- `GET /api/master-predictor` - Generate predictions with all 58 patterns
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
1. Monitor user feedback for UX improvements
2. Consider adding sound effects for ball animations
3. Implement ticket history/comparison feature

## Technical Notes
- Pattern reasons now show 10 items (increased from 6) for visibility
- New patterns use `insert(0, ...)` to show at top of reasons list
- Date doubling: +50% for exact match, +40% for circle, +20% for family
