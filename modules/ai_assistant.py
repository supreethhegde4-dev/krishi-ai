"""
Gemini Agricultural AI Assistant for Krishi AI.
Provides:
1. Context-aware conversational agronomic, financial, and logistics advice
2. Privacy guard (sanitizes context; strips passwords, session tokens, and secrets)
3. Strict reliance on actual platform computations (zero hallucinated prices)
4. Offline deterministic expert rules engine when GEMINI_API_KEY is not configured
"""
import datetime
from typing import Dict, Any, List

from modules.api_clients import GeminiAgriClient


def build_farmer_system_context(
    user: Dict[str, Any],
    farm: Dict[str, Any],
    crop_name: str = "Tomato",
    benchmark_price_kg: float = 18.5,
    predicted_yield_qtl: float = 105.0,
    best_mandi_name: str = "K.R.Nagar APMC",
    best_mandi_net_proceeds: float = 11000.0,
    best_mandi_dist_km: float = 48.0,
    weather_summary: str = "24°C, 65% RH, Optimal Solar Radiation"
) -> Dict[str, Any]:
    """
    Constructs a sanitized context payload from session state.
    Guarantees no passwords, session tokens, or sensitive hashes are included.
    """
    return {
        "full_name": user.get("full_name", "Farmer"),
        "farm_name": farm.get("farm_name", "Farm Enterprise"),
        "acreage": farm.get("acreage", 2.5),
        "district": farm.get("district", "Ramanagara"),
        "state": farm.get("state", "Karnataka"),
        "primary_crop": crop_name,
        "soil_summary": f"Soil Type: {farm.get('soil_type', 'Red Loam')}",
        "benchmark_modal_price_kg": benchmark_price_kg,
        "predicted_yield_quintal": predicted_yield_qtl,
        "best_mandi_name": best_mandi_name,
        "best_mandi_net_proceeds": best_mandi_net_proceeds,
        "best_mandi_distance_km": best_mandi_dist_km,
        "weather_summary": weather_summary
    }


def query_agricultural_assistant(
    prompt: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Routes farmer query to Gemini 2.5 Flash if configured,
    or falls back to the deterministic agricultural reasoning engine.
    """
    return GeminiAgriClient.ask_agricultural_assistant(
        user_question=prompt,
        farmer_context=context
    )
