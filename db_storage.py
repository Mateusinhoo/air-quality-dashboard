import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date, DateTime, text
from datetime import datetime, timedelta

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Function to initialize and get database connection
def get_db_connection():
    if not DATABASE_URL:
        st.warning("Database connection not configured. Historical data storage is disabled.")
        return None
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # simple test query
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Function to create tables if they don't exist
def initialize_tables():
    """Create database tables if they don't exist"""
    engine = get_db_connection()
    if not engine:
        return False
    
    try:
        # Create readings table if it doesn't exist
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS air_quality_readings (
                    id SERIAL PRIMARY KEY,
                    zip_code VARCHAR(10) NOT NULL,
                    location_name VARCHAR(100) NOT NULL,
                    pollutant VARCHAR(10) NOT NULL,
                    date_observed DATE NOT NULL,
                    aqi INTEGER,
                    category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_readings_zip_date 
                ON air_quality_readings (zip_code, date_observed);
            """))
        return True
    except Exception as e:
        st.warning(f"Error initializing database tables: {e}")
        return False

# Function to store air quality readings
def store_air_quality_data(air_quality_data, location_names):
    """
    Store air quality data in the database
    
    Args:
        air_quality_data (dict): Dictionary with ZIP codes as keys and readings as values
        location_names (dict): Dictionary mapping ZIP codes to location names
    """
    engine = get_db_connection()
    if not engine:
        return
    
    try:
        # Process the data and insert into database
        rows_to_insert = []
        
        for zip_code, pollutant_data in air_quality_data.items():
            location_name = location_names.get(zip_code, f"Location {zip_code}")
            
            for pollutant_name, reading in pollutant_data.items():
                if isinstance(reading, dict) and 'AQI' in reading:
                    # Parse date
                    date_str = reading.get('DateObserved', '').strip()
                    try:
                        date_observed = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except:
                        # If date parsing fails, use current date
                        date_observed = datetime.now().date()
                    
                    # Create a row for insertion
                    rows_to_insert.append({
                        'zip_code': zip_code,
                        'location_name': location_name,
                        'pollutant': pollutant_name,
                        'date_observed': date_observed,
                        'aqi': reading.get('AQI'),
                        'category': reading.get('Category', {}).get('Name', 'Unknown')
                    })
        
        # Insert the data into the database
        if rows_to_insert:
            df = pd.DataFrame(rows_to_insert)
            df.to_sql('air_quality_readings', engine, if_exists='append', index=False)
    
    except Exception as e:
        st.warning(f"Error storing data in database: {e}")

# Function to retrieve historical air quality data from the database
def get_historical_data_from_db(zip_codes, days=7):
    """
    Retrieve historical air quality data from the database
    
    Args:
        zip_codes (list): List of ZIP codes to retrieve data for
        days (int): Number of days of historical data to retrieve
        
    Returns:
        dict: Dictionary with ZIP codes as keys and readings as values
    """
    engine = get_db_connection()
    if not engine:
        return {}
    
    result = {}
    for zip_code in zip_codes:
        result[zip_code] = {"PM2.5": [], "O3": []}
    
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Query the database for historical data
        query = f"""
            SELECT * FROM air_quality_readings
            WHERE zip_code IN ({', '.join([f"'{z}'" for z in zip_codes])})
            AND date_observed BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY date_observed, zip_code, pollutant
        """
        
        df = pd.read_sql(query, engine)
        
        if not df.empty:
            # Process the data into the expected format
            for _, row in df.iterrows():
                zip_code = row['zip_code']
                pollutant = row['pollutant']
                
                if zip_code in result and pollutant in ["PM2.5", "O3"]:
                    # Convert date_observed to string format if it's a datetime object
                    date_str = None
                    if isinstance(row['date_observed'], datetime):
                        date_str = row['date_observed'].strftime("%Y-%m-%d")
                    elif hasattr(row['date_observed'], 'strftime'):  # pandas Timestamp
                        date_str = row['date_observed'].strftime("%Y-%m-%d")
                    else:
                        date_str = str(row['date_observed'])
                    
                    result[zip_code][pollutant].append({
                        "AQI": row['aqi'],
                        "DateObserved": date_str,
                        "Category": row['category'],
                        "ParameterName": pollutant,
                        "ReportingArea": row['location_name']
                    })
        
        return result
    
    except Exception as e:
        st.warning(f"Error retrieving historical data from database: {e}")
        return {}

# Initialize tables when module is imported
initialize_tables()

def store_api_data(air_quality_data, location_name_map):
    """
    Wrapper to store air quality API data using store_air_quality_data.
    Includes debug print messages for Render logs.
    """
    from datetime import datetime
    print("🔄 Starting API data storage...")

    if air_quality_data:
        try:
            store_air_quality_data(air_quality_data, location_name_map)
            print("✅ Finished storing API data.")
        except Exception as e:
            print(f"❌ Failed to store API data: {e}")
    else:
        print("⚠️ No air quality data to store.")