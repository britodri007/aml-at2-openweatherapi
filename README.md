# Weather Forecasting API (AT2)

This project enhances weather forecasting by embedding machine learning into Open-Meteo’s services. Two models are deployed as APIs:

Rain Prediction (Logistic Regression): forecasts rain (yes/no) exactly seven days ahead.

Precipitation Forecast (Ridge Regression): estimates rainfall volume (mm) over the next three days.

Both models are deployed with FastAPI and hosted on Render, making them accessible in real time.

# Setup
# Clone the Repository
git clone https://github.com/britodri007/aml-at2-experiment.git
cd aml-at2-experiment

## Create Virtual Environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

## Install Dependencies
pip install -r requirements.txt

# Deployment
Run Locally
uvicorn app.main:app --reload


Open Swagger UI at http://localhost:8000/docs

Health check available at http://localhost:8000/health

Hosted Deployment

- Models are deployed on Render and accessible through structured HTTP endpoints:

- Rain prediction endpoint: /predict/rain

- Precipitation endpoint: /predict/precipitation/fall

- Docs: /docs

- Health check: /health

# Usage
1. Rain Prediction (Classification)

Endpoint: POST /predict/rain
Example request:

{
  "temperature_2m_mean": 19.2,
  "dew_point_2m_max": 14.8,
  "relative_humidity_2m_mean": 72.0,
  "surface_pressure_mean": 1012.4,
  "shortwave_radiation_sum": 18.5,
  "sunshine_duration": 9.0,
  "daylight_duration": 12.1,
  "wind_gusts_10m_max": 45.0,
  "cloud_cover_max": 85.0,
  "weather_code": 3,
  "dewpoint_spread": 4.4,
  "sunshine_ratio": 0.74
}


Response:

{
  "probability_rain": 0.62,
  "prediction": 1,
  "label": "rain"
}

2. Precipitation Forecast (Regression)

Endpoint: POST /predict/precipitation/fall
Example request:

{
  "cloud_cover_mean": 65.0,
  "relative_humidity_2m_mean": 78.0,
  "precipitation_hours": 3.0,
  "weather_code": 3,
  "surface_pressure_mean": 1009.8,
  "wind_gusts_10m_max": 50.0,
  "cloud_cover_max": 92.0,
  "temperature_2m_mean": 18.6,
  "shortwave_radiation_sum": 14.2,
  "dew_point_2m_max": 15.1,
  "dewpoint_spread": 3.5,
  "sunshine_ratio": 0.62
}


Response:

{
  "precip_3d_sum_mm": 12.4
}

# Troubleshooting

- ModuleNotFoundError: Ensure you activated the virtual environment before running.

- Port already in use: Stop any other uvicorn/FastAPI apps or run on another port with --port 8080.

- Invalid JSON input: Check feature names and types match those in the API docs (/docs).

- Deployment slow on Render: Free tier may take longer to wake up; consider scaling up.