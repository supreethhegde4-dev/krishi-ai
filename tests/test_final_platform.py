"""
Comprehensive Final Platform Verification Suite for Krishi AI.
Tests:
1. Multi-Role Authentication & Access Control (Farmer, Buyer, Inspector, Admin)
2. External API Clients & Fallbacks (data.gov.in, Open-Meteo, NASA POWER, Gemini, Pl@ntNet)
3. Produce Supply & Listing Engine
4. Multimodal Crop Image Quality & Inspector Sign-off Workflow
5. Transaction Protection, Tare Discrepancy Auditing & APMC Dispute Engine
6. Gemini Agricultural AI Assistant Context Sanitization & Deterministic Rules
7. Unified Decision Report Synthesis & ReportLab PDF Generation
8. Core ML Models (Crop Suitability Classifier, Yield Regressor, SHAP TreeExplainer, Lag Forecaster)
"""
import os
import sys
import unittest
import datetime
import pandas as pd
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from modules.auth_db import init_db, authenticate_user, get_user_by_session_token, invalidate_session
from modules.api_clients import (
    DataGovInMandiClient, OpenMeteoWeatherClient, NasaPowerClient,
    GeminiAgriClient, PlantNetClient, get_api_status_report
)
from modules.image_intelligence import analyze_produce_batch, GRADE_CONFIGS
from modules.transaction_protection import evaluate_transaction_risk
from modules.buyer_connect_db import (
    init_buyer_connect_tables, create_produce_listing, get_all_produce_listings,
    create_crop_inspection, get_all_inspections, verify_crop_inspection,
    record_trade_transaction, get_transactions_for_user, file_transaction_dispute
)
from modules.ai_assistant import build_farmer_system_context, query_agricultural_assistant
from modules.pdf_report_generator import generate_unified_pdf_report
from modules.decision_engine import generate_unified_decision_report
from modules.data_loader import load_normalized_marketplace_data
from modules.crop_advisor import recommend_crop
from modules.yield_analytics import predict_crop_yield
from modules.explainable_ai import explain_yield_prediction


class TestFinalKrishiAIPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        init_buyer_connect_tables()
        cls.df_market = load_normalized_marketplace_data()

    def test_01_multi_role_authentication(self):
        """Verifies authentication for all 4 roles: Farmer, Buyer, Inspector, Admin."""
        # 1. Farmer
        s_f, _, _, u_f = authenticate_user("farmer@krishiai.com", "Password@123")
        self.assertTrue(s_f, "Farmer login must succeed")
        self.assertEqual(u_f["role"], "farmer")

        # 2. Buyer
        s_b, _, _, u_b = authenticate_user("buyer@krishiai.com", "Password@123")
        self.assertTrue(s_b, "Buyer login must succeed")
        self.assertEqual(u_b["role"], "buyer")

        # 3. Inspector
        s_i, _, _, u_i = authenticate_user("inspector@krishiai.com", "Inspector@123")
        self.assertTrue(s_i, "Inspector login must succeed")
        self.assertEqual(u_i["role"], "inspector")

        # 4. Admin
        s_a, _, _, u_a = authenticate_user("admin@krishiai.com", "Admin@123")
        self.assertTrue(s_a, "Admin login must succeed")
        self.assertEqual(u_a["role"], "admin")

    def test_02_api_status_monitor(self):
        """Verifies the health check reporter returns all 6 core services."""
        status = get_api_status_report()
        self.assertEqual(len(status), 6, "Must monitor all 6 integration services")
        services = [s["name"] for s in status]
        self.assertIn("data.gov.in AGMARKNET", services)
        self.assertIn("Open-Meteo Weather API", services)
        self.assertIn("Google Gemini Generative AI", services)

    def test_03_open_meteo_weather_and_alerts(self):
        """Verifies Open-Meteo weather fetching and agronomic risk rules."""
        wx = OpenMeteoWeatherClient.get_weather_intelligence(12.7209, 77.2799)
        self.assertIn("current", wx)
        self.assertIn("daily_forecast", wx)
        self.assertIn("agronomic_alerts", wx)
        cur = wx["current"]
        self.assertGreater(cur["temperature_c"], -10.0)
        self.assertLess(cur["temperature_c"], 60.0)

    def test_04_datagov_mandi_client_and_fallback(self):
        """Verifies data.gov.in AGMARKNET client serves records either live or via lakehouse fallback."""
        mandi = DataGovInMandiClient.fetch_live_mandi_prices(state="Karnataka", commodity="Tomato", limit=5)
        self.assertIn("source", mandi)
        self.assertIn("data", mandi)
        self.assertGreater(len(mandi["data"]), 0, "Mandi records must not be empty")

    def test_05_produce_listings_supply_creation(self):
        """Verifies farmer produce listing creation in SQLite."""
        succ, msg, l_id = create_produce_listing(
            farmer_id=1,
            farmer_name="Ramesh Gowda",
            farmer_phone="+91 98450 12345",
            crop="Tomato",
            variety="Local Special",
            quantity_quintals=50.0,
            expected_price_per_quintal=1850.0,
            quality_grade="Grade A (Premium)",
            harvest_date="2026-11-25",
            village="Ramanagara Rural",
            district="Ramanagara",
            state="Karnataka",
            latitude=12.7209,
            longitude=77.2799,
            notes="Fully matured, organic pest management applied."
        )
        self.assertTrue(succ, f"Produce listing creation failed: {msg}")
        self.assertIsNotNone(l_id)
        listings = get_all_produce_listings()
        self.assertGreater(len(listings), 0)

    def test_06_crop_inspection_and_certification_lifecycle(self):
        """Verifies AI inspection record creation and subsequent Human Inspector sign-off."""
        batch_ref = f"BATCH-TEST-{int(datetime.datetime.now().timestamp())}"
        s_c, _, i_id = create_crop_inspection(
            batch_ref=batch_ref,
            farmer_id=1,
            farmer_name="Ramesh Gowda",
            crop="Tomato",
            quantity_quintals=30.0,
            ai_grade="Grade A (Premium Export)",
            ai_confidence=93.5,
            ai_damage_notes="Uniform coloration; zero foliar blight."
        )
        self.assertTrue(s_c)
        self.assertIsNotNone(i_id)

        # Inspector certifies lot
        s_v, msg_v = verify_crop_inspection(
            inspection_id=i_id,
            inspector_id=3,
            inspector_name="Dr. Anand Murthy",
            inspector_grade="Grade A (Premium Export)",
            brix_reading=5.4,
            size_caliper_mm=60.0,
            defect_percent=3.2,
            inspection_notes="Passed official APMC Grade A export criteria."
        )
        self.assertTrue(s_v)
        self.assertIn("Certificate #", msg_v)

    def test_07_transaction_protection_and_scam_detection(self):
        """Verifies mathematical tare discrepancy detection and loss quantification."""
        audit = evaluate_transaction_risk(
            farmer_weight_kg=1000.0,
            weighbridge_weight_kg=850.0,  # 150 kg shortfall = 15% discrepancy
            agreed_rate_per_kg=18.0,
            paid_rate_per_kg=16.0,        # 2.0 Rs/kg rate cut
            deductions_amount=600.0,
            payment_received=13000.0
        )
        self.assertEqual(audit["risk_level"], "CRITICAL_DISCREPANCY")
        self.assertEqual(audit["weight_diff_kg"], 150.0)
        self.assertEqual(audit["weight_diff_pct"], 15.0)
        self.assertTrue(audit["dispute_recommended"])
        self.assertGreater(audit["total_shortfall_rs"], 4000.0)

    def test_08_gemini_assistant_context_and_fallback(self):
        """Verifies assistant context builder strips private secrets and answers agronomic questions."""
        user = {"id": 1, "full_name": "Ramesh Gowda", "email": "farmer@krishiai.com", "role": "farmer"}
        farm = {"farm_name": "Green Valley", "acreage": 3.5, "district": "Ramanagara", "state": "Karnataka", "soil_type": "Red Loam"}
        context = build_farmer_system_context(user, farm, crop_name="Tomato", benchmark_price_kg=18.5)
        self.assertNotIn("password_hash", context)
        self.assertNotIn("token", context)

        resp = query_agricultural_assistant("What is the best selling price for my Tomato today?", context)
        self.assertIn("answer", resp)
        self.assertIn("₹18.50", resp["answer"])

    def test_09_pdf_report_generation(self):
        """Verifies that the ReportLab PDF generator produces valid, non-empty binary PDF data."""
        dummy_report = {
            "metadata": {"crop": "Tomato", "farmer_name": "Ramesh Gowda", "farm_name": "Green Valley Farm", "district": "Ramanagara", "state": "Karnataka", "generated_at": "November 18, 2026"},
            "1_historical_performance": {"avg_historical_price_kg": 18.5, "peak_price_month": "July"},
            "2_current_conditions": {"holding_acreage": 3.5, "soil_n_p_k": "N:90 | P:50 | K:60 kg/ha", "soil_ph": 6.5, "current_weather": "24.5°C", "soil_health_rating": "Optimal"},
            "3_expected_yield": {"total_harvest_kg": 26480, "predicted_yield_per_acre": 105.9},
            "4_future_market_price": {"forecast_14_day": 19.8, "projected_trend": "Bullish"},
            "5_risk_assessment": {"composite_score": 18, "risk_badge": "Low Risk"},
            "6_best_marketplace": {"mandi": "K.R.Nagar APMC", "district": "Mysore", "state": "Karnataka", "road_distance_km": 48.2, "travel_duration": "1h 12m", "recommended_vehicle": "Mini Truck"},
            "7_estimated_net_revenue": {"gross_market_value": 12500, "total_transport_cost": 850, "total_mandi_deductions": 420, "net_proceeds": 11230, "net_realized_price_kg": 18.2, "arbitrage_advantage_vs_nearest": 410},
            "8_recommended_decisions": ["Dispatch to K.R.Nagar APMC for optimal arbitrage.", "Apply MOP prior to transit harvest."]
        }
        pdf = generate_unified_pdf_report(dummy_report)
        self.assertIsInstance(pdf, bytes)
        self.assertTrue(pdf.startswith(b"%PDF-"), "Generated buffer must be a valid PDF format")
        self.assertGreater(len(pdf), 2000, "PDF payload must contain full report elements")

    def test_10_end_to_end_ml_decision_pipeline(self):
        """Verifies full ML inference pipeline: Crop Rec -> Yield Pred -> SHAP Attribution -> Decision Report."""
        # 1. Crop recommendation
        rec = recommend_crop(90, 50, 60, 24.5, 68.0, 6.5, 75.0)
        self.assertIn("primary_crop", rec)

        # 2. Yield prediction
        yd = predict_crop_yield("Tomato", 3.5, 90, 50, 60, 75.0, 6.5)
        self.assertGreater(yd["predicted_yield_per_acre"], 50.0)

        # 3. SHAP attribution
        shap_res = explain_yield_prediction("Tomato", 3.5, 90, 50, 60, 75.0, 6.5)
        self.assertIn("base_value_quintal", shap_res)
        self.assertIn("top_positive_driver", shap_res)

        # 4. Decision Report
        farm_profile = {"full_name": "Ramesh Gowda", "farm_name": "Green Valley", "district": "Ramanagara", "state": "Karnataka", "acreage": 3.5, "latitude": 12.7209, "longitude": 77.2799}
        rep = generate_unified_decision_report(
            farm_profile=farm_profile,
            crop_name="Tomato",
            quantity_kg=500.0,
            n_val=90, p_val=50, k_val=60, ph_val=6.5,
            temp_c=24.5, humidity_pct=65.0, rainfall_mm=75.0,
            df_marketplace=self.df_market
        )
        self.assertIn("6_best_marketplace", rep)
        self.assertIn("7_estimated_net_revenue", rep)
        self.assertIn("8_recommended_decisions", rep)


if __name__ == "__main__":
    unittest.main()
