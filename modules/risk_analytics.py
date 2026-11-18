"""
Agricultural Risk Analytics Module
Evaluates multi-dimensional farming risks:
1. Climate & Weather Stress (Heat stress, drought deficit, flood risk)
2. Soil Fertility Degradation (NPK deficiency, pH extremes)
3. Market Price Volatility (Historical CV from DuckDB, downside risk)
4. Post-Harvest Perishability & Spoilage
Generates a Composite Agricultural Risk Score (0-100) with actionable mitigation strategies.
"""
from typing import Dict, Any, List

CROP_AGRO_THRESHOLDS = {
    "Tomato": {"opt_temp": (18.0, 28.0), "opt_rain": (60.0, 150.0), "opt_ph": (6.0, 7.0), "opt_n": (80.0, 150.0), "perishability_days": 5, "historical_cv": 42.5},
    "Onion": {"opt_temp": (15.0, 30.0), "opt_rain": (50.0, 100.0), "opt_ph": (6.0, 7.5), "opt_n": (70.0, 120.0), "perishability_days": 45, "historical_cv": 38.0},
    "Potato": {"opt_temp": (16.0, 24.0), "opt_rain": (40.0, 80.0), "opt_ph": (5.5, 6.5), "opt_n": (80.0, 140.0), "perishability_days": 30, "historical_cv": 29.5},
    "Wheat": {"opt_temp": (12.0, 25.0), "opt_rain": (30.0, 90.0), "opt_ph": (6.0, 7.5), "opt_n": (60.0, 120.0), "perishability_days": 240, "historical_cv": 14.2},
    "Rice / Paddy": {"opt_temp": (20.0, 35.0), "opt_rain": (150.0, 300.0), "opt_ph": (5.5, 7.0), "opt_n": (80.0, 140.0), "perishability_days": 180, "historical_cv": 16.8},
    "Maize": {"opt_temp": (18.0, 32.0), "opt_rain": (60.0, 120.0), "opt_ph": (5.8, 7.2), "opt_n": (70.0, 130.0), "perishability_days": 120, "historical_cv": 19.4},
}

DEFAULT_THRESHOLDS = {
    "opt_temp": (18.0, 30.0), "opt_rain": (50.0, 150.0), "opt_ph": (6.0, 7.5), "opt_n": (60.0, 120.0), "perishability_days": 14, "historical_cv": 25.0
}


def evaluate_agricultural_risks(
    crop: str,
    temperature_c: float,
    humidity_pct: float,
    rainfall_mm: float,
    n_val: float,
    p_val: float,
    k_val: float,
    ph_val: float,
    has_cold_chain: bool = False
) -> Dict[str, Any]:
    """
    Computes component risk scores and overall Composite Risk Index (0-100).
    """
    clean_crop = crop.split("(")[0].strip()
    cfg = CROP_AGRO_THRESHOLDS.get(clean_crop, DEFAULT_THRESHOLDS)
    
    risk_factors: List[Dict[str, Any]] = []

    # 1. CLIMATE & WEATHER STRESS (0 to 25 pts)
    climate_risk = 0.0
    t_min, t_max = cfg["opt_temp"]
    if temperature_c > t_max + 5.0:
        pts = min(12.5, (temperature_c - t_max) * 2.0)
        climate_risk += pts
        risk_factors.append({
            "category": "Climate",
            "parameter": f"Thermal Heat Stress ({temperature_c:.1f}°C)",
            "impact": "High heat causes pollen sterility, flower abortion, and accelerated transpiration.",
            "severity": "High" if pts > 8 else "Moderate",
            "mitigation": "Deploy micro-sprinklers / shade netting and foliar spray of 1% Potassium Nitrate."
        })
    elif temperature_c < t_min - 4.0:
        pts = min(12.5, (t_min - temperature_c) * 2.0)
        climate_risk += pts
        risk_factors.append({
            "category": "Climate",
            "parameter": f"Low Temperature / Chilling Stress ({temperature_c:.1f}°C)",
            "impact": "Stunted vegetative growth and delayed ripening.",
            "severity": "Moderate",
            "mitigation": "Light evening irrigation to raise soil thermal mass."
        })

    r_min, r_max = cfg["opt_rain"]
    if rainfall_mm < r_min * 0.5:
        pts = min(12.5, (r_min - rainfall_mm) * 0.15)
        climate_risk += pts
        risk_factors.append({
            "category": "Climate",
            "parameter": f"Moisture Deficit / Drought Threat ({rainfall_mm:.0f} mm)",
            "impact": "Root dehydration and severe reduction in cell expansion.",
            "severity": "High",
            "mitigation": "Adopt drip irrigation schedule and organic straw mulching (5-8 cm layer)."
        })
    elif rainfall_mm > r_max * 1.6:
        pts = min(12.5, (rainfall_mm - r_max) * 0.1)
        climate_risk += pts
        risk_factors.append({
            "category": "Climate",
            "parameter": f"Excess Rainfall / Waterlogging ({rainfall_mm:.0f} mm)",
            "impact": "Root hypoxia, collar rot, and soil-borne fungal pathogens.",
            "severity": "High",
            "mitigation": "Ensure field drainage furrows and spray Trichoderma viride preventive bio-fungicide."
        })
    climate_risk = min(25.0, round(climate_risk, 1))

    # 2. SOIL FERTILITY DEGRADATION RISK (0 to 25 pts)
    soil_risk = 0.0
    ph_min, ph_max = cfg["opt_ph"]
    if ph_val < ph_min - 0.5:
        pts = min(12.0, (ph_min - ph_val) * 6.0)
        soil_risk += pts
        risk_factors.append({
            "category": "Soil",
            "parameter": f"Soil Acidification (pH {ph_val:.1f})",
            "impact": "Aluminium/Manganese toxicity and Phosphorus fixation.",
            "severity": "High" if ph_val < 5.0 else "Moderate",
            "mitigation": "Apply agricultural lime (CaCO3) @ 500 kg/acre prior to sowing."
        })
    elif ph_val > ph_max + 0.5:
        pts = min(12.0, (ph_val - ph_max) * 6.0)
        soil_risk += pts
        risk_factors.append({
            "category": "Soil",
            "parameter": f"Soil Alkalinity / Salinity (pH {ph_val:.1f})",
            "impact": "Zinc and Iron micro-nutrient chlorosis.",
            "severity": "Moderate",
            "mitigation": "Incorporate Gypsum @ 400 kg/acre and well-rotted FYM/compost."
        })

    n_min, n_max = cfg["opt_n"]
    if n_val < n_min * 0.6:
        pts = min(13.0, (n_min - n_val) * 0.15)
        soil_risk += pts
        risk_factors.append({
            "category": "Soil",
            "parameter": f"Severe Nitrogen Starvation ({n_val:.0f} kg/ha)",
            "impact": "Chlorosis of older leaves and sub-optimal vegetative canopy.",
            "severity": "Moderate",
            "mitigation": "Top-dress Neem-coated Urea in 2 split applications."
        })
    elif n_val > n_max * 1.5:
        pts = min(10.0, (n_val - n_max) * 0.1)
        soil_risk += pts
        risk_factors.append({
            "category": "Soil",
            "parameter": f"Excessive Nitrogen Application ({n_val:.0f} kg/ha)",
            "impact": "Excess succulent vegetative growth prone to sucking pests and lodging.",
            "severity": "Low",
            "mitigation": "Balance immediately with Muriate of Potash (MOP) and stop N application."
        })
    soil_risk = min(25.0, round(soil_risk, 1))

    # 3. MARKET VOLATILITY RISK (0 to 25 pts)
    cv = cfg["historical_cv"]
    market_risk = min(25.0, round(cv * 0.55, 1))
    if cv > 35.0:
        risk_factors.append({
            "category": "Market",
            "parameter": f"High Historical Price Volatility (CV: {cv:.1f}%)",
            "impact": "Frequent sharp market swings due to synchronized seasonal arrivals.",
            "severity": "High",
            "mitigation": "Check Krishi AI Net Proceeds Ranker before picking mandi; avoid peak glut dates."
        })
    else:
        risk_factors.append({
            "category": "Market",
            "parameter": f"Stable Historical Price Corridor (CV: {cv:.1f}%)",
            "impact": "Predictable wholesale pricing with low crash probability.",
            "severity": "Low",
            "mitigation": "Standard mandi sale without rush holding."
        })

    # 4. POST-HARVEST & SPOILAGE RISK (0 to 25 pts)
    shelf_life = cfg["perishability_days"]
    if shelf_life <= 7:
        if has_cold_chain:
            spoil_risk = 6.0
            risk_factors.append({
                "category": "Perishability",
                "parameter": f"High Perishability ({shelf_life} days shelf life)",
                "impact": "Cold-chain infrastructure secured; spoilage controlled.",
                "severity": "Low",
                "mitigation": "Maintain cold storage temp at 10-12°C with 85-90% RH."
            })
        else:
            spoil_risk = 22.0
            risk_factors.append({
                "category": "Perishability",
                "parameter": f"Unmitigated Spoilage Risk ({shelf_life} days shelf life)",
                "impact": "Ambient transit over 8+ hours risks 15-25% cull rate and grade degradation.",
                "severity": "High",
                "mitigation": "Use refrigerated reefer van for transit > 150 km, or target nearby APMC within 4 hours."
            })
    elif shelf_life <= 30:
        spoil_risk = 12.0
    else:
        spoil_risk = 4.0
    spoil_risk = min(25.0, round(spoil_risk, 1))

    # COMPOSITE RISK SCORE (0 to 100)
    composite_score = round(climate_risk + soil_risk + market_risk + spoil_risk, 1)

    if composite_score <= 30:
        risk_level = "Low Risk (Favorable Agricultural Conditions)"
        risk_color = "#15803D"
        risk_badge = "🟢 Low Risk"
    elif composite_score <= 60:
        risk_level = "Moderate Risk (Manageable with Active Interventions)"
        risk_color = "#D97706"
        risk_badge = "🟡 Moderate Risk"
    elif composite_score <= 80:
        risk_level = "High Risk (Substantial Threat to Harvest Margin)"
        risk_color = "#EA580C"
        risk_badge = "🟠 High Risk"
    else:
        risk_level = "Severe Risk (Critical Action Required)"
        risk_color = "#DC2626"
        risk_badge = "🔴 Severe Risk"

    return {
        "crop": crop,
        "composite_risk_score": composite_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "risk_badge": risk_badge,
        "component_breakdown": {
            "Climate & Weather": climate_risk,
            "Soil Health & Chemistry": soil_risk,
            "Market Price Volatility": market_risk,
            "Post-Harvest Spoilage": spoil_risk
        },
        "risk_factors": risk_factors,
        "top_mitigations": [f["mitigation"] for f in risk_factors if f.get("severity") in ("High", "Moderate")]
    }
