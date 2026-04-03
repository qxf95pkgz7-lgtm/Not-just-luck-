import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Sparkles, RefreshCw, ChevronDown, ChevronUp, Gift, Star, Globe } from "lucide-react";

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
  
  // Saved names for quick selection
  const savedNames = [
    { name: "Patrick Pulfer", birthday: "16/06/1977" },
    { name: "Samantha Pulfer", birthday: "04/01/1978" },
    { name: "Jack Pulfer", birthday: "27/08/2015" }
  ];
  const [numTickets, setNumTickets] = useState(1);
  const [oliviaKiss, setOliviaKiss] = useState(false);
  const [showKissHearts, setShowKissHearts] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateMessage, setUpdateMessage] = useState('');

  // Olivia's Kiss of Luck function
  const giveKissOfLuck = () => {
    setOliviaKiss(true);
    setShowKissHearts(true);
    
    // Play "Ya man" sound
    const utterance = new SpeechSynthesisUtterance("Ya man!");
    utterance.rate = 0.8;
    utterance.pitch = 0.7;
    speechSynthesis.speak(utterance);
    
    // Reset after animation
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

  const fetchPrediction = useCallback(async () => {
    try {
      setLoading(true);
      setWheelSpinning(false);
      
      const apiBase = lotteryMode === 'swiss' ? `${API}/master-predictor` : `${API}/euromillions/master-predictor`;
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
      if (params.length > 0) url += `?${params.join('&')}`;
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // EuroMillions uses POST, Swiss Lotto uses GET
      const res = lotteryMode === 'euro' 
        ? await axios.post(apiBase, {
            birthday: birthday || null,
            name: fullName || null,
            locked_positions: Object.fromEntries(Object.entries(lockedPositions).filter(([k,v]) => v !== "" && (k !== 'p6' || lotteryMode === 'swiss')).map(([k,v]) => [k, parseInt(v)])),
            num_tickets: numTickets
          })
        : await axios.get(url);
      
      // Transform EuroMillions response format
      if (lotteryMode === 'euro' && res.data.tickets) {
        const mainTicket = res.data.tickets[0];
        const transformed = {
          main_prediction: mainTicket.numbers,
          stars_prediction: mainTicket.stars,
          average_confidence: Math.round(mainTicket.confidence * 100),
          alternate_numbers: res.data.tickets.length > 1 ? res.data.tickets[1].numbers : [3, 11, 19, 27, 33],
          all_tickets: res.data.tickets.map((t, i) => ({
            ticket_num: i + 1,
            numbers: t.numbers,
            stars: t.stars,
            confidence: Math.round(t.confidence * 100)
          }))
        };
        setPrediction(transformed);
      } else {
        setPrediction(res.data);
      }
      
      const ballCount = lotteryMode === 'swiss' ? 6 : 5;
      setTimeout(() => setWheelSpinning(true), ballCount * 2000);
    } catch (e) {
      console.error("Error:", e);
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
  }, [birthday, fullName, lockedPositions, numTickets, lotteryMode]);

  const fetchStats = useCallback(async () => {
    try {
      const endpoint = lotteryMode === 'swiss' ? `${API}/dashboard` : `${API}/euromillions/stats`;
      const res = await axios.get(endpoint);
      setStats(res.data);
    } catch (e) {
      console.error("Error:", e);
    }
  }, [lotteryMode]);

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
              confidence: Math.round(t.confidence * 100)
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
  }, [lotteryMode]);

  return (
    <div className="min-h-screen pb-10">
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

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4">
        <div className="lucky-card p-6 mb-6" style={lotteryMode === 'euro' ? { background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.98) 100%)', borderColor: 'rgba(59,130,246,0.3)' } : {}}>
          <h2 className="text-lg font-semibold text-center text-slate-200 mb-6">
            Your Lucky Numbers
          </h2>
          
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
          
          {/* Status */}
          <div className="text-center mt-6 mb-4">
            {!loading && !prediction && (
              <p className="text-slate-400 text-sm">Press the button to generate your lucky numbers</p>
            )}
            {prediction && !loading && (
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm border ${
                lotteryMode === 'swiss' 
                  ? 'bg-gradient-to-r from-emerald-900/30 to-emerald-800/30 border-emerald-500/20' 
                  : 'bg-gradient-to-r from-blue-900/30 to-blue-800/30 border-blue-500/20'
              }`}>
                <span className={lotteryMode === 'swiss' ? 'text-emerald-400' : 'text-blue-400'}>✓</span>
                <span className={`font-medium ${lotteryMode === 'swiss' ? 'text-emerald-300' : 'text-blue-300'}`}>Numbers generated</span>
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
                className={`px-6 py-2 rounded-full font-bold text-sm transition-all duration-300 ${
                  oliviaKiss 
                    ? 'bg-gradient-to-r from-pink-500 to-red-500 text-white scale-110 shadow-lg shadow-pink-500/50' 
                    : 'bg-gradient-to-r from-pink-600/30 to-red-600/30 text-pink-300 hover:from-pink-500/50 hover:to-red-500/50 border border-pink-500/30'
                }`}
                data-testid="olivia-kiss-btn"
              >
                💋 Olivia's Kiss of Luck 💋
              </button>
              
              {/* Flying Hearts Animation */}
              {showKissHearts && (
                <div className="absolute inset-0 pointer-events-none overflow-visible">
                  {[...Array(8)].map((_, i) => (
                    <span
                      key={i}
                      className="absolute text-2xl animate-ping"
                      style={{
                        left: `${20 + Math.random() * 60}%`,
                        top: `${Math.random() * 100}%`,
                        animationDelay: `${i * 0.1}s`,
                        animationDuration: '1s'
                      }}
                    >
                      {['💋', '❤️', '💕', '💗'][i % 4]}
                    </span>
                  ))}
                </div>
              )}
            </div>
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
              {/* Quick Select Names */}
              <div>
                <label className="text-xs text-slate-400 mb-2 block">Quick Select</label>
                <div className="flex flex-wrap gap-2">
                  {savedNames.map((person, idx) => (
                    <button
                      key={idx}
                      onClick={() => { setFullName(person.name); setBirthday(person.birthday); }}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                        fullName === person.name 
                          ? lotteryMode === 'swiss' 
                            ? 'bg-amber-500 text-gray-900' 
                            : 'bg-blue-500 text-white'
                          : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600'
                      }`}
                      data-testid={`quick-name-${idx}`}
                    >
                      {person.name.split(' ')[0]}
                    </button>
                  ))}
                </div>
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
                disabled={loading || !birthday}
                className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all duration-300 ${
                  birthday 
                    ? lotteryMode === 'swiss'
                      ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-gray-900 hover:from-amber-400 hover:to-amber-500 shadow-lg'
                      : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-400 hover:to-blue-500 shadow-lg'
                    : 'bg-slate-700 text-slate-400 cursor-not-allowed'
                }`}
                data-testid="birthday-generate-btn"
              >
                {loading ? <><Sparkles className="w-5 h-5 animate-spin" /><span>Generating...</span></> : <><Sparkles className="w-5 h-5" /><span>Generate with Birthday</span></>}
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
                Generate multiple ticket predictions ranked by confidence. <span className={lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400'}>{lotteryMode === 'swiss' ? '3.50 CHF' : '3.50 fr'} per ticket</span>
              </p>
              
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm text-slate-300">How many tickets?</span>
                  <span className={`text-xs font-semibold ${lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400'}`}>
                    Total: {(numTickets * 3.5).toFixed(2)} fr
                  </span>
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {[1, 3, 5, 8, 10, 15, 20].map(n => (
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
                        {(n * 3.5).toFixed(1)}
                      </span>
                    </button>
                  ))}
                </div>
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
                      <div className="flex gap-1.5 flex-1">
                        {ticket.numbers.map((num, i) => (
                          <Ball key={i} number={num} size="xs" maxNum={maxNum} />
                        ))}
                        {lotteryMode === 'euro' && ticket.stars && ticket.stars.map((star, i) => (
                          <StarBall key={`star-${i}`} number={star} size="xs" />
                        ))}
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
                className="mt-4 w-full py-2.5 rounded-xl font-bold flex items-center justify-center gap-2 transition-all duration-300 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white hover:from-emerald-400 hover:to-emerald-500 shadow-lg disabled:opacity-50"
                data-testid="generate-tickets-btn"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                {loading ? 'Generating...' : `🎫 Generate ${numTickets} Ticket${numTickets > 1 ? 's' : ''}`}
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
              <span className="text-slate-400 text-xs">Based on </span>
              <span className={`font-bold text-sm ${lotteryMode === 'swiss' ? 'text-amber-400' : 'text-blue-400'}`}>
                {stats.total_draws || stats.total || 0}
              </span>
              <span className="text-slate-400 text-xs"> historical draws</span>
              
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

        {/* Footer */}
        <div className="text-center text-slate-500 text-xs mt-6 pb-4">
          <p>Good luck! Play responsibly.</p>
        </div>
      </main>
    </div>
  );
}

export default App;
