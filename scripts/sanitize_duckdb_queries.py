import os
import re

def sanitize_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    # Add sanitizer helper if not present
    helper = """
import re

def _sanitize_sql_param(val):
    if val is None:
        return ""
    # Whitelist alphanumeric, spaces, dashes, dots, parentheses, slashes
    clean = re.sub(r"[^\\w\\s\\-\\(\\)\\.\\/]", "", str(val)).strip()
    return clean
"""
    if "_sanitize_sql_param" not in code:
        # insert after imports
        import_end = code.find("PARQUET_GLOB")
        if import_end != -1:
            code = code[:import_end] + helper + "\n" + code[import_end:]

    # Replace where_clauses assignments with sanitized params
    code = re.sub(
        r"where_clauses\s*=\s*\[f[\"']Commodity = '\{commodity\}'[\"'],\s*[\"']Modal_Price > 0[\"']\]",
        "clean_comm = _sanitize_sql_param(commodity)\n        where_clauses = [f\"Commodity = '{clean_comm}'\", \"Modal_Price > 0\"]",
        code
    )
    code = re.sub(
        r"where_clauses\.append\(f[\"']State = '\{state\}'[\"']\)",
        "clean_state = _sanitize_sql_param(state)\n            where_clauses.append(f\"State = '{clean_state}'\")",
        code
    )
    code = re.sub(
        r"where_clauses\.append\(f[\"']District = '\{district\}'[\"']\)",
        "clean_dist = _sanitize_sql_param(district)\n            where_clauses.append(f\"District = '{clean_dist}'\")",
        code
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Sanitized DuckDB query inputs in {filepath}")

sanitize_file("modules/historical_intelligence.py")
sanitize_file("modules/trend_shift_detector.py")
