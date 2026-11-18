import os

target_file = os.path.join(os.path.dirname(__file__), "..", "modules", "buyer_connect_db.py")

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update init_buyer_connect_tables to create new tables
table_addition = """
    # 4. Farmer Produce Listings (Marketplace Supply)
    c.execute('''
    CREATE TABLE IF NOT EXISTS farmer_produce_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        farmer_name TEXT NOT NULL,
        farmer_phone TEXT NOT NULL,
        crop TEXT NOT NULL,
        variety TEXT NOT NULL,
        quantity_quintals REAL NOT NULL,
        expected_price_per_quintal REAL NOT NULL,
        quality_grade TEXT NOT NULL,
        harvest_date TEXT NOT NULL,
        village TEXT NOT NULL,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        notes TEXT,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TEXT NOT NULL,
        FOREIGN KEY (farmer_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # 5. Crop Inspections (AI Assessed & Human Inspector Verified)
    c.execute('''
    CREATE TABLE IF NOT EXISTS crop_inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_ref TEXT UNIQUE NOT NULL,
        farmer_id INTEGER NOT NULL,
        farmer_name TEXT NOT NULL,
        crop TEXT NOT NULL,
        quantity_quintals REAL NOT NULL,
        ai_grade TEXT NOT NULL,
        ai_confidence REAL NOT NULL,
        ai_damage_notes TEXT,
        inspector_id INTEGER,
        inspector_name TEXT,
        inspector_grade TEXT,
        brix_reading REAL,
        size_caliper_mm REAL,
        defect_percent REAL,
        inspection_notes TEXT,
        status TEXT NOT NULL DEFAULT 'AI_ASSESSED',
        certificate_hash TEXT,
        created_at TEXT NOT NULL,
        verified_at TEXT,
        FOREIGN KEY (farmer_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (inspector_id) REFERENCES users (id) ON DELETE SET NULL
    )
    ''')

    # 6. Trade Transactions & Scam Protection
    c.execute('''
    CREATE TABLE IF NOT EXISTS trade_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quotation_id INTEGER,
        farmer_id INTEGER NOT NULL,
        farmer_name TEXT NOT NULL,
        buyer_id INTEGER NOT NULL,
        buyer_name TEXT NOT NULL,
        crop TEXT NOT NULL,
        farmer_weight_kg REAL NOT NULL,
        weighbridge_weight_kg REAL NOT NULL,
        weight_discrepancy_kg REAL NOT NULL,
        agreed_rate_per_kg REAL NOT NULL,
        paid_rate_per_kg REAL NOT NULL,
        deductions_amount REAL NOT NULL DEFAULT 0.0,
        deduction_reason TEXT,
        payment_received REAL NOT NULL,
        total_agreed_amount REAL NOT NULL,
        payment_status TEXT NOT NULL DEFAULT 'PAID',
        risk_level TEXT NOT NULL DEFAULT 'LOW',
        weighbridge_slip_ref TEXT,
        payment_slip_ref TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (farmer_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (buyer_id) REFERENCES buyers (id) ON DELETE CASCADE
    )
    ''')

    # 7. Transaction Disputes
    c.execute('''
    CREATE TABLE IF NOT EXISTS transaction_disputes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        buyer_id INTEGER NOT NULL,
        dispute_type TEXT NOT NULL,
        claimed_loss_amount REAL NOT NULL,
        dispute_statement TEXT NOT NULL,
        evidence_file TEXT,
        resolution_status TEXT NOT NULL DEFAULT 'FILED',
        admin_notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (transaction_id) REFERENCES trade_transactions (id) ON DELETE CASCADE
    )
    ''')
"""

if "CREATE TABLE IF NOT EXISTS farmer_produce_listings" not in code:
    code = code.replace("conn.commit()\n    seed_verified_buyers_and_requirements(conn)", table_addition + "\n    conn.commit()\n    seed_verified_buyers_and_requirements(conn)")

# 2. Add Helper Functions at the end
new_functions = '''

# ==============================================================================
# PRODUCE LISTINGS (FARMER SUPPLY)
# ==============================================================================
def create_produce_listing(
    farmer_id: int,
    farmer_name: str,
    farmer_phone: str,
    crop: str,
    variety: str,
    quantity_quintals: float,
    expected_price_per_quintal: float,
    quality_grade: str,
    harvest_date: str,
    village: str,
    district: str,
    state: str,
    latitude: float,
    longitude: float,
    notes: Optional[str] = None
) -> Tuple[bool, str, Optional[int]]:
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        c.execute("""
        INSERT INTO farmer_produce_listings (
            farmer_id, farmer_name, farmer_phone, crop, variety, quantity_quintals,
            expected_price_per_quintal, quality_grade, harvest_date, village,
            district, state, latitude, longitude, notes, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
        """, (
            farmer_id, farmer_name, farmer_phone, crop, variety, quantity_quintals,
            expected_price_per_quintal, quality_grade, harvest_date, village,
            district, state, latitude, longitude, notes, now_str
        ))
        conn.commit()
        return True, "Produce listing created successfully.", c.lastrowid
    except Exception as e:
        conn.rollback()
        return False, f"Failed to create produce listing: {str(e)}", None
    finally:
        conn.close()


def get_all_produce_listings(status: str = "ACTIVE") -> List[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM farmer_produce_listings WHERE status = ? ORDER BY created_at DESC", (status,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_farmer_produce_listings(farmer_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM farmer_produce_listings WHERE farmer_id = ? ORDER BY created_at DESC", (farmer_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==============================================================================
# CROP INSPECTIONS (AI ASSESSED & HUMAN INSPECTOR VERIFIED)
# ==============================================================================
def create_crop_inspection(
    batch_ref: str,
    farmer_id: int,
    farmer_name: str,
    crop: str,
    quantity_quintals: float,
    ai_grade: str,
    ai_confidence: float,
    ai_damage_notes: str
) -> Tuple[bool, str, Optional[int]]:
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        c.execute("""
        INSERT INTO crop_inspections (
            batch_ref, farmer_id, farmer_name, crop, quantity_quintals,
            ai_grade, ai_confidence, ai_damage_notes, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'AI_ASSESSED', ?)
        """, (batch_ref, farmer_id, farmer_name, crop, quantity_quintals, ai_grade, ai_confidence, ai_damage_notes, now_str))
        conn.commit()
        return True, "Crop inspection record created.", c.lastrowid
    except Exception as e:
        conn.rollback()
        return False, f"Failed to create inspection: {str(e)}", None
    finally:
        conn.close()


def get_all_inspections(status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    if status:
        c.execute("SELECT * FROM crop_inspections WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        c.execute("SELECT * FROM crop_inspections ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def verify_crop_inspection(
    inspection_id: int,
    inspector_id: int,
    inspector_name: str,
    inspector_grade: str,
    brix_reading: float,
    size_caliper_mm: float,
    defect_percent: float,
    inspection_notes: str
) -> Tuple[bool, str]:
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    import hashlib
    cert_hash = hashlib.sha256(f"INSP_{inspection_id}_{inspector_name}_{now_str}".encode("utf-8")).hexdigest()[:16].upper()
    try:
        c.execute("""
        UPDATE crop_inspections
        SET inspector_id = ?,
            inspector_name = ?,
            inspector_grade = ?,
            brix_reading = ?,
            size_caliper_mm = ?,
            defect_percent = ?,
            inspection_notes = ?,
            status = 'HUMAN_VERIFIED',
            certificate_hash = ?,
            verified_at = ?
        WHERE id = ?
        """, (
            inspector_id, inspector_name, inspector_grade, brix_reading,
            size_caliper_mm, defect_percent, inspection_notes, cert_hash, now_str, inspection_id
        ))
        conn.commit()
        return True, f"Inspection verified successfully. Certificate #{cert_hash}"
    except Exception as e:
        conn.rollback()
        return False, f"Verification failed: {str(e)}"
    finally:
        conn.close()


# ==============================================================================
# TRADE TRANSACTIONS & DISPUTES
# ==============================================================================
def record_trade_transaction(
    farmer_id: int,
    farmer_name: str,
    buyer_id: int,
    buyer_name: str,
    crop: str,
    farmer_weight_kg: float,
    weighbridge_weight_kg: float,
    agreed_rate_per_kg: float,
    paid_rate_per_kg: float,
    deductions_amount: float = 0.0,
    deduction_reason: Optional[str] = None,
    payment_received: float = 0.0,
    weighbridge_slip_ref: Optional[str] = None,
    notes: Optional[str] = None
) -> Tuple[bool, str, Optional[int]]:
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    weight_disc = farmer_weight_kg - weighbridge_weight_kg
    total_agreed = farmer_weight_kg * agreed_rate_per_kg
    disc_pct = (weight_disc / farmer_weight_kg * 100.0) if farmer_weight_kg > 0 else 0.0

    risk = "LOW"
    if disc_pct > 10.0 or (agreed_rate_per_kg - paid_rate_per_kg) > 2.0 or deductions_amount > total_agreed * 0.1:
        risk = "CRITICAL_DISCREPANCY"
    elif disc_pct > 4.0 or deductions_amount > 0:
        risk = "MODERATE_DISCREPANCY"

    p_status = "PAID" if payment_received >= (total_agreed - deductions_amount) * 0.95 else "PARTIAL"

    try:
        c.execute("""
        INSERT INTO trade_transactions (
            farmer_id, farmer_name, buyer_id, buyer_name, crop,
            farmer_weight_kg, weighbridge_weight_kg, weight_discrepancy_kg,
            agreed_rate_per_kg, paid_rate_per_kg, deductions_amount, deduction_reason,
            payment_received, total_agreed_amount, payment_status, risk_level,
            weighbridge_slip_ref, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            farmer_id, farmer_name, buyer_id, buyer_name, crop,
            farmer_weight_kg, weighbridge_weight_kg, weight_disc,
            agreed_rate_per_kg, paid_rate_per_kg, deductions_amount, deduction_reason,
            payment_received, total_agreed, p_status, risk, weighbridge_slip_ref, notes, now_str
        ))
        conn.commit()
        return True, "Trade transaction recorded successfully.", c.lastrowid
    except Exception as e:
        conn.rollback()
        return False, f"Failed to record transaction: {str(e)}", None
    finally:
        conn.close()


def get_transactions_for_user(user_id: int, role: str = "farmer") -> List[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    if role == "buyer":
        c.execute("SELECT * FROM trade_transactions WHERE buyer_id = ? ORDER BY created_at DESC", (user_id,))
    elif role == "admin" or role == "inspector":
        c.execute("SELECT * FROM trade_transactions ORDER BY created_at DESC")
    else:
        c.execute("SELECT * FROM trade_transactions WHERE farmer_id = ? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def file_transaction_dispute(
    transaction_id: int,
    farmer_id: int,
    buyer_id: int,
    dispute_type: str,
    claimed_loss_amount: float,
    dispute_statement: str,
    evidence_file: Optional[str] = None
) -> Tuple[bool, str]:
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        c.execute("""
        INSERT INTO transaction_disputes (
            transaction_id, farmer_id, buyer_id, dispute_type,
            claimed_loss_amount, dispute_statement, evidence_file,
            resolution_status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'FILED', ?, ?)
        """, (
            transaction_id, farmer_id, buyer_id, dispute_type,
            claimed_loss_amount, dispute_statement, evidence_file, now_str, now_str
        ))
        c.execute("UPDATE trade_transactions SET payment_status = 'DISPUTED' WHERE id = ?", (transaction_id,))
        conn.commit()
        return True, "Dispute filed successfully and submitted to APMC grievance cell."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to file dispute: {str(e)}"
    finally:
        conn.close()
'''

if "def create_produce_listing" not in code:
    code += new_functions

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESSFULLY EXPANDED buyer_connect_db.py")
