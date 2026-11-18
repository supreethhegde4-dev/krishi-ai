import os
import glob
import subprocess

print("=== ACCURATE TEST DISCOVERY & INVENTORY ===")
test_files = sorted(glob.glob("tests/test_*.py"))
for tf in test_files:
    with open(tf, "r", encoding="utf-8") as f:
        code = f.read()
    
    # Check if unittest based
    has_unittest = "unittest.TestCase" in code
    # Count def test_
    methods = [line.strip() for line in code.split("\n") if line.strip().startswith("def test_")]
    # Count print([Test
    printed_tests = [line.strip() for line in code.split("\n") if "[Test " in line and "PASS" in line or "[Test " in line and "..." in line]
    
    print(f"File: {tf}")
    print(f"  - Framework: {'unittest.TestCase' if has_unittest else 'Procedural Script'}")
    print(f"  - def test_ methods count: {len(methods)}")
    print(f"  - Procedural test steps count: {len(printed_tests)//2 if printed_tests else 0}")
