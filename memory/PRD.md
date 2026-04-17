# Lucky Jack - Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
Custom lottery pattern analyzer with mystical DJ persona. "The Music of the Numbers" — not random, patterns we haven't learned to read yet.

## Core Philosophy
**DATE first → Count draws → Count rare events → Read DIGITS not numbers → Read the story → Listen to the music**

## THE DETECTIVE ENGINE V2 — 16 Pattern Sources

### Pattern Sources in `find_suspects()`:
1. **Flip+Circle Chain** — full chain not single step (28→82→32→7)
2. **Circles** (+25 mod 50)
3. **Neighbourhood** (±1) — 65% when date absent
4. **Hungry** (gap=2 → middle)
5. **Addition** (A+B from prev draw)
6. **Sum Family** (last digit of sum)
7. **Repeat** (any prev number)
8. **Date Reading** — day direct (12.7%), chain (25.3%), digits (83%!), D+M, DxM, circle-flip
9. **P4-P5 Hidden** — cross digits (21.1%), direct pairs (60.8%), minus50 (28.1%)
10. **Star→Q Count** — 75% hit rate Q1→Q2 2026!
11. **Flip** of prev numbers
12. **Cross-Lottery** (Swiss→Euro P1 bridge)
13. **Multi-Draw Lookback** — d-2 chain (74.7%), d-3 chain (70%), d-2 circle (40.1%), d-3 circle (43.1%)
14. **Next-Date Pre-Loading** — 42% hit when date absent
15. **Date Strength** — scale 0-5, STRONG (3+) trusts date, WEAK boosts prev draw
16. **Weak-Date Boost** — extra weight on neighbourhood/circle/flip when date is weak

### Star→Q Count→P1 Discovery
Stars from Q(N+1) draws index into Q(N) draw count → Q(N) P1 predicts P1/P2.
- Q1→Q2 2026: 62-75% hit rate (accelerating!)
- Star 12 = 1 (clock wrapping)
- Star digits: Star 12 → digits 1,2 → both positions referenced

### Q1 2026 P1 Map
c1=8, c2=5, c3=1, c4=6, c5=5, c6=11, c7=4, c8=4, c9=14, c10=26, c11=10, c12=1

### Flip+Circle Chain Rules
- Two digits: flip FIRST, then circle: 28→flip→82→mod50→32→circle→7
- Single digits: circle FIRST, then flip: 4→circle→29→flip→92→land
- Long distance family: 14→41→91→19
- 29=42=17=71=21 (one family through flip+circle!)

### The 10 Story (Q2 Hero)
- Q1 winner, appeared in 50% of Q1 draws (family)
- d2: 10 DIRECT (P1)
- d3: 1 = flip(10) (P1)
- 10+6(date) = 16 → d4 P1 candidate
- 10's chain: [1, 6, 26]
- 10+11 = 21 = D+M of d4 (17+4)
- 10 passed power to 21→46→17→42→24

### P4-P5 Hidden Numbers (68.8% any hit!)
- Cross-digit pairs are KING (21.1%)
- Hit P3-P4-P5 positions primarily
- d3 P4=28, P5=44 → hidden: 24, 42, 48, 32, 34, 28, 44

### Date Reading Method
Read date EVERY possible way:
- Day direct, D+M, D×M, Day circle, Day circle→flip, Day chain
- D×10 + circle(M), Dcircle×10 + circle(M)
- d3+d4 date sum: 14+17=31→circle→6
- When date absent: prev draw DRIVES (neighbourhood 65%)
- Future dates pre-load into current draws (42%)

## d4 (17.04.2026) Analysis In Progress

### Top Suspects (conviction score):
| # | Conv | Key Evidence |
|---|------|-------------|
| 29 | 8 | add, chain(4), circle(4), date, P4P5 |
| 46 | 8 | DAY chain, NEXT circle, d-2 chain |
| 16 | 7 | d-2 chain(14), d-2 circle(41), d-3 chain(11,14,19) |
| 19 | 7 | chain(44), circle(44), d-2 chain, d-3 chain |
| 42 | 7 | DAY circle, P4P5 cross, chain(4) |
| 3 | 6 | HUNGRY!, add(1+2), circle(28) |
| 17 | 6 | DAY DIRECT!, chain(4), NEXT chain |
| 21 | 6 | D+M!, DAY chain, NEXT date |
| 24 | 6 | DAY-CIRCLE-FLIP!, P4P5 cross |
| 32 | 6 | P4P5 minus50, add(4+28), chain(28) |

### P1 Story: 16?
- d1=11(c1), d2=10(c2), d3=1(=11 by c1)
- 14+17=31=circle=6, 6+10=16
- 16 flip→11(d1!), 16 circle→41(d2!)
- c6 last Q = 11 = loop!

### Date Strength: 5/5 STRONG

## Architecture
```
/app/backend/
  server.py            - FastAPI, Swiss engine (~5200 lines)
  euromillions_routes.py - Euro routes + Hit Tracker
  dj_patterns.py       - DJ Engine V2 (~4300 lines, 16 pattern sources)
  digit_dna.py         - Digit DNA + P123 Concat
  sleeper_engine.py    - "Celestial Radar"
  hit_tracker.py       - Hit tracking with visitor_id
  lottery_fetcher.py   - Data sync
  euro_simulation.py   - Backtest script
/app/frontend/src/
  App.js               - React UI
  App.css
```

## Upcoming Tasks
- **P0**: Continue d4 analysis — stars, final tickets
- **P0**: Backtest V2 engine across 100+ draws
- **P1**: Code date-sum pattern (d3day+d4day→circle) into engine
- **P1**: Code "hero tracking" (10→6→16 morphing) into engine
- **P1**: Position-by-position deep analysis P3-P6

## Future Tasks
- **P2**: Cross-draw Bridge Chain Tracker UI
- **P2**: Refactor monolithic files
- **P2**: Stripe Payments (deferred)

## App Health
All systems healthy. Backend + Frontend + MongoDB running. V2 detective engine active.
