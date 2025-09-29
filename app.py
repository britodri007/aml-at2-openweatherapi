# app.py
import os
from datetime import date
from typing import Dict, Any

import requests
import streamlit as st

DEFAULT_API_BASE = os.getenv("API_BASE", "https://<your-fastapi-on-render>.onrender.com")
TIMEOUT = 15  # seconds


def call_api(base: str, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    url = f"{base.rstrip('/')}{path}"
    try:
        r = requests.get(url, params=params or {}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP {r.status_code}: {e}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


st.set_page_config(page_title="Open Meteo – Sydney", page_icon="🌦️", layout="centered")
st.title("Open Meteo – Sydney ")

with st.sidebar:
    st.header("Settings")
    api_base = st.text_input("FastAPI Base URL", value=DEFAULT_API_BASE)
    if st.button("Health check"):
        res = call_api(api_base, "/health/")
        if "error" in res:
            st.error(res["error"])
        else:
            st.success(res)

st.write("Pick a date (YYYY-MM-DD). The app calls your FastAPI and shows results.")

d = st.date_input("Date", value=date(2024, 1, 1), format="YYYY-MM-DD")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Rain in +7 days?"):
        res = call_api(api_base, "/predict/rain/", {"date": d.isoformat()})
        st.subheader("Rain (+7d)")
        st.json(res)

with col2:
    if st.button("3-day precipitation"):
        res = call_api(api_base, "/predict/precipitation/fall/", {"date": d.isoformat()})
        st.subheader("3-day precipitation")
        st.json(res)

with col3:
    if st.button("Run both"):
        rain = call_api(api_base, "/predict/rain/", {"date": d.isoformat()})
        precip = call_api(api_base, "/predict/precipitation/fall/", {"date": d.isoformat()})
        st.subheader("Rain (+7d)")
        st.json(rain)
        st.subheader("3-day precipitation")
        st.json(precip)

st.caption("Tip: set API_BASE env var when deploying the Streamlit app.")