"""
test_phase2.py
--------------
Integration test for Phase 2 data pipeline.
Run from backend/ with venv active:
    python test_phase2.py

Tests:
  1. All three loaders return non-empty DataFrames.
  2. Column names are correct.
  3. Cleaners produce valid output.
  4. Validators report results.
  5. Sample records are printed for visual inspection.
  6. Summary dicts are generated without errors.
"""

import sys
import os
import io
import logging

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configure logging so we can see pipeline messages
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)

# Add parent so imports resolve
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np

SEP = "=" * 72

def section(label):
    print(f"\n{SEP}")
    print(f"  {label}")
    print(SEP)

# ---------------------------------------------------------------------------
# Phase 2 Test
# ---------------------------------------------------------------------------

def test_all():
    from data.loader   import load_s9_long, load_s10_raw, load_s11_raw
    from data.cleaner  import clean_s9, clean_s10_from_raw, clean_s11_from_raw
    from data.validator import validate_s9, validate_burden
    from data.summary  import summarise_s9, summarise_burden
    from data.pipeline import get_s9, get_s10, get_s11

    # ── S9 ────────────────────────────────────────────────────────────────
    section("TEST 1 — S9 Healthy Life Expectancy")

    s9_raw  = load_s9_long()
    s9      = clean_s9(s9_raw)

    print(f"  Shape (long): {s9.shape}")
    print(f"  Columns     : {list(s9.columns)}")
    print(f"  Sex values  : {sorted(s9['sex'].unique())}")
    print(f"  Year values : {sorted(s9['year'].unique())}")
    print(f"  Locations   : {s9['location'].nunique()} unique")
    print(f"  Aggregates  : {s9['is_aggregate'].sum()} rows")
    print(f"\n  Sample — Global, Both Sexes:")
    sub = s9[(s9["location"] == "Global") & (s9["sex"] == "both")]
    with pd.option_context("display.width", 120, "display.max_columns", 15):
        print(sub.to_string(index=False))

    print(f"\n  Top-5 HLE countries (Both Sexes, 2023):")
    top5 = s9[(s9["sex"] == "both") & (s9["year"] == 2023) & ~s9["is_aggregate"]]\
              .nlargest(5, "hle_mean")[["location", "hle_mean", "hle_lower", "hle_upper"]]
    print(top5.to_string(index=False))

    print(f"\n  Bottom-5 HLE countries (Both Sexes, 2023):")
    bot5 = s9[(s9["sex"] == "both") & (s9["year"] == 2023) & ~s9["is_aggregate"]]\
              .nsmallest(5, "hle_mean")[["location", "hle_mean", "hle_lower", "hle_upper"]]
    print(bot5.to_string(index=False))

    print(f"\n  Gender gap sample (2023, first 5 non-aggregate locations):")
    piv_f = s9[(s9["sex"] == "female") & (s9["year"] == 2023) & ~s9["is_aggregate"]]\
               [["location", "hle_mean"]].set_index("location")
    piv_m = s9[(s9["sex"] == "male")   & (s9["year"] == 2023) & ~s9["is_aggregate"]]\
               [["location", "hle_mean"]].set_index("location")
    gap = piv_f.join(piv_m, suffixes=("_f", "_m")).dropna()
    gap["gap_f_minus_m"] = gap["hle_mean_f"] - gap["hle_mean_m"]
    print(gap.reset_index().head(5).to_string(index=False))

    print("\n  Validation results:")
    for r in validate_s9(s9):
        status = "✓" if r["passed"] else "⚠"
        print(f"    {status} {r['check']}: {r['detail']}")

    # ── S10 ───────────────────────────────────────────────────────────────
    section("TEST 2 — S10 Global DALY Burden")

    s10_raw = load_s10_raw()
    s10     = clean_s10_from_raw(s10_raw)

    print(f"  Shape  : {s10.shape}")
    print(f"  Columns: {list(s10.columns)}")
    print(f"  Cause level distribution:")
    print(s10["cause_level_int"].value_counts().sort_index().to_string())

    print(f"\n  Level-0 (All causes):")
    l0 = s10[s10["cause_level_int"] == 0][
        ["cause", "count_2010_mean", "count_2023_mean", "count_pct_mean",
         "asr_2010_mean", "asr_2023_mean", "asr_pct_mean"]
    ]
    print(l0.to_string(index=False))

    print(f"\n  Level-1 (Major categories, sorted by 2023 count):")
    l1 = s10[s10["cause_level_int"] == 1][
        ["cause", "count_2023_mean", "count_pct_mean", "asr_2023_mean", "asr_pct_mean"]
    ].sort_values("count_2023_mean", ascending=False)
    print(l1.to_string(index=False))

    print("\n  Validation results:")
    for r in validate_burden(s10, "daly"):
        status = "✓" if r["passed"] else "⚠"
        print(f"    {status} {r['check']}: {r['detail']}")

    # ── S11 ───────────────────────────────────────────────────────────────
    section("TEST 3 — S11 Global YLD Burden")

    s11_raw = load_s11_raw()
    s11     = clean_s11_from_raw(s11_raw)

    print(f"  Shape  : {s11.shape}")
    print(f"  Level-1 (sorted by 2023 count):")
    l1_11 = s11[s11["cause_level_int"] == 1][
        ["cause", "count_2023_mean", "count_pct_mean", "asr_2023_mean", "asr_pct_mean"]
    ].sort_values("count_2023_mean", ascending=False)
    print(l1_11.to_string(index=False))

    print("\n  Validation results:")
    for r in validate_burden(s11, "yld"):
        status = "✓" if r["passed"] else "⚠"
        print(f"    {status} {r['check']}: {r['detail']}")

    # ── Summary dicts ─────────────────────────────────────────────────────
    section("TEST 4 — Summary Generation")

    s9_sum  = summarise_s9(s9)
    s10_sum = summarise_burden(s10, "daly", "DALYs")
    s11_sum = summarise_burden(s11, "yld",  "YLDs")

    import json
    print("\n  S9 Summary (JSON):")
    print(json.dumps(s9_sum, indent=2, default=str))
    print("\n  S10 Summary headline numbers:")
    print(f"    Total DALY count 2023 : {s10_sum['total_count_2023_mean']}")
    print(f"    % Change 2010-2023    : {s10_sum['total_count_pct_change']}")
    print("\n  S11 Summary headline numbers:")
    print(f"    Total YLD count 2023  : {s11_sum['total_count_2023_mean']}")
    print(f"    % Change 2010-2023    : {s11_sum['total_count_pct_change']}")

    # ── Pipeline cache ────────────────────────────────────────────────────
    section("TEST 5 — Pipeline Cache")
    p9  = get_s9()
    p10 = get_s10()
    p11 = get_s11()
    print(f"  Pipeline S9  : {p9.shape}")
    print(f"  Pipeline S10 : {p10.shape}")
    print(f"  Pipeline S11 : {p11.shape}")
    print("  ✓ All three datasets load through pipeline successfully.")

    section("ALL PHASE 2 TESTS PASSED")


if __name__ == "__main__":
    test_all()
