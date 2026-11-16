"""
recommendations/engine.py
-------------------------
Transparent, rule-based recommendation system for regional health inequality surveillance.
Operates strictly on empirical analytical results from Dataset S9 and machine learning outputs.

Flag Types:
  1. FLAG_LOW_HLE: Locations with relatively low Healthy Life Expectancy (< Low SDI benchmark: 56.9 yrs).
  2. FLAG_HLE_DECLINE: Locations showing negative progress between 2010 and 2023 (pct_change < 0).
  3. FLAG_LARGE_GENDER_GAP: Locations with extreme female-male disparities (|gap| >= 5.0 yrs or reversed gap < 0).
  4. FLAG_CLUSTER_PROFILE: Policy groupings derived from K-Means cluster profiles.

Scientific Integrity:
  - Heuristic public health policy surveillance only.
  - Strict non-causal disclaimer.
  - No medical diagnoses or individual clinical guidance.
"""

from typing import Any, Dict, List, Optional
import pandas as pd

from data.pipeline import get_s9
from ml.clustering import run_kmeans_clustering

ACADEMIC_DISCLAIMER = (
    "DISCLAIMER & METHODOLOGICAL BOUNDARIES: "
    "These evidence-based recommendations are generated via transparent heuristic decision rules applied to "
    "observational epidemiological surveillance data (GBD 2023). Statistical associations and cluster groupings "
    "reflect empirical correlations and baseline developmental patterns; they DO NOT establish causal relationships. "
    "This system provides macro-level public health policy prioritization flags and must NOT be used for clinical "
    "diagnoses, patient medical management, or individual clinical interventions."
)


def _safe_float(val: Any, decimals: int = 2) -> Optional[float]:
    if val is None or pd.isna(val):
        return None
    try:
        return round(float(val), decimals)
    except (ValueError, TypeError):
        return None


def generate_recommendations(
    low_hle_threshold: float = 56.9,   # Low SDI benchmark
    gender_gap_threshold: float = 5.0,  # Extreme gap threshold
    max_per_category: int = 15,
) -> Dict[str, Any]:
    """
    Evaluates rule-based criteria across all empirical records and returns categorized flags.
    """
    df = get_s9()
    countries_df = df[~df["is_aggregate"]].copy()

    # -----------------------------------------------------------------------
    # 1. FLAG_LOW_HLE: Locations with 2023 HLE strictly below benchmark
    # -----------------------------------------------------------------------
    sub_2023_both = countries_df[(countries_df["year"] == 2023) & (countries_df["sex"] == "both")].copy()
    sub_2023_both = sub_2023_both.dropna(subset=["hle_mean"]).sort_values("hle_mean", ascending=True)

    low_hle_rows = sub_2023_both[sub_2023_both["hle_mean"] < low_hle_threshold]
    # Remove duplicate location names keeping lowest
    low_hle_rows = low_hle_rows.drop_duplicates(subset=["location"])

    low_hle_flags = []
    for rank, (_, row) in enumerate(low_hle_rows.head(max_per_category).iterrows(), start=1):
        hle_val = _safe_float(row["hle_mean"])
        lower = _safe_float(row["hle_lower"])
        upper = _safe_float(row["hle_upper"])
        gap_to_benchmark = _safe_float(low_hle_threshold - hle_val) if hle_val else None

        low_hle_flags.append({
            "flag_id": f"LOW_HLE_{rank:03d}",
            "flag_type": "FLAG_LOW_HLE",
            "category": "High Vulnerability",
            "severity": "HIGH",
            "location": row["location"],
            "metric_used": "hle_2023_mean (Both Sexes)",
            "actual_value": f"{hle_val} yrs [95% UI: {lower}–{upper}]",
            "benchmark_reference": f"Low SDI Benchmark: {low_hle_threshold} yrs",
            "disparity_delta": f"-{gap_to_benchmark} yrs below Low SDI",
            "reason": f"Healthy Life Expectancy ({hle_val} yrs) is significantly below the Low SDI benchmark ({low_hle_threshold} yrs).",
            "policy_focus": (
                "Prioritize universal primary healthcare (PHC) coverage, clean water/sanitation infrastructure, "
                "routine childhood immunization, and maternal mortality reduction programs."
            ),
        })

    # -----------------------------------------------------------------------
    # 2. FLAG_HLE_DECLINE: Locations showing decline between 2010 and 2023
    # -----------------------------------------------------------------------
    decline_rows = sub_2023_both[sub_2023_both["pct_change_mean"] < 0].sort_values("pct_change_mean", ascending=True)
    decline_rows = decline_rows.drop_duplicates(subset=["location"])

    decline_flags = []
    for rank, (_, row) in enumerate(decline_rows.head(max_per_category).iterrows(), start=1):
        pct = _safe_float(row["pct_change_mean"])
        pct_lower = _safe_float(row["pct_change_lower"])
        pct_upper = _safe_float(row["pct_change_upper"])
        hle_val = _safe_float(row["hle_mean"])

        decline_flags.append({
            "flag_id": f"DECLINE_{rank:03d}",
            "flag_type": "FLAG_HLE_DECLINE",
            "category": "Health Reversal Alert",
            "severity": "CRITICAL" if (pct and pct < -3.0) else "MEDIUM",
            "location": row["location"],
            "metric_used": "pct_change_mean (2010–2023)",
            "actual_value": f"{pct}% [95% UI: {pct_lower}% to {pct_upper}%] (2023 HLE: {hle_val} yrs)",
            "benchmark_reference": "Global Progress Benchmark: +3.2% increase",
            "disparity_delta": f"{pct}% contraction in healthy life span",
            "reason": f"Longitudinal reversal in population health with a {pct}% contraction in HLE between 2010 and 2023.",
            "policy_focus": (
                "Investigate underlying systemic disruptions (armed conflict, health financing collapse, pandemic shocks, "
                "or environmental crises) to restore health system resilience and emergency care supply chains."
            ),
        })

    # -----------------------------------------------------------------------
    # 3. FLAG_LARGE_GENDER_GAP: Extreme female advantage or reversed gap
    # -----------------------------------------------------------------------
    fem_sub = countries_df[(countries_df["year"] == 2023) & (countries_df["sex"] == "female")].set_index("location")
    mal_sub = countries_df[(countries_df["year"] == 2023) & (countries_df["sex"] == "male")].set_index("location")
    joined_gender = fem_sub.join(mal_sub, suffixes=("_f", "_m"), how="inner").dropna(subset=["hle_mean_f", "hle_mean_m"])
    joined_gender["gap"] = joined_gender["hle_mean_f"] - joined_gender["hle_mean_m"]
    joined_gender = joined_gender[~joined_gender.index.duplicated(keep="first")]

    # Extreme positive gaps (large female advantage > 5.0 yrs)
    wide_gap_rows = joined_gender[joined_gender["gap"] >= gender_gap_threshold].sort_values("gap", ascending=False)
    # Reversed or narrow gaps (gap < 0)
    rev_gap_rows = joined_gender[joined_gender["gap"] < 0].sort_values("gap", ascending=True)

    gender_flags = []
    # Add widest female advantages
    for rank, (loc, row) in enumerate(wide_gap_rows.head(max_per_category // 2).iterrows(), start=1):
        gap_val = _safe_float(row["gap"])
        f_val = _safe_float(row["hle_mean_f"])
        m_val = _safe_float(row["hle_mean_m"])
        gender_flags.append({
            "flag_id": f"GENDER_WIDE_{rank:03d}",
            "flag_type": "FLAG_LARGE_GENDER_GAP",
            "category": "Excess Male Mortality Divergence",
            "severity": "HIGH",
            "location": str(loc),
            "metric_used": "gender_gap (Female HLE - Male HLE)",
            "actual_value": f"+{gap_val} yrs (Female: {f_val} yrs vs. Male: {m_val} yrs)",
            "benchmark_reference": "Global Gender Gap Benchmark: +2.0 yrs",
            "disparity_delta": f"+{_safe_float(gap_val - 2.0)} yrs above global benchmark",
            "reason": f"Substantial longevity disparity with female HLE exceeding male HLE by {gap_val} years (>{gender_gap_threshold} yrs).",
            "policy_focus": (
                "Deploy targeted men's health initiatives: adult cardiovascular screening, tobacco/alcohol harm reduction, "
                "mental health support, and occupational safety regulations in industrial and transport sectors."
            ),
        })

    # Add reversed gaps
    for rank, (loc, row) in enumerate(rev_gap_rows.head(max_per_category // 2).iterrows(), start=1):
        gap_val = _safe_float(row["gap"])
        f_val = _safe_float(row["hle_mean_f"])
        m_val = _safe_float(row["hle_mean_m"])
        gender_flags.append({
            "flag_id": f"GENDER_REV_{rank:03d}",
            "flag_type": "FLAG_LARGE_GENDER_GAP",
            "category": "Reversed Gender Advantage",
            "severity": "CRITICAL",
            "location": str(loc),
            "metric_used": "gender_gap (Female HLE - Male HLE)",
            "actual_value": f"{gap_val} yrs (Female: {f_val} yrs vs. Male: {m_val} yrs)",
            "benchmark_reference": "Global Gender Gap Benchmark: +2.0 yrs",
            "disparity_delta": f"{_safe_float(gap_val - 2.0)} yrs deficit relative to global parity",
            "reason": f"Anomalous reverse gender gap where male HLE exceeds female HLE by {abs(gap_val)} years.",
            "policy_focus": (
                "Urgently address maternal health risks, access barriers to obstetric emergency care, "
                "female nutritional disparities, and socio-economic determinants impeding women's health capital."
            ),
        })

    # -----------------------------------------------------------------------
    # 4. FLAG_CLUSTER_PROFILE: Group-level policy recommendations via ML
    # -----------------------------------------------------------------------
    ml_result = run_kmeans_clustering(k=3, include_aggregates=False)
    cluster_profiles = ml_result.get("cluster_profiles", [])

    group_flags = []
    for c in cluster_profiles:
        cid = c["cluster_id"]
        cname = c["name"]
        size = c["location_count"]
        m_hle = c.get("mean_hle_2023")
        m_gain = c.get("mean_net_gain")
        m_pct = c.get("mean_pct_change")

        if cid == 0:
            policy_strategy = (
                "Strategic Catch-Up: Emphasize primary healthcare investments, basic maternal-child health packages, "
                "and communicable disease eradication to drive high marginal gains in healthy life years."
            )
            severity = "HIGH"
        elif cid == 1:
            policy_strategy = (
                "Dual Burden Transition: Manage emerging Non-Communicable Diseases (hypertension, diabetes, cardiovascular) "
                "while consolidating control over residual infectious disease threats."
            )
            severity = "MEDIUM"
        else:
            policy_strategy = (
                "Healthy Aging & Morbidity Compression: Focus on chronic disease screening, musculoskeletal health, "
                "mental health integration, and reducing lived disability (YLDs) to compress morbidity in older cohorts."
            )
            severity = "MAINTENANCE"

        group_flags.append({
            "flag_id": f"CLUSTER_PROFILE_{cid}",
            "flag_type": "FLAG_CLUSTER_PROFILE",
            "category": f"K-Means Cluster {cid} Profile",
            "severity": severity,
            "group_name": cname,
            "badge": c.get("badge", "Tier"),
            "location_count": size,
            "metric_used": "Multivariate Centroid (9 continuous features)",
            "actual_value": f"Avg 2023 HLE: {m_hle} yrs | 1990–2023 Gain: +{m_gain} yrs | 2010–23 % Change: {m_pct}%",
            "reason": f"Homogeneous epidemiological developmental cluster comprising {size} locations with shared health dynamics.",
            "sample_locations": c.get("sample_locations", [])[:6],
            "policy_focus": policy_strategy,
        })

    # Summary metrics
    total_flags = len(low_hle_flags) + len(decline_flags) + len(gender_flags) + len(group_flags)

    return {
        "status": "success",
        "total_flags_generated": total_flags,
        "criteria": {
            "low_hle_threshold": low_hle_threshold,
            "gender_gap_threshold": gender_gap_threshold,
        },
        "flags": {
            "low_hle": low_hle_flags,
            "hle_decline": decline_flags,
            "gender_disparity": gender_flags,
            "cluster_groups": group_flags,
        },
        "disclaimer": ACADEMIC_DISCLAIMER,
    }
