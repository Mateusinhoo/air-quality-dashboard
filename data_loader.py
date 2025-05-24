# data_loader.py
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("AIRNOW_API_KEY")

def get_air_quality_data(zip_code, pollutant):
    url = "http://www.airnowapi.org/aq/observation/zipCode/current/"
    params = {
        "format": "application/json",
        "zipCode": zip_code,
        "distance": 25,
        "API_KEY": API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Filter for selected pollutant
        filtered = [entry for entry in data if entry["ParameterName"] == pollutant]
        if not filtered:
            return pd.DataFrame(columns=["Date", "Value"])

        entry = filtered[0]
        return pd.DataFrame({
            "Date": [entry["DateObserved"]],
            "Value": [entry["AQI"]]
        })

    except Exception as e:
        print("Error fetching air quality data:", e)
        return pd.DataFrame(columns=["Date", "Value"])

def get_asthma_data(zip_code):
    return pd.DataFrame({"Zip": [zip_code], "Asthma Rate": [12.3]})
