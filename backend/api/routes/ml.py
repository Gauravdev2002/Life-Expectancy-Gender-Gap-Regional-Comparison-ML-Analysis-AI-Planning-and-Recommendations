"""
api/routes/ml.py
----------------
FastAPI routes exposing Machine Learning (K-Means Clustering and PCA) services.
"""

from fastapi import APIRouter, HTTPException, Query

from ml.clustering import (
    FEATURE_DEFINITIONS,
    run_kmeans_clustering,
)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/features")
async def get_feature_definitions():
    """Returns the descriptions and rationale for the engineered numerical features."""
    return {"features": FEATURE_DEFINITIONS}


@router.get("/clustering")
async def get_clustering_results(
    k: int = Query(3, ge=2, le=6, description="Number of clusters (default 3)"),
    include_aggregates: bool = Query(False, description="Whether to include macro aggregates")
):
    """
    Executes K-Means Clustering and PCA on Dataset S9.
    Returns:
      - Silhouette score and inertia across tested k in [2, 6]
      - PCA 2D coordinates with 83%+ explained variance
      - Cluster profiles with mean, min, max, net gain, and gender gap
      - Location points for scatter plotting
    """
    try:
        results = run_kmeans_clustering(k=k, include_aggregates=include_aggregates)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
