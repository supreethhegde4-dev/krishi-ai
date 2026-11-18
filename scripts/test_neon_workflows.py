"""
Verifies end-to-end workflows (Farmer, Buyer, Inspector, Transactions) directly against Neon PostgreSQL.
"""
import os
import sys
import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from modules.auth_db import (
    authenticate_user, register_user, get_user_by_session_token,
    invalidate_session, delete_user_account
)
from modules.buyer_connect_db import (
    create_buyer_requirement, submit_farmer_quotation,
    create_produce_listing, create_crop_inspection, verify_crop_inspection,
    get_all_buyers, get_active_requirements
)
from modules.db_engine import check_database_health, is_postgres_configured

def main():
    print("[1] Verifying Neon PostgreSQL Connection...")
    h = check_database_health()
    print(f"  • Database: {h['database_type']} (Status: {h['status']})")
    assert h["is_persistent_cloud"] == True

    # 1. Test Existing User Authentication on Neon
    print("\n[2] Testing Authentication against Neon PostgreSQL...")
    ok, msg, token, user = authenticate_user("farmer@krishiai.com", "Password@123")
    print(f"  • Login result: {ok} | Name: {user['full_name']} | Role: {user['role']}")
    assert ok == True
    assert token is not None

    # Verify session in Neon
    sess_user = get_user_by_session_token(token)
    assert sess_user is not None
    assert sess_user["email"] == "farmer@krishiai.com"
    print("  • Session token verified in Neon database.")
    invalidate_session(token)

    # 2. Test Farmer Registration & Farm Profile on Neon
    ts = int(datetime.datetime.now().timestamp())
    test_email = f"neon_test_farmer_{ts}@krishitest.in"
    print(f"\n[3] Registering Test Farmer ({test_email}) on Neon PostgreSQL...")
    reg_ok, reg_msg = register_user(
        full_name="Somanna Gowda",
        email=test_email,
        password="SecurePass#2026",
        phone="+91 94480 11223",
        role="farmer"
    )
    print(f"  • Registration: {reg_ok} ({reg_msg})")
    assert reg_ok == True

    # Login newly registered user
    l_ok, _, l_token, new_user = authenticate_user(test_email, "SecurePass#2026")
    assert l_ok == True
    new_uid = new_user["id"]
    print(f"  • New Farmer ID in Neon: #{new_uid}")

    # 3. Create Produce Listing on Neon
    print("\n[4] Creating Farmer Produce Listing on Neon PostgreSQL...")
    list_ok, list_msg, list_id = create_produce_listing(
        farmer_id=new_uid,
        farmer_name="Somanna Gowda",
        farmer_phone="+91 94480 11223",
        crop="Tomato",
        variety="Vaishnavi Hybrid",
        quantity_quintals=50.0,
        expected_price_per_quintal=2200.0,
        quality_grade="Grade A",
        harvest_date=datetime.date.today().isoformat(),
        village="Kolar Rural",
        district="Kolar",
        state="Karnataka",
        latitude=13.1367,
        longitude=78.1292,
        notes="Drip-irrigated premium harvest."
    )
    print(f"  • Produce Listing Created: {list_ok} | Listing ID #{list_id}")
    assert list_ok == True
    assert list_id > 0

    # 4. Create Buyer Requirement & Farmer Quotation on Neon
    print("\n[5] Testing Buyer Requirement & Farmer Quotation on Neon PostgreSQL...")
    buyers = get_all_buyers()
    assert len(buyers) > 0
    test_buyer_id = buyers[0]["id"]

    req_ok, req_msg, req_id = create_buyer_requirement(
        buyer_id=test_buyer_id,
        crop="Tomato",
        quantity_quintals=30.0,
        min_quality_grade="Grade A",
        offered_price_per_quintal=2400.0,
        delivery_location="Bengaluru Cold Hub",
        delivery_district="Bengaluru Urban",
        delivery_state="Karnataka",
        delivery_lat=12.9716,
        delivery_lon=77.5946,
        required_by_date=(datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
        additional_specs="Target Brix >= 5.0",
        urgency_level="High"
    )
    print(f"  • Buyer Requirement Created: {req_ok} | Req ID #{req_id}")
    assert req_ok == True

    q_ok, q_msg, q_id = submit_farmer_quotation(
        requirement_id=req_id,
        farmer_id=new_uid,
        farmer_name="Somanna Gowda",
        farmer_phone="+91 94480 11223",
        crop="Tomato",
        offered_quantity_quintals=30.0,
        quoted_price_per_quintal=2350.0,
        offered_grade="Grade A",
        dispatch_location="Kolar Mandi Gate",
        dispatch_district="Kolar",
        dispatch_state="Karnataka",
        dispatch_lat=13.1367,
        dispatch_lon=78.1292,
        expected_delivery_date=(datetime.date.today() + datetime.timedelta(days=2)).isoformat()
    )
    print(f"  • Quotation Submitted: {q_ok} | Quotation ID #{q_id}")
    assert q_ok == True

    # 5. Crop Inspection & Certificate Lifecycle on Neon
    print("\n[6] Testing Quality Inspection & Certification on Neon PostgreSQL...")
    i_ok, i_msg, insp_id = create_crop_inspection(
        batch_ref=f"BATCH-NEON-{ts%10000:04d}",
        farmer_id=new_uid,
        farmer_name="Somanna Gowda",
        crop="Tomato",
        quantity_quintals=50.0,
        ai_grade="Grade A (Premium Export)",
        ai_confidence=95.0,
        ai_damage_notes="Zero visible defects."
    )
    print(f"  • AI Inspection Batch Created: {i_ok} | Insp ID #{insp_id}")
    assert i_ok == True

    v_ok, v_msg = verify_crop_inspection(
        inspection_id=insp_id,
        inspector_id=2,  # Admin user ID
        inspector_name="Quality Auditor",
        inspector_grade="Grade A (Premium Export)",
        brix_reading=5.8,
        size_caliper_mm=64.0,
        defect_percent=2.5,
        inspection_notes="Passed export tolerance standards."
    )
    print(f"  • Human Verification Signed: {v_ok} ({v_msg})")
    assert v_ok == True

    # Cleanup test user (cascades)
    delete_user_account(new_uid)
    print(f"\n[7] Cleaned up temporary test user #{new_uid} and cascaded child records.")

    print("\n" + "="*60)
    print("ALL REAL NEON POSTGRESQL WORKFLOWS VERIFIED 100% SUCCESSFULLY!")
    print("="*60)

if __name__ == "__main__":
    main()
