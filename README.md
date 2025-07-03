Welcome to Max's macro analysis repo.
Each week I'll be analyzing the FX spot market, choosing a different cross to trade, and discussing the short and long term result of that trade.

Please feel free to reach out to me at @max-kent-23 on instagram

## Setup

1. Install the requirements:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the repository root with your API key:

```
ALPHAVANTAGE_API_KEY=YOUR_KEY_HERE
```

The `.env` file is ignored by git so your key won't be committed.

3. Run one of the data scripts, e.g.:

```bash
python scripts/daily_pull.py
```

The scripts automatically load the `.env` file using `python-dotenv`.
