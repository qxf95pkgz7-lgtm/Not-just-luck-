"""
🎻 SWISS DATE-TUNING VALIDATOR — The DJ's Music Engine
═══════════════════════════════════════════════════════════════════════

Learned live from the DJ's teachings (/app/memory/swiss_music_notes.md).

META-RULE: Every draw plays a different tune. We don't search for ONE
pattern. Instead we listen to each generated ticket and count how many
date-tunings it satisfies. Tuned > flat.

The date is always inside the draw. This module checks HOW a ticket
carries the date's voice.

Range: Swiss Lotto 1-42 (not Euro 1-50).
Circle rule: Swiss-circle(n) = (n + 21) mod 42  → half of 42, not 25.
"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime


# ─── Core Swiss primitives ────────────────────────────────────────────

def swiss_wrap(n: int) -> Optional[int]:
    """Any value > 42 wraps via n-42; values <= 0 return None; else pass through."""
    if n is None:
        return None
    while n > 42:
        n -= 42
    if 1 <= n <= 42:
        return n
    return None


def swiss_circle(n: int) -> Optional[int]:
    """Swiss circle: +21 mod 42 (half of 42)."""
    if n is None or n < 1:
        return None
    return swiss_wrap(n + 21)


def swiss_flip(n: int) -> Optional[int]:
    """Reverse digits, then Swiss-wrap if needed."""
    if n is None or n < 10:
        return n  # single digits flip to themselves
    f = int(str(n)[::-1])
    return swiss_wrap(f)


def silence_agent(month: int) -> int:
    """Swiss-circle of the month. For April (4), silence = 25."""
    return (month + 21) if 1 <= month <= 12 else 0


# ─── Date parsing ─────────────────────────────────────────────────────

def parse_swiss_date(date_str: str) -> Tuple[int, int, int, int]:
    """
    Parse 'DD.MM.YYYY' → (day, month, year_prefix, year_suffix).
    Year is split as YYYY → (20, 26) for 2026.
    """
    dt = datetime.strptime(date_str, '%d.%m.%Y')
    yr_str = f'{dt.year:04d}'
    year_pre = int(yr_str[:2])
    year_suf = int(yr_str[2:])
    return dt.day, dt.month, year_pre, year_suf


def date_sum(date_str: str) -> int:
    """day + month + year_prefix + year_suffix — the full date sum."""
    d, m, yp, ys = parse_swiss_date(date_str)
    return d + m + yp + ys


def date_targets(date_str: str) -> Dict[str, int]:
    """
    Build the target-spiral for a date.
    Returns all candidate target numbers (may exceed 42; use swiss_wrap later).
    """
    d, m, yp, ys = parse_swiss_date(date_str)
    day_str = f'{d:02d}'
    month_str = f'{m:d}'
    sc_day = swiss_circle(d) or 0
    sc_month = silence_agent(m)
    
    targets = {
        'raw': int(day_str + month_str),                    # e.g. 154
        'shifted': int(day_str + month_str) + 21,            # e.g. 175
        'circle_day': int(f'{sc_day}{month_str}'),           # e.g. 364 = 36|4
        'paired_circle': int(f'{sc_day}{sc_month}'),         # e.g. 3625 = 36|25
        'digit_sum': sum(int(c) for c in f'{d:02d}{m:02d}{yp:02d}{ys:02d}'),
    }
    return targets


# ─── Tuning formulas (from /app/memory/swiss_music_notes.md) ─────────

def tune_p5_plus_year(ticket: List[int], date_str: str) -> bool:
    """🎻 P5 + year-suffix = date-sum."""
    if len(ticket) < 6: return False
    srt = sorted(ticket)
    _, _, _, ys = parse_swiss_date(date_str)
    return srt[4] + ys == date_sum(date_str)


def tune_circle_p5_flip_p6(ticket: List[int], date_str: str) -> bool:
    """🎻 circle(P5) + flip(P6) = date-sum."""
    if len(ticket) < 6: return False
    srt = sorted(ticket)
    p5, p6 = srt[4], srt[5]
    c5 = swiss_circle(p5) or 0
    # flip of P6 — allow raw 2-digit reverse (may exceed 42; use raw int here)
    f6_raw = int(str(p6)[::-1]) if p6 >= 10 else p6
    return c5 + f6_raw == date_sum(date_str)


def tune_p2_times_10_plus_p3(ticket: List[int], date_str: str) -> bool:
    """🎻🎻 P2×10 + P3 = date target (any of raw/shifted/circle)."""
    if len(ticket) < 6: return False
    srt = sorted(ticket)
    p2, p3 = srt[1], srt[2]
    val = p2 * 10 + p3
    t = date_targets(date_str)
    return val in (t['raw'], t['shifted'], t['circle_day'], t['paired_circle'])


def tune_day_plus_silence(ticket: List[int], date_str: str) -> bool:
    """🎻 day + silence-agent = some Pn."""
    d, m, _, _ = parse_swiss_date(date_str)
    sa = silence_agent(m)
    target = swiss_wrap(d + sa)
    return target is not None and target in ticket


def tune_month_double_plus_year(ticket: List[int], date_str: str) -> bool:
    """🎻 month×2 + year-suffix = some Pn."""
    _, m, _, ys = parse_swiss_date(date_str)
    target = swiss_wrap(m * 2 + ys)
    return target is not None and target in ticket


def tune_p4_plus_lucky(ticket: List[int], lucky: Optional[int], date_str: str) -> bool:
    """🎻 P4 + Lucky → flip → P3  OR  swiss-wrap → some Pn."""
    if len(ticket) < 4 or lucky is None: return False
    srt = sorted(ticket)
    p4 = srt[3]
    s = p4 + lucky
    flipped = int(str(s)[::-1]) if s >= 10 else s
    flipped_wrap = swiss_wrap(flipped)
    wrap = swiss_wrap(s)
    return (flipped_wrap in ticket) or (wrap in ticket)


def tune_digit_coverage(ticket: List[int], date_str: str) -> bool:
    """🎻 The date's digits all appear somewhere in the ticket (digit-sequence bridge)."""
    d, m, _, ys = parse_swiss_date(date_str)
    digits_needed = set(f'{d:02d}{m:02d}{ys:02d}')
    digits_in_ticket = set()
    for n in ticket:
        for c in f'{n:02d}':
            digits_in_ticket.add(c)
    return digits_needed.issubset(digits_in_ticket)


def tune_silence_addition(ticket: List[int], date_str: str) -> bool:
    """🎻 Some ticket number = another ticket number + silence (silence hiding in pair)."""
    _, m, _, _ = parse_swiss_date(date_str)
    sa = silence_agent(m)
    s = set(ticket)
    for n in ticket:
        v = swiss_wrap(n + sa)
        if v is not None and v != n and v in s:
            return True
    return False


def tune_p2p3_minus_silence_echo(ticket: List[int], date_str: str, prior_draws: List[Dict] = None) -> bool:
    """🎻 P2 + P3 − silence = echo of a number from a prior draw."""
    if len(ticket) < 3 or not prior_draws: return False
    _, m, _, _ = parse_swiss_date(date_str)
    sa = silence_agent(m)
    srt = sorted(ticket)
    echo = swiss_wrap(srt[1] + srt[2] - sa)
    if echo is None: return False
    for pd in prior_draws[:3]:
        if echo in pd.get('numbers', []):
            return True
    return False


# ─── 🌉 Euro → Swiss bridge ───────────────────────────────────────────

def euro_to_swiss(n: int) -> Optional[int]:
    """
    🎻 Translate a Euro number (1-50) to its Swiss voice.
    Rule: keep subtracting 21 until ≤ 21 (half-of-42 reduction).
      22 → 1,  23 → 2,  28 → 7,  41 → 20,  47 → 47−21=26 → 26−21=5.
    Numbers ≤ 21 stay as-is.
    """
    if n is None or n < 1 or n > 50: return None
    v = n
    while v > 21:
        v -= 21
    return v if 1 <= v <= 21 else None


def euro_family(n: int) -> List[int]:
    """
    🎻 Cross-lottery family of n: [self, flip-raw, Euro-wrap-of-flip, Swiss-bridge].
    Example: 28 → [28, 82, 32, 7].
    Returns unique Swiss-valid + Euro-valid values.
    """
    fam = {n}
    # flip (raw 2-digit reverse, no wrap)
    if n >= 10:
        f_raw = int(str(n)[::-1])
        fam.add(f_raw)
        # Euro-wrap of flip
        if f_raw > 50:
            fam.add(f_raw - 50)
        elif f_raw < 1:
            pass
    # Swiss bridge
    sb = euro_to_swiss(n)
    if sb is not None:
        fam.add(sb)
    return sorted(fam)


def tune_euro_bridge(ticket: List[int], last_euro_numbers: List[int]) -> bool:
    """
    🎻 Check if this Swiss ticket carries at least 2 Euro-bridge voices
    from the last Euro draw (n → n−21 residues).
    """
    if not last_euro_numbers: return False
    swiss_voices = set()
    for en in last_euro_numbers:
        sv = euro_to_swiss(en)
        if sv is not None:
            swiss_voices.add(sv)
    hits = sum(1 for n in ticket if n in swiss_voices)
    return hits >= 2


# ─── Master validator ────────────────────────────────────────────────

TUNING_FORMULAS = [
    ('P5+year=date_sum',            tune_p5_plus_year),
    ('circle(P5)+flip(P6)=date_sum', tune_circle_p5_flip_p6),
    ('P2*10+P3=date_target',        tune_p2_times_10_plus_p3),
    ('day+silence=Pn',              tune_day_plus_silence),
    ('month*2+year=Pn',             tune_month_double_plus_year),
    ('digit_coverage',              tune_digit_coverage),
    ('silence_hiding_in_pair',      tune_silence_addition),
]


def score_date_tuning(ticket: List[int], date_str: str,
                       lucky: Optional[int] = None,
                       prior_draws: List[Dict] = None,
                       last_euro_numbers: List[int] = None) -> Dict:
    """
    🎻🎧 MASTER TUNING VALIDATOR
    
    For a generated Swiss Lotto ticket (6 numbers + optional Lucky),
    count how many date-tunings are active.
    
    Returns:
        {
            "score": int,                  # how many tunings active
            "active_tunings": [str, ...],  # names of the ones that fired
            "ticket": list,
            "date": str,
            "tuned": bool,                 # score >= 1
        }
    """
    active = []
    for name, fn in TUNING_FORMULAS:
        try:
            if fn(ticket, date_str):
                active.append(name)
        except Exception:
            pass
    # Special 2-arg tunings
    try:
        if tune_p4_plus_lucky(ticket, lucky, date_str):
            active.append('P4+Lucky→flip/wrap→Pn')
    except Exception:
        pass
    try:
        if tune_p2p3_minus_silence_echo(ticket, date_str, prior_draws or []):
            active.append('P2+P3-silence=prior_echo')
    except Exception:
        pass
    # 🌉 Euro → Swiss bridge
    try:
        if tune_euro_bridge(ticket, last_euro_numbers or []):
            active.append('euro_bridge≥2voices')
    except Exception:
        pass
    
    return {
        "score": len(active),
        "active_tunings": active,
        "ticket": sorted(ticket) if ticket else [],
        "date": date_str,
        "tuned": len(active) >= 1,
    }


# ─── Quick self-test against the book ─────────────────────────────────

if __name__ == "__main__":
    print("🎻 Verifying tunings against the three Q2 draws in the book...\n")
    
    last_euro = [22, 23, 28, 41, 47]  # 17.04.2026
    
    cases = [
        ("08.04.2026", [2, 9, 21, 22, 26, 35], 3),   # Q2d1
        ("11.04.2026", [1, 6, 8, 14, 22, 34], 1),    # Q2d2
        ("15.04.2026", [4, 12, 34, 38, 39, 40], 5),  # Q2d3
    ]
    for date_str, ticket, lucky in cases:
        r = score_date_tuning(ticket, date_str, lucky=lucky, last_euro_numbers=last_euro)
        print(f"📅 {date_str}  {ticket}  🍀 {lucky}")
        print(f"   date_sum = {date_sum(date_str)}  targets = {date_targets(date_str)}")
        print(f"   ACTIVE TUNINGS ({r['score']}): {r['active_tunings']}")
        print()
    
    # Euro → Swiss bridge demo
    print("🌉 Euro → Swiss bridge from last Euro draw [22, 23, 28, 41, 47]:")
    for en in last_euro:
        print(f"   {en} → Swiss voice = {euro_to_swiss(en)}  | family: {euro_family(en)}")
