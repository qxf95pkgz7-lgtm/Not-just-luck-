# Lucky Jack - Product Requirements Document

## Overview
Swiss Lotto and EuroMillions Pattern Analyzer featuring custom numerology patterns, progressive generation, and embedded historical draws.

**Last Updated:** 2026-04-06

---

## Core Features

### 1. Swiss Lotto Generator
- 61 custom numerology patterns
- Story Numbers Mega Boost (Pattern 61)
- Circle partner calculations (+/-21)
- Hit tracker dashboard
- Persona modifiers (Avi, Dathi, Olivia)

### 2. EuroMillions Generator
- 20 custom patterns including:
  - Reverse Circle (9.5%)
  - Universe Annoying ±1 (17.3%)
  - Digit Family (32.9%)
  - RC (Rare Event) Count
  - 514 Formula
  - 514 Gap Pattern
- Circle partner calculations (+/-25)

### 3. Data Management
- 1,379 Swiss Lotto draws (2004-2026)
- 1,612 EuroMillions draws (2004-2026)
- Manual draw upload endpoints
- Hit tracking and statistics

---

## Completed Features (This Session)

### EuroMillions Patterns Added:
- [x] Fixed date sorting (DD.MM.YYYY parsing)
- [x] Reverse Circle pattern
- [x] Universe Annoying ±1 pattern
- [x] Digit Family pattern
- [x] RC Count pattern
- [x] RC Circle pattern
- [x] RC Outsider pattern
- [x] 514 Formula pattern
- [x] 514 Gap pattern
- [x] 514 Current Gap pattern

### Pricing Update:
- [x] Swiss Lotto: 2.50 CHF per ticket
- [x] EuroMillions: 3.50 CHF per ticket

### Documentation:
- [x] EUROMILLIONS_PATTERNS.md created
- [x] CONFIG.json updated
- [x] MASTER_BACKUP.md updated

---

## Pending Items

### P0 (Critical):
- [ ] Continue Q1 2026 Analysis (Find "new hero")

### P1 (Important):
- [ ] Fix lottery_fetcher.py auto-sync
- [ ] Refactor server.py (extract 61 patterns to separate module)

### P2 (Nice to have):
- [ ] Wire hit stats into predictor weights
- [ ] Dedicated EuroMillions UI improvements
- [ ] Add "Last Draw" display for EuroMillions (like Swiss)

### P3 (Backlog):
- [ ] Clean up /app/euromillions/ abandoned directory

---

## Technical Architecture

```
/app/
├── backend/
│   ├── server.py           # Swiss Lotto (61 patterns, ~4300 lines)
│   ├── euromillions_routes.py  # EuroMillions (20 patterns, ~1400 lines)
│   ├── hit_tracker.py      # Generation history
│   ├── story_pattern_generator.py  # Story tickets
│   └── lottery_fetcher.py  # Auto-sync (broken)
├── frontend/
│   └── src/App.js          # Main UI
└── memory/
    ├── PRD.md              # This file
    ├── MASTER_BACKUP.md    # Complete knowledge base
    ├── EUROMILLIONS_PATTERNS.md  # Pattern documentation
    └── CONFIG.json         # Configuration
```

---

## API Endpoints

### Swiss Lotto:
- `GET /api/master-predictor` - Generate tickets
- `GET /api/last-draw` - Get last draw
- `POST /api/add-draw` - Manual add
- `GET /api/hit-stats` - Hit statistics

### EuroMillions:
- `POST /api/euromillions/master-predictor` - Generate tickets
- `GET /api/euromillions/draws` - Get draws
- `POST /api/euromillions/update-results` - Manual add

---

## Key Formulas

### Swiss Circle Partner:
```
N ≤ 21: Partner = N + 21
N > 21: Partner = N - 21
```

### EuroMillions Reverse Circle:
```
N → (N + 25 with wrap) → Reverse digits → Partner
```

### 514 Formula:
```
P4_circle + (P5 × 10) + Star1 + Star2 = P1|P2 next draw
```

---

## User Persona

The app maintains an enthusiastic, mystical data scientist character:
- "Ya man! 🍀"
- Deep pattern analysis
- Story-based explanations
- Circle partner connections

---

## Session History

### 2026-04-06:
- Discovered 514 Formula
- Added 6 new EuroMillions patterns
- Fixed pricing (Swiss 2.50, Euro 3.50)
- Analyzed RC patterns across 1612 draws
- Created comprehensive backups

---

*Document maintained for fork continuity*
