#  Stock Intelligence Dashboard

A mini financial data platform built with **FastAPI + Python + Chart.js**, tracking real NSE Indian stock data with smart custom metrics.

---

Features

| Feature | Details |
|---|---|
| Real stock data | Fetched from NSE via `yfinance` |
| REST API | 5 endpoints with auto Swagger docs |
| Custom metrics | Volatility Score + Momentum Score |
| Dashboard | Interactive charts with 30/60/90 day filters |
| Compare stocks | Side-by-side comparison chart |
| Gainers/Losers | Real-time top movers widget |

---

##  Custom Metrics (Creativity)

### Volatility Score
> Rolling 30-day standard deviation of daily returns

A high score means the stock moves unpredictably — useful for risk assessment.

### Momentum Score
> `(today's close − 30-day average) / 30-day average × 100`

Positive = stock is trending above its average (bullish signal).
Negative = stock is underperforming its recent average (bearish signal).

---

## Setup Instructions

### 1. Clone the project
```bash
git clone https://github.com/Akhil-cloud77/intern.git
cd stock-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
uvicorn main:app --reload
```

> On first launch, stock data is fetched automatically. This takes ~30 seconds.

### 4. Open the dashboard
```
http://127.0.0.1:8000
```

### 5. View Swagger API docs
```
http://127.0.0.1:8000/docs
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/companies` | GET | List all available stocks |
| `/data/{symbol}` | GET | Last 30 days of OHLCV + metrics |
| `/summary/{symbol}` | GET | 52W high/low, avg, volatility, momentum |
| `/compare?symbol1=X&symbol2=Y` | GET | Compare two stocks |
| `/gainers-losers` | GET | Top 3 gainers and losers |

---

## 📊 Stocks Tracked

`RELIANCE` · `TCS` · `INFY` · `HDFCBANK` · `WIPRO` · `ICICIBANK` · `SBIN` · `BAJFINANCE`

---

## 🗂️ Project Structure

```
stock-dashboard/
├── main.py          ← FastAPI app + all endpoints
├── data_fetch.py    ← yfinance data download + cleaning
├── database.py      ← SQLite setup + query functions
├── requirements.txt
├── README.md
└── frontend/
    └── index.html   ← Dashboard UI (Chart.js)
```

---

## 💡 Design Decisions

- **FastAPI over Flask** — automatic Swagger docs at `/docs`, faster, type-safe
- **SQLite over PostgreSQL** — zero setup, portable, perfect for this scale
- **yfinance** — free, no API key needed, real NSE data
- **Volatility + Momentum** — added as creative metrics beyond the basic requirements
- **CORS enabled** — frontend and backend can run separately without issues

---

## 👨‍💻 Built for Jarnox Internship Assignment
