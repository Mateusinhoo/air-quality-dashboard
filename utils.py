import pandas as pd
from datetime import datetime, timedelta
from config import AQI_CATEGORIES

def get_aqi_category(aqi_value):
    """Determine the AQI category based on the numerical value."""
    if aqi_value is None:
        return None
    
    for category, info in AQI_CATEGORIES.items():
        lower, upper = info["range"]
        if lower <= aqi_value <= upper:
            return category
    
    return "Hazardous" if aqi_value > 500 else None

def get_aqi_color(aqi_value):
    """Get the color associated with an AQI value."""
    category = get_aqi_category(aqi_value)
    if category:
        return AQI_CATEGORIES[category]["color"]
    return "#808080"  # Gray for unknown

def format_datetime(dt_str):
    """Format a datetime string for display."""
    if not dt_str:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M %Z")
    except:
        return dt_str

def generate_date_range(days=7):
    """Generate a date range for the past N days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    date_range = []
    current_date = start_date
    
    while current_date <= end_date:
        date_range.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return date_range

def calculate_average_aqi(data):
    """Calculate average AQI values from a dataset."""
    if not data:
        return None
    
    aqi_sum = 0
    count = 0
    
    for entry in data:
        if entry.get('AQI') is not None:
            aqi_sum += entry['AQI']
            count += 1
    
    if count == 0:
        return None
    
    return round(aqi_sum / count)

def prepare_time_series_data(historical_data):
    """Prepare time series data for visualization."""
    if not historical_data:
        return pd.DataFrame()
    
    data_points = []
    
    for zip_code, pollutant_data in historical_data.items():
        for pollutant, readings in pollutant_data.items():
            for reading in readings:
                data_points.append({
                    'ZIP': zip_code,
                    'Pollutant': pollutant,
                    'Date': reading.get('DateObserved', ''),
                    'AQI': reading.get('AQI', None),
                    'Category': get_aqi_category(reading.get('AQI')),
                    'Location': reading.get('ReportingArea', '')
                })
    
    df = pd.DataFrame(data_points)
    
    # Convert Date to datetime if it's not empty
    if not df.empty and 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.sort_values('Date')
    
    return df

def prepare_comparison_data(current_data):
    """Prepare data for ZIP code comparison."""
    if not current_data:
        return pd.DataFrame()
    
    data_points = []
    
    for zip_code, pollutant_data in current_data.items():
        for pollutant, reading in pollutant_data.items():
            data_points.append({
                'ZIP': zip_code,
                'Pollutant': pollutant,
                'AQI': reading.get('AQI', None),
                'Category': get_aqi_category(reading.get('AQI')),
                'Location': reading.get('ReportingArea', '')
            })
    
    return pd.DataFrame(data_points)
