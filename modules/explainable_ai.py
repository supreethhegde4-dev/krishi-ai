"""
Explainable AI (XAI) Module for Krishi AI
Leverages SHAP (SHapley Additive exPlanations) TreeExplainer to break down
why the machine learning model generated a specific prediction, which factors
acted as positive boosters versus negative bottlenecks, and suggested agronomic actions.
"""
import os
import joblib
import numpy as np
import pandas as pd
import shap
import plotly.graph_objects as go
from typing import Dict, Any, List

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
YIELD_MODEL_PATH = os.path.join(MODELS_DIR, "yield_prediction_model.pkl")


def explain_yield_prediction(
    crop_name: str,
    acreage: float,
    soil_n: float,
    soil_p: float,
    soil_k: float,
    rainfall: float,
    ph: float
) -> Dict[str, Any]:
    """
    Computes exact SHAP contribution values for a yield prediction.
    """
    crop_cap = crop_name.capitalize()
    
    if not os.path.exists(YIELD_MODEL_PATH):
        return {
            "crop": crop_cap,
            "base_value_quintal": 25.0,
            "predicted_yield_quintal": 25.0,
            "feature_impacts": [],
            "positive_factors": [],
            "negative_factors": [],
            "top_positive_driver": "Baseline Soil Average",
            "top_negative_driver": "None",
            "natural_explanations": [],
            "waterfall_fig": None
        }

    model_bundle = joblib.load(YIELD_MODEL_PATH)
    reg = model_bundle["model"]
    le = model_bundle["label_encoder"]
    feat_cols = model_bundle["features"]

    # Crop encoding
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

    predicted_val = float(reg.predict(input_df)[0])

    # SHAP TreeExplainer
    explainer = shap.TreeExplainer(reg)
    shap_values = explainer.shap_values(input_df)
    
    # Base value (expected value of model over training distribution)
    base_val = float(explainer.expected_value[0] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value)

    # Feature names mapping for farmer display
    display_names = {
        "crop_encoded": f"Crop Variety ({crop_cap})",
        "acreage": f"Cultivated Acreage ({acreage:.1f} acres)",
        "n_level": f"Soil Nitrogen ({soil_n:.0f} kg/ha)",
        "p_level": f"Soil Phosphorus ({soil_p:.0f} kg/ha)",
        "k_level": f"Soil Potassium ({soil_k:.0f} kg/ha)",
        "rainfall": f"Precipitation ({rainfall:.0f} mm)",
        "ph": f"Soil pH ({ph:.1f})"
    }

    feature_impacts = []
    vals = shap_values[0] if len(shap_values.shape) > 1 else shap_values

    for col, sv in zip(feat_cols, vals):
        sv_float = round(float(sv), 2)
        feature_impacts.append({
            "raw_feature": col,
            "feature_label": display_names.get(col, col),
            "shap_value": sv_float,
            "direction": "Positive Booster" if sv_float >= 0 else "Limiting Bottleneck",
            "abs_impact": abs(sv_float)
        })

    # Sort by absolute impact
    feature_impacts.sort(key=lambda x: x["abs_impact"], reverse=True)

    positive_factors = [f for f in feature_impacts if f["shap_value"] > 0]
    negative_factors = [f for f in feature_impacts if f["shap_value"] < 0]

    # Generate actionable explanations
    explanations = []
    for f in feature_impacts[:4]:
        raw = f["raw_feature"]
        sv = f["shap_value"]
        if raw == "n_level":
            if sv > 0:
                explanations.append(f"🟢 **Soil Nitrogen (+{sv:.1f} Q/acre):** Adequate vegetative nutrition is actively supporting yield accumulation.")
            else:
                explanations.append(f"🔴 **Soil Nitrogen ({sv:.1f} Q/acre):** Sub-optimal N levels are acting as a limiting bottleneck. Recommended: Top-dress Urea.")
        elif raw == "rainfall":
            if sv > 0:
                explanations.append(f"🟢 **Precipitation (+{sv:.1f} Q/acre):** Moisture levels are within favorable canopy growth range.")
            else:
                explanations.append(f"🔴 **Precipitation ({sv:.1f} Q/acre):** Moisture deficit constrained yield. Recommended: Increase supplementary drip irrigation.")
        elif raw == "ph":
            if sv > 0:
                explanations.append(f"🟢 **Soil pH (+{sv:.1f} Q/acre):** Balanced soil chemistry facilitates optimal macro and micro-nutrient absorption.")
            else:
                explanations.append(f"🔴 **Soil pH ({sv:.1f} Q/acre):** pH imbalance is limiting nutrient bioavailability. Recommended: Soil conditioning.")
        elif raw == "k_level":
            if sv > 0:
                explanations.append(f"🟢 **Potassium (+{sv:.1f} Q/acre):** High K promotes fruit firmness, water retention, and pest disease resistance.")
            else:
                explanations.append(f"🔴 **Potassium ({sv:.1f} Q/acre):** Low K reduces fruit size and disease tolerance. Recommended: Apply MOP (Muriate of Potash).")

    # Plotly Waterfall Chart
    fig = go.Figure(go.Waterfall(
        name="Yield Breakdown",
        orientation="v",
        measure=["relative"] * len(feature_impacts) + ["total"],
        x=[f["feature_label"].split("(")[0].strip() for f in feature_impacts] + ["Final Predicted Yield"],
        textposition="outside",
        text=[f"{f['shap_value']:+.1f}" for f in feature_impacts] + [f"{predicted_val:.1f} Q/ac"],
        y=[f["shap_value"] for f in feature_impacts] + [predicted_val],
        connector={"line": {"color": "#94A3B8"}},
        decreasing={"marker": {"color": "#EF4444"}},
        increasing={"marker": {"color": "#10B981"}},
        totals={"marker": {"color": "#0D5C3A"}}
    ))

    fig.update_layout(
        title="<b>SHAP Feature Contribution to Crop Yield (Quintals/Acre)</b>",
        showlegend=False,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(showgrid=False, title="Agronomic Parameters"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Impact on Yield (Q/acre)")
    )

    top_pos_driver = positive_factors[0]["feature_label"] if positive_factors else "Balanced Agronomy"
    top_neg_driver = negative_factors[0]["feature_label"] if negative_factors else "No Limiting Factors"

    return {
        "crop": crop_cap,
        "base_value_quintal": round(base_val, 1),
        "predicted_yield_quintal": round(predicted_val, 1),
        "feature_impacts": feature_impacts,
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "top_positive_driver": top_pos_driver,
        "top_negative_driver": top_neg_driver,
        "natural_explanations": explanations,
        "waterfall_fig": fig
    }
