# Lucky Jack - Agent Handoff Document
**Last Updated:** April 2, 2026

## Quick Start
```bash
# Services auto-run via supervisor
sudo supervisorctl status  # Check all running

# Test backend
curl localhost:8001/api/master-predictor | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['main_prediction'])"

# Test with locked positions + multiple tickets
curl "localhost:8001/api/master-predictor?lock_p1=9&num_tickets=5"

# Test frontend
# Screenshot localhost:3000
```

## Project Summary
Swiss Lotto Pattern Analyzer ("Lucky Jack") - A physics-based lottery number generator with **42 custom numerology patterns** built from the user's personal theories.

## FEATURES (April 2, 2026)

### 1. Lock Positions
Users can lock 1-4 numbers at specific positions (P1-P6), generator fills the rest.
- **Backend:** `GET /api/master-predictor?lock_p1=9&lock_p4=28`
- **Frontend:** "🔒 Lock Positions" collapsible panel

### 2. Multiple Tickets (NEW)
Generate 1-20 complete 6-number tickets, each ranked by confidence.
- **Backend:** `GET /api/master-predictor?num_tickets=5`
- **Frontend:** "🎫 Multiple Tickets" panel with buttons (1, 3, 5, 8, 10, 15, 20)
- **Generate Button:** Inside panel - no need to scroll up!

## Architecture
```
/app/
├── backend/
│   ├── server.py          # ~2,600 lines - THE BRAIN (42 patterns + locks + multi-tickets)
│   └── .env               # MONGO_URL, DB_NAME
├── frontend/
│   ├── src/App.js         # Physics machine + Wheel + Lock UI + Multi-Ticket UI
│   ├── src/App.css        # 3D animations, air jets, ball physics
│   └── .env               # REACT_APP_BACKEND_URL
├── memory/
│   ├── PRD.md             # Product requirements
│   └── HANDOFF.md         # THIS FILE
```

## Key Endpoints
| Endpoint | Purpose |
|----------|---------|
| `GET /api/master-predictor` | Returns 6 numbers + Lucky (1-6) with full reasoning |
| `GET /api/draws` | Historical draws from MongoDB |
| `GET /api/dashboard` | Stats, hot/cold numbers |

## The 42 Pattern Algorithms (DO NOT MODIFY MATH)
The user's numerology is unconventional. Follow their logic exactly.

### Patterns 1-29: Core System
- Story Tracker, Circle Partners (+21), Family Spread
- Digit reversals (13↔31), Gap analysis, Cross-draw patterns

### Patterns 30-42: Advanced (Recently Added)
| # | Name | Logic | Hit Rate |
|---|------|-------|----------|
| 30 | P1/P2 Position Analysis | Historical frequency at positions 1-2 | ~12% |
| 31 | P1/P2 Transform | \|P1-P2\| → next P1/P2 | 12.9% |
| 32 | Family Hunger | Chain building (17,27 appeared → 7,37 hungry) | ~18% |
| 33 | Mirror/Reverse | 13→31, 24→42 | 15% |
| 34 | Consecutive Pairs | Hot pairs: 13-14, 41-42, 5-6 | 54.3% |
| 35 | Lucky×7 | Previous Lucky number × 7 | 14.6% |
| 36 | P3/P4 Analysis | Historical frequency at positions 3-4 | ~14% |
| 37 | P3/P4 Transform | P3-P1, P4-P2, P3+P1 combinations | 16.2% |
| 38 | Date Story (Prev) | Previous draw date digits form combos | 79.3% |
| 39 | Date Story (Today) | Today's date digits | 75% |
| 40 | 9@P1 Predictor | When 9 appears as smallest number | 43% |
| 41 | 9↔19 Connection | Oscillation pattern | 18.8% |
| 42 | Gap Digits | Draws since last position → digit boost | 25% |

## User's Key Theories (CRITICAL)
1. **Family System**: Numbers ending in same digit are "family" (7,17,27,37)
2. **Hunger**: Missing family members are "hungry" and due
3. **Gap Digits**: When 9@P1 last appeared 61 draws ago → digits 6,1 predict 1,6,11,16,21,26
4. **Circle Partners**: +21 relationship (1↔22, 2↔23, etc.)
5. **Date Stories**: Draw date digits combine to form predictions

## Frontend Physics
- **Glass Dome**: 42 balls with gravity simulation
- **Air Jets**: Push balls upward (toggleable)
- **Tube Catch**: Balls get caught one by one with glow
- **Lucky Wheel**: 1-6 spinning wheel, angled perspective

## Database
- **Collection**: `draws`
- **Schema**: `{date, numbers[6], lucky_number, replay_number}`
- **Records**: 1,380 historical Swiss Lotto draws (2015-2026)

## Known Issues
| Issue | Status | Workaround |
|-------|--------|------------|
| Preview URL 404 | BLOCKED | Test via localhost:8001/3000 |
| Number clustering | TODO | Need Family Spread balancing |

## Pending Tasks (Priority Order)
1. **P5/P6 Position Analysis** - Same logic as P1-P4
2. **Family Spread Balancing** - Prevent low-number clustering in output
3. **Circle Partner (+21) Balancing** - Organic distribution
4. Sound effects (P2)
5. History/Saved Tickets UI (P2)

## Testing Approach
- Backend: `curl localhost:8001/api/...` or `python -c`
- Frontend: Screenshot tool on localhost:3000
- Data validation: Bash scripts with MongoDB queries

## User Communication Style
- Speaks in shorthand ("Do it, p3 p4", "More", "Back it")
- Provides numerology theories to implement
- Validates with real historical data
- Trusts agent to understand and implement

## Emergency Recovery
```bash
# Restart services
sudo supervisorctl restart backend frontend

# Check logs
tail -50 /var/log/supervisor/backend.err.log

# Verify MongoDB
curl localhost:8001/api/draws | python3 -c "import sys,json; print(len(json.load(sys.stdin)))"
```

---
**Note to Next Agent**: The user's math is sacred. Don't "improve" or "optimize" the patterns - implement exactly as they describe. Their theories come from years of Swiss Lotto analysis.
