"""
test_phase8_integration.py
--------------------------
Directly tests all 11 user-specified canonical integration endpoints via TestClient.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

canonical_endpoints = [
    ("GET",  "/api/metadata", None),
    ("GET",  "/api/analyze/hle?location=Global&year=2023&sex=both", None),
    ("GET",  "/api/analyze/gender-gap?year=2023", None),
    ("GET",  "/api/analyze/trends?grouping=sdi", None),
    ("GET",  "/api/analyze/regional-comparison?grouping=sdi&year=2023", None),
    ("GET",  "/api/ml/clusters?k=3", None),
    ("GET",  "/api/global-burden/daly?level=2&top_n=5", None),
    ("GET",  "/api/global-burden/yld?level=2&top_n=5", None),
    ("POST", "/api/plan", {"goal_id": "ANALYZE_HEALTH_INEQUALITY"}),
    ("GET",  "/api/recommendations?low_hle_threshold=56.9", None),
    ("GET",  "/api/reports", None),
]

print("=" * 65)
print("TESTING PHASE 8 CANONICAL INTEGRATION ENDPOINTS")
print("=" * 65)

all_passed = True
for method, path, payload in canonical_endpoints:
    if method == "GET":
        resp = client.get(path)
    else:
        resp = client.post(path, json=payload)

    status = resp.status_code
    passed = status == 200
    if not passed:
        all_passed = False
        print(f"[FAIL] {method:4s} {path} -> {status}")
        print(f"       Response: {resp.text[:200]}")
    else:
        # Check that response body has valid data
        data = resp.json()
        keys_summary = list(data.keys()) if isinstance(data, dict) else f"list({len(data)})"
        print(f"[PASS] {method:4s} {path} -> 200 OK | {keys_summary}")

assert all_passed, "Some endpoints failed!"
print("\nALL 11 CANONICAL INTEGRATION ENDPOINTS TESTED AND VERIFIED SUCCESSFULLY!")
