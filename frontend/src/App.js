import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { 
  LayoutDashboard, History, Link2, Target, Plus, RefreshCw, 
  TrendingUp, Hash, Clock, Trash2, X, Zap, Layers, Timer
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Number Ball Component
const NumberBall = ({ number, size = "md" }) => {
  const isLow = number <= 21;
  const sizeClasses = {
    sm: "w-8 h-8 text-sm",
    md: "w-10 h-10 text-base",
    lg: "w-14 h-14 text-xl"
  };
  
  return (
    <div 
      className={`${sizeClasses[size]} rounded-lg flex items-center justify-center font-mono font-bold ${
        isLow ? "bg-sky-500" : "bg-orange-500"
      } text-white shadow-lg`}
      data-testid={`number-ball-${number}`}
    >
      {number}
    </div>
  );
};

// Family Badge Component
const FamilyBadge = ({ family }) => (
  <span 
    className={`px-2 py-1 rounded text-xs font-mono ${
      family === 1 
        ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" 
        : "bg-orange-500/10 text-orange-400 border border-orange-500/20"
    }`}
  >
    {family}
  </span>
);

// Dashboard Tab
const Dashboard = ({ stats, onRefresh }) => {
  if (!stats) return <div className="text-center py-10 text-zinc-400">Loading...</div>;

  return (
    <div className="space-y-6" data-testid="dashboard-panel">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 text-sm">Total Draws</span>
            <Clock className="w-4 h-4 text-zinc-500" />
          </div>
          <p className="text-4xl font-mono font-bold text-sky-400 mt-2" data-testid="total-draws">
            {stats.total_draws}
          </p>
        </div>
        
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 text-sm">Rare Events</span>
            <Target className="w-4 h-4 text-zinc-500" />
          </div>
          <p className="text-4xl font-mono font-bold text-white mt-2">{stats.rare_events}</p>
          <span className="text-zinc-500 text-xs">Unusual positions detected</span>
        </div>
        
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 text-sm">Chain Links</span>
            <Link2 className="w-4 h-4 text-zinc-500" />
          </div>
          <p className="text-4xl font-mono font-bold text-white mt-2">{stats.chain_links}</p>
          <span className="text-zinc-500 text-xs">Number connections found</span>
        </div>
        
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 text-sm">Series Found</span>
            <TrendingUp className="w-4 h-4 text-zinc-500" />
          </div>
          <p className="text-4xl font-mono font-bold text-white mt-2">{stats.series_found}</p>
          <span className="text-zinc-500 text-xs">Consecutive patterns</span>
        </div>
      </div>

      {/* Number Groups */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <LayoutDashboard className="w-5 h-5" /> Number Groups
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-[#0F0F10] rounded-lg p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sky-400 font-medium">Group 1 (Low)</span>
              <span className="text-zinc-400 text-sm px-2 py-1 bg-[#18181A] rounded">1-21</span>
            </div>
            <p className="text-4xl font-mono font-bold text-white">{stats.group1_count}</p>
            <div className="mt-3 h-2 bg-[#27272A] rounded-full overflow-hidden">
              <div 
                className="h-full bg-sky-500 rounded-full transition-all duration-500"
                style={{ width: `${stats.group1_percentage}%` }}
              />
            </div>
            <span className="text-zinc-500 text-xs mt-1 block">{stats.group1_percentage}% of draws</span>
          </div>
          
          <div className="bg-[#0F0F10] rounded-lg p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-orange-400 font-medium">Group 2 (High)</span>
              <span className="text-zinc-400 text-sm px-2 py-1 bg-[#18181A] rounded">22-42</span>
            </div>
            <p className="text-4xl font-mono font-bold text-white">{stats.group2_count}</p>
            <div className="mt-3 h-2 bg-[#27272A] rounded-full overflow-hidden">
              <div 
                className="h-full bg-orange-500 rounded-full transition-all duration-500"
                style={{ width: `${stats.group2_percentage}%` }}
              />
            </div>
            <span className="text-zinc-500 text-xs mt-1 block">{stats.group2_percentage}% of draws</span>
          </div>
        </div>
      </div>

      {/* Hot & Cold Numbers */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-orange-400">
            <TrendingUp className="w-5 h-5" /> Hot Numbers
          </h3>
          <div className="flex flex-wrap gap-2">
            {stats.hot_numbers.map((item, i) => (
              <div key={i} className="flex items-center gap-1">
                <NumberBall number={item.number} size="sm" />
                <span className="text-zinc-500 text-xs font-mono">{item.count}x</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-sky-400">
            <Hash className="w-5 h-5" /> Cold Numbers
          </h3>
          <div className="flex flex-wrap gap-2">
            {stats.cold_numbers.map((item, i) => (
              <div key={i} className="flex items-center gap-1">
                <NumberBall number={item.number} size="sm" />
                <span className="text-zinc-500 text-xs font-mono">{item.count}x</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Last Draws */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5" /> Last Draws
        </h3>
        <div className="space-y-3">
          {stats.last_draws.map((draw, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b border-[#27272A]/50 last:border-0">
              <span className="text-zinc-400 font-mono text-sm">{draw.date}</span>
              <div className="flex gap-2">
                {draw.numbers.map((num, j) => (
                  <NumberBall key={j} number={num} size="sm" />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Draw History Tab
const DrawHistory = ({ draws, onDelete }) => {
  return (
    <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5" data-testid="draw-history-panel">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Clock className="w-5 h-5" /> Draw History
      </h3>
      
      <div className="overflow-x-auto">
        <table className="w-full" data-testid="draw-history-table">
          <thead>
            <tr className="text-xs uppercase tracking-wider text-zinc-400 border-b border-[#27272A]">
              <th className="text-left pb-3 font-medium">Date</th>
              <th className="text-left pb-3 font-medium">Draw #</th>
              <th className="text-left pb-3 font-medium">Numbers</th>
              <th className="text-left pb-3 font-medium">Families</th>
              <th className="text-right pb-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {draws.map((draw) => (
              <tr key={draw.id} className="border-b border-[#27272A]/50 hover:bg-[#27272A]/20">
                <td className="py-4 font-mono text-sm">{draw.date}</td>
                <td className="py-4 font-mono text-sm text-zinc-400">{draw.draw_number || "-"}</td>
                <td className="py-4">
                  <div className="flex gap-2">
                    {draw.numbers.map((num, i) => (
                      <NumberBall key={i} number={num} size="sm" />
                    ))}
                  </div>
                </td>
                <td className="py-4">
                  <div className="flex gap-1">
                    {draw.families.map((f, i) => (
                      <FamilyBadge key={i} family={f} />
                    ))}
                  </div>
                </td>
                <td className="py-4 text-right">
                  <button 
                    onClick={() => onDelete(draw.id)}
                    className="text-red-400 hover:text-red-300 p-2 hover:bg-red-500/10 rounded"
                    data-testid={`delete-draw-${draw.id}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {draws.length === 0 && (
        <div className="text-center py-10 text-zinc-500">
          No draws yet. Add your first draw!
        </div>
      )}
    </div>
  );
};

// Quarter Predictor Tab
const QuarterPredictor = ({ prediction, loading, onRefresh }) => {
  if (loading) return <div className="text-center py-10 text-zinc-400">Loading predictor...</div>;
  if (!prediction) return <div className="text-center py-10 text-zinc-400">Click refresh to load predictions</div>;

  const pos = prediction.next_draw_position;

  return (
    <div className="space-y-6" data-testid="quarter-predictor-panel">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-4 text-center">
          <span className="text-zinc-400 text-sm">Year</span>
          <p className="text-2xl font-mono font-bold text-white">{prediction.current_year}</p>
        </div>
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-4 text-center">
          <span className="text-zinc-400 text-sm">Draws This Year</span>
          <p className="text-2xl font-mono font-bold text-sky-400">{prediction.total_draws_this_year}</p>
        </div>
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-4 text-center">
          <span className="text-zinc-400 text-sm">Current Quarter</span>
          <p className="text-2xl font-mono font-bold text-orange-400">Q{prediction.current_quarter}</p>
        </div>
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-4 text-center">
          <span className="text-zinc-400 text-sm">Next Position</span>
          <p className="text-2xl font-mono font-bold text-green-400">{pos.from_top}/{pos.from_bottom}</p>
        </div>
      </div>

      {/* Position Numbers */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-yellow-400">
          <Zap className="w-5 h-5" /> Position Numbers
          <span className="text-zinc-400 text-sm font-normal ml-2">
            (Position {pos.from_top} ↓ + {pos.from_bottom} ↑ = {pos.sum})
          </span>
        </h3>
        <div className="flex gap-6">
          {prediction.position_numbers.map((p, i) => (
            <div key={i} className="text-center">
              <NumberBall number={p.number} size="lg" />
              <span className="text-zinc-400 text-xs mt-2 block">{p.type.replace('_', ' ')}</span>
              <span className="text-yellow-400 text-xs font-mono">{p.confidence}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Linked Suggestions */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-green-400">
          <Link2 className="w-5 h-5" /> Linked Numbers (Digit Patterns)
        </h3>
        <div className="flex flex-wrap gap-3">
          {prediction.linked_suggestions.map((l, i) => (
            <div key={i} className="bg-[#0F0F10] rounded-lg p-3 text-center">
              <NumberBall number={l.number} size="sm" />
              <span className="text-zinc-500 text-xs mt-1 block">↔ {l.linked_to}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Historical at this position */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-purple-400">
          <History className="w-5 h-5" /> Historical at Position {pos.from_top}
        </h3>
        <div className="space-y-2">
          {prediction.historical_at_position.map((h, i) => {
            const hasPos = h.numbers.includes(pos.from_top) || h.numbers.includes(pos.from_bottom);
            return (
              <div key={i} className={`bg-[#0F0F10] rounded-lg p-3 flex items-center justify-between ${hasPos ? 'border border-green-500/30' : ''}`}>
                <div className="flex items-center gap-3">
                  <span className="text-zinc-400 font-mono text-sm">{h.year} Q{h.quarter}</span>
                  <div className="flex gap-1">
                    {h.numbers.map((n, j) => (
                      <NumberBall key={j} number={n} size="sm" />
                    ))}
                  </div>
                </div>
                {hasPos && <span className="text-green-400 text-sm">✓ hit</span>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Top Historical Numbers */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-orange-400">
          <TrendingUp className="w-5 h-5" /> Hot at This Position
        </h3>
        <div className="flex flex-wrap gap-3">
          {prediction.historical_suggestions.slice(0, 8).map((h, i) => (
            <div key={i} className="bg-[#0F0F10] rounded-lg p-3 text-center min-w-[70px]">
              <NumberBall number={h.number} size="sm" />
              <span className="text-zinc-500 text-xs mt-1 block">{h.count}x</span>
              <span className="text-orange-400 text-xs font-mono">{h.confidence}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Last Draw */}
      {prediction.last_draw && (
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5" /> Last Draw ({prediction.last_draw.date})
          </h3>
          <div className="flex gap-3">
            {prediction.last_draw.numbers.map((n, i) => (
              <NumberBall key={i} number={n} size="md" />
            ))}
          </div>
        </div>
      )}

      {/* Date Patterns - NEW */}
      {prediction.date_patterns && prediction.date_patterns.length > 0 && (
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-cyan-400">
            <Clock className="w-5 h-5" /> Date Patterns (from last draw)
          </h3>
          <div className="flex flex-wrap gap-4">
            {prediction.date_patterns.map((dp, i) => (
              <div key={i} className="bg-[#0F0F10] rounded-lg p-3 text-center min-w-[100px]">
                <NumberBall number={dp.number} size="md" />
                <span className="text-zinc-400 text-xs mt-2 block">{dp.reason}</span>
                <span className="text-cyan-400 text-xs font-mono">{dp.confidence}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Advanced Patterns Tab
const AdvancedPatterns = ({ patterns, loading, onRefresh }) => {
  if (loading) return <div className="text-center py-10 text-zinc-400">Analyzing patterns from 2020...</div>;
  if (!patterns) return <div className="text-center py-10 text-zinc-400">Click refresh to load advanced patterns</div>;

  return (
    <div className="space-y-6" data-testid="advanced-patterns-panel">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Advanced Pattern Analysis (from {patterns.from_year})</h2>
        <span className="text-zinc-400 text-sm">{patterns.total_draws_analyzed} draws analyzed</span>
      </div>

      {/* Series Completions - Your 10-11-12 + 34→13 pattern */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-yellow-400">
          <Zap className="w-5 h-5" /> Series Completions (Digit Reversal)
          <span className="bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 px-2 py-1 rounded text-xs ml-2">
            {patterns.series_completions?.length || 0} found
          </span>
        </h3>
        <div className="space-y-3 max-h-72 overflow-y-auto">
          {patterns.series_completions?.map((p, i) => (
            <div key={i} className="bg-[#0F0F10] rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-zinc-400 text-sm font-mono">{p.date}</span>
                <span className="text-yellow-400 text-xs">Series: {p.full_series?.join('-')}</span>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                {p.series?.map((n, j) => <NumberBall key={j} number={n} size="sm" />)}
                <span className="text-zinc-500">+</span>
                <NumberBall number={p.completed_by} size="sm" />
                <span className="text-zinc-500">→</span>
                <span className="text-yellow-400 font-mono font-bold">{p.as_reversed}</span>
              </div>
            </div>
          ))}
          {(!patterns.series_completions || patterns.series_completions.length === 0) && (
            <div className="text-zinc-500 text-center py-4">No series completions found</div>
          )}
        </div>
      </div>

      {/* Cross-Draw Connections - Your 4+5=45→54→12 pattern */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-green-400">
          <Link2 className="w-5 h-5" /> Cross-Draw Digit Sums
          <span className="bg-green-500/10 text-green-400 border border-green-500/20 px-2 py-1 rounded text-xs ml-2">
            {patterns.cross_draw_connections?.length || 0} found
          </span>
        </h3>
        <div className="space-y-2 max-h-72 overflow-y-auto">
          {patterns.cross_draw_connections?.slice(0, 20).map((p, i) => (
            <div key={i} className="bg-[#0F0F10] rounded-lg p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <NumberBall number={p.numbers[0]} size="sm" />
                <span className="text-zinc-500">+</span>
                <NumberBall number={p.numbers[1]} size="sm" />
                <span className="text-zinc-500">=</span>
                <span className="font-mono text-white">{p.combined}</span>
                <span className="text-zinc-500">→</span>
                <span className="font-mono text-green-400">{p.reversed}</span>
                <span className="text-zinc-500">Σ</span>
                <span className="font-mono text-green-400 font-bold">{p.digit_sum}</span>
              </div>
              <span className="text-zinc-500 text-xs">{p.date}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Digit Sum Patterns */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-purple-400">
          <Hash className="w-5 h-5" /> Digit Sum Appearances
          <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2 py-1 rounded text-xs ml-2">
            {patterns.digit_sum_patterns?.length || 0} found
          </span>
        </h3>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {patterns.digit_sum_patterns?.slice(0, 15).map((p, i) => (
            <div key={i} className="bg-[#0F0F10] rounded-lg p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <NumberBall number={p.n1} size="sm" />
                <span className="text-zinc-500">+</span>
                <NumberBall number={p.n2} size="sm" />
                <span className="text-zinc-500">=</span>
                <span className="font-mono text-purple-400 font-bold">{p.sum}</span>
                <span className="text-zinc-500 text-xs ml-2">
                  (in {p.sum_in_draw ? 'same draw' : 'prev draw'})
                </span>
              </div>
              <span className="text-zinc-500 text-xs">{p.date}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Digit Reversals in Draws */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-orange-400">
          <RefreshCw className="w-5 h-5" /> Digit Reversals in Draws
          <span className="bg-orange-500/10 text-orange-400 border border-orange-500/20 px-2 py-1 rounded text-xs ml-2">
            {patterns.digit_reversals_in_draws?.length || 0} found
          </span>
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 max-h-60 overflow-y-auto">
          {patterns.digit_reversals_in_draws?.slice(0, 24).map((p, i) => (
            <div key={i} className="bg-[#0F0F10] rounded-lg p-2 text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <NumberBall number={p.number} size="sm" />
                <span className="text-zinc-500">→</span>
                <span className={`font-mono font-bold ${p.in_draw ? 'text-green-400' : 'text-orange-400'}`}>
                  {p.reversed}
                </span>
              </div>
              <span className="text-zinc-500 text-xs">{p.date}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Patterns Tab
const Patterns = ({ patterns }) => {
  if (!patterns) return <div className="text-center py-10 text-zinc-400">Loading...</div>;

  return (
    <div className="space-y-6" data-testid="patterns-panel">
      {/* Digit Reversals */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Link2 className="w-5 h-5" /> Digit Reversals
          <span className="bg-sky-500/10 text-sky-400 border border-sky-500/20 px-2 py-1 rounded text-xs ml-2">
            {patterns.digit_reversals.length} pairs
          </span>
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {patterns.digit_reversals.map((pair, i) => (
            <div key={i} className="bg-[#0F0F10] rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <NumberBall number={pair.num1} size="sm" />
                <span className="text-zinc-500">→</span>
                <NumberBall number={pair.num2} size="sm" />
              </div>
              <span className="text-zinc-500 text-xs font-mono">
                {pair.count1}x / {pair.count2}x
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Series Patterns */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5" /> Series Patterns
          <span className="bg-orange-500/10 text-orange-400 border border-orange-500/20 px-2 py-1 rounded text-xs ml-2">
            {patterns.series_patterns.length} found
          </span>
        </h3>
        <div className="space-y-3">
          {patterns.series_patterns.slice(0, 10).map((series, i) => (
            <div key={i} className="bg-[#0F0F10] rounded-lg p-4 flex items-center justify-between">
              <div>
                <span className="text-zinc-400 text-sm font-mono">{series.date}</span>
                <div className="flex gap-2 mt-2">
                  {series.numbers.map((num, j) => (
                    <NumberBall key={j} number={num} size="sm" />
                  ))}
                </div>
              </div>
              <span className="bg-orange-500/10 text-orange-400 px-2 py-1 rounded text-xs">
                {series.length} series
              </span>
            </div>
          ))}
        </div>
        
        {patterns.series_patterns.length === 0 && (
          <div className="text-center py-6 text-zinc-500">
            No consecutive series found in recent draws
          </div>
        )}
      </div>
    </div>
  );
};

// Predictions Tab
const Predictions = ({ predictions, onRefresh }) => {
  if (!predictions) return <div className="text-center py-10 text-zinc-400">Loading...</div>;

  return (
    <div className="space-y-6" data-testid="predictions-panel">
      {/* Smart Number Generator */}
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400" /> Smart Number Generator
          </h3>
          <button 
            onClick={onRefresh}
            className="p-2 hover:bg-[#27272A] rounded-lg transition-colors"
            data-testid="refresh-predictions"
          >
            <RefreshCw className="w-4 h-4 text-zinc-400" />
          </button>
        </div>
        
        <div className="mb-4">
          <span className="text-zinc-400 text-sm">Suggested Numbers:</span>
          <div className="flex gap-3 mt-3">
            {predictions.suggested_numbers.map((num, i) => (
              <div key={i} className="text-center">
                <NumberBall number={num} size="lg" />
                <span className="text-zinc-500 text-xs mt-1 block">#{i + 1}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <span className="text-zinc-400 text-sm">Why these numbers:</span>
          <div className="space-y-2 mt-3">
            {predictions.explanations.map((exp, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-[#27272A]/50 last:border-0">
                <div className="flex items-center gap-3">
                  <NumberBall number={exp.number} size="sm" />
                  <span className="text-zinc-300 text-sm">{exp.reason}</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-mono ${
                  exp.confidence >= 70 ? "bg-green-500/10 text-green-400" : "bg-yellow-500/10 text-yellow-400"
                }`}>
                  {exp.confidence}%
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-4 bg-[#0F0F10] rounded-lg p-3 font-mono text-xs text-zinc-500">
          Analysis: {predictions.cross_draw_patterns.length} addition patterns | {predictions.gap_analysis.length} due numbers | G1:G2 ratio 9:8
        </div>
      </div>

      {/* Cross-Draw Patterns & Gap Analysis */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Layers className="w-5 h-5" /> Cross-Draw Patterns
            <span className="bg-sky-500/10 text-sky-400 border border-sky-500/20 px-2 py-1 rounded text-xs ml-2">
              {predictions.cross_draw_patterns.length} found
            </span>
          </h3>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {predictions.cross_draw_patterns.slice(0, 10).map((pattern, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <NumberBall number={pattern.a} size="sm" />
                <span className="text-zinc-500">+</span>
                <NumberBall number={pattern.b} size="sm" />
                <span className="text-zinc-500">=</span>
                <NumberBall number={pattern.c} size="sm" />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-5">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Timer className="w-5 h-5" /> Gap Analysis (Due Numbers)
          </h3>
          <div className="flex flex-wrap gap-2">
            {predictions.gap_analysis.map((item, i) => (
              <div key={i} className="bg-[#0F0F10] rounded-lg p-2 text-center min-w-[60px]">
                <NumberBall number={item.number} size="sm" />
                <span className="text-zinc-500 text-xs mt-1 block">{item.gap} draws</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Add Draw Modal
const AddDrawModal = ({ isOpen, onClose, onSubmit }) => {
  const [numbers, setNumbers] = useState(["", "", "", "", "", ""]);
  const [date, setDate] = useState("");
  const [drawNumber, setDrawNumber] = useState("");
  const [error, setError] = useState("");

  const handleNumberChange = (index, value) => {
    const newNumbers = [...numbers];
    newNumbers[index] = value;
    setNumbers(newNumbers);
    setError("");
  };

  const handleSubmit = () => {
    const nums = numbers.map(n => parseInt(n)).filter(n => !isNaN(n));
    
    if (nums.length !== 6) {
      setError("Please enter all 6 numbers");
      return;
    }
    if (nums.some(n => n < 1 || n > 42)) {
      setError("Numbers must be between 1 and 42");
      return;
    }
    if (new Set(nums).size !== 6) {
      setError("Numbers must be unique");
      return;
    }
    if (!date) {
      setError("Please select a date");
      return;
    }

    onSubmit({ numbers: nums, date, draw_number: drawNumber || null });
    setNumbers(["", "", "", "", "", ""]);
    setDate("");
    setDrawNumber("");
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" data-testid="add-draw-modal">
      <div className="bg-[#18181A] border border-[#27272A] rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Add New Draw</h2>
          <button onClick={onClose} className="p-1 hover:bg-[#27272A] rounded" data-testid="close-modal">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-4">
          <label className="text-zinc-400 text-sm block mb-2">Draw Numbers (1-42)</label>
          <div className="grid grid-cols-6 gap-2">
            {numbers.map((num, i) => (
              <input
                key={i}
                type="number"
                min="1"
                max="42"
                value={num}
                onChange={(e) => handleNumberChange(i, e.target.value)}
                className="bg-[#0F0F10] border border-[#27272A] focus:border-blue-500 rounded-md px-2 py-3 text-center font-mono text-white w-full"
                placeholder={`#${i + 1}`}
                data-testid={`number-input-${i + 1}`}
              />
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-zinc-400 text-sm block mb-2">Draw Date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="bg-[#0F0F10] border border-[#27272A] focus:border-blue-500 rounded-md px-3 py-2 text-white w-full"
              data-testid="draw-date-input"
            />
          </div>
          <div>
            <label className="text-zinc-400 text-sm block mb-2">Draw Number (Optional)</label>
            <input
              type="text"
              value={drawNumber}
              onChange={(e) => setDrawNumber(e.target.value)}
              placeholder="e.g., 1234"
              className="bg-[#0F0F10] border border-[#27272A] focus:border-blue-500 rounded-md px-3 py-2 text-white w-full"
              data-testid="draw-number-input"
            />
          </div>
        </div>

        {error && (
          <div className="text-red-400 text-sm mb-4 bg-red-500/10 border border-red-500/20 rounded p-2">
            {error}
          </div>
        )}

        <button
          onClick={handleSubmit}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-md transition-colors"
          data-testid="submit-draw-button"
        >
          Add Draw
        </button>
      </div>
    </div>
  );
};

// Main App
function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [stats, setStats] = useState(null);
  const [draws, setDraws] = useState([]);
  const [patterns, setPatterns] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [advancedPatterns, setAdvancedPatterns] = useState(null);
  const [advancedLoading, setAdvancedLoading] = useState(false);
  const [quarterPrediction, setQuarterPrediction] = useState(null);
  const [quarterLoading, setQuarterLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchDashboard = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/dashboard`);
      setStats(res.data);
    } catch (e) {
      console.error("Error fetching dashboard:", e);
    }
  }, []);

  const fetchDraws = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/draws`);
      setDraws(res.data);
    } catch (e) {
      console.error("Error fetching draws:", e);
    }
  }, []);

  const fetchPatterns = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/patterns`);
      setPatterns(res.data);
    } catch (e) {
      console.error("Error fetching patterns:", e);
    }
  }, []);

  const fetchPredictions = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/predictions`);
      setPredictions(res.data);
    } catch (e) {
      console.error("Error fetching predictions:", e);
    }
  }, []);

  const fetchAdvancedPatterns = useCallback(async () => {
    try {
      setAdvancedLoading(true);
      const res = await axios.get(`${API}/advanced-patterns?from_year=2020`);
      setAdvancedPatterns(res.data);
    } catch (e) {
      console.error("Error fetching advanced patterns:", e);
    } finally {
      setAdvancedLoading(false);
    }
  }, []);

  const fetchQuarterPrediction = useCallback(async () => {
    try {
      setQuarterLoading(true);
      const res = await axios.get(`${API}/quarter-predictor`);
      setQuarterPrediction(res.data);
    } catch (e) {
      console.error("Error fetching quarter prediction:", e);
    } finally {
      setQuarterLoading(false);
    }
  }, []);

  const seedData = async () => {
    try {
      setLoading(true);
      await axios.post(`${API}/seed`);
      await refreshAll();
    } catch (e) {
      console.error("Error seeding data:", e);
    } finally {
      setLoading(false);
    }
  };

  const refreshAll = async () => {
    setLoading(true);
    await Promise.all([fetchDashboard(), fetchDraws(), fetchPatterns(), fetchPredictions()]);
    setLoading(false);
  };

  const handleAddDraw = async (drawData) => {
    try {
      await axios.post(`${API}/draws`, drawData);
      await refreshAll();
    } catch (e) {
      console.error("Error adding draw:", e);
      alert(e.response?.data?.detail || "Error adding draw");
    }
  };

  const handleDeleteDraw = async (id) => {
    if (!window.confirm("Delete this draw?")) return;
    try {
      await axios.delete(`${API}/draws/${id}`);
      await refreshAll();
    } catch (e) {
      console.error("Error deleting draw:", e);
    }
  };

  useEffect(() => {
    refreshAll();
    fetchAdvancedPatterns();
    fetchQuarterPrediction();
    // Auto-seed if no data
    const checkAndSeed = async () => {
      const res = await axios.get(`${API}/dashboard`);
      if (res.data.total_draws === 0) {
        await seedData();
      }
    };
    checkAndSeed();
  }, []);

  const tabs = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "history", label: "Draw History", icon: History },
    { id: "patterns", label: "Patterns", icon: Link2 },
    { id: "advanced", label: "Advanced", icon: Zap },
    { id: "predictor", label: "Predictor", icon: Target },
    { id: "predictions", label: "Smart Gen", icon: TrendingUp }
  ];

  return (
    <div className="min-h-screen bg-[#0F0F10] text-white">
      {/* Header */}
      <header className="border-b border-[#27272A] px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-xl">✦</span>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight" style={{ fontFamily: "Manrope, sans-serif" }}>
                LUCKY JACK
              </h1>
              <p className="text-zinc-500 text-xs">Switzerland Lotto Pattern Analyzer</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button 
              onClick={refreshAll}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 border border-[#27272A] hover:bg-[#27272A] rounded-md transition-colors disabled:opacity-50"
              data-testid="refresh-button"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
            <button 
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
              data-testid="add-draw-button"
            >
              <Plus className="w-4 h-4" />
              <span>Add Draw</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* Tabs */}
        <div className="flex space-x-1 bg-[#18181A] p-1 rounded-lg border border-[#27272A] mb-6 w-fit">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === tab.id
                  ? "bg-[#27272A] text-white shadow-sm"
                  : "text-zinc-400 hover:text-white hover:bg-[#27272A]/50"
              }`}
              data-testid={`${tab.id}-tab`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "dashboard" && <Dashboard stats={stats} onRefresh={refreshAll} />}
        {activeTab === "history" && <DrawHistory draws={draws} onDelete={handleDeleteDraw} />}
        {activeTab === "patterns" && <Patterns patterns={patterns} />}
        {activeTab === "advanced" && <AdvancedPatterns patterns={advancedPatterns} loading={advancedLoading} onRefresh={fetchAdvancedPatterns} />}
        {activeTab === "predictor" && <QuarterPredictor prediction={quarterPrediction} loading={quarterLoading} onRefresh={fetchQuarterPrediction} />}
        {activeTab === "predictions" && <Predictions predictions={predictions} onRefresh={fetchPredictions} />}
      </main>

      {/* Add Draw Modal */}
      <AddDrawModal 
        isOpen={showAddModal} 
        onClose={() => setShowAddModal(false)} 
        onSubmit={handleAddDraw}
      />
    </div>
  );
}

export default App;
