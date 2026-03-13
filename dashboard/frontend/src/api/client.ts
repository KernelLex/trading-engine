import axios from 'axios';
import type {
    SentimentData,
    MacroEventsData,
    Hypothesis,
    Strategy,
    Backtest,
    Explanation,
    TradeSimulation
} from '../types';

const API_BASE = 'http://localhost:8000/api';

export const api = {
    getSentiment: () => axios.get<SentimentData>(`${API_BASE}/sentiment`).then(r => r.data),
    getMacroEvents: () => axios.get<MacroEventsData>(`${API_BASE}/macro-events`).then(r => r.data),
    getHypotheses: () => axios.get<Hypothesis[]>(`${API_BASE}/hypotheses`).then(r => r.data),
    getStrategies: () => axios.get<Strategy[]>(`${API_BASE}/strategies`).then(r => r.data),
    getBacktests: () => axios.get<Backtest[]>(`${API_BASE}/backtests`).then(r => r.data),
    getExplanations: () => axios.get<Explanation[]>(`${API_BASE}/explanations`).then(r => r.data),
    getTradeSimulation: (strategyId: string) => axios.get<TradeSimulation>(`${API_BASE}/trades/${strategyId}`).then(r => r.data),
};
