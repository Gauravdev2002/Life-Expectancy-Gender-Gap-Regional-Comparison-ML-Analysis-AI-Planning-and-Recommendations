"""
api/routes/regional.py
----------------------
API endpoints for Regional Comparison and Trend Analysis.
Exposes comparative groupings (SDI quintiles, GBD super-regions, GBD regions),
increase/decrease trajectories, and top/bottom rankings.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from analytics.regional_analytics import (
    get_grouping_names,
    get_regional_comparison,
    get_regional_historical_trends,
    get_increase_decrease_analysis,
    get_top_and_bottom_locations,
)

router = APIRouter(prefix="/analytics/regional", tags=["Regional Comparison"])


@router.get("/groupings")
async def fetch_grouping_names():
    """Returns available regional classification structures."""
    try:
        return get_grouping_names()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison")
async def fetch_regional_comparison(
    grouping: str = Query("sdi", pattern="^(sdi|super_regions|regions)$"),
    year: int = Query(2023),
    sex: str = Query("both", pattern="^(both|female|male)$")
):
    """Compare HLE across regional tiers or SDI quintiles for a chosen year and sex."""
    try:
        return get_regional_comparison(grouping=grouping, year=year, sex=sex)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def fetch_regional_trends(
    grouping: str = Query("sdi", pattern="^(sdi|super_regions|regions)$")
):
    """Time-series trajectory matrix across regional groupings (1990, 2010, 2020, 2023)."""
    try:
        return get_regional_historical_trends(grouping=grouping)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/increase-decrease")
async def fetch_increase_decrease(
    include_aggregates: bool = Query(False),
    n: int = Query(5, ge=1, le=50)
):
    """Identifies locations with the largest percentage increases and decreases between 2010 and 2023."""
    try:
        return get_increase_decrease_analysis(include_aggregates=include_aggregates, n=n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-bottom")
async def fetch_top_bottom(
    year: int = Query(2023),
    include_aggregates: bool = Query(False),
    n: int = Query(5, ge=1, le=50)
):
    """Retrieve detailed Top 5 and Bottom 5 location tables for the latest year."""
    try:
        return get_top_and_bottom_locations(year=year, include_aggregates=include_aggregates, n=n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
