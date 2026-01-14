#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "yfinance>=0.2.40",
#     "pandas>=2.0.0",
# ]
# ///
"""
Stock analysis using Yahoo Finance data.

Usage:
    uv run analyze_stock.py TICKER [TICKER2 ...] [--output text|json] [--verbose]
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Literal

import pandas as pd
import yfinance as yf


@dataclass
class StockData:
    ticker: str
    info: dict
    earnings_history: pd.DataFrame | None
    analyst_info: dict | None
    price_history: pd.DataFrame | None


@dataclass
class EarningsSurprise:
    score: float
    explanation: str
    actual_eps: float | None = None
    expected_eps: float | None = None
    surprise_pct: float | None = None


@dataclass
class Fundamentals:
    score: float
    key_metrics: dict
    explanation: str


@dataclass
class AnalystSentiment:
    score: float | None
    summary: str
    consensus_rating: str | None = None
    price_target: float | None = None
    current_price: float | None = None
    upside_pct: float | None = None
    num_analysts: int | None = None


@dataclass
class HistoricalPatterns:
    score: float
    pattern_desc: str
    beats_last_4q: int | None = None
    avg_reaction_pct: float | None = None


@dataclass
class Signal:
    ticker: str
    company_name: str
    recommendation: Literal["BUY", "HOLD", "SELL"]
    confidence: float
    final_score: float
    supporting_points: list[str]
    caveats: list[str]
    timestamp: str
    components: dict


def fetch_stock_data(ticker: str, verbose: bool = False) -> StockData | None:
    """Fetch stock data from Yahoo Finance with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if verbose:
                print(f"Fetching data for {ticker}... (attempt {attempt + 1}/{max_retries})", file=sys.stderr)

            stock = yf.Ticker(ticker)
            info = stock.info

            # Validate ticker
            if not info or "regularMarketPrice" not in info:
                return None

            # Fetch earnings history
            try:
                earnings_history = stock.earnings_dates
            except Exception:
                earnings_history = None

            # Fetch analyst info
            try:
                analyst_info = {
                    "recommendations": stock.recommendations,
                    "analyst_price_targets": stock.analyst_price_targets,
                }
            except Exception:
                analyst_info = None

            # Fetch price history (1 year for historical patterns)
            try:
                price_history = stock.history(period="1y")
            except Exception:
                price_history = None

            return StockData(
                ticker=ticker,
                info=info,
                earnings_history=earnings_history,
                analyst_info=analyst_info,
                price_history=price_history,
            )

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                if verbose:
                    print(f"Error fetching {ticker}: {e}. Retrying in {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
            else:
                if verbose:
                    print(f"Failed to fetch {ticker} after {max_retries} attempts", file=sys.stderr)
                return None

    return None


def analyze_earnings_surprise(data: StockData) -> EarningsSurprise | None:
    """Analyze earnings surprise from most recent quarter."""
    if data.earnings_history is None or data.earnings_history.empty:
        return None

    try:
        # Get most recent earnings with actual data
        recent = data.earnings_history.sort_index(ascending=False).head(10)

        for idx, row in recent.iterrows():
            if pd.notna(row.get("Reported EPS")) and pd.notna(row.get("EPS Estimate")):
                actual = float(row["Reported EPS"])
                expected = float(row["EPS Estimate"])

                if expected == 0:
                    continue

                surprise_pct = ((actual - expected) / abs(expected)) * 100

                # Score based on surprise percentage
                if surprise_pct > 10:
                    score = 1.0
                elif surprise_pct > 5:
                    score = 0.7
                elif surprise_pct > 0:
                    score = 0.3
                elif surprise_pct > -5:
                    score = -0.3
                elif surprise_pct > -10:
                    score = -0.7
                else:
                    score = -1.0

                explanation = f"{'Beat' if surprise_pct > 0 else 'Missed'} by {abs(surprise_pct):.1f}%"

                return EarningsSurprise(
                    score=score,
                    explanation=explanation,
                    actual_eps=actual,
                    expected_eps=expected,
                    surprise_pct=surprise_pct,
                )

        return None

    except Exception:
        return None


def analyze_fundamentals(data: StockData) -> Fundamentals | None:
    """Analyze fundamental metrics."""
    info = data.info
    scores = []
    metrics = {}
    explanations = []

    try:
        # P/E Ratio (lower is better, but consider growth)
        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        if pe_ratio and pe_ratio > 0:
            metrics["pe_ratio"] = round(pe_ratio, 2)
            if pe_ratio < 15:
                scores.append(0.5)
                explanations.append(f"Attractive P/E: {pe_ratio:.1f}x")
            elif pe_ratio > 30:
                scores.append(-0.3)
                explanations.append(f"Elevated P/E: {pe_ratio:.1f}x")
            else:
                scores.append(0.1)

        # Operating Margin
        op_margin = info.get("operatingMargins")
        if op_margin:
            metrics["operating_margin"] = round(op_margin, 3)
            if op_margin > 0.15:
                scores.append(0.5)
                explanations.append(f"Strong margin: {op_margin*100:.1f}%")
            elif op_margin < 0.05:
                scores.append(-0.5)
                explanations.append(f"Weak margin: {op_margin*100:.1f}%")

        # Revenue Growth
        rev_growth = info.get("revenueGrowth")
        if rev_growth:
            metrics["revenue_growth_yoy"] = round(rev_growth, 3)
            if rev_growth > 0.20:
                scores.append(0.5)
                explanations.append(f"Strong growth: {rev_growth*100:.1f}% YoY")
            elif rev_growth < 0.05:
                scores.append(-0.3)
                explanations.append(f"Slow growth: {rev_growth*100:.1f}% YoY")
            else:
                scores.append(0.2)

        # Debt to Equity
        debt_equity = info.get("debtToEquity")
        if debt_equity is not None:
            metrics["debt_to_equity"] = round(debt_equity / 100, 2)
            if debt_equity < 50:
                scores.append(0.3)
            elif debt_equity > 200:
                scores.append(-0.5)
                explanations.append(f"High debt: D/E {debt_equity/100:.1f}x")

        if not scores:
            return None

        # Average and normalize
        avg_score = sum(scores) / len(scores)
        normalized_score = max(-1.0, min(1.0, avg_score))

        explanation = "; ".join(explanations) if explanations else "Mixed fundamentals"

        return Fundamentals(
            score=normalized_score,
            key_metrics=metrics,
            explanation=explanation,
        )

    except Exception:
        return None


def analyze_analyst_sentiment(data: StockData) -> AnalystSentiment | None:
    """Analyze analyst sentiment and price targets."""
    info = data.info

    try:
        # Get current price
        current_price = info.get("regularMarketPrice") or info.get("currentPrice")
        if not current_price:
            return None

        # Get target price
        target_price = info.get("targetMeanPrice")

        # Get number of analysts
        num_analysts = info.get("numberOfAnalystOpinions")

        # Get recommendation
        recommendation = info.get("recommendationKey")

        if not target_price or not recommendation:
            return AnalystSentiment(
                score=None,
                summary="No analyst coverage available",
            )

        # Calculate upside
        upside_pct = ((target_price - current_price) / current_price) * 100

        # Score based on recommendation and upside
        rec_scores = {
            "strong_buy": 1.0,
            "buy": 0.7,
            "hold": 0.0,
            "sell": -0.7,
            "strong_sell": -1.0,
        }

        base_score = rec_scores.get(recommendation, 0.0)

        # Adjust based on upside
        if upside_pct > 20:
            score = min(1.0, base_score + 0.3)
        elif upside_pct > 10:
            score = min(1.0, base_score + 0.15)
        elif upside_pct < -10:
            score = max(-1.0, base_score - 0.3)
        else:
            score = base_score

        # Format recommendation
        rec_display = recommendation.replace("_", " ").title()

        summary = f"{rec_display} with {abs(upside_pct):.1f}% {'upside' if upside_pct > 0 else 'downside'}"
        if num_analysts:
            summary += f" ({num_analysts} analysts)"

        return AnalystSentiment(
            score=score,
            summary=summary,
            consensus_rating=rec_display,
            price_target=target_price,
            current_price=current_price,
            upside_pct=upside_pct,
            num_analysts=num_analysts,
        )

    except Exception:
        return AnalystSentiment(
            score=None,
            summary="Error analyzing analyst sentiment",
        )


def analyze_historical_patterns(data: StockData) -> HistoricalPatterns | None:
    """Analyze historical earnings patterns."""
    if data.earnings_history is None or data.price_history is None:
        return None

    if data.earnings_history.empty or data.price_history.empty:
        return None

    try:
        # Get last 4 quarters earnings dates
        earnings_dates = data.earnings_history.sort_index(ascending=False).head(4)

        beats = 0
        reactions = []

        for earnings_date, row in earnings_dates.iterrows():
            if pd.notna(row.get("Reported EPS")) and pd.notna(row.get("EPS Estimate")):
                actual = float(row["Reported EPS"])
                expected = float(row["EPS Estimate"])

                if actual > expected:
                    beats += 1

                # Try to get price reaction (day of earnings)
                try:
                    earnings_day = pd.Timestamp(earnings_date).date()

                    # Find closest trading day
                    price_data = data.price_history[data.price_history.index.date == earnings_day]

                    if not price_data.empty:
                        day_change = ((price_data["Close"].iloc[0] - price_data["Open"].iloc[0]) / price_data["Open"].iloc[0]) * 100
                        reactions.append(day_change)
                except Exception:
                    continue

        total_quarters = len(earnings_dates)
        if total_quarters == 0:
            return None

        # Score based on beat rate
        beat_rate = beats / total_quarters

        if beat_rate == 1.0:
            score = 0.8
        elif beat_rate >= 0.75:
            score = 0.5
        elif beat_rate >= 0.5:
            score = 0.0
        elif beat_rate >= 0.25:
            score = -0.5
        else:
            score = -0.8

        # Pattern description
        pattern_desc = f"{beats}/{total_quarters} quarters beat expectations"

        if reactions:
            avg_reaction = sum(reactions) / len(reactions)
            pattern_desc += f", avg reaction {avg_reaction:+.1f}%"
        else:
            avg_reaction = None

        return HistoricalPatterns(
            score=score,
            pattern_desc=pattern_desc,
            beats_last_4q=beats,
            avg_reaction_pct=avg_reaction,
        )

    except Exception:
        return None


def synthesize_signal(
    ticker: str,
    company_name: str,
    earnings: EarningsSurprise | None,
    fundamentals: Fundamentals | None,
    analysts: AnalystSentiment | None,
    historical: HistoricalPatterns | None,
) -> Signal:
    """Synthesize all components into a final signal."""

    # Collect available components with weights
    components = []
    weights = []

    if earnings:
        components.append(("earnings", earnings.score))
        weights.append(0.35)

    if fundamentals:
        components.append(("fundamentals", fundamentals.score))
        weights.append(0.25)

    if analysts and analysts.score is not None:
        components.append(("analysts", analysts.score))
        weights.append(0.25)

    if historical:
        components.append(("historical", historical.score))
        weights.append(0.15)

    # Require at least 2 components
    if len(components) < 2:
        return Signal(
            ticker=ticker,
            company_name=company_name,
            recommendation="HOLD",
            confidence=0.0,
            final_score=0.0,
            supporting_points=["Insufficient data for analysis"],
            caveats=["Limited data available"],
            timestamp=datetime.now().isoformat(),
            components={},
        )

    # Normalize weights
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    # Calculate weighted score
    final_score = sum(score * weight for (_, score), weight in zip(components, normalized_weights))

    # Determine recommendation
    if final_score > 0.33:
        recommendation = "BUY"
    elif final_score < -0.33:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    confidence = abs(final_score)

    # Generate supporting points
    supporting_points = []

    if earnings and earnings.actual_eps is not None:
        supporting_points.append(
            f"{earnings.explanation} - EPS ${earnings.actual_eps:.2f} vs ${earnings.expected_eps:.2f} expected"
        )

    if fundamentals and fundamentals.explanation:
        supporting_points.append(fundamentals.explanation)

    if analysts and analysts.summary:
        supporting_points.append(f"Analyst consensus: {analysts.summary}")

    if historical and historical.pattern_desc:
        supporting_points.append(f"Historical pattern: {historical.pattern_desc}")

    # Generate caveats
    caveats = []

    if not analysts or analysts.score is None:
        caveats.append("Limited or no analyst coverage")

    if not earnings:
        caveats.append("No recent earnings data available")

    if len(components) < 4:
        caveats.append("Analysis based on limited data components")

    if not caveats:
        caveats.append("Market conditions can change rapidly")

    # Build components dict for output
    components_dict = {}
    if earnings:
        components_dict["earnings_surprise"] = {
            "score": earnings.score,
            "actual_eps": earnings.actual_eps,
            "expected_eps": earnings.expected_eps,
            "surprise_pct": earnings.surprise_pct,
            "explanation": earnings.explanation,
        }

    if fundamentals:
        components_dict["fundamentals"] = {
            "score": fundamentals.score,
            **fundamentals.key_metrics,
        }

    if analysts:
        components_dict["analyst_sentiment"] = {
            "score": analysts.score,
            "consensus_rating": analysts.consensus_rating,
            "price_target": analysts.price_target,
            "current_price": analysts.current_price,
            "upside_pct": analysts.upside_pct,
            "num_analysts": analysts.num_analysts,
        }

    if historical:
        components_dict["historical_patterns"] = {
            "score": historical.score,
            "beats_last_4q": historical.beats_last_4q,
            "avg_reaction_pct": historical.avg_reaction_pct,
        }

    return Signal(
        ticker=ticker,
        company_name=company_name,
        recommendation=recommendation,
        confidence=confidence,
        final_score=final_score,
        supporting_points=supporting_points[:5],  # Limit to 5
        caveats=caveats[:3],  # Limit to 3
        timestamp=datetime.now().isoformat(),
        components=components_dict,
    )


def format_output_text(signal: Signal) -> str:
    """Format signal as text output."""
    lines = [
        "=" * 77,
        f"STOCK ANALYSIS: {signal.ticker} ({signal.company_name})",
        f"Generated: {signal.timestamp}",
        "=" * 77,
        "",
        f"RECOMMENDATION: {signal.recommendation} (Confidence: {signal.confidence*100:.0f}%)",
        "",
        "SUPPORTING POINTS:",
    ]

    for point in signal.supporting_points:
        lines.append(f"• {point}")

    lines.extend([
        "",
        "CAVEATS:",
    ])

    for caveat in signal.caveats:
        lines.append(f"• {caveat}")

    lines.extend([
        "",
        "=" * 77,
        "DISCLAIMER: This analysis is for informational purposes only and does NOT",
        "constitute financial advice. Consult a licensed financial advisor before",
        "making investment decisions. Data provided by Yahoo Finance.",
        "=" * 77,
    ])

    return "\n".join(lines)


def format_output_json(signal: Signal) -> str:
    """Format signal as JSON output."""
    output = {
        **asdict(signal),
        "disclaimer": "NOT FINANCIAL ADVICE. For informational purposes only.",
    }
    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze stocks using Yahoo Finance data"
    )
    parser.add_argument(
        "tickers",
        nargs="+",
        help="Stock ticker(s) to analyze"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output to stderr"
    )

    args = parser.parse_args()

    results = []

    for ticker in args.tickers:
        ticker = ticker.upper()

        if args.verbose:
            print(f"\n=== Analyzing {ticker} ===\n", file=sys.stderr)

        # Fetch data
        data = fetch_stock_data(ticker, verbose=args.verbose)

        if data is None:
            print(f"Error: Invalid ticker '{ticker}' or data unavailable", file=sys.stderr)
            sys.exit(2)

        # Get company name
        company_name = data.info.get("longName") or data.info.get("shortName") or ticker

        # Analyze all components
        earnings = analyze_earnings_surprise(data)
        fundamentals = analyze_fundamentals(data)
        analysts = analyze_analyst_sentiment(data)
        historical = analyze_historical_patterns(data)

        if args.verbose:
            print(f"Components analyzed:", file=sys.stderr)
            print(f"  Earnings: {'✓' if earnings else '✗'}", file=sys.stderr)
            print(f"  Fundamentals: {'✓' if fundamentals else '✗'}", file=sys.stderr)
            print(f"  Analysts: {'✓' if analysts and analysts.score else '✗'}", file=sys.stderr)
            print(f"  Historical: {'✓' if historical else '✗'}\n", file=sys.stderr)

        # Synthesize signal
        signal = synthesize_signal(
            ticker=ticker,
            company_name=company_name,
            earnings=earnings,
            fundamentals=fundamentals,
            analysts=analysts,
            historical=historical,
        )

        results.append(signal)

    # Output results
    if args.output == "json":
        if len(results) == 1:
            print(format_output_json(results[0]))
        else:
            print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        for i, signal in enumerate(results):
            if i > 0:
                print("\n")
            print(format_output_text(signal))


if __name__ == "__main__":
    main()
