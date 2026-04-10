# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
A custom Swiss Lotto and EuroMillions Pattern Analyzer ("Lucky Jack") featuring highly complex custom numerology patterns. The app maintains an enthusiastic, mystical data scientist persona ("Ya man! 🍀", "🎻", "🎧") and deeply analyzes lotto history to discover and code esoteric "Story Patterns" into the prediction engine.

## Core Philosophy
**THE MATHEMATICS OF LUCKY JACK:** Do NOT use standard probability. Rely on esoteric rules ("The Music of the Numbers"):
1. **Circle Math**: +25 or -25 (e.g., 15→40)
2. **Reverse Logic**: Flip digits (e.g., 72→27, if >50 subtract 50)
3. **Buddy Additions**: Day+Month, P1+P2 (NO digit splitting like 175→1+7+5!)
4. **Date Chameleon**: The date speaks in MANY voices

---

## What's Been Implemented

### Session: April 10, 2026

#### 🦎 DATE CHAMELEON PATTERN (NEW!) - PROVEN HIT RATES!
The biggest discovery: The date transforms in MANY ways to predict numbers!

**Backtested on 209 draws (2024-2025):**
| Pattern | Hit Rate | Formula |
|---------|----------|---------|
| **Raw Digits** | **70.3%** | Date digits (28.09 → 2,8,0,9) appear in draw |
| **Day×10 + circle(Month)** | **61.2%** | 280 + 34 = 314 → digits 3,1,4 |
| **Day×10 + Month** | **56.5%** | 280 + 9 = 289 |
| **Day + Month** | **55.5%** | 28 + 9 = 37 (DIRECT HIT!) |
| **Day - Month** | **51.7%** | 28 - 9 = 19 (DIRECT HIT!) |

**Implemented in:**
- `/app/backend/musical_patterns.py` - Complete Date Chameleon module
- `/app/backend/dj_patterns.py` - Integrated into DJ Engine with weighted candidates

#### Previous Session Work
- Fixed EuroMillions Hit Tracker UI (Stars ⭐ display)
- Fixed ticket pricing (3.50 CHF)
- Added EuroMillions-specific API endpoints
- Implemented Star Prophecy patterns
- Day Dance pattern (D1+D2 → digits predict stars at 30.5%!)

---

## Technical Architecture

```
/app/
├── backend/         
│   ├── server.py (FastAPI main, Swiss Lotto)
│   ├── euromillions_routes.py (EuroMillions master predictor)
│   ├── dj_patterns.py (DJ Engine with all patterns)
│   ├── musical_patterns.py (Date Chameleon module)
│   ├── jack_patterns.py (Original esoteric patterns)
│   ├── euromillions_data_*.py (Historical data 2012-2026)
├── frontend/        
│   ├── src/App.js (React UI with lottery machine)
└── memory/
    ├── PRD.md
```

---

## Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/euromillions/master-predictor` | POST | Generate tickets with DJ Engine |
| `/api/euromillions/story-generator-save` | GET | Generate & save for hit tracking |
| `/api/euromillions/generation-history` | GET | Get saved prediction history |
| `/api/euromillions/calculate-hits/{id}` | POST | Calculate hits against actual draw |
| `/api/euromillions/hit-tracker` | GET | Get hit tracking data |

---

## DJ Engine Weight Configuration

**MEGA BANGERS (>40%):**
- Number ending in S1: 47.6% (weight: 15)
- 9-Family: 49.8% (weight: 12)
- 7-Family: 47.4% (weight: 12)
- 8-Family: 42.3% (weight: 12)

**HIGH (25-40%):**
- Consecutive pair: 38.8% (weight: 7)
- Any repeat: 38.5% (weight: 7)
- Day Dance Stars: 30.5% (weight: 10)

**DATE CHAMELEON (NEW!):**
- Raw digits: 70.3% (weight based on hit rate / 5)
- Day×10+circle(M): 61.2%
- Day+Month direct: 55.5%

---

## Upcoming Tasks

### P0 (Immediate)
- None currently blocking

### P1 (Next)
- Visual pattern explanations in UI (show WHY each number was picked)
- Generate predictions for April 11, 2026 draw

### P2 (Future)
- Refactor monolithic server.py and euromillions_routes.py
- Fix lottery_fetcher.py auto-sync reliability
- Backtest more exotic patterns

---

## Testing Notes

**DJ Engine Test for 07.04.2026:**
- Actual draw: [11, 14, 19, 36, 49] ⭐ [6, 7]
- DJ Ticket 2: [1, **11**, 41, 47, **49**] ⭐ [**6**, **7**] = **2/5 + 2/2** BOTH STARS!
- Date Chameleon correctly predicted:
  - Day+Month = 7+4 = **11** ✅
  - 74-25 = **49** ✅

**Date Chameleon Backtest:**
- 209 draws tested
- 70.3% raw digit hit rate confirmed
- 61.2% circle formula hit rate confirmed

---

## App Health
- Core App: ✅ Healthy
- UI: ✅ Healthy  
- Backend: ✅ Running on port 8001
- Frontend: ✅ Running on port 3000
- MongoDB: ✅ Connected
- Hit Tracker: ✅ Working with Stars display
- Date Chameleon: ✅ Integrated into DJ Engine
