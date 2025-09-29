# app/main.py
from fastapi import FastAPI, Query
import joblib, os, json
from datetime import datetime, timedelta

app = FastAPI(title="Weather Prediction API", version="1.0")

# Paths
RAIN_MODEL_PATH = os.path.join("models", "rain_or_not", "logreg_model.joblib")
RAIN_FEATURES_PATH = os.path.join("models", "rain_or_not", "feature_cols.json")
PRECIP_MODEL_PATH = os.path.join("models", "precipitation_fall", "ridge_model.joblib")
PRECIP_FEATURES_PATH = os.path.join("models", "precipitation_fall", "feature_cols.json")

# Load models + feature definitions
try:
    rain_model = joblib.load(RAIN_MODEL_PATH)
    with open(RAIN_FEATURES_PATH, "r") as f:
        rain_features = json.load(f)
except Exception as e:
    raise RuntimeError(f"Could not load classification model: {e}")

try:
    precip_model = joblib.load(PRECIP_MODEL_PATH)
    with open(PRECIP_FEATURES_PATH, "r") as f:
        precip_features = json.load(f)
except Exception as e:
    raise RuntimeError(f"Could not load regression model: {e}")


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
            "/predict/rain/": "GET – ?date=YYYY-MM-DD",
            "/predict/precipitation/fall/": "GET – ?date=YYYY-MM-DD"
        },
        "input": {"date": "YYYY-MM-DD"},
        "output_examples": {
            "/predict/rain/": {
                "input_date": "2023-01-01",
                "prediction": {"date": "2023-01-08", "will_rain": True}
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
        "github_repo": "https://github.com/britodri007/aml-at2-openweatherapi.git"
    }


@app.get("/health/")
def health():
    return {"status": "API is running!"}


@app.get("/predict/rain/")
def predict_rain(date: str = Query(..., description="YYYY-MM-DD")):
    try:
        input_date = datetime.strptime(date, "%Y-%m-%d")
        target_date = input_date + timedelta(days=7)

        # Dummy input with correct number of features (12)
        X_dummy = [[0] * len(rain_features)]
        prediction = rain_model.predict(X_dummy)[0]

        return {
            "input_date": date,
            "prediction": {
                "date": target_date.strftime("%Y-%m-%d"),
                "will_rain": bool(prediction),
            }
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/predict/precipitation/fall/")
def predict_precipitation(date: str = Query(..., description="YYYY-MM-DD")):
    try:
        input_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = input_date + timedelta(days=1)
        end_date = input_date + timedelta(days=3)

        # Dummy input with correct number of features (20)
        X_dummy = [[0] * len(precip_features)]
        prediction = float(precip_model.predict(X_dummy)[0])

        return {
            "input_date": date,
            "prediction": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "precipitation_fall": round(prediction, 2),
            }
        }
    except Exception as e:
        return {"error": str(e)}