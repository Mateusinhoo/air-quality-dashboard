from database import store_api_data
import streamlit as st
import pandas as pd
from datetime import datetime

from config import COLORADO_ZIPS, DEFAULT_ZIPS, AQI_CATEGORIES, POLLUTANTS
from air_quality_data import get_cached_air_quality_data
from visualizations import plot_aqi_comparison, plot_aqi_time_series, create_aqi_indicator
from utils import get_aqi_category, format_datetime, prepare_comparison_data, prepare_time_series_data

st.set_page_config(
    page_title="Colorado Air Quality Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <h1 style='text-align: center; font-size: 2.8rem; color: #4B8BBE;'>
        🪱 Colorado Air Quality Dashboard
    </h1>
    <p style='text-align: center; font-size: 1.1rem; color: #6c757d; margin-bottom: 2rem;'>
        Real-time PM2.5 and Ozone levels in selected ZIP codes — updated daily
    </p>
    <hr style='margin-top: -1rem; margin-bottom: 2rem;' />
""", unsafe_allow_html=True)

# Sidebar controls
st.sidebar.header("Settings")
selected_zips = st.sidebar.multiselect(
    "Select ZIP Codes",
    options=list(COLORADO_ZIPS.keys()),
    default=DEFAULT_ZIPS,
    format_func=lambda x: f"{x} - {COLORADO_ZIPS.get(x, 'Unknown')}"
)
if not selected_zips:
    selected_zips = DEFAULT_ZIPS
    st.sidebar.warning(f"No ZIP codes selected. Using defaults: {', '.join(DEFAULT_ZIPS)}")

if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# AQI info sidebar
st.sidebar.header("AQI Information")
for category, info in AQI_CATEGORIES.items():
    st.sidebar.markdown(
        f"<div style='background-color: {info['color']}; padding: 5px; border-radius: 5px;'>"
        f"<strong>{category}:</strong> {info['range'][0]}-{info['range'][1]}"
        f"</div>", unsafe_allow_html=True
    )

# Pollutant descriptions
st.sidebar.header("Pollutant Information")
for pollutant, info in POLLUTANTS.items():
    with st.sidebar.expander(f"{info['name']} ({pollutant})"):
        st.write(info["description"])

# Load and store data
with st.spinner("Loading air quality data..."):
    try:
        current_data, historical_data = get_cached_air_quality_data(selected_zips)
        store_api_data(current_data, COLORADO_ZIPS)
        comparison_data = prepare_comparison_data(current_data)
        time_series_data = prepare_time_series_data(historical_data)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

if not current_data and not historical_data:
    st.error("No data available. Please check your API key and database settings.")
    st.stop()

# Display key insights and charts (moved to separate UI module in future refactor)

# ------------------ Key Insights Section ------------------ #
if comparison_data is not None and not comparison_data.empty:
    pm25_data = comparison_data[comparison_data['Pollutant'] == 'PM2.5']
    o3_data = comparison_data[comparison_data['Pollutant'] == 'O3']

    highest_pm25 = highest_o3 = None
    highest_pm25_zip = highest_o3_zip = None

    if not pm25_data.empty:
        highest_pm25_row = pm25_data.loc[pm25_data['AQI'].idxmax()]
        highest_pm25 = highest_pm25_row['AQI']
        highest_pm25_zip = highest_pm25_row['ZIP']

    if not o3_data.empty:
        highest_o3_row = o3_data.loc[o3_data['AQI'].idxmax()]
        highest_o3 = highest_o3_row['AQI']
        highest_o3_zip = highest_o3_row['ZIP']

    # Determine worst overall AQI
    if (highest_pm25 or 0) >= (highest_o3 or 0):
        worst_aqi = highest_pm25
        worst_zip = highest_pm25_zip
        worst_pollutant = "PM2.5"
    else:
        worst_aqi = highest_o3
        worst_zip = highest_o3_zip
        worst_pollutant = "Ozone"

    worst_category = get_aqi_category(worst_aqi)
    worst_loc = COLORADO_ZIPS.get(worst_zip, 'Unknown')

    class_map = {
        "Good": "good-aqi", "Moderate": "moderate-aqi",
        "Unhealthy for Sensitive Groups": "sensitive-aqi",
        "Unhealthy": "unhealthy-aqi", "Very Unhealthy": "very-unhealthy-aqi",
        "Hazardous": "hazardous-aqi"
    }

    st.markdown(f"""
        <div class="key-insights">
            <div class="insights-header">📊 Key Insights</div>
            <div class="insights-content">
                Today's worst air quality: 
                <span class="{class_map.get(worst_category, '')}">{worst_zip} - {worst_loc}</span> 
                ({worst_pollutant}: {worst_aqi} – {worst_category})
            </div>
        </div>
    """, unsafe_allow_html=True)

# ------------------ Current Air Quality Overview ------------------ #
st.header("Current Air Quality")
col1, col2 = st.columns(2)

with col1:
    st.subheader("PM2.5 (Fine Particulate Matter)")
    if len(selected_zips) > 0:
        indicator_cols = st.columns(min(3, len(selected_zips)))
        for i, zip_code in enumerate(selected_zips):
            if zip_code in current_data and "PM2.5" in current_data[zip_code]:
                pm25_data = current_data[zip_code]["PM2.5"]
                aqi = pm25_data.get("AQI")
                fig = create_aqi_indicator(aqi, f"{zip_code} - {COLORADO_ZIPS.get(zip_code, 'Unknown')}")
                if fig:
                    with indicator_cols[i % len(indicator_cols)]:
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown(f"**Category:** {get_aqi_category(aqi)}")
                        st.markdown(f"**Last Updated:** {format_datetime(pm25_data.get('DateObserved', ''))}")
            else:
                st.warning(f"No PM2.5 data for {zip_code}")

with col2:
    st.subheader("Ozone (O₃)")
    if len(selected_zips) > 0:
        indicator_cols = st.columns(min(3, len(selected_zips)))
        for i, zip_code in enumerate(selected_zips):
            if zip_code in current_data and "O3" in current_data[zip_code]:
                o3_data = current_data[zip_code]["O3"]
                aqi = o3_data.get("AQI")
                fig = create_aqi_indicator(aqi, f"{zip_code} - {COLORADO_ZIPS.get(zip_code, 'Unknown')}")
                if fig:
                    with indicator_cols[i % len(indicator_cols)]:
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown(f"**Category:** {get_aqi_category(aqi)}")
                        st.markdown(f"**Last Updated:** {format_datetime(o3_data.get('DateObserved', ''))}")
            else:
                st.warning(f"No Ozone data for {zip_code}")

# ------------------ Air Quality Comparisons ------------------ #
st.header("Air Quality Comparisons")
col1, col2 = st.columns(2)

with col1:
    st.subheader("PM2.5 Comparison")
    fig = plot_aqi_comparison(comparison_data, "PM2.5")
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No PM2.5 comparison data available.")

with col2:
    st.subheader("Ozone Comparison")
    fig = plot_aqi_comparison(comparison_data, "O3")
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No Ozone comparison data available.")

# ------------------ Historical AQI Trends ------------------ #
import plotly.express as px

st.header("Air Quality Trends (Last 7 Days)")
selected_pollutant = st.selectbox("Choose a pollutant", ["O3", "PM2.5"])

records = []

for zip_code, pollutant_data in historical_data.items():
    readings = pollutant_data.get(selected_pollutant, [])
    for entry in readings:
        records.append({
            "ZIP Code": zip_code,
            "Date": entry["DateObserved"],
            "AQI": entry["AQI"]
        })

# FAKE DATA fallback for testing (remove this in production)
if not records:
    import random
    today = datetime.now().date()
    zip_codes = ["80204", "80301", "80521"]
    for zip_code in zip_codes:
        for i in range(7):
            records.append({
                "ZIP Code": zip_code,
                "Date": str(today - timedelta(days=i)),
                "AQI": random.randint(20, 130)
            })

if records:
    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])
    zip_options = sorted(df["ZIP Code"].unique())
    selected_zip = st.selectbox("Filter by ZIP Code", ["All ZIPs"] + zip_options)

    if selected_zip != "All ZIPs":
        df = df[df["ZIP Code"] == selected_zip]

    fig = px.line(
        df,
        x="Date", y="AQI", color="ZIP Code", markers=True,
        title=f"{selected_pollutant} AQI Trends by ZIP Code",
        hover_data={"ZIP Code": True, "Date": True, "AQI": True}
    )

    # AQI color bands
    fig.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1, line_width=0)
    fig.add_hrect(y0=51, y1=100, fillcolor="yellow", opacity=0.1, line_width=0)
    fig.add_hrect(y0=101, y1=150, fillcolor="orange", opacity=0.1, line_width=0)
    fig.add_hrect(y0=151, y1=200, fillcolor="red", opacity=0.1, line_width=0)
    fig.add_hrect(y0=201, y1=300, fillcolor="purple", opacity=0.1, line_width=0)
    fig.add_hrect(y0=301, y1=500, fillcolor="maroon", opacity=0.1, line_width=0)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No historical data available for this pollutant.")

# ------------------ Health Implications ------------------ #
st.header("Health Implications of Air Quality")
st.markdown("""
Air quality can significantly affect human health, especially for sensitive groups such as:
- Children and older adults
- People with heart or lung disease
- People who are active outdoors

The Air Quality Index (AQI) provides a standardized way to understand air pollution levels and their potential health effects.
""")

# Table for health info based on AQI category
health_data = []
for category, info in AQI_CATEGORIES.items():
    lower, upper = info["range"]
    health_data.append({
        "Category": category,
        "AQI Range": f"{lower} - {upper}",
        "Health Implications": info["description"],
        "Color": info["color"]
    })

health_df = pd.DataFrame(health_data)

for _, row in health_df.iterrows():
    st.markdown(
        f"<div style='background-color: {row['Color']}; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
        f"<strong>{row['Category']} ({row['AQI Range']}):</strong> {row['Health Implications']}"
        f"</div>", unsafe_allow_html=True
    )

# ------------------ Footer ------------------ #
st.markdown("---")
st.markdown("Data source: [AirNow API](https://docs.airnowapi.org/)")
st.markdown("Dashboard updated daily | Last refresh: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

st.markdown("---")
st.markdown("Built by Mateus Di Francesco — Pre-med student exploring public health through code 💻🧬")
