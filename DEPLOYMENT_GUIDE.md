# Complete Deployment Guide
## AI-Based Regional Health Inequality and Life Expectancy Intelligence System

This guide outlines **5 tested deployment strategies** for college presentations, public portfolios, and production hosting.

---

## Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │             Web Browser                │
                      │   (http://your-app.onrender.com)       │
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │         FastAPI Engine (Port 8000)     │
                      │                                        │
                      │  ┌──────────────────────────────────┐  │
                      │  │ Static React SPA (frontend/dist) │  │
                      │  └──────────────────────────────────┘  │
                      │  ┌──────────────────────────────────┐  │
                      │  │ REST APIs (/api/...)             │  │
                      │  └──────────────────────────────────┘  │
                      │  ┌──────────────────────────────────┐  │
                      │  │ ML & Planning Engine             │  │
                      │  └──────────────────────────────────┘  │
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │        Cleaned Excel Datasets          │
                      │         (datasets/S9, S10, S11)        │
                      └────────────────────────────────────────┘
```

---

## Method 1: Render.com (Recommended — 100% Free, Unified Single Service)

This is the easiest and most reliable method for college projects:
* **Single service**: Both React frontend and FastAPI backend run together on port 8000.
* **Zero CORS issues**: Frontend and API share the exact same domain.
* **Free tier**: Uses Render's free Web Service tier.

### Step 1: Push Project to GitHub
1. Create a repository on [GitHub](https://github.com): e.g., `health-inequality-intelligence-system`.
2. Open terminal in the project root:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of full-stack health intelligence system"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
   git push -u origin main
   ```

### Step 2: Deploy on Render
1. Go to [Render.com](https://render.com/) and sign up / log in with GitHub.
2. Click **New +** -> **Web Service**.
3. Select your GitHub repository.
4. Render will detect the `Dockerfile` automatically:
   * **Name**: `health-inequality-system`
   * **Language / Environment**: `Docker`
   * **Region**: Choose the closest region (e.g. Singapore, Frankfurt, Oregon)
   * **Instance Type**: `Free`
5. Click **Create Web Service**.
6. Render builds the React frontend in Stage 1, configures Python & dependencies in Stage 2, and deploys the app in ~3–5 minutes.
7. Once deployed, Render gives you a public URL (e.g., `https://health-inequality-system.onrender.com`).

---

## Method 2: Docker Containerization (Run Anywhere with 1 Command)

If you have Docker Desktop installed, you can build and run the entire full-stack system in a single container locally or on any cloud VPS (AWS, GCP, DigitalOcean).

### Build & Run:
```bash
# In the project root:
docker compose up --build
```

### Access:
* Web Application: `http://localhost:8000/`
* Swagger API Docs: `http://localhost:8000/docs`
* Health Check: `http://localhost:8000/api/health/`

### Stop:
```bash
docker compose down
```

---

## Method 3: Split Deployment (Frontend on Vercel + Backend on Render)

If your college evaluator prefers separate frontend and backend URLs:

### Part A: Deploy Backend on Render
1. In Render, select **New +** -> **Web Service**.
2. Connect your repository.
3. Configure:
   * **Root Directory**: `backend`
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
4. In Environment Variables, set:
   * `DATASETS_DIR` = `../datasets`
5. Click **Deploy**. Note your backend URL: e.g., `https://health-api.onrender.com`.

### Part B: Deploy Frontend on Vercel
1. Go to [Vercel.com](https://vercel.com/) and sign in with GitHub.
2. Click **Add New Project** -> Select your repo.
3. In Project Settings:
   * **Framework Preset**: `Vite`
   * **Root Directory**: `frontend`
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
4. In **Environment Variables**, add:
   * **Key**: `VITE_API_BASE_URL`
   * **Value**: `https://health-api.onrender.com/api`
5. Click **Deploy**.
6. Your React frontend is live on Vercel with instant global CDN caching and automatic rewrites via `frontend/vercel.json`.

---

## Method 4: Instant Public URL for Presentations (Zero Hosting Cost)

If you want to present live from your laptop to an external projector, professor's phone, or remote viva via Google Meet / Zoom without setting up cloud accounts:

### Using Localtunnel (Free, no registration needed):
1. Make sure your local servers are running (e.g. double-click `start_system.bat`).
2. In a new PowerShell terminal, run:
   ```bash
   npx localtunnel --port 5173
   ```
3. Localtunnel prints a public URL:
   `your url is: https://health-ai-presentation.loca.lt`
4. Anyone on any device can open this link to view your live interactive dashboard during the presentation!

### Using Ngrok:
```bash
ngrok http 5173
```

---

## Method 5: Production Ubuntu Linux Server (AWS EC2 / DigitalOcean Droplet)

For long-term institutional deployment on a Linux VPS:

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nodejs npm nginx git

# 2. Clone repository
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git /var/www/health-ai
cd /var/www/health-ai

# 3. Build frontend
cd frontend
npm install
npm run build
cd ..

# 4. Set up Python environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Create Systemd Service for FastAPI (/etc/systemd/system/health-ai.service)
sudo bash -c 'cat <<EOF > /etc/systemd/system/health-ai.service
[Unit]
Description=Health Inequality FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/health-ai/backend
ExecStart=/var/www/health-ai/backend/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# 6. Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable health-ai
sudo systemctl start health-ai

# 7. Configure Nginx reverse proxy
# Proxy traffic from port 80 to http://127.0.0.1:8000
```

---

## Pre-Deployment Verification Checklist

Before publishing your deployment, verify that all systems are operational:

- [x] All 3 Excel datasets (`datasets/S9`, `datasets/S10`, `datasets/S11`) are committed and present.
- [x] Master test suite passed **50/50 tests (100%)** via `test_master_suite.py`.
- [x] Production build `npm run build` succeeds without syntax or bundle errors.
- [x] Static asset mounting configured in FastAPI `main.py`.
- [x] CORS allowed origins configured to accept deployed domains.
- [x] Environment variable fallback for `DATASETS_DIR` enabled in `backend/data/loader.py`.
- [x] Client-side routing supported via SPA fallback in `backend/main.py` and `frontend/vercel.json`.
