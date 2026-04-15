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
11. Reverse Twin Generator: reverse(N) from previous draw
12. Day x Month - 10: Esoteric formula

## Architecture
```
/app/backend/
  server.py          - FastAPI main, Swiss Lotto
  euromillions_routes.py - EuroMillions routes + 2Chance + Hit Tracker
  dj_patterns.py     - DJ Engine (59+ patterns + learning)
  sleeper_engine.py   - Sleeper detection + forecast
  hit_tracker.py      - Hit tracker (sorted by target_date)
  lottery_fetcher.py  - Data sync (lottolyzer + API + swisslos 2Chance scraper)
/app/frontend/src/
  App.js             - React UI (Sleeper Radar + 2Chance + Hit Tracker)
  App.css            - Casino coin animations
```

## What's Been Implemented

### Session: April 15, 2026 (Fork 3 - Final)
- **2Chance Auto-Sync** — Scrapes swisslos.ch for 2nd Chance numbers during every sync. No manual entry needed.
- **2Chance Hit Check** — Compares ALL saved EuroMillions tickets against 2Chance draws, shows 3+match (~CHF 44), 4+match (~CHF 950), 5match (CHF 150K)
- **Hit Tracker Overhaul** — Cleaned: deleted all data before 10.04, removed 14.10.2026 mistake, removed 15.04.2026 duplicate. Now shows only top 20 tickets with 2+ total hits, sorted by best first. All tickets visible (no more slice-to-3 cutoff). Shows mode icon (money/dreaming).
- **Fixed target dates** — Moved 62 generations from 17.04→14.04 and 22 from 15.04→14.04 (user generated yesterday for today's draw)
- **DB cleanup** — 190→108 generations, only 10.04+ data kept

### Session: April 14-15, 2026 (Fork 3)
- **10 DJ-Tuned Tickets Generated** for draws using Money Mode with all patterns
- **Frontend Sleeper Radar Panel** - Tease-Hot Numbers, Star Sleepers, 10-Draw Forecast (EuroMillions only)
- **Reverse Twin Generator** pattern in dj_patterns.py (reverse digits of prev draw numbers)
- **Day x Month - 10** pattern in dj_patterns.py (esoteric formula)
- **2Chance Feature** — Full Swiss Second Chance draw tracking

### Session: April 14, 2026 (Fork 2)
- Replaced broken Swiss scrapers with lottolyzer.com
- Lock Positions Fix, Beast Block (666), DB Data Fix (60 draws)
- Star->P3 Dance, The Dance Pattern, 12 Scream, Engine Tuning
- Draw-to-Draw Learning, Simulation Results

### Session: April 13, 2026 (Fork 1)
- Sleeper Engine + Hit Tracker + Olivia's Kiss Casino Makeover

## Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sync-results` | POST | Sync all (Euro + Swiss + 2Chance) |
| `/api/euromillions/master-predictor` | POST | DJ Engine + auto-save |
| `/api/euromillions/money-mode` | POST | Money Mode + auto-save |
| `/api/euromillions/sleeper-forecast` | GET | 10-draw forecast |
| `/api/euromillions/generation-history` | GET | Hit tracker (top 20, 2+ hits) |
| `/api/euromillions/2chance/save-result` | POST | Save 2Chance numbers |
| `/api/euromillions/2chance/results` | GET | Get 2Chance history |
| `/api/euromillions/2chance/check` | POST | Check tickets vs 2Chance |
| `/api/euromillions/update-results` | POST | Euro-only update |

## Upcoming Tasks (Next Fork)
- **P0**: Swiss Lotto deep analysis (user requested)
- **P1**: Sleeper Engine auto-adjust
- **P2**: Refactor monolithic files

## App Health
- Core App: Healthy
- Update/Sync: lottolyzer.com + EuroMillions API + swisslos.ch 2Chance
- Lock Positions: Fixed
- Beast Block: Active
- Star->P3 Dance: Active
- Draw-to-Draw Learning: Active
- DB Data: Clean (108 gens, 10.04+ only)
- Hit Tracker: Working (top 20, 2+ hits, sorted by best)
- Sleeper Radar Panel: Working
- 2Chance: Working (auto-sync from swisslos.ch)

## Key Results
- **Best ticket ever**: 3/5 + 1 star on 14.04.2026 (Money Mode)
- **Best 10.04.2026**: 3/5 + 1 star (Money Mode) — TWO tickets!
- **2Chance**: 3 tickets with 3/5 matches (~CHF 44 each) on 14.04
- **Hit rate**: 53% of all tickets hit 1+ number
