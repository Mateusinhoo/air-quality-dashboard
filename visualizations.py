import streamlit as st
import pydeck as pdk
import pandas as pd
import plotly.graph_objects as go
import base64

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

def get_aqi_color(aqi):
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

def get_flag_image():
    # US flag SVG as base64
    flag_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480">
        <defs>
            <clipPath id="a">
                <path fill-opacity=".7" d="M0 0h682.7v512H0z"/>
            </clipPath>
        </defs>
        <g fill-rule="evenodd" clip-path="url(#a)" transform="scale(.9375)">
            <path fill="#bd3d44" d="M0 0h972.8v39.4H0zm0 78.8h972.8v39.4H0zm0 78.7h972.8V197H0zm0 78.8h972.8v39.4H0zm0 78.8h972.8v39.4H0zm0 78.7h972.8v39.4H0zm0 78.8h972.8V512H0z"/>
            <path fill="#fff" d="M0 39.4h972.8v39.4H0zm0 78.8h972.8v39.3H0zm0 78.7h972.8v39.4H0zm0 78.8h972.8v39.4H0zm0 78.8h972.8v39.4H0zm0 78.7h972.8v39.4H0z"/>
            <path fill="#192f5d" d="M0 0h389.1v275.7H0z"/>
            <path fill="#fff" d="M32.4 11.8L36 22.7h11.4l-9.2 6.7 3.5 11-9.3-6.8-9.2 6.7 3.5-10.9-9.3-6.7H29zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.5 11-9.2-6.8-9.3 6.7 3.5-10.9-9.2-6.7h11.4zm64.8 0l3.6 10.9H177l-9.2 6.7 3.5 11-9.3-6.8-9.2 6.7 3.5-10.9-9.3-6.7h11.5zm64.9 0l3.5 10.9H242l-9.3 6.7 3.6 11-9.3-6.8-9.3 6.7 3.6-10.9-9.3-6.7h11.4zm64.8 0l3.6 10.9h11.4l-9.2 6.7 3.5 11-9.3-6.8-9.2 6.7 3.5-10.9-9.2-6.7h11.4zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.6 11-9.3-6.8-9.3 6.7 3.6-10.9-9.3-6.7h11.5zM64.9 39.4l3.5 10.9h11.5L70.6 57 74 67.9l-9-6.7-9.3 6.7L59 57l-9-6.7h11.4zm64.8 0l3.6 10.9h11.4l-9.3 6.7 3.6 10.9-9.3-6.7-9.3 6.7L124 57l-9.3-6.7h11.5zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.5 10.9-9.2-6.7-9.3 6.7 3.5-10.9-9.2-6.7H191zm64.8 0l3.6 10.9h11.4l-9.3 6.7 3.6 10.9-9.3-6.7-9.2 6.7 3.5-10.9-9.3-6.7H256zm64.9 0l3.5 10.9h11.5L330 57l3.5 10.9-9.2-6.7-9.3 6.7 3.5-10.9-9.2-6.7h11.4zM32.4 66.9L36 78h11.4l-9.2 6.7 3.5 10.9-9.3-6.8-9.2 6.8 3.5-11-9.3-6.7H29zm64.9 0l3.5 11h11.5l-9.3 6.7 3.5 10.9-9.2-6.8-9.3 6.8 3.5-11-9.2-6.7h11.4zm64.8 0l3.6 11H177l-9.2 6.7 3.5 10.9-9.3-6.8-9.2 6.8 3.5-11-9.3-6.7h11.5zm64.9 0l3.5 11H242l-9.3 6.7 3.6 10.9-9.3-6.8-9.3 6.8 3.6-11-9.3-6.7h11.4zm64.8 0l3.6 11h11.4l-9.2 6.7 3.5 10.9-9.3-6.8-9.2 6.8 3.5-11-9.2-6.7h11.4zm64.9 0l3.5 11h11.5l-9.3 6.7 3.6 10.9-9.3-6.8-9.3 6.8 3.6-11-9.3-6.7h11.5zM64.9 94.5l3.5 10.9h11.5l-9.3 6.7 3.5 11-9.2-6.8-9.3 6.7 3.5-10.9-9.2-6.7h11.4zm64.8 0l3.6 10.9h11.4l-9.3 6.7 3.6 11-9.3-6.8-9.3 6.7 3.6-10.9-9.3-6.7h11.5zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.5 11-9.2-6.8-9.3 6.7 3.5-10.9-9.2-6.7H191zm64.8 0l3.6 10.9h11.4l-9.2 6.7 3.5 11-9.3-6.8-9.2 6.7 3.5-10.9-9.3-6.7H256zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.5 11-9.2-6.8-9.3 6.7 3.5-10.9-9.2-6.7h11.4zM32.4 122.1L36 133h11.4l-9.2 6.7 3.5 11-9.3-6.8-9.2 6.7 3.5-10.9-9.3-6.7H29zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.5 10.9-9.2-6.7-9.3 6.7 3.5-10.9-9.2-6.7h11.4zm64.8 0l3.6 10.9H177l-9.2 6.7 3.5 10.9-9.3-6.7-9.2 6.7 3.5-10.9-9.3-6.7h11.5zm64.9 0l3.5 10.9H242l-9.3 6.7 3.6 10.9-9.3-6.7-9.3 6.7 3.6-10.9-9.3-6.7h11.4zm64.8 0l3.6 10.9h11.4l-9.2 6.7 3.5 10.9-9.3-6.7-9.2 6.7 3.5-10.9-9.2-6.7h11.4zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.6 10.9-9.3-6.7-9.3 6.7 3.6-10.9-9.3-6.7h11.5zM64.9 149.7l3.5 10.9h11.5l-9.3 6.7 3.5 10.9-9.2-6.8-9.3 6.8 3.5-11-9.2-6.7h11.4zm64.8 0l3.6 10.9h11.4l-9.3 6.7 3.6 10.9-9.3-6.8-9.3 6.8 3.6-11-9.3-6.7h11.5zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.5 10.9-9.2-6.8-9.3 6.8 3.5-11-9.2-6.7H191zm64.8 0l3.6 10.9h11.4l-9.2 6.7 3.5 10.9-9.3-6.8-9.2 6.8 3.5-11-9.3-6.7H256zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.5 10.9-9.2-6.8-9.3 6.8 3.5-11-9.2-6.7h11.4zM32.4 177.2l3.6 11h11.4l-9.2 6.7 3.5 10.8-9.3-6.7-9.2 6.7 3.5-10.9-9.3-6.7H29zm64.9 0l3.5 11h11.5l-9.3 6.7 3.6 10.8-9.3-6.7-9.3 6.7 3.6-10.9-9.3-6.7h11.4zm64.8 0l3.6 11H177l-9.2 6.7 3.5 10.8-9.3-6.7-9.2 6.7 3.5-10.9-9.3-6.7h11.5zm64.9 0l3.5 11H242l-9.3 6.7 3.6 10.8-9.3-6.7-9.3 6.7 3.6-10.9-9.3-6.7h11.4zm64.8 0l3.6 11h11.4l-9.2 6.7 3.5 10.8-9.3-6.7-9.2 6.7 3.5-10.9-9.2-6.7h11.4zm64.9 0l3.5 11h11.5l-9.3 6.7 3.6 10.8-9.3-6.7-9.3 6.7 3.6-10.9-9.3-6.7h11.5zM64.9 204.8l3.5 10.9h11.5l-9.3 6.7 3.5 11-9.2-6.8-9.3 6.7 3.5-10.9-9.2-6.7h11.4zm64.8 0l3.6 10.9h11.4l-9.3 6.7 3.6 11-9.3-6.8-9.3 6.7 3.6-10.9-9.3-6.7h11.5zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.5 11-9.2-6.8-9.3 6.7 3.5-10.9-9.2-6.7H191zm64.8 0l3.6 10.9h11.4l-9.2 6.7 3.5 11-9.3-6.8-9.2 6.7 3.5-10.9-9.3-6.7H256zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.5 11-9.2-6.8-9.3 6.7 3.5-10.9-9.2-6.7h11.4zM32.4 232.4l3.6 10.9h11.4l-9.2 6.7 3.5 10.9-9.3-6.7-9.2 6.7 3.5-11-9.3-6.7H29zm64.9 0l3.5 10.9h11.5L103 250l3.6 10.9-9.3-6.7-9.3 6.7 3.6-11-9.3-6.7h11.4zm64.8 0l3.6 10.9H177l-9 6.7 3.5 10.9-9.3-6.7-9.2 6.7 3.5-11-9.3-6.7h11.5zm64.9 0l3.5 10.9H242l-9.3 6.7 3.6 10.9-9.3-6.7-9.3 6.7 3.6-11-9.3-6.7h11.4zm64.8 0l3.6 10.9h11.4l-9.2 6.7 3.5 10.9-9.3-6.7-9.2 6.7 3.5-11-9.2-6.7h11.4zm64.9 0l3.5 10.9h11.5l-9.3 6.7 3.6 10.9-9.3-6.7-9.3 6.7 3.6-11-9.3-6.7h11.5z"/>
        </g>
    </svg>
    """
    encoded_flag = base64.b64encode(flag_svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{encoded_flag}"

def show_aqi_rankings(data):
    try:
        df = pd.DataFrame(data)

        if df.empty:
            st.info("No data available for rankings.")
            return

        most_polluted = df.sort_values(by="AQI", ascending=False).head(10).reset_index(drop=True)
        cleanest = df.sort_values(by="AQI", ascending=True).head(10).reset_index(drop=True)
        
        # Custom CSS for professional styling
        st.markdown("""
        <style>
        .ranking-card {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        
        .ranking-title {
            font-size: 18px;
            font-weight: 600;
            color: #1e3a8a;
            margin-bottom: 5px;
        }
        
        .ranking-subtitle {
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 15px;
        }
        
        .aqi-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 600;
            text-align: center;
            min-width: 40px;
            color: #1f2937;
        }
        
        .flag-icon {
            width: 20px;
            height: 14px;
            margin-right: 8px;
            vertical-align: middle;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get flag image
        flag_img = get_flag_image()
        
        # Use Streamlit columns for layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="ranking-card">', unsafe_allow_html=True)
            st.markdown('<div class="ranking-title">Live most polluted city ranking</div>', unsafe_allow_html=True)
            st.markdown('<div class="ranking-subtitle">Real-time Colorado most polluted city ranking</div>', unsafe_allow_html=True)
            
            # Create a clean dataframe for display
            for i, row in most_polluted.iterrows():
                aqi = row['AQI']
                aqi_color = get_aqi_color(aqi)
                
                # Create a row with flag icon and colored AQI badge
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f3f4f6;">
                    <div style="width: 30px; text-align: left;">{i+1}</div>
                    <div style="flex-grow: 1; display: flex; align-items: center;">
                        <img src="{flag_img}" class="flag-icon">
                        {row['city']} ({row['zip']})
                    </div>
                    <div>
                        <span class="aqi-badge" style="background-color: {aqi_color};">{aqi}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="ranking-card">', unsafe_allow_html=True)
            st.markdown('<div class="ranking-title">Live cleanest city ranking</div>', unsafe_allow_html=True)
            st.markdown('<div class="ranking-subtitle">Real-time Colorado cleanest city ranking</div>', unsafe_allow_html=True)
            
            # Create a clean dataframe for display
            for i, row in cleanest.iterrows():
                aqi = row['AQI']
                aqi_color = get_aqi_color(aqi)
                
                # Create a row with flag icon and colored AQI badge
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f3f4f6;">
                    <div style="width: 30px; text-align: left;">{i+1}</div>
                    <div style="flex-grow: 1; display: flex; align-items: center;">
                        <img src="{flag_img}" class="flag-icon">
                        {row['city']} ({row['zip']})
                    </div>
                    <div>
                        <span class="aqi-badge" style="background-color: {aqi_color};">{aqi}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error displaying rankings: {e}")
        import traceback
        st.text(traceback.format_exc())

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
