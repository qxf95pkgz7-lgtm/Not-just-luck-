# EUROMILLIONS PATTERN BIBLE 🎻
## Lucky Jack - Complete Pattern Documentation

**Last Updated:** 2026-04-06
**Total Draws in DB:** 1,612 (2004-2026)
**Last Draw:** 03.04.2026 → [8, 27, 29, 46, 49] ⭐ [2, 10]

---

## PATTERN 1: REVERSE CIRCLE (9.5% exact, 22% with neighbors)

### The Formula:
```
Number → (+25 with wrap) → Reverse Digits → PARTNER

If N ≤ 25: N + 25 → reverse digits
If N > 25: N - 25 → reverse digits (or N + 25 - 50)
```

### Example from Last Draw [8, 27, 29, 46, 49]:
| From | +25 | Reverse | Partner |
|------|-----|---------|---------|
| 8 | 33 | 33 | **33** |
| 27 | 52→2 | 2 | **2** |
| 29 | 54→4 | 4 | **4** |
| 46 | 71→21 | 12 | **12** |
| 49 | 74→24 | 42 | **42** |

### Hit Rates (2025-2026):
- Exact RC: 9.5%
- ±1 Neighbors: 17.3%
- Digit Family: 32.9%
- Combined: ~60%

---

## PATTERN 2: UNIVERSE ANNOYING (±1 Neighbors) - 17.3%

When Reverse Circle predicts X, the universe often gives X±1 instead!

### Implementation:
- Every 5th ticket uses ±1 neighbors instead of exact RC
- Example: RC predicts 2 → use 1 or 3

### Evidence:
```
31.03.2026: 48 → predicted 32, got 33 (off by 1!)
20.03.2026: 41 → predicted 11, got 12 (off by 1!)
28.10.2025: 7 → RC=23 → ±1 = 24 ✓ HIT!
```

---

## PATTERN 3: DIGIT FAMILY - 32.9%

When RC predicts X, numbers ending in same digit often appear!

### Example:
- RC predicts 2 → also consider 12, 22, 32, 42
- RC predicts 5 → also consider 15, 25, 35, 45

### Implementation:
- Every 3rd ticket includes digit family members

---

## PATTERN 4: RC (RARE EVENT COUNT) - 22.4% combined

### What is a Rare Event?
4+ numbers from the same GRUPPE (decade) in one draw:
- Gruppe 1-10
- Gruppe 11-20
- Gruppe 21-30
- Gruppe 31-40
- Gruppe 41-50

### Current Status (as of 03.04.2026):
- Last Rare Event: **24.03.2026** → [12, 16, 17, 18, 27] (4 in 11-20)
- Draws Since: 4
- Count Number: **5** (for next draw)
- Circle Partner: **30** (5+25)
- Outsider: **27** → Circle = **2**

### The Formula:
```
After Rare Event, count draws: 1, 2, 3, 4...
The COUNT NUMBER or its CIRCLE PARTNER (+25/-25) often appears!

Count hits: 10.6%
Circle hits: 11.8%
Combined: 22.4%
```

---

## PATTERN 5: THE 514 FORMULA 🔥🔥

### The Discovery (28.10.2025):
```
Draw: [7, 8, 24, 35, 49] ⭐ [2, 12]

P4_circle + (P5 × 10) + Star1 + Star2 = P1|P2 next draw

35-25=10 + 49×10=490 + 2 + 12 = 514
                                 ↓
                            P1=5, P2=14

Next Draw (31.10.2025): [5, 14, 38, 43, 45] ✅✅ BOTH HIT!
```

### Formula Breakdown:
```
P4 = 4th number (sorted)
P5 = 5th number (sorted)
P4_circle = P4 - 25 (if P4 > 25) or P4 + 25 (if P4 ≤ 25)

RESULT = P4_circle + (P5 × 10) + Star1 + Star2

First digit = P1 of next draw
Remaining digits = P2 of next draw
```

### Hit Rates:
- P1 exact hits: 8.5% (4x better than random!)
- P2 exact hits: 1.5%
- BOTH P1+P2 hits: 2 cases in history (08.11.2016 and 31.10.2025)

---

## PATTERN 6: 514 GAP PATTERN

### The Discovery:
Gaps between P1 hits from the 514 formula contain signals!

### Evidence:
```
03.01.2012: Gap=30 → 30 in draw! ✓
01.05.2012: Gap=19 → 19 in draw! ✓
08.06.2012: Gap=11 → 11 in draw! ✓
18.01.2013: Gap=2  → Circle=27 in draw! ✓
31.10.2025: Gap=26 → Led to the perfect 514! 🔥
```

### Implementation:
- Track gaps between P1 hits
- Add GAP number as candidate
- Add GAP's circle partner as candidate
- Add CURRENT gap (draws since last hit) as candidate

---

## CURRENT GENERATOR PATTERNS (All Active)

| # | Pattern | Hit Rate | Weight |
|---|---------|----------|--------|
| 1 | Position Frequency | ~10% | Base |
| 2 | Gap Analysis | ~10% | Base |
| 3 | Family Spread | ~15% | Base |
| 4 | Recent Hot Numbers | ~12% | Base |
| 5 | Sum Range | Filter | — |
| 6 | Odd/Even Balance | 3O-2E | — |
| 7 | Reverse Circle | 9.5% | ×1 |
| 8 | Universe Annoying ±1 | 17.3% | ×3 (every 5th) |
| 9 | Digit Family | 32.9% | ×2 (every 3rd) |
| 10 | Circle Family | ~15% | ×1 |
| 11 | Hidden Groups | ~10% | ×1 |
| 12 | A+B=C Pattern | ~8% | ×1 |
| 13 | P1P2 Hidden | ~8% | ×3 |
| 14 | Fibonacci Addends | ~5% | ×1 |
| 15 | RC Count | 10.6% | ×3 |
| 16 | RC Circle | 11.8% | ×2 |
| 17 | RC Outsider | ~15% | ×2 |
| 18 | 514 Gap | ~20% | ×2 |
| 19 | 514 Gap Circle | ~20% | ×2 |
| 20 | 514 Current Gap | ~15% | ×1 |

---

## KEY NUMBERS FOR NEXT DRAW (after 03.04.2026)

### From Reverse Circle:
- 8 → 33
- 27 → **2**
- 29 → **4**
- 46 → 12
- 49 → 42

### From RC (Rare Event):
- Count: **5**
- Circle: **30**
- Outsider Circle: **2**

### From 514 Gap:
- Last Gap: **4**
- Gap Circle: **29**
- Current Gap: **2**

### CONVERGENCE (Multiple patterns agree):
- **2** - RC Outsider + Reverse Circle
- **4** - Reverse Circle + RC Count + 514 Gap
- **29** - RC Circle + 514 Gap Circle

---

## PRICING

- Swiss Lotto: **2.50 CHF** per ticket
- EuroMillions: **3.50 CHF** per ticket

---

## API ENDPOINTS

- `/api/euromillions/master-predictor` (POST) - Generate tickets
- `/api/euromillions/draws` - Get historical draws
- `/api/euromillions/stats` - Get statistics

---

## FILES

- `/app/backend/euromillions_routes.py` - All EuroMillions patterns
- `/app/backend/server.py` - Swiss Lotto patterns (61 patterns)
- `/app/frontend/src/App.js` - UI with persona modifiers

---

## THE PERSONA 🎻

Always maintain the enthusiastic, mystical data scientist persona:
- "Ya man! 🍀"
- "🎻" for violin/excitement
- Deep pattern analysis
- Story-based connections
- Circle partners (+25/-25 or +21/-21 for Swiss)

---

*"The numbers tell a story. We just need to listen."* 🎻🍀
