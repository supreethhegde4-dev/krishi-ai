"""
Soil Intelligence Engine for Krishi AI.
Analyzes macronutrient levels, pH balance, organic fertility, and computes Soil Health Index.
"""
from typing import Dict, Any, List


def evaluate_soil_health(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    ph: float,
    organic_carbon_pct: float = 0.55
) -> Dict[str, Any]:
    """
    Evaluates soil parameters against ICAR standard agricultural benchmarks.
    """
    # 1. Nitrogen Classification (kg/ha equivalent)
    if nitrogen < 40:
        n_status = "Deficient (Low)"
        n_score = 45.0
        n_color = "#c62828"
        n_advice = "Severe Nitrogen deficit. Apply well-decomposed FYM or split urea/neem-coated nitrogen."
    elif nitrogen <= 90:
        n_status = "Optimum (Moderate)"
        n_score = 90.0
        n_color = "#2e7d32"
        n_advice = "Nitrogen is in the ideal productive range for vegetative growth."
    else:
        n_status = "Excess (High)"
        n_score = 75.0
        n_color = "#f57c00"
        n_advice = "Excess nitrogen can cause succulent growth and increased pest vulnerability. Reduce synthetic N."

    # 2. Phosphorus Classification
    if phosphorus < 25:
        p_status = "Deficient (Low)"
        p_score = 45.0
        p_color = "#c62828"
        p_advice = "Low phosphorus limits root elongation. Apply Single Super Phosphate (SSP) or DAP as basal dose."
    elif phosphorus <= 65:
        p_status = "Optimum (Moderate)"
        p_score = 92.0
        p_color = "#2e7d32"
        p_advice = "Phosphorus level is well balanced for vigorous root development and early flowering."
    else:
        p_status = "High"
        p_score = 80.0
        p_color = "#1565c0"
        p_advice = "Ample phosphorus reserves. No heavy basal phosphate needed for next cycle."

    # 3. Potassium Classification
    if potassium < 25:
        k_status = "Deficient (Low)"
        k_score = 45.0
        k_color = "#c62828"
        k_advice = "Potassium deficiency impairs fruit sizing and disease resistance. Apply Muriate of Potash (MOP)."
    elif potassium <= 70:
        k_status = "Optimum (Moderate)"
        k_score = 95.0
        k_color = "#2e7d32"
        k_advice = "Potassium is optimal for osmotic regulation, pest resilience, and quality fruit firmness."
    else:
        k_status = "High"
        k_score = 85.0
        k_color = "#1565c0"
        k_advice = "High potassium promotes drought tolerance. Maintain standard maintenance doses."

    # 4. Soil pH Evaluation
    if ph < 5.8:
        ph_status = "Strongly Acidic"
        ph_score = 50.0
        ph_color = "#c62828"
        ph_advice = "Acidic soil causes aluminum toxicity and locks phosphorus. Apply agricultural lime (calcium carbonate) at 200 kg/acre."
    elif ph <= 7.4:
        ph_status = "Near-Neutral (Optimal)"
        ph_score = 95.0
        ph_color = "#2e7d32"
        ph_advice = "Optimal pH range. Maximum nutrient bioavailability for all major and micronutrients."
    elif ph <= 8.3:
        ph_status = "Moderately Alkaline"
        ph_score = 70.0
        ph_color = "#f57c00"
        ph_advice = "Alkaline tendency reduces zinc and iron availability. Incorporate gypsum and organic compost."
    else:
        ph_status = "Sodic / Highly Alkaline"
        ph_score = 40.0
        ph_color = "#c62828"
        ph_advice = "Sodic condition. Apply gypsum at 500 kg/acre followed by flushing and green manuring (dhaincha)."

    # 5. Organic Carbon Score
    oc_score = min(100.0, max(20.0, organic_carbon_pct * 140.0))

    # Overall Soil Health Index (0 - 100)
    health_index = round(0.25 * n_score + 0.25 * p_score + 0.25 * k_score + 0.15 * ph_score + 0.10 * oc_score, 1)

    if health_index >= 85:
        overall_condition = "Excellent Soil Fertility"
        health_color = "#2e7d32"
    elif health_index >= 68:
        overall_condition = "Good Agricultural Condition"
        health_color = "#1565c0"
    elif health_index >= 50:
        overall_condition = "Moderate – Requires Soil Amendments"
        health_color = "#f57c00"
    else:
        overall_condition = "Poor – Immediate Remediation Needed"
        health_color = "#c62828"

    return {
        "health_index": health_index,
        "overall_condition": overall_condition,
        "health_color": health_color,
        "nutrients": {
            "Nitrogen (N)": {"value": nitrogen, "unit": "kg/ha", "status": n_status, "color": n_color, "advice": n_advice},
            "Phosphorus (P)": {"value": phosphorus, "unit": "kg/ha", "status": p_status, "color": p_color, "advice": p_advice},
            "Potassium (K)": {"value": potassium, "unit": "kg/ha", "status": k_status, "color": k_color, "advice": k_advice},
            "Soil Reaction (pH)": {"value": ph, "unit": "pH", "status": ph_status, "color": ph_color, "advice": ph_advice},
            "Organic Carbon (OC)": {"value": organic_carbon_pct, "unit": "%", "status": "Adequate" if organic_carbon_pct >= 0.5 else "Low", "color": "#2e7d32" if organic_carbon_pct >= 0.5 else "#f57c00", "advice": "Add 2-3 tonnes Farm Yard Manure (FYM) per acre to sustain microbiological life."}
        }
    }
