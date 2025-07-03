import os
import sqlite3
from datetime import timedelta

import pandas as pd
import matplotlib.pyplot as plt

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'market_data.db')


def load_data():
    """Load market_data table into a pandas DataFrame sorted by date."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('SELECT * FROM market_data', conn, parse_dates=['date'])
    conn.close()
    df.sort_values('date', inplace=True)
    return df


def print_latest_prices(df):
    """Print the most recent prices for EUR/USD, SPY, and Treasuries."""
    latest = df.iloc[-1]
    print(f"Latest data ({latest['date'].date()}):")
    print(f"  EUR/USD: {latest['eurusd']}")
    print(f"  SPY: {latest['sp500']}")
    print(f"  10Y Treasury: {latest['treasury']}")


def plot_period(df, days, label):
    """Create scatter plots for the given timeframe."""
    last_date = df['date'].max()
    start_date = last_date - timedelta(days=days)
    subset = df[df['date'] >= start_date]

    fig, axes = plt.subplots(3, 1, figsize=(10, 12))

    axes[0].scatter(subset['date'], subset['eurusd'], s=10)
    axes[0].set_title(f'EUR/USD - last {label}')
    axes[0].set_ylabel('Price')

    axes[1].scatter(subset['date'], subset['sp500'], s=10, color='orange')
    axes[1].set_title(f'SPY - last {label}')
    axes[1].set_ylabel('Price')

    axes[2].scatter(subset['date'], subset['treasury'], s=10, color='green')
    axes[2].set_title(f'10Y Treasury Yield - last {label}')
    axes[2].set_ylabel('Yield')

    for ax in axes:
        ax.grid(True)

    plt.tight_layout()
    plt.show()


def main():
    if not os.path.exists(DB_PATH):
        print('Database not found. Run pull scripts first.')
        return

    df = load_data()
    if df.empty:
        print('No data available.')
        return

    print_latest_prices(df)

    plot_period(df, 90, '3 months')
    plot_period(df, 14, '2 weeks')


if __name__ == '__main__':
    main()

