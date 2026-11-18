import os
import sys
import duckdb
import pandas as pd
import numpy as np

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PARQUET_GLOB = os.path.abspath("data/historical_parquet/parquet/*.parquet").replace("\\", "/")
con = duckdb.connect()

query = f"""
    SELECT 
        CAST(Arrival_Date AS DATE) as date,
        round(avg(Modal_Price) / 100.0, 2) as price_kg,
        count(*) as arrival_cnt
    FROM read_parquet('{PARQUET_GLOB}')
    WHERE Commodity = 'Tomato' AND State = 'Karnataka' AND Modal_Price > 0
    GROUP BY date
    ORDER BY date ASC
"""
df = con.execute(query).df()
print(f"Loaded {len(df)} daily price points for Tomato in Karnataka.")
print(df.head(5))
print(df.tail(5))

# Calculate Moving Averages and Rolling Metrics
df["sma_7"] = df["price_kg"].rolling(window=7, min_periods=1).mean()
df["sma_30"] = df["price_kg"].rolling(window=30, min_periods=1).mean()
df["ema_7"] = df["price_kg"].ewm(span=7, adjust=False).mean()
df["ema_30"] = df["price_kg"].ewm(span=30, adjust=False).mean()
df["rolling_std"] = df["price_kg"].rolling(window=30, min_periods=1).std().fillna(1.0)
df["bollinger_upper"] = df["sma_30"] + (2.0 * df["rolling_std"])
df["bollinger_lower"] = (df["sma_30"] - (2.0 * df["rolling_std"])).clip(lower=0.0)

# Slopes (gradient over 7 days vs prior 30 days)
df["pct_change_7d"] = df["price_kg"].pct_change(periods=7) * 100.0
df["pct_change_30d"] = df["price_kg"].pct_change(periods=30) * 100.0
df["arrival_pct_change_7d"] = df["arrival_cnt"].pct_change(periods=7) * 100.0

# Detect Golden Crosses and Death Crosses
df["cross_signal"] = np.where(df["ema_7"] > df["ema_30"], 1, -1)
df["cross_change"] = df["cross_signal"].diff()

bullish_crosses = df[df["cross_change"] == 2]
bearish_crosses = df[df["cross_change"] == -2]

print(f"\nDetected {len(bullish_crosses)} Bullish Reversal Crossovers (Golden Cross).")
print(f"Detected {len(bearish_crosses)} Bearish Collapse Crossovers (Death Cross).")

print("\nSample Bullish Shifts:")
print(bullish_crosses[["date", "price_kg", "sma_7", "sma_30", "pct_change_7d"]].tail(3))

print("\nSample Bearish Shifts:")
print(bearish_crosses[["date", "price_kg", "sma_7", "sma_30", "pct_change_7d"]].tail(3))
