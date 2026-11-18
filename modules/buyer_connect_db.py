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


def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_buyer_connect_tables():
    """Initializes tables for buyers, industry requirements, and quotations."""
    conn = get_db_connection()
    c = conn.cursor()

    # 1. Registered Buyers & Industries
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
        verified_status INTEGER NOT NULL DEFAULT 1,
        rating REAL NOT NULL DEFAULT 4.8,
        total_deals_completed INTEGER NOT NULL DEFAULT 10,
        payment_terms TEXT NOT NULL DEFAULT 'Within 24 Hours of Delivery / Quality Check',
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
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

    conn.commit()
    seed_verified_buyers_and_requirements(conn)
    conn.close()


def seed_verified_buyers_and_requirements(conn: sqlite3.Connection):
    """Seeds verified, realistic Indian agro-processors, mills, and retail aggregators."""
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM buyers")
    if c.fetchone()[0] > 0:
        return

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    today = datetime.date.today()

    # Seeded Buyer Profiles (Centered around South & Central India with realistic logistics hubs)
    sample_buyers = [
        (
            1, "ITC Agri-Business Division", "Food Processing & FMCG",
            "Sanjay Kulkarni", "+91 98451 22334", "sanjay.k@itcagri.in",
            "ITC Food Processing Plant, Bidadi Industrial Area Phase II",
            "Ramanagara", "Karnataka", 12.7981, 77.4005, 1, 4.9, 48,
            "100% Direct Bank Transfer within 24h of Gate Inspection", now_str
        ),
        (
            None, "Nilgiris Fresh Agro Foods Ltd", "Wholesale & Supermarket Chain",
            "Praveen Nair", "+91 97410 88991", "procure@nilgirisfresh.com",
            "Nilgiris Central Cold Hub, Mysore Road, Kengeri",
            "Bangalore Urban", "Karnataka", 12.9121, 77.4833, 1, 4.8, 32,
            "Immediate payment on weighbridge receipt + quality clearance", now_str
        ),
        (
            None, "Haldiram Snacks Procurement Unit", "Snacks & Savory Processing",
            "Rajesh Agarwal", "+91 94221 66770", "procure.south@haldirams.biz",
            "Haldiram Southern Logistics Hub, Electronic City Phase 2",
            "Bangalore Urban", "Karnataka", 12.8399, 77.6770, 1, 4.7, 56,
            "RTGS within 48 Hours of Lab Grade Certification", now_str
        ),
        (
            None, "Akshayakalpa Organic Foods", "Organic Dairy & Farm Produce",
            "Dr. Shashi Kumar", "+91 99002 44551", "sourcing@akshayakalpa.org",
            "Akshayakalpa Processing Campus, Tiptur Highway",
            "Tumakuru", "Karnataka", 13.2584, 76.4789, 1, 4.9, 29,
            "Weekly settlement with premium organic certification bonus", now_str
        ),
        (
            None, "BigBasket Fresh Sourcing Logistics", "E-Commerce Fresh Aggregator",
            "Kavitha Swaminathan", "+91 98801 33445", "farmer.connect@bigbasket.com",
            "BigBasket Regional Distribution Center, Hoskote Industrial Area",
            "Bangalore Rural", "Karnataka", 13.0722, 77.7983, 1, 4.8, 74,
            "T+1 settlement via UPI / Bank IMPS upon grading", now_str
        ),
        (
            None, "Mother Dairy Fruit & Vegetable (Safal)", "Horticultural Processing Hub",
            "Maheshwar Reddy", "+91 98112 77889", "horticulture.blr@safal.in",
            "Safal Agro Park, Doddaballapur Integrated Food Complex",
            "Bangalore Rural", "Karnataka", 13.2924, 77.5417, 1, 4.7, 61,
            "Direct NEFT payment on official APMC weigh slip clearance", now_str
        ),
        (
            None, "Godrej Agrovet Procurement Center", "Feed & Agricultural Processing",
            "Venkatesh Prasad", "+91 96200 11223", "v.prasad@godrejagrovet.com",
            "Godrej Processing Facility, SIPCOT Industrial Park, Hosur",
            "Krishnagiri", "Tamil Nadu", 12.7409, 77.8253, 1, 4.6, 38,
            "Net 3 days bank settlement with transparent digital moisture test", now_str
        ),
        (
            None, "Keventer Agro Processing Ltd", "Beverages & Puree Processing",
            "Aniruddha Bose", "+91 93310 55442", "procurement@keventeragro.com",
            "Keventer Food Park, Chittoor Highway Bypass",
            "Chittoor", "Andhra Pradesh", 13.2172, 79.1003, 1, 4.8, 22,
            "Immediate gate pass token with RTGS payment within 24h", now_str
        )
    ]

    c.executemany("""
    INSERT INTO buyers (
        user_id, company_name, business_type, contact_person, phone, email,
        facility_address, district, state, latitude, longitude,
        verified_status, rating, total_deals_completed, payment_terms, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_buyers)

    # Fetch buyer IDs
    c.execute("SELECT id, company_name, district, state, latitude, longitude FROM buyers")
    buyer_map = {row["company_name"]: row for row in c.fetchall()}

    # Sample Industry Requirements
    sample_reqs = [
        # 1. ITC - Tomato Puree & Ketchup Grade
        (
            buyer_map["ITC Agri-Business Division"]["id"],
            "Tomato", 250.0, "Grade A (Premium)", 2400.0,
            "ITC Food Processing Plant, Gate 3, Bidadi Phase II",
            "Ramanagara", "Karnataka", 12.7981, 77.4005,
            (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
            "Firm ripe tomatoes, TSS Brix > 4.5, uniform red color, zero fruit borer damage. Crates supplied by ITC at delivery bay.",
            "Urgent", "OPEN", now_str
        ),
        # 2. Nilgiris - Table Fresh Tomato
        (
            buyer_map["Nilgiris Fresh Agro Foods Ltd"]["id"],
            "Tomato", 80.0, "Grade A (Premium)", 2550.0,
            "Nilgiris Distribution Center, Kengeri",
            "Bangalore Urban", "Karnataka", 12.9121, 77.4833,
            (today + datetime.timedelta(days=4)).strftime("%Y-%m-%d"),
            "Semi-ripe to ripe table quality. Minimum diameter 50mm, no mechanical bruising. Packed in 20kg plastic crates.",
            "Standard", "OPEN", now_str
        ),
        # 3. BigBasket - Daily Tomato Sourcing
        (
            buyer_map["BigBasket Fresh Sourcing Logistics"]["id"],
            "Tomato", 120.0, "Grade B (Standard)", 2200.0,
            "BigBasket DC, Hoskote Hub",
            "Bangalore Rural", "Karnataka", 13.0722, 77.7983,
            (today + datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
            "Standard hybrid tomatoes. Brix > 3.8. Sorting on unloading belt with instant digital payment.",
            "Urgent", "OPEN", now_str
        ),
        # 4. Haldiram - Chip Grade Potato
        (
            buyer_map["Haldiram Snacks Procurement Unit"]["id"],
            "Potato", 350.0, "Grade A (Premium)", 2100.0,
            "Haldiram Southern Logistics Hub, Electronic City",
            "Bangalore Urban", "Karnataka", 12.8399, 77.6770,
            (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"),
            "Processing varieties (Kufri Chipsona / Atlantic). Sugar < 0.1%, specific gravity > 1.080, dry matter > 20%. Size 45-75mm.",
            "Contract Season", "OPEN", now_str
        ),
        # 5. Mother Dairy / Safal - Fresh Potato
        (
            buyer_map["Mother Dairy Fruit & Vegetable (Safal)"]["id"],
            "Potato", 150.0, "Grade B (Standard)", 1850.0,
            "Safal Agro Park, Doddaballapur",
            "Bangalore Rural", "Karnataka", 13.2924, 77.5417,
            (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"),
            "Firm potatoes, free from greening and internal browning. Size > 40mm. 50kg ventilated gunny bags.",
            "Standard", "OPEN", now_str
        ),
        # 6. Nilgiris - Nashik/Karnataka Onion
        (
            buyer_map["Nilgiris Fresh Agro Foods Ltd"]["id"],
            "Onion", 180.0, "Grade A (Premium)", 2650.0,
            "Nilgiris Central Cold Hub, Kengeri",
            "Bangalore Urban", "Karnataka", 12.9121, 77.4833,
            (today + datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
            "Medium-large red onions (50-65mm). Well-cured thin neck, dry papery scales, zero sprouting or mold.",
            "Urgent", "OPEN", now_str
        ),
        # 7. BigBasket - Red Onion
        (
            buyer_map["BigBasket Fresh Sourcing Logistics"]["id"],
            "Onion", 200.0, "Grade B (Standard)", 2400.0,
            "BigBasket Regional DC, Hoskote",
            "Bangalore Rural", "Karnataka", 13.0722, 77.7983,
            (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
            "Grade B standard onions. Moisture content < 14%. Immediate gate inspection.",
            "Standard", "OPEN", now_str
        ),
        # 8. Akshayakalpa - Certified Organic Tomato
        (
            buyer_map["Akshayakalpa Organic Foods"]["id"],
            "Tomato", 40.0, "Certified Organic", 3200.0,
            "Akshayakalpa Processing Campus, Tiptur",
            "Tumakuru", "Karnataka", 13.2584, 76.4789,
            (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"),
            "100% NPOP / Jaivik Bharat certified organic. Zero chemical residue test mandatory before intake. Premium price paid.",
            "Standard", "OPEN", now_str
        ),
        # 9. Godrej Agrovet - Feed Maize
        (
            buyer_map["Godrej Agrovet Procurement Center"]["id"],
            "Maize", 500.0, "Grade B (Standard)", 2250.0,
            "Godrej Facility, SIPCOT Hosur",
            "Krishnagiri", "Tamil Nadu", 12.7409, 77.8253,
            (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"),
            "Yellow feed maize. Moisture < 12.5%, foreign matter < 1%, aflatoxin < 20 ppb. Bulk tanker or 50kg bags accepted.",
            "Contract Season", "OPEN", now_str
        ),
        # 10. Keventer Agro - Fresh Banana (Robusta / Yelakki)
        (
            buyer_map["Keventer Agro Processing Ltd"]["id"],
            "Banana", 200.0, "Grade A (Premium)", 1950.0,
            "Keventer Food Park, Chittoor Highway",
            "Chittoor", "Andhra Pradesh", 13.2172, 79.1003,
            (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
            "Robusta / Cavendish green mature banana for ripening chambers. 3/4 full, clean bunches without latex staining.",
            "Standard", "OPEN", now_str
        ),
        # 11. Mother Dairy Safal - Fresh Cabbage & Cauliflower
        (
            buyer_map["Mother Dairy Fruit & Vegetable (Safal)"]["id"],
            "Cabbage", 100.0, "Grade A (Premium)", 1450.0,
            "Safal Agro Park, Doddaballapur",
            "Bangalore Rural", "Karnataka", 13.2924, 77.5417,
            (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
            "Solid green heads, outer wrapper leaves intact, 1.0 - 1.8 kg head size. Unsprayed in final 10 days.",
            "Urgent", "OPEN", now_str
        ),
        # 12. ITC Agri-Business - Premium Milling Wheat
        (
            buyer_map["ITC Agri-Business Division"]["id"],
            "Wheat", 450.0, "Grade A (Premium)", 2850.0,
            "ITC Aashirvaad Milling Unit, Bidadi Industrial Area",
            "Ramanagara", "Karnataka", 12.7981, 77.4005,
            (today + datetime.timedelta(days=15)).strftime("%Y-%m-%d"),
            "Lok-1 or Sharbati hard amber durum wheat. Gluten > 11%, moisture < 11%, zero weeviled grains. Instant laboratory test.",
            "Contract Season", "OPEN", now_str
        )
    ]

    c.executemany("""
    INSERT INTO buyer_requirements (
        buyer_id, crop, quantity_quintals, min_quality_grade, offered_price_per_quintal,
        delivery_location, delivery_district, delivery_state, delivery_lat, delivery_lon,
        required_by_date, additional_specs, urgency_level, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_reqs)

    # Seed Sample Farmer Quotations to demonstrate full status workflow
    c.execute("SELECT id FROM buyer_requirements WHERE crop = 'Tomato' LIMIT 2")
    req_rows = c.fetchall()
    if req_rows:
        req1_id = req_rows[0][0]
        req2_id = req_rows[1][0] if len(req_rows) > 1 else req1_id

        past_date = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        c.execute("""
        INSERT INTO farmer_quotations (
            requirement_id, farmer_id, farmer_name, farmer_phone, crop,
            offered_quantity_quintals, quoted_price_per_quintal, offered_grade,
            dispatch_location, dispatch_district, dispatch_state, dispatch_lat, dispatch_lon,
            expected_delivery_date, farmer_notes, status, counter_price_per_quintal, buyer_feedback,
            created_at, updated_at
        ) VALUES (
            ?, 1, 'Ramesh Gowda', '+91 98450 12345', 'Tomato',
            45.0, 2450.0, 'Grade A (Premium)',
            'Ramanagara Rural Holding', 'Ramanagara', 'Karnataka', 12.7209, 77.2799,
            ?, 'Fresh morning harvest. Tomatoes harvested in semi-ripe condition, sorted in plastic crates.',
            'ACCEPTED', NULL, 'Quotation approved. Please dispatch batch to Bidadi Gate 3 between 7:00 AM and 11:00 AM.',
            ?, ?
        )
        """, (req1_id, (today + datetime.timedelta(days=2)).strftime("%Y-%m-%d"), past_date, now_str))

        c.execute("""
        INSERT INTO farmer_quotations (
            requirement_id, farmer_id, farmer_name, farmer_phone, crop,
            offered_quantity_quintals, quoted_price_per_quintal, offered_grade,
            dispatch_location, dispatch_district, dispatch_state, dispatch_lat, dispatch_lon,
            expected_delivery_date, farmer_notes, status, counter_price_per_quintal, buyer_feedback,
            created_at, updated_at
        ) VALUES (
            ?, 1, 'Ramesh Gowda', '+91 98450 12345', 'Tomato',
            30.0, 2600.0, 'Grade A (Premium)',
            'Ramanagara Rural Holding', 'Ramanagara', 'Karnataka', 12.7209, 77.2799,
            ?, 'Batch available from polyhouse drip block.',
            'UNDER_REVIEW', NULL, 'Under physical sample review by QC Officer.',
            ?, ?
        )
        """, (req2_id, (today + datetime.timedelta(days=3)).strftime("%Y-%m-%d"), now_str, now_str))

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
