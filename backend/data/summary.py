"""
data/summary.py
---------------
Generates descriptive summary statistics and metadata for each dataset.
These summaries are served by the /api/datasets/ endpoints and displayed
on the Overview and other dashboard pages.

All values come from the actual data — nothing is hardcoded.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _safe_float(val) -> float | None:
    """Return a Python float or None (never NaN, which breaks JSON)."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    return round(float(val), 2)


# ===========================================================================
# S9 Summary
# ===========================================================================

def summarise_s9(df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate a summary of the S9 HLE dataset.
    Returns a JSON-serialisable dict.
    """
    # Work only on 'both' sexes + 2023 for headline numbers
    df_both_2023 = df[(df["sex"] == "both") & (df["year"] == 2023) & ~df["is_aggregate"]]
    df_both      = df[(df["sex"] == "both") & ~df["is_aggregate"]]

    all_locs = df["location"].unique().tolist()
    n_locs   = len([l for l in all_locs if l not in
                    {"Global", "Low SDI", "Low-middle SDI", "Middle SDI",
                     "High-middle SDI", "High SDI"}])

    global_row_2023 = df[(df["location"] == "Global") & (df["sex"] == "both") & (df["year"] == 2023)]
    global_hle_2023 = _safe_float(global_row_2023["hle_mean"].values[0]) \
        if len(global_row_2023) > 0 else None

    global_row_1990 = df[(df["location"] == "Global") & (df["sex"] == "both") & (df["year"] == 1990)]
    global_hle_1990 = _safe_float(global_row_1990["hle_mean"].values[0]) \
        if len(global_row_1990) > 0 else None

    # Top / bottom 5 countries by HLE in 2023
    country_2023 = df_both_2023.dropna(subset=["hle_mean"])
    top5 = country_2023.nlargest(5, "hle_mean")[["location", "hle_mean", "hle_lower", "hle_upper"]]\
                        .rename(columns={"hle_mean": "hle", "hle_lower": "lower", "hle_upper": "upper"})\
                        .to_dict(orient="records")
    bot5 = country_2023.nsmallest(5, "hle_mean")[["location", "hle_mean", "hle_lower", "hle_upper"]]\
                        .rename(columns={"hle_mean": "hle", "hle_lower": "lower", "hle_upper": "upper"})\
                        .to_dict(orient="records")

    # Global gender gap: Female Global HLE - Male Global HLE in 2023
    g_fem = df[(df["location"] == "Global") & (df["sex"] == "female") & (df["year"] == 2023)]["hle_mean"]
    g_mal = df[(df["location"] == "Global") & (df["sex"] == "male") & (df["year"] == 2023)]["hle_mean"]
    global_gap_2023 = _safe_float(g_fem.values[0] - g_mal.values[0]) if len(g_fem) > 0 and len(g_mal) > 0 else None

    # Country-level gender gap in 2023
    piv = df[(df["year"] == 2023) & ~df["is_aggregate"]]
    female_2023 = piv[piv["sex"] == "female"][["location", "hle_mean"]].set_index("location")
    male_2023   = piv[piv["sex"] == "male"  ][["location", "hle_mean"]].set_index("location")
    gap_df      = female_2023.join(male_2023, suffixes=("_f", "_m")).dropna()
    gap_df["gap"] = gap_df["hle_mean_f"] - gap_df["hle_mean_m"]

    return {
        "dataset"              : "S9",
        "title"                : "Healthy Life Expectancy by Location and Sex",
        "scope"                : "Country, region, and SDI-group level",
        "years_covered"        : [1990, 2010, 2020, 2023],
        "sex_groups"           : ["Both Sexes", "Females", "Males"],
        "total_rows_long"      : len(df),
        "unique_locations"     : n_locs,
        "includes_aggregates"  : True,
        "uncertainty_intervals": True,
        "global_hle_1990"      : global_hle_1990,
        "global_hle_2023"      : global_hle_2023,
        "hle_range_2023"       : {
            "min": _safe_float(country_2023["hle_mean"].min()),
            "max": _safe_float(country_2023["hle_mean"].max()),
        },
        "gender_gap_global_2023": global_gap_2023,
        "top5_hle_2023" : top5,
        "bot5_hle_2023" : bot5,
        "missing_hle_rows": int(df["has_missing_hle"].sum()),
    }


# ===========================================================================
# S10 / S11 Summary
# ===========================================================================

def summarise_burden(df: pd.DataFrame, metric_label: str, metric_full: str) -> dict[str, Any]:
    """
    Generate a summary of S10 (DALY) or S11 (YLD) burden dataset.

    Parameters
    ----------
    df           : Cleaned burden DataFrame
    metric_label : Short label, e.g. 'daly' or 'yld'
    metric_full  : Full name for display
    """
    top_level   = df[df["cause_level_int"] == 0]
    all_causes  = top_level[top_level["cause"].str.lower() == "all causes"]

    total_count_2023 = _safe_float(
        all_causes["count_2023_mean"].values[0] if len(all_causes) > 0 else None
    )
    total_pct_change = _safe_float(
        all_causes["count_pct_mean"].values[0]  if len(all_causes) > 0 else None
    )

    # Level-1 causes (top categories)
    lvl1 = df[df["cause_level_int"] == 1][
        ["cause", "count_2023_mean", "count_pct_mean",
         "asr_2023_mean", "asr_pct_mean"]
    ].dropna(subset=["cause"]).copy()

    lvl1_sorted = lvl1.sort_values("count_2023_mean", ascending=False)
    lvl1_records = []
    for _, r in lvl1_sorted.iterrows():
        lvl1_records.append({
            "cause"           : r["cause"],
            "count_2023_mean" : _safe_float(r["count_2023_mean"]),
            "count_pct_change": _safe_float(r["count_pct_mean"]),
            "asr_2023_mean"   : _safe_float(r["asr_2023_mean"]),
            "asr_pct_change"  : _safe_float(r["asr_pct_mean"]),
        })

    return {
        "dataset"               : f"S{10 if metric_label == 'daly' else 11}",
        "title"                 : f"Global {metric_full} Counts and Age-Standardised Rate Changes",
        "metric"                : metric_full,
        "scope"                 : "Global, Both Sexes",
        "years_compared"        : [2010, 2023],
        "total_cause_rows"      : len(df),
        "cause_levels"          : sorted(df["cause_level_int"].unique().tolist()),
        "uncertainty_intervals" : True,
        "total_count_2023_mean" : total_count_2023,
        "total_count_pct_change": total_pct_change,
        "level1_causes"         : lvl1_records,
        "missing_count_rows"    : int(df["has_missing_counts"].sum()),
    }
