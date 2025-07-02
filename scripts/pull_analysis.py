import os
import sqlite3
from datetime import datetime, timedelta

try:
    import pandas as pd
except ImportError:  # fallback if pandas is not installed
    pd = None

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'market_data.db')


def load_data():
    if pd:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql('SELECT * FROM market_data', conn, parse_dates=["date"])
        conn.close()
        df.sort_values('date', inplace=True)
        return df
    else:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT date, eurusd, sp500, treasury FROM market_data')
        rows = cur.fetchall()
        conn.close()
        rows = [(datetime.strptime(r[0], '%Y-%m-%d').date(), r[1], r[2], r[3]) for r in rows]
        rows.sort(key=lambda x: x[0])
        return rows


def summarize():
    data = load_data()
    if not data:
        print('No data found')
        return
    if pd:
        today = data['date'].max()
        today_row = data[data['date'] == today].iloc[0]
        last_week = data[data['date'] >= today - timedelta(days=6)]
        year_ago_date = today - timedelta(days=365)
        year_ago = data.loc[data['date'] <= year_ago_date].tail(1)
        print(f"Today's data ({today.date()}): EUR/USD={today_row['eurusd']}, SP500={today_row['sp500']}, Treasury={today_row['treasury']}")
        print('\nLast 7 days average:')
        print(last_week[['eurusd', 'sp500', 'treasury']].mean())
        if not year_ago.empty:
            yoy = ((today_row[['eurusd', 'sp500', 'treasury']] - year_ago[['eurusd', 'sp500', 'treasury']].iloc[0]) / year_ago[['eurusd', 'sp500', 'treasury']].iloc[0]) * 100
            print('\nYear over Year change (%):')
            print(yoy)
    else:
        today = data[-1][0]
        today_row = data[-1]
        week_data = [r for r in data if r[0] >= today - timedelta(days=6)]
        print(f"Today's data ({today}): EUR/USD={today_row[1]}, SP500={today_row[2]}, Treasury={today_row[3]}")
        if week_data:
            avg_fx = sum(r[1] for r in week_data if r[1] is not None) / len([r for r in week_data if r[1] is not None])
            avg_sp = sum(r[2] for r in week_data if r[2] is not None) / len([r for r in week_data if r[2] is not None])
            avg_ts = sum(r[3] for r in week_data if r[3] is not None) / len([r for r in week_data if r[3] is not None])
            print('\nLast 7 days average:')
            print(f'EUR/USD={avg_fx}, SP500={avg_sp}, Treasury={avg_ts}')
        year_ago_date = today - timedelta(days=365)
        year_ago_rows = [r for r in data if r[0] <= year_ago_date]
        if year_ago_rows:
            year_ago = year_ago_rows[-1]
            yoy_fx = ((today_row[1] - year_ago[1]) / year_ago[1]) * 100 if year_ago[1] else None
            yoy_sp = ((today_row[2] - year_ago[2]) / year_ago[2]) * 100 if year_ago[2] else None
            yoy_ts = ((today_row[3] - year_ago[3]) / year_ago[3]) * 100 if year_ago[3] else None
            print('\nYear over Year change (%):')
            print(f'EUR/USD={yoy_fx}, SP500={yoy_sp}, Treasury={yoy_ts}')


def main():
    if not os.path.exists(DB_PATH):
        print('Database not found. Run pull scripts first.')
        return
    summarize()


if __name__ == '__main__':
    main()
