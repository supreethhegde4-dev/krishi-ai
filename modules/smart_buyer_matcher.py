"""
Smart Buyer & Industry Matching Engine for Krishi AI.
Ranks industrial buyers and purchasing requirements based on:
1. Geographic distance & road transit duration
2. Crop type & variety match
3. Quantity compatibility (fulfillment lot ratio)
4. Quality grade compatibility (Grade A, B, C, Organic)
5. Transportation cost & logistics economics
6. Net Farmer Revenue vs APMC Mandi benchmark
7. Overall Multi-Factor Suitability Score (0 - 100%)
"""
import os
import math
from typing import Dict, Any, List, Optional

from modules.buyer_connect_db import get_active_requirements, get_all_buyers
from modules.geo_ors import haversine_distance_km, estimate_road_distance_demo
from modules.transport_engine import DEFAULT_VEHICLE_CONFIGS, calculate_transport_cost

# Quality Grade Ranking
GRADE_HIERARCHY = {
    "Certified Organic": 4,
    "Grade A (Premium)": 3,
    "Grade B (Standard)": 2,
    "Grade C (Commercial)": 1
}


def evaluate_quality_compatibility(farmer_grade: str, required_min_grade: str) -> Tuple[float, str]:
    """
    Evaluates grade compatibility.
    Returns (score_0_100, explainer).
    """
    f_rank = GRADE_HIERARCHY.get(farmer_grade, 2)
    r_rank = GRADE_HIERARCHY.get(required_min_grade, 2)

    if f_rank == 4 and r_rank < 4:
        return 100.0, "Certified Organic lot exceeds buyer standard specification (Premium intake)."
    elif f_rank >= r_rank:
        return 100.0, f"Quality Grade '{farmer_grade}' fully meets or exceeds buyer minimum requirement '{required_min_grade}'."
    elif f_rank == r_rank - 1:
        return 65.0, f"Offered Grade '{farmer_grade}' is one tier below preferred '{required_min_grade}'. May require commercial grading allowance."
    else:
        return 25.0, f"Offered Grade '{farmer_grade}' does not meet required minimum '{required_min_grade}'."


def evaluate_quantity_compatibility(farmer_qty_qtl: float, required_qty_qtl: float) -> Tuple[float, str]:
    """
    Evaluates quantity compatibility.
    Returns (score_0_100, explainer).
    """
    if required_qty_qtl <= 0:
        return 50.0, "Open intake lot."

    ratio = farmer_qty_qtl / required_qty_qtl

    if ratio >= 1.0:
        return 100.0, f"Full batch fulfillment: Available quantity ({farmer_qty_qtl:.1f} Qtl) satisfies 100% of required lot."
    elif ratio >= 0.5:
        return 92.0, f"Substantial supply lot: Fulfills {ratio*100:.0f}% of total requirement ({farmer_qty_qtl:.1f} of {required_qty_qtl:.1f} Qtl)."
    elif ratio >= 0.2:
        return 82.0, f"Viable dispatch lot: Fulfills {ratio*100:.0f}% of requirement. Buyer aggregates partial truckloads."
    elif ratio >= 0.05:
        return 68.0, f"Small partial lot ({ratio*100:.0f}% of requirement). Best combined with regional FPO dispatch."
    else:
        return 45.0, f"Very small volume ({ratio*100:.1f}% of requirement). High relative freight per quintal."


def compute_buyer_freight_cost(
    farmer_lat: float,
    farmer_lon: float,
    delivery_lat: float,
    delivery_lon: float,
    quantity_quintals: float,
    vehicle_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates deterministic transport cost from farmer holding to buyer facility.
    """
    road_km, duration_sec = estimate_road_distance_demo(farmer_lat, farmer_lon, delivery_lat, delivery_lon)
    produce_kg = quantity_quintals * 100.0

    # Auto-select optimal vehicle if not specified
    if not vehicle_key or vehicle_key not in DEFAULT_VEHICLE_CONFIGS:
        if produce_kg <= 1200:
            vehicle_key = "Mini Truck (Normal)"
        else:
            vehicle_key = "Goods Truck (Normal)"

    v_config = DEFAULT_VEHICLE_CONFIGS[vehicle_key]
    cost_info = calculate_transport_cost(
        quantity_kg=produce_kg,
        road_distance_km=road_km,
        driving_duration_sec=duration_sec,
        vehicle_config=v_config
    )

    cost_info["total_cost"] = cost_info.get("total_transport_cost", 0.0)
    cost_info["road_distance_km"] = road_km
    cost_info["duration_sec"] = duration_sec
    cost_info["duration_hours"] = round(duration_sec / 3600.0, 1)
    cost_info["vehicle_name"] = v_config["name"]
    cost_info["freight_per_quintal"] = round(cost_info["total_cost"] / max(1.0, quantity_quintals), 2)

    return cost_info


def match_buyers_for_farmer(
    farmer_lat: float,
    farmer_lon: float,
    crop: str = "Tomato",
    quantity_quintals: float = 30.0,
    farmer_grade: str = "Grade A (Premium)",
    min_asking_price: Optional[float] = None,
    max_distance_km: Optional[float] = None,
    vehicle_key: Optional[str] = None,
    benchmark_mandi_price_qtl: float = 2100.0
) -> List[Dict[str, Any]]:
    """
    Main Smart Matching Engine:
    Ranks active buyer requirements against farmer profile and harvest lot.
    """
    # Fetch all active requirements matching crop (or all open requirements if crop == "All Crops")
    reqs = get_active_requirements(crop=crop if crop != "All Crops" else None)

    matched_deals: List[Dict[str, Any]] = []

    for req in reqs:
        d_lat = req["delivery_lat"]
        d_lon = req["delivery_lon"]

        # 1. Geographic Distance & Freight
        freight = compute_buyer_freight_cost(
            farmer_lat=farmer_lat,
            farmer_lon=farmer_lon,
            delivery_lat=d_lat,
            delivery_lon=d_lon,
            quantity_quintals=quantity_quintals,
            vehicle_key=vehicle_key
        )
        dist_km = freight["road_distance_km"]

        # Filter out if exceeds max distance filter
        if max_distance_km is not None and max_distance_km > 0 and dist_km > max_distance_km:
            continue

        # Distance Score (0 - 100): 100 if <= 20 km, 0 if >= 300 km
        dist_score = max(0.0, min(100.0, 100.0 - ((dist_km - 20.0) / 280.0 * 100.0))) if dist_km > 20 else 100.0

        # 2. Crop Match
        crop_match_score = 100.0 if req["crop"].lower() == crop.lower() else 70.0

        # 3. Quantity Compatibility
        quant_score, quant_explainer = evaluate_quantity_compatibility(quantity_quintals, req["quantity_quintals"])

        # 4. Quality Compatibility
        qual_score, qual_explainer = evaluate_quality_compatibility(farmer_grade, req["min_quality_grade"])

        # 5. Price & Economics
        offered_price_qtl = req["offered_price_per_quintal"]
        offered_price_kg = round(offered_price_qtl / 100.0, 2)

        # Filter out if buyer offers below farmer minimum asking price
        if min_asking_price is not None and min_asking_price > 0 and offered_price_qtl < min_asking_price:
            continue

        gross_revenue = round(offered_price_qtl * quantity_quintals, 2)
        total_freight_cost = freight["total_cost"]
        net_revenue = round(gross_revenue - total_freight_cost, 2)
        net_price_per_qtl = round(net_revenue / max(1.0, quantity_quintals), 2)
        net_price_per_kg = round(net_price_per_qtl / 100.0, 2)

        # Benchmark comparison (Mandi gate vs Buyer direct contract)
        # Mandi baseline: price - 3% cess - ₹40/qtl loading - local transport
        mandi_gross = round(benchmark_mandi_price_qtl * quantity_quintals, 2)
        mandi_local_cost = round(total_freight_cost * 0.45, 2)  # Local mandi typically closer
        mandi_deductions = round(mandi_gross * 0.03 + 40.0 * quantity_quintals, 2)
        mandi_net = round(mandi_gross - mandi_local_cost - mandi_deductions, 2)

        net_profit_delta = round(net_revenue - mandi_net, 2)
        roi_gain_pct = round((net_profit_delta / max(1.0, mandi_net)) * 100.0, 1)

        # Price Score (0 - 100)
        # Higher score if offered net price exceeds benchmark mandi
        price_ratio = net_price_per_qtl / max(1.0, benchmark_mandi_price_qtl)
        if price_ratio >= 1.25:
            price_score = 100.0
        elif price_ratio >= 1.0:
            price_score = 75.0 + ((price_ratio - 1.0) / 0.25 * 25.0)
        elif price_ratio >= 0.85:
            price_score = 50.0 + ((price_ratio - 0.85) / 0.15 * 25.0)
        else:
            price_score = max(10.0, price_ratio * 50.0)

        # 6. Credibility Score
        buyer_rating = req.get("buyer_rating", 4.8)
        verified = req.get("verified_status", 1)
        cred_score = (buyer_rating / 5.0 * 70.0) + (30.0 if verified else 10.0)

        # 7. Composite Weighted Suitability Score (0 - 100%)
        # Price (30%), Distance (25%), Quantity (20%), Quality (15%), Credibility (10%)
        suitability_score = round(
            (0.30 * price_score) +
            (0.25 * dist_score) +
            (0.20 * quant_score) +
            (0.15 * qual_score) +
            (0.10 * cred_score),
            1
        )

        # Recommendation Tier Badge
        if suitability_score >= 85.0:
            match_badge = "🌟 Top Match (Prime Deal)"
            badge_color = "#15803D"
        elif suitability_score >= 70.0:
            match_badge = "🟢 Favorable Opportunity"
            badge_color = "#16A34A"
        elif suitability_score >= 55.0:
            match_badge = "🟡 Moderate Match"
            badge_color = "#D97706"
        else:
            match_badge = "⚪ Low Compatibility"
            badge_color = "#64748B"

        matched_deals.append({
            "requirement_id": req["id"],
            "buyer_id": req["buyer_id"],
            "company_name": req["company_name"],
            "business_type": req["business_type"],
            "contact_person": req["contact_person"],
            "phone": req.get("buyer_phone", ""),
            "email": req.get("buyer_email", ""),
            "verified_status": bool(req.get("verified_status", 1)),
            "buyer_rating": buyer_rating,
            "total_deals_completed": req.get("total_deals_completed", 12),
            "payment_terms": req.get("payment_terms", "Standard 24h"),
            "facility_address": req["facility_address"],
            "delivery_location": req["delivery_location"],
            "delivery_district": req["delivery_district"],
            "delivery_state": req["delivery_state"],
            "crop": req["crop"],
            "required_quantity_quintals": req["quantity_quintals"],
            "min_quality_grade": req["min_quality_grade"],
            "offered_price_per_quintal": offered_price_qtl,
            "offered_price_per_kg": offered_price_kg,
            "required_by_date": req["required_by_date"],
            "additional_specs": req.get("additional_specs", ""),
            "urgency_level": req.get("urgency_level", "Standard"),
            # Logistics & Economics
            "distance_km": dist_km,
            "duration_hours": freight["duration_hours"],
            "vehicle_used": freight["vehicle_name"],
            "total_freight_cost": total_freight_cost,
            "freight_per_quintal": freight["freight_per_quintal"],
            "farmer_quantity_quintals": quantity_quintals,
            "gross_revenue": gross_revenue,
            "net_revenue": net_revenue,
            "net_price_per_qtl": net_price_per_qtl,
            "net_price_per_kg": net_price_per_kg,
            "mandi_net_baseline": mandi_net,
            "net_profit_delta": net_profit_delta,
            "roi_gain_pct": roi_gain_pct,
            # Match Scoring Breakdown
            "suitability_score": suitability_score,
            "match_badge": match_badge,
            "badge_color": badge_color,
            "score_price": round(price_score, 1),
            "score_distance": round(dist_score, 1),
            "score_quantity": round(quant_score, 1),
            "score_quality": round(qual_score, 1),
            "score_credibility": round(cred_score, 1),
            "quantity_explainer": quant_explainer,
            "quality_explainer": qual_explainer
        })

    # Sort primarily by suitability score descending, then net profit descending
    matched_deals.sort(key=lambda x: (x["suitability_score"], x["net_profit_delta"]), reverse=True)
    return matched_deals
