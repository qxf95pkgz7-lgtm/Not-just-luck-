import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Sparkles, RefreshCw, ChevronDown, ChevronUp, Gift } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Ball colors like billiard balls
const getBallColor = (num) => {
  const colors = [
    "from-yellow-400 to-yellow-500",    // 1-7: Solids
    "from-blue-400 to-blue-600",
    "from-red-400 to-red-600",
    "from-purple-400 to-purple-600",
    "from-orange-400 to-orange-600",
    "from-green-400 to-green-600",
    "from-rose-400 to-rose-600",
    "from-amber-400 to-amber-600",      // 8: Black (special)
    "from-yellow-300 to-yellow-400",    // 9-15: Stripes
    "from-blue-300 to-blue-500",
    "from-red-300 to-red-500",
    "from-purple-300 to-purple-500",
    "from-orange-300 to-orange-500",
    "from-green-300 to-green-500",
    "from-rose-300 to-rose-500",
  ];
  return colors[(num - 1) % colors.length];
};

// Single Ball Component
const Ball = ({ number, size = "sm", isWinner = false, isSpinning = false, delay = 0, style = {} }) => {
  const sizeClasses = {
    xs: "w-8 h-8 text-xs",
    sm: "w-10 h-10 text-sm",
    md: "w-14 h-14 text-base",
    lg: "w-20 h-20 text-xl"
  };
  
  const color = getBallColor(number);
  
  return (
    <div 
      className={`
        ${sizeClasses[size]} rounded-full flex items-center justify-center 
        font-bold text-white shadow-lg bg-gradient-to-br ${color}
        ${isWinner ? 'winner-ball' : ''}
        ${isSpinning ? 'spinning-ball' : ''}
        transition-all duration-500
      `}
      style={{ 
        animationDelay: `${delay}ms`,
        boxShadow: isWinner 
          ? '0 0 20px rgba(255,184,0,0.6), 0 4px 15px rgba(0,0,0,0.2)' 
          : '0 4px 10px rgba(0,0,0,0.15), inset 0 -2px 6px rgba(0,0,0,0.1), inset 0 2px 6px rgba(255,255,255,0.3)',
        ...style
      }}
    >
      <span className="relative z-10">{number}</span>
      {/* Shine effect */}
      <div className="absolute top-1 left-1 w-2 h-2 bg-white/40 rounded-full" />
    </div>
  );
};

// Lottery Ball Machine with Result Slots - Simplified
const BallMachine = ({ isProcessing, winningNumbers }) => {
  const [balls, setBalls] = useState([]);
  const [phase, setPhase] = useState('idle'); // idle, spinning, complete
  const [showResults, setShowResults] = useState(false);

  // Initialize all 42 balls
  useEffect(() => {
    const allBalls = Array.from({ length: 42 }, (_, i) => ({
      number: i + 1,
      x: Math.random() * 80 + 10,
      y: Math.random() * 80 + 10,
      vx: (Math.random() - 0.5) * 4,
      vy: (Math.random() - 0.5) * 4
    }));
    setBalls(allBalls);
  }, []);

  // Handle processing phases
  useEffect(() => {
    if (isProcessing) {
      setPhase('spinning');
      setShowResults(false);
      // Reset balls with faster movement
      const allBalls = Array.from({ length: 42 }, (_, i) => ({
        number: i + 1,
        x: Math.random() * 80 + 10,
        y: Math.random() * 80 + 10,
        vx: (Math.random() - 0.5) * 6,
        vy: (Math.random() - 0.5) * 6
      }));
      setBalls(allBalls);
    } else if (winningNumbers.length > 0 && phase === 'spinning') {
      // Only transition to complete if we were spinning
      setPhase('complete');
      setTimeout(() => {
        setShowResults(true);
      }, 300);
    } else if (winningNumbers.length > 0 && phase === 'idle') {
      // Initial load with numbers - show them immediately
      setShowResults(true);
      setPhase('complete');
    }
  }, [isProcessing, winningNumbers, phase]);

  // Animate balls when spinning
  useEffect(() => {
    if (phase !== 'spinning') return;

    const interval = setInterval(() => {
      setBalls(prev => prev.map(ball => {
        let newX = ball.x + ball.vx;
        let newY = ball.y + ball.vy;
        let newVx = ball.vx;
        let newVy = ball.vy;

        // Bounce off walls
        if (newX < 5 || newX > 95) newVx = -newVx * 0.9;
        if (newY < 5 || newY > 95) newVy = -newVy * 0.9;

        // Add some randomness
        newVx += (Math.random() - 0.5) * 0.5;
        newVy += (Math.random() - 0.5) * 0.5;

        // Clamp velocity
        newVx = Math.max(-5, Math.min(5, newVx));
        newVy = Math.max(-5, Math.min(5, newVy));

        return {
          ...ball,
          x: Math.max(5, Math.min(95, newX)),
          y: Math.max(5, Math.min(95, newY)),
          vx: newVx,
          vy: newVy
        };
      }));
    }, 50);

    return () => clearInterval(interval);
  }, [phase]);

  return (
    <div className="flex flex-col items-center">
      {/* Two boxes side by side */}
      <div className="flex items-center justify-center gap-4 mb-6">
        {/* Box 1: The 42 Ball Machine */}
        <div className="relative w-44 h-44 flex-shrink-0">
          <div 
            className="absolute inset-0 rounded-2xl overflow-hidden"
            style={{
              background: 'linear-gradient(180deg, rgba(255,255,255,0.9) 0%, rgba(255,248,240,0.95) 100%)',
              boxShadow: 'inset 0 0 20px rgba(0,0,0,0.1), 0 8px 30px rgba(0,0,0,0.1)',
              border: '3px solid #FFD700'
            }}
          >
            {/* Balls inside */}
            {balls.map((ball) => (
              <div
                key={ball.number}
                className="absolute"
                style={{
                  left: `${ball.x}%`,
                  top: `${ball.y}%`,
                  transform: 'translate(-50%, -50%)',
                  transition: phase === 'spinning' ? 'none' : 'all 0.3s ease'
                }}
              >
                <Ball 
                  number={ball.number} 
                  size="xs"
                  isSpinning={phase === 'spinning'}
                />
              </div>
            ))}
          </div>
          {/* Label */}
          <div className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap">
            <span className="text-xs font-bold text-amber-600">🎱 42 Balls</span>
          </div>
          {/* Bottom decoration */}
          <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-12 h-3 bg-gradient-to-r from-amber-400 to-amber-500 rounded-b-lg" />
        </div>

        {/* Arrow */}
        <div className="text-2xl text-amber-400 animate-pulse">→</div>

        {/* Box 2: Lucky 6 Result Box */}
        <div className="relative w-44 h-44 flex-shrink-0">
          <div 
            className="absolute inset-0 rounded-2xl flex items-center justify-center"
            style={{
              background: 'linear-gradient(180deg, #FFF9E6 0%, #FFF3CD 100%)',
              boxShadow: 'inset 0 0 20px rgba(255,184,0,0.1), 0 8px 30px rgba(0,0,0,0.08)',
              border: '3px solid #FFD700'
            }}
          >
            {/* Floating emojis */}
            <span className="absolute top-2 left-2 text-lg animate-bounce">🍀</span>
            <span className="absolute top-2 right-2 text-lg animate-bounce" style={{animationDelay: '0.3s'}}>🤞</span>
            <span className="absolute bottom-2 left-2 text-sm animate-pulse">✨</span>
            <span className="absolute bottom-2 right-2 text-sm animate-pulse" style={{animationDelay: '0.5s'}}>🌟</span>
            
            {/* Center content */}
            <div className="text-center">
              <span className="text-lg font-bold text-amber-600">LUCKY</span>
              <div className="text-4xl font-bold text-amber-500">6</div>
              {phase === 'spinning' && (
                <span className="text-xs text-amber-500 animate-pulse">🤞 Mixing...</span>
              )}
            </div>
          </div>
          {/* Label */}
          <div className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap">
            <span className="text-xs font-bold text-amber-600">🍀 Winners</span>
          </div>
          {/* Bottom decoration */}
          <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-12 h-3 bg-gradient-to-r from-amber-400 to-amber-500 rounded-b-lg" />
        </div>
      </div>

      {/* Winning balls - horizontal row below the boxes */}
      <div 
        className="p-4 rounded-2xl min-h-[70px] flex items-center justify-center"
        style={{
          background: showResults ? 'linear-gradient(180deg, #FFF9E6 0%, #FFF3CD 100%)' : 'transparent',
          boxShadow: showResults ? '0 4px 20px rgba(0,0,0,0.08)' : 'none',
          border: showResults ? '3px solid #FFD700' : '3px dashed #FFD70050',
          minWidth: '320px'
        }}
      >
        {showResults && winningNumbers.length > 0 ? (
          <div className="flex gap-3">
            {winningNumbers.map((num, i) => (
              <div 
                key={num}
                className="ball-jump-in"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <Ball number={num} size="md" isWinner={true} />
              </div>
            ))}
          </div>
        ) : (
          <span className="text-amber-300 text-sm">
            {phase === 'spinning' ? '🎰 Drawing your lucky numbers...' : '🍀 Your lucky numbers will appear here 🤞'}
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
          <span className="text-3xl animate-bounce">🍀</span>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent">
            Lucky Jack
          </h1>
          <span className="text-3xl animate-bounce" style={{animationDelay: '0.2s'}}>🤞</span>
        </div>
        <p className="text-gray-400 text-sm">✨ Your Lucky Number Generator ✨</p>
      </header>

      {/* Main Content */}
      <main className="max-w-lg mx-auto px-4">
        {/* Ball Machine Card */}
        <div className="lucky-card p-6 mb-6">
          <h2 className="text-xl font-bold text-center text-gray-800 mb-6">
            ✨ Your Lucky Numbers ✨
          </h2>
          
          {/* Ball Machine + Result Slots */}
          <BallMachine 
            isProcessing={loading}
            winningNumbers={prediction?.main_prediction || []}
          />
          
          {/* Prompt text */}
          <div className="text-center mt-8 mb-4">
            {!loading && !prediction && (
              <p className="text-gray-400 text-sm">🤞 Press the button to get lucky numbers! 🍀</p>
            )}
            {prediction && !loading && (
              <span className="inline-flex items-center gap-2 bg-gradient-to-r from-amber-100 to-orange-100 px-4 py-2 rounded-full text-sm">
                <span>🍀</span>
                <span className="font-semibold text-amber-700">
                  {'⭐'.repeat(Math.min(5, Math.ceil(prediction.average_confidence / 20)))} Magic!
                </span>
                <span>🤞</span>
              </span>
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
            <span className="font-semibold text-gray-700">🎂 Personalize Your Luck 🤞</span>
            {showPersonal ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
          </div>
          
          {showPersonal && (
            <div className="mt-4 space-y-3">
              <div>
                <label className="text-xs text-gray-500 mb-1 block">🎂 Birthday</label>
                <input
                  type="text"
                  value={birthday}
                  onChange={(e) => setBirthday(e.target.value)}
                  placeholder="DD/MM/YYYY"
                  className="w-full px-4 py-2 rounded-xl border border-amber-200 focus:border-amber-400 outline-none text-sm"
                  data-testid="birthday-input"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">🔤 Full Name (optional)</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                  className="w-full px-4 py-2 rounded-xl border border-amber-200 focus:border-amber-400 outline-none text-sm"
                  data-testid="name-input"
                />
              </div>
              
              {/* Birthday Generate Button */}
              <button 
                onClick={fetchPrediction}
                disabled={loading || !birthday}
                className={`w-full py-3 rounded-xl font-bold text-white flex items-center justify-center gap-2 transition-all duration-300 ${
                  birthday 
                    ? 'bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5' 
                    : 'bg-gray-300 cursor-not-allowed'
                }`}
                data-testid="birthday-generate-btn"
              >
                {loading ? (
                  <>
                    <Sparkles className="w-5 h-5 animate-spin" />
                    <span>🎂 Generating Your Birthday Magic...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>🎂 Generate with Birthday Magic! ✨</span>
                  </>
                )}
              </button>
              
              {(prediction?.birthday_mode || prediction?.name_mode) && (
                <div className="bg-gradient-to-r from-pink-50 to-rose-50 rounded-xl p-3 text-xs border border-pink-200">
                  {prediction.birthday_mode && (
                    <div className="flex items-center gap-2 text-pink-700">
                      <span>🎂</span>
                      <span className="font-semibold">Birthday numbers:</span>
                      <span>{prediction.birthday_mode.lucky_numbers.slice(0, 4).join(", ")}</span>
                    </div>
                  )}
                  {prediction.name_mode && (
                    <div className="flex items-center gap-2 text-rose-700 mt-1">
                      <span>🔤</span>
                      <span className="font-semibold">Name numbers:</span>
                      <span>{prediction.name_mode.lucky_numbers.slice(0, 4).join(", ")}</span>
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
              <span className="font-semibold text-gray-700 flex items-center gap-2">
                <Gift className="w-4 h-4 text-amber-500" /> Bonus Numbers
              </span>
              {showBonus ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
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
        <div className="text-center text-gray-400 text-xs mt-6">
          <p>🍀 Good luck! Play responsibly 🤞</p>
          <p className="mt-1 text-gray-300">May fortune smile upon you ✨</p>
        </div>
      </main>
    </div>
  );
}

export default App;
