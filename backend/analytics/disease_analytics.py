"""
analytics/disease_analytics.py
------------------------------
Specialized analytical module for Global Disease Burden using Datasets S10 (DALYs)
and S11 (YLDs).

Key Principles:
  1. Operates exclusively on cleaned Global Datasets S10 (DALYs) and S11 (YLDs).
  2. STRICT DEMOGRAPHIC SEPARATION: S10 and S11 are global both-sexes cause-level
     datasets and are NEVER merged with location-level S9 records.
  3. DALY = Disability-Adjusted Life Years (Premature mortality YLL + Disability YLD).
  4. YLD = Years Lived with Disability (pure non-fatal morbidity burden).
  5. Preserves all 95% uncertainty intervals (Lower, Upper) and 2010-2023 percentage changes.
"""

import math
from typing import Any, Dict, List, Optional
import pandas as pd

from data.pipeline import get_s10, get_s11


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


def get_disease_burden_overview() -> Dict[str, Any]:
    """
    Computes global totals and overarching epidemiological transition metrics
    for both DALYs (S10) and YLDs (S11).
    """
    s10 = get_s10()
    s11 = get_s11()

    # Level 0 (All causes)
    daly_all = s10[s10["cause_level_int"] == 0].iloc[0] if not s10[s10["cause_level_int"] == 0].empty else None
    yld_all = s11[s11["cause_level_int"] == 0].iloc[0] if not s11[s11["cause_level_int"] == 0].empty else None

    # Top Level 2 cause for each
    s10_l2 = s10[s10["cause_level_int"] == 2].sort_values("count_2023_mean", ascending=False)
    s11_l2 = s11[s11["cause_level_int"] == 2].sort_values("count_2023_mean", ascending=False)

    top_daly = s10_l2.iloc[0] if not s10_l2.empty else None
    top_yld = s11_l2.iloc[0] if not s11_l2.empty else None

    # Non-fatal fraction: Global YLD / Global DALY (disability proportion of total burden)
    disability_ratio = None
    if daly_all is not None and yld_all is not None:
        d_val = daly_all["count_2023_mean"]
        y_val = yld_all["count_2023_mean"]
        if d_val and d_val > 0:
            disability_ratio = (y_val / d_val) * 100.0

    return {
        "daly_summary": {
            "metric": "DALYs (Disability-Adjusted Life Years)",
            "description": "Total health loss combining premature mortality (YLL) and non-fatal disability (YLD).",
            "count_2023_mean": _safe_float(daly_all["count_2023_mean"]) if daly_all is not None else None,
            "count_2023_lower": _safe_float(daly_all["count_2023_lower"]) if daly_all is not None else None,
            "count_2023_upper": _safe_float(daly_all["count_2023_upper"]) if daly_all is not None else None,
            "asr_2023_mean": _safe_float(daly_all["asr_2023_mean"]) if daly_all is not None else None,
            "asr_2023_lower": _safe_float(daly_all["asr_2023_lower"]) if daly_all is not None else None,
            "asr_2023_upper": _safe_float(daly_all["asr_2023_upper"]) if daly_all is not None else None,
            "asr_pct_change": _safe_float(daly_all["asr_pct_mean"]) if daly_all is not None else None,
            "leading_cause": top_daly["cause"] if top_daly is not None else None,
            "leading_cause_count": _safe_float(top_daly["count_2023_mean"]) if top_daly is not None else None,
        },
        "yld_summary": {
            "metric": "YLDs (Years Lived with Disability)",
            "description": "Direct measure of chronic non-fatal morbidity and living with health conditions.",
            "count_2023_mean": _safe_float(yld_all["count_2023_mean"]) if yld_all is not None else None,
            "count_2023_lower": _safe_float(yld_all["count_2023_lower"]) if yld_all is not None else None,
            "count_2023_upper": _safe_float(yld_all["count_2023_upper"]) if yld_all is not None else None,
            "asr_2023_mean": _safe_float(yld_all["asr_2023_mean"]) if yld_all is not None else None,
            "asr_2023_lower": _safe_float(yld_all["asr_2023_lower"]) if yld_all is not None else None,
            "asr_2023_upper": _safe_float(yld_all["asr_2023_upper"]) if yld_all is not None else None,
            "asr_pct_change": _safe_float(yld_all["asr_pct_mean"]) if yld_all is not None else None,
            "leading_cause": top_yld["cause"] if top_yld is not None else None,
            "leading_cause_count": _safe_float(top_yld["count_2023_mean"]) if top_yld is not None else None,
        },
        "disability_share_percent": _safe_float(disability_ratio, 1),
    }


def get_level1_broad_breakdown() -> Dict[str, Any]:
    """
    Calculates the distribution of the 3 major Level-1 cause categories
    for both DALYs and YLDs in 2023:
      1. Communicable, maternal, neonatal, and nutritional diseases
      2. Non-communicable diseases (NCDs)
      3. Injuries
    """
    s10 = get_s10()
    s11 = get_s11()

    def _extract_l1(df, metric_key):
        l1 = df[df["cause_level_int"] == 1].copy()
        total_counts = l1["count_2023_mean"].sum()
        res = []
        for _, row in l1.iterrows():
            c = row["count_2023_mean"]
            pct = (c / total_counts * 100.0) if (total_counts and total_counts > 0) else None
            res.append({
                "cause": row["cause"],
                "short_name": (
                    "Communicable & Maternal" if "Communicable" in row["cause"]
                    else "Non-Communicable (NCDs)" if "Non-communicable" in row["cause"]
                    else "Injuries"
                ),
                "metric": metric_key,
                "count_2023": _safe_float(c),
                "share_percent": _safe_float(pct, 1),
                "asr_2023": _safe_float(row["asr_2023_mean"]),
                "asr_pct_change": _safe_float(row["asr_pct_mean"]),
            })
        return res

    return {
        "daly_categories": _extract_l1(s10, "DALYs"),
        "yld_categories": _extract_l1(s11, "YLDs"),
    }


def get_top_causes(
    metric: str = "daly",
    level: int = 2,
    n: int = 10,
    sort_by: str = "count_2023_mean",
) -> List[Dict[str, Any]]:
    """
    Returns top N causes for DALYs or YLDs at the specified hierarchy level (default Level 2).
    """
    df = get_s10() if metric.lower() == "daly" else get_s11()
    sub = df[df["cause_level_int"] == level].copy()

    col = "asr_2023_mean" if sort_by == "asr" else "count_2023_mean"
    sub = sub.sort_values(by=col, ascending=False).head(n)

    out = []
    for rank, (_, row) in enumerate(sub.iterrows(), start=1):
        out.append({
            "rank": rank,
            "cause": row["cause"],
            "level": int(row["cause_level_int"]),
            "count_2010_mean": _safe_float(row["count_2010_mean"]),
            "count_2023_mean": _safe_float(row["count_2023_mean"]),
            "count_2023_lower": _safe_float(row["count_2023_lower"]),
            "count_2023_upper": _safe_float(row["count_2023_upper"]),
            "count_pct_change": _safe_float(row["count_pct_mean"]),
            "asr_2010_mean": _safe_float(row["asr_2010_mean"]),
            "asr_2023_mean": _safe_float(row["asr_2023_mean"]),
            "asr_2023_lower": _safe_float(row["asr_2023_lower"]),
            "asr_2023_upper": _safe_float(row["asr_2023_upper"]),
            "asr_pct_change": _safe_float(row["asr_pct_mean"]),
        })
    return out


def get_daly_vs_yld_comparison() -> List[Dict[str, Any]]:
    """
    Compares Level-2 causes across DALYs and YLDs to reveal fatal vs chronic disability profiles.
    Matches causes present in both S10 and S11.
    """
    s10 = get_s10()
    s11 = get_s11()

    s10_l2 = s10[s10["cause_level_int"] == 2][["cause", "count_2023_mean", "asr_2023_mean", "asr_pct_mean"]]
    s11_l2 = s11[s11["cause_level_int"] == 2][["cause", "count_2023_mean", "asr_2023_mean", "asr_pct_mean"]]

    merged = s10_l2.merge(s11_l2, on="cause", suffixes=("_daly", "_yld"))
    merged["disability_ratio_pct"] = (merged["count_2023_mean_yld"] / merged["count_2023_mean_daly"]) * 100.0

    # Sort by total DALY count
    merged = merged.sort_values("count_2023_mean_daly", ascending=False)

    records = []
    for _, row in merged.iterrows():
        # Characterize burden type
        ratio = row["disability_ratio_pct"]
        if ratio >= 80.0:
            burden_type = "Predominantly Disabling (Non-Fatal)"
        elif ratio <= 30.0:
            burden_type = "Predominantly Fatal (Premature Mortality)"
        else:
            burden_type = "Mixed Fatal & Chronic"

        records.append({
            "cause": row["cause"],
            "daly_count_2023": _safe_float(row["count_2023_mean_daly"]),
            "daly_asr_2023": _safe_float(row["asr_2023_mean_daly"]),
            "yld_count_2023": _safe_float(row["count_2023_mean_yld"]),
            "yld_asr_2023": _safe_float(row["asr_2023_mean_yld"]),
            "disability_ratio_pct": _safe_float(ratio, 1),
            "burden_type": burden_type,
            "daly_asr_trend": _safe_float(row["asr_pct_mean_daly"]),
            "yld_asr_trend": _safe_float(row["asr_pct_mean_yld"]),
        })

    return records


def get_disease_burden_table(
    metric: str = "daly",
    level: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "count_2023_mean",
    sort_asc: bool = False,
    page: int = 1,
    page_size: int = 15,
) -> Dict[str, Any]:
    """
    Paginated, searchable table of causes for S10 (DALY) or S11 (YLD).
    """
    df = get_s10() if metric.lower() == "daly" else get_s11()
    sub = df.copy()

    if level is not None and level >= 0:
        sub = sub[sub["cause_level_int"] == level]

    if search:
        s = search.strip().lower()
        sub = sub[sub["cause"].str.lower().str.contains(s, na=False)]

    # Sorting
    if sort_by in sub.columns:
        sub = sub.sort_values(by=sort_by, ascending=sort_asc)
    else:
        sub = sub.sort_values(by="count_2023_mean", ascending=False)

    total_records = len(sub)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged = sub.iloc[start_idx:end_idx]

    records = []
    for _, row in paged.iterrows():
        records.append({
            "cause": row["cause"],
            "level": int(row["cause_level_int"]),
            "count_2010_mean": _safe_float(row["count_2010_mean"]),
            "count_2023_mean": _safe_float(row["count_2023_mean"]),
            "count_2023_lower": _safe_float(row["count_2023_lower"]),
            "count_2023_upper": _safe_float(row["count_2023_upper"]),
            "count_pct_change": _safe_float(row["count_pct_mean"]),
            "asr_2010_mean": _safe_float(row["asr_2010_mean"]),
            "asr_2023_mean": _safe_float(row["asr_2023_mean"]),
            "asr_2023_lower": _safe_float(row["asr_2023_lower"]),
            "asr_2023_upper": _safe_float(row["asr_2023_upper"]),
            "asr_pct_change": _safe_float(row["asr_pct_mean"]),
        })

    return {
        "metric": metric.lower(),
        "total": total_records,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total_records / page_size) if page_size > 0 else 1,
        "records": records,
    }
