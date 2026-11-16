# AI-Based Regional Health Inequality and Life Expectancy Intelligence System

An end-to-end, explainable artificial intelligence and data intelligence platform developed for analyzing global and regional health inequalities, gender life expectancy gaps, socio-demographic disparities, and disease burdens.

Built with **React.js**, **Tailwind CSS**, **Recharts**, **Python**, **FastAPI**, **Pandas**, **Scikit-learn**, and classical **HTN/STRIPS AI Planning**.

---

## 1. Project Architecture

The platform is designed with a strict four-layer architecture ensuring scientific validity, explainability, and zero hallucinated or fake statistics:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER (REACT 18)                        │
│  - Tailwind CSS Light Theme        - Recharts Interactive Graphs               │
│  - Multi-Year Trajectory Lines     - Parity Reference Scatter Plots            │
│  - Disease Morbidity Matrices      - HTN/STRIPS Execution Visualizer           │
│  - PDF/Print & Markdown Exporter   - Paginated Searchable Tables               │
└───────────────────────────────────────┬────────────────────────────────────────┘
                                        │ REST API (JSON / HTTP)
┌───────────────────────────────────────▼────────────────────────────────────────┐
│                        API & ROUTING LAYER (FASTAPI)                           │
│  - /api/metadata                   - /api/analyze/hle                          │
│  - /api/analyze/gender-gap         - /api/analyze/trends                       │
│  - /api/analyze/regional           - /api/ml/clusters                          │
│  - /api/global-burden/daly         - /api/global-burden/yld                    │
│  - /api/plan (HTN/STRIPS)          - /api/recommendations & /reports           │
└──────────────────┬────────────────────┬────────────────────┬───────────────────┘
                   │                    │                    │
┌──────────────────▼──────┐ ┌───────────▼──────────┐ ┌───────▼──────────────────┐
│  DATA & ANALYTICS LAYER │ │  MACHINE LEARNING    │ │    AI PLANNING ENGINE    │
│  - Multi-Year HLE (S9)  │ │  - StandardScaler    │ │  - STRIPS Preconditions  │
│  - Gender Gap (F - M)   │ │  - K-Means (k in 2..6│ │  - Monotonic Transitions │
│  - SDI Quintiles Span   │ │  - Silhouette Score  │ │  - Frame Problem Solution│
│  - S10 DALYs / S11 YLDs │ │  - 2D PCA (83.8% Var)│ │  - HTN Goal Decomposition│
└─────────────────────────┘ └──────────────────────┘ └──────────────────────────┘
```

---

## 2. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, Recharts, React Router v6 |
| **Backend** | Python 3.14, FastAPI, Uvicorn, Pydantic v2 |
| **Data Processing** | Pandas, NumPy, OpenPyXL |
| **Machine Learning** | Scikit-learn (K-Means Clustering, PCA, StandardScaler, Silhouette Score) |
| **AI Planning** | STRIPS Action Formalism, WorldState Calculus, HTN Compound Task Decomposer |
| **Surveillance & Reports** | Deterministic Heuristic Rule-Engine, GitHub-Flavored Markdown, CSS Print-to-PDF |

---

## 3. Verified Empirical Datasets

All metrics derive strictly from the three actual Global Burden of Disease (GBD 2023) Excel files located in `datasets/`:

1. **`S9_Healthy_Life_Expectancy_By_Location_and_Sex.xlsx` (Primary Dataset)**:
   - Contains location-level estimates across 860 locations (national, regional, subnational) for 1990, 2010, 2020, and 2023.
   - Provides Both Sexes, Female, and Male HLE, along with 2010–2023 percentage change.
   - Retains 95% uncertainty intervals `[Lower, Upper]` for all values.
2. **`S10_Global_DALY_Counts_and_Age_Standardised_Rate_Changes.xlsx`**:
   - Contains global both-sexes Disability-Adjusted Life Years (DALYs) across 376 causes in a 5-tier hierarchy (Levels 0–4).
   - Captures comprehensive health loss combining premature mortality (YLL) and lived disability (YLD).
3. **`S11_Global_YLD_Counts_and_Age_Standardised_Rate_Changes.xlsx`**:
   - Contains global both-sexes Years Lived with Disability (YLDs) across 376 causes.
   - Isolates chronic non-fatal morbidity (living with disability).

> **DEMOGRAPHIC ISOLATION RULE:** S10 and S11 are global cause-level aggregates. To preserve scientific validity and prevent ecological fallacies, they are maintained as separate context and **never merged** onto location records in S9.

---

## 4. Key Empirical Findings (Verified Against Excel Data)

- **Global Healthy Life Expectancy (2023)**: **63.1 years** (95% UI: [60.2, 65.6]), an increase of $+7.2$ years since 1990 (55.9 yrs).
- **Global Gender Gap (2023)**: **+2.0 years** ($\text{Female } 64.2\text{ yrs} - \text{Male } 62.2\text{ yrs}$), Parity Ratio: **1.032**.
- **Socio-demographic Inequality Span**: **11.0 years** difference between High SDI (**67.9 yrs**) and Low SDI (**56.9 yrs**).
- **Extreme Gender Gaps**: Widest in Eastern Europe (Ukraine $+7.9$ yrs, Russia $+7.3$ yrs); reversed gaps in Balochistan ($-3.0$ yrs) and UAE ($-2.8$ yrs).
- **Global Disease Burden**: **2.80 Billion DALYs** and **990 Million YLDs**. Chronic disability accounts for **35.4%** of all global health span loss.
- **Epidemiological Shift**: Non-Communicable Diseases (NCDs) now drive **64.4%** of DALYs and **80.5%** of YLDs.
- **Mental Disorders Morbidity Surge**: Mental disorders are the #1 cause of lived disability (171M YLDs), surging **+25.0%** in age-standardised rate from 2010 to 2023.

---

## 5. Summary of Implemented Algorithms

### Algorithm 1: K-Means Clustering
- **Feature Matrix**: 9 standardized continuous epidemiological features extracted from Dataset S9:
  `[hle_1990, hle_2010, hle_2020, hle_2023, female_hle_2023, male_hle_2023, gender_gap_2023, net_gain_1990_2023, pct_change_2010_2023]`.
- **Feature Scaling**: Normalized using `StandardScaler` ($\mu = 0, \sigma = 1$).
- **Cluster Selection**: Evaluated across candidate $k \in [2, 6]$ using the **Silhouette Score**; $k=3$ was selected as the optimal trade-off between clustering cohesion ($0.384$) and human interpretability:
  - **Cluster 0**: *High Vulnerability & Developing Infrastructure* (Mean HLE: 56.8 yrs).
  - **Cluster 1**: *Transitional & Emerging Health Systems* (Mean HLE: 63.8 yrs).
  - **Cluster 2**: *High Life Expectancy & Resilient Health Systems* (Mean HLE: 70.7 yrs).

### Algorithm 2: 2D Principal Component Analysis (PCA)
- Reduces the 9-dimensional standardized feature space to 2 orthogonal principal components:
  - **PC1 (69.7% of variance)**: Captures baseline health development and overall longevity level.
  - **PC2 (14.1% of variance)**: Captures longitudinal momentum, net progress, and gender gap magnitude.
  - **Total Explained Variance**: **83.8%** of all information retained in the 2D visual projection.

### Algorithm 3: STRIPS Action Schema & The Classical Frame Problem
- **Formalism**: Actions defined as triplets $\langle \text{Preconditions}, \text{Add Effects}, \text{Delete Effects} \rangle$.
- **Applicability Rule**: Action $a$ can be executed in state $S$ if and only if $\text{Preconditions}(a) \subseteq S$.
- **State Transition Equation**:
  $$\text{State}_{t+1} = (\text{State}_t \setminus \text{Delete Effects}) \cup \text{Add Effects}$$
- **Frame Problem Resolution**: Facts not explicitly listed in delete effects persist unchanged without requiring explicit non-change axioms.

### Algorithm 4: Hierarchical Task Network (HTN) Decomposition
- Defines 5 distinct compound user goals:
  - `ANALYZE_HEALTH_INEQUALITY`
  - `COMPARE_REGIONAL_HLE`
  - `ANALYZE_GENDER_GAP`
  - `IDENTIFY_LOW_HLE_LOCATIONS`
  - `GENERATE_HEALTH_REPORT`
- Distinct compound goals decompose into different ordered sequences of primitive STRIPS tasks, proving that the planner is intelligent and goal-differentiated rather than a fixed linear script.

### Algorithm 5: Heuristic Policy Surveillance Engine
- Deterministic rule engine assigning 4 categorized surveillance flags:
  1. `FLAG_LOW_HLE`: HLE $< 56.9$ yrs (Low SDI benchmark).
  2. `FLAG_HLE_DECLINE`: Negative progress between 2010 and 2023.
  3. `FLAG_LARGE_GENDER_GAP`: Extreme disparity ($\ge 5.0$ yrs or reversed gap $< 0$).
  4. `FLAG_CLUSTER_PROFILE`: Macro-policy strategies tailored to K-Means clusters.

---

## 6. Installation & Execution Guide

### Prerequisites
- **Python**: Version 3.10+ (Tested on Python 3.14)
- **Node.js**: Version 18+ and `npm`

### Step 1: Clone or Navigate to Project Directory
```powershell
cd "c:\Users\gy696\OneDrive\Desktop\AI project"
```

### Step 2: Backend Setup
```powershell
cd backend
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload --port 8000
```
Backend API will be running at `http://localhost:8000`  
Swagger Interactive API Documentation: `http://localhost:8000/docs`

### Step 3: Frontend Setup
Open a separate PowerShell terminal window:
```powershell
cd "c:\Users\gy696\OneDrive\Desktop\AI project\frontend"

# Install npm dependencies (if not already installed)
npm install

# Start the Vite development server
npm run dev
```
Frontend Dashboard will open at `http://localhost:5173`

---

## 7. College Project Demonstration Workflow

When presenting this project to external examiners or professors, follow this structured 8-step demonstration path:

1. **Overview Dashboard (`/overview`)**:
   - Point out the real-time green connection banner to FastAPI.
   - Highlight the live KPI cards: Global HLE (63.1 yrs), Global Gender Gap (+2.0 yrs), and ML Cluster parameters.
2. **Life Expectancy Analysis (`/life-expectancy`)**:
   - Demonstrate the location dropdown (e.g. choose "Japan", "India", or "Central African Republic").
   - Show how the line chart updates historical trajectories for Both Sexes, Female, and Male.
   - Point out that uncertainty intervals `[Lower, Upper]` are preserved.
3. **Gender Gap Analysis (`/gender-gap`)**:
   - Showcase the Parity Scatter Plot ($y = x$ line).
   - Switch years between 1990 and 2023 to demonstrate historical gender convergence/divergence.
   - Explain why Ukraine (+7.9 yrs) and Russia (+7.3 yrs) have massive male mortality deficits, while Balochistan (-3.0 yrs) exhibits a reversed gap.
4. **Regional Comparison (`/regional`)**:
   - Switch groupings between SDI Quintiles, GBD Super-Regions, and GBD Analytical Regions.
   - Show the 11.0-year developmental gap between High SDI (67.9 yrs) and Low SDI (56.9 yrs).
5. **Machine Learning Analysis (`/ml-analysis`)**:
   - Explain feature standardization via `StandardScaler`.
   - Interact with the $k$-slider: show how silhouette scores vary across $k \in [2, 6]$.
   - Show the 2D PCA scatter plot capturing 83.8% of feature variance.
6. **Disease Burden & Disability (`/disease-burden`)**:
   - Explain the demographic isolation rule (why S10/S11 are not joined to country S9 records).
   - Toggle between DALYs (fatal + disabling) and YLDs (disability).
   - Point out the #1 disabling cause: Mental Disorders (+25.0% surge).
7. **AI Planning (`/ai-planning`)**:
   - Select different compound goals (e.g., `ANALYZE_GENDER_GAP` vs. `COMPARE_REGIONAL_HLE`).
   - Show that the planner generates different HTN task plans.
   - Click **Run Live Execution** to watch the STRIPS state transitions in real time and view the synthesized evidence brief.
8. **Recommendations & Downloadable Reports (`/recommendations`)**:
   - Review the 4 categorized surveillance flag tabs.
   - Click **Print / PDF Report** to show the styled printable report.
   - Click **Download Markdown** to show export versatility.

---

## 8. Important Viva Questions & Model Answers

### Q1: What makes this project an "Intelligence System" rather than just a basic data dashboard?
> **Answer:** A dashboard merely plots raw values. This system couples descriptive epidemiology with **two automated artificial intelligence layers**:
> 1. **Unsupervised Machine Learning**: Automatically classifies countries into developmental tiers using continuous multivariate trajectory vectors and projects them onto principal components.
> 2. **HTN & STRIPS AI Planning**: Accepts high-level analytical goals, decomposes them into domain tasks, verifies preconditions, resolves the Frame Problem during state transitions, and autonomously synthesizes evidence-based policy briefs.

### Q2: How does the AI Planner resolve the Classical Frame Problem?
> **Answer:** The Frame Problem concerns how an agent can represent that most facts in a world state remain unchanged when an action occurs. In this system, every STRIPS action defines explicit `add_effects` and `delete_effects`. The transition calculus updates state $S$ via:
> $$S_{t+1} = (S_t \setminus \text{Delete Effects}) \cup \text{Add Effects}$$
> Facts not in `delete_effects` are guaranteed to persist without writing explicit persistence axioms for every untouched predicate.

### Q3: Why are datasets S10 and S11 kept separate from dataset S9?
> **Answer:** Dataset S9 contains location-specific records across countries and subnational units. Datasets S10 and S11 are global cause-level aggregates across both sexes. Merging global cause numbers onto individual country records would commit the **Ecological Fallacy**—falsely attributing global cause distributions to a specific national population without country-specific cause-of-death data.

### Q4: Why did you use K-Means and PCA together?
> **Answer:** K-Means operates in the original 9-dimensional standardized feature space, finding geometric cluster centroids. However, 9-dimensional clusters cannot be visualized directly by humans. PCA performs orthogonal linear dimensionality reduction, projecting the 9 features onto 2 principal components while retaining **83.8% of total variance**, providing visual explainability of cluster boundaries.

### Q5: What are the ethical and epistemological limitations?
> **Answer:**
> 1. **No Causal Inferences**: Statistical correlations and cluster memberships demonstrate empirical associations; they do not establish direct clinical causation.
> 2. **Non-Clinical Boundaries**: The system is designed strictly for macro-level public health surveillance and health system resource planning; it provides **no individual medical diagnoses or clinical patient treatments**.

---

## 9. Final Project Directory Structure

```
AI project/
├── datasets/
│   ├── S9_Healthy_Life_Expectancy_By_Location_and_Sex.xlsx
│   ├── S10_Global_DALY_Counts_and_Age_Standardised_Rate_Changes.xlsx
│   └── S11_Global_YLD_Counts_and_Age_Standardised_Rate_Changes.xlsx
├── backend/
│   ├── analytics/
│   │   ├── hle_analytics.py
│   │   ├── regional_analytics.py
│   │   ├── gender_analytics.py
│   │   └── disease_analytics.py
│   ├── api/
│   │   └── routes/
│   │       ├── health.py
│   │       ├── overview.py
│   │       ├── datasets.py
│   │       ├── hle.py
│   │       ├── regional.py
│   │       ├── gender.py
│   │       ├── disease.py
│   │       ├── ml.py
│   │       ├── planning.py
│   │       ├── reports.py
│   │       └── integration.py
│   ├── core/
│   │   └── config.py
│   ├── data/
│   │   ├── loader.py
│   │   ├── cleaner.py
│   │   ├── validator.py
│   │   ├── summary.py
│   │   └── pipeline.py
│   ├── ml/
│   │   └── clustering.py
│   ├── planning/
│   │   ├── strips.py
│   │   ├── htn.py
│   │   └── executor.py
│   ├── recommendations/
│   │   ├── engine.py
│   │   └── report_generator.py
│   ├── main.py
│   ├── requirements.txt
│   └── test_master_suite.py
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Sidebar.jsx
    │   │   ├── TopBar.jsx
    │   │   ├── PageHeader.jsx
    │   │   └── StatCard.jsx
    │   ├── pages/
    │   │   ├── Overview.jsx
    │   │   ├── LifeExpectancy.jsx
    │   │   ├── GenderGap.jsx
    │   │   ├── RegionalComparison.jsx
    │   │   ├── MLAnalysis.jsx
    │   │   ├── DiseaseBurden.jsx
    │   │   ├── AIPlanning.jsx
    │   │   ├── Recommendations.jsx
    │   │   └── AboutProject.jsx
    │   ├── services/
    │   │   └── api.js
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.js
```

---

## 10. License & Disclaimers

Developed for academic demonstration and health intelligence research.  
*Data Source: Global Burden of Disease (GBD 2023), Institute for Health Metrics and Evaluation (IHME).*  
*All findings are for educational and policy surveillance purposes only.*
