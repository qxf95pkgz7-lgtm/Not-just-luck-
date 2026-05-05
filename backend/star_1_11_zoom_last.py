"""
Deep zoom on the LAST ⭐[1, 11] event:
Seed: 20.01.2026 → mains [11, 18, 19, 22, 50] ⭐[1, 11]
ND  : 23.01.2026 → mains [4, 5, 13, 21, 42]  ⭐[3, 10]
ND2 : 27.01.2026 → mains [4, 23, 42, 43, 47] ⭐[3, 9]

Tonight: 05.05.2026 (Q2 d9) — ND of 01.05.2026 ⭐[1,11] event.
"""
from datetime import datetime

SEED_DATE = "20.01.2026"
SEED_MAINS = [11, 18, 19, 22, 50]
SEED_STARS = [1, 11]

ND_DATE = "23.01.2026"
ND_MAINS = [4, 5, 13, 21, 42]
ND_STARS = [3, 10]

ND2_DATE = "27.01.2026"
ND2_MAINS = [4, 23, 42, 43, 47]
ND2_STARS = [3, 9]

print("🎯 SEED 20.01.2026  →  mains", SEED_MAINS, "⭐", SEED_STARS)
print("➡️  ND  23.01.2026  →  mains", ND_MAINS, "⭐", ND_STARS)
print("➡️  ND2 27.01.2026  →  mains", ND2_MAINS, "⭐", ND2_STARS)
print()

# === DATE ANALYSIS ===
print("📅 DATE BRIDGE")
seed_dt = datetime.strptime(SEED_DATE, "%d.%m.%Y")
nd_dt = datetime.strptime(ND_DATE, "%d.%m.%Y")
print(f"   Seed: day={seed_dt.day} month={seed_dt.month} sum={seed_dt.day + seed_dt.month}")
print(f"   ND  : day={nd_dt.day} month={nd_dt.month} sum={nd_dt.day + nd_dt.month}")
print(f"   Gap : {(nd_dt - seed_dt).days} days")
print()

# === STAR ANALYSIS ===
print("⭐ STAR JOURNEY")
print(f"   Seed [1, 11] → ND [3, 10]")
print(f"   star drift: 1→3 (+2),  11→10 (-1)")
print(f"   star sum: 12 → 13 (+1)")
print(f"   1+11=12. ND has 3 (12÷4=3) and 10 (12-2=10)")
print(f"   ND2 [3, 9]: ⭐3 STAYS, 10→9 (-1)")
print(f"   ⭐3 persists in ND AND ND2 — the dominant voice")
print()

# === MAINS BRIDGE ANALYSIS ===
print("🎻 MAINS BRIDGE seed → ND")
print(f"   Seed: {SEED_MAINS}")
print(f"   ND  : {ND_MAINS}")
for s in SEED_MAINS:
    bridges = []
    for n in ND_MAINS:
        if s == n: bridges.append(f"raw")
        if s - n in (1, 2, 3, 7, 14): bridges.append(f"-{s-n}")
        if n - s in (1, 2, 3, 7, 14): bridges.append(f"+{n-s}")
        if s + n == 51: bridges.append(f"51-mirror with {n}")
        if abs(s - n) == 25: bridges.append(f"+25-circle with {n}")
        if str(s)[::-1] == str(n) or str(n)[::-1] == str(s): bridges.append(f"flip→{n}")
        if s % 10 == n % 10: bridges.append(f"family-{n%10} with {n}")
        if (s + 28) % 50 == n or (n + 28) % 50 == s: bridges.append(f"28-mirror with {n}")
    if bridges:
        print(f"   {s:2d} → {bridges[:3]}")
print()

# === DIGIT DECONSTRUCTION ===
print("🔢 DIGIT CLUES (seed → ND)")
seed_digits = []
for n in SEED_MAINS + SEED_STARS:
    seed_digits.extend([int(d) for d in str(n)])
nd_digits = []
for n in ND_MAINS + ND_STARS:
    nd_digits.extend([int(d) for d in str(n)])
from collections import Counter
print(f"   Seed digits: {sorted(seed_digits)} | counts: {dict(Counter(seed_digits))}")
print(f"   ND digits  : {sorted(nd_digits)} | counts: {dict(Counter(nd_digits))}")
shared_digits = set(seed_digits) & set(nd_digits)
print(f"   Shared digits: {sorted(shared_digits)}")
print()

# === DATE-WRITES-DRAW CHECK on ND ===
print("📅 Did the DATE 23.01.2026 write the ND draw?")
print(f"   ND date: 23/01/2026")
print(f"   ND mains: {ND_MAINS}")
print(f"   23 directly? no, but 21=23-2, 13 is reverse of 31 (×11 family?)")
print(f"   ND digits include {sorted(set(nd_digits))} — strong 1,2,3,4 cluster")
print(f"   Dom: digit-2 appears 3×, digit-3 appears 4×, digit-1 appears 5×, digit-4 appears 2×")
print()

# === Tonight's parallels ===
print("🌌 TONIGHT'S MIRROR (05.05.2026 ND of 01.05.2026 ⭐[1,11])")
TONIGHT_DT = datetime.strptime("05.05.2026", "%d.%m.%Y")
SEED_NOW_MAINS = [3, 9, 42, 46, 47]
SEED_NOW_STARS = [1, 11]
NOW_SEED_DT = datetime.strptime("01.05.2026", "%d.%m.%Y")
print(f"   Tonight date: 05.05.2026  day=5 month=5 sum=10")
print(f"   01.05.2026 seed: {SEED_NOW_MAINS} ⭐{SEED_NOW_STARS}")
print(f"   Gap: {(TONIGHT_DT - NOW_SEED_DT).days} days")
print()
print("🪞 MAP THE 20.01-precedent ONTO TONIGHT")
print("   Precedent showed:")
print("   • ⭐3 → louder than baseline, stayed for ND AND ND2")
print("   • ⭐10 in ND, ⭐9 in ND2 (the 9-10 cluster)")
print("   • P1 was 4 (low-door ≤5 ✓)")
print("   • P5 was 42 (42 was IN the seed of tonight's 01.05! magnetism?)")
print("   • mains had 5 (today's day = 5)")
print("   • zero direct carryover from the 20.01 mains")
print()
print("   APPLIED TO TONIGHT:")
print("   • ⭐3 likely persistent (matches DJ's stack)")
print("   • ⭐10 likely companion (NOT ⭐7 like the wider history said)")
print("   • P1 in low door {1,2,3,4,5}")
print("   • Today's day=5, look for 5 or 5-family in mains: 5, 15, 25, 35, 45")
print("   • P5 in 40s zone — consistent with 47-magnet ceiling")
print()

# === Q1 vs Q2 sanity check ===
print("🔬 Q1 v Q2 SANITY: How DIFFERENT was the precedent month from tonight?")
print(f"   Seed 20.01.2026 day-month-sum=21, weekday=Tuesday")
print(f"   Tonight 05.05.2026 day-month-sum=10, weekday=Tuesday")
print(f"   SAME weekday cycle. Q1→Q2 shift but Tuesday-Tuesday rhyme")
