import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from config import AIRNOW_API_KEY, COLORADO_ZIPS
import db_storage

def fetch_current_air_quality(zip_codes):
    """
    Fetch current air quality data for specified ZIP codes.
    
    Args:
        zip_codes (list): List of ZIP codes to fetch data for
        
    Returns:
        dict: Dictionary with ZIP codes as keys and pollutant data as values
    """
    if not AIRNOW_API_KEY:
        st.error("AirNow API key is missing. Please set the AIRNOW_API_KEY environment variable.")
        return {}
    
    current_data = {}
    
    for zip_code in zip_codes:
        try:
            # Base URL for the AirNow API
            url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
            
            # Query parameters
            params = {
                "format": "application/json",
                "zipCode": zip_code,
                "distance": 25,  # Radius in miles
                "API_KEY": AIRNOW_API_KEY
            }
            
            # Make the API call
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse the response
            data = response.json()
            
            # Process the data for easier access
            pollutant_data = {}
            for item in data:
                pollutant = item.get("ParameterName")
                
                # We're only interested in PM2.5 and Ozone
                if pollutant in ["PM2.5", "O3"]:
                    pollutant_data[pollutant] = item
            
            # Store the data for this ZIP code
            current_data[zip_code] = pollutant_data
            
        except requests.exceptions.RequestException as e:
            st.warning(f"Unable to retrieve air quality data for {COLORADO_ZIPS.get(zip_code, zip_code)}.")
            continue
        except json.JSONDecodeError:
            st.warning(f"Unable to process data for {COLORADO_ZIPS.get(zip_code, zip_code)}.")
            continue
    
    return current_data

def fetch_historical_air_quality(zip_codes, days=7):
    """
    Fetch historical air quality data for specified ZIP codes.
    
    Args:
        zip_codes (list): List of ZIP codes to fetch data for
        days (int): Number of days of historical data to fetch
        
    Returns:
        dict: Dictionary with ZIP codes as keys and historical data as values
    """
    if not AIRNOW_API_KEY:
        st.error("AirNow API key is missing. Please set the AIRNOW_API_KEY environment variable.")
        return {}
    
    historical_data = {}
    
    # Generate date range (today and the past 'days' days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for the API
    start_date_str = start_date.strftime("%Y-%m-%dT00")
    end_date_str = end_date.strftime("%Y-%m-%dT23")
    
    for zip_code in zip_codes:
        try:
            # Base URL for the AirNow API
            url = "https://www.airnowapi.org/aq/observation/zipCode/historical/"
            
            # Query parameters
            params = {
                "format": "application/json",
                "zipCode": zip_code,
                "startDate": start_date_str,
                "endDate": end_date_str,
                "distance": 25,  # Radius in miles
                "API_KEY": AIRNOW_API_KEY
            }
            
            # Make the API call
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Process the data for easier access
            pollutant_data = {"PM2.5": [], "O3": []}
            for item in data:
                pollutant = item.get("ParameterName")
                
                # We're only interested in PM2.5 and Ozone
                if pollutant in ["PM2.5", "O3"]:
                    pollutant_data[pollutant].append(item)
            
            # Store the data for this ZIP code
            historical_data[zip_code] = pollutant_data
            
        except requests.exceptions.RequestException as e:
            st.warning(f"Unable to retrieve historical air quality data for {COLORADO_ZIPS.get(zip_code, zip_code)}.")
            continue
        except json.JSONDecodeError:
            st.warning(f"Unable to process historical data for {COLORADO_ZIPS.get(zip_code, zip_code)}.")
            continue
    
    return historical_data

def get_air_quality_data(zip_codes):
    current_data = fetch_current_air_quality(zip_codes)
    api_historical_data = fetch_historical_air_quality(zip_codes)

    return current_data, api_historical_data

@st.cache_data(ttl=3600)
def get_cached_data_only(zip_codes):
    return get_air_quality_data(zip_codes)

def get_cached_air_quality_data(zip_codes):
    current_data, api_historical_data = get_cached_data_only(zip_codes)

    # Store current data in DB
    if current_data:
        db_storage.store_air_quality_data(current_data, COLORADO_ZIPS)

    if api_historical_data:
        db_storage.store_air_quality_data(api_historical_data, COLORADO_ZIPS)
        historical_data = api_historical_data
    else:
        historical_data = db_storage.get_historical_data_from_db(zip_codes)
        

    return current_data, historical_data
