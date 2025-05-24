import pandas as pd
import datetime

def get_air_quality_data(zip_code, pollutant):
    # Fake/mock data until API integration
    dates = pd.date_range(end=datetime.date.today(), periods=7)
    values = [round(20 + i * 2.5, 1) for i in range(7)]
    return pd.DataFrame({"Date": dates, "Value": values})

def get_asthma_data(zip_code):
    # Fake/mock data until CSV integration
    return pd.DataFrame({"Zip": [zip_code], "Asthma Rate": [12.3]})
