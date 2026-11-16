"""
data/pipeline.py
----------------
Single entry point that orchestrates load → clean → validate for all datasets.

Usage:
    from data.pipeline import get_s9, get_s10, get_s11, get_all_datasets

Each getter function caches its result in memory on first call (module-level
singleton pattern). Subsequent calls return the same DataFrame without
re-reading the Excel file, keeping the API fast.

The pipeline does NOT merge S10/S11 with S9 — they are kept as independent
global-level datasets.
"""

import logging
from typing import Optional
import pandas as pd

from data.loader  import load_s9_long, load_s10_raw, load_s11_raw
from data.cleaner import clean_s9, clean_s10_from_raw, clean_s11_from_raw
from data.validator import validate_s9, validate_burden

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory cache  (None until first access)
# ---------------------------------------------------------------------------
_cache: dict[str, Optional[pd.DataFrame]] = {
    "s9":  None,
    "s10": None,
    "s11": None,
}

_validation_results: dict[str, list] = {}


def _run_pipeline(key: str, loader, cleaner, validator_fn) -> pd.DataFrame:
    """Generic load → clean → validate pipeline."""
    if _cache[key] is not None:
        return _cache[key]

    logger.info("Pipeline: loading %s …", key.upper())
    raw     = loader()
    cleaned = cleaner(raw)
    results = validator_fn(cleaned)

    _validation_results[key] = results

    n_pass = sum(1 for r in results if r["passed"])
    n_fail = sum(1 for r in results if not r["passed"])
    logger.info(
        "Pipeline %s: %d checks PASSED, %d WARNINGS", key.upper(), n_pass, n_fail
    )

    _cache[key] = cleaned
    return cleaned


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_s9() -> pd.DataFrame:
    """Return cleaned S9 HLE dataset (long format)."""
    return _run_pipeline(
        "s9",
        loader       = load_s9_long,
        cleaner      = clean_s9,
        validator_fn = validate_s9,
    )


def get_s10() -> pd.DataFrame:
    """Return cleaned S10 DALY burden dataset."""
    return _run_pipeline(
        "s10",
        loader       = load_s10_raw,
        cleaner      = clean_s10_from_raw,
        validator_fn = lambda df: validate_burden(df, "daly"),
    )


def get_s11() -> pd.DataFrame:
    """Return cleaned S11 YLD burden dataset."""
    return _run_pipeline(
        "s11",
        loader       = load_s11_raw,
        cleaner      = clean_s11_from_raw,
        validator_fn = lambda df: validate_burden(df, "yld"),
    )


def get_all_datasets() -> dict[str, pd.DataFrame]:
    """Load and cache all three datasets. Returns dict keyed by 's9', 's10', 's11'."""
    return {"s9": get_s9(), "s10": get_s10(), "s11": get_s11()}


def get_validation_results() -> dict[str, list]:
    """Return validation results for all loaded datasets."""
    return _validation_results


def reset_cache() -> None:
    """Force a full reload on next access (useful for testing)."""
    for k in _cache:
        _cache[k] = None
    _validation_results.clear()
    logger.info("Dataset cache cleared.")
