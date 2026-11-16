"""
test_master_suite.py
--------------------
Phase 9 Master Automated Testing Suite.
Executes systematic quality assurance across all 12 analytical, ML, AI, and API layers.
"""

import sys
import io
import time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi.testclient import TestClient

print("=" * 75)
print("  MASTER QUALITY ASSURANCE & VERIFICATION TEST SUITE (PHASE 9)")
print("=" * 75)
start_all = time.time()

passed_count = 0
failed_count = 0

def check(name: str, condition: bool, details: str = ""):
    global passed_count, failed_count
    if condition:
        passed_count += 1
        print(f"  [PASS] {name} {details}")
    else:
        failed_count += 1
        print(f"  [FAIL] {name} {details}")

# ===========================================================================
# 1. Excel Dataset Loading & Integrity
# ===========================================================================
print("\n--- TEST SECTION 1: EXCEL DATASET LOADING ---")
from data.loader import load_s9_long, load_s10_raw, load_s11_raw

raw_s9 = load_s9_long()
check("S9 Raw Load", len(raw_s9) > 0, f"({len(raw_s9)} records loaded)")
check("S9 Multi-Year Columns", all(c in raw_s9.columns for c in ["location", "sex", "year", "hle_mean"]), "Columns intact")

raw_s10 = load_s10_raw()
check("S10 Raw Load (DALY)", len(raw_s10) > 0, f"({len(raw_s10)} rows loaded)")

raw_s11 = load_s11_raw()
check("S11 Raw Load (YLD)", len(raw_s11) > 0, f"({len(raw_s11)} rows loaded)")

# ===========================================================================
# 2. Data Cleaning & Missing Value Handling
# ===========================================================================
print("\n--- TEST SECTION 2: DATA CLEANING & VALIDATION ---")
from data.pipeline import get_s9, get_s10, get_s11

s9 = get_s9()
check("S9 Cleaned Structure", s9["location"].nunique() >= 700, f"({s9['location'].nunique()} unique locations)")
check("S9 Footnotes Filtered", not any(s9["location"].str.startswith("*")), "No leading asterisks/footnotes")
check("S9 Uncertainty Bounds", "hle_lower" in s9.columns and "hle_upper" in s9.columns, "95% UI preserved")
check("S9 Missing Value Flag", "has_missing_hle" in s9.columns, "Explicit missing value tracking")

s10 = get_s10()
check("S10 Demographic Isolation", "metric" in s10.columns and s10["metric"].iloc[0] == "daly", "Isolated as global DALYs")
check("S10 Cause Hierarchy", set(s10["cause_level_int"].unique()) >= {0, 1, 2, 3, 4}, "Levels 0-4 present")

s11 = get_s11()
check("S11 Demographic Isolation", "metric" in s11.columns and s11["metric"].iloc[0] == "yld", "Isolated as global YLDs")

# ===========================================================================
# 3. HLE Calculations Verified Against Original Records
# ===========================================================================
print("\n--- TEST SECTION 3: HLE EMPIRICAL CALCULATIONS ---")
from analytics.hle_analytics import get_location_trend, get_hle_rankings

g_trend = get_location_trend("Global")
t_map = {t["year"]: t for t in g_trend["trend"]}

check("Global 1990 HLE Match", t_map[1990]["both_mean"] == 55.9, f"(Found: {t_map[1990]['both_mean']} yrs)")
check("Global 2010 HLE Match", t_map[2010]["both_mean"] == 61.1, f"(Found: {t_map[2010]['both_mean']} yrs)")
check("Global 2020 HLE Match", t_map[2020]["both_mean"] == 62.6, f"(Found: {t_map[2020]['both_mean']} yrs)")
check("Global 2023 HLE Match", t_map[2023]["both_mean"] == 63.1, f"(Found: {t_map[2023]['both_mean']} yrs)")
check("Global 2023 UI Bounds", t_map[2023]["both_lower"] == 60.2 and t_map[2023]["both_upper"] == 65.6, "[60.2, 65.6]")

rankings = get_hle_rankings(year=2023, sex="both", include_aggregates=False, n=5)
check("Top Location Validated", len(rankings["highest"]) == 5, f"(Top: {rankings['highest'][0]['location']} {rankings['highest'][0]['hle_mean']} yrs)")
check("Bottom Location Validated", len(rankings["lowest"]) == 5, f"(Lowest: {rankings['lowest'][0]['location']} {rankings['lowest'][0]['hle_mean']} yrs)")

# ===========================================================================
# 4. Female vs Male Gender Gap Calculations
# ===========================================================================
print("\n--- TEST SECTION 4: GENDER GAP CALCULATIONS ---")
from analytics.gender_analytics import get_gender_gap_overview, get_gender_rankings

g_gap_ov = get_gender_gap_overview(year=2023)
check("Global Female HLE", g_gap_ov["global_female_hle"] == 64.2, "(64.2 yrs)")
check("Global Male HLE", g_gap_ov["global_male_hle"] == 62.2, "(62.2 yrs)")
check("Global Gender Gap (F - M)", g_gap_ov["global_gender_gap"] == 2.0, "(+2.0 yrs)")
check("Global Parity Ratio", g_gap_ov["global_parity_ratio"] == 1.032, "(Ratio: 1.032)")

g_extremes = get_gender_rankings(year=2023, n=5)
check("Widest Female Advantage", g_extremes["widest_female_advantage"][0]["gender_gap"] >= 7.0, f"({g_extremes['widest_female_advantage'][0]['location']} +{g_extremes['widest_female_advantage'][0]['gender_gap']} yrs)")
check("Reversed Gender Gap", g_extremes["narrowest_or_reverse_gap"][0]["gender_gap"] < 0, f"({g_extremes['narrowest_or_reverse_gap'][0]['location']} {g_extremes['narrowest_or_reverse_gap'][0]['gender_gap']} yrs)")

# ===========================================================================
# 5. Regional & SDI Quintile Comparisons
# ===========================================================================
print("\n--- TEST SECTION 5: REGIONAL & SDI COMPARISONS ---")
from analytics.regional_analytics import get_regional_comparison

sdi_records = get_regional_comparison(grouping="sdi", year=2023, sex="both")
sdi_map = {r["region"]: r for r in sdi_records}

high_sdi = sdi_map["High SDI"]["hle_mean"]
low_sdi = sdi_map["Low SDI"]["hle_mean"]
sdi_gap = round(high_sdi - low_sdi, 2)

check("High SDI HLE Match", high_sdi == 67.9, "(67.9 yrs)")
check("Low SDI HLE Match", low_sdi == 56.9, "(56.9 yrs)")
check("SDI Inequality Span", sdi_gap == 11.0, f"(High - Low = {sdi_gap} yrs)")

# ===========================================================================
# 6. K-Means Clustering
# ===========================================================================
print("\n--- TEST SECTION 6: K-MEANS CLUSTERING ---")
from ml.clustering import run_kmeans_clustering

ml_eval = run_kmeans_clustering(k=3, include_aggregates=False)
check("K-Means Cluster Count", ml_eval["k_clusters"] == 3, "k=3 clusters created")
check("Locations Clustered", ml_eval["total_locations"] > 600, f"({ml_eval['total_locations']} locations clustered)")
check("Silhouette Score Evaluated", 0.30 <= ml_eval["silhouette_score"] <= 0.50, f"(Score: {ml_eval['silhouette_score']})")
check("Candidate Scores (k=2..6)", len(ml_eval["evaluation_scores"]) == 5, "Evaluated k in [2, 6]")

# ===========================================================================
# 7. PCA & Explained Variance
# ===========================================================================
print("\n--- TEST SECTION 7: PCA & 2D PROJECTION ---")
pca_info = ml_eval["pca_summary"]
check("PC1 Variance", pca_info["pc1_explained_variance_pct"] > 60.0, f"({pca_info['pc1_explained_variance_pct']}%)")
check("PC2 Variance", pca_info["pc2_explained_variance_pct"] > 10.0, f"({pca_info['pc2_explained_variance_pct']}%)")
check("Total 2D Explained Variance", pca_info["total_explained_variance_pct"] > 80.0, f"({pca_info['total_explained_variance_pct']}%)")
check("2D Coordinates Generated", len(ml_eval["location_points"]) == ml_eval["total_locations"], "All points have (x, y)")

# ===========================================================================
# 8. STRIPS Action Preconditions & State Transitions (Frame Problem)
# ===========================================================================
print("\n--- TEST SECTION 8: STRIPS CALCULUS & FRAME PROBLEM ---")
from planning.strips import WorldState, StripsAction
from planning.htn import PRIMITIVE_ACTIONS

ws = WorldState(initial_predicates={"DATASET_AVAILABLE", "PRIOR_UNTOUCHED_FACT"})
load_action = PRIMITIVE_ACTIONS["LOAD_DATASET"]

check("Precondition Verification", load_action.is_applicable(ws.predicates), "DATASET_AVAILABLE satisfied")
ws.transition(load_action, 1)
check("Add Effect Applied", "DATA_LOADED" in ws.predicates, "DATA_LOADED added")
check("Frame Problem Preserved", "PRIOR_UNTOUCHED_FACT" in ws.predicates, "Untouched fact persists without deletion")

# ===========================================================================
# 9. HTN Task Decomposition for Multiple Distinct Goals
# ===========================================================================
print("\n--- TEST SECTION 9: HTN TASK DECOMPOSITION ---")
from planning.htn import HtnPlanner, COMPOUND_GOALS

planner = HtnPlanner()
plans = {}
for g_id in COMPOUND_GOALS:
    p = planner.decompose(g_id)
    plans[g_id] = [step["action"] for step in p["plan"]]

check("Multiple Goals Supported", len(plans) == 5, "5 compound goals defined")
check("Goal Differentiation", plans["ANALYZE_HEALTH_INEQUALITY"] != plans["COMPARE_REGIONAL_HLE"], "Inequality vs Regional plans differ")
check("Gender Plan Specificity", "COMPUTE_GENDER_DIFFERENTIALS" in plans["ANALYZE_GENDER_GAP"], "Gender action in gender plan")
check("Clustering Plan Specificity", "RUN_CLUSTERING" in plans["ANALYZE_HEALTH_INEQUALITY"], "Clustering action in inequality plan")

# ===========================================================================
# 10. FastAPI Canonical REST Endpoints
# ===========================================================================
print("\n--- TEST SECTION 10: FASTAPI ENDPOINT SUITE ---")
from main import app

client = TestClient(app)

endpoints_to_test = [
    ("GET", "/api/metadata"),
    ("GET", "/api/analyze/hle?location=Global"),
    ("GET", "/api/analyze/gender-gap?year=2023"),
    ("GET", "/api/analyze/trends?grouping=sdi"),
    ("GET", "/api/analyze/regional-comparison?grouping=sdi&year=2023"),
    ("GET", "/api/ml/clusters?k=3"),
    ("GET", "/api/global-burden/daly?level=2"),
    ("GET", "/api/global-burden/yld?level=2"),
    ("POST", "/api/plan", {"goal_id": "ANALYZE_HEALTH_INEQUALITY"}),
    ("GET", "/api/recommendations?low_hle_threshold=56.9"),
    ("GET", "/api/reports"),
]

endpoint_passes = 0
for method, path, *payload in endpoints_to_test:
    if method == "GET":
        r = client.get(path)
    else:
        r = client.post(path, json=payload[0])
    if r.status_code == 200:
        endpoint_passes += 1

check("Canonical REST API Suite", endpoint_passes == len(endpoints_to_test), f"({endpoint_passes}/{len(endpoints_to_test)} responded with 200 OK)")

# ===========================================================================
# 11. Recommendation Engine & Surveillance Flags
# ===========================================================================
print("\n--- TEST SECTION 11: RECOMMENDATION ENGINE ---")
from recommendations.engine import generate_recommendations

recs = generate_recommendations()
flags = recs["flags"]

check("Low HLE Flags Generated", len(flags["low_hle"]) > 0, f"({len(flags['low_hle'])} flags)")
check("HLE Decline Flags Generated", len(flags["hle_decline"]) > 0, f"({len(flags['hle_decline'])} flags)")
check("Gender Disparity Flags Generated", len(flags["gender_disparity"]) > 0, f"({len(flags['gender_disparity'])} flags)")
check("Cluster Group Policies", len(flags["cluster_groups"]) == 3, f"({len(flags['cluster_groups'])} clusters profiled)")

# ===========================================================================
# 12. Automated Multi-Format Report Generation
# ===========================================================================
print("\n--- TEST SECTION 12: REPORT GENERATION ---")
from recommendations.report_generator import (
    compile_full_report,
    generate_markdown_report,
    generate_html_report,
)

rep_data = compile_full_report()
check("Master Report JSON Compiled", len(rep_data.keys()) >= 8, f"({len(rep_data.keys())} sections)")

md_rep = generate_markdown_report()
check("Markdown Report Generated", len(md_rep) > 5000, f"({len(md_rep)} characters)")

html_rep = generate_html_report()
check("Printable HTML Generated", "<!DOCTYPE html>" in html_rep and "@media print" in html_rep, "CSS Print ready")

# ===========================================================================
# Final QA Tally
# ===========================================================================
duration = round(time.time() - start_all, 2)
print("\n" + "=" * 75)
print(f"  MASTER TEST SUITE SUMMARY: {passed_count} PASSED, {failed_count} FAILED ({duration}s)")
print("=" * 75)

assert failed_count == 0, f"{failed_count} tests failed!"
print("\nALL SYSTEM MODULES TESTED & VALIDATED WITH 100% SUCCESS RATE!\n")
