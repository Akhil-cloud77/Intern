"""
data_fetch.py
Fetches real Indian stock data using yfinance,
cleans it, and calculates all required metrics.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from database import save_to_db

# ─── List of Indian stocks to track ───────────────────────────────────────────
# .NS = NSE (National Stock Exchange) suffix required by yfinance
STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS":      "TCS.NS",
    "INFY":     "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "WIPRO":    "WIPRO.NS",
    "ICICIBANK":"ICICIBANK.NS",
    "SBIN":     "SBIN.NS",
    "BAJFINANCE":"BAJFINANCE.NS",
}

def fetch_and_process(symbol: str, ticker: str) -> pd.DataFrame:
    """
    Downloads 1 year of data for a stock, cleans it,
    and adds calculated metrics. Returns a clean DataFrame.
    """
    print(f"  Fetching {symbol}...")

    # Download 1 year of daily OHLCV data
    raw = yf.download(ticker, period="1y", interval="1d", progress=False)

    if raw.empty:
        print(f"  WARNING: No data for {symbol}, skipping.")
        return pd.DataFrame()

    # ── Flatten multi-level columns if present ─────────────────────────────
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    # ── Rename columns to lowercase ────────────────────────────────────────
    raw = raw.rename(columns={
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Volume": "volume"
    })

    # ── Keep only the columns we need ─────────────────────────────────────
    df = raw[["open", "high", "low", "close", "volume"]].copy()

    # ── Clean: drop rows where close price is missing ──────────────────────
    df.dropna(subset=["close"], inplace=True)

    # ── Fix date column ────────────────────────────────────────────────────
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df.reset_index(inplace=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")  # clean string format

    # ── Add symbol column ──────────────────────────────────────────────────
    df["symbol"] = symbol

    # ── Metric 1: Daily Return (%) ─────────────────────────────────────────
    # Formula: (Close - Open) / Open * 100
    df["daily_return"] = ((df["close"] - df["open"]) / df["open"] * 100).round(2)

    # ── Metric 2: 7-day Moving Average ────────────────────────────────────
    # Average of last 7 closing prices — smooths out daily noise
    df["ma_7"] = df["close"].rolling(window=7).mean().round(2)

    # ── Metric 3: 52-week High & Low ──────────────────────────────────────
    df["week52_high"] = df["close"].max().round(2)
    df["week52_low"]  = df["close"].min().round(2)

    # ── Metric 4 (CREATIVE): Volatility Score ─────────────────────────────
    # Standard deviation of daily returns over last 30 days
    # High score = risky stock, Low score = stable stock
    df["volatility"] = df["daily_return"].rolling(window=30).std().round(2)

    # ── Metric 5 (CREATIVE): Momentum Score ───────────────────────────────
    # Compares today's close to 30-day average
    # Positive = stock trending up, Negative = trending down
    ma_30 = df["close"].rolling(window=30).mean()
    df["momentum"] = ((df["close"] - ma_30) / ma_30 * 100).round(2)

    # ── Fill any remaining NaN values with 0 ──────────────────────────────
    df.fillna(0, inplace=True)

    return df


def fetch_all():
    """Fetches data for all stocks and saves to database."""
    print("Starting data fetch for all stocks...\n")
    all_data = []

    for symbol, ticker in STOCKS.items():
        df = fetch_and_process(symbol, ticker)
        if not df.empty:
            all_data.append(df)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        save_to_db(combined)
        print(f"\nDone! Saved {len(combined)} rows to database.")
    else:
        print("No data fetched. Check your internet connection.")


if __name__ == "__main__":
    fetch_all()
