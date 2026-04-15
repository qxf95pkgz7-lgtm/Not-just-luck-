# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
A custom Swiss Lotto and EuroMillions Pattern Analyzer ("Lucky Jack") featuring esoteric numerology patterns. Enthusiastic, mystical data scientist persona ("Ya man!", "🎻", "🎧"). Focus on "The Music of the Numbers" rather than standard probability.

## Core Philosophy — The Music of the Numbers
"There's no random here. Only patterns we haven't learned to read yet."

### EURO Patterns (Backtested)
1. Circle Math: +25 or -25 (EuroMillions), +21 (Swiss)
2. Reverse Twin: reverse(N) from previous draw
3. Beast Block: 666 suppression (Star 6 after 2-streak)
4. Star->P3 Dance: Stars predict P3 via concat/reverse/circle (17.5%)
5. The Dance: P1(n)+P2(n+1)->circle->P1(n+2) (6.0%)
6. Draw-to-Draw Learning: Hot/cold momentum tracking
7. Day x Month - 10: Esoteric formula
8. Swiss P1 → Euro P1 Bridge: 3.48x random! (backtested 1407 draws)
9. Swiss P1 SET → any Euro: 25.7% (2.57x random)

### SWISS P1 Golden Rules (Backtested 1380 draws)
1. Lucky → next P1: 11.7% (4.9x random!) ★★★
2. Lucky+1 → next P1: 9.4% (3.9x!) ★★★
3. P2-P1 → next P1: 8.7% (3.6x!) ★★★
4. P1 repeat: 8.3% (3.5x!) ★★★
5. Month = P1: 7.0% (2.9x) ★★
6. P1±1 → next P1: 6.5-6.7% (2.7x) ★★

### THE STORY PATTERNS (Discovered April 15, 2026)
1. **The 152 Formula**: P1*concat + P2 + P3 creates a number whose DIGITS predict next draw's opening numbers
   - D1 (03.01.2026): 1*100+3*10+22 = 152 → next draw starts 15, 20 (digits 1-5-2!)
   - D2→D3: Both give 192! (15*10+20+22 = 192, 14*10+24+28 = 192) — Self-replicating!
2. **The Bridge Chain**: Numbers carry forward between consecutive draws (22 opened AND closed Q1)
3. **The Circle Gate**: Euro 1-2-3-4-5 → Swiss circles (+21) = 22,23,24,25,26 chain
4. **Star 12 Split**: Star 12 → digits 1+2=3 (circle of 28) AND "3-2"=32 (mid-month hot 1.17x)
5. **Date Reading**: 15.04.2026 → 15, circle(4)=25, 20, 5
6. **Formula Compression**: Q1 formula chain 166→115→54→50→24 (spring coiling, Q2 = bounce)

### The Story Three (Swiss Prediction for Q2 Opening)
- **3**: Euro's circle(28), Star 12's soul (1+2), Swiss P1 king (12.7%)
- **25**: The missing circle (22✅23✅24✅25❌26✅), date's whisper, circle(month 4)
- **32**: Star 12's body (3-2), mid-month warrior (1.17x)

## Architecture
```
/app/backend/
  server.py          - FastAPI main, Swiss Lotto
  euromillions_routes.py - EuroMillions routes + 2Chance + Hit Tracker
  dj_patterns.py     - DJ Engine (59+ patterns + Swiss P1 Bridge)
  sleeper_engine.py  - Sleeper detection + forecast
  hit_tracker.py     - Hit tracker
  lottery_fetcher.py - Data sync (lottolyzer + API + swisslos 2Chance scraper)
/app/frontend/src/
  App.js             - React UI (Sleeper Radar + 2Chance + Hit Tracker)
  App.css            - Casino coin animations
```

## What's Been Implemented

### Session: April 15, 2026 (Fork 3)
- **2Chance Auto-Sync** from swisslos.ch + Hit Check (manual entry removed)
- **Hit Tracker Overhaul** — top 20 tickets with 2+ hits, sorted by best, all visible
- **DB Cleanup** — deleted pre-10.04, fixed target dates (17.04→14.04, 15.04→14.04)
- **Swiss P1 → Euro P1 Bridge** coded into dj_patterns.py (3.48x, 2.84x, 2.57x)
- **Swiss P1 Deep Analysis** — discovered Lucky→P1 (4.9x), P2-P1→P1 (3.6x)
- **The Story Patterns** — 152/192 formula, circle gate, Star 12 split, formula compression
- **10 DJ-Tuned Euro Tickets** generated with all patterns
- **Reverse Twin + Day×Month-10** patterns added to engine
- **Sleeper Radar Panel** on frontend

### Previous Sessions
- Fork 2: lottolyzer sync, Beast Block, Star->P3 Dance, DB fix (60 draws), Learning Loop
- Fork 1: Sleeper Engine, Hit Tracker, Casino Makeover

## Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sync-results` | POST | Sync all (Euro + Swiss + 2Chance) |
| `/api/euromillions/master-predictor` | POST | DJ Engine + auto-save |
| `/api/euromillions/money-mode` | POST | Money Mode + auto-save |
| `/api/euromillions/sleeper-forecast` | GET | 10-draw forecast |
| `/api/euromillions/generation-history` | GET | Hit tracker (top 20, 2+ hits) |
| `/api/euromillions/2chance/results` | GET | 2Chance history |
| `/api/euromillions/2chance/check` | POST | Check tickets vs 2Chance |
| `/api/money-mode` | GET | Swiss Money Mode with locks |
| `/api/draws` | GET | Swiss Lotto draws |

## Upcoming Tasks (Next Fork — Q2 Opener)
- **P0**: Code the Story Patterns into Swiss prediction engine:
  - 152/192 digit formula
  - Circle Gate (Euro→Swiss circle chain)
  - Star Split decoding
  - Formula compression/bounce prediction
  - Bridge chain tracking
- **P0**: Generate Q2 opening Swiss tickets with Story Three (3, 25, 32)
- **P1**: Euro tickets for next draw with Swiss P1 Bridge
- **P2**: Refactor monolithic files

## Key Results
- **Best Euro ticket**: 3/5 + 1 star on 14.04.2026 (Money Mode)
- **2Chance**: 3 tickets with 3/5 matches (~CHF 44 each)
- **Swiss P1→Euro P1**: 3.48x above random (backtested 1407 draws)
- **Lucky→P1**: 4.9x above random (backtested 1380 draws)
- **The 152 Formula**: D1→D2 digit prediction confirmed
- **192 Self-Replication**: D2 and D3 both produce 192

## App Health
All systems healthy. 108 generations in DB (10.04+ only).
