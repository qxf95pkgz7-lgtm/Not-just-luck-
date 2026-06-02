"""
🪞 Mirror-Date → Sister-d Canon (Session 45 — DJ teaching)

CANON: For any mirror date (day∈{year-suffix, flip(year-suffix), palindrome}),
       the COMPARISON draw is at d-position = digit_sum(day) of the SAME quarter.

       Optional Q-mirror anchor: day + year-suffix = secondary d-position.

Proof:
  23.05.2023 mirror (day=23 == year-suffix 23) → digit_sum(23)=5 → Q2 d5 = 21.04.2023 ✓
  02.06.2020 (day=02, year=20, flip-mirror) → digit_sum(02)=2 → Q2 d2 = ???
  02.06.2026 (day=02, year=26, "2-26") → digit_sum(02)=2 → Q2 d2 = ???

For tonight: BD 29.05.2026 [5,14,18,31,35] ⭐(2,12) → see what Q2-2026 d2 sings.
"""

import asyncio
import os
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ENV = {}
for line in (Path(__file__).parent / ".env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    ENV[k.strip()] = v.strip().strip('"').strip("'")
os.environ.setdefault("MONGO_URL", ENV["MONGO_URL"])
os.environ.setdefault("DB_NAME", ENV["DB_NAME"])

from motor.motor_asyncio import AsyncIOMotorClient


def parse_date(s):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None


def q_for(dt):
    return (dt.month - 1) // 3 + 1


def is_mirror(dt):
    """Return True + tag if date is a mirror."""
    day = dt.day
    ys = dt.year % 100
    flip_ys = int(f"{ys:02d}"[::-1])
    flip_day = int(f"{day:02d}"[::-1])
    palindrome = f"{day:02d}{dt.month:02d}{dt.year:04d}"
    if day == ys:
        return ("M1", f"day=={ys}=year-suffix")
    if day == flip_ys:
        return ("M2", f"day={day}==flip(year)={flip_ys}")
    if flip_day == ys:
        return ("M3", f"flip(day)={flip_day}==year-suffix={ys}")
    if palindrome == palindrome[::-1]:
        return ("M7", "full palindrome")
    return None


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    docs = await db.euromillions_draws.find({}).to_list(length=None)

    rows = []
    for d in docs:
        ds = d.get("date") or d.get("draw_date")
        dt = parse_date(ds) if ds else None
        if not dt:
            continue
        rows.append({
            "dt": dt,
            "mains": list(d.get("mains") or d.get("numbers") or []),
            "stars": list(d.get("stars") or d.get("lucky_stars") or []),
        })
    rows.sort(key=lambda r: r["dt"])

    # Build q-d index: (year, q) → ordered list of (d_index, row)
    qd_index = defaultdict(list)
    for r in rows:
        qd_index[(r["dt"].year, q_for(r["dt"]))].append(r)
    for key in qd_index:
        qd_index[key].sort(key=lambda r: r["dt"])

    def get_dn(year, q, d):
        bucket = qd_index.get((year, q), [])
        if 1 <= d <= len(bucket):
            return bucket[d - 1]
        return None

    def qd_of(dt):
        bucket = qd_index.get((dt.year, q_for(dt)), [])
        for i, r in enumerate(bucket, start=1):
            if r["dt"].date() == dt.date():
                return i
        return None

    print("=" * 90)
    print("🪞 STRONG-MIRROR Euro draws + their digit_sum-d SISTER (same quarter)")
    print("=" * 90)
    print(f"{'date':<12} {'qd':<6} {'tag':<8} {'mains→':<25} {'⭐':<10}"
          f"   ‖   {'sis-d':<6} {'sis-date':<12} {'sis-mains':<25} {'sis-⭐':<10}")
    print("-" * 130)

    pairs = []
    for r in rows:
        m = is_mirror(r["dt"])
        if not m:
            continue
        code, desc = m
        d_mirror = qd_of(r["dt"])
        if d_mirror is None:
            continue
        ds_d = sum(int(c) for c in f"{r['dt'].day:02d}")
        sister = get_dn(r["dt"].year, q_for(r["dt"]), ds_d)
        # Secondary Q-mirror: day + year-suffix
        qmirror_d = r["dt"].day + (r["dt"].year % 100)
        qmirror = get_dn(r["dt"].year, q_for(r["dt"]), qmirror_d)
        if sister:
            mains_str = str(r["mains"])
            stars_str = str(r["stars"])
            smains_str = str(sister["mains"])
            sstars_str = str(sister["stars"])
            print(f"{r['dt'].strftime('%d.%m.%Y'):<12} Q{q_for(r['dt'])}d{d_mirror:<3} {code:<8} {mains_str:<25} {stars_str:<10}"
                  f"   ‖   d{ds_d:<5} {sister['dt'].strftime('%d.%m.%Y'):<12} {smains_str:<25} {sstars_str:<10}")
            pairs.append({
                "mirror_date": r["dt"].strftime("%d.%m.%Y"),
                "mirror_qd": (q_for(r["dt"]), d_mirror),
                "mirror_code": code,
                "mirror_mains": r["mains"],
                "mirror_stars": r["stars"],
                "sister_d": ds_d,
                "sister_date": sister["dt"].strftime("%d.%m.%Y"),
                "sister_mains": sister["mains"],
                "sister_stars": sister["stars"],
                "qmirror_d": qmirror_d if qmirror else None,
                "qmirror_date": qmirror["dt"].strftime("%d.%m.%Y") if qmirror else None,
                "qmirror_mains": qmirror["mains"] if qmirror else None,
            })

    # Cross-grammar: numbers that appear in BOTH mirror and sister-d
    print()
    print("=" * 90)
    print("🎼 MIRROR↔SISTER-D NUMBER OVERLAP (raw + ±25 carrier + ±1/2 neighbor)")
    print("=" * 90)
    grammar_count = Counter()
    for p in pairs:
        ovr_raw = set(p["mirror_mains"]) & set(p["sister_mains"])
        # carrier overlap (±25)
        carrier_overlap = set()
        for m in p["mirror_mains"]:
            for s in p["sister_mains"]:
                if abs(m - s) == 25:
                    carrier_overlap.add((m, s))
        # neighbor
        neighbor_overlap = set()
        for m in p["mirror_mains"]:
            for s in p["sister_mains"]:
                if abs(m - s) in (1, 2):
                    neighbor_overlap.add((m, s))
        star_overlap = set(p["mirror_stars"]) & set(p["sister_stars"])

        grammar_count["raw_main"] += len(ovr_raw)
        grammar_count["carrier_25"] += len(carrier_overlap)
        grammar_count["neighbor_12"] += len(neighbor_overlap)
        grammar_count["star_raw"] += len(star_overlap)

        if ovr_raw or carrier_overlap or star_overlap:
            print(f"  {p['mirror_date']:<12} → {p['sister_date']:<12}  "
                  f"raw={sorted(ovr_raw)} carrier(±25)={sorted(carrier_overlap)} "
                  f"neighbor(±1/2)={sorted(neighbor_overlap)} star={sorted(star_overlap)}")
    print()
    print(f"Tally across {len(pairs)} pairs: raw={grammar_count['raw_main']}  "
          f"carrier±25={grammar_count['carrier_25']}  neighbor={grammar_count['neighbor_12']}  "
          f"star={grammar_count['star_raw']}")
    print(f"Avg per pair:  raw {grammar_count['raw_main']/max(1,len(pairs)):.2f}  "
          f"carrier {grammar_count['carrier_25']/max(1,len(pairs)):.2f}  "
          f"neighbor {grammar_count['neighbor_12']/max(1,len(pairs)):.2f}  "
          f"star {grammar_count['star_raw']/max(1,len(pairs)):.2f}")

    # TONIGHT — synthetic for 02.06.2026
    print()
    print("=" * 90)
    print("🎯 TONIGHT 02.06.2026 — SISTER-D PROJECTION")
    print("=" * 90)
    today = datetime(2026, 6, 2)
    today_q = q_for(today)
    today_d = qd_of(today)
    digit_sum_day = sum(int(c) for c in f"{today.day:02d}")
    sister_d = digit_sum_day  # = 2
    sister = get_dn(today.year, today_q, sister_d)
    qmirror_d = today.day + (today.year % 100)  # 2+26 = 28
    qmirror = get_dn(today.year, today_q, qmirror_d)
    print(f"  today qd: Q{today_q}d{today_d} (02.06.2026)")
    print(f"  digit_sum(day=02) = {digit_sum_day} → sister at Q{today_q}d{sister_d}")
    if sister:
        print(f"  sister-d ({sister['dt'].strftime('%d.%m.%Y')}): mains={sister['mains']} stars={sister['stars']}")
    qmir_msg = f"Q{today_q}d{qmirror_d}"
    if qmirror:
        print(f"  Q-mirror at {qmir_msg} ({qmirror['dt'].strftime('%d.%m.%Y')}): mains={qmirror['mains']} stars={qmirror['stars']}")
    else:
        print(f"  Q-mirror at {qmir_msg} → DOES NOT EXIST in Q{today_q} 2026 (only 27 d max)")
        # Try the modular wrap: 28 mod 27 = 1 (Q-loop) OR Q-1 mirror
        bucket = qd_index.get((today.year, today_q), [])
        max_d = len(bucket)
        wrap_d = ((qmirror_d - 1) % max_d) + 1 if max_d > 0 else None
        if wrap_d:
            wrap_row = get_dn(today.year, today_q, wrap_d)
            if wrap_row:
                print(f"  → wrapped to d{wrap_d} ({wrap_row['dt'].strftime('%d.%m.%Y')}): mains={wrap_row['mains']} stars={wrap_row['stars']}")

    # Now cross-correlate with BD 29.05.2026
    bd = next(r for r in rows if r["dt"].strftime("%d.%m.%Y") == "29.05.2026")
    print(f"\n  BD 29.05.2026: mains={bd['mains']} stars={bd['stars']}")

    if sister:
        s_mains = set(sister["mains"])
        b_mains = set(bd["mains"])
        print()
        print("  CROSS-CHORD (sister-d × BD):")
        raw = sorted(s_mains & b_mains)
        print(f"    raw overlap: {raw}")
        carriers = []
        for s in s_mains:
            for b in b_mains:
                if abs(s - b) == 25:
                    carriers.append((s, b))
        print(f"    ±25 carrier: {sorted(carriers)}")
        nbrs = []
        for s in s_mains:
            for b in b_mains:
                if abs(s - b) in (1, 2):
                    nbrs.append((s, b))
        print(f"    ±1/2 neighbor: {sorted(nbrs)}")

    # Save
    Path("/app/backend/data").mkdir(exist_ok=True)
    Path("/app/backend/data/mirror_sister_d_canon.json").write_text(
        json.dumps({
            "pairs": pairs,
            "grammar_count": dict(grammar_count),
            "today_projection": {
                "mirror_date": today.strftime("%d.%m.%Y"),
                "qd": (today_q, today_d),
                "sister_d": sister_d,
                "sister_date": sister["dt"].strftime("%d.%m.%Y") if sister else None,
                "sister_mains": sister["mains"] if sister else None,
                "sister_stars": sister["stars"] if sister else None,
                "qmirror_d": qmirror_d,
                "qmirror_exists": qmirror is not None,
            },
        }, indent=2, default=str))
    print("\n💾 /app/backend/data/mirror_sister_d_canon.json")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
