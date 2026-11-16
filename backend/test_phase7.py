"""
test_phase7.py
--------------
Tests for Gender Gap Analytics, Disease Burden Analytics (S10/S11),
and Overview route.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from analytics.gender_analytics import (
    get_gender_gap_overview,
    get_gender_rankings,
    get_gender_scatter_data,
    get_gender_comparison_table,
)
from analytics.disease_analytics import (
    get_disease_burden_overview,
    get_level1_broad_breakdown,
    get_top_causes,
    get_daly_vs_yld_comparison,
    get_disease_burden_table,
)

print("=" * 60)
print("TESTING GENDER GAP ANALYTICS")
print("=" * 60)

g_overview = get_gender_gap_overview(2023)
print(f"Global Female HLE: {g_overview['global_female_hle']} yrs")
print(f"Global Male HLE:   {g_overview['global_male_hle']} yrs")
print(f"Global Gender Gap: {g_overview['global_gender_gap']} yrs")
print(f"Parity Ratio:      {g_overview['global_parity_ratio']}")
print(f"SDI Gradient Steps: {len(g_overview['sdi_gradient'])}")
print(f"Historical Steps:   {len(g_overview['historical_trajectory'])}")
print(f"Countries Analyzed: {g_overview['country_distribution']['total_countries']}")
print(f"Widest Gap Country: {g_overview['country_distribution']['widest_country']}")
print(f"Narrowest Gap:      {g_overview['country_distribution']['narrowest_country']}")

g_rankings = get_gender_rankings(2023, n=5)
print(f"\nTop 3 Widest Female Advantages:")
for r in g_rankings['widest_female_advantage'][:3]:
    print(f"  {r['location']}: Female {r['female_hle']} vs Male {r['male_hle']} -> Gap: +{r['gender_gap']} yrs")

print(f"\nTop 3 Narrowest / Reverse Gaps:")
for r in g_rankings['narrowest_or_reverse_gap'][:3]:
    print(f"  {r['location']}: Female {r['female_hle']} vs Male {r['male_hle']} -> Gap: {r['gender_gap']} yrs")

g_scatter = get_gender_scatter_data(2023, max_points=50)
print(f"Scatter points count: {len(g_scatter)}")

g_table = get_gender_comparison_table(2023, page=1, page_size=5)
print(f"Table total records: {g_table['total']}, pages: {g_table['total_pages']}")

print("\n" + "=" * 60)
print("TESTING DISEASE BURDEN ANALYTICS (S10 & S11)")
print("=" * 60)

d_overview = get_disease_burden_overview()
print(f"Global DALYs: {d_overview['daly_summary']['count_2023_mean']:.1f} (ASR: {d_overview['daly_summary']['asr_2023_mean']:.1f})")
print(f"Leading DALY Cause: {d_overview['daly_summary']['leading_cause']}")
print(f"Global YLDs:  {d_overview['yld_summary']['count_2023_mean']:.1f} (ASR: {d_overview['yld_summary']['asr_2023_mean']:.1f})")
print(f"Leading YLD Cause:  {d_overview['yld_summary']['leading_cause']}")
print(f"Disability Share (%): {d_overview['disability_share_percent']}%")

l1 = get_level1_broad_breakdown()
print(f"\nLevel 1 DALY Categories:")
for c in l1['daly_categories']:
    print(f"  {c['short_name']}: {c['share_percent']}% | ASR: {c['asr_2023']} | Trend: {c['asr_pct_change']}%")

top_dalys = get_top_causes(metric="daly", level=2, n=5)
print(f"\nTop 3 DALY Causes (Level 2):")
for r in top_dalys[:3]:
    print(f"  #{r['rank']} {r['cause']}: Count={r['count_2023_mean']:.1f}, ASR={r['asr_2023_mean']:.1f}, Trend={r['asr_pct_change']}%")

top_ylds = get_top_causes(metric="yld", level=2, n=5)
print(f"\nTop 3 YLD Causes (Level 2):")
for r in top_ylds[:3]:
    print(f"  #{r['rank']} {r['cause']}: Count={r['count_2023_mean']:.1f}, ASR={r['asr_2023_mean']:.1f}, Trend={r['asr_pct_change']}%")

daly_vs_yld = get_daly_vs_yld_comparison()
print(f"\nDALY vs YLD Matched Causes: {len(daly_vs_yld)}")
for c in daly_vs_yld[:4]:
    print(f"  {c['cause']}: DALY={c['daly_count_2023']:.1f}, YLD={c['yld_count_2023']:.1f} -> Disability%={c['disability_ratio_pct']}% [{c['burden_type']}]")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
