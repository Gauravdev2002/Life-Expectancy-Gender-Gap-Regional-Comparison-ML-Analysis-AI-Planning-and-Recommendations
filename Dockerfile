# =============================================================================
# Production Multi-Stage Dockerfile
# Stage 1: Build the React 18 / Vite Frontend
# Stage 2: Python FastAPI Backend + Datasets + Static Assets
# =============================================================================

# --- Stage 1: Frontend Build ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend dependencies and install
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build production bundle
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Final Production Container ---
FROM python:3.12-slim AS runner
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code and datasets
COPY backend/ ./backend/
COPY datasets/ ./datasets/

# Copy built frontend assets from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    DATASETS_DIR=/app/datasets \
    FRONTEND_DIST=/app/frontend/dist \
    HOST=0.0.0.0 \
    PORT=8000

# Expose production port
EXPOSE 8000

# Working directory inside backend
WORKDIR /app/backend

# Run FastAPI via Uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
