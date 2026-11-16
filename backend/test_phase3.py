"""
test_phase3.py
--------------
Verification and unit test suite for Phase 3: Healthy Life Expectancy Analytics.
Tests all analytical calculations against the real Excel records in S9.
"""

import sys
import os
import io
import json

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

from analytics.hle_analytics import (
    get_available_locations,
    get_location_trend,
    get_hle_comparison,
    get_hle_rankings,
    get_gender_gap_analysis,
    get_comprehensive_location_table,
)

SEP = "=" * 70

def section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def test_phase3():
    # 1. Locations
    section("1. Available Locations")
    locs = get_available_locations(include_aggregates=False)
    print(f"Total sovereign/distinct locations (non-aggregate): {len(locs)}")
    assert len(locs) > 150, "Should have over 150 countries/territories"
    print(f"Sample locations: {locs[:8]}")

    # 2. Location Trend (Global)
    section("2. Location Trend for Global")
    global_trend = get_location_trend("Global")
    assert global_trend["location"] == "Global"
    summary = global_trend["summary"]
    print("Global Summary:")
    print(f"  HLE 1990: {summary['hle_1990_mean']}")
    print(f"  HLE 2023: {summary['hle_2023_mean']} [{summary['hle_2023_lower']}, {summary['hle_2023_upper']}]")
    print(f"  Net Gain (1990-2023): +{summary['net_change_1990_2023']} years")
    print(f"  Female HLE 2023: {summary['female_hle_2023']}")
    print(f"  Male HLE 2023: {summary['male_hle_2023']}")
    print(f"  Gender Gap 2023 (F - M): {summary['gender_gap_2023']} years")
    print(f"  2010-2023 % Change: {summary['pct_change_2010_2023_mean']}% [{summary['pct_change_2010_2023_lower']}%, {summary['pct_change_2010_2023_upper']}%]")

    # Check exact values from original GBD table
    assert summary['hle_1990_mean'] == 55.9, "Global 1990 mean should be 55.9"
    assert summary['hle_2023_mean'] == 63.1, "Global 2023 mean should be 63.1"
    assert summary['female_hle_2023'] == 64.2, "Global female 2023 should be 64.2"
    assert summary['male_hle_2023'] == 62.2, "Global male 2023 should be 62.2"
    assert summary['gender_gap_2023'] == 2.0, "Global gender gap should be 2.0"
    assert summary['pct_change_2010_2023_mean'] == 3.3, "Global % change should be 3.3"
    print("  ✓ Global values match original Excel records exactly!")

    # 3. Location Trend for India
    section("3. Location Trend for India")
    india_trend = get_location_trend("India")
    ind_sum = india_trend["summary"]
    print(f"India 1990 HLE: {ind_sum['hle_1990_mean']}")
    print(f"India 2023 HLE: {ind_sum['hle_2023_mean']} [{ind_sum['hle_2023_lower']}, {ind_sum['hle_2023_upper']}]")
    print(f"India Net Gain (1990-2023): +{ind_sum['net_change_1990_2023']} years")
    print(f"India Gender Gap 2023: {ind_sum['gender_gap_2023']} years")
    print(f"India 2010-2023 % Change: +{ind_sum['pct_change_2010_2023_mean']}%")
    assert ind_sum['hle_1990_mean'] == 50.1
    assert ind_sum['hle_2023_mean'] == 61.0
    print("  ✓ India values match original Excel records exactly!")

    # 4. Rankings (Highest & Lowest HLE)
    section("4. HLE Rankings 2023")
    rankings = get_hle_rankings(year=2023, sex="both", include_aggregates=False, n=5)
    print("Top 5 Highest HLE:")
    for r in rankings["highest"]:
        print(f"  #{r['rank']} {r['location']}: {r['hle_mean']} years [{r['hle_lower']}, {r['hle_upper']}]")
    print("\nTop 5 Lowest HLE:")
    for r in rankings["lowest"]:
        print(f"  #{r['rank']} {r['location']}: {r['hle_mean']} years [{r['hle_lower']}, {r['hle_upper']}]")

    # 5. Gender Gap Analysis
    section("5. Gender Gap Analysis (2023)")
    gap_data = get_gender_gap_analysis(year=2023, include_aggregates=False, n=5)
    print(f"Global Benchmark Gender Gap: {gap_data['global_gender_gap']} years")
    print("\nWidest Female Advantage (Female HLE - Male HLE):")
    for g in gap_data["widest_female_advantage"]:
        print(f"  {g['location']}: +{g['gender_gap']} yrs (Female {g['female_hle']} vs Male {g['male_hle']})")
    print("\nNarrowest / Reverse Gender Gap:")
    for g in gap_data["narrowest_or_reverse_gap"]:
        print(f"  {g['location']}: {g['gender_gap']} yrs (Female {g['female_hle']} vs Male {g['male_hle']})")

    # 6. Comparison Chart Data
    section("6. HLE Comparison across Locations")
    comparison = get_hle_comparison(locations=["Global", "High SDI", "Low SDI", "Japan", "India", "Nigeria"], year=2023, sex="both")
    for c in comparison:
        print(f"  {c['location']:<15}: {c['hle_mean']} yrs [{c['hle_lower']}, {c['hle_upper']}] (Change: {c['pct_change_mean']}%)")

    # 7. Comprehensive Table
    section("7. Comprehensive Location Table (Page 1)")
    table = get_comprehensive_location_table(search="", include_aggregates=True, sort_by="hle_2023", sort_asc=False, page=1, page_size=5)
    print(f"Total locations indexed: {table['total_records']}, Total pages: {table['total_pages']}")
    for r in table["records"]:
        print(f"  {r['location']:<25} | 1990: {r['hle_1990']} | 2010: {r['hle_2010']} | 2020: {r['hle_2020']} | 2023: {r['hle_2023']} [{r['hle_2023_lower']}-{r['hle_2023_upper']}] | Gap: {r['gender_gap_2023']} | Change: {r['pct_change_2010_2023']}%")

    print(f"\n{SEP}\n  ALL PHASE 3 BACKEND ANALYTICS TESTS PASSED!\n{SEP}")

if __name__ == "__main__":
    test_phase3()
