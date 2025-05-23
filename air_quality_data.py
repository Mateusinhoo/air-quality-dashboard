import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from config import AIRNOW_API_KEY, COLORADO_ZIPS
from database import store_api_data, get_historical_data_from_db

# ------------------ Fetch Current Air Quality ------------------ #
def fetch_current_air_quality(zip_codes):
    if not AIRNOW_API_KEY:
        st.error("AirNow API key is missing.")
        return {}

    current_data = {}

    for zip_code in zip_codes:
        try:
            url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
            params = {
                "format": "application/json",
                "zipCode": zip_code,
                "distance": 25,
                "API_KEY": AIRNOW_API_KEY
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            current_data[zip_code] = {
                item["ParameterName"]: item
                for item in data
                if item["ParameterName"] in ["PM2.5", "O3"]
            }

        except Exception as e:
            st.warning(f"{zip_code} — API error: {e}")
            continue

    return current_data

# ------------------ Fetch Historical AQI ------------------ #
def fetch_historical_air_quality(zip_codes, days=7):
    if not AIRNOW_API_KEY:
        st.error("AirNow API key is missing.")
        return {}

    historical_data = {}
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_str = start_date.strftime("%Y-%m-%dT00")
    end_str = end_date.strftime("%Y-%m-%dT23")

    for zip_code in zip_codes:
        try:
            url = "https://www.airnowapi.org/aq/observation/zipCode/historical/"
            params = {
                "format": "application/json",
                "zipCode": zip_code,
                "startDate": start_str,
                "endDate": end_str,
                "distance": 25,
                "API_KEY": AIRNOW_API_KEY
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Group by pollutant
            historical_data[zip_code] = {"PM2.5": [], "O3": []}
            for item in data:
                param = item.get("ParameterName")
                if param in ["PM2.5", "O3"]:
                    historical_data[zip_code][param].append(item)

        except Exception as e:
            st.warning(f"{zip_code} — historical API error: {e}")
            continue

    return historical_data

# ------------------ Cached API + DB Storage ------------------ #
@st.cache_data(ttl=3600)
def get_cached_air_quality_data(zip_codes):
    current_data = fetch_current_air_quality(zip_codes)
    historical_api = fetch_historical_air_quality(zip_codes)

    if current_data:
        store_api_data(current_data, COLORADO_ZIPS)

    if historical_api:
        store_api_data(historical_api, COLORADO_ZIPS)
        historical_data = historical_api
    else:
        historical_data = get_historical_data_from_db(zip_codes)

    return current_data, historical_data
