import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Ball colors for main numbers (1-50)
const getMainBallColor = (num) => {
  if (num <= 10) return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  if (num <= 20) return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
  if (num <= 30) return 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
  if (num <= 40) return 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)';
  return 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)';
};

// Star colors
const STAR_COLOR = 'linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%)';

function App() {
  const [draws, setDraws] = useState([]);
  const [stats, setStats] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [spinning, setSpinning] = useState(false);
  const [showNumbers, setShowNumbers] = useState(false);
  const [birthday, setBirthday] = useState('');
  const [name, setName] = useState('');
  const [numTickets, setNumTickets] = useState(1);
  const [lockedPositions, setLockedPositions] = useState({});
  const [activeTab, setActiveTab] = useState('predictor');
  const [analyzeNumbers, setAnalyzeNumbers] = useState('');
  const [analyzeStars, setAnalyzeStars] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);

  useEffect(() => {
    fetchDraws();
    fetchStats();
  }, []);

  const fetchDraws = async () => {
    try {
      const res = await fetch(`${API_URL}/api/draws?limit=20`);
      const data = await res.json();
      setDraws(data.draws || []);
    } catch (err) {
      console.error('Failed to fetch draws:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/stats`);
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const generatePrediction = useCallback(async () => {
    setLoading(true);
    setSpinning(true);
    setShowNumbers(false);
    setPrediction(null);

    try {
      const res = await fetch(`${API_URL}/api/master-predictor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          birthday: birthday || null,
          name: name || null,
          num_tickets: numTickets,
          locked_positions: Object.keys(lockedPositions).length > 0 ? lockedPositions : null,
        }),
      });
      const data = await res.json();

      // Simulate spinning animation
      setTimeout(() => {
        setSpinning(false);
        setTimeout(() => {
          setPrediction(data);
          setShowNumbers(true);
          setLoading(false);
        }, 500);
      }, 3000);
    } catch (err) {
      console.error('Prediction failed:', err);
      setSpinning(false);
      setLoading(false);
    }
  }, [birthday, name, numTickets, lockedPositions]);

  const analyzeTicket = async () => {
    if (!analyzeNumbers || !analyzeStars) return;
    
    try {
      const res = await fetch(
        `${API_URL}/api/analyze-ticket?numbers=${encodeURIComponent(analyzeNumbers)}&stars=${encodeURIComponent(analyzeStars)}`
      );
      const data = await res.json();
      setAnalysisResult(data);
    } catch (err) {
      console.error('Analysis failed:', err);
    }
  };

  const handleLockPosition = (position, value) => {
    if (value && !isNaN(parseInt(value)) && parseInt(value) >= 1 && parseInt(value) <= 50) {
      setLockedPositions(prev => ({ ...prev, [position]: parseInt(value) }));
    } else {
      setLockedPositions(prev => {
        const newLocked = { ...prev };
        delete newLocked[position];
        return newLocked;
      });
    }
  };

  return (
    <div className="app" data-testid="euromillions-app">
      {/* Stars Background */}
      <div className="stars-bg">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="star-particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
            }}
          />
        ))}
      </div>

      {/* Header */}
      <header className="header">
        <div className="logo">
          <span className="star-icon">⭐</span>
          <h1>Lucky Stars</h1>
          <span className="star-icon">⭐</span>
        </div>
        <p className="subtitle">EuroMillions Pattern Analyzer</p>
        <p className="rules">5 Numbers (1-50) + 2 Stars (1-12)</p>
      </header>

      {/* Navigation */}
      <nav className="nav-tabs">
        <button
          data-testid="nav-predictor"
          className={`nav-tab ${activeTab === 'predictor' ? 'active' : ''}`}
          onClick={() => setActiveTab('predictor')}
        >
          🎰 Predictor
        </button>
        <button
          data-testid="nav-history"
          className={`nav-tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📊 History
        </button>
        <button
          data-testid="nav-analyze"
          className={`nav-tab ${activeTab === 'analyze' ? 'active' : ''}`}
          onClick={() => setActiveTab('analyze')}
        >
          🔍 Analyze
        </button>
        <button
          data-testid="nav-stats"
          className={`nav-tab ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          📈 Stats
        </button>
      </nav>

      <main className="main-content">
        {/* Predictor Tab */}
        {activeTab === 'predictor' && (
          <div className="predictor-section" data-testid="predictor-section">
            {/* Lottery Machine */}
            <div className="lottery-machine">
              <div className={`ball-chamber ${spinning ? 'spinning' : ''}`}>
                {/* Main Number Balls */}
                <div className="main-balls-container">
                  {[...Array(50)].map((_, i) => (
                    <div
                      key={i}
                      className={`ball main-ball ${spinning ? 'bouncing' : ''}`}
                      style={{
                        background: getMainBallColor(i + 1),
                        animationDelay: `${Math.random() * 0.5}s`,
                        left: `${10 + Math.random() * 80}%`,
                        top: `${10 + Math.random() * 60}%`,
                      }}
                    >
                      {i + 1}
                    </div>
                  ))}
                </div>

                {/* Star Balls */}
                <div className="star-balls-container">
                  {[...Array(12)].map((_, i) => (
                    <div
                      key={i}
                      className={`ball star-ball ${spinning ? 'bouncing' : ''}`}
                      style={{
                        background: STAR_COLOR,
                        animationDelay: `${Math.random() * 0.5}s`,
                        left: `${15 + Math.random() * 70}%`,
                        top: `${70 + Math.random() * 20}%`,
                      }}
                    >
                      ⭐{i + 1}
                    </div>
                  ))}
                </div>
              </div>

              {/* Result Display */}
              {showNumbers && prediction && (
                <div className="result-display" data-testid="prediction-result">
                  <h3>Your Lucky Numbers</h3>
                  <div className="result-numbers">
                    {prediction.tickets[0].numbers.map((num, i) => (
                      <div
                        key={i}
                        className="result-ball main"
                        style={{ background: getMainBallColor(num), animationDelay: `${i * 0.2}s` }}
                      >
                        {num}
                      </div>
                    ))}
                    <span className="separator">+</span>
                    {prediction.tickets[0].stars.map((star, i) => (
                      <div
                        key={`star-${i}`}
                        className="result-ball star"
                        style={{ background: STAR_COLOR, animationDelay: `${(5 + i) * 0.2}s` }}
                      >
                        {star}
                      </div>
                    ))}
                  </div>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${prediction.tickets[0].confidence * 100}%` }}
                    />
                    <span>{Math.round(prediction.tickets[0].confidence * 100)}% Confidence</span>
                  </div>
                </div>
              )}
            </div>

            {/* Controls */}
            <div className="controls-panel">
              {/* Personalization */}
              <div className="control-group">
                <h4>✨ Personalization</h4>
                <div className="input-row">
                  <input
                    type="text"
                    placeholder="Birthday (DD.MM.YYYY)"
                    value={birthday}
                    onChange={(e) => setBirthday(e.target.value)}
                    data-testid="birthday-input"
                  />
                  <input
                    type="text"
                    placeholder="Your Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    data-testid="name-input"
                  />
                </div>
              </div>

              {/* Lock Positions */}
              <div className="control-group">
                <h4>🔒 Lock Positions (P1-P5)</h4>
                <div className="lock-positions">
                  {['P1', 'P2', 'P3', 'P4', 'P5'].map((pos) => (
                    <div key={pos} className="lock-input">
                      <label>{pos}</label>
                      <input
                        type="number"
                        min="1"
                        max="50"
                        placeholder="-"
                        value={lockedPositions[pos] || ''}
                        onChange={(e) => handleLockPosition(pos, e.target.value)}
                        data-testid={`lock-${pos.toLowerCase()}`}
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Ticket Count */}
              <div className="control-group">
                <h4>🎫 Number of Tickets</h4>
                <div className="ticket-selector">
                  <input
                    type="range"
                    min="1"
                    max="20"
                    value={numTickets}
                    onChange={(e) => setNumTickets(parseInt(e.target.value))}
                    data-testid="ticket-slider"
                  />
                  <span className="ticket-count">{numTickets} ticket{numTickets > 1 ? 's' : ''}</span>
                  <span className="ticket-price">€{(numTickets * 2.5).toFixed(2)}</span>
                </div>
              </div>

              {/* Generate Button */}
              <button
                className={`generate-btn ${loading ? 'loading' : ''}`}
                onClick={generatePrediction}
                disabled={loading}
                data-testid="generate-btn"
              >
                {loading ? '✨ Generating...' : '🎰 Generate Lucky Numbers'}
              </button>
            </div>

            {/* Multiple Tickets Display */}
            {prediction && prediction.tickets.length > 1 && (
              <div className="tickets-grid" data-testid="tickets-grid">
                <h3>Your {prediction.total_tickets} Tickets (Total: €{prediction.total_price.toFixed(2)})</h3>
                <div className="tickets-list">
                  {prediction.tickets.map((ticket, idx) => (
                    <div key={idx} className="ticket-card">
                      <div className="ticket-header">
                        <span className="ticket-num">#{ticket.ticket_number}</span>
                        <span className="ticket-confidence">{Math.round(ticket.confidence * 100)}%</span>
                      </div>
                      <div className="ticket-numbers">
                        {ticket.numbers.map((num, i) => (
                          <span key={i} className="mini-ball main" style={{ background: getMainBallColor(num) }}>
                            {num}
                          </span>
                        ))}
                        <span className="mini-separator">+</span>
                        {ticket.stars.map((star, i) => (
                          <span key={`s-${i}`} className="mini-ball star" style={{ background: STAR_COLOR }}>
                            {star}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Patterns Used */}
            {prediction && (
              <div className="patterns-panel" data-testid="patterns-panel">
                <h4>🔮 Patterns Applied</h4>
                <div className="patterns-list">
                  {prediction.tickets[0].patterns_used.map((pattern, i) => (
                    <span key={i} className="pattern-tag">{pattern}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="history-section" data-testid="history-section">
            <h2>Recent EuroMillions Draws</h2>
            <div className="draws-list">
              {draws.map((draw, idx) => (
                <div key={idx} className="draw-card">
                  <span className="draw-date">{draw.date}</span>
                  <div className="draw-numbers">
                    {draw.numbers.map((num, i) => (
                      <span key={i} className="mini-ball main" style={{ background: getMainBallColor(num) }}>
                        {num}
                      </span>
                    ))}
                    <span className="mini-separator">+</span>
                    {draw.stars.map((star, i) => (
                      <span key={`s-${i}`} className="mini-ball star" style={{ background: STAR_COLOR }}>
                        {star}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analyze Tab */}
        {activeTab === 'analyze' && (
          <div className="analyze-section" data-testid="analyze-section">
            <h2>Analyze Your Ticket</h2>
            <div className="analyze-form">
              <div className="input-group">
                <label>Main Numbers (comma-separated)</label>
                <input
                  type="text"
                  placeholder="e.g., 5, 12, 23, 34, 45"
                  value={analyzeNumbers}
                  onChange={(e) => setAnalyzeNumbers(e.target.value)}
                  data-testid="analyze-numbers-input"
                />
              </div>
              <div className="input-group">
                <label>Star Numbers (comma-separated)</label>
                <input
                  type="text"
                  placeholder="e.g., 3, 9"
                  value={analyzeStars}
                  onChange={(e) => setAnalyzeStars(e.target.value)}
                  data-testid="analyze-stars-input"
                />
              </div>
              <button className="analyze-btn" onClick={analyzeTicket} data-testid="analyze-btn">
                🔍 Analyze Ticket
              </button>
            </div>

            {analysisResult && (
              <div className="analysis-result" data-testid="analysis-result">
                <div className="analysis-header">
                  <h3>Analysis Result</h3>
                  <div className={`rating ${analysisResult.rating?.toLowerCase()}`}>
                    {analysisResult.rating} ({analysisResult.score}/100)
                  </div>
                </div>
                <div className="analyzed-numbers">
                  {analysisResult.numbers?.map((num, i) => (
                    <span key={i} className="mini-ball main" style={{ background: getMainBallColor(num) }}>
                      {num}
                    </span>
                  ))}
                  <span className="mini-separator">+</span>
                  {analysisResult.stars?.map((star, i) => (
                    <span key={`s-${i}`} className="mini-ball star" style={{ background: STAR_COLOR }}>
                      {star}
                    </span>
                  ))}
                </div>
                <div className="insights-list">
                  {analysisResult.insights?.map((insight, i) => (
                    <div key={i} className="insight-item">{insight}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Stats Tab */}
        {activeTab === 'stats' && stats && (
          <div className="stats-section" data-testid="stats-section">
            <h2>Statistical Analysis</h2>
            
            <div className="stats-grid">
              <div className="stat-card">
                <h4>Total Draws Analyzed</h4>
                <span className="stat-value">{stats.total_draws}</span>
              </div>
              <div className="stat-card">
                <h4>Typical Sum Range</h4>
                <span className="stat-value">{stats.sum_stats?.min} - {stats.sum_stats?.max}</span>
                <span className="stat-sub">Avg: {stats.sum_stats?.avg}</span>
              </div>
              <div className="stat-card">
                <h4>Consecutive Pair Rate</h4>
                <span className="stat-value">{stats.consecutive_pair_rate}%</span>
              </div>
              <div className="stat-card">
                <h4>Circle Partner Rate</h4>
                <span className="stat-value">{stats.circle_partner_rate}%</span>
              </div>
            </div>

            <div className="frequency-section">
              <h3>Number Frequency (Top 15)</h3>
              <div className="frequency-bars">
                {stats.number_frequency && Object.entries(stats.number_frequency)
                  .slice(0, 15)
                  .map(([num, count]) => (
                    <div key={num} className="freq-item">
                      <span className="mini-ball main" style={{ background: getMainBallColor(parseInt(num)) }}>
                        {num}
                      </span>
                      <div className="freq-bar">
                        <div 
                          className="freq-fill" 
                          style={{ width: `${(count / stats.total_draws) * 100 * 5}%` }}
                        />
                      </div>
                      <span className="freq-count">{count}</span>
                    </div>
                  ))}
              </div>
            </div>

            <div className="frequency-section">
              <h3>Star Frequency</h3>
              <div className="frequency-bars">
                {stats.star_frequency && Object.entries(stats.star_frequency)
                  .map(([num, count]) => (
                    <div key={num} className="freq-item">
                      <span className="mini-ball star" style={{ background: STAR_COLOR }}>
                        {num}
                      </span>
                      <div className="freq-bar star">
                        <div 
                          className="freq-fill" 
                          style={{ width: `${(count / (stats.total_draws * 2)) * 100 * 6}%` }}
                        />
                      </div>
                      <span className="freq-count">{count}</span>
                    </div>
                  ))}
              </div>
            </div>

            <div className="distribution-section">
              <h3>Odd/Even Distribution</h3>
              <div className="distribution-chips">
                {stats.odd_even_distribution && Object.entries(stats.odd_even_distribution)
                  .sort((a, b) => b[1] - a[1])
                  .map(([ratio, freq]) => (
                    <div key={ratio} className="dist-chip">
                      <span className="dist-ratio">{ratio}</span>
                      <span className="dist-freq">{(freq * 100).toFixed(1)}%</span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Lucky Stars - EuroMillions Pattern Analyzer</p>
        <p className="disclaimer">For entertainment purposes only. Gambling involves risk.</p>
      </footer>
    </div>
  );
}

export default App;
