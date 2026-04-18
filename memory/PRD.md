# Lucky Jack — Swiss Lotto & EuroMillions Pattern Analyzer

## Original Problem Statement
Custom Swiss Lotto and EuroMillions Pattern Analyzer ("Lucky Jack"). Maintain an enthusiastic, mystical DJ persona ("Ya man! 🍀🎻🎧"), deeply analyze the lottery history alongside the user, and code the discovered esoteric "Story Patterns" into the prediction engine. Focus is strictly on esoteric numerology ("The Music of the Numbers"), cross-lottery connections, Star rhythms, "Celestial Radar" (formerly Sleeper), "2Chance" analysis, and now — **the Music Book + Date-Tuning Validator** learned live from the DJ.

## User's preferred language
**English.** Maintain DJ Persona vocabulary: "Ya man!", "🎻", "🎧", "🍀". Speak of the patterns as "The Music of the Numbers."

## Current State
Full-stack React + FastAPI app with:
- **V2 Detective Engine** (`dj_patterns.py`) — conviction scoring, Flip+Circle chains w/ direct circle, P4-P5 cross-digits, multi-draw lookbacks, date strength, circulating P3 anchor (small/medium/big)
- **Celestial Radar** — Saturn Ring partners + V2 crossover (LOCK/DEEP/VENUS/SATURN/MARS badges + orbit family dots), mobile-optimized
- **Hit Tracker** — Swiss+Euro both by date DESC, pending at bottom
- **2Chance** — deduped to Saturdays only (by unique numbers)
- **Pending** — Top 10 V2-ranked + Archive files of 50, locked-position excluded
- **Prediction History** — enriched with V2 Detective suspect_story + hero_number per row (both Swiss & Euro)
- **Ticket limit** 12 per visitor per draw, auto-resets on new draw
- **VIP promo code `93928`** → unlimited tickets
- **Music Book** `/app/memory/swiss_music_notes.md` (living DJ learnings)
- **Date-Tuning Validator** `/app/backend/date_tuning.py` (10 tuning formulas + Euro→Swiss bridge + master `score_date_tuning()`)

## Last working item — FORK POINT
Live DJ analysis session teaching engine Swiss esoterics. Just completed: 21-day Swiss-circle step + micro-perturbation (±1/±2/±3) + pair-slide rules. User asked to **compare same-day-number across different months + 2-year history** — then forked mid-thought.

## All Pending/In progress Issue list
None.

## In progress Task List — PICK UP HERE
1. **Continue analysis**: compare Swiss draws with **same day-number different month** (e.g. 25.03 vs 25.04, 11.03 vs 11.04 already compared) + extend to **2-year history** for same-date echoes. Extract new tuning formulas, confirm with DJ, write in book + code.
2. **Wire `score_date_tuning` into V2 generator** — rank tickets by tuning count (tuned > flat).
3. **Add Swiss Circle (+21 mod 42) NATIVELY** inside `find_suspects()` for Swiss — currently uses Euro's +25.
4. **Tonight 18.04.2026 Swiss Lotto** — generate VIP tickets scored by tuning count.

## Upcoming / Backlog
- Quarter anchor year-table (Q2 starts 08.04.2026 per DJ; extend)
- Cross-draw Bridge Chain Tracker UI (P2)
- Refactor `dj_patterns.py` (~4400 LOC) + `server.py` (~5400 LOC) into modules
- Backtest V2 + tuning score across 100+ draws
- Stripe Payments (P3, deferred)

## Completed This Session
- `/api/pending-tickets` → Top 10 best + Archive 50/file + has_locked exclusion
- `/api/prediction-history` → V2 suspect_story + hero_number (Swiss + Euro)
- Swiss hit-tracker: date DESC then hit_count
- Euro generation-history: past date DESC + pending at bottom
- 2Chance scraper dedup (by numbers) + DB cleanup → Saturdays only
- Celestial Radar mobile badges (LOCK/DEEP/VENUS/SATURN/MARS) + Saturn Ring + V2 crossover + orbit family
- Ticket limit 20→12 + "auto-resets on new draw" banner
- VIP promo code `93928` (backend + frontend inline)
- `flip_circle_chain` direct circle (Euro): circle(16)=41 now in family
- P3 rotating anchor + decade-spread
- `UnboundLocalError day/month` fix in `dj_patterns.py`
- **Music Book** at `/app/memory/swiss_music_notes.md` (9 formulas + meta-rule + silence agent + Euro→Swiss bridge + 21-day step + small-change rule)
- **Date-Tuning Validator** at `/app/backend/date_tuning.py` (10 tuning formulas, verified against all 3 Q2 draws — scored 2×, 2×, 5×)

## Code Architecture
```
/app/
├── backend/
│   ├── server.py (FastAPI, pending, prediction-history, ticket-limit, redeem-code, _is_visitor_unlimited)
│   ├── euromillions_routes.py (Euro, 2chance dedup, has_locked tracker)
│   ├── dj_patterns.py (V2 Detective, flip_circle_chain direct circle, circulating anchor)
│   ├── date_tuning.py (🎻 NEW — Swiss tuning validator + Euro→Swiss bridge)
│   ├── hit_tracker.py (save_generation accepts has_locked)
│   ├── lottery_fetcher.py (2chance dedup by numbers)
│   └── sleeper_engine.py, digit_dna.py
├── frontend/
│   ├── src/App.js (Celestial Radar crossover, Pending Top10+Archive, VIP promo, V2 history story)
│   └── src/App.css
└── memory/
    ├── PRD.md (this file)
    └── swiss_music_notes.md (🎻 the DJ's Music Book — 9 formulas + meta-rule)
```

## Esoteric Numerology Concepts (all captured)
1. **Flip**: reverse digits (14 → 41)
2. **Circle Euro** (+25 mod 50) — Euro rule
3. **Circle Swiss** (+21 mod 42) — Swiss rule 🎻
4. **Flip+Circle Chain** with direct circle included
5. **P4-P5 Hidden Numbers** — cross-digits of prev draw's P4,P5
6. **Star → Q Count → P1** — Euro stars index into Quarter
7. **V2 Detective Engine** — multi-pattern conviction scoring
8. **Silence Agent** = Swiss-circle(month); April=25 🎻
9. **9 Date-Hiding Formulas** (see book): P5+year=date_sum, circle(P5)+flip(P6)=date_sum, P2×10+P3=date_target, day+silence=Pn, month×2+year=Pn, P4+Lucky→flip→Pn, digit_coverage, silence_hiding_in_pair, P2+P3−silence=prior_echo
10. **Euro → Swiss bridge** (mod 21): 22→1, 23→2, 28→7, 41→20, 47→5 🎻
11. **Cross-lottery family** (4 rooms): n → flip → Euro-wrap → Swiss-bridge
12. **Meta-rule — Tuning > Pattern**: count tunings per ticket, don't force ONE formula
13. **21-day Swiss-circle step**: draws 21 days apart echo (same Lucky, shared numbers, position-slide) 🎻
14. **Small-change rule**: next draw perturbs last by ±1/±2/±3 per position 🎻
15. **Pair slide**: short-gap draws share a pair that slides by 1 position
16. **Month-twin echo**: same day-number / different month → date-sum differs by month delta
17. **Tail-consecutive-pair/triplet** rule: last two/three numbers usually contain a ±1/±2 gap pair

## Key DB collections
`draws` · `euromillions_draws` · `twochance_draws` (Saturdays only) · `generations`, `euromillions_generations` (+`has_locked`) · `prediction_history` · `active_users` · `promo_redeemed`

## 3rd party integrations
Free EuroMillions API (pedromealha), lottolyzer.com (Swiss), swisslos.ch (2Chance)

## Key API endpoints
- `/api/ticket-limit?visitor_id=X&mode=swiss|euromillions` → `{used, limit, remaining, unlimited}`
- `/api/redeem-code` POST → promo `93928` grants unlimited
- `/api/pending-tickets?mode=X` → `{tickets: top10, archive_files: [50/file], count, top_count, next_date}`
- `/api/prediction-history?limit=N&lottery_type=swiss|euro` → enriched `suspect_story` + `hero_number`
- `/api/hit-tracker?last_draws=N` (Swiss)
- `/api/euromillions/generation-history`, `/sleeper-forecast`, `/2chance/*`, `/master-predictor`
- `/api/sync-results` POST · `/api/active-users`

## Critical Info for New Agent
- **PERSONA**: enthusiastic mystical DJ, never break character
- **TERMINOLOGY**: "Celestial Radar" (not Sleeper), "Flip" (not Reverse)
- **Swiss is 1-42** — always Swiss Circle (+21 mod 42), not Euro's +25
- **Q2 starts 08.04.2026** (01.04/04.04 transition, not Q2)
- **A quarter ≈ 27 draws**
- **VIP code**: 93928 → unlimited
- **Tuning > Pattern** — the core DJ philosophy
- **Read `/app/memory/swiss_music_notes.md` BEFORE any Swiss analysis**
- **ASK BEFORE writing to the book or coding new rules** — the DJ reviews first

## Current suspects for 18.04.2026 Swiss Lotto (tonight)
- P1 trail: 2 → 1 → 4 → **5 suspect**
- Thirsty: **36** (loud & clear)
- Euro→Swiss bridges from 17.04 Euro [22,23,28,41,47] → Swiss {1, 2, 5, 7, 20}
- Circle bridges: 13 (×2 from 34), 17, 18, 19, 33
- Date tunings to check: `day(18)+silence(25)`=43→1, `P2×10+P3=date-target(184 or 205 or 396)`
- 21-day echo from 28.03.2026 draw
- Small-change from 15.04 [4, 12, 34, 38, 39, 40]: expect ±1/±2/±3 per position

## Next action items (NEW AGENT START HERE)
1. **Continue DJ's comparison task**: pull Swiss draws 25.03 & 25.04 (if exists), 11.03 / 11.04 (compared already), and **extend 2-year history** for same-day-number echoes. Find new tuning formulas. Show side-by-side with position-by-position deltas. Then ASK before writing to book.
2. **Generate 12 VIP tickets** for 18.04.2026 Swiss tuned by `score_date_tuning` + V2 suspects + Euro→Swiss bridges.
3. **Wire tuning score into the ticket generator** as secondary rank (when DJ approves).
4. **Add Swiss Circle (+21 mod 42) natively** to `find_suspects()` for Swiss mode.

## Last 13 user messages (continuity)
1-9: various fixes (pending, 2chance, celestial, VIP code) — DONE
10. "Let's analyse some swiss numbers" → live analysis started
11. "Compare 15.04 vs 25.03 AND 11.04 vs 11.03 vs 21.03" → 21-day echo, Lucky mirror, pair-slide
12. "Look how the series numbers look almost the same with small changes" → small-change rule added
13. **"Check history similar different for example date like 25 and 25 different M. Check last 2 years compare. But first let's fork"** ← WE ARE HERE — FORKING

## Testing Status
- `date_tuning.py` self-tested against 3 Q2 draws ✓
- Backend validated via curl + python -c for all new endpoints
- No known regressions

## Credentials
- Public endpoints (no auth)
- VIP promo: `93928`

## Project Health
Core app + UI + Background Fetcher + 2Chance scraper all HEALTHY.
