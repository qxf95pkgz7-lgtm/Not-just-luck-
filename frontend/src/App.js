import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Sparkles, RefreshCw, ChevronDown, ChevronUp, Gift, Star, Globe, History, Trash2, Target, TrendingUp, CheckCircle2, XCircle, Clock, Zap, Eye } from "lucide-react";

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

// EuroMillions Star Ball - Gold star design
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
  const [nextDrawTickets, setNextDrawTickets] = useState(0);
  const [nextDrawDate, setNextDrawDate] = useState('');
  const [pendingTickets, setPendingTickets] = useState([]);
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
  
  // Sleeper Radar State
  const [showSleeperRadar, setShowSleeperRadar] = useState(false);
  const [sleeperData, setSleeperData] = useState(null);
  const [sleeperLoading, setSleeperLoading] = useState(false);
  
  // Swiss Sleeper State
  const [showSwissSleepers, setShowSwissSleepers] = useState(false);
  const [swissSleeperData, setSwissSleeperData] = useState(null);
  const [swissSleeperLoading, setSwissSleeperLoading] = useState(false);
  
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
        const res = await axios.get(`${API}/euromillions/generation-history?limit=30`);
        setGenerationHistory(res.data.generations || []);
      } else {
        // Use the new clean hit-tracker endpoint for Swiss
        const res = await axios.get(`${API}/hit-tracker?last_draws=3`);
        setGenerationHistory(res.data.results || []);
        setLastDraw(res.data.last_draws?.[0] || null);
      }
    } catch (e) {
      console.error("Error fetching generation history:", e);
    } finally {
      setHitTrackerLoading(false);
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
  
  // Load hit tracker data when section is opened
  useEffect(() => {
    if (showHitTracker) {
      fetchLastDraw();
      fetchGenerationHistory();
      fetchHitStats();
    }
  }, [showHitTracker, lotteryMode]);
  
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
  useEffect(() => {
    if (showSleeperRadar && lotteryMode === 'euro') {
      fetchSleeperForecast();
    }
  }, [showSleeperRadar, lotteryMode]);

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
  }, [showSwissSleepers, lotteryMode]);
  
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
      const res = await axios.get(`${API}/pending-tickets?mode=${lotteryMode}`);
      setPendingTickets(res.data.tickets || []);
      setNextDrawDate(res.data.next_date || '');
    } catch (e) {}
  };
  useEffect(() => { fetchTicketCounter(); fetchPendingTickets(); }, [lotteryMode]);

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
        alert(e.response.data?.detail || "Ticket limit reached! Maximum 20 tickets per draw.");
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

      {/* LAST DRAW DISPLAY - Always Visible */}
      {lastDraw && (
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
        {/* PENDING TICKETS BOX — Left side */}
        <div className="hidden lg:block w-72 flex-shrink-0" data-testid="pending-tickets-panel">
          <div className="sticky top-4 lucky-card p-3 border border-amber-500/20">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-amber-400 font-semibold text-xs">Pending Tickets</span>
              <span className="text-emerald-400 font-mono font-bold text-sm">{pendingTickets.length}</span>
            </div>
            <div className="text-slate-500 text-[9px] mb-2">For draw: {nextDrawDate}</div>
            <div className="space-y-1.5 max-h-[70vh] overflow-y-auto">
              {pendingTickets.length === 0 ? (
                <div className="text-center text-slate-600 text-[10px] py-3">
                  No tickets yet
                </div>
              ) : pendingTickets.map((t, idx) => (
                <div key={idx} className="p-1.5 rounded-md bg-slate-800/50 border border-slate-700/30">
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
                </div>
              ))}
            </div>
            {pendingTickets.length > 0 && (
              <div className="mt-1.5 pt-1.5 border-t border-slate-700/30 text-center">
                <span className="text-slate-500 text-[9px]">{pendingTickets.length} tickets ready</span>
              </div>
            )}
          </div>
        </div>

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
            <span className="text-emerald-400 font-mono font-bold">{pendingTickets.length}</span>
          </button>
          <div className="p-2 rounded-lg bg-slate-800/60 border border-emerald-500/20 flex items-center gap-2">
            <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span></span>
            <span className="text-emerald-400 font-mono font-bold">{activeUsers}</span>
            <span className="text-slate-500 text-[10px]">online</span>
          </div>
        </div>
        <div className="lg:hidden mb-3">
          <div id="mobile-pending" className="hidden mt-2 space-y-1.5 max-h-64 overflow-y-auto">
            {pendingTickets.map((t, idx) => (
              <div key={idx} className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/30">
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
              </div>
            ))}
          </div>
        </div>
        {/* Ticket Limit Notice */}
        <div className="mb-3 px-3 py-2 rounded-lg bg-slate-800/40 border border-slate-700/40 flex items-center justify-center gap-2" data-testid="ticket-limit-notice">
          <span className="text-slate-500 text-xs">You can generate up to <span className="text-amber-400 font-semibold">20 tickets</span> per {lotteryMode === 'swiss' ? 'Swiss Lotto' : 'EuroMillions'} draw</span>
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
              disabled={loading}
              className="lucky-btn flex items-center gap-2 mx-auto"
              style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)', color: '#fbbf24' } : {}}
              data-testid="generate-btn"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              {loading ? '🤞 Finding Lucky Numbers...' : lotteryMode === 'swiss' ? '🍀 Get New Numbers 🍀' : '⭐ Get New Numbers ⭐'}
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
        {lotteryMode === 'swiss' && (
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

        {/* SLEEPER RADAR - EuroMillions Only */}
        {lotteryMode === 'euro' && (
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
                              <div className="flex items-center gap-2 mt-0.5">
                                <span className="text-[10px] text-slate-500">
                                  {s.overdue >= 1.0 ? `${s.overdue.toFixed(1)}x distant` : `orbit ${s.gap}`}
                                </span>
                                {s.tease_score >= 3 && (
                                  <span className="text-[10px] px-1 rounded bg-purple-500/20 text-purple-300">VENUS ALIGNED</span>
                                )}
                                {s.circle_boost > 1.5 && (
                                  <span className="text-[10px] px-1 rounded bg-indigo-500/20 text-indigo-300">SATURN RING</span>
                                )}
                                {s.overdue >= 3.0 && (
                                  <span className="text-[10px] px-1 rounded bg-red-500/20 text-red-300">MARS RETURN</span>
                                )}
                              </div>
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

        {/* 2CHANCE - Swiss Second Chance Draw (EuroMillions only) */}
        {lotteryMode === 'euro' && (
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

        {/* HIT TRACKER SECTION - Story Generator History & Hits */}
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
                            {r.hit_count >= 4 ? '💰' : r.hit_count >= 3 ? '🔥' : '✓'} For: <span className="text-slate-200 font-semibold">{r.target_date}</span>
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
                        <div className="text-[10px] text-slate-500 mt-1">
                          Actual: {r.actual_numbers?.join(', ')} L={r.actual_lucky}
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
              <h2 className="text-xl font-bold text-amber-400 mb-4">How to Use Lucky Jack</h2>
              
              <div className="text-slate-300 text-sm space-y-4">
                <p className="text-white font-semibold">Lucky Jack reads the rhythm of the stars to help you pick your lottery numbers.</p>
                
                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">Two Lotteries</h3>
                  <p>Switch between <span className="text-white font-medium">Swiss Lotto</span> (6 numbers 1-42 + Lucky) and <span className="text-white font-medium">EuroMillions</span> (5 numbers 1-50 + 2 Stars) using the toggle at the top.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">Two Modes</h3>
                  <p><span className="text-white font-medium">Jackpot Mode</span> — Uses all celestial alignments for maximum coverage.</p>
                  <p><span className="text-white font-medium">Money Mode</span> — Focused on hitting 3+ numbers. The stars whisper which combinations have the strongest resonance. Generates multiple tickets with different energies: Core, Spread, and Crazy.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">Multiple Tickets</h3>
                  <p>Open the ticket selector to generate 2 to 20 tickets at once. Swiss Lotto starts at 2 tickets (5 CHF). Each ticket carries a different cosmic frequency — some are grounded, some reach for the high stars.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">Celestial Radar</h3>
                  <p>Numbers travel through cosmic orbits — some are close to Earth, others are in <span className="text-red-400">deep orbit</span> near distant galaxies. The Celestial Radar shows you which numbers are <span className="text-amber-400">approaching our orbit</span> (about to appear). When a planet aligns with these numbers, magic happens.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">Hit Tracker</h3>
                  <p>Every ticket you generate is saved and compared against actual draw results. The Hit Tracker shows your best tickets from the last 3 draws — only tickets with 2 or more correct numbers appear. Green balls = hits!</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">The Engine</h3>
                  <p>Behind the scenes, Lucky Jack listens to the music of the universe. The numbers follow celestial orbits, cosmic bridges between the seven planets, and rhythmic cycles that echo from Mercury to Neptune. Our engine reads these stellar harmonics and translates them into your tickets.</p>
                  <p className="text-slate-400 text-xs mt-1">Patterns include: Celestial DNA resonance, Star bridge connections, Cosmic rhythm cycles, Sleeper energy waves, and Cross-constellation harmonics.</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">Ticket Counters</h3>
                  <p>At the top you can see how many tickets have been generated in total, and how many are lined up for the next draw. The universe is listening!</p>
                </div>

                <div>
                  <h3 className="text-amber-300 font-semibold mb-1">Tips</h3>
                  <ul className="list-disc list-inside space-y-1 text-slate-400">
                    <li>Generate at least 10 tickets for best coverage</li>
                    <li>Check the Celestial Radar before playing — numbers in deep orbit carry powerful energy from Andromeda</li>
                    <li>The Crazy tickets reach where others don't — sometimes the stars surprise us</li>
                    <li>Use the Hit Tracker to learn which cosmic frequencies work best for you</li>
                    <li>Play responsibly — the stars guide, but never guarantee</li>
                  </ul>
                </div>
              </div>
              
              <button 
                onClick={() => setShowGuide(false)}
                className="mt-5 w-full bg-amber-500 hover:bg-amber-400 text-black font-bold py-2 rounded-lg transition-colors"
                data-testid="guide-close"
              >
                Got it!
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
