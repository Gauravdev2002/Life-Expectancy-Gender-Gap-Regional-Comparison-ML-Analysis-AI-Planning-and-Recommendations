"""
api/routes/health.py
--------------------
Simple health-check endpoint.
Useful to verify the backend is running before connecting the frontend.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("/")
async def health_check():
    """Returns a simple status message so the frontend can ping the backend."""
    return {
        "status": "ok",
        "message": "Health Inequality Intelligence System backend is running.",
    }
