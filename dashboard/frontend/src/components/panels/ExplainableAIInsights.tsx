import React, { useState } from 'react';
import type { Explanation } from '../../types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { Zap, BrainCircuit } from 'lucide-react';

interface Props {
    data: Explanation[] | null;
}

export const ExplainableAIInsights: React.FC<Props> = ({ data }) => {
    const [selectedIdx, setSelectedIdx] = useState(0);

    if (!data) return <div className="p-4 bg-gray-800 rounded-lg animate-pulse h-64"></div>;
    if (data.length === 0) return <div className="p-4 bg-gray-800 rounded-lg text-gray-500 text-center h-64 flex items-center justify-center">No Explanations available.</div>;

    const expl = data[selectedIdx];

    // Format SHAP values for Bar Chart
    const shapData = Object.entries(expl.shap_values || {})
        .sort((a, b) => b[1] - a[1]) // Descending
        .slice(0, 5) // Top 5
        .map(([key, val]) => ({
            name: key.replace(/_/g, ' '),
            shap: parseFloat(val.toFixed(3))
        }));

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-lg border border-gray-700 h-full flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-200 flex items-center gap-2">
                    <BrainCircuit className="w-5 h-5 text-purple-400" />
                    Explainable AI Insights (SHAP)
                </h3>

                {/* Simple strategy selector if multiple exist */}
                {data.length > 1 && (
                    <select
                        className="bg-gray-900 border border-gray-600 rounded px-2 py-1 text-xs text-gray-300 outline-none"
                        value={selectedIdx}
                        onChange={e => setSelectedIdx(Number(e.target.value))}
                    >
                        {data.slice(0, 10).map((e, idx) => (
                            <option key={e.explanation_id} value={idx}>{e.strategy_name}</option>
                        ))}
                    </select>
                )}
            </div>

            <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* SHAP Importance Vector Chart */}
                <div className="h-48 relative">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 20, bottom: 0, left: 10 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={true} vertical={false} />
                            <XAxis type="number" hide />
                            <YAxis dataKey="name" type="category" width={100} tick={{ fill: '#9CA3AF', fontSize: 10 }} axisLine={false} tickLine={false} />
                            <Tooltip
                                cursor={{ fill: '#1F2937' }}
                                contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }}
                                itemStyle={{ color: '#C084FC' }}
                            />
                            <Bar dataKey="shap" radius={[0, 4, 4, 0]}>
                                {shapData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={index === 0 ? '#C084FC' : '#8B5CF6'} opacity={1 - index * 0.15} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                    <div className="absolute top-0 right-0 text-[10px] text-gray-400 bg-gray-900 px-2 py-0.5 rounded opacity-80">
                        Top Feature Contributions
                    </div>
                </div>

                {/* Narrative & Dominant Factors */}
                <div className="flex flex-col space-y-4">
                    <div className="p-3 bg-purple-900/20 border border-purple-500/30 rounded-lg text-sm text-purple-200">
                        {expl.explanation_text}
                    </div>

                    <div>
                        <h4 className="text-xs uppercase font-semibold text-gray-500 mb-2">Dominant Market Factors</h4>
                        <div className="flex flex-wrap gap-2">
                            {Object.entries(expl.dominant_market_factors || {})
                                .sort((a, b) => b[1] - a[1])
                                .slice(0, 3)
                                .map(([factor, score]) => (
                                    <div key={factor} className="px-2 py-1 bg-gray-900 border border-gray-700 rounded-md flex items-center gap-2">
                                        <span className="text-xs text-gray-300 capitalize">{factor.replace(/_/g, ' ')}</span>
                                        <span className="text-xs font-mono text-purple-400">{(score * 100).toFixed(0)}%</span>
                                    </div>
                                ))}
                        </div>
                    </div>

                    <div className="flex items-center gap-2 mt-auto text-xs text-gray-500">
                        <Zap className="w-3 h-3 text-yellow-500" />
                        Confidence: {(expl.confidence_score * 100).toFixed(1)}%
                    </div>
                </div>
            </div>
        </div>
    );
};
