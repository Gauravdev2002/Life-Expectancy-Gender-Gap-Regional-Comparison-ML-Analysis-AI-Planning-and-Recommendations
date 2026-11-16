# Step-by-Step Project Execution Guide

**Project Title:** AI-Based Regional Health Inequality and Life Expectancy Intelligence System  
**OS:** Windows 10 / 11  
**Shell:** PowerShell  

This guide provides copy-pasteable instructions to run both the FastAPI Backend and the React.js Frontend on your local machine.

---

## Prerequisites Check

Before starting, ensure you have the following installed on your computer:
1. **Python** (version 3.10, 3.11, 3.12, 3.13, or 3.14)
2. **Node.js** (version 18 or above) with `npm`

You can verify them by opening PowerShell and typing:
```powershell
python --version
node --version
npm --version
```

---

## Step 1: Start the Backend API (FastAPI)

1. Open a new **PowerShell** window.
2. Navigate to the project backend directory:
   ```powershell
   cd "c:\Users\gy696\OneDrive\Desktop\AI project\backend"
   ```
3. Activate the existing Python virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   *(Note: You will see `(venv)` appear at the beginning of your PowerShell prompt).*

   > **If you see an execution policy error (`script cannot be loaded because running scripts is disabled`):**  
   > Run this command once in PowerShell:  
   > `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`  
   > Then try running `.\venv\Scripts\Activate.ps1` again.

4. Start the FastAPI server using Uvicorn:
   ```powershell
   uvicorn main:app --reload --port 8000
   ```
5. You should see output similar to:
   ```text
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process
   INFO:     Application startup complete.
   ```
6. **Keep this terminal window open!** The backend is now running live on port 8000.
   - Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc Documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Step 2: Start the Frontend Dashboard (React + Vite)

1. Open a **second, separate PowerShell window** (do not close the backend terminal).
2. Navigate to the project frontend directory:
   ```powershell
   cd "c:\Users\gy696\OneDrive\Desktop\AI project\frontend"
   ```
3. Start the Vite development server:
   ```powershell
   npm run dev
   ```
4. You should see output similar to:
   ```text
     VITE v6.4.6  ready in 250 ms

     ➜  Local:   http://localhost:5173/
     ➜  Network: use --host to expose
     ➜  press h + enter to show help
   ```
5. **Keep this terminal open!** The frontend is now running live on port 5173.

---

## Step 3: Open the Application in Your Browser

Open your web browser (Chrome, Edge, Brave, or Firefox) and visit:
👉 **[http://localhost:5173](http://localhost:5173)**

When the page loads, you will see:
- A green **"Backend is online and responding correctly"** indicator banner.
- All 9 dashboard pages accessible from the left sidebar:
  1. **Overview** (`/overview`): System summary, live KPI cards, and quick navigation.
  2. **Life Expectancy** (`/life-expectancy`): Location selector (860 locations), historical trend lines, and data tables.
  3. **Gender Gap Analysis** (`/gender-gap`): Female vs Male parity scatter plot, SDI gradient, and extreme gaps.
  4. **Regional Comparison** (`/regional`): SDI quintiles, GBD super-regions, and gainers vs decliners.
  5. **ML Analysis** (`/ml-analysis`): Dynamic K-Means $k$-slider, Silhouette score evaluation, 2D PCA plot, and cluster profiles.
  6. **Disease Burden** (`/disease-burden`): Global DALYs (S10) and YLDs (S11), NCD dominance, and disabling conditions.
  7. **AI Planning** (`/ai-planning`): 5 compound goals, visual HTN task pipeline, STRIPS inspector, and real-time execution trace.
  8. **Recommendations** (`/recommendations`): Heuristic surveillance flags, printable HTML/PDF report, and Markdown export.
  9. **About Project** (`/about`): System architecture, dataset specifications, and college viva defense guide.

---

## Step 4: How to Run the Automated Master Test Suite

Whenever you want to verify that all 50 analytical, machine learning, AI planning, and API checks pass with 100% success rate:

1. Open PowerShell and navigate to the backend:
   ```powershell
   cd "c:\Users\gy696\OneDrive\Desktop\AI project\backend"
   .\venv\Scripts\Activate.ps1
   $env:PYTHONPATH="."
   python test_master_suite.py
   ```
2. You will see:
   ```text
   ===========================================================================
     MASTER TEST SUITE SUMMARY: 50 PASSED, 0 FAILED
   ===========================================================================
   ALL SYSTEM MODULES TESTED & VALIDATED WITH 100% SUCCESS RATE!
   ```

---

## Step 5: How to Stop the Application

When you are done with your demonstration:
1. In the frontend terminal, press `CTRL + C` and type `y` to terminate the dev server.
2. In the backend terminal, press `CTRL + C` to shut down Uvicorn.
3. Close the PowerShell windows.
