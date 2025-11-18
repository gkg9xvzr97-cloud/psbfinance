import requests
import pandas as pd

ALPHA_KEY = "79T4YLBTP8L9E9FK"

def alpha_overview(symbol: str) -> dict:
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Alpha returns {} when no data; check presence of Name
            return data if data.get("Name") else {}
    except Exception:
        pass
    return {}

def alpha_daily(symbol: str) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            js = r.json()
            ts = js.get("Time Series (Daily)", {})
            if ts:
                df = pd.DataFrame.from_dict(ts, orient="index")
                df.index = pd.to_datetime(df.index)
                df = df.rename(columns={
                    "1. open": "Open", "2. high": "High", "3. low": "Low",
                    "4. close": "Close", "5. volume": "Volume"
                }).sort_index()
                df = df.reset_index().rename(columns={"index": "Date"})
                df[["Open","High","Low","Close","Volume"]] = df[["Open","High","Low","Close","Volume"]].apply(pd.to_numeric, errors="coerce")
                return df
    except Exception:
        pass
    return pd.DataFrame()
