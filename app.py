import streamlit as st
from config import COLORADO_ZIPS, POLLUTANTS
from data_loader import get_air_quality_data, get_asthma_data, get_map_data
from visualizations import (
    create_aqi_map,
    show_aqi_rankings,
    plot_pollution_trend,
    plot_asthma_vs_pollution
)

# Page config
st.set_page_config(page_title="Colorado Air & Asthma Tracker", page_icon="🫁", layout="wide")

# Custom CSS for styling - Enhanced for a clean, professional look
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #2c3e50;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
            color: #1e3a8a;
        }

        h2 {
            font-weight: 600;
            font-size: 1.8rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #1e3a8a;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.5rem;
        }

        h3 {
            font-weight: 600;
            font-size: 1.4rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: #2563eb;
        }

        p, li, div {
            font-size: 1rem;
            line-height: 1.6;
            color: #4b5563;
        }

        .stMetric {
            border: 1px solid #e5e7eb;
            padding: 1.5rem;
            border-radius: 0.75rem;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            text-align: center;
        }

        /* Card styling for sections */
        .card {
            background-color: #ffffff;
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }

        /* Button styling */
        .stButton button {
            background-color: #2563eb;
            color: white;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
            border: none;
        }

        /* Selectbox styling */
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 0.5rem;
            border: 1px solid #e5e7eb;
        }

        /* Radio button styling */
        .stRadio [role="radiogroup"] {
            padding: 0.5rem;
            background-color: #f9fafb;
            border-radius: 0.5rem;
        }

        /* Separator styling */
        hr {
            margin-top: 2rem;
            margin-bottom: 2rem;
            border: 0;
            height: 1px;
            background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0));
        }

        /* Caption styling */
        .caption {
            font-size: 0.875rem;
            color: #6b7280;
            font-style: italic;
            margin-bottom: 1rem;
        }

        /* Footer styling */
        .footer {
            text-align: center;
            padding: 2rem 0;
            font-size: 0.875rem;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
            margin-top: 3rem;
        }
    </style>
""", unsafe_allow_html=True)

# Title and intro
st.markdown("# 🫁 Colorado Air & Asthma Tracker")
st.markdown("Explore real-time air quality across Colorado ZIP codes and how it correlates with asthma.")
st.markdown("---")

# Map section
st.markdown("## 🗺️ Colorado Air Quality Map")
st.markdown('<p class="caption">Interactive map showing air quality levels across Colorado. Larger circles indicate higher pollution levels.</p>', unsafe_allow_html=True)

# Map visualization
map_data = get_map_data()
create_aqi_map(map_data)

# Rankings section
st.markdown("---")
st.markdown("## 📊 Air Quality Rankings")
st.markdown('<p class="caption">Comparison of the most polluted and cleanest ZIP codes in Colorado based on current air quality data.</p>', unsafe_allow_html=True)

# Rankings visualization
show_aqi_rankings(map_data)

st.markdown("---")

# ZIP and pollutant selection
st.markdown("## 📍 Location & Pollutant Selection")
st.markdown('<p class="caption">Select a specific ZIP code and pollutant type to view detailed data.</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    zip_code = st.selectbox("Choose a ZIP Code", COLORADO_ZIPS)
with col2:
    pollutant = st.radio("Select a pollutant", POLLUTANTS)

# Data fetch
air_data = get_air_quality_data(zip_code, pollutant)
asthma_data = get_asthma_data(zip_code)

# Pollution trend section
st.markdown("## 📈 Pollution Trend Analysis")
st.markdown('<p class="caption">Recent air quality levels for the selected ZIP and pollutant. Interactive and zoomable chart.</p>', unsafe_allow_html=True)

plot_pollution_trend(air_data, pollutant)

# Asthma correlation section
st.markdown("## 🫁 Asthma and Pollution Correlation")
st.markdown('<p class="caption">This chart compares recent pollution trends with local asthma rates, showing potential health impacts.</p>', unsafe_allow_html=True)

plot_asthma_vs_pollution(air_data, asthma_data)

# Enhanced footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <div>
        <strong>Data Sources:</strong> AirNow API & CDC Asthma Data | 
        <strong>Updated:</strong> Real-time | 
        <strong>Coverage:</strong> Colorado ZIP Codes
    </div>
    <div style="margin-top: 0.5rem;">
        Built with 💙 for Colorado • Powered by Streamlit • © 2025
    </div>
</div>
""", unsafe_allow_html=True)
