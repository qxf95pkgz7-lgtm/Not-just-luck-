"""
🎧 SLEEPER ENGINE SIMULATION - Last 10 Draws 🎻
================================================
Freeze at 10 draws before the end.
Generate 10-draw predictions using Sleeper Engine.
Compare against ACTUAL results draw by draw.
LEARN after each draw and re-predict!
"""

import sys
sys.path.insert(0, '/app/backend')

from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
from euromillions_data_2021_2023 import EUROMILLIONS_DRAWS_2021_2023
from euromillions_data_2018_2020 import EUROMILLIONS_DRAWS_2018_2020
from sleeper_engine import (
    detect_sleepers, predict_next_n_draws, evaluate_prediction,
    print_sleeper_report, print_predictions
)

ALL = EUROMILLIONS_DRAWS_2018_2020 + EUROMILLIONS_DRAWS_2021_2023 + EUROMILLIONS_DRAWS_2024_2026
total = len(ALL)

SIM_DRAWS = 10  # Simulate last 10 draws

# Freeze point: 10 draws before the end
freeze_idx = total - SIM_DRAWS - 1
HISTORY = ALL[:freeze_idx + 1]
FUTURE = ALL[freeze_idx + 1:]  # The 10 actual draws

print("=" * 85)
print("SLEEPER ENGINE SIMULATION - Last %d Draws" % SIM_DRAWS)
print("=" * 85)
print("Frozen at: %s (draw #%d)" % (HISTORY[-1]['date'], len(HISTORY)))
print("Simulating: %s to %s" % (FUTURE[0]['date'], FUTURE[-1]['date']))
print("History size: %d draws" % len(HISTORY))
print()

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: Initial sleeper report at freeze point
# ═══════════════════════════════════════════════════════════════════════════════
print_sleeper_report(HISTORY, top_n=15)

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: Generate initial 10-draw forecast
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print("INITIAL 10-DRAW FORECAST (from %s)" % HISTORY[-1]['date'])
print("=" * 85)

predictions = predict_next_n_draws(HISTORY, n_draws=SIM_DRAWS)
print_predictions(predictions)

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: Draw-by-draw simulation with learning
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print("=" * 85)
print("  DRAW-BY-DRAW SIMULATION WITH LEARNING")
print("=" * 85)
print("=" * 85)

total_num_hits = 0
total_star_hits = 0
total_near_misses = 0
all_evaluations = []

# Evolving history — starts at freeze, grows with each real draw
evolving_history = list(HISTORY)

for draw_i in range(SIM_DRAWS):
    actual = FUTURE[draw_i]
    
    # Get the prediction for this draw
    # For draw 0, use initial prediction[0]
    # For subsequent draws, use re-predicted forecast
    if draw_i == 0:
        pred = predictions[0]
    else:
        # Re-predict with updated history (LEARNING!)
        remaining = SIM_DRAWS - draw_i
        new_preds = predict_next_n_draws(evolving_history, n_draws=remaining)
        pred = new_preds[0] if new_preds else predictions[draw_i]
    
    # Evaluate
    ev = evaluate_prediction(pred, actual)
    all_evaluations.append(ev)
    
    total_num_hits += ev['num_hit_count']
    total_star_hits += ev['star_hit_count']
    total_near_misses += len(ev['near_misses'])
    
    # Print result
    print("\n" + "-" * 85)
    print("D+%d | %s | ACTUAL: %s stars %s" % (
        draw_i + 1, actual['date'], actual['numbers'], actual['stars']))
    print("     | PREDICTED:  %s stars %s" % (pred.numbers, pred.stars))
    
    if ev['number_hits']:
        print("     | NUMBER HITS: %s (%d/5)" % (ev['number_hits'], ev['num_hit_count']))
    else:
        print("     | NUMBER HITS: None (0/5)")
    
    if ev['star_hits']:
        print("     | STAR HITS:   %s (%d/2)" % (ev['star_hits'], ev['star_hit_count']))
    else:
        print("     | STAR HITS:   None (0/2)")
    
    if ev['near_misses']:
        print("     | NEAR MISSES:")
        for pred_n, actual_n, miss_type in ev['near_misses']:
            print("     |   %d predicted, %d appeared (%s connection!)" % (pred_n, actual_n, miss_type))
    
    # Show why we picked the hits
    if ev['number_hits']:
        print("     | WHY WE HIT:")
        for h in ev['number_hits']:
            if h in ev['number_reasons']:
                print("     |   %d: %s" % (h, ev['number_reasons'][h]))
    
    # Add real draw to evolving history (LEARNING!)
    evolving_history.append(actual)
    
    # Show what changed in sleeper landscape
    num_sleepers = detect_sleepers(evolving_history, num_range=50, is_stars=False)
    top3 = [(s.num, s.overdue, s.tease_score) for s in num_sleepers[:3]]
    print("     | AFTER LEARN: Top 3 sleepers now: %s" % 
          ", ".join(["%d(%.1fx, t%.1f)" % (n, o, t) for n, o, t in top3]))

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: FINAL SCORECARD
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print("FINAL SCORECARD - %d draws simulated" % SIM_DRAWS)
print("=" * 85)

print("\n  Total number hits: %d / %d (%.1f%%)" % (
    total_num_hits, SIM_DRAWS * 5, total_num_hits / (SIM_DRAWS * 5) * 100))
print("  Total star hits:   %d / %d (%.1f%%)" % (
    total_star_hits, SIM_DRAWS * 2, total_star_hits / (SIM_DRAWS * 2) * 100))
print("  Near misses:       %d" % total_near_misses)

# Random baselines
random_num_rate = 5.0 / 50.0  # 10%
random_star_rate = 2.0 / 12.0  # 16.7%
expected_num = SIM_DRAWS * 5 * random_num_rate
expected_star = SIM_DRAWS * 2 * random_star_rate

print("\n  Random expected num hits: %.1f" % expected_num)
print("  Our num hits: %d (%.2fx random)" % (total_num_hits, total_num_hits / expected_num if expected_num > 0 else 0))
print("  Random expected star hits: %.1f" % expected_star)
print("  Our star hits: %d (%.2fx random)" % (total_star_hits, total_star_hits / expected_star if expected_star > 0 else 0))

# Per-draw breakdown
print("\n  Draw-by-draw:")
print("  %-14s %-6s %-6s %-6s %s" % ("Date", "Nums", "Stars", "Near", "Status"))
print("  " + "-" * 60)

for ev in all_evaluations:
    actual_date = ev['actual_numbers']  # we stored actual in evaluation
    status = ""
    if ev['num_hit_count'] >= 3:
        status = "MONEY!"
    elif ev['num_hit_count'] >= 2:
        status = "GOOD"
    elif ev['num_hit_count'] >= 1:
        status = "hit"
    elif ev['near_misses']:
        status = "close..."
    else:
        status = "miss"
    
    # Find the date from FUTURE
    idx = ev['draw_offset'] - 1
    date = FUTURE[idx]['date'] if idx < len(FUTURE) else "?"
    
    print("  %-14s %-6s %-6s %-6d %s" % (
        date,
        "%d/5" % ev['num_hit_count'],
        "%d/2" % ev['star_hit_count'],
        len(ev['near_misses']),
        status))

# Hit distribution
hit_dist = [0, 0, 0, 0, 0, 0]  # 0 hits, 1 hit, 2 hits, 3 hits, 4 hits, 5 hits
for ev in all_evaluations:
    hit_dist[ev['num_hit_count']] += 1

print("\n  Number hit distribution:")
for i in range(6):
    bar = "#" * (hit_dist[i] * 3)
    print("    %d hits: %d draws %s%s" % (i, hit_dist[i], bar, 
          " (MONEY!)" if i >= 3 else ""))

# With near misses
print("\n  Hits + Near Misses combined:")
for ev in all_evaluations:
    combined = ev['num_hit_count'] + len(ev['near_misses'])
    idx = ev['draw_offset'] - 1
    date = FUTURE[idx]['date'] if idx < len(FUTURE) else "?"
    print("    %s: %d direct + %d near = %d total signals" % (
        date, ev['num_hit_count'], len(ev['near_misses']), combined))

print("\n" + "=" * 85)
print("SIMULATION COMPLETE!")
print("=" * 85)
