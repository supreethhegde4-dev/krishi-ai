"""
RBAC and Security Hardening Test Suite for Krishi AI.
Tests role escalation defense, administrative provisioning, buyer verification RBAC,
conflict of interest enforcement, and inactive admin revocation.
"""
import unittest
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.db_engine import get_db_connection
from modules.auth_db import (
    register_user,
    provision_admin_user,
    provision_inspector_user,
    PUBLIC_ROLES,
    PRIVILEGED_ROLES
)
from modules.buyer_connect_db import (
    verify_buyer_account,
    verify_crop_inspection
)


class TestRBACSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Locates or sets up active test users with different roles."""
        conn = get_db_connection()
        c = conn.cursor()
        
        # 1. Active Admin
        c.execute("SELECT id, role, is_active FROM users WHERE role = 'admin' AND is_active = 1 LIMIT 1;")
        admin_row = c.fetchone()
        if not admin_row:
            c.execute("""
                INSERT INTO users (email, password_hash, full_name, role, is_active, created_at)
                VALUES ('rbac_admin_test@krishiai.org', 'testhash', 'RBAC Admin Test', 'admin', 1, CURRENT_TIMESTAMP)
            """)
            conn.commit()
            cls.admin_id = c.lastrowid
        else:
            cls.admin_id = admin_row["id"] if hasattr(admin_row, "__getitem__") else admin_row[0]

        # 2. Inactive Admin
        c.execute("SELECT id FROM users WHERE role = 'admin' AND is_active = 0 LIMIT 1;")
        inact_row = c.fetchone()
        if not inact_row:
            c.execute("""
                INSERT INTO users (email, password_hash, full_name, role, is_active, created_at)
                VALUES ('rbac_inactive_admin@krishiai.org', 'testhash', 'Inactive Admin', 'admin', 0, CURRENT_TIMESTAMP)
            """)
            conn.commit()
            cls.inactive_admin_id = c.lastrowid
        else:
            cls.inactive_admin_id = inact_row["id"] if hasattr(inact_row, "__getitem__") else inact_row[0]

        # 3. Active Farmer
        c.execute("SELECT id FROM users WHERE role = 'farmer' AND is_active = 1 LIMIT 1;")
        farmer_row = c.fetchone()
        cls.farmer_id = farmer_row["id"] if hasattr(farmer_row, "__getitem__") else farmer_row[0]

        # 4. Active Buyer
        c.execute("SELECT id FROM users WHERE role = 'buyer' AND is_active = 1 LIMIT 1;")
        buyer_row = c.fetchone()
        if not buyer_row:
            c.execute("""
                INSERT INTO users (email, password_hash, full_name, role, is_active, created_at)
                VALUES ('rbac_buyer_test@krishiai.org', 'testhash', 'RBAC Buyer Test', 'buyer', 1, CURRENT_TIMESTAMP)
            """)
            conn.commit()
            cls.buyer_id = c.lastrowid
        else:
            cls.buyer_id = buyer_row["id"] if hasattr(buyer_row, "__getitem__") else buyer_row[0]

        # 5. Active Inspector
        c.execute("SELECT id FROM users WHERE role = 'inspector' AND is_active = 1 LIMIT 1;")
        insp_row = c.fetchone()
        if not insp_row:
            c.execute("""
                INSERT INTO users (email, password_hash, full_name, role, is_active, created_at)
                VALUES ('rbac_inspector_test@krishiai.org', 'testhash', 'RBAC Inspector Test', 'inspector', 1, CURRENT_TIMESTAMP)
            """)
            conn.commit()
            cls.inspector_id = c.lastrowid
        else:
            cls.inspector_id = insp_row["id"] if hasattr(insp_row, "__getitem__") else insp_row[0]

        # 6. Target Unverified Buyer Record
        c.execute("SELECT id FROM buyers WHERE verified_status = 0 LIMIT 1;")
        unv_buyer = c.fetchone()
        if not unv_buyer:
            c.execute("""
                INSERT INTO buyers (user_id, company_name, gst_number, verified_status, rating, total_deals_completed)
                VALUES (?, 'Unverified Test Corp', '29AABCU9603R1Z2', 0, 0.0, 0)
            """, (cls.buyer_id,))
            conn.commit()
            cls.target_buyer_id = c.lastrowid
        else:
            cls.target_buyer_id = unv_buyer["id"] if hasattr(unv_buyer, "__getitem__") else unv_buyer[0]

        # 7. Crop Inspection Record for testing self-inspection
        c.execute("SELECT id, farmer_id FROM crop_inspections LIMIT 1;")
        crop_insp = c.fetchone()
        if crop_insp:
            cls.test_inspection_id = crop_insp["id"] if hasattr(crop_insp, "__getitem__") else crop_insp[0]
            cls.inspection_farmer_id = crop_insp["farmer_id"] if hasattr(crop_insp, "__getitem__") else crop_insp[1]
        else:
            cls.test_inspection_id = 1
            cls.inspection_farmer_id = cls.farmer_id

        conn.close()

    def test_01_public_registration_blocks_admin(self):
        """Verifies that public registration rejects self-assignment of 'admin' role."""
        ok, msg = register_user(
            full_name="Attacker Admin",
            email="attacker_admin@malicious.com",
            password="Password123",
            role="admin"
        )
        self.assertFalse(ok)
        self.assertIn("cannot be self-registered", msg)

    def test_02_public_registration_blocks_inspector(self):
        """Verifies that public registration rejects self-assignment of 'inspector' role."""
        ok, msg = register_user(
            full_name="Attacker Inspector",
            email="attacker_inspector@malicious.com",
            password="Password123",
            role="inspector"
        )
        self.assertFalse(ok)
        self.assertIn("cannot be self-registered", msg)

    def test_03_farmer_cannot_verify_buyer(self):
        """Verifies that a farmer cannot verify a buyer account."""
        ok, msg = verify_buyer_account(self.target_buyer_id, admin_id=self.farmer_id)
        self.assertFalse(ok)
        self.assertIn("Unauthorized", msg)

    def test_04_buyer_cannot_verify_buyer(self):
        """Verifies that a buyer cannot verify another buyer account."""
        ok, msg = verify_buyer_account(self.target_buyer_id, admin_id=self.buyer_id)
        self.assertFalse(ok)
        self.assertIn("Unauthorized", msg)

    def test_05_inactive_admin_cannot_verify_buyer(self):
        """Verifies that an inactive administrator cannot perform buyer verification."""
        ok, msg = verify_buyer_account(self.target_buyer_id, admin_id=self.inactive_admin_id)
        self.assertFalse(ok)
        self.assertIn("Unauthorized", msg)

    def test_06_unauthenticated_user_cannot_verify_buyer(self):
        """Verifies that an invalid/non-existent user ID cannot verify a buyer."""
        ok, msg = verify_buyer_account(self.target_buyer_id, admin_id=9999999)
        self.assertFalse(ok)
        self.assertIn("not found", msg)

    def test_07_inspector_cannot_provision_admin(self):
        """Verifies that an inspector cannot authorize or provision an administrator."""
        ok, msg = provision_admin_user(
            full_name="Unauthorized Admin",
            email="fake_admin@krishiai.org",
            password="AdminPassword123",
            authorized_by_admin_id=self.inspector_id
        )
        self.assertFalse(ok)
        self.assertIn("Unauthorized", msg)

    def test_08_farmer_cannot_verify_own_produce(self):
        """Verifies that a producer cannot act as inspector to certify their own crop batch."""
        ok, msg = verify_crop_inspection(
            inspection_id=self.test_inspection_id,
            inspector_id=self.inspection_farmer_id,  # Caller is the owner of the crop
            inspector_name="Self Certifier",
            inspector_grade="Grade A+",
            brix_reading=14.5,
            size_caliper_mm=75.0,
            defect_percent=0.5,
            inspection_notes="Self certified produce."
        )
        self.assertFalse(ok)
        self.assertTrue("Conflict of interest" in msg or "Unauthorized" in msg)


if __name__ == "__main__":
    unittest.main()
