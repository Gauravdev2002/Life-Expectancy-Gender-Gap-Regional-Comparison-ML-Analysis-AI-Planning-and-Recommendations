"""
api/routes/gender.py
--------------------
API routes for Gender Health Inequality Analysis.
Provides endpoints for global benchmarks, SDI gradients, rankings,
scatter plot datasets, and paginated tabular data.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from analytics.gender_analytics import (
    get_gender_gap_overview,
    get_gender_rankings,
    get_gender_scatter_data,
    get_gender_comparison_table,
)

router = APIRouter(prefix="/analytics/gender", tags=["Gender Analytics"])


@router.get("/overview")
async def fetch_gender_overview(year: int = Query(2023, ge=1990, le=2023)):
    """Fetch global benchmarks, SDI gradients, historical trajectories, and distributions."""
    try:
        return get_gender_gap_overview(year=year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rankings")
async def fetch_gender_rankings(
    year: int = Query(2023, ge=1990, le=2023),
    n: int = Query(10, ge=1, le=50),
):
    """Fetch top N largest female advantages and narrowest/reversed gender gaps."""
    try:
        return get_gender_rankings(year=year, n=n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scatter")
async def fetch_gender_scatter(
    year: int = Query(2023, ge=1990, le=2023),
    max_points: int = Query(200, ge=20, le=1000),
):
    """Fetch Female HLE vs Male HLE scatter data with equality line reference."""
    try:
        return {"year": year, "points": get_gender_scatter_data(year=year, max_points=max_points)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/table")
async def fetch_gender_table(
    year: int = Query(2023, ge=1990, le=2023),
    search: Optional[str] = Query(None),
    sort_by: str = Query("gender_gap"),
    sort_asc: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
):
    """Fetch paginated, searchable gender gap comparison table."""
    try:
        return get_gender_comparison_table(
            year=year,
            search=search,
            sort_by=sort_by,
            sort_asc=sort_asc,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
