# visualizations.py
import streamlit as st
import pydeck as pdk
import pandas as pd
import matplotlib.pyplot as plt


def create_aqi_map(data):
    if not data:
        st.warning("No air quality data to display.")
        return

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


def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good", "#a8e05f"
    elif aqi <= 100:
        return "Moderate", "#fdd74b"
    elif aqi <= 150:
        return "Unhealthy for Sensitive", "#fe9b57"
    elif aqi <= 200:
        return "Unhealthy", "#fe6a69"
    elif aqi <= 300:
        return "Very Unhealthy", "#a97abc"
    else:
        return "Hazardous", "#a87383"


def show_aqi_cards(data):
    df = pd.DataFrame(data)
    cols = st.columns(len(df))
    for i, row in df.iterrows():
        category, color = get_aqi_category(row['AQI'])
        card_html = f"""
        <div style='background-color:{color}; padding:1rem; border-radius:1rem; text-align:center; box-shadow:0 2px 5px rgba(0,0,0,0.1);'>
            <h3 style='margin:0;'>ZIP {row['zip']}</h3>
            <p style='font-size:2rem; margin:0;'>{row['AQI']}</p>
            <small>{row['Pollutant']}</small><br>
            <span style='font-size:0.9rem;'>{category}</span>
        </div>
        """
        cols[i].markdown(card_html, unsafe_allow_html=True)


def plot_pollution_trend(data, pollutant):
    fig, ax = plt.subplots()
    ax.plot(data["Date"], data["Value"], marker='o')
    ax.set_title(f"{pollutant} Trend Over Time")
    ax.set_ylabel(f"{pollutant} Level")
    ax.set_xlabel("Date")
    ax.grid(True)
    st.pyplot(fig)


def plot_asthma_vs_pollution(air_data, asthma_data):
    st.metric(label="Current Asthma Rate", value=f"{asthma_data['Asthma Rate'].iloc[0]}%")
    st.line_chart(air_data.set_index("Date"))
