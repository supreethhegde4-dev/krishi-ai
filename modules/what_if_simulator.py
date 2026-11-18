"""
What-If Agricultural Simulation Engine
Allows farmers to simulate changes in rainfall, temperature, soil nutrients,
and acreage to evaluate how shifts in environmental and management factors
impact predicted harvest volume, gross revenue, and risk levels.
"""
from typing import Dict, Any
from modules.yield_analytics import predict_crop_yield
from modules.risk_analytics import evaluate_agricultural_risks


def run_what_if_simulation(
    crop_name: str,
    baseline_params: Dict[str, float],
    simulated_params: Dict[str, float],
    mandi_price_kg: float = 16.5
) -> Dict[str, Any]:
    """
    Runs dual-inference (Baseline vs Simulated) and computes delta comparisons.
    """
    # 1. BASELINE PREDICTIONS
    base_yield = predict_crop_yield(
        crop_name=crop_name,
        acreage=baseline_params.get("acreage", 2.5),
        soil_n=baseline_params.get("soil_n", 85.0),
        soil_p=baseline_params.get("soil_p", 55.0),
        soil_k=baseline_params.get("soil_k", 58.0),
        rainfall=baseline_params.get("rainfall", 82.0),
        ph=baseline_params.get("ph", 6.5)
    )

    base_risk = evaluate_agricultural_risks(
        crop=crop_name,
        temperature_c=baseline_params.get("temperature", 25.0),
        humidity_pct=baseline_params.get("humidity", 70.0),
        rainfall_mm=baseline_params.get("rainfall", 82.0),
        n_val=baseline_params.get("soil_n", 85.0),
        p_val=baseline_params.get("soil_p", 55.0),
        k_val=baseline_params.get("soil_k", 58.0),
        ph_val=baseline_params.get("ph", 6.5)
    )

    base_rev = base_yield["total_yield_kg"] * mandi_price_kg

    # 2. SIMULATED PREDICTIONS
    sim_yield = predict_crop_yield(
        crop_name=crop_name,
        acreage=simulated_params.get("acreage", baseline_params.get("acreage", 2.5)),
        soil_n=simulated_params.get("soil_n", baseline_params.get("soil_n", 85.0)),
        soil_p=simulated_params.get("soil_p", baseline_params.get("soil_p", 55.0)),
        soil_k=simulated_params.get("soil_k", baseline_params.get("soil_k", 58.0)),
        rainfall=simulated_params.get("rainfall", baseline_params.get("rainfall", 82.0)),
        ph=simulated_params.get("ph", baseline_params.get("ph", 6.5))
    )

    sim_risk = evaluate_agricultural_risks(
        crop=crop_name,
        temperature_c=simulated_params.get("temperature", baseline_params.get("temperature", 25.0)),
        humidity_pct=simulated_params.get("humidity", baseline_params.get("humidity", 70.0)),
        rainfall_mm=simulated_params.get("rainfall", baseline_params.get("rainfall", 82.0)),
        n_val=simulated_params.get("soil_n", baseline_params.get("soil_n", 85.0)),
        p_val=simulated_params.get("soil_p", baseline_params.get("soil_p", 55.0)),
        k_val=simulated_params.get("soil_k", baseline_params.get("soil_k", 58.0)),
        ph_val=simulated_params.get("ph", baseline_params.get("ph", 6.5))
    )

    sim_rev = sim_yield["total_yield_kg"] * mandi_price_kg

    # 3. DELTA COMPUTATION
    yield_delta_kg = round(sim_yield["total_yield_kg"] - base_yield["total_yield_kg"], 1)
    yield_delta_pct = round(((sim_yield["total_yield_kg"] - base_yield["total_yield_kg"]) / (base_yield["total_yield_kg"] if base_yield["total_yield_kg"] > 0 else 1.0)) * 100.0, 1)

    rev_delta = round(sim_rev - base_rev, 2)
    rev_delta_pct = round(((sim_rev - base_rev) / (base_rev if base_rev > 0 else 1.0)) * 100.0, 1)

    risk_delta_pts = round(sim_risk["composite_risk_score"] - base_risk["composite_risk_score"], 1)

    # 4. SENSITIVITY SUMMARY
    insights = []
    if simulated_params.get("rainfall") != baseline_params.get("rainfall"):
        r_diff = simulated_params.get("rainfall") - baseline_params.get("rainfall")
        insights.append(f"Rainfall shift ({r_diff:+.0f} mm): {'Improved canopy vigor' if r_diff > 0 else 'Induced slight water deficit'}")

    if simulated_params.get("soil_n") != baseline_params.get("soil_n"):
        n_diff = simulated_params.get("soil_n") - baseline_params.get("soil_n")
        insights.append(f"Nitrogen shift ({n_diff:+.0f} kg/ha): Directly altered vegetative biomass potential")

    if simulated_params.get("temperature") != baseline_params.get("temperature"):
        t_diff = simulated_params.get("temperature") - baseline_params.get("temperature")
        insights.append(f"Temperature change ({t_diff:+.1f}°C): Impacted metabolic rate & thermal stress index")

    return {
        "crop": crop_name,
        "mandi_price_kg": mandi_price_kg,
        "baseline": {
            "params": baseline_params,
            "yield_per_acre": base_yield["predicted_yield_per_acre"],
            "total_yield_kg": base_yield["total_yield_kg"],
            "total_yield_quintals": base_yield["total_yield_quintals"],
            "gross_revenue": base_rev,
            "risk_score": base_risk["composite_risk_score"],
            "risk_badge": base_risk["risk_badge"]
        },
        "simulated": {
            "params": simulated_params,
            "yield_per_acre": sim_yield["predicted_yield_per_acre"],
            "total_yield_kg": sim_yield["total_yield_kg"],
            "total_yield_quintals": sim_yield["total_yield_quintals"],
            "gross_revenue": sim_rev,
            "risk_score": sim_risk["composite_risk_score"],
            "risk_badge": sim_risk["risk_badge"]
        },
        "deltas": {
            "yield_kg": yield_delta_kg,
            "yield_pct": yield_delta_pct,
            "revenue": rev_delta,
            "revenue_pct": rev_delta_pct,
            "risk_score": risk_delta_pts,
            "risk_direction": "Decreased Risk (Safer)" if risk_delta_pts < 0 else ("Increased Risk" if risk_delta_pts > 0 else "Neutral")
        },
        "insights": insights
    }
