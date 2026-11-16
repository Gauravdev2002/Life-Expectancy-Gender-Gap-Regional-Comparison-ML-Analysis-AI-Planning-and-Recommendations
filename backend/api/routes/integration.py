"""
api/routes/integration.py
-------------------------
Unified Phase 8 REST API integration endpoints.
Directly maps the canonical REST endpoints requested for complete frontend-backend integration:

  - GET  /api/metadata
  - GET  /api/analyze/hle
  - GET  /api/analyze/gender-gap
  - GET  /api/analyze/trends
  - GET  /api/analyze/regional-comparison
  - GET  /api/ml/clusters
  - GET  /api/global-burden/daly
  - GET  /api/global-burden/yld
  - POST /api/plan
  - GET  /api/recommendations
  - GET  /api/reports
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from data.pipeline import get_s9, get_s10, get_s11
from analytics.hle_analytics import (
    get_available_locations,
    get_location_trend,
    get_hle_rankings,
    get_comprehensive_location_table,
)
from analytics.gender_analytics import (
    get_gender_gap_overview,
    get_gender_rankings,
    get_gender_scatter_data,
    get_gender_comparison_table,
)
from analytics.regional_analytics import (
    get_regional_comparison,
    get_regional_historical_trends,
    get_increase_decrease_analysis,
    get_top_and_bottom_locations,
)
from ml.clustering import run_kmeans_clustering, FEATURE_DEFINITIONS
from analytics.disease_analytics import (
    get_disease_burden_overview,
    get_level1_broad_breakdown,
    get_top_causes,
    get_daly_vs_yld_comparison,
    get_disease_burden_table,
)
from planning.htn import HtnPlanner, COMPOUND_GOALS
from planning.executor import PlanExecutor

planner = HtnPlanner()
executor = PlanExecutor()
from recommendations.engine import generate_recommendations
from recommendations.report_generator import compile_full_report

router = APIRouter(tags=["Phase 8 Integration Endpoints"])


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------
class PlanRequest(BaseModel):
    goal_id: str = Field(..., description="Target compound planning goal identifier")


# ---------------------------------------------------------------------------
# 1. GET /api/metadata
# ---------------------------------------------------------------------------
@router.get("/metadata")
async def get_system_metadata():
    """
    Returns unified metadata across all datasets, models, and capabilities.
    """
    try:
        s9 = get_s9()
        s10 = get_s10()
        s11 = get_s11()

        return {
            "system_name": "AI-Based Regional Health Inequality and Life Expectancy Intelligence System",
            "version": "1.0.0",
            "status": "Operational & Fully Integrated",
            "datasets": [
                {
                    "id": "S9",
                    "title": "Healthy Life Expectancy By Location and Sex",
                    "total_records": len(s9),
                    "unique_locations": int(s9["location"].nunique()),
                    "years_covered": [1990, 2010, 2020, 2023],
                    "sexes": ["both", "female", "male"],
                    "scope": "Subnational, national, regional, and global HLE with 95% UI",
                },
                {
                    "id": "S10",
                    "title": "Global DALY Counts and Age-Standardised Rate Changes",
                    "total_causes": len(s10),
                    "hierarchy_levels": [0, 1, 2, 3, 4],
                    "metrics": ["count_2010", "count_2023", "count_pct_change", "asr_2010", "asr_2023", "asr_pct_change"],
                    "scope": "Global both-sexes cause-level DALYs (premature death + disability)",
                },
                {
                    "id": "S11",
                    "title": "Global YLD Counts and Age-Standardised Rate Changes",
                    "total_causes": len(s11),
                    "hierarchy_levels": [0, 1, 2, 3, 4],
                    "metrics": ["count_2010", "count_2023", "count_pct_change", "asr_2010", "asr_2023", "asr_pct_change"],
                    "scope": "Global both-sexes cause-level YLDs (pure chronic non-fatal disability)",
                },
            ],
            "capabilities": {
                "hle_analytics": True,
                "gender_gap_analysis": True,
                "regional_comparison": True,
                "ml_clustering": True,
                "global_disease_burden": True,
                "ai_planning": True,
                "recommendation_engine": True,
                "report_generation": True,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metadata: {str(e)}")


# ---------------------------------------------------------------------------
# 2. GET /api/analyze/hle
# ---------------------------------------------------------------------------
@router.get("/analyze/hle")
async def analyze_hle(
    location: str = Query("Global", description="Target location name"),
    year: int = Query(2023, ge=1990, le=2023),
    sex: str = Query("both", pattern="^(both|female|male)$"),
    n_rankings: int = Query(10, ge=1, le=50),
):
    """
    Returns comprehensive HLE analysis for a location, including trajectory,
    summary KPIs, and global rankings.
    """
    try:
        trend_data = get_location_trend(location=location)
        rankings = get_hle_rankings(year=year, sex=sex, include_aggregates=False, n=n_rankings)
        return {
            "selected_location": trend_data.get("location"),
            "is_aggregate": trend_data.get("is_aggregate"),
            "year": year,
            "sex": sex,
            "summary_kpis": trend_data.get("summary_kpis", {}),
            "historical_trends": trend_data.get("trends", []),
            "global_rankings": {
                "highest": rankings.get("highest", []),
                "lowest": rankings.get("lowest", []),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HLE analysis error: {str(e)}")


# ---------------------------------------------------------------------------
# 3. GET /api/analyze/gender-gap
# ---------------------------------------------------------------------------
@router.get("/analyze/gender-gap")
async def analyze_gender_gap(
    year: int = Query(2023, ge=1990, le=2023),
    n: int = Query(10, ge=1, le=50),
    max_scatter_points: int = Query(100, ge=10, le=500),
):
    """
    Returns full Gender Gap analysis including global benchmarks, SDI gradients,
    extreme female advantages vs reversed gaps, and scatter parity data.
    """
    try:
        overview = get_gender_gap_overview(year=year)
        rankings = get_gender_rankings(year=year, n=n)
        scatter = get_gender_scatter_data(year=year, max_points=max_scatter_points)
        return {
            "year": year,
            "global_benchmarks": {
                "global_female_hle": overview.get("global_female_hle"),
                "global_male_hle": overview.get("global_male_hle"),
                "global_gender_gap": overview.get("global_gender_gap"),
                "global_parity_ratio": overview.get("global_parity_ratio"),
            },
            "sdi_gradient": overview.get("sdi_gradient", []),
            "historical_trajectory": overview.get("historical_trajectory", []),
            "country_distribution": overview.get("country_distribution", {}),
            "rankings": rankings,
            "scatter_points": scatter,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gender gap analysis error: {str(e)}")


# ---------------------------------------------------------------------------
# 4. GET /api/analyze/trends
# ---------------------------------------------------------------------------
@router.get("/analyze/trends")
async def analyze_trends(
    grouping: str = Query("sdi", pattern="^(sdi|super_regions|regions)$"),
    include_gainers_decliners: bool = Query(True),
    n: int = Query(5, ge=1, le=20),
):
    """
    Returns multi-year historical HLE trajectories (1990–2023) across regional tiers,
    along with locations experiencing the largest increases and decreases.
    """
    try:
        trajectories = get_regional_historical_trends(grouping=grouping)
        increase_decrease = (
            get_increase_decrease_analysis(include_aggregates=False, n=n)
            if include_gainers_decliners
            else None
        )
        return {
            "grouping": grouping,
            "trajectories": trajectories,
            "gainers_and_decliners": increase_decrease,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trends analysis error: {str(e)}")


# ---------------------------------------------------------------------------
# 5. GET /api/analyze/regional-comparison
# ---------------------------------------------------------------------------
@router.get("/analyze/regional-comparison")
async def analyze_regional_comparison(
    grouping: str = Query("sdi", pattern="^(sdi|super_regions|regions)$"),
    year: int = Query(2023, ge=1990, le=2023),
    sex: str = Query("both", pattern="^(both|female|male)$"),
    n_rankings: int = Query(5, ge=1, le=20),
):
    """
    Compares HLE, gender gaps, and 2010–2023 percentage changes across regional tiers.
    """
    try:
        comparison_data = get_regional_comparison(grouping=grouping, year=year, sex=sex)
        top_bottom = get_top_and_bottom_locations(year=year, include_aggregates=False, n=n_rankings)
        return {
            "grouping": grouping,
            "year": year,
            "sex": sex,
            "regional_records": comparison_data,
            "top_locations": top_bottom.get("top_locations", []),
            "bottom_locations": top_bottom.get("bottom_locations", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regional comparison error: {str(e)}")


# ---------------------------------------------------------------------------
# 6. GET /api/ml/clusters
# ---------------------------------------------------------------------------
@router.get("/ml/clusters")
async def analyze_ml_clusters(
    k: int = Query(3, ge=2, le=6),
    include_aggregates: bool = Query(False),
):
    """
    Executes K-Means Clustering and 2D PCA on Dataset S9, returning cluster profiles,
    silhouette evaluation, and 2D projection coordinates.
    """
    try:
        return run_kmeans_clustering(k=k, include_aggregates=include_aggregates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Machine learning clustering error: {str(e)}")


# ---------------------------------------------------------------------------
# 7. GET /api/global-burden/daly
# ---------------------------------------------------------------------------
@router.get("/global-burden/daly")
async def get_global_burden_daly(
    level: int = Query(2, ge=1, le=4),
    top_n: int = Query(10, ge=1, le=50),
    sort_by: str = Query("count", pattern="^(count|asr)$"),
):
    """
    Returns global DALY metrics from Dataset S10 (premature death + disability).
    """
    try:
        overview = get_disease_burden_overview()
        breakdown = get_level1_broad_breakdown()
        top_causes = get_top_causes(metric="daly", level=level, n=top_n, sort_by=sort_by)
        return {
            "metric": "daly",
            "title": "Disability-Adjusted Life Years (DALYs) - Dataset S10",
            "summary": overview.get("daly_summary", {}),
            "level1_categories": breakdown.get("daly_categories", []),
            "top_causes": top_causes,
            "isolation_note": "S10 is global cause-level data, strictly isolated from S9 country records.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Global DALY fetch error: {str(e)}")


# ---------------------------------------------------------------------------
# 8. GET /api/global-burden/yld
# ---------------------------------------------------------------------------
@router.get("/global-burden/yld")
async def get_global_burden_yld(
    level: int = Query(2, ge=1, le=4),
    top_n: int = Query(10, ge=1, le=50),
    sort_by: str = Query("count", pattern="^(count|asr)$"),
):
    """
    Returns global YLD metrics from Dataset S11 (living with chronic disability).
    """
    try:
        overview = get_disease_burden_overview()
        breakdown = get_level1_broad_breakdown()
        top_causes = get_top_causes(metric="yld", level=level, n=top_n, sort_by=sort_by)
        return {
            "metric": "yld",
            "title": "Years Lived with Disability (YLDs) - Dataset S11",
            "summary": overview.get("yld_summary", {}),
            "chronic_disability_share_percent": overview.get("disability_share_percent"),
            "level1_categories": breakdown.get("yld_categories", []),
            "top_causes": top_causes,
            "isolation_note": "S11 is global cause-level data, strictly isolated from S9 country records.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Global YLD fetch error: {str(e)}")


# ---------------------------------------------------------------------------
# 9. POST /api/plan
# ---------------------------------------------------------------------------
@router.post("/plan")
async def plan_and_execute(req: PlanRequest):
    """
    Accepts a user's compound analytical goal, decomposes it via HTN into primitive
    tasks, and executes the state-based STRIPS workflow, returning live trace & brief.
    """
    try:
        goal_id = req.goal_id.strip().upper()
        if goal_id not in COMPOUND_GOALS:
            valid_goals = list(COMPOUND_GOALS.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported goal '{goal_id}'. Must be one of: {valid_goals}",
            )

        decomposition = planner.decompose(goal_id)
        execution_result = executor.execute_goal(goal_id)

        return {
            "status": "success",
            "goal_id": goal_id,
            "goal_title": COMPOUND_GOALS[goal_id]["title"],
            "decomposition": decomposition,
            "execution": execution_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Planning error: {str(e)}")


# ---------------------------------------------------------------------------
# 10. GET /api/recommendations
# ---------------------------------------------------------------------------
@router.get("/recommendations")
async def get_system_recommendations(
    low_hle_threshold: float = Query(56.9, ge=40.0, le=75.0),
    gender_gap_threshold: float = Query(5.0, ge=1.0, le=15.0),
    max_per_category: int = Query(15, ge=1, le=50),
):
    """
    Returns transparent rule-based public health surveillance flags across 4 categories:
    Low HLE, HLE Decline, Gender Disparity, and ML Cluster Groups.
    """
    try:
        return generate_recommendations(
            low_hle_threshold=low_hle_threshold,
            gender_gap_threshold=gender_gap_threshold,
            max_per_category=max_per_category,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations error: {str(e)}")


# ---------------------------------------------------------------------------
# 11. GET /api/reports
# ---------------------------------------------------------------------------
@router.get("/reports")
async def get_master_report():
    """
    Returns the comprehensive, consolidated health intelligence report.
    """
    try:
        return compile_full_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report compilation error: {str(e)}")
