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

## What's Been Implemented (Jan 2026)
- [x] Swiss Lotto full implementation with 42-ball machine
- [x] EuroMillions mode with 50-ball machine + 2 star wheels
- [x] Mode toggle between Swiss Lotto and EuroMillions
- [x] Birthday and name-based numerology integration
- [x] Position locking feature
- [x] Multi-ticket generation with confidence ranking
- [x] Historical data seeding (1511 EuroMillions draws 2012-2026, 1380+ Swiss Lotto draws)
- [x] Pattern analysis algorithms (frequency, gap, family spread, sum range, odd/even)
- [x] Responsive animated UI with realistic ball physics
- [x] **NEW: Gap-6 Trigger Pattern** - When previous star gap=6, predicts extreme gaps (8-11)
- [x] **NEW: Gap Oscillation Pattern** - Small gaps→mid gaps, large gaps→small gaps
- [x] **NEW: Consecutive Cluster Pattern** - 63% of extreme gap draws have consecutive main numbers

## API Endpoints
### Swiss Lotto
- `GET /api/master-predictor` - Generate predictions
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
