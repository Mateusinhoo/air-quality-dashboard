import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import COLORADO_ZIPS, AQI_CATEGORIES
from utils import get_aqi_category, get_aqi_color

def plot_aqi_comparison(comparison_data, pollutant):
    """
    Create a bar chart comparing AQI values across ZIP codes for a specific pollutant.
    
    Args:
        comparison_data (pd.DataFrame): Data prepared for comparison
        pollutant (str): Pollutant to visualize (PM2.5 or O3)
        
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if comparison_data.empty:
        return None
    
    # Filter data for the specified pollutant
    filtered_data = comparison_data[comparison_data['Pollutant'] == pollutant].copy()
    
    if filtered_data.empty:
        return None
    
    # Add location names for display
    filtered_data['Location_Name'] = filtered_data['ZIP'].apply(lambda x: f"{x} - {COLORADO_ZIPS.get(x, 'Unknown')}")
    
    # Sort by AQI value
    filtered_data = filtered_data.sort_values('AQI', ascending=False)
    
    # Get colors based on AQI values
    bar_colors = [get_aqi_color(aqi) for aqi in filtered_data['AQI']]
    
    # Create the bar chart
    fig = px.bar(
        filtered_data, 
        x='Location_Name', 
        y='AQI',
        labels={'Location_Name': 'Location', 'AQI': 'Air Quality Index'},
        title=f'Air Quality Index ({pollutant}) Comparison by Location'
    )
    
    # Update marker colors
    fig.update_traces(marker_color=bar_colors)
    
    # Add horizontal lines for AQI category boundaries
    for category, info in AQI_CATEGORIES.items():
        if category != "Good":  # Skip the lowest boundary
            lower_bound = info["range"][0]
            fig.add_shape(
                type="line",
                x0=-0.5,
                y0=lower_bound,
                x1=len(filtered_data) - 0.5,
                y1=lower_bound,
                line=dict(color="rgba(0,0,0,0.3)", width=1, dash="dash"),
            )
            fig.add_annotation(
                x=len(filtered_data) - 0.5,
                y=lower_bound + 5,
                text=category,
                showarrow=False,
                font=dict(size=10),
                xanchor="right"
            )
    
    # Layout improvements
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        margin=dict(t=50, l=50, r=50, b=100)
    )
    
    return fig

def plot_aqi_time_series(time_series_data, selected_zips, pollutant):
    """
    Create a time series plot of AQI values for selected ZIP codes and a specific pollutant.
    
    Args:
        time_series_data (pd.DataFrame): Time series data
        selected_zips (list): ZIP codes to include in the plot
        pollutant (str): Pollutant to visualize (PM2.5 or O3)
        
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if time_series_data.empty:
        return None
    
    # Filter data for the selected pollutant and ZIP codes
    filtered_data = time_series_data[
        (time_series_data['Pollutant'] == pollutant) & 
        (time_series_data['ZIP'].isin(selected_zips))
    ]
    
    if filtered_data.empty:
        return None
    
    # Add location names for display
    filtered_data['Location_Name'] = filtered_data['ZIP'].apply(lambda x: f"{x} - {COLORADO_ZIPS.get(x, 'Unknown')}")
    
    # Create the line chart
    fig = px.line(
        filtered_data, 
        x='Date', 
        y='AQI', 
        color='Location_Name',
        labels={'Date': 'Date', 'AQI': 'Air Quality Index', 'Location_Name': 'Location'},
        title=f'Air Quality Index ({pollutant}) Trend',
        markers=True,
        line_shape='linear'
    )
    
    # Add horizontal regions for AQI categories
    for category, info in AQI_CATEGORIES.items():
        lower, upper = info["range"]
        if category == "Hazardous":
            # For the highest category, extend to a reasonable upper limit
            upper = 500
        
        fig.add_shape(
            type="rect",
            x0=filtered_data['Date'].min(),
            y0=lower,
            x1=filtered_data['Date'].max(),
            y1=upper,
            fillcolor=info["color"],
            opacity=0.15,
            layer="below",
            line_width=0,
        )
    
    # Layout improvements
    fig.update_layout(
        height=500,
        margin=dict(t=50, l=50, r=50, b=50),
        hovermode="x unified"
    )
    
    # Add category labels on the right side
    for category, info in AQI_CATEGORIES.items():
        lower, upper = info["range"]
        middle = (lower + upper) / 2
        fig.add_annotation(
            x=filtered_data['Date'].max(),
            y=middle,
            xref="x",
            yref="y",
            text=category,
            showarrow=False,
            xanchor="left",
            xshift=10,
            font=dict(size=10)
        )
    
    return fig

def create_aqi_indicator(aqi_value, title):
    """
    Create a gauge indicator for AQI value.
    
    Args:
        aqi_value (int): The AQI value to display
        title (str): Title for the gauge
        
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if aqi_value is None:
        return None
    
    category = get_aqi_category(aqi_value)
    color = get_aqi_color(aqi_value)
    
    # Create the gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [0, 300], 'tickwidth': 1},
            'bar': {'color': color},
            'steps': [
                {'range': info['range'], 'color': info['color']} 
                for _, info in AQI_CATEGORIES.items()
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': aqi_value
            }
        }
    ))
    
    # Layout improvements
    fig.update_layout(
        height=200,
        margin=dict(t=50, b=0, l=25, r=25)
    )
    
    return fig
