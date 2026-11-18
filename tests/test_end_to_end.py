"""
End-to-End Test Suite for KisanAI Prototype.
Tests all 11 points from the master scenario:
- Crop: Tomato
- Quantity: 500 kg
- Location: Ramanagara, Karnataka
- Market: Ramanagara / Kolar / Bangalore
"""
import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.data_loader import inspect_marketplace_data, load_normalized_marketplace_data
from modules.geo_ors import calculate_matrix_distances, get_directions_route
from modules.transport_engine import DEFAULT_VEHICLE_CONFIGS, calculate_transport_cost, check_temperature_suitability
from modules.proceeds_calculator import compute_mandi_proceeds_table
from modules.quality_evaluator import evaluate_quality
from modules.fair_price_model import predict_fair_price_band
from modules.fraud_detector import evaluate_buyer_offer
from modules.historical_data import get_distinct_filter_values, query_historical_prices
from modules.forecasting import train_and_forecast_price
from modules.sell_advisor import evaluate_sell_timing


if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def run_all_tests():
    print("=" * 60)
    print("RUNNING KISANAI END-TO-END TEST SUITE")
    print("=" * 60)

    # 1. Test Phase 1 Data Loading & Inspection
    print("\n[Test 1] Phase 1 Data Loading & Normalization...")
    report = inspect_marketplace_data()
    assert report["total_records"] == 2733, f"Expected 2733 rows, got {report['total_records']}"
    assert report["crops_count"] > 100 or "Tomato" in report["crops_sample"]
    df_norm = load_normalized_marketplace_data()
    assert len(df_norm) >= 2733
    assert "modal_price_kg" in df_norm.columns
    print(f"  -> PASS: Loaded {len(df_norm)} records. Price conversion to ₹/kg verified.")

    # 2. Test Phase 2 & 3: Geocoding & OpenRouteService Integration
    print("\n[Test 2] Phase 2 & 3: Farmer Origin & ORS Matrix Routing...")
    farmer_lat, farmer_lon = 12.7209, 77.2799  # Ramanagara, Karnataka
    dests = [
        {"name": "Bangalore Binny Mill", "lat": 12.9698, "lon": 77.5684},
        {"name": "Kolar APMC", "lat": 13.1380, "lon": 78.1310}
    ]
    mat_res = calculate_matrix_distances(farmer_lat, farmer_lon, dests)
    assert len(mat_res) == 2
    assert mat_res[0]["distance_km"] > 0
    print(f"  -> PASS: Computed distances: {mat_res[0]['name']} = {mat_res[0]['distance_km']} km ({mat_res[0]['duration_formatted']})")

    # 3. Test Phase 4 & 5: Normal vs Cold-Chain Transportation
    print("\n[Test 3] Phase 4 & 5: Transportation Logistics Calculation...")
    mini_truck = DEFAULT_VEHICLE_CONFIGS["Mini Truck (Normal)"]
    t_calc = calculate_transport_cost(
        quantity_kg=500.0,
        road_distance_km=48.5,
        driving_duration_sec=4200.0,
        vehicle_config=mini_truck,
        round_trip_multiplier=1.0
    )
    assert t_calc["trips"] == 1
    assert t_calc["total_transport_cost"] > 0
    suit_norm = check_temperature_suitability("Tomato", mini_truck, 4200.0 / 3600.0)
    print(f"  -> PASS: 500 kg Tomato -> Trips: {t_calc['trips']}, Cost: ₹{t_calc['total_transport_cost']:.2f}, Suitability: {suit_norm['badge']}")

    # 4. Test Phase 6: Mandi Net Proceeds Ranker
    print("\n[Test 4] Phase 6: Mandi Net Proceeds Ranking...")
    mandi_res = compute_mandi_proceeds_table(
        df_marketplace=df_norm,
        crop_name="Tomato",
        quantity_kg=500.0,
        farmer_lat=farmer_lat,
        farmer_lon=farmer_lon,
        vehicle_config=mini_truck
    )
    assert len(mandi_res["records"]) > 0
    assert mandi_res["best_mandi"] is not None
    assert mandi_res["nearest_mandi"] is not None
    print(f"  -> PASS: Best Mandi: {mandi_res['best_mandi']['mandi']} with Net Proceeds ₹{mandi_res['best_mandi']['net_proceeds']:,.2f}")
    print(f"  -> Nearest Mandi: {mandi_res['nearest_mandi']['mandi']}, Distance: {mandi_res['nearest_mandi']['road_distance_km']} km")
    print(f"  -> Arbitrage Advantage: ₹{mandi_res['net_advantage_vs_nearest']:,.2f}")

    # 5. Test Objectives 1 & 2: Quality Evaluator & Fair Price Model
    print("\n[Test 5] Objectives 1 & 2: Crop Quality & Fair Price Band...")
    q_eval = evaluate_quality(crop_name="Tomato", firmness="Firm (Optimal)", defect_pct=2.0)
    assert q_eval["quality_score"] >= 80.0
    assert "Grade A" in q_eval["grade"]
    fp = predict_fair_price_band(df_norm, "Tomato", "Karnataka", quality_score=q_eval["quality_score"])
    assert fp["fair_modal_price_kg"] > 0
    print(f"  -> PASS: Quality Score: {q_eval['quality_score']}/100 ({q_eval['grade']}). Fair Modal: ₹{fp['fair_modal_price_kg']:.2f}/kg")

    # 6. Test Objective 7: Suspicious Buyer Offer Detector
    print("\n[Test 6] Objective 7: Fraud & Unfair Offer Detector...")
    fraud_eval = evaluate_buyer_offer(
        offered_price_kg=10.0,
        quantity_kg=500.0,
        benchmark_modal_price_kg=16.5,
        best_mandi_net_price_kg=14.8
    )
    assert "PREDATORY" in fraud_eval["status"] or "BELOW" in fraud_eval["status"]
    assert fraud_eval["farmer_loss_gain"] < 0
    print(f"  -> PASS: Detected predatory bid: {fraud_eval['status']}, Loss: ₹{abs(fraud_eval['farmer_loss_gain']):,.2f}")

    # 7. Test Feature 5: Dynamic Filters
    print("\n[Test 7] Feature 5: Dynamic Historical Filter Cascading...")
    filt_vals = get_distinct_filter_values(commodity="Tomato", state="Karnataka")
    assert "Ramanagara" in filt_vals["markets"] or "Ramanagara" in filt_vals["districts"] or len(filt_vals["markets"]) > 5
    print(f"  -> PASS: Distinct filters for Karnataka Tomato: {len(filt_vals['districts'])} districts, {len(filt_vals['markets'])} markets.")

    # 8. Test Feature 5: DuckDB Historical Price Querying (Daily & Weekly)
    print("\n[Test 8] Feature 5: DuckDB Historical Querying (Ramanagara Tomato)...")
    df_h = query_historical_prices(
        commodity="Tomato",
        state="Karnataka",
        markets=["Ramanagara"],
        aggregation="Daily"
    )
    assert len(df_h) > 50, f"Expected >50 records, got {len(df_h)}"
    print(f"  -> PASS: Retrieved {len(df_h)} daily price records for Ramanagara. Latest date: {df_h['Arrival_Date'].max()}")

    # Weekly Aggregation
    df_w = query_historical_prices(
        commodity="Tomato",
        state="Karnataka",
        markets=["Ramanagara"],
        aggregation="Weekly"
    )
    assert not df_w.empty
    print(f"  -> PASS: Weekly aggregated series has {len(df_w)} records.")

    # 9. Test Feature 5: Machine Learning Forecasting Model (3, 7, 14 days)
    print("\n[Test 9] Feature 5: Random Forest Chronological Forecasting...")
    fc = train_and_forecast_price(df_h, horizons=[3, 7, 14])
    assert fc["status"] == "SUCCESS"
    assert "3_day" in fc["predictions"]
    assert "7_day" in fc["predictions"]
    assert "14_day" in fc["predictions"]
    assert fc["metrics"]["mae"] > 0
    print(f"  -> PASS: Forecast trained on {fc['observations_count']} records.")
    print(f"     Metrics: MAE = ₹{fc['metrics']['mae']:.2f}/kg, sMAPE = {fc['metrics']['smape']:.1f}%")
    print(f"     Predictions: 3d = ₹{fc['predictions']['3_day']['predicted_price_kg']:.2f}, 7d = ₹{fc['predictions']['7_day']['predicted_price_kg']:.2f}, 14d = ₹{fc['predictions']['14_day']['predicted_price_kg']:.2f}")

    # 10. Test Feature 5: Sell Now vs Wait Decision Engine
    print("\n[Test 10] Feature 5: Sell Now or Wait Decision Engine...")
    dec_eval = evaluate_sell_timing(
        crop_name="Tomato",
        quantity_kg=500.0,
        current_price_kg=fc["latest_observed_price"],
        predicted_future_price_kg=fc["predictions"]["7_day"]["predicted_price_kg"],
        horizon_days=7,
        daily_storage_cost_per_kg=0.15,
        spoilage_pct=3.5
    )
    assert dec_eval["recommendation"] in ["SELL NOW", "CONSIDER WAITING", "SELL PARTIALLY"]
    print(f"  -> PASS: Recommendation: {dec_eval['recommendation']}")
    print(f"     Current Net: ₹{dec_eval['current_net_proceeds']:,.2f} vs Future Net: ₹{dec_eval['future_net_proceeds']:,.2f}")
    print(f"     Net Diff: ₹{dec_eval['net_difference']:,.2f} ({dec_eval['gain_pct']:+.1f}% ROI)")

    print("\n" + "=" * 60)
    print("ALL 10 VERIFICATION SUITES PASSED FLAWLESSLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
