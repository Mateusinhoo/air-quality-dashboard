import streamlit as st
import pydeck as pdk
import pandas as pd
import plotly.graph_objects as go

def create_aqi_map(data):
    if not data:
        st.warning("No air quality data to display.")
        return

    df = pd.DataFrame(data)
    df["radius"] = df["AQI"].apply(lambda x: 4000 + x * 200)

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
                get_fill_color='[255 - AQI*2, 255 - AQI, AQI, 100]',
                get_radius="radius",
                pickable=True,
                opacity=0.6,
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

def show_aqi_rankings(data):
    df = pd.DataFrame(data)

    if df.empty:
        st.info("No data available for rankings.")
        return

    most_polluted = df.sort_values(by="AQI", ascending=False).head(10).reset_index(drop=True)
    cleanest = df.sort_values(by="AQI", ascending=True).head(10).reset_index(drop=True)

    st.markdown("""
        <style>
            .rank-wrapper {
                display: flex;
                justify-content: center;
                align-items: flex-start;
                gap: 60px;
                margin-top: 2rem;
                margin-bottom: 2rem;
                flex-wrap: wrap;
            }
            .rank-box {
                background-color: #1e1e1e;
                border-radius: 12px;
                padding: 1.5rem 2rem;
                width: 360px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            }
            .rank-box h4 {
                text-align: center;
                margin-bottom: 1.2rem;
                color: #fff;
                font-size: 1.25rem;
            }
            .rank-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem 0;
                color: #eee;
                font-size: 0.95rem;
                border-bottom: 1px solid #333;
            }
            .rank-label {
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 0.4rem;
            }
            .rank-aqi {
                padding: 0.3rem 0.7rem;
                border-radius: 8px;
                font-weight: bold;
                font-size: 0.9rem;
            }
        </style>
        <div class='rank-wrapper'>
    """, unsafe_allow_html=True)

    def get_color(aqi):
        if aqi <= 50:
            return "#a8e05f"
        elif aqi <= 100:
            return "#fdd74b"
        elif aqi <= 150:
            return "#fe9b57"
        elif aqi <= 200:
            return "#fe6a69"
        elif aqi <= 300:
            return "#a97abc"
        else:
            return "#a87383"

    polluted_html = "<div class='rank-box'><h4>🏴 Most Polluted ZIPs</h4>"
    for i, row in most_polluted.iterrows():
        color = get_color(row['AQI'])
        polluted_html += f"""
        <div class='rank-row'>
            <span class='rank-label'>🇺🇸 {i+1}. {row['city']} ({row['zip']})</span>
            <span class='rank-aqi' style='background-color:{color}; color:#000;'>{row['AQI']}</span>
        </div>
        """
    polluted_html += "</div>"

    clean_html = "<div class='rank-box'><h4>🌿 Cleanest ZIPs</h4>"
    for i, row in cleanest.iterrows():
        color = get_color(row['AQI'])
        clean_html += f"""
        <div class='rank-row'>
            <span class='rank-label'>🇺🇸 {i+1}. {row['city']} ({row['zip']})</span>
            <span class='rank-aqi' style='background-color:{color}; color:#000;'>{row['AQI']}</span>
        </div>
        """
    clean_html += "</div></div>"

    st.markdown(polluted_html + clean_html, unsafe_allow_html=True)

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
