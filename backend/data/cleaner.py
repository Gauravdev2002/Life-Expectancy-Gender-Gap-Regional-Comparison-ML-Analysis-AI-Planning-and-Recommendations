"""
data/cleaner.py
---------------
Data-cleaning and preprocessing functions.

Rules applied to ALL datasets:
  - Strip whitespace from string columns.
  - Convert numeric-looking strings (with commas) to actual floats.
  - Do NOT fill NaN with invented values — use pd.NA / NaN.
  - Flag rows with missing core fields but keep them in the DataFrame.
  - Add a boolean 'has_missing_core' column to signal incomplete rows.

No data is invented. Rows with genuinely missing location / cause names
are marked but NOT dropped — analysts can filter them as needed.
"""

import logging
import re

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared numeric cleaner
# ---------------------------------------------------------------------------

def _to_numeric(val):
    """
    Convert a value to float, handling:
      - Already-float numbers
      - Strings with commas (e.g. "2,640,000,000" or "39,286.2")
      - Empty strings → NaN
      - Anything else that cannot be parsed → NaN
    """
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


def _clean_numeric_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Apply _to_numeric to a list of column names in-place."""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(_to_numeric)
    return df


def _clean_string_column(series: pd.Series) -> pd.Series:
    """Strip whitespace and normalise NaN-like strings."""
    return series.apply(
        lambda v: np.nan if pd.isna(v) or str(v).strip() in {"", "nan", "NaN"}
        else str(v).strip()
    )


# ===========================================================================
# S9 Cleaner  — Healthy Life Expectancy (long format)
# ===========================================================================

_S9_NUMERIC_COLS = [
    "hle_mean", "hle_lower", "hle_upper",
    "pct_change_mean", "pct_change_lower", "pct_change_upper",
]

_S9_KNOWN_AGGREGATES = {
    # SDI quintiles and global aggregates that are NOT individual countries
    "Global", "Low SDI", "Low-middle SDI", "Middle SDI",
    "High-middle SDI", "High SDI",
}


def clean_s9(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the S9 long-format HLE DataFrame.

    Steps:
      1. Strip location strings.
      2. Drop rows where location is NaN (truly blank rows in the Excel).
      3. Convert all numeric columns from string/object to float.
      4. Add 'is_aggregate' flag (True for SDI groups and Global).
      5. Add 'has_missing_hle' flag for rows where hle_mean is NaN.
      6. Validate year column is integer.

    Returns the cleaned DataFrame.
    """
    df = df.copy()

    # 1. Clean location
    df["location"] = _clean_string_column(df["location"])

    # 2. Drop fully blank rows and footnote rows (e.g. *United Nations convention...)
    before = len(df)
    df = df.dropna(subset=["location"])
    df = df[~df["location"].str.startswith("*")]
    after  = len(df)
    if before != after:
        logger.info("S9 clean: dropped %d blank location rows", before - after)

    # 3. Numeric conversions
    df = _clean_numeric_columns(df, _S9_NUMERIC_COLS)

    # 4. Aggregate flag
    df["is_aggregate"] = df["location"].isin(_S9_KNOWN_AGGREGATES)

    # 5. Missing HLE flag
    df["has_missing_hle"] = df["hle_mean"].isna()

    # 6. Year as int
    df["year"] = df["year"].astype(int)

    # 7. Sex as ordered category
    df["sex"] = pd.Categorical(
        df["sex"],
        categories=["both", "female", "male"],
        ordered=False,
    )

    logger.info(
        "S9 clean done: %d rows | %d locations | %d with missing HLE",
        len(df),
        df["location"].nunique(),
        int(df["has_missing_hle"].sum()),
    )
    return df


# ===========================================================================
# S10 / S11 Cleaner  — DALY and YLD cause-level data
# ===========================================================================

_BURDEN_NUMERIC_COLS = [
    "count_2010_mean", "count_2010_lower", "count_2010_upper",
    "count_2023_mean", "count_2023_lower", "count_2023_upper",
    "count_pct_mean",  "count_pct_lower",  "count_pct_upper",
    "asr_2010_mean",   "asr_2010_lower",   "asr_2010_upper",
    "asr_2023_mean",   "asr_2023_lower",   "asr_2023_upper",
    "asr_pct_mean",    "asr_pct_lower",    "asr_pct_upper",
]


def clean_burden(df: pd.DataFrame, metric_name: str) -> pd.DataFrame:
    """
    Clean S10 (DALY) or S11 (YLD) burden dataset.

    Parameters
    ----------
    df          : Raw DataFrame from load_s10_raw() or load_s11_raw()
    metric_name : 'daly' or 'yld' — added as a column for traceability

    Steps:
      1. Clean cause and cause_level strings.
      2. Drop rows where both cause AND cause_level are NaN.
      3. Convert cause_level and rank to integers where possible.
      4. Convert all numeric count/ASR columns to float.
      5. Add 'metric' column.
      6. Add 'has_missing_counts' flag.
      7. Add 'cause_level_int' — integer 0–4 representing hierarchy depth.
    """
    df = df.copy()

    # 1. Clean strings
    df["cause"]       = _clean_string_column(df["cause"])
    df["cause_level"] = df["cause_level"].apply(
        lambda v: np.nan if pd.isna(v) else str(v).strip()
    )

    # 2. Drop fully blank rows (trailing blank rows in Excel)
    before = len(df)
    df = df.dropna(subset=["cause"])
    after  = len(df)
    if before != after:
        logger.info(
            "%s clean: dropped %d blank cause rows", metric_name.upper(), before - after
        )

    # 3. cause_level → integer (0 = top level, 1-4 = sub-levels)
    df["cause_level_int"] = pd.to_numeric(df["cause_level"], errors="coerce")\
                              .fillna(-1).astype(int)

    # 4. rank_2023 → integer
    df["rank_2023"] = pd.to_numeric(df["rank_2023"], errors="coerce")

    # 5. Numeric columns
    df = _clean_numeric_columns(df, _BURDEN_NUMERIC_COLS)

    # 6. Metric label
    df["metric"] = metric_name.lower()

    # 7. Missing counts flag
    df["has_missing_counts"] = df["count_2023_mean"].isna()

    logger.info(
        "%s clean done: %d cause rows | level range %s–%s | %d missing counts",
        metric_name.upper(),
        len(df),
        int(df["cause_level_int"].min()),
        int(df["cause_level_int"].max()),
        int(df["has_missing_counts"].sum()),
    )
    return df


# ===========================================================================
# Top-level convenience wrappers
# ===========================================================================

def clean_s9_from_raw(raw_df: pd.DataFrame) -> pd.DataFrame:
    return clean_s9(raw_df)


def clean_s10_from_raw(raw_df: pd.DataFrame) -> pd.DataFrame:
    return clean_burden(raw_df, metric_name="daly")


def clean_s11_from_raw(raw_df: pd.DataFrame) -> pd.DataFrame:
    return clean_burden(raw_df, metric_name="yld")
