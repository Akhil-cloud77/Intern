"""
main.py
FastAPI backend — run with: uvicorn main:app --reload
Then open: http://127.0.0.1:8000/docs  (auto Swagger UI!)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import database as db
import os

# ── Create the FastAPI app ─────────────────────────────────────────────────────
app = FastAPI(
    title="Stock Intelligence Dashboard API",
    description="Mini financial data platform with real NSE stock data.",
    version="1.0.0",
)

# ── Allow frontend (HTML page) to call this API ────────────────────────────────
# Without this, the browser blocks cross-origin requests (CORS error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, replace * with your actual domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve the frontend HTML from the /frontend folder ─────────────────────────
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


# ══════════════════════════════════════════════════════════════════════════════
# ROOT — serves the dashboard HTML page
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/", include_in_schema=False)
def root():
    """Serves the frontend dashboard."""
    return FileResponse("frontend/index.html")


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 1: GET /companies
# Returns all available stock symbols
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/companies", tags=["Stocks"])
def get_companies():
    """
    Returns a list of all companies available in the database.
    
    Example response:
    { "companies": ["HDFCBANK", "INFY", "RELIANCE", "TCS", ...] }
    """
    companies = db.get_companies()
    if not companies:
        raise HTTPException(
            status_code=404,
            detail="No companies found. Run data_fetch.py first."
        )
    return {"companies": companies, "count": len(companies)}


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 2: GET /data/{symbol}
# Returns last 30 days of stock data for a given symbol
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/data/{symbol}", tags=["Stocks"])
def get_stock_data(symbol: str):
    """
    Returns the last 30 days of stock data for a company.
    
    - **symbol**: Stock symbol e.g. TCS, INFY, RELIANCE
    
    Includes: open, high, low, close, volume, daily_return, ma_7, volatility, momentum
    """
    symbol = symbol.upper()  # normalize: tcs → TCS
    df = db.get_last_30_days(symbol)

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for symbol '{symbol}'. Check spelling."
        )

    return {
        "symbol": symbol,
        "count":  len(df),
        "data":   df.to_dict(orient="records"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 3: GET /summary/{symbol}
# Returns 52-week stats + custom metrics for a symbol
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/summary/{symbol}", tags=["Stocks"])
def get_summary(symbol: str):
    """
    Returns a summary for a stock symbol including:
    - 52-week high and low
    - Average closing price
    - Volatility score (custom metric)
    - Momentum score (custom metric)
    """
    symbol = symbol.upper()
    summary = db.get_summary(symbol)

    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"No summary data for '{symbol}'."
        )

    return summary


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 4 (BONUS): GET /compare?symbol1=INFY&symbol2=TCS
# Compares two stocks side by side
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/compare", tags=["Comparison"])
def compare_stocks(symbol1: str, symbol2: str):
    """
    Compares two stocks' performance over the last 30 days.
    
    Example: /compare?symbol1=INFY&symbol2=TCS
    
    Returns close prices, daily returns, and momentum for both.
    """
    s1 = symbol1.upper()
    s2 = symbol2.upper()

    if s1 == s2:
        raise HTTPException(
            status_code=400,
            detail="Please provide two different stock symbols."
        )

    result = db.get_compare(s1, s2)

    if not result[s1] or not result[s2]:
        raise HTTPException(
            status_code=404,
            detail=f"Data missing for one or both symbols: {s1}, {s2}"
        )

    return {
        "comparison": result,
        "symbols": [s1, s2],
    }


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 5 (BONUS): GET /gainers-losers
# Returns top 3 gainers and losers of the day
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/gainers-losers", tags=["Insights"])
def gainers_losers():
    """
    Returns the top 3 gainers and top 3 losers based on latest daily return.
    Great for the dashboard's 'Market Insights' section.
    """
    result = db.get_top_gainers_losers()
    return result


# ══════════════════════════════════════════════════════════════════════════════
# STARTUP EVENT — auto-fetch data when server starts (if DB is empty)
# ══════════════════════════════════════════════════════════════════════════════
@app.on_event("startup")
def startup_event():
    """
    When the server starts, check if we have data.
    If not, automatically fetch it. This runs once on launch.
    """
    companies = db.get_companies()
    if not companies:
        print("Database is empty — fetching stock data now...")
        from data_fetch import fetch_all
        fetch_all()
    else:
        print(f"Database ready. {len(companies)} stocks loaded.")
