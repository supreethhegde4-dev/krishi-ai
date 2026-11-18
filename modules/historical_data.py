"""
Historical Agricultural Market Price Loader using DuckDB and Parquet.
Designed for high performance over millions of records from 2023 to 2026.
"""
import os
import zipfile
import duckdb
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PARQUET_DIR = os.path.join(DATA_DIR, "historical_parquet", "parquet")
DOWNLOADS_ZIP = r"C:\Users\Supreeth hegde\Downloads\archive (1).zip"


def ensure_historical_parquet_available() -> str:
    """Ensures historical parquet files are extracted into data directory."""
    if os.path.exists(PARQUET_DIR) and len(os.listdir(PARQUET_DIR)) >= 4:
        return PARQUET_DIR

    os.makedirs(PARQUET_DIR, exist_ok=True)
    if os.path.exists(DOWNLOADS_ZIP):
        with zipfile.ZipFile(DOWNLOADS_ZIP, 'r') as zf:
            for y in ['2023', '2024', '2025', '2026']:
                member = f"parquet/{y}.parquet"
                try:
                    zf.extract(member, os.path.join(DATA_DIR, "historical_parquet"))
                except Exception:
                    pass
    return PARQUET_DIR


def get_parquet_glob() -> str:
    ensure_historical_parquet_available()
    return os.path.join(PARQUET_DIR, "*.parquet").replace("\\", "/")


def get_distinct_filter_values(
    commodity: Optional[str] = "Tomato",
    state: Optional[str] = None,
    district: Optional[str] = None
) -> Dict[str, List[str]]:
    """
    Retrieves dynamically cascaded filter values using DuckDB lazy aggregation.
    """
    parquet_glob = get_parquet_glob()
    con = duckdb.connect()

    # Base conditions
    conds = []
    if commodity:
        conds.append(f"Commodity = '{commodity}'")
    if state and state != "All States":
        conds.append(f"State = '{state}'")
    if district and district != "All Districts":
        conds.append(f"District = '{district}'")

    where_clause = f"WHERE {' AND '.join(conds)}" if conds else ""

    query = f"""
        SELECT 
            DISTINCT State, District, Market, Variety, Grade
        FROM read_parquet('{parquet_glob}')
        {where_clause}
    """
    try:
        df_filters = con.execute(query).df()
        states = sorted(df_filters['State'].dropna().unique().tolist())
        districts = sorted(df_filters['District'].dropna().unique().tolist())
        markets = sorted(df_filters['Market'].dropna().unique().tolist())
        varieties = sorted(df_filters['Variety'].dropna().unique().tolist())
        grades = sorted(df_filters['Grade'].dropna().unique().tolist())
    except Exception:
        states, districts, markets, varieties, grades = [], [], [], [], []

    # Get commodities list if not already filtered
    try:
        df_comm = con.execute(f"SELECT DISTINCT Commodity FROM read_parquet('{parquet_glob}') LIMIT 200").df()
        commodities = sorted(df_comm['Commodity'].dropna().unique().tolist())
    except Exception:
        commodities = ["Tomato", "Onion", "Potato", "Brinjal", "Banana"]

    return {
        "commodities": commodities,
        "states": states,
        "districts": districts,
        "markets": markets,
        "varieties": varieties,
        "grades": grades
    }


def query_historical_prices(
    commodity: str = "Tomato",
    state: Optional[str] = "Karnataka",
    district: Optional[str] = None,
    markets: Optional[List[str]] = None,
    variety: Optional[str] = None,
    grade: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    aggregation: str = "Daily"  # Daily, Weekly, Monthly
) -> pd.DataFrame:
    """
    Queries historical prices and converts from ₹/quintal to ₹/kg.
    """
    parquet_glob = get_parquet_glob()
    con = duckdb.connect()

    conds = [f"Commodity = '{commodity}'"]
    if state and state != "All States":
        conds.append(f"State = '{state}'")
    if district and district != "All Districts":
        conds.append(f"District = '{district}'")
    if markets and "All Markets" not in markets and len(markets) > 0:
        markets_str = "', '".join([m.replace("'", "''") for m in markets])
        conds.append(f"Market IN ('{markets_str}')")
    if variety and variety != "All Varieties":
        conds.append(f"Variety = '{variety}'")
    if grade and grade != "All Grades":
        conds.append(f"Grade = '{grade}'")
    if start_date:
        conds.append(f"Arrival_Date >= '{start_date}'")
    if end_date:
        conds.append(f"Arrival_Date <= '{end_date}'")

    # Exclude zero/corrupt prices
    conds.append("Modal_Price > 0")

    where_clause = f"WHERE {' AND '.join(conds)}"

    sql = f"""
        SELECT 
            Arrival_Date,
            State,
            District,
            Market,
            Commodity,
            Variety,
            Grade,
            Min_Price / 100.0 AS min_price_kg,
            Max_Price / 100.0 AS max_price_kg,
            Modal_Price / 100.0 AS modal_price_kg
        FROM read_parquet('{parquet_glob}')
        {where_clause}
        ORDER BY Arrival_Date ASC
    """

    df = con.execute(sql).df()
    if df.empty:
        return df

    # Parse dates
    df['date'] = pd.to_datetime(df['Arrival_Date'], errors='coerce')
    df = df.dropna(subset=['date']).sort_values('date')

    # Aggregation
    if aggregation in ["Weekly", "Monthly"]:
        # Group by Market and frequency
        freq = "W-MON" if aggregation == "Weekly" else "MS"
        resampled_dfs = []
        for m_name, group in df.groupby("Market"):
            group = group.set_index("date")
            agg_g = group.resample(freq).agg({
                "min_price_kg": "min",
                "max_price_kg": "max",
                "modal_price_kg": "mean",
                "Market": "first",
                "State": "first",
                "District": "first",
                "Commodity": "first"
            }).dropna(subset=["modal_price_kg"]).reset_index()
            agg_g['Arrival_Date'] = agg_g['date'].dt.strftime('%Y-%m-%d')
            resampled_dfs.append(agg_g)
        if resampled_dfs:
            df = pd.concat(resampled_dfs, ignore_index=True)

    return df
