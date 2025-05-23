import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# ------------------ Connect to Database ------------------ #
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        st.warning("❗ DATABASE_URL not set. Skipping database features.")
        return None
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# ------------------ Initialize Tables ------------------ #
def initialize_tables():
    engine = get_db_connection()
    if not engine:
        return False
    try:
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
                CREATE INDEX IF NOT EXISTS idx_zip_date 
                ON air_quality_readings (zip_code, date_observed);
            """))
        return True
    except Exception as e:
        st.error(f"❌ Error initializing tables: {e}")
        return False

# ------------------ Store Readings ------------------ #
def store_api_data(air_quality_data, zip_name_map):
    engine = get_db_connection()
    if not engine:
        return

    rows = []

    for zip_code, pollutant_data in air_quality_data.items():
        location_name = zip_name_map.get(zip_code, f"Location {zip_code}")
        for pollutant, reading in pollutant_data.items():
            if isinstance(reading, dict) and "AQI" in reading:
                date_str = reading.get("DateObserved", "")
                try:
                    date_observed = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
                except:
                    date_observed = datetime.now().date()

                category = reading.get("Category", {}).get("Name", "Unknown")
                rows.append({
                    "zip_code": zip_code,
                    "location_name": location_name,
                    "pollutant": pollutant,
                    "date_observed": date_observed,
                    "aqi": reading.get("AQI"),
                    "category": category
                })

    if rows:
        try:
            df = pd.DataFrame(rows)
            df.to_sql("air_quality_readings", engine, if_exists="append", index=False)
        except Exception as e:
            st.warning(f"⚠️ Error inserting data into database: {e}")

# ------------------ Load Historical Data ------------------ #
def get_historical_data_from_db(zip_codes, days=7):
    engine = get_db_connection()
    if not engine:
        return {}

    result = {z: {"PM2.5": [], "O3": []} for z in zip_codes}

    try:
        end = datetime.now().date()
        start = end - timedelta(days=days)
        zips = ", ".join(f"'{z}'" for z in zip_codes)

        query = f"""
            SELECT * FROM air_quality_readings
            WHERE zip_code IN ({zips})
              AND date_observed BETWEEN '{start}' AND '{end}'
            ORDER BY date_observed, zip_code, pollutant;
        """

        df = pd.read_sql(query, engine)

        for _, row in df.iterrows():
            zip_code = row["zip_code"]
            pollutant = row["pollutant"]
            if zip_code in result and pollutant in result[zip_code]:
                result[zip_code][pollutant].append({
                    "AQI": row["aqi"],
                    "DateObserved": str(row["date_observed"]),
                    "Category": row["category"],
                    "ParameterName": pollutant,
                    "ReportingArea": row["location_name"]
                })

    except Exception as e:
        st.warning(f"⚠️ Error loading historical data: {e}")

    return result

# ------------------ Run on Import ------------------ #
initialize_tables()
