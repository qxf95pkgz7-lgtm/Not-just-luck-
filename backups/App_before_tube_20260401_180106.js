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

// Realistic Lottery Ball Machine with Glass Dome
const BallMachine = ({ isProcessing, winningNumbers }) => {
  const [balls, setBalls] = useState([]);
  const [phase, setPhase] = useState('idle');
  const [showResults, setShowResults] = useState(false);
  
  const GRAVITY = 0.12;
  const AIR_FORCE = -0.9;
  const FRICTION = 0.985;
  const BOUNCE = 0.65;

  // Initialize balls at bottom
  useEffect(() => {
    const allBalls = Array.from({ length: 42 }, (_, i) => ({
      number: i + 1,
      x: 8 + (i % 7) * 13 + Math.random() * 4,
      y: 65 + Math.floor(i / 7) * 6 + Math.random() * 4,
      vx: 0,
      vy: 0
    }));
    setBalls(allBalls);
  }, []);

  useEffect(() => {
    if (isProcessing) {
      setPhase('spinning');
      setShowResults(false);
    } else if (winningNumbers.length > 0 && phase === 'spinning') {
      setPhase('complete');
      setTimeout(() => setShowResults(true), 400);
    } else if (winningNumbers.length > 0 && phase === 'idle') {
      setShowResults(true);
      setPhase('complete');
    }
  }, [isProcessing, winningNumbers, phase]);

  // Physics loop
  useEffect(() => {
    const interval = setInterval(() => {
      setBalls(prev => prev.map(ball => {
        let vx = ball.vx;
        let vy = ball.vy + GRAVITY;
        
        if (phase === 'spinning') {
          vy += AIR_FORCE + (Math.random() - 0.5) * 0.4;
          vx += (Math.random() - 0.5) * 1.2;
        }
        
        vx *= FRICTION;
        vy *= FRICTION;
        
        let x = ball.x + vx;
        let y = ball.y + vy;
        
        // Boundaries
        if (x < 6) { x = 6; vx = -vx * BOUNCE; }
        if (x > 94) { x = 94; vx = -vx * BOUNCE; }
        if (y < 8) { y = 8; vy = -vy * BOUNCE; }
        if (y > 90) { y = 90; vy = -vy * BOUNCE; }
        
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
          className="relative w-[340px] h-[320px] rounded-[40px] p-2"
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
            {/* Glass reflection effect */}
            <div 
              className="absolute inset-0 pointer-events-none rounded-[32px]"
              style={{
                background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 40%, transparent 60%, rgba(255,255,255,0.03) 100%)'
              }}
            />
            
            {/* Air jets indicator */}
            <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-3">
              {[...Array(7)].map((_, i) => (
                <div 
                  key={i}
                  className="relative"
                >
                  <div 
                    className={`w-2 h-2 rounded-full transition-all duration-300`}
                    style={{
                      background: phase === 'spinning' 
                        ? 'radial-gradient(circle, #60a5fa 0%, #3b82f6 50%, transparent 100%)' 
                        : 'rgba(60,70,90,0.5)',
                      boxShadow: phase === 'spinning' ? '0 0 12px #3b82f6, 0 0 20px #60a5fa50' : 'none'
                    }}
                  />
                  {phase === 'spinning' && (
                    <div 
                      className="absolute bottom-full left-1/2 -translate-x-1/2 w-1 animate-pulse"
                      style={{
                        height: '30px',
                        background: 'linear-gradient(to top, rgba(96,165,250,0.6), transparent)',
                        filter: 'blur(2px)'
                      }}
                    />
                  )}
                </div>
              ))}
            </div>
            
            {/* Balls */}
            {balls.map((ball) => (
              <div
                key={ball.number}
                className="absolute"
                style={{
                  left: `${ball.x}%`,
                  top: `${ball.y}%`,
                  transform: 'translate(-50%, -50%)',
                  zIndex: Math.floor(ball.y),
                  transition: 'none'
                }}
              >
                <Ball 
                  number={ball.number} 
                  size="sm"
                  isSpinning={phase === 'spinning'}
                />
              </div>
            ))}
          </div>
          
          {/* Metallic rim */}
          <div 
            className="absolute inset-0 rounded-[40px] pointer-events-none"
            style={{
              border: '3px solid transparent',
              borderImage: 'linear-gradient(180deg, #d4af37 0%, #8b7355 50%, #d4af37 100%) 1'
            }}
          />
        </div>
        
        {/* Machine Stand */}
        <div 
          className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-48 h-6 rounded-b-xl"
          style={{
            background: 'linear-gradient(180deg, #3d3d4a 0%, #2a2a35 100%)',
            boxShadow: '0 4px 15px rgba(0,0,0,0.4)'
          }}
        />
        
        {/* Brand plate */}
        <div 
          className="absolute -bottom-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full"
          style={{
            background: 'linear-gradient(135deg, #d4af37 0%, #b8860b 100%)',
            boxShadow: '0 2px 8px rgba(212,175,55,0.3)'
          }}
        >
          <span className="text-[10px] font-bold text-gray-900 tracking-wider">LUCKY JACK</span>
        </div>
      </div>

      {/* Results Display */}
      <div 
        className="px-6 py-4 rounded-2xl min-h-[80px] flex items-center justify-center"
        style={{
          background: showResults 
            ? 'linear-gradient(180deg, rgba(30,35,50,0.95) 0%, rgba(20,25,35,0.98) 100%)' 
            : 'transparent',
          boxShadow: showResults ? '0 8px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)' : 'none',
          border: showResults ? '2px solid rgba(212,175,55,0.3)' : '2px dashed rgba(212,175,55,0.2)',
          minWidth: '380px',
          borderRadius: '20px'
        }}
      >
        {showResults && winningNumbers.length > 0 ? (
          <div className="flex gap-3">
            {winningNumbers.map((num, i) => (
              <div 
                key={num}
                className="ball-jump-in"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <Ball number={num} size="md" isWinner={true} />
              </div>
            ))}
          </div>
        ) : (
          <span className="text-slate-400 text-sm font-medium">
            {phase === 'spinning' 
              ? '🌀 Air jets activated — selecting numbers...' 
              : '✨ Press button to start the machine'}
          </span>
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
  
  // Personal mode
  const [birthday, setBirthday] = useState("");
  const [fullName, setFullName] = useState("");

  const fetchPrediction = useCallback(async () => {
    try {
      setLoading(true);
      
      let url = `${API}/master-predictor`;
      const params = [];
      if (birthday) params.push(`birthday=${encodeURIComponent(birthday)}`);
      if (fullName) params.push(`name=${encodeURIComponent(fullName)}`);
      if (params.length > 0) url += `?${params.join('&')}`;
      
      // Delay for animation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const res = await axios.get(url);
      setPrediction(res.data);
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
        alternate_numbers: [3, 11, 19, 27, 33, 39]
      });
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
      <main className="max-w-lg mx-auto px-4">
        {/* Main Content */}
        <div className="lucky-card p-6 mb-6">
          <h2 className="text-lg font-semibold text-center text-slate-200 mb-6">
            Your Lucky Numbers
          </h2>
          
          {/* Ball Machine */}
          <BallMachine 
            isProcessing={loading}
            winningNumbers={prediction?.main_prediction || []}
          />
          
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
