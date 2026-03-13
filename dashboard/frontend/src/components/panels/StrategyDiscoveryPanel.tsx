import React from 'react';
import type { Strategy } from '../../types';
import { Lock, Shield, Layers, ChevronRight } from 'lucide-react';

interface Props {
    data: Strategy[] | null;
}

export const StrategyDiscoveryPanel: React.FC<Props> = ({ data }) => {
    if (!data) return <div className="p-4 bg-gray-800 rounded-lg animate-pulse h-64"></div>;

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-lg border border-gray-700 h-[400px] flex flex-col">
            <h3 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
                <Layers className="w-5 h-5 text-indigo-400" />
                Strategy Discovery
            </h3>

            <div className="overflow-y-auto flex-1 custom-scrollbar pr-2 space-y-4">
                {data.map(s => (
                    <div key={s.strategy_id} className="p-3 bg-gray-900 rounded-lg border border-gray-700 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-2 opacity-50 text-indigo-400 group-hover:opacity-100 transition-opacity">
                            <ChevronRight className="w-5 h-5" />
                        </div>

                        <div className="flex justify-between items-start mb-2 pr-6">
                            <h4 className="font-semibold text-gray-100 truncate">{s.strategy_name}</h4>
                            <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase font-bold tracking-wider ${s.status === 'promoted' ? 'bg-indigo-900/50 text-indigo-300' :
                                s.status === 'validated' ? 'bg-blue-900/50 text-blue-300' :
                                    'bg-gray-700 text-gray-400'
                                }`}>
                                {s.status}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs text-gray-400 mb-2">
                            <div className="flex flex-col">
                                <span className="uppercase text-[10px] font-semibold text-gray-500">Asset</span>
                                <span className="truncate text-gray-300">{s.asset_scope}</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="uppercase text-[10px] font-semibold text-gray-500">Confidence</span>
                                <span className="text-indigo-300 font-mono">{(s.confidence_score * 100).toFixed(1)}%</span>
                            </div>
                        </div>

                        <div className="space-y-1.5 mt-3 pt-3 border-t border-gray-700/50">
                            <div className="flex items-start gap-2 text-xs">
                                <span className="font-semibold text-green-400 w-10">ENTRY</span>
                                <span className="text-gray-300 line-clamp-1 flex-1">{s.entry_conditions}</span>
                            </div>
                            <div className="flex items-start gap-2 text-xs">
                                <span className="font-semibold text-red-400 w-10">EXIT</span>
                                <span className="text-gray-300 line-clamp-1 flex-1">{s.exit_conditions}</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-amber-500/80 mt-1">
                                <Shield className="w-3 h-3" />
                                <span className="truncate">{s.risk_rules}</span>
                            </div>
                        </div>
                    </div>
                ))}
                {data.length === 0 && (
                    <div className="text-gray-500 text-center py-8">No strategies.</div>
                )}
            </div>
        </div>
    );
};
