"""
Mandi Net Proceeds & Comparison Calculator for KisanAI.
Complies with Phase 6: Gross revenue, mandi expenses, transport deductions, ranking, and nearest vs best mandi comparison.
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from modules.geo_ors import calculate_matrix_distances, format_duration
from modules.transport_engine import calculate_transport_cost, check_temperature_suitability


DEFAULT_MANDI_FEES = {
    "mandi_cess_pct": 1.5,      # Standard state APMC cess (1.5%)
    "commission_pct": 2.0,      # Commission agent fee (2.0%)
    "labor_per_kg": 0.30        # Mandi unloading/weighing labor charge (₹0.30/kg)
}


def compute_mandi_proceeds_table(
    df_marketplace: pd.DataFrame,
    crop_name: str,
    quantity_kg: float,
    farmer_lat: float,
    farmer_lon: float,
    vehicle_config: Dict[str, Any],
    variety: Optional[str] = None,
    grade: Optional[str] = None,
    round_trip_multiplier: float = 1.0,
    mandi_fees: Optional[Dict[str, float]] = None,
    ors_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes comparative financial proceeds for all eligible mandis.
    """
    fees = mandi_fees or DEFAULT_MANDI_FEES
    cess_rate = fees.get("mandi_cess_pct", 1.5) / 100.0
    comm_rate = fees.get("commission_pct", 2.0) / 100.0
    labor_rate = fees.get("labor_per_kg", 0.30)

    # 1. Filter matching commodity
    df_crop = df_marketplace[
        (df_marketplace['commodity'].str.lower() == crop_name.lower()) &
        (df_marketplace['is_valid'] == True)
    ].copy()

    if df_crop.empty:
        # Fallback to loose search
        df_crop = df_marketplace[
            df_marketplace['commodity'].str.lower().str.contains(crop_name.lower()) &
            (df_marketplace['is_valid'] == True)
        ].copy()

    if df_crop.empty:
        return {
            "records": [],
            "best_mandi": None,
            "nearest_mandi": None,
            "highest_gross_mandi": None,
            "fallback_note": f"No active market listings found for '{crop_name}'."
        }

    # Fallback explanation for grade/variety
    fallback_note = None
    if variety and variety != "All Varieties":
        df_var = df_crop[df_crop['variety'].str.lower() == variety.lower()]
        if not df_var.empty:
            df_crop = df_var
        else:
            fallback_note = f"Specific variety '{variety}' was not found in all mandis; included comparable varieties."

    if grade and grade != "All Grades":
        df_grd = df_crop[df_crop['grade'].str.lower() == grade.lower()]
        if not df_grd.empty:
            df_crop = df_grd
        else:
            note = f"Exact grade '{grade}' was unavailable in some mandis; used FAQ/standard fallback."
            fallback_note = f"{fallback_note} | {note}" if fallback_note else note

    # Deduplicate by market (take highest modal price if multiple listings)
    df_unique_markets = df_crop.sort_values(by="modal_price_kg", ascending=False).drop_duplicates(subset=["state", "district", "market"])

    # Prepare destinations for distance calculation
    destinations = []
    from modules.geo_ors import load_coordinates_cache
    coords_cache = load_coordinates_cache()

    market_records = []
    for _, row in df_unique_markets.iterrows():
        m_name = row['market']
        dist_name = row['district']
        st_name = row['state']
        
        # Multi-level coordinate resolution
        clean_m_name = m_name.replace(" APMC", "").replace(" (F&V)", "").replace(" (Grain Market)", "").strip()
        candidates = [
            f"{m_name}, {dist_name}, {st_name}",
            f"{clean_m_name}, {dist_name}, {st_name}",
            m_name,
            clean_m_name,
            f"{dist_name}, {st_name}",
            dist_name
        ]
        
        lat, lon = None, None
        for c_key in candidates:
            if c_key in coords_cache and isinstance(coords_cache[c_key], dict):
                lat = coords_cache[c_key].get("lat")
                lon = coords_cache[c_key].get("lon")
                if lat is not None and lon is not None:
                    break
        
        # Fuzzy/substring match if exact key not in cache
        if lat is None or lon is None:
            m_low = clean_m_name.lower()
            for k, val in coords_cache.items():
                if isinstance(val, dict) and (k.lower() in m_low or m_low in k.lower()):
                    lat = val.get("lat")
                    lon = val.get("lon")
                    if lat is not None and lon is not None:
                        break

        # Centroid approximation fallback
        if lat is None or lon is None:
            lat, lon = 20.5937, 78.9629

        destinations.append({
            "name": m_name,
            "district": dist_name,
            "state": st_name,
            "lat": lat,
            "lon": lon,
            "modal_price_kg": row['modal_price_kg'],
            "min_price_kg": row['min_price_kg'],
            "max_price_kg": row['max_price_kg'],
            "variety": row['variety'],
            "grade": row['grade'],
            "arrival_date": row['arrival_date']
        })

    # Calculate road matrix distances
    matrix_results = calculate_matrix_distances(farmer_lat, farmer_lon, destinations, api_key=ors_api_key)

    processed_rows = []
    for item in matrix_results:
        road_km = item.get("distance_km", 25.0)
        dur_s = item.get("duration_sec", 3600.0)
        modal_price = item["modal_price_kg"]
        
        # Financial Calculations
        gross_revenue = quantity_kg * modal_price
        
        # Transport Cost
        t_calc = calculate_transport_cost(
            quantity_kg=quantity_kg,
            road_distance_km=road_km,
            driving_duration_sec=dur_s,
            vehicle_config=vehicle_config,
            round_trip_multiplier=round_trip_multiplier
        )
        transport_cost = t_calc["total_transport_cost"]
        
        # Mandi fees
        mandi_cess = gross_revenue * cess_rate
        commission = gross_revenue * comm_rate
        labor_fee = quantity_kg * labor_rate
        total_selling_expenses = transport_cost + mandi_cess + commission + labor_fee
        
        net_proceeds = gross_revenue - total_selling_expenses
        net_price_realized = net_proceeds / quantity_kg if quantity_kg > 0 else 0.0

        # Suitability
        suitability = check_temperature_suitability(crop_name, vehicle_config, dur_s / 3600.0)

        processed_rows.append({
            "mandi": item["name"],
            "district": item["district"],
            "state": item["state"],
            "arrival_date": item["arrival_date"],
            "variety": item["variety"],
            "grade": item["grade"],
            "modal_price_kg": round(modal_price, 2),
            "min_price_kg": round(item["min_price_kg"], 2),
            "max_price_kg": round(item["max_price_kg"], 2),
            "road_distance_km": round(road_km, 1),
            "driving_duration": format_duration(dur_s),
            "driving_duration_sec": dur_s,
            "gross_revenue": round(gross_revenue, 2),
            "transport_cost": round(transport_cost, 2),
            "mandi_cess": round(mandi_cess, 2),
            "commission": round(commission, 2),
            "labor_fee": round(labor_fee, 2),
            "total_expenses": round(total_selling_expenses, 2),
            "net_proceeds": round(net_proceeds, 2),
            "net_price_per_kg": round(net_price_realized, 2),
            "distance_source": item.get("source", "DEMO"),
            "suitability_badge": suitability["badge"],
            "suitability_msg": suitability["message"]
        })

    # Sort descending by Net Proceeds
    processed_rows.sort(key=lambda x: x["net_proceeds"], reverse=True)

    # Key comparisons
    best_mandi = processed_rows[0] if processed_rows else None
    
    # Nearest mandi (lowest road distance)
    nearest_mandi = min(processed_rows, key=lambda x: x["road_distance_km"]) if processed_rows else None
    
    # Highest gross mandi
    highest_gross_mandi = max(processed_rows, key=lambda x: x["gross_revenue"]) if processed_rows else None

    # Compute comparative advantage
    net_advantage = 0.0
    extra_distance = 0.0
    if best_mandi and nearest_mandi:
        net_advantage = round(best_mandi["net_proceeds"] - nearest_mandi["net_proceeds"], 2)
        extra_distance = round(best_mandi["road_distance_km"] - nearest_mandi["road_distance_km"], 1)

    return {
        "records": processed_rows,
        "best_mandi": best_mandi,
        "nearest_mandi": nearest_mandi,
        "highest_gross_mandi": highest_gross_mandi,
        "net_advantage_vs_nearest": net_advantage,
        "extra_distance_vs_nearest": extra_distance,
        "fallback_note": fallback_note
    }
