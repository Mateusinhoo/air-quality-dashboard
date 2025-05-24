import streamlit as st
from config import COLORADO_ZIPS, POLLUTANTS
from data_loader import get_air_quality_data, get_asthma_data, get_map_data
from visualizations import (
    create_aqi_map,
    show_aqi_cards,
    plot_pollution_trend,
    plot_asthma_vs_pollution
)

st.set_page_config(page_title="Colorado Air & Asthma Tracker", page_icon="🫁", layout="wide")

# Title and subtitle
st.markdown("# 🫁 Colorado Air & Asthma Tracker")
st.markdown("Explore real-time air quality across Colorado ZIP codes and how it correlates with asthma.")

# Full-width interactive map
st.markdown("## 🗺️ Colorado Air Quality Map")
map_data = get_map_data()
create_aqi_map(map_data)

# Color-coded AQI summary cards
st.markdown("## 🧭 AQI Summary by Region")
show_aqi_cards(map_data)

# ZIP & pollutant selection
col1, col2 = st.columns([1, 1])
with col1:
    zip_code = st.selectbox("Choose a ZIP Code", COLORADO_ZIPS)
with col2:
    pollutant = st.radio("Select a pollutant", POLLUTANTS)

# Get air and asthma data
air_data = get_air_quality_data(zip_code, pollutant)
asthma_data = get_asthma_data(zip_code)

# Trend and correlation charts
st.markdown("### 📊 Pollution Trend")
plot_pollution_trend(air_data, pollutant)

st.markdown("### 🫁 Asthma and Pollution Correlation")
plot_asthma_vs_pollution(air_data, asthma_data)
