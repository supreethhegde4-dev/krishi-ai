import os
import sys
import pandas as pd
import duckdb

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("1. INSPECTING COMMODITY PRICE CSV")
print("="*60)
csv_path = "data/marketplace_extracted/commodity_price.csv"
if os.path.exists(csv_path):
    df_c = pd.read_csv(csv_path)
    print(f"Shape: {df_c.shape}")
    print("Columns and Types:")
    for col, dtype in df_c.dtypes.items():
        nulls = df_c[col].isnull().sum()
        print(f"  - {col} ({dtype}): {nulls} nulls")
    print("\nSample row:")
    print(df_c.head(1).to_dict(orient="records"))
    print(f"Unique commodities ({df_c['Commodity'].nunique()}):", df_c['Commodity'].unique()[:10])
    print(f"Unique states ({df_c['State'].nunique()}):", df_c['State'].unique()[:10])
else:
    print(f"File not found: {csv_path}")

print("\n" + "="*60)
print("2. INSPECTING HISTORICAL PARQUET (DUCKDB)")
print("="*60)
parquet_dir = "data/historical_parquet/parquet"
if os.path.exists(parquet_dir):
    con = duckdb.connect()
    parquet_files = [os.path.join(parquet_dir, f) for f in os.listdir(parquet_dir) if f.endswith(".parquet")]
    print(f"Discovered {len(parquet_files)} parquet files:")
    for pf in parquet_files:
        sz = os.path.getsize(pf) / (1024 * 1024)
        cnt = con.execute(f"SELECT count(*) FROM read_parquet('{pf.replace(chr(92), '/')}')").fetchone()[0]
        print(f"  - {os.path.basename(pf)}: {sz:.2f} MB, {cnt:,} rows")

    summary = con.execute(f"""
        SELECT 
            count(*) as total_rows,
            min(Arrival_Date) as min_date,
            max(Arrival_Date) as max_date,
            count(distinct State) as states_count,
            count(distinct District) as districts_count,
            count(distinct Market) as markets_count,
            count(distinct Commodity) as commodities_count
        FROM read_parquet('{parquet_dir.replace(chr(92), "/")}/*.parquet')
    """).df()
    print("\nAggregated Time-Series Summary:")
    print(summary.to_string(index=False))

    schema_df = con.execute(f"""
        DESCRIBE SELECT * FROM read_parquet('{parquet_files[0].replace(chr(92), "/")}') LIMIT 1
    """).df()
    print("\nParquet Schema:")
    for _, row in schema_df.iterrows():
        print(f"  - {row['column_name']}: {row['column_type']}")

    print("\nTop 10 Commodities by record count:")
    top_crops = con.execute(f"""
        SELECT Commodity, count(*) as count, round(avg(Modal_Price), 1) as avg_modal_quintal
        FROM read_parquet('{parquet_dir.replace(chr(92), "/")}/*.parquet')
        GROUP BY Commodity
        ORDER BY count DESC
        LIMIT 10
    """).df()
    print(top_crops.to_string(index=False))

print("\n" + "="*60)
print("3. INSPECTING TRAINED ML MODELS")
print("="*60)
import joblib
for m in ["models/crop_recommendation_model.pkl", "models/yield_prediction_model.pkl"]:
    if os.path.exists(m):
        obj = joblib.load(m)
        print(f"\nModel: {m}")
        if isinstance(obj, dict):
            print("  Type: Dict metadata bundle")
            print("  Keys:", list(obj.keys()))
            if "model" in obj:
                print("  Underlying model:", type(obj["model"]))
            if "features" in obj:
                print("  Features:", obj["features"])
        else:
            print("  Type:", type(obj))
