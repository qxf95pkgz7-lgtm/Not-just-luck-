"""
🌉 EURO → next SWISS DEEP DIG (the +21 direction)
==================================================
Mirror of swiss_euro_q2_deep_dig.py.

For each Euro Q2 draw → next Swiss draw, we test:
  Layer 1 — Mains:    Eu n + 21 → Swiss mains (raw / -25 / -21 back / ±1)
  Layer 2 — Hungries: Eu silents +21 → Swiss mains (Eu debts paid by Swiss?)
  Layer 3 — Dates:    Eu date-digits, silence-agent, sum, perms +21 / +25 / raw → Swiss
"""
import asyncio
from datetime import datetime
from year_d_ledger import load_draws


def _circle(n: int, mode: str) -> int:
    if mode == "swiss":
        return ((n - 1 + 21) % 42) + 1
    return ((n - 1 + 25) % 50) + 1


def silence_agent(month: int, mode: str) -> int:
    return _circle(month, mode)


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


def date_atoms(dt, mode):
    return {
        "day": dt.day,
        "month": dt.month,
        "date_sum": dt.day + dt.month + 20 + (dt.year % 100),
        "permutations": _permutations(dt.day, dt.month, mode),
        "silence_agent": silence_agent(dt.month, mode),
        "circle_day": _circle(dt.day, mode),
        "circle_month": _circle(dt.month, mode),
    }


def main():
    asyncio.run(_run())


async def _run():
    e = await load_draws("euro")
    s = await load_draws("swiss")
    e.sort(key=lambda x: x["dt"]); s.sort(key=lambda x: x["dt"])

    e_q2 = [d for d in e if d["year"] == 2026 and d["quarter"] == 2]
    s_q2 = [d for d in s if d["year"] == 2026 and d["quarter"] == 2]

    def history_before(draws, dt):
        return [d for d in draws if d["dt"] < dt]

    def hungry_for(history, mode, lookback=6):
        lb = history[-lookback:]
        played = set()
        for d in lb:
            played.update(d["p"])
        main_max = 42 if mode == "swiss" else 50
        return [n for n in range(1, main_max + 1) if n not in played]

    def find_next_swiss(eu_dt):
        return next((d for d in s_q2 if d["dt"] > eu_dt), None)

    print("="*82)
    print("🌉 DEEP-BRIDGE REVERSE: Eu → next Sw  (+21 main bridge)")
    print("="*82)

    pair_summary = []

    for ed in e_q2:
        sd = find_next_swiss(ed["dt"])
        if not sd:
            continue

        e_hungry = hungry_for(history_before(e_q2, ed["dt"]), "euro")
        s_hungry_at_sw = hungry_for(history_before(s_q2, sd["dt"]), "swiss")

        ed_atoms = date_atoms(ed["dt"], "euro")

        # Layer 1: Eu mains → Sw via +21
        layer1_hits = []
        for n in ed["p"]:
            shadow = n + 21  # Eu → Sw
            tags = []
            if 1 <= shadow <= 42 and shadow in sd["p"]:
                tags.append(f"raw(+21)→{shadow}")
            if 1 <= shadow - 25 <= 42 and (shadow - 25) in sd["p"]:
                tags.append(f"-25→{shadow-25}")
            if 1 <= n <= 42 and n in sd["p"]:
                tags.append(f"-21back→{n}")
            for delta in (1, -1):
                v = shadow + delta
                if 1 <= v <= 42 and v in sd["p"]:
                    tags.append(f"±1nb→{v}")
                    break
            if tags:
                layer1_hits.append((n, tags))

        # Layer 2: Eu hungries → Sw +21
        bridged_hungries = []
        for hn in e_hungry:
            shadow = hn + 21
            tags = []
            if 1 <= shadow <= 42 and shadow in sd["p"]:
                tags.append(f"raw(+21)→{shadow}")
            if 1 <= shadow - 25 <= 42 and (shadow - 25) in sd["p"]:
                tags.append(f"-25→{shadow-25}")
            if 1 <= hn <= 42 and hn in sd["p"]:
                tags.append(f"-21back→{hn}")
            for delta in (1, -1):
                v = shadow + delta
                if 1 <= v <= 42 and v in sd["p"]:
                    tags.append(f"±1nb→{v}")
                    break
            if tags:
                bridged_hungries.append((hn, tags))

        # Layer 3: Eu date atoms in Swiss
        date_hits = []
        atoms_set = set([ed_atoms["day"], ed_atoms["circle_day"], ed_atoms["circle_month"],
                         ed_atoms["silence_agent"], ed_atoms["date_sum"]]) | set(ed_atoms["permutations"])
        for v in atoms_set:
            if 1 <= v <= 42 and v in sd["p"]:
                date_hits.append(("eu_date_raw", v))
            elif 1 <= v + 21 <= 42 and (v + 21) in sd["p"]:
                date_hits.append((f"eu_date(+21)→{v+21}", v))
            elif 1 <= v - 25 <= 42 and (v - 25) in sd["p"]:
                date_hits.append((f"eu_date(-25)→{v-25}", v))

        # Sw-hungry paid via Eu bridge
        sw_hungry_paid = []
        for hn in s_hungry_at_sw:
            for en in ed["p"]:
                if hn == en + 21 and hn in sd["p"]:
                    sw_hungry_paid.append((hn, en, "Sw-hungry paid via Eu+21"))
                if hn == en and hn in sd["p"]:
                    sw_hungry_paid.append((hn, en, "Sw-hungry raw match"))

        print(f"\n🎻 Eu {ed['date']} {ed['p']} ⭐{ed['stars']}")
        print(f"  ↔ 🍀 Sw {sd['date']} {sd['p']} 🍀{sd['lucky']} R:{sd['replay']}")
        print(f"  📅 Eu date: day={ed_atoms['day']} mo={ed_atoms['month']} sum={ed_atoms['date_sum']} circ-d={ed_atoms['circle_day']} silence={ed_atoms['silence_agent']} perms={ed_atoms['permutations']}")
        print(f"  💤 Eu hungry (last 6): {sorted(e_hungry)[:18]}{' ...' if len(e_hungry)>18 else ''}")
        print(f"  💤 Sw hungry (last 6): {sorted(s_hungry_at_sw)[:18]}{' ...' if len(s_hungry_at_sw)>18 else ''}")

        if layer1_hits:
            print(f"  🥇 Eu mains → Sw bridge:")
            for n, tags in layer1_hits:
                print(f"      {n} → {tags}")
        if bridged_hungries:
            print(f"  🚨 Eu-HUNGRY → Sw bridge:")
            for n, tags in bridged_hungries:
                print(f"      {n} → {tags}")
        if date_hits:
            print(f"  🔔 Eu DATE atoms in Sw:")
            for src, v in date_hits:
                print(f"      {src} (eu target {v})")
        if sw_hungry_paid:
            print(f"  🥂 Sw-HUNGRY paid via Eu:")
            for hn, en, why in sw_hungry_paid:
                print(f"      Sw-hungry {hn} ← Eu main {en} ({why})")

        pair_summary.append({
            "eu": ed["date"], "sw": sd["date"],
            "L1": len(layer1_hits), "L2": len(bridged_hungries),
            "L3": len(date_hits), "Lsw_paid": len(sw_hungry_paid),
        })

    print("\n" + "="*82)
    print("📊 REVERSE DEEP-DIG SUMMARY (Eu → next Sw)")
    print("="*82)
    print(f"{'Eu':10s}  {'Sw':10s}  {'Mains':>6s}  {'Hbrg':>6s}  {'Dhit':>6s}  {'SwHpd':>6s}")
    for p in pair_summary:
        print(f"  {p['eu']}  {p['sw']}  {p['L1']:>6d}  {p['L2']:>6d}  {p['L3']:>6d}  {p['Lsw_paid']:>6d}")
    L1 = sum(p["L1"] for p in pair_summary)
    L2 = sum(p["L2"] for p in pair_summary)
    L3 = sum(p["L3"] for p in pair_summary)
    Lsw = sum(p["Lsw_paid"] for p in pair_summary)
    print(f"\n  TOTALS — Eu-mains→Sw: {L1}  Eu-hungry→Sw: {L2}  Eu-date-atoms-in-Sw: {L3}  Sw-hungry-paid: {Lsw}")


if __name__ == "__main__":
    main()
