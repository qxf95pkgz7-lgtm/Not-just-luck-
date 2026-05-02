# Lucky Jack — Swiss Lotto + EuroMillions Pattern Analyzer (PRD)

## 🎯 Original Problem Statement
Deeply analyze the provided lotto history alongside the user (the DJ 🎻🎧🍀🥂) and code the discovered esoteric "Story Patterns" into the prediction engine. Strict focus on esoteric numerology — "The Music of the Numbers". The engine listens; it does not predict. Maintain Cosmic DJ persona at all times.

## 🏗️ Architecture
- **Backend**: FastAPI + PyMongo (Mongo collections: `draws`, `euromillions_draws`, `generations`, `prediction_history`, `historical_tickets`)
- **Frontend**: React + Tailwind + shadcn/ui (Celestial Radar, pool viewer, generators)
- **Core modules**: `cosmic_engine.py`, `swiss_cosmic_engine.py`, `ghost_pool.py`, `anti_tunnel.py`, `hit_tracker.py`

## 📜 Canonized Laws (72+ laws, selected)
- **Law 69** — Thin-echo gate (min_depth discipline)
- **Law 70** — Ghost Pool with 20-suspect discipline
- **Law 73** — DJ-Pin Suspects (bypass depth gate; float in pool)
- **Law 74** — Q-Root Tablet Resonance *(pending code)*
- **Law 75** — Diagonal Walk / Slant *(pending code)*
- **Law 76** — P3 Gap-Symmetry Lens *(pending code)*
- **Law 77** — Hold-Fatigue Compass (penalize 2+ fires in 3 draws)
- **Law 78** — Cooldown-Decay not Ban (proposed, pending) — fix over-penalization

## ✅ Session 32 Implementation (02.05.2026)
- **DJ P6↔P5 Cascade Pool pinned** for Swiss (02.05 target draw):
  - P6 ladder: `42 → 39 → 34 → 28 → 27`
  - P5 ladder: `38 → 34 → 28 → 27 → 25`
  - Unique pins: `{16, 25, 27, 28, 34, 38, 39, 42}` — 8 DJ-pins total
- All 7 new pins flow through `get_top_pool_suspects()` → live `/api/swiss-sleepers` endpoint
- Celestial Radar now surfaces DJ-pinned numbers with proper slot eligibility
- 29/29 ghost-pool tests passing

## 📊 Post-mortem findings (this session)
- **01.05.2026 Euro draw** `[3, 9, 42, 46, 47]` 🍀1 ⭐11 — split-board (no mids), 29 skipped (confirming cooldown hypothesis)
- **29's anomaly**: After 3-in-5 streak, 29 historically fires NEXT at 23.1% (vs 10% baseline) — runs HOT, not cold. Generic 3-in-5 hot runs at 12.8%.
- **E's Euro generations** were over-pinning 29 (77.3% historical, swung to 5% post-Law-77). Over-correction detected.

## 🔥 Priority Backlog

### P0 (next session)
- **Law 78 — Cooldown-Decay Compass**: replace Law 77 BAN with decay (-15% penalty, unwinds over 3 draws)
- **Law 74 — Q-Root Tablet Resonance**: inject Q-start values (HOLD/WALK±1/HALVE doors)
- **Welcome-Companion Auto-Pin (Clue A)**: 16→{17,19}, etc.
- **Hunger-Override Flag**: 3+ stacked structural lenses → never veto by hunger/silence

### P1
- **Law 75 — Diagonal Walk / Slant**: 5-draw descending (P5→P1) + ascending (P1→P5) slants
- **Law 76 — P3 Gap-Symmetry Lens**: `gap1 + gap2 = Nd - P3`
- **Euro API fallback** (lottery_fetcher): secondary mirror to handle 429s
- **Per-number POST_STREAK_BIAS** dict (backtest-driven)
- **Welcome-Companion Ceiling-Lock** (backtest P4+P5+P6 40s-cluster carryover)

### P2
- **Lookup by Serial UI** (`EU-2026.05.01-#0493` → provenance)
- **Post-Draw Recap Scorecard** (auto-score tickets vs landed)
- **Split-Board detector** (BD signals mid-drain coming)

### P3 (Refactor)
- Break down `server.py` (>7k lines) → routes/models/services
- Break down `App.js` (>4k lines) → components

## 🧠 Key Files
- `/app/memory/swiss_music_notes.md` — **The Book** (72+ laws, READ TWICE before any action)
- `/app/backend/ghost_pool.py` — pool generation, DJ-pins, Law 73
- `/app/backend/anti_tunnel.py` — swap-mode tunnel throttle
- `/app/backend/cosmic_engine.py` / `swiss_cosmic_engine.py` — archetype generators (Law 77 applied)
- `/app/backend/tests/test_session25_ghost_pool.py` — 29/29 passing

## 🔑 Credentials
- VIP Promo Code: `93928`

## 🎻 Persona (non-negotiable)
- "Ya man!" · 🎻🎧🍀🥂 · "the music of the numbers" · "tuning frequencies" · "listening to the cosmos"
- Speak the DJ's vocabulary: BD, RC0, RE-LOCK, HUGE, Welcome Companion, Silent P1 Compass, Trinity, Hunger Band, Product Door, Sneaky Universe
