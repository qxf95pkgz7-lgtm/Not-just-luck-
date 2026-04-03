import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Sparkles, RefreshCw, ChevronDown, ChevronUp, Star, Upload } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL || "http://localhost:8002";

// Ball component for main numbers (1-50)
const Ball = ({ number, size = "md", isWinner = false }) => {
  const sizeClasses = {
    xs: "w-8 h-8 text-xs",
    sm: "w-10 h-10 text-sm",
    md: "w-12 h-12 text-base",
    lg: "w-14 h-14 text-lg"
  };
  
  // Color based on decade
  const getColor = (n) => {
    if (n <= 10) return "from-blue-500 to-blue-700";
    if (n <= 20) return "from-green-500 to-green-700";
    if (n <= 30) return "from-yellow-500 to-yellow-700";
    if (n <= 40) return "from-orange-500 to-orange-700";
    return "from-red-500 to-red-700";
  };
  
  return (
    <div className={`
      ${sizeClasses[size]} 
      rounded-full 
      bg-gradient-to-br ${getColor(number)}
      flex items-center justify-center 
      font-bold text-white
      shadow-lg
      ${isWinner ? 'ring-2 ring-yellow-400 animate-pulse' : ''}
    `}>
      {number}
    </div>
  );
};

// Star component for star numbers (1-12)
const StarBall = ({ number, size = "md" }) => {
  const sizeClasses = {
    sm: "w-10 h-10 text-sm",
    md: "w-12 h-12 text-base",
    lg: "w-14 h-14 text-lg"
  };
  
  return (
    <div className={`
      ${sizeClasses[size]}
      flex items-center justify-center
      relative
    `}>
      <Star className="absolute w-full h-full text-yellow-400 fill-yellow-400" />
      <span className="relative z-10 font-bold text-yellow-900">{number}</span>
    </div>
  );
};

// Physics-based Ball Machine
const BallMachine = ({ isProcessing, mainNumbers, starNumbers }) => {
  const [phase, setPhase] = useState('idle');
  const [selectedMain, setSelectedMain] = useState([]);
  const [selectedStars, setSelectedStars] = useState([]);
  
  useEffect(() => {
    if (isProcessing) {
      setPhase('spinning');
      setSelectedMain([]);
      setSelectedStars([]);
      
      // Animate main numbers one by one
      mainNumbers.forEach((num, idx) => {
        setTimeout(() => {
          setSelectedMain(prev => [...prev, num]);
        }, (idx + 1) * 1500);
      });
      
      // Animate stars after main numbers
      starNumbers.forEach((num, idx) => {
        setTimeout(() => {
          setSelectedStars(prev => [...prev, num]);
        }, (mainNumbers.length + idx + 1) * 1500);
      });
      
      // Complete
      setTimeout(() => {
        setPhase('complete');
      }, (mainNumbers.length + starNumbers.length + 1) * 1500);
    }
  }, [isProcessing, mainNumbers, starNumbers]);
  
  return (
    <div className="relative">
      {/* Machine Container */}
      <div className="bg-gradient-to-b from-slate-800 to-slate-900 rounded-3xl p-6 border border-slate-700">
        {/* Glass Dome */}
        <div className="relative h-48 bg-gradient-to-b from-slate-700/50 to-slate-800/50 rounded-full mx-auto w-64 border border-slate-600 overflow-hidden">
          {/* Floating balls animation */}
          <div className="absolute inset-0 flex flex-wrap justify-center items-center gap-1 p-4">
            {Array.from({length: 20}, (_, i) => (
              <div 
                key={i}
                className={`w-4 h-4 rounded-full opacity-60 ${
                  phase === 'spinning' ? 'animate-bounce' : ''
                }`}
                style={{
                  backgroundColor: ['#3b82f6', '#22c55e', '#eab308', '#f97316', '#ef4444'][i % 5],
                  animationDelay: `${i * 0.1}s`
                }}
              />
            ))}
          </div>
          
          {/* Center glow */}
          {phase === 'spinning' && (
            <div className="absolute inset-0 bg-blue-500/20 animate-pulse" />
          )}
        </div>
        
        {/* Selected Numbers Display */}
        <div className="mt-6 space-y-4">
          {/* Main Numbers */}
          <div className="flex justify-center gap-2">
            {[0,1,2,3,4].map(idx => (
              <div key={idx} className="relative">
                {selectedMain[idx] ? (
                  <Ball number={selectedMain[idx]} isWinner={true} />
                ) : (
                  <div className="w-12 h-12 rounded-full bg-slate-700/50 border-2 border-dashed border-slate-600 flex items-center justify-center text-slate-500">
                    ?
                  </div>
                )}
              </div>
            ))}
          </div>
          
          {/* Stars */}
          <div className="flex justify-center gap-3">
            {[0,1].map(idx => (
              <div key={idx}>
                {selectedStars[idx] ? (
                  <StarBall number={selectedStars[idx]} />
                ) : (
                  <div className="w-12 h-12 flex items-center justify-center">
                    <Star className="w-10 h-10 text-slate-600" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
        
        {/* Status */}
        <div className="text-center mt-4">
          {phase === 'idle' && (
            <span className="text-slate-400 text-sm">Press button to generate</span>
          )}
          {phase === 'spinning' && (
            <span className="text-blue-400 text-sm animate-pulse">
              🌪️ Selecting numbers... ({selectedMain.length}/5 + {selectedStars.length}/2 ⭐)
            </span>
          )}
          {phase === 'complete' && (
            <span className="text-emerald-400 text-sm">✓ Your EuroMillions numbers!</span>
          )}
        </div>
      </div>
    </div>
  );
};

// Main App
function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showLocks, setShowLocks] = useState(false);
  const [showMultiTickets, setShowMultiTickets] = useState(false);
  const [stats, setStats] = useState(null);
  
  // Locked positions
  const [lockedMain, setLockedMain] = useState({ p1: "", p2: "", p3: "", p4: "", p5: "" });
  const [lockedStars, setLockedStars] = useState({ s1: "", s2: "" });
  const [numTickets, setNumTickets] = useState(1);
  
  const getLockedMainCount = () => Object.values(lockedMain).filter(v => v !== "").length;
  const getLockedStarCount = () => Object.values(lockedStars).filter(v => v !== "").length;
  
  const handleMainLockChange = (pos, value) => {
    const num = parseInt(value);
    if (value === "" || (num >= 1 && num <= 50)) {
      if (value !== "" && getLockedMainCount() >= 4 && lockedMain[pos] === "") return;
      setLockedMain(prev => ({...prev, [pos]: value}));
    }
  };
  
  const handleStarLockChange = (pos, value) => {
    const num = parseInt(value);
    if (value === "" || (num >= 1 && num <= 12)) {
      setLockedStars(prev => ({...prev, [pos]: value}));
    }
  };
  
  const fetchPrediction = useCallback(async () => {
    try {
      setLoading(true);
      
      let url = `${API}/master-predictor`;
      const params = [];
      
      if (lockedMain.p1) params.push(`lock_p1=${lockedMain.p1}`);
      if (lockedMain.p2) params.push(`lock_p2=${lockedMain.p2}`);
      if (lockedMain.p3) params.push(`lock_p3=${lockedMain.p3}`);
      if (lockedMain.p4) params.push(`lock_p4=${lockedMain.p4}`);
      if (lockedMain.p5) params.push(`lock_p5=${lockedMain.p5}`);
      if (lockedStars.s1) params.push(`lock_star1=${lockedStars.s1}`);
      if (lockedStars.s2) params.push(`lock_star2=${lockedStars.s2}`);
      if (numTickets > 1) params.push(`num_tickets=${numTickets}`);
      
      if (params.length > 0) url += `?${params.join('&')}`;
      
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const res = await axios.get(url);
      setPrediction(res.data);
    } catch (e) {
      console.error("Error:", e);
      // Fallback random
      const mainNums = [];
      while (mainNums.length < 5) {
        const n = Math.floor(Math.random() * 50) + 1;
        if (!mainNums.includes(n)) mainNums.push(n);
      }
      const stars = [];
      while (stars.length < 2) {
        const n = Math.floor(Math.random() * 12) + 1;
        if (!stars.includes(n)) stars.push(n);
      }
      setPrediction({
        main_prediction: mainNums.sort((a,b) => a-b),
        star_prediction: stars.sort((a,b) => a-b),
        average_confidence: 50
      });
    } finally {
      setLoading(false);
    }
  }, [lockedMain, lockedStars, numTickets]);
  
  useEffect(() => {
    axios.get(`${API}/dashboard`).then(res => setStats(res.data)).catch(() => {});
  }, []);
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-blue-950 to-slate-900 text-white">
      {/* Header */}
      <header className="py-6 px-4 text-center border-b border-blue-800/30">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-yellow-400 to-blue-400 bg-clip-text text-transparent">
          🌟 EuroMillions Pattern Analyzer
        </h1>
        <p className="text-blue-300/70 mt-1">5 Numbers (1-50) + 2 Stars (1-12)</p>
        {stats?.total_draws > 0 && (
          <p className="text-xs text-slate-500 mt-1">{stats.total_draws} historical draws loaded</p>
        )}
      </header>
      
      <main className="max-w-2xl mx-auto p-4 space-y-6">
        {/* Ball Machine */}
        <BallMachine 
          isProcessing={loading}
          mainNumbers={prediction?.main_prediction || []}
          starNumbers={prediction?.star_prediction || []}
        />
        
        {/* Generate Button */}
        <button
          onClick={fetchPrediction}
          disabled={loading}
          className="w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all duration-300 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:opacity-50 shadow-lg shadow-blue-900/50"
          data-testid="generate-btn"
        >
          <RefreshCw className={`w-6 h-6 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Generating...' : 'Generate EuroMillions Numbers'}
        </button>
        
        {/* Lock Positions */}
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <div 
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setShowLocks(!showLocks)}
            data-testid="lock-toggle"
          >
            <span className="font-semibold flex items-center gap-2">
              🔒 Lock Positions
              {(getLockedMainCount() > 0 || getLockedStarCount() > 0) && (
                <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full">
                  {getLockedMainCount()}/4 + {getLockedStarCount()}/2⭐
                </span>
              )}
            </span>
            {showLocks ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </div>
          
          {showLocks && (
            <div className="mt-4 space-y-4">
              {/* Main number locks */}
              <div>
                <p className="text-xs text-slate-400 mb-2">Main Numbers (1-50)</p>
                <div className="grid grid-cols-5 gap-2">
                  {['p1', 'p2', 'p3', 'p4', 'p5'].map((pos, idx) => (
                    <div key={pos} className="text-center">
                      <label className="text-xs text-slate-500">P{idx + 1}</label>
                      <input
                        type="number"
                        min="1"
                        max="50"
                        value={lockedMain[pos]}
                        onChange={(e) => handleMainLockChange(pos, e.target.value)}
                        placeholder="—"
                        className={`w-full px-1 py-2 rounded-lg text-center text-sm font-bold
                          ${lockedMain[pos] ? 'bg-blue-500/20 border-blue-500/50 text-blue-400' : 'bg-slate-700/50 border-slate-600 text-white'}
                          border focus:outline-none`}
                        data-testid={`lock-${pos}`}
                      />
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Star locks */}
              <div>
                <p className="text-xs text-slate-400 mb-2">Star Numbers (1-12)</p>
                <div className="grid grid-cols-2 gap-2 max-w-[200px] mx-auto">
                  {['s1', 's2'].map((pos, idx) => (
                    <div key={pos} className="text-center">
                      <label className="text-xs text-yellow-500">⭐{idx + 1}</label>
                      <input
                        type="number"
                        min="1"
                        max="12"
                        value={lockedStars[pos]}
                        onChange={(e) => handleStarLockChange(pos, e.target.value)}
                        placeholder="—"
                        className={`w-full px-1 py-2 rounded-lg text-center text-sm font-bold
                          ${lockedStars[pos] ? 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400' : 'bg-slate-700/50 border-slate-600 text-white'}
                          border focus:outline-none`}
                        data-testid={`lock-${pos}`}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Multiple Tickets */}
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <div 
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setShowMultiTickets(!showMultiTickets)}
            data-testid="multi-tickets-toggle"
          >
            <span className="font-semibold flex items-center gap-2">
              🎫 Multiple Tickets
              {numTickets > 1 && (
                <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full">
                  {numTickets} tickets
                </span>
              )}
            </span>
            {showMultiTickets ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </div>
          
          {showMultiTickets && (
            <div className="mt-4">
              <p className="text-xs text-slate-400 mb-3">
                Generate multiple tickets. <span className="text-yellow-400">€2.50 per ticket</span>
              </p>
              
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm">How many?</span>
                  <span className="text-xs text-yellow-400 font-semibold">
                    Total: €{(numTickets * 2.5).toFixed(2)}
                  </span>
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {[1, 3, 5, 8, 10, 15, 20].map(n => (
                    <button
                      key={n}
                      onClick={() => setNumTickets(n)}
                      className={`flex flex-col items-center px-2 py-1.5 rounded-lg text-sm font-medium transition-all
                        ${numTickets === n ? 'bg-emerald-500 text-white' : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'}`}
                      data-testid={`tickets-${n}`}
                    >
                      <span className="font-bold">{n}</span>
                      <span className={`text-[10px] ${numTickets === n ? 'text-emerald-100' : 'text-slate-500'}`}>
                        €{(n * 2.5).toFixed(1)}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Display tickets */}
              {prediction?.all_tickets && prediction.all_tickets.length > 1 && (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {prediction.all_tickets.map((ticket, idx) => (
                    <div 
                      key={idx}
                      className={`flex items-center gap-2 p-2 rounded-lg ${
                        idx === 0 ? 'bg-gradient-to-r from-yellow-500/20 to-yellow-600/10 border border-yellow-500/30' : 'bg-slate-800/50'
                      }`}
                    >
                      <span className={`text-xs font-bold w-6 ${idx === 0 ? 'text-yellow-400' : 'text-slate-500'}`}>
                        #{ticket.ticket_num}
                      </span>
                      <div className="flex gap-1 flex-1">
                        {ticket.main_numbers.map((num, i) => (
                          <Ball key={i} number={num} size="xs" />
                        ))}
                        <span className="mx-1 text-slate-500">+</span>
                        {ticket.stars.map((num, i) => (
                          <StarBall key={i} number={num} size="sm" />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <button 
                onClick={fetchPrediction}
                disabled={loading}
                className="mt-4 w-full py-2.5 rounded-xl font-bold flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white hover:from-emerald-400 hover:to-emerald-500"
                data-testid="generate-tickets-btn"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Generate {numTickets} Ticket{numTickets > 1 ? 's' : ''}
              </button>
            </div>
          )}
        </div>
        
        {/* Stats */}
        {stats?.total_draws > 0 && (
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
            <h3 className="font-semibold mb-3">📊 Statistics ({stats.total_draws} draws)</h3>
            
            {stats.last_draw && (
              <div className="mb-4">
                <p className="text-xs text-slate-400 mb-1">Last Draw: {stats.last_draw.date}</p>
                <div className="flex gap-2 items-center">
                  {stats.last_draw.numbers?.map((n, i) => (
                    <Ball key={i} number={n} size="sm" />
                  ))}
                  <span className="text-slate-500">+</span>
                  {stats.last_draw.stars?.map((s, i) => (
                    <StarBall key={i} number={s} size="sm" />
                  ))}
                </div>
              </div>
            )}
            
            {stats.hot_main && (
              <div className="text-sm">
                <span className="text-slate-400">Hot numbers: </span>
                <span className="text-red-400">
                  {stats.hot_main.slice(0, 5).map(([n]) => n).join(', ')}
                </span>
              </div>
            )}
          </div>
        )}
        
        {/* No Data Message */}
        {stats?.total_draws === 0 && (
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 text-center">
            <Upload className="w-8 h-8 mx-auto mb-2 text-yellow-400" />
            <p className="text-yellow-400 font-semibold">No Historical Data</p>
            <p className="text-sm text-slate-400 mt-1">
              Import EuroMillions draw history to enable pattern analysis
            </p>
          </div>
        )}
        
        {/* Footer */}
        <footer className="text-center text-xs text-slate-500 py-4">
          Good luck! Play responsibly 🍀
        </footer>
      </main>
    </div>
  );
}

export default App;
