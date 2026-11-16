"""
analytics/gender_analytics.py
-----------------------------
Specialized analytical module for Gender Health Inequality in Life Expectancy.
Computes Female HLE, Male HLE, Gender Gap (Female HLE - Male HLE),
Parity Ratio (Female / Male), historical trends (1990-2023), and SDI disparities.

All calculations derive directly from the cleaned Dataset S9.
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from data.pipeline import get_s9

SDI_LEVELS = ["Low SDI", "Low-middle SDI", "Middle SDI", "High-middle SDI", "High SDI"]


def _safe_float(val: Any, decimals: int = 2) -> Optional[float]:
    if val is None:
        return None
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, decimals)
    except (ValueError, TypeError):
        return None


def get_gender_gap_overview(year: int = 2023) -> Dict[str, Any]:
    """
    Computes global benchmark, SDI gradient, and summary statistics
    for the Gender Gap (Female HLE - Male HLE) for the specified year.
    """
    df = get_s9()
    sub = df[df["year"] == year].copy()

    # Global Benchmark
    g_fem = sub[(sub["location"] == "Global") & (sub["sex"] == "female")]
    g_mal = sub[(sub["location"] == "Global") & (sub["sex"] == "male")]

    global_f = g_fem["hle_mean"].values[0] if not g_fem.empty else None
    global_m = g_mal["hle_mean"].values[0] if not g_mal.empty else None
    global_gap = (global_f - global_m) if (global_f is not None and global_m is not None) else None
    parity_ratio = (global_f / global_m) if (global_f and global_m and global_m > 0) else None

    # SDI Quintiles Gender Gap
    sdi_data = []
    for sdi in SDI_LEVELS:
        s_fem = sub[(sub["location"] == sdi) & (sub["sex"] == "female")]
        s_mal = sub[(sub["location"] == sdi) & (sub["sex"] == "male")]
        f_val = s_fem["hle_mean"].values[0] if not s_fem.empty else None
        m_val = s_mal["hle_mean"].values[0] if not s_mal.empty else None
        gap = (f_val - m_val) if (f_val is not None and m_val is not None) else None
        sdi_data.append({
            "sdi_level": sdi,
            "female_hle": _safe_float(f_val),
            "male_hle": _safe_float(m_val),
            "gender_gap": _safe_float(gap),
        })

    # Historical Global Trajectory (1990, 2010, 2020, 2023)
    history = []
    for y in [1990, 2010, 2020, 2023]:
        y_fem = df[(df["location"] == "Global") & (df["sex"] == "female") & (df["year"] == y)]
        y_mal = df[(df["location"] == "Global") & (df["sex"] == "male") & (df["year"] == y)]
        f_v = y_fem["hle_mean"].values[0] if not y_fem.empty else None
        m_v = y_mal["hle_mean"].values[0] if not y_mal.empty else None
        g_v = (f_v - m_v) if (f_v is not None and m_v is not None) else None
        history.append({
            "year": y,
            "female_hle": _safe_float(f_v),
            "male_hle": _safe_float(m_v),
            "gender_gap": _safe_float(g_v),
        })

    # Country-level Distribution (exclude aggregates)
    countries_df = sub[~sub["is_aggregate"]].copy()
    fem_c = countries_df[countries_df["sex"] == "female"].set_index("location")
    mal_c = countries_df[countries_df["sex"] == "male"].set_index("location")
    joined = fem_c.join(mal_c, suffixes=("_f", "_m"), how="inner").dropna(subset=["hle_mean_f", "hle_mean_m"])
    joined["gap"] = joined["hle_mean_f"] - joined["hle_mean_m"]
    # Drop duplicate location names
    joined = joined[~joined.index.duplicated(keep="first")]

    widest = joined.sort_values("gap", ascending=False).iloc[0] if not joined.empty else None
    narrowest = joined.sort_values("gap", ascending=True).iloc[0] if not joined.empty else None

    distribution = {
        "mean_gap": _safe_float(joined["gap"].mean()),
        "median_gap": _safe_float(joined["gap"].median()),
        "min_gap": _safe_float(joined["gap"].min()),
        "max_gap": _safe_float(joined["gap"].max()),
        "countries_with_female_advantage": int((joined["gap"] > 0).sum()),
        "countries_with_male_advantage": int((joined["gap"] < 0).sum()),
        "total_countries": len(joined),
        "widest_country": {
            "location": str(widest.name) if widest is not None else None,
            "gap": _safe_float(widest["gap"]) if widest is not None else None,
            "female_hle": _safe_float(widest["hle_mean_f"]) if widest is not None else None,
            "male_hle": _safe_float(widest["hle_mean_m"]) if widest is not None else None,
        } if widest is not None else None,
        "narrowest_country": {
            "location": str(narrowest.name) if narrowest is not None else None,
            "gap": _safe_float(narrowest["gap"]) if narrowest is not None else None,
            "female_hle": _safe_float(narrowest["hle_mean_f"]) if narrowest is not None else None,
            "male_hle": _safe_float(narrowest["hle_mean_m"]) if narrowest is not None else None,
        } if narrowest is not None else None,
    }

    return {
        "year": year,
        "global_female_hle": _safe_float(global_f),
        "global_male_hle": _safe_float(global_m),
        "global_gender_gap": _safe_float(global_gap),
        "global_parity_ratio": _safe_float(parity_ratio, 3),
        "sdi_gradient": sdi_data,
        "historical_trajectory": history,
        "country_distribution": distribution,
    }


def get_gender_rankings(year: int = 2023, n: int = 10) -> Dict[str, Any]:
    """
    Returns top N locations with largest female advantage (widest positive gap)
    and top N locations with narrowest gap or male advantage.
    """
    df = get_s9()
    sub = df[(df["year"] == year) & (~df["is_aggregate"])].copy()

    fem = sub[sub["sex"] == "female"].set_index("location")
    mal = sub[sub["sex"] == "male"].set_index("location")

    joined = fem.join(mal, suffixes=("_f", "_m"), how="inner").dropna(subset=["hle_mean_f", "hle_mean_m"])
    joined["gap"] = joined["hle_mean_f"] - joined["hle_mean_m"]
    joined["parity_ratio"] = joined["hle_mean_f"] / joined["hle_mean_m"]
    joined = joined[~joined.index.duplicated(keep="first")]

    widest_df = joined.sort_values("gap", ascending=False).head(n)
    narrowest_df = joined.sort_values("gap", ascending=True).head(n)

    def _format(tdf):
        out = []
        for loc, row in tdf.iterrows():
            out.append({
                "location": str(loc),
                "female_hle": _safe_float(row["hle_mean_f"]),
                "female_lower": _safe_float(row["hle_lower_f"]),
                "female_upper": _safe_float(row["hle_upper_f"]),
                "male_hle": _safe_float(row["hle_mean_m"]),
                "male_lower": _safe_float(row["hle_lower_m"]),
                "male_upper": _safe_float(row["hle_upper_m"]),
                "gender_gap": _safe_float(row["gap"]),
                "parity_ratio": _safe_float(row["parity_ratio"], 3),
            })
        return out

    return {
        "year": year,
        "widest_female_advantage": _format(widest_df),
        "narrowest_or_reverse_gap": _format(narrowest_df),
    }


def get_gender_scatter_data(year: int = 2023, max_points: int = 200) -> List[Dict[str, Any]]:
    """
    Generates data points for Female HLE vs Male HLE scatter plot with parity reference.
    """
    df = get_s9()
    sub = df[(df["year"] == year) & (~df["is_aggregate"])].copy()

    fem = sub[sub["sex"] == "female"].set_index("location")
    mal = sub[sub["sex"] == "male"].set_index("location")

    joined = fem.join(mal, suffixes=("_f", "_m"), how="inner").dropna(subset=["hle_mean_f", "hle_mean_m"])
    joined["gap"] = joined["hle_mean_f"] - joined["hle_mean_m"]
    joined = joined[~joined.index.duplicated(keep="first")]

    # Sample if greater than max_points, but keep extremes
    if len(joined) > max_points:
        joined = joined.sort_values("gap")
        indices = np.linspace(0, len(joined) - 1, max_points, dtype=int)
        joined = joined.iloc[indices]

    pts = []
    for loc, row in joined.iterrows():
        f = _safe_float(row["hle_mean_f"])
        m = _safe_float(row["hle_mean_m"])
        gap = _safe_float(row["gap"])
        pts.append({
            "location": str(loc),
            "female_hle": f,
            "male_hle": m,
            "gender_gap": gap,
            "equality_reference": m,  # y=x line
        })
    return pts


def get_gender_comparison_table(
    year: int = 2023,
    search: Optional[str] = None,
    sort_by: str = "gender_gap",
    sort_asc: bool = False,
    page: int = 1,
    page_size: int = 15,
) -> Dict[str, Any]:
    """
    Paginated, searchable table of all locations comparing female and male HLE.
    """
    df = get_s9()
    sub = df[(df["year"] == year) & (~df["is_aggregate"])].copy()

    fem = sub[sub["sex"] == "female"].set_index("location")
    mal = sub[sub["sex"] == "male"].set_index("location")

    joined = fem.join(mal, suffixes=("_f", "_m"), how="inner").dropna(subset=["hle_mean_f", "hle_mean_m"])
    joined["gender_gap"] = joined["hle_mean_f"] - joined["hle_mean_m"]
    joined["parity_ratio"] = joined["hle_mean_f"] / joined["hle_mean_m"]
    joined = joined[~joined.index.duplicated(keep="first")].reset_index()

    if search:
        s = search.strip().lower()
        joined = joined[joined["location"].str.lower().str.contains(s, na=False)]

    # Sorting
    sort_col_map = {
        "gender_gap": "gender_gap",
        "female_hle": "hle_mean_f",
        "male_hle": "hle_mean_m",
        "parity_ratio": "parity_ratio",
        "location": "location",
    }
    col = sort_col_map.get(sort_by, "gender_gap")
    joined = joined.sort_values(by=col, ascending=sort_asc)

    total_records = len(joined)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged = joined.iloc[start_idx:end_idx]

    records = []
    for _, row in paged.iterrows():
        records.append({
            "location": row["location"],
            "female_hle": _safe_float(row["hle_mean_f"]),
            "female_lower": _safe_float(row["hle_lower_f"]),
            "female_upper": _safe_float(row["hle_upper_f"]),
            "male_hle": _safe_float(row["hle_mean_m"]),
            "male_lower": _safe_float(row["hle_lower_m"]),
            "male_upper": _safe_float(row["hle_upper_m"]),
            "gender_gap": _safe_float(row["gender_gap"]),
            "parity_ratio": _safe_float(row["parity_ratio"], 3),
        })

    return {
        "total": total_records,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total_records / page_size) if page_size > 0 else 1,
        "records": records,
    }
