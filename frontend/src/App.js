import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Sparkles, RefreshCw, ChevronDown, ChevronUp, Gift, Star, Globe, History, Trash2, Target, TrendingUp, CheckCircle2, XCircle, Clock, Zap, Eye } from "lucide-react";
import RollingDateWheel from "./components/RollingDateWheel";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Swiss Lotto Ball Component - white with colored stripe
const Ball = ({ number, size = "sm", isWinner = false, isSpinning = false, delay = 0, style = {}, maxNum = 42 }) => {
  const getStripeColor = (num) => {
    if (maxNum === 50) {
      // EuroMillions colors (1-50)
      if (num <= 10) return { bg: '#e53935', name: 'red' }; 
      if (num <= 20) return { bg: '#fb8c00', name: 'orange' };
      if (num <= 30) return { bg: '#fdd835', name: 'yellow' };
      if (num <= 40) return { bg: '#43a047', name: 'green' };
      return { bg: '#1e88e5', name: 'blue' };
    }
    // Swiss Lotto colors (1-42)
    if (num <= 9) return { bg: '#e53935', name: 'red' }; 
    if (num <= 19) return { bg: '#fb8c00', name: 'orange' };
    if (num <= 29) return { bg: '#fdd835', name: 'yellow' };
    if (num <= 39) return { bg: '#43a047', name: 'green' };
    return { bg: '#1e88e5', name: 'blue' };
  };

  const sizeConfig = {
    xs: { ball: 'w-6 h-6', text: 'text-[7px]', stripe: 'h-[40%]' },
    sm: { ball: 'w-8 h-8', text: 'text-[9px]', stripe: 'h-[40%]' },
    md: { ball: 'w-12 h-12', text: 'text-sm', stripe: 'h-[38%]' },
    lg: { ball: 'w-16 h-16', text: 'text-lg', stripe: 'h-[36%]' }
  };

  const { bg: stripeColor } = getStripeColor(number);
  const config = sizeConfig[size];

  return (
    <div 
      className={`
        ${config.ball} rounded-full flex items-center justify-center relative
        ${isWinner ? 'winner-ball' : ''}
        ${isSpinning ? 'animate-spin' : ''}
      `}
      style={{ 
        background: 'linear-gradient(145deg, #ffffff 0%, #f5f5f5 40%, #e8e8e8 100%)',
        boxShadow: isWinner 
          ? `0 0 25px ${stripeColor}90, 0 4px 15px rgba(0,0,0,0.3), inset 0 2px 4px rgba(255,255,255,0.9)` 
          : '0 3px 10px rgba(0,0,0,0.25), inset 0 2px 4px rgba(255,255,255,0.9), inset 0 -2px 4px rgba(0,0,0,0.05)',
        animationDelay: `${delay}ms`,
        animationDuration: isSpinning ? '0.25s' : '2s',
        ...style
      }}
    >
      <div 
        className={`absolute inset-x-0 top-1/2 -translate-y-1/2 ${config.stripe} flex items-center justify-center overflow-hidden`}
        style={{ 
          background: `linear-gradient(180deg, ${stripeColor} 0%, ${stripeColor}dd 100%)`,
          boxShadow: 'inset 0 1px 2px rgba(255,255,255,0.3), inset 0 -1px 2px rgba(0,0,0,0.2)'
        }}
      >
        <span 
          className={`font-black text-white ${config.text}`}
          style={{ textShadow: '0 1px 2px rgba(0,0,0,0.5)', letterSpacing: '-0.5px' }}
        >
          {number}
        </span>
      </div>
      <div 
        className="absolute top-[8%] left-[18%] w-[30%] h-[25%] rounded-full"
        style={{ background: 'radial-gradient(ellipse, rgba(255,255,255,0.95) 0%, transparent 70%)' }}
      />
    </div>
  );
};

// 🎯 Random-vs-E reality check box (DJ canon 29.04.2026)
// Shows how the engine beats pure random chance — Jackpot vs Money mode.
const RandomVsEBox = ({ data, mode }) => {
  if (!data || !data.actual_draw) return null;
  const random = data.random || {};
  const jackpot = data.engine?.jackpot;
  const money = data.engine?.money;
  const target = data.target_date || '?';
  const labelM = mode === 'euro' ? '⭐' : '🍀';

  const fmt = (p) => {
    if (p == null || p === undefined) return '—';
    const v = p * 100;
    if (v < 0.01) return v.toExponential(1) + '%';
    if (v < 1) return v.toFixed(2) + '%';
    return v.toFixed(1) + '%';
  };
  const mult = (e, r) => {
    if (e == null || r == null || r === 0) return null;
    const x = e / r;
    if (!isFinite(x)) return null;
    return x;
  };
  const multBadge = (m) => {
    if (m == null) return <span className="text-slate-500 text-[8px]">—</span>;
    const cls = m >= 2 ? 'text-emerald-300 bg-emerald-500/15 border-emerald-400/40'
              : m >= 1 ? 'text-amber-300 bg-amber-500/15 border-amber-400/40'
              : 'text-rose-300 bg-rose-500/15 border-rose-400/40';
    return <span className={`px-1 rounded border text-[9px] font-mono font-bold ${cls}`}>{m.toFixed(1)}×</span>;
  };

  const tiers = [
    { key: 'p_2plus_total', label: '2+ hits' },
    { key: 'p_3plus_total', label: '3+ hits' },
    { key: 'p_4plus_total', label: '4+ hits' },
  ];

  const Section = ({ title, engine, color }) => (
    <div className="mb-1.5" data-testid={`rvse-section-${title.toLowerCase()}`}>
      <div className={`flex items-center justify-between text-[9px] font-bold mb-0.5 ${color}`}>
        <span>{title}</span>
        <span className="text-slate-500 font-mono">n={engine?.n ?? 0}</span>
      </div>
      <table className="w-full text-[9px] tabular-nums">
        <thead className="text-slate-500">
          <tr>
            <th className="text-left font-normal">tier</th>
            <th className="text-right font-normal">random</th>
            <th className="text-right font-normal">E</th>
            <th className="text-right font-normal pl-1">×</th>
          </tr>
        </thead>
        <tbody>
          {tiers.map(t => {
            const r = random[t.key];
            const e = engine ? engine[t.key] : null;
            const m = mult(e, r);
            return (
              <tr key={t.key} data-testid={`rvse-row-${title.toLowerCase()}-${t.key}`}>
                <td className="text-slate-300">{t.label}</td>
                <td className="text-right text-slate-400 font-mono">{fmt(r)}</td>
                <td className={`text-right font-mono font-bold ${e != null && r != null && e > r ? 'text-emerald-300' : 'text-slate-300'}`}>{fmt(e)}</td>
                <td className="text-right pl-1">{multBadge(m)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="mb-2 p-2 rounded-lg border border-emerald-500/30 bg-gradient-to-br from-emerald-900/20 to-slate-900/40" data-testid="random-vs-e-box">
      <div className="flex items-center justify-between mb-1">
        <span className="text-emerald-300 text-[10px] font-black tracking-wide">🎯 RANDOM vs E</span>
        <span className="text-slate-500 text-[8px]">d {target}</span>
      </div>
      <div className="text-slate-500 text-[8px] mb-1.5">
        Theoretical chance per ticket vs E's actual {labelM} hit rate
        {data.recap_fallback && <span className="ml-1 text-amber-400">• recap</span>}
      </div>
      {jackpot && jackpot.n > 0 && (
        <Section title="Jackpot" engine={jackpot} color="text-amber-300" />
      )}
      {money && money.n > 0 && (
        <Section title="Money" engine={money} color="text-cyan-300" />
      )}
      {(!jackpot || jackpot.n === 0) && (!money || money.n === 0) && (
        <div className="text-[9px] text-slate-500 italic text-center py-2">
          No engine data yet for {target}
        </div>
      )}
    </div>
  );
};



// EuroMillions Star Ball - Gold star design

// 📜 HISTORY PANEL — past draws archive (DJ canon 29.04.2026)
// Compact dropdown showing past target dates + ticket counts; click to expand.
const HistoryPanel = ({ mode, api }) => {
  const [open, setOpen] = useState(false);
  const [dates, setDates] = useState([]);
  const [activeDate, setActiveDate] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    axios.get(`${api}/history/dates?mode=${mode}`)
      .then(r => setDates(r.data?.dates || []))
      .catch(() => setDates([]))
      .finally(() => setLoading(false));
  }, [open, mode, api]);

  const openDate = async (d) => {
    setActiveDate(d);
    setLoading(true);
    try {
      const r = await axios.get(`${api}/history/tickets?mode=${mode}&target_date=${d}&limit=200`);
      setTickets(r.data?.tickets || []);
    } catch { setTickets([]); }
    setLoading(false);
  };

  const downloadCsv = (d) => {
    const url = `${api}/history/export.csv?mode=${mode}${d ? `&target_date=${d}` : ''}`;
    window.open(url, '_blank');
  };

  return (
    <div className="mb-2 p-1.5 rounded-lg border border-slate-700/40 bg-slate-900/50" data-testid="history-panel">
      <button
        className="w-full flex items-center justify-between text-[10px] font-bold text-amber-300 hover:text-amber-200"
        onClick={() => setOpen(!open)}
        data-testid="history-panel-toggle"
      >
        <span>📜 History · past draws</span>
        <span className="text-[9px] text-slate-500">{open ? '▼' : '▶'}</span>
      </button>
      {open && (
        <div className="mt-1.5">
          <button
            onClick={() => downloadCsv(activeDate)}
            className="text-[9px] px-1.5 py-0.5 rounded border border-emerald-600/40 text-emerald-300 hover:bg-emerald-700/20 mb-1"
            data-testid="history-download-csv"
          >⬇ CSV {activeDate ? `(${activeDate})` : '(all)'}</button>
          <div className="grid grid-cols-2 gap-1 max-h-32 overflow-y-auto">
            {(dates || []).map(d => (
              <button
                key={d.target_date}
                onClick={() => openDate(d.target_date)}
                className={`text-left px-1.5 py-0.5 rounded text-[9px] font-mono ${activeDate === d.target_date ? 'bg-amber-500/20 border border-amber-400/50 text-amber-200' : 'bg-slate-800/40 hover:bg-slate-700/40 text-slate-300'}`}
                data-testid={`history-date-${d.target_date}`}
                title={`${d.count} tickets · max ${d.max_hits} hits · ${d.n_2plus}/2+ · ${d.n_3plus}/3+`}
              >
                {d.target_date}
                <span className="text-[8px] text-slate-500 ml-1">{d.count}</span>
                {d.n_3plus > 0 && <span className="text-[8px] text-emerald-400 ml-1">★{d.n_3plus}</span>}
              </button>
            ))}
          </div>
          {activeDate && (
            <div className="mt-1.5 max-h-48 overflow-y-auto">
              <div className="text-[9px] text-slate-400 mb-1">
                {tickets.length} tickets for {activeDate}
              </div>
              {(tickets || []).slice(0, 50).map((t, i) => {
                const total = (t.hits || {}).total || 0;
                const cls = total >= 3 ? 'border-emerald-500/40 bg-emerald-500/5'
                          : total >= 2 ? 'border-amber-500/40 bg-amber-500/5'
                          : 'border-slate-700/30';
                return (
                  <div key={t.serial || i} className={`mb-1 p-1 rounded border ${cls}`} data-testid={`history-ticket-${i}`}>
                    <div className="text-[8px] font-mono text-amber-400/80">🎫 {t.serial || '—'}</div>
                    <div className="text-[10px] font-mono text-slate-200">
                      [{(t.numbers || []).join(', ')}]
                      {mode === 'swiss' && t.lucky != null && <span className="ml-1 text-amber-300">🍀{t.lucky}</span>}
                      {mode === 'euro' && t.stars && <span className="ml-1 text-yellow-300">⭐[{t.stars.join(', ')}]</span>}
                    </div>
                    {t.hits && (
                      <div className="text-[9px] text-slate-400">
                        {t.hits.mains}m{mode === 'euro' ? `+${t.hits.stars}s` : (t.hits.lucky_hit ? '+🍀' : '')} = <span className={total >= 2 ? 'text-emerald-300 font-bold' : ''}>{total}h</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
          {loading && <div className="text-[9px] text-slate-500 mt-1">loading...</div>}
        </div>
      )}
    </div>
  );
};


const StarBall = ({ number, size = "sm", isWinner = false, isSpinning = false }) => {
  const sizeConfig = {
    xs: { ball: 'w-6 h-6', text: 'text-[8px]' },
    sm: { ball: 'w-8 h-8', text: 'text-[10px]' },
    md: { ball: 'w-10 h-10', text: 'text-sm' },
    lg: { ball: 'w-14 h-14', text: 'text-lg' }
  };
  const config = sizeConfig[size];

  return (
    <div 
      className={`${config.ball} rounded-full flex items-center justify-center relative ${isSpinning ? 'animate-spin' : ''}`}
      style={{ 
        background: isWinner 
          ? 'linear-gradient(145deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%)'
          : 'linear-gradient(145deg, #fcd34d 0%, #fbbf24 50%, #f59e0b 100%)',
        boxShadow: isWinner 
          ? '0 0 20px rgba(251,191,36,0.8), 0 4px 15px rgba(0,0,0,0.3)' 
          : '0 3px 10px rgba(0,0,0,0.25), inset 0 2px 4px rgba(255,255,255,0.5)'
      }}
    >
      <Star className="absolute w-full h-full p-1 text-yellow-200/30" fill="currentColor" />
      <span className={`font-black text-gray-900 ${config.text} relative z-10`} style={{ textShadow: '0 1px 1px rgba(255,255,255,0.3)' }}>
        {number}
      </span>
    </div>
  );
};

// Lucky Number Wheel - for Swiss Lotto
const LuckyWheel = ({ luckyNumber, isSpinning, onComplete }) => {
  const [rotation, setRotation] = useState(0);
  const [settled, setSettled] = useState(false);
  const numbers = [1, 2, 3, 4, 5, 6];
  
  useEffect(() => {
    if (isSpinning && luckyNumber) {
      setSettled(false);
      const targetAngle = (luckyNumber - 1) * 60;
      const finalRotation = 360 * 6 + (360 - targetAngle);
      setRotation(finalRotation);
      setTimeout(() => { setSettled(true); if (onComplete) onComplete(); }, 3500);
    }
  }, [isSpinning, luckyNumber, onComplete]);

  useEffect(() => { if (!isSpinning && !settled) setRotation(0); }, [isSpinning, settled]);

  return (
    <div className="flex flex-col items-center">
      <div className="text-xs font-semibold text-amber-400 mb-1">⭐ Lucky</div>
      <div className="relative w-20 h-20">
        <div className="absolute -top-2 left-1/2 -translate-x-1/2 z-20" style={{ width: 0, height: 0, borderLeft: '7px solid transparent', borderRight: '7px solid transparent', borderTop: '10px solid #d4af37', filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.4))' }} />
        <div className="absolute inset-0 rounded-full" style={{ background: 'linear-gradient(180deg, #4a4a5a 0%, #2a2a35 50%, #3a3a45 100%)', boxShadow: '0 4px 15px rgba(0,0,0,0.5), inset 0 1px 3px rgba(255,255,255,0.1)' }} />
        <div className="absolute inset-[6px] rounded-full overflow-hidden" style={{ background: 'conic-gradient(from 0deg, #1e293b 0deg, #334155 60deg, #1e293b 60deg, #334155 120deg, #1e293b 120deg, #334155 180deg, #1e293b 180deg, #334155 240deg, #1e293b 240deg, #334155 300deg, #1e293b 300deg, #334155 360deg)', transform: `rotate(${rotation}deg)`, transition: isSpinning ? 'transform 3.5s cubic-bezier(0.12, 0.8, 0.2, 1)' : 'none', boxShadow: 'inset 0 0 20px rgba(0,0,0,0.5)' }}>
          {numbers.map((num, i) => {
            const angle = i * 60;
            const isWinnerNum = settled && num === luckyNumber;
            return (
              <div key={num} className="absolute" style={{ left: '50%', top: '50%', transform: `translate(-50%, -50%) rotate(${angle}deg) translateY(-24px)` }}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-500 ${isWinnerNum ? 'scale-110' : ''}`} style={{ background: isWinnerNum ? 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)' : 'linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%)', color: isWinnerNum ? '#1a1a24' : '#1e293b', boxShadow: isWinnerNum ? '0 0 12px rgba(251,191,36,0.9)' : '0 1px 4px rgba(0,0,0,0.3)', transform: `rotate(-${angle + rotation}deg)`, transition: isSpinning ? 'transform 3.5s cubic-bezier(0.12, 0.8, 0.2, 1)' : 'none' }}>
                  {num}
                </div>
              </div>
            );
          })}
        </div>
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-5 rounded-full z-10" style={{ background: 'linear-gradient(145deg, #d4af37 0%, #b8860b 100%)', boxShadow: '0 2px 6px rgba(0,0,0,0.4)' }}>
          <div className="absolute inset-1 rounded-full" style={{ background: 'linear-gradient(145deg, #3a3a45 0%, #2a2a35 100%)' }} />
        </div>
        {settled && <div className="absolute inset-0 rounded-full pointer-events-none animate-pulse" style={{ boxShadow: '0 0 25px rgba(251,191,36,0.5)' }} />}
      </div>
      <div className={`mt-1 text-center transition-all duration-500 ${settled ? 'opacity-100' : 'opacity-0'}`}>
        <span className="text-xl font-black text-amber-400" style={{ textShadow: '0 0 8px rgba(251,191,36,0.5)' }}>{luckyNumber}</span>
      </div>
    </div>
  );
};

// Star Wheel for EuroMillions (1-12)
const StarWheel = ({ starNumber, isSpinning, index = 0 }) => {
  const [rotation, setRotation] = useState(0);
  const [settled, setSettled] = useState(false);
  const numbers = Array.from({ length: 12 }, (_, i) => i + 1);
  
  useEffect(() => {
    if (isSpinning && starNumber) {
      setSettled(false);
      const targetAngle = (starNumber - 1) * 30;
      const finalRotation = 360 * (5 + index) + (360 - targetAngle);
      setRotation(finalRotation);
      setTimeout(() => setSettled(true), 3500 + index * 500);
    }
  }, [isSpinning, starNumber, index]);

  useEffect(() => { if (!isSpinning && !settled) setRotation(0); }, [isSpinning, settled]);

  return (
    <div className="flex flex-col items-center">
      <div className="text-xs font-semibold text-amber-400 mb-1">⭐ Star {index + 1}</div>
      <div className="relative w-16 h-16">
        <div className="absolute -top-1 left-1/2 -translate-x-1/2 z-20" style={{ width: 0, height: 0, borderLeft: '5px solid transparent', borderRight: '5px solid transparent', borderTop: '8px solid #fbbf24', filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.4))' }} />
        <div className="absolute inset-0 rounded-full" style={{ background: 'linear-gradient(180deg, #78350f 0%, #451a03 50%, #78350f 100%)', boxShadow: '0 4px 15px rgba(0,0,0,0.5)' }} />
        <div className="absolute inset-[4px] rounded-full overflow-hidden" style={{ background: 'conic-gradient(from 0deg, #1e293b 0deg, #0f172a 30deg, #1e293b 30deg, #0f172a 60deg, #1e293b 60deg, #0f172a 90deg, #1e293b 90deg, #0f172a 120deg, #1e293b 120deg, #0f172a 150deg, #1e293b 150deg, #0f172a 180deg, #1e293b 180deg, #0f172a 210deg, #1e293b 210deg, #0f172a 240deg, #1e293b 240deg, #0f172a 270deg, #1e293b 270deg, #0f172a 300deg, #1e293b 300deg, #0f172a 330deg, #1e293b 330deg, #0f172a 360deg)', transform: `rotate(${rotation}deg)`, transition: isSpinning ? `transform ${3.5 + index * 0.5}s cubic-bezier(0.12, 0.8, 0.2, 1)` : 'none' }}>
          {numbers.map((num, i) => {
            const angle = i * 30;
            const isWinnerNum = settled && num === starNumber;
            return (
              <div key={num} className="absolute" style={{ left: '50%', top: '50%', transform: `translate(-50%, -50%) rotate(${angle}deg) translateY(-20px)` }}>
                <div className={`w-4 h-4 rounded-full flex items-center justify-center font-bold text-[8px] ${isWinnerNum ? 'scale-125' : ''}`} style={{ background: isWinnerNum ? 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)' : 'linear-gradient(145deg, #fcd34d 0%, #fbbf24 100%)', color: '#1a1a24', boxShadow: isWinnerNum ? '0 0 10px rgba(251,191,36,0.9)' : '0 1px 3px rgba(0,0,0,0.3)', transform: `rotate(-${angle + rotation}deg)`, transition: isSpinning ? `transform ${3.5 + index * 0.5}s cubic-bezier(0.12, 0.8, 0.2, 1)` : 'none' }}>
                  {num}
                </div>
              </div>
            );
          })}
        </div>
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded-full z-10" style={{ background: 'linear-gradient(145deg, #fbbf24 0%, #d97706 100%)' }}>
          <Star className="w-full h-full p-0.5 text-yellow-100" fill="currentColor" />
        </div>
        {settled && <div className="absolute inset-0 rounded-full pointer-events-none animate-pulse" style={{ boxShadow: '0 0 20px rgba(251,191,36,0.6)' }} />}
      </div>
      <div className={`mt-1 text-center transition-all duration-500 ${settled ? 'opacity-100' : 'opacity-0'}`}>
        <span className="text-lg font-black text-amber-400">{starNumber}</span>
      </div>
    </div>
  );
};

// Swiss Lotto Ball Machine
const SwissLottoBallMachine = ({ isProcessing, winningNumbers }) => {
  const [balls, setBalls] = useState([]);
  const [phase, setPhase] = useState('idle');
  const [selectedBalls, setSelectedBalls] = useState([]);
  const [currentCatch, setCurrentCatch] = useState(null);
  const [selectionIndex, setSelectionIndex] = useState(0);
  const [catchPhase, setCatchPhase] = useState('none');
  const [hasInitialized, setHasInitialized] = useState(false);
  const GRAVITY = 0.18, FRICTION = 0.98, BOUNCE = 0.75;

  useEffect(() => {
    const allBalls = Array.from({ length: 42 }, (_, i) => ({
      number: i + 1, x: 15 + (i % 7) * 10 + Math.random() * 5, y: 55 + Math.floor(i / 7) * 6 + Math.random() * 3,
      vx: (Math.random() - 0.5) * 0.5, vy: 0, captured: false
    }));
    setBalls(allBalls);
    setHasInitialized(true);
  }, []);

  useEffect(() => {
    if (isProcessing && (phase === 'idle' || phase === 'complete')) {
      setPhase('spinning'); setSelectedBalls([]); setSelectionIndex(0); setCurrentCatch(null); setCatchPhase('none');
      setBalls(prev => prev.map(b => ({ ...b, captured: false })));
    } else if (!isProcessing && phase === 'spinning' && winningNumbers.length > 0) {
      const delay = setTimeout(() => setPhase('selecting'), 2000);
      return () => clearTimeout(delay);
    }
  }, [isProcessing, winningNumbers, phase]);

  useEffect(() => {
    if (phase === 'selecting' && selectionIndex < winningNumbers.length && catchPhase === 'none') {
      const ballNumber = winningNumbers[selectionIndex];
      setCatchPhase('catching'); setCurrentCatch(ballNumber);
      setBalls(prev => prev.map(b => b.number === ballNumber ? { ...b, captured: true } : b));
      setTimeout(() => setCatchPhase('rolling'), 600);
      setTimeout(() => { setCatchPhase('revealed'); setSelectedBalls(prev => [...prev, ballNumber]); }, 1200);
      setTimeout(() => { setCatchPhase('none'); setCurrentCatch(null); setSelectionIndex(prev => prev + 1); }, 1800);
    } else if (phase === 'selecting' && selectionIndex >= winningNumbers.length && catchPhase === 'none') {
      setPhase('complete');
      setTimeout(() => {
        winningNumbers.forEach((ballNum, idx) => {
          setTimeout(() => {
            setBalls(prev => prev.map(b => b.number === ballNum ? { ...b, captured: false, x: 30 + Math.random() * 40, y: 20, vy: 2, vx: (Math.random() - 0.5) * 2 } : b));
          }, idx * 300 + 800);
        });
        setTimeout(() => { setPhase('idle'); setSelectedBalls([]); }, winningNumbers.length * 300 + 1500);
      }, 3000);
    }
  }, [phase, selectionIndex, winningNumbers, catchPhase]);

  useEffect(() => {
    if (hasInitialized && winningNumbers.length > 0 && phase === 'idle' && selectedBalls.length === 0) {
      setSelectedBalls(winningNumbers); setPhase('complete');
    }
  }, [hasInitialized, winningNumbers, phase, selectedBalls.length]);

  useEffect(() => {
    const interval = setInterval(() => {
      setBalls(prev => prev.map(ball => {
        if (ball.captured) return ball;
        let vx = ball.vx, vy = ball.vy;
        vy += GRAVITY;
        const isSpinning = phase === 'spinning' || phase === 'selecting';
        if (isSpinning) {
          vy -= 0.6; if (ball.y > 50) vy -= 1.4 + Math.random() * 0.6; else if (ball.y > 30) vy -= 0.5;
          vx += (Math.random() - 0.5) * 2.5; vy += (Math.random() - 0.5) * 1.8;
          if (Math.random() < 0.1) { vy -= 3 + Math.random() * 2; vx += (Math.random() - 0.5) * 3; }
        } else {
          vy -= 0.25; if (ball.y > 60) vy -= 0.4 + Math.random() * 0.3;
          vx += (Math.random() - 0.5) * 0.8; vy += (Math.random() - 0.5) * 0.5;
          if (Math.random() < 0.03) vy -= 1.5;
        }
        vx *= FRICTION; vy *= FRICTION;
        const maxV = isSpinning ? 7 : 3;
        vx = Math.max(-maxV, Math.min(maxV, vx)); vy = Math.max(-maxV, Math.min(maxV, vy));
        let x = ball.x + vx, y = ball.y + vy;
        if (x < 8) { x = 8; vx = Math.abs(vx) * BOUNCE; }
        if (x > 82) { x = 82; vx = -Math.abs(vx) * BOUNCE; }
        if (y < 10) { y = 10; vy = Math.abs(vy) * BOUNCE; }
        if (y > 85) { y = 85; vy = -Math.abs(vy) * BOUNCE; }
        return { ...ball, x, y, vx, vy };
      }));
    }, 25);
    return () => clearInterval(interval);
  }, [phase]);

  return (
    <div className="flex flex-col items-center">
      <div className="relative mb-4">
        <div className="relative w-[280px] h-[260px] rounded-[32px] p-2" style={{ background: 'linear-gradient(180deg, #2d2d3a 0%, #1a1a24 100%)', boxShadow: '0 15px 40px rgba(0,0,0,0.5), inset 0 2px 1px rgba(255,255,255,0.1)' }}>
          <div className="relative w-full h-full rounded-[26px] overflow-hidden" style={{ background: 'linear-gradient(180deg, rgba(20,25,40,0.95) 0%, rgba(10,15,25,0.98) 100%)', boxShadow: 'inset 0 0 50px rgba(0,0,0,0.5)' }}>
            <div className="absolute inset-0 pointer-events-none rounded-[26px]" style={{ background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 40%)' }} />
            <div className="absolute right-0 top-[15%] w-14 h-[65%] z-30">
              <div className="absolute right-1 top-0 w-10 h-6" style={{ background: 'linear-gradient(180deg, #4a4a5a 0%, #3d3d4a 100%)', clipPath: 'polygon(0% 0%, 100% 0%, 85% 100%, 15% 100%)' }} />
              <div className="absolute right-2 top-5 w-8 h-[82%] rounded-b-lg overflow-hidden" style={{ background: 'linear-gradient(90deg, rgba(60,65,80,0.9) 0%, rgba(80,85,100,0.8) 50%, rgba(60,65,80,0.9) 100%)', border: '2px solid rgba(100,105,120,0.4)' }} />
              <div className={`absolute right-3 top-4 w-6 h-2 rounded-full transition-all duration-200 ${catchPhase === 'catching' ? 'bg-amber-400' : 'bg-slate-600'}`} style={{ boxShadow: catchPhase === 'catching' ? '0 0 12px rgba(251,191,36,0.8)' : '0 1px 3px rgba(0,0,0,0.3)' }} />
              {currentCatch && (
                <div className={`absolute right-3 transition-all ease-in-out ${catchPhase === 'catching' ? 'top-5 scale-100 duration-300' : catchPhase === 'rolling' ? 'top-[65%] scale-95 duration-600' : 'top-[80%] scale-90 opacity-0 duration-300'}`}>
                  <Ball number={currentCatch} size="sm" isWinner={true} />
                </div>
              )}
            </div>
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="relative">
                  <div className="w-2 h-2 rounded-full" style={{ background: 'radial-gradient(circle, #60a5fa 0%, #3b82f6 70%)', boxShadow: (phase === 'spinning' || phase === 'selecting') ? '0 0 10px #3b82f6' : '0 0 5px #3b82f680' }} />
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 w-1.5" style={{ height: (phase === 'spinning' || phase === 'selecting') ? '35px' : '18px', background: 'linear-gradient(to top, rgba(96,165,250,0.6), transparent)', filter: 'blur(2px)', animation: 'airJet 0.3s ease-in-out infinite alternate', opacity: (phase === 'spinning' || phase === 'selecting') ? 1 : 0.4 }} />
                </div>
              ))}
            </div>
            {balls.map((ball) => (
              <div key={ball.number} className={`absolute transition-opacity duration-300 ${ball.captured ? 'opacity-0' : 'opacity-100'}`} style={{ left: `${ball.x}%`, top: `${ball.y}%`, transform: 'translate(-50%, -50%) scale(0.8)', zIndex: Math.floor(ball.y) }}>
                <Ball number={ball.number} size="sm" isSpinning={phase === 'spinning' || phase === 'selecting'} />
              </div>
            ))}
          </div>
          <div className="absolute inset-0 rounded-[32px] pointer-events-none" style={{ border: '2px solid rgba(212,175,55,0.4)' }} />
        </div>
        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full" style={{ background: 'linear-gradient(135deg, #d4af37 0%, #b8860b 100%)' }}>
          <span className="text-[8px] font-bold text-gray-900 tracking-wider">LUCKY JACK</span>
        </div>
      </div>
      <div className="px-4 py-3 rounded-xl" style={{ background: 'linear-gradient(180deg, rgba(30,35,50,0.95) 0%, rgba(20,25,35,0.98) 100%)', boxShadow: '0 6px 20px rgba(0,0,0,0.4)', border: '2px solid rgba(212,175,55,0.3)', minWidth: '300px' }}>
        {catchPhase !== 'none' && currentCatch && (
          <div className="text-center mb-3">
            <span className={`text-sm font-bold ${catchPhase === 'catching' ? 'text-amber-400 animate-pulse' : catchPhase === 'rolling' ? 'text-amber-300' : 'text-emerald-400'}`}>
              {catchPhase === 'catching' && '⚡ Ball caught!'}{catchPhase === 'rolling' && '🎱 Rolling...'}{catchPhase === 'revealed' && `✨ Number ${currentCatch}!`}
            </span>
          </div>
        )}
        <div className="flex gap-2 justify-center">
          {[0, 1, 2, 3, 4, 5].map((i) => {
            const ballNumber = selectedBalls[i];
            const isBeingRevealed = catchPhase === 'revealed' && i === selectedBalls.length - 1;
            return (
              <div key={i} className="relative">
                {ballNumber ? (
                  <div className={isBeingRevealed ? 'ball-jump-in' : ''}><Ball number={ballNumber} size="sm" isWinner={true} /></div>
                ) : (
                  <div className={`w-9 h-9 rounded-full border-2 flex items-center justify-center ${phase === 'selecting' && i === selectedBalls.length ? 'border-amber-500 animate-pulse' : 'border-dashed border-slate-600'}`} style={{ background: phase === 'selecting' && i === selectedBalls.length ? 'radial-gradient(circle, rgba(245,158,11,0.15) 0%, transparent 70%)' : 'rgba(30,40,60,0.5)' }}>
                    <span className="text-slate-500 text-sm">{i + 1}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <div className="text-center mt-3">
          {phase === 'idle' && selectedBalls.length === 0 && <span className="text-slate-400 text-sm">Press button to start</span>}
          {phase === 'spinning' && <span className="text-blue-400 text-sm animate-pulse">🌪️ Mixing balls...</span>}
          {phase === 'selecting' && selectedBalls.length < 6 && <span className="text-amber-400 text-sm">Ball {Math.min(selectedBalls.length + 1, 6)} of 6</span>}
          {phase === 'complete' && <span className="text-emerald-400 text-sm">✓ Your lucky numbers!</span>}
        </div>
      </div>
    </div>
  );
};

// EuroMillions Ball Machine (5 balls from 1-50)
const EuroMillionsBallMachine = ({ isProcessing, winningNumbers }) => {
  const [balls, setBalls] = useState([]);
  const [phase, setPhase] = useState('idle');
  const [selectedBalls, setSelectedBalls] = useState([]);
  const [currentCatch, setCurrentCatch] = useState(null);
  const [selectionIndex, setSelectionIndex] = useState(0);
  const [catchPhase, setCatchPhase] = useState('none');
  const [hasInitialized, setHasInitialized] = useState(false);
  const GRAVITY = 0.18, FRICTION = 0.98, BOUNCE = 0.75;

  useEffect(() => {
    const allBalls = Array.from({ length: 50 }, (_, i) => ({
      number: i + 1, x: 12 + (i % 10) * 8 + Math.random() * 3, y: 50 + Math.floor(i / 10) * 8 + Math.random() * 3,
      vx: (Math.random() - 0.5) * 0.5, vy: 0, captured: false
    }));
    setBalls(allBalls);
    setHasInitialized(true);
  }, []);

  useEffect(() => {
    if (isProcessing && (phase === 'idle' || phase === 'complete')) {
      setPhase('spinning'); setSelectedBalls([]); setSelectionIndex(0); setCurrentCatch(null); setCatchPhase('none');
      setBalls(prev => prev.map(b => ({ ...b, captured: false })));
    } else if (!isProcessing && phase === 'spinning' && winningNumbers.length > 0) {
      const delay = setTimeout(() => setPhase('selecting'), 2000);
      return () => clearTimeout(delay);
    }
  }, [isProcessing, winningNumbers, phase]);

  useEffect(() => {
    if (phase === 'selecting' && selectionIndex < winningNumbers.length && catchPhase === 'none') {
      const ballNumber = winningNumbers[selectionIndex];
      setCatchPhase('catching'); setCurrentCatch(ballNumber);
      setBalls(prev => prev.map(b => b.number === ballNumber ? { ...b, captured: true } : b));
      setTimeout(() => setCatchPhase('rolling'), 600);
      setTimeout(() => { setCatchPhase('revealed'); setSelectedBalls(prev => [...prev, ballNumber]); }, 1200);
      setTimeout(() => { setCatchPhase('none'); setCurrentCatch(null); setSelectionIndex(prev => prev + 1); }, 1800);
    } else if (phase === 'selecting' && selectionIndex >= winningNumbers.length && catchPhase === 'none') {
      setPhase('complete');
      setTimeout(() => {
        winningNumbers.forEach((ballNum, idx) => {
          setTimeout(() => {
            setBalls(prev => prev.map(b => b.number === ballNum ? { ...b, captured: false, x: 30 + Math.random() * 40, y: 20, vy: 2, vx: (Math.random() - 0.5) * 2 } : b));
          }, idx * 300 + 800);
        });
        setTimeout(() => { setPhase('idle'); setSelectedBalls([]); }, winningNumbers.length * 300 + 1500);
      }, 3000);
    }
  }, [phase, selectionIndex, winningNumbers, catchPhase]);

  useEffect(() => {
    if (hasInitialized && winningNumbers.length > 0 && phase === 'idle' && selectedBalls.length === 0) {
      setSelectedBalls(winningNumbers); setPhase('complete');
    }
  }, [hasInitialized, winningNumbers, phase, selectedBalls.length]);

  useEffect(() => {
    const interval = setInterval(() => {
      setBalls(prev => prev.map(ball => {
        if (ball.captured) return ball;
        let vx = ball.vx, vy = ball.vy;
        vy += GRAVITY;
        const isSpinning = phase === 'spinning' || phase === 'selecting';
        if (isSpinning) {
          vy -= 0.6; if (ball.y > 50) vy -= 1.4 + Math.random() * 0.6; else if (ball.y > 30) vy -= 0.5;
          vx += (Math.random() - 0.5) * 2.5; vy += (Math.random() - 0.5) * 1.8;
          if (Math.random() < 0.1) { vy -= 3 + Math.random() * 2; vx += (Math.random() - 0.5) * 3; }
        } else {
          vy -= 0.25; if (ball.y > 60) vy -= 0.4 + Math.random() * 0.3;
          vx += (Math.random() - 0.5) * 0.8; vy += (Math.random() - 0.5) * 0.5;
          if (Math.random() < 0.03) vy -= 1.5;
        }
        vx *= FRICTION; vy *= FRICTION;
        const maxV = isSpinning ? 7 : 3;
        vx = Math.max(-maxV, Math.min(maxV, vx)); vy = Math.max(-maxV, Math.min(maxV, vy));
        let x = ball.x + vx, y = ball.y + vy;
        if (x < 6) { x = 6; vx = Math.abs(vx) * BOUNCE; }
        if (x > 84) { x = 84; vx = -Math.abs(vx) * BOUNCE; }
        if (y < 10) { y = 10; vy = Math.abs(vy) * BOUNCE; }
        if (y > 85) { y = 85; vy = -Math.abs(vy) * BOUNCE; }
        return { ...ball, x, y, vx, vy };
      }));
    }, 25);
    return () => clearInterval(interval);
  }, [phase]);

  return (
    <div className="flex flex-col items-center">
      <div className="relative mb-4">
        <div className="relative w-[280px] h-[260px] rounded-[32px] p-2" style={{ background: 'linear-gradient(180deg, #1e3a5f 0%, #0f172a 100%)', boxShadow: '0 15px 40px rgba(0,0,0,0.5), inset 0 2px 1px rgba(255,255,255,0.1)' }}>
          <div className="relative w-full h-full rounded-[26px] overflow-hidden" style={{ background: 'linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', boxShadow: 'inset 0 0 50px rgba(0,0,0,0.5)' }}>
            <div className="absolute inset-0 pointer-events-none rounded-[26px]" style={{ background: 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 40%)' }} />
            <div className="absolute right-0 top-[15%] w-14 h-[65%] z-30">
              <div className="absolute right-1 top-0 w-10 h-6" style={{ background: 'linear-gradient(180deg, #1e40af 0%, #1e3a8a 100%)', clipPath: 'polygon(0% 0%, 100% 0%, 85% 100%, 15% 100%)' }} />
              <div className="absolute right-2 top-5 w-8 h-[82%] rounded-b-lg overflow-hidden" style={{ background: 'linear-gradient(90deg, rgba(30,58,138,0.9) 0%, rgba(59,130,246,0.4) 50%, rgba(30,58,138,0.9) 100%)', border: '2px solid rgba(59,130,246,0.3)' }} />
              <div className={`absolute right-3 top-4 w-6 h-2 rounded-full transition-all duration-200 ${catchPhase === 'catching' ? 'bg-blue-400' : 'bg-slate-600'}`} />
              {currentCatch && (
                <div className={`absolute right-3 transition-all ease-in-out ${catchPhase === 'catching' ? 'top-5 scale-100 duration-300' : catchPhase === 'rolling' ? 'top-[65%] scale-95 duration-600' : 'top-[80%] scale-90 opacity-0 duration-300'}`}>
                  <Ball number={currentCatch} size="sm" isWinner={true} maxNum={50} />
                </div>
              )}
            </div>
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="relative">
                  <div className="w-2 h-2 rounded-full" style={{ background: 'radial-gradient(circle, #fbbf24 0%, #f59e0b 70%)', boxShadow: (phase === 'spinning' || phase === 'selecting') ? '0 0 10px #fbbf24' : '0 0 5px #fbbf2480' }} />
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 w-1.5" style={{ height: (phase === 'spinning' || phase === 'selecting') ? '35px' : '18px', background: 'linear-gradient(to top, rgba(251,191,36,0.6), transparent)', filter: 'blur(2px)', animation: 'airJet 0.3s ease-in-out infinite alternate', opacity: (phase === 'spinning' || phase === 'selecting') ? 1 : 0.4 }} />
                </div>
              ))}
            </div>
            {balls.map((ball) => (
              <div key={ball.number} className={`absolute transition-opacity duration-300 ${ball.captured ? 'opacity-0' : 'opacity-100'}`} style={{ left: `${ball.x}%`, top: `${ball.y}%`, transform: 'translate(-50%, -50%) scale(0.7)', zIndex: Math.floor(ball.y) }}>
                <Ball number={ball.number} size="sm" isSpinning={phase === 'spinning' || phase === 'selecting'} maxNum={50} />
              </div>
            ))}
          </div>
          <div className="absolute inset-0 rounded-[32px] pointer-events-none" style={{ border: '2px solid rgba(59,130,246,0.4)' }} />
        </div>
        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full" style={{ background: 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)' }}>
          <span className="text-[8px] font-bold text-yellow-300 tracking-wider">EUROMILLIONS</span>
        </div>
      </div>
      <div className="px-4 py-3 rounded-xl" style={{ background: 'linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', boxShadow: '0 6px 20px rgba(0,0,0,0.4)', border: '2px solid rgba(59,130,246,0.3)', minWidth: '280px' }}>
        {catchPhase !== 'none' && currentCatch && (
          <div className="text-center mb-3">
            <span className={`text-sm font-bold ${catchPhase === 'catching' ? 'text-blue-400 animate-pulse' : catchPhase === 'rolling' ? 'text-blue-300' : 'text-emerald-400'}`}>
              {catchPhase === 'catching' && '⚡ Ball caught!'}{catchPhase === 'rolling' && '🎱 Rolling...'}{catchPhase === 'revealed' && `✨ Number ${currentCatch}!`}
            </span>
          </div>
        )}
        <div className="flex gap-2 justify-center">
          {[0, 1, 2, 3, 4].map((i) => {
            const ballNumber = selectedBalls[i];
            const isBeingRevealed = catchPhase === 'revealed' && i === selectedBalls.length - 1;
            return (
              <div key={i} className="relative">
                {ballNumber ? (
                  <div className={isBeingRevealed ? 'ball-jump-in' : ''}><Ball number={ballNumber} size="sm" isWinner={true} maxNum={50} /></div>
                ) : (
                  <div className={`w-9 h-9 rounded-full border-2 flex items-center justify-center ${phase === 'selecting' && i === selectedBalls.length ? 'border-blue-500 animate-pulse' : 'border-dashed border-slate-600'}`} style={{ background: phase === 'selecting' && i === selectedBalls.length ? 'radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%)' : 'rgba(15,23,42,0.5)' }}>
                    <span className="text-slate-500 text-sm">{i + 1}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <div className="text-center mt-3">
          {phase === 'idle' && selectedBalls.length === 0 && <span className="text-slate-400 text-sm">Press button to start</span>}
          {phase === 'spinning' && <span className="text-blue-400 text-sm animate-pulse">🌪️ Mixing balls...</span>}
          {phase === 'selecting' && selectedBalls.length < 5 && <span className="text-blue-400 text-sm">Ball {Math.min(selectedBalls.length + 1, 5)} of 5</span>}
          {phase === 'complete' && <span className="text-emerald-400 text-sm">✓ Your lucky numbers!</span>}
        </div>
      </div>
    </div>
  );
};

// Main App
function App() {
  const [lotteryMode, setLotteryMode] = useState('swiss'); // 'swiss' or 'euro'
  const [prediction, setPrediction] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPersonal, setShowPersonal] = useState(false);
  const [showBonus, setShowBonus] = useState(false);
  const [showLocks, setShowLocks] = useState(false);
  const [showMultiTickets, setShowMultiTickets] = useState(false);
  const [wheelSpinning, setWheelSpinning] = useState(false);
  const [birthday, setBirthday] = useState("");
  const [fullName, setFullName] = useState("");
  const [lockedPositions, setLockedPositions] = useState({ p1: "", p2: "", p3: "", p4: "", p5: "", p6: "" });
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
  const [ticketCounter, setTicketCounter] = useState(0);
  const [isUnlimited, setIsUnlimited] = useState(false);
  const [generatorStatus, setGeneratorStatus] = useState({ open: true, reason: '', reopensAt: null });
  const [showCodeInput, setShowCodeInput] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoMsg, setPromoMsg] = useState(null);
  const [nextDrawTickets, setNextDrawTickets] = useState(0);
  const [nextDrawDate, setNextDrawDate] = useState('');
  const [pendingTickets, setPendingTickets] = useState([]);
  const [pendingTotal, setPendingTotal] = useState(0);
  // 🎻 Random vs E reality-check box (DJ canon 29.04.2026)
  const [randomVsE, setRandomVsE] = useState(null);
  const [archiveFiles, setArchiveFiles] = useState([]);
  const [openArchive, setOpenArchive] = useState(null);
  // 📦 Full ticket archive (per target_date, loaded on demand)
  const [archiveByDate, setArchiveByDate] = useState({});       // { 'dd.mm.yyyy': { tickets: [], loading: bool } }
  const [archiveDateOpen, setArchiveDateOpen] = useState(null);  // which draw date is expanded
  const [rareSeed, setRareSeed] = useState(null);
  const [djCalls, setDjCalls] = useState(null);
  const [jackPicks, setJackPicks] = useState({ mains: [], stars: [] });
  const [huntBoxes, setHuntBoxes] = useState([]);       // active hunt boxes for current mode
  const [huntTickets, setHuntTickets] = useState({});    // { boxId: [tickets...] }
  const [huntLoading, setHuntLoading] = useState(false);
  const [huntSuspectInput, setHuntSuspectInput] = useState("");
  const [sidebarFolded, setSidebarFolded] = useState(() => {
    try { return localStorage.getItem('lj_sidebar_folded') === '1'; } catch (e) { return false; }
  });
  const toggleSidebar = () => {
    setSidebarFolded(prev => {
      const next = !prev;
      try { localStorage.setItem('lj_sidebar_folded', next ? '1' : '0'); } catch (e) {}
      return next;
    });
  };
  const [diagnostics, setDiagnostics] = useState(null);
  const [activeUsers, setActiveUsers] = useState(0);
  const [totalUsers, setTotalUsers] = useState(0);
  
  // Special personas with secret number modifiers
  // The magic is hidden - only the generator knows!
  const [activePersonas, setActivePersonas] = useState([]);
  const personas = [
    { name: "Avi", modifier: "+1" },
    { name: "Olivia", modifier: "-1" },
    { name: "Dathi", modifier: "+1" }
  ];
  
  // Toggle persona selection (allow multiple for Avi+Dathi)
  const togglePersona = (personaName) => {
    setActivePersonas(prev => {
      if (prev.includes(personaName)) {
        // Deselect
        return prev.filter(p => p !== personaName);
      } else {
        // If selecting Olivia, clear others (Olivia is exclusive)
        if (personaName === "Olivia") {
          return ["Olivia"];
        }
        // If Olivia was selected and now selecting Avi or Dathi, replace
        if (prev.includes("Olivia")) {
          return [personaName];
        }
        // Allow Avi + Dathi together
        return [...prev, personaName];
      }
    });
  };
  const [numTickets, setNumTickets] = useState(2);
  const [generationMode, setGenerationMode] = useState('jackpot'); // 'jackpot' or 'money'
  const [oliviaKiss, setOliviaKiss] = useState(false);
  const [showKissHearts, setShowKissHearts] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateMessage, setUpdateMessage] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [historyStats, setHistoryStats] = useState(null);
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncResult, setSyncResult] = useState(null);
  
  // Hit Tracker State
  const [showHitTracker, setShowHitTracker] = useState(false);
  const [lastDraw, setLastDraw] = useState(null);
  const [generationHistory, setGenerationHistory] = useState([]);
  const [hitStats, setHitStats] = useState(null);
  const [hitTrackerLoading, setHitTrackerLoading] = useState(false);
  const [storyTickets, setStoryTickets] = useState(null);
  const [storyLoading, setStoryLoading] = useState(false);
  const [perDrawStats, setPerDrawStats] = useState([]);
  // 🎯 S40.2 — Hit Tracker "Full File" toggle (DJ canon 16.05.2026)
  const [hitTrackerFullFile, setHitTrackerFullFile] = useState(false);
  
  // Sleeper Radar State
  const [showSleeperRadar, setShowSleeperRadar] = useState(false);
  const [sleeperData, setSleeperData] = useState(null);
  const [sleeperLoading, setSleeperLoading] = useState(false);
  
  // Swiss Sleeper State
  const [showSwissSleepers, setShowSwissSleepers] = useState(false);
  const [swissSleeperData, setSwissSleeperData] = useState(null);
  const [swissSleeperLoading, setSwissSleeperLoading] = useState(false);

  // 🧠 E's Cosmic Brain State (Session 30)
  const [showCosmicBrain, setShowCosmicBrain] = useState(false);
  const [cosmicBrainLoading, setCosmicBrainLoading] = useState(false);
  const [cosmicBrainData, setCosmicBrainData] = useState(null);
  const [brainTargetDate, setBrainTargetDate] = useState('05.05.2026');
  const [brainSeedMains, setBrainSeedMains] = useState('3,9,42,46,47');
  const [brainSeedStars, setBrainSeedStars] = useState('1,11');
  const [brainPinMains, setBrainPinMains] = useState('');
  const [brainPinStars, setBrainPinStars] = useState('');

  // 🎻 DJ "We Think That..." 3 Big Suspects (Session 31)
  const [djSuspects, setDjSuspects] = useState(null);
  const [djSuspectsEdit, setDjSuspectsEdit] = useState(false);
  const [djSuspectsInput, setDjSuspectsInput] = useState('');
  const [djSuspectsNote, setDjSuspectsNote] = useState('');
  const [djSuspectsTarget, setDjSuspectsTarget] = useState('');

  // 👻 Ghost Counting Engine — Session 33 (Wed/Sat separated)
  const [showGhostLedger, setShowGhostLedger] = useState(false);
  const [ghostLedgerData, setGhostLedgerData] = useState(null);
  const [ghostLedgerLoading, setGhostLedgerLoading] = useState(false);
  const [ghostTargetDate, setGhostTargetDate] = useState('06.05.2026');

  // 🎼 Cosmic Voices — Session 34 (10 lenses + convergence)
  const [showCosmicVoices, setShowCosmicVoices] = useState(false);
  const [cosmicVoicesData, setCosmicVoicesData] = useState(null);
  const [cosmicVoicesLoading, setCosmicVoicesLoading] = useState(false);
  const [cosmicVoicesTarget, setCosmicVoicesTarget] = useState('08.05.2026');
  const [cosmicVoicesPins, setCosmicVoicesPins] = useState('');

  // 🚪 Ghost Engine — Session 38/39 (`?+Pa=Pb` doors, 9-10d deep-sleep, chainless cash-windows)
  const [showGhostEngine, setShowGhostEngine] = useState(false);
  const [ghostEngineData, setGhostEngineData] = useState(null);
  const [ghostEngineLoading, setGhostEngineLoading] = useState(false);
  const [ghostEngineTarget, setGhostEngineTarget] = useState('13.05.2026');
  const [ghostEngineLookback, setGhostEngineLookback] = useState(10);
  // 🎬 Cosmic Replay slider — walks historical quarters forward d-by-d
  const [replayMode, setReplayMode] = useState(false);
  const [replayDates, setReplayDates] = useState([]); // list of dd.mm.yyyy in selected Q
  const [replayIdx, setReplayIdx] = useState(0);
  const [replayLoading, setReplayLoading] = useState(false);

  // 📖 Story Composer — Session 40 (DJ canon: fuses Brain + Ghost + Hungry + Prince)
  const [showStoryComposer, setShowStoryComposer] = useState(false);
  const [storyComposerData, setStoryComposerData] = useState(null);
  const [storyComposerLoading, setStoryComposerLoading] = useState(false);
  const [storyComposerTarget, setStoryComposerTarget] = useState('13.05.2026');
  const [storyComposerCount, setStoryComposerCount] = useState(10);
  const [storyExpandedIdx, setStoryExpandedIdx] = useState(null);

  // 🎫 Sneaky Universe Symphony — Session 35
  const [sneakySymphonyData, setSneakySymphonyData] = useState(null);
  const [sneakySymphonyLoading, setSneakySymphonyLoading] = useState(false);
  
  // 2Chance State
  const [show2Chance, setShow2Chance] = useState(false);
  const [twoChanceResults, setTwoChanceResults] = useState(null);
  const [twoChanceHistory, setTwoChanceHistory] = useState([]);
  const [twoChanceChecking, setTwoChanceChecking] = useState(false);

  // Sync latest lottery results from external sources
  const syncLatestResults = async () => {
    setSyncLoading(true);
    setSyncResult(null);
    try {
      const res = await axios.post(`${API}/sync-results`);
      setSyncResult(res.data);
      // Refresh stats after sync
      fetchStats();
      // Also refresh last draw
      fetchLastDraw();
    } catch (e) {
      console.error("Sync error:", e);
      setSyncResult({ error: "Failed to sync results" });
    } finally {
      setSyncLoading(false);
    }
  };
  
  // Fetch last draw result - based on lottery mode
  const fetchLastDraw = async () => {
    try {
      const endpoint = lotteryMode === 'swiss' 
        ? `${API}/last-draw` 
        : `${API}/euromillions/draws?limit=1`;
      const res = await axios.get(endpoint);
      
      if (lotteryMode === 'euro') {
        // Transform EuroMillions response
        const draws = res.data.draws || res.data;
        if (draws && draws.length > 0) {
          const lastEuroDraw = draws[0];
          setLastDraw({
            date: lastEuroDraw.date,
            numbers: lastEuroDraw.numbers,
            stars: lastEuroDraw.stars,
            lucky_number: null, // EuroMillions doesn't have lucky number
            replay_number: null
          });
        }
      } else {
        setLastDraw(res.data);
      }
    } catch (e) {
      console.error("Error fetching last draw:", e);
    }
  };
  
  // Fetch generation history with hits — UNIFIED for both Swiss and Euro
  const fetchGenerationHistory = async () => {
    setHitTrackerLoading(true);
    try {
      if (lotteryMode === 'euro') {
        const res = await axios.get(`${API}/euromillions/generation-history?limit=30`, { timeout: 20000 });
        setGenerationHistory(res.data.generations || []);
        setPerDrawStats(res.data.per_draw_stats || []);
      } else {
        // Use the new clean hit-tracker endpoint for Swiss
        // 🎯 S40.2 — `include_all=true` returns EVERY ticket per draw (full file)
        const allParam = hitTrackerFullFile ? '&include_all=true' : '';
        const res = await axios.get(`${API}/hit-tracker?last_draws=4&limit=200${allParam}`, { timeout: 20000 });
        setGenerationHistory(res.data.results || []);
        setLastDraw(res.data.last_draws?.[0] || null);
        setPerDrawStats(res.data.per_draw_stats || []);
      }
    } catch (e) {
      console.error("Error fetching generation history:", e);
      // graceful fallback so "Loading..." never sticks forever
      setGenerationHistory([]);
      setPerDrawStats([]);
    } finally {
      setHitTrackerLoading(false);
    }
  };

  // 📦 Load the FULL archive for a specific target_date (lazy on first expand)
  const loadArchiveForDate = async (targetDate) => {
    if (archiveByDate[targetDate]?.tickets) return;
    setArchiveByDate((prev) => ({ ...prev, [targetDate]: { tickets: [], loading: true } }));
    try {
      const mode = lotteryMode === 'euro' ? 'euro' : 'swiss';
      const res = await axios.get(`${API}/tickets-archive?mode=${mode}&target_date=${encodeURIComponent(targetDate)}&limit=1000`);
      setArchiveByDate((prev) => ({
        ...prev,
        [targetDate]: { tickets: res.data.tickets || [], loading: false, total: res.data.total_tickets || 0 },
      }));
    } catch (e) {
      console.error('Archive load error:', e);
      setArchiveByDate((prev) => ({ ...prev, [targetDate]: { tickets: [], loading: false, error: true } }));
    }
  };

  const toggleArchiveDate = (td) => {
    if (archiveDateOpen === td) {
      setArchiveDateOpen(null);
    } else {
      setArchiveDateOpen(td);
      loadArchiveForDate(td);
    }
  };
  
  // Fetch overall hit stats - based on lottery mode
  const fetchHitStats = async () => {
    try {
      const endpoint = lotteryMode === 'euro'
        ? `${API}/euromillions/hit-stats`
        : `${API}/hit-stats`;
      const res = await axios.get(endpoint);
      setHitStats(res.data);
    } catch (e) {
      console.error("Error fetching hit stats:", e);
    }
  };
  
  // 🎻 Fetch the random-vs-engine box for current mode (last completed draw)
  const fetchRandomVsE = async () => {
    try {
      const url = `${API}/random-vs-engine?mode=${lotteryMode}`;
      const res = await axios.get(url);
      setRandomVsE(res.data);
    } catch (e) {
      console.error('random-vs-engine fetch failed:', e);
    }
  };

  // Generate story tickets and save for tracking - based on lottery mode
  const generateStoryTickets = async () => {
    setStoryLoading(true);
    try {
      const endpoint = lotteryMode === 'euro'
        ? `${API}/euromillions/story-generator-save`
        : `${API}/story-generator-save`;
      const res = await axios.get(endpoint);
      setStoryTickets(res.data);
      // Refresh history after generating
      fetchGenerationHistory();
      fetchHitStats();
    } catch (e) {
      console.error("Error generating story tickets:", e);
    } finally {
      setStoryLoading(false);
    }
  };
  
  // Calculate hits for a specific generation - based on lottery mode
  const calculateHits = async (generationId) => {
    try {
      const endpoint = lotteryMode === 'euro'
        ? `${API}/euromillions/calculate-hits/${generationId}`
        : `${API}/calculate-hits/${generationId}`;
      const res = await axios.post(endpoint);
      // Refresh history to show updated hits
      fetchGenerationHistory();
      fetchHitStats();
      return res.data;
    } catch (e) {
      console.error("Error calculating hits:", e);
    }
  };
  
  // Recalculate all pending hits - based on lottery mode
  const recalculateAllHits = async () => {
    setHitTrackerLoading(true);
    try {
      const endpoint = lotteryMode === 'euro'
        ? `${API}/euromillions/recalculate-all-hits`
        : `${API}/recalculate-all-hits`;
      await axios.post(endpoint);
      fetchGenerationHistory();
      fetchHitStats();
    } catch (e) {
      console.error("Error recalculating hits:", e);
    } finally {
      setHitTrackerLoading(false);
    }
  };
  
  // Load hit tracker data when section is opened (also re-loads when toggle flips)
  useEffect(() => {
    if (showHitTracker) {
      fetchLastDraw();
      fetchGenerationHistory();
      fetchHitStats();
    }
  }, [showHitTracker, lotteryMode, hitTrackerFullFile]);
  
  // Sleeper Radar fetch
  const fetchSleeperForecast = async () => {
    setSleeperLoading(true);
    try {
      const res = await axios.get(`${API}/euromillions/sleeper-forecast`);
      setSleeperData(res.data);
    } catch (e) {
      console.error("Error fetching sleeper forecast:", e);
    } finally {
      setSleeperLoading(false);
    }
  };
  
  // Load sleeper data when panel is opened (EuroMillions only)
  // 🌠 Also refetch on nextDrawDate change so the radar updates every d.
  useEffect(() => {
    if (showSleeperRadar && lotteryMode === 'euro') {
      fetchSleeperForecast();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showSleeperRadar, lotteryMode, nextDrawDate]);

  // Swiss Sleeper fetch
  const fetchSwissSleepers = async () => {
    setSwissSleeperLoading(true);
    try {
      const res = await axios.get(`${API}/swiss-sleepers`);
      setSwissSleeperData(res.data);
    } catch (e) {
      console.error("Error fetching swiss sleepers:", e);
    } finally {
      setSwissSleeperLoading(false);
    }
  };

  useEffect(() => {
    if (showSwissSleepers && lotteryMode === 'swiss') {
      fetchSwissSleepers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showSwissSleepers, lotteryMode, nextDrawDate]);

  // 🎻 Load DJ Suspects on mount + when lotteryMode changes
  const loadDjSuspects = async () => {
    try {
      const mode = lotteryMode === 'euro' ? 'euro' : 'swiss';
      const res = await axios.get(`${API}/dj-suspects?mode=${mode}`);
      setDjSuspects(res.data);
      setDjSuspectsInput((res.data?.suspects || []).join(','));
      setDjSuspectsNote(res.data?.note || '');
      setDjSuspectsTarget(res.data?.target_date || '');
    } catch (e) {
      console.error("DJ suspects load error:", e);
    }
  };

  const saveDjSuspects = async () => {
    try {
      const mode = lotteryMode === 'euro' ? 'euro' : 'swiss';
      const arr = djSuspectsInput.split(',').map(s => parseInt(s.trim(), 10)).filter(n => Number.isFinite(n)).slice(0, 3);
      if (arr.length === 0) { alert('🎻 Drop 1-3 suspect numbers (comma-separated).'); return; }
      await axios.post(`${API}/dj-suspects`, {
        mode,
        target_date: djSuspectsTarget || '',
        suspects: arr,
        note: djSuspectsNote,
      });
      setDjSuspectsEdit(false);
      await loadDjSuspects();
    } catch (e) {
      console.error("DJ suspects save error:", e);
      alert(`Save failed: ${e?.response?.data?.error || e.message}`);
    }
  };

  useEffect(() => { loadDjSuspects(); /* eslint-disable-next-line */ }, [lotteryMode]);

  // 🧠 E's Cosmic Brain — run on demand (Session 30)
  const runCosmicBrain = async () => {
    setCosmicBrainLoading(true);
    try {
      const params = new URLSearchParams({
        seed_mains: brainSeedMains,
        seed_stars: brainSeedStars,
      });
      if (brainPinMains.trim()) params.append('pin_mains', brainPinMains);
      if (brainPinStars.trim()) params.append('pin_stars', brainPinStars);
      const res = await axios.get(
        `${API}/dj-orchestra/${brainTargetDate}?${params.toString()}`
      );
      setCosmicBrainData(res.data);
    } catch (e) {
      console.error("Cosmic Brain error:", e);
      setCosmicBrainData({ error: e.message });
    } finally {
      setCosmicBrainLoading(false);
    }
  };

  // 👻 Ghost Counter — Session 33 (Wed/Sat separated)
  const fetchGhostLedger = async () => {
    setGhostLedgerLoading(true);
    try {
      const m = lotteryMode === 'euro' ? 'euro' : 'swiss';
      const res = await axios.get(`${API}/ghost-counter/${ghostTargetDate}/${m}?weekday_split=true`);
      setGhostLedgerData(res.data);
    } catch (e) {
      console.error("Ghost Ledger error:", e);
      setGhostLedgerData({ error: e.message });
    } finally {
      setGhostLedgerLoading(false);
    }
  };

  // 🎼 Cosmic Voices — Session 34 (10 lenses + convergence)
  const fetchCosmicVoices = async () => {
    setCosmicVoicesLoading(true);
    try {
      const m = lotteryMode === 'euro' ? 'euro' : 'swiss';
      const pinParam = cosmicVoicesPins ? `&pin_mains=${encodeURIComponent(cosmicVoicesPins)}` : '';
      const res = await axios.get(`${API}/cosmic-voices/${cosmicVoicesTarget}/${m}?lens=all${pinParam}`);
      setCosmicVoicesData(res.data);
    } catch (e) {
      console.error("Cosmic Voices error:", e);
      setCosmicVoicesData({ error: e.message });
    } finally {
      setCosmicVoicesLoading(false);
    }
  };

  // 🎫 Sneaky Universe Symphony — Session 35
  const fetchSneakySymphony = async () => {
    setSneakySymphonyLoading(true);
    try {
      const pinParam = cosmicVoicesPins ? `?pin_mains=${encodeURIComponent(cosmicVoicesPins)}` : '';
      const res = await axios.get(`${API}/sneaky-symphony/${cosmicVoicesTarget}/euro${pinParam}`);
      setSneakySymphonyData(res.data);
    } catch (e) {
      console.error("Sneaky Symphony error:", e);
      setSneakySymphonyData({ error: e.message });
    } finally {
      setSneakySymphonyLoading(false);
    }
  };

  // 🚪 Ghost Engine — Session 38/39 (`?+Pa=Pb` doors)
  const fetchGhostEngine = async (overrideDate = null) => {
    setGhostEngineLoading(true);
    try {
      const m = lotteryMode === 'euro' ? 'euro' : 'swiss';
      const dt = overrideDate || ghostEngineTarget;
      const res = await axios.get(
        `${API}/ghost-ledger/${dt}/${m}?lookback=${ghostEngineLookback}`
      );
      setGhostEngineData(res.data);
    } catch (e) {
      console.error("Ghost Engine error:", e);
      setGhostEngineData({ error: e.message });
    } finally {
      setGhostEngineLoading(false);
    }
  };

  // 📖 Story Composer — Session 40 — fuses Brain + Ghost + Hungry + Prince
  const fetchStoryComposer = async () => {
    setStoryComposerLoading(true);
    try {
      const m = lotteryMode === 'euro' ? 'euro' : 'swiss';
      const res = await axios.get(
        `${API}/story-tickets/${storyComposerTarget}/${m}?count=${storyComposerCount}`
      );
      setStoryComposerData(res.data);
      setStoryExpandedIdx(null);
    } catch (e) {
      console.error("Story Composer error:", e);
      setStoryComposerData({ error: e.message });
    } finally {
      setStoryComposerLoading(false);
    }
  };

  // 🎬 Cosmic Replay — build the slider date list using ghost-ledger's window
  const buildReplayDates = async () => {
    setReplayLoading(true);
    try {
      const m = lotteryMode === 'euro' ? 'euro' : 'swiss';
      // Pull a wide window (30 d) for the slider
      const res = await axios.get(
        `${API}/ghost-ledger/${ghostEngineTarget}/${m}?lookback=30`
      );
      const dates = (res.data?.draws_window || [])
        .map((d) => d.date)
        .filter(Boolean);
      if (dates.length > 0) {
        // Add the current target as the last stop on the timeline
        const timeline = [...dates, ghostEngineTarget];
        setReplayDates(timeline);
        setReplayIdx(timeline.length - 1);
        setGhostEngineData(res.data);
      }
    } catch (e) {
      console.error('Replay build error:', e);
    } finally {
      setReplayLoading(false);
    }
  };
  const stepReplay = async (delta) => {
    const next = Math.min(replayDates.length - 1, Math.max(0, replayIdx + delta));
    if (next === replayIdx) return;
    setReplayIdx(next);
    const dt = replayDates[next];
    setGhostEngineTarget(dt);
    await fetchGhostEngine(dt);
  };
  
  // 🧠 Swiss Brain — Session 37 (10-ticket Swiss symphony)
  const [swissBrainData, setSwissBrainData] = useState(null);
  const [swissBrainLoading, setSwissBrainLoading] = useState(false);
  const [swissBrainTarget, setSwissBrainTarget] = useState('2026-05-09');
  const [swissBrainEnvelopes, setSwissBrainEnvelopes] = useState('');
  const fetchSwissBrain = async () => {
    setSwissBrainLoading(true);
    try {
      const envParam = swissBrainEnvelopes ? `&extra_envelopes=${encodeURIComponent(swissBrainEnvelopes)}` : '';
      const res = await axios.get(`${API}/swiss-symphony/${swissBrainTarget}?count=10${envParam}`);
      setSwissBrainData(res.data);
    } catch (e) {
      console.error("Swiss Brain error:", e);
      setSwissBrainData({ error: e.message });
    } finally {
      setSwissBrainLoading(false);
    }
  };

  // 2Chance functions
  const check2ChanceHits = async () => {
    setTwoChanceChecking(true);
    try {
      const res = await axios.post(`${API}/euromillions/2chance/check`);
      setTwoChanceResults(res.data.results || []);
    } catch (e) {
      console.error("Error checking 2Chance:", e);
    } finally {
      setTwoChanceChecking(false);
    }
  };
  
  const fetch2ChanceHistory = async () => {
    try {
      const res = await axios.get(`${API}/euromillions/2chance/results`);
      setTwoChanceHistory(res.data.draws || []);
    } catch (e) {
      console.error("Error fetching 2Chance history:", e);
    }
  };
  
  useEffect(() => {
    if (show2Chance && lotteryMode === 'euro') {
      fetch2ChanceHistory();
    }
  }, [show2Chance, lotteryMode]);
  
  // Fetch last draw on initial load and when lottery mode changes
  useEffect(() => {
    fetchLastDraw();
    // Clear story tickets when switching modes
    setStoryTickets(null);
    // Refresh generation history for the new mode
    if (showHitTracker) {
      fetchGenerationHistory();
      fetchHitStats();
    }
  }, [lotteryMode]);

  // Ticket counter — fetch on load and after generations
  const fetchTicketCounter = async () => {
    try {
      const res = await axios.get(`${API}/ticket-counter`);
      setTicketCounter(res.data.total || 0);
      setNextDrawTickets(res.data.next_draw_tickets || 0);
      setNextDrawDate(res.data.next_draw_date || '');
    } catch (e) {}
  };
  const fetchPendingTickets = async () => {
    try {
      // 🎻 Pass visitor_id so backend can pin user's own locked tickets first
      const vid = localStorage.getItem('lj_visitor_id') || '';
      const url = vid
        ? `${API}/pending-tickets?mode=${lotteryMode}&visitor_id=${encodeURIComponent(vid)}`
        : `${API}/pending-tickets?mode=${lotteryMode}`;
      const res = await axios.get(url);
      setPendingTickets(res.data.tickets || []);
      setPendingTotal(res.data.count || 0);
      setArchiveFiles(res.data.archive_files || []);
      setNextDrawDate(res.data.next_date || '');
      setRareSeed(res.data.rare_seed || null);
      setDjCalls(res.data.dj_calls || null);
      setDiagnostics(res.data.diagnostics || null);
    } catch (e) {}
  };
  // 🎯 Hunt Box — fetch active boxes and their tickets for current mode
  const fetchHuntBoxes = async () => {
    try {
      const res = await axios.get(`${API}/hunt-box/active?mode=${lotteryMode === 'swiss' ? 'swiss' : 'euro'}`);
      const boxes = res.data.boxes || [];
      // If no boxes exist for Euro, auto-seed the default (P5=50 with 10,27,32)
      if (boxes.length === 0 && lotteryMode === 'euro') {
        try {
          const seed = await axios.post(`${API}/hunt-box/seed-default`);
          if (seed.data.box) boxes.push(seed.data.box);
        } catch (e) {}
      }
      setHuntBoxes(boxes);
      // Fetch tickets for each box
      const ticketMap = {};
      for (const b of boxes) {
        try {
          const tr = await axios.get(`${API}/hunt-box/${b.id}/tickets`);
          ticketMap[b.id] = tr.data.tickets || [];
        } catch (e) { ticketMap[b.id] = []; }
      }
      setHuntTickets(ticketMap);
    } catch (e) {}
  };
  const refreshHuntBox = async (boxId) => {
    setHuntLoading(true);
    try {
      const tr = await axios.get(`${API}/hunt-box/${boxId}/tickets`);
      setHuntTickets(prev => ({ ...prev, [boxId]: tr.data.tickets || [] }));
    } catch (e) {}
    setHuntLoading(false);
  };
  const addHuntSuspect = async (boxId, n) => {
    const box = huntBoxes.find(b => b.id === boxId);
    if (!box) return;
    const next = Array.from(new Set([...(box.jack_picks || []), n])).sort((a,b) => a-b);
    try {
      await axios.put(`${API}/hunt-box/${boxId}/suspects`, { jack_picks: next });
      setHuntBoxes(prev => prev.map(b => b.id === boxId ? { ...b, jack_picks: next } : b));
      await refreshHuntBox(boxId);
    } catch (e) {}
  };
  const removeHuntSuspect = async (boxId, n) => {
    const box = huntBoxes.find(b => b.id === boxId);
    if (!box) return;
    const next = (box.jack_picks || []).filter(x => x !== n);
    try {
      await axios.put(`${API}/hunt-box/${boxId}/suspects`, { jack_picks: next });
      setHuntBoxes(prev => prev.map(b => b.id === boxId ? { ...b, jack_picks: next } : b));
      await refreshHuntBox(boxId);
    } catch (e) {}
  };
  // 🎻 Check VIP/unlimited status from backend
  const fetchUnlimitedStatus = async () => {
    try {
      const vid = localStorage.getItem('lj_visitor_id') || '';
      const mode = lotteryMode === 'swiss' ? 'swiss' : 'euromillions';
      const url = vid
        ? `${API}/ticket-limit?visitor_id=${encodeURIComponent(vid)}&mode=${mode}`
        : `${API}/ticket-limit?mode=${mode}`;
      const res = await axios.get(url);
      setIsUnlimited(!!res.data.unlimited);
      // 🕒 Pick up generator open/closed status
      setGeneratorStatus({
        open: res.data.generator_open !== false,
        reason: res.data.closed_reason || '',
        reopensAt: res.data.reopens_at || null,
      });
    } catch (e) {}
  };
  // 🎻 Redeem promo code
  const redeemPromoCode = async () => {
    const vid = localStorage.getItem('lj_visitor_id') || '';
    if (!vid) { setPromoMsg({ ok: false, text: 'Please wait — loading...' }); return; }
    if (!promoCode.trim()) { setPromoMsg({ ok: false, text: 'Enter a code' }); return; }
    try {
      const res = await axios.post(`${API}/redeem-code`, { visitor_id: vid, code: promoCode.trim() });
      setIsUnlimited(!!res.data.unlimited);
      setPromoMsg({ ok: true, text: res.data.message || 'VIP unlocked!' });
      setPromoCode('');
      setTimeout(() => setShowCodeInput(false), 1200);
    } catch (e) {
      setPromoMsg({ ok: false, text: e.response?.data?.detail || 'Invalid code' });
    }
  };
  useEffect(() => { fetchTicketCounter(); fetchPendingTickets(); fetchUnlimitedStatus(); fetchHuntBoxes(); fetchRandomVsE(); }, [lotteryMode]);
  // 🕒 Refresh generator open/closed status every 60s so UI flips when cutoff opens/closes
  useEffect(() => {
    const id = setInterval(fetchUnlimitedStatus, 60000);
    return () => clearInterval(id);
  }, [lotteryMode]);

  // ─── ACTIVE USER HEARTBEAT ───────────────────────
  useEffect(() => {
    let vid = localStorage.getItem('lj_visitor_id');
    if (!vid) {
      vid = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2) + Date.now().toString(36);
      localStorage.setItem('lj_visitor_id', vid);
    }
    const sendHeartbeat = async () => {
      try {
        const res = await axios.post(`${API}/heartbeat`, { visitor_id: vid });
        setActiveUsers(res.data.active_users || 0);
        setTotalUsers(res.data.total_users || 0);
      } catch (e) {}
    };
    sendHeartbeat();
    const interval = setInterval(sendHeartbeat, 60000); // every 60s
    return () => clearInterval(interval);
  }, []);

  // Olivia's Kiss of Luck function - MIXES DIGITS from P1, P2, P3!
  // Falls back to Circle Math (±25) when mixing isn't possible
  const giveKissOfLuck = () => {
    const nums = prediction?.main_prediction;
    if (!prediction || !nums || nums.length < 3) return;
    
    setOliviaKiss(true);
    setShowKissHearts(true);
    
    // Get first 3 numbers (P1, P2, P3)
    const p1 = nums[0];
    const p2 = nums[1];
    const p3 = nums[2];
    
    // Extract all digits from P1, P2, P3
    const allDigits = [...String(p1), ...String(p2), ...String(p3)].map(d => parseInt(d));
    
    const maxNum = lotteryMode === 'swiss' ? 42 : 50;
    const kissedNumbers = [];
    const usedNums = new Set(nums);
    
    // Try to create numbers by mixing digits
    const tryMixDigits = () => {
      const results = [];
      for (let attempt = 0; attempt < 3; attempt++) {
        let newNum = null;
        let tries = 0;
        
        while (tries < 30 && newNum === null) {
          // Shuffle digits
          const shuffled = [...allDigits].sort(() => Math.random() - 0.5);
          
          // Try different combinations
          const candidates = [];
          
          // Two digit combinations
          for (let i = 0; i < shuffled.length; i++) {
            for (let j = 0; j < shuffled.length; j++) {
              if (i !== j) {
                const num = shuffled[i] * 10 + shuffled[j];
                if (num >= 1 && num <= maxNum) candidates.push(num);
              }
            }
          }
          
          // Single digits
          for (const d of shuffled) {
            if (d >= 1 && d <= maxNum) candidates.push(d);
          }
          
          // Pick a valid one
          const validCandidates = candidates.filter(n => 
            !usedNums.has(n) && !results.includes(n)
          );
          
          if (validCandidates.length > 0) {
            newNum = validCandidates[Math.floor(Math.random() * validCandidates.length)];
          }
          tries++;
        }
        
        if (newNum !== null) {
          results.push(newNum);
          usedNums.add(newNum);
        }
      }
      return results;
    };
    
    // Circle Math fallback: n + 25 or n - 25
    const circleNumber = (n) => {
      const plus = n + 25;
      const minus = n - 25;
      const candidates = [];
      if (plus <= maxNum && !usedNums.has(plus)) candidates.push(plus);
      if (minus >= 1 && !usedNums.has(minus)) candidates.push(minus);
      if (candidates.length > 0) {
        return candidates[Math.floor(Math.random() * candidates.length)];
      }
      return null;
    };
    
    // Try mixing first
    let mixedNums = tryMixDigits();
    
    // If we couldn't get 3 numbers from mixing, use Circle Math for remaining
    const originalNums = [p1, p2, p3];
    let circleUsed = false;
    
    while (mixedNums.length < 3) {
      const sourceNum = originalNums[mixedNums.length];
      const circled = circleNumber(sourceNum);
      if (circled !== null) {
        mixedNums.push(circled);
        usedNums.add(circled);
        circleUsed = true;
      } else {
        // Last resort: find any unused number
        for (let n = 1; n <= maxNum; n++) {
          if (!usedNums.has(n)) {
            mixedNums.push(n);
            usedNums.add(n);
            break;
          }
        }
      }
    }
    
    // Update prediction with kissed P1, P2, P3
    if (mixedNums.length >= 3) {
      const newNumbers = [...nums];
      newNumbers[0] = mixedNums[0];
      newNumbers[1] = mixedNums[1];
      newNumbers[2] = mixedNums[2];
      
      // Sort to maintain order
      newNumbers.sort((a, b) => a - b);
      
      setPrediction(prev => ({
        ...prev,
        main_prediction: newNumbers,
        kissed: true,
        originalNumbers: prev.originalNumbers || prev.main_prediction,
        kissedFrom: [p1, p2, p3],
        kissedTo: mixedNums,
        circleUsed: circleUsed
      }));
    }
    
    // Play casino coins falling sound using Web Audio API
    const playCoinSound = () => {
      try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        // Create multiple coin drop sounds in sequence
        for (let i = 0; i < 8; i++) {
          const osc = audioCtx.createOscillator();
          const gain = audioCtx.createGain();
          
          osc.connect(gain);
          gain.connect(audioCtx.destination);
          
          // High metallic coin sound
          osc.frequency.setValueAtTime(2000 + Math.random() * 3000, audioCtx.currentTime + i * 0.08);
          osc.frequency.exponentialRampToValueAtTime(800 + Math.random() * 500, audioCtx.currentTime + i * 0.08 + 0.05);
          osc.type = 'square';
          
          gain.gain.setValueAtTime(0.15, audioCtx.currentTime + i * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + i * 0.08 + 0.12);
          
          osc.start(audioCtx.currentTime + i * 0.08);
          osc.stop(audioCtx.currentTime + i * 0.08 + 0.12);
        }
        
        // Final jackpot chime
        setTimeout(() => {
          const osc2 = audioCtx.createOscillator();
          const gain2 = audioCtx.createGain();
          osc2.connect(gain2);
          gain2.connect(audioCtx.destination);
          osc2.frequency.setValueAtTime(1200, audioCtx.currentTime);
          osc2.frequency.setValueAtTime(1600, audioCtx.currentTime + 0.1);
          osc2.frequency.setValueAtTime(2000, audioCtx.currentTime + 0.2);
          osc2.type = 'sine';
          gain2.gain.setValueAtTime(0.2, audioCtx.currentTime);
          gain2.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
          osc2.start(audioCtx.currentTime);
          osc2.stop(audioCtx.currentTime + 0.4);
        }, 700);
      } catch (e) {
        // Fallback: no sound
      }
    };
    
    playCoinSound();
    
    setTimeout(() => {
      setOliviaKiss(false);
    }, 1500);
    setTimeout(() => {
      setShowKissHearts(false);
    }, 2500);
  };

  const maxLocks = lotteryMode === 'swiss' ? 4 : 3;
  const maxPositions = lotteryMode === 'swiss' ? 6 : 5;
  const maxNum = lotteryMode === 'swiss' ? 42 : 50;

  const handleLockChange = (position, value) => {
    const num = parseInt(value);
    if (value === "" || (num >= 1 && num <= maxNum)) {
      const currentLocks = Object.values(lockedPositions).filter(v => v !== "").length;
      const isNewLock = lockedPositions[position] === "" && value !== "";
      if (isNewLock && currentLocks >= maxLocks) return;
      setLockedPositions(prev => ({...prev, [position]: value}));
    }
  };

  const getLockedCount = () => Object.values(lockedPositions).filter(v => v !== "").length;

  // Apply persona modifiers to prediction numbers (supports multiple personas)
  const applyPersonaModifiers = (numbers, personas, maxNum) => {
    if (!personas || personas.length === 0) return numbers;
    
    let modified = [...numbers];
    const allPositions = [...Array(modified.length).keys()];
    
    // Check if both Avi and Dathi are selected
    const hasAvi = personas.includes("Avi");
    const hasDathi = personas.includes("Dathi");
    const hasOlivia = personas.includes("Olivia");
    
    if (hasAvi && hasDathi) {
      // BOTH Avi and Dathi selected - they modify DIFFERENT positions
      // Shuffle all positions
      const shuffled = [...allPositions].sort(() => Math.random() - 0.5);
      
      // Avi gets first 2-3 positions
      const aviCount = Math.random() < 0.5 ? 2 : 3;
      const aviPositions = shuffled.slice(0, aviCount);
      
      // Dathi gets next 2-3 positions (different from Avi)
      const dathiCount = Math.random() < 0.5 ? 2 : 3;
      const remainingPositions = shuffled.slice(aviCount);
      const dathiPositions = remainingPositions.slice(0, Math.min(dathiCount, remainingPositions.length));
      
      // Apply Avi's +1
      aviPositions.forEach(idx => {
        let newN = modified[idx] + 1;
        if (newN > maxNum) newN = 1;
        modified[idx] = newN;
      });
      
      // Apply Dathi's +1 to DIFFERENT positions
      dathiPositions.forEach(idx => {
        let newN = modified[idx] + 1;
        if (newN > maxNum) newN = 1;
        modified[idx] = newN;
      });
    } else if (hasOlivia) {
      // Olivia alone - subtracts 1 from 2-3 random positions
      const numPositions = Math.random() < 0.5 ? 2 : 3;
      const shuffled = [...allPositions].sort(() => Math.random() - 0.5);
      const positions = shuffled.slice(0, numPositions);
      
      positions.forEach(idx => {
        let newN = modified[idx] - 1;
        if (newN < 1) newN = maxNum;
        modified[idx] = newN;
      });
    } else if (hasAvi) {
      // Avi alone - adds 1 to 2-3 random positions
      const numPositions = Math.random() < 0.5 ? 2 : 3;
      const shuffled = [...allPositions].sort(() => Math.random() - 0.5);
      const positions = shuffled.slice(0, numPositions);
      
      positions.forEach(idx => {
        let newN = modified[idx] + 1;
        if (newN > maxNum) newN = 1;
        modified[idx] = newN;
      });
    } else if (hasDathi) {
      // Dathi alone - adds 1 to 2-3 random positions
      const numPositions = Math.random() < 0.5 ? 2 : 3;
      const shuffled = [...allPositions].sort(() => Math.random() - 0.5);
      const positions = shuffled.slice(0, numPositions);
      
      positions.forEach(idx => {
        let newN = modified[idx] + 1;
        if (newN > maxNum) newN = 1;
        modified[idx] = newN;
      });
    }
    
    // Ensure no duplicates and sort
    const unique = [...new Set(modified)];
    while (unique.length < numbers.length) {
      const extra = Math.floor(Math.random() * maxNum) + 1;
      if (!unique.includes(extra)) unique.push(extra);
    }
    return unique.sort((a, b) => a - b);
  };

  const fetchPrediction = useCallback(async () => {
    try {
      setLoading(true);
      setWheelSpinning(false);
      
      // Select API endpoint based on lottery mode AND generation mode
      let apiBase;
      if (lotteryMode === 'swiss') {
        // Swiss Lotto: jackpot (master-predictor) or money mode
        apiBase = generationMode === 'money' 
          ? `${API}/money-mode`
          : `${API}/master-predictor`;
      } else {
        // EuroMillions: jackpot (master-predictor) or money mode
        apiBase = generationMode === 'money' 
          ? `${API}/euromillions/money-mode`
          : `${API}/euromillions/master-predictor`;
      }
      
      let url = apiBase;
      const params = [];
      if (birthday) params.push(`birthday=${encodeURIComponent(birthday)}`);
      if (fullName) params.push(`name=${encodeURIComponent(fullName)}`);
      
      if (lockedPositions.p1) params.push(`lock_p1=${lockedPositions.p1}`);
      if (lockedPositions.p2) params.push(`lock_p2=${lockedPositions.p2}`);
      if (lockedPositions.p3) params.push(`lock_p3=${lockedPositions.p3}`);
      if (lockedPositions.p4) params.push(`lock_p4=${lockedPositions.p4}`);
      if (lockedPositions.p5) params.push(`lock_p5=${lockedPositions.p5}`);
      if (lotteryMode === 'swiss' && lockedPositions.p6) params.push(`lock_p6=${lockedPositions.p6}`);
      
      if (numTickets > 1) params.push(`num_tickets=${numTickets}`);
      // Swiss money mode requires minimum 2 tickets
      if (lotteryMode === 'swiss' && generationMode === 'money' && numTickets <= 1) {
        params.push('num_tickets=2');
      }
      // Pass visitor_id for ticket limit
      const vid = localStorage.getItem('lj_visitor_id') || '';
      if (vid) params.push(`visitor_id=${encodeURIComponent(vid)}`);
      if (params.length > 0) url += `?${params.join('&')}`;
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // EuroMillions uses POST, Swiss Lotto uses GET
      const res = lotteryMode === 'euro' 
        ? await axios.post(apiBase, {
            birthday: birthday || null,
            name: fullName || null,
            locked_positions: Object.fromEntries(Object.entries(lockedPositions).filter(([k,v]) => v !== "" && (k !== 'p6' || lotteryMode === 'swiss')).map(([k,v]) => [k, parseInt(v)])),
            num_tickets: numTickets,
            target_date: null,
            visitor_id: vid
          })
        : await axios.get(url);
      
      // Transform EuroMillions response format
      if (lotteryMode === 'euro' && res.data.tickets) {
        const mainTicket = res.data.tickets[0];
        const maxNum = 50;
        const transformed = {
          main_prediction: applyPersonaModifiers(mainTicket.numbers, activePersonas, maxNum),
          stars_prediction: mainTicket.stars,
          average_confidence: Math.round(mainTicket.confidence * 100),
          alternate_numbers: res.data.tickets.length > 1 ? res.data.tickets[1].numbers : [3, 11, 19, 27, 33],
          all_tickets: res.data.tickets.map((t, i) => ({
            ticket_num: i + 1,
            numbers: applyPersonaModifiers(t.numbers, activePersonas, maxNum),
            stars: t.stars,
            confidence: Math.round(t.confidence * 100),
            scenario: t.scenario || null,
            patterns_used: t.patterns_used || []
          })),
          persona_applied: activePersonas.join('+') || null
        };
        setPrediction(transformed);
      } else if (lotteryMode === 'swiss' && res.data.tickets) {
        // Swiss Money Mode returns { tickets: [...] } format
        const mainTicket = res.data.tickets[0];
        const maxNum = 42;
        const transformed = {
          main_prediction: applyPersonaModifiers(mainTicket.numbers, activePersonas, maxNum),
          lucky_prediction: mainTicket.lucky_number,
          average_confidence: Math.round((mainTicket.confidence || 0.75) * 100),
          alternate_numbers: res.data.tickets.length > 1 ? res.data.tickets[1].numbers : [],
          all_tickets: res.data.tickets.map((t, i) => ({
            ticket_num: i + 1,
            numbers: applyPersonaModifiers(t.numbers, activePersonas, maxNum),
            lucky: t.lucky_number,
            confidence: Math.round((t.confidence || 0.75) * 100),
            ticket_type: t.ticket_type || 'core',
            patterns_used: t.patterns_used || []
          })),
          total_price: res.data.total_price,
          engine: res.data.engine,
          target_date: res.data.target_date,
          digit_dna: res.data.digit_dna,
          sleepers: res.data.sleepers,
          persona_applied: activePersonas.join('+') || null
        };
        setPrediction(transformed);
      } else {
        // Swiss Lotto master-predictor (has main_prediction directly)
        const maxNum = 42;
        const modifiedData = {
          ...res.data,
          main_prediction: applyPersonaModifiers(res.data.main_prediction, activePersonas, maxNum),
          persona_applied: activePersonas.join('+') || null
        };
        setPrediction(modifiedData);
      }
      
      const ballCount = lotteryMode === 'swiss' ? 6 : 5;
      setTimeout(() => setWheelSpinning(true), ballCount * 2000);
      fetchTicketCounter();
      fetchPendingTickets(); // Update pending box after generation
    } catch (e) {
      console.error("Error:", e);
      // Handle ticket limit reached
      if (e.response && e.response.status === 429) {
        alert(e.response.data?.detail || "🎻 Ticket limit reached! Maximum 20 tickets per draw per lottery.");
        setLoading(false);
        return;
      }
      // 🕒 Handle draw-time cutoff (HTTP 423 Locked)
      if (e.response && e.response.status === 423) {
        alert(e.response.data?.detail || "🎻 Generator closed — draw in session. Reopens at 23:00.");
        // refresh status so banner shows immediately
        fetchUnlimitedStatus();
        setLoading(false);
        return;
      }
      // Fallback
      if (lotteryMode === 'swiss') {
        const randomNums = [];
        while (randomNums.length < 6) {
          const n = Math.floor(Math.random() * 42) + 1;
          if (!randomNums.includes(n)) randomNums.push(n);
        }
        setPrediction({
          main_prediction: randomNums.sort((a, b) => a - b),
          average_confidence: Math.floor(Math.random() * 30) + 50,
          alternate_numbers: [3, 11, 19, 27, 33, 39],
          lucky_prediction: Math.floor(Math.random() * 6) + 1
        });
      } else {
        const randomNums = [];
        while (randomNums.length < 5) {
          const n = Math.floor(Math.random() * 50) + 1;
          if (!randomNums.includes(n)) randomNums.push(n);
        }
        const stars = [];
        while (stars.length < 2) {
          const n = Math.floor(Math.random() * 12) + 1;
          if (!stars.includes(n)) stars.push(n);
        }
        setPrediction({
          main_prediction: randomNums.sort((a, b) => a - b),
          stars_prediction: stars.sort((a, b) => a - b),
          average_confidence: Math.floor(Math.random() * 30) + 50,
          alternate_numbers: [3, 11, 19, 27, 33]
        });
      }
      setTimeout(() => setWheelSpinning(true), 10000);
    } finally {
      setLoading(false);
    }
  }, [birthday, fullName, lockedPositions, numTickets, lotteryMode, activePersonas, generationMode]);

  const fetchStats = useCallback(async () => {
    try {
      const endpoint = lotteryMode === 'swiss' ? `${API}/dashboard` : `${API}/euromillions/stats`;
      const res = await axios.get(endpoint);
      setStats(res.data);
    } catch (e) {
      console.error("Error:", e);
    }
  }, [lotteryMode]);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/prediction-history?limit=50&lottery_type=${lotteryMode === 'swiss' ? 'swiss' : 'euromillions'}`);
      setHistory(res.data.history || []);
      setHistoryStats(res.data.stats || null);
    } catch (e) {
      console.error("Error fetching history:", e);
    }
  }, [lotteryMode]);

  const clearHistory = async () => {
    if (window.confirm('Clear all prediction history?')) {
      try {
        await axios.delete(`${API}/prediction-history/clear`);
        setHistory([]);
        setHistoryStats(null);
      } catch (e) {
        console.error("Error clearing history:", e);
      }
    }
  };

  useEffect(() => {
    fetchStats();
    const fetchInitial = async () => {
      try {
        const apiBase = lotteryMode === 'swiss' ? `${API}/master-predictor` : `${API}/euromillions/master-predictor`;
        const res = lotteryMode === 'euro' 
          ? await axios.post(apiBase, { num_tickets: 1 })
          : await axios.get(apiBase);
        
        // Transform EuroMillions response format
        if (lotteryMode === 'euro' && res.data.tickets) {
          const mainTicket = res.data.tickets[0];
          const transformed = {
            main_prediction: mainTicket.numbers,
            stars_prediction: mainTicket.stars,
            average_confidence: Math.round(mainTicket.confidence * 100),
            alternate_numbers: [3, 11, 19, 27, 33],
            all_tickets: res.data.tickets.map((t, i) => ({
              ticket_num: i + 1,
              numbers: t.numbers,
              stars: t.stars,
              confidence: Math.round(t.confidence * 100),
              scenario: t.scenario || null,
              patterns_used: t.patterns_used || []
            }))
          };
          setPrediction(transformed);
        } else {
          setPrediction(res.data);
        }
      } catch (e) {
        console.error("Error:", e);
        // Demo fallback
        if (lotteryMode === 'swiss') {
          setPrediction({ main_prediction: [7, 14, 21, 28, 35, 42], average_confidence: 77, alternate_numbers: [3, 11, 19, 27, 33, 39], lucky_prediction: 3 });
        } else {
          setPrediction({ main_prediction: [5, 17, 23, 38, 44], stars_prediction: [4, 9], average_confidence: 72, alternate_numbers: [8, 12, 29, 36, 47] });
        }
      }
    };
    fetchInitial();
  }, [fetchStats, lotteryMode]);

  // Reset state when switching modes
  useEffect(() => {
    setPrediction(null);
    setLockedPositions({ p1: "", p2: "", p3: "", p4: "", p5: "", p6: "" });
    setShowLocks(false);
    setShowPersonal(false);
    setShowBonus(false);
    setShowMultiTickets(false);
    setWheelSpinning(false);
    setShowHistory(false);
  }, [lotteryMode]);

  // Fetch history when showing it
  useEffect(() => {
    if (showHistory) {
      fetchHistory();
    }
  }, [showHistory, fetchHistory]);

  return (
    <div className="min-h-screen pb-10">
      {/* How to Use — removed from fixed position, will be inline */}

      {/* Header */}
      <header className="text-center py-6">
        <div className="flex items-center justify-center gap-3 mb-1">
          <span className="text-3xl">{lotteryMode === 'swiss' ? '🎱' : '🌟'}</span>
          <h1 
            className="text-3xl font-bold"
            style={{
              background: lotteryMode === 'swiss' 
                ? 'linear-gradient(135deg, #d4af37 0%, #f0d060 50%, #d4af37 100%)'
                : 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 50%, #fbbf24 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            Lucky Jack
          </h1>
          <span className="text-3xl">{lotteryMode === 'swiss' ? '🍀' : '⭐'}</span>
        </div>
        <p className="text-slate-400 text-sm">{lotteryMode === 'swiss' ? 'Swiss Lotto' : 'EuroMillions'} Number Generator</p>
        {ticketCounter > 0 && (
          <div className="mt-2 flex items-center justify-center gap-3" data-testid="ticket-counters">
            {/* All-time counter — small */}
            <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-slate-800/60 border border-slate-700/50" data-testid="ticket-counter">
              <span className="text-amber-400 text-xs font-mono font-bold">{ticketCounter.toLocaleString()}</span>
              <span className="text-slate-500 text-[10px]">total tickets</span>
            </div>
            {/* Next draw counter — bigger, more prominent */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-xl bg-gradient-to-r from-emerald-900/40 to-emerald-800/30 border border-emerald-500/40" data-testid="next-draw-counter">
              <span className="text-emerald-400 text-xl font-mono font-black tracking-tight">{nextDrawTickets}</span>
              <div className="flex flex-col leading-none">
                <span className="text-slate-300 text-[10px] font-semibold">for next draw</span>
                <span className="text-slate-500 text-[9px]">{nextDrawDate}</span>
              </div>
            </div>
          </div>
        )}
        
        {/* Lottery Mode Toggle */}
        <div className="flex justify-center mt-4">
          <div className="inline-flex rounded-full p-1" style={{ background: 'rgba(30,35,50,0.9)', border: '1px solid rgba(100,100,120,0.3)' }}>
            <button
              onClick={() => setLotteryMode('swiss')}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 flex items-center gap-2 ${
                lotteryMode === 'swiss' 
                  ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-gray-900 shadow-lg' 
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              data-testid="swiss-lotto-toggle"
            >
              🇨🇭 Swiss Lotto
            </button>
            <button
              onClick={() => setLotteryMode('euro')}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 flex items-center gap-2 ${
                lotteryMode === 'euro' 
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg' 
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              data-testid="euromillions-toggle"
            >
              🇪🇺 EuroMillions
            </button>
          </div>
        </div>
      </header>

      {/* LAST DRAW DISPLAY - VIP-only (hidden in public mode to keep secrets) */}
      {lastDraw && isUnlimited && (
        <div className="max-w-2xl mx-auto px-4 mb-4">
          <div 
            className="p-3 rounded-xl flex items-center justify-between flex-wrap gap-2"
            style={{ 
              background: lotteryMode === 'swiss' 
                ? 'linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(5,150,105,0.1) 100%)'
                : 'linear-gradient(135deg, rgba(59,130,246,0.15) 0%, rgba(37,99,235,0.1) 100%)',
              border: lotteryMode === 'swiss'
                ? '1px solid rgba(16,185,129,0.3)'
                : '1px solid rgba(59,130,246,0.3)',
              boxShadow: lotteryMode === 'swiss'
                ? '0 4px 15px rgba(16,185,129,0.1)'
                : '0 4px 15px rgba(59,130,246,0.1)'
            }}
            data-testid="last-draw-display"
          >
            <div className="flex items-center gap-2">
              <span className={`font-semibold text-sm ${lotteryMode === 'swiss' ? 'text-emerald-400' : 'text-blue-400'}`}>
                📊 Last {lotteryMode === 'swiss' ? 'Swiss' : 'Euro'} Draw:
              </span>
              <span className="text-slate-300 text-sm font-medium">{lastDraw.date}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                {lastDraw.numbers?.map((n, i) => (
                  <div 
                    key={i} 
                    className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                    style={{
                      background: lotteryMode === 'swiss' 
                        ? `radial-gradient(circle at 30% 30%, ${
                            n <= 7 ? '#ef4444' : n <= 14 ? '#f97316' : n <= 21 ? '#eab308' : 
                            n <= 28 ? '#22c55e' : n <= 35 ? '#3b82f6' : '#8b5cf6'
                          } 0%, ${
                            n <= 7 ? '#b91c1c' : n <= 14 ? '#c2410c' : n <= 21 ? '#a16207' : 
                            n <= 28 ? '#15803d' : n <= 35 ? '#1d4ed8' : '#6d28d9'
                          } 100%)`
                        : `radial-gradient(circle at 30% 30%, ${
                            n <= 10 ? '#ef4444' : n <= 20 ? '#f97316' : n <= 30 ? '#eab308' : 
                            n <= 40 ? '#22c55e' : '#3b82f6'
                          } 0%, ${
                            n <= 10 ? '#b91c1c' : n <= 20 ? '#c2410c' : n <= 30 ? '#a16207' : 
                            n <= 40 ? '#15803d' : '#1d4ed8'
                          } 100%)`,
                      boxShadow: '0 2px 4px rgba(0,0,0,0.3), inset 0 1px 2px rgba(255,255,255,0.3)',
                      color: 'white',
                      textShadow: '0 1px 2px rgba(0,0,0,0.5)'
                    }}
                  >
                    {n}
                  </div>
                ))}
              </div>
              {/* Swiss Lotto lucky number */}
              {lotteryMode === 'swiss' && lastDraw.lucky_number && (
                <div className="flex items-center gap-1 ml-2 px-2 py-1 rounded-full" style={{ background: 'rgba(251,191,36,0.2)', border: '1px solid rgba(251,191,36,0.4)' }}>
                  <span className="text-amber-400 text-xs">🍀</span>
                  <span className="text-amber-400 font-bold text-sm">{lastDraw.lucky_number}</span>
                </div>
              )}
              {/* Swiss Lotto replay number */}
              {lotteryMode === 'swiss' && lastDraw.replay_number && (
                <div className="flex items-center gap-1 px-2 py-1 rounded-full" style={{ background: 'rgba(139,92,246,0.2)', border: '1px solid rgba(139,92,246,0.4)' }}>
                  <span className="text-purple-400 text-xs">🔄</span>
                  <span className="text-purple-400 font-bold text-sm">{lastDraw.replay_number}</span>
                </div>
              )}
              {/* EuroMillions stars */}
              {lotteryMode === 'euro' && lastDraw.stars && (
                <div className="flex items-center gap-1 ml-2">
                  {lastDraw.stars.map((s, i) => (
                    <div 
                      key={i}
                      className="w-7 h-7 flex items-center justify-center text-xs font-bold"
                      style={{
                        background: 'radial-gradient(circle at 30% 30%, #fbbf24 0%, #d97706 100%)',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.3), inset 0 1px 2px rgba(255,255,255,0.3)',
                        color: '#1e1b4b',
                        textShadow: '0 1px 0px rgba(255,255,255,0.3)',
                        clipPath: 'polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)'
                      }}
                    >
                      {s}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Content with Pending Tickets sidebar */}
      <div className="max-w-6xl mx-auto px-4 flex gap-3 justify-center">
        {/* 🌌 COSMIC SIDEBAR — foldable */}
        {sidebarFolded ? (
          <div className="hidden lg:flex flex-col items-center pt-4" data-testid="sidebar-folded">
            <button
              onClick={toggleSidebar}
              className="group flex flex-col items-center gap-2 px-1.5 py-3 rounded-r-lg bg-gradient-to-b from-amber-500/20 to-slate-900/60 border border-l-0 border-amber-500/30 hover:border-amber-400/80 transition sticky top-4"
              title="Unfold the cosmos"
              data-testid="sidebar-unfold-btn"
            >
              <span className="text-amber-300 text-lg">🌌</span>
              <span className="text-amber-400/80 text-[9px] font-bold tracking-wider rotate-180" style={{ writingMode: 'vertical-rl' }}>
                Unfold Cosmos
              </span>
              <span className="text-amber-300/60 text-[9px]">▸</span>
            </button>
          </div>
        ) : (
        <div className="hidden lg:block w-72 flex-shrink-0" data-testid="pending-tickets-panel">
          <div className="sticky top-4 lucky-card p-3 border border-amber-500/20 relative">
            <button
              onClick={toggleSidebar}
              className="absolute -right-3 top-4 z-10 w-6 h-6 rounded-full bg-amber-500 text-slate-900 hover:bg-amber-300 flex items-center justify-center shadow-lg shadow-amber-500/40 border border-amber-200 transition"
              title="Fold the cosmos"
              data-testid="sidebar-fold-btn"
            >
              <span className="text-[10px] font-black">◂</span>
            </button>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-amber-400 font-semibold text-xs">🎻 Top 10 Predicted</span>
              <span className="text-emerald-400 font-mono font-bold text-sm">{pendingTickets.length}/{pendingTotal}</span>
            </div>
            <div className="text-slate-500 text-[9px] mb-2">For draw: {nextDrawDate} <span className="text-slate-600">• engine-ranked</span></div>

            {/* 🎯 Random vs E reality-check box (DJ canon 29.04.2026) */}
            {randomVsE && randomVsE.actual_draw && (
              <RandomVsEBox data={randomVsE} mode={lotteryMode} />
            )}

            {/* 📜 History — past draws archive (DJ canon 29.04.2026) */}
            <HistoryPanel mode={lotteryMode} api={API} />

            {lotteryMode === 'euro' && isUnlimited && diagnostics && Array.isArray(diagnostics.narrative) && diagnostics.narrative.length > 0 && (
              <div className="mb-2 p-1.5 rounded-md border border-cyan-500/40 bg-gradient-to-br from-cyan-900/25 to-slate-900/20" data-testid="diagnostics-panel">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-cyan-300 text-[10px] font-bold">🔬 Live Frequencies</span>
                  <span className="flex gap-1">
                    {diagnostics.snap_back_active && <span className="px-1 py-0.5 rounded bg-rose-500/25 text-rose-300 text-[8px] font-bold">🔄 gravity-pull</span>}
                    {diagnostics.rare_active && <span className="px-1 py-0.5 rounded bg-fuchsia-500/25 text-fuchsia-300 text-[8px] font-bold">🌌 cosmic-storm</span>}
                  </span>
                </div>
                <ul className="space-y-0.5 text-[9px] text-slate-300 leading-tight">
                  {diagnostics.narrative.map((line, i) => (
                    <li key={i} className="truncate" title={line} data-testid={`diag-narrative-${i}`}>{line}</li>
                  ))}
                </ul>
              </div>
            )}
            {/* 🌌 COSMOS ORBIT — persistent celestial alignment chambers */}
            {huntBoxes.length > 0 && huntBoxes.map((hb) => {
              const tickets = huntTickets[hb.id] || [];
              const mx = hb.mode === 'euro' ? 50 : 42;
              return (
                <div key={hb.id} className="mb-2 p-2 rounded-md border-2 border-amber-500/50 bg-gradient-to-br from-amber-900/20 via-orange-900/15 to-slate-900/40" data-testid={`hunt-box-${hb.id}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-amber-300 text-[11px] font-black tracking-wide">{hb.label}</span>
                    <button
                      onClick={() => refreshHuntBox(hb.id)}
                      disabled={huntLoading}
                      className="text-[9px] text-amber-400 hover:text-amber-200 font-bold px-1.5 py-0.5 rounded border border-amber-600/40 hover:border-amber-400/80 transition"
                      data-testid={`hunt-refresh-${hb.id}`}
                    >{huntLoading ? '…' : '🎧 re-tune'}</button>
                  </div>
                  <div className="text-[9px] text-slate-400 mb-1">
                    🎻 Tuning the cosmos until <span className="text-amber-300 font-mono font-bold">P5 = {hb.target_value}</span> crowns the finale — re-tunes every cycle until the alignment lands 🍀
                  </div>
                  {/* Resonator chips with release */}
                  <div className="flex flex-wrap gap-1 mb-1.5">
                    {(hb.jack_picks || []).map(n => (
                      <button
                        key={n}
                        onClick={() => removeHuntSuspect(hb.id, n)}
                        className="px-2 py-0.5 text-[10px] font-black rounded-full bg-amber-400 text-slate-900 hover:bg-red-400 hover:text-white border border-amber-200 transition"
                        title={`${n} — release from the song`}
                        data-testid={`hunt-suspect-${n}`}
                      >{n} ✕</button>
                    ))}
                    {/* Weave-in resonator input */}
                    <div className="flex items-center gap-1">
                      <input
                        type="number"
                        min="1"
                        max={mx}
                        value={huntSuspectInput}
                        onChange={(e) => setHuntSuspectInput(e.target.value)}
                        placeholder="+♪"
                        className="w-12 px-1.5 py-0.5 text-[10px] rounded bg-slate-800 border border-amber-600/40 text-amber-300 focus:outline-none focus:border-amber-400"
                        data-testid={`hunt-suspect-input-${hb.id}`}
                      />
                      <button
                        onClick={() => {
                          const n = parseInt(huntSuspectInput);
                          if (n >= 1 && n <= mx && n !== hb.target_value) {
                            addHuntSuspect(hb.id, n);
                            setHuntSuspectInput("");
                          }
                        }}
                        className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-500 text-slate-900 hover:bg-amber-300 transition"
                        data-testid={`hunt-add-${hb.id}`}
                      >weave</button>
                    </div>
                  </div>
                  {/* 5 auto-generated symphonies */}
                  <div className="space-y-1 pt-1 border-t border-amber-600/20">
                    {tickets.length === 0 ? (
                      <div className="text-[9px] text-slate-500 py-1 text-center">🌌 The cosmos is silent — tap 🎧 re-tune to summon the symphony</div>
                    ) : tickets.map((t, ti) => (
                      <div key={ti} className="flex items-center justify-between gap-1 px-1.5 py-1 rounded bg-slate-900/60 border border-amber-600/20" data-testid={`hunt-ticket-${hb.id}-${ti}`}>
                        <div className="flex flex-col flex-1 min-w-0">
                          <div className="flex items-center gap-1 flex-wrap">
                            <span className="text-[9px] text-amber-400/90 font-mono">{t.archetype}</span>
                          </div>
                          <div className="flex items-center gap-1 flex-wrap mt-0.5">
                            {t.mains.map((n, ni) => {
                              const isTarget = n === hb.target_value;
                              const isSuspect = (hb.jack_picks || []).includes(n);
                              return (
                                <span
                                  key={ni}
                                  className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-[10px] font-black border ${isTarget ? 'bg-rose-500 text-white border-rose-300 shadow shadow-rose-500/60' : isSuspect ? 'bg-amber-400 text-slate-900 border-amber-200' : 'bg-slate-700 text-slate-200 border-slate-500'}`}
                                  title={isTarget ? '🌟 crown alignment' : isSuspect ? '🎻 resonator' : 'harmonic fill'}
                                >{n}</span>
                              );
                            })}
                            {hb.mode === 'euro' && t.stars && t.stars.length > 0 && (
                              <>
                                <span className="text-amber-400/60 text-[9px]">⭐</span>
                                {t.stars.map((s, si) => (
                                  <span key={si} className="inline-flex items-center justify-center w-5 h-5 rounded-full text-[9px] font-black bg-amber-300 text-slate-900 border border-amber-200">{s}</span>
                                ))}
                              </>
                            )}
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <div className="text-[9px] text-amber-400/70 font-mono">♪ {t.score}</div>
                          <div className="text-[8px] text-slate-500">{t.unique_laws_hit}✨</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
            {lotteryMode === 'euro' && isUnlimited && djCalls && Array.isArray(djCalls.user_hungry_list_next_3d) && djCalls.user_hungry_list_next_3d.length > 0 && (() => {
              const hungry = djCalls.user_hungry_list_next_3d;
              const hungryMains = hungry.filter(n => n >= 1 && n <= 50 && !(hungry.includes(n) && n <= 12 && djCalls.star_locks?.includes(n)));
              // separate by Euro ranges — numbers 1-12 could be either main or star. We keep them in mains by default; DJ's star_locks define stars.
              const mainsPool = hungry.filter(n => n >= 1 && n <= 50);
              const starsPool = [...new Set([...(djCalls.star_locks || []), ...(djCalls.star_extensions || [])])].filter(n => n >= 1 && n <= 12);
              const toggleMain = (n) => {
                setJackPicks(p => {
                  const has = p.mains.includes(n);
                  if (has) return { ...p, mains: p.mains.filter(x => x !== n) };
                  if (p.mains.length >= 5) return p;
                  return { ...p, mains: [...p.mains, n].sort((a,b)=>a-b) };
                });
              };
              const toggleStar = (n) => {
                setJackPicks(p => {
                  const has = p.stars.includes(n);
                  if (has) return { ...p, stars: p.stars.filter(x => x !== n) };
                  if (p.stars.length >= 2) return p;
                  return { ...p, stars: [...p.stars, n].sort((a,b)=>a-b) };
                });
              };
              const lockReady = jackPicks.mains.length === 5 && jackPicks.stars.length === 2;
              const lockAndGenerate = async () => {
                try {
                  const locked_positions = {};
                  jackPicks.mains.forEach((n, i) => { locked_positions[`p${i+1}`] = n; });
                  jackPicks.stars.forEach((n, i) => { locked_positions[`s${i+1}`] = n; });
                  const res = await axios.post(`${API}/euromillions/generate`, {
                    birthday: '',
                    name: 'Jack',
                    locked_positions,
                    visitor_id: localStorage.getItem('visitor_id') || '',
                  });
                  if (res.data && res.data.tickets) {
                    toast.success(`🎻 Jack's ticket locked! ${jackPicks.mains.join(', ')} ⭐${jackPicks.stars.join(',')}`);
                    setJackPicks({ mains: [], stars: [] });
                    fetchPendingTickets && fetchPendingTickets();
                  }
                } catch (e) { toast.error('Lock failed: ' + (e.response?.data?.detail || e.message)); }
              };
              return (
                <div className="mb-2 p-1.5 rounded-md border border-lime-500/40 bg-gradient-to-br from-lime-900/20 to-emerald-900/10" data-testid="jack-box">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-lime-300 text-[10px] font-bold">🎻 Jack 👀</span>
                    <span className="text-lime-400/70 text-[8px] font-mono">silent voices · next 3 songs</span>
                  </div><div className="text-[8px] text-slate-400 mb-1">Tap to lock at position</div>
                  <div className="flex flex-wrap gap-1 mb-1">
                    {mainsPool.map(n => {
                      const picked = jackPicks.mains.includes(n);
                      return (
                        <button
                          key={n}
                          onClick={() => toggleMain(n)}
                          className={`w-7 h-7 rounded-full text-[10px] font-black border transition-all ${picked
                            ? 'bg-lime-400 text-slate-900 border-lime-300 shadow shadow-lime-400/40'
                            : 'bg-slate-800 text-lime-300 border-lime-600/40 hover:border-lime-400/80'}`}
                          data-testid={`jack-chip-main-${n}`}
                        >{n}</button>
                      );
                    })}
                  </div>
                  {starsPool.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-1 pt-1 border-t border-lime-600/20">
                      <span className="text-[9px] text-amber-400/80 self-center mr-1">⭐</span>
                      {starsPool.map(n => {
                        const picked = jackPicks.stars.includes(n);
                        return (
                          <button
                            key={`s-${n}`}
                            onClick={() => toggleStar(n)}
                            className={`w-6 h-6 rounded-full text-[9px] font-black border transition-all ${picked
                              ? 'bg-amber-300 text-slate-900 border-amber-200 shadow shadow-amber-400/40'
                              : 'bg-slate-800 text-amber-300 border-amber-600/40 hover:border-amber-400'}`}
                            data-testid={`jack-chip-star-${n}`}
                          >{n}</button>
                        );
                      })}
                    </div>
                  )}
                  <div className="flex items-center justify-between text-[9px] pt-1 border-t border-lime-600/20">
                    <span className="text-slate-400">
                      picked {jackPicks.mains.length}/5 · ⭐ {jackPicks.stars.length}/2
                    </span>
                    <button
                      onClick={lockAndGenerate}
                      disabled={!lockReady}
                      className={`px-2 py-0.5 rounded text-[9px] font-bold transition-all ${lockReady
                        ? 'bg-lime-400 text-slate-900 hover:bg-lime-300'
                        : 'bg-slate-800 text-slate-600 cursor-not-allowed'}`}
                      data-testid="jack-lock-btn"
                    >Lock & Generate</button>
                  </div>
                </div>
              );
            })()}
            {rareSeed && rareSeed.draws_since <= 8 && isUnlimited && (
              <div className="mb-2 p-1.5 rounded-md border border-fuchsia-500/40 bg-gradient-to-br from-fuchsia-900/30 to-purple-900/20" data-testid="rare-event-banner">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-fuchsia-300 text-[10px] font-bold">🌌 COSMIC STORM</span>
                  <span className="text-fuchsia-400/80 text-[9px] font-mono">{rareSeed.date} • +{rareSeed.draws_since}</span>
                </div>
                <div className="text-[9px] text-slate-400 mb-0.5">Storm Chord [{(rareSeed.numbers || []).join(', ')}]{rareSeed.stars && rareSeed.stars.length > 0 ? ` ⭐ [${rareSeed.stars.join(', ')}]` : ''}</div>
                {(rareSeed.unreleased_mains?.length > 0 || rareSeed.unreleased_stars?.length > 0) && (
                  <div className="text-[9px] text-fuchsia-300 font-semibold" title="Storm notes still humming in the silence">
                    💤 Silent Voices: {(rareSeed.unreleased_mains || []).join(', ')}{rareSeed.unreleased_stars?.length > 0 ? ` ⭐${rareSeed.unreleased_stars.join(',')}` : ''}
                  </div>
                )}
              </div>
            )}
            <div className="space-y-1.5 max-h-[55vh] overflow-y-auto">
              {pendingTickets.length === 0 ? (
                <div className="text-center text-slate-600 text-[10px] py-3">
                  No engine tickets yet
                </div>
              ) : pendingTickets.map((t, idx) => {
                const dr = t.date_resonance;
                const tierClass = dr ? (
                  dr.tier === 'full_echo' ? 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/40' :
                  dr.tier === 'harmonic'  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                  dr.tier === 'tune'      ? 'bg-sky-500/15 text-sky-300 border-sky-500/30' :
                                            'bg-slate-700/40 text-slate-400 border-slate-600/40'
                ) : '';
                return (
                <div key={idx} className="p-1.5 rounded-md bg-slate-800/50 border border-slate-700/30" data-testid={`pending-ticket-${idx}`}>
                  {t.serial && (
                    <div className="text-[8px] font-mono text-amber-400/80 mb-0.5 truncate" data-testid={`pending-serial-${idx}`}>
                      🎫 {t.serial}
                    </div>
                  )}
                  <div className="flex items-center justify-center gap-1">
                    {t.numbers?.map((n, i) => {
                      const slotKey = `P${i+1}`;
                      const isLocked = t.has_locked && t.locked_positions && t.locked_positions[slotKey] === n;
                      return (
                        <div key={i} className={`relative ${isLocked ? 'ring-2 ring-amber-400/70 rounded-full' : ''}`}>
                          <Ball number={n} size="xs" maxNum={lotteryMode === 'euro' ? 50 : 42} />
                          {isLocked && (
                            <span className="absolute -top-1 -right-1 text-[8px] leading-none" data-testid={`lock-marker-${idx}-p${i+1}`}>🔒</span>
                          )}
                        </div>
                      );
                    })}
                    {lotteryMode === 'swiss' && t.lucky != null && (
                      <div className="w-6 h-6 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-sm shadow-amber-500/30 ml-1">
                        <span className="text-white text-[9px] font-black">{t.lucky}</span>
                      </div>
                    )}
                    {lotteryMode === 'euro' && t.stars && t.stars.length > 0 && (
                      <>
                        {t.stars.map((s, si) => (
                          <div key={si} className="w-6 h-6 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center shadow-sm shadow-yellow-500/30 ml-0.5">
                            <span className="text-white text-[8px] font-black">{s}</span>
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                  {t.has_locked && t.locked_positions && Object.keys(t.locked_positions).length > 0 && (
                    <div
                      className={`mt-1 px-1.5 py-0.5 rounded border text-[9px] font-mono flex items-center justify-between gap-1 ${
                        t.is_mine
                          ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300'
                          : 'border-amber-500/40 bg-amber-500/10 text-amber-300'
                      }`}
                      title={Object.entries(t.locked_positions).map(([k,v]) => `${k}=${v}`).join(', ')}
                      data-testid={`lock-badge-${idx}`}
                    >
                      <span className="truncate">🔒 {Object.entries(t.locked_positions).map(([k,v]) => `${k}:${v}`).join(' · ')}</span>
                      <span className="font-bold tabular-nums">{t.is_mine ? '🎫 your lock' : 'locked pick'}</span>
                    </div>
                  )}
                  {lotteryMode === 'euro' && dr && (
                    <div
                      className={`mt-1 px-1.5 py-0.5 rounded border text-[9px] font-mono flex items-center justify-between gap-1 ${tierClass}`}
                      title={(dr.signals || []).join('\n')}
                      data-testid={`date-resonance-badge-${idx}`}
                    >
                      <span className="truncate">{dr.badge}</span>
                      <span className="font-bold tabular-nums">{dr.score >= 0 ? `+${dr.score}` : dr.score}</span>
                    </div>
                  )}
                  {t.rare_echo && t.rare_echo.score > 0 && isUnlimited && (
                    <div
                      className="mt-1 px-1.5 py-0.5 rounded border border-fuchsia-500/40 bg-fuchsia-500/15 text-fuchsia-300 text-[9px] font-mono flex items-center justify-between gap-1"
                      title={`Holds silent voices: ${(t.rare_echo.held_mains || []).join(', ')}${t.rare_echo.held_stars?.length ? ' ⭐ ' + t.rare_echo.held_stars.join(',') : ''}`}
                      data-testid={`rare-echo-badge-${idx}`}
                    >
                      <span className="truncate">🌌 storm echo</span>
                      <span className="font-bold tabular-nums">+{t.rare_echo.score}</span>
                    </div>
                  )}
                  {t.dj_call && t.dj_call.score !== 0 && isUnlimited && (
                    <div
                      className={`mt-1 px-1.5 py-0.5 rounded border text-[9px] font-mono flex items-center justify-between gap-1 ${
                        t.dj_call.score >= 80 ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                        t.dj_call.score >= 40 ? 'bg-lime-500/15 text-lime-300 border-lime-500/40' :
                        t.dj_call.score > 0   ? 'bg-sky-500/10 text-sky-300 border-sky-500/30' :
                                                'bg-rose-500/15 text-rose-300 border-rose-500/40'
                      }`}
                      title={(t.dj_call.signals || []).join('\n')}
                      data-testid={`dj-call-badge-${idx}`}
                    >
                      <span className="truncate">{t.dj_call.badge}</span>
                      <span className="font-bold tabular-nums">{t.dj_call.score >= 0 ? `+${t.dj_call.score}` : t.dj_call.score}</span>
                    </div>
                  )}
                </div>
                );
              })}
            </div>
            {pendingTickets.length > 0 && (
              <div className="mt-1.5 pt-1.5 border-t border-slate-700/30 text-center">
                <span className="text-slate-500 text-[9px]">{pendingTickets.length} top picks</span>
              </div>
            )}
            
            {/* 🎻 Archive files — 50 tickets per file, sorted by generation time */}
            {archiveFiles.length > 0 && (
              <div className="mt-3 pt-2 border-t border-slate-700/40">
                <div className="text-slate-400 text-[10px] mb-1.5 flex items-center gap-1">
                  <span>📁 Archive</span>
                  <span className="text-slate-600">({archiveFiles.length} file{archiveFiles.length > 1 ? 's' : ''})</span>
                </div>
                <div className="space-y-1">
                  {archiveFiles.map((af, fi) => (
                    <div key={fi} className="rounded-md bg-slate-800/40 border border-slate-700/30">
                      <button
                        onClick={() => setOpenArchive(openArchive === fi ? null : fi)}
                        className="w-full px-2 py-1.5 flex items-center justify-between text-left hover:bg-slate-700/30 rounded-md"
                        data-testid={`archive-file-${fi}`}
                      >
                        <span className="text-[10px] text-amber-300 font-mono">{af.file_name}</span>
                        <span className="text-[9px] text-slate-500">{af.count} tickets {openArchive === fi ? '▲' : '▼'}</span>
                      </button>
                      {openArchive === fi && (
                        <div className="px-1.5 pb-1.5 space-y-1 max-h-[40vh] overflow-y-auto">
                          {af.tickets?.map((t, ti) => (
                            <div key={ti} className="p-1 rounded bg-slate-900/60 border border-slate-800/50">
                              <div className="flex items-center justify-center gap-0.5 flex-wrap">
                                {t.numbers?.map((n, i) => (
                                  <Ball key={i} number={n} size="xs" maxNum={lotteryMode === 'euro' ? 50 : 42} />
                                ))}
                                {lotteryMode === 'swiss' && t.lucky != null && (
                                  <div className="w-5 h-5 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-sm ml-0.5">
                                    <span className="text-white text-[8px] font-black">{t.lucky}</span>
                                  </div>
                                )}
                                {lotteryMode === 'euro' && t.stars && t.stars.length > 0 && (
                                  <>
                                    {t.stars.map((s, si) => (
                                      <div key={si} className="w-5 h-5 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center shadow-sm">
                                        <span className="text-white text-[8px] font-black">{s}</span>
                                      </div>
                                    ))}
                                  </>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        )}

        {/* Main Generator */}
        <main className="flex-1 max-w-2xl">

        {/* Mobile pending tickets + active users (collapsed) */}
        <div className="lg:hidden mb-3 flex gap-2">
          <button 
            onClick={() => document.getElementById('mobile-pending')?.classList.toggle('hidden')}
            className="flex-1 p-2 rounded-lg bg-slate-800/60 border border-amber-500/20 flex items-center justify-between"
            data-testid="pending-mobile-toggle"
          >
            <span className="text-amber-400 text-sm font-semibold">Pending</span>
            <span className="text-emerald-400 font-mono font-bold">{pendingTotal}</span>
          </button>
          <div className="p-2 rounded-lg bg-slate-800/60 border border-emerald-500/20 flex items-center gap-2">
            <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span></span>
            <span className="text-emerald-400 font-mono font-bold">{activeUsers}</span>
            <span className="text-slate-500 text-[10px]">online</span>
          </div>
        </div>
        <div className="lg:hidden mb-3">
          <div id="mobile-pending" className="hidden mt-2 space-y-1.5 max-h-80 overflow-y-auto">
            <div className="text-[10px] text-slate-500 px-1">Top {pendingTickets.length} of {pendingTotal} • engine-ranked</div>
            {pendingTickets.map((t, idx) => {
              const dr = t.date_resonance;
              const tierClass = dr ? (
                dr.tier === 'full_echo' ? 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/40' :
                dr.tier === 'harmonic'  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                dr.tier === 'tune'      ? 'bg-sky-500/15 text-sky-300 border-sky-500/30' :
                                          'bg-slate-700/40 text-slate-400 border-slate-600/40'
              ) : '';
              return (
              <div key={idx} className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/30" data-testid={`mobile-pending-ticket-${idx}`}>
                <div className="flex items-center justify-center gap-1">
                  {t.numbers?.map((n, i) => (
                    <Ball key={i} number={n} size="xs" maxNum={lotteryMode === 'euro' ? 50 : 42} />
                  ))}
                  {lotteryMode === 'swiss' && t.lucky != null && (
                    <div className="w-6 h-6 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-sm shadow-amber-500/30 ml-1">
                      <span className="text-white text-[9px] font-black">{t.lucky}</span>
                    </div>
                  )}
                  {lotteryMode === 'euro' && t.stars && t.stars.length > 0 && (
                    <>
                      {t.stars.map((s, si) => (
                        <div key={si} className="w-6 h-6 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center shadow-sm shadow-yellow-500/30 ml-0.5">
                          <span className="text-white text-[8px] font-black">{s}</span>
                        </div>
                      ))}
                    </>
                  )}
                </div>
                {lotteryMode === 'euro' && dr && (
                  <div
                    className={`mt-1 px-1.5 py-0.5 rounded border text-[9px] font-mono flex items-center justify-between gap-1 ${tierClass}`}
                    title={(dr.signals || []).join('\n')}
                  >
                    <span className="truncate">{dr.badge}</span>
                    <span className="font-bold tabular-nums">{dr.score >= 0 ? `+${dr.score}` : dr.score}</span>
                  </div>
                )}
                {t.rare_echo && t.rare_echo.score > 0 && isUnlimited && (
                  <div
                    className="mt-1 px-1.5 py-0.5 rounded border border-fuchsia-500/40 bg-fuchsia-500/15 text-fuchsia-300 text-[9px] font-mono flex items-center justify-between gap-1"
                    title={`Holds silent voices: ${(t.rare_echo.held_mains || []).join(', ')}${t.rare_echo.held_stars?.length ? ' ⭐ ' + t.rare_echo.held_stars.join(',') : ''}`}
                  >
                    <span className="truncate">🌌 storm echo</span>
                    <span className="font-bold tabular-nums">+{t.rare_echo.score}</span>
                  </div>
                )}
                {t.dj_call && t.dj_call.score !== 0 && isUnlimited && (
                  <div
                    className={`mt-1 px-1.5 py-0.5 rounded border text-[9px] font-mono flex items-center justify-between gap-1 ${
                      t.dj_call.score >= 80 ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                      t.dj_call.score >= 40 ? 'bg-lime-500/15 text-lime-300 border-lime-500/40' :
                      t.dj_call.score > 0   ? 'bg-sky-500/10 text-sky-300 border-sky-500/30' :
                                              'bg-rose-500/15 text-rose-300 border-rose-500/40'
                    }`}
                    title={(t.dj_call.signals || []).join('\n')}
                  >
                    <span className="truncate">{t.dj_call.badge}</span>
                    <span className="font-bold tabular-nums">{t.dj_call.score >= 0 ? `+${t.dj_call.score}` : t.dj_call.score}</span>
                  </div>
                )}
              </div>
              );
            })}
            {/* Mobile Archive files */}
            {archiveFiles.length > 0 && (
              <div className="mt-2 pt-2 border-t border-slate-700/40 space-y-1">
                <div className="text-[10px] text-slate-400 px-1">📁 Archive ({archiveFiles.length} file{archiveFiles.length > 1 ? 's' : ''})</div>
                {archiveFiles.map((af, fi) => (
                  <div key={fi} className="rounded-md bg-slate-800/40 border border-slate-700/30">
                    <button
                      onClick={() => setOpenArchive(openArchive === `m-${fi}` ? null : `m-${fi}`)}
                      className="w-full px-2 py-1.5 flex items-center justify-between text-left"
                      data-testid={`mobile-archive-file-${fi}`}
                    >
                      <span className="text-[10px] text-amber-300 font-mono">{af.file_name}</span>
                      <span className="text-[9px] text-slate-500">{af.count} tickets {openArchive === `m-${fi}` ? '▲' : '▼'}</span>
                    </button>
                    {openArchive === `m-${fi}` && (
                      <div className="px-1.5 pb-1.5 space-y-1 max-h-60 overflow-y-auto">
                        {af.tickets?.map((t, ti) => (
                          <div key={ti} className="p-1 rounded bg-slate-900/60 border border-slate-800/50">
                            <div className="flex items-center justify-center gap-0.5 flex-wrap">
                              {t.numbers?.map((n, i) => (
                                <Ball key={i} number={n} size="xs" maxNum={lotteryMode === 'euro' ? 50 : 42} />
                              ))}
                              {lotteryMode === 'swiss' && t.lucky != null && (
                                <div className="w-5 h-5 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center ml-0.5">
                                  <span className="text-white text-[8px] font-black">{t.lucky}</span>
                                </div>
                              )}
                              {lotteryMode === 'euro' && t.stars && t.stars.length > 0 && (
                                <>
                                  {t.stars.map((s, si) => (
                                    <div key={si} className="w-5 h-5 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center">
                                      <span className="text-white text-[8px] font-black">{s}</span>
                                    </div>
                                  ))}
                                </>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        {/* 🕒 Draw-Time Cutoff Banner */}
        {!generatorStatus.open && !isUnlimited && (
          <div className="mb-3 px-4 py-3 rounded-lg bg-gradient-to-r from-amber-900/30 via-rose-900/30 to-amber-900/30 border border-amber-500/40 flex flex-col items-center gap-1" data-testid="generator-closed-banner">
            <span className="text-amber-300 text-sm font-semibold flex items-center gap-1.5">
              🎻 Draw in session — generator paused 🎧
            </span>
            <span className="text-amber-200/80 text-xs text-center">
              {generatorStatus.reason}
              {generatorStatus.reopensAt && (
                <> · reopens at <span className="text-amber-300 font-mono">{new Date(generatorStatus.reopensAt).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span></>
              )}
            </span>
            <span className="text-amber-300/60 text-[10px] italic">Ya man, listen to the frequencies first 🥂</span>
          </div>
        )}

        {/* Ticket Limit Notice */}
        <div className="mb-3 px-3 py-2 rounded-lg bg-slate-800/40 border border-slate-700/40 flex flex-col items-center justify-center gap-1.5" data-testid="ticket-limit-notice">
          {isUnlimited ? (
            <span className="text-xs flex items-center gap-1.5 flex-wrap justify-center">
              <span className="px-2 py-0.5 rounded-full bg-gradient-to-r from-fuchsia-500/30 to-amber-500/30 text-amber-200 font-semibold">🎻 VIP unlocked</span>
              <span className="text-slate-400">— unlimited tickets on {lotteryMode === 'swiss' ? 'Swiss Lotto' : 'EuroMillions'}</span>
            </span>
          ) : (
            <span className="text-slate-500 text-xs text-center">You can generate up to <span className="text-amber-400 font-semibold">20 tickets</span> per {lotteryMode === 'swiss' ? 'Swiss Lotto' : 'EuroMillions'} draw <span className="text-slate-600">• auto-resets on new draw</span></span>
          )}
          {!isUnlimited && (
            <button
              onClick={() => { setShowCodeInput(!showCodeInput); setPromoMsg(null); }}
              className="text-[11px] text-slate-400 hover:text-amber-300 underline decoration-dotted"
              data-testid="promo-code-toggle"
            >
              {showCodeInput ? 'close' : 'Have a code?'}
            </button>
          )}
          {showCodeInput && !isUnlimited && (
            <div className="flex items-center gap-2 mt-1 w-full max-w-xs">
              <input
                type="text"
                inputMode="numeric"
                value={promoCode}
                onChange={(e) => setPromoCode(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') redeemPromoCode(); }}
                placeholder="Enter code"
                className="flex-1 px-2.5 py-1 rounded-md bg-slate-900/60 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-amber-400 placeholder-slate-600"
                data-testid="promo-code-input"
                autoFocus
              />
              <button
                onClick={redeemPromoCode}
                className="px-3 py-1 rounded-md bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-medium whitespace-nowrap transition-all"
                data-testid="promo-code-submit"
              >
                Unlock 🎻
              </button>
            </div>
          )}
          {promoMsg && (
            <span className={`text-[11px] ${promoMsg.ok ? 'text-emerald-400' : 'text-rose-400'}`} data-testid="promo-code-msg">
              {promoMsg.text}
            </span>
          )}
        </div>
        <div className="lucky-card p-6 mb-6" style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', borderColor: 'rgba(59,130,246,0.3)' } : {}}>
          <div className="flex items-center justify-center gap-3 mb-6">
            <button
              onClick={() => setShowGuide(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-500/15 border border-amber-500/30 text-amber-400 hover:bg-amber-500/25 transition-all"
              data-testid="how-to-use-inline-btn"
            >
              <span>?</span> How to Use
            </button>
            <h2 className="text-lg font-semibold text-slate-200">
              Your Lucky Numbers
            </h2>
          </div>
          
          {/* Ball Machine + Wheels */}
          <div className="flex items-start justify-center">
            {lotteryMode === 'swiss' ? (
              <>
                <SwissLottoBallMachine isProcessing={loading} winningNumbers={prediction?.main_prediction || []} />
                <div className="-ml-3 mt-10" style={{ transform: 'perspective(300px) rotateY(-20deg)' }}>
                  <LuckyWheel luckyNumber={prediction?.lucky_prediction || 1} isSpinning={wheelSpinning} />
                </div>
              </>
            ) : (
              <>
                <EuroMillionsBallMachine isProcessing={loading} winningNumbers={prediction?.main_prediction || []} />
                <div className="-ml-2 mt-8 flex flex-col gap-3" style={{ transform: 'perspective(300px) rotateY(-15deg)' }}>
                  <StarWheel starNumber={prediction?.stars_prediction?.[0] || 1} isSpinning={wheelSpinning} index={0} />
                  <StarWheel starNumber={prediction?.stars_prediction?.[1] || 2} isSpinning={wheelSpinning} index={1} />
                </div>
              </>
            )}
          </div>
          
          {/* Status / Mode Selection */}
          <div className="text-center mt-6 mb-4">
            {!loading && !prediction && (
              <p className="text-slate-400 text-sm">Press the button to generate your lucky numbers</p>
            )}
            {prediction && !loading && (
              <div className="flex flex-col items-center gap-3">
                {/* Mode Toggle Buttons - Both Swiss and Euro */}
                <div className="flex gap-2">
                  <button
                    onClick={() => { setGenerationMode('money'); fetchPrediction(); }}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 ${
                      generationMode === 'money'
                        ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-white shadow-lg shadow-amber-500/30 scale-105'
                        : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700 border border-slate-600/50'
                    }`}
                    data-testid="quick-money-mode-btn"
                  >
                    <span className="text-lg">💰</span>
                    <span>Money Mode</span>
                  </button>
                  <button
                    onClick={() => { setGenerationMode('jackpot'); fetchPrediction(); }}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 ${
                      generationMode === 'jackpot'
                        ? lotteryMode === 'swiss'
                          ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-lg shadow-emerald-500/30 scale-105'
                          : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30 scale-105'
                        : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700 border border-slate-600/50'
                    }`}
                    data-testid="quick-dreaming-mode-btn"
                  >
                    <span className="text-lg">🌟</span>
                    <span>Dreaming Mode</span>
                  </button>
                </div>
              </div>
            )}
          </div>
          
          {/* Generate Button */}
          <div className="text-center space-y-3">
            <button 
              onClick={fetchPrediction}
              disabled={loading || (!generatorStatus.open && !isUnlimited)}
              className="lucky-btn flex items-center gap-2 mx-auto"
              style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)', color: '#fbbf24' } : {}}
              data-testid="generate-btn"
              title={!generatorStatus.open && !isUnlimited ? `🎻 ${generatorStatus.reason}` : ''}
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              {loading ? '🤞 Finding Lucky Numbers...' 
                : (!generatorStatus.open && !isUnlimited) ? '🎻 Paused — Draw in Session 🎧'
                : lotteryMode === 'swiss' ? '🍀 Get New Numbers 🍀' : '⭐ Get New Numbers ⭐'}
            </button>
            
            {/* Olivia's Kiss of Luck */}
            <div className="relative inline-block">
              <button
                onClick={giveKissOfLuck}
                disabled={!prediction}
                className={`px-6 py-2 rounded-full font-bold text-sm transition-all duration-300 ${
                  !prediction
                    ? 'bg-slate-700/30 text-slate-500 cursor-not-allowed'
                    : oliviaKiss 
                      ? 'bg-gradient-to-r from-yellow-500 to-amber-500 text-white scale-110 shadow-lg shadow-yellow-500/50' 
                      : 'bg-gradient-to-r from-yellow-600/30 to-amber-600/30 text-yellow-300 hover:from-yellow-500/50 hover:to-amber-500/50 border border-yellow-500/30'
                }`}
                data-testid="olivia-kiss-btn"
              >
                🍀 Olivia's Kiss 🍀
              </button>
              
              {/* Flying Coins Animation */}
              {showKissHearts && (
                <div className="absolute inset-0 pointer-events-none overflow-visible">
                  {[...Array(12)].map((_, i) => (
                    <span
                      key={i}
                      className="absolute text-xl"
                      style={{
                        left: `${10 + Math.random() * 80}%`,
                        top: `-20%`,
                        animation: `fall ${0.6 + Math.random() * 0.8}s ease-in forwards`,
                        animationDelay: `${i * 0.07}s`,
                      }}
                    >
                      {['🪙', '💰', '🪙', '💵'][i % 4]}
                    </span>
                  ))}
                </div>
              )}
            </div>
            
            {/* Show Kiss Transformation */}
            {prediction?.kissed && prediction?.kissedFrom && prediction?.kissedTo && (
              <div className="mt-2 p-2 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                <p className="text-xs text-yellow-300 text-center">
                  🍀 Kissed: {prediction.kissedFrom.join(', ')} → <span className="font-bold text-yellow-200">{prediction.kissedTo.join(', ')}</span>
                  {prediction.circleUsed && <span className="ml-1 text-amber-300">(🔄 +Circle)</span>}
                </p>
              </div>
            )}
            
            {/* Sync Latest Results Button */}
            <button
              onClick={syncLatestResults}
              disabled={syncLoading}
              className={`px-4 py-2 rounded-full text-xs font-medium transition-all duration-300 ${
                syncLoading
                  ? 'bg-slate-700 text-slate-400 cursor-wait'
                  : 'bg-gradient-to-r from-green-600/30 to-emerald-600/30 text-green-300 hover:from-green-500/50 hover:to-emerald-500/50 border border-green-500/30'
              }`}
              data-testid="sync-results-btn"
            >
              {syncLoading ? '🔄 Syncing...' : '📡 Update Draws'}
            </button>
            
            {/* Sync Result Message */}
            {syncResult && (
              <div className={`mt-2 text-xs px-3 py-1 rounded-lg ${
                syncResult.error 
                  ? 'bg-red-500/20 text-red-300' 
                  : syncResult.total_new > 0 
                    ? 'bg-green-500/20 text-green-300'
                    : 'bg-slate-700/50 text-slate-400'
              }`}>
                {syncResult.error || syncResult.message}
              </div>
            )}
            
            {/* Auto-sync schedule info */}
            <p className="text-xs text-slate-500 mt-2 text-center">
              📅 Auto-sync: Wed & Sat (Swiss), Tue & Fri (Euro) at 21:00 UTC
            </p>
          </div>
        </div>

        {/* Personalize Card */}
        <div className="lucky-card p-4 mb-4" style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', borderColor: 'rgba(59,130,246,0.3)' } : {}}>
          <div className="flex items-center justify-between cursor-pointer" onClick={() => setShowPersonal(!showPersonal)}>
            <span className="font-semibold text-slate-200">Personalize Your Numbers</span>
            {showPersonal ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </div>
          
          {showPersonal && (
            <div className="mt-4 space-y-3">
              {/* Persona Selection - Secret modifiers! */}
              <div>
                <label className="text-xs text-slate-400 mb-2 block">Choose Your Lucky Persona ✨</label>
                <div className="flex flex-wrap gap-2">
                  {personas.map((persona, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        togglePersona(persona.name);
                        // Set full name to selected personas
                        const newPersonas = activePersonas.includes(persona.name) 
                          ? activePersonas.filter(p => p !== persona.name)
                          : (persona.name === "Olivia" ? ["Olivia"] : 
                             activePersonas.includes("Olivia") ? [persona.name] : 
                             [...activePersonas, persona.name]);
                        setFullName(newPersonas.join(' & ') || '');
                      }}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        activePersonas.includes(persona.name)
                          ? lotteryMode === 'swiss' 
                            ? 'bg-amber-500 text-gray-900 ring-2 ring-amber-300' 
                            : 'bg-blue-500 text-white ring-2 ring-blue-300'
                          : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600'
                      }`}
                      data-testid={`persona-${persona.name.toLowerCase()}`}
                    >
                      {persona.name}
                    </button>
                  ))}
                </div>
                {activePersonas.length > 0 && (
                  <p className="text-xs text-slate-500 mt-2 italic">
                    ✨ Secret magic activated...
                  </p>
                )}
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Birthday</label>
                <input
                  type="text"
                  value={birthday}
                  onChange={(e) => setBirthday(e.target.value)}
                  placeholder="DD/MM/YYYY"
                  className="w-full px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-600 text-white placeholder-slate-500 focus:border-amber-500/50 focus:outline-none text-sm"
                  data-testid="birthday-input"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Full Name (optional)</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                  className="w-full px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-600 text-white placeholder-slate-500 focus:border-amber-500/50 focus:outline-none text-sm"
                  data-testid="name-input"
                />
              </div>
              <button 
                onClick={fetchPrediction}
                disabled={loading}
                className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all duration-300 ${
                  lotteryMode === 'swiss'
                    ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-gray-900 hover:from-amber-400 hover:to-amber-500 shadow-lg'
                    : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-400 hover:to-blue-500 shadow-lg'
                }`}
                data-testid="persona-generate-btn"
              >
                {loading ? (
                  <><Sparkles className="w-5 h-5 animate-spin" /><span>Generating...</span></>
                ) : (
                  <><Sparkles className="w-5 h-5" /><span>
                    {activePersonas.length > 0 
                      ? `Generate with ${activePersonas.join(' & ')}` 
                      : birthday 
                        ? 'Generate with Birthday' 
                        : 'Generate Lucky Numbers'}
                  </span></>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Lock Positions Card */}
        <div className="lucky-card p-4 mb-4" style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', borderColor: 'rgba(59,130,246,0.3)' } : {}}>
          <div className="flex items-center justify-between cursor-pointer" onClick={() => setShowLocks(!showLocks)} data-testid="lock-positions-toggle">
            <span className="font-semibold text-slate-200 flex items-center gap-2">
              🔒 Lock Positions
              {getLockedCount() > 0 && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${lotteryMode === 'swiss' ? 'bg-amber-500/20 text-amber-400' : 'bg-blue-500/20 text-blue-400'}`}>
                  {getLockedCount()}/{maxLocks}
                </span>
              )}
            </span>
            {showLocks ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </div>
          
          {showLocks && (
            <div className="mt-4">
              <p className="text-xs text-slate-400 mb-3">
                Lock 1-{maxLocks} numbers at specific positions. Generator fills the rest.
              </p>
              
              <div className={`grid gap-2 mb-3 ${lotteryMode === 'swiss' ? 'grid-cols-6' : 'grid-cols-5'}`}>
                {Array.from({ length: maxPositions }, (_, idx) => `p${idx + 1}`).map((pos, idx) => (
                  <div key={pos} className="text-center">
                    <label className="text-xs text-slate-500 block mb-1">P{idx + 1}</label>
                    <input
                      type="number"
                      min="1"
                      max={maxNum}
                      value={lockedPositions[pos] || ""}
                      onChange={(e) => handleLockChange(pos, e.target.value)}
                      placeholder="—"
                      disabled={lockedPositions[pos] === "" && getLockedCount() >= maxLocks}
                      className={`w-full px-1 py-2 rounded-lg text-center text-sm font-bold
                        ${lockedPositions[pos] 
                          ? lotteryMode === 'swiss' ? 'bg-amber-500/20 border-amber-500/50 text-amber-400' : 'bg-blue-500/20 border-blue-500/50 text-blue-400'
                          : 'bg-slate-800/50 border-slate-600 text-white placeholder-slate-600'}
                        ${lockedPositions[pos] === "" && getLockedCount() >= maxLocks ? 'opacity-50 cursor-not-allowed' : ''}
                        border focus:outline-none`}
                      data-testid={`lock-${pos}`}
                    />
                  </div>
                ))}
              </div>
              
              {getLockedCount() > 0 && (
                <button
                  onClick={() => setLockedPositions({ p1: "", p2: "", p3: "", p4: "", p5: "", p6: "" })}
                  className="mt-3 w-full py-2 rounded-lg bg-slate-700/50 text-slate-400 text-sm hover:bg-slate-700 transition-colors"
                  data-testid="clear-locks-btn"
                >
                  Clear All Locks
                </button>
              )}
            </div>
          )}
        </div>

        {/* Multi-Ticket Mode */}
        <div className="lucky-card p-4 mb-4" style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', borderColor: 'rgba(59,130,246,0.3)' } : {}}>
          <div className="flex items-center justify-between cursor-pointer" onClick={() => setShowMultiTickets(!showMultiTickets)} data-testid="multi-tickets-toggle">
            <span className="font-semibold text-slate-200 flex items-center gap-2">
              🎫 Multiple Tickets
              {numTickets > 1 && (
                <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full">{numTickets} tickets</span>
              )}
            </span>
            {showMultiTickets ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </div>
          
          {showMultiTickets && (
            <div className="mt-4">
              <p className="text-xs text-slate-400 mb-3">
                Generate multiple ticket predictions ranked by confidence. <span className={lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400'}>{lotteryMode === 'swiss' ? '2.50 CHF' : '3.50 CHF'} per ticket</span>
              </p>
              
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm text-slate-300">How many tickets?</span>
                  <span className={`text-xs font-semibold ${lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400'}`}>
                    Total: {(numTickets * (lotteryMode === 'swiss' ? 2.5 : 3.5)).toFixed(2)} CHF
                  </span>
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {(lotteryMode === 'swiss' ? [2, 3, 5, 8, 10, 15, 20] : [1, 3, 5, 8, 10, 15, 20]).map(n => (
                    <button
                      key={n}
                      onClick={() => setNumTickets(n)}
                      className={`flex flex-col items-center px-2 py-1.5 rounded-lg text-sm font-medium transition-all
                        ${numTickets === n 
                          ? 'bg-emerald-500 text-white' 
                          : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'}`}
                      data-testid={`tickets-${n}`}
                    >
                      <span className="font-bold">{n}</span>
                      <span className={`text-[10px] ${numTickets === n ? 'text-emerald-100' : 'text-slate-500'}`}>
                        {(n * (lotteryMode === 'swiss' ? 2.5 : 3.5)).toFixed(1)}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* GENERATION MODE TOGGLE */}
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm text-slate-300">Generation Mode</span>
                </div>
                {lotteryMode === 'swiss' ? (
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setGenerationMode('jackpot')}
                    className={`flex flex-col items-center px-3 py-2.5 rounded-lg transition-all ${
                      generationMode === 'jackpot'
                        ? 'bg-gradient-to-r from-amber-600 to-amber-700 text-white shadow-lg shadow-amber-500/25'
                        : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                    }`}
                    data-testid="mode-jackpot"
                  >
                    <span className="font-bold text-sm">Jackpot</span>
                    <span className="text-[10px] opacity-75">All patterns</span>
                  </button>
                  <button
                    onClick={() => setGenerationMode('money')}
                    className={`flex flex-col items-center px-3 py-2.5 rounded-lg transition-all ${
                      generationMode === 'money'
                        ? 'bg-gradient-to-r from-emerald-600 to-emerald-700 text-white shadow-lg shadow-emerald-500/25'
                        : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                    }`}
                    data-testid="mode-money"
                  >
                    <span className="font-bold text-sm">Money Mode</span>
                    <span className="text-[10px] opacity-75">DNA + Sleepers</span>
                  </button>
                </div>
                ) : (
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setGenerationMode('jackpot')}
                    className={`flex flex-col items-center px-3 py-2.5 rounded-lg transition-all ${
                      generationMode === 'jackpot'
                        ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-500/25'
                        : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                    }`}
                    data-testid="jackpot-mode-btn"
                  >
                    <span className="font-bold text-sm">Jackpot</span>
                    <span className="text-[10px] opacity-75">All 5 + 2 stars</span>
                  </button>
                  <button
                    onClick={() => setGenerationMode('money')}
                    className={`flex flex-col items-center px-3 py-2.5 rounded-lg transition-all ${
                      generationMode === 'money'
                        ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-white shadow-lg shadow-amber-500/25'
                        : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                    }`}
                    data-testid="money-mode-btn"
                  >
                    <span className="font-bold text-sm">Money Mode</span>
                    <span className="text-[10px] opacity-75">3+ hits focus</span>
                  </button>
                </div>
                )}
                {generationMode === 'money' && (
                  <div className="mt-2 p-2 rounded-lg bg-amber-500/10 border border-amber-500/30">
                    <p className="text-xs text-amber-400 text-center">
                      {lotteryMode === 'swiss' 
                        ? '💰 DNA + Sleepers + P2 engine — target 3+ numbers'
                        : '💰 Focus on consistent small wins: 3+2⭐ (~€50-100), 3+1⭐ (~€15-20)'}
                    </p>
                  </div>
                )}
              </div>
              
              {/* Display all tickets */}
              {prediction?.all_tickets && prediction.all_tickets.length > 1 && (
                <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
                  {prediction.all_tickets.map((ticket, idx) => (
                    <div 
                      key={idx}
                      className={`flex items-center gap-3 p-2 rounded-lg ${
                        idx === 0 
                          ? lotteryMode === 'swiss' 
                            ? 'bg-gradient-to-r from-amber-500/20 to-amber-600/10 border border-amber-500/30'
                            : 'bg-gradient-to-r from-blue-500/20 to-blue-600/10 border border-blue-500/30'
                          : 'bg-slate-800/50 border border-slate-700/50'
                      }`}
                    >
                      <span className={`text-xs font-bold w-6 ${idx === 0 ? (lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400') : 'text-slate-500'}`}>
                        #{ticket.ticket_num}
                      </span>
                      {/* Scenario label for EuroMillions */}
                      {lotteryMode === 'euro' && ticket.scenario && (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                          ticket.scenario === 'low' ? 'bg-green-500/20 text-green-400' :
                          ticket.scenario === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-purple-500/20 text-purple-400'
                        }`}>
                          {ticket.scenario === 'low' ? '📉 Low' : ticket.scenario === 'medium' ? '📊 Mid' : '📈 High'}
                        </span>
                      )}
                      {/* Ticket type for Swiss Money Mode */}
                      {lotteryMode === 'swiss' && ticket.ticket_type && (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                          ticket.ticket_type === 'crazy' ? 'bg-purple-500/20 text-purple-400' :
                          ticket.ticket_type === 'spread' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-emerald-500/20 text-emerald-400'
                        }`}>
                          {ticket.ticket_type === 'crazy' ? '🤪' : ticket.ticket_type === 'spread' ? '🎯' : '🧬'}
                        </span>
                      )}
                      <div className="flex gap-1.5 flex-1">
                        {ticket.numbers.map((num, i) => (
                          <Ball key={i} number={num} size="xs" maxNum={maxNum} />
                        ))}
                        {lotteryMode === 'euro' && ticket.stars && ticket.stars.map((star, i) => (
                          <StarBall key={`star-${i}`} number={star} size="xs" />
                        ))}
                        {lotteryMode === 'swiss' && ticket.lucky && (
                          <span className="text-xs text-amber-400 font-bold ml-1">L:{ticket.lucky}</span>
                        )}
                      </div>
                      <span className={`text-xs ${idx === 0 ? (lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400') : 'text-slate-500'}`}>
                        {Math.round(ticket.confidence)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
              
              <button 
                onClick={fetchPrediction}
                disabled={loading}
                className={`mt-4 w-full py-2.5 rounded-xl font-bold flex items-center justify-center gap-2 transition-all duration-300 shadow-lg disabled:opacity-50 ${
                  lotteryMode === 'euro' && generationMode === 'money'
                    ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-white hover:from-amber-400 hover:to-amber-500'
                    : 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white hover:from-emerald-400 hover:to-emerald-500'
                }`}
                data-testid="generate-tickets-btn"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                {loading 
                  ? 'Generating...' 
                  : lotteryMode === 'euro' && generationMode === 'money'
                    ? `💰 Generate ${numTickets} Money Mode Ticket${numTickets > 1 ? 's' : ''}`
                    : `🎫 Generate ${numTickets} Ticket${numTickets > 1 ? 's' : ''}`
                }
              </button>
            </div>
          )}
        </div>

        {/* Bonus Numbers */}
        {prediction && (
          <div className="lucky-card p-4 mb-4" style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', borderColor: 'rgba(59,130,246,0.3)' } : {}}>
            <div className="flex items-center justify-between cursor-pointer" onClick={() => setShowBonus(!showBonus)}>
              <span className="font-semibold text-slate-200 flex items-center gap-2">
                <Gift className={`w-4 h-4 ${lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400'}`} /> Bonus Numbers
              </span>
              {showBonus ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
            </div>
            
            {showBonus && (
              <div className="mt-4">
                <div className="flex flex-wrap justify-center gap-2">
                  {prediction.alternate_numbers?.map((n, i) => (
                    <Ball key={i} number={n} size="sm" maxNum={maxNum} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Stats Card */}
        {stats && (
          <div className="lucky-card p-4 mb-4" style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', borderColor: 'rgba(59,130,246,0.3)' } : {}}>
            <div className="text-center">
              <span className="text-slate-400 text-xs">Mapped from </span>
              <span className={`font-bold text-sm ${lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400'}`}>
                {stats.total_draws || stats.total || 0}
              </span>
              <span className="text-slate-400 text-xs"> celestial cycles</span>
              
              {/* Update Results Button - EuroMillions only */}
              {lotteryMode === 'euro' && (
                <button
                  onClick={async () => {
                    setUpdateLoading(true);
                    try {
                      const res = await axios.post(`${API}/euromillions/update-results`);
                      setUpdateMessage(`✅ ${res.data.message} Latest: ${res.data.latest_draw?.date}`);
                      // Refresh stats
                      const statsRes = await axios.get(`${API}/euromillions/stats`);
                      setStats(statsRes.data);
                    } catch (err) {
                      setUpdateMessage('❌ Update failed');
                    }
                    setUpdateLoading(false);
                    setTimeout(() => setUpdateMessage(''), 5000);
                  }}
                  disabled={updateLoading}
                  className="ml-3 px-3 py-1 text-xs rounded-full bg-blue-600/30 text-blue-300 hover:bg-blue-600/50 transition-all"
                  data-testid="update-results-btn"
                >
                  {updateLoading ? '🔄 Updating...' : '🔄 Update Results'}
                </button>
              )}
            </div>
            {updateMessage && (
              <div className="text-center mt-2 text-xs text-emerald-400">{updateMessage}</div>
            )}
          </div>
        )}

        {/* Prediction History */}
        <div className="lucky-card p-4 mb-4" style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', borderColor: 'rgba(59,130,246,0.3)' } : {}}>
          <div className="flex items-center justify-between cursor-pointer" onClick={() => setShowHistory(!showHistory)}>
            <span className="font-semibold text-slate-200 flex items-center gap-2">
              <History className={`w-4 h-4 ${lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400'}`} /> Prediction History
              {historyStats?.total_predictions > 0 && (
                <span className="text-xs text-slate-500">({historyStats.total_predictions})</span>
              )}
            </span>
            {showHistory ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </div>
          
          {showHistory && (
            <div className="mt-4">
              {/* Stats summary */}
              {historyStats && historyStats.total_predictions > 0 && (
                <div className="flex justify-between items-center mb-3 text-xs text-slate-400">
                  <span>📊 {historyStats.total_predictions} predictions saved</span>
                  <button 
                    onClick={clearHistory}
                    className="flex items-center gap-1 text-red-400 hover:text-red-300 transition-colors"
                  >
                    <Trash2 className="w-3 h-3" /> Clear
                  </button>
                </div>
              )}
              
              {/* History list */}
              <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
                {history.length === 0 ? (
                  <div className="text-center text-slate-500 text-sm py-4">
                    No predictions yet. Generate some!
                  </div>
                ) : (
                  history.map((h, idx) => (
                    <div 
                      key={h.id || idx}
                      className={`p-2 rounded-lg text-xs ${
                        lotteryMode === 'swiss'
                          ? 'bg-gradient-to-r from-amber-500/10 to-amber-600/5 border border-amber-500/20'
                          : 'bg-gradient-to-r from-blue-500/10 to-blue-600/5 border border-blue-500/20'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-slate-500">
                          {new Date(h.created_at).toLocaleDateString('de-CH')} {new Date(h.created_at).toLocaleTimeString('de-CH', {hour: '2-digit', minute:'2-digit'})}
                        </span>
                        <span className={`font-medium ${lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400'}`}>
                          {h.confidence?.toFixed(0)}%
                        </span>
                      </div>
                      <div className="flex items-center gap-1 flex-wrap">
                        {h.numbers?.map((n, i) => (
                          <Ball key={i} number={n} size="xs" maxNum={lotteryMode === 'swiss' ? 42 : 50} />
                        ))}
                        {h.lucky_number && lotteryMode === 'swiss' && (
                          <span className="ml-2 text-amber-400">🍀 {h.lucky_number}</span>
                        )}
                        {h.stars && lotteryMode === 'euro' && (
                          <span className="ml-2 text-yellow-400">⭐ {h.stars.join(', ')}</span>
                        )}
                      </div>
                      {/* 🎻 V2 Detective suspect story */}
                      {h.suspect_story && h.suspect_story.length > 0 && (
                        <div className="mt-1.5 pt-1.5 border-t border-slate-700/30">
                          {h.hero_number != null && (
                            <div className="text-[10px] mb-1 flex items-center gap-1 flex-wrap">
                              <span className="text-fuchsia-400">🎻 Hero:</span>
                              <span className="font-bold text-fuchsia-200">{h.hero_number}</span>
                              <span className="text-slate-500">· convicted by</span>
                              <span className="text-fuchsia-300">{h.suspect_story[0]?.conviction}×</span>
                              <span className="text-slate-500">patterns</span>
                            </div>
                          )}
                          <div className="space-y-0.5">
                            {h.suspect_story.map((s, si) => (
                              <div key={si} className="text-[10px] text-slate-400 flex items-start gap-1">
                                <span className="text-indigo-300 font-mono w-5 flex-shrink-0">#{s.n}</span>
                                <span className="text-slate-600">→</span>
                                <span className="truncate" title={s.patterns.join(', ')}>
                                  {s.patterns.slice(0, 2).map((p, pi) => (
                                    <span key={pi} className="mr-1 px-1 rounded bg-indigo-500/10 text-indigo-300">{
                                      p.replace(/WEAK-BOOST-/g, '')
                                       .replace(/P4P5-CROSS-50/g, 'P4P5×')
                                       .replace(/P4P5-CROSS/g, 'P4P5')
                                       .replace(/P4P5-hidden/g, 'P4P5·h')
                                       .replace(/DAY-CHAIN/g, 'DATE')
                                       .replace(/DAY-DIRECT/g, 'DAY')
                                       .replace(/NEXT-DATE/g, 'NEXT-D')
                                       .replace(/star-Q/g, '⭐Q')
                                    }</span>
                                  ))}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {h.matches !== null && h.matches !== undefined && (
                        <div className="mt-1 text-emerald-400">
                          ✓ {h.matches} match{h.matches !== 1 ? 'es' : ''}
                          {h.lucky_match && ' + Lucky!'}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* SWISS SLEEPER RADAR */}
        {lotteryMode === 'swiss' && isUnlimited && (
          <div className="lucky-card p-4 mb-4" data-testid="swiss-sleeper-panel">
            <button 
              onClick={() => setShowSwissSleepers(!showSwissSleepers)}
              className="w-full flex items-center justify-between text-left"
              data-testid="swiss-sleeper-toggle"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">😴</span>
                <span className="font-semibold text-slate-200">Celestial Radar</span>
                <span className="text-xs text-slate-400">Planetary alignments shifting</span>
              </div>
              <span className="text-slate-400">{showSwissSleepers ? '▲' : '▼'}</span>
            </button>
            
            {showSwissSleepers && (
              <div className="mt-3" data-testid="swiss-sleeper-content">
                {swissSleeperLoading ? (
                  <div className="text-center text-slate-400 py-4">Reading planetary positions...</div>
                ) : swissSleeperData ? (
                  <div className="space-y-3">
                    <div className="text-xs text-slate-400 mb-2">
                      Last draw: {swissSleeperData.last_draw} | Orbital cycle: ~{swissSleeperData.expected_gap} rotations
                    </div>

                    {/* 🌠 POOL TOP 6 — best suspects from the cosmic pool */}
                    {swissSleeperData.pool_top_6?.length > 0 && (
                      <div className="rounded-lg border border-amber-500/30 bg-gradient-to-br from-amber-950/30 to-slate-900/50 p-2.5"
                           data-testid="swiss-pool-top6">
                        <div className="text-xs font-semibold text-amber-300 mb-1.5 flex items-center justify-between">
                          <span className="flex items-center gap-1">
                            <span>🌠</span> TOP 6 SUSPECTS · for d {swissSleeperData.pool_target_date || '—'}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            from {swissSleeperData.pool_built_from || '—'}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-1.5">
                          {swissSleeperData.pool_top_6.map((s) => {
                            const pinned = !!s.pinned;
                            const drunk = !!s.drunk;
                            const ringClass = pinned
                              ? 'border-rose-400/70 bg-rose-500/15 text-rose-200'
                              : drunk
                              ? 'border-violet-400/70 bg-violet-500/15 text-violet-200'
                              : 'border-emerald-500/50 bg-emerald-600/10 text-emerald-200';
                            return (
                              <div
                                key={s.n}
                                className={`relative px-1.5 py-1 rounded border ${ringClass} text-[11px] font-bold`}
                                title={`${s.lenses?.join(' · ') || ''}\nslots: ${(s.slots || []).join(', ')}\ndepth ${s.depth}${pinned ? ' · DJ-pinned' : ''}${drunk ? ' · drunk-cosmos' : ''}`}
                                data-testid={`swiss-pool-top6-${s.n}`}
                              >
                                <div className="flex items-baseline justify-between gap-1">
                                  <span className="text-base tabular-nums">{s.n}</span>
                                  <span className="text-[8px] opacity-70">
                                    {pinned ? '📌' : drunk ? '🍀' : `d${s.depth}`}
                                  </span>
                                </div>
                                <div className="text-[8px] opacity-60 truncate">
                                  {(s.slots || []).join('·')}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    
                    {/* Deep Sleepers */}
                    {swissSleeperData.deep?.length > 0 && (
                      <div>
                        <div className="text-xs font-semibold text-red-400 mb-1 flex items-center gap-1">
                          <span>🔴</span> DEEP ORBIT — {swissSleeperData.deep.length} numbers in distant constellation
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {swissSleeperData.deep.map(s => (
                            <div key={s.number} className="relative group">
                              <div className="w-10 h-10 rounded-full bg-red-900/40 border-2 border-red-500/60 flex items-center justify-center text-sm font-bold text-red-300 hover:scale-110 transition-transform cursor-default">
                                {s.number}
                              </div>
                              <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-700 text-xs px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                {s.gap}d ({s.ratio}x)
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Wake Zone */}
                    {swissSleeperData.wake?.length > 0 && (
                      <div>
                        <div className="text-xs font-semibold text-amber-400 mb-1 flex items-center gap-1">
                          <span>⏰</span> APPROACHING EARTH — {swissSleeperData.wake.length} numbers entering our orbit
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {swissSleeperData.wake.map(s => (
                            <div key={s.number} className="relative group">
                              <div className="w-10 h-10 rounded-full bg-amber-900/30 border-2 border-amber-500/50 flex items-center justify-center text-sm font-bold text-amber-300 hover:scale-110 transition-transform cursor-default">
                                {s.number}
                              </div>
                              <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-700 text-xs px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                {s.gap}d ({s.ratio}x)
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Fresh (recently appeared) */}
                    <div>
                      <div className="text-xs font-semibold text-emerald-400 mb-1 flex items-center gap-1">
                        <span>🟢</span> GROUNDED — Recently visited Earth
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {swissSleeperData.fresh?.slice(0, 15).map(s => (
                          <span key={s.number} className="px-2 py-0.5 rounded bg-emerald-900/20 border border-emerald-600/30 text-emerald-400 text-xs">
                            {s.number}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-slate-500 py-3 text-sm">No celestial data available</div>
                )}
              </div>
            )}
          </div>
        )}

        {/* SLEEPER RADAR - EuroMillions Only — VIP only (pattern reveal) */}
        {lotteryMode === 'euro' && isUnlimited && (
          <div className="lucky-card p-4 mb-4" data-testid="sleeper-radar-panel">
            <button 
              onClick={() => setShowSleeperRadar(!showSleeperRadar)}
              className="w-full flex items-center justify-between text-left"
              data-testid="sleeper-radar-toggle"
            >
              <div className="flex items-center gap-2">
                <Eye className="w-5 h-5 text-purple-400" />
                <span className="font-semibold text-slate-200">Celestial Radar</span>
                <span className="text-xs text-purple-400/70">(Planetary Convergence)</span>
              </div>
              {showSleeperRadar ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </button>
            
            {showSleeperRadar && (
              <div className="mt-4 space-y-4">
                {sleeperLoading ? (
                  <div className="flex items-center justify-center py-8 gap-2">
                    <RefreshCw className="w-5 h-5 text-purple-400 animate-spin" />
                    <span className="text-slate-400 text-sm">Scanning celestial frequencies...</span>
                  </div>
                ) : sleeperData ? (
                  <>
                    {/* Radar Header Stats */}
                    <div className="flex items-center justify-between text-xs text-slate-500">
                      <span>Last Draw: <span className="text-slate-300 font-medium">{sleeperData.last_draw}</span></span>
                      <span>{sleeperData.total_draws_analyzed} celestial cycles mapped</span>
                    </div>

                    {/* 🌠 POOL TOP 6 — best suspects from the cosmic pool */}
                    {sleeperData.pool_top_6?.length > 0 && (
                      <div className="rounded-lg border border-amber-500/30 bg-gradient-to-br from-amber-950/30 to-slate-900/50 p-2.5"
                           data-testid="euro-pool-top6">
                        <div className="text-xs font-semibold text-amber-300 mb-1.5 flex items-center justify-between">
                          <span className="flex items-center gap-1">
                            <span>🌠</span> TOP 6 SUSPECTS · for d {sleeperData.pool_target_date || '—'}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            from {sleeperData.pool_built_from || '—'}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-1.5">
                          {sleeperData.pool_top_6.map((s) => {
                            const pinned = !!s.pinned;
                            const drunk = !!s.drunk;
                            const ringClass = pinned
                              ? 'border-rose-400/70 bg-rose-500/15 text-rose-200'
                              : drunk
                              ? 'border-violet-400/70 bg-violet-500/15 text-violet-200'
                              : 'border-emerald-500/50 bg-emerald-600/10 text-emerald-200';
                            return (
                              <div
                                key={s.n}
                                className={`relative px-1.5 py-1 rounded border ${ringClass} text-[11px] font-bold`}
                                title={`${s.lenses?.join(' · ') || ''}\nslots: ${(s.slots || []).join(', ')}\ndepth ${s.depth}${pinned ? ' · DJ-pinned' : ''}${drunk ? ' · drunk-cosmos' : ''}`}
                                data-testid={`euro-pool-top6-${s.n}`}
                              >
                                <div className="flex items-baseline justify-between gap-1">
                                  <span className="text-base tabular-nums">{s.n}</span>
                                  <span className="text-[8px] opacity-70">
                                    {pinned ? '📌' : drunk ? '🍀' : `d${s.depth}`}
                                  </span>
                                </div>
                                <div className="text-[8px] opacity-60 truncate">
                                  {(s.slots || []).join('·')}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    
                    {/* Top Number Sleepers */}
                    <div className="p-3 rounded-lg" style={{ background: 'linear-gradient(135deg, rgba(147,51,234,0.12) 0%, rgba(79,70,229,0.08) 100%)', border: '1px solid rgba(147,51,234,0.25)' }}>
                      <div className="flex items-center gap-2 mb-3">
                        <Zap className="w-4 h-4 text-purple-400" />
                        <span className="text-sm font-semibold text-purple-300">Mercury Rising</span>
                      </div>
                      <div className="space-y-2">
                        {sleeperData.sleeper_report?.slice(0, 6).map((s, idx) => (
                          <div key={s.num} className="flex items-center gap-2" data-testid={`sleeper-number-${s.num}`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                              idx < 2 ? 'ring-2 ring-purple-400/60' : ''
                            }`} style={{
                              background: s.composite_score >= 60 
                                ? 'linear-gradient(135deg, #9333ea 0%, #7c3aed 100%)' 
                                : s.composite_score >= 45 
                                  ? 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)'
                                  : 'linear-gradient(135deg, #475569 0%, #334155 100%)',
                              color: 'white',
                              boxShadow: s.composite_score >= 60 ? '0 0 12px rgba(147,51,234,0.4)' : '0 2px 4px rgba(0,0,0,0.3)'
                            }}>
                              {s.num}
                            </div>
                            
                            {/* 🎻 Saturn Ring — Circle partner orbit */}
                            {s.circle_partner && s.circle_partner >= 1 && s.circle_partner <= 50 && (
                              <div
                                className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border border-indigo-400/50"
                                style={{
                                  background: s.circle_partner_conviction >= 3
                                    ? 'linear-gradient(135deg, rgba(99,102,241,0.3), rgba(79,70,229,0.5))'
                                    : 'rgba(99,102,241,0.15)',
                                  color: s.circle_partner_conviction >= 3 ? '#c7d2fe' : '#94a3b8',
                                  boxShadow: s.circle_partner_conviction >= 4 ? '0 0 8px rgba(99,102,241,0.5)' : 'none'
                                }}
                                data-testid={`sleeper-circle-${s.circle_partner}`}
                                title={`Saturn Ring: ${s.num} + 25 = ${s.circle_partner}  (Detective conviction: ${s.circle_partner_conviction || 0})`}
                              >
                                {s.circle_partner}
                              </div>
                            )}
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <div className="flex-1 h-1.5 rounded-full bg-slate-700/50 overflow-hidden">
                                  <div className="h-full rounded-full transition-all duration-500" style={{
                                    width: `${Math.min(100, s.composite_score * 1.3)}%`,
                                    background: s.composite_score >= 60 
                                      ? 'linear-gradient(90deg, #a855f7, #ec4899)' 
                                      : s.composite_score >= 45 
                                        ? 'linear-gradient(90deg, #818cf8, #a78bfa)'
                                        : 'linear-gradient(90deg, #64748b, #94a3b8)'
                                  }} />
                                </div>
                                <span className="text-xs text-slate-400 w-8 text-right">{s.composite_score.toFixed(0)}</span>
                              </div>
                              <div className="flex items-center gap-1 mt-0.5 flex-wrap">
                                <span className="text-[10px] text-slate-500 whitespace-nowrap">
                                  {s.overdue >= 1.0 ? `${s.overdue.toFixed(1)}x distant` : `orbit ${s.gap}`}
                                </span>
                                {/* 🎻 Detective Conviction crossover */}
                                {s.detective_conviction >= 5 && (
                                  <span className="text-[10px] px-1.5 rounded bg-fuchsia-500/20 text-fuchsia-300 font-semibold whitespace-nowrap" title={`V2 Detective: ${s.detective_conviction} patterns`}>
                                    LOCK ×{s.detective_conviction}
                                  </span>
                                )}
                                {s.detective_conviction >= 3 && s.detective_conviction < 5 && (
                                  <span className="text-[10px] px-1.5 rounded bg-indigo-500/20 text-indigo-300 whitespace-nowrap" title={`V2 Detective: ${s.detective_conviction} patterns`}>
                                    DEEP ×{s.detective_conviction}
                                  </span>
                                )}
                                {s.tease_score >= 3 && (
                                  <span className="text-[10px] px-1 rounded bg-purple-500/20 text-purple-300 whitespace-nowrap">VENUS</span>
                                )}
                                {s.circle_boost > 1.5 && (
                                  <span className="text-[10px] px-1 rounded bg-indigo-500/20 text-indigo-300 whitespace-nowrap">SATURN</span>
                                )}
                                {s.overdue >= 3.0 && (
                                  <span className="text-[10px] px-1 rounded bg-red-500/20 text-red-300 whitespace-nowrap">MARS</span>
                                )}
                              </div>
                              {/* 🎻 Orbit family — small dots of morph candidates */}
                              {s.orbit_family && s.orbit_family.length > 0 && (
                                <div className="flex items-center gap-1 mt-1">
                                  <span className="text-[9px] text-slate-600">orbit:</span>
                                  {s.orbit_family.slice(0, 4).map((n) => {
                                    const conv = (s.orbit_convictions && s.orbit_convictions[String(n)]) || 0;
                                    return (
                                      <span
                                        key={n}
                                        className="inline-flex items-center justify-center w-4 h-4 rounded-full text-[8px] font-semibold"
                                        style={{
                                          background: conv >= 3 ? 'rgba(236,72,153,0.25)' : 'rgba(71,85,105,0.4)',
                                          color: conv >= 3 ? '#fbcfe8' : '#94a3b8',
                                          border: conv >= 5 ? '1px solid rgba(236,72,153,0.6)' : 'none',
                                        }}
                                        title={`${n} — Detective conviction: ${conv}`}
                                        data-testid={`orbit-num-${n}`}
                                      >
                                        {n}
                                      </span>
                                    );
                                  })}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {/* Star Sleepers */}
                    <div className="p-3 rounded-lg" style={{ background: 'linear-gradient(135deg, rgba(251,191,36,0.1) 0%, rgba(245,158,11,0.06) 100%)', border: '1px solid rgba(251,191,36,0.25)' }}>
                      <div className="flex items-center gap-2 mb-2">
                        <Star className="w-4 h-4 text-amber-400" fill="currentColor" />
                        <span className="text-sm font-semibold text-amber-300">Constellation Signals</span>
                      </div>
                      <div className="flex flex-wrap gap-3">
                        {sleeperData.star_sleepers?.slice(0, 5).map((s) => (
                          <div key={s.star} className="flex items-center gap-1.5 px-2 py-1 rounded-lg" 
                            style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.2)' }}
                            data-testid={`sleeper-star-${s.star}`}
                          >
                            <div className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold" style={{
                              background: s.overdue >= 5 
                                ? 'linear-gradient(135deg, #f59e0b, #ef4444)' 
                                : 'linear-gradient(135deg, #fbbf24, #f59e0b)',
                              color: '#1e1b4b'
                            }}>
                              {s.star}
                            </div>
                            <div className="text-[10px]">
                              <div className="text-amber-300 font-medium">{s.overdue.toFixed(1)}x</div>
                              <div className="text-slate-500">cycle {s.gap}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {/* D+1 Forecast */}
                    {sleeperData.forecast?.length > 0 && (
                      <div className="p-3 rounded-lg" style={{ background: 'linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(5,150,105,0.06) 100%)', border: '1px solid rgba(16,185,129,0.25)' }}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-emerald-400" />
                            <span className="text-sm font-semibold text-emerald-300">Planetary Forecast</span>
                          </div>
                          <span className="text-xs text-emerald-400/70">{sleeperData.forecast[0].confidence.toFixed(0)}% alignment</span>
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                          {sleeperData.forecast[0].numbers.map((n, i) => (
                            <Ball key={i} number={n} size="sm" maxNum={50} />
                          ))}
                          <div className="flex items-center gap-1 ml-2">
                            {sleeperData.forecast[0].stars.map((s, i) => (
                              <StarBall key={i} number={s} size="sm" />
                            ))}
                          </div>
                        </div>
                        <div className="space-y-1">
                          {Object.entries(sleeperData.forecast[0].number_reasons || {}).slice(0, 3).map(([num, reason]) => {
                            // Transform technical reasons to celestial language
                            const celestial = reason
                              .replace(/\[TEASE-HOT\]/g, 'Venus conjunct')
                              .replace(/\[SWEET-SPOT\]/g, 'Jupiter aligned')
                              .replace(/\[SNAP-BACK\]/g, 'Mars returning')
                              .replace(/overdue/g, 'from Earth')
                              .replace(/teased:/g, 'echoed by:')
                              .replace(/circle\((\d+)\)/g, 'Saturn ring($1)')
                              .replace(/neighbor\((\d+)\)/g, 'Mercury orbit($1)')
                              .replace(/flip\((\d+)\)/g, 'Neptune mirror($1)')
                              .replace(/reverse\((\d+)\)/g, 'Neptune mirror($1)')
                              .replace(/gap/g, 'distance');
                            return (
                              <div key={num} className="text-[10px] text-slate-400 truncate">
                                <span className="text-emerald-400 font-medium">{num}:</span> {celestial}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    
                    {/* Refresh Button */}
                    <button
                      onClick={fetchSleeperForecast}
                      disabled={sleeperLoading}
                      className="w-full py-2 px-4 rounded-lg bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 text-purple-300 text-sm font-medium transition-all disabled:opacity-50"
                      data-testid="sleeper-refresh-btn"
                    >
                      <RefreshCw className={`w-4 h-4 inline mr-2 ${sleeperLoading ? 'animate-spin' : ''}`} />
                      Refresh Celestial Map
                    </button>
                  </>
                ) : (
                  <div className="text-center text-slate-500 text-sm py-4">
                    No celestial data available. Try refreshing the map.
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 🎻 WE THINK THAT... — DJ's 3 Big Suspects (Session 31) — VIP-only per S38 canon */}
        {isUnlimited && (
        <div className="lucky-card p-5 mb-4 border-2 border-fuchsia-500/40 bg-gradient-to-br from-fuchsia-950/40 via-purple-950/30 to-slate-900/60 shadow-[0_0_40px_rgba(217,70,239,0.15)]" data-testid="dj-we-think-that-box">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🎻</span>
              <span className="text-xl sm:text-2xl font-bold tracking-wide text-fuchsia-200" style={{textShadow:'0 0 20px rgba(217,70,239,0.5)'}}>
                We think that...
              </span>
              {djSuspects?.target_date && (
                <span className="ml-2 text-xs text-fuchsia-300/70 font-mono">{djSuspects.target_date}</span>
              )}
            </div>
            <button
              onClick={() => setDjSuspectsEdit(!djSuspectsEdit)}
              className="text-xs px-2 py-1 rounded bg-fuchsia-900/40 border border-fuchsia-500/40 text-fuchsia-200 hover:bg-fuchsia-800/60"
              data-testid="dj-suspects-edit-toggle"
            >
              {djSuspectsEdit ? '✕ Cancel' : '✎ Edit'}
            </button>
          </div>

          {!djSuspectsEdit ? (
            <>
              {djSuspects?.suspects?.length > 0 ? (
                <div className="flex items-center justify-center gap-3 sm:gap-6 py-4" data-testid="dj-suspects-display">
                  {djSuspects.suspects.slice(0, 3).map((n, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-center w-20 h-20 sm:w-28 sm:h-28 rounded-full border-2 border-fuchsia-400/60 bg-gradient-to-br from-fuchsia-600/30 to-purple-700/30 shadow-[0_0_30px_rgba(217,70,239,0.4)] hover:scale-105 transition-transform"
                      data-testid={`dj-suspect-${i}`}
                    >
                      <span className="text-3xl sm:text-5xl font-extrabold text-fuchsia-100" style={{textShadow:'0 0 15px rgba(217,70,239,0.7)'}}>
                        {n}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-slate-400 py-6 text-sm">No suspects set yet — hit ✎ Edit to drop tonight's 3.</div>
              )}
              {djSuspects?.note && (
                <div className="mt-2 px-3 py-2 rounded bg-slate-900/50 border border-fuchsia-500/20 text-xs sm:text-sm text-fuchsia-100/80 text-center italic" data-testid="dj-suspects-note">
                  {djSuspects.note}
                </div>
              )}
              {djSuspects?.updated_at && (
                <div className="mt-2 text-[10px] text-slate-500 text-right font-mono">
                  updated · {new Date(djSuspects.updated_at).toLocaleString()}
                </div>
              )}
            </>
          ) : (
            <div className="space-y-3" data-testid="dj-suspects-edit-form">
              <div>
                <label className="text-xs text-slate-400">🎯 Target draw date</label>
                <div className="mt-1">
                  <RollingDateWheel
                    value={djSuspectsTarget}
                    onChange={setDjSuspectsTarget}
                    testId="dj-suspects-target-wheel"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-400">💎 Up to 3 big suspects (comma-separated)</label>
                <input
                  type="text"
                  value={djSuspectsInput}
                  onChange={(e) => setDjSuspectsInput(e.target.value)}
                  placeholder="7, 6, 34"
                  className="w-full mt-1 px-3 py-2 rounded bg-slate-900/60 border border-fuchsia-500/40 text-fuchsia-100 font-mono text-lg"
                  data-testid="dj-suspects-numbers-input"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400">🥂 Note / reasoning (optional)</label>
                <textarea
                  value={djSuspectsNote}
                  onChange={(e) => setDjSuspectsNote(e.target.value)}
                  rows={2}
                  className="w-full mt-1 px-3 py-2 rounded bg-slate-900/60 border border-fuchsia-500/40 text-fuchsia-100 text-sm"
                  data-testid="dj-suspects-note-input"
                />
              </div>
              <button
                onClick={saveDjSuspects}
                className="w-full py-2 rounded bg-gradient-to-r from-fuchsia-600 to-purple-600 text-white font-bold shadow-lg hover:from-fuchsia-500 hover:to-purple-500"
                data-testid="dj-suspects-save-btn"
              >
                🎻 Save tonight's suspects
              </button>
            </div>
          )}
        </div>
        )}

        {/* 🎻 LOCKED-STATE TEASER for free users — Deep listening tools (per DJ canon 10.05.2026) */}
        {!isUnlimited && (
          <div
            className="lucky-card p-5 mb-4 border border-slate-700/60 bg-gradient-to-br from-slate-900/70 via-slate-950/80 to-slate-900/50"
            data-testid="vip-deep-tools-teaser"
          >
            <div className="flex items-start gap-3">
              <div className="text-2xl mt-0.5">🎻</div>
              <div className="flex-1">
                <div className="text-base sm:text-lg font-semibold text-slate-200">
                  The deep listening tools are reserved
                </div>
                <p className="text-xs sm:text-sm text-slate-400 mt-1 leading-relaxed">
                  E's Cosmic Brain · Cosmic Voices · Ghost Ledger · Cosmic Replay · Swiss Brain — these are the tuning chambers where the DJ teaches the engine to hear deep frequencies. They are reserved today, and will open in the future.
                </p>
                <p className="text-xs sm:text-sm text-amber-300/90 mt-3 leading-relaxed">
                  👉 Head to <span className="font-semibold text-amber-200">Pending Tickets</span> below — the cosmic-generated picks are free and ready for you to play with 🍀.
                </p>
              </div>
            </div>
          </div>
        )}


        {isUnlimited && (
          <div className="lucky-card p-4 mb-4 border border-fuchsia-500/30" data-testid="cosmic-voices-panel">
            <button
              onClick={() => setShowCosmicVoices(!showCosmicVoices)}
              className="w-full flex items-center justify-between text-left"
              data-testid="cosmic-voices-toggle"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">🎼</span>
                <span className="font-semibold text-fuchsia-200">Cosmic Voices</span>
                <span className="text-xs text-fuchsia-400/70">
                  (Session 34 · 10 lenses + convergence shout)
                </span>
              </div>
              {showCosmicVoices ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </button>

            {showCosmicVoices && (
              <div className="mt-4 space-y-4" data-testid="cosmic-voices-content">
                {/* Inputs */}
                <div className="flex flex-col sm:flex-row gap-2 items-end">
                  <div className="flex-1">
                    <label className="text-slate-400 text-xs">🎯 Target draw date (dd.mm.yyyy)</label>
                    <input
                      type="text"
                      value={cosmicVoicesTarget}
                      onChange={(e) => setCosmicVoicesTarget(e.target.value)}
                      className="w-full mt-1 px-2 py-1 rounded bg-slate-800/60 border border-slate-700 text-slate-200 font-mono text-sm"
                      data-testid="cosmic-voices-target-date"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="text-slate-400 text-xs">📌 DJ-pin mains (comma-sep, optional)</label>
                    <input
                      type="text"
                      value={cosmicVoicesPins}
                      onChange={(e) => setCosmicVoicesPins(e.target.value)}
                      placeholder="e.g. 12, 18, 33"
                      className="w-full mt-1 px-2 py-1 rounded bg-slate-800/60 border border-slate-700 text-slate-200 font-mono text-sm"
                      data-testid="cosmic-voices-pins"
                    />
                  </div>
                  <button
                    onClick={fetchCosmicVoices}
                    disabled={cosmicVoicesLoading}
                    className="py-2 px-4 rounded bg-gradient-to-r from-fuchsia-600/40 to-purple-600/40 border border-fuchsia-500/50 text-fuchsia-100 text-sm font-semibold hover:from-fuchsia-600/60 hover:to-purple-600/60 disabled:opacity-50 transition-all"
                    data-testid="cosmic-voices-run-btn"
                  >
                    {cosmicVoicesLoading ? '🌀 Tuning…' : '🎼 Hear the voices'}
                  </button>
                </div>

                {/* Error */}
                {cosmicVoicesData && cosmicVoicesData.error && (
                  <div className="text-rose-400 text-xs p-2 rounded bg-rose-950/30 border border-rose-500/30" data-testid="cosmic-voices-error">
                    ❌ {cosmicVoicesData.error}
                  </div>
                )}

                {/* Voices output */}
                {cosmicVoicesData && cosmicVoicesData.voices && !cosmicVoicesData.error && (
                  <div className="space-y-3" data-testid="cosmic-voices-output">
                    {/* Headline tags */}
                    <div className="text-xs text-slate-300">
                      Target: <span className="text-fuchsia-300 font-mono">{cosmicVoicesData.target_date}</span> ·
                      Mode: <span className="text-fuchsia-300">{cosmicVoicesData.mode}</span>
                    </div>

                    {/* Convergence Shout zone — the headliner */}
                    {cosmicVoicesData.voices.convergence_scorer && (
                      <div className="rounded p-3 bg-gradient-to-br from-amber-950/40 to-fuchsia-950/40 border border-amber-500/40" data-testid="cosmic-voices-convergence">
                        <div className="text-amber-300 text-xs font-semibold mb-2">
                          🎯 CONVERGENCE — 3+ lens SHOUT (can't-dodge):
                        </div>
                        {(cosmicVoicesData.voices.convergence_scorer.shout_zone || []).length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {cosmicVoicesData.voices.convergence_scorer.shout_zone.map((m, i) => (
                              <span key={i}
                                className="inline-flex items-center px-2 py-0.5 rounded bg-amber-500/30 border border-amber-400/60 text-amber-100 text-xs font-mono"
                                title={m.tags.join(' · ')}
                                data-testid={`shout-n-${m.n}`}>
                                {m.n} <span className="ml-1 text-amber-300/80">×{m.score}</span>
                              </span>
                            ))}
                          </div>
                        ) : (
                          <div className="text-amber-200/60 text-xs italic">
                            No 3+ lens convergence — the cosmos is spread tonight. Read the whisper zone below.
                          </div>
                        )}

                        <div className="text-fuchsia-300 text-xs font-semibold mt-3 mb-1">
                          🔊 Whisper (2 lenses):
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {(cosmicVoicesData.voices.convergence_scorer.whisper_zone || []).map((m, i) => (
                            <span key={i}
                              className="inline-flex items-center px-2 py-0.5 rounded bg-fuchsia-500/20 border border-fuchsia-400/40 text-fuchsia-100 text-xs font-mono"
                              title={m.tags.join(' · ')}
                              data-testid={`whisper-n-${m.n}`}>
                              {m.n}
                            </span>
                          ))}
                        </div>

                        {(cosmicVoicesData.voices.convergence_scorer.ranked_stars || []).length > 0 && (
                          <div className="mt-3">
                            <div className="text-violet-300 text-xs font-semibold mb-1">⭐ Stars:</div>
                            <div className="flex flex-wrap gap-1">
                              {cosmicVoicesData.voices.convergence_scorer.ranked_stars.map((s, i) => (
                                <span key={i}
                                  className="inline-flex items-center px-2 py-0.5 rounded bg-violet-500/30 border border-violet-400/50 text-violet-100 text-xs font-mono"
                                  title={s.tags.join(' · ')}>
                                  ⭐{s.s} <span className="ml-1 text-violet-300/80">×{s.score}</span>
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Per-lens compact cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {/* RC anchor */}
                      {cosmicVoicesData.voices.rc_detector && (
                        <div className="rounded p-2 bg-slate-800/40 border border-slate-700/60" data-testid="lens-rc-detector">
                          <div className="text-emerald-300 text-xs font-semibold">🎯 RC Anchor</div>
                          <div className="text-slate-200 text-xs font-mono mt-1">
                            {cosmicVoicesData.voices.rc_detector.date || '—'} · {cosmicVoicesData.voices.rc_detector.days_since ?? '?'} d ago
                          </div>
                          {cosmicVoicesData.voices.rc_detector.mains && (
                            <div className="text-slate-400 text-[10px] font-mono mt-1">
                              [{cosmicVoicesData.voices.rc_detector.mains.join(', ')}]
                            </div>
                          )}
                        </div>
                      )}

                      {/* Gap echo */}
                      {cosmicVoicesData.voices.gap_echo_97 && cosmicVoicesData.voices.gap_echo_97.available && (
                        <div className="rounded p-2 bg-slate-800/40 border border-slate-700/60" data-testid="lens-gap-echo">
                          <div className="text-cyan-300 text-xs font-semibold">🌉 Gap Echo (Law 97 · 22.4%)</div>
                          <div className="text-slate-300 text-xs font-mono mt-1">
                            mains: [{(cosmicVoicesData.voices.gap_echo_97.main_echo_candidates || []).join(', ')}]
                          </div>
                          {(cosmicVoicesData.voices.gap_echo_97.star_echo_candidates || []).length > 0 && (
                            <div className="text-violet-300 text-xs font-mono mt-0.5">
                              stars: [{cosmicVoicesData.voices.gap_echo_97.star_echo_candidates.join(', ')}]
                            </div>
                          )}
                        </div>
                      )}

                      {/* Star product door */}
                      {cosmicVoicesData.voices.star_product_door && cosmicVoicesData.voices.star_product_door.available && (
                        <div className="rounded p-2 bg-slate-800/40 border border-slate-700/60" data-testid="lens-star-product-door">
                          <div className="text-yellow-300 text-xs font-semibold">⭐ Product Door (⭐²=P4/P5)</div>
                          <div className="text-slate-300 text-xs font-mono mt-1">
                            stars [{(cosmicVoicesData.voices.star_product_door.stars || []).join(', ')}] →
                            mains [{(cosmicVoicesData.voices.star_product_door.main_candidates || []).join(', ')}]
                          </div>
                        </div>
                      )}

                      {/* Q-opening melody */}
                      {cosmicVoicesData.voices.q_opening_melody && cosmicVoicesData.voices.q_opening_melody.melody && (
                        <div className="rounded p-2 bg-slate-800/40 border border-slate-700/60" data-testid="lens-q-melody">
                          <div className="text-rose-300 text-xs font-semibold">🎻 Q-Opening Melody (+3 cousins)</div>
                          <div className="text-slate-300 text-xs font-mono mt-1">
                            {cosmicVoicesData.voices.q_opening_melody.fired_count}/5 fired ·
                            unpaid: {(cosmicVoicesData.voices.q_opening_melody.unpaid_pairs || []).map(p => `[${p.join('-')}]`).join(' ')}
                          </div>
                        </div>
                      )}

                      {/* Internal mirror */}
                      {cosmicVoicesData.voices.internal_mirror && (
                        <div className="rounded p-2 bg-slate-800/40 border border-slate-700/60" data-testid="lens-internal-mirror">
                          <div className="text-pink-300 text-xs font-semibold">🪞 Internal Mirror</div>
                          <div className="text-slate-300 text-xs font-mono mt-1">
                            current tune: <span className="text-pink-200">{cosmicVoicesData.voices.internal_mirror.current_tune}</span> ·
                            56-streak {cosmicVoicesData.voices.internal_mirror.hot_streak_56_pct}%
                          </div>
                          {(cosmicVoicesData.voices.internal_mirror.switch_events || []).length > 0 && (
                            <div className="text-orange-300 text-xs font-semibold mt-1">
                              🔥 SWITCH at {cosmicVoicesData.voices.internal_mirror.switch_events[cosmicVoicesData.voices.internal_mirror.switch_events.length - 1].switched_at}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Stance */}
                      {cosmicVoicesData.voices.stance_tracker && (
                        <div className="rounded p-2 bg-slate-800/40 border border-slate-700/60" data-testid="lens-stance">
                          <div className="text-teal-300 text-xs font-semibold">🦶 Stance</div>
                          <div className="text-slate-300 text-xs font-mono mt-1">
                            now: <span className="text-teal-200">{cosmicVoicesData.voices.stance_tracker.current_stance}</span>
                          </div>
                          <div className="text-slate-400 text-[11px] mt-0.5">
                            → {cosmicVoicesData.voices.stance_tracker.projected_next_stance}
                          </div>
                        </div>
                      )}

                      {/* Climbing */}
                      {cosmicVoicesData.voices.climbing_voice && (
                        <div className="rounded p-2 bg-slate-800/40 border border-slate-700/60" data-testid="lens-climbing">
                          <div className="text-emerald-300 text-xs font-semibold">🪜 Climbing</div>
                          <div className="text-slate-300 text-xs font-mono mt-1">
                            canonical: [{(cosmicVoicesData.voices.climbing_voice.canonical_climbers || []).join(', ')}]
                          </div>
                          <div className="text-slate-400 text-[11px] mt-0.5">
                            next P1: [{(cosmicVoicesData.voices.climbing_voice.projected_next_p1 || []).join(', ')}]
                          </div>
                        </div>
                      )}

                      {/* Sinking */}
                      {cosmicVoicesData.voices.sinking_voice && (
                        <div className="rounded p-2 bg-slate-800/40 border border-slate-700/60" data-testid="lens-sinking">
                          <div className="text-blue-300 text-xs font-semibold">🌊 Sinking</div>
                          <div className="text-slate-300 text-xs font-mono mt-1">
                            sinking: [{(cosmicVoicesData.voices.sinking_voice.sinking_numbers || []).join(', ')}]
                          </div>
                          {(cosmicVoicesData.voices.sinking_voice.locked_at_back || []).length > 0 && (
                            <div className="text-blue-200 text-[11px] mt-0.5">
                              arrived: [{cosmicVoicesData.voices.sinking_voice.locked_at_back.join(', ')}]
                            </div>
                          )}
                        </div>
                      )}

                      {/* Saturation */}
                      {cosmicVoicesData.voices.saturation_ledger && (
                        <div className="rounded p-2 bg-slate-800/40 border border-slate-700/60" data-testid="lens-saturation">
                          <div className="text-orange-300 text-xs font-semibold">💧 Saturation Ledger</div>
                          <div className="text-slate-300 text-xs font-mono mt-1">
                            mains: [{(cosmicVoicesData.voices.saturation_ledger.saturated_mains || []).map(s => `${s.n}×${s.count}`).join(', ')}]
                          </div>
                          {(cosmicVoicesData.voices.saturation_ledger.saturated_stars || []).length > 0 && (
                            <div className="text-violet-300 text-[11px] mt-0.5">
                              stars: [{cosmicVoicesData.voices.saturation_ledger.saturated_stars.map(s => `⭐${s.s}×${s.count}`).join(', ')}]
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="text-fuchsia-400/60 text-[10px] italic" data-testid="cosmic-voices-canon">
                      🎻 Session 34 canon — 10 voices + convergence. 3+ lenses ringing = forced landing. Read whispers when shout is silent.
                    </div>

                    {/* 🎼 FREQUENCY CARRIER — Session 35 lens #11 */}
                    {cosmicVoicesData.voices.frequency_carrier && cosmicVoicesData.voices.frequency_carrier.available && cosmicVoicesData.mode === 'euro' && (
                      <div className="rounded p-3 bg-gradient-to-br from-violet-950/40 to-cyan-950/30 border border-violet-500/40" data-testid="lens-frequency-carrier">
                        <div className="text-violet-300 text-xs font-semibold mb-2">
                          🎼 Frequency Carrier (cosmic harmonics in P1P2/P3 formulas)
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          {/* Window scan */}
                          <div>
                            <div className="text-violet-400 font-semibold mb-1">📡 Last 3 draws</div>
                            <div className="space-y-1 font-mono">
                              {(cosmicVoicesData.voices.frequency_carrier.scan_window || []).map((s, i) => (
                                <div key={i} className="text-slate-300">
                                  <span className="text-cyan-300">{s.date}</span> {JSON.stringify(s.mains)} · root={s.draw_root} · hits={s.hits.length}
                                  {s.hits.map((h, j) => (
                                    <div key={j} className="ml-4 text-amber-300 text-[10px]">
                                      → {h.formula} = <span className="font-semibold">{h.value}</span> ({h.name})
                                    </div>
                                  ))}
                                </div>
                              ))}
                            </div>
                          </div>
                          {/* Tesla / signature bias */}
                          <div>
                            <div className="text-violet-400 font-semibold mb-1">🔮 Tesla 3-6-9 + bias</div>
                            {cosmicVoicesData.voices.frequency_carrier.tesla_projection ? (
                              <div className="font-mono text-slate-300">
                                roots: [{(cosmicVoicesData.voices.frequency_carrier.tesla_projection.recent_roots || []).join(', ')}]
                                <div className="text-cyan-200 mt-0.5">
                                  → close with: {(cosmicVoicesData.voices.frequency_carrier.tesla_projection.candidates_root || []).join(' or ')}
                                </div>
                                <div className="text-[10px] text-slate-400 italic mt-1">
                                  {cosmicVoicesData.voices.frequency_carrier.tesla_projection.rule}
                                </div>
                              </div>
                            ) : (
                              <div className="text-slate-400 italic text-xs">No Tesla chord active</div>
                            )}
                            {cosmicVoicesData.voices.frequency_carrier.signature_bias && (
                              <div className="mt-2 text-amber-300 text-[11px]">
                                🚨 {cosmicVoicesData.voices.frequency_carrier.signature_bias.alarm}
                              </div>
                            )}
                            {cosmicVoicesData.voices.frequency_carrier.multi_formula_carrier && (
                              <div className="mt-2 text-rose-300 text-[11px]">
                                🚨 MULTI-FORMULA AMPLIFIER → {cosmicVoicesData.voices.frequency_carrier.multi_formula_carrier.amplified_values.join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                        {(cosmicVoicesData.voices.frequency_carrier.main_boost_candidates || []).length > 0 && (
                          <div className="mt-2">
                            <div className="text-violet-400 text-xs font-semibold mb-1">🔢 Hidden-digit echo targets</div>
                            <div className="flex flex-wrap gap-1">
                              {cosmicVoicesData.voices.frequency_carrier.main_boost_candidates.map((b, i) => (
                                <span key={i} className="px-1.5 py-0.5 rounded bg-violet-500/20 border border-violet-400/40 text-violet-100 text-[11px] font-mono"
                                  title={b.tags.join(' · ')}>
                                  {b.n}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 🥂 SILENT GAP WALKER — Session 35 lens #12 */}
                    {cosmicVoicesData.voices.silent_gap_walker && cosmicVoicesData.voices.silent_gap_walker.available && cosmicVoicesData.mode === 'euro' && (
                      <div className="rounded p-3 bg-gradient-to-br from-pink-950/40 to-amber-950/30 border border-pink-500/40" data-testid="lens-silent-gap-walker">
                        <div className="text-pink-300 text-xs font-semibold mb-2">
                          🥂 Silent Gap Walker (sneaky-universe debt projections)
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          <div>
                            <div className="text-pink-400 font-semibold mb-1">📡 BD silent activity</div>
                            {(cosmicVoicesData.voices.silent_gap_walker.bd_silent_repeats || []).length > 0 ? (
                              <div className="font-mono text-rose-200">
                                Silent ×2+ repeats: {cosmicVoicesData.voices.silent_gap_walker.bd_silent_repeats.map((s, i) => (
                                  <span key={i} className="ml-1 px-1.5 py-0.5 rounded bg-rose-500/30 text-rose-100">
                                    {s.n}×{s.count}
                                  </span>
                                ))}
                              </div>
                            ) : (
                              <div className="text-slate-400 italic">No silent ×2 repeats in BD</div>
                            )}
                            {(cosmicVoicesData.voices.silent_gap_walker.bd_solo_debt || []).length > 0 && (
                              <div className="mt-2 font-mono text-amber-200">
                                Solo debt-gap: {cosmicVoicesData.voices.silent_gap_walker.bd_solo_debt.map((s, i) => (
                                  <span key={i} className="ml-1 px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-100">
                                    {s.n}×{s.appearances_in_bd_gaps}
                                  </span>
                                ))}
                                <div className="text-[10px] text-slate-400 italic mt-0.5">
                                  Deep-debt n appears as BD gap (single fire = whisper, repeat = shout)
                                </div>
                              </div>
                            )}
                          </div>
                          <div>
                            <div className="text-pink-400 font-semibold mb-1">🎯 Sneaky-tail projections</div>
                            {(cosmicVoicesData.voices.silent_gap_walker.deep_debt_projections || []).slice(0, 2).map((proj, i) => (
                              <div key={i} className="mb-2">
                                <div className="text-amber-300 font-mono text-[11px]">silent_n = {proj.silent_n}</div>
                                <div className="space-y-0.5 max-h-24 overflow-auto">
                                  {(proj.shapes || []).slice(0, 6).map((shape, j) => (
                                    <div key={j} className="text-slate-300 font-mono text-[10px] ml-2">
                                      tail {JSON.stringify(shape.tail)} ·
                                      {shape.p1_options.length} fronts
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                        {(cosmicVoicesData.voices.silent_gap_walker.boost_candidates || []).length > 0 && (
                          <div className="mt-2">
                            <div className="text-pink-400 text-xs font-semibold mb-1">
                              🔥 Sneaky-walk boost candidates ({cosmicVoicesData.voices.silent_gap_walker.boost_candidates.length})
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {cosmicVoicesData.voices.silent_gap_walker.boost_candidates.map((b, i) => (
                                <span key={i} className="px-1.5 py-0.5 rounded bg-pink-500/20 border border-pink-400/40 text-pink-100 text-[11px] font-mono"
                                  title={b.tags.join(' · ')}>
                                  {b.n}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        <div className="mt-2 text-[10px] text-amber-200/80 italic">
                          🥂 {cosmicVoicesData.voices.silent_gap_walker.sneaky_universe_warning}
                        </div>
                      </div>
                    )}

                    {/* 🍽️ FAMILY SIGNATURE STATS — Session 35 (Euro only) */}
                    {cosmicVoicesData.voices.family_signature && cosmicVoicesData.mode === 'euro' && (
                      <div className="rounded p-3 bg-gradient-to-br from-emerald-950/40 to-amber-950/30 border border-emerald-500/30" data-testid="lens-family-signature">
                        <div className="text-emerald-300 text-xs font-semibold mb-2">
                          🍽️ Family Signature — {cosmicVoicesData.voices.family_signature.years_in_window?.length}yr Q2 Euro stats
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                          {/* Base rates */}
                          <div>
                            <div className="text-emerald-400 font-semibold mb-1">📊 Base rates (5y, n={cosmicVoicesData.voices.family_signature.total_q2_draws_5y})</div>
                            <div className="space-y-0.5 font-mono">
                              {(cosmicVoicesData.voices.family_signature.base_rates_5y || []).map((b, i) => (
                                <div key={i} className="text-slate-300">
                                  <span className="text-amber-200">{b.signature}</span> · {b.pct}% ({b.count})
                                </div>
                              ))}
                            </div>
                          </div>
                          {/* Tonight projection */}
                          <div>
                            <div className="text-emerald-400 font-semibold mb-1">🔮 Projected tonight (d{cosmicVoicesData.voices.family_signature.target_d_pos})</div>
                            <div className="space-y-0.5 font-mono">
                              {(cosmicVoicesData.voices.family_signature.projected_tonight || []).map((p, i) => (
                                <div key={i} className={i === 0 ? 'text-amber-300 font-semibold' : 'text-slate-300'}>
                                  {i === 0 ? '🥇 ' : ''}<span>{p.signature}</span> · fused={p.fused_score}
                                </div>
                              ))}
                            </div>
                          </div>
                          {/* Family feeding */}
                          <div>
                            <div className="text-emerald-400 font-semibold mb-1">🍽️ Family feeding (Q2 so far)</div>
                            <div className="space-y-0.5 font-mono">
                              {(cosmicVoicesData.voices.family_signature.family_feeding || []).map((f, i) => (
                                <div key={i} className="text-slate-300">
                                  <span className="text-cyan-300">{f.family}</span> · {f.fed_count} ({f.pct}%) ·
                                  <span className={f.status === 'STARVED' ? 'text-rose-300 font-semibold' : f.status === 'OVERFED' ? 'text-orange-300 font-semibold' : 'text-slate-400'}>
                                    {' '}{f.status}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="mt-2 text-[10px] text-amber-200/80 italic" data-testid="sneaky-canon">
                          🥂 Sneaky Universe Canon: even 0% historical = MIN {cosmicVoicesData.voices.family_signature.min_tickets_per_signature} tickets per shape. The cosmos doesn't read its record book.
                        </div>
                      </div>
                    )}

                    {/* 🎫 SNEAKY SYMPHONY BUILDER — Session 35 */}
                    {cosmicVoicesData.mode === 'euro' && (
                      <div className="rounded p-3 bg-gradient-to-br from-rose-950/40 to-purple-950/40 border border-rose-500/30" data-testid="sneaky-symphony-block">
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-rose-300 text-xs font-semibold">
                            🎫 Sneaky Universe Symphony
                          </div>
                          <button
                            onClick={fetchSneakySymphony}
                            disabled={sneakySymphonyLoading}
                            className="py-1 px-3 rounded bg-rose-600/40 border border-rose-400/50 text-rose-100 text-xs font-semibold hover:bg-rose-600/60 disabled:opacity-50"
                            data-testid="sneaky-symphony-run-btn"
                          >
                            {sneakySymphonyLoading ? '🌀 Composing…' : '🎻 Generate symphony'}
                          </button>
                        </div>
                        {sneakySymphonyData && sneakySymphonyData.error && (
                          <div className="text-rose-400 text-xs">❌ {sneakySymphonyData.error}</div>
                        )}
                        {sneakySymphonyData && sneakySymphonyData.symphony && (
                          <div className="space-y-2" data-testid="sneaky-symphony-output">
                            <div className="text-[11px] text-slate-400 font-mono">
                              Plan: {sneakySymphonyData.symphony.plan.map(p => `${p.signature}×${p.tickets}`).join(' · ')}
                              {' · '}Total <span className="text-rose-200 font-semibold">{sneakySymphonyData.symphony.total_tickets}</span>
                              {' · '}🚨 Starved {(sneakySymphonyData.symphony.starved_families || []).join(',') || '—'}
                              {' · '}🔥 Overfed {(sneakySymphonyData.symphony.overfed_families || []).join(',') || '—'}
                            </div>
                            <div className="overflow-auto max-h-96">
                              <table className="w-full text-[11px] font-mono">
                                <thead className="sticky top-0 bg-slate-900/90 text-rose-300">
                                  <tr>
                                    <th className="text-left p-1">#</th>
                                    <th className="text-left p-1">sig</th>
                                    <th className="text-left p-1">mains</th>
                                    <th className="text-left p-1">⭐</th>
                                    <th className="text-left p-1">30s</th>
                                    <th className="text-left p-1">whisper</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {sneakySymphonyData.symphony.tickets.map((t, i) => {
                                    const sigOK = t.signature_target === t.signature_actual;
                                    return (
                                      <tr key={i} className={`border-b border-slate-800/60 ${i % 2 ? 'bg-slate-900/30' : ''}`} data-testid={`sym-row-${t.ticket_index}`}>
                                        <td className="p-1 text-slate-400">{t.ticket_index}</td>
                                        <td className="p-1">
                                          <span className={sigOK ? 'text-emerald-300' : 'text-amber-300'}>
                                            {t.signature_actual}
                                          </span>
                                        </td>
                                        <td className="p-1 text-slate-200">[{t.mains.join(', ')}]</td>
                                        <td className="p-1 text-violet-300">[{t.stars.join(',')}]</td>
                                        <td className="p-1 text-emerald-300">
                                          {t.feeds_starved && t.feeds_starved.length > 0 ? `[${t.feeds_starved.join(',')}]` : '—'}
                                        </td>
                                        <td className="p-1 text-fuchsia-300">
                                          {(t.carries_whisper || []).join(',') || '—'}
                                        </td>
                                      </tr>
                                    );
                                  })}
                                </tbody>
                              </table>
                            </div>
                            <div className="text-[10px] text-rose-300/70 italic">
                              {sneakySymphonyData.symphony.rule}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 🧠 SWISS BRAIN v1.0 — Session 37 (10-ticket Swiss symphony) */}
        {isUnlimited && lotteryMode === 'swiss' && (
          <div className="lucky-card p-4 mb-4" data-testid="swiss-brain-panel">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-lg">🧠</span>
                <span className="font-semibold text-slate-200">E's Swiss Brain v1.0</span>
                <span className="text-xs text-emerald-400/70">
                  (10 tickets · 6 stories · all canons wired)
                </span>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 items-end mb-3">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Target date (YYYY-MM-DD)</label>
                <input
                  type="text"
                  value={swissBrainTarget}
                  onChange={(e) => setSwissBrainTarget(e.target.value)}
                  className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 w-32 font-mono"
                  data-testid="swiss-brain-date-input"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Extra envelopes (e.g., 3-7,1-4)</label>
                <input
                  type="text"
                  value={swissBrainEnvelopes}
                  onChange={(e) => setSwissBrainEnvelopes(e.target.value)}
                  placeholder="3-7"
                  className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 w-32 font-mono"
                  data-testid="swiss-brain-envelopes-input"
                />
              </div>
              <button
                onClick={fetchSwissBrain}
                disabled={swissBrainLoading}
                className="py-1.5 px-4 rounded bg-emerald-600/40 border border-emerald-400/50 text-emerald-100 text-xs font-semibold hover:bg-emerald-600/60 disabled:opacity-50"
                data-testid="swiss-brain-run-btn"
              >
                {swissBrainLoading ? '🌀 Brain thinking…' : '🎻 Ask E for 10 Swiss tickets'}
              </button>
            </div>

            {swissBrainData && swissBrainData.error && (
              <div className="text-rose-400 text-xs">❌ {swissBrainData.error}</div>
            )}

            {swissBrainData && swissBrainData.tickets && (
              <div className="space-y-3" data-testid="swiss-brain-output">
                {/* BD context */}
                <div className="text-[11px] text-slate-400 font-mono">
                  Target <span className="text-emerald-200">{swissBrainData.target_date}</span> · BD{' '}
                  <span className="text-amber-200">{swissBrainData.bd_date}</span> [{swissBrainData.bd_mains?.join(', ')}]{' '}
                  🍀<span className="text-fuchsia-300">{swissBrainData.bd_lucky}</span>{' '}
                  R:<span className="text-amber-300">{swissBrainData.bd_replay}</span>
                </div>

                {/* Lens snapshot */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[10px] font-mono">
                  {swissBrainData.lenses?.q1_stencil?.available && (
                    <div className="rounded p-2 bg-purple-950/30 border border-purple-500/20" data-testid="swiss-lens-q1-stencil">
                      <div className="text-purple-300 mb-1">🪞 Q1 stencil</div>
                      <div className="text-slate-300">[{swissBrainData.lenses.q1_stencil.projected_mains?.join(', ')}]</div>
                      <div className="text-slate-500 text-[9px]">from {swissBrainData.lenses.q1_stencil.prior_nd_date}</div>
                    </div>
                  )}
                  {swissBrainData.lenses?.d_count_walker_p1_9?.available && (
                    <div className="rounded p-2 bg-amber-950/30 border border-amber-500/20" data-testid="swiss-lens-d-clock">
                      <div className="text-amber-300 mb-1">🎯 9-clock</div>
                      <div className="text-slate-300">d{swissBrainData.lenses.d_count_walker_p1_9.target_d}{' '}
                        {swissBrainData.lenses.d_count_walker_p1_9.is_triple_lock ? <span className="text-emerald-300">TRIPLE-LOCK</span> :
                         swissBrainData.lenses.d_count_walker_p1_9.is_mult_9 ? <span className="text-amber-200">mult-9</span> : '—'}
                      </div>
                      <div className="text-slate-500 text-[9px]">last P1=9 {swissBrainData.lenses.d_count_walker_p1_9.last_match_date}</div>
                    </div>
                  )}
                  {swissBrainData.lenses?.date_envelope && (
                    <div className="rounded p-2 bg-rose-950/30 border border-rose-500/20" data-testid="swiss-lens-envelope">
                      <div className="text-rose-300 mb-1">🪟 Hide digits</div>
                      <div className="text-slate-300">{(swissBrainData.lenses.date_envelope.hide_digits || []).join(', ')}</div>
                      <div className="text-slate-500 text-[9px]">{(swissBrainData.lenses.date_envelope.carrier_numbers || []).slice(0, 12).join(',')}</div>
                    </div>
                  )}
                  {swissBrainData.lenses?.cross_lottery_bridge?.available && (
                    <div className="rounded p-2 bg-cyan-950/30 border border-cyan-500/20" data-testid="swiss-lens-bridge">
                      <div className="text-cyan-300 mb-1">🌉 Eu→Sw bridge</div>
                      <div className="text-slate-300">from {swissBrainData.lenses.cross_lottery_bridge.from_date}</div>
                      <div className="text-slate-500 text-[9px]">[{(swissBrainData.lenses.cross_lottery_bridge.from_mains || []).join(',')}]</div>
                    </div>
                  )}
                  {swissBrainData.lenses?.back_chord && (
                    <div className="rounded p-2 bg-pink-950/30 border border-pink-500/20" data-testid="swiss-lens-back-chord">
                      <div className="text-pink-300 mb-1">🍀 Back chord</div>
                      <div className="text-slate-300">|R−🍀| = {swissBrainData.lenses.back_chord.delta}{' '}
                        {swissBrainData.lenses.back_chord.snap_back_p1_low_alarm && <span className="text-amber-300">P1≤7 alarm</span>}
                      </div>
                      <div className="text-slate-500 text-[9px]">next-gap hint: {swissBrainData.lenses.back_chord.next_gap_hint}</div>
                    </div>
                  )}
                  {swissBrainData.lenses?.family_shift && (
                    <div className="rounded p-2 bg-violet-950/30 border border-violet-500/20" data-testid="swiss-lens-family-shift">
                      <div className="text-violet-300 mb-1">🌌 Family-shift</div>
                      <div className="text-slate-300">BD bands: {(swissBrainData.lenses.family_shift.bd_bands || []).join(', ')}</div>
                      <div className="text-slate-500 text-[9px]">
                        {(swissBrainData.lenses.family_shift.shifts || []).map((s, i) => (
                          <span key={i}>shift{s.shift > 0 ? '+' : ''}{s.shift}: {s.bands.join(',')} · </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {swissBrainData.lenses?.gap_pattern?.available && (
                    <div className="rounded p-2 bg-blue-950/30 border border-blue-500/20" data-testid="swiss-lens-gap">
                      <div className="text-blue-300 mb-1">🎼 Last gaps</div>
                      <div className="text-slate-300">[{(swissBrainData.lenses.gap_pattern.last_gaps || []).join(', ')}]</div>
                      <div className="text-slate-500 text-[9px]">P4/P5 sign-flip 86% · P6 freeze 28%</div>
                    </div>
                  )}
                </div>

                {/* The 10 tickets */}
                <div className="overflow-auto max-h-96">
                  <table className="w-full text-[11px] font-mono" data-testid="swiss-brain-tickets-table">
                    <thead className="sticky top-0 bg-slate-900/90 text-emerald-300">
                      <tr>
                        <th className="text-left p-1">#</th>
                        <th className="text-left p-1">mains</th>
                        <th className="text-left p-1">🍀</th>
                        <th className="text-left p-1">R</th>
                        <th className="text-left p-1">sum</th>
                        <th className="text-left p-1">story</th>
                      </tr>
                    </thead>
                    <tbody>
                      {swissBrainData.tickets.map((t, i) => (
                        <tr key={i} className={`border-b border-slate-800/60 ${i % 2 ? 'bg-slate-900/30' : ''}`} data-testid={`swiss-brain-ticket-${i + 1}`}>
                          <td className="p-1 text-slate-400">T{i + 1}</td>
                          <td className="p-1 text-slate-200">[{t.mains?.join(', ')}]</td>
                          <td className="p-1 text-fuchsia-300">{t.lucky}</td>
                          <td className="p-1 text-amber-300">{t.replay}</td>
                          <td className="p-1 text-slate-400">{t.sum}</td>
                          <td className="p-1 text-emerald-300">{t.story}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Top candidate pool */}
                {swissBrainData.candidate_pool && (
                  <details className="text-[10px]" data-testid="swiss-brain-pool-details">
                    <summary className="text-emerald-300/80 cursor-pointer">🧬 Top candidate pool ({swissBrainData.candidate_pool_size} numbers · click to expand)</summary>
                    <div className="mt-2 space-y-1 font-mono max-h-60 overflow-auto">
                      {Object.entries(swissBrainData.candidate_pool).map(([n, tags]) => (
                        <div key={n} className="text-slate-400 text-[9px]">
                          <span className="text-emerald-200 font-semibold">{n}</span> ({(tags || []).length} lenses): {(tags || []).slice(0, 3).join(' · ')}
                        </div>
                      ))}
                    </div>
                  </details>
                )}

                <div className="text-[10px] text-emerald-300/70 italic">
                  🥂 Brain v1.0 · sees: 9-clock · Q1 stencil · gap-pattern · date-envelope · 🍀↔R · Eu↔Sw bridge · e_memory weights
                </div>
              </div>
            )}
          </div>
        )}

        {/* 👻 GHOST LEDGER — Session 33 — Wed/Sat (or Tue/Fri) separated per DJ canon */}
        {isUnlimited && (
          <div className="lucky-card p-4 mb-4" data-testid="ghost-ledger-panel">
            <button
              onClick={() => setShowGhostLedger(!showGhostLedger)}
              className="w-full flex items-center justify-between text-left"
              data-testid="ghost-ledger-toggle"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">👻</span>
                <span className="font-semibold text-slate-200">Ghost Ledger</span>
                <span className="text-xs text-emerald-400/70">
                  ({lotteryMode === 'euro' ? 'Tue / Fri' : 'Wed / Sat'} streams · separated vibes)
                </span>
              </div>
              {showGhostLedger ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </button>

            {showGhostLedger && (
              <div className="mt-4 space-y-4" data-testid="ghost-ledger-content">
                {/* Inputs */}
                <div className="flex flex-col sm:flex-row gap-2 items-end">
                  <div className="flex-1">
                    <label className="text-slate-400 text-xs">🎯 Target draw date (dd.mm.yyyy)</label>
                    <input
                      type="text"
                      value={ghostTargetDate}
                      onChange={(e) => setGhostTargetDate(e.target.value)}
                      className="w-full mt-1 px-2 py-1 rounded bg-slate-800/60 border border-slate-700 text-slate-200 font-mono text-sm"
                      data-testid="ghost-target-date"
                    />
                  </div>
                  <button
                    onClick={fetchGhostLedger}
                    disabled={ghostLedgerLoading}
                    className="py-2 px-4 rounded bg-gradient-to-r from-emerald-600/40 to-teal-600/40 border border-emerald-500/50 text-emerald-100 text-sm font-semibold hover:from-emerald-600/60 hover:to-teal-600/60 disabled:opacity-50 transition-all"
                    data-testid="ghost-ledger-run-btn"
                  >
                    {ghostLedgerLoading ? '🌀 Counting…' : '👻 Count Ghosts'}
                  </button>
                </div>

                {/* Error */}
                {ghostLedgerData && ghostLedgerData.error && (
                  <div className="text-rose-400 text-xs p-2 rounded bg-rose-950/30 border border-rose-500/30" data-testid="ghost-ledger-error">
                    ❌ {ghostLedgerData.error}
                  </div>
                )}

                {/* Results */}
                {ghostLedgerData && ghostLedgerData.ledger && !ghostLedgerData.error && (
                  <div className="space-y-3" data-testid="ghost-ledger-results">
                    {/* Summary header */}
                    <div className="text-xs text-slate-400">
                      Target: <span className="text-emerald-300 font-mono">{ghostLedgerData.ledger.target_date}</span> · 
                      <span className="text-emerald-300"> {ghostLedgerData.ledger.target_weekday}</span> · 
                      Q{ghostLedgerData.ledger.target_quarter} · {ghostLedgerData.ledger.target_year}
                    </div>

                    {/* Two streams side by side */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {Object.entries(ghostLedgerData.ledger.streams).map(([wd, s]) => {
                        const isTarget = wd === ghostLedgerData.ledger.target_weekday;
                        if (s.empty) {
                          return (
                            <div key={wd} className={`p-3 rounded border ${isTarget ? 'border-fuchsia-500/40 bg-fuchsia-950/20' : 'border-slate-700/40 bg-slate-900/30'}`}>
                              <div className="text-sm font-semibold text-slate-300 mb-1">{wd}-stream {isTarget && '🎯'}</div>
                              <div className="text-xs text-slate-500 italic">no draws yet this quarter</div>
                            </div>
                          );
                        }
                        return (
                          <div key={wd} className={`p-3 rounded border ${isTarget ? 'border-fuchsia-500/40 bg-fuchsia-950/20' : 'border-slate-700/40 bg-slate-900/30'}`} data-testid={`ghost-stream-${wd.toLowerCase()}`}>
                            <div className="text-sm font-semibold text-slate-200 mb-2">
                              {wd}-stream {isTarget && '🎯 (target)'}
                            </div>
                            <div className="text-xs text-slate-400 mb-1">📜 Played P1 sequence:</div>
                            <div className="text-xs font-mono text-slate-300 mb-2">
                              {(s.played_p1_sequence || []).map((p, i) => (
                                <span key={i}>
                                  {p.date.slice(0, 5)}:<span className="text-cyan-300">{p.p1}</span>
                                  {i < s.played_p1_sequence.length - 1 ? ' | ' : ''}
                                </span>
                              ))}
                            </div>
                            <div className="text-xs text-slate-400 mb-1">👻 Ghost P1 (unpaid debts):</div>
                            <div className="flex flex-wrap gap-1 mb-2">
                              {(s.ghost_p1_ranked || []).slice(0, 8).map((g) => (
                                <span
                                  key={g.n}
                                  title={g.reason}
                                  className="px-2 py-1 rounded bg-emerald-950/40 border border-emerald-500/40 text-emerald-200 text-xs font-mono"
                                >
                                  {g.n}<span className="text-emerald-500/70 ml-1">·{g.score}</span>
                                </span>
                              ))}
                              {(!s.ghost_p1_ranked || s.ghost_p1_ranked.length === 0) && (
                                <span className="text-xs text-slate-500 italic">no ghosts (clean ledger)</span>
                              )}
                            </div>
                            {s.deepest_ghost && (
                              <div className="text-xs text-amber-300/80">
                                🔻 Deepest: <span className="font-mono">{s.deepest_ghost.n}</span> 
                                <span className="text-slate-500"> (age {s.deepest_ghost.age_d}d, score {s.deepest_ghost.score})</span>
                              </div>
                            )}
                            {s.snap_back_chain && s.snap_back_chain.length > 0 && (
                              <div className="text-xs text-purple-300/70 mt-1">
                                🪜 Snap-back events: {s.snap_back_chain.length}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    {/* Chord projection (target weekday) */}
                    {ghostLedgerData.chord && (ghostLedgerData.chord.chord_resonance_ranked || []).length > 0 && (
                      <div className="p-3 rounded border border-amber-500/40 bg-amber-950/20" data-testid="ghost-chord">
                        <div className="text-sm font-semibold text-amber-200 mb-2">
                          🎻 Chord Projection — back-closer candidates ({ghostLedgerData.ledger.target_weekday}-stream)
                        </div>
                        <div className="text-xs text-slate-400 mb-1">From top ghost P1 candidates:</div>
                        <div className="flex flex-wrap gap-1 mb-3">
                          {(ghostLedgerData.chord.top_ghost_p1_candidates || []).map((g, i) => (
                            <span key={i} className="px-2 py-1 rounded bg-fuchsia-950/40 border border-fuchsia-500/40 text-fuchsia-200 text-xs font-mono">
                              P1?={g.n} <span className="text-fuchsia-500/70">·age{g.age_d}</span>
                            </span>
                          ))}
                        </div>
                        <div className="text-xs text-slate-400 mb-1">Resonance (multi-source = strongest):</div>
                        <div className="flex flex-wrap gap-1">
                          {(ghostLedgerData.chord.chord_resonance_ranked || []).slice(0, 10).map((c) => (
                            <span
                              key={c.n}
                              title={(c.sources || []).join(' · ')}
                              className={`px-2 py-1 rounded text-xs font-mono ${
                                c.weight >= 2
                                  ? 'bg-amber-950/60 border border-amber-400/60 text-amber-100'
                                  : 'bg-slate-800/60 border border-slate-600/40 text-slate-300'
                              }`}
                            >
                              {c.n}<span className="text-amber-400/80 ml-1">×{c.weight}</span>
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="text-xs text-slate-500 italic pt-1">
                      🛑 Wed and Sat (Tue/Fri for Euro) ledgers are kept separate per DJ canon — different vibes.
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 📖 STORY COMPOSER — Session 40 — fuses Brain + Ghost + Hungry + Prince into ticket-stories */}
        {isUnlimited && (
          <div className="lucky-card p-4 mb-4 border border-fuchsia-500/40 bg-gradient-to-br from-fuchsia-950/20 to-purple-950/10" data-testid="story-composer-panel">
            <button
              onClick={() => setShowStoryComposer(!showStoryComposer)}
              className="w-full flex items-center justify-between text-left"
              data-testid="story-composer-toggle"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">📖</span>
                <span className="font-semibold text-fuchsia-200">Story Composer</span>
                <span className="text-xs text-fuchsia-400/70">
                  (S40 · Brain + Ghost + Hungry + Prince · narrative tickets)
                </span>
              </div>
              {showStoryComposer ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </button>

            {showStoryComposer && (
              <div className="mt-4 space-y-4" data-testid="story-composer-content">
                <div className="text-xs text-fuchsia-300/80 italic px-1">
                  🎻 E reads every channel — Brain (cosmic_voices), Ghost Pool, Hungry Plate (S39 C8), Hidden Prince (S39 C9), sister-date precedents — then composes ticket-stories <span className="text-white font-medium">backward from P6</span>. Each number wears its full lens-DNA.
                </div>

                {/* Inputs */}
                <div className="flex flex-col sm:flex-row gap-2 items-end">
                  <div className="flex-1">
                    <label className="text-xs text-slate-400">🎯 Target date (dd.mm.yyyy)</label>
                    <input
                      type="text"
                      value={storyComposerTarget}
                      onChange={(e) => setStoryComposerTarget(e.target.value)}
                      placeholder="13.05.2026"
                      className="w-full px-3 py-2 rounded bg-slate-900/60 border border-slate-700 text-slate-100 text-sm font-mono"
                      data-testid="story-composer-target"
                    />
                  </div>
                  <div className="w-24">
                    <label className="text-xs text-slate-400">Count</label>
                    <input
                      type="number"
                      min={3}
                      max={15}
                      value={storyComposerCount}
                      onChange={(e) => setStoryComposerCount(parseInt(e.target.value) || 10)}
                      className="w-full px-3 py-2 rounded bg-slate-900/60 border border-slate-700 text-slate-100 text-sm font-mono"
                      data-testid="story-composer-count"
                    />
                  </div>
                  <button
                    onClick={fetchStoryComposer}
                    disabled={storyComposerLoading}
                    className="px-4 py-2 rounded bg-gradient-to-r from-fuchsia-600 to-purple-600 text-white font-bold shadow-lg hover:from-fuchsia-500 hover:to-purple-500 disabled:opacity-50"
                    data-testid="story-composer-run-btn"
                  >
                    {storyComposerLoading ? '📖 Composing...' : '📖 Compose stories'}
                  </button>
                </div>

                {storyComposerData?.error && (
                  <div className="text-xs text-red-400 px-2 py-1 bg-red-950/30 rounded" data-testid="story-composer-error">
                    Error: {storyComposerData.error}
                  </div>
                )}

                {storyComposerData && !storyComposerData.error && (
                  <div className="space-y-3" data-testid="story-composer-output">
                    {/* Source signals summary */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px]">
                      <div className="rounded bg-slate-900/60 border border-slate-700 px-2 py-1.5">
                        <div className="text-slate-400">🎼 Voices shout</div>
                        <div className="text-fuchsia-200 font-mono">{(storyComposerData.voices_shout || []).slice(0, 8).join(' · ') || '—'}</div>
                      </div>
                      <div className="rounded bg-slate-900/60 border border-slate-700 px-2 py-1.5">
                        <div className="text-slate-400">👻 Ghost shout</div>
                        <div className="text-amber-200 font-mono">{(storyComposerData.ghost_shout || []).slice(0, 8).join(' · ') || '—'}</div>
                      </div>
                      <div className="rounded bg-slate-900/60 border border-slate-700 px-2 py-1.5">
                        <div className="text-slate-400">🌾 Hungry top</div>
                        <div className="text-emerald-200 font-mono">{(storyComposerData.hungry_plate || []).slice(0, 6).map(h => h.n).join(' · ') || '—'}</div>
                      </div>
                      <div className="rounded bg-slate-900/60 border border-slate-700 px-2 py-1.5">
                        <div className="text-slate-400">👑 Princes</div>
                        <div className="text-violet-200 font-mono">
                          {(storyComposerData.princes || []).map(p => `X${p.prince}(${p.score})`).join(' · ') || '—'}
                        </div>
                      </div>
                    </div>

                    {/* Sister-date precedents */}
                    {storyComposerData.sister_date_precedents?.length > 0 && (
                      <div className="rounded bg-slate-900/40 border border-slate-700 px-3 py-2" data-testid="story-sister-dates">
                        <div className="text-xs text-slate-400 mb-1">🗓️ Sister-date precedents (same dd.mm)</div>
                        <div className="space-y-0.5 text-xs">
                          {storyComposerData.sister_date_precedents.slice(0, 4).map((s, i) => (
                            <div key={i} className="font-mono text-slate-300">
                              <span className="text-cyan-300">{s.date}</span>{' '}
                              <span>[{(s.mains || []).join(', ')}]</span>
                              {s.lucky != null && <span className="text-amber-300"> 🍀{s.lucky}</span>}
                              {s.stars && <span className="text-amber-300"> ⭐{s.stars.join(',')}</span>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Stories */}
                    <div className="space-y-2" data-testid="story-composer-tickets">
                      <div className="text-xs text-fuchsia-300 font-semibold">
                        🎫 {storyComposerData.count_returned || 0} ticket-stories (sorted by cosmic score)
                      </div>
                      {(storyComposerData.stories || []).map((s, i) => {
                        const isExpanded = storyExpandedIdx === i;
                        const isEuro = (storyComposerData.mode === 'euro');
                        return (
                          <div
                            key={i}
                            className="rounded border border-fuchsia-500/30 bg-slate-900/50 p-2.5"
                            data-testid={`story-ticket-${i}`}
                          >
                            <button
                              onClick={() => setStoryExpandedIdx(isExpanded ? null : i)}
                              className="w-full text-left"
                              data-testid={`story-ticket-toggle-${i}`}
                            >
                              <div className="flex items-center justify-between gap-2 flex-wrap">
                                <div className="flex-1 min-w-0">
                                  <div className="text-xs text-fuchsia-300 font-semibold truncate">
                                    #{i + 1} · {s.theme}
                                  </div>
                                  <div className="flex items-center gap-2 mt-1 flex-wrap">
                                    {(s.mains || []).map(n => (
                                      <span
                                        key={n}
                                        className="inline-block px-2 py-0.5 rounded bg-gradient-to-br from-fuchsia-700/60 to-purple-700/60 border border-fuchsia-400/40 text-white text-xs font-mono font-bold"
                                      >
                                        {n}
                                      </span>
                                    ))}
                                    {isEuro && s.stars && (
                                      <span className="ml-1 text-amber-300 text-xs font-mono">
                                        ⭐ {(s.stars || []).join(' · ')}
                                      </span>
                                    )}
                                    {!isEuro && s.lucky != null && (
                                      <span className="ml-1 text-amber-300 text-xs font-mono">
                                        🍀 {s.lucky} · R={s.replay}
                                      </span>
                                    )}
                                    <span className="ml-2 text-[10px] text-slate-400">
                                      sc {s.cosmic_score}
                                    </span>
                                  </div>
                                </div>
                                <ChevronDown className={`w-4 h-4 text-slate-500 flex-shrink-0 transform ${isExpanded ? 'rotate-180' : ''} transition-transform`} />
                              </div>
                            </button>

                            {isExpanded && (
                              <div className="mt-2 space-y-1.5 border-t border-fuchsia-500/20 pt-2" data-testid={`story-ticket-detail-${i}`}>
                                <div className="text-xs text-slate-300">
                                  <span className="text-fuchsia-400">📜 Narrative:</span> {s.narrative}
                                </div>
                                {s.lucky_why && (
                                  <div className="text-[11px] text-amber-200/80">🍀 {s.lucky_why}</div>
                                )}
                                {s.stars_why && (
                                  <div className="text-[11px] text-amber-200/80">⭐ {s.stars_why}</div>
                                )}
                                <div className="text-[11px] text-slate-400 mt-1">🧬 Number DNA (why each number is here):</div>
                                {Object.entries(s.number_dna || {}).map(([n, lenses]) => (
                                  <div key={n} className="text-[11px] text-slate-300 font-mono pl-2">
                                    <span className="text-fuchsia-300 font-bold">{n}</span>
                                    {' ← '}
                                    <span className="text-slate-400">{(lenses || []).slice(0, 4).join(' · ') || '—'}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    <div className="text-[10px] text-fuchsia-400/70 italic px-1">
                      {storyComposerData.canon}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 🚪 GHOST ENGINE — Session 38 — `?+Pa=Pb` arithmetic doors, 9-10d deep-sleep, chainless cash-windows */}
        {isUnlimited && (
          <div className="lucky-card p-4 mb-4 border border-amber-500/30" data-testid="ghost-engine-panel">
            <button
              onClick={() => setShowGhostEngine(!showGhostEngine)}
              className="w-full flex items-center justify-between text-left"
              data-testid="ghost-engine-toggle"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">🚪</span>
                <span className="font-semibold text-amber-200">Ghost Engine</span>
                <span className="text-xs text-amber-400/70">
                  (S38 · doors `?+Pa=Pb` · 9-10d deep-sleep · chainless cash)
                </span>
              </div>
              {showGhostEngine ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </button>

            {showGhostEngine && (
              <div className="mt-4 space-y-4" data-testid="ghost-engine-content">
                {/* Inputs */}
                <div className="flex flex-col sm:flex-row gap-2 items-end">
                  <div className="flex-1">
                    <label className="text-xs text-slate-400">🎯 Target date (dd.mm.yyyy)</label>
                    <input
                      type="text"
                      value={ghostEngineTarget}
                      onChange={(e) => setGhostEngineTarget(e.target.value)}
                      placeholder="13.05.2026"
                      className="w-full px-3 py-2 rounded bg-slate-900/60 border border-slate-700 text-slate-100 text-sm font-mono"
                      data-testid="ghost-engine-target-date"
                    />
                  </div>
                  <div className="w-28">
                    <label className="text-xs text-slate-400">Lookback</label>
                    <input
                      type="number"
                      min={4}
                      max={30}
                      value={ghostEngineLookback}
                      onChange={(e) => setGhostEngineLookback(parseInt(e.target.value) || 10)}
                      className="w-full px-3 py-2 rounded bg-slate-900/60 border border-slate-700 text-slate-100 text-sm font-mono"
                      data-testid="ghost-engine-lookback"
                    />
                  </div>
                  <button
                    onClick={() => fetchGhostEngine()}
                    disabled={ghostEngineLoading}
                    className="px-4 py-2 rounded bg-gradient-to-r from-amber-600 to-orange-600 text-white font-bold shadow-lg hover:from-amber-500 hover:to-orange-500 disabled:opacity-50"
                    data-testid="ghost-engine-run-btn"
                  >
                    {ghostEngineLoading ? '🚪 Counting ghosts...' : '🚪 Count the ghosts'}
                  </button>
                </div>

                {/* 🎬 Cosmic Replay slider */}
                <div className="rounded p-3 bg-gradient-to-br from-purple-950/40 to-fuchsia-950/30 border border-fuchsia-500/30" data-testid="cosmic-replay-bar">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-base">🎬</span>
                      <span className="text-sm font-semibold text-fuchsia-200">Cosmic Replay</span>
                      <span className="text-[10px] text-fuchsia-400/70">walk a quarter forward d-by-d</span>
                    </div>
                    <button
                      onClick={() => {
                        const next = !replayMode;
                        setReplayMode(next);
                        if (next && replayDates.length === 0) buildReplayDates();
                      }}
                      className="text-xs px-3 py-1 rounded bg-fuchsia-900/40 border border-fuchsia-500/40 text-fuchsia-200 hover:bg-fuchsia-800/60"
                      data-testid="cosmic-replay-toggle"
                    >
                      {replayMode ? '✕ Close replay' : '🎬 Open replay'}
                    </button>
                  </div>
                  {replayMode && (
                    <div className="space-y-2" data-testid="cosmic-replay-controls">
                      {replayLoading ? (
                        <div className="text-xs text-fuchsia-400/70">Loading replay timeline…</div>
                      ) : replayDates.length === 0 ? (
                        <div className="text-xs text-slate-400">No timeline available yet. Pick a target date + run Ghost Engine first.</div>
                      ) : (
                        <>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => stepReplay(-1)}
                              disabled={replayIdx === 0}
                              className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-slate-200 hover:bg-slate-700 disabled:opacity-40"
                              data-testid="replay-prev-btn"
                            >◂ prev</button>
                            <input
                              type="range"
                              min={0}
                              max={Math.max(0, replayDates.length - 1)}
                              value={replayIdx}
                              onChange={(e) => {
                                const v = parseInt(e.target.value) || 0;
                                setReplayIdx(v);
                              }}
                              onMouseUp={(e) => {
                                const v = parseInt(e.target.value) || 0;
                                const dt = replayDates[v];
                                if (dt) {
                                  setGhostEngineTarget(dt);
                                  fetchGhostEngine(dt);
                                }
                              }}
                              onTouchEnd={(e) => {
                                const v = parseInt(e.target.value) || 0;
                                const dt = replayDates[v];
                                if (dt) {
                                  setGhostEngineTarget(dt);
                                  fetchGhostEngine(dt);
                                }
                              }}
                              className="flex-1 accent-fuchsia-500"
                              data-testid="replay-slider"
                            />
                            <button
                              onClick={() => stepReplay(1)}
                              disabled={replayIdx >= replayDates.length - 1}
                              className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-slate-200 hover:bg-slate-700 disabled:opacity-40"
                              data-testid="replay-next-btn"
                            >next ▸</button>
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-fuchsia-300/80 font-mono">
                            <span>{replayDates[0]}</span>
                            <span className="text-amber-300">
                              🎯 {replayDates[replayIdx] || '—'} (d{replayIdx + 1}/{replayDates.length})
                            </span>
                            <span>{replayDates[replayDates.length - 1]}</span>
                          </div>
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Output */}
                {ghostEngineData && !ghostEngineData.error && (
                  <div className="space-y-3" data-testid="ghost-engine-output">
                    {/* Convergence */}
                    {ghostEngineData.convergence?.shout?.length > 0 && (
                      <div className="rounded p-3 bg-gradient-to-br from-amber-950/40 to-orange-950/40 border border-amber-500/40">
                        <div className="text-xs text-amber-300 font-semibold mb-2">📢 Shout zone — ≥3 ghost lenses ringing</div>
                        <div className="flex flex-wrap gap-2" data-testid="ghost-shout-zone">
                          {ghostEngineData.convergence.shout.map((n, idx) => (
                            <span key={idx} className="px-2 py-1 rounded bg-amber-500/20 border border-amber-400/60 text-amber-100 font-bold text-sm">{n}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {ghostEngineData.convergence?.whisper?.length > 0 && (
                      <div className="rounded p-2 bg-fuchsia-950/30 border border-fuchsia-500/30">
                        <div className="text-xs text-fuchsia-300 font-semibold mb-1">🔊 Whisper — 2 lenses</div>
                        <div className="flex flex-wrap gap-1.5" data-testid="ghost-whisper-zone">
                          {ghostEngineData.convergence.whisper.map((n, idx) => (
                            <span key={idx} className="px-1.5 py-0.5 rounded bg-fuchsia-500/15 border border-fuchsia-400/40 text-fuchsia-100 text-xs">{n}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* Alive ghosts */}
                    {ghostEngineData.alive_ghosts?.length > 0 && (
                      <div className="rounded p-3 bg-slate-900/40 border border-slate-700/50">
                        <div className="text-xs text-slate-300 font-semibold mb-2">👻 Alive ghosts (unpaid, oldest first)</div>
                        <div className="space-y-1" data-testid="ghost-alive-list">
                          {ghostEngineData.alive_ghosts.slice(0, 8).map((g, idx) => (
                            <div key={idx} className="flex items-center justify-between text-xs gap-2">
                              <div className="flex items-center gap-2">
                                <span className="px-2 py-0.5 rounded bg-emerald-500/20 border border-emerald-400/40 text-emerald-100 font-bold">{g.n}</span>
                                <span className="text-slate-400 font-mono">{g.born_door}</span>
                                <span className="text-slate-500">@{g.born_date}</span>
                              </div>
                              <div className="text-amber-300/80">age {g.age}d</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* Quarter shape + saturation + chainless */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                      {ghostEngineData.quarter_shape?.chord && (
                        <div className="rounded p-2 bg-slate-900/40 border border-slate-700/50">
                          <div className="text-[10px] text-slate-400 uppercase tracking-wider">🎼 Quarter shape</div>
                          <div className="text-sm font-mono text-amber-200 mt-1">{ghostEngineData.quarter_shape.chord}</div>
                          <div className="text-[10px] text-slate-500">hit {ghostEngineData.quarter_shape.count}/{ghostEngineData.quarter_shape.total_draws}</div>
                        </div>
                      )}
                      {ghostEngineData.saturation?.saturated?.length > 0 && (
                        <div className="rounded p-2 bg-slate-900/40 border border-slate-700/50">
                          <div className="text-[10px] text-slate-400 uppercase tracking-wider">🌌 Saturation</div>
                          {ghostEngineData.saturation.saturated.slice(0, 3).map((s, i) => (
                            <div key={i} className="text-sm text-fuchsia-200 font-mono">
                              {s.n} ×{s.count} <span className="text-slate-500 text-[10px]">{s.decade}</span>
                            </div>
                          ))}
                          {ghostEngineData.saturation.next_family_rare_zone && (
                            <div className="text-[10px] text-amber-300 mt-1">→ family-rare zone {ghostEngineData.saturation.next_family_rare_zone}</div>
                          )}
                        </div>
                      )}
                      <div className="rounded p-2 bg-slate-900/40 border border-slate-700/50">
                        <div className="text-[10px] text-slate-400 uppercase tracking-wider">🔇 Chainless</div>
                        <div className="text-sm text-emerald-300 font-mono">
                          {(ghostEngineData.chainless_windows || []).filter(c => c.is_cash_window).length} cash-windows
                        </div>
                        <div className="text-[10px] text-slate-500">in last {ghostEngineData.lookback} draws</div>
                      </div>
                    </div>
                    {/* Closures summary */}
                    {ghostEngineData.closed_ghosts_summary && (
                      <div className="rounded p-2 bg-slate-900/30 border border-slate-700/40 text-[11px] text-slate-300">
                        <span className="text-emerald-300 font-semibold">Closures · </span>
                        total {ghostEngineData.closed_ghosts_summary.total} ·
                        alive {ghostEngineData.closed_ghosts_summary.alive} ·
                        closed {ghostEngineData.closed_ghosts_summary.closed} ·
                        💤 deep-sleep {ghostEngineData.closed_ghosts_summary.deep_sleep_closures} ·
                        🪜 4-late {ghostEngineData.closed_ghosts_summary.late_4_5_closures}
                      </div>
                    )}
                    <div className="text-[10px] text-amber-400/60 italic">{ghostEngineData.canon}</div>
                  </div>
                )}
                {ghostEngineData?.error && (
                  <div className="text-rose-400 text-xs p-2 rounded bg-rose-950/30 border border-rose-500/30" data-testid="ghost-engine-error">
                    {ghostEngineData.error}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 🧠 E's COSMIC BRAIN — Session 30 — VIP only */}
        {lotteryMode === 'euro' && isUnlimited && (
          <div className="lucky-card p-4 mb-4" data-testid="cosmic-brain-panel">
            <button
              onClick={() => setShowCosmicBrain(!showCosmicBrain)}
              className="w-full flex items-center justify-between text-left"
              data-testid="cosmic-brain-toggle"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">🧠</span>
                <span className="font-semibold text-slate-200">E's Cosmic Brain</span>
                <span className="text-xs text-fuchsia-400/70">(20-ticket Symphony · 432 Hz)</span>
              </div>
              {showCosmicBrain ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </button>

            {showCosmicBrain && (
              <div className="mt-4 space-y-4" data-testid="cosmic-brain-content">
                {/* Inputs */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div>
                    <label className="text-slate-400">🎯 Target date (dd.mm.yyyy)</label>
                    <input
                      type="text"
                      value={brainTargetDate}
                      onChange={(e) => setBrainTargetDate(e.target.value)}
                      className="w-full mt-1 px-2 py-1 rounded bg-slate-800/60 border border-slate-700 text-slate-200 font-mono"
                      data-testid="brain-target-date"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">🌌 Seed mains (comma-sep)</label>
                    <input
                      type="text"
                      value={brainSeedMains}
                      onChange={(e) => setBrainSeedMains(e.target.value)}
                      className="w-full mt-1 px-2 py-1 rounded bg-slate-800/60 border border-slate-700 text-slate-200 font-mono"
                      data-testid="brain-seed-mains"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">⭐ Seed stars (comma-sep)</label>
                    <input
                      type="text"
                      value={brainSeedStars}
                      onChange={(e) => setBrainSeedStars(e.target.value)}
                      className="w-full mt-1 px-2 py-1 rounded bg-slate-800/60 border border-slate-700 text-slate-200 font-mono"
                      data-testid="brain-seed-stars"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">📌 DJ-pin mains (optional)</label>
                    <input
                      type="text"
                      value={brainPinMains}
                      onChange={(e) => setBrainPinMains(e.target.value)}
                      placeholder="e.g. 28,38"
                      className="w-full mt-1 px-2 py-1 rounded bg-slate-800/60 border border-slate-700 text-slate-200 font-mono"
                      data-testid="brain-pin-mains"
                    />
                  </div>
                </div>

                <button
                  onClick={runCosmicBrain}
                  disabled={cosmicBrainLoading}
                  className="w-full py-2 px-4 rounded bg-gradient-to-r from-fuchsia-600/40 to-purple-600/40 border border-fuchsia-500/50 text-fuchsia-100 font-semibold hover:from-fuchsia-600/60 hover:to-purple-600/60 disabled:opacity-50 transition-all"
                  data-testid="cosmic-brain-run-btn"
                >
                  {cosmicBrainLoading ? '🌀 Tuning the cosmos…' : '🎻 Run the Brain'}
                </button>

                {/* Results */}
                {cosmicBrainData && cosmicBrainData.error && (
                  <div className="text-rose-400 text-xs p-2 rounded bg-rose-950/30 border border-rose-500/30">
                    ❌ {cosmicBrainData.error}
                  </div>
                )}

                {cosmicBrainData && cosmicBrainData.tickets && (
                  <div className="space-y-3" data-testid="cosmic-brain-results">
                    {/* Brain summary cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {/* Frequency card */}
                      <div className="rounded border border-fuchsia-500/30 bg-fuchsia-950/20 p-2.5"
                           data-testid="brain-frequency-card">
                        <div className="text-[10px] text-fuchsia-400 font-semibold mb-1">🎼 FREQUENCY</div>
                        <div className="text-fuchsia-100 font-mono text-sm">
                          {cosmicBrainData.brain_summary?.frequency_primary?.freq || '—'} Hz
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          {cosmicBrainData.brain_summary?.frequency_primary?.decode || ''}
                        </div>
                        <div className="text-[10px] text-slate-500 mt-1 font-mono">
                          divisors: {Object.entries(cosmicBrainData.brain_summary?.frequency_divisors || {})
                            .map(([k, v]) => `${k}→${v}`).join(' · ') || '—'}
                        </div>
                      </div>
                      {/* Envelope card */}
                      <div className="rounded border border-purple-500/30 bg-purple-950/20 p-2.5"
                           data-testid="brain-envelope-card">
                        <div className="text-[10px] text-purple-400 font-semibold mb-1">📅 DATE ENVELOPE</div>
                        <div className="text-purple-100 font-mono text-sm">
                          {cosmicBrainData.brain_summary?.envelope?.day}-{cosmicBrainData.brain_summary?.envelope?.month}
                          {cosmicBrainData.brain_summary?.envelope?.is_void
                            ? <span className="text-amber-400 ml-2">VOID</span>
                            : <span className="text-emerald-400 ml-2">hides {JSON.stringify(cosmicBrainData.brain_summary?.envelope?.hidden_digits)}</span>}
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          d×m={cosmicBrainData.brain_summary?.envelope?.day_x_month} · sum={cosmicBrainData.brain_summary?.envelope?.date_sum_dj}
                        </div>
                      </div>
                      {/* Precedent card */}
                      <div className="rounded border border-amber-500/30 bg-amber-950/20 p-2.5 sm:col-span-2"
                           data-testid="brain-precedent-card">
                        <div className="text-[10px] text-amber-400 font-semibold mb-1">🪞 PRECEDENT (last identical-stars event)</div>
                        {cosmicBrainData.brain_summary?.precedent_summary?.seed_date ? (
                          <div className="text-amber-100 text-xs font-mono">
                            {cosmicBrainData.brain_summary.precedent_summary.seed_date} →&nbsp;
                            <span className="text-emerald-300">{cosmicBrainData.brain_summary.precedent_summary.nd_date}</span>
                            &nbsp;mains <span className="font-bold">{JSON.stringify(cosmicBrainData.brain_summary.precedent_summary.nd_mains)}</span>
                            &nbsp;⭐<span className="font-bold">{JSON.stringify(cosmicBrainData.brain_summary.precedent_summary.nd_stars)}</span>
                          </div>
                        ) : (
                          <div className="text-slate-400 text-xs">No precedent found.</div>
                        )}
                      </div>
                    </div>

                    {/* Suspects table */}
                    <div className="rounded border border-emerald-500/30 bg-emerald-950/20 p-2.5"
                         data-testid="brain-suspects-card">
                      <div className="text-[10px] text-emerald-400 font-semibold mb-1.5">💎 RANKED SUSPECTS (top 10)</div>
                      <div className="grid grid-cols-2 sm:grid-cols-5 gap-1.5">
                        {(cosmicBrainData.brain_summary?.ranked_suspects_top10 || []).map((s) => (
                          <div key={s.n}
                               className="rounded border border-emerald-500/40 bg-emerald-600/10 px-1.5 py-1"
                               title={s.tags?.join(' · ')}
                               data-testid={`brain-suspect-${s.n}`}>
                            <div className="flex items-baseline justify-between">
                              <span className="text-emerald-100 font-bold tabular-nums">{s.n}</span>
                              <span className="text-[8px] text-emerald-400/70">×{s.score}</span>
                            </div>
                            <div className="text-[8px] text-emerald-300/70 truncate">
                              {(s.tags || []).slice(0, 2).join('·')}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Stars table */}
                    <div className="rounded border border-yellow-500/30 bg-yellow-950/20 p-2.5"
                         data-testid="brain-stars-card">
                      <div className="text-[10px] text-yellow-400 font-semibold mb-1.5">⭐ RANKED STARS (top 6)</div>
                      <div className="flex flex-wrap gap-1.5">
                        {(cosmicBrainData.brain_summary?.ranked_stars_top6 || []).map((s) => (
                          <div key={s.s}
                               className="rounded border border-yellow-500/40 bg-yellow-600/10 px-2 py-1"
                               title={s.tags?.join(' · ')}
                               data-testid={`brain-star-${s.s}`}>
                            <span className="text-yellow-100 font-bold">⭐{s.s}</span>
                            <span className="text-[9px] text-yellow-400/60 ml-1">×{s.score}</span>
                            <div className="text-[8px] text-yellow-300/70">
                              {(s.tags || []).slice(0, 1).join('·')}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Lens fires */}
                    <div className="grid grid-cols-3 gap-2 text-[10px]">
                      <div className={`rounded border p-1.5 ${cosmicBrainData.brain_summary?.law_90?.fires ? 'border-rose-500/50 bg-rose-950/30 text-rose-200' : 'border-slate-700 bg-slate-900/30 text-slate-500'}`}
                           data-testid="brain-law90">
                        <div className="font-semibold">📍 Law 90</div>
                        <div>{cosmicBrainData.brain_summary?.law_90?.fires ? '🚨 FIRES' : 'silent'}</div>
                        <div>last P3: {cosmicBrainData.brain_summary?.law_90?.last_p3}</div>
                      </div>
                      <div className={`rounded border p-1.5 ${cosmicBrainData.brain_summary?.law_89?.fires ? 'border-cyan-500/50 bg-cyan-950/30 text-cyan-200' : 'border-slate-700 bg-slate-900/30 text-slate-500'}`}
                           data-testid="brain-law89">
                        <div className="font-semibold">📍 Law 89</div>
                        <div>{cosmicBrainData.brain_summary?.law_89?.fires ? '🚨 FIRES' : 'silent'}</div>
                        <div>last P2: {cosmicBrainData.brain_summary?.law_89?.last_p2}</div>
                      </div>
                      <div className={`rounded border p-1.5 ${cosmicBrainData.brain_summary?.saturation_47?.saturated ? 'border-orange-500/50 bg-orange-950/30 text-orange-200' : 'border-slate-700 bg-slate-900/30 text-slate-500'}`}
                           data-testid="brain-saturation">
                        <div className="font-semibold">📍 47-saturation</div>
                        <div>{cosmicBrainData.brain_summary?.saturation_47?.fires_count || 0}/{cosmicBrainData.brain_summary?.saturation_47?.window || 4}</div>
                        <div>{cosmicBrainData.brain_summary?.saturation_47?.saturated ? '🚨 collapse' : 'no fold'}</div>
                      </div>
                    </div>

                    {/* The 20-ticket symphony */}
                    <div className="rounded border border-fuchsia-500/40 bg-gradient-to-br from-fuchsia-950/30 to-purple-950/30 p-3"
                         data-testid="brain-tickets-card">
                      <div className="text-xs font-semibold text-fuchsia-200 mb-2 flex items-center justify-between">
                        <span>🎼 THE {cosmicBrainData.ticket_count}-TICKET SYMPHONY</span>
                        <span className="text-[10px] text-fuchsia-400/60 font-mono">7 archetypes · {cosmicBrainData.target_date}</span>
                      </div>
                      <div className="space-y-1.5">
                        {(cosmicBrainData.tickets || []).map((t) => {
                          const archColor = (t.archetype || '').startsWith('A.') ? 'border-fuchsia-500/40 bg-fuchsia-950/20'
                            : (t.archetype || '').startsWith('B.') ? 'border-purple-500/40 bg-purple-950/20'
                            : (t.archetype || '').startsWith('C.') ? 'border-emerald-500/40 bg-emerald-950/20'
                            : (t.archetype || '').startsWith('D.') ? 'border-amber-500/40 bg-amber-950/20'
                            : (t.archetype || '').startsWith('E.') ? 'border-rose-500/40 bg-rose-950/20'
                            : (t.archetype || '').startsWith('F.') ? 'border-orange-500/40 bg-orange-950/20'
                            : 'border-cyan-500/40 bg-cyan-950/20';
                          return (
                            <div key={t.ticket_no}
                                 className={`rounded border ${archColor} p-2`}
                                 data-testid={`brain-ticket-${t.ticket_no}`}>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-[10px] text-slate-400 font-mono">#{t.ticket_no}</span>
                                <span className="text-[10px] text-slate-300 font-semibold">{t.archetype}</span>
                              </div>
                              <div className="flex flex-wrap items-center gap-1 mb-1">
                                {(t.mains || []).map((n) => (
                                  <Ball key={n} number={n} size="xs" maxNum={50} />
                                ))}
                                <span className="text-slate-500 mx-1">·</span>
                                {(t.stars || []).map((s) => (
                                  <span key={s} className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-yellow-500/20 border border-yellow-400/40 text-yellow-200 text-[10px] font-bold">
                                    ⭐{s}
                                  </span>
                                ))}
                              </div>
                              <div className="text-[10px] text-slate-400 italic">{t.reasoning}</div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 2CHANCE - Swiss Second Chance Draw (EuroMillions only) — VIP only */}
        {lotteryMode === 'euro' && isUnlimited && (
          <div className="lucky-card p-4 mb-4" data-testid="twochance-panel">
            <button 
              onClick={() => setShow2Chance(!show2Chance)}
              className="w-full flex items-center justify-between text-left"
              data-testid="twochance-toggle"
            >
              <div className="flex items-center gap-2">
                <Gift className="w-5 h-5 text-orange-400" />
                <span className="font-semibold text-slate-200">2Chance</span>
                <span className="text-xs text-orange-400/70">(Auto-synced with Euro)</span>
              </div>
              {show2Chance ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </button>
            
            {show2Chance && (
              <div className="mt-4 space-y-4">
                {/* Saved 2Chance Draws */}
                {twoChanceHistory.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-xs text-slate-400">Recent 2Chance Draws:</span>
                    {twoChanceHistory.slice(0, 5).map((d, idx) => (
                      <div key={idx} className="flex items-center gap-2 p-2 rounded-lg bg-slate-800/40 border border-slate-700/50">
                        <span className="text-xs text-slate-400 w-20">{d.date}</span>
                        <div className="flex items-center gap-1">
                          {d.numbers?.map((n, i) => (
                            <Ball key={i} number={n} size="xs" maxNum={50} />
                          ))}
                        </div>
                        {d.source && <span className="text-[9px] text-slate-600 ml-auto">{d.source}</span>}
                      </div>
                    ))}
                  </div>
                )}
                
                {twoChanceHistory.length === 0 && (
                  <div className="text-center text-slate-500 text-sm py-2">
                    No 2Chance draws yet. Hit "Update Draws" to sync.
                  </div>
                )}
                
                {/* Check 2Chance Hits Button */}
                <button
                  onClick={check2ChanceHits}
                  disabled={twoChanceChecking}
                  className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white font-bold text-sm transition-all disabled:opacity-50"
                  data-testid="twochance-check-btn"
                >
                  {twoChanceChecking ? (
                    <span className="flex items-center justify-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin" /> Checking...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      <CheckCircle2 className="w-4 h-4" /> Check 2Chance Hits
                    </span>
                  )}
                </button>
                
                {/* 2Chance Results */}
                {twoChanceResults && twoChanceResults.map((r, idx) => (
                  <div key={idx} className="p-3 rounded-lg" style={{ background: 'linear-gradient(135deg, rgba(251,146,60,0.08) 0%, rgba(234,88,12,0.04) 100%)', border: '1px solid rgba(251,146,60,0.2)' }}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-orange-300">2Chance {r.date}</span>
                        <div className="flex items-center gap-1">
                          {r.twochance_numbers?.map((n, i) => (
                            <Ball key={i} number={n} size="xs" maxNum={50} />
                          ))}
                        </div>
                      </div>
                      <span className="text-xs text-slate-500">{r.tickets_checked} checked</span>
                    </div>
                    
                    {r.winners?.length > 0 ? (
                      <div className="space-y-1.5">
                        <span className="text-xs text-emerald-400 font-medium">{r.total_matches} ticket(s) with 2+ matches!</span>
                        {r.winners.map((w, widx) => {
                          const matchSet = new Set(w.matches);
                          return (
                            <div key={widx} className={`flex items-center gap-2 p-1.5 rounded-lg ${
                              w.match_count >= 3 ? 'bg-emerald-500/15 border border-emerald-500/30' : 'bg-slate-700/30'
                            }`}>
                              <span className={`text-xs font-bold ${
                                w.match_count >= 4 ? 'text-amber-400' : w.match_count >= 3 ? 'text-emerald-400' : 'text-slate-400'
                              }`}>{w.match_count}/5</span>
                              <div className="flex items-center gap-0.5">
                                {w.numbers.map((n, ni) => (
                                  <div key={ni} className={`w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-bold ${
                                    matchSet.has(n)
                                      ? 'bg-orange-500 text-white ring-1 ring-orange-400'
                                      : 'bg-slate-700 text-slate-400'
                                  }`}>{n}</div>
                                ))}
                              </div>
                              <span className={`text-[10px] ml-auto ${
                                w.match_count >= 3 ? 'text-emerald-400 font-bold' : 'text-slate-500'
                              }`}>{w.prize_tier}</span>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">No tickets with 2+ matches</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* HIT TRACKER SECTION - Story Generator History & Hits — VIP only */}
        {isUnlimited && (
        <div className="lucky-card p-4 mb-4">
          <button 
            onClick={() => setShowHitTracker(!showHitTracker)}
            className="w-full flex items-center justify-between text-left"
          >
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-emerald-400" />
              <span className="font-semibold text-slate-200">🎯 Hit Tracker</span>
              <span className="text-xs text-slate-500">(Story Generator History)</span>
            </div>
            {showHitTracker ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </button>
          
          {showHitTracker && (
            <div className="mt-4 space-y-4">
              {/* 🎯 S40.2 — "Full File" toggle (Swiss only) */}
              {lotteryMode === 'swiss' && (
                <div className="flex items-center justify-between gap-2 px-3 py-2 rounded-lg bg-slate-900/40 border border-slate-700">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-300">📂 Full file per draw</span>
                    <span className="text-[10px] text-slate-500">(show every generated ticket, not only 2+ hits)</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer" data-testid="hit-tracker-full-toggle-label">
                    <input
                      type="checkbox"
                      checked={hitTrackerFullFile}
                      onChange={(e) => setHitTrackerFullFile(e.target.checked)}
                      className="sr-only peer"
                      data-testid="hit-tracker-full-toggle"
                    />
                    <div className="w-10 h-5 bg-slate-700 peer-focus:ring-2 peer-focus:ring-emerald-400 rounded-full peer peer-checked:after:translate-x-5 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-600"></div>
                  </label>
                </div>
              )}

              {/* Last Draw Result */}
              {lastDraw && (
                <div className={`p-3 rounded-lg bg-gradient-to-r ${
                  lotteryMode === 'euro' 
                    ? 'from-blue-500/20 to-blue-600/10 border border-blue-500/30'
                    : 'from-emerald-500/20 to-emerald-600/10 border border-emerald-500/30'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`font-semibold text-sm ${lotteryMode === 'euro' ? 'text-blue-400' : 'text-emerald-400'}`}>
                      📊 Last {lotteryMode === 'euro' ? 'Euro' : 'Swiss'} Draw
                    </span>
                    <span className="text-slate-400 text-xs">{lastDraw.date}</span>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    {lastDraw.numbers?.map((n, i) => (
                      <Ball key={i} number={n} size="sm" maxNum={lotteryMode === 'euro' ? 50 : 42} />
                    ))}
                    {lotteryMode === 'euro' && lastDraw.stars && (
                      <span className="ml-2 px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-400 text-sm font-medium">
                        ⭐ {lastDraw.stars.join(', ')}
                      </span>
                    )}
                    {lotteryMode === 'swiss' && lastDraw.lucky_number && (
                      <span className="ml-2 px-2 py-1 rounded-full bg-amber-500/20 text-amber-400 text-sm font-medium">
                        🍀 {lastDraw.lucky_number}
                      </span>
                    )}
                  </div>
                </div>
              )}
              
              {/* Stats Overview */}
              {hitStats?.stats && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700 text-center">
                    <div className="text-xl font-bold text-amber-400">{hitStats.stats.total_generations}</div>
                    <div className="text-xs text-slate-500">Generations</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700 text-center">
                    <div className="text-xl font-bold text-emerald-400">{hitStats.stats.total_number_hits}</div>
                    <div className="text-xs text-slate-500">Total Hits</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700 text-center">
                    <div className="text-xl font-bold text-blue-400">{hitStats.stats.best_ever_hits}</div>
                    <div className="text-xs text-slate-500">Best Ticket</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700 text-center">
                    <div className="text-xl font-bold text-purple-400">{hitStats.stats.tickets_with_3plus}</div>
                    <div className="text-xs text-slate-500">3+ Hits</div>
                  </div>
                </div>
              )}
              
              {/* PER-DRAW PULSE — draw-to-draw breakdown (Swiss + Euro) */}
              {perDrawStats.length > 0 && (
                <div className={`p-3 rounded-lg bg-gradient-to-br from-slate-800/60 to-slate-900/80 border ${lotteryMode === 'euro' ? 'border-blue-500/20' : 'border-amber-500/20'}`} data-testid="per-draw-pulse">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`font-semibold text-sm flex items-center gap-2 ${lotteryMode === 'euro' ? 'text-blue-400' : 'text-amber-400'}`}>
                      🎻 Draw-to-Draw Pulse
                    </span>
                    <span className="text-slate-500 text-[10px]">Generated per draw • Hit rate</span>
                  </div>
                  <div className="space-y-1.5">
                    {perDrawStats.map((s, idx) => (
                      <div key={idx} className="p-2 rounded-md bg-slate-900/60 border border-slate-700/40" data-testid={`per-draw-row-${idx}`}>
                        <div className="flex items-center justify-between gap-2 text-xs">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="text-slate-400 font-mono">
                              {s.window_label || s.date}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 flex-wrap justify-end">
                            <span className="text-slate-300">
                              <span className={`font-bold ${lotteryMode === 'euro' ? 'text-blue-400' : 'text-amber-400'}`}>{s.total_generated}</span>
                              <span className="text-slate-500"> gen</span>
                            </span>
                            <span className="text-slate-300">
                              <span className="text-emerald-400 font-bold">{s.hits_2plus}</span>
                              <span className="text-slate-500"> ×2+</span>
                            </span>
                            {s.hits_3plus > 0 && (
                              <span className="text-purple-400 font-bold">{s.hits_3plus}× 3+</span>
                            )}
                            {s.hits_4plus > 0 && (
                              <span className="text-pink-400 font-bold">{s.hits_4plus}× 4+ 🔥</span>
                            )}
                            <span className="px-1.5 py-0.5 rounded bg-blue-500/15 text-blue-300 font-semibold">
                              best {s.best_total_match ?? s.best_hit}/{lotteryMode === 'euro' ? 5 : 6}{s.best_ticket?.lucky_hit ? '+L' : ''}
                            </span>
                            <span className={`px-1.5 py-0.5 rounded font-bold ${
                              s.hit_rate_pct >= 20 ? 'bg-emerald-500/20 text-emerald-300' :
                              s.hit_rate_pct >= 10 ? 'bg-amber-500/20 text-amber-300' :
                              'bg-slate-700/40 text-slate-400'
                            }`}>
                              {s.hit_rate_pct}%
                            </span>
                          </div>
                        </div>
                        {/* BEST TICKET OF THE DRAW — inline callout */}
                        {s.best_ticket && s.best_ticket.total_match >= 2 && (
                          <div className="mt-2 p-2 rounded bg-gradient-to-r from-amber-500/10 to-amber-600/5 border border-amber-500/30" data-testid={`best-ticket-${idx}`}>
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-amber-300 font-semibold text-[11px]">
                                🏆 Lucky Jack #{s.best_ticket.ticket_num_in_window} · {s.best_ticket.nickname}
                              </span>
                              <span className="text-[10px] text-slate-400">
                                {s.best_ticket.total_match}/{lotteryMode === 'euro' ? 5 : 6} match
                              </span>
                            </div>
                            <div className="flex items-center gap-1 flex-wrap">
                              {s.best_ticket.numbers?.map((n, i) => {
                                const isHit = (s.best_ticket.hits || []).includes(n);
                                return (
                                  <div key={i} className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${
                                    isHit ? 'bg-emerald-500 text-white ring-2 ring-emerald-300' : 'bg-slate-700 text-slate-300'
                                  }`}>{n}</div>
                                );
                              })}
                              <span className={`text-[10px] ml-1 ${s.best_ticket.lucky_hit ? 'text-emerald-300 font-bold' : 'text-amber-400/60'}`}>
                                🍀{s.best_ticket.lucky}{s.best_ticket.lucky_hit ? ' ✓' : ''}
                              </span>
                            </div>
                            <div className="text-[10px] text-slate-400 mt-1">
                              🕐 {s.best_ticket.generated_at ? new Date(s.best_ticket.generated_at).toLocaleString() : '—'} · {s.best_ticket.generation_type}
                            </div>
                          </div>
                        )}
                        {/* 📦 FULL ARCHIVE TOGGLE — DJ wants every ticket with date */}
                        <button
                          onClick={() => toggleArchiveDate(s.date)}
                          className="mt-2 w-full text-left text-[10px] text-slate-400 hover:text-amber-300 transition-colors flex items-center justify-between px-1"
                          data-testid={`archive-toggle-${idx}`}
                        >
                          <span>📦 {archiveDateOpen === s.date ? 'Hide' : 'Show'} all {s.total_generated} tickets</span>
                          <span className="text-slate-600">{archiveDateOpen === s.date ? '▲' : '▼'}</span>
                        </button>
                        {archiveDateOpen === s.date && (
                          <div className="mt-2 p-2 rounded bg-slate-950/60 border border-slate-700/40 max-h-64 overflow-y-auto">
                            {archiveByDate[s.date]?.loading ? (
                              <div className="text-[10px] text-slate-500 text-center py-2">Loading archive…</div>
                            ) : !archiveByDate[s.date]?.tickets?.length ? (
                              <div className="text-[10px] text-slate-500 text-center py-2">No tickets.</div>
                            ) : (
                              <div className="space-y-1">
                                <div className="text-[10px] text-slate-500 mb-1">
                                  {archiveByDate[s.date].total} total · sorted newest first
                                </div>
                                {archiveByDate[s.date].tickets.map((t) => (
                                  <div key={`${t.ticket_num_global}-${t.generated_at}`} className={`flex items-center gap-1 text-[10px] px-1 py-0.5 rounded ${
                                    t.total_match >= 3 ? 'bg-emerald-500/10' : t.total_match >= 2 ? 'bg-amber-500/5' : ''
                                  }`}>
                                    <span className="text-slate-500 w-8">#{t.ticket_num_global}</span>
                                    <div className="flex items-center gap-0.5">
                                      {t.numbers?.map((n, i) => {
                                        const isHit = (t.hits || []).includes(n);
                                        return (
                                          <div key={i} className={`w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold ${
                                            isHit ? 'bg-emerald-500 text-white' : 'bg-slate-700 text-slate-300'
                                          }`}>{n}</div>
                                        );
                                      })}
                                    </div>
                                    {lotteryMode === 'euro' ? (
                                      <span className="text-yellow-400/80 ml-0.5">⭐{(t.stars || []).join(',')}</span>
                                    ) : (
                                      <span className={`ml-0.5 ${t.lucky_hit ? 'text-emerald-300 font-bold' : 'text-amber-400/60'}`}>
                                        🍀{t.lucky}{t.lucky_hit ? '✓' : ''}
                                      </span>
                                    )}
                                    {t.draw_known && t.total_match > 0 && (
                                      <span className={`text-[9px] ml-0.5 ${t.total_match >= 3 ? 'text-emerald-400 font-bold' : 'text-slate-400'}`}>
                                        {t.total_match}pc
                                      </span>
                                    )}
                                    <span className="text-slate-600 ml-auto text-[9px]">
                                      {t.generated_at ? new Date(t.generated_at).toLocaleString([], {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'}) : ''}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Generate Story Tickets Button */}
              <div className="flex gap-2">
                <button
                  onClick={generateStoryTickets}
                  disabled={storyLoading}
                  className={`flex-1 py-2 px-4 rounded-lg bg-gradient-to-r ${
                    lotteryMode === 'euro' 
                      ? 'from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600'
                      : 'from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600'
                  } text-white font-semibold text-sm transition-all disabled:opacity-50`}
                >
                  {storyLoading ? '🔮 Generating...' : `🎻 Generate Story Tickets (8 × ${lotteryMode === 'euro' ? '3.50' : '2.50'} = ${lotteryMode === 'euro' ? '28' : '20'} CHF)`}
                </button>
                <button
                  onClick={recalculateAllHits}
                  disabled={hitTrackerLoading}
                  className="py-2 px-3 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm transition-all disabled:opacity-50"
                  title="Recalculate all pending hits"
                >
                  <RefreshCw className={`w-4 h-4 ${hitTrackerLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>
              
              {/* Latest Generated Tickets */}
              {storyTickets && (
                <div className={`p-3 rounded-lg bg-gradient-to-r ${
                  lotteryMode === 'euro'
                    ? 'from-blue-500/10 to-blue-600/5 border border-blue-500/20'
                    : 'from-amber-500/10 to-amber-600/5 border border-amber-500/20'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`font-semibold text-sm ${lotteryMode === 'euro' ? 'text-blue-400' : 'text-amber-400'}`}>
                      🎻 ALL STORIES COMBINED! {lotteryMode === 'euro' ? '⭐' : '🍀'}
                    </span>
                    <span className="text-slate-400 text-xs">Target: {storyTickets.target_date}</span>
                  </div>
                  <div className="space-y-2">
                    {storyTickets.tickets?.map((ticket, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-xs">
                        <span className="text-slate-500 w-6">T{idx + 1}:</span>
                        <div className="flex items-center gap-1">
                          {ticket.numbers?.map((n, i) => (
                            <Ball key={i} number={n} size="xs" maxNum={lotteryMode === 'euro' ? 50 : 42} />
                          ))}
                        </div>
                        {lotteryMode === 'euro' ? (
                          <span className="text-yellow-400">⭐{ticket.stars?.join(',')}</span>
                        ) : (
                          <span className="text-amber-400">🍀{ticket.lucky}</span>
                        )}
                        <span className="text-slate-500 text-[10px] ml-1">{ticket.story}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-2 text-center text-emerald-400 text-xs font-medium">
                    {storyTickets.cost_estimate} 🎲
                  </div>
                </div>
              )}
              
              {/* Generation History */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-300 font-medium text-sm">
                    {lotteryMode === 'swiss' ? '🎯 Best Tickets (2+ hits, last 3 draws)' : '📜 Generation History'}
                  </span>
                  {generationHistory.length > 0 && (
                    <span className="text-slate-500 text-xs">{generationHistory.length} results</span>
                  )}
                </div>
                <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
                  {hitTrackerLoading ? (
                    <div className="text-center text-slate-500 text-sm py-4">Loading...</div>
                  ) : generationHistory.length === 0 ? (
                    <div className="text-center text-slate-500 text-sm py-4">
                      No generations saved yet. Generate numbers to start tracking!
                    </div>
                  ) : lotteryMode === 'swiss' ? (
                    /* SWISS CLEAN HIT TRACKER */
                    generationHistory.map((r, idx) => (
                      <div 
                        key={idx}
                        className={`p-3 rounded-lg border ${
                          r.hit_count >= 4 ? 'bg-gradient-to-r from-amber-500/20 to-amber-600/10 border-amber-400/40' :
                          r.hit_count >= 3 ? 'bg-gradient-to-r from-emerald-500/20 to-emerald-600/10 border-emerald-400/40' :
                          'bg-gradient-to-r from-emerald-500/10 to-emerald-600/5 border-emerald-500/20'
                        }`}
                        data-testid={`hit-result-${idx}`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-slate-400 text-xs">
                            {r.hit_count >= 4 ? '💰' : r.hit_count >= 3 ? '🔥' : '✓'} #{r.ticket_num || idx+1} · <span className="text-slate-200 font-semibold">{r.window_label || r.target_date}</span>
                          </span>
                          <span className={`text-xs font-bold ${r.hit_count >= 3 ? 'text-emerald-400' : 'text-slate-400'}`}>
                            {r.hit_count}/6 {r.lucky_hit ? '+L' : ''}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          {r.numbers?.map((n, i) => {
                            const isHit = r.hits?.includes(n);
                            return (
                              <div key={i} className={`w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold ${
                                isHit ? 'bg-emerald-500 text-white ring-2 ring-emerald-400' : 'bg-slate-700 text-slate-400'
                              }`}>
                                {n}
                              </div>
                            );
                          })}
                          <span className={`text-xs ml-1 ${r.lucky_hit ? 'text-emerald-400 font-bold' : 'text-amber-400/50'}`}>
                            🍀{r.lucky}
                          </span>
                          <span className="text-[9px] text-slate-600 ml-auto">{r.story}</span>
                        </div>
                        <div className="text-[10px] text-slate-500 mt-1 flex flex-wrap gap-x-2">
                          <span>Actual: {r.actual_numbers?.join(', ')} L={r.actual_lucky}</span>
                          {r.generated_at && <span className="text-slate-600">🕐 {new Date(r.generated_at).toLocaleString()}</span>}
                          {typeof r.days_from_bd === 'number' && <span className="text-slate-600">{r.days_from_bd >= 0 ? `+${r.days_from_bd}d from BD` : `${r.days_from_bd}d pre-BD`}</span>}
                        </div>
                      </div>
                    ))
                  ) : (
                    /* EURO GENERATION HISTORY (original format) */
                    generationHistory.map((gen, idx) => {
                      const modeLabel = gen.mode === 'money' ? '💰' : gen.mode === 'dreaming' ? '🌟' : '🎻';
                      return (
                      <div 
                        key={gen._id || idx}
                        className={`p-3 rounded-lg border ${
                          gen.hits_calculated 
                            ? gen.best_ticket_hits >= 2
                              ? 'bg-gradient-to-r from-emerald-500/20 to-emerald-600/10 border-emerald-400/40'
                              : 'bg-gradient-to-r from-emerald-500/10 to-emerald-600/5 border-emerald-500/20'
                            : 'bg-gradient-to-r from-slate-500/10 to-slate-600/5 border-slate-500/20'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {gen.hits_calculated ? (
                              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            ) : (
                              <Clock className="w-4 h-4 text-slate-400" />
                            )}
                            <span className="text-slate-400 text-xs">
                              {modeLabel} For: <span className="text-slate-200 font-semibold">{gen.target_date}</span>
                            </span>
                          </div>
                          <span className="text-slate-500 text-xs">
                            {gen.tickets?.length || 0} tickets
                          </span>
                        </div>
                        
                        {/* Show tickets with hit highlighting */}
                        <div className="space-y-1">
                          {gen.tickets?.map((ticket, tidx) => {
                            const hitResult = gen.hit_results?.[tidx];
                            const hitNumbers = new Set(hitResult?.number_hits || []);
                            const hitStars = new Set(hitResult?.star_hits || []);
                            const totalHits = (hitResult?.hit_count || 0) + (hitResult?.star_hit_count || 0);
                            
                            return (
                              <div key={tidx} className={`flex items-center gap-1 text-xs ${totalHits >= 3 ? 'p-1 rounded bg-emerald-500/10 border border-emerald-500/20' : ''}`}>
                                <span className={`w-5 ${totalHits >= 3 ? 'text-emerald-400 font-bold' : 'text-slate-500'}`}>
                                  {totalHits >= 4 ? '💰' : totalHits >= 3 ? '🔥' : '✓'}
                                </span>
                                <div className="flex items-center gap-0.5">
                                  {ticket.numbers?.map((n, i) => (
                                    <div 
                                      key={i} 
                                      className={`w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-bold ${
                                        hitNumbers.has(n) 
                                          ? 'bg-emerald-500 text-white ring-2 ring-emerald-400' 
                                          : 'bg-slate-700 text-slate-300'
                                      }`}
                                    >
                                      {n}
                                    </div>
                                  ))}
                                </div>
                                {lotteryMode === 'euro' ? (
                                  <span className={`text-[10px] ${hitResult?.star_hit_count > 0 ? 'text-yellow-400 font-bold' : 'text-yellow-400/50'}`}>
                                    ⭐{ticket.stars?.join(',')}
                                  </span>
                                ) : (
                                  <span className={`text-[10px] ${hitResult?.lucky_hit ? 'text-emerald-400 font-bold' : 'text-amber-400/50'}`}>
                                    🍀{ticket.lucky}
                                  </span>
                                )}
                                {hitResult && (
                                  <span className={`text-[10px] ml-1 ${totalHits >= 3 ? 'text-emerald-400 font-bold' : 'text-emerald-400'}`}>
                                    ({hitResult.hit_count}/{lotteryMode === 'euro' ? '5' : '6'}{lotteryMode === 'euro' ? ` +${hitResult.star_hit_count || 0}⭐` : (hitResult.lucky_hit ? ' +L' : '')})
                                  </span>
                                )}
                                {ticket._mode && (
                                  <span className="text-[9px] text-slate-600 ml-auto">{ticket._mode === 'money' ? '💰' : '🌟'}</span>
                                )}
                              </div>
                            );
                          })}
                        </div>
                        
                        {/* Hit Summary */}
                        {gen.hits_calculated && (
                          <div className="mt-2 pt-2 border-t border-slate-700/50 flex items-center justify-between">
                            <div className="flex items-center gap-3 text-xs">
                              <span className="text-emerald-400">✓ {gen.total_hits} hits</span>
                              {lotteryMode === 'euro' ? (
                                <span className="text-yellow-400">⭐ {gen.star_hits || 0} stars</span>
                              ) : (
                                <span className="text-amber-400">🍀 {gen.lucky_hits} lucky</span>
                              )}
                              <span className="text-blue-400">🏆 Best: {gen.best_ticket_hits}/{lotteryMode === 'euro' ? '5' : '6'}</span>
                            </div>
                          </div>
                        )}
                        
                        {/* Calculate Hits Button for pending */}
                        {!gen.hits_calculated && (
                          <button
                            onClick={() => calculateHits(gen._id)}
                            className="mt-2 w-full py-1 px-2 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 text-xs transition-all"
                          >
                            Calculate Hits
                          </button>
                        )}
                      </div>
                    );})
                  )}
                </div>
                {generationHistory.some(g => !g.hits_calculated) && (
                  <button
                    onClick={recalculateAllHits}
                    disabled={hitTrackerLoading}
                    className={`w-full mt-4 py-3 px-4 rounded-lg font-bold text-lg transition-all disabled:opacity-50 ${
                      lotteryMode === 'euro'
                        ? 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white'
                        : 'bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white'
                    }`}
                    data-testid="check-all-hits-btn"
                  >
                    {hitTrackerLoading ? (
                      <span className="flex items-center justify-center gap-2">
                        <RefreshCw className="w-5 h-5 animate-spin" />
                        Checking...
                      </span>
                    ) : (
                      <span className="flex items-center justify-center gap-2">
                        <CheckCircle2 className="w-5 h-5" />
                        ✅ CHECK ALL PENDING HITS
                      </span>
                    )}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
        )}

        {/* Footer */}
        <div className="text-center text-slate-500 text-xs mt-6 pb-4">
          <p>Good luck! Play responsibly.</p>
          <div className="flex items-center justify-center gap-4 mt-1">
            <button 
              onClick={() => setShowGuide(true)}
              className="underline hover:text-slate-300 transition-colors"
              data-testid="guide-link"
            >
              How to Use
            </button>
            <span className="text-slate-700">|</span>
            <button 
              onClick={() => setShowDisclaimer(true)}
              className="underline hover:text-slate-300 transition-colors"
              data-testid="disclaimer-link"
            >
              Disclaimer & Terms
            </button>
          </div>
        </div>

        {/* HOW TO USE GUIDE */}
        {showGuide && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4" data-testid="guide-modal">
            <div className="bg-slate-800 border border-slate-600 rounded-xl max-w-lg w-full p-6 max-h-[80vh] overflow-y-auto">
              <h2 className="text-xl font-bold text-amber-400 mb-4">🎻 How to Use Lucky Jack</h2>
              
              <div className="text-slate-300 text-sm space-y-4">
                <p className="text-white font-semibold">Ya man 🍀 — Lucky Jack listens to the music of the numbers. Every draw has a rhythm. We tune into it with you.</p>
                
                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🎯 Two Lotteries · 20 + 20 Tickets</h3>
                  <p>Switch between <span className="text-white font-medium">Swiss Lotto</span> (6 numbers 1-42 + Lucky) and <span className="text-white font-medium">EuroMillions</span> (5 numbers 1-50 + 2 Stars) using the toggle at the top.</p>
                  <p className="mt-1"><span className="text-amber-400 font-semibold">You get 20 tickets per draw per lottery — independently.</span> That's up to <span className="text-emerald-400 font-bold">40 tickets total</span> per user across both modes. The count resets automatically when each new draw lands.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🌌 The Crown Cosmos (Hunt Box)</h3>
                  <p>A persistent cosmic chamber that waits for a specific pattern to land — currently <span className="text-rose-300 font-mono font-bold">P5 = 50</span>. Inside, the DJ drops <span className="text-amber-300">resonators</span> (suspect numbers like 10, 27, 32) and the engine weaves <span className="text-white font-medium">5 auto-generated symphonies</span> every draw, re-tuning itself until the alignment arrives 🎻.</p>
                  <p className="mt-1 text-slate-400 text-xs">Each symphony rides a different archetype: All-Cosmos Fill · Mirror Orbit · Starlight Harmonics · Silent Nebula · Meridian Bridge. Hunt Box tickets are FREE and don't count against your 20.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🎻 Two Generator Modes</h3>
                  <p><span className="text-white font-medium">Dreaming Mode</span> — Reaches for the full cosmos. All alignments, all frequencies, maximum coverage.</p>
                  <p><span className="text-white font-medium">Money Mode</span> — Focused on hitting 3+ numbers. The stars whisper which combinations have the strongest resonance.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🎫 Multiple Tickets</h3>
                  <p>Open the ticket selector to generate <span className="text-amber-400 font-semibold">2 to 20 tickets</span> at once. Each ticket carries a different cosmic frequency — some riding gravity-pull tides, some reaching for distant orbits, some singing cycle-close symmetries.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🌠 Celestial Radar</h3>
                  <p>Numbers travel through cosmic orbits — some close to Earth, others in <span className="text-red-400">deep orbit</span> near distant galaxies. The Radar shows which numbers are <span className="text-amber-400">approaching our orbit</span>. When a planet aligns with a silent voice, the music surfaces.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🎧 Hit Tracker + Draw-to-Draw Pulse</h3>
                  <p>Every ticket is saved and compared against real results. The Hit Tracker shows your strongest tickets from the last 3 draws — green balls = hits. The Pulse panel shows per-draw generation counts, hit rates, and the best ticket shape from each draw's winners.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🎻 Jack Box (your own calls)</h3>
                  <p>Inside the sidebar you'll find the DJ's Jack Box — your silent-voices list for the next 3 songs, your P1/P2 locks, triple-locks, and deep-orbit picks. The engine listens to these and bends its symphonies to honour your ears.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🔬 Live Frequencies (Diagnostics)</h3>
                  <p>A narrative panel that transcribes the current cosmic weather — gravity-pull active, storm cycle, ascending chords, deep-orbit echoes, starlight harmonics. Every symphony is built on these frequencies.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🌌 Foldable Cosmos Sidebar</h3>
                  <p>The entire left sidebar (Top 10 · Live Frequencies · Crown Cosmos · Jack Box · Archive) can fold into a slim strip with the <span className="text-amber-300">◂</span> button — one click to give the stage full width, another to bring the cosmos back. Your choice is remembered across sessions.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🎼 The Engine Behind the Music</h3>
                  <p>Lucky Jack listens to 20+ cosmic frequencies live: Starlight Harmonics, Ascending Chords, Cosmic Loops, Silent-String Yearning, Twin-Echo Reflections, Running Tides, Cross-Constellation Bridges, Storm Closing Ceremony, Date Resonances, Orbital Translations, Sibling Camps… every number ranked by how many lenses ring on it at once.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🎫 Where to start (Free)</h3>
                  <p>Open the <span className="text-amber-200 font-semibold">Pending Tickets</span> panel — every draw, the engine drops a fresh batch of cosmic-tuned picks. Browse them, learn the patterns, and use them as inspiration to choose your own lottery numbers 🍀.</p>
                  <p className="mt-1">Also free: the <span className="text-white font-medium">Top Predicted Numbers</span> for the upcoming draw + the <span className="text-white font-medium">Hit Tracker</span> to see how E performed on past draws.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🎻 Deep listening tools (Reserved)</h3>
                  <p>The deeper tuning chambers — <span className="text-white font-medium">E's Cosmic Brain · Cosmic Voices · Ghost Ledger · Ghost Engine · Cosmic Replay · Swiss Brain</span> — are reserved today. They will open in the future. For now, the Pending Tickets carry their wisdom into the picks you can play with.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">🍀 Tips</h3>
                  <ul className="list-disc list-inside space-y-1 text-slate-400">
                    <li>Generate at least 10 tickets for broad coverage — the cosmos rewards diversity</li>
                    <li>Drop resonators into the Crown Cosmos when you hear a specific number calling</li>
                    <li>Check the Live Frequencies panel — if <span className="text-rose-300">gravity-pull</span> is active, play low P1s</li>
                    <li>Watch the Hit Tracker Pulse — learn which archetypes sing loudest for YOU</li>
                    <li>Play responsibly — the stars guide, but never guarantee 🎧</li>
                  </ul>
                </div>
              </div>
              
              <button 
                onClick={() => setShowGuide(false)}
                className="mt-5 w-full bg-amber-500 hover:bg-amber-400 text-black font-bold py-2 rounded-lg transition-colors"
                data-testid="guide-close"
              >
                Ya man — let's play 🎻🍀
              </button>
            </div>
          </div>
        )}

        {/* Disclaimer Modal */}
        {showDisclaimer && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4" data-testid="disclaimer-modal">
            <div className="bg-slate-800 border border-slate-600 rounded-xl max-w-lg w-full p-6 max-h-[80vh] overflow-y-auto">
              <h2 className="text-xl font-bold text-amber-400 mb-4">Disclaimer & Terms of Use</h2>
              
              <div className="text-slate-300 text-sm space-y-3">
                <p className="font-semibold text-white">Lucky Jack is an entertainment platform.</p>
                
                <p>This application helps you choose lottery numbers using mathematical pattern analysis, historical data, and digit-based algorithms. It is designed purely for entertainment and convenience purposes.</p>
                
                <p className="font-semibold text-amber-300">No Guarantee of Winning</p>
                <p>Lottery draws are celestial events influenced by the cosmic dance of the seven planets. Lucky Jack reads the music of the universe to suggest your numbers. All generated numbers are inspired by stellar harmonics and planetary alignments. Play responsibly.</p>
                
                <p className="font-semibold text-amber-300">Play Responsibly</p>
                <p>Only spend what you can afford to lose. If you feel that gambling is becoming a problem, please seek help. Lucky Jack is not a gambling platform — it is a number selection tool.</p>
                
                <p className="font-semibold text-amber-300">Data & Privacy</p>
                <p>Lucky Jack uses publicly available lottery draw history. No personal data is collected or stored. Generated tickets are stored locally for hit tracking purposes only.</p>
                
                <p className="font-semibold text-amber-300">Accuracy</p>
                <p>While we strive to maintain accurate historical data, we cannot guarantee the completeness or accuracy of all lottery results. Always verify your tickets against official lottery sources.</p>
                
                <p className="text-slate-400 text-xs mt-4">By using Lucky Jack, you acknowledge that this is an entertainment tool and accept these terms.</p>
              </div>
              
              <button 
                onClick={() => setShowDisclaimer(false)}
                className="mt-5 w-full bg-amber-500 hover:bg-amber-400 text-black font-bold py-2 rounded-lg transition-colors"
                data-testid="disclaimer-close"
              >
                I Understand
              </button>
            </div>
          </div>
        )}
      </main>

        {/* ACTIVE USERS — Right side */}
        <div className="hidden lg:block w-40 flex-shrink-0" data-testid="active-users-panel">
          <div className="sticky top-4 lucky-card p-2.5 border border-emerald-500/20">
            <div className="flex items-center gap-1.5 mb-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-emerald-400 font-semibold text-xs">Live Users</span>
            </div>
            <div className="text-center py-3">
              <div className="text-emerald-400 text-3xl font-mono font-black" data-testid="active-user-count">{activeUsers}</div>
              <div className="text-slate-500 text-[9px] mt-1">currently online</div>
            </div>
            <div className="border-t border-slate-700/30 pt-2 mt-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-500 text-[9px]">All-time users</span>
                <span className="text-slate-300 text-xs font-mono font-bold" data-testid="total-user-count">{totalUsers}</span>
              </div>
            </div>
          </div>
        </div>

      </div> {/* Close flex wrapper */}
    </div>
  );
}

export default App;
