"""
Fertilizer Advisor Engine for Krishi AI.
Calculates crop-specific NPK nutrient requirements vs soil deficit,
recommends standard commercial Indian fertilizers (Urea, DAP, MOP, SSP),
computes 50kg bag dosage per acre, and provides agronomic split schedules.
"""
from typing import Dict, Any, List

# Recommended N-P-K nutrient intake benchmarks in kg/acre for prominent Indian crops
CROP_NUTRIENT_DEMAND_PER_ACRE = {
    "Tomato": {"N": 50.0, "P": 30.0, "K": 40.0, "duration_days": 110},
    "Rice": {"N": 40.0, "P": 20.0, "K": 20.0, "duration_days": 120},
    "Maize": {"N": 45.0, "P": 25.0, "K": 20.0, "duration_days": 100},
    "Banana": {"N": 80.0, "P": 35.0, "K": 90.0, "duration_days": 330},
    "Cotton": {"N": 45.0, "P": 20.0, "K": 20.0, "duration_days": 160},
    "Chickpea": {"N": 10.0, "P": 25.0, "K": 15.0, "duration_days": 95},
    "Potato": {"N": 60.0, "P": 40.0, "K": 50.0, "duration_days": 90},
    "Wheat": {"N": 45.0, "P": 20.0, "K": 15.0, "duration_days": 125},
    "Coffee": {"N": 40.0, "P": 30.0, "K": 40.0, "duration_days": 365}
}


def calculate_fertilizer_prescription(
    crop_name: str,
    soil_n: float,
    soil_p: float,
    soil_k: float,
    acreage: float = 1.0
) -> Dict[str, Any]:
    """
    Computes precise fertilizer dosage and application stages based on soil test values.
    """
    base_crop = crop_name.capitalize()
    demand = CROP_NUTRIENT_DEMAND_PER_ACRE.get(base_crop, {"N": 45.0, "P": 25.0, "K": 25.0, "duration_days": 100})

    # Net nutrient deficit per acre considering soil reserves
    # (assuming ~35% of soil test value is immediately bio-available in active root zone)
    n_needed = max(10.0, demand["N"] - (soil_n * 0.25))
    p_needed = max(5.0, demand["P"] - (soil_p * 0.25))
    k_needed = max(5.0, demand["K"] - (soil_k * 0.25))

    # Total nutrient needed for farm acreage
    total_n = n_needed * acreage
    total_p = p_needed * acreage
    total_k = k_needed * acreage

    # Commercial Fertilizer Conversion
    # 1. DAP (18% N, 46% P2O5) supplies P and partial N
    dap_kg = (total_p / 0.46)
    n_from_dap = dap_kg * 0.18
    
    # 2. Urea (46% N) supplies remaining N
    remaining_n = max(0.0, total_n - n_from_dap)
    urea_kg = (remaining_n / 0.46)
    
    # 3. MOP - Muriate of Potash (60% K2O) supplies K
    mop_kg = (total_k / 0.60)

    # 50 kg Bag equivalents
    dap_bags = round(dap_kg / 50.0, 1)
    urea_bags = round(urea_kg / 50.0, 1)
    mop_bags = round(mop_kg / 50.0, 1)

    # Application Split Schedule
    splits = [
        {
            "stage": "Basal Dressing (At Transplanting / Sowing)",
            "timing": "Day 0",
            "dap_kg": round(dap_kg, 1),
            "urea_kg": round(urea_kg * 0.25, 1),
            "mop_kg": round(mop_kg * 0.50, 1),
            "method": "Band placement 5 cm beside and below root zone. Mix well with organic compost."
        },
        {
            "stage": "First Top Dressing (Vegetative Growth)",
            "timing": "25 - 30 Days After Planting",
            "dap_kg": 0.0,
            "urea_kg": round(urea_kg * 0.40, 1),
            "mop_kg": 0.0,
            "method": "Side dressing in ring pattern followed by light irrigation. Incorporate into moist soil."
        },
        {
            "stage": "Second Top Dressing (Flowering & Fruit Setting)",
            "timing": "50 - 60 Days After Planting",
            "dap_kg": 0.0,
            "urea_kg": round(urea_kg * 0.35, 1),
            "mop_kg": round(mop_kg * 0.50, 1),
            "method": "Broadcasting between rows prior to fertigation or post-weeding hoeing."
        }
    ]

    return {
        "crop": base_crop,
        "acreage": acreage,
        "nutrient_demands_kg": {
            "N": round(total_n, 1),
            "P": round(total_p, 1),
            "K": round(total_k, 1)
        },
        "fertilizers": [
            {
                "name": "DAP (Diammonium Phosphate 18:46:0)",
                "total_kg": round(dap_kg, 1),
                "bags_50kg": dap_bags,
                "purpose": "Primary source of Phosphorus for deep root establishment and initial Nitrogen boost."
            },
            {
                "name": "Urea (Neem Coated 46:0:0)",
                "total_kg": round(urea_kg, 1),
                "bags_50kg": urea_bags,
                "purpose": "Essential for chlorophyll synthesis, foliage canopy, and vegetative branching."
            },
            {
                "name": "MOP (Muriate of Potash 0:0:60)",
                "total_kg": round(mop_kg, 1),
                "bags_50kg": mop_bags,
                "purpose": "Maximizes fruit sizing, shelf life firmness, disease immunity, and drought tolerance."
            }
        ],
        "schedule": splits,
        "organic_tip": "Apply 3 - 5 tonnes of well-composted Farm Yard Manure (FYM) or 1 tonne vermicompost per acre during final land preparation to improve fertilizer absorption efficiency by 25%."
    }
