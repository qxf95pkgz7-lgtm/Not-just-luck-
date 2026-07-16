/* RollingNumberWheel — single-value odometer ribbon for picking ONE number
   in a range (e.g. ticket count 1–20, lock position 1–42, lucky number 1–6).
   Matches RollingDateWheel aesthetic (brass tumbler on fuchsia/cyan glass).

   Props:
     value    — current number (number)
     onChange — (n: number) => void
     min      — lower bound (inclusive), default 1
     max      — upper bound (inclusive), default 99
     label    — optional caption above the wheel
     width    — px (default 72)
     testId   — for data-testid
     allowZero — if true, treats 0 as a valid value (e.g. "unlocked")
*/
import React, { useState, useRef, useEffect, useCallback } from 'react';

const pad2 = (n) => String(n).padStart(2, '0');

function Wheel({ value, min, max, format = pad2, onChange, width = 72, testId }) {
  const ref = useRef(null);
  const dragging = useRef(false);
  const startY = useRef(0);
  const startVal = useRef(value);
  const ITEM_H = 36;
  const VISIBLE = 5;

  const range = (max - min + 1);
  const clamp = (v) => {
    let x = v;
    while (x < min) x += range;
    while (x > max) x -= range;
    return x;
  };

  const onDown = useCallback((e) => {
    dragging.current = true;
    startY.current = e.touches ? e.touches[0].clientY : e.clientY;
    startVal.current = value;
    e.preventDefault();
  }, [value]);

  const onMove = useCallback((e) => {
    if (!dragging.current) return;
    const y = e.touches ? e.touches[0].clientY : e.clientY;
    const dy = startY.current - y;
    const steps = Math.round(dy / ITEM_H);
    if (steps !== 0) {
      const next = clamp(startVal.current + steps);
      if (next !== value) onChange(next);
    }
  }, [onChange, value]);

  const onUp = useCallback(() => { dragging.current = false; }, []);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const handlers = [
      ['mousedown', onDown], ['mousemove', onMove], ['mouseup', onUp], ['mouseleave', onUp],
      ['touchstart', onDown, { passive: false }], ['touchmove', onMove, { passive: false }], ['touchend', onUp],
    ];
    handlers.forEach(([ev, fn, opts]) => el.addEventListener(ev, fn, opts));
    return () => handlers.forEach(([ev, fn]) => el.removeEventListener(ev, fn));
  }, [onDown, onMove, onUp]);

  const onWheel = (e) => {
    e.preventDefault();
    const step = e.deltaY > 0 ? 1 : -1;
    onChange(clamp(value + step));
  };

  const items = [];
  for (let i = -2; i <= 2; i++) {
    items.push({ v: clamp(value + i), offset: i });
  }

  return (
    <div
      ref={ref}
      onWheel={onWheel}
      data-testid={testId}
      className="relative overflow-hidden cursor-ns-resize select-none rounded-md"
      style={{
        width: width + 'px',
        height: (VISIBLE * ITEM_H) + 'px',
        background: 'linear-gradient(180deg, rgba(15,12,30,0.95) 0%, rgba(40,20,60,0.85) 50%, rgba(15,12,30,0.95) 100%)',
        boxShadow: 'inset 0 12px 24px -8px rgba(0,0,0,0.7), inset 0 -12px 24px -8px rgba(0,0,0,0.7), 0 0 0 1px rgba(217,70,239,0.35)',
        touchAction: 'none',
      }}
    >
      <div
        className="absolute left-0 right-0 pointer-events-none"
        style={{
          top: (2 * ITEM_H) + 'px',
          height: ITEM_H + 'px',
          background: 'linear-gradient(180deg, rgba(217,70,239,0.18), rgba(34,211,238,0.12))',
          borderTop: '1px solid rgba(217,70,239,0.55)',
          borderBottom: '1px solid rgba(34,211,238,0.55)',
        }}
      />
      {items.map(({ v, offset }) => {
        const isSelected = offset === 0;
        const opacity = isSelected ? 1 : 0.35 + 0.25 * (2 - Math.abs(offset));
        return (
          <div
            key={offset}
            className="absolute left-0 right-0 flex items-center justify-center font-mono"
            style={{
              top: ((offset + 2) * ITEM_H) + 'px',
              height: ITEM_H + 'px',
              fontSize: isSelected ? '22px' : '18px',
              fontWeight: isSelected ? 700 : 500,
              color: isSelected ? '#f5d0fe' : '#94a3b8',
              opacity,
              textShadow: isSelected ? '0 0 12px rgba(217,70,239,0.6)' : 'none',
              transition: 'font-size 0.12s, color 0.12s',
            }}
          >
            {format(v)}
          </div>
        );
      })}
    </div>
  );
}

export default function RollingNumberWheel({
  value,
  onChange,
  min = 1,
  max = 99,
  label,
  width,
  testId = 'rolling-number',
  allowZero = false,
  formatValue,
  twoDigit = false,
}) {
  // Normalize incoming value
  const lo = allowZero ? Math.min(0, min) : min;
  const initial = typeof value === 'number' && Number.isFinite(value) ? value : lo;
  const [n, setN] = useState(initial);

  useEffect(() => {
    if (typeof value === 'number' && Number.isFinite(value) && value !== n) setN(value);
  }, [value]);

  useEffect(() => {
    if (n !== value) onChange(n);
  }, [n]);

  // Two-digit mode: render TENS + UNITS wheels side by side.
  // User rolls each digit independently — much faster than scrolling
  // through 1..50.
  if (twoDigit) {
    const tensMax = Math.min(9, Math.floor(max / 10));
    const tens = Math.max(0, Math.floor(n / 10));
    const units = Math.max(0, n % 10);

    const combine = (t, u) => {
      let combined = t * 10 + u;
      if (combined > max) combined = max;
      if (combined < 0) combined = 0;
      if (!allowZero && combined < min && combined !== 0) combined = min;
      return combined;
    };

    return (
      <div data-testid={testId} className="inline-flex flex-col items-center p-2 rounded-lg"
        style={{
          background: 'linear-gradient(180deg, rgba(15,23,42,0.6), rgba(15,23,42,0.85))',
          border: '1px solid rgba(217,70,239,0.25)',
        }}
      >
        {label && (
          <span className="text-[9px] uppercase tracking-wider text-fuchsia-300/70 mb-1 font-semibold">
            {label}
          </span>
        )}
        <div className="flex gap-1 items-center">
          <Wheel
            value={tens}
            min={0}
            max={tensMax}
            format={(v) => String(v)}
            onChange={(t) => setN(combine(t, units))}
            width={34}
            testId={`${testId}-tens`}
          />
          <Wheel
            value={units}
            min={0}
            max={9}
            format={(v) => String(v)}
            onChange={(u) => setN(combine(tens, u))}
            width={34}
            testId={`${testId}-units`}
          />
        </div>
        {formatValue && n === 0 && (
          <span className="text-[9px] text-fuchsia-300/60 mt-0.5 font-mono">
            {formatValue(0)}
          </span>
        )}
      </div>
    );
  }

  // Single-wheel mode (default)
  // Auto-size wheel width based on max digit count
  const digits = String(max).length;
  const w = width || (digits >= 3 ? 86 : 72);
  const fmt = formatValue || ((v) => digits >= 2 ? pad2(v) : String(v));

  return (
    <div data-testid={testId} className="inline-flex flex-col items-center p-2 rounded-lg"
      style={{
        background: 'linear-gradient(180deg, rgba(15,23,42,0.6), rgba(15,23,42,0.85))',
        border: '1px solid rgba(217,70,239,0.25)',
      }}
    >
      {label && (
        <span className="text-[9px] uppercase tracking-wider text-fuchsia-300/70 mb-1 font-semibold">
          {label}
        </span>
      )}
      <Wheel
        value={n}
        min={lo}
        max={max}
        format={fmt}
        onChange={setN}
        width={w}
        testId={`${testId}-wheel`}
      />
    </div>
  );
}
