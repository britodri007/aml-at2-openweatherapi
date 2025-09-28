# app/main.py
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import os, json, joblib
from datetime import datetime, timedelta
import pandas as pd

app = FastAPI(
    title="Weather Prediction API",
    version="1.0",
    description="Predict rain (+7 days) and 3-day precipitation for Sydney."
)

# ---------- Paths
ROOT = os.path.dirname(__file__)
RAIN_DIR   = os.path.join(ROOT, "..", "models", "rain_or_not")
PRECIP_DIR = os.path.join(ROOT, "..", "models", "precipitation_fall")

RAIN_MODEL_PATH   = os.path.join(RAIN_DIR, "logreg_model.joblib")
RAIN_FEATS_PATH   = os.path.join(RAIN_DIR, "feature_cols.json")
PRECIP_MODEL_PATH = os.path.join(PRECIP_DIR, "ridge_model.joblib")
PRECIP_FEATS_PATH = os.path.join(PRECIP_DIR, "feature_cols.json")

# ---------- Load models + feature schemas
try:
    rain_model = joblib.load(RAIN_MODEL_PATH)         # sklearn Pipeline
    with open(RAIN_FEATS_PATH) as f:
        rain_features = json.load(f)                  # list[str] or list[int]
except Exception as e:
    raise RuntimeError(f"Could not load rain model/feats: {e}")

try:
    precip_model = joblib.load(PRECIP_MODEL_PATH)     # sklearn Pipeline
    with open(PRECIP_FEATS_PATH) as f:
        precip_features = json.load(f)
except Exception as e:
    raise RuntimeError(f"Could not load precipitation model/feats: {e}")

def zero_row(columns):
    """Make a 1xN DataFrame of zeros with exact training schema."""
    return pd.DataFrame([[0]*len(columns)], columns=columns)

# ---------- Endpoints

@app.get("/")
def root():
    return {
        "project": "Open Meteo – ML Forecasts for Sydney",
        "objectives": [
            "Binary classification: will it rain exactly +7 days from a given date?",
            "Regression: 3-day cumulative precipitation (mm) from a given date."
        ],
        "endpoints": {
            "/health/": "GET – service status",
            "/predict/rain/": "GET – ?date=YYYY-MM-DD -> will_rain boolean for date+7",
            "/predict/precipitation/fall/": "GET – ?date=YYYY-MM-DD -> mm sum over next 3 days"
        },
        "input": {
            "date": "YYYY-MM-DD (training uses data <= 2024; 2025+ treated as production)"
        },
        "output_examples": {
            "/predict/rain/": {
                "input_date": "2023-01-01",
                "prediction": {
                    "date": "2023-01-08",
                    "will_rain": True
                }
            },
            "/predict/precipitation/fall/": {
                "input_date": "2023-01-01",
                "prediction": {
                    "start_date": "2023-01-02",
                    "end_date": "2023-01-04",
                    "precipitation_fall": "28.2"
                }
            }
        },
        "github_repo": "<<< add your API repo URL here >>>"
    }

@app.get("/health/")
def health():
    return {"status": "✅ API is running!"}

@app.get("/predict/rain/")
def predict_rain(
    date: str = Query(..., description="Date in format YYYY-MM-DD")
):
    """
    Returns if it will rain in exactly 7 days from the given date.
    NOTE: This demo uses a zero-filled row that matches the training schema.
          Replace `X` with real engineered features when ready.
    """
    try:
        input_date = datetime.strptime(date, "%Y-%m-%d").date()
        target_date = input_date + timedelta(days=7)

        X = zero_row(rain_features)
        y = int(rain_model.predict(X)[0])
        will_rain = bool(y)

        return {
            "input_date": input_date.isoformat(),
            "prediction": {
                "date": target_date.isoformat(),
                "will_rain": will_rain
            }
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.get("/predict/precipitation/fall/")
def predict_precipitation(
    date: str = Query(..., description="Date in format YYYY-MM-DD")
):
    """
    Returns cumulative precipitation (mm) for the next 3 days.
    NOTE: This demo uses a zero-filled row that matches the training schema.
          Replace `X` with real engineered features when ready.
    """
    try:
        input_date = datetime.strptime(date, "%Y-%m-%d").date()
        start_date = input_date + timedelta(days=1)
        end_date   = input_date + timedelta(days=3)

        X = zero_row(precip_features)
        y = float(precip_model.predict(X)[0])

        # Assignment example shows precipitation_fall as a string
        return {
            "input_date": input_date.isoformat(),
            "prediction": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "precipitation_fall": f"{round(y, 2)}"
            }
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
