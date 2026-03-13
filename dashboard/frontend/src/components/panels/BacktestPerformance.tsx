import React from 'react';
import type { Backtest } from '../../types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine, ScatterChart, Scatter, Cell } from 'recharts';
import { PieChart } from 'lucide-react';

interface Props {
    data: Backtest[] | null;
}

export const BacktestPerformance: React.FC<Props> = ({ data }) => {
    if (!data) return <div className="p-4 bg-gray-800 rounded-lg animate-pulse h-64"></div>;

    // Scatter plot data mapping Risk (Max DD) vs Reward (Sharpe or Return)
    const scatterData = data.map(b => ({
        name: b.strategy_name,
        x: b.max_drawdown * 100, // DD%
        y: parseFloat(b.sharpe_ratio.toFixed(2)),
        z: b.total_return * 100 // Bubble size / color indicator
    }));

    // Simple leaderboard
    const topStrats = [...data].sort((a, b) => b.sharpe_ratio - a.sharpe_ratio).slice(0, 5);

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-lg border border-gray-700">
            <h3 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
                <PieChart className="w-5 h-5 text-emerald-400" />
                Backtest Performance
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-64">
                {/* Risk/Reward Scatter Mapping */}
                <div className="h-full relative">
                    <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis type="number" dataKey="x" name="Max Drawdown (%)" stroke="#9CA3AF">
                                {/* Reversed domain logic is tricky in recharts scatter without custom ticks, so we keep normal but x is DD% */}
                            </XAxis>
                            <YAxis type="number" dataKey="y" name="Sharpe Ratio" stroke="#9CA3AF" />
                            <Tooltip
                                cursor={{ strokeDasharray: '3 3' }}
                                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                                formatter={(val: any, name: any, info: any) => [val, name === 'x' ? 'Max DD %' : 'Sharpe']}
                                labelFormatter={() => ''}
                            />
                            <ReferenceLine y={0.5} stroke="#6B7280" strokeDasharray="3 3" />
                            <ReferenceLine x={15} stroke="#6B7280" strokeDasharray="3 3" />
                            <Scatter name="Strategies" data={scatterData} fill="#3B82F6">
                                {scatterData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.y > 1.0 ? '#10B981' : entry.y < 0 ? '#EF4444' : '#3B82F6'} />
                                ))}
                            </Scatter>
                        </ScatterChart>
                    </ResponsiveContainer>
                    <div className="absolute top-2 right-2 text-[10px] text-gray-500">Risk vs Reward</div>
                </div>

                {/* Top 5 Leaderboard */}
                <div className="overflow-y-auto custom-scrollbar flex flex-col justify-start">
                    <table className="w-full text-left text-sm text-gray-300">
                        <thead className="text-xs uppercase bg-gray-900/50 text-gray-500 sticky top-0">
                            <tr>
                                <th className="px-3 py-2">Strategy</th>
                                <th className="px-3 py-2 text-right">Sharpe</th>
                                <th className="px-3 py-2 text-right">Return</th>
                            </tr>
                        </thead>
                        <tbody>
                            {topStrats.map(s => (
                                <tr key={s.backtest_id} className="border-b border-gray-700/50 hover:bg-gray-700">
                                    <td className="px-3 py-2 font-medium truncate max-w-[120px]" title={s.strategy_name}>{s.strategy_name}</td>
                                    <td className="px-3 py-2 text-right text-emerald-400 font-mono">{s.sharpe_ratio.toFixed(2)}</td>
                                    <td className="px-3 py-2 text-right font-mono">{(s.total_return * 100).toFixed(1)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
