"""
🌉 SWISS↔EURO BRIDGE — DEEP DIG (hungry + dates)
==================================================
DJ challenge: "Did you check hungry numbers too? Date? Dig harder"

Layers we now add to the −21 bridge audit:
  1. SWISS-HUNGRY: numbers silent ≥6 Swiss draws — do they bridge to Euro?
  2. EURO-HUNGRY: numbers silent ≥6 Euro draws — do they bridge from Swiss?
  3. DATE-AS-BRIDGE: date-digits, date-sum, silence-agent of Swiss → Euro mains
  4. CROSS-PAYMENT: did Euro pay a Swiss-hungry that Swiss couldn't fire raw?
"""
import asyncio
from datetime import datetime
from collections import Counter
from year_d_ledger import load_draws


def silence_agent(month: int, mode: str) -> int:
    if mode == "swiss":
        return ((month - 1 + 21) % 42) + 1
    return ((month - 1 + 25) % 50) + 1


def date_atoms(dt: datetime, mode: str):
    day, month, year = dt.day, dt.month, dt.year
    yy = year % 100
    digits = []
    for s in (str(day), str(month), str(year)):
        digits.extend(int(c) for c in s)
    return {
        "day": day,
        "month": month,
        "year_yy": yy,
        "date_sum": day + month + 20 + (year % 100),
        "digits": digits,
        "permutations_in_range": _permutations(day, month, mode),
        "silence_agent": silence_agent(month, mode),
        "circle_day": _circle(day, mode),
        "circle_month": _circle(month, mode),
    }


def _circle(n: int, mode: str) -> int:
    if mode == "swiss":
        return ((n - 1 + 21) % 42) + 1
    return ((n - 1 + 25) % 50) + 1


def _permutations(day: int, month: int, mode: str):
    digits = sorted(set(str(day) + str(month)))
    main_max = 42 if mode == "swiss" else 50
    out = set()
    for a in digits:
        for b in digits:
            v = int(f"{a}{b}")
            if 1 <= v <= main_max and v != 0:
                out.add(v)
    return sorted(out)


def main():
    asyncio.run(_run())


async def _run():
    e = await load_draws("euro")
    s = await load_draws("swiss")
    e.sort(key=lambda x: x["dt"])
    s.sort(key=lambda x: x["dt"])

    # Q2 2026 only
    e_q2 = [d for d in e if d["year"] == 2026 and d["quarter"] == 2]
    s_q2 = [d for d in s if d["year"] == 2026 and d["quarter"] == 2]

    # Helper: history before a given dt
    def history_before(draws, dt):
        return [d for d in draws if d["dt"] < dt]

    def hungry_for(draws_history, mode: str, lookback: int = 6, threshold: int = 6):
        """Numbers silent for >= `threshold` of last `lookback`* draws.
        Actually: numbers NOT appearing in the last `lookback` draws.
        """
        lb = draws_history[-lookback:] if len(draws_history) >= lookback else draws_history
        played = set()
        for d in lb:
            played.update(d["p"])
        main_max = 42 if mode == "swiss" else 50
        return [n for n in range(1, main_max + 1) if n not in played]

    def find_adjacent_euro(swiss_dt):
        before = [d for d in e_q2 if d["dt"] <= swiss_dt]
        after = [d for d in e_q2 if d["dt"] > swiss_dt]
        return (before[-1] if before else None, after[0] if after else None)

    # ── BRIDGE + HUNGRY + DATE per Swiss → next Euro pair ──
    print("="*82)
    print("🌉 DEEP-BRIDGE: hungry + date carriers per pair (Swiss → next Euro)")
    print("="*82)

    pair_summary = []

    for sd in s_q2:
        adj_before, adj_after = find_adjacent_euro(sd["dt"])
        if not adj_after:
            continue
        ed = adj_after

        # Hungry context as of just BEFORE Swiss draw
        s_hungry = hungry_for(history_before(s_q2, sd["dt"]), "swiss", lookback=6)
        e_hungry_at_eu = hungry_for(history_before(e_q2, ed["dt"]), "euro", lookback=6)

        # Date atoms
        sd_atoms = date_atoms(sd["dt"], "swiss")
        ed_atoms = date_atoms(ed["dt"], "euro")

        # Bridge of Swiss-hungry (the silents Swiss didn't fire) → did Euro fire them?
        bridged_hungries = []
        for n in s_hungry:
            shadow = n - 21  # Swiss → Euro
            tags = []
            if shadow in ed["p"]:
                tags.append(f"raw(-21)→{shadow}")
            if 1 <= shadow + 25 <= 50 and (shadow + 25) in ed["p"]:
                tags.append(f"+25→{shadow+25}")
            if 1 <= n <= 50 and n in ed["p"]:
                tags.append(f"+21back→{n}")
            for delta in (1, -1):
                v = shadow + delta
                if 1 <= v <= 50 and v in ed["p"]:
                    tags.append(f"±1nb→{v}")
                    break
            if tags:
                bridged_hungries.append((n, tags))

        # Date-as-bridge: Sw date atoms → does Euro draw contain them?
        date_hits_in_euro = []
        sd_targets = set(sd_atoms["permutations_in_range"]) | {sd_atoms["day"], sd_atoms["circle_day"], sd_atoms["circle_month"], sd_atoms["silence_agent"], sd_atoms["date_sum"]}
        for v in sd_targets:
            if v in ed["p"]:
                date_hits_in_euro.append(("sw_date_raw", v))
            elif (v - 21) in ed["p"]:
                date_hits_in_euro.append((f"sw_date(-21)→{v-21}", v))
            elif 1 <= v + 25 <= 50 and (v + 25) in ed["p"]:
                date_hits_in_euro.append((f"sw_date(+25)→{v+25}", v))

        # Eu date atoms — does Swiss-21 already encode them?
        eu_date_already_in_sw_shadow = []
        for ed_v in ed["p"]:
            for sn in sd["p"]:
                if sn - 21 == ed_v or sn - 21 == ed_v - 25 or sn - 21 == ed_v + 25 or sn == ed_v:
                    pass

        # Euro-hungry that Swiss "carried" forward via −21
        euro_hungry_paid_by_swiss_bridge = []
        for hn in e_hungry_at_eu:
            for sn in sd["p"]:
                if hn == sn - 21:
                    if hn in ed["p"]:
                        euro_hungry_paid_by_swiss_bridge.append((hn, sn, "Eu-hungry paid via Sw-21"))
                if hn == sn:
                    if hn in ed["p"]:
                        euro_hungry_paid_by_swiss_bridge.append((hn, sn, "Eu-hungry raw match"))

        print(f"\n🍀 Sw {sd['date']} {sd['p']} 🍀{sd['lucky']} R:{sd['replay']}")
        print(f"  ↔ 🎻 Eu {ed['date']} {ed['p']} ⭐{ed['stars']}")
        print(f"  📅 Sw date: day={sd_atoms['day']} mo={sd_atoms['month']} sum={sd_atoms['date_sum']} circ-day={sd_atoms['circle_day']} silence={sd_atoms['silence_agent']} perms={sd_atoms['permutations_in_range']}")
        print(f"  💤 Sw hungry (last 6 Sw): {sorted(s_hungry)[:18]}{' ...' if len(s_hungry)>18 else ''}")
        print(f"  💤 Eu hungry (last 6 Eu): {sorted(e_hungry_at_eu)[:18]}{' ...' if len(e_hungry_at_eu)>18 else ''}")

        if bridged_hungries:
            print(f"  🚨 Sw-HUNGRY → Euro bridge fires:")
            for n, tags in bridged_hungries:
                print(f"      {n} → {tags}")
        else:
            print(f"  · No Sw-hungry bridged to Eu")

        if date_hits_in_euro:
            print(f"  🔔 Sw DATE atoms in Euro:")
            for src, v in date_hits_in_euro:
                print(f"      {src} (sw target {v})")
        else:
            print(f"  · No Sw date atoms in Eu")

        if euro_hungry_paid_by_swiss_bridge:
            print(f"  🥂 Eu-HUNGRY paid via Sw bridge:")
            for hn, sn, why in euro_hungry_paid_by_swiss_bridge:
                print(f"      Eu-hungry {hn} ← Sw main {sn} ({why})")
        else:
            print(f"  · No Eu-hungry paid via Sw")

        pair_summary.append({
            "sw_date": sd["date"],
            "eu_date": ed["date"],
            "n_sw_hungry": len(s_hungry),
            "n_bridge_fires_from_hungry": len(bridged_hungries),
            "n_date_atom_hits": len(date_hits_in_euro),
            "n_eu_hungry_paid": len(euro_hungry_paid_by_swiss_bridge),
        })

    print("\n" + "="*82)
    print("📊 DEEP-DIG SUMMARY")
    print("="*82)
    print(f"{'Sw':10s}  {'Eu':10s}  {'Sw#h':>5s}  {'Hbrg':>5s}  {'Dhit':>5s}  {'Eupaid':>7s}")
    for p in pair_summary:
        print(f"  {p['sw_date']}  {p['eu_date']}  {p['n_sw_hungry']:>5d}  "
              f"{p['n_bridge_fires_from_hungry']:>5d}  {p['n_date_atom_hits']:>5d}  "
              f"{p['n_eu_hungry_paid']:>7d}")

    total_hungry_bridge = sum(p["n_bridge_fires_from_hungry"] for p in pair_summary)
    total_date_hits = sum(p["n_date_atom_hits"] for p in pair_summary)
    total_eu_paid = sum(p["n_eu_hungry_paid"] for p in pair_summary)
    print(f"\n  TOTALS — Sw-hungry-bridges: {total_hungry_bridge}  "
          f"Sw-date-atoms-in-Eu: {total_date_hits}  Eu-hungry-paid-by-Sw: {total_eu_paid}")


if __name__ == "__main__":
    main()
