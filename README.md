# 🌦️ Open Meteo AI Weather Prediction

FastAPI app serving two ML models:  
- **Rain in +7 days** (binary classification)  
- **3-day cumulative precipitation** (regression)

---

## What this is (assignment summary)

- **Unit:** 36120 – AT2 (ML as a Service)  
- **Goal:** Ship two ML models behind an API (runs locally, with Docker, or on Render).  
- **Stack:** FastAPI, Uvicorn, scikit-learn, pandas, numpy.  
- **Docs:** Swagger at `/` (root), ReDoc at `/redoc`.  
- **Models required on disk:**  
  - `models/rain_or_not/logreg_model.joblib`  
  - `models/rain_or_not/feature_cols.json`  
  - `models/precipitation_fall/ridge_model.joblib`  
  - `models/precipitation_fall/feature_cols.json`

---

## Quick Start (Local, Poetry recommended)

### 1. Clone this repo
```bash
git clone https://github.com/britodri007/aml-at2-openweatherapi
cd aml-at2-openweatherapi
```

### 2. Install deps (Poetry, Python 3.11.x)
```bash
poetry lock
poetry install --with dev
```

### 3. Activate the venv
```bash
poetry env activate
# or
& .\.venv\Scripts\Activate.ps1
```

### 4. Make sure model files are in place
```
models/
 ├─ rain_or_not/
 │   ├─ logreg_model.joblib
 │   └─ feature_cols.json
 └─ precipitation_fall/
     ├─ ridge_model.joblib
     └─ feature_cols.json
```

### 5. Run the API
```bash
uvicorn app:app --reload
```

- Swagger UI → [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
- ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🐍 Run with pip instead (optional)

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## 🐳 Docker (local)

### Build the image
```bash
docker build -t open-meteo-api .
```

### Run it
```bash
docker run -p 8000:8000 open-meteo-api
```

Swagger will be live at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## ☁️ Deploy on Render with Docker

1. Push this repo (with `Dockerfile`) to GitHub.  
2. In Render → **New Web Service** → connect the repo.  
3. Choose **Runtime: Docker**.  
4. Make sure your models are committed to the repo (or load them from a Render Disk / bucket at the same paths).  
5. Render will build the image using the `Dockerfile` automatically.  
6. API will run on:
```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```
7. Health check: visit `/` → Swagger should load.  

---

## Quick test after deploy

```bash
# Swagger endpoint
curl -I https://<your-service>.onrender.com/

# Example POST request (rain prediction)
curl -X POST "https://<your-service>.onrender.com/predict/rain"   -H "Content-Type: application/json"   -d @sample_rain.json
```

---

## 🔧 Deployment Files

### Dockerfile
```dockerfile
# ---------- base ----------
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

# system deps you might need (uvicorn performance, build tools, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# ---------- deps (PIP route) ----------
FROM base AS deps-pip
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------- deps (Poetry route) ----------
FROM base AS deps-poetry
ENV POETRY_VERSION=1.8.3
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --only main

# ---------- runtime ----------
FROM base AS runtime
# Choose ONE of these COPY lines based on your dep manager:
# Using pip:
COPY --from=deps-pip /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=deps-pip /usr/local/bin /usr/local/bin
# Using Poetry (comment pip lines above and uncomment below):
# COPY --from=deps-poetry /usr/local/lib/python3.11 /usr/local/lib/python3.11
# COPY --from=deps-poetry /usr/local/bin /usr/local/bin

# Copy app code
COPY . .

# Expose port (Render sets $PORT at runtime; EXPOSE is informational)
EXPOSE 8000

# Start FastAPI (Render sets $PORT — use it)
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
```

### .dockerignore
```dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.dist/
.venv/
.git/
.gitignore
.env
.env.*
*.ipynb_checkpoints
data/
notebooks/
```

---

##  Notes

- Only **four model files** are required for the API to run (see above).  
- Keep your `.dockerignore` tight so the Docker image stays small.  
- On Render, `$PORT` is auto-set — don’t hardcode `8000`.  
- If models are large, consider using a Render Disk instead of committing them.  

---
