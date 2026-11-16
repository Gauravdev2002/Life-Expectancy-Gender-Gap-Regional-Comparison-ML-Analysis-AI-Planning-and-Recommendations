"""
test_api_endpoints.py
---------------------
Tests all FastAPI endpoints end-to-end using TestClient.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

endpoints = [
    ("GET", "/api/health/"),
    ("GET", "/api/overview/"),
    ("GET", "/api/analytics/hle/locations"),
    ("GET", "/api/analytics/hle/trend?location=Global"),
    ("GET", "/api/analytics/regional/groupings"),
    ("GET", "/api/analytics/regional/comparison?grouping=sdi&year=2023"),
    ("GET", "/api/ml/clustering?k=3"),
    ("GET", "/api/planning/goals"),
    ("POST", "/api/planning/plan", {"goal_id": "ANALYZE_HEALTH_INEQUALITY"}),
    ("GET", "/api/analytics/gender/overview?year=2023"),
    ("GET", "/api/analytics/gender/rankings?year=2023&n=5"),
    ("GET", "/api/analytics/gender/scatter?year=2023&max_points=20"),
    ("GET", "/api/analytics/gender/table?year=2023&page=1&page_size=5"),
    ("GET", "/api/analytics/disease/overview"),
    ("GET", "/api/analytics/disease/breakdown"),
    ("GET", "/api/analytics/disease/top-causes?metric=daly&level=2&n=5"),
    ("GET", "/api/analytics/disease/top-causes?metric=yld&level=2&n=5"),
    ("GET", "/api/analytics/disease/comparison"),
    ("GET", "/api/analytics/disease/table?metric=daly&level=2&page=1&page_size=5"),
    ("GET", "/api/reports/recommendations"),
    ("GET", "/api/reports/full"),
    ("GET", "/api/reports/download/markdown"),
    ("GET", "/api/reports/download/html"),
]

print("=" * 60)
print("TESTING ALL FASTAPI ENDPOINTS")
print("=" * 60)

for method, path, *body in endpoints:
    if method == "GET":
        resp = client.get(path)
    else:
        resp = client.post(path, json=body[0] if body else {})
    status = resp.status_code
    passed = "PASS" if status == 200 else "FAIL"
    print(f"[{passed}] {method} {path} -> {status}")
    assert status == 200, f"Endpoint {path} failed with {status}: {resp.text}"

print("\nALL 19 API ENDPOINTS RESPONDED WITH STATUS 200 OK!")
