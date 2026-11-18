"""
Machine Learning Price Forecasting Model for KisanAI.
Uses RandomForestRegressor with chronological time-series lag features,
strict temporal train/test split, recursive multi-step forecasting, and baseline comparison.
"""
import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_smape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculates Symmetric Mean Absolute Percentage Error (sMAPE)."""
    denominator = (np.abs(actual) + np.abs(predicted)) / 2.0
    diff = np.abs(predicted - actual) / np.where(denominator == 0, 1e-6, denominator)
    return float(np.mean(diff) * 100.0)


def create_time_series_features(df_series: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs chronological time-series lag and rolling features.
    Expects df_series sorted by date with 'modal_price_kg'.
    """
    df = df_series.copy()
    if 'date' not in df.columns:
        df['date'] = pd.to_datetime(df['Arrival_Date'])
    df = df.sort_values('date').reset_index(drop=True)

    # Calendar & Cyclical features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    df['day_of_year'] = df['date'].dt.dayofyear
    
    # Cyclical seasonal transformation
    df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12.0)
    df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12.0)

    # Lags (using observation indices)
    df['lag_1'] = df['modal_price_kg'].shift(1)
    df['lag_7'] = df['modal_price_kg'].shift(7)
    df['lag_14'] = df['modal_price_kg'].shift(14)
    df['lag_30'] = df['modal_price_kg'].shift(30)

    # Rolling averages
    df['rolling_7'] = df['modal_price_kg'].shift(1).rolling(window=7, min_periods=3).mean()
    df['rolling_30'] = df['modal_price_kg'].shift(1).rolling(window=30, min_periods=7).mean()

    # Fallback backfills for initial lag gaps
    df['lag_1'] = df['lag_1'].bfill()
    df['lag_7'] = df['lag_7'].fillna(df['lag_1'])
    df['lag_14'] = df['lag_14'].fillna(df['lag_7'])
    df['lag_30'] = df['lag_30'].fillna(df['lag_14'])
    df['rolling_7'] = df['rolling_7'].fillna(df['lag_1'])
    df['rolling_30'] = df['rolling_30'].fillna(df['rolling_7'])

    return df


FEATURE_COLS = [
    'lag_1', 'lag_7', 'lag_14', 'lag_30',
    'rolling_7', 'rolling_30',
    'day_of_week', 'month', 'week_of_year',
    'sin_month', 'cos_month'
]


def train_and_forecast_price(
    df_raw: pd.DataFrame,
    horizons: List[int] = [3, 7, 14],
    test_ratio: float = 0.15
) -> Dict[str, Any]:
    """
    Trains a RandomForest model on chronological train split,
    validates on out-of-time test split, and generates future predictions.
    """
    if len(df_raw) < 20:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": f"Only {len(df_raw)} historical observations available. Minimum 20 records required for reliable forecast.",
            "predictions": {},
            "metrics": {},
            "forecast_series": None
        }

    # Aggregate by date if multiple entries per day
    df_daily = df_raw.groupby('Arrival_Date', as_index=False).agg({
        'modal_price_kg': 'mean',
        'min_price_kg': 'min',
        'max_price_kg': 'max'
    })
    df_daily['date'] = pd.to_datetime(df_daily['Arrival_Date'])
    df_daily = df_daily.sort_values('date').reset_index(drop=True)

    df_feat = create_time_series_features(df_daily)

    # Chronological Train/Test Split (No future data leakage!)
    total_len = len(df_feat)
    split_idx = max(int(total_len * (1 - test_ratio)), total_len - 30)
    split_idx = min(split_idx, total_len - 10)

    train_df = df_feat.iloc[:split_idx].copy()
    test_df = df_feat.iloc[split_idx:].copy()

    X_train = train_df[FEATURE_COLS]
    y_train = train_df['modal_price_kg']
    X_test = test_df[FEATURE_COLS]
    y_test = test_df['modal_price_kg']

    # Train Random Forest Regressor
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)

    # Evaluate on hold-out test set
    y_pred_test = rf.predict(X_test)
    residuals = y_test.values - y_pred_test
    residual_std = float(np.std(residuals)) if len(residuals) > 0 else 1.5

    mae = float(mean_absolute_error(y_test, y_pred_test))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
    smape = calculate_smape(y_test.values, y_pred_test)

    # Baseline comparison (Lag-1 persistence baseline)
    y_baseline = test_df['lag_1'].values
    baseline_mae = float(mean_absolute_error(y_test, y_baseline))
    baseline_rmse = float(np.sqrt(mean_squared_error(y_test, y_baseline)))

    # Fit final model on full historical dataset
    rf_full = RandomForestRegressor(
        n_estimators=120,
        max_depth=8,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
    rf_full.fit(df_feat[FEATURE_COLS], df_feat['modal_price_kg'])

    # Multi-step Recursive Forecasting for up to max horizon
    max_h = max(horizons)
    future_dates = []
    future_preds = []
    future_upper = []
    future_lower = []

    last_date = df_daily['date'].max()
    curr_series = list(df_feat['modal_price_kg'].values)

    for step in range(1, max_h + 1):
        step_date = last_date + pd.Timedelta(days=step)
        
        # Build features for this future step
        lag_1_val = curr_series[-1]
        lag_7_val = curr_series[-7] if len(curr_series) >= 7 else lag_1_val
        lag_14_val = curr_series[-14] if len(curr_series) >= 14 else lag_7_val
        lag_30_val = curr_series[-30] if len(curr_series) >= 30 else lag_14_val
        roll_7_val = float(np.mean(curr_series[-7:]))
        roll_30_val = float(np.mean(curr_series[-30:])) if len(curr_series) >= 30 else roll_7_val

        m = step_date.month
        feat_vector = pd.DataFrame([{
            'lag_1': lag_1_val,
            'lag_7': lag_7_val,
            'lag_14': lag_14_val,
            'lag_30': lag_30_val,
            'rolling_7': roll_7_val,
            'rolling_30': roll_30_val,
            'day_of_week': step_date.dayofweek,
            'month': m,
            'week_of_year': int(step_date.isocalendar().week),
            'sin_month': np.sin(2 * np.pi * m / 12.0),
            'cos_month': np.cos(2 * np.pi * m / 12.0)
        }])

        pred_val = float(rf_full.predict(feat_vector[FEATURE_COLS])[0])
        # Uncertainty band expands with horizon
        horizon_uncertainty = residual_std * np.sqrt(1 + 0.12 * step)
        
        curr_series.append(pred_val)
        future_dates.append(step_date.strftime('%Y-%m-%d'))
        future_preds.append(round(pred_val, 2))
        future_upper.append(round(pred_val + 1.64 * horizon_uncertainty, 2))
        future_lower.append(round(max(1.0, pred_val - 1.64 * horizon_uncertainty), 2))

    # Compile predictions at specific horizons
    preds_dict = {}
    for h in horizons:
        if h <= len(future_preds):
            idx = h - 1
            preds_dict[f"{h}_day"] = {
                "horizon_days": h,
                "target_date": future_dates[idx],
                "predicted_price_kg": future_preds[idx],
                "confidence_lower_kg": future_lower[idx],
                "confidence_upper_kg": future_upper[idx]
            }

    forecast_df = pd.DataFrame({
        "Arrival_Date": future_dates,
        "predicted_modal_price_kg": future_preds,
        "confidence_upper_kg": future_upper,
        "confidence_lower_kg": future_lower
    })

    return {
        "status": "SUCCESS",
        "model_version": "krishi-forecast-v1.2.0-rf-timeseries",
        "prediction_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "disclaimer": "Agricultural price forecasts represent statistical time-series projections based on historical APMC arrivals and do not constitute a financial guarantee of future realization.",
        "observations_count": len(df_raw),
        "latest_observed_date": last_date.strftime('%Y-%m-%d'),
        "latest_observed_price": round(float(df_daily['modal_price_kg'].iloc[-1]), 2),
        "predictions": preds_dict,
        "forecast_series": forecast_df,
        "metrics": {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "smape": round(smape, 2),
            "baseline_mae": round(baseline_mae, 2),
            "baseline_rmse": round(baseline_rmse, 2),
            "residual_std": round(residual_std, 2),
            "outperformed_baseline": mae <= baseline_mae
        }
    }
