"""
Data Loader & Normalizer for KisanAI Marketplace Data.
Fulfills Phase 1 requirements: inspection, extraction, normalization, and reporting.
"""
import os
import zipfile
import pandas as pd
from typing import Tuple, Dict, Any


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
ZIP_PATH = os.path.join(DATA_DIR, "marketplace_prices.zip")
EXTRACT_DIR = os.path.join(DATA_DIR, "marketplace_extracted")
CSV_PATH = os.path.join(EXTRACT_DIR, "commodity_price.csv")


def ensure_extracted() -> str:
    """Safely extracts marketplace_prices.zip without modifying or deleting the ZIP."""
    if os.path.exists(CSV_PATH):
        return CSV_PATH
    
    if os.path.exists(ZIP_PATH):
        os.makedirs(EXTRACT_DIR, exist_ok=True)
        with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
            zf.extractall(EXTRACT_DIR)
        return CSV_PATH
        
    raise FileNotFoundError(f"Neither {CSV_PATH} nor {ZIP_PATH} found!")


def inspect_marketplace_data() -> Dict[str, Any]:
    """
    Produces comprehensive data inspection report as required by Phase 1.
    """
    csv_file = ensure_extracted()
    
    # Check raw zip contents
    discovered_files = []
    if os.path.exists(ZIP_PATH):
        with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
            discovered_files = [info.filename for info in zf.infolist()]
    else:
        discovered_files = [os.path.basename(csv_file)]
        
    df_raw = pd.read_csv(csv_file)
    total_records = len(df_raw)
    
    # Identify price columns
    price_cols = [c for c in df_raw.columns if 'Price' in c or 'price' in c]
    
    # Check invalid prices
    invalid_price_count = 0
    for col in price_cols:
        try:
            numeric_col = pd.to_numeric(df_raw[col], errors='coerce')
            invalid_price_count += int((numeric_col <= 0).sum() + numeric_col.isna().sum())
        except Exception:
            pass
            
    crops = sorted(df_raw['Commodity'].dropna().unique().tolist())
    markets = sorted(df_raw['Market'].dropna().unique().tolist())
    states = sorted(df_raw['State'].dropna().unique().tolist())
    dates = sorted(df_raw['Arrival_Date'].dropna().unique().tolist())
    
    report = {
        "files_discovered": discovered_files,
        "total_records": total_records,
        "raw_columns": list(df_raw.columns),
        "crops_count": len(crops),
        "markets_count": len(markets),
        "states_count": len(states),
        "crops_sample": crops[:12],
        "states_sample": states,
        "date_range": (dates[0] if dates else "N/A", dates[-1] if dates else "N/A"),
        "price_units": "₹/quintal (1 quintal = 100 kg)",
        "coordinates_in_raw": False,
        "transport_rates_in_raw": False,
        "invalid_zero_price_rows": invalid_price_count,
        "missing_values_by_column": df_raw.isna().sum().to_dict()
    }
    return report


def load_normalized_marketplace_data() -> pd.DataFrame:
    """
    Normalizes dataset into internal schema:
    - Standardizes column names
    - Converts ₹/quintal to ₹/kg
    - Flags invalid / zero prices
    - Preserves raw values for traceability
    """
    csv_file = ensure_extracted()
    df = pd.read_csv(csv_file)
    
    # Clean whitespace
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
        
    # Map raw columns
    col_map = {
        'State': 'state',
        'District': 'district',
        'Market': 'market',
        'Commodity': 'commodity',
        'Variety': 'variety',
        'Grade': 'grade',
        'Arrival_Date': 'arrival_date',
        'Min_x0020_Price': 'min_price_quintal',
        'Max_x0020_Price': 'max_price_quintal',
        'Modal_x0020_Price': 'modal_price_quintal',
        'Min_Price': 'min_price_quintal',
        'Max_Price': 'max_price_quintal',
        'Modal_Price': 'modal_price_quintal'
    }
    
    df_clean = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    
    # Ensure numeric price columns
    for p_col in ['min_price_quintal', 'max_price_quintal', 'modal_price_quintal']:
        if p_col in df_clean.columns:
            df_clean[p_col] = pd.to_numeric(df_clean[p_col], errors='coerce').fillna(0.0)
            
    # Deterministic price conversion: Price per kg = Price per quintal / 100
    df_clean['min_price_kg'] = df_clean['min_price_quintal'] / 100.0
    df_clean['max_price_kg'] = df_clean['max_price_quintal'] / 100.0
    df_clean['modal_price_kg'] = df_clean['modal_price_quintal'] / 100.0
    
    # Flag valid records (Modal price > 0)
    df_clean['is_valid'] = (df_clean['modal_price_kg'] > 0) & (df_clean['min_price_kg'] <= df_clean['max_price_kg'])
    
    return df_clean


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    rep = inspect_marketplace_data()
    print("Marketplace Inspection Report:")
    for k, v in rep.items():
        print(f"  {k}: {v}")
    
    df_norm = load_normalized_marketplace_data()
    print(f"\nNormalized rows: {len(df_norm)}")
    print("Sample Normalized Row:\n", df_norm.iloc[0].to_dict())
