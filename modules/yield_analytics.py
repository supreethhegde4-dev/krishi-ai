"""
Yield Analytics Engine for Krishi AI.
Uses trained Random Forest model to forecast harvest yield per acre and total volume,
computes yield gap analysis against state benchmarks, and projects gross farmgate value.
"""
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
YIELD_MODEL_PATH = os.path.join(MODELS_DIR, "yield_prediction_model.pkl")


def load_yield_model():
    if os.path.exists(YIELD_MODEL_PATH):
        return joblib.load(YIELD_MODEL_PATH)
    return None


BENCHMARK_YIELDS_QUINTAL_PER_ACRE = {
    "Tomato": {"district_avg": 95.0, "state_avg": 110.0, "high_performing": 150.0},
    "Rice": {"district_avg": 18.0, "state_avg": 21.0, "high_performing": 28.0},
    "Maize": {"district_avg": 22.0, "state_avg": 26.0, "high_performing": 34.0},
    "Banana": {"district_avg": 140.0, "state_avg": 165.0, "high_performing": 210.0},
    "Cotton": {"district_avg": 9.0, "state_avg": 11.5, "high_performing": 16.0},
    "Potato": {"district_avg": 85.0, "state_avg": 105.0, "high_performing": 140.0},
    "Chickpea": {"district_avg": 7.5, "state_avg": 9.0, "high_performing": 13.0},
    "Wheat": {"district_avg": 16.0, "state_avg": 19.5, "high_performing": 25.0},
    "Coffee": {"district_avg": 6.5, "state_avg": 8.0, "high_performing": 11.0}
}


def predict_crop_yield(
    crop_name: str,
    acreage: float,
    soil_n: float,
    soil_p: float,
    soil_k: float,
    rainfall: float,
    ph: float
) -> Dict[str, Any]:
    """
    Predicts yield in quintals/acre and total farm volume.
    """
    crop_cap = crop_name.capitalize()
    model_bundle = load_yield_model()

    if model_bundle:
        try:
            reg = model_bundle["model"]
            le = model_bundle["label_encoder"]
            feat_cols = model_bundle["features"]

            # Encode crop (or fallback to Tomato if unknown)
            if crop_cap in le.classes_:
                c_enc = le.transform([crop_cap])[0]
            else:
                c_enc = le.transform(["Tomato"])[0]

            input_df = pd.DataFrame([{
                "crop_encoded": c_enc,
                "acreage": acreage,
                "n_level": soil_n,
                "p_level": soil_p,
                "k_level": soil_k,
                "rainfall": rainfall,
                "ph": ph
            }])[feat_cols]

            pred_yield_per_acre = float(reg.predict(input_df)[0])
        except Exception:
            bench = BENCHMARK_YIELDS_QUINTAL_PER_ACRE.get(crop_cap, {"state_avg": 100.0})
            pred_yield_per_acre = bench["state_avg"]
    else:
        bench = BENCHMARK_YIELDS_QUINTAL_PER_ACRE.get(crop_cap, {"state_avg": 100.0})
        pred_yield_per_acre = bench["state_avg"]

    pred_yield_per_acre = round(max(5.0, pred_yield_per_acre), 1)
    total_yield_quintals = round(pred_yield_per_acre * acreage, 1)
    total_yield_kg = round(total_yield_quintals * 100.0, 0)

    # Benchmark comparisons
    benchmarks = BENCHMARK_YIELDS_QUINTAL_PER_ACRE.get(
        crop_cap,
        {"district_avg": pred_yield_per_acre * 0.85, "state_avg": pred_yield_per_acre, "high_performing": pred_yield_per_acre * 1.3}
    )

    state_avg = benchmarks["state_avg"]
    yield_gap_pct = round(((pred_yield_per_acre - state_avg) / state_avg) * 100.0, 1)

    return {
        "crop": crop_cap,
        "acreage": acreage,
        "predicted_yield_per_acre": pred_yield_per_acre,
        "total_yield_quintals": total_yield_quintals,
        "total_yield_kg": total_yield_kg,
        "district_avg_yield": benchmarks["district_avg"],
        "state_avg_yield": benchmarks["state_avg"],
        "high_performing_yield": benchmarks["high_performing"],
        "yield_gap_pct": yield_gap_pct,
        "performance_rating": "Superior / Above State Average" if yield_gap_pct >= 5 else ("On-Par with Regional Average" if yield_gap_pct >= -10 else "Sub-Optimal (Yield Gap Exists)")
    }
