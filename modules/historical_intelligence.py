"""
Historical Agricultural Intelligence Module
Performs high-speed analytical aggregation and anomaly detection across 16.37M parquet records
using DuckDB. Answers: "What happened in the past?"
"""
import os
import duckdb
import pandas as pd
import numpy as np

PARQUET_GLOB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "historical_parquet", "parquet", "*.parquet"
).replace("\\", "/")


def get_historical_database_metrics():
    """Returns macro statistics for the 16.37M parquet dataset."""
    con = duckdb.connect()
    try:
        query = f"""
            SELECT 
                count(*) as total_records,
                min(Arrival_Date) as min_date,
                max(Arrival_Date) as max_date,
                count(distinct State) as total_states,
                count(distinct District) as total_districts,
                count(distinct Market) as total_markets,
                count(distinct Commodity) as total_commodities
            FROM read_parquet('{PARQUET_GLOB}')
        """
        df = con.execute(query).df()
        return df.iloc[0].to_dict()
    finally:
        con.close()


def get_commodity_yoy_trends(commodity: str, state: str = None, district: str = None):
    """
    Computes Year-over-Year price statistics, price ranges, and growth rates
    for a given commodity.
    """
    con = duckdb.connect()
    try:
        where_clauses = [f"Commodity = '{commodity}'", "Modal_Price > 0"]
        if state and state != "All States":
            where_clauses.append(f"State = '{state}'")
        if district and district != "All Districts":
            where_clauses.append(f"District = '{district}'")
        
        where_str = " AND ".join(where_clauses)

        query = f"""
            SELECT 
                YEAR(CAST(Arrival_Date AS DATE)) as year,
                count(*) as total_arrivals,
                round(avg(Modal_Price) / 100.0, 2) as avg_modal_price_kg,
                round(min(Min_Price) / 100.0, 2) as min_price_kg,
                round(max(Max_Price) / 100.0, 2) as max_price_kg,
                round(stddev(Modal_Price) / 100.0, 2) as price_stddev
            FROM read_parquet('{PARQUET_GLOB}')
            WHERE {where_str}
            GROUP BY year
            ORDER BY year ASC
        """
        df = con.execute(query).df()
        
        if not df.empty:
            # Calculate YoY percentage growth
            df["yoy_growth_pct"] = df["avg_modal_price_kg"].pct_change() * 100.0
            df["yoy_growth_pct"] = df["yoy_growth_pct"].fillna(0.0).round(1)
            
            # Overall CAGR (2023 to 2026 or available span)
            if len(df) > 1 and df["avg_modal_price_kg"].iloc[0] > 0:
                p_start = df["avg_modal_price_kg"].iloc[0]
                p_end = df["avg_modal_price_kg"].iloc[-1]
                years = len(df) - 1
                cagr = ((p_end / p_start) ** (1 / years) - 1) * 100.0
            else:
                cagr = 0.0
        else:
            cagr = 0.0

        return {
            "commodity": commodity,
            "yoy_records": df.to_dict(orient="records"),
            "df_yoy": df,
            "cagr_pct": round(cagr, 1)
        }
    finally:
        con.close()


def get_monthly_seasonal_profile(commodity: str, state: str = None):
    """
    Computes average price and arrival volume across 12 calendar months (Jan to Dec)
    to identify seasonal troughs and peaks.
    """
    con = duckdb.connect()
    try:
        where_clauses = [f"Commodity = '{commodity}'", "Modal_Price > 0"]
        if state and state != "All States":
            where_clauses.append(f"State = '{state}'")
        
        where_str = " AND ".join(where_clauses)

        query = f"""
            SELECT 
                MONTH(CAST(Arrival_Date AS DATE)) as month_num,
                count(*) as arrival_count,
                round(avg(Modal_Price) / 100.0, 2) as avg_price_kg
            FROM read_parquet('{PARQUET_GLOB}')
            WHERE {where_str}
            GROUP BY month_num
            ORDER BY month_num ASC
        """
        df = con.execute(query).df()
        
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        if not df.empty:
            df["month_name"] = df["month_num"].apply(lambda m: month_names[int(m)-1] if 1 <= int(m) <= 12 else str(m))
            mean_price = df["avg_price_kg"].mean()
            df["seasonality_index"] = round((df["avg_price_kg"] / (mean_price if mean_price > 0 else 1.0)) * 100.0, 1)
            
            peak_row = df.loc[df["avg_price_kg"].idxmax()]
            trough_row = df.loc[df["avg_price_kg"].idxmin()]
            
            return {
                "df_seasonal": df,
                "peak_month": peak_row["month_name"],
                "peak_price_kg": peak_row["avg_price_kg"],
                "trough_month": trough_row["month_name"],
                "trough_price_kg": trough_row["avg_price_kg"],
                "price_spread_pct": round(((peak_row["avg_price_kg"] - trough_row["avg_price_kg"]) / (trough_row["avg_price_kg"] if trough_row["avg_price_kg"] > 0 else 1)) * 100, 1)
            }
        else:
            return {"df_seasonal": pd.DataFrame(), "peak_month": "N/A", "peak_price_kg": 0, "trough_month": "N/A", "trough_price_kg": 0, "price_spread_pct": 0}
    finally:
        con.close()


def detect_historical_price_anomalies(commodity: str, state: str = None, threshold_std: float = 2.0):
    """
    Identifies historical price shock dates (unusual spikes or price collapses)
    based on rolling z-scores (> 2 standard deviations).
    """
    con = duckdb.connect()
    try:
        where_clauses = [f"Commodity = '{commodity}'", "Modal_Price > 0"]
        if state and state != "All States":
            where_clauses.append(f"State = '{state}'")
        
        where_str = " AND ".join(where_clauses)

        query = f"""
            SELECT 
                Arrival_Date as date_str,
                round(avg(Modal_Price) / 100.0, 2) as modal_price_kg,
                count(*) as transactions
            FROM read_parquet('{PARQUET_GLOB}')
            WHERE {where_str}
            GROUP BY Arrival_Date
            ORDER BY Arrival_Date ASC
        """
        df = con.execute(query).df()
        
        if len(df) < 10:
            return []

        df["date"] = pd.to_datetime(df["date_str"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date")
        
        mean_p = df["modal_price_kg"].mean()
        std_p = df["modal_price_kg"].std()
        if std_p == 0:
            return []

        df["z_score"] = (df["modal_price_kg"] - mean_p) / std_p
        
        # Filter anomalies
        anomalies_df = df[df["z_score"].abs() >= threshold_std].copy()
        anomalies_df["anomaly_type"] = anomalies_df["z_score"].apply(
            lambda z: "Severe Price Spike" if z > 0 else "Severe Price Crash"
        )
        
        results = []
        for _, row in anomalies_df.head(15).iterrows():
            results.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                "price_kg": row["modal_price_kg"],
                "z_score": round(row["z_score"], 2),
                "type": row["anomaly_type"],
                "deviation_pct": round(((row["modal_price_kg"] - mean_p) / mean_p) * 100, 1)
            })
            
        return results
    finally:
        con.close()


def get_regional_market_benchmarks(commodity: str, top_n: int = 10):
    """
    Ranks top performing states and mandis for a commodity by volume and average modal price.
    """
    con = duckdb.connect()
    try:
        query_states = f"""
            SELECT 
                State,
                count(*) as total_arrivals,
                round(avg(Modal_Price) / 100.0, 2) as avg_price_kg,
                round(min(Min_Price) / 100.0, 2) as min_price_kg,
                round(max(Max_Price) / 100.0, 2) as max_price_kg
            FROM read_parquet('{PARQUET_GLOB}')
            WHERE Commodity = '{commodity}' AND Modal_Price > 0
            GROUP BY State
            ORDER BY avg_price_kg DESC
            LIMIT {top_n}
        """
        df_states = con.execute(query_states).df()

        query_mandis = f"""
            SELECT 
                Market,
                District,
                State,
                count(*) as total_arrivals,
                round(avg(Modal_Price) / 100.0, 2) as avg_price_kg
            FROM read_parquet('{PARQUET_GLOB}')
            WHERE Commodity = '{commodity}' AND Modal_Price > 0
            GROUP BY Market, District, State
            ORDER BY total_arrivals DESC
            LIMIT {top_n}
        """
        df_mandis = con.execute(query_mandis).df()

        return {
            "top_states_by_price": df_states,
            "top_mandis_by_volume": df_mandis
        }
    finally:
        con.close()
