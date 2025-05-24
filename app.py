# app.py
import streamlit as st
from config import COLORADO_ZIPS, POLLUTANTS
from data_loader import get_air_quality_data, get_asthma_data
from visualizations import plot_pollution_trend, plot_asthma_vs_pollution

st.set_page_config(page_title="Colorado Air & Asthma Tracker", page_icon="🫁", layout="wide")

st.markdown("# 🫁 Colorado Air & Asthma Tracker")
st.markdown("Explore the relationship between air quality and asthma in Colorado ZIP codes.")

col1, col2 = st.columns([1, 1])
with col1:
    zip_code = st.selectbox("Choose a ZIP Code", COLORADO_ZIPS)
with col2:
    pollutant = st.radio("Select a pollutant", POLLUTANTS)

air_data = get_air_quality_data(zip_code, pollutant)
asthma_data = get_asthma_data(zip_code)

st.markdown("### 📊 Pollution Trend")
plot_pollution_trend(air_data, pollutant)

st.markdown("### 🫁 Asthma and Pollution Correlation")
plot_asthma_vs_pollution(air_data, asthma_data)
