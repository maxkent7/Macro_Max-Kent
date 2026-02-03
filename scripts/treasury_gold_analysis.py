import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'market_data.db')


def load_data():
    """Load market_data table into a pandas DataFrame sorted by date."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('SELECT * FROM market_data', conn, parse_dates=['date'])
    conn.close()
    df.sort_values('date', inplace=True)
    return df


def summarize_relationship(df):
    subset = df[['date', 'treasury', 'gold']].dropna()
    if subset.empty:
        print('No overlapping treasury and gold data found.')
        return None
    correlation = subset['treasury'].corr(subset['gold'])
    latest = subset.iloc[-1]
    print(f"Latest data ({latest['date'].date()}):")
    print(f"  10Y Treasury: {latest['treasury']}")
    print(f"  Gold (GLD): {latest['gold']}")
    print(f"Correlation (treasury vs gold): {correlation:.3f}")
    return subset


def plot_relationship(subset):
    fig, axes = plt.subplots(2, 1, figsize=(10, 10))

    axes[0].plot(subset['date'], subset['treasury'], label='10Y Treasury', color='green')
    axes[0].set_ylabel('Yield')
    axes[0].set_title('10Y Treasury Yield Over Time')
    axes[0].grid(True)

    axes[1].plot(subset['date'], subset['gold'], label='Gold (GLD)', color='goldenrod')
    axes[1].set_ylabel('Price')
    axes[1].set_title('Gold (GLD) Price Over Time')
    axes[1].grid(True)

    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8, 6))
    plt.scatter(subset['treasury'], subset['gold'], s=12, alpha=0.7)
    plt.xlabel('10Y Treasury Yield')
    plt.ylabel('Gold (GLD) Price')
    plt.title('Gold vs 10Y Treasury Yield')
    plt.grid(True)
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

    subset = summarize_relationship(df)
    if subset is None:
        return

    plot_relationship(subset)


if __name__ == '__main__':
    main()
