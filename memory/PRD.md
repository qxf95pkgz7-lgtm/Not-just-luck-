# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
A custom Swiss Lotto and EuroMillions Pattern Analyzer ("Lucky Jack") featuring esoteric numerology patterns. Enthusiastic, mystical data scientist persona ("Ya man!", "🎻", "🎧"). Focus on "The Music of the Numbers" rather than standard probability.

## Core Philosophy
1. Circle Math: +25 or -25
2. Reverse Logic: Flip digits
3. Buddy Additions: Day+Month, P1+P2
4. Date Chameleon: The date speaks in MANY voices
5. Cross-Lottery Vibes: Swiss to Euro connections
6. Sleeper Wake Alarm: Overdue numbers snap back
7. Beast Block: 666 suppression (Star 6 after 2-streak)
8. Star->P3 Dance: Stars predict P3 via concat/reverse/circle (17.5%)
9. The Dance: P1(n)+P2(n+1)->circle->P1(n+2) (6.0%)
10. Draw-to-Draw Learning: Hot/cold momentum tracking
11. Reverse Twin Generator: reverse(N) from previous draw (NEW)
12. Day x Month - 10: Esoteric formula (NEW)

## Architecture
```
/app/backend/
  server.py          - FastAPI main, Swiss Lotto
  euromillions_routes.py - EuroMillions routes + all APIs
  dj_patterns.py     - DJ Engine (59+ patterns + learning)
  sleeper_engine.py   - Sleeper detection + forecast
  hit_tracker.py      - Hit tracker (sorted by target_date)
  lottery_fetcher.py  - Data sync (lottolyzer.com + API)
/app/frontend/src/
  App.js             - React UI (+ Sleeper Radar Panel)
  App.css            - Casino coin animations
```

## What's Been Implemented

### Session: April 15, 2026 (Fork 3 continued)
- **2Chance (Swiss Second Draw)** — Full feature: manual entry of 2Chance numbers, save to DB, check ALL EuroMillions tickets against 2Chance results, show winners with prize tiers (3/5=CHF 44, 4/5=CHF 950, 5/5=CHF 150K)
- **Hit Tracker Fixed** — API now returns ALL generations merged by date+mode (was only showing 10). Shows 190 generations properly
- **2 draws already saved**: 14.04.2026 [2,11,12,34,49] and 10.04.2026 [6,19,23,42,47]

### Session: April 14, 2026 (Fork 3)
- **10 DJ-Tuned Tickets Generated** for 15.04.2026 using Money Mode with all new patterns
- **Frontend Sleeper Radar Panel** - Tease-Hot Numbers, Star Sleepers, 10-Draw Forecast (EuroMillions only)
- **Reverse Twin Generator** pattern coded into dj_patterns.py and integrated into both engines
- **Day x Month - 10** pattern coded into dj_patterns.py and integrated into both engines
- ALL TESTS PASS: 19/19 backend, 10/10 frontend

### Session: April 14, 2026 (Fork 2)
- **PERMANENT FIX: Update/Sync** - Replaced 3 broken Swiss scrapers with lottolyzer.com
- **Lock Positions Fix** - Case mismatch p1->P1, added Money Mode locks, duplicate prevention
- **Beast Block (666)** - Star 6 suppressed after 2-streak (77% block rate)
- **DB Data Fix** - 60 wrong EuroMillions draws corrected from API
- **Star->P3 Dance** - 5 formulas: concat(S2,S1)->circle, rev(S1+S2), S1+S2+25, S2+25, rev(S1*S2)
- **The Dance Pattern** - P1(n)+P2(n+1)->circle->P1(n+2) coded into Money Mode
- **12 Scream Pattern** - S1+S1=12 signal boosts number 12 (2.1x baseline)
- **Engine Tuning** - Fixed Money Mode repetition bias, position-aware weights, decade spread
- **Draw-to-Draw Learning** - Hot/cold number tracking, P3 momentum, star momentum, cold sleeper circle boost
- **Simulation Results**: P3 coverage 90%, Star coverage 100%, consistent across Aug2025-Apr2026

### Session: April 13, 2026 (Fork 1)
- Sleeper Engine + integration into DJ patterns
- Hit Tracker rebuilt (auto-save, sort by target_date)
- Olivia's Kiss Casino Makeover

## Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sync-results` | POST | Sync both lotteries |
| `/api/euromillions/master-predictor` | POST | DJ Engine + auto-save |
| `/api/euromillions/money-mode` | POST | Money Mode + auto-save |
| `/api/euromillions/sleeper-forecast` | GET | 10-draw forecast |
| `/api/euromillions/generation-history` | GET | Hit tracker (all gens merged) |
| `/api/euromillions/update-results` | POST | Euro-only update |
| `/api/euromillions/2chance/save-result` | POST | Save 2Chance draw numbers |
| `/api/euromillions/2chance/results` | GET | Get 2Chance history |
| `/api/euromillions/2chance/check` | POST | Check tickets vs 2Chance |

## Upcoming Tasks
- **P1**: Sleeper Engine auto-adjust (recalculate after real draw results)
- **P1**: Try scraping swisslos.ch for automatic 2Chance result fetching
- **P2**: Refactor monolithic files (server.py, euromillions_routes.py, dj_patterns.py)

## App Health
- Core App: Healthy
- Update/Sync: lottolyzer.com
- Lock Positions: Fixed
- Beast Block: Active
- Star->P3 Dance: Active
- Draw-to-Draw Learning: Active
- DB Data: Corrected (60 fixes)
- Hit Tracker: Working (fixed - shows all 190 gens)
- Sleeper Radar Panel: Working
- Reverse Twin Pattern: Active
- Day x Month - 10 Pattern: Active
- 2Chance Panel: Working (manual entry + check)
