from database import store_api_data
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from config import COLORADO_ZIPS, DEFAULT_ZIPS, AQI_CATEGORIES, POLLUTANTS
from air_quality_data import get_cached_air_quality_data
from visualizations import plot_aqi_comparison, plot_aqi_time_series, create_aqi_indicator
from utils import get_aqi_category, format_datetime, prepare_comparison_data, prepare_time_series_data

# ✅ SET PAGE CONFIG — MUST BE FIRST Streamlit command
st.set_page_config(
    page_title="Colorado Air Quality Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === THEME SWITCHING ===
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"], index=0)
custom_css = """
    <style>
        body { font-family: 'Segoe UI', sans-serif; }
        .main { background-color: %s; color: %s; }
        h1, h2, h3, h4 { color: %s; }
        .stButton>button { background-color: #4B8BBE; color: white; border-radius: 8px; }
        .stButton>button:hover { background-color: #3a6e99; }
    </style>
""" % (
    "#f8f9fa" if theme == "Light" else "#1e1e1e",
    "#212529" if theme == "Light" else "#f8f9fa",
    "#4B8BBE"
)
st.markdown(custom_css, unsafe_allow_html=True)

# === HEADER ===
st.markdown("""
    <h1 style='text-align: center; font-size: 2.6rem;'>🌍 Colorado Air Quality Dashboard</h1>
    <p style='text-align: center; font-size: 1.1rem; color: #6c757d;'>
        Explore real-time air quality and regional asthma data by ZIP code
    </p>
    <hr style='margin-top: -1rem; margin-bottom: 2rem;' />
""", unsafe_allow_html=True)

# === SIDEBAR FILTER ===
st.sidebar.header("ZIP Code Filter")
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

# === Fetch and Prepare Data ===
data = get_cached_air_quality_data()
time_series_data = prepare_time_series_data(data, selected_zips)
comparison_data = prepare_comparison_data(data, selected_zips)

# === Dashboard Layout ===
st.subheader("Current Air Quality by ZIP Code")
st.write("Use the charts below to view PM2.5 and Ozone levels across regions.")
st.plotly_chart(plot_aqi_comparison(comparison_data), use_container_width=True)

st.subheader("Air Quality Trends Over Time")
st.plotly_chart(plot_aqi_time_series(time_series_data), use_container_width=True)

st.subheader("Asthma Rates (Coming Soon)")
st.info("Asthma prevalence data by ZIP or county will be integrated here in the next update.")
