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
