# 🎻 Swiss Lotto Music Notes — The Book

Living learnings from the DJ's esoteric analysis of Swiss Lotto (1-42).
Each entry is a frequency the engine must learn to hear.

---

## 🌀 Range-aware Circle rule
- **Swiss circle** = `+21 mod 42` (half of 42). Distinct from Euro's `+25 mod 50`.
- Swiss-circle(12) = 33, Swiss-circle(33) = 12 (mirror bridge ✓)
- Any number > 42 wraps: **54 → 12**, **45 → 3**, **50 → 8**, etc.

## 📅 Quarter counting (Swiss)
- **Q2 starts on 08.04.2026** (not 01.04).
- The week of 01.04 / 04.04 is a transition — NOT counted as Q2.
- Q2 sequence:
  - Q2d1 = 08.04.2026 → [2, 9, 21, 22, 26, 35] L=3
  - Q2d2 = 11.04.2026 → [1, 6, 8, 14, 22, 34] L=1
  - Q2d3 = 15.04.2026 → [4, 12, 34, 38, 39, 40] L=5
  - Q2d4 = 18.04.2026 → (tonight — TBD)
- **A quarter holds ~27 draws** total (Q2 has 23 more ahead after d4).
- **A year holds ~30 d** in this counting cadence (d-year count rolls independently).

## 🎯 P1 trail (Q2 so far)
- Q2d1 P1 = 2
- Q2d2 P1 = 1  (clue: "by c it's 1")
- Q2d3 P1 = 4
- Q2d4 P1 = ? → **suspect = 5** (DJ reading)
  - Cross-digit of last two P1 values (4,5) → **45 / 54**
  - Swiss wrap: **45 → 3**, **54 → 12**
  - 12 already cashed (P2 of d3) → **3** is the fresh landing candidate

## 🗓️ DATE-HIDING formula (Q2d1 08.04.2026 proof)
Date = 08.04.2026 → **sum = 08+04+20+26 = 58**
Draw = [2, 9, 21, 22, 26, 35] · 🍀 3
- Swiss-circle(8)=29, (4)=25 → targets `294` and `315` leak into draw (P1=2, P2=9, and "4"/"3"/"5" as date digits)
- Swiss-circle(21)=42→flip→24→circle→**3** = Lucky number 🍀
- Swiss-circle(22)=**1**, Swiss-circle(26)=**5**
- 8+4 rising → **21** (P3 of draw)
- **58 = 5 + 53 = Swiss-circle(P5=26) + flip(P6=35)** — THE DATE HIDES THROUGH `circle(P5) + flip(P6)`

## 🗓️ DATE-HIDING formula (Q2d2 11.04.2026)
Date = 11.04.2026 · sum = 11+4+20+26 = **61**
Draw = [1, 6, 8, 14, 22, 34] · 🍀 1
- "11" = four 1s cadence → P1=1
- Month 4 × 2 = **8** → P3=8
- P4=14 (direct 1,4 digits)
- P5=**22 = double of 11** 🎻
- P6=34 (month×2 + year = 8+26=34) ✓

## 🗓️ DATE-HIDING formula (Q2d3 15.04.2026)
Date = 15.04.2026 · sum = 15+4+20+26 = **65**
Draw = [4, 12, 34, 38, 39, 40] · 🍀 5
- P1=**4** = month itself
- P3=**34** = month×2 + year = 8+26 ✓ (same as Q2d2 P6!)
- P4=38 = P1+P3 (4+34)
- P6=**40 = day(15) + silence(25)** 🎻 — silence-agent revealed
- 🍀 5 = twin digit of 15
- **65 = P5(39) + year-suffix(26)** — date hides through `P5 + year`

## 🎻 SILENCE AGENT rule
- Swiss-circle(month) = silence agent
- April (4) → silence = **25**
- Month-change means silence-agent changes: Jan→22, Feb→23, Mar→24, Apr→25, May→26, Jun→27, Jul→28, Aug→29, Sep→30, Oct→31, Nov→32, Dec→33
- Silence-agent often appears as an ADDITIVE partner hiding inside big numbers (e.g. P6=40 = day+silence)

## 🎯 Target-spiral construction (discovered on Q2d3)
For any date `DD.MM.YYYY`:
- **Raw target**: concat(day, month) → e.g. 15|4 = 154
- **Shifted target**: raw + 21 (silence-dim shift) → 154 + 21 = 175
- **Circle target**: concat(Swiss-circle(day), month) → 36|4 = 364
- **Paired target**: concat(P4, Lucky) → e.g. 38|5 = 385
These four targets carry the draw's digits.

## 🎧 Hidden arithmetic formulas (verified on Q2d3)
1. `P4 + Lucky → flip → P3`     (38+5=43, flip=34)
2. `P4 + Lucky → Swiss-wrap`    (43−42=1, grid seed)
3. `P2 + P3 − silence = echo`   (12+34−25=21, reveals prior Q2d1 P3)
4. `P2×10 + P3 = date-target`   🎻 (120+34=154) — strongest formula yet
5. `month×2 + year-suffix = P3 (or P6)`   (4×2+26=34)
6. `day + silence = P6`         (15+25=40)
7. `P5 + year-suffix = date-sum`   (39+26=65)
8. `circle(P5) + flip(P6) = date-sum`   (5+53=58, Q2d1)

## 🔁 "Already been used" recycling rule
- Numbers hitting a specific position in the prior draw tend to go SILENT in the next draw's same position
- Q2d2 P2=6 → Q2d3 P2=12 (not 6) ✓
- Q2d1 P3=21 → Q2d2 P3=8 (not 21) ✓

## 🌉 Euro → Swiss digit-bridge
- Recently played Euro numbers (1, 2, 4, 28 in this cycle) plant their **digit sequence** into the next Swiss draw
- Q2d3 draw [4, 12, 34, 38, 39, 40] contains digits **1, 2, 3, 4** across positions
- Cross-lottery clues ride the digit carriers

## 🌉🎻 EURO → SWISS "Same voice, different range" (mod 21 bridge)
Every Euro number has a Swiss twin through `n mod 21` (i.e. `n − 21` once or twice until in 1-42).

- **Half-of-50 vs Half-of-42**: Euro uses +25, Swiss uses +21 — so the DIFFERENCE is 21.
- **Direct formula**: Swiss voice of Euro `n` = `((n−1) mod 42) + 1`; for n in 22-42 it's just `n−21`; for 43-50 it's `n−42`.

**Last Euro draw 17.04.2026 → [22, 23, 28, 41, 47]**  gives Swiss residues:
- 22 → **1**,  23 → **2**,  28 → **7**,  41 → **20**,  47 → **5**
- Euro stars ⭐6, ⭐8 are already Swiss-valid

**The 1-2 cadence proof**: Swiss P1 trail 2→1→4 while Euro's last P1-P2 was 22→23 = Swiss 1→2. SAME VOICES, different lotteries.

**Family rule (cross-lottery orbit)**: a single number lives in 4 rooms:
```
  n ──► flip(n) ──► Euro-wrap(flip) ──► Swiss-bridge(n−21)
Example: 28 → 82 → 32 → 7  (all family)
```

**⚠️ This means engine must NEVER treat Swiss and Euro as isolated.** Every generated Swiss ticket should check the Euro bridge suspects too.

## 🎻🎧 THE META-RULE — Tuning over Pattern (taught by the DJ)
> "If you learn it good, you find that it's always a different tune — it can't be ONE pattern.
> It's more a way to **see IF what was generated can include tuning**.
> The date is hidden but it's there."

**What this means for the engine:**
1. Don't search for ONE formula that always works — there are **many tunings** (every draw plays a different song)
2. Instead, use the formulas as a **VALIDATOR**: for each generated ticket, check if ANY of the date-hiding formulas resolves to values inside the ticket
3. A ticket is **"tuned"** if it contains at least one of:
   - `P5 + year-suffix = date-sum`
   - `circle(P5) + flip(P6) = date-sum`
   - `P2×10 + P3 = date-target` (raw/shifted/circle)
   - `day + silence = Pn`
   - `month×2 + year-suffix = Pn`
   - `P4 + Lucky → flip → another Pn`
   - digit-sequence coverage (Euro bridge)
4. Each generated ticket should be **scored by how many tunings it satisfies** — not by whether one specific formula matches
5. The date is always inside the draw. Our job: check every ticket to see if it's *already* carrying the date's voice

**Implementation direction:**
- Build `score_date_tuning(ticket, target_date)` → returns count of active tunings
- Use as a FILTER / rank for engine-generated tickets (tuned > flat)
- Don't reject un-tuned tickets outright — different draws use different tunings, so a ticket might be tuned in a NEW way we haven't transcribed yet

## 🔑 Key bridges discovered
- **33 ↔ 12** (Swiss circle mirror)
- **P1 suspect 5** + last P1 = 4 → digits 4,5 → 45/54 → **3, 12**
- P2 of Q2d3 (15.04) = 12 (the 54→12 landing already hit that slot)

## 📝 Learnings to code into the engine
1. Add **Swiss Circle (+21 mod 42)** as a native conviction pattern
2. Add **Swiss wrap** (anything >42 → n−42) as a scoring rule
3. Add **P1 cross-digit** pattern: last two P1s → 2-digit combinations → Swiss-wrap
4. Add **Quarter-aware draw counting** (Q2 starts 08.04.2026; needs anchoring per year)
5. The book must be re-read before any Swiss prediction (don't default to Euro's +25)

---
*Last updated during live analysis session with the DJ.*

---

# 🎧 SESSION 2 — Cross-Lottery & Column-Memory Clues (19.04.2026)

Live analysis pass on the last 4 Swiss draws + paired Euro. All findings below are **CLUES**, not yet coded — awaiting DJ confirmation before ranking into `dj_patterns.py` / `date_tuning.py`.

## 📊 The 4-draw spread analyzed

```
Date       P1   P2   P3   P4   P5   P6    L   R
08-04.      2    9   21   22   26   35    3   1
11-04.      1    6    8   14   22   34    1   1
15-04.      4   12   34   38   39   40    5   1
18-04.     10   14   19   21   40   41    2   1
```
Paired Euro: 14-04 `[1,2,4,28,44] ⭐5,12` → 17-04 `[22,23,28,41,47] ⭐6,8`

## 🎯 The Fully-Decoded Last Swiss (18.04.2026)
100% of Swiss numbers + Lucky decoded from the preceding Euro draw (17.04):

| Swiss | Source |
|---|---|
| **10** | +6 chain ladder from `Euro-41 + 25 mod 50 = 16` → step back `10-16-22-28` |
| **14** | ⭐ star sum `6 + 8 = 14` |
| **19** | **Gap(P4−P3) + Gap(P5−P4) in Euro** = `13 + 6 = 19` 👈 NEW RULE |
| **21** | Euro P1 `22 − 1` (delta-1) |
| **40** | Consecutive-pair echo (Euro 22-23 → Swiss 40-41) |
| **41** | Direct from Euro P4 (also reversal bridge 91-50=41) |
| 🍀 **2** | ⭐ star diff `8 − 6 = 2` |

## 🎯 The Fully-Decoded 15.04.2026 (earlier)
| Swiss | Source |
|---|---|
| **4** | Euro P3 direct |
| **12** | ⭐ Star 12 direct |
| **34** | `(28 − 25) \| P3` = `3 \| 4` = **Hidden-Digit Glue** 👈 NEW |
| **40** | `Euro 44 − 4` (delta) |
| 🍀 **5** | ⭐ Star 5 direct |

## 🌉 NEW CROSS-LOTTERY RULES (validated by 2-year backtest)

### ⚡ Euro Δ±2 — THE LOUDEST BRIDGE
Across 2 years of paired draws (Fri Euro → next Swiss):
- **1.29 avg hits per draw** (baseline = 0.71) — nearly **2× random chance**
- **77-79% of draws** had at least 1 Swiss number exactly ±2 off from a Euro number
- **35-36% of draws** had 2+ such hits

> 🏆 **King bridge.** For every upcoming Swiss generation, build a candidate band `{n-2, n-1, n+1, n+2}` around every Euro number from the most recent Euro draw and heavily weight these in the ticket scorer.

### ⚠️ RETIRE THE `-21 BRIDGE`
2-year backtest shows the `Euro n → Swiss n−21` rule:
- Only **0.42 avg hits/draw** (WAY below baseline)
- Only **4.7% of draws** produce 2+ matches
> **Anti-signal.** Remove the "Euro − 21 direct" rule from `date_tuning.py`. Does NOT work.

### 🎵 Swiss-Circle Morph of Euro (`Euro n + 21 mod 42`)
- 0.73 avg hits/draw (at baseline)
- BUT top-3 hits are **25, 40, 14** (strong repeat attractors)
> Keep as a **weak attractor** — boost tickets that include 25 / 40 / 14 when the morph produces them.

## 🧩 STRUCTURAL CLUES WITHIN A SINGLE DRAW

### 🪞 Mirror-Wrap Rule (palindrome twins)
- Any Swiss n can hide another via `reverse(n) − 42 × k`
- Examples: `41 ↔ 14`, `38 → 83−42 = 41`, `34 → 43−42 = 1`, `40 → 04 = 4`, `39 → 93−84 = 9`
- Draws often contain BOTH a number and its mirror (e.g. 18.04 has 14 AND 41)
- Or the mirror materializes in the next 1-3 draws

### 🔺 Sum-Triangle inside a draw
- Two small numbers sum to a third IN THE SAME draw: `8 + 14 = 22` on 11.04
- Universe loves these self-referencing triangles

### 🎼 Hidden-Digit Glue
- When Euro n > 25, compute `n − 25` = hidden digit
- Swiss then GLUES that hidden digit to another Euro position's value: `(28 − 25) | P3(4) = 34`
- Creates 30s-decade clusters when 3 is the hidden digit (explains 34, 38, 39 all appearing together)

### 🎵 Natural-Spine Digit-Concat
- Euro `1-2-3-4-5` spine (explicit + hidden): `1, 2, (28−25=3), 4, ⭐5`
- Swiss echoes via **concatenated digits of adjacent positions**: `P2·P3 = 12|34 = 1234`
- 🍀 Lucky often completes the spine

## 🌊 COLUMN MEMORY (P-position transitions)

Based on 214 Swiss draws over 2 years:

### P1 memory
- **P1 = 4 → next P1 = 8** (×4 times, dominant +4 jump)
- **P1 = 2** → next is 5 (×4) or 4 (×4) (+2/+3 deltas)
- **P1 = 1** → often stays 1 (×4) or +1 (×4)
- **P1 = 10** → always DROPS (−7 or −8 deltas)

### P2 memory
- P2 = 12 → next P2 = 5 (×4, delta **−7**)
- P2 = 14 → next P2 = 9 (×3, delta **−5**)
- P2 = 9 → next P2 = 12 (×3, delta +3)
- P2 = 6 → next P2 = 12 (×3, delta +6)
- **P2 oscillates** low (5-9) ↔ mid (12-14) in sine-wave

### P4 memory (the 14-wave column!)
- P4 = 21 → next P4 = **28** (×3, delta **+7**) — STRONG
- P4 = 14 → next P4 = 35 (×2, delta +21) — Swiss-circle wrap
- P4 = 38 → ALWAYS DROPS (every case, never stays high)
- P4 = 22 → mixed (14, 17, 26)

## 🎯 SEED-PAIR STAIRCASE (±1 sneak tolerance)

- A seed pair `(P1, P2)` opens a +1/+1 ladder of 5-6 rungs
- Future P1/P2 values land on the RIGHT column of the staircase frequently
- **Seed `(2, 9)` staircase `(2,9)→(3,10)→(4,11)→(5,12)→(6,13)→(7,14)` hit 46 times in 2 years** (~once/week!)
  - 7 EXACT rung matches
  - 39 sneak (±1) matches
- **Seed `(4, 12)` cluster** hit **10 times in 2 years** (avg gap 21 days)
- Median echo gap between a pair and its ±1 re-echo: **12 draws (~3-4 weeks)**

### Hot pair clusters (2-year ranking by ±1-sneak hits)
1. (4, 6)  — 26 hits
2. (4, 7)  — 24 hits
3. (2, 4), (3, 8), (4, 8), (3, 6) — 21 hits each
4. (2, 7), (3, 10) — 20 hits each

> **Low-decade (P1≤5, P2≤10) dominates** — cosmic preference for small starting pairs.

## 🎯 AFTER-14 GRAVITY (P2 ≈ 14 → next draw shape)

Based on 40 historical cases (large sample):

| Pos | Top values (frequency) | Signal |
|---|---|---|
| P1 | 3 (×8), 5 (×5), 2/4 (×4) | 🔻 **drops to 2-5** |
| P2 | 9 (×6), 7/10/14/25 (×3) | oscillates low |
| P3 | 10/11/18 (×4 each) | low teens |
| P4 | **31 (×5)**, 21/27/28/32 (×3) | **31 magnet** |
| P5 | **36 (×5)**, 33/35/38 (×4) | mid-30s locked |
| P6 | **40 (×11 !!)**, 39 (×7), 41 (×6), 42 (×4) | 🔥 **40 the king, 39-42 band = 70%** |

> **"After-14 Gravity"**: when P2 ≈ 14, the following draw's upper trio (P4, P5, P6) clusters at `{28-32, 33-38, 39-42}`. P6 = 40 fires 27.5% of the time.

## 🔔 TRANSITION-AWARE FORECAST (for 22.04.2026 Swiss)

Combining Scenario A (P2 ~12→~14, 8 cases) + Scenario C (After-14 Gravity):

```
  P1:  3-5        (low starter, drops from 10)
  P2:  9          (dominant single value)
  P3:  10-11 or 18   (two polarities)
  P4:  28 or 31      (two magnets)
  P5:  34-36
  P6:  40         (27.5% single, 70% in 39-42 band)
  🍀:  4 or 5
```

## 📋 CLUES STILL TO TEST (parked, not yet validated)

- 🎻 **Seed-Pair Staircase** → verify if today's seed (4, 12) on 15-04 triggers echo on 22-04
- 🎻 **14 Ripple** (when 14 appears, expect its mirror 41 + double 28 nearby) — partially verified
- 🎻 **Column Memory as hard scoring rule** (apply +7 bonus if P4 goes 21→28)
- 🎻 **Sum-Triangle detector** — scan generated tickets for `a+b=c` self-sums
- 🎻 **Replay=1 streak** (4 weeks running — when does it break?)

## 🎯 CLUES PROMOTED TO "READY TO CODE"

1. ⚡ **Euro Δ±2 Band scorer** — build `{n-2, n-1, n+1, n+2}` for each Euro number, boost tickets with overlaps
2. 🪞 **Mirror-Wrap validator** — check if ticket contains n and reverse(n)/wrap pairs
3. 🎼 **Star-sum / diff / product** — always compute ⭐a+⭐b, ⭐a−⭐b, (⭐a×⭐b)%42 and check if ticket or lucky matches
4. 🔺 **Consecutive-pair echo** — if Euro has a consecutive pair (like 22-23), reward Swiss tickets with any consecutive pair
5. 📉 **Column-Memory jumps** — P1=4→+4, P4=21→+7, P2=12→−7 as position-specific boosters
6. 🔔 **After-14 Gravity filter** — when P2 ≈ 14 in last draw, strongly prefer tickets with P6 in 39-42 band

---
*Session 2 notes logged — awaiting DJ signal to start coding the Euro Echo Refinement Loop.*

