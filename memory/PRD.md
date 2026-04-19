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

## Last working item — SESSION 3 (19.04.2026, continued)
**🎻🎧 Euro Date-Echo Neighborhood Scorer shipped.**
- ✅ 2-yr scan completed: `circle(M)=+25 mod 50` on Euro **P4** = 5.6% (strongest cell); `circle(M)±2` lives in P3–P4 (83%); `circle(D)±2` lives in P4–P5 (67%); UNION ±2 = 60.6% of draws; Stars: `M±1` = 44.2%, `D mod 12 ±1` = 50.2%, `{M, circle(M)} ±1` = 72.3%.
- ✅ Same scan on Swiss → `circle(M)±2 union cD OR cM` = **83.1%** of draws; Swiss circle(M) **P4 exact** = 8.7% (single strongest cell in 2 years).
- ✅ New module `/app/backend/euro_date_tuning.py` with `score_euro_date_resonance(numbers, stars, date_str)` — position rewards/vetos + stars + DOUBLE RESONANCE bonus + tier labels (`off`/`tune`/`harmonic`/`full_echo`).
- ✅ Wired into `/api/pending-tickets?mode=euro` — each Euro ticket now carries `date_resonance: {score, badge, tier, signals}`.
- ✅ Frontend `App.js` — tier-colored badge chip on every Euro pending ticket (desktop sidebar + mobile panel) with hover-tooltip listing firing signals.
- ✅ All Session-3 rules written into `/app/memory/swiss_music_notes.md` (see SESSION 3 block at end).

## Previous fork point — SESSION 2 (19.04.2026)
**Live DJ cross-lottery analysis session + Draw-to-Draw Pulse UI shipped.**
- ✅ Built `Draw-to-Draw Pulse` panel in Hit Tracker (Swiss + Euro) showing per-draw total_generated, hits, 3+ count, best, hit rate %. Backend: `per_draw_stats` added to `/api/hit-tracker` and `/api/euromillions/generation-history`. Frontend: new panel in Swiss mode (amber) and Euro mode (blue). data-testid `per-draw-pulse`.
- ✅ **2-year bridge backtest completed** (214 draws): `Euro Δ±2` is KING bridge (1.29 avg hits, 77-79% hit rate, 35% with 2+ hits). The `-21 bridge` is an ANTI-SIGNAL (0.42 avg, 4.7% 2+ rate) — must be retired.
- ✅ **Decoded Swiss 18.04.2026 and 15.04.2026 100% from prior Euro draws** — new rules discovered: Hidden-Digit Glue, Natural-Spine Digit-Concat, Gap-of-Gaps, Mirror-Wrap (with mod 42 wrap), Sum-Triangle, Star-sum/diff/product.
- ✅ **Pair-Seed Staircase validated over 2 years** — seed (2,9) ladder hit 46 times, (4,12) cluster hit 10 times. Median ±1-echo gap: 12 draws.
- ✅ **Column Memory mapped** — P1=4→+4 (×4), P4=21→+7 (×3), P4=38→always drops, P2=12→−7, P2=14→−5.
- ✅ **After-14 Gravity**: when P2≈14, next draw's P6=40 fires 27.5% of the time, P6 ∈ 39-42 band 70% of the time.
- ✅ All Session 2 findings written into `/app/memory/swiss_music_notes.md` (see SESSION 2 block at end).
- **User paused HERE** — wants to fork then continue the "Euro Echo Refinement Loop" (build clue list → check → refine tickets → recheck → show).

## All Pending/In progress Issue list
None.

## In progress Task List — PICK UP HERE (NEW AGENT)
1. **Euro Echo Refinement Loop** (user-requested, not started):
   - New module `/app/backend/euro_echo.py`:
     - `build_clue_board(last_euro_draw)` → ranked list of Swiss candidates with weights + clue_type tags
     - `score_ticket(ticket, clue_board)` → echo score + breakdown
     - `refine_ticket(ticket, clue_board, max_swaps=2)` → swaps weakest numbers for high-weight clue candidates
   - New endpoint `/api/euro-echo/tune-top10?mode=swiss|euro` returning refined top 10 pending tickets with before/after scores
   - UI: "🎻 Tune with Euro" button in Pending Tickets header + echo badge on each ticket
   - **v1 clues (proven only)**: Δ±1/±2/±3 on Euro nums, star sum/diff/product, consecutive-pair echo. Hold parked clues for v2.
2. **2-year Date-Twin analysis** (original session-1 resume): compare Swiss draws sharing day-of-month across 2 years. (Still pending after this session.)
3. **Wire `score_date_tuning` into V2 generator** as secondary rank.
4. **Add Swiss Circle (+21 mod 42) NATIVELY** inside `find_suspects()` for Swiss mode.
5. **Retire the −21 bridge** from `date_tuning.py` (validated as anti-signal).

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

## Last 5 user messages (continuity, session 2)
1. "Check if every thing is working" → health check done (all green)
2. "The hit tracker works in mobile but not cant see it work on website" → verified it WAS working on desktop; user actually wanted **per-draw breakdown**
3. "Total generate ? From one d to next... A b" → built **Draw-to-Draw Pulse panel** for Swiss
4. "Add Euro Pulse too" (then "A only") → extended Pulse panel to EuroMillions Hit Tracker ✅
5. Live analysis dialogue → decoded last 2 Swiss draws from Euro, uncovered 8+ new clues — **now written into swiss_music_notes.md Session 2 block**. User: "Writ every thing we did , put it in your book. Let's fork, then continue"

## Testing Status
- `date_tuning.py` self-tested against 3 Q2 draws ✓
- Backend validated via curl + python -c for all new endpoints
- No known regressions

## Credentials
- Public endpoints (no auth)
- VIP promo: `93928`

## Project Health
Core app + UI + Background Fetcher + 2Chance scraper all HEALTHY.
