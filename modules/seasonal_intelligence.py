"""
Seasonal Agricultural Intelligence Module
Evaluates seasonal cultivation windows, historical seasonal price variations,
and regional crop performance patterns for Indian agriculture.
"""
import datetime
from typing import Dict, Any, List

# Indian Agro-Climatic Seasonal Crop Calendar
CROP_SEASONAL_CALENDAR: Dict[str, Dict[str, Any]] = {
    "Tomato": {
        "seasons": ["Kharif", "Rabi", "Summer"],
        "primary_season": "Rabi",
        "sowing_months": ["June-July", "October-November", "January-February"],
        "harvesting_months": ["September-October", "January-March", "April-May"],
        "favorable_temp_c": (18.0, 28.0),
        "favorable_rainfall_mm": (60.0, 150.0),
        "peak_price_window": "June to August (Monsoon Supply Gap)",
        "low_price_window": "January to February (Winter Peak Glut)",
        "production_hubs": ["Kolar (KA)", "Ramanagara (KA)", "Madanapalle (AP)", "Nashik (MH)"],
        "agro_notes": "Night temperatures below 13°C cause poor fruit set; monsoon rains cause fruit cracking and fungal blight."
    },
    "Onion": {
        "seasons": ["Kharif", "Late Kharif", "Rabi"],
        "primary_season": "Rabi (65% of national output)",
        "sowing_months": ["June-July", "September-October", "November-December"],
        "harvesting_months": ["October-November", "January-February", "March-May"],
        "favorable_temp_c": (15.0, 30.0),
        "favorable_rainfall_mm": (65.0, 100.0),
        "peak_price_window": "October to December (Post-Monsoon Exhaustion)",
        "low_price_window": "March to May (Rabi Harvest Glut)",
        "production_hubs": ["Nashik (MH)", "Lasalgaon (MH)", "Ahmednagar (MH)", "Bagalkot (KA)"],
        "agro_notes": "Rabi onions have high dry matter and 4-6 months storage life; Kharif onions have high moisture and spoil within 3-4 weeks."
    },
    "Potato": {
        "seasons": ["Rabi"],
        "primary_season": "Rabi",
        "sowing_months": ["October-November"],
        "harvesting_months": ["January-March"],
        "favorable_temp_c": (16.0, 24.0),
        "favorable_rainfall_mm": (40.0, 80.0),
        "peak_price_window": "October to November (Cold Store Depletion)",
        "low_price_window": "February to April (Main Harvest)",
        "production_hubs": ["Agra (UP)", "Jalandhar (PB)", "Hooghly (WB)", "Hassan (KA)"],
        "agro_notes": "Tuberization completely halts above 30°C soil temperature; requires cold-chain infrastructure for multi-month holding."
    },
    "Wheat": {
        "seasons": ["Rabi"],
        "primary_season": "Rabi",
        "sowing_months": ["November-December"],
        "harvesting_months": ["March-May"],
        "favorable_temp_c": (12.0, 25.0),
        "favorable_rainfall_mm": (30.0, 100.0),
        "peak_price_window": "December to February (Pre-Harvest Lean Period)",
        "low_price_window": "April to May (Peak Mandi Arrivals)",
        "production_hubs": ["Karnal (HR)", "Ludhiana (PB)", "Sehore (MP)", "Meerut (UP)"],
        "agro_notes": "Terminal heat waves during grain filling in March can reduce kernel weight by 15-20%."
    },
    "Rice / Paddy": {
        "seasons": ["Kharif", "Rabi / Boro"],
        "primary_season": "Kharif",
        "sowing_months": ["June-July", "November-December"],
        "harvesting_months": ["October-December", "April-May"],
        "favorable_temp_c": (20.0, 35.0),
        "favorable_rainfall_mm": (150.0, 300.0),
        "peak_price_window": "August to October (Pre-Kharif Harvest)",
        "low_price_window": "November to January (Paddy Procurement Peak)",
        "production_hubs": ["Thanjavur (TN)", "East Godavari (AP)", "Burdwan (WB)", "Gurdaspur (PB)"],
        "agro_notes": "Requires standing water during tillering and panicle initiation; highly vulnerable to blast and brown planthopper."
    },
    "Maize": {
        "seasons": ["Kharif", "Rabi"],
        "primary_season": "Kharif",
        "sowing_months": ["June-July", "October-November"],
        "harvesting_months": ["September-October", "February-March"],
        "favorable_temp_c": (18.0, 32.0),
        "favorable_rainfall_mm": (60.0, 120.0),
        "peak_price_window": "July to August",
        "low_price_window": "October to November",
        "production_hubs": ["Davanagere (KA)", "Chhindwara (MP)", "Gulbarga (KA)", "Karimnagar (TS)"],
        "agro_notes": "Susceptible to waterlogging during first 30 days of seedling emergence; fall armyworm monitoring essential."
    }
}

DEFAULT_CROP_SEASON = {
    "seasons": ["Kharif", "Rabi"],
    "primary_season": "Kharif",
    "sowing_months": ["June-July", "October-November"],
    "harvesting_months": ["October-November", "March-April"],
    "favorable_temp_c": (20.0, 30.0),
    "favorable_rainfall_mm": (50.0, 150.0),
    "peak_price_window": "Pre-harvest lean window (Month before major arrivals)",
    "low_price_window": "Harvest month peak arrival glut",
    "production_hubs": ["Major APMC Market Hubs"],
    "agro_notes": "Match sowing cycle with local monsoon onset and regional frost/heat thresholds."
}


def get_seasonal_crop_intelligence(crop_name: str) -> Dict[str, Any]:
    """Retrieves agro-climatic seasonal intelligence for a crop."""
    # Match crop name
    clean_name = crop_name.split("(")[0].strip()
    profile = CROP_SEASONAL_CALENDAR.get(clean_name, DEFAULT_CROP_SEASON)
    
    current_month_num = datetime.date.today().month
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    cur_month_str = month_names[current_month_num - 1]

    # Evaluate current agricultural calendar stage
    is_sowing_now = any(cur_month_str in m for m in profile["sowing_months"])
    is_harvest_now = any(cur_month_str in m for m in profile["harvesting_months"])
    
    if is_sowing_now:
        current_stage = "Optimal Sowing Window (Favorable Sowing & Soil Prep)"
        stage_badge = "🌱 Sowing Stage"
    elif is_harvest_now:
        current_stage = "Active Harvest Cycle (Prepare Storage & Mandi Logistics)"
        stage_badge = "🌾 Harvest Stage"
    else:
        current_stage = "Vegetative / Intercultural Management Phase"
        stage_badge = "🌿 Growth Stage"

    return {
        "crop": crop_name,
        "clean_name": clean_name,
        "current_month": cur_month_str,
        "current_stage": current_stage,
        "stage_badge": stage_badge,
        "primary_season": profile["primary_season"],
        "all_seasons": profile["seasons"],
        "sowing_windows": profile["sowing_months"],
        "harvest_windows": profile["harvesting_months"],
        "favorable_temp_c": profile["favorable_temp_c"],
        "favorable_rainfall_mm": profile["favorable_rainfall_mm"],
        "peak_price_window": profile["peak_price_window"],
        "low_price_window": profile["low_price_window"],
        "production_hubs": profile["production_hubs"],
        "agronomic_advisory": profile["agro_notes"]
    }
