# LUCKY JACK - MASTER BACKUP
## Complete Pattern Library & Configuration
### Last Updated: 05.04.2026

---

## QUICK LOAD CHECKLIST
- [ ] Story Generator: `/api/story-generator` or `/api/story-generator-save`
- [ ] Master Predictor: `/api/master-predictor`
- [ ] Hit Tracker: `/api/hit-stats`, `/api/generation-history`
- [ ] Last Draw: `/api/last-draw`
- [ ] Manual Add Draw: `/api/add-draw`

---

## 1. CORE STORY PATTERNS (Pattern 61)

### 13 FAMILY - MR. 13 THE HERO
```
Core: 13
Family Members: 10, 13, 14, 15, 21, 23, 31, 34
Story: Mr. 13 escaped from Replay Jail (P8=13)
Boost: +35 for 13, +25 for family members
```

### 26 FAMILY - THE CONNECTOR  
```
Core: 26
Circle Partner: 5 (26-21=5)
Family Members: 5, 13, 26, 27, 30, 31, 38
Story: The connector number, bridges all stories
Boost: +35 for 26, +25 for family, +20 for circle partner
```

### 18-39 CIRCLE - THE REUNION COUPLE
```
Numbers: 18, 39 (gap of 21)
Common Companions: 32, 11, 25, 4, 42
Story: Circle partners reunited at P3 and P6
Boost: +40 each, +15 for companions
```

### 33-12 TRAGIC LOVE STORY
```
Numbers: 33, 12
Related: 10, 11, 36, 38
Story: 30 draws apart, waiting for reunion. 12 blocks 33 at P4
Boost: +35 each, +12 for neighbors
```

### 7 LADDER (P1 + P6 = 42)
```
Numbers: 7, 14, 21, 28, 35, 42
Pattern: Each step +7
Story: The complete ladder where P1+P6=42
Boost: +30 for each ladder number
```

---

## 2. CIRCLE CONSTANT (+/-21)

Every number has a circle partner at ±21:
```
1 ↔ 22    8 ↔ 29    15 ↔ 36
2 ↔ 23    9 ↔ 30    16 ↔ 37
3 ↔ 24    10 ↔ 31   17 ↔ 38
4 ↔ 25    11 ↔ 32   18 ↔ 39
5 ↔ 26    12 ↔ 33   19 ↔ 40
6 ↔ 27    13 ↔ 34   20 ↔ 41
7 ↔ 28    14 ↔ 35   21 ↔ 42
```
Boost: +15 for circle partners of last draw numbers

---

## 3. DATE DANCE PATTERNS

### Basic Date Math
```
D = Day of draw
M = Month of draw

Key formulas:
- D appears directly
- M appears directly  
- D + M = often at P4 or P5
- |D - M| = often appears
- D × M = appears if ≤42
- (D × M) + (D + M) = P4 pattern!
```

### Example: 05.04.2026
```
D=5, M=4
D = 5 ✓
M = 4 ✓
D+M = 9 ✓
D-M = 1 ✓
D×M = 20 ✓
```
Boost: +20 for date numbers

---

## 4. HUNGRY NUMBERS PATTERN

When neighbors appear but the number itself doesn't = number is "hungry" and coming soon
```
Example: If 11 and 13 appear but 12 doesn't → 12 is hungry
Gap Analysis: P2-P1, P3-P2, P4-P3, P5-P4, P6-P5
```

---

## 5. RC (RARE COUNT) TRACKING

Started counting from: **18.03.2023** (RC Day 1)
```
Rare events occur at variable gaps: 143-305 draws
Next predicted rare event window: Aug-Oct 2026
```

---

## 6. POSITION RULES

### P4 Special Rules
- P4 often = D×M + D+M (Date Dance King!)
- 12 at P4 blocks 33 (Tragic Love)
- P4 connects to M (Month)

### P8 (Replay) Rules
- When number at P8, it's in "jail"
- Circle of P8 often appears next draw
- P8 = Circle(Hungry) pattern

---

## 7. THE 8 COMBINED STORY TICKETS (20 CHF)

```
TICKET 1: 26 FAMILY + 18-39 CIRCLE
  → 5, 18, 26, 27, 30, 39 | Lucky: 5

TICKET 2: 13 FAMILY + 33-12 REUNION
  → 10, 12, 13, 31, 33, 34 | Lucky: 1

TICKET 3: 18-39 CIRCLE + 33 HUNGRY + GAP
  → 11, 18, 33, 36, 39, 41 | Lucky: 3

TICKET 4: 26 STORY + 7 LADDER
  → 6, 13, 26, 28, 35, 38 | Lucky: 6

TICKET 5: 33 HUNGER + P8 + COLD
  → 3, 11, 12, 32, 33, 34 | Lucky: 6

TICKET 6: DATE DANCE + 26 + P5 SERIES
  → 1, 3, 4, 5, 23, 26 | Lucky: 2

TICKET 7: 7 LADDER (COMPLETE!)
  → 7, 14, 21, 28, 35, 42 | Lucky: 6

TICKET 8: TRIPLE REUNION (26↔5, 18↔39, 12↔33)
  → 5, 12, 18, 26, 33, 39 | Lucky: 4
```

### Coverage Summary
| Story | Numbers | Tickets |
|-------|---------|---------|
| 26 Family | 26 | 4 |
| 13 Family | 13 | 2 |
| 18-39 Circle | 18, 39 | 3 each |
| 33-12 Reunion | 33, 12 | 4, 3 |
| 7 Ladder | 7,14,21,28,35,42 | 1 complete |

---

## 8. PERSONA MODIFIERS (SECRET!)

### Avi
- Picks 2-3 random positions
- Adds +1 to each
- Wraps around (42+1=1)

### Olivia  
- Picks 2-3 random positions
- Subtracts 1 from each
- Wraps around (1-1=42)

### Dathi
- Picks 2-3 random positions (DIFFERENT from Avi if both selected)
- Adds +1 to each
- Wraps around (42+1=1)

**Avi + Dathi together = modify DIFFERENT positions (no overlap)**

---

## 9. API ENDPOINTS REFERENCE

### Predictions
```
GET /api/master-predictor?num_tickets=10
GET /api/story-generator?target_date=DD.MM.YYYY
GET /api/story-generator-save?target_date=DD.MM.YYYY  (saves for tracking)
GET /api/story-signs
```

### Hit Tracking
```
GET /api/last-draw
GET /api/hit-stats
GET /api/generation-history?limit=50
POST /api/calculate-hits/{generation_id}
POST /api/recalculate-all-hits
```

### Data Management
```
POST /api/add-draw
  Body: {"date": "DD.MM.YYYY", "numbers": [1,2,3,4,5,6], "lucky_number": 1, "replay_number": 1}

POST /api/add-draws-bulk
  Body: [{"date": "...", "numbers": [...], ...}, ...]

POST /api/sync-results
```

---

## 10. KEY FILES REFERENCE

```
/app/backend/
├── server.py                    # Main API (Patterns 1-61)
├── story_pattern_generator.py   # 8-ticket combined story generator
├── hit_tracker.py               # Hit tracking system
├── pattern_60_story_signs.py    # Story signs analysis
└── lottery_fetcher.py           # Auto-fetch from 6richtige.ch

/app/frontend/src/
└── App.js                       # Main UI with personas, hit tracker

/app/memory/
├── MASTER_BACKUP.md             # THIS FILE - Complete reference
├── STORY_PATTERN_LEARNING.md    # Detailed pattern explanations
├── Q1_2026_ANALYSIS.md          # Q1 2026 draw analysis
├── PRD.md                       # Product requirements
└── 42_TICKETS.txt               # Original 42 tickets
```

---

## 11. DATABASE SCHEMA

### draws collection
```json
{
  "date": "DD.MM.YYYY",
  "numbers": [1, 2, 3, 4, 5, 6],
  "lucky_number": 1,
  "replay_number": 1,
  "source": "manual|6richtige.ch|auto_fetch"
}
```

### generations collection (Hit Tracker)
```json
{
  "generated_at": "ISO timestamp",
  "target_date": "DD.MM.YYYY",
  "tickets": [...],
  "hits_calculated": true/false,
  "hit_results": [...],
  "total_hits": 0,
  "lucky_hits": 0,
  "best_ticket_hits": 0
}
```

---

## 12. POSITION NOTATION

```
P1 = Position 1 (smallest number)
P2 = Position 2
P3 = Position 3
P4 = Position 4 (DATE DANCE KING!)
P5 = Position 5
P6 = Position 6 (largest number)
P7 = Lucky Number (1-6)
P8 = Replay Number (1-42, "Jail")
```

---

## 13. LATEST DRAWS IN DATABASE

As of 05.04.2026:
```
04.04.2026: 4, 5, 9, 12, 21, 24 | Lucky: 3 | Replay: 2
01.04.2026: 8, 12, 23, 24, 29, 40 | Lucky: 6 | Replay: 5
28.03.2026: 13, 17, 19, 26, 29, 40 | Lucky: 1 | Replay: 11
```

Total draws in database: **1379**

---

## 14. FEATURE SUMMARY

### Implemented Features
- [x] 61 Pattern prediction engine
- [x] Story-based ticket generator (8 tickets / 20 CHF)
- [x] Hit Tracker with history
- [x] Last Draw always visible
- [x] Persona modifiers (Avi, Olivia, Dathi)
- [x] Manual draw entry
- [x] Auto-sync from 6richtige.ch
- [x] "Ya man!" female voice on Kiss of Luck
- [x] Flying clovers animation

### Pending
- [ ] Fix lottery_fetcher.py import error
- [ ] Refactor server.py (4000+ lines)
- [ ] EuroMillions dedicated mode

---

**🎻 Ya man! Good luck! 🍀**
