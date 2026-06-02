/* RollingDateWheel — gas-station odometer style date picker
   Three scroll wheels (DD / MM / YYYY), touch-drag or wheel-scroll
   Value format: "dd.mm.yyyy"  (e.g., "29.05.2026")
   Aesthetic: vintage brass tumblers on dark fuchsia/cyan glass
*/
import React, { useState, useRef, useEffect, useCallback } from 'react';

const pad2 = (n) => String(n).padStart(2, '0');

// One wheel — renders a vertical odometer ribbon
function Wheel({ value, min, max, format = pad2, onChange, width = 64, testId }) {
  const ref = useRef(null);
  const dragging = useRef(false);
  const startY = useRef(0);
  const startVal = useRef(value);
  const ITEM_H = 36; // px per row
  const VISIBLE = 5; // total rows visible, center is selected

  const range = (max - min + 1);
  const clamp = (v) => {
    let x = v;
    while (x < min) x += range;
    while (x > max) x -= range;
    return x;
  };

  // Pointer drag handlers
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

  // Build visible items: [value-2, value-1, value, value+1, value+2]
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
      {/* highlight band over selected */}
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
      {/* item rows */}
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

// Helper: days-in-month with leap-year awareness
function daysInMonth(m, y) {
  return new Date(y, m, 0).getDate();
}

// MAIN component
export default function RollingDateWheel({ value, onChange, minYear = 2004, maxYear = 2030, testId = 'rolling-date' }) {
  // Parse incoming "dd.mm.yyyy" or fall back to today
  const parse = (v) => {
    if (!v || typeof v !== 'string') {
      const t = new Date();
      return { d: t.getDate(), m: t.getMonth() + 1, y: t.getFullYear() };
    }
    const parts = v.split('.');
    return {
      d: parseInt(parts[0], 10) || 1,
      m: parseInt(parts[1], 10) || 1,
      y: parseInt(parts[2], 10) || new Date().getFullYear(),
    };
  };
  const initial = parse(value);
  const [d, setD] = useState(initial.d);
  const [m, setM] = useState(initial.m);
  const [y, setY] = useState(initial.y);

  // Sync from prop on external change
  useEffect(() => {
    if (!value) return;
    const p = parse(value);
    if (p.d !== d || p.m !== m || p.y !== y) {
      setD(p.d); setM(p.m); setY(p.y);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  // Emit out whenever any wheel changes (clamp day to month length)
  useEffect(() => {
    const maxDay = daysInMonth(m, y);
    let dd = d;
    if (dd > maxDay) { dd = maxDay; setD(maxDay); }
    const out = `${pad2(dd)}.${pad2(m)}.${y}`;
    if (out !== value) onChange(out);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [d, m, y]);

  const maxDay = daysInMonth(m, y);

  return (
    <div data-testid={testId} className="inline-flex items-stretch gap-1.5 p-2 rounded-lg"
      style={{
        background: 'linear-gradient(180deg, rgba(15,23,42,0.6), rgba(15,23,42,0.85))',
        border: '1px solid rgba(217,70,239,0.25)',
      }}
    >
      <div className="flex flex-col items-center">
        <span className="text-[9px] uppercase tracking-wider text-fuchsia-300/70 mb-1 font-semibold">Day</span>
        <Wheel value={d} min={1} max={maxDay} onChange={setD} testId={`${testId}-day`} />
      </div>
      <div className="text-fuchsia-400/50 font-mono text-2xl self-center pt-3">.</div>
      <div className="flex flex-col items-center">
        <span className="text-[9px] uppercase tracking-wider text-fuchsia-300/70 mb-1 font-semibold">Month</span>
        <Wheel value={m} min={1} max={12} onChange={setM} testId={`${testId}-month`} />
      </div>
      <div className="text-fuchsia-400/50 font-mono text-2xl self-center pt-3">.</div>
      <div className="flex flex-col items-center">
        <span className="text-[9px] uppercase tracking-wider text-fuchsia-300/70 mb-1 font-semibold">Year</span>
        <Wheel value={y} min={minYear} max={maxYear} format={(v) => String(v)} width={86} onChange={setY} testId={`${testId}-year`} />
      </div>
    </div>
  );
}
