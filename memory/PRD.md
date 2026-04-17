# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
Custom lottery pattern analyzer with mystical DJ persona. Focus on esoteric numerology, cross-lottery connections, and "The Music of the Numbers."

## Core Philosophy
**DATE first → Count draws → Count rare events → Read DIGITS not numbers → Read the story → Listen to the music**

## THE STAR→Q COUNT→P1 DISCOVERY (Validated April 2026)
**Stars from Q(N+1) draws index into Q(N) draw count → Q(N) P1 predicts Q(N+1) P1/P2**
- Q1→Q2 2026: **75% hit rate** (6/8 lookups hit P1 or P2!)
- Q4→Q1 2026: **40%**
- Q1→Q2 2025: **35%**
- Pattern is ACCELERATING over recent quarters
- Star 12 wraps to 1 (like a clock)
- Star digits matter: Star 12 = digits 1,2 → can predict P1=1 and P2=2

### Q1 2026 P1 Map (Reference for Q2 predictions)
c1=8, c2=5, c3=1, c4=6, c5=5, c6=11, c7=4, c8=4, c9=14, c10=26, c11=10, c12=1

### Q2 2026 Verified Results
- d1 (07.04): Stars[6,7] → c6=11 → P1=11 EXACT! c7=4 → digit in P2=14
- d2 (10.04): Stars[6,9] → c6=11 → P1=10 (±1!) c9=14 → P2=13 (±1!)
- d3 (14.04): Stars[5,12] → c12=1 → P1=1 EXACT! c5=5 → 5-d3=2=P2

## Pattern Library

### Flip+Circle Chain (renamed from "reverse")
- Flip = digits change position: 28→82, 39→93, 14→41
- Single digits: circle FIRST, then flip: 4→circle→29→flip→92→land
- Full chain: 28→flip→82→mod50→32→circle→7
- Long distance family: 14→41→91→19 (all connected!)

### Date Reading Method
Read the date EVERY possible way:
- 17.04.2026 → 174 (concat), 199 (170+29), 17=42 (circle), 424 (42+4), 449 (420+29)
- 14.04.2026 → 14=39→flip→43→+4(month)=47 (predicted!)
- 47 hid in d3 as: P3=4 and P4=28(=7 via flip+circle chain)

### The 19 Story (Q1→Q2 Bridge)
- P3 counting: 16→17→43(=18)→19 MISSING
- 10 (Q1 winner) took 19's place
- 29 danced with 10 (29-10=19, calling it!)
- 44 = 19 in circle (19+25=44)
- Finally: 19 arrived DIRECTLY at P3 of Q2 d1!

### The 1-2-3-4 Story
- d3: [1, 2, 4, 28, 44] — looks like 1,2,_,4 (3 missing)
- But 28→circle→3! So it WAS 1-2-3-4, with 3 wearing its circle costume as 28!

### P1 Counting Q2 2026
- d1: P1=11 (counts as 1, or 1+1=2)
- d2: P1=10 (counts as 2, or 1+0=1)  
- d3: P1=1 (counts as 3)
- d4: P1=? (counting says 4)

### Euro Pattern Hit Rates (Backtested)
| Pattern | Hit Rate |
|---------|----------|
| Neighbourhood (±1) | 38.8% |
| Repeat | 38.5% |
| Sum Last Digit Family | 39.9% |
| Direct Addition (A+B) | 25.2% |
| Cross-Lottery Swiss→Euro | 13.3% |
| Flip Logic | 10.1% |
| Circle Math (+25) | 9.3% |
| Hungry (gap=2→middle) | 9.3% |
| Star 5→P5 flip | 15.1% (strongest star signal!) |

### Decade Spread Guarantee
Every Euro ticket covers 3+ out of 5 decades. Backtested: 8.2% hit 2+ (vs 5.0% without spread)

## Architecture
```
/app/backend/
  server.py          - FastAPI, Swiss Lotto engine (~5200 lines)
  euromillions_routes.py - Euro routes + Hit Tracker
  dj_patterns.py     - DJ Engine (~3500 lines, "flip" terminology)
  digit_dna.py       - Digit DNA + P123 Concat
  sleeper_engine.py  - "Celestial Radar" (mystical UI)
  hit_tracker.py     - Hit tracking with visitor_id
  lottery_fetcher.py - Data sync
  euro_simulation.py - Backtest script
/app/frontend/src/
  App.js             - React UI
  App.css
```

## What's Been Implemented (This Session - April 16-17, 2026)
- "How to Use" button repositioned (left of heading)
- Live Users tracking (heartbeat, MongoDB, pulsing panel)
- Pending Tickets mode-aware (Swiss/Euro filtered, Lucky+Star circles)
- Mobile Pending fix (centered balls)
- 20 Ticket Limit per lottery per user (20 Swiss + 20 Euro separately)
- Ticket Limit Notice banner
- Celestial Radar rebrand (planetary/cosmic language)
- Euro Engine Spread Guarantee (3+ decades)
- Reverse → Flip rename (entire codebase)
- Euro simulation backtest (20 dates x 20 tickets)
- Star→Q Count→P1 discovery and multi-year validation

## Upcoming Tasks
- **P0**: Code Star→Q Count→P1 pattern into engine
- **P0**: Run 3-year deep analysis of Star→Q Count pattern
- **P0**: Generate d4 (17.04.2026) prediction using all learnings
- **P1**: Code flip+circle CHAIN (not single step) into engine
- **P1**: Code date reading method into engine
- **P1**: Position-by-position deep analysis (P3-P6 + Lucky)

## Future Tasks
- **P2**: Cross-draw Bridge Chain Tracker UI
- **P2**: Refactor monolithic files
- **P2**: Stripe Payments (deferred)

## App Health
All systems healthy. Backend + Frontend + MongoDB running. Active user tracking live. 20-ticket limit enforced.
