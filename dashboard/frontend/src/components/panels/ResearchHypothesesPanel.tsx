import React, { useState } from 'react';
import type { Hypothesis } from '../../types';
import { Target, Lightbulb, Clock } from 'lucide-react';

interface Props {
    data: Hypothesis[] | null;
}

export const ResearchHypothesesPanel: React.FC<Props> = ({ data }) => {
    const [filter, setFilter] = useState('');

    if (!data) return <div className="p-4 bg-gray-800 rounded-lg animate-pulse h-64"></div>;

    const filtered = data.filter(h =>
        h.title?.toLowerCase().includes(filter.toLowerCase()) ||
        h.sector?.toLowerCase().includes(filter.toLowerCase())
    );

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-lg border border-gray-700 h-[400px] flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-200 flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-yellow-400" />
                    AI Research Hypotheses
                </h3>
                <input
                    type="text"
                    placeholder="Filter..."
                    className="bg-gray-900 border border-gray-600 rounded px-3 py-1 text-sm text-gray-200 outline-none focus:border-blue-500"
                    value={filter}
                    onChange={e => setFilter(e.target.value)}
                />
            </div>

            <div className="overflow-y-auto flex-1 custom-scrollbar pr-2 space-y-3">
                {filtered.map(h => (
                    <div key={h.hypothesis_id} className="p-3 bg-gray-700/40 rounded-lg border border-gray-600 hover:border-gray-400 transition-colors">
                        <div className="flex justify-between items-start mb-2">
                            <h4 className="font-medium text-gray-200 text-sm">{h.title}</h4>
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${h.expected_direction === 'bullish' ? 'bg-green-900/50 text-green-400 border border-green-800' :
                                h.expected_direction === 'bearish' ? 'bg-red-900/50 text-red-400 border border-red-800' :
                                    'bg-gray-800 text-gray-300 border border-gray-700'
                                }`}>
                                {h.expected_direction}
                            </span>
                        </div>

                        <div className="flex gap-4 text-xs text-gray-400 mb-2">
                            <span className="flex items-center gap-1"><Target className="w-3 h-3" /> {(h.confidence_score * 100).toFixed(0)}% Conf</span>
                            <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {h.holding_period}</span>
                            {h.sector && <span className="bg-gray-800 px-1.5 py-0.5 rounded">{h.sector}</span>}
                        </div>

                        <p className="text-xs text-gray-300 line-clamp-2" title={h.trigger_conditions}>
                            {h.trigger_conditions}
                        </p>
                    </div>
                ))}
                {filtered.length === 0 && (
                    <div className="text-gray-500 text-center py-8">No hypotheses match.</div>
                )}
            </div>
        </div>
    );
};
