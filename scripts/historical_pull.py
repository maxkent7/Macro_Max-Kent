import os
import sqlite3
import requests
from datetime import datetime

API_KEY = "FNCR1BXVQXZ2Q8A0"
BASE_URL = 'https://www.alphavantage.co/query'
DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'market_data.db')


def create_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS market_data (
            date TEXT PRIMARY KEY,
            eurusd REAL,
            sp500 REAL,
            treasury REAL
        )
        """
    )
    conn.commit()
    conn.close()


def fetch_fx_history():
    params = {
        'function': 'FX_DAILY',
        'from_symbol': 'EUR',
        'to_symbol': 'USD',
        'outputsize': 'full',
        'apikey': API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get('Time Series FX (Daily)', {})
    result = {}
    for d, v in data.items():
        if d >= '2001-01-01':
            result[d] = float(v['4. close'])
    return result


def fetch_sp500_history():
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': 'SPY',
        'outputsize': 'full',
        'apikey': API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get('Time Series (Daily)', {})
    result = {}
    for d, v in data.items():
        if d >= '2001-01-01':
            result[d] = float(v['4. close'])
    return result


def fetch_treasury_history():
    params = {
        'function': 'TREASURY_YIELD',
        'interval': 'daily',
        'maturity': '10year',
        'apikey': API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get('data', [])
    result = {}
    for item in data:
        d = item.get('date')
        if not d or d < '2001-01-01':
            continue
        val = item.get('value')
        try:
            result[d] = float(val)
        except (TypeError, ValueError):
            continue
    return result


def update_db(fx, spx, tsy):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    dates = set(fx) | set(spx) | set(tsy)
    for d in sorted(dates):
        cur.execute(
            'INSERT OR REPLACE INTO market_data (date, eurusd, sp500, treasury) VALUES (?, ?, ?, ?)',
            (d, fx.get(d), spx.get(d), tsy.get(d)),
        )
    conn.commit()
    conn.close()


def main():
    if not API_KEY:
        raise SystemExit('ALPHAVANTAGE_API_KEY environment variable not set')
    create_db()
    fx = fetch_fx_history()
    spx = fetch_sp500_history()
    tsy = fetch_treasury_history()
    update_db(fx, spx, tsy)
    if fx:
        latest_date = max(fx)
        print(f"EUR/USD on {latest_date}: {fx[latest_date]}")
    print('API ran ok')


if __name__ == '__main__':
    main()
