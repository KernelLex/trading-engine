export interface SentimentData {
    sector_sentiment: {
        sector: string;
        date: string;
        sentiment: number;
    }[];
    news_sentiment: {
        headline: string;
        sentiment_label: string;
        sentiment_score: number;
        timestamp: string;
    }[];
    social_sentiment: {
        subreddit: string;
        sentiment_label: string;
        sentiment_score: number;
        timestamp: string;
    }[];
}

export interface MacroEventsData {
    macro_indicators: {
        series_id: string;
        indicator_name: string;
        date: string;
        value: number;
    }[];
    market_events: {
        event_type: string;
        timestamp: string;
        related_tickers: string;
        confidence_score: number;
    }[];
}

export interface Hypothesis {
    hypothesis_id: string;
    title: string;
    confidence_score: number;
    trigger_conditions: string;
    expected_direction: string;
    supporting_signals: string;
    sector: string;
    holding_period: string;
}

export interface Strategy {
    strategy_id: string;
    strategy_name: string;
    asset_scope: string;
    entry_conditions: string;
    exit_conditions: string;
    risk_rules: string;
    confidence_score: number;
    status: string;
}

export interface Backtest {
    backtest_id: string;
    strategy_id: string;
    start_date: string;
    end_date: string;
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    strategy_name: string;
}

export interface Explanation {
    explanation_id: string;
    strategy_id: string;
    timestamp: string;
    explanation_text: string;
    confidence_score: number;
    dominant_market_factors: Record<string, number>;
    shap_values: Record<string, number>;
    key_signals: string[];
    strategy_name: string;
}

export interface TradeSimulation {
    trades: {
        trade_id: string;
        asset: string;
        entry_timestamp: string;
        exit_timestamp: string;
        entry_price: number;
        exit_price: number;
        pnl: number;
        holding_period: number;
    }[];
    prices: {
        date: string;
        close: number;
    }[];
}
