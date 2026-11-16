"""
api/routes/reports.py
---------------------
API routes for Evidence-Based Recommendations and Automated Report Generation.
Provides downloadable Markdown, HTML, and structured JSON reports.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, PlainTextResponse

from recommendations.engine import generate_recommendations
from recommendations.report_generator import (
    compile_full_report,
    generate_markdown_report,
    generate_html_report,
)

router = APIRouter(prefix="/reports", tags=["Recommendations & Reports"])


@router.get("/recommendations")
async def fetch_recommendations(
    low_hle_threshold: float = Query(56.9, ge=40.0, le=75.0),
    gender_gap_threshold: float = Query(5.0, ge=1.0, le=15.0),
    max_per_category: int = Query(15, ge=1, le=50),
):
    """Fetch categorized rule-based surveillance recommendations."""
    try:
        return generate_recommendations(
            low_hle_threshold=low_hle_threshold,
            gender_gap_threshold=gender_gap_threshold,
            max_per_category=max_per_category,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/full")
async def fetch_full_report():
    """Fetch the master intelligence report in structured JSON format."""
    try:
        return compile_full_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/markdown")
async def download_markdown_report():
    """Download the full formatted intelligence report as a GitHub-flavored Markdown file."""
    try:
        content = generate_markdown_report()
        return Response(
            content=content,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": "attachment; filename=regional_health_inequality_report.md"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/html", response_class=HTMLResponse)
async def view_or_print_html_report():
    """Render the full report in an elegant printable HTML format with print-to-PDF styles."""
    try:
        content = generate_html_report()
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
