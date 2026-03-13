import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, BarChart, Bar } from 'recharts';
import type { SentimentData } from '../../types';

interface Props {
    data: SentimentData | null;
}

export const MarketSentimentMonitor: React.FC<Props> = ({ data }) => {
    if (!data) return <div className="p-4 bg-gray-800 rounded-lg animate-pulse h-64"></div>;

    // Process sector sentiment for a simple bar chart
    // Group by sector, taking the most recent sentiment score per sector
    const latestSectorData = data.sector_sentiment.reduce((acc, curr) => {
        if (!acc[curr.sector] || new Date(curr.date) > new Date(acc[curr.sector].date)) {
            acc[curr.sector] = curr;
        }
        return acc;
    }, {} as Record<string, any>);

    const sectorChartData = Object.values(latestSectorData).map(d => ({
        name: d.sector,
        sentiment: parseFloat(d.sentiment.toFixed(2))
    }));

    // Process news sentiment over time (mocking dates to group them if necessary, or just sequence)
    const newsChartData = data.news_sentiment.slice(0, 20).reverse().map((d, i) => ({
        time: i,
        score: d.sentiment_score,
        headline: d.headline
    }));

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Sector Sentiment Heatmap/Bar */}
            <div className="bg-gray-800 p-4 rounded-xl shadow-lg border border-gray-700">
                <h3 className="text-lg font-semibold mb-4 text-gray-200">Sector Sentiment</h3>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={sectorChartData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
                            <XAxis type="number" domain={[-1, 1]} stroke="#9CA3AF" />
                            <YAxis dataKey="name" type="category" width={100} stroke="#9CA3AF" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                                itemStyle={{ color: '#E5E7EB' }}
                            />
                            <Bar dataKey="sentiment" fill="#3B82F6" radius={[0, 4, 4, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Recent News Sentiment Trend */}
            <div className="bg-gray-800 p-4 rounded-xl shadow-lg border border-gray-700">
                <h3 className="text-lg font-semibold mb-4 text-gray-200">Recent News Sentiment</h3>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={newsChartData}>
                            <defs>
                                <linearGradient id="colorColor" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                            <XAxis dataKey="time" hide />
                            <YAxis domain={[-1, 1]} stroke="#9CA3AF" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                                labelFormatter={() => ''}
                                formatter={(value: any, name: any, props: any) => [value, props.payload.headline]}
                            />
                            <Area type="monotone" dataKey="score" stroke="#10B981" fillOpacity={1} fill="url(#colorColor)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};
