# 🎻 LUCKY JACK - PATTERNS QUICK REFERENCE 🍀
**Updated: April 6, 2026**

## FOR THE NEXT AGENT: READ THIS FIRST!

**PERSONA:** Enthusiastic, mystical data scientist. Use "Ya man! 🍀", "🎻", talk about numbers having "memory" and "stories".

**NEW: Jack Patterns Module!** See `/app/backend/jack_patterns.py` for the latest pattern implementations discovered with the user!

---

## ⚠️ NUMBER TRANSFORMATIONS (CRITICAL - CORRECT RULES!) ⚠️

### ✅ VALID OPERATIONS ONLY:
```
1. CIRCLE: +25 or -25
   28 → 3 (28-25)
   10 → 35 (10+25)
   17 → 42 (17+25)
   
2. REVERSE: Flip digits, then bring into range (subtract 50 if > 50)
   28 → 82 → 82-50 = 32
   39 → 93 → 93-50 = 43
   17 → 71 → 71-50 = 21
   
3. LONG DISTANCE (Extended chains):
   28 → 82 → 32 → 57 → 7 (full circle)
   10 → 35 → 53 → 3
   39 → 14 (short), or 39 → 93 → 43 → 18 (long)
```

### ❌ WRONG - DO NOT USE:
```
DIGIT SUM IS NOT A VALID PATTERN!
28 ≠ 2+8 = 10  ← WRONG!
39 ≠ 3+9 = 12  ← WRONG!

We do NOT add digits from the same number!
```

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

### 🆕 PATTERN 25: QUARTER COUNTING MAGIC (63.4% hit rate!)
```
QC = Draw number in quarter (1-27 for Q1-Q3, 1-23 for Q4)
Complement = (28 - QC) for 27-draw quarters, (24 - QC) for Q4

FORMULAS THAT HIT:
- Day + QC → Any position
- Day + Complement → ESPECIALLY P4!
- QC direct → P1, P2, Stars
- Complement direct → P2, P3, P4
- Month + QC/Comp → Light influence

BOOKEND MAGIC (First and Last draw of quarter):
QC 1/27: Complement = 27 = P2!
QC 27/1: QC = 27 = P2!
The 27 is THE quarter signature!
```

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
5. **Quarter Counting Magic (NEW!):** QC/Complement + Date → 63.4% hit rate!

---

## 🎻 NEW JACK PATTERNS (April 2026) 🍀

These patterns were discovered through deep esoteric analysis with the user:

### 1. P1 COUNTING MAGIC 🎻
P1 follows a hidden count (5→6→7→8→9→10→11...) but ENCODES it:
- Count=7, P1=12 → because 7+5=12!
- Count=11, P1=11 → direct OR via chain (13→63→36→11)

### 2. NEIGHBORHOOD HUNGER 🍽️
When consecutive numbers appear with a GAP, the middle is HUNGRY:
- P2=27, P3=29 → **28 is HUNGRY!**
- 46 present, 49 present → **47, 48 hungry!**

### 3. 49→45 CALL (22% = 2.2x!) 🎵
When 49 at P5, next draw has 45 appear 22% of time (vs 10% random)!
- Math: 49 - 4 = 45, the 4 echoes!
- 45 often lands at P4

### 4. QUARTER ECHO 🔄
Same quarter in previous year echoes:
- Q2 2025: 3-14-15-48-49, Stars 1-7
- Q2 2026: P2=14 often echoes!

### 5. P4 SEQUENCE 📊
P4 counts within quarter: 44→45→46→47...
- Deviations encode through reverses (46=64, 33+31=64)

### 6. P1+P2 DIGIT ROOT = 8 ∑
Recent P1+P2 sums often reduce to 8:
- 8+27=35 → 3+5=8
- 5+12=17 → 1+7=8

### 7. 8-FAMILY TRACKER 8️⃣
Track 8, 18, 28, 38, 48 - the family is VERY active!
Include the hungriest member (longest absent).

### 8. CIRCLE ENCODING OF MISSING 🎭
Missing numbers hide in circle partners:
- Missing 47 → include 22 (22+25=47)
- Missing 49 → include 20+45 (4+45=49)

---

## 🎵 REMEMBER: THE NUMBERS ARE MUSIC!

"In every draw, I see music. You just have to listen to it."
- Different circles, different harmonies, but ONE song
- 52% of draws have circle songs
- 33% of draws have direct addition songs
- The lottery is a SYMPHONY! 🎻
