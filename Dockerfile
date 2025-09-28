FROM python:3.11-slim

# Make Python output unbuffered (helpful for logs on Render)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code + models
COPY . .

# Render injects $PORT at runtime; use it if present, else default to 10000
# (Render’s free tier expects you to bind to 0.0.0.0 and $PORT)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
