import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Sparkles, RefreshCw, ChevronDown, ChevronUp, Gift } from "lucide-react";

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

// Lucky Number Wheel - spins like a car wheel viewed from front
const LuckyWheel = ({ luckyNumber, isSpinning, onComplete }) => {
  const [rotation, setRotation] = useState(0);
  const [settled, setSettled] = useState(false);
  const numbers = [1, 2, 3, 4, 5, 6];
  
  useEffect(() => {
    if (isSpinning && luckyNumber) {
      setSettled(false);
      // Calculate final rotation: spin several times + land on lucky number
      // Each number is 60 degrees apart (360/6)
      // Number 1 at top (0°), going clockwise: 2=60°, 3=120°, 4=180°, 5=240°, 6=300°
      const targetAngle = (luckyNumber - 1) * 60;
      // Spin 6 full rotations + land on target at top
      const finalRotation = 360 * 6 + (360 - targetAngle);
      setRotation(finalRotation);
      
      // Settle after animation
      setTimeout(() => {
        setSettled(true);
        if (onComplete) onComplete();
      }, 3500);
    }
  }, [isSpinning, luckyNumber, onComplete]);

  // Reset when starting new spin
  useEffect(() => {
    if (!isSpinning && !settled) {
      setRotation(0);
    }
  }, [isSpinning, settled]);

  return (
    <div className="flex flex-col items-center">
      <div className="text-sm font-semibold text-amber-400 mb-2">⭐ Lucky Number</div>
      
      {/* Wheel container */}
      <div className="relative w-28 h-28">
        {/* Pointer at top */}
        <div 
          className="absolute -top-3 left-1/2 -translate-x-1/2 z-20"
          style={{
            width: 0,
            height: 0,
            borderLeft: '10px solid transparent',
            borderRight: '10px solid transparent',
            borderTop: '14px solid #d4af37',
            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.4))'
          }}
        />
        
        {/* Outer metallic ring */}
        <div 
          className="absolute inset-0 rounded-full"
          style={{
            background: 'linear-gradient(180deg, #4a4a5a 0%, #2a2a35 50%, #3a3a45 100%)',
            boxShadow: '0 6px 25px rgba(0,0,0,0.6), inset 0 2px 4px rgba(255,255,255,0.15), inset 0 -2px 4px rgba(0,0,0,0.3)'
          }}
        />
        
        {/* Spinning wheel face */}
        <div 
          className="absolute inset-2 rounded-full overflow-hidden"
          style={{
            background: 'conic-gradient(from 0deg, #1e293b 0deg, #334155 60deg, #1e293b 60deg, #334155 120deg, #1e293b 120deg, #334155 180deg, #1e293b 180deg, #334155 240deg, #1e293b 240deg, #334155 300deg, #1e293b 300deg, #334155 360deg)',
            transform: `rotate(${rotation}deg)`,
            transition: isSpinning ? 'transform 3.5s cubic-bezier(0.12, 0.8, 0.2, 1)' : 'none',
            boxShadow: 'inset 0 0 30px rgba(0,0,0,0.6)'
          }}
        >
          {/* Numbers arranged in circle - counter-rotate to stay upright */}
          {numbers.map((num, i) => {
            const angle = i * 60; // 360/6 = 60 degrees apart
            const isWinner = settled && num === luckyNumber;
            return (
              <div
                key={num}
                className="absolute"
                style={{
                  left: '50%',
                  top: '50%',
                  transform: `translate(-50%, -50%) rotate(${angle}deg) translateY(-32px)`,
                }}
              >
                <div 
                  className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-base transition-all duration-500 ${
                    isWinner ? 'scale-125' : ''
                  }`}
                  style={{
                    background: isWinner 
                      ? 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)'
                      : 'linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%)',
                    color: isWinner ? '#1a1a24' : '#1e293b',
                    boxShadow: isWinner 
                      ? '0 0 20px rgba(251,191,36,0.9), 0 4px 12px rgba(0,0,0,0.4)'
                      : '0 2px 8px rgba(0,0,0,0.4), inset 0 1px 2px rgba(255,255,255,0.8)',
                    transform: `rotate(-${angle + rotation}deg)`, // Counter-rotate to keep upright
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
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full z-10"
          style={{
            background: 'linear-gradient(145deg, #d4af37 0%, #b8860b 100%)',
            boxShadow: '0 3px 10px rgba(0,0,0,0.5), inset 0 2px 4px rgba(255,255,255,0.3)'
          }}
        >
          <div 
            className="absolute inset-1 rounded-full"
            style={{
              background: 'linear-gradient(145deg, #3a3a45 0%, #2a2a35 100%)',
            }}
          />
        </div>
        
        {/* Winner glow */}
        {settled && (
          <div 
            className="absolute inset-0 rounded-full pointer-events-none animate-pulse"
            style={{
              boxShadow: '0 0 40px rgba(251,191,36,0.6), inset 0 0 20px rgba(251,191,36,0.2)'
            }}
          />
        )}
      </div>
      
      {/* Result display */}
      <div className={`mt-3 text-center transition-all duration-500 ${settled ? 'opacity-100 scale-100' : 'opacity-0 scale-75'}`}>
        <span className="text-2xl font-black text-amber-400" style={{ textShadow: '0 0 10px rgba(251,191,36,0.5)' }}>
          {luckyNumber}
        </span>
      </div>
    </div>
  );
};


// Realistic Lottery Ball Machine with Tube Selection
const BallMachine = ({ isProcessing, winningNumbers }) => {
  const [balls, setBalls] = useState([]);
  const [phase, setPhase] = useState('idle'); // idle, spinning, selecting, complete
  const [selectedBalls, setSelectedBalls] = useState([]);
  const [currentCatch, setCurrentCatch] = useState(null); // Ball currently caught in tube
  const [selectionIndex, setSelectionIndex] = useState(0);
  const [catchPhase, setCatchPhase] = useState('none'); // none, catching, rolling, revealed
  const [hasInitialized, setHasInitialized] = useState(false);
  
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
      // All done!
      setPhase('complete');
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
      {/* Machine Container */}
      <div className="relative mb-6">
        {/* Machine Frame */}
        <div 
          className="relative w-[360px] h-[340px] rounded-[40px] p-2"
          style={{
            background: 'linear-gradient(180deg, #2d2d3a 0%, #1a1a24 100%)',
            boxShadow: '0 20px 60px rgba(0,0,0,0.5), inset 0 2px 1px rgba(255,255,255,0.1)'
          }}
        >
          {/* Inner Glass Container */}
          <div 
            className="relative w-full h-full rounded-[32px] overflow-hidden"
            style={{
              background: 'linear-gradient(180deg, rgba(20,25,40,0.95) 0%, rgba(10,15,25,0.98) 100%)',
              boxShadow: 'inset 0 0 60px rgba(0,0,0,0.5), inset 0 -20px 40px rgba(0,0,0,0.3)'
            }}
          >
            {/* Glass reflection */}
            <div 
              className="absolute inset-0 pointer-events-none rounded-[32px]"
              style={{
                background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 40%)'
              }}
            />
            
            {/* === BIG DRAMATIC TUBE on the right === */}
            <div className="absolute right-0 top-[15%] w-20 h-[70%] z-30">
              {/* Funnel opening - catches the ball */}
              <div 
                className="absolute right-1 top-0 w-14 h-8"
                style={{
                  background: 'linear-gradient(180deg, #4a4a5a 0%, #3d3d4a 100%)',
                  clipPath: 'polygon(0% 0%, 100% 0%, 85% 100%, 15% 100%)',
                  boxShadow: 'inset 0 -3px 8px rgba(0,0,0,0.4)'
                }}
              />
              
              {/* Tube body - transparent so you see ball rolling */}
              <div 
                className="absolute right-3 top-7 w-10 h-[85%] rounded-b-xl overflow-hidden"
                style={{
                  background: 'linear-gradient(90deg, rgba(60,65,80,0.9) 0%, rgba(80,85,100,0.8) 50%, rgba(60,65,80,0.9) 100%)',
                  boxShadow: 'inset 3px 0 10px rgba(0,0,0,0.5), inset -3px 0 10px rgba(0,0,0,0.5), 0 0 20px rgba(0,0,0,0.3)',
                  border: '2px solid rgba(100,105,120,0.5)'
                }}
              >
                {/* Inner tube glass effect */}
                <div 
                  className="absolute inset-1 rounded-b-lg"
                  style={{
                    background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%)'
                  }}
                />
              </div>
              
              {/* Stopper mechanism - GLOWS when catching */}
              <div 
                className={`absolute right-4 top-6 w-8 h-3 rounded-full transition-all duration-200 ${
                  catchPhase === 'catching' ? 'bg-amber-400 scale-110' : 'bg-slate-600'
                }`}
                style={{
                  boxShadow: catchPhase === 'catching' 
                    ? '0 0 20px rgba(251,191,36,0.8), 0 0 40px rgba(251,191,36,0.4)' 
                    : '0 2px 4px rgba(0,0,0,0.3)'
                }}
              />
              
              {/* Ball rolling through tube - BIG and visible! */}
              {currentCatch && (
                <div 
                  className={`absolute right-4 transition-all ease-in-out ${
                    catchPhase === 'catching' ? 'top-8 scale-125 duration-300' : 
                    catchPhase === 'rolling' ? 'top-[70%] scale-110 duration-700' : 
                    'top-[90%] scale-100 opacity-0 duration-300'
                  }`}
                  style={{
                    filter: catchPhase === 'catching' ? 'drop-shadow(0 0 15px rgba(255,200,0,0.8))' : 'none'
                  }}
                >
                  <Ball number={currentCatch} size="md" isWinner={true} />
                </div>
              )}
              
              {/* Exit chute at bottom */}
              <div 
                className="absolute right-2 bottom-0 w-12 h-4 rounded-b-lg"
                style={{
                  background: 'linear-gradient(180deg, #3d3d4a 0%, #2a2a35 100%)',
                  boxShadow: '0 4px 10px rgba(0,0,0,0.4)'
                }}
              />
            </div>
            
            {/* Air jets at bottom - always on! */}
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="relative">
                  <div 
                    className="w-3 h-3 rounded-full transition-all"
                    style={{
                      background: 'radial-gradient(circle, #60a5fa 0%, #3b82f6 70%)',
                      boxShadow: (phase === 'spinning' || phase === 'selecting') 
                        ? '0 0 15px #3b82f6, 0 0 25px #60a5fa' 
                        : '0 0 8px #3b82f680'
                    }}
                  />
                  {/* Air stream - always visible, stronger during spin */}
                  <div 
                    className="absolute bottom-full left-1/2 -translate-x-1/2 w-2"
                    style={{
                      height: (phase === 'spinning' || phase === 'selecting') ? '50px' : '25px',
                      background: 'linear-gradient(to top, rgba(96,165,250,0.7), transparent)',
                      filter: 'blur(3px)',
                      animation: 'airJet 0.3s ease-in-out infinite alternate',
                      opacity: (phase === 'spinning' || phase === 'selecting') ? 1 : 0.5
                    }}
                  />
                </div>
              ))}
            </div>
            
            {/* Floating Balls */}
            {balls.map((ball) => (
              <div
                key={ball.number}
                className={`absolute transition-opacity duration-300 ${ball.captured ? 'opacity-0' : 'opacity-100'}`}
                style={{
                  left: `${ball.x}%`,
                  top: `${ball.y}%`,
                  transform: 'translate(-50%, -50%)',
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
            className="absolute inset-0 rounded-[40px] pointer-events-none"
            style={{
              border: '3px solid rgba(212,175,55,0.4)'
            }}
          />
        </div>
        
        {/* Brand plate */}
        <div 
          className="absolute -bottom-2 left-1/2 -translate-x-1/2 px-5 py-1.5 rounded-full"
          style={{
            background: 'linear-gradient(135deg, #d4af37 0%, #b8860b 100%)',
            boxShadow: '0 2px 10px rgba(212,175,55,0.4)'
          }}
        >
          <span className="text-xs font-bold text-gray-900 tracking-wider">LUCKY JACK</span>
        </div>
      </div>

      {/* Results Display - Shows numbers one by one as they're caught */}
      <div 
        className="px-6 py-5 rounded-2xl"
        style={{
          background: 'linear-gradient(180deg, rgba(30,35,50,0.95) 0%, rgba(20,25,35,0.98) 100%)',
          boxShadow: '0 8px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)',
          border: '2px solid rgba(212,175,55,0.3)',
          minWidth: '420px'
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
        
        {/* Number slots */}
        <div className="flex gap-3 justify-center">
          {[0, 1, 2, 3, 4, 5].map((i) => {
            const ballNumber = selectedBalls[i];
            const isBeingRevealed = catchPhase === 'revealed' && i === selectedBalls.length - 1;
            
            return (
              <div key={i} className="relative">
                {ballNumber ? (
                  <div className={isBeingRevealed ? 'ball-jump-in' : ''}>
                    <Ball number={ballNumber} size="md" isWinner={true} />
                  </div>
                ) : (
                  <div 
                    className={`w-12 h-12 rounded-full border-2 flex items-center justify-center ${
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
                    <span className="text-slate-500 text-lg">{i + 1}</span>
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
          {phase === 'selecting' && (
            <span className="text-amber-400 text-sm">
              Ball {selectedBalls.length + 1} of 6
            </span>
          )}
          {phase === 'complete' && (
            <span className="text-emerald-400 text-sm">✓ Your lucky numbers!</span>
          )}
        </div>
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
  const [wheelSpinning, setWheelSpinning] = useState(false);
  
  // Personal mode
  const [birthday, setBirthday] = useState("");
  const [fullName, setFullName] = useState("");

  const fetchPrediction = useCallback(async () => {
    try {
      setLoading(true);
      setWheelSpinning(false); // Reset wheel
      
      let url = `${API}/master-predictor`;
      const params = [];
      if (birthday) params.push(`birthday=${encodeURIComponent(birthday)}`);
      if (fullName) params.push(`name=${encodeURIComponent(fullName)}`);
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
  }, [birthday, fullName]);

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
          
          {/* Ball Machine + Lucky Wheel */}
          <div className="flex items-start justify-center gap-6">
            {/* Ball Machine */}
            <BallMachine 
              isProcessing={loading}
              winningNumbers={prediction?.main_prediction || []}
            />
            
            {/* Lucky Number Wheel */}
            <div className="mt-8">
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
