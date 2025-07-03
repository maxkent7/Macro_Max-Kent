import os
import sqlite3
import requests
from datetime import date

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
if not API_KEY:
    raise SystemExit("ALPHAVANTAGE_API_KEY environment variable not set")
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
    ) # the section goes and looks for the SQL database. 
    conn.commit()
    conn.close()


def fetch_fx_today():
    params = {
        'function': 'CURRENCY_EXCHANGE_RATE',
        'from_currency': 'EUR',
        'to_currency': 'USD',
        'apikey': API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get('Realtime Currency Exchange Rate', {})
    return float(data.get('5. Exchange Rate'))


def fetch_sp500_today():
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': 'SPY',
        'outputsize': 'compact',
        'apikey': API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get('Time Series (Daily)', {})
    if not data:
        return None
    latest_date = sorted(data.keys())[-1]
    return float(data[latest_date]['4. close'])


def fetch_treasury_today():
    params = {
        'function': 'TREASURY_YIELD',
        'interval': 'daily',
        'maturity': '10year',
        'apikey': API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get('data', [])
    if not data:
        return None
    return float(data[0]['value'])


def update_db(fx, spx, tsy):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    d = date.today().isoformat()
    cur.execute(
        'INSERT OR REPLACE INTO market_data (date, eurusd, sp500, treasury) VALUES (?, ?, ?, ?)',
        (d, fx, spx, tsy),
    )
    conn.commit()
    conn.close()


def main():
    if not API_KEY:
        raise SystemExit('ALPHAVANTAGE_API_KEY environment variable not set')
    create_db()
    fx = fetch_fx_today()
    spx = fetch_sp500_today()
    tsy = fetch_treasury_today()
    update_db(fx, spx, tsy)
    print(f"EUR/USD today: {fx}")
    print('API ran ok')


if __name__ == '__main__':
    main()