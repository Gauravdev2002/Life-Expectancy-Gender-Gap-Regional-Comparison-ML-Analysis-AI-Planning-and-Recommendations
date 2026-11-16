"""
api/routes/disease.py
---------------------
API routes exposing Global Disease Burden analytics from Datasets S10 (DALY) and S11 (YLD).
Strictly separate from country-level S9 HLE records.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from analytics.disease_analytics import (
    get_disease_burden_overview,
    get_level1_broad_breakdown,
    get_top_causes,
    get_daly_vs_yld_comparison,
    get_disease_burden_table,
)

router = APIRouter(prefix="/analytics/disease", tags=["Disease Burden Analytics"])


@router.get("/overview")
async def fetch_disease_overview():
    """Fetch global totals, leading causes, and non-fatal burden ratio for DALYs and YLDs."""
    try:
        return get_disease_burden_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/breakdown")
async def fetch_level1_breakdown():
    """Fetch Level 1 broad cause category breakdown (Communicable vs NCDs vs Injuries)."""
    try:
        return get_level1_broad_breakdown()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-causes")
async def fetch_top_causes(
    metric: str = Query("daly", pattern="^(daly|yld)$"),
    level: int = Query(2, ge=1, le=4),
    n: int = Query(10, ge=1, le=50),
    sort_by: str = Query("count", pattern="^(count|asr)$"),
):
    """Fetch top N causes by count or age-standardised rate (ASR)."""
    try:
        return get_top_causes(metric=metric, level=level, n=n, sort_by=sort_by)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison")
async def fetch_daly_vs_yld():
    """Fetch comparison matrix of Level 2 causes between fatal DALYs and disabling YLDs."""
    try:
        return {"causes": get_daly_vs_yld_comparison()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/table")
async def fetch_disease_table(
    metric: str = Query("daly", pattern="^(daly|yld)$"),
    level: Optional[int] = Query(None, ge=0, le=4),
    search: Optional[str] = Query(None),
    sort_by: str = Query("count_2023_mean"),
    sort_asc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
):
    """Fetch paginated, searchable cause table for S10 (DALY) or S11 (YLD)."""
    try:
        return get_disease_burden_table(
            metric=metric,
            level=level,
            search=search,
            sort_by=sort_by,
            sort_asc=sort_asc,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
