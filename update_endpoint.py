from air_quality_data import get_cached_air_quality_data
from config import COLORADO_ZIPS

import streamlit as st

# Detect if this is a "ping" to update data
query_params = st.experimental_get_query_params()
if "update" in query_params:
    get_cached_air_quality_data(COLORADO_ZIPS)
    st.write("✅ Data updated successfully.")
    st.stop()