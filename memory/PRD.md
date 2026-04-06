# LUCKY JACK - Product Requirements Document
## Swiss Lotto & EuroMillions Pattern Analyzer
### Version 2.0 - Updated 05.04.2026

---

## OVERVIEW

Lucky Jack is a sophisticated lottery prediction application that uses 61 custom numerology patterns, historical data analysis, and story-based generation to create lottery tickets. The app maintains an enthusiastic, mystical data-scientist persona.

**Live URL:** https://jackpot-analysis-hub.preview.emergentagent.com

---

## IMPLEMENTED FEATURES

### Core Prediction Engine
- [x] 61 Pattern algorithms in master predictor
- [x] Story Pattern Generator (Pattern 61 - Avi Patterns)
- [x] Date Dance calculations
- [x] Circle Partnership (+/-21) tracking
- [x] Hungry Numbers detection
- [x] RC (Rare Count) from 18.03.2023
- [x] 7 Ladder pattern (P1+P6=42)

### Story Families
- [x] 13 Family (Mr. 13 the Hero)
- [x] 26 Family (The Connector)
- [x] 18-39 Circle (Reunion Couple)
- [x] 33-12 Tragic Love Story
- [x] Triple Reunion ticket

### User Interface
- [x] Last Draw always visible at top
- [x] Ball machine animation
- [x] Lucky wheel
- [x] Persona selection (Avi, Olivia, Dathi) - SECRET modifiers
- [x] Olivia's Kiss of Luck with female "Ya man!" voice
- [x] Flying clovers animation
- [x] Hit Tracker section
- [x] Generation history with hit marking
- [x] Multiple tickets generation
- [x] Lock positions feature

### Hit Tracking System
- [x] Save generated tickets
- [x] Compare vs actual draws
- [x] Mark hitting numbers (green highlight)
- [x] Track lucky hits
- [x] Overall statistics dashboard
- [x] Generation history

### Data Management
- [x] 1379 historical Swiss Lotto draws
- [x] Manual draw entry endpoint
- [x] Bulk draw import
- [x] Auto-sync from 6richtige.ch (primary)
- [x] Fallback to lottoland, swisslos.ch

---

## PERSONAS (SECRET FUNCTIONS)

| Name | Display | Secret Function |
|------|---------|-----------------|
| Avi | "Avi" | +1 to 2-3 random positions |
| Olivia | "Olivia" | -1 from 2-3 random positions |
| Dathi | "Dathi" | +1 to 2-3 random positions |

**Rule:** Avi + Dathi can be selected together (different positions)
**Rule:** Olivia is exclusive

---

## API ENDPOINTS

### Predictions
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/master-predictor` | GET | Main predictor with 61 patterns |
| `/api/story-generator` | GET | Story-based 8 tickets |
| `/api/story-generator-save` | GET | Generate + save for tracking |
| `/api/story-signs` | GET | Story signs analysis |

### Hit Tracking
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/last-draw` | GET | Most recent draw |
| `/api/hit-stats` | GET | Overall statistics |
| `/api/generation-history` | GET | All saved generations |
| `/api/calculate-hits/{id}` | POST | Calculate hits for generation |
| `/api/recalculate-all-hits` | POST | Batch recalculate |

### Data Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/add-draw` | POST | Manual draw entry |
| `/api/add-draws-bulk` | POST | Bulk import |
| `/api/sync-results` | POST | Trigger auto-sync |

---

## TECHNICAL STACK

- **Frontend:** React 18, Tailwind CSS, Shadcn/UI
- **Backend:** FastAPI, Python 3.11
- **Database:** MongoDB
- **Voice:** Web Speech Synthesis API

---

## FILE STRUCTURE

```
/app/
├── backend/
│   ├── server.py                 # 4000+ lines, 61 patterns
│   ├── story_pattern_generator.py
│   ├── hit_tracker.py
│   ├── pattern_60_story_signs.py
│   └── lottery_fetcher.py
├── frontend/src/
│   └── App.js
└── memory/
    ├── MASTER_BACKUP.md          # Complete pattern library
    ├── STORY_PATTERN_LEARNING.md
    ├── Q1_2026_ANALYSIS.md
    └── PRD.md
```

---

## PENDING TASKS

### P1 - High Priority
- [ ] Fix lottery_fetcher.py import error
- [ ] Refactor server.py into modules

### P2 - Medium Priority  
- [ ] EuroMillions dedicated mode
- [ ] Compare to Draw UI feature

### P3 - Low Priority
- [ ] Sound effects for ball machine
- [ ] Clean up /app/euromillions/ directory

---

## SESSION CHANGELOG

### 05.04.2026 (Current Session)
- Added permanent "Last Draw" display at top
- Integrated Story Patterns (61) into Master Predictor
- Created Hit Tracker system (save, compare, mark hits)
- Added manual draw entry endpoints
- Changed personas to SECRET (no +1/-1 shown)
- Avi + Dathi can now work together (different positions)
- Changed Olivia's Kiss to green clovers (luck, not love)
- Added female "Ya man! Good luck!" voice
- Added draws: 01.04.2026, 04.04.2026
- Created MASTER_BACKUP.md

### Previous Sessions
- Built 60 pattern prediction engine
- Created story_pattern_generator.py
- Discovered Date Dance, Circle Partners, Hungry Numbers
- Analyzed Q1 2026 draws (1-5)
- Codified 13 Family, 26 Family, 18-39 Circle, 33-12 Love

---

## CONTACTS

**Data Source:** 6richtige.ch (Swiss Lotto results)
**Total Draws:** 1379

---

🎻 Ya man! Good luck! 🍀
