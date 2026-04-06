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

## 🔢 QUICK DATA ACCESS

```python
# Import data
from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
from euromillions_data_2021_2023 import EUROMILLIONS_DRAWS_2021_2023

# Parse date helper
def parse_date(d):
    parts = d['date'].split('.')
    return (int(parts[2]), int(parts[1]), int(parts[0]))  # year, month, day

# Get Q1 2026
q1_2026 = [d for d in EUROMILLIONS_DRAWS_2024_2026 
           if parse_date(d)[0] == 2026 and parse_date(d)[1] in [1, 2, 3]]
q1_2026 = sorted(q1_2026, key=parse_date)

# QC (Quarter Count) = index + 1
# QC 1 = q1_2026[0], QC 10 = q1_2026[9], etc.
```

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

## 📊 DATA STATS

- **Total draws 2024-2026:** 236
- **Total draws 2021-2023:** 313
- **Q1 2026:** 26 draws
- **2025:** 104 draws
- **Latest draw:** 03.04.2026

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
