"""
api/routes/hle.py
-----------------
API routes exposing Healthy Life Expectancy (HLE) analytical engines.
Integrates with frontend LifeExpectancy dashboard.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from analytics.hle_analytics import (
    get_available_locations,
    get_location_trend,
    get_hle_comparison,
    get_hle_rankings,
    get_gender_gap_analysis,
    get_comprehensive_location_table,
)

router = APIRouter(prefix="/analytics/hle", tags=["HLE Analytics"])


@router.get("/locations")
async def fetch_locations(include_aggregates: bool = Query(True)):
    """Return sorted list of available locations for selection dropdowns."""
    try:
        locs = get_available_locations(include_aggregates=include_aggregates)
        return {"count": len(locs), "locations": locs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend")
async def fetch_location_trend(location: str = Query("Global")):
    """
    Return historical year-wise HLE trend (1990, 2010, 2020, 2023),
    gender disaggregation, calculated gender gap, and summary KPIs for a specific location.
    """
    try:
        data = get_location_trend(location=location)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison")
async def fetch_comparison(
    locations: Optional[str] = Query(None, description="Comma-separated location names"),
    year: int = Query(2023),
    sex: str = Query("both", pattern="^(both|female|male)$")
):
    """Compare HLE across locations for a given year and sex."""
    try:
        loc_list = [l.strip() for l in locations.split(",")] if locations else None
        return get_hle_comparison(locations=loc_list, year=year, sex=sex)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rankings")
async def fetch_rankings(
    year: int = Query(2023),
    sex: str = Query("both", pattern="^(both|female|male)$"),
    include_aggregates: bool = Query(False),
    n: int = Query(10, ge=1, le=50)
):
    """Retrieve top N highest and bottom N lowest HLE locations."""
    try:
        return get_hle_rankings(year=year, sex=sex, include_aggregates=include_aggregates, n=n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gender-gap")
async def fetch_gender_gap(
    year: int = Query(2023),
    include_aggregates: bool = Query(False),
    n: int = Query(10, ge=1, le=50)
):
    """Calculate and rank locations by Gender HLE Gap (Female HLE - Male HLE)."""
    try:
        return get_gender_gap_analysis(year=year, include_aggregates=include_aggregates, n=n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/table")
async def fetch_table(
    search: Optional[str] = Query(None),
    include_aggregates: bool = Query(True),
    sort_by: str = Query("hle_2023"),
    sort_asc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100)
):
    """Paginated, searchable, sortable location-wise table."""
    try:
        return get_comprehensive_location_table(
            search=search,
            include_aggregates=include_aggregates,
            sort_by=sort_by,
            sort_asc=sort_asc,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
