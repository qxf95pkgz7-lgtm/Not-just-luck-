import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Sparkles, RefreshCw, ChevronDown, ChevronUp, Gift, Lock } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Realistic Ball Component - white with colored stripe
const Ball = ({ number, size = "sm", isWinner = false, isSpinning = false, delay = 0, style = {} }) => {
  // Ball stripe colors based on number ranges (like real lottery)
  const getStripeColor = (num) => {
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
      {/* Colored stripe band */}
      <div 
        className={`absolute inset-x-0 top-1/2 -translate-y-1/2 ${config.stripe} flex items-center justify-center overflow-hidden`}
        style={{ 
          background: `linear-gradient(180deg, ${stripeColor} 0%, ${stripeColor}dd 100%)`,
          boxShadow: 'inset 0 1px 2px rgba(255,255,255,0.3), inset 0 -1px 2px rgba(0,0,0,0.2)'
        }}
      >
        <span 
          className={`font-black text-white ${config.text}`}
          style={{ 
            textShadow: '0 1px 2px rgba(0,0,0,0.5)',
            letterSpacing: '-0.5px'
          }}
        >
          {number}
        </span>
      </div>
      
      {/* Top shine */}
      <div 
        className="absolute top-[8%] left-[18%] w-[30%] h-[25%] rounded-full"
        style={{
          background: 'radial-gradient(ellipse, rgba(255,255,255,0.95) 0%, transparent 70%)'
        }}
      />
    </div>
  );
};

// Lucky Number Wheel - spins like a car wheel viewed from front - COMPACT
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
      
      setTimeout(() => {
        setSettled(true);
        if (onComplete) onComplete();
      }, 3500);
    }
  }, [isSpinning, luckyNumber, onComplete]);

  useEffect(() => {
    if (!isSpinning && !settled) {
      setRotation(0);
    }
  }, [isSpinning, settled]);

  return (
    <div className="flex flex-col items-center">
      <div className="text-xs font-semibold text-amber-400 mb-1">⭐ Lucky</div>
      
      {/* Wheel container - SMALLER */}
      <div className="relative w-20 h-20">
        {/* Pointer */}
        <div 
          className="absolute -top-2 left-1/2 -translate-x-1/2 z-20"
          style={{
            width: 0,
            height: 0,
            borderLeft: '7px solid transparent',
            borderRight: '7px solid transparent',
            borderTop: '10px solid #d4af37',
            filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.4))'
          }}
        />
        
        {/* Outer ring */}
        <div 
          className="absolute inset-0 rounded-full"
          style={{
            background: 'linear-gradient(180deg, #4a4a5a 0%, #2a2a35 50%, #3a3a45 100%)',
            boxShadow: '0 4px 15px rgba(0,0,0,0.5), inset 0 1px 3px rgba(255,255,255,0.1)'
          }}
        />
        
        {/* Spinning wheel */}
        <div 
          className="absolute inset-[6px] rounded-full overflow-hidden"
          style={{
            background: 'conic-gradient(from 0deg, #1e293b 0deg, #334155 60deg, #1e293b 60deg, #334155 120deg, #1e293b 120deg, #334155 180deg, #1e293b 180deg, #334155 240deg, #1e293b 240deg, #334155 300deg, #1e293b 300deg, #334155 360deg)',
            transform: `rotate(${rotation}deg)`,
            transition: isSpinning ? 'transform 3.5s cubic-bezier(0.12, 0.8, 0.2, 1)' : 'none',
            boxShadow: 'inset 0 0 20px rgba(0,0,0,0.5)'
          }}
        >
          {/* Numbers */}
          {numbers.map((num, i) => {
            const angle = i * 60;
            const isWinner = settled && num === luckyNumber;
            return (
              <div
                key={num}
                className="absolute"
                style={{
                  left: '50%',
                  top: '50%',
                  transform: `translate(-50%, -50%) rotate(${angle}deg) translateY(-24px)`,
                }}
              >
                <div 
                  className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-500 ${
                    isWinner ? 'scale-110' : ''
                  }`}
                  style={{
                    background: isWinner 
                      ? 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)'
                      : 'linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%)',
                    color: isWinner ? '#1a1a24' : '#1e293b',
                    boxShadow: isWinner 
                      ? '0 0 12px rgba(251,191,36,0.9)'
                      : '0 1px 4px rgba(0,0,0,0.3)',
                    transform: `rotate(-${angle + rotation}deg)`,
                    transition: isSpinning ? 'transform 3.5s cubic-bezier(0.12, 0.8, 0.2, 1)' : 'none'
                  }}
                >
                  {num}
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Center hub */}
        <div 
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-5 rounded-full z-10"
          style={{
            background: 'linear-gradient(145deg, #d4af37 0%, #b8860b 100%)',
            boxShadow: '0 2px 6px rgba(0,0,0,0.4)'
          }}
        >
          <div 
            className="absolute inset-1 rounded-full"
            style={{
              background: 'linear-gradient(145deg, #3a3a45 0%, #2a2a35 100%)',
            }}
          />
        </div>
        
        {/* Glow */}
        {settled && (
          <div 
            className="absolute inset-0 rounded-full pointer-events-none animate-pulse"
            style={{
              boxShadow: '0 0 25px rgba(251,191,36,0.5)'
            }}
          />
        )}
      </div>
      
      {/* Result */}
      <div className={`mt-1 text-center transition-all duration-500 ${settled ? 'opacity-100' : 'opacity-0'}`}>
        <span className="text-xl font-black text-amber-400" style={{ textShadow: '0 0 8px rgba(251,191,36,0.5)' }}>
          {luckyNumber}
        </span>
      </div>
    </div>
  );
};


// Realistic Lottery Ball Machine with Tube Selection
const BallMachine = ({ isProcessing, winningNumbers }) => {
  const [balls, setBalls] = useState([]);
  const [phase, setPhase] = useState('idle'); // idle, spinning, selecting, complete, resetting
  const [selectedBalls, setSelectedBalls] = useState([]);
  const [currentCatch, setCurrentCatch] = useState(null); // Ball currently caught in tube
  const [selectionIndex, setSelectionIndex] = useState(0);
  const [catchPhase, setCatchPhase] = useState('none'); // none, catching, rolling, revealed
  const [hasInitialized, setHasInitialized] = useState(false);
  const [fallingBalls, setFallingBalls] = useState([]); // Balls falling back into dome
  
  const GRAVITY = 0.18;  // Strong gravity - balls WANT to fall
  const FRICTION = 0.98;
  const BOUNCE = 0.75;

  // Initialize all 42 balls - scattered for more interesting start
  useEffect(() => {
    const allBalls = Array.from({ length: 42 }, (_, i) => ({
      number: i + 1,
      x: 15 + (i % 7) * 10 + Math.random() * 5,
      y: 55 + Math.floor(i / 7) * 6 + Math.random() * 3,
      vx: (Math.random() - 0.5) * 0.5,
      vy: 0,
      captured: false
    }));
    setBalls(allBalls);
    setHasInitialized(true);
  }, []);

  // Handle processing phases
  useEffect(() => {
    if (isProcessing && (phase === 'idle' || phase === 'complete')) {
      // Starting new spin
      setPhase('spinning');
      setSelectedBalls([]);
      setSelectionIndex(0);
      setCurrentCatch(null);
      setCatchPhase('none');
      setBalls(prev => prev.map(b => ({ ...b, captured: false })));
    } else if (!isProcessing && phase === 'spinning' && winningNumbers.length > 0) {
      // After 2 seconds of spinning, start catching balls one by one
      const delay = setTimeout(() => {
        setPhase('selecting');
      }, 2000);
      return () => clearTimeout(delay);
    }
  }, [isProcessing, winningNumbers, phase]);

  // Ball catching sequence - one at a time with dramatic tube animation
  useEffect(() => {
    if (phase === 'selecting' && selectionIndex < winningNumbers.length && catchPhase === 'none') {
      const ballNumber = winningNumbers[selectionIndex];
      
      // Phase 1: Ball gets CAUGHT by the stopper
      setCatchPhase('catching');
      setCurrentCatch(ballNumber);
      
      // Mark ball as captured (disappears from floating)
      setBalls(prev => prev.map(b => 
        b.number === ballNumber ? { ...b, captured: true } : b
      ));
      
      // Phase 2: After 0.6s, ball ROLLS through tube
      setTimeout(() => {
        setCatchPhase('rolling');
      }, 600);
      
      // Phase 3: After 1.2s total, number is REVEALED
      setTimeout(() => {
        setCatchPhase('revealed');
        setSelectedBalls(prev => [...prev, ballNumber]);
      }, 1200);
      
      // Phase 4: After 1.8s, ready for next ball
      setTimeout(() => {
        setCatchPhase('none');
        setCurrentCatch(null);
        setSelectionIndex(prev => prev + 1);
      }, 1800);
    } else if (phase === 'selecting' && selectionIndex >= winningNumbers.length && catchPhase === 'none') {
      // All done! Start the falling back animation after 3 seconds
      setPhase('complete');
      
      // After 3 seconds, start dropping balls back into dome
      setTimeout(() => {
        setPhase('resetting');
        // Drop balls one by one with staggered timing
        winningNumbers.forEach((ballNum, idx) => {
          setTimeout(() => {
            setFallingBalls(prev => [...prev, ballNum]);
            // After ball finishes falling, mark it as not captured
            setTimeout(() => {
              setBalls(prev => prev.map(b => 
                b.number === ballNum ? { 
                  ...b, 
                  captured: false,
                  x: 30 + Math.random() * 40,
                  y: 20 + Math.random() * 10,
                  vy: 2 + Math.random() * 2,
                  vx: (Math.random() - 0.5) * 2
                } : b
              ));
              setFallingBalls(prev => prev.filter(n => n !== ballNum));
            }, 800);
          }, idx * 300); // Stagger each ball by 300ms
        });
        
        // After all balls have fallen, reset to idle
        setTimeout(() => {
          setPhase('idle');
          setSelectedBalls([]);
        }, winningNumbers.length * 300 + 1000);
      }, 3000);
    }
  }, [phase, selectionIndex, winningNumbers, catchPhase]);

  // Show initial results on first load only (not on re-render)
  useEffect(() => {
    if (hasInitialized && winningNumbers.length > 0 && phase === 'idle' && selectedBalls.length === 0) {
      // Show initial results immediately without animation
      setSelectedBalls(winningNumbers);
      setPhase('complete');
    }
  }, [hasInitialized, winningNumbers, phase, selectedBalls.length]);

  // Physics loop - GRAVITY vs AIR JETS battle!
  useEffect(() => {
    const interval = setInterval(() => {
      setBalls(prev => prev.map(ball => {
        if (ball.captured) return ball;
        
        let vx = ball.vx;
        let vy = ball.vy;
        
        // GRAVITY always pulls down
        vy += GRAVITY;
        
        const isSpinning = phase === 'spinning' || phase === 'selecting';
        
        // AIR JETS - always on but stronger during spin!
        if (isSpinning) {
          // INTENSE air during spin
          vy -= 0.6;
          if (ball.y > 50) {
            vy -= 1.4 + Math.random() * 0.6;
          } else if (ball.y > 30) {
            vy -= 0.5;
          }
          vx += (Math.random() - 0.5) * 2.5;
          vy += (Math.random() - 0.5) * 1.8;
          if (Math.random() < 0.1) {
            vy -= 3 + Math.random() * 2;
            vx += (Math.random() - 0.5) * 3;
          }
        } else {
          // GENTLE floating when idle/complete - balls still move!
          vy -= 0.25;
          if (ball.y > 60) {
            vy -= 0.4 + Math.random() * 0.3;
          }
          vx += (Math.random() - 0.5) * 0.8;
          vy += (Math.random() - 0.5) * 0.5;
          if (Math.random() < 0.03) {
            vy -= 1.5;
          }
        }
        
        vx *= FRICTION;
        vy *= FRICTION;
        
        const maxV = isSpinning ? 7 : 3;
        vx = Math.max(-maxV, Math.min(maxV, vx));
        vy = Math.max(-maxV, Math.min(maxV, vy));
        
        let x = ball.x + vx;
        let y = ball.y + vy;
        
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
      {/* Machine Container - COMPACT */}
      <div className="relative mb-4">
        {/* Machine Frame */}
        <div 
          className="relative w-[280px] h-[260px] rounded-[32px] p-2"
          style={{
            background: 'linear-gradient(180deg, #2d2d3a 0%, #1a1a24 100%)',
            boxShadow: '0 15px 40px rgba(0,0,0,0.5), inset 0 2px 1px rgba(255,255,255,0.1)'
          }}
        >
          {/* Inner Glass Container */}
          <div 
            className="relative w-full h-full rounded-[26px] overflow-hidden"
            style={{
              background: 'linear-gradient(180deg, rgba(20,25,40,0.95) 0%, rgba(10,15,25,0.98) 100%)',
              boxShadow: 'inset 0 0 50px rgba(0,0,0,0.5), inset 0 -15px 30px rgba(0,0,0,0.3)'
            }}
          >
            {/* Glass reflection */}
            <div 
              className="absolute inset-0 pointer-events-none rounded-[26px]"
              style={{
                background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 40%)'
              }}
            />
            
            {/* === TUBE - Smaller === */}
            <div className="absolute right-0 top-[15%] w-14 h-[65%] z-30">
              {/* Funnel */}
              <div 
                className="absolute right-1 top-0 w-10 h-6"
                style={{
                  background: 'linear-gradient(180deg, #4a4a5a 0%, #3d3d4a 100%)',
                  clipPath: 'polygon(0% 0%, 100% 0%, 85% 100%, 15% 100%)',
                  boxShadow: 'inset 0 -2px 6px rgba(0,0,0,0.4)'
                }}
              />
              
              {/* Tube body */}
              <div 
                className="absolute right-2 top-5 w-8 h-[82%] rounded-b-lg overflow-hidden"
                style={{
                  background: 'linear-gradient(90deg, rgba(60,65,80,0.9) 0%, rgba(80,85,100,0.8) 50%, rgba(60,65,80,0.9) 100%)',
                  boxShadow: 'inset 2px 0 8px rgba(0,0,0,0.5), inset -2px 0 8px rgba(0,0,0,0.5)',
                  border: '2px solid rgba(100,105,120,0.4)'
                }}
              />
              
              {/* Stopper */}
              <div 
                className={`absolute right-3 top-4 w-6 h-2 rounded-full transition-all duration-200 ${
                  catchPhase === 'catching' ? 'bg-amber-400' : 'bg-slate-600'
                }`}
                style={{
                  boxShadow: catchPhase === 'catching' 
                    ? '0 0 12px rgba(251,191,36,0.8)' 
                    : '0 1px 3px rgba(0,0,0,0.3)'
                }}
              />
              
              {/* Ball in tube */}
              {currentCatch && (
                <div 
                  className={`absolute right-3 transition-all ease-in-out ${
                    catchPhase === 'catching' ? 'top-5 scale-100 duration-300' : 
                    catchPhase === 'rolling' ? 'top-[65%] scale-95 duration-600' : 
                    'top-[80%] scale-90 opacity-0 duration-300'
                  }`}
                  style={{
                    filter: catchPhase === 'catching' ? 'drop-shadow(0 0 10px rgba(255,200,0,0.7))' : 'none'
                  }}
                >
                  <Ball number={currentCatch} size="sm" isWinner={true} />
                </div>
              )}
            </div>
            
            {/* Air jets - fewer */}
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="relative">
                  <div 
                    className="w-2 h-2 rounded-full transition-all"
                    style={{
                      background: 'radial-gradient(circle, #60a5fa 0%, #3b82f6 70%)',
                      boxShadow: (phase === 'spinning' || phase === 'selecting') 
                        ? '0 0 10px #3b82f6' 
                        : '0 0 5px #3b82f680'
                    }}
                  />
                  <div 
                    className="absolute bottom-full left-1/2 -translate-x-1/2 w-1.5"
                    style={{
                      height: (phase === 'spinning' || phase === 'selecting') ? '35px' : '18px',
                      background: 'linear-gradient(to top, rgba(96,165,250,0.6), transparent)',
                      filter: 'blur(2px)',
                      animation: 'airJet 0.3s ease-in-out infinite alternate',
                      opacity: (phase === 'spinning' || phase === 'selecting') ? 1 : 0.4
                    }}
                  />
                </div>
              ))}
            </div>
            
            {/* Floating Balls - Smaller */}
            {balls.map((ball) => (
              <div
                key={ball.number}
                className={`absolute transition-opacity duration-300 ${ball.captured ? 'opacity-0' : 'opacity-100'}`}
                style={{
                  left: `${ball.x}%`,
                  top: `${ball.y}%`,
                  transform: 'translate(-50%, -50%) scale(0.8)',
                  zIndex: Math.floor(ball.y)
                }}
              >
                <Ball 
                  number={ball.number} 
                  size="sm"
                  isSpinning={phase === 'spinning' || phase === 'selecting'}
                />
              </div>
            ))}
          </div>
          
          {/* Gold rim */}
          <div 
            className="absolute inset-0 rounded-[32px] pointer-events-none"
            style={{
              border: '2px solid rgba(212,175,55,0.4)'
            }}
          />
        </div>
        
        {/* Brand plate */}
        <div 
          className="absolute -bottom-1 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full"
          style={{
            background: 'linear-gradient(135deg, #d4af37 0%, #b8860b 100%)',
            boxShadow: '0 2px 6px rgba(212,175,55,0.4)'
          }}
        >
          <span className="text-[8px] font-bold text-gray-900 tracking-wider">LUCKY JACK</span>
        </div>
      </div>

      {/* Results Display - Compact */}
      <div 
        className="px-4 py-3 rounded-xl"
        style={{
          background: 'linear-gradient(180deg, rgba(30,35,50,0.95) 0%, rgba(20,25,35,0.98) 100%)',
          boxShadow: '0 6px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)',
          border: '2px solid rgba(212,175,55,0.3)',
          minWidth: '300px'
        }}
      >
        {/* Current catching indicator */}
        {catchPhase !== 'none' && currentCatch && (
          <div className="text-center mb-3">
            <span className={`text-sm font-bold ${
              catchPhase === 'catching' ? 'text-amber-400 animate-pulse' :
              catchPhase === 'rolling' ? 'text-amber-300' :
              'text-emerald-400'
            }`}>
              {catchPhase === 'catching' && '⚡ Ball caught!'}
              {catchPhase === 'rolling' && '🎱 Rolling...'}
              {catchPhase === 'revealed' && `✨ Number ${currentCatch}!`}
            </span>
          </div>
        )}
        
        {/* Number slots - smaller */}
        <div className="flex gap-2 justify-center">
          {[0, 1, 2, 3, 4, 5].map((i) => {
            const ballNumber = selectedBalls[i];
            const isBeingRevealed = catchPhase === 'revealed' && i === selectedBalls.length - 1;
            
            return (
              <div key={i} className="relative">
                {ballNumber ? (
                  <div className={isBeingRevealed ? 'ball-jump-in' : ''}>
                    <Ball number={ballNumber} size="sm" isWinner={true} />
                  </div>
                ) : (
                  <div 
                    className={`w-9 h-9 rounded-full border-2 flex items-center justify-center ${
                      phase === 'selecting' && i === selectedBalls.length 
                        ? 'border-amber-500 animate-pulse' 
                        : 'border-dashed border-slate-600'
                    }`}
                    style={{ 
                      background: phase === 'selecting' && i === selectedBalls.length
                        ? 'radial-gradient(circle, rgba(245,158,11,0.15) 0%, transparent 70%)'
                        : 'rgba(30,40,60,0.5)' 
                    }}
                  >
                    <span className="text-slate-500 text-sm">{i + 1}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        {/* Status text */}
        <div className="text-center mt-3">
          {phase === 'idle' && selectedBalls.length === 0 && (
            <span className="text-slate-400 text-sm">Press button to start</span>
          )}
          {phase === 'spinning' && (
            <span className="text-blue-400 text-sm animate-pulse">🌪️ Mixing balls...</span>
          )}
          {phase === 'selecting' && selectedBalls.length < 6 && (
            <span className="text-amber-400 text-sm">
              Ball {Math.min(selectedBalls.length + 1, 6)} of 6
            </span>
          )}
          {phase === 'complete' && (
            <span className="text-emerald-400 text-sm">✓ Your lucky numbers!</span>
          )}
          {phase === 'resetting' && (
            <span className="text-blue-400 text-sm animate-pulse">🎱 Balls returning...</span>
          )}
        </div>
        
        {/* Falling balls indicator */}
        {fallingBalls.length > 0 && (
          <div className="absolute top-0 left-1/2 -translate-x-1/2 flex gap-2">
            {fallingBalls.map((num, idx) => (
              <div 
                key={num} 
                className="ball-fall-down"
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                <Ball number={num} size="sm" isWinner={true} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Main App
function App() {
  const [prediction, setPrediction] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPersonal, setShowPersonal] = useState(false);
  const [showBonus, setShowBonus] = useState(false);
  const [showLocks, setShowLocks] = useState(false);
  const [showMultiTickets, setShowMultiTickets] = useState(false);
  const [wheelSpinning, setWheelSpinning] = useState(false);
  
  // Personal mode
  const [birthday, setBirthday] = useState("");
  const [fullName, setFullName] = useState("");
  
  // Locked positions (P1-P6) - user can lock 1-4 positions
  const [lockedPositions, setLockedPositions] = useState({
    p1: "", p2: "", p3: "", p4: "", p5: "", p6: ""
  });
  
  // Multi-ticket mode
  const [numTickets, setNumTickets] = useState(1);

  const handleLockChange = (position, value) => {
    // Validate: must be 1-42 or empty
    const num = parseInt(value);
    if (value === "" || (num >= 1 && num <= 42)) {
      // Count current locks
      const currentLocks = Object.values(lockedPositions).filter(v => v !== "").length;
      const isClearing = value === "";
      const isNewLock = lockedPositions[position] === "" && value !== "";
      
      // Max 4 locks
      if (isNewLock && currentLocks >= 4) {
        return; // Silently reject
      }
      
      setLockedPositions(prev => ({...prev, [position]: value}));
    }
  };

  const getLockedCount = () => Object.values(lockedPositions).filter(v => v !== "").length;

  const fetchPrediction = useCallback(async () => {
    try {
      setLoading(true);
      setWheelSpinning(false); // Reset wheel
      
      let url = `${API}/master-predictor`;
      const params = [];
      if (birthday) params.push(`birthday=${encodeURIComponent(birthday)}`);
      if (fullName) params.push(`name=${encodeURIComponent(fullName)}`);
      
      // Add locked positions
      if (lockedPositions.p1) params.push(`lock_p1=${lockedPositions.p1}`);
      if (lockedPositions.p2) params.push(`lock_p2=${lockedPositions.p2}`);
      if (lockedPositions.p3) params.push(`lock_p3=${lockedPositions.p3}`);
      if (lockedPositions.p4) params.push(`lock_p4=${lockedPositions.p4}`);
      if (lockedPositions.p5) params.push(`lock_p5=${lockedPositions.p5}`);
      if (lockedPositions.p6) params.push(`lock_p6=${lockedPositions.p6}`);
      
      // Add num_tickets
      if (numTickets > 1) params.push(`num_tickets=${numTickets}`);
      
      if (params.length > 0) url += `?${params.join('&')}`;
      
      // Delay for animation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const res = await axios.get(url);
      setPrediction(res.data);
      
      // Start wheel spinning after main balls are done (about 12 seconds for 6 balls)
      setTimeout(() => {
        setWheelSpinning(true);
      }, 12000);
    } catch (e) {
      console.error("Error:", e);
      // Generate random lucky numbers as fallback
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
      setTimeout(() => {
        setWheelSpinning(true);
      }, 12000);
    } finally {
      setLoading(false);
    }
  }, [birthday, fullName, lockedPositions, numTickets]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/dashboard`);
      setStats(res.data);
    } catch (e) {
      console.error("Error:", e);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    // Initial prediction without animation
    const fetchInitial = async () => {
      try {
        const res = await axios.get(`${API}/master-predictor`);
        setPrediction(res.data);
      } catch (e) {
        console.error("Error:", e);
        // Fallback demo prediction when API fails
        setPrediction({
          main_prediction: [7, 14, 21, 28, 35, 42],
          average_confidence: 77,
          alternate_numbers: [3, 11, 19, 27, 33, 39]
        });
      }
    };
    fetchInitial();
  }, [fetchStats]);

  return (
    <div className="min-h-screen pb-10">
      {/* Header */}
      <header className="text-center py-6">
        <div className="flex items-center justify-center gap-3 mb-1">
          <span className="text-3xl">🎱</span>
          <h1 
            className="text-3xl font-bold"
            style={{
              background: 'linear-gradient(135deg, #d4af37 0%, #f0d060 50%, #d4af37 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            Lucky Jack
          </h1>
          <span className="text-3xl">🍀</span>
        </div>
        <p className="text-slate-400 text-sm">Swiss Lotto Number Generator</p>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4">
        {/* Main Content */}
        <div className="lucky-card p-6 mb-6">
          <h2 className="text-lg font-semibold text-center text-slate-200 mb-6">
            Your Lucky Numbers
          </h2>
          
          {/* Ball Machine + Lucky Wheel - Connected */}
          <div className="flex items-start justify-center">
            {/* Ball Machine */}
            <BallMachine 
              isProcessing={loading}
              winningNumbers={prediction?.main_prediction || []}
            />
            
            {/* Lucky Wheel - Angled perspective, connected tight */}
            <div className="-ml-3 mt-10" style={{ transform: 'perspective(300px) rotateY(-20deg)' }}>
              <LuckyWheel 
                luckyNumber={prediction?.lucky_prediction || 1}
                isSpinning={wheelSpinning}
              />
            </div>
          </div>
          
          {/* Prompt text */}
          <div className="text-center mt-6 mb-4">
            {!loading && !prediction && (
              <p className="text-slate-400 text-sm">Press the button to generate your lucky numbers</p>
            )}
            {prediction && !loading && (
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-emerald-900/30 to-emerald-800/30 px-4 py-2 rounded-full text-sm border border-emerald-500/20">
                <span className="text-emerald-400">✓</span>
                <span className="text-emerald-300 font-medium">Numbers generated</span>
              </div>
            )}
          </div>
          
          {/* Generate Button */}
          <div className="text-center">
            <button 
              onClick={fetchPrediction}
              disabled={loading}
              className="lucky-btn flex items-center gap-2 mx-auto"
              data-testid="generate-btn"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              {loading ? '🤞 Finding Lucky Numbers...' : '🍀 Get New Numbers 🍀'}
            </button>
          </div>
        </div>

        {/* Personalize Card */}
        <div className="lucky-card p-4 mb-4">
          <div 
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setShowPersonal(!showPersonal)}
          >
            <span className="font-semibold text-slate-200">Personalize Your Numbers</span>
            {showPersonal ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </div>
          
          {showPersonal && (
            <div className="mt-4 space-y-3">
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
                    ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-gray-900 hover:from-amber-400 hover:to-amber-500 shadow-lg' 
                    : 'bg-slate-700 text-slate-400 cursor-not-allowed'
                }`}
                data-testid="birthday-generate-btn"
              >
                {loading ? (
                  <>
                    <Sparkles className="w-5 h-5 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate with Birthday</span>
                  </>
                )}
              </button>
              
              {(prediction?.birthday_mode || prediction?.name_mode) && (
                <div className="bg-slate-800/50 rounded-xl p-3 text-xs border border-slate-600/50">
                  {prediction.birthday_mode && (
                    <div className="flex items-center gap-2 text-slate-300">
                      <span className="text-amber-400">✦</span>
                      <span className="font-medium">Birthday numbers:</span>
                      <span className="text-amber-300">{prediction.birthday_mode.lucky_numbers.slice(0, 4).join(", ")}</span>
                    </div>
                  )}
                  {prediction.name_mode && (
                    <div className="flex items-center gap-2 text-slate-300 mt-1">
                      <span className="text-amber-400">✦</span>
                      <span className="font-medium">Name numbers:</span>
                      <span className="text-amber-300">{prediction.name_mode.lucky_numbers.slice(0, 4).join(", ")}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Lock Positions Card */}
        <div className="lucky-card p-4 mb-4">
          <div 
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setShowLocks(!showLocks)}
            data-testid="lock-positions-toggle"
          >
            <span className="font-semibold text-slate-200 flex items-center gap-2">
              🔒 Lock Positions
              {getLockedCount() > 0 && (
                <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full">
                  {getLockedCount()}/4
                </span>
              )}
            </span>
            {showLocks ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </div>
          
          {showLocks && (
            <div className="mt-4">
              <p className="text-xs text-slate-400 mb-3">
                Lock 1-4 numbers at specific positions. Generator fills the rest.
              </p>
              
              <div className="grid grid-cols-6 gap-2 mb-3">
                {['p1', 'p2', 'p3', 'p4', 'p5', 'p6'].map((pos, idx) => (
                  <div key={pos} className="text-center">
                    <label className="text-xs text-slate-500 block mb-1">P{idx + 1}</label>
                    <input
                      type="number"
                      min="1"
                      max="42"
                      value={lockedPositions[pos]}
                      onChange={(e) => handleLockChange(pos, e.target.value)}
                      placeholder="—"
                      disabled={lockedPositions[pos] === "" && getLockedCount() >= 4}
                      className={`w-full px-1 py-2 rounded-lg text-center text-sm font-bold
                        ${lockedPositions[pos] 
                          ? 'bg-amber-500/20 border-amber-500/50 text-amber-400' 
                          : 'bg-slate-800/50 border-slate-600 text-white placeholder-slate-600'}
                        ${lockedPositions[pos] === "" && getLockedCount() >= 4 
                          ? 'opacity-50 cursor-not-allowed' 
                          : ''}
                        border focus:border-amber-500/50 focus:outline-none`}
                      data-testid={`lock-${pos}`}
                    />
                  </div>
                ))}
              </div>
              
              {/* Position hints */}
              <div className="text-xs text-slate-500 space-y-1 bg-slate-800/30 rounded-lg p-2">
                <div className="flex justify-between">
                  <span>P1-P2:</span><span className="text-slate-400">Low (1-15)</span>
                </div>
                <div className="flex justify-between">
                  <span>P3-P4:</span><span className="text-slate-400">Mid (10-32)</span>
                </div>
                <div className="flex justify-between">
                  <span>P5-P6:</span><span className="text-slate-400">High (25-42)</span>
                </div>
              </div>
              
              {getLockedCount() > 0 && (
                <button
                  onClick={() => setLockedPositions({p1: "", p2: "", p3: "", p4: "", p5: "", p6: ""})}
                  className="mt-3 w-full py-2 rounded-lg bg-slate-700/50 text-slate-400 text-sm hover:bg-slate-700 transition-colors"
                  data-testid="clear-locks-btn"
                >
                  Clear All Locks
                </button>
              )}
              
              {/* Show locked positions in response */}
              {prediction?.locked_positions && Object.keys(prediction.locked_positions).length > 0 && (
                <div className="mt-3 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
                  <div className="flex items-center gap-2 text-xs text-amber-400">
                    <span>🔒 Locked:</span>
                    {Object.entries(prediction.locked_positions).map(([pos, num]) => (
                      <span key={pos} className="bg-amber-500/20 px-2 py-0.5 rounded">
                        {pos}={num}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Multi-Ticket Mode */}
        <div className="lucky-card p-4 mb-4">
          <div 
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setShowMultiTickets(!showMultiTickets)}
            data-testid="multi-tickets-toggle"
          >
            <span className="font-semibold text-slate-200 flex items-center gap-2">
              🎫 Multiple Tickets
              {numTickets > 1 && (
                <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full">
                  {numTickets} tickets
                </span>
              )}
            </span>
            {showMultiTickets ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </div>
          
          {showMultiTickets && (
            <div className="mt-4">
              <p className="text-xs text-slate-400 mb-3">
                Generate multiple ticket predictions ranked by confidence.
              </p>
              
              {/* Ticket count selector */}
              <div className="flex items-center gap-3 mb-4">
                <span className="text-sm text-slate-300">How many tickets?</span>
                <div className="flex gap-1">
                  {[1, 3, 5, 8, 10, 15, 20].map(n => (
                    <button
                      key={n}
                      onClick={() => setNumTickets(n)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                        ${numTickets === n 
                          ? 'bg-emerald-500 text-white' 
                          : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'}`}
                      data-testid={`tickets-${n}`}
                    >
                      {n}
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
                          ? 'bg-gradient-to-r from-amber-500/20 to-amber-600/10 border border-amber-500/30' 
                          : 'bg-slate-800/50 border border-slate-700/50'
                      }`}
                    >
                      <span className={`text-xs font-bold w-6 ${idx === 0 ? 'text-amber-400' : 'text-slate-500'}`}>
                        #{ticket.ticket_num}
                      </span>
                      <div className="flex gap-1.5 flex-1">
                        {ticket.numbers.map((num, i) => (
                          <Ball key={i} number={num} size="xs" />
                        ))}
                      </div>
                      <span className={`text-xs ${idx === 0 ? 'text-amber-400' : 'text-slate-500'}`}>
                        {Math.round(ticket.confidence)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Generate button inside panel */}
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
          <div className="lucky-card p-4 mb-4">
            <div 
              className="flex items-center justify-between cursor-pointer"
              onClick={() => setShowBonus(!showBonus)}
            >
              <span className="font-semibold text-slate-200 flex items-center gap-2">
                <Gift className="w-4 h-4 text-amber-400" /> Bonus Numbers
              </span>
              {showBonus ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
            </div>
            
            {showBonus && (
              <div className="mt-4">
                <div className="flex flex-wrap justify-center gap-2">
                  {prediction.alternate_numbers.map((n, i) => (
                    <Ball key={i} number={n} size="sm" />
                  ))}
                </div>
              </div>
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
