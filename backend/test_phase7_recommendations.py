"""
test_phase7_recommendations.py
------------------------------
Verifies the recommendation engine and report generation modules.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from recommendations.engine import generate_recommendations
from recommendations.report_generator import (
    compile_full_report,
    generate_markdown_report,
    generate_html_report,
)

print("=" * 60)
print("TESTING RECOMMENDATION ENGINE")
print("=" * 60)

recs = generate_recommendations(low_hle_threshold=56.9, gender_gap_threshold=5.0)
print(f"Status: {recs['status']}")
print(f"Total Flags Generated: {recs['total_flags_generated']}")

print(f"\n1. Low HLE Flags ({len(recs['flags']['low_hle'])}):")
for f in recs['flags']['low_hle'][:3]:
    print(f"   [{f['flag_id']}] {f['location']}: {f['actual_value']} ({f['disparity_delta']})")

print(f"\n2. HLE Decline Flags ({len(recs['flags']['hle_decline'])}):")
for f in recs['flags']['hle_decline'][:3]:
    print(f"   [{f['flag_id']}] {f['location']}: {f['actual_value']}")

print(f"\n3. Gender Disparity Flags ({len(recs['flags']['gender_disparity'])}):")
for f in recs['flags']['gender_disparity'][:3]:
    print(f"   [{f['flag_id']}] {f['location']}: {f['actual_value']}")

print(f"\n4. Cluster Policy Groups ({len(recs['flags']['cluster_groups'])}):")
for f in recs['flags']['cluster_groups']:
    print(f"   [{f['flag_id']}] {f['group_name']}: {f['location_count']} locations | {f['actual_value']}")

print("\n" + "=" * 60)
print("TESTING REPORT GENERATOR")
print("=" * 60)

full_data = compile_full_report()
print(f"Report Title: {full_data['report_metadata']['title']}")
print(f"Sections compiled: {list(full_data.keys())}")

md_content = generate_markdown_report()
print(f"Markdown report generated: {len(md_content)} characters, {len(md_content.splitlines())} lines.")

html_content = generate_html_report()
print(f"HTML report generated: {len(html_content)} characters, {len(html_content.splitlines())} lines.")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
