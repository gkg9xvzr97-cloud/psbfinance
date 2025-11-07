# psbfinance
A student-built finance dashboard to explore stock data and download financials
# Market Intelligence + Portfolio Optimizer (Streamlit)

A Bloomberg-style market dashboard combined with a Modern Portfolio Theory optimizer
(efficient frontier, min-variance, max-Sharpe).

## Run locally
pip install -r requirements.txt
streamlit run app.py

## Notes
- Data source: Yahoo Finance via `yfinance`
- Optimization: scipy.optimize (SLSQP)
