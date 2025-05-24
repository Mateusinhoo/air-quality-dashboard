import streamlit as st
import pydeck as pdk
import pandas as pd
import plotly.graph_objects as go


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
        <div style='background-color:{color}; padding:1rem; border-radius:1rem;
                    text-align:center; box-shadow:0 2px 5px rgba(0,0,0,0.1);'>
            <h3 style='margin:0;'>ZIP {row['zip']}</h3>
            <p style='font-size:2rem; margin:0;'>{row['AQI']}</p>
            <small>{row['Pollutant']}</small><br>
            <span style='font-size:0.9rem;'>{category}</span>
        </div>
        """
        cols[i].markdown(card_html, unsafe_allow_html=True)


def plot_pollution_trend(data, pollutant):
    if data.empty:
        st.info("No air quality trend data available for this ZIP and pollutant.")
        return

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["Date"],
        y=data["Value"],
        mode="lines+markers",
        name=f"{pollutant} Level",
        line=dict(color="#1976d2", width=3)
    ))

    fig.update_layout(
        height=300,
        title=f"{pollutant} Trend Over Time",
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="white",
        plot_bgcolor="#f0f2f6",
        font=dict(size=13, color="#333"),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_asthma_vs_pollution(air_data, asthma_data):
    if air_data.empty or asthma_data.empty:
        st.info("Not enough data to compare asthma and pollution.")
        return

    asthma_rate = asthma_data['Asthma Rate'].iloc[0]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=air_data["Date"],
        y=air_data["Value"],
        mode="lines+markers",
        name="Pollution Level",
        line=dict(color="#1976d2", width=3)
    ))

    fig.add_trace(go.Scatter(
        x=air_data["Date"],
        y=[asthma_rate] * len(air_data),
        mode="lines",
        name=f"Asthma Rate ({asthma_rate}%)",
        line=dict(color="#d32f2f", dash="dash")
    ))

    fig.update_layout(
        height=300,
        title="Pollution vs Asthma Rate",
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="white",
        plot_bgcolor="#f0f2f6",
        font=dict(size=13, color="#333"),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
