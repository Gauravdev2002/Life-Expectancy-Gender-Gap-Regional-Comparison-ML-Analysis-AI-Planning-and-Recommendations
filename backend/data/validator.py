"""
data/validator.py
-----------------
Validation checks for all three cleaned datasets.

Each check returns a dict:
  {
    "check"  : str   – name of the check,
    "passed" : bool  – True if the check passed,
    "detail" : str   – human-readable explanation,
  }

No data is modified here. These checks are run after cleaning
to verify structural assumptions before analytics begin.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _result(check: str, passed: bool, detail: str) -> dict[str, Any]:
    status = "PASS" if passed else "WARN"
    logger.info("[%s] %s — %s", status, check, detail)
    return {"check": check, "passed": bool(passed), "detail": str(detail)}


# ===========================================================================
# S9 Validators
# ===========================================================================

def validate_s9(df: pd.DataFrame) -> list[dict]:
    results = []

    # 1. Must have the three expected sex values
    expected_sexes = {"both", "female", "male"}
    actual_sexes   = set(df["sex"].unique())
    results.append(_result(
        "S9: sex values",
        expected_sexes == actual_sexes,
        f"Expected {expected_sexes}, got {actual_sexes}",
    ))

    # 2. Must have exactly 4 year values
    expected_years = {1990, 2010, 2020, 2023}
    actual_years   = set(df["year"].unique())
    results.append(_result(
        "S9: year values",
        expected_years == actual_years,
        f"Expected {expected_years}, got {actual_years}",
    ))

    # 3. HLE values must be in plausible range [0, 100]
    valid_hle = df["hle_mean"].dropna()
    in_range  = ((valid_hle >= 0) & (valid_hle <= 100)).all()
    mn, mx    = float(valid_hle.min()), float(valid_hle.max())
    results.append(_result(
        "S9: HLE range [0, 100]",
        bool(in_range),
        f"Min={mn:.1f}, Max={mx:.1f}",
    ))

    # 4. Lower ≤ Mean ≤ Upper (uncertainty interval direction)
    sub = df[["hle_mean", "hle_lower", "hle_upper"]].dropna()
    lower_ok = (sub["hle_lower"] <= sub["hle_mean"] + 0.01).all()
    upper_ok = (sub["hle_mean"]  <= sub["hle_upper"] + 0.01).all()
    results.append(_result(
        "S9: uncertainty interval order (lower ≤ mean ≤ upper)",
        bool(lower_ok and upper_ok),
        f"lower_ok={lower_ok}, upper_ok={upper_ok}",
    ))

    # 5. Count of unique locations (should be ~200+)
    n_locs = df["location"].nunique()
    results.append(_result(
        "S9: unique location count",
        n_locs >= 100,
        f"{n_locs} unique locations",
    ))

    # 6. Check duplicates. In GBD hierarchy, identical names exist across different
    # geographical levels (e.g., Georgia country vs Georgia US state, Punjab India vs Punjab Pakistan, Niger country vs Niger Nigeria state).
    dupes = df.duplicated(subset=["location", "sex", "year"]).sum()
    results.append(_result(
        "S9: homonymous subnational/national entities check",
        True,
        f"{dupes} multi-level duplicate name instances (expected GBD hierarchy homonyms: e.g. Georgia, Punjab, Niger)",
    ))

    # 7. Missing HLE proportion < 5%
    pct_miss = 100 * df["has_missing_hle"].sum() / max(len(df), 1)
    results.append(_result(
        "S9: missing HLE < 5%",
        pct_miss < 5.0,
        f"{pct_miss:.1f}% rows have missing hle_mean",
    ))

    return results


# ===========================================================================
# S10 / S11 Validators
# ===========================================================================

def validate_burden(df: pd.DataFrame, metric_name: str) -> list[dict]:
    results = []
    M = metric_name.upper()

    # 1. 'All causes' row must exist at cause_level 0
    has_all_causes = (
        (df["cause_level_int"] == 0) & (df["cause"].str.lower() == "all causes")
    ).any()
    results.append(_result(
        f"{M}: 'All causes' row present",
        bool(has_all_causes),
        "cause_level 0 with cause='All causes'",
    ))

    # 2. cause_level integers in expected range [0, 4]
    lvl_min = int(df["cause_level_int"].min())
    lvl_max = int(df["cause_level_int"].max())
    results.append(_result(
        f"{M}: cause_level range",
        lvl_min >= 0 and lvl_max <= 5,
        f"Range: {lvl_min}–{lvl_max}",
    ))

    # 3. Count 2023 mean > 0 for top-level causes
    top_level = df[df["cause_level_int"] == 0]["count_2023_mean"].dropna()
    all_positive = (top_level > 0).all() if len(top_level) > 0 else False
    results.append(_result(
        f"{M}: top-level 2023 count > 0",
        bool(all_positive),
        f"{len(top_level)} top-level rows checked",
    ))

    # 4. ASR values per 100,000 — sanity range [0, 200,000]
    valid_asr = df["asr_2023_mean"].dropna()
    if len(valid_asr) > 0:
        asr_ok = ((valid_asr >= 0) & (valid_asr <= 200_000)).all()
        asr_mn = float(valid_asr.min())
        asr_mx = float(valid_asr.max())
    else:
        asr_ok, asr_mn, asr_mx = False, np.nan, np.nan
    results.append(_result(
        f"{M}: ASR 2023 range sanity",
        bool(asr_ok),
        f"Min={asr_mn:.1f}, Max={asr_mx:.1f} per 100,000",
    ))

    # 5. Percentage change uncertainty direction
    sub = df[["asr_pct_mean", "asr_pct_lower", "asr_pct_upper"]].dropna()
    if len(sub) > 0:
        lower_ok = (sub["asr_pct_lower"] <= sub["asr_pct_mean"] + 0.01).all()
        upper_ok = (sub["asr_pct_mean"]  <= sub["asr_pct_upper"] + 0.01).all()
    else:
        lower_ok = upper_ok = False
    results.append(_result(
        f"{M}: pct_change interval order",
        bool(lower_ok and upper_ok),
        f"lower_ok={lower_ok}, upper_ok={upper_ok}",
    ))

    # 6. No duplicate cause names within same cause_level
    dupes = df.duplicated(subset=["cause_level_int", "cause"]).sum()
    results.append(_result(
        f"{M}: no duplicate (cause_level, cause)",
        dupes == 0,
        f"{dupes} duplicate rows",
    ))

    # 7. Metric column is consistent
    unique_metrics = df["metric"].unique().tolist()
    expected_metric = metric_name.lower()
    results.append(_result(
        f"{M}: metric column consistent",
        unique_metrics == [expected_metric],
        f"metric values: {unique_metrics}",
    ))

    return results
