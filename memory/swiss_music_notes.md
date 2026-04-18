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
