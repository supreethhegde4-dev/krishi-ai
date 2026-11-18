"""
Comprehensive Unit Test Suite for Krishi AI Predictive Intelligence & Decision System
Verifies:
1. Historical Intelligence (DuckDB 16.37M aggregations, YoY trends, anomalies)
2. Seasonal Intelligence (Crop calendars, optimal windows)
3. Agricultural Risk Analytics (Multi-factor risk scoring, composite index)
4. What-If Simulation Engine (Dual-inference, delta computation)
5. Explainable AI (SHAP TreeExplainer, waterfall values)
6. Unified Decision Intelligence Report (8-section synthesis)
"""
import os
import sys
import unittest
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.historical_intelligence import (
    get_historical_database_metrics, get_commodity_yoy_trends,
    get_monthly_seasonal_profile, detect_historical_price_anomalies,
    get_regional_market_benchmarks
)
from modules.seasonal_intelligence import get_seasonal_crop_intelligence
from modules.risk_analytics import evaluate_agricultural_risks
from modules.what_if_simulator import run_what_if_simulation
from modules.explainable_ai import explain_yield_prediction
from modules.decision_engine import generate_unified_decision_report
from modules.data_loader import load_normalized_marketplace_data


class TestPredictiveIntelligence(unittest.TestCase):

    def test_01_historical_database_metrics(self):
        """Verify DuckDB parquet metrics across 16.37M rows."""
        metrics = get_historical_database_metrics()
        self.assertGreater(metrics["total_records"], 10_000_000)
        self.assertEqual(metrics["total_states"], 32)
        print(f"\n[Test 1] Historical Parquet Records: {metrics['total_records']:,} rows across {metrics['total_states']} States")

    def test_02_commodity_yoy_trends(self):
        """Verify YoY price trends and CAGR."""
        res = get_commodity_yoy_trends("Tomato", state="Karnataka")
        self.assertIn("yoy_records", res)
        self.assertTrue(len(res["yoy_records"]) >= 2)
        print(f"[Test 2] Tomato Karnataka YoY: {len(res['yoy_records'])} years analyzed, CAGR: {res['cagr_pct']}%")

    def test_03_monthly_seasonality(self):
        """Verify 12-month seasonality profile."""
        res = get_monthly_seasonal_profile("Tomato", state="Karnataka")
        self.assertIn("peak_month", res)
        self.assertIn("trough_month", res)
        print(f"[Test 3] Seasonal Profile: Peak = {res['peak_month']} (₹{res['peak_price_kg']}/kg), Trough = {res['trough_month']}")

    def test_04_anomaly_detection(self):
        """Verify rolling z-score price anomaly detector."""
        anomalies = detect_historical_price_anomalies("Tomato", state="Karnataka", threshold_std=2.0)
        self.assertIsInstance(anomalies, list)
        print(f"[Test 4] Price Anomalies Detected: {len(anomalies)} historical price shock events")

    def test_05_seasonal_crop_intelligence(self):
        """Verify agro-climatic seasonal calendars."""
        intel = get_seasonal_crop_intelligence("Tomato")
        self.assertEqual(intel["clean_name"], "Tomato")
        self.assertIn("Rabi", intel["all_seasons"])
        print(f"[Test 5] Seasonal Intelligence: Stage = {intel['stage_badge']}, Primary = {intel['primary_season']}")

    def test_06_agricultural_risk_analytics(self):
        """Verify multi-factor agricultural risk engine."""
        risk = evaluate_agricultural_risks(
            crop="Tomato",
            temperature_c=36.0,  # Heat stress
            humidity_pct=40.0,
            rainfall_mm=25.0,    # Drought stress
            n_val=40.0,          # Nitrogen deficiency
            p_val=45.0,
            k_val=45.0,
            ph_val=5.2           # Acidic stress
        )
        self.assertGreater(risk["composite_risk_score"], 40.0)
        self.assertIn("risk_badge", risk)
        print(f"[Test 6] Risk Score: {risk['composite_risk_score']}/100 ({risk['risk_badge']})")

    def test_07_what_if_simulation(self):
        """Verify What-If simulation delta analysis."""
        baseline = {"acreage": 2.5, "soil_n": 85.0, "soil_p": 55.0, "soil_k": 58.0, "rainfall": 82.0, "ph": 6.5, "temperature": 25.0, "humidity": 70.0}
        simulated = {"acreage": 2.5, "soil_n": 120.0, "soil_p": 65.0, "soil_k": 75.0, "rainfall": 110.0, "ph": 6.8, "temperature": 24.0, "humidity": 75.0}
        
        sim_res = run_what_if_simulation("Tomato", baseline, simulated, mandi_price_kg=16.5)
        self.assertIn("deltas", sim_res)
        print(f"[Test 7] What-If Simulation: Yield Delta = {sim_res['deltas']['yield_kg']:+.0f} kg ({sim_res['deltas']['yield_pct']:+.1f}%), Revenue Delta = ₹{sim_res['deltas']['revenue']:+,.2f}")

    def test_08_explainable_ai_shap(self):
        """Verify SHAP TreeExplainer feature attributions."""
        xai = explain_yield_prediction(
            crop_name="Tomato",
            acreage=2.5,
            soil_n=85.0,
            soil_p=55.0,
            soil_k=58.0,
            rainfall=82.0,
            ph=6.5
        )
        self.assertIn("feature_impacts", xai)
        self.assertIn("waterfall_fig", xai)
        print(f"[Test 8] Explainable AI: Base Value = {xai['base_value_quintal']} Q/ac, Predicted = {xai['predicted_yield_quintal']} Q/ac, Top Driver = {xai['feature_impacts'][0]['feature_label']}")

    def test_09_unified_decision_report(self):
        """Verify 8-section Agricultural Decision Report."""
        df_m = load_normalized_marketplace_data()
        farm = {
            "full_name": "Ramesh Gowda",
            "farm_name": "Ramesh Organic Estate",
            "district": "Ramanagara",
            "state": "Karnataka",
            "acreage": 2.5,
            "latitude": 12.7209,
            "longitude": 77.2799
        }
        report = generate_unified_decision_report(
            farm_profile=farm,
            crop_name="Tomato",
            quantity_kg=500.0,
            n_val=85.0,
            p_val=55.0,
            k_val=58.0,
            ph_val=6.5,
            temp_c=25.2,
            humidity_pct=71.0,
            rainfall_mm=82.0,
            df_marketplace=df_m,
            vehicle_type="Mini Truck (Normal)"
        )
        self.assertIn("1_historical_performance", report)
        self.assertIn("6_best_marketplace", report)
        self.assertIn("7_estimated_net_revenue", report)
        self.assertIn("8_recommended_decisions", report)
        self.assertEqual(len(report["8_recommended_decisions"]), 5)
        print(f"[Test 9] Decision Report Generated: Best Mandi = {report['6_best_marketplace']['mandi']}, Net Proceeds = ₹{report['7_estimated_net_revenue']['net_proceeds']:,.2f}")


if __name__ == "__main__":
    unittest.main()
