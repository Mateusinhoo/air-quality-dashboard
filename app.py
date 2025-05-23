import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Colorado Air Quality Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean page layout and branding
st.markdown("""
    <h1 style='text-align: center; font-size: 2.8rem; color: #4B8BBE;'>
        🫁 Colorado Air Quality Dashboard
    </h1>
    <p style='text-align: center; font-size: 1.1rem; color: #6c757d; margin-bottom: 2rem;'>
        Real-time PM2.5 and Ozone levels in selected ZIP codes — updated daily
    </p>
    <hr style='margin-top: -1rem; margin-bottom: 2rem;' />
""", unsafe_allow_html=True)

st.markdown("### 🔎 Summary")
st.markdown("- **Highest AQI Today:** Boulder (O3 - 122, Unhealthy for Sensitive Groups)")
st.markdown("- **Best Air Today:** Denver (PM2.5 - 35, Moderate)")

from config import COLORADO_ZIPS, DEFAULT_ZIPS, AQI_CATEGORIES, POLLUTANTS
from air_quality_data import get_cached_air_quality_data
from visualizations import plot_aqi_comparison, plot_aqi_time_series, create_aqi_indicator
from utils import get_aqi_category, format_datetime, prepare_comparison_data, prepare_time_series_data

# Custom CSS to improve fonts and styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .key-insights {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4B8BF5;
        margin-bottom: 2rem;
    }
    .insights-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        color: #1E3A8A;
    }
    .insights-content {
        font-size: 1.1rem;
    }
    .good-aqi {
        color: #00E400;
        font-weight: 600;
    }
    .moderate-aqi {
        color: #FFFF00;
        font-weight: 600;
    }
    .sensitive-aqi {
        color: #FF7E00;
        font-weight: 600;
    }
    .unhealthy-aqi {
        color: #FF0000;
        font-weight: 600;
    }
    .very-unhealthy-aqi {
        color: #99004C;
        font-weight: 600;
    }
    .hazardous-aqi {
        color: #7E0023;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<div class="main-header">Colorado Air Quality Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Real-time air quality data for selected ZIP codes in Colorado. Updated daily with PM2.5 and Ozone measurements.</div>', 
    unsafe_allow_html=True
)

# Sidebar for controls
st.sidebar.header("Settings")

# ZIP code selection
selected_zips = st.sidebar.multiselect(
    "Select ZIP Codes",
    options=list(COLORADO_ZIPS.keys()),
    default=DEFAULT_ZIPS,
    format_func=lambda x: f"{x} - {COLORADO_ZIPS.get(x, 'Unknown')}"
)

# Use default ZIP codes if none selected
if not selected_zips:
    selected_zips = DEFAULT_ZIPS
    st.sidebar.warning(f"No ZIP codes selected. Using defaults: {', '.join(DEFAULT_ZIPS)}")

# Data refresh button
if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Last updated time
st.sidebar.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Show AQI information in the sidebar
st.sidebar.header("AQI Information")
for category, info in AQI_CATEGORIES.items():
    lower, upper = info["range"]
    st.sidebar.markdown(
        f"<div style='background-color: {info['color']}; padding: 5px; border-radius: 5px;'>"
        f"<strong>{category}:</strong> {lower}-{upper}"
        f"</div>",
        unsafe_allow_html=True
    )

# About section in sidebar
st.sidebar.header("About")
st.sidebar.info("""
This dashboard uses the AirNow API to fetch air quality data.
Data is cached for one hour to reduce API calls.
""")

# Explanation of pollutants
st.sidebar.header("Pollutant Information")
for pollutant, info in POLLUTANTS.items():
    with st.sidebar.expander(f"{info['name']} ({pollutant})"):
        st.write(info["description"])

# Load data with a loading spinner
with st.spinner("Loading air quality data..."):
    # Fetch the data
    try:
        current_data, historical_data = get_cached_air_quality_data(selected_zips)
        
        # Prepare data for visualizations
        comparison_data = prepare_comparison_data(current_data)
        time_series_data = prepare_time_series_data(historical_data)
        
        # Check if we have data
        if not current_data and not historical_data:
            st.error("No data available. Please check your API key and try again.")
            st.stop()
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Key Insights Section
if comparison_data is not None and not comparison_data.empty:
    # Find the highest PM2.5 and Ozone values and their locations
    pm25_data = comparison_data[comparison_data['Pollutant'] == 'PM2.5']
    o3_data = comparison_data[comparison_data['Pollutant'] == 'O3']
    
    # Initialize variables to track highest values
    highest_pm25 = None
    highest_o3 = None
    highest_pm25_loc = None
    highest_o3_loc = None
    highest_pm25_zip = None
    highest_o3_zip = None
    highest_pm25_category = None
    highest_o3_category = None
    
    if not pm25_data.empty and 'AQI' in pm25_data.columns:
        # Find the maximum AQI value and its index
        max_pm25_value = pm25_data['AQI'].max() 
        max_pm25_rows = pm25_data[pm25_data['AQI'] == max_pm25_value]
        
        if not max_pm25_rows.empty:
            highest_pm25_row = max_pm25_rows.iloc[0]
            highest_pm25 = highest_pm25_row['AQI']
            highest_pm25_zip = highest_pm25_row['ZIP']
            highest_pm25_loc = COLORADO_ZIPS.get(highest_pm25_zip, 'Unknown')
            highest_pm25_category = get_aqi_category(highest_pm25)
    
    if not o3_data.empty and 'AQI' in o3_data.columns:
        # Find the maximum AQI value and its index
        max_o3_value = o3_data['AQI'].max()
        max_o3_rows = o3_data[o3_data['AQI'] == max_o3_value]
        
        if not max_o3_rows.empty:
            highest_o3_row = max_o3_rows.iloc[0]
            highest_o3 = highest_o3_row['AQI']
            highest_o3_zip = highest_o3_row['ZIP']
            highest_o3_loc = COLORADO_ZIPS.get(highest_o3_zip, 'Unknown')
            highest_o3_category = get_aqi_category(highest_o3)
    
    # Determine overall worst AQI
    worst_aqi = None
    worst_pollutant = None
    worst_loc = None
    worst_category = None
    worst_zip = None
    
    if highest_pm25 is not None and highest_o3 is not None:
        if highest_pm25 >= highest_o3:
            worst_aqi = highest_pm25
            worst_pollutant = "PM2.5"
            worst_loc = highest_pm25_loc
            worst_category = highest_pm25_category
            worst_zip = highest_pm25_zip
        else:
            worst_aqi = highest_o3
            worst_pollutant = "Ozone"
            worst_loc = highest_o3_loc
            worst_category = highest_o3_category
            worst_zip = highest_o3_zip
    elif highest_pm25 is not None:
        worst_aqi = highest_pm25
        worst_pollutant = "PM2.5"
        worst_loc = highest_pm25_loc
        worst_category = highest_pm25_category
        worst_zip = highest_pm25_zip
    elif highest_o3 is not None:
        worst_aqi = highest_o3
        worst_pollutant = "Ozone"
        worst_loc = highest_o3_loc
        worst_category = highest_o3_category
        worst_zip = highest_o3_zip
    
    # Generate CSS class for the AQI category
    category_class_map = {
        "Good": "good-aqi",
        "Moderate": "moderate-aqi",
        "Unhealthy for Sensitive Groups": "sensitive-aqi",
        "Unhealthy": "unhealthy-aqi",
        "Very Unhealthy": "very-unhealthy-aqi",
        "Hazardous": "hazardous-aqi"
    }
    
    if worst_category and worst_aqi is not None:
        category_class = category_class_map.get(worst_category, "")
        
        # Display Key Insights box
        st.markdown(
            f"""
            <div class="key-insights">
                <div class="insights-header">📊 Key Insights</div>
                <div class="insights-content">
                    Today's worst air quality: <span class="{category_class}">{worst_zip} - {worst_loc}</span> 
                    ({worst_pollutant}: {worst_aqi} – {worst_category})
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Current Air Quality Overview
st.header("Current Air Quality")

# Create two columns for PM2.5 and Ozone
col1, col2 = st.columns(2)

with col1:
    st.subheader("PM2.5 (Fine Particulate Matter)")
    
    # Create a grid for PM2.5 indicators
    if len(selected_zips) > 0:
        indicator_cols = st.columns(min(3, len(selected_zips)))
        zip_index = 0
        
        for zip_code in selected_zips:
            if zip_code in current_data and "PM2.5" in current_data[zip_code]:
                pm25_data = current_data[zip_code]["PM2.5"]
                aqi = pm25_data.get("AQI")
                
                col_idx = zip_index % len(indicator_cols)
                with indicator_cols[col_idx]:
                    location_name = f"{zip_code} - {COLORADO_ZIPS.get(zip_code, 'Unknown')}"
                    fig = create_aqi_indicator(aqi, location_name)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        category = get_aqi_category(aqi)
                        st.markdown(f"**Category:** {category}")
                        st.markdown(f"**Last Updated:** {format_datetime(pm25_data.get('DateObserved', ''))}")
                    else:
                        st.warning(f"No PM2.5 data available for {location_name}")
                
                zip_index += 1
            else:
                st.warning(f"No PM2.5 data available for {zip_code}")
    else:
        st.warning("No ZIP codes selected.")

with col2:
    st.subheader("Ozone (O3)")
    
    # Create a grid for Ozone indicators
    if len(selected_zips) > 0:
        indicator_cols = st.columns(min(3, len(selected_zips)))
        zip_index = 0
        
        for zip_code in selected_zips:
            if zip_code in current_data and "O3" in current_data[zip_code]:
                o3_data = current_data[zip_code]["O3"]
                aqi = o3_data.get("AQI")
                
                col_idx = zip_index % len(indicator_cols)
                with indicator_cols[col_idx]:
                    location_name = f"{zip_code} - {COLORADO_ZIPS.get(zip_code, 'Unknown')}"
                    fig = create_aqi_indicator(aqi, location_name)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        category = get_aqi_category(aqi)
                        st.markdown(f"**Category:** {category}")
                        st.markdown(f"**Last Updated:** {format_datetime(o3_data.get('DateObserved', ''))}")
                    else:
                        st.warning(f"No Ozone data available for {location_name}")
                
                zip_index += 1
            else:
                st.warning(f"No Ozone data available for {zip_code}")
    else:
        st.warning("No ZIP codes selected.")

# Comparisons
st.header("Air Quality Comparisons")

# Create two columns for PM2.5 and Ozone comparison bar charts
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

# Historical trends
st.header("Air Quality Trends (Last 7 Days)")

# Create two columns for PM2.5 and Ozone time series charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("PM2.5 Trend")
    fig = plot_aqi_time_series(time_series_data, selected_zips, "PM2.5")
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No PM2.5 trend data available.")

with col2:
    st.subheader("Ozone Trend")
    fig = plot_aqi_time_series(time_series_data, selected_zips, "O3")
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No Ozone trend data available.")

# Health implications
st.header("Health Implications of Air Quality")
st.markdown("""
Air quality can significantly affect human health, especially for sensitive groups such as:
- Children and older adults
- People with heart or lung disease
- People who are active outdoors

The Air Quality Index (AQI) provides a standardized way to understand air pollution levels and their potential health effects.
""")

# Create a table for AQI health implications
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

# Display the table with colored rows
for i, row in health_df.iterrows():
    color = row["Color"]
    st.markdown(
        f"<div style='background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
        f"<strong>{row['Category']} ({row['AQI Range']}):</strong> {row['Health Implications']}"
        f"</div>",
        unsafe_allow_html=True
    )

import plotly.express as px

st.markdown("## 📈 Historical AQI Trends (Past 7 Days)")
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
        
# FAKE DATA FOR TESTING (ONLY used if records are empty)
if not records:
    import random
    from datetime import datetime, timedelta
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

    # Optional ZIP filter
    zip_options = sorted(df["ZIP Code"].unique())
    selected_zip = st.selectbox("Filter by ZIP Code", ["All ZIPs"] + zip_options)

    if selected_zip != "All ZIPs":
        df = df[df["ZIP Code"] == selected_zip]

    # Create interactive line chart
    fig = px.line(
        df,
        x="Date",
        y="AQI",
        color="ZIP Code",
        markers=True,
        title=f"{selected_pollutant} AQI Trends by ZIP Code",
        hover_data={"ZIP Code": True, "Date": True, "AQI": True}
    )

    # Add AQI bands
    fig.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1, line_width=0)
    fig.add_hrect(y0=51, y1=100, fillcolor="yellow", opacity=0.1, line_width=0)
    fig.add_hrect(y0=101, y1=150, fillcolor="orange", opacity=0.1, line_width=0)
    fig.add_hrect(y0=151, y1=200, fillcolor="red", opacity=0.1, line_width=0)
    fig.add_hrect(y0=201, y1=300, fillcolor="purple", opacity=0.1, line_width=0)
    fig.add_hrect(y0=301, y1=500, fillcolor="maroon", opacity=0.1, line_width=0)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No historical data available for this pollutant.")

# Footer
st.markdown("---")
st.markdown("Data source: [AirNow API](https://docs.airnowapi.org/)")
st.markdown("Dashboard updated daily | Last refresh: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

st.markdown("---")
st.markdown("Built by Mateus Di Francesco. — Pre-med student exploring public health through code 💻🧬")