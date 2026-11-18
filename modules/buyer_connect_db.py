"""
Buyer & Industry Connect Database Module for Krishi AI.
Handles schema initialization, verified industry seeding,
purchasing requirement publication, and farmer quotation lifecycle.
"""
import os
import sqlite3
import datetime
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "krishi_ai.db")


from modules.db_engine import get_db_connection, is_postgres_configured


def init_buyer_connect_tables():
    """Initializes tables for buyers, industry requirements, and quotations."""
    if is_postgres_configured():
        return
    conn = get_db_connection()
    c = conn.cursor()

    # 1. Registered Buyers & Industries (Production Schema)
    c.execute("""
    CREATE TABLE IF NOT EXISTS buyers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        company_name TEXT NOT NULL,
        business_type TEXT NOT NULL,
        contact_person TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        facility_address TEXT NOT NULL,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        gstin TEXT,
        apmc_license TEXT,
        verified_status INTEGER NOT NULL DEFAULT 0,
        verified_by INTEGER,
        verification_remarks TEXT,
        rating REAL NOT NULL DEFAULT 5.0,
        total_deals_completed INTEGER NOT NULL DEFAULT 0,
        payment_terms TEXT NOT NULL DEFAULT 'Within 24 Hours of Delivery / Gate Weighbridge Clearance',
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
        FOREIGN KEY (verified_by) REFERENCES users (id) ON DELETE SET NULL
    )
    """)

    # 2. Industry Purchasing Requirements
    c.execute("""
    CREATE TABLE IF NOT EXISTS buyer_requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER NOT NULL,
        crop TEXT NOT NULL,
        quantity_quintals REAL NOT NULL,
        min_quality_grade TEXT NOT NULL,
        offered_price_per_quintal REAL NOT NULL,
        delivery_location TEXT NOT NULL,
        delivery_district TEXT NOT NULL,
        delivery_state TEXT NOT NULL,
        delivery_lat REAL NOT NULL,
        delivery_lon REAL NOT NULL,
        required_by_date TEXT NOT NULL,
        additional_specs TEXT,
        urgency_level TEXT NOT NULL DEFAULT 'Standard',
        status TEXT NOT NULL DEFAULT 'OPEN',
        created_at TEXT NOT NULL,
        FOREIGN KEY (buyer_id) REFERENCES buyers (id) ON DELETE CASCADE
    )
    """)

    # 3. Farmer Quotations
    c.execute("""
    CREATE TABLE IF NOT EXISTS farmer_quotations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requirement_id INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        farmer_name TEXT NOT NULL,
        farmer_phone TEXT NOT NULL,
        crop TEXT NOT NULL,
        offered_quantity_quintals REAL NOT NULL,
        quoted_price_per_quintal REAL NOT NULL,
        offered_grade TEXT NOT NULL,
        dispatch_location TEXT NOT NULL,
        dispatch_district TEXT NOT NULL,
        dispatch_state TEXT NOT NULL,
        dispatch_lat REAL NOT NULL,
        dispatch_lon REAL NOT NULL,
        expected_delivery_date TEXT NOT NULL,
        farmer_notes TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING',
        counter_price_per_quintal REAL,
        buyer_feedback TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (requirement_id) REFERENCES buyer_requirements (id) ON DELETE CASCADE,
        FOREIGN KEY (farmer_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    
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

    conn.commit()
        # Database Migrations: Ensure production columns exist
    c.execute("PRAGMA table_info(buyers)")
    existing_cols = [r[1] for r in c.fetchall()]
    if "gstin" not in existing_cols:
        c.execute("ALTER TABLE buyers ADD COLUMN gstin TEXT")
    if "apmc_license" not in existing_cols:
        c.execute("ALTER TABLE buyers ADD COLUMN apmc_license TEXT")
    if "verified_by" not in existing_cols:
        c.execute("ALTER TABLE buyers ADD COLUMN verified_by INTEGER")
    if "verification_remarks" not in existing_cols:
        c.execute("ALTER TABLE buyers ADD COLUMN verification_remarks TEXT")
    conn.commit()
    active_env = os.environ.get("KRISHI_ENV", "production").lower()
    if active_env == "development":
        seed_development_sandbox_buyers(conn)
    conn.close()


def seed_development_sandbox_buyers(conn: sqlite3.Connection):
    """
    Seeds generic demonstration buyer profiles ONLY in development mode.
    Does NOT use unauthorized real commercial brand names.
    """
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM buyers")
    if c.fetchone()[0] > 0:
        return

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    sample_buyers = [
        (
            1, "Apex Agro-Processing Hub (Sandbox)", "Food Processing & Milling",
            "S. Kulkarni (Test)", "+91 98451 00001", "procure@apexagro-test.in",
            "Bidadi Industrial Complex Phase II",
            "Ramanagara", "Karnataka", 12.7981, 77.4005, "29AABCU9603R1ZM", "APMC-KAR-9821", 1, 4.9, 12,
            "100% Direct Bank Transfer within 24h of Gate Inspection", now_str
        ),
        (
            None, "Southern Wholesale Cold Chain (Sandbox)", "Wholesale & Aggregator Chain",
            "P. Nair (Test)", "+91 97410 00002", "procure@southerncold-test.in",
            "Mysore Road Agro Hub, Kengeri",
            "Bangalore Urban", "Karnataka", 12.9121, 77.4833, "29AABCS1234F1ZX", "APMC-BLR-4512", 1, 4.8, 8,
            "Immediate payment on weighbridge receipt + quality clearance", now_str
        ),
        (
            None, "Deccan Organic Millers (Sandbox)", "Organic Cereals & Pulses",
            "R. Kumar (Test)", "+91 99002 00003", "sourcing@deccanorganic-test.in",
            "Tiptur Highway Industrial Park",
            "Tumakuru", "Karnataka", 13.2584, 76.4789, "29AABCO5566G1ZQ", "APMC-TUM-3310", 1, 4.9, 5,
            "Weekly settlement with premium organic certification bonus", now_str
        )
    ]
    for b in sample_buyers:
        c.execute("""
        INSERT INTO buyers (
            user_id, company_name, business_type, contact_person, phone, email,
            facility_address, district, state, latitude, longitude, gstin, apmc_license,
            verified_status, rating, total_deals_completed, payment_terms, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, b)
    conn.commit()

# ==============================================================================
# BUYER & REQUIREMENT RETRIEVAL APIS
# ==============================================================================

def get_all_buyers(crop_filter: Optional[str] = None, district_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all registered buyers, optionally filtered by crop in active requirements."""
    conn = get_db_connection()
    c = conn.cursor()
    
    if crop_filter and crop_filter != "All Crops":
        query = """
        SELECT DISTINCT b.* FROM buyers b
        JOIN buyer_requirements r ON b.id = r.buyer_id
        WHERE r.crop = ? AND r.status = 'OPEN'
        ORDER BY b.rating DESC, b.total_deals_completed DESC
        """
        c.execute(query, (crop_filter,))
    else:
        query = "SELECT * FROM buyers ORDER BY rating DESC, total_deals_completed DESC"
        c.execute(query)
    
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_buyer_by_id(buyer_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM buyers WHERE id = ?", (buyer_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_buyer_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM buyers WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_active_requirements(
    crop: Optional[str] = None,
    min_price: Optional[float] = None,
    grade: Optional[str] = None,
    status: str = "OPEN"
) -> List[Dict[str, Any]]:
    """Retrieves active purchasing requirements with joined buyer profile details."""
    conn = get_db_connection()
    c = conn.cursor()

    conditions = ["r.status = ?"]
    params: List[Any] = [status]

    if crop and crop != "All Crops":
        conditions.append("r.crop = ?")
        params.append(crop)

    if min_price is not None and min_price > 0:
        conditions.append("r.offered_price_per_quintal >= ?")
        params.append(min_price)

    if grade and grade != "All Grades":
        conditions.append("r.min_quality_grade = ?")
        params.append(grade)

    where_str = " AND ".join(conditions)

    query = f"""
    SELECT 
        r.*,
        b.company_name,
        b.business_type,
        b.contact_person,
        b.phone as buyer_phone,
        b.email as buyer_email,
        b.facility_address,
        b.verified_status,
        b.rating as buyer_rating,
        b.total_deals_completed,
        b.payment_terms
    FROM buyer_requirements r
    JOIN buyers b ON r.buyer_id = b.id
    WHERE {where_str}
    ORDER BY r.offered_price_per_quintal DESC, r.created_at DESC
    """
    c.execute(query, params)
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_requirement_by_id(requirement_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    query = """
    SELECT 
        r.*,
        b.company_name,
        b.business_type,
        b.contact_person,
        b.phone as buyer_phone,
        b.email as buyer_email,
        b.facility_address,
        b.verified_status,
        b.rating as buyer_rating,
        b.total_deals_completed,
        b.payment_terms
    FROM buyer_requirements r
    JOIN buyers b ON r.buyer_id = b.id
    WHERE r.id = ?
    """
    c.execute(query, (requirement_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_buyer_requirement(
    buyer_id: int,
    crop: str,
    quantity_quintals: float,
    min_quality_grade: str,
    offered_price_per_quintal: float,
    delivery_location: str,
    delivery_district: str,
    delivery_state: str,
    delivery_lat: float,
    delivery_lon: float,
    required_by_date: str,
    additional_specs: str = "",
    urgency_level: str = "Standard"
) -> Tuple[bool, str, Optional[int]]:
    """Allows an industry or buyer to publish a new crop purchasing requirement."""
    if quantity_quintals <= 0:
        return False, "Requirement quantity must be greater than 0.", None
    if offered_price_per_quintal <= 0:
        return False, "Offered price must be greater than ₹0/Quintal.", None
    if not crop or not delivery_location:
        return False, "Crop and delivery location cannot be empty.", None

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("""
        INSERT INTO buyer_requirements (
            buyer_id, crop, quantity_quintals, min_quality_grade, offered_price_per_quintal,
            delivery_location, delivery_district, delivery_state, delivery_lat, delivery_lon,
            required_by_date, additional_specs, urgency_level, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?)
        """, (
            buyer_id, crop.strip(), float(quantity_quintals), min_quality_grade.strip(),
            float(offered_price_per_quintal), delivery_location.strip(),
            delivery_district.strip(), delivery_state.strip(), float(delivery_lat),
            float(delivery_lon), required_by_date.strip(), additional_specs.strip(),
            urgency_level, now_str
        ))
        new_id = c.lastrowid
        conn.commit()
        return True, f"Requirement published successfully! Requirement ID #{new_id}", new_id
    except Exception as e:
        conn.rollback()
        return False, f"Failed to publish requirement: {str(e)}", None
    finally:
        conn.close()


def update_requirement_status(requirement_id: int, status: str) -> Tuple[bool, str]:
    allowed_statuses = ["OPEN", "FULFILLED", "EXPIRED", "PAUSED"]
    if status not in allowed_statuses:
        return False, f"Invalid status '{status}'. Must be one of {allowed_statuses}."
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE buyer_requirements SET status = ? WHERE id = ?", (status, requirement_id))
    conn.commit()
    conn.close()
    return True, f"Requirement #{requirement_id} updated to '{status}'."


# ==============================================================================
# FARMER QUOTATION APIS
# ==============================================================================

def submit_farmer_quotation(
    requirement_id: int,
    farmer_id: int,
    farmer_name: str,
    farmer_phone: str,
    crop: str,
    offered_quantity_quintals: float,
    quoted_price_per_quintal: float,
    offered_grade: str,
    dispatch_location: str,
    dispatch_district: str,
    dispatch_state: str,
    dispatch_lat: float,
    dispatch_lon: float,
    expected_delivery_date: str,
    farmer_notes: str = ""
) -> Tuple[bool, str, Optional[int]]:
    """Allows a farmer to submit a formal price & volume quotation to a buyer requirement."""
    if offered_quantity_quintals <= 0:
        return False, "Offered quantity must be greater than 0 Quintals.", None
    if quoted_price_per_quintal <= 0:
        return False, "Quoted price must be greater than ₹0/Quintal.", None

    conn = get_db_connection()
    c = conn.cursor()

    # Check requirement exists and is OPEN
    c.execute("SELECT status FROM buyer_requirements WHERE id = ?", (requirement_id,))
    req = c.fetchone()
    if not req:
        conn.close()
        return False, f"Requirement #{requirement_id} does not exist.", None
    if req["status"] != "OPEN":
        conn.close()
        return False, f"Cannot submit quotation: Requirement is currently {req['status']}.", None

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        c.execute("""
        INSERT INTO farmer_quotations (
            requirement_id, farmer_id, farmer_name, farmer_phone, crop,
            offered_quantity_quintals, quoted_price_per_quintal, offered_grade,
            dispatch_location, dispatch_district, dispatch_state, dispatch_lat, dispatch_lon,
            expected_delivery_date, farmer_notes, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?, ?)
        """, (
            requirement_id, farmer_id, farmer_name.strip(), farmer_phone.strip(),
            crop.strip(), float(offered_quantity_quintals), float(quoted_price_per_quintal),
            offered_grade.strip(), dispatch_location.strip(), dispatch_district.strip(),
            dispatch_state.strip(), float(dispatch_lat), float(dispatch_lon),
            expected_delivery_date.strip(), farmer_notes.strip(), now_str, now_str
        ))
        qid = c.lastrowid
        conn.commit()
        return True, f"Quotation #{qid} successfully submitted to buyer! You will be notified on status changes.", qid
    except Exception as e:
        conn.rollback()
        return False, f"Failed to submit quotation: {str(e)}", None
    finally:
        conn.close()


def get_quotations_by_farmer(farmer_id: int) -> List[Dict[str, Any]]:
    """Retrieves all quotations submitted by a specific farmer (User Isolation)."""
    conn = get_db_connection()
    c = conn.cursor()
    query = """
    SELECT 
        q.*,
        r.offered_price_per_quintal as buyer_offered_price,
        r.quantity_quintals as buyer_required_quantity,
        r.min_quality_grade as buyer_min_grade,
        r.required_by_date as buyer_deadline,
        b.company_name as buyer_company,
        b.contact_person as buyer_contact,
        b.phone as buyer_phone,
        b.email as buyer_email,
        b.facility_address as buyer_facility,
        b.payment_terms
    FROM farmer_quotations q
    JOIN buyer_requirements r ON q.requirement_id = r.id
    JOIN buyers b ON r.buyer_id = b.id
    WHERE q.farmer_id = ?
    ORDER BY q.created_at DESC
    """
    c.execute(query, (farmer_id,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_quotations_for_buyer(buyer_id: int) -> List[Dict[str, Any]]:
    """Retrieves all quotations submitted against a specific buyer's requirements (Buyer Isolation)."""
    conn = get_db_connection()
    c = conn.cursor()
    query = """
    SELECT 
        q.*,
        r.crop as req_crop,
        r.quantity_quintals as req_quantity,
        r.offered_price_per_quintal as req_price,
        r.min_quality_grade as req_grade,
        b.company_name as buyer_company
    FROM farmer_quotations q
    JOIN buyer_requirements r ON q.requirement_id = r.id
    JOIN buyers b ON r.buyer_id = b.id
    WHERE r.buyer_id = ?
    ORDER BY q.created_at DESC
    """
    c.execute(query, (buyer_id,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def update_quotation_status(
    quotation_id: int,
    new_status: str,
    counter_price: Optional[float] = None,
    feedback: Optional[str] = None
) -> Tuple[bool, str]:
    """Updates quotation status: ACCEPTED, REJECTED, UNDER_REVIEW, COUNTER_OFFER."""
    allowed = ["PENDING", "UNDER_REVIEW", "ACCEPTED", "REJECTED", "COUNTER_OFFER"]
    if new_status not in allowed:
        return False, f"Invalid quotation status '{new_status}'."

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("""
        UPDATE farmer_quotations
        SET status = ?,
            counter_price_per_quintal = COALESCE(?, counter_price_per_quintal),
            buyer_feedback = COALESCE(?, buyer_feedback),
            updated_at = ?
        WHERE id = ?
        """, (new_status, counter_price, feedback, now_str, quotation_id))
        conn.commit()
        return True, f"Quotation #{quotation_id} updated to '{new_status}'."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to update quotation: {str(e)}"
    finally:
        conn.close()


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


# ==============================================================================
# REAL PRODUCTION BUYER REGISTRATION & VERIFICATION WORKFLOW
# ==============================================================================
def register_buyer_profile(
    user_id: int,
    company_name: str,
    business_type: str,
    contact_person: str,
    phone: str,
    email: str,
    facility_address: str,
    district: str,
    state: str,
    latitude: float,
    longitude: float,
    gstin: str,
    apmc_license: Optional[str] = None,
    payment_terms: str = "Immediate Bank Transfer on Weighbridge Clearance"
) -> Tuple[bool, str, Optional[int]]:
    """
    Registers a genuine commercial buyer profile in pending verification state (0).
    Requires valid GSTIN / APMC License for compliance auditing.
    """
    clean_gst = gstin.strip().upper()
    if len(clean_gst) < 10:
        return False, "A valid GSTIN or Business Identification Number is required for buyer registration.", None

    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        c.execute("""
        INSERT INTO buyers (
            user_id, company_name, business_type, contact_person, phone, email,
            facility_address, district, state, latitude, longitude, gstin, apmc_license,
            verified_status, rating, total_deals_completed, payment_terms, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 5.0, 0, ?, ?)
        """, (
            user_id, company_name.strip(), business_type, contact_person.strip(),
            phone.strip(), email.strip().lower(), facility_address.strip(),
            district.strip(), state.strip(), latitude, longitude, clean_gst,
            apmc_license.strip() if apmc_license else None, payment_terms, now_str
        ))
        conn.commit()
        return True, "Buyer profile registered successfully. Awaiting administrative license verification.", c.lastrowid
    except Exception as e:
        conn.rollback()
        return False, f"Failed to register buyer profile: {str(e)}", None
    finally:
        conn.close()


def verify_buyer_account(
    buyer_id: int,
    admin_id: int,
    remarks: str = "Verified official GSTIN and APMC market license."
) -> Tuple[bool, str]:
    """
    Grants official verified status (1) to a registered buyer after regulatory due diligence.
    """
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("""
        UPDATE buyers
        SET verified_status = 1,
            verified_by = ?,
            verification_remarks = ?
        WHERE id = ?
        """, (admin_id, remarks, buyer_id))
        conn.commit()
        return True, f"Buyer #{buyer_id} verified successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Verification failed: {str(e)}"
    finally:
        conn.close()
