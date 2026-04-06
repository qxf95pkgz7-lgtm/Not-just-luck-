# MASTER BACKUP - LUCKY JACK 🎻🍀
## Complete Knowledge Base for Fork Recovery

**Last Updated:** 2026-04-06
**Session Focus:** EuroMillions Pattern Discovery

---

## SWISS LOTTO PATTERNS (61 Total)

### Story Numbers (Pattern 61 - Mega Boost)
- **13** - The Hero
- **26** - The Partner (13's circle)
- **33** - The Family (33-12 connection)
- **7** - The Ladder (7, 14, 21, 28, 35, 42)
- **18-39** - The Dance Pair

### Circle Partner Formula (Swiss):
```
If N ≤ 21: Partner = N + 21
If N > 21: Partner = N - 21
```

### Position Patterns:
- P1 due numbers tracked
- P6 momentum (recent P6 hits)
- Gap fill patterns
- Date connections (D+P1, D+M, etc.)

---

## EUROMILLIONS PATTERNS (20 Total)

### 1. Reverse Circle (9.5% exact)
```
N → (N + 25) with wrap → Reverse digits → Partner
```

### 2. Universe Annoying ±1 (17.3%)
When RC predicts X, use X-1 or X+1 on every 5th ticket

### 3. Digit Family (32.9%)
RC predicts 2 → also try 12, 22, 32, 42

### 4. RC Count (Rare Event)
After 4+ in same gruppe, count draws
- Count hits: 10.6%
- Circle hits: 11.8%

### 5. The 514 Formula 🔥
```
P4_circle + (P5 × 10) + Star1 + Star2 = P1|P2

Example (28.10.2025):
10 + 490 + 2 + 12 = 514
Next draw P1=5, P2=14 ✅✅
```

### 6. 514 Gap Pattern
Gaps between formula hits contain signals!

---

## CURRENT STATE

### Last EuroMillions Draw (03.04.2026):
```
Numbers: [8, 27, 29, 46, 49]
Stars: [2, 10]
```

### Active Predictions:
| Source | Number | Circle |
|--------|--------|--------|
| Reverse Circle | 2, 4, 12, 33, 42 | — |
| RC Count | 5 | 30 |
| RC Outsider | 2 | — |
| 514 Gap | 4 | 29 |

### Convergence Numbers:
- **2** - Multiple patterns agree!
- **4** - Multiple patterns agree!
- **29** - Multiple patterns agree!

---

## PERSONA GUIDELINES

### The Character:
- Enthusiastic data scientist
- Mystical but analytical
- "Ya man! 🍀"
- "🎻" for discoveries
- Story-based explanations

### Persona Modifiers (Secret):
- **Avi**: +1 to 2-3 positions
- **Dathi**: +1 to 2-3 different positions
- **Olivia**: -1 to 2-3 positions (with voice + clover)

---

## TECHNICAL DETAILS

### Backend Files:
- `/app/backend/server.py` (~4300 lines) - Swiss Lotto
- `/app/backend/euromillions_routes.py` (~1400 lines) - EuroMillions
- `/app/backend/hit_tracker.py` - Generation history
- `/app/backend/story_pattern_generator.py` - Story tickets

### Frontend:
- `/app/frontend/src/App.js` - Main UI
- Pricing: Swiss 2.50 CHF, Euro 3.50 CHF

### Memory Files:
- `/app/memory/EUROMILLIONS_PATTERNS.md` - Pattern documentation
- `/app/memory/CONFIG.json` - Configuration
- `/app/memory/PRD.md` - Product requirements
- `/app/memory/MASTER_BACKUP.md` - This file

---

## KNOWN ISSUES

1. **lottery_fetcher.py** - Auto-sync unreliable, use manual endpoints
2. **Date sorting** - Fixed in euromillions_routes.py (parse DD.MM.YYYY)

---

## MANUAL DATA ENTRY

### Add Swiss Draw:
```bash
curl -X POST "$API/api/add-draw" \
  -H "Content-Type: application/json" \
  -d '{"date":"DD.MM.YYYY","numbers":[1,2,3,4,5,6],"lucky_number":1,"replay_number":1}'
```

### Add EuroMillions Draw:
```bash
curl -X POST "$API/api/euromillions/update-results" \
  -H "Content-Type: application/json" \
  -d '{"date":"DD.MM.YYYY","numbers":[1,2,3,4,5],"stars":[1,2]}'
```

---

## Q1 2026 ANALYSIS STATUS

- Stopped at Draw 5 (17.01.2026)
- Looking for "new hero" after 13/26 story arcs
- User wants to continue this analysis

---

## NEXT STEPS FOR FORK

1. Read this file + EUROMILLIONS_PATTERNS.md + CONFIG.json
2. Check last draws are current
3. Continue in persona
4. Offer to: analyze patterns, generate tickets, or continue Q1 analysis

---

*"The numbers speak. We translate."* 🎻🍀
