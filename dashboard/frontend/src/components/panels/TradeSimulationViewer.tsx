import React, { useState, useEffect } from 'react';
import type { TradeSimulation } from '../../types';
import { api } from '../../api/client';
import { ComposedChart, Line, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Activity } from 'lucide-react';

interface Props {
    strategyId: string | null;
}

export const TradeSimulationViewer: React.FC<Props> = ({ strategyId }) => {
    const [data, setData] = useState<TradeSimulation | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!strategyId) {
            setData(null);
            return;
        }
        setLoading(true);
        api.getTradeSimulation(strategyId).then(res => {
            setData(res);
            setLoading(false);
        }).catch(() => {
            setLoading(false);
        });
    }, [strategyId]);

    if (!strategyId) {
        return (
            <div className="p-4 bg-gray-800/50 rounded-xl border border-gray-700/50 h-64 flex flex-col items-center justify-center text-gray-500">
                <Activity className="w-8 h-8 mb-2 opacity-50" />
                <p>Select a backtest from the table or pick a strategy to view its trade overlay.</p>
            </div>
        );
    }

    if (loading) return <div className="p-4 bg-gray-800 rounded-xl animate-pulse h-64 border border-gray-700"></div>;
    if (!data || data.trades.length === 0) return <div className="p-4 bg-gray-800 rounded-xl text-gray-500 flex items-center justify-center h-64 border border-gray-700">No trade data available.</div>;

    // Prepare chart data by merging prices and trades
    const chartData = data.prices.map(p => {
        const ptDateStr = p.date.split('T')[0];
        const tradeEntry = data.trades.find(t => t.entry_timestamp.startsWith(ptDateStr));
        const tradeExit = data.trades.find(t => t.exit_timestamp && t.exit_timestamp.startsWith(ptDateStr));

        return {
            date: ptDateStr,
            close: p.close,
            entry: tradeEntry ? tradeEntry.entry_price : null,
            exit: tradeExit ? tradeExit.exit_price : null,
            pnl: tradeExit ? tradeExit.pnl : null
        };
    });

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-lg border border-gray-700 h-[400px] flex flex-col">
            <h3 className="text-lg font-semibold text-gray-200 mb-2 flex items-center justify-between">
                <span className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-cyan-400" />
                    Trade Execution View ({data.trades[0]?.asset})
                </span>
                <span className="text-xs font-normal text-gray-400 bg-gray-900 px-2 py-1 rounded">
                    {data.trades.length} Trades Simulated
                </span>
            </h3>

            <div className="flex-1 w-full min-h-0 relative">
                <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                        <XAxis dataKey="date" stroke="#9CA3AF" tick={{ fontSize: 10 }} minTickGap={30} />
                        <YAxis domain={['auto', 'auto']} stroke="#9CA3AF" tick={{ fontSize: 10 }} />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
                            labelStyle={{ color: '#9CA3AF', marginBottom: '4px' }}
                        />
                        {/* Price Line */}
                        <Line type="monotone" dataKey="close" stroke="#6B7280" strokeWidth={1} dot={false} activeDot={{ r: 4 }} />

                        {/* Entry Points (Green/Blue) */}
                        <Scatter dataKey="entry" name="Buy/Entry" fill="#3B82F6" />

                        {/* Exit Points (Red/Green based on PnL) */}
                        <Scatter dataKey="exit" name="Sell/Exit" fill="#10B981">
                            {chartData.map((entry, index) => {
                                if (entry.exit !== null) {
                                    return <Cell key={`cell-${index}`} fill={(entry.pnl && entry.pnl > 0) ? '#10B981' : '#EF4444'} />
                                }
                                return <Cell key={`cell-${index}`} />
                            })}
                        </Scatter>
                    </ComposedChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
