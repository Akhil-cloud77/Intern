"""
database.py
Sets up SQLite database and provides helper functions
to save and query stock data.
"""

import sqlite3
import pandas as pd

DB_PATH = "stocks.db"  # Database file will be created in your project folder


def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def create_table():
    """Creates the stock_data table if it doesn't already exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol      TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            open        REAL,
            high        REAL,
            low         REAL,
            close       REAL,
            volume      REAL,
            daily_return REAL,
            ma_7        REAL,
            week52_high REAL,
            week52_low  REAL,
            volatility  REAL,
            momentum    REAL,
            UNIQUE(symbol, date)   -- prevents duplicate rows
        )
    """)
    conn.commit()
    conn.close()


def save_to_db(df: pd.DataFrame):
    """Saves a DataFrame to the database. Skips duplicates automatically."""
    create_table()
    conn = get_connection()
    # 'replace' on conflict = updates existing rows instead of erroring
    df.to_sql("stock_data", conn, if_exists="append", index=False,
              method="multi")
    conn.close()


def get_companies() -> list:
    """Returns a list of all unique stock symbols in the database."""
    conn = get_connection()
    cursor = conn.execute("SELECT DISTINCT symbol FROM stock_data ORDER BY symbol")
    symbols = [row[0] for row in cursor.fetchall()]
    conn.close()
    return symbols


def get_last_30_days(symbol: str) -> pd.DataFrame:
    """Returns the last 30 trading days of data for a given symbol."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT * FROM stock_data
        WHERE symbol = ?
        ORDER BY date DESC
        LIMIT 30
    """, conn, params=(symbol,))
    conn.close()
    return df.sort_values("date")  # return in ascending date order


def get_summary(symbol: str) -> dict:
    """Returns 52-week high, low, and average close for a symbol."""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT
            MAX(week52_high)   AS high_52w,
            MIN(week52_low)    AS low_52w,
            ROUND(AVG(close),2) AS avg_close,
            MAX(volatility)    AS max_volatility,
            ROUND(AVG(momentum),2) AS avg_momentum
        FROM stock_data
        WHERE symbol = ?
    """, conn, params=(symbol,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "symbol":        symbol,
            "high_52w":      row[0],
            "low_52w":       row[1],
            "avg_close":     row[2],
            "max_volatility": row[3],
            "avg_momentum":  row[4],
        }
    return {}


def get_compare(symbol1: str, symbol2: str) -> dict:
    """Returns last 30 days for two stocks side by side for comparison."""
    df1 = get_last_30_days(symbol1)
    df2 = get_last_30_days(symbol2)

    return {
        symbol1: df1[["date","close","daily_return","ma_7","momentum"]].to_dict(orient="records"),
        symbol2: df2[["date","close","daily_return","ma_7","momentum"]].to_dict(orient="records"),
    }


def get_top_gainers_losers() -> dict:
    """Returns top 3 gainers and losers based on latest daily return."""
    conn = get_connection()

    # Get the most recent date for each symbol
    df = pd.read_sql("""
        SELECT symbol, date, close, daily_return
        FROM stock_data
        WHERE (symbol, date) IN (
            SELECT symbol, MAX(date) FROM stock_data GROUP BY symbol
        )
        ORDER BY daily_return DESC
    """, conn)
    conn.close()

    return {
        "gainers": df.head(3).to_dict(orient="records"),
        "losers":  df.tail(3).to_dict(orient="records"),
    }
