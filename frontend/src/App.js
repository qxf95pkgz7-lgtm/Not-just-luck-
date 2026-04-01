import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Sparkles, Star, Gift, RefreshCw, ChevronDown, ChevronUp } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Lucky Ball Component with fun colors
const LuckyBall = ({ number, size = "md", delay = 0 }) => {
  const colors = [
    "from-amber-400 to-orange-500",
    "from-emerald-400 to-green-500", 
    "from-sky-400 to-blue-500",
    "from-pink-400 to-rose-500",
    "from-violet-400 to-purple-500",
    "from-teal-400 to-cyan-500"
  ];
  
  const colorIndex = (number - 1) % colors.length;
  
  const sizeClasses = {
    sm: "w-10 h-10 text-sm",
    md: "w-14 h-14 text-lg",
    lg: "w-20 h-20 text-2xl"
  };
  
  return (
    <div 
      className={`${sizeClasses[size]} rounded-full flex items-center justify-center font-bold text-white shadow-lg bg-gradient-to-br ${colors[colorIndex]} transform hover:scale-110 transition-all duration-300`}
      style={{ 
        animationDelay: `${delay}ms`,
        boxShadow: '0 4px 15px rgba(0,0,0,0.15), inset 0 -3px 10px rgba(0,0,0,0.1)'
      }}
    >
      {number}
    </div>
  );
};

// Spinning Lucky Wheel
const SpinningWheel = ({ numbers, isSpinning }) => {
  return (
    <div className="relative w-64 h-64 mx-auto my-8">
      {/* Outer ring */}
      <div 
        className={`absolute inset-0 rounded-full border-8 border-amber-300 ${isSpinning ? 'spin-slow' : ''}`}
        style={{
          background: 'conic-gradient(from 0deg, #FFD700, #FF9500, #FF6B6B, #A78BFA, #60A5FA, #4ADE80, #FFD700)'
        }}
      />
      
      {/* Inner circle */}
      <div className="absolute inset-4 rounded-full bg-gradient-to-br from-amber-50 to-orange-50 flex items-center justify-center shadow-inner">
        <div className="text-center">
          <div className="flex flex-wrap justify-center gap-2 p-4">
            {numbers.slice(0, 6).map((n, i) => (
              <LuckyBall key={i} number={n} size="sm" delay={i * 100} />
            ))}
          </div>
        </div>
      </div>
      
      {/* Decorative stars */}
      <Sparkles className="absolute -top-4 -right-4 w-8 h-8 text-amber-400 float" />
      <Star className="absolute -bottom-2 -left-2 w-6 h-6 text-amber-400 float" style={{animationDelay: '0.5s'}} />
      <Sparkles className="absolute top-1/2 -right-6 w-6 h-6 text-amber-400 float" style={{animationDelay: '1s'}} />
    </div>
  );
};

// Simple Stats Card
const StatCard = ({ label, value, icon, color = "amber" }) => {
  const colors = {
    amber: "from-amber-400 to-orange-500",
    green: "from-emerald-400 to-green-500",
    blue: "from-sky-400 to-blue-500",
    pink: "from-pink-400 to-rose-500"
  };
  
  return (
    <div className="lucky-card p-4 text-center">
      <div className={`w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-br ${colors[color]} flex items-center justify-center text-white`}>
        {icon}
      </div>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
};

// Main App
function App() {
  const [prediction, setPrediction] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [spinning, setSpinning] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  
  // Personal mode
  const [birthday, setBirthday] = useState("");
  const [fullName, setFullName] = useState("");
  const [usePersonal, setUsePersonal] = useState(false);

  const fetchPrediction = useCallback(async () => {
    try {
      setLoading(true);
      setSpinning(true);
      
      let url = `${API}/master-predictor`;
      const params = [];
      if (usePersonal && birthday) params.push(`birthday=${encodeURIComponent(birthday)}`);
      if (usePersonal && fullName) params.push(`name=${encodeURIComponent(fullName)}`);
      if (params.length > 0) url += `?${params.join('&')}`;
      
      // Add delay for spinning effect
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const res = await axios.get(url);
      setPrediction(res.data);
    } catch (e) {
      console.error("Error:", e);
    } finally {
      setLoading(false);
      setSpinning(false);
    }
  }, [birthday, fullName, usePersonal]);

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
    fetchPrediction();
  }, []);

  return (
    <div className="min-h-screen pb-10">
      {/* Header */}
      <header className="text-center py-8">
        <div className="flex items-center justify-center gap-3 mb-2">
          <span className="text-4xl">🍀</span>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent">
            Lucky Jack
          </h1>
          <span className="text-4xl">🎰</span>
        </div>
        <p className="text-gray-500">Swiss Lotto Pattern Analyzer</p>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4">
        {/* Quick Stats */}
        {stats && (
          <div className="grid grid-cols-2 gap-4 mb-8">
            <StatCard 
              label="Total Draws" 
              value={stats.total_draws.toLocaleString()} 
              icon={<span className="text-lg">📊</span>}
              color="amber"
            />
            <StatCard 
              label="Draw Position" 
              value={`#${stats.total_draws + 1}`} 
              icon={<span className="text-lg">🎯</span>}
              color="green"
            />
          </div>
        )}

        {/* Lucky Wheel with Prediction */}
        <div className="lucky-card p-8 mb-8">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
            ✨ Your Lucky Numbers ✨
          </h2>
          <p className="text-center text-gray-500 mb-4">
            {prediction ? `Draw #${prediction.for_draw.draw_number}` : 'Loading...'}
          </p>
          
          {/* Spinning Wheel */}
          <SpinningWheel 
            numbers={prediction?.main_prediction || [1, 2, 3, 4, 5, 6]} 
            isSpinning={spinning}
          />
          
          {/* Confidence */}
          {prediction && (
            <div className="text-center mt-4">
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-amber-100 to-orange-100 px-6 py-3 rounded-full">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <span className="font-bold text-amber-700">
                  {prediction.average_confidence}% Lucky Score
                </span>
              </div>
            </div>
          )}
          
          {/* Generate Button */}
          <div className="text-center mt-6">
            <button 
              onClick={fetchPrediction}
              disabled={loading}
              className="lucky-btn flex items-center gap-2 mx-auto"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Finding Lucky Numbers...' : 'Get New Prediction'}
            </button>
          </div>
        </div>

        {/* Personal Mode Card */}
        <div className="lucky-card p-6 mb-8">
          <div 
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setUsePersonal(!usePersonal)}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">✨</span>
              <h3 className="font-bold text-gray-800">Personalize Your Luck</h3>
            </div>
            {usePersonal ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
          </div>
          
          {usePersonal && (
            <div className="mt-4 space-y-4">
              <div>
                <label className="text-sm text-gray-500 mb-1 block">🎂 Birthday</label>
                <input
                  type="text"
                  value={birthday}
                  onChange={(e) => setBirthday(e.target.value)}
                  placeholder="DD/MM/YYYY"
                  className="w-full px-4 py-3 rounded-xl border border-amber-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-100 outline-none transition-all"
                />
              </div>
              <div>
                <label className="text-sm text-gray-500 mb-1 block">🔤 Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                  className="w-full px-4 py-3 rounded-xl border border-amber-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-100 outline-none transition-all"
                />
              </div>
              
              {(prediction?.birthday_mode || prediction?.name_mode) && (
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 space-y-2">
                  {prediction.birthday_mode && (
                    <p className="text-sm text-amber-700">
                      🎂 Lucky from birthday: {prediction.birthday_mode.lucky_numbers.slice(0, 5).join(", ")}
                    </p>
                  )}
                  {prediction.name_mode && (
                    <p className="text-sm text-amber-700">
                      🔤 Lucky from name: {prediction.name_mode.lucky_numbers.slice(0, 5).join(", ")}
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Alternate Numbers */}
        {prediction && (
          <div className="lucky-card p-6 mb-8">
            <div 
              className="flex items-center justify-between cursor-pointer"
              onClick={() => setShowDetails(!showDetails)}
            >
              <div className="flex items-center gap-3">
                <Gift className="w-6 h-6 text-amber-500" />
                <h3 className="font-bold text-gray-800">Bonus Numbers</h3>
              </div>
              {showDetails ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
            </div>
            
            {showDetails && (
              <div className="mt-4">
                <div className="flex flex-wrap justify-center gap-3">
                  {prediction.alternate_numbers.map((n, i) => (
                    <LuckyBall key={i} number={n} size="sm" delay={i * 50} />
                  ))}
                </div>
                
                {/* Last Draw */}
                {prediction.last_draw && (
                  <div className="mt-6 text-center">
                    <p className="text-sm text-gray-500 mb-2">Last Draw ({prediction.last_draw.date})</p>
                    <div className="flex flex-wrap justify-center gap-2">
                      {prediction.last_draw.numbers.map((n, i) => (
                        <div key={i} className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center font-bold text-gray-600 text-sm">
                          {n}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-gray-400 text-sm mt-8">
          <p>🍀 Good luck! Play responsibly 🎰</p>
          <p className="mt-1">Based on {stats?.total_draws.toLocaleString() || '...'} real Swiss Lotto draws</p>
        </div>
      </main>
    </div>
  );
}

export default App;
