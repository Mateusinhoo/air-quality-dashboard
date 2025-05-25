# data_loader.py
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import random

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

def get_map_data():
    zip_codes = [
        ("80202", "Denver", 39.7508, -104.9965),
        ("80301", "Boulder", 40.0395, -105.2309),
        ("80521", "Fort Collins", 40.5853, -105.0844),
        ("80903", "Colorado Springs", 38.8339, -104.8214),
        ("80014", "Aurora", 39.6662, -104.8351),
        ("80401", "Golden", 39.7555, -105.2211),
        ("81611", "Aspen", 39.1911, -106.8175),
        ("81657", "Vail", 39.6403, -106.3742),
        ("80538", "Loveland", 40.4170, -105.0740),
        ("81003", "Pueblo", 38.2544, -104.6091),
        ("81620", "Avon", 39.6319, -106.5222),
        ("80501", "Longmont", 40.1672, -105.1019),
        ("81435", "Telluride", 37.9375, -107.8123),
        ("81230", "Gunnison", 38.5458, -106.9253),
        ("81212", "Canon City", 38.4494, -105.2253),
        ("81416", "Delta", 38.7401, -108.0720),
        ("81101", "Alamosa", 37.4694, -105.8700),
        ("81052", "Lamar", 38.0871, -102.6204),
        ("81301", "Durango", 37.2753, -107.8801),
        ("80550", "Windsor", 40.4770, -104.9014),
        ("81625", "Craig", 40.5153, -107.5469),
        ("81201", "Salida", 38.5347, -105.9989),
        ("80461", "Leadville", 39.2508, -106.2925),
        ("81401", "Montrose", 38.4783, -107.8762),
        ("81082", "Trinidad", 37.1695, -104.5008),
        ("80701", "Fort Morgan", 40.2508, -103.8000),
        ("80504", "Firestone", 40.1636, -104.9367),
        ("81007", "Pueblo West", 38.3508, -104.7222),
        ("80817", "Fountain", 38.6822, -104.7003),
        ("80831", "Peyton", 38.9608, -104.6006)
    ]

    # Only use PM2.5 as the pollutant as per user request
    pollutant = "PM2.5"

    mock_data = []
    for zip_code, city, lat, lon in zip_codes:
        aqi = random.randint(5, 150)
        mock_data.append({
            "zip": zip_code,
            "city": city,
            "lat": lat,
            "lon": lon,
            "AQI": aqi,
            "Pollutant": pollutant
        })

    return mock_data
