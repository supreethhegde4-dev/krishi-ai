"""
Transportation Engine for KisanAI.
Complies with Phase 4 (Normal & Cold-chain specifications) and Phase 5 (Deterministic formulas).
"""
import math
from typing import Dict, Any, List


# Editable Default Prototype Transportation Configurations
DEFAULT_VEHICLE_CONFIGS = {
    "Mini Truck (Normal)": {
        "type": "NORMAL",
        "name": "Mini Truck (Tata Ace / Bolero)",
        "capacity_kg": 1000,
        "rate_per_km": 22.0,
        "base_charge": 500.0,
        "min_fare": 800.0,
        "loading_unloading_fee": 400.0,
        "toll_other_charges": 150.0,
        "temperature_range": "Ambient",
        "suitable_temp_min": 18,
        "suitable_temp_max": 40,
        "available": True,
        "loading_time_mins": 30,
        "unloading_time_mins": 30
    },
    "Goods Truck (Normal)": {
        "type": "NORMAL",
        "name": "Standard Goods Truck (7.5 Ton)",
        "capacity_kg": 6000,
        "rate_per_km": 36.0,
        "base_charge": 1500.0,
        "min_fare": 2500.0,
        "loading_unloading_fee": 1000.0,
        "toll_other_charges": 400.0,
        "temperature_range": "Ambient",
        "suitable_temp_min": 18,
        "suitable_temp_max": 40,
        "available": True,
        "loading_time_mins": 60,
        "unloading_time_mins": 60
    },
    "Reefer Mini Truck (Cold-Chain)": {
        "type": "REFRIGERATED",
        "name": "Refrigerated Mini Truck (Chilled)",
        "capacity_kg": 1200,
        "rate_per_km": 38.0,
        "base_charge": 1200.0,
        "min_fare": 1800.0,
        "loading_unloading_fee": 600.0,
        "toll_other_charges": 200.0,
        "temperature_range": "10°C to 15°C (Chilled Produce)",
        "suitable_temp_min": 10,
        "suitable_temp_max": 15,
        "available": True,
        "loading_time_mins": 35,
        "unloading_time_mins": 35
    },
    "Reefer Heavy Truck (Cold-Chain)": {
        "type": "REFRIGERATED",
        "name": "Refrigerated Container Truck (Deep Chill)",
        "capacity_kg": 6000,
        "rate_per_km": 55.0,
        "base_charge": 2800.0,
        "min_fare": 4500.0,
        "loading_unloading_fee": 1400.0,
        "toll_other_charges": 500.0,
        "temperature_range": "2°C to 12°C (Multi-temp Reefer)",
        "suitable_temp_min": 2,
        "suitable_temp_max": 12,
        "available": True,
        "loading_time_mins": 75,
        "unloading_time_mins": 75
    }
}


def check_temperature_suitability(crop_name: str, vehicle_config: Dict[str, Any], travel_hours: float) -> Dict[str, Any]:
    """
    Evaluates cold-chain suitability based on crop perishability and travel duration.
    """
    is_perishable = crop_name.lower() in [
        "tomato", "banana", "mango", "capsicum", "coriander(leaves)", 
        "green chilli", "cucumbar(kheera)", "bhindi(ladies finger)", "apple", "grape"
    ]
    
    is_reefer = vehicle_config.get("type") == "REFRIGERATED"
    
    if not is_perishable:
        return {
            "suitable": True,
            "badge": "Suitable",
            "message": f"{crop_name} is durable. Normal transport is completely cost-effective.",
            "recommendation": "Normal Transport Recommended"
        }
        
    # Crop is perishable
    if is_reefer:
        return {
            "suitable": True,
            "badge": "Cold-Chain Protected",
            "message": f"Refrigerated environment preserves {crop_name} firmness and eliminates heat spoilage.",
            "recommendation": "Cold-Chain Highly Recommended" if travel_hours > 2.5 else "Cold-Chain Optional"
        }
    else:
        if travel_hours > 3.0:
            return {
                "suitable": False,
                "badge": "High Spoilage Risk",
                "message": f"Normal transport for >{travel_hours:.1f} hrs in ambient temperature risks significant decay & weight loss.",
                "recommendation": "Consider Refrigerated Transport"
            }
        else:
            return {
                "suitable": True,
                "badge": "Acceptable for Short Haul",
                "message": f"Short distance transit ({travel_hours:.1f} hrs) is manageable with normal covered vehicle.",
                "recommendation": "Normal Transport Acceptable"
            }


def calculate_transport_cost(
    quantity_kg: float,
    road_distance_km: float,
    driving_duration_sec: float,
    vehicle_config: Dict[str, Any],
    round_trip_multiplier: float = 1.0,
    handling_buffer_mins: float = 20.0
) -> Dict[str, Any]:
    """
    Deterministic transportation calculation complying strictly with Phase 5:
    - Trips = Ceiling(Quantity kg / Vehicle Capacity kg)
    - Cost per trip = Base charge + (Distance × Rate/km × Multiplier) + Additional charges
    - Total cost = Trips × Cost per trip
    - Delivery time = Driving duration + Loading + Unloading + Buffer
    """
    capacity = float(vehicle_config.get("capacity_kg", 1000))
    rate_km = float(vehicle_config.get("rate_per_km", 22.0))
    base_charge = float(vehicle_config.get("base_charge", 500.0))
    min_fare = float(vehicle_config.get("min_fare", 800.0))
    loading_unloading = float(vehicle_config.get("loading_unloading_fee", 400.0))
    additional_tolls = float(vehicle_config.get("toll_other_charges", 150.0))
    
    # 1. Number of trips
    trips = math.ceil(quantity_kg / capacity) if capacity > 0 else 1
    trips = max(1, trips)
    
    # 2. Cost per trip
    distance_charge = road_distance_km * rate_km * round_trip_multiplier
    subtotal_trip = base_charge + distance_charge + loading_unloading + additional_tolls
    cost_per_trip = max(min_fare, subtotal_trip)
    
    # 3. Total transportation cost
    total_transport_cost = trips * cost_per_trip
    cost_per_kg = total_transport_cost / quantity_kg if quantity_kg > 0 else 0.0
    
    # 4. Delivery time calculation
    loading_mins = float(vehicle_config.get("loading_time_mins", 30))
    unloading_mins = float(vehicle_config.get("unloading_time_mins", 30))
    
    # Single trip delivery time
    per_trip_duration_sec = driving_duration_sec + (loading_mins + unloading_mins + handling_buffer_mins) * 60.0
    
    # Total completion time if multiple trips
    if trips == 1:
        total_completion_sec = per_trip_duration_sec
    else:
        # Each return journey adds driving time back and subsequent loading/unloading
        total_completion_sec = (trips * driving_duration_sec * round_trip_multiplier) + (trips * (loading_mins + unloading_mins) * 60.0) + (handling_buffer_mins * 60.0)
        
    return {
        "vehicle_name": vehicle_config.get("name", "Vehicle"),
        "vehicle_type": vehicle_config.get("type", "NORMAL"),
        "vehicle_capacity_kg": capacity,
        "trips": trips,
        "road_distance_km": road_distance_km,
        "round_trip_multiplier": round_trip_multiplier,
        "cost_per_trip": round(cost_per_trip, 2),
        "total_transport_cost": round(total_transport_cost, 2),
        "cost_per_kg": round(cost_per_kg, 2),
        "per_trip_duration_sec": per_trip_duration_sec,
        "total_completion_sec": total_completion_sec,
        "temperature_range": vehicle_config.get("temperature_range", "Ambient"),
        "distance_charge": round(distance_charge, 2),
        "base_charge": base_charge,
        "loading_unloading_fee": loading_unloading,
        "toll_other_charges": additional_tolls
    }
