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

### NEW: Digit DNA Pattern (Discovered April 15, 2026)
The digits from date + circles + date math + previous draw's circle readings create a "digit field" that predicts the next draw.
- **Field accuracy: 5.3/6 across 1,380 draws (2013-2026)**
- **96.2% of draws have 4+ numbers in the digit field**
- **Strongest source: P4P5P6 concat from prev draw (36.8% hit rate)**

### NEW: P123 Concat Digit Pattern (Discovered April 15, 2026)
Reading P1+P2+P3 as a digit string, the digits predict the next draw's numbers.
- **56% chance of 3+ hits when 5+ unique digits** (backtested 1 year)
- Three sources: P123 from prev draw + date concat + P123 from prev-prev draw
- Numbers appearing in multiple pools get strongest boost

### NEW: P6 Circle Bridge — Swiss→Euro (Discovered April 15, 2026)
Swiss P6 connects to Euro through BOTH circle constants:
- Swiss P6 - 21 = Euro number (Swiss circle): 18% hit
- Swiss P6 - 25 = Euro number (Euro circle): 27% hit
- **Combined: 40% hit rate** (1 in 2.5 draws!)
- Strongest sums: 76 (75%), 66 (75%), 64 (67%)
- Current: P6=35+34=69, P2 concat="96" → bridges to 9, 10, 13, 14 in Euro

### NEW: 69 Math Pattern (Discovered April 15, 2026)
When P6+P6=69 and P2 concat=96:
- |6-9|=3, 6+9=15, circle(6)=27, circle(9)=30, 69-42=27
- 35-14=21 (Swiss circle), 34-13=21 (Swiss circle)
- 35-10=25 (Euro circle), 34-9=25 (Euro circle)
- ALL FOUR bridges hit simultaneously on 10.04.2026!
- **prev P2 ± 1 = 12.6% = 5.3x random!** (strongest P2 predictor)
- prev P1 + Lucky = 5.4% = 2.3x random
- Month = P2: 3.8% = 1.6x random

### Position Analysis (1,381 draws)
- P1: avg=6.0, 81% in 1-9
- P2: avg=12.1, 88% in 1-19
- P3: avg=18.2, 95% below 30 (only 4.9% ≥30!)
- P4: avg=24.6
- P5: avg=31.1, 67% ≥30
- P6: avg=37.3, 93% ≥30
- Average numbers ≥30 per draw: 1.9

### THE STORY PATTERNS
1. **The 152 Formula**: P1*concat + P2 + P3 creates digits predicting next draw
2. **The Bridge Chain**: Numbers carry forward between consecutive draws
3. **The Circle Gate**: Euro 1-2-3-4-5 → Swiss circles (+21)
4. **Star 12 Split**: Star 12 → digits 1+2=3 AND "3-2"=32
5. **Formula Compression**: Q1 chain 166→115→54→50→24 (spring coiling → Q2 bounce)

### The Story Three (Swiss Prediction for Q2 Opening)
- **3**: Euro's circle(28), Star 12's soul (1+2), Swiss P1 king (12.7%)
- **25**: The missing circle (22✓23✓24✓25❌26✓), date's whisper
- **32**: Star 12's body (3-2), mid-month warrior (1.17x)

## Architecture
```
/app/backend/
  server.py          - FastAPI main, Swiss Lotto, Money Mode v5
  euromillions_routes.py - EuroMillions routes + 2Chance + Hit Tracker
  dj_patterns.py     - DJ Engine (59+ patterns + Swiss P1 Bridge)
  digit_dna.py       - NEW! Digit DNA + P123 Concat pattern engine
  sleeper_engine.py  - Sleeper detection + forecast
  hit_tracker.py     - Hit tracker
  lottery_fetcher.py - Data sync (lottolyzer + API + swisslos 2Chance scraper)
/app/frontend/src/
  App.js             - React UI (Sleeper Radar + 2Chance + Hit Tracker)
  App.css            - Casino coin animations
```

## What's Been Implemented

### Session: April 16, 2026 (Fork 6 - Current)
- **"How to Use" button repositioned** — moved to left of "Your Lucky Numbers" heading above ball generator
- **Live Users tracking** — anonymous heartbeat system, MongoDB `active_users` collection, pulsing green panel on right side
- **Pending Tickets mode-aware** — filters by Swiss/Euro based on active lottery mode, shows Stars for Euro tickets
- **Layout rebalanced** — both side panels nudged toward center for better visual balance
- **Mobile Pending fix** — centered balls, amber Lucky circles and yellow Star circles on mobile
- **20 Ticket Limit** — max 20 tickets per visitor per draw (combined Swiss+Euro), enforced via visitor_id tracking

### Session: April 15, 2026 (Fork 5)
- **Digit DNA Engine** — date + circles + date math + prev draw circles → digit field (5.3/6 over 1,380 draws)
- **P123 Concat Pattern** — digit story across draws (56% at 3+ with 5 unique digits)
- **P2 Prediction Rule** — prev P2 ±1 = 5.3x random
- **Family Rhythm** — decade density analysis for grouping predictions
- **69 Bridge** — P6 Circle Bridge Swiss→Euro coded into engine
- **Hit Tracker overhaul** — top 20 tickets with 2+ hits, unified format
- **Dual Ticket Counters** — all-time & next draw totals in UI
- **Pending Tickets Box** — scrollable side panel showing saved tickets
- **How to Use modal** — mystical guide explaining all app features
- **Money Mode v5** — DNA + P123 + P2 + 1 High Guarantee + Crazy tickets
- **Min 2 tickets** = 5 CHF (Swiss Lotto rule)
- **Simulation API** — `/api/digit-dna/simulate?target_date=DD.MM.YYYY`
- **Multi-year backtest** — validated across 2013-2026 (1,381 draws)
- **Deployment blocker fixed** — .gitignore cleaned

### Session: April 15, 2026 (Fork 3)
- 2Chance Auto-Sync, Hit Tracker Overhaul, DB Cleanup
- Swiss P1 → Euro P1 Bridge, Swiss P1 Deep Analysis
- The Story Patterns, Reverse Twin + Day×Month-10, Sleeper Radar

### Previous Sessions
- Fork 2: lottolyzer sync, Beast Block, Star->P3 Dance, DB fix, Learning Loop
- Fork 1: Sleeper Engine, Hit Tracker, Casino Makeover

## Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/money-mode` | GET | Swiss Money Mode v5 (DNA + P123 + P2 + Sleepers, min 2 tickets) |
| `/api/swiss-sleepers` | GET | Swiss Lotto sleeper analysis (deep/wake/fresh) |
| `/api/digit-dna/simulate` | GET | Backtest Digit DNA for any date |
| `/api/sync-results` | POST | Sync all (Euro + Swiss + 2Chance) |
| `/api/euromillions/master-predictor` | POST | DJ Engine + auto-save |
| `/api/euromillions/money-mode` | POST | Euro Money Mode (now with P2 + P123) |
| `/api/euromillions/sleeper-forecast` | GET | 10-draw forecast |
| `/api/euromillions/generation-history` | GET | Hit tracker (top 20, 2+ hits) |
| `/api/draws` | GET | Swiss Lotto draws |

## Engine Performance (v5)
- Q1 2026: avg best 2.3/6, **36% get 3+ hits** from 10 tickets
- Two 4/6 hits: 03.01.2026 and 14.03.2026
- P2 prediction: 12% actual (baseline 7%, 1.7x boost)
- Random 2022-2025: avg best 2.0/6

## Upcoming Tasks
- **P0**: Code Q1→Q2 transition stories into prediction engine
- **P1**: Position-by-position deep analysis for P3-P6 and Lucky
- **P1**: Euro tickets with Swiss P1 Bridge for next EuroMillions
- **P2**: Cross-draw Bridge Chain Tracker UI
- **P2**: Refactor monolithic files (server.py ~5000 lines, dj_patterns.py ~3400 lines)

## App Health
All systems healthy. Backend + Frontend + MongoDB running. Deployment blocker (.gitignore) fixed. Active user tracking live.
