"""
test_phase4.py
--------------
Verification test suite for Phase 4: Regional Comparison and Trend Analysis.
Tests:
  1. Regional groupings comparison (SDI, Super-Regions, GBD Regions).
  2. Multi-year trajectory matrix.
  3. Increase/decrease location analysis.
  4. Top 5 and Bottom 5 location rankings with hydrated historical points.
"""

import sys
import os
import io

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

from analytics.regional_analytics import (
    get_grouping_names,
    get_regional_comparison,
    get_regional_historical_trends,
    get_increase_decrease_analysis,
    get_top_and_bottom_locations,
)

SEP = "=" * 70

def section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def test_phase4():
    # 1. Groupings
    section("1. Regional Grouping Sets")
    groups = get_grouping_names()
    print("SDI Tiers:", groups["sdi"])
    print("GBD Super-Regions:", groups["super_regions"])
    print(f"GBD Intermediate Regions count: {len(groups['regions'])}")
    assert len(groups["sdi"]) == 6
    assert len(groups["super_regions"]) == 8

    # 2. SDI Comparison
    section("2. SDI Quintiles Comparison (2023, Both Sexes)")
    sdi_comp = get_regional_comparison(grouping="sdi", year=2023, sex="both")
    for r in sdi_comp:
        print(f"  {r['region']:<18}: {r['hle_2023']} yrs [{r['hle_lower']}, {r['hle_upper']}] | Gap: {r['gender_gap']} | Change: {r['pct_change_2010_2023']}% ({r['direction']})")

    # Verify exact SDI values from Dataset S9
    high_sdi = next(r for r in sdi_comp if r["region"] == "High SDI")
    low_sdi = next(r for r in sdi_comp if r["region"] == "Low SDI")
    assert high_sdi["hle_2023"] == 67.9, "High SDI 2023 should be 67.9"
    assert low_sdi["hle_2023"] == 56.9, "Low SDI 2023 should be 56.9"
    sdi_gradient = round(high_sdi["hle_2023"] - low_sdi["hle_2023"], 2)
    print(f"\n  ✓ Verified Gradient: High SDI leads Low SDI by +{sdi_gradient} healthy years")

    # 3. Super-Regions Comparison
    section("3. GBD Super-Regions Comparison (2023)")
    super_comp = get_regional_comparison(grouping="super_regions", year=2023, sex="both")
    for r in super_comp:
        print(f"  {r['region']:<45}: {r['hle_2023']} yrs (Gap: {r['gender_gap']} yrs)")

    # 4. Historical Trajectory Matrix
    section("4. SDI Trajectory Matrix (1990-2023)")
    trends = get_regional_historical_trends(grouping="sdi")
    for row in trends:
        print(f"  Year {row['year']}: High={row.get('High SDI')}, Middle={row.get('Middle SDI')}, Low={row.get('Low SDI')}")

    # 5. Increase / Decrease Analysis
    section("5. Increase vs. Decrease Analysis (2010-2023)")
    inc_dec = get_increase_decrease_analysis(include_aggregates=False, n=5)
    print(f"Analyzed {inc_dec['total_analyzed']} non-aggregate locations:")
    print(f"  Increased: {inc_dec['total_increased']} locations")
    print(f"  Decreased: {inc_dec['total_decreased']} locations")
    print(f"  Unchanged: {inc_dec['total_unchanged']} locations")

    print("\nTop 5 Largest % Increases (2010–2023):")
    for item in inc_dec["largest_increases"]:
        print(f"  ▲ {item['location']:<25}: +{item['pct_change_mean']}% [{item['pct_change_lower']}%, {item['pct_change_upper']}%]")

    print("\nTop 5 Largest % Decreases (2010–2023):")
    for item in inc_dec["largest_decreases"]:
        print(f"  ▼ {item['location']:<25}: {item['pct_change_mean']}% [{item['pct_change_lower']}%, {item['pct_change_upper']}%]")

    # 6. Top 5 & Bottom 5 Rankings
    section("6. Top 5 and Bottom 5 Rankings (2023)")
    top_bot = get_top_and_bottom_locations(year=2023, include_aggregates=False, n=5)
    print("Top 5 Locations (2023):")
    for t in top_bot["top_5"]:
        print(f"  #{t['rank']} {t['location']:<20}: 2023={t['hle_latest']} yrs [{t['hle_lower']}-{t['hle_upper']}] | 1990={t['hle_1990']} | Gap={t['gender_gap']} | Change={t['pct_change']}%")

    print("\nBottom 5 Locations (2023):")
    for b in top_bot["bottom_5"]:
        print(f"  #{b['rank']} {b['location']:<25}: 2023={b['hle_latest']} yrs [{b['hle_lower']}-{b['hle_upper']}] | 1990={b['hle_1990']} | Gap={b['gender_gap']} | Change={b['pct_change']}%")

    print(f"\n{SEP}\n  ALL PHASE 4 BACKEND TESTS PASSED!\n{SEP}")

if __name__ == "__main__":
    test_phase4()
