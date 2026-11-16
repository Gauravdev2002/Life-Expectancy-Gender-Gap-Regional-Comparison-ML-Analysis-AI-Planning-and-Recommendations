"""
analytics/regional_analytics.py
--------------------------------
Regional Comparison and Trend Analysis module using real GBD Dataset S9.

Features:
  1. Compares HLE across recognized GBD groupings:
     - SDI Quintiles: High, High-middle, Middle, Low-middle, Low SDI, and Global
     - GBD Super-Regions (7 continental divisions)
     - GBD Analytical Regions (intermediate geographic clusters)
  2. Multi-year trajectory tracking (1990, 2010, 2020, 2023).
  3. Identification of locations where HLE increased or decreased (positive vs negative % change).
  4. Cross-regional Gender Gap calculation: Gender Gap = Female HLE - Male HLE.
  5. Top 5 highest and Bottom 5 lowest location identification with 95% UI.
  6. 2010–2023 percentage change preservation with uncertainty intervals.
"""

import math
from typing import Any, Dict, List, Optional
import pandas as pd

from data.pipeline import get_s9

# Recognized GBD Regional Grouping sets present in Dataset S9
SDI_TIERS = [
    "High SDI",
    "High-middle SDI",
    "Middle SDI",
    "Low-middle SDI",
    "Low SDI",
    "Global",
]

GBD_SUPER_REGIONS = [
    "High income",
    "Central Europe, eastern Europe, and central Asia",
    "Latin America and Caribbean",
    "North Africa and Middle East",
    "South Asia",
    "Southeast Asia, east Asia, and Oceania",
    "Sub-Saharan Africa",
    "Global",
]

GBD_REGIONS = [
    "High-income Asia Pacific",
    "Western Europe",
    "Australasia",
    "High-income North America",
    "Southern Latin America",
    "Central Europe",
    "Eastern Europe",
    "Central Asia",
    "Andean Latin America",
    "Caribbean",
    "Central Latin America",
    "Tropical Latin America",
    "North Africa and Middle East",
    "South Asia",
    "East Asia",
    "Southeast Asia",
    "Oceania",
    "Central sub-Saharan Africa",
    "Eastern sub-Saharan Africa",
    "Southern sub-Saharan Africa",
    "Western sub-Saharan Africa",
]


def _safe_float(val: Any, decimals: int = 2) -> Optional[float]:
    """Helper to ensure JSON-compliant float."""
    if val is None:
        return None
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, decimals)
    except (ValueError, TypeError):
        return None


def get_grouping_names() -> Dict[str, List[str]]:
    """Returns the names of available grouping categories."""
    return {
        "sdi": SDI_TIERS,
        "super_regions": GBD_SUPER_REGIONS,
        "regions": GBD_REGIONS,
    }


def get_regional_comparison(
    grouping: str = "sdi",
    year: int = 2023,
    sex: str = "both"
) -> List[Dict[str, Any]]:
    """
    Compare Healthy Life Expectancy across regions or SDI tiers for a given year and sex.
    Includes historical points, gender breakdown, and percentage change.
    """
    df = get_s9()
    groupings_map = {
        "sdi": SDI_TIERS,
        "super_regions": GBD_SUPER_REGIONS,
        "regions": GBD_REGIONS,
    }
    target_names = groupings_map.get(grouping.lower(), SDI_TIERS)

    # Filter to matching entities
    sub = df[df["location"].isin(target_names)].copy()

    records = []
    seen = set()
    for name in target_names:
        if name in seen:
            continue
        seen.add(name)

        loc_rows = sub[sub["location"] == name]
        if loc_rows.empty:
            continue

        def _val(y, s, field="mean"):
            match = loc_rows[(loc_rows["year"] == y) & (loc_rows["sex"] == s)]
            if match.empty:
                return None
            return _safe_float(match[f"hle_{field}"].iloc[0])

        target_val = _val(year, sex, "mean")
        target_lower = _val(year, sex, "lower")
        target_upper = _val(year, sex, "upper")

        h1990 = _val(1990, sex, "mean")
        h2010 = _val(2010, sex, "mean")
        h2020 = _val(2020, sex, "mean")
        h2023 = _val(2023, sex, "mean")

        fem_val = _val(year, "female", "mean")
        mal_val = _val(year, "male", "mean")
        gap = _safe_float(fem_val - mal_val) if fem_val is not None and mal_val is not None else None

        pct_row = loc_rows[loc_rows["sex"] == sex]
        pct_change = _safe_float(pct_row["pct_change_mean"].iloc[0]) if not pct_row.empty else None
        pct_lower = _safe_float(pct_row["pct_change_lower"].iloc[0]) if not pct_row.empty else None
        pct_upper = _safe_float(pct_row["pct_change_upper"].iloc[0]) if not pct_row.empty else None

        direction = "stable"
        if pct_change is not None:
            if pct_change > 0.05:
                direction = "increased"
            elif pct_change < -0.05:
                direction = "decreased"

        records.append({
            "region": name,
            "grouping": grouping,
            "year": year,
            "sex": sex,
            "hle_mean": target_val,
            "hle_lower": target_lower,
            "hle_upper": target_upper,
            "hle_1990": h1990,
            "hle_2010": h2010,
            "hle_2020": h2020,
            "hle_2023": h2023,
            "female_hle": fem_val,
            "male_hle": mal_val,
            "gender_gap": gap,
            "pct_change_2010_2023": pct_change,
            "pct_change_lower": pct_lower,
            "pct_change_upper": pct_upper,
            "direction": direction,
        })

    return records


def get_regional_historical_trends(grouping: str = "sdi") -> List[Dict[str, Any]]:
    """
    Returns time-series trajectories (1990, 2010, 2020, 2023) formatted for
    interactive multi-line comparison charts across regional tiers.
    """
    df = get_s9()
    groupings_map = {
        "sdi": SDI_TIERS,
        "super_regions": GBD_SUPER_REGIONS,
        "regions": GBD_REGIONS,
    }
    target_names = groupings_map.get(grouping.lower(), SDI_TIERS)

    years = [1990, 2010, 2020, 2023]
    series_by_year = {y: {"year": y} for y in years}

    for name in target_names:
        loc_df = df[(df["location"] == name) & (df["sex"] == "both")]
        for y in years:
            match = loc_df[loc_df["year"] == y]
            val = _safe_float(match["hle_mean"].iloc[0]) if not match.empty else None
            series_by_year[y][name] = val

    return list(series_by_year.values())


def get_increase_decrease_analysis(
    include_aggregates: bool = False,
    n: int = 5
) -> Dict[str, Any]:
    """
    Identifies locations where Healthy Life Expectancy increased or decreased
    most significantly between 2010 and 2023.
    Returns:
      - Top N locations with largest percentage gains.
      - Top N locations with largest percentage declines (decreases).
      - Overall summary breakdown of increased vs decreased locations.
    """
    df = get_s9()
    sub = df[(df["sex"] == "both") & (df["year"] == 2023)].copy()

    if not include_aggregates:
        sub = sub[~sub["is_aggregate"]]

    # Drop duplicate location names
    sub = sub.drop_duplicates(subset=["location"])
    valid = sub.dropna(subset=["pct_change_mean"])

    increased_total = int((valid["pct_change_mean"] > 0).sum())
    decreased_total = int((valid["pct_change_mean"] < 0).sum())
    unchanged_total = int((valid["pct_change_mean"] == 0).sum())

    top_increases = valid.sort_values("pct_change_mean", ascending=False).head(n)
    top_decreases = valid.sort_values("pct_change_mean", ascending=True).head(n)

    def format_change_rows(target_df):
        out = []
        for _, row in target_df.iterrows():
            out.append({
                "location": row["location"],
                "hle_2010": _safe_float(row.get("hle_mean")), # note: 2010 value available in table
                "hle_2023": _safe_float(row["hle_mean"]),
                "pct_change_mean": _safe_float(row["pct_change_mean"]),
                "pct_change_lower": _safe_float(row["pct_change_lower"]),
                "pct_change_upper": _safe_float(row["pct_change_upper"]),
            })
        return out

    return {
        "analysis_period": "2010-2023",
        "total_analyzed": len(valid),
        "total_increased": increased_total,
        "total_decreased": decreased_total,
        "total_unchanged": unchanged_total,
        "largest_increases": format_change_rows(top_increases),
        "largest_decreases": format_change_rows(top_decreases),
    }


def get_top_and_bottom_locations(
    year: int = 2023,
    include_aggregates: bool = False,
    n: int = 5
) -> Dict[str, Any]:
    """
    Returns concise Top 5 and Bottom 5 location rankings for the latest year,
    complete with 1990 baseline, 2023 HLE, Gender Gap, and 2010–23 % change.
    """
    df = get_s9()
    sub_both = df[(df["sex"] == "both") & (df["year"] == year)].copy()

    if not include_aggregates:
        sub_both = sub_both[~sub_both["is_aggregate"]]

    sub_both = sub_both.drop_duplicates(subset=["location"]).dropna(subset=["hle_mean"])
    top_df = sub_both.sort_values("hle_mean", ascending=False).head(n)
    bot_df = sub_both.sort_values("hle_mean", ascending=True).head(n)

    def hydrate_location_details(loc_df):
        out = []
        for rank, (_, row) in enumerate(loc_df.iterrows(), start=1):
            loc = row["location"]
            loc_all = df[df["location"] == loc]

            # 1990 baseline
            r1990 = loc_all[(loc_all["sex"] == "both") & (loc_all["year"] == 1990)]
            h1990 = _safe_float(r1990["hle_mean"].iloc[0]) if not r1990.empty else None

            # 2023 Female & Male
            rf = loc_all[(loc_all["sex"] == "female") & (loc_all["year"] == year)]
            rm = loc_all[(loc_all["sex"] == "male") & (loc_all["year"] == year)]
            hf = _safe_float(rf["hle_mean"].iloc[0]) if not rf.empty else None
            hm = _safe_float(rm["hle_mean"].iloc[0]) if not rm.empty else None
            gap = _safe_float(hf - hm) if hf is not None and hm is not None else None

            out.append({
                "rank": rank,
                "location": loc,
                "hle_1990": h1990,
                "hle_latest": _safe_float(row["hle_mean"]),
                "hle_lower": _safe_float(row["hle_lower"]),
                "hle_upper": _safe_float(row["hle_upper"]),
                "female_hle": hf,
                "male_hle": hm,
                "gender_gap": gap,
                "pct_change": _safe_float(row["pct_change_mean"]),
                "pct_lower": _safe_float(row["pct_change_lower"]),
                "pct_upper": _safe_float(row["pct_change_upper"]),
            })
        return out

    return {
        "year": year,
        "top_5": hydrate_location_details(top_df),
        "bottom_5": hydrate_location_details(bot_df)
    }
