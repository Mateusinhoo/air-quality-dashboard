import streamlit as st
from config import COLORADO_ZIPS, POLLUTANTS
from data_loader import get_air_quality_data, get_asthma_data, get_map_data
from visualizations import (
    create_aqi_map,
    show_aqi_cards,
    plot_pollution_trend,
    plot_asthma_vs_pollution
)

# Page config
st.set_page_config(page_title="Colorado Air & Asthma Tracker", page_icon="🫁", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI&display=swap');

        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            color: #222;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        h1, h2, h3 {
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .stMetric {
            border: 1px solid #eee;
            padding: 1.5rem;
            border-radius: 1rem;
            background-color: #f9f9f9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Title and intro
st.markdown("# 🫁 Colorado Air & Asthma Tracker")
st.markdown("Explore real-time air quality across Colorado ZIP codes and how it correlates with asthma.")
st.markdown("---")

# Map section
st.markdown("## 🗺️ Colorado Air Quality Map")
map_data = get_map_data()
create_aqi_map(map_data)
st.markdown("&nbsp;", unsafe_allow_html=True)

# AQI cards
st.markdown("## 🧭 AQI Summary by Region")
show_aqi_cards(map_data)
st.markdown("---")

# ZIP and pollutant selection
col1, col2 = st.columns([1, 1])
with col1:
    zip_code = st.selectbox("Choose a ZIP Code", COLORADO_ZIPS)
with col2:
    pollutant = st.radio("Select a pollutant", POLLUTANTS)

# Data fetch
air_data = get_air_quality_data(zip_code, pollutant)
asthma_data = get_asthma_data(zip_code)

# Visualizations
st.markdown("### 📊 Pollution Trend")
st.caption("Recent air quality levels for the selected ZIP and pollutant.")
plot_pollution_trend(air_data, pollutant)
st.markdown("&nbsp;", unsafe_allow_html=True)

st.markdown("### 🫁 Asthma and Pollution Correlation")
st.caption("Compare the recent pollution trend with the local asthma rate.")
plot_asthma_vs_pollution(air_data, asthma_data)
st.markdown("&nbsp;", unsafe_allow_html=True)

# Footer (optional)
st.markdown("---")
st.markdown("<div style='text-align:center; font-size:0.9rem; color:#888;'>Built by Mateus · Powered by Streamlit · AirNow & CDC data</div>", unsafe_allow_html=True)
