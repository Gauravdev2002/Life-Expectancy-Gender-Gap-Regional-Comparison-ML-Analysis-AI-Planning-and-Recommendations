"""
inspect_datasets.py
-------------------
Raw deep-inspection of all three Excel files.
Run from the backend/ directory with the venv active:
    python inspect_datasets.py

Outputs sheet names, raw header rows, column names, dtypes,
shape, missing value counts, and sample rows for every sheet.
No data is modified here — this is read-only exploration.
"""

import sys
import os
import json

import pandas as pd
import numpy as np
from openpyxl import load_workbook

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATASETS_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets")

FILES = {
    "S9": "S9_Healthy_Life_Expectancy_By_Location_and_Sex.xlsx",
    "S10": "S10_Global_DALY_Counts_and_Age_Standardised_Rate_Changes.xlsx",
    "S11": "S11_Global_YLD_Counts_and_Age_Standardised_Rate_Changes.xlsx",
}

SEPARATOR = "=" * 80


def sep(label=""):
    print(f"\n{SEPARATOR}")
    if label:
        print(f"  {label}")
        print(SEPARATOR)


def inspect_raw_rows(filepath, sheet_name, n_rows=10):
    """Read and print the first n raw rows without any header parsing."""
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=None, nrows=n_rows)
    print(f"\n--- First {n_rows} RAW rows of sheet '{sheet_name}' ---")
    with pd.option_context("display.max_columns", None, "display.width", 200,
                           "display.max_colwidth", 60):
        print(df.to_string())


def inspect_sheet(filepath, sheet_name, header_row, n_sample=5):
    """
    Read a sheet treating `header_row` (0-indexed) as the header.
    Returns the DataFrame and prints summary info.
    """
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=header_row)
    print(f"\n  Shape          : {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  Columns ({df.shape[1]}):")
    for i, col in enumerate(df.columns):
        dtype  = str(df[col].dtype)
        n_null = int(df[col].isna().sum())
        pct    = round(100 * n_null / max(len(df), 1), 1)
        print(f"    [{i:03d}] {str(col):<55} dtype={dtype:<10} nulls={n_null} ({pct}%)")
    print(f"\n  Sample rows (first {n_sample}):")
    with pd.option_context("display.max_columns", None, "display.width", 200,
                           "display.max_colwidth", 50):
        print(df.head(n_sample).to_string())
    return df


def inspect_file(key, filename):
    filepath = os.path.join(DATASETS_DIR, filename)
    sep(f"FILE: {key}  —  {filename}")
    print(f"  Full path : {filepath}")
    print(f"  File size : {os.path.getsize(filepath):,} bytes")

    # ── Sheet names ──────────────────────────────────────────────────────────
    wb   = load_workbook(filepath, read_only=True, data_only=True)
    sheets = wb.sheetnames
    wb.close()
    print(f"  Sheets    : {sheets}")

    # ── Inspect every sheet ──────────────────────────────────────────────────
    for sheet in sheets:
        sep(f"  SHEET: '{sheet}'  in  {key}")

        # First: print first 10 raw rows to see merged headers
        inspect_raw_rows(filepath, sheet, n_rows=12)

        # Then try with header=0 (default) for quick overview
        print(f"\n  === Reading with header=0 (default) ===")
        inspect_sheet(filepath, sheet, header_row=0, n_sample=5)

    return sheets


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("DATASET DEEP INSPECTION")
    print("Python:", sys.version)
    print("Pandas:", pd.__version__)
    print("NumPy :", np.__version__)

    results = {}
    for key, filename in FILES.items():
        results[key] = inspect_file(key, filename)

    sep("INSPECTION COMPLETE")
    print("\nSummary of sheets per file:")
    for k, sheets in results.items():
        print(f"  {k}: {sheets}")
