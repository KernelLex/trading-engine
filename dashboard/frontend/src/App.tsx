import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import type {
  SentimentData,
  MacroEventsData,
  Hypothesis,
  Strategy,
  Backtest,
  Explanation
} from './types';

// Importing Panels
import { MarketSentimentMonitor } from './components/panels/MarketSentimentMonitor';
import { MarketIntelligencePanel } from './components/panels/MarketIntelligencePanel';
import { ResearchHypothesesPanel } from './components/panels/ResearchHypothesesPanel';
import { StrategyDiscoveryPanel } from './components/panels/StrategyDiscoveryPanel';
import { BacktestPerformance } from './components/panels/BacktestPerformance';
import { ExplainableAIInsights } from './components/panels/ExplainableAIInsights';
import { TradeSimulationViewer } from './components/panels/TradeSimulationViewer';

import { Activity, RefreshCw } from 'lucide-react';

const App: React.FC = () => {
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [macroEvents, setMacroEvents] = useState<MacroEventsData | null>(null);
  const [hypotheses, setHypotheses] = useState<Hypothesis[] | null>(null);
  const [strategies, setStrategies] = useState<Strategy[] | null>(null);
  const [backtests, setBacktests] = useState<Backtest[] | null>(null);
  const [explanations, setExplanations] = useState<Explanation[] | null>(null);

  // State for Trade Simulation View selection
  const [selectedStrategyId, setSelectedStrategyId] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [sen, mac, hyp, str, bac, exp] = await Promise.all([
        api.getSentiment(),
        api.getMacroEvents(),
        api.getHypotheses(),
        api.getStrategies(),
        api.getBacktests(),
        api.getExplanations()
      ]);
      setSentiment(sen);
      setMacroEvents(mac);
      setHypotheses(hyp);
      setStrategies(str);
      setBacktests(bac);
      setExplanations(exp);

      // Auto-select the first strategy that has a backtest for the Trade Simulation Viewer
      if (bac.length > 0) {
        setSelectedStrategyId(bac[0].strategy_id);
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    // Refresh every 5 minutes
    const interval = setInterval(fetchAllData, 300000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#0f1219] text-gray-200 font-sans p-4 md:p-6 lg:p-8">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-gray-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-lg border border-blue-500/30">
            <Activity className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">AI Market Intelligence Hub</h1>
            <p className="text-sm text-gray-400">Phase 7: Real-Time Quantitative Evaluation Dashboard</p>
          </div>
        </div>

        <button
          onClick={fetchAllData}
          disabled={loading}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-2 rounded-lg border border-gray-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </header>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Row 1: Sentiment & Macro (Intelligence Layer) */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          <MarketSentimentMonitor data={sentiment} />
        </div>
        <div className="lg:col-span-4">
          <MarketIntelligencePanel data={macroEvents} />
        </div>

        {/* Row 2: Hypotheses & Strategies (Discovery Layer) */}
        <div className="lg:col-span-6">
          <ResearchHypothesesPanel data={hypotheses} />
        </div>
        <div className="lg:col-span-6">
          <StrategyDiscoveryPanel data={strategies} />
        </div>

        {/* Row 3: Backtest Performance & Explainable AI */}
        <div className="lg:col-span-6">
          <BacktestPerformance data={backtests} />
        </div>
        <div className="lg:col-span-6">
          <ExplainableAIInsights data={explanations} />
        </div>

        {/* Row 4: Trade Simulation Viewer */}
        <div className="lg:col-span-12 mb-12">
          <div className="flex justify-between items-end mb-4 px-1">
            <h2 className="text-xl font-semibold text-gray-200">Execution Simulation Overlay</h2>
            <select
              className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 outline-none w-64"
              value={selectedStrategyId || ''}
              onChange={e => setSelectedStrategyId(e.target.value)}
            >
              <option value="" disabled>Select a Backtested Strategy</option>
              {backtests?.map(b => (
                <option key={b.backtest_id} value={b.strategy_id}>{b.strategy_name}</option>
              ))}
            </select>
          </div>
          <TradeSimulationViewer strategyId={selectedStrategyId} />
        </div>

      </div>
    </div>
  );
}

export default App;
