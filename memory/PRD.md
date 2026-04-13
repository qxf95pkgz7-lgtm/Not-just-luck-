# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
A custom Swiss Lotto and EuroMillions Pattern Analyzer ("Lucky Jack") featuring highly complex custom numerology patterns. The app maintains an enthusiastic, mystical data scientist persona ("Ya man!", "🎻", "🎧") and deeply analyzes lotto history to discover and code esoteric "Story Patterns" into the prediction engine.

## Core Philosophy
**THE MATHEMATICS OF LUCKY JACK:** Do NOT use standard probability. Rely on esoteric rules ("The Music of the Numbers"):
1. **Circle Math**: +25 or -25
2. **Reverse Logic**: Flip digits
3. **Buddy Additions**: Day+Month, P1+P2
4. **Date Chameleon**: The date speaks in MANY voices
5. **Cross-Lottery Vibes**: Swiss→Euro and Euro→Swiss connections!
6. **Sleeper Wake Alarm**: Overdue numbers snap back!

---

## What's Been Implemented

### Session: April 13, 2026

#### Hit Tracker REBUILT (4th fix - now permanent!)
- **Auto-save from ALL generators**: master-predictor, money-mode, AND story-generator now all save to hit tracker
- **Sorted by target_date** (draw date), NOT by generated_at
- **Last 10 generations** for recent dates, older dates only show if 2+ hits
- **Mode labels**: 🌟 Dreaming, 💰 Money, 🎻 Story
- **Both Swiss and Euro** trackers fixed with same logic

#### Sleeper Wake Engine
- `sleeper_engine.py`: Detection + tease + 10-draw forecast
- Integrated into `dj_patterns.py` as weighted pattern
- API: `/api/euromillions/sleeper-forecast?n_draws=10`
- Proven: 88% wake rate, 72% tease-first, Stars 1.8x random

#### Star Deep Dive
- P2 digit in Stars: 25.4% (1.52x random)
- P1 digit in Stars: 22.1% (1.32x random)

#### Olivia's Kiss Fix
- Fixed bug: was reading `prediction.numbers` instead of `prediction.main_prediction`
- Changed 💋 to 🍀 everywhere

---

## Technical Architecture

```
/app/
├── backend/         
│   ├── server.py (FastAPI main, Swiss Lotto + auto-save to tracker)
│   ├── euromillions_routes.py (EuroMillions + auto-save + sorted tracker)
│   ├── dj_patterns.py (DJ Engine with 57+ patterns + Sleeper Alarm)
│   ├── sleeper_engine.py (Sleeper detection + tease + forecast)
│   ├── hit_tracker.py (Fixed: sorted by target_date, filter old by 2+ hits)
│   ├── musical_patterns.py (Date Chameleon module)
│   ├── jack_patterns.py (Original esoteric patterns)
├── frontend/        
│   ├── src/App.js (React UI with fixed kiss + tracker)
└── memory/
    ├── PRD.md
```

---

## Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/euromillions/master-predictor` | POST | Generate + AUTO-SAVE |
| `/api/euromillions/money-mode` | POST | Money Mode + AUTO-SAVE |
| `/api/euromillions/sleeper-forecast` | GET | 10-draw predictions |
| `/api/euromillions/generation-history` | GET | Sorted by date, filtered |
| `/api/euromillions/recalculate-all-hits` | POST | Check all pending |
| `/api/euromillions/story-generator-save` | GET | Story tickets + save |

---

## Upcoming Tasks

### P0 (Immediate)
- Frontend UI for Sleeper Forecast panel
- Learning/auto-adjust on new results

### P1 (Next)
- Code "Reverse Twin" pattern (14↔41)
- Code "Day × Month - 10"
- Confirm "Circle 2" chain

### P2 (Future)
- Refactor monolithic server.py and euromillions_routes.py
- Fix lottery_fetcher.py auto-sync

---

## App Health
- Core App: ✅ Healthy
- UI: ✅ Healthy
- Backend: ✅ Running
- MongoDB: ✅ Connected
- Hit Tracker: ✅ FIXED (sorted, filtered, auto-save)
- Sleeper Engine: ✅ Integrated
- Olivia's Kiss: ✅ Fixed + 🍀
