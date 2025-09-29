# Dockerfile
FROM python:3.11-slim

# avoid .pyc & enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# install system deps (optional but good for pandas/scikit)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# install python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest (models, app, etc.)
COPY . .

# default start command for Render or local docker run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

