# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
A custom Swiss Lotto and EuroMillions Pattern Analyzer ("Lucky Jack") featuring esoteric numerology patterns. Enthusiastic, mystical data scientist persona ("Ya man!", "🎻", "🎧"). Focus on "The Music of the Numbers" rather than standard probability.

## Core Philosophy — The Music of the Numbers
"There's no random here. Only patterns we haven't learned to read yet."

### EURO Patterns (Backtested)
1. Circle Math: +25 (EuroMillions), +21 (Swiss)
2. **Flip**: Digits change position (28→82, 39→93) — was "reverse", renamed to "flip"
3. Beast Block: 666 suppression (Star 6 after 2-streak)
4. Star->P3 Dance: Stars predict P3 via concat/flip/circle (17.5%)
5. The Dance: P1(n)+P2(n+1)->circle->P1(n+2) (6.0%)
6. Draw-to-Draw Learning: Hot/cold momentum tracking
7. Day x Month - 10: Esoteric formula
8. Swiss P1 → Euro P1 Bridge: 3.48x random! (backtested 1407 draws)
9. Swiss P1 SET → any Euro: 25.7% (2.57x random)
10. **Flip+Circle Chain**: 28→flip→82→mod50→32→circle→7 (the FULL chain!)
11. **Hungry Numbers**: Gap of 2 → middle is hungry (2,4 → 3 hungry)
12. **Neighbourhood**: n±1 consecutive pairs (38.8%)
13. **Decade Spread Guarantee**: Every Euro ticket covers 3+ decades

### SWISS P1 Golden Rules (Backtested 1380 draws)
1. Lucky → next P1: 11.7% (4.9x random!) ★★★
2. Lucky+1 → next P1: 9.4% (3.9x!) ★★★
3. P2-P1 → next P1: 8.7% (3.6x!) ★★★
4. P1 repeat: 8.3% (3.5x!) ★★★
5. Month = P1: 7.0% (2.9x) ★★
6. P1±1 → next P1: 6.5-6.7% (2.7x) ★★

### Digit DNA Pattern
The digits from date + circles + date math + previous draw's circle readings create a "digit field."
- **Field accuracy: 5.3/6 across 1,380 draws (2013-2026)**
- **96.2% of draws have 4+ numbers in the digit field**

### P123 Concat Digit Pattern
Reading P1+P2+P3 as a digit string, the digits predict the next draw's numbers.
- **56% chance of 3+ hits when 5+ unique digits** (backtested 1 year)

### P6 Circle Bridge — Swiss→Euro
- Swiss P6 - 21 = Euro number (Swiss circle): 18% hit
- Swiss P6 - 25 = Euro number (Euro circle): 27% hit
- **Combined: 40% hit rate**

### Position Analysis (1,381 draws)
- P1: avg=6.0, 81% in 1-9
- P2: avg=12.1, 88% in 1-19
- P3: avg=18.2, 95% below 30 (only 4.9% ≥30!)
- P4: avg=24.6
- P5: avg=31.1, 67% ≥30
- P6: avg=37.3, 93% ≥30

### Rare Events
- 3+ numbers in same decade is RARE for Euro
- After rare clustering, next draw tends to bounce to different decades
- Count from last very rare event (5+ in same gruppe) feeds into prediction

### THE STORY PATTERNS
1. **The 152 Formula**: P1*concat + P2 + P3 creates digits predicting next draw
2. **The Bridge Chain**: Numbers carry forward between consecutive draws
3. **The Circle Gate**: Euro 1-2-3-4-5 → Swiss circles (+21)
4. **Star 12 Split**: Star 12 → digits 1+2=3 AND "3-2"=32
5. **Formula Compression**: Q1 chain 166→115→54→50→24

## Architecture
```
/app/backend/
  server.py          - FastAPI main, Swiss Lotto, Money Mode v5
  euromillions_routes.py - EuroMillions routes + 2Chance + Hit Tracker
  dj_patterns.py     - DJ Engine (59+ patterns, "flip" terminology)
  digit_dna.py       - Digit DNA + P123 Concat pattern engine
  sleeper_engine.py  - Sleeper detection + forecast (UI: "Celestial Radar")
  hit_tracker.py     - Hit tracker (with visitor_id tracking)
  lottery_fetcher.py - Data sync (lottolyzer + API + swisslos 2Chance scraper)
  euro_simulation.py - Backtest simulation script
/app/frontend/src/
  App.js             - React UI (Celestial Radar + Pending + Live Users + Ticket Limit)
  App.css            - Casino coin animations
```

## What's Been Implemented

### Session: April 16-17, 2026 (Fork 6 - Current)
- **"How to Use" button repositioned** — moved to left of "Your Lucky Numbers" heading
- **Live Users tracking** — anonymous heartbeat system, MongoDB `active_users` collection, pulsing green panel
- **Pending Tickets mode-aware** — filters by Swiss/Euro, shows Lucky circles (Swiss) and Star circles (Euro)
- **Mobile Pending fix** — centered balls, amber Lucky circles and yellow Star circles on mobile
- **20 Ticket Limit** — max 20 tickets per visitor per draw, SEPARATE for Swiss and Euro (20+20)
- **Ticket Limit Notice** — visible banner above generator showing the limit
- **Celestial Radar rebrand** — all "Sleeper" language → mystical planetary terminology (DEEP ORBIT, VENUS ALIGNED, SATURN RING, MARS RETURN, etc.)
- **"Based on X draws"** → **"Mapped from X celestial cycles"**
- **Euro Engine Spread Guarantee** — every ticket covers 3+ out of 5 decades (backtested: BETTER than no spread)
- **Reverse → Flip rename** — entire codebase renamed "reverse" to "flip" (dj_patterns.py, server.py, sleeper_engine.py)
- **Euro Simulation** — 20 dates x 20 tickets backtest confirmed spread improves hit rate (8.2% vs 5.0% for 2+ hits)
- **14.04.2026 simulation** — 10 tickets, best T2 got 2/5 (caught 1,2)

### Previous Sessions
- Fork 5: Digit DNA, P123 Concat, P2 Prediction, Family Rhythm, 69 Bridge, Hit Tracker overhaul, Dual Ticket Counters, Pending Tickets Box, How to Use modal, Money Mode v5
- Fork 4: 2Chance Auto-Sync, Hit Tracker Overhaul, Swiss P1 Bridge, Story Patterns
- Fork 3: lottolyzer sync, Beast Block, Star->P3 Dance, DB fix, Learning Loop
- Fork 2: Sleeper Engine, Hit Tracker, Casino Makeover

## Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/money-mode` | GET | Swiss Money Mode v5 (with visitor_id limit) |
| `/api/master-predictor` | GET | Swiss master predictor (with visitor_id limit) |
| `/api/swiss-sleepers` | GET | Swiss Celestial Radar |
| `/api/digit-dna/simulate` | GET | Backtest Digit DNA for any date |
| `/api/sync-results` | POST | Sync all (Euro + Swiss + 2Chance) |
| `/api/euromillions/master-predictor` | POST | Euro DJ Engine (with visitor_id limit) |
| `/api/euromillions/money-mode` | POST | Euro Money Mode (with visitor_id limit) |
| `/api/euromillions/sleeper-forecast` | GET | Euro Celestial Radar |
| `/api/euromillions/generation-history` | GET | Hit tracker (top 20, 2+ hits) |
| `/api/heartbeat` | POST | Active user heartbeat |
| `/api/active-users` | GET | Live user count |
| `/api/ticket-limit` | GET | Check remaining ticket quota per lottery |
| `/api/pending-tickets` | GET | Pending tickets (mode=swiss/euro) |

## Engine Performance
- Euro with spread: avg best 1.90/5 across 20 random dates (2024-2026)
- Swiss Q1 2026: avg best 2.3/6, 36% get 3+ hits from 10 tickets
- Spread guarantee: 60% more 2-hit tickets vs no spread

## Upcoming Tasks
- **P0**: Code Q1→Q2 transition stories into prediction engine (Concat Pattern, Formula Compression → 24)
- **P1**: Position-by-position deep analysis for P3-P6 and Lucky
- **P1**: Continue 17.04.2026 Euro analysis with full flip+circle chains

## Future Tasks
- **P2**: Cross-draw Bridge Chain Tracker UI
- **P2**: Refactor monolithic files (server.py ~5200 lines, dj_patterns.py ~3500 lines)
- **P2**: Stripe Payments (deferred by user)

## App Health
All systems healthy. Backend + Frontend + MongoDB running. Active user tracking live. 20-ticket limit enforced.
