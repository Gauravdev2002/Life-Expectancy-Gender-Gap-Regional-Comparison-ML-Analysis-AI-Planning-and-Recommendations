"""
data/loader.py
--------------
Reusable data-loading functions for all three datasets.

Each function:
  1. Reads the Excel file from the datasets/ directory.
  2. Correctly handles the multi-row merged headers.
  3. Assigns clean, descriptive column names.
  4. Returns a raw (unfiltered) pandas DataFrame.

No data is invented or imputed here — that happens in cleaner.py.

Column naming conventions
--------------------------
S9  columns: location, sex, year, hle_mean, hle_lower, hle_upper,
             pct_change_mean, pct_change_lower, pct_change_upper
S10 columns: cause_level, cause, rank_2023, metric (count/asr),
             year, mean, lower, upper, pct_change_mean,
             pct_change_lower, pct_change_upper
S11 columns: same as S10 (YLD instead of DALY)
"""

import os
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(__file__)           # backend/data/

def _dataset_path(filename: str) -> str:
    # Check environment variable first
    if "DATASETS_DIR" in os.environ:
        candidate = os.path.join(os.environ["DATASETS_DIR"], filename)
        if os.path.exists(candidate):
            return os.path.abspath(candidate)
    
    # Potential relative paths
    search_paths = [
        os.path.join(_HERE, "..", "..", "datasets", filename),
        os.path.join(_HERE, "..", "datasets", filename),
        os.path.join(os.getcwd(), "datasets", filename),
        os.path.join(os.getcwd(), "..", "datasets", filename),
    ]
    for sp in search_paths:
        if os.path.exists(sp):
            return os.path.abspath(sp)

    raise FileNotFoundError(
        f"Dataset '{filename}' not found in any standard location: {search_paths}\n"
        "Make sure the datasets/ folder is available."
    )


# ===========================================================================
# S9 — Healthy Life Expectancy by Location and Sex
# ===========================================================================

# The Excel sheet has a 4-row header block (rows 0-3):
#   Row 0 : title string (merged across all columns)
#   Row 1 : sex sections  → "Location", "Both Sexes", NaN…, "Females", NaN…, "Males", NaN…
#   Row 2 : year groups   → 1990, 2010, 2020, 2023, "Percentage Change, 2010-2023"
#   Row 3 : sub-columns   → Mean, Lower, Upper (repeated)
#
# Data starts at row 4 (0-indexed).
# Total columns: 46  (1 location + 15 per sex × 3 sexes)
# Layout per sex (15 columns):
#   1990 mean/lower/upper | 2010 mean/lower/upper | 2020 mean/lower/upper |
#   2023 mean/lower/upper | PctChange mean/lower/upper

def _build_s9_column_names() -> list[str]:
    """
    Programmatically constructs the 46 flat column names
    matching the S9 multi-row merged header structure.
    """
    names = ["location"]
    for sex in ["both", "female", "male"]:
        for year in ["1990", "2010", "2020", "2023"]:
            for bound in ["mean", "lower", "upper"]:
                names.append(f"{sex}_{year}_{bound}")
        for bound in ["mean", "lower", "upper"]:
            names.append(f"{sex}_pct_change_{bound}")
    return names   # 1 + 3*(4*3 + 3) = 1 + 3*15 = 46 columns


def load_s9_raw() -> pd.DataFrame:
    """
    Load S9 Healthy Life Expectancy dataset.

    Returns a wide-format DataFrame where each row is a location
    and columns cover all sex/year/bound combinations.

    Shape: ~204 data rows × 46 columns (after skipping 4 header rows).
    """
    path  = _dataset_path("S9_Healthy_Life_Expectancy_By_Location_and_Sex.xlsx")
    names = _build_s9_column_names()

    df = pd.read_excel(
        path,
        sheet_name="sheet1",
        header=None,         # We handle headers manually
        skiprows=4,          # Skip title + 3 header rows
        names=names,
        engine="openpyxl",
    )

    logger.info("S9 raw loaded: %d rows × %d cols", len(df), len(df.columns))
    return df


def load_s9_long() -> pd.DataFrame:
    """
    Load S9 and reshape from wide to long format.

    Returns one row per (location, sex, year) combination.
    Preserves uncertainty intervals (lower, upper).
    Does NOT melt the percentage-change columns — those stay separate.

    Columns: location, sex, year, hle_mean, hle_lower, hle_upper,
             pct_change_mean, pct_change_lower, pct_change_upper
    """
    wide = load_s9_raw()
    records = []

    years = ["1990", "2010", "2020", "2023"]

    for _, row in wide.iterrows():
        location = row["location"]
        if pd.isna(location) or str(location).strip() == "":
            continue

        for sex in ["both", "female", "male"]:
            for year in years:
                hle_mean  = row.get(f"{sex}_{year}_mean")
                hle_lower = row.get(f"{sex}_{year}_lower")
                hle_upper = row.get(f"{sex}_{year}_upper")

            # Percentage change 2010-2023 (single value per sex, not per year)
                pct_mean  = row.get(f"{sex}_pct_change_mean")
                pct_lower = row.get(f"{sex}_pct_change_lower")
                pct_upper = row.get(f"{sex}_pct_change_upper")

                records.append({
                    "location"         : str(location).strip(),
                    "sex"              : sex,
                    "year"             : int(year),
                    "hle_mean"         : hle_mean,
                    "hle_lower"        : hle_lower,
                    "hle_upper"        : hle_upper,
                    "pct_change_mean"  : pct_mean,
                    "pct_change_lower" : pct_lower,
                    "pct_change_upper" : pct_upper,
                })

    df = pd.DataFrame(records)
    logger.info("S9 long: %d rows × %d cols", len(df), len(df.columns))
    return df


# ===========================================================================
# S10 — Global DALY Counts and Age-Standardised Rate Changes
# ===========================================================================

# The Excel sheet has a 4-row header block (rows 0-3):
#   Row 0 : title string
#   Row 1 : section labels → "Cause Level", "Cause", "Rank…",
#            "Counts (millions)" [merged 6 cols], "Age-standardised Rate…" [merged 6 cols]
#   Row 2 : year groups → 2010, 2023, "Percentage Change, 2010-2023" (×2 for Counts & ASR)
#   Row 3 : Mean / Lower / Upper  (repeated per year & section)
#
# Data starts at row 4 (0-indexed).
# Total columns: 21
# Layout:
#   cause_level | cause | rank |
#   count_2010_mean | count_2010_lower | count_2010_upper |
#   count_2023_mean | count_2023_lower | count_2023_upper |
#   count_pct_mean  | count_pct_lower  | count_pct_upper  |
#   asr_2010_mean   | asr_2010_lower   | asr_2010_upper   |
#   asr_2023_mean   | asr_2023_lower   | asr_2023_upper   |
#   asr_pct_mean    | asr_pct_lower    | asr_pct_upper

_S10_S11_COLUMNS = [
    "cause_level", "cause", "rank_2023",
    "count_2010_mean", "count_2010_lower", "count_2010_upper",
    "count_2023_mean", "count_2023_lower", "count_2023_upper",
    "count_pct_mean",  "count_pct_lower",  "count_pct_upper",
    "asr_2010_mean",   "asr_2010_lower",   "asr_2010_upper",
    "asr_2023_mean",   "asr_2023_lower",   "asr_2023_upper",
    "asr_pct_mean",    "asr_pct_lower",    "asr_pct_upper",
]


def load_s10_raw() -> pd.DataFrame:
    """
    Load S10 Global DALY Counts and Age-Standardised Rate Changes.

    Scope  : Global, Both Sexes
    Metric : DALYs (Disability-Adjusted Life Years)
    Shape  : ~375 rows × 21 columns (cause hierarchy rows)

    count_* columns are in millions as stored in the file.
    asr_*   columns are per 100,000 population.
    """
    path = _dataset_path(
        "S10_Global_DALY_Counts_and_Age_Standardised_Rate_Changes.xlsx"
    )
    df = pd.read_excel(
        path,
        sheet_name="sheet1",
        header=None,
        skiprows=4,
        names=_S10_S11_COLUMNS,
        engine="openpyxl",
    )
    logger.info("S10 raw loaded: %d rows × %d cols", len(df), len(df.columns))
    return df


def load_s11_raw() -> pd.DataFrame:
    """
    Load S11 Global YLD Counts and Age-Standardised Rate Changes.

    Scope  : Global, Both Sexes
    Metric : YLDs (Years Lived with Disability)
    Shape  : ~370 rows × 21 columns (cause hierarchy rows)

    count_* columns are in millions as stored in the file.
    asr_*   columns are per 100,000 population.
    """
    path = _dataset_path(
        "S11_Global_YLD_Counts_and_Age_Standardised_Rate_Changes.xlsx"
    )
    df = pd.read_excel(
        path,
        sheet_name="sheet1",
        header=None,
        skiprows=4,
        names=_S10_S11_COLUMNS,
        engine="openpyxl",
    )
    logger.info("S11 raw loaded: %d rows × %d cols", len(df), len(df.columns))
    return df
