import os
import re

print("=== SQL INJECTION & SECURITY QUERY AUDIT ===")

modules = [os.path.join("modules", f) for f in os.listdir("modules") if f.endswith(".py")]
modules.append("app.py")

sql_risks = []

for mod in modules:
    with open(mod, "r", encoding="utf-8") as f:
        code = f.read()
    
    lines = code.split("\n")
    for idx, line in enumerate(lines):
        # Look for f-strings or % formatting inside execute( or query(
        if re.search(r'\.(execute|execute_sql|query)\s*\(\s*f["\']', line) or re.search(r'\.(execute|execute_sql|query)\s*\(\s*["\'].*%s', line):
            # Check if it has where clause interpolation
            sql_risks.append((mod, idx + 1, line.strip()))

print(f"Total potential dynamic query points: {len(sql_risks)}")
for r in sql_risks:
    print(f"  {r[0]}:{r[1]} -> {r[2]}")
