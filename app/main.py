# app/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import date, timedelta
import pandas as pd
import joblib
import os

# -----------------------------
# Basic paths (relative to repo)
# -----------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIN_MODEL_PATH = os.path.join(ROOT_DIR, "models", "rain_or_not", "logreg_model.joblib")
PRECIP_MODEL_PATH = os.path.join(ROOT_DIR, "models", "precipitation_fall", "ridge_model.joblib")
PARQUET_PATH = os.path.join(ROOT_DIR, "data", "features_daily.parquet")
CSV_PATH = os.path.join(ROOT_DIR, "data", "features_daily.csv")

# -----------------------------
# Load models (once at startup)
# -----------------------------
try:
    rain_model = joblib.load(RAIN_MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Could not load classification model: {e}")

try:
    precip_model = joblib.load(PRECIP_MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Could not load regression model: {e}")

# -----------------------------
# Load features table (CSV or Parquet)
# Must contain a 'time' column with dates
# -----------------------------
if os.path.exists(PARQUET_PATH):
    features_df = pd.read_parquet(PARQUET_PATH)
elif os.path.exists(CSV_PATH):
    features_df = pd.read_csv(CSV_PATH)
else:
    raise RuntimeError(
        "No features file found. Put 'features_daily.parquet' or 'features_daily.csv' in the data/ folder."
    )

if "time" not in features_df.columns:
    raise RuntimeError("Features table must include a 'time' column.")

features_df = features_df.copy()
features_df["time"] = pd.to_datetime(features_df["time"]).dt.date
features_df = features_df.set_index("time")  # so we can look up rows by date easily

# -----------------------------
# Simple response models
# -----------------------------
class RainResponse(BaseModel):
    input_date: date
    prediction: dict

class PrecipResponse(BaseModel):
    input_date: date
    prediction: dict

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(
    title="Open Meteo AT2 API",
    description="Simple API for: rain in +7 days (classification) and 3-day precipitation sum (regression).",
    version="1.0.0",
)

@app.get("/")
def home():
    return {
        "message": "Open Meteo AT2 API",
        "endpoints": {
            "/health/": "GET health check",
            "/predict/rain/?date=YYYY-MM-DD": "Rain in exactly +7 days (binary)",
            "/predict/precipitation/fall/?date=YYYY-MM-DD": "3-day precipitation sum (mm)",
        },
    }

@app.get("/health/")
def health():
    return {"status": "ok"}

def get_features_row(d: date) -> pd.DataFrame:
    """Return a single-row DataFrame for the requested date, or 404."""
    if d not in features_df.index:
        raise HTTPException(status_code=404, detail=f"No features found for {d}.")
    # keep it as a DataFrame (shape [1, n_features])
    return features_df.loc[d:d]

@app.get("/predict/rain/", response_model=RainResponse)
def predict_rain(date: date = Query(..., description="YYYY-MM-DD")):
    X = get_features_row(date)

    # If your saved object is a Pipeline with a classifier, this works directly
    if hasattr(rain_model, "predict_proba"):
        prob = float(rain_model.predict_proba(X)[0, 1])
    else:
        # very simple fallback if no predict_proba (not ideal, but beginner-friendly)
        y_hat = int(rain_model.predict(X)[0])
        prob = 1.0 if y_hat == 1 else 0.0

    will_rain = bool(prob >= 0.5)

    return {
        "input_date": date,
        "prediction": {
            "date": date + timedelta(days=7),
            "will_rain": will_rain,
            "prob": round(prob, 4),
        },
    }

@app.get("/predict/precipitation/fall/", response_model=PrecipResponse)
def predict_precip(date: date = Query(..., description="YYYY-MM-DD")):
    X = get_features_row(date)

    y_hat = float(precip_model.predict(X)[0])

    # NOTE: if you trained on log1p(target), you must invert it here:
    # import numpy as np
    # y_hat = float(np.expm1(y_hat))

    return {
        "input_date": date,
        "prediction": {
            "start_date": date + timedelta(days=1),
            "end_date": date + timedelta(days=3),
            "precipitation_fall": round(y_hat, 2),
        },
    }
