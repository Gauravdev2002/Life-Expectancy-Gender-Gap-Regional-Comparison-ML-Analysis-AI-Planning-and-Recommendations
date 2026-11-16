"""
api/routes/datasets.py
-----------------------
REST endpoints that expose the three cleaned datasets to the frontend.

All endpoints load data via the pipeline (cached after first call).
No data is fabricated — all values come directly from the Excel files.

Endpoints:
  GET /api/datasets/info          – metadata + summary for all 3 datasets
  GET /api/datasets/s9/summary    – S9 HLE overview statistics
  GET /api/datasets/s9/locations  – list of unique locations
  GET /api/datasets/s9/hle        – HLE data with optional filters
  GET /api/datasets/s10/summary   – S10 DALY burden summary
  GET /api/datasets/s11/summary   – S11 YLD burden summary
  GET /api/datasets/s10/causes    – DALY cause list (level 1)
  GET /api/datasets/s11/causes    – YLD cause list (level 1)
  GET /api/datasets/validate      – run validation checks on all datasets
"""

import logging
import math
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from data.pipeline  import get_s9, get_s10, get_s11, get_validation_results
from data.summary   import summarise_s9, summarise_burden

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["Datasets"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_for_json(obj):
    """Recursively replace NaN/inf with None and convert numpy types to native Python."""
    if isinstance(obj, dict):
        return {k: _clean_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_for_json(i) for i in obj]
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return None if math.isnan(float(obj)) else float(obj)
    return obj


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to JSON-safe list of records."""
    return _clean_for_json(df.to_dict(orient="records"))


# ---------------------------------------------------------------------------
# Dataset Info (all three in one call)
# ---------------------------------------------------------------------------

@router.get("/info")
async def get_dataset_info():
    """
    Load all three datasets and return high-level metadata.
    This is the first endpoint called by the dashboard on startup.
    """
    try:
        s9  = get_s9()
        s10 = get_s10()
        s11 = get_s11()
        return _clean_for_json({
            "status": "loaded",
            "datasets": {
                "s9" : {
                    "name"  : "S9 — Healthy Life Expectancy",
                    "rows"  : len(s9),
                    "cols"  : len(s9.columns),
                    "scope" : "Location × Sex × Year",
                },
                "s10": {
                    "name"  : "S10 — Global DALY Burden",
                    "rows"  : len(s10),
                    "cols"  : len(s10.columns),
                    "scope" : "Global, Both Sexes",
                },
                "s11": {
                    "name"  : "S11 — Global YLD Burden",
                    "rows"  : len(s11),
                    "cols"  : len(s11.columns),
                    "scope" : "Global, Both Sexes",
                },
            },
        })
    except Exception as e:
        logger.exception("Error loading datasets")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# S9 Endpoints
# ---------------------------------------------------------------------------

@router.get("/s9/summary")
async def get_s9_summary():
    """Full summary statistics for the S9 HLE dataset."""
    try:
        df = get_s9()
        return _clean_for_json(summarise_s9(df))
    except Exception as e:
        logger.exception("Error summarising S9")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/s9/locations")
async def get_s9_locations(include_aggregates: bool = False):
    """
    Return list of unique location names.
    Set include_aggregates=true to include SDI groups and 'Global'.
    """
    df = get_s9()
    if not include_aggregates:
        df = df[~df["is_aggregate"]]
    locations = sorted(df["location"].dropna().unique().tolist())
    return {"count": len(locations), "locations": locations}


@router.get("/s9/hle")
async def get_s9_hle(
    sex: Optional[str]      = Query(None, description="both | female | male"),
    year: Optional[int]     = Query(None, description="1990 | 2010 | 2020 | 2023"),
    location: Optional[str] = Query(None, description="Exact location name"),
    aggregates_only: bool   = Query(False),
    limit: int              = Query(100, le=1000),
):
    """
    Return filtered HLE records.
    All uncertainty intervals (lower, upper) are preserved.
    """
    df = get_s9()

    if sex:
        if sex not in {"both", "female", "male"}:
            raise HTTPException(400, "sex must be 'both', 'female', or 'male'")
        df = df[df["sex"] == sex]

    if year:
        if year not in {1990, 2010, 2020, 2023}:
            raise HTTPException(400, "year must be 1990, 2010, 2020, or 2023")
        df = df[df["year"] == year]

    if location:
        df = df[df["location"].str.lower() == location.lower()]

    if aggregates_only:
        df = df[df["is_aggregate"]]

    df = df.head(limit)
    return {"count": len(df), "records": _df_to_records(df)}


# ---------------------------------------------------------------------------
# S10 Endpoints
# ---------------------------------------------------------------------------

@router.get("/s10/summary")
async def get_s10_summary():
    """Full summary for the S10 DALY burden dataset."""
    try:
        df = get_s10()
        return _clean_for_json(
            summarise_burden(df, "daly", "Disability-Adjusted Life Years (DALYs)")
        )
    except Exception as e:
        logger.exception("Error summarising S10")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/s10/causes")
async def get_s10_causes(level: Optional[int] = Query(None, description="Cause level 0-4")):
    """Return DALY cause list, optionally filtered by cause_level_int."""
    df = get_s10()
    if level is not None:
        df = df[df["cause_level_int"] == level]
    cols = ["cause_level_int", "cause", "rank_2023",
            "count_2023_mean", "count_2023_lower", "count_2023_upper",
            "count_pct_mean",  "asr_2023_mean", "asr_pct_mean"]
    df = df[cols].dropna(subset=["cause"])
    return {"count": len(df), "records": _df_to_records(df)}


# ---------------------------------------------------------------------------
# S11 Endpoints
# ---------------------------------------------------------------------------

@router.get("/s11/summary")
async def get_s11_summary():
    """Full summary for the S11 YLD burden dataset."""
    try:
        df = get_s11()
        return _clean_for_json(
            summarise_burden(df, "yld", "Years Lived with Disability (YLDs)")
        )
    except Exception as e:
        logger.exception("Error summarising S11")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/s11/causes")
async def get_s11_causes(level: Optional[int] = Query(None, description="Cause level 0-4")):
    """Return YLD cause list, optionally filtered by cause_level_int."""
    df = get_s11()
    if level is not None:
        df = df[df["cause_level_int"] == level]
    cols = ["cause_level_int", "cause", "rank_2023",
            "count_2023_mean", "count_2023_lower", "count_2023_upper",
            "count_pct_mean",  "asr_2023_mean", "asr_pct_mean"]
    df = df[cols].dropna(subset=["cause"])
    return {"count": len(df), "records": _df_to_records(df)}


# ---------------------------------------------------------------------------
# Validation Endpoint
# ---------------------------------------------------------------------------

@router.get("/validate")
async def run_validation():
    """
    Run all validation checks across loaded datasets.
    Returns pass/fail status for each check.
    """
    try:
        # Trigger load if not already cached
        get_s9(); get_s10(); get_s11()
        results = get_validation_results()
        summary = {}
        for key, checks in results.items():
            n_pass = sum(1 for c in checks if c["passed"])
            n_fail = sum(1 for c in checks if not c["passed"])
            summary[key.upper()] = {
                "passed": n_pass,
                "warnings": n_fail,
                "checks": checks,
            }
        return _clean_for_json(summary)
    except Exception as e:
        logger.exception("Error during validation")
        raise HTTPException(status_code=500, detail=str(e))
