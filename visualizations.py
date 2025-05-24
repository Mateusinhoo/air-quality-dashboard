import streamlit as st
import matplotlib.pyplot as plt

def plot_pollution_trend(data, pollutant):
    fig, ax = plt.subplots()
    ax.plot(data["Date"], data["Value"], marker='o')
    ax.set_title(f"{pollutant} Trend Over Time")
    ax.set_ylabel(f"{pollutant} Level")
    ax.set_xlabel("Date")
    st.pyplot(fig)

def plot_asthma_vs_pollution(air_data, asthma_data):
    st.metric(label="Current Asthma Rate", value=f"{asthma_data['Asthma Rate'].iloc[0]}%")
    st.line_chart(air_data.set_index("Date"))

import streamlit as st
import pydeck as pdk
import pandas as pd

def create_aqi_map(data):
    if data.empty:
        st.warning("No air quality data to display.")
        return

    # Example data format: [{zip: 80202, lat: 39.75, lon: -104.99, AQI: 85, Pollutant: "PM2.5"}]
    df = pd.DataFrame(data)

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=39.55,
            longitude=-105.78,
            zoom=6,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position='[lon, lat]',
                get_fill_color='[255 - AQI*2, 255 - AQI, AQI]',
                get_radius=7000,
                pickable=True,
                opacity=0.7,
            ),
        ],
        tooltip={"text": "ZIP: {zip}\nAQI: {AQI}\nPollutant: {Pollutant}"}
    ))
