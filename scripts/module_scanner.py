import os
import re

modules = os.listdir("modules")
print(f"Total files in modules/: {len(modules)}")

findings = []

for m in sorted(modules):
    if not m.endswith(".py"):
        continue
    path = os.path.join("modules", m)
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    
    # Check for demo/mock/synthetic keywords
    demo_hits = re.findall(r'(demo|mock|synthetic|sample|seed|fake|dummy|fallback|heuristic)', code, re.IGNORECASE)
    # Check for hardcoded brands or names
    brand_hits = re.findall(r'(itc|bigbasket|haldiram|akshayakalpa|safal|godrej|keventer)', code, re.IGNORECASE)
    # Check for accuracy claims
    claim_hits = re.findall(r'(\d+\.?\d*%\s*(accuracy|confidence|precision|recall|oob)|r\^?2\s*(>|=|\s*of)?\s*\d+\.?\d*)', code, re.IGNORECASE)
    
    lines = code.split("\n")
    findings.append({
        "module": m,
        "lines": len(lines),
        "demo_terms_count": len(demo_hits),
        "brands_count": len(brand_hits),
        "claims": [c[0] for c in claim_hits],
        "has_sql": "sqlite" in code.lower() or "execute(" in code,
        "has_network": "requests." in code or "urllib" in code
    })

print(f"{'Module':32} | {'Lines':6} | {'Demo terms':10} | {'Brands':6} | Claims")
print("-" * 80)
for f in findings:
    claims_str = ", ".join(f["claims"][:2]) if f["claims"] else "-"
    print(f"{f['module']:32} | {f['lines']:6} | {f['demo_terms_count']:10} | {f['brands_count']:6} | {claims_str}")
