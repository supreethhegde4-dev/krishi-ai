"""
Unit and Integration Test Suite for Krishi AI - Buyer & Industry Connect Module.
Covers:
1. Database Schema & Seed Verification (Buyers, Requirements, Quotations)
2. Smart Buyer Matching Engine (Distance, Freight Economics, Multi-factor Suitability)
3. Quality & Quantity Compatibility Logic
4. Farmer Quotation Submission & Input Validation
5. Buyer Quotation Review Lifecycle (Pending, Accepted, Rejected, Feedback)
6. Farmer & Buyer Data Isolation
7. Buyer Authentication & Role Integration
"""
import os
import sys
import unittest
import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from modules.buyer_connect_db import (
    init_buyer_connect_tables, get_all_buyers, get_buyer_by_id,
    get_active_requirements, get_requirement_by_id,
    create_buyer_requirement, submit_farmer_quotation,
    get_quotations_by_farmer, get_quotations_for_buyer,
    update_quotation_status, update_requirement_status
)
from modules.smart_buyer_matcher import (
    match_buyers_for_farmer, evaluate_quality_compatibility,
    evaluate_quantity_compatibility, compute_buyer_freight_cost
)
from modules.auth_db import authenticate_user


class TestBuyerConnectSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initializes tables and seeds test state."""
        init_buyer_connect_tables()

    def test_01_buyers_seeding_and_retrieval(self):
        """Validates that verified industrial buyers are seeded with complete profile fields."""
        buyers = get_all_buyers()
        self.assertGreaterEqual(len(buyers), 8, "Expected at least 8 seeded industrial buyers")
        
        # Verify first buyer structure
        b = buyers[0]
        self.assertIn("company_name", b)
        self.assertIn("business_type", b)
        self.assertIn("contact_person", b)
        self.assertIn("phone", b)
        self.assertIn("facility_address", b)
        self.assertIn("rating", b)
        self.assertIn("verified_status", b)
        self.assertIn("payment_terms", b)
        self.assertGreaterEqual(b["rating"], 4.0)

        # Verify crop-specific buyer filtering
        tomato_buyers = get_all_buyers(crop_filter="Tomato")
        self.assertGreaterEqual(len(tomato_buyers), 3, "Expected at least 3 buyers sourcing Tomato")
        print(f"\n[Test 1] Buyers Seeded: {len(buyers)} verified corporate buyers ({len(tomato_buyers)} sourcing Tomato)")

    def test_02_requirements_seeding_and_creation(self):
        """Validates requirement retrieval, filtering, and publication of new requirements."""
        reqs = get_active_requirements()
        self.assertGreaterEqual(len(reqs), 10, "Expected at least 10 active requirements")

        # Test crop filter
        potato_reqs = get_active_requirements(crop="Potato")
        self.assertGreaterEqual(len(potato_reqs), 2)
        for r in potato_reqs:
            self.assertEqual(r["crop"], "Potato")
            self.assertGreater(r["quantity_quintals"], 0)
            self.assertGreater(r["offered_price_per_quintal"], 0)

        # Test publication of a new requirement
        buyer_id = reqs[0]["buyer_id"]
        success, msg, new_rid = create_buyer_requirement(
            buyer_id=buyer_id,
            crop="Capsicum",
            quantity_quintals=50.0,
            min_quality_grade="Grade A (Premium)",
            offered_price_per_quintal=3500.0,
            delivery_location="ITC Processing Bay 4, Bidadi",
            delivery_district="Ramanagara",
            delivery_state="Karnataka",
            delivery_lat=12.7981,
            delivery_lon=77.4005,
            required_by_date=(datetime.date.today() + datetime.timedelta(days=12)).strftime("%Y-%m-%d"),
            additional_specs="Green bell capsicum, minimum fruit weight 150g, zero puncture damage.",
            urgency_level="Urgent"
        )
        self.assertTrue(success, f"Failed to publish requirement: {msg}")
        self.assertIsNotNone(new_rid)

        # Retrieve and verify newly published requirement
        new_req = get_requirement_by_id(new_rid)
        self.assertIsNotNone(new_req)
        self.assertEqual(new_req["crop"], "Capsicum")
        self.assertEqual(new_req["quantity_quintals"], 50.0)
        self.assertEqual(new_req["offered_price_per_quintal"], 3500.0)
        print(f"[Test 2] Requirements Verified: {len(reqs)} existing lots, New Requirement #{new_rid} published successfully")

    def test_03_smart_buyer_matching_engine(self):
        """Validates multi-factor matching, distance routing, and net profit calculations."""
        # Farmer in Ramanagara (12.7209, 77.2799) with 30 Quintals Tomato
        deals = match_buyers_for_farmer(
            farmer_lat=12.7209,
            farmer_lon=77.2799,
            crop="Tomato",
            quantity_quintals=30.0,
            farmer_grade="Grade A (Premium)",
            benchmark_mandi_price_qtl=2100.0
        )
        self.assertGreaterEqual(len(deals), 3, "Expected at least 3 matched buyers for Tomato")

        # Top deal should have highest suitability and positive profit advantage
        top = deals[0]
        self.assertGreaterEqual(top["suitability_score"], 75.0, "Top deal suitability score should be >= 75%")
        self.assertGreater(top["net_revenue"], 0, "Net revenue must be positive")
        self.assertGreater(top["distance_km"], 0, "Distance must be calculated")
        self.assertGreater(top["total_freight_cost"], 0, "Freight cost must be computed")
        self.assertEqual(top["gross_revenue"], round(top["offered_price_per_quintal"] * 30.0, 2))
        self.assertEqual(top["net_revenue"], round(top["gross_revenue"] - top["total_freight_cost"], 2))

        # Check distance filtering
        close_deals = match_buyers_for_farmer(
            farmer_lat=12.7209,
            farmer_lon=77.2799,
            crop="Tomato",
            quantity_quintals=30.0,
            farmer_grade="Grade A (Premium)",
            max_distance_km=50.0
        )
        for d in close_deals:
            self.assertLessEqual(d["distance_km"], 50.0)

        print(f"[Test 3] Smart Matching: {len(deals)} deals evaluated. Top Match = {top['company_name']} ({top['suitability_score']}/100, Net Extra Profit: ₹{top['net_profit_delta']:+,.2f})")

    def test_04_compatibility_logic(self):
        """Validates quality grade hierarchy and quantity fulfillment scoring."""
        # Grade compatibility
        score_a, _ = evaluate_quality_compatibility("Grade A (Premium)", "Grade A (Premium)")
        self.assertEqual(score_a, 100.0)

        score_org, _ = evaluate_quality_compatibility("Certified Organic", "Grade A (Premium)")
        self.assertEqual(score_org, 100.0)

        score_b_for_a, _ = evaluate_quality_compatibility("Grade B (Standard)", "Grade A (Premium)")
        self.assertEqual(score_b_for_a, 65.0)

        # Quantity fulfillment ratio
        q_full, _ = evaluate_quantity_compatibility(100.0, 80.0)
        self.assertEqual(q_full, 100.0)

        q_part, _ = evaluate_quantity_compatibility(25.0, 100.0)
        self.assertGreaterEqual(q_part, 80.0)
        print("[Test 4] Compatibility Scoring: Grade hierarchy & lot fulfillment ratio verified")

    def test_05_quotation_submission_and_lifecycle(self):
        """Tests quotation submission, status updates (Pending -> Accepted), and input validation."""
        reqs = get_active_requirements(crop="Tomato")
        self.assertTrue(len(reqs) > 0)
        target_req = reqs[0]

        # 1. Invalid quantity rejection
        sub_fail, msg, _ = submit_farmer_quotation(
            requirement_id=target_req["id"],
            farmer_id=1,
            farmer_name="Ramesh Gowda",
            farmer_phone="+91 98450 12345",
            crop="Tomato",
            offered_quantity_quintals=-5.0,  # Invalid
            quoted_price_per_quintal=2400.0,
            offered_grade="Grade A (Premium)",
            dispatch_location="Ramanagara",
            dispatch_district="Ramanagara",
            dispatch_state="Karnataka",
            dispatch_lat=12.7209,
            dispatch_lon=77.2799,
            expected_delivery_date="2026-11-25"
        )
        self.assertFalse(sub_fail)
        self.assertIn("greater than 0", msg)

        # 2. Valid quotation submission
        sub_ok, msg, qid = submit_farmer_quotation(
            requirement_id=target_req["id"],
            farmer_id=1,
            farmer_name="Ramesh Gowda",
            farmer_phone="+91 98450 12345",
            crop="Tomato",
            offered_quantity_quintals=25.0,
            quoted_price_per_quintal=2450.0,
            offered_grade="Grade A (Premium)",
            dispatch_location="Ramanagara Holding",
            dispatch_district="Ramanagara",
            dispatch_state="Karnataka",
            dispatch_lat=12.7209,
            dispatch_lon=77.2799,
            expected_delivery_date=(datetime.date.today() + datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
            farmer_notes="Morning batch, hand sorted."
        )
        self.assertTrue(sub_ok)
        self.assertIsNotNone(qid)

        # 3. Farmer retrieval
        f_quotes = get_quotations_by_farmer(1)
        my_quote = next((q for q in f_quotes if q["id"] == qid), None)
        self.assertIsNotNone(my_quote)
        self.assertEqual(my_quote["status"], "PENDING")
        self.assertEqual(my_quote["quoted_price_per_quintal"], 2450.0)

        # 4. Buyer status update to ACCEPTED
        up_ok, up_msg = update_quotation_status(
            quotation_id=qid,
            new_status="ACCEPTED",
            feedback="Bid accepted. Deliver to Bidadi processing dock 2."
        )
        self.assertTrue(up_ok)

        # 5. Verify status after acceptance
        f_quotes_updated = get_quotations_by_farmer(1)
        accepted_quote = next((q for q in f_quotes_updated if q["id"] == qid), None)
        self.assertIsNotNone(accepted_quote)
        self.assertEqual(accepted_quote["status"], "ACCEPTED")
        self.assertEqual(accepted_quote["buyer_feedback"], "Bid accepted. Deliver to Bidadi processing dock 2.")
        print(f"[Test 5] Quotation Lifecycle: Quotation #{qid} submitted, validated, and updated to ACCEPTED")

    def test_06_data_isolation(self):
        """Ensures farmers only see their quotations and buyers only see quotations for their requirements."""
        # Farmer 1 quotations
        f1_quotes = get_quotations_by_farmer(1)
        for q in f1_quotes:
            self.assertEqual(q["farmer_id"], 1)

        # Hypothetical farmer 999 should have 0 quotations
        f_empty = get_quotations_by_farmer(9999)
        self.assertEqual(len(f_empty), 0)

        # Buyer 1 quotations
        b1_quotes = get_quotations_for_buyer(1)
        for bq in b1_quotes:
            # Each quotation must be linked to a requirement belonging to buyer 1
            req = get_requirement_by_id(bq["requirement_id"])
            self.assertEqual(req["buyer_id"], 1)
        print("[Test 6] Data Isolation: Strict isolation confirmed between farmers and buyer accounts")

    def test_07_buyer_authentication_and_role(self):
        """Verifies buyer account credentials and role authorization."""
        ok, msg, token, user = authenticate_user("buyer@krishiai.com", "Password@123")
        self.assertTrue(ok)
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "buyer")
        self.assertIn("Vikramaditya", user["full_name"])
        print(f"[Test 7] Buyer Authentication: {user['email']} authenticated with role '{user['role']}'")


if __name__ == "__main__":
    unittest.main()
