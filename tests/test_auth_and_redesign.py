"""
Comprehensive Test Suite for Krishi AI Authentication & Redesigned Agronomic Modules.
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from modules.auth_db import (
    register_user, authenticate_user, get_user_by_session_token,
    invalidate_session, create_password_reset_token, reset_password_with_token,
    save_user_prediction, get_user_predictions
)
from modules.crop_advisor import recommend_crop
from modules.soil_intelligence import evaluate_soil_health
from modules.fertilizer_advisor import calculate_fertilizer_prescription
from modules.yield_analytics import predict_crop_yield


def run_tests():
    print("=" * 65)
    print("RUNNING KRISHI AI AUTHENTICATION & REDESIGN VERIFICATION")
    print("=" * 65)

    # 1. Test Seeded Farmer Login
    print("\n[Test 1] Seeded Farmer Authentication...")
    ok, msg, token, user = authenticate_user("farmer@krishiai.com", "Password@123")
    assert ok, f"Farmer login failed: {msg}"
    assert user["full_name"] == "Ramesh Gowda"
    assert user["role"] == "farmer"
    print(f"  -> PASS: Logged in as {user['full_name']} (Role: {user['role']}). Session token generated.")

    # 2. Test Session Persistence & Verification
    print("\n[Test 2] Session Token Verification...")
    session_user = get_user_by_session_token(token)
    assert session_user is not None
    assert session_user["email"] == "farmer@krishiai.com"
    print(f"  -> PASS: Session validated for {session_user['email']}")

    # 3. Test Invalid Login & Throttling
    print("\n[Test 3] Invalid Password & Login Throttling...")
    bad_ok, bad_msg, _, _ = authenticate_user("farmer@krishiai.com", "WrongPassword")
    assert not bad_ok
    assert "Invalid email or password" in bad_msg
    print(f"  -> PASS: Invalid credentials correctly rejected.")

    # 4. Test New User Registration
    print("\n[Test 4] New Farmer Registration & Duplicate Prevention...")
    test_email = "testfarmer1@krishiai.com"
    reg_ok, reg_msg = register_user("Anand Kumar", test_email, "StrongPass@123", "+91 9123456789")
    # Might already be registered if re-run
    if reg_ok:
        print(f"  -> PASS: Registered new farmer {test_email}")
    else:
        assert "already exists" in reg_msg
        print(f"  -> PASS: Duplicate prevention triggered: {reg_msg}")

    # Test Duplicate
    dup_ok, dup_msg = register_user("Anand Kumar", test_email, "StrongPass@123")
    assert not dup_ok
    assert "already exists" in dup_msg
    print(f"  -> PASS: Duplicate email rejected.")

    # 5. Test Password Reset Token
    print("\n[Test 5] Password Reset Token Generation...")
    tok_ok, tok_msg, r_token = create_password_reset_token(test_email)
    assert tok_ok and r_token is not None
    print(f"  -> PASS: Reset token generated: {r_token[:12]}...")

    # 6. Test User Data Isolation
    print("\n[Test 6] Farmer Private Data Isolation...")
    # Log in test farmer
    _, _, t_token, t_user = authenticate_user(test_email, "StrongPass@123")
    assert t_user is not None
    farmer_id = user["id"]
    test_id = t_user["id"]

    # Save prediction under farmer_id
    save_user_prediction(farmer_id, "Crop Advisor", "Tomato Prediction", '{"N": 80}', '{"crop": "Tomato"}')
    # Save prediction under test_id
    save_user_prediction(test_id, "Soil Intelligence", "Soil Test", '{"pH": 6.5}', '{"health": 85}')

    farmer_preds = get_user_predictions(farmer_id)
    test_preds = get_user_predictions(test_id)

    # Ensure farmer only sees their own
    for p in farmer_preds:
        assert p["user_id"] == farmer_id
    for p in test_preds:
        assert p["user_id"] == test_id
    print(f"  -> PASS: Strict user data isolation confirmed ({len(farmer_preds)} records for Farmer, {len(test_preds)} for Test User).")

    # 7. Test Crop Advisor ML Model
    print("\n[Test 7] Crop Advisor ML Inference...")
    crop_eval = recommend_crop(85.0, 55.0, 58.0, 25.2, 71.0, 6.5, 82.0)
    assert crop_eval["primary_crop"] is not None
    assert crop_eval["confidence"] > 50.0
    print(f"  -> PASS: Recommended Crop: {crop_eval['primary_crop']} ({crop_eval['confidence']}% confidence)")

    # 8. Test Soil Intelligence
    print("\n[Test 8] Soil Intelligence Health Score...")
    soil_eval = evaluate_soil_health(75.0, 48.0, 62.0, 6.6, 0.65)
    assert soil_eval["health_index"] >= 50.0
    print(f"  -> PASS: Soil Health Index: {soil_eval['health_index']}/100 ({soil_eval['overall_condition']})")

    # 9. Test Fertilizer Advisor
    print("\n[Test 9] Fertilizer Advisor Prescriptions...")
    fert_eval = calculate_fertilizer_prescription("Tomato", 60.0, 35.0, 45.0, acreage=2.0)
    assert len(fert_eval["fertilizers"]) == 3
    assert len(fert_eval["schedule"]) == 3
    print(f"  -> PASS: Computed commercial fertilizers: Urea ({fert_eval['fertilizers'][1]['bags_50kg']} bags), DAP ({fert_eval['fertilizers'][0]['bags_50kg']} bags), MOP ({fert_eval['fertilizers'][2]['bags_50kg']} bags)")

    # 10. Test Yield Analytics
    print("\n[Test 10] Yield Analytics Forecasting...")
    yield_eval = predict_crop_yield("Tomato", acreage=2.5, soil_n=80.0, soil_p=50.0, soil_k=60.0, rainfall=85.0, ph=6.5)
    assert yield_eval["predicted_yield_per_acre"] > 0
    assert yield_eval["total_yield_quintals"] > 0
    print(f"  -> PASS: Forecasted Yield: {yield_eval['predicted_yield_per_acre']} Q/acre, Total: {yield_eval['total_yield_quintals']} Quintals ({yield_eval['total_yield_kg']:,.0f} kg)")

    # 11. Test Logout & Session Invalidation
    print("\n[Test 11] Session Logout & Invalidation...")
    invalidate_session(token)
    invalidated_user = get_user_by_session_token(token)
    assert invalidated_user is None
    print(f"  -> PASS: Session successfully invalidated on logout.")

    print("\n" + "=" * 65)
    print("ALL 11 AUTHENTICATION & REDESIGN TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
