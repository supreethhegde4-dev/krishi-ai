with open("modules/auth_db.py", "r", encoding="utf-8") as f:
    code = f.read()

# Find seed_development_accounts
fn_start = code.find("def seed_development_accounts(conn: sqlite3.Connection):")
dpdp_start = code.find("# ==============================================================================\n# DPDP ACT 2023 COMPLIANCE", fn_start)

seed_func = code[fn_start:dpdp_start]
# Remove it from the bottom
code_clean = code[:fn_start] + code[dpdp_start:]

# Insert it before init_db
init_db_idx = code_clean.find("def init_db")
code_fixed = code_clean[:init_db_idx] + seed_func + "\n\n" + code_clean[init_db_idx:]

with open("modules/auth_db.py", "w", encoding="utf-8") as f:
    f.write(code_fixed)

print("Fixed definition order in modules/auth_db.py")
