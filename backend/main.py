"""
main.py
-------
FastAPI application entry point.

How it works:
  1. Creates the FastAPI app with metadata.
  2. Adds CORS middleware so the React frontend (port 5173) can call the API.
  3. Registers all API routers (each router handles one feature area).
  4. Run with:  uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.routes.health   import router as health_router
from api.routes.overview import router as overview_router
from api.routes.datasets import router as datasets_router
from api.routes.hle      import router as hle_router
from api.routes.regional import router as regional_router
from api.routes.ml       import router as ml_router
from api.routes.planning import router as planning_router
from api.routes.gender   import router as gender_router
from api.routes.disease  import router as disease_router
from api.routes.reports  import router as reports_router
from api.routes.integration import router as integration_router

# ---------------------------------------------------------------------------
# Create the FastAPI application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Backend API for the AI-Based Regional Health Inequality "
        "and Life Expectancy Intelligence System."
    ),
    docs_url="/docs",   # Swagger UI  → http://localhost:8000/docs
    redoc_url="/redoc", # ReDoc UI    → http://localhost:8000/redoc
)

# ---------------------------------------------------------------------------
# CORS – allow the Vite/React dev server to call this API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register routers
# Each router is a separate file inside api/routes/
# ---------------------------------------------------------------------------
app.include_router(health_router,   prefix="/api")   # /api/health/
app.include_router(overview_router, prefix="/api")   # /api/overview/
app.include_router(datasets_router, prefix="/api")   # /api/datasets/
app.include_router(hle_router,      prefix="/api")   # /api/analytics/hle/
app.include_router(regional_router, prefix="/api")   # /api/analytics/regional/
app.include_router(ml_router,       prefix="/api")   # /api/ml/
app.include_router(planning_router, prefix="/api")   # /api/planning/
app.include_router(gender_router,   prefix="/api")   # /api/analytics/gender/
app.include_router(disease_router,  prefix="/api")   # /api/analytics/disease/
app.include_router(reports_router,  prefix="/api")   # /api/reports/
app.include_router(integration_router, prefix="/api") # Phase 8 Canonical Integration Endpoints

# ---------------------------------------------------------------------------
# Static frontend serving (Optional unified full-stack deployment)
# If frontend/dist is built, FastAPI serves both frontend and API from 1 service!
# ---------------------------------------------------------------------------
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

_DIST_CANDIDATES = [
    os.environ.get("FRONTEND_DIST"),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")),
    os.path.abspath(os.path.join(os.getcwd(), "frontend", "dist")),
    os.path.abspath(os.path.join(os.getcwd(), "dist")),
]
_DIST_DIR = next((p for p in _DIST_CANDIDATES if p and os.path.isdir(p)), None)

if _DIST_DIR:
    assets_dir = os.path.join(_DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Do not catch /api, /docs, /redoc, /openapi.json
        if full_path.startswith(("api", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404, detail="Not Found")
        
        file_path = os.path.join(_DIST_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(_DIST_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return {"message": f"Welcome to {settings.APP_NAME} API", "docs": "/docs"}
else:
    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME} API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
        }


# ---------------------------------------------------------------------------
# Run directly (development only)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
