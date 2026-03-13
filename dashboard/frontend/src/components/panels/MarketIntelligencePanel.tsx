import React from 'react';
import type { MacroEventsData } from '../../types';
import { AlertCircle, TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface Props {
    data: MacroEventsData | null;
}

export const MarketIntelligencePanel: React.FC<Props> = ({ data }) => {
    if (!data) return <div className="p-4 bg-gray-800 rounded-lg animate-pulse h-48"></div>;

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-lg border border-gray-700 h-full overflow-hidden flex flex-col">
            <h3 className="text-lg font-semibold mb-4 text-gray-200 flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-400" />
                Market Intelligence & Macro
            </h3>

            <div className="space-y-4 overflow-y-auto pr-2 pb-4 flex-1 custom-scrollbar">
                {/* Alerts Section (Mock logic based on large events) */}
                {data.market_events.slice(0, 5).map((ev, i) => (
                    <div key={i} className="flex gap-3 items-start p-3 bg-gray-700/50 rounded-lg border border-gray-600">
                        {ev.confidence_score > 0.8 ? (
                            <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
                        ) : (
                            <Activity className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                        )}
                        <div>
                            <div className="flex items-center gap-2">
                                <span className="font-medium text-sm text-gray-200 capitalize">{ev.event_type.replace('_', ' ')}</span>
                                <span className="text-xs text-gray-400">{new Date(ev.timestamp).toLocaleDateString()}</span>
                            </div>
                            <p className="text-sm text-gray-400 mt-1 truncate">
                                Tickers: {ev.related_tickers || 'N/A'} (Confidence: {(ev.confidence_score * 100).toFixed(0)}%)
                            </p>
                        </div>
                    </div>
                ))}

                {/* Macro Indicators Snippet */}
                <div className="mt-4 pt-4 border-t border-gray-600">
                    <h4 className="text-sm font-semibold text-gray-300 mb-2">Recent Macro Readings</h4>
                    <div className="grid grid-cols-2 gap-2">
                        {data.macro_indicators.slice(0, 4).map((m, i) => (
                            <div key={i} className="p-2 bg-gray-900 rounded border border-gray-700">
                                <div className="text-xs text-gray-400 truncate" title={m.indicator_name}>{m.indicator_name || m.series_id}</div>
                                <div className="text-sm font-bold text-gray-200">{m.value?.toFixed(2) || 'N/A'}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
