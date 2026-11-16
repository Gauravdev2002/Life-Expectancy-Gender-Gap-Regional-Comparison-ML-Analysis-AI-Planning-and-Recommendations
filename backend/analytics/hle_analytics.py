"""
analytics/hle_analytics.py
--------------------------
Core analytical module for Healthy Life Expectancy (HLE) calculations using Dataset S9.

All functions operate strictly on the cleaned Dataset S9 from the data pipeline.
Features:
  1. Multi-year comparison (1990, 2010, 2020, 2023).
  2. Gender-disaggregated analysis (Both Sexes, Female, Male).
  3. Precise Gender Gap calculation: Gender Gap = Female HLE - Male HLE.
  4. Ranking identification (highest and lowest HLE locations).
  5. 2010-2023 percentage change analysis preserving uncertainty bounds (Lower, Upper).
  6. Robust handling of missing values without synthetic fabrication.
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from data.pipeline import get_s9


def _safe_float(val: Any, decimals: int = 2) -> Optional[float]:
    """Helper to ensure JSON-compliant float (no NaN or inf)."""
    if val is None:
        return None
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, decimals)
    except (ValueError, TypeError):
        return None


def get_available_locations(include_aggregates: bool = True) -> List[str]:
    """Returns sorted unique location names available in S9."""
    df = get_s9()
    if not include_aggregates:
        df = df[~df["is_aggregate"]]
    return sorted(df["location"].dropna().unique().tolist())


def get_location_trend(location: str) -> Dict[str, Any]:
    """
    Get year-wise HLE trajectory for a specific location across all 4 years
    (1990, 2010, 2020, 2023) for Both Sexes, Female, and Male,
    including the calculated Gender Gap and 2010-2023 percentage change.
    """
    df = get_s9()
    loc_df = df[df["location"].str.lower() == location.strip().lower()]

    if loc_df.empty:
        # Fallback to Global if location not found
        loc_df = df[df["location"].str.lower() == "global"]
        location = "Global"

    actual_loc_name = loc_df["location"].iloc[0]
    is_aggregate = bool(loc_df["is_aggregate"].iloc[0])

    years = [1990, 2010, 2020, 2023]
    trends = []

    for y in years:
        row_both = loc_df[(loc_df["sex"] == "both") & (loc_df["year"] == y)]
        row_f = loc_df[(loc_df["sex"] == "female") & (loc_df["year"] == y)]
        row_m = loc_df[(loc_df["sex"] == "male") & (loc_df["year"] == y)]

        both_mean = row_both["hle_mean"].values[0] if not row_both.empty else None
        both_lower = row_both["hle_lower"].values[0] if not row_both.empty else None
        both_upper = row_both["hle_upper"].values[0] if not row_both.empty else None

        f_mean = row_f["hle_mean"].values[0] if not row_f.empty else None
        f_lower = row_f["hle_lower"].values[0] if not row_f.empty else None
        f_upper = row_f["hle_upper"].values[0] if not row_f.empty else None

        m_mean = row_m["hle_mean"].values[0] if not row_m.empty else None
        m_lower = row_m["hle_lower"].values[0] if not row_m.empty else None
        m_upper = row_m["hle_upper"].values[0] if not row_m.empty else None

        gender_gap = None
        if f_mean is not None and m_mean is not None:
            gender_gap = f_mean - m_mean

        trends.append({
            "year": y,
            "both_mean": _safe_float(both_mean),
            "both_lower": _safe_float(both_lower),
            "both_upper": _safe_float(both_upper),
            "female_mean": _safe_float(f_mean),
            "female_lower": _safe_float(f_lower),
            "female_upper": _safe_float(f_upper),
            "male_mean": _safe_float(m_mean),
            "male_lower": _safe_float(m_lower),
            "male_upper": _safe_float(m_upper),
            "gender_gap": _safe_float(gender_gap),
        })

    # Percentage change 2010-2023 directly from dataset
    pct_both_row = loc_df[loc_df["sex"] == "both"]
    pct_both_mean = pct_both_row["pct_change_mean"].iloc[0] if not pct_both_row.empty else None
    pct_both_lower = pct_both_row["pct_change_lower"].iloc[0] if not pct_both_row.empty else None
    pct_both_upper = pct_both_row["pct_change_upper"].iloc[0] if not pct_both_row.empty else None

    pct_f_row = loc_df[loc_df["sex"] == "female"]
    pct_f_mean = pct_f_row["pct_change_mean"].iloc[0] if not pct_f_row.empty else None
    pct_f_lower = pct_f_row["pct_change_lower"].iloc[0] if not pct_f_row.empty else None
    pct_f_upper = pct_f_row["pct_change_upper"].iloc[0] if not pct_f_row.empty else None

    pct_m_row = loc_df[loc_df["sex"] == "male"]
    pct_m_mean = pct_m_row["pct_change_mean"].iloc[0] if not pct_m_row.empty else None
    pct_m_lower = pct_m_row["pct_change_lower"].iloc[0] if not pct_m_row.empty else None
    pct_m_upper = pct_m_row["pct_change_upper"].iloc[0] if not pct_m_row.empty else None

    # Summary metrics for quick KPI cards
    y1990 = next((t for t in trends if t["year"] == 1990), {})
    y2023 = next((t for t in trends if t["year"] == 2023), {})

    net_change_1990_2023 = None
    if y2023.get("both_mean") is not None and y1990.get("both_mean") is not None:
        net_change_1990_2023 = _safe_float(y2023["both_mean"] - y1990["both_mean"])

    return {
        "location": actual_loc_name,
        "is_aggregate": is_aggregate,
        "trend": trends,
        "summary": {
            "hle_2023_mean": y2023.get("both_mean"),
            "hle_2023_lower": y2023.get("both_lower"),
            "hle_2023_upper": y2023.get("both_upper"),
            "hle_1990_mean": y1990.get("both_mean"),
            "net_change_1990_2023": net_change_1990_2023,
            "female_hle_2023": y2023.get("female_mean"),
            "male_hle_2023": y2023.get("male_mean"),
            "gender_gap_2023": y2023.get("gender_gap"),
            "pct_change_2010_2023_mean": _safe_float(pct_both_mean),
            "pct_change_2010_2023_lower": _safe_float(pct_both_lower),
            "pct_change_2010_2023_upper": _safe_float(pct_both_upper),
            "pct_change_female": _safe_float(pct_f_mean),
            "pct_change_male": _safe_float(pct_m_mean),
        }
    }


def get_hle_comparison(
    locations: Optional[List[str]] = None,
    year: int = 2023,
    sex: str = "both"
) -> List[Dict[str, Any]]:
    """
    Compare Healthy Life Expectancy across a specified list of locations for a given year and sex.
    Defaults to global SDI quintiles and key benchmarks if no locations specified.
    """
    df = get_s9()
    if locations is None or len(locations) == 0:
        locations = [
            "Global", "High SDI", "High-middle SDI", "Middle SDI",
            "Low-middle SDI", "Low SDI", "Japan", "Singapore",
            "United States of America", "India", "China", "Nigeria"
        ]

    # Map possible naming variations (e.g. USA vs United States of America)
    loc_lower = [l.strip().lower() for l in locations]
    filtered = df[(df["year"] == year) & (df["sex"] == sex) & (df["location"].str.lower().isin(loc_lower))]

    # Deduplicate in case multiple records match
    seen = set()
    records = []
    for _, r in filtered.iterrows():
        loc = r["location"]
        if loc in seen:
            continue
        seen.add(loc)
        records.append({
            "location": loc,
            "year": int(r["year"]),
            "sex": str(r["sex"]),
            "is_aggregate": bool(r["is_aggregate"]),
            "hle_mean": _safe_float(r["hle_mean"]),
            "hle_lower": _safe_float(r["hle_lower"]),
            "hle_upper": _safe_float(r["hle_upper"]),
            "pct_change_mean": _safe_float(r["pct_change_mean"]),
            "pct_change_lower": _safe_float(r["pct_change_lower"]),
            "pct_change_upper": _safe_float(r["pct_change_upper"]),
        })

    # Sort descending by hle_mean
    records.sort(key=lambda x: (x["hle_mean"] if x["hle_mean"] is not None else -999), reverse=True)
    return records


def get_hle_rankings(
    year: int = 2023,
    sex: str = "both",
    include_aggregates: bool = False,
    n: int = 10
) -> Dict[str, Any]:
    """
    Identifies the top N and bottom N locations by Healthy Life Expectancy
    with complete uncertainty bounds.
    """
    df = get_s9()
    filtered = df[(df["year"] == year) & (df["sex"] == sex)].copy()

    if not include_aggregates:
        filtered = filtered[~filtered["is_aggregate"]]

    # Drop duplicate name entries keeping highest
    filtered = filtered.sort_values("hle_mean", ascending=False).drop_duplicates(subset=["location"])
    valid = filtered.dropna(subset=["hle_mean"])

    top_n_df = valid.head(n)
    bot_n_df = valid.tail(n).iloc[::-1]  # lowest first

    def format_rows(sub_df):
        res = []
        for rank, (_, row) in enumerate(sub_df.iterrows(), start=1):
            res.append({
                "rank": rank,
                "location": row["location"],
                "hle_mean": _safe_float(row["hle_mean"]),
                "hle_lower": _safe_float(row["hle_lower"]),
                "hle_upper": _safe_float(row["hle_upper"]),
                "pct_change_mean": _safe_float(row["pct_change_mean"]),
            })
        return res

    return {
        "year": year,
        "sex": sex,
        "total_analyzed": len(valid),
        "highest": format_rows(top_n_df),
        "lowest": format_rows(bot_n_df)
    }


def get_gender_gap_analysis(
    year: int = 2023,
    include_aggregates: bool = False,
    n: int = 10
) -> Dict[str, Any]:
    """
    Analyzes the Gender Gap (Female HLE - Male HLE) across locations.
    Returns:
      - Top N locations with largest female advantage (positive gap).
      - Top N locations with narrowest gap or male advantage.
      - Global gender gap benchmark.
    """
    df = get_s9()
    sub = df[df["year"] == year].copy()

    # Calculate global benchmark
    g_fem = sub[(sub["location"] == "Global") & (sub["sex"] == "female")]["hle_mean"]
    g_mal = sub[(sub["location"] == "Global") & (sub["sex"] == "male")]["hle_mean"]
    global_gap = _safe_float(g_fem.values[0] - g_mal.values[0]) if not g_fem.empty and not g_mal.empty else None

    if not include_aggregates:
        sub = sub[~sub["is_aggregate"]]

    fem = sub[sub["sex"] == "female"].set_index("location")
    mal = sub[sub["sex"] == "male"].set_index("location")

    joined = fem.join(mal, suffixes=("_f", "_m"), how="inner").dropna(subset=["hle_mean_f", "hle_mean_m"])
    joined["gender_gap"] = joined["hle_mean_f"] - joined["hle_mean_m"]

    # Remove duplicate location index names if any
    joined = joined[~joined.index.duplicated(keep="first")]

    widest_df = joined.sort_values("gender_gap", ascending=False).head(n)
    narrowest_df = joined.sort_values("gender_gap", ascending=True).head(n)

    def format_gap_rows(target_df):
        out = []
        for loc, row in target_df.iterrows():
            out.append({
                "location": str(loc),
                "female_hle": _safe_float(row["hle_mean_f"]),
                "female_lower": _safe_float(row["hle_lower_f"]),
                "female_upper": _safe_float(row["hle_upper_f"]),
                "male_hle": _safe_float(row["hle_mean_m"]),
                "male_lower": _safe_float(row["hle_lower_m"]),
                "male_upper": _safe_float(row["hle_upper_m"]),
                "gender_gap": _safe_float(row["gender_gap"]),
            })
        return out

    return {
        "year": year,
        "global_gender_gap": global_gap,
        "widest_female_advantage": format_gap_rows(widest_df),
        "narrowest_or_reverse_gap": format_gap_rows(narrowest_df)
    }


def get_comprehensive_location_table(
    search: Optional[str] = None,
    include_aggregates: bool = True,
    sort_by: str = "hle_2023",
    sort_asc: bool = False,
    page: int = 1,
    page_size: int = 25
) -> Dict[str, Any]:
    """
    Builds a consolidated multi-year, gender-disaggregated data table for all locations.
    Enables interactive frontend sorting, filtering, and pagination.
    """
    df = get_s9()
    if not include_aggregates:
        df = df[~df["is_aggregate"]]

    locs = df["location"].drop_duplicates()
    if search:
        locs = locs[locs.str.lower().str.contains(search.strip().lower(), na=False)]

    records = []
    for loc in locs:
        sub_loc = df[df["location"] == loc]
        is_agg = bool(sub_loc["is_aggregate"].iloc[0])

        def _val(y, s, field="mean"):
            match = sub_loc[(sub_loc["year"] == y) & (sub_loc["sex"] == s)]
            if match.empty:
                return None
            return _safe_float(match[f"hle_{field}"].iloc[0])

        h1990 = _val(1990, "both")
        h2010 = _val(2010, "both")
        h2020 = _val(2020, "both")
        h2023 = _val(2023, "both")

        h2023_lower = _val(2023, "both", "lower")
        h2023_upper = _val(2023, "both", "upper")

        h2023_f = _val(2023, "female")
        h2023_m = _val(2023, "male")

        gap_2023 = None
        if h2023_f is not None and h2023_m is not None:
            gap_2023 = _safe_float(h2023_f - h2023_m)

        pct_match = sub_loc[sub_loc["sex"] == "both"]
        pct_change = _safe_float(pct_match["pct_change_mean"].iloc[0]) if not pct_match.empty else None
        pct_lower = _safe_float(pct_match["pct_change_lower"].iloc[0]) if not pct_match.empty else None
        pct_upper = _safe_float(pct_match["pct_change_upper"].iloc[0]) if not pct_match.empty else None

        records.append({
            "location": loc,
            "is_aggregate": is_agg,
            "hle_1990": h1990,
            "hle_2010": h2010,
            "hle_2020": h2020,
            "hle_2023": h2023,
            "hle_2023_lower": h2023_lower,
            "hle_2023_upper": h2023_upper,
            "female_hle_2023": h2023_f,
            "male_hle_2023": h2023_m,
            "gender_gap_2023": gap_2023,
            "pct_change_2010_2023": pct_change,
            "pct_change_lower": pct_lower,
            "pct_change_upper": pct_upper,
        })

    # Sorting
    def sort_key(item):
        val = item.get(sort_by)
        if val is None:
            return -999999 if not sort_asc else 999999
        return val

    records.sort(key=sort_key, reverse=not sort_asc)

    total_count = len(records)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_records = records[start_idx:end_idx]

    return {
        "total_records": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total_count / page_size) if page_size > 0 else 1,
        "records": paginated_records
    }
