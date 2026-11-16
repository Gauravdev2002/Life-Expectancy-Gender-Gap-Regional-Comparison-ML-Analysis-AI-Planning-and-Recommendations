# Backend API Service: Regional Health Inequality & Life Expectancy

FastAPI-powered backend intelligence engine providing descriptive epidemiological analytics, unsupervised machine learning, HTN/STRIPS AI planning, and automated surveillance report generation.

---

## 1. Directory Structure

```
backend/
├── analytics/
│   ├── hle_analytics.py        # Location-level HLE time-series & trajectory
│   ├── regional_analytics.py   # SDI quintiles & GBD regional tiers
│   ├── gender_analytics.py     # Sex-disaggregated parity & gap calculations
│   └── disease_analytics.py    # Separate S10 (DALY) & S11 (YLD) cause metrics
├── api/
│   └── routes/
│       ├── health.py           # GET /api/health/
│       ├── overview.py         # GET /api/overview/
│       ├── datasets.py         # /api/datasets/* (raw inspect & summaries)
│       ├── hle.py              # /api/analytics/hle/*
│       ├── regional.py         # /api/analytics/regional/*
│       ├── gender.py           # /api/analytics/gender/*
│       ├── disease.py          # /api/analytics/disease/*
│       ├── ml.py               # /api/ml/*
│       ├── planning.py         # /api/planning/*
│       ├── reports.py          # /api/reports/*
│       └── integration.py      # Canonical Phase 8 REST endpoints
├── core/
│   └── config.py               # App configuration & CORS settings
├── data/
│   ├── loader.py               # Raw Excel loaders (S9, S10, S11)
│   ├── cleaner.py              # Data normalization, typing & flags
│   ├── validator.py            # Integrity constraints & boundary checks
│   ├── summary.py              # Empirical statistical summaries
│   └── pipeline.py             # Singleton in-memory cache & orchestrator
├── ml/
│   └── clustering.py           # StandardScaler, K-Means (k in 2..6), 2D PCA
├── planning/
│   ├── strips.py               # Formal StripsAction & WorldState calculus
│   ├── htn.py                  # Compound goal decompositions & action registry
│   └── executor.py             # Operational runner bridging state transitions
├── recommendations/
│   ├── engine.py               # 4-tier rule-based heuristic surveillance engine
│   └── report_generator.py     # Markdown, HTML/PDF, and JSON generators
├── main.py                     # FastAPI entry point & router mounting
├── requirements.txt            # Runtime dependencies
└── test_master_suite.py        # Master QA automated test suite (50 tests)
```

---

## 2. Setup & Execution

### Prerequisites
- Python 3.10+ (Tested on Python 3.14 on Windows)

### Commands
```powershell
# From the backend directory:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload --port 8000
```

- API Base: `http://localhost:8000`
- Swagger UI Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

---

## 3. Running Automated Tests

Run the master test suite:
```powershell
$env:PYTHONPATH="."
python test_master_suite.py
```
This executes all 50 automated tests across data loading, HLE calculations, gender gaps, regional SDI tiers, K-Means clustering, 2D PCA variance, STRIPS state calculus, HTN decomposition, and all REST endpoints.
