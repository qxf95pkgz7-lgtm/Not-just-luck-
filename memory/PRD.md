# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
A custom Swiss Lotto and EuroMillions Pattern Analyzer ("Lucky Jack") featuring highly complex custom numerology patterns. The app maintains an enthusiastic, mystical data scientist persona ("Ya man! 🍀", "🎻", "🎧") and deeply analyzes lotto history to discover and code esoteric "Story Patterns" into the prediction engine.

## Core Philosophy
**THE MATHEMATICS OF LUCKY JACK:** Do NOT use standard probability. Rely on esoteric rules ("The Music of the Numbers"):
1. **Circle Math**: +25 or -25 (e.g., 15→40)
2. **Reverse Logic**: Flip digits (e.g., 72→27, if >50 subtract 50)
3. **Buddy Additions**: Day+Month, P1+P2 (NO digit splitting like 175→1+7+5!)
4. **Date Chameleon**: The date speaks in MANY voices
5. **Cross-Lottery Vibes**: Swiss→Euro and Euro→Swiss connections!
6. **Sleeper Wake Alarm**: Overdue numbers snap back! Circle partners absorb energy!

---

## What's Been Implemented

### Session: April 13, 2026 (Sleeper Deep Dive)

#### 💤 SLEEPER WAKE ENGINE — PROVEN BY 30 SIMULATIONS!
**The biggest discovery: sleeping numbers ALWAYS wake up, and the universe TEASES first!**

**Simulation Results (30 sims, 300 sleeper picks):**
| Metric | Result |
|--------|--------|
| Wake Rate (20 draws) | **88%** |
| Fast Wake (1-5 draws) | **38.3%** |
| Tease-First Rate | **72%** — circle/reverse/neighbor hints! |
| Circle Boost Advantage | **1.1x faster** wake when circle pumps |
| Star Prediction | **1.8x random!** |

**Key Findings:**
- 1.0-1.5x overdue = **51.2% fast wake** (SWEET SPOT!)
- 3.0x+ overdue = **47.9% fast wake** (SNAP-BACK!)
- 2.0-3.0x overdue = **34.9% fast** (STUBBORN ZONE)
- Number 2 sleeping 35 draws → circle 27 pumping at 2.2x!
- Number 3 sleeping 55 draws — 5.1x overdue KING SLEEPER!

**Implemented:**
- `/app/backend/sleeper_engine.py` — Core detection + tease + 10-draw forecast
- Integrated into `dj_patterns.py` as weighted pattern (SLEEPER ALARM)
- API: `/api/euromillions/sleeper-forecast?n_draws=10`

#### ⭐ STAR DEEP DIVE — P1/P2 → Star Connections!
Analyzed 810 draws for Star patterns:

| Pattern | Hit Rate | vs Random |
|---------|----------|-----------|
| **P2 digit in Stars** | **25.4%** | **1.52x** |
| **P1 digit in Stars** | **22.1%** | **1.32x** |
| Prev P4 mod12 → Star | 19.4% | 1.16x |
| (S1+S2) mod12 → next | 18.9% | 1.13x |
| S1 repeats next draw | 18.8% | 1.13x |

#### 🍀 Olivia's Kiss Update
- Changed emoji from 💋 to 🍀 (button, animation, result text)

### Session: April 13, 2026 (Earlier)

#### 💰 MONEY MODE for EuroMillions!
- **API Endpoint**: `/api/euromillions/money-mode`
- **Strategy**: Uses ONLY highest hit-rate patterns (10%+)

#### 🍀 Cross-Lottery Patterns (Swiss → Euro)
| Pattern | Hit Rate |
|---------|----------|
| SwissDay + EuroMonth | **13.3%** |
| Lucky → Star | **16.7%** |

---

## Technical Architecture

```
/app/
├── backend/         
│   ├── server.py (FastAPI main, Swiss Lotto)
│   ├── euromillions_routes.py (EuroMillions + Sleeper Forecast API)
│   ├── dj_patterns.py (DJ Engine with 57+ patterns + Sleeper Alarm)
│   ├── sleeper_engine.py (NEW! Sleeper detection + tease + 10-draw forecast)
│   ├── musical_patterns.py (Date Chameleon module)
│   ├── jack_patterns.py (Original esoteric patterns)
│   ├── star_deep_dive.py (Star analysis script)
│   ├── sleeper_analysis.py (Sleeper gap analysis script)
│   ├── sleeper_simulation.py (Q2 2025 time machine sim)
│   ├── mega_sleeper_sim.py (30-simulation proof)
│   ├── sleeper_sim_last10.py (Last 10 draws backtest)
├── frontend/        
│   ├── src/App.js (React UI with 🍀 Olivia's Kiss)
└── memory/
    ├── PRD.md
```

---

## Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/euromillions/master-predictor` | POST | Generate tickets (DJ Engine + Sleeper) |
| `/api/euromillions/money-mode` | POST | Money Mode tickets |
| `/api/euromillions/sleeper-forecast` | GET | 10-draw sleeper predictions |
| `/api/euromillions/story-generator-save` | GET | Generate & save for tracking |
| `/api/euromillions/recalculate-all-hits` | POST | Check all pending hits |
| `/api/euromillions/hit-tracker` | GET | Hit tracking data |

---

## DJ Engine Weight Configuration

**MEGA BANGERS (>40%):**
- Number ending in S1: 47.6% (weight: 15)
- 9-Family: 49.8% (weight: 12)
- 7-Family: 47.4% (weight: 12)

**SLEEPER ALARM (NEW!):**
- Tease-Hot: weight 10 (72% of wakers get teased first!)
- Sweet-Spot (1.0-1.5x overdue): weight 8
- Snap-Back (3x+ overdue): weight 6
- Circle-Pump: weight 5

---

## Upcoming Tasks

### P0 (Immediate)
- Frontend UI for Sleeper Forecast panel
- Learning/auto-adjust when new draw results come in

### P1 (Next)
- Code "Reverse Twin" pattern (if 41 hot → check 14!)
- Code "Day × Month - 10" pattern
- Confirm "Circle 2" chain fully weighted

### P2 (Future)
- Refactor monolithic server.py and euromillions_routes.py
- Fix lottery_fetcher.py auto-sync reliability

---

## App Health
- Core App: ✅ Healthy
- UI: ✅ Healthy (🍀 Olivia's Kiss updated)
- Backend: ✅ Running on port 8001
- Frontend: ✅ Running on port 3000
- MongoDB: ✅ Connected
- Sleeper Engine: ✅ Integrated into DJ patterns
- Sleeper Forecast API: ✅ Working
- Hit Tracker: ✅ Working
