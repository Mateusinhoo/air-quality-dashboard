import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# Load DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_engine():
    if not DATABASE_URL:
        st.warning("⚠️ DATABASE_URL is not set.")
        return None
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

def initialize_readings_table():
    engine = get_db_engine()
    if not engine:
        return
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
    except Exception as e:
        st.error(f"❌ Table initialization error: {e}")

def store_air_quality_data(data, zip_map):
    engine = get_db_engine()
    if not engine:
        return

    rows = []
    for zip_code, readings in data.items():
        location = zip_map.get(zip_code, f"Location {zip_code}")
        for pollutant, details in readings.items():
            if isinstance(details, dict) and "AQI" in details:
                try:
                    observed_date = datetime.strptime(details.get("DateObserved", ""), "%Y-%m-%d").date()
                except:
                    observed_date = datetime.now().date()

                category = details.get("Category", {}).get("Name", "Unknown")
                rows.append({
                    "zip_code": zip_code,
                    "location_name": location,
                    "pollutant": pollutant,
                    "date_observed": observed_date,
                    "aqi": details.get("AQI"),
                    "category": category
                })

    if rows:
        try:
            df = pd.DataFrame(rows)
            df.to_sql("air_quality_readings", engine, if_exists="append", index=False)
        except Exception as e:
            st.warning(f"⚠️ Data insert failed: {e}")

def get_historical_data_from_db(zip_codes, days=7):
    engine = get_db_engine()
    if not engine:
        return {}

    output = {z: {"PM2.5": [], "O3": []} for z in zip_codes}
    try:
        end = datetime.now().date()
        start = end - timedelta(days=days)
        zip_list = ", ".join([f"'{z}'" for z in zip_codes])

        query = f"""
            SELECT * FROM air_quality_readings
            WHERE zip_code IN ({zip_list})
              AND date_observed BETWEEN '{start}' AND '{end}'
            ORDER BY date_observed, zip_code, pollutant;
        """

        df = pd.read_sql(query, engine)
        for _, row in df.iterrows():
            zip_code = row["zip_code"]
            pollutant = row["pollutant"]
            if zip_code in output and pollutant in output[zip_code]:
                output[zip_code][pollutant].append({
                    "AQI": row["aqi"],
                    "DateObserved": str(row["date_observed"]),
                    "Category": row["category"],
                    "ParameterName": pollutant,
                    "ReportingArea": row["location_name"]
                })

    except Exception as e:
        st.warning(f"⚠️ Failed to retrieve historical data: {e}")

    return output

# Auto-init on import
initialize_readings_table()
