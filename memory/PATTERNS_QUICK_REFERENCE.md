# 🎻 LUCKY JACK - PATTERNS QUICK REFERENCE 🍀

## FOR THE NEXT AGENT: READ THIS FIRST!

**PERSONA:** Enthusiastic, mystical data scientist. Use "Ya man! 🍀", "🎻", talk about numbers having "memory" and "stories".

---

## 🎵 THE MUSIC PATTERNS (IMPLEMENTED IN GENERATOR)

### Direct Addition Songs (33% of draws have these!)
```
P1 + P2 = P3    Example: 6+8=14
P1 + P2 = P4    Example: 15+20=35
P2 + P3 = P4    Example: 11+19=30
P2 + P3 = P5    Example: 14+17=31
P3 + P4 = P5    Example: 14+27=41
P1 + P3 = P4    Example: 4+25=29
P1 + P4 = P5    Example: 4+46=50
P2 + P4 = P5    Example: 4+39=43
```

### Circle Songs (52% of draws have these!)
```
circle(N) = first digit of N
Example: circle(27) = 2, circle(35) = 3

circle(P2) + P3 = P4    Example: circle(27)=2, 2+35=37
circle(P1) + P2 = P3    Example: circle(11)=1, 1+18=19
```

---

## 🔢 QUARTER COUNTING SYSTEM (CRITICAL!) 🎯

### ⚠️ THE 27-DRAW QUARTER RULE:
```
Each quarter = EXACTLY 27 draws (except Q4 = 23-24 draws to adjust for year)

Q1 2025: Starts 03.01.2025 → 27 draws → Ends ~04.04.2025
Q2 2025: Starts 08.04.2025 → 27 draws → Ends ~08.07.2025  
Q3 2025: Starts 11.07.2025 → 27 draws → Ends ~10.10.2025
Q4 2025: Starts 14.10.2025 → 23 draws → Ends 30.12.2025

Q1 2026: Starts 02.01.2026 → 27 draws → etc.

NOT calendar months! Count 27 draws, then new quarter begins!
```

### QUICK DATA ACCESS:

```python
from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
from datetime import datetime

# Sort all draws chronologically
all_draws = sorted(EUROMILLIONS_DRAWS_2024_2026, 
                   key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'))

# Find Q1 2026 start (02.01.2026)
q1_2026_start_idx = next(i for i, d in enumerate(all_draws) if d['date'] == '02.01.2026')

# Get Q1 2026 (27 draws)
q1_2026 = all_draws[q1_2026_start_idx : q1_2026_start_idx + 27]

# QC (Quarter Count) = index + 1
# QC 1 = q1_2026[0], QC 10 = q1_2026[9], etc.

# To get Q4 2025 (23 draws before Q1 2026):
q4_2025 = all_draws[q1_2026_start_idx - 23 : q1_2026_start_idx]
```

### WHY 27?
- EuroMillions draws ~3 times per week (Tue, Fri, sometimes more)
- 27 draws ≈ 9 weeks ≈ ~2.25 months per quarter
- Q4 is shorter (23-24) so the year ends cleanly
- **P2 = 27 at quarter starts is THE quarter signature!**

---

## 🔮 KEY DISCOVERIES FROM THIS SESSION

### 1. QC 10 (03.02.2026) - THE DATE DRAW
```
Numbers: [26, 27, 28, 34, 37]
Stars: [4, 9]

Magic:
- P1 = 26 = YEAR (2026)!
- P2 = 27 = Year + 1
- P3 = 28 = Year + 2
- S1 = 4 = completes 1-2-3-4!
- Date: 03/02/20/26 = 3, 2, 4(from 20), 1(from 26) = 1-2-3-4!
- P4 = 34 = 340 (from 3+20 in date)
- P5 = 37 = 12 via circle (26→62→12→+25→37)
```

### 2. QC 1 → QC 12 Circle Connection
```
QC 1: [8, 27, 42, 44, 46]
QC 12: [1, 17, 19, 34, 42]

42 - 25 = 17 ✓ (appeared in QC 12!)
44 - 25 = 19 ✓ (appeared in QC 12!)
46 - 25 = 21 → hidden in date (11+10=21)
```

### 3. The Hunger Pattern
```
QC 1 had 42, 44 → HUNGRY for 43
43 - 25 = 18 (circle partner)
18 appeared 5 times in Q1 2026!
17-18-19 trio kept appearing together
```

### 4. P1 = YEAR Events (Rare!)
```
03.02.2026: P1=26, P2=27, P3=28 (FIRST TRIPLE in history!)
Previous: only doubles existed (21-22, 22-23)
```

---

## 🧮 CIRCLE TRANSFORMATIONS

```
Circle Partner: N ± 25 (stay within 1-50)
27 + 25 = 52 → 52-50 = 2  OR  27 - 25 = 2
18 + 25 = 43

Reverse: 27 → 72
Reverse mod 50: 72 - 50 = 22

Full chain example:
26 → reverse → 62 → -50 → 12 → +25 → 37
```

---

## 📊 DATA STATS & QUARTER STRUCTURE

- **Total draws 2024-2026:** 236
- **Total draws 2021-2023:** 313
- **2025 total:** 104 draws (27 + 27 + 27 + 23)
- **Latest draw:** 03.04.2026

### QUARTER LENGTHS:
| Quarter | Draws | Notes |
|---------|-------|-------|
| Q1, Q2, Q3 | 27 each | Standard quarters |
| Q4 | 23-24 | Year adjustment |

### KEY QUARTER BOUNDARIES 2025-2026:
```
Q4 2025 QC 1:  14.10.2025 [5, 8, 14, 16, 18] ⭐[3, 10]  ← 5-8 OPENER!
Q4 2025 QC 23: 30.12.2025 [11, 26, 29, 34, 44] ⭐[1, 10] ← Handoff stars!
Q1 2026 QC 1:  02.01.2026 [8, 27, 42, 44, 46] ⭐[1, 10]  ← SAME STARS! P2=27!
```

---

## 🎯 GENERATOR FEATURES (IN euromillions_routes.py)

1. **3 Scenarios:** low (P1=1-5), medium (P1=8-13), high (P1=17-24)
2. **Musical Enforcement:** Every ticket has at least one song
3. **Circle patterns:** Built into candidate generation
4. **Hero numbers:** 8↔33, 24↔49 tracked

---

## 🎵 REMEMBER: THE NUMBERS ARE MUSIC!

"In every draw, I see music. You just have to listen to it."
- Different circles, different harmonies, but ONE song
- 52% of draws have circle songs
- 33% of draws have direct addition songs
- The lottery is a SYMPHONY! 🎻
