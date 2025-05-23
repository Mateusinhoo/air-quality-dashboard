import os

# API configuration
AIRNOW_API_KEY = os.getenv("AIRNOW_API_KEY", "")

# Colorado ZIP codes with their names
# A selection of major Colorado cities/areas
COLORADO_ZIPS = {
    "80202": "Denver Downtown",
    "80246": "Denver East",
    "80301": "Boulder",
    "80903": "Colorado Springs",
    "80521": "Fort Collins",
    "80401": "Golden",
    "81601": "Glenwood Springs",
    "81435": "Telluride",
    "80487": "Steamboat Springs",
    "80621": "Greeley"
}

# Default ZIP codes to display if none selected
DEFAULT_ZIPS = ["80202", "80301", "80903", "80521"]

# AQI Categories and their descriptions
AQI_CATEGORIES = {
    "Good": {
        "range": (0, 50),
        "color": "#00E400",
        "description": "Air quality is satisfactory, and air pollution poses little or no risk."
    },
    "Moderate": {
        "range": (51, 100),
        "color": "#FFFF00",
        "description": "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
    },
    "Unhealthy for Sensitive Groups": {
        "range": (101, 150),
        "color": "#FF7E00",
        "description": "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
    },
    "Unhealthy": {
        "range": (151, 200),
        "color": "#FF0000",
        "description": "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
    },
    "Very Unhealthy": {
        "range": (201, 300),
        "color": "#99004C",
        "description": "Health alert: The risk of health effects is increased for everyone."
    },
    "Hazardous": {
        "range": (301, 500),
        "color": "#7E0023",
        "description": "Health warning of emergency conditions: everyone is more likely to be affected."
    }
}

# Pollutant information
POLLUTANTS = {
    "PM2.5": {
        "name": "Fine Particulate Matter",
        "description": "Fine particulate matter (PM2.5) consists of tiny particles or droplets in the air that are 2.5 microns or less in width. Sources include fires, power plants, and vehicles. It can penetrate deep into the lungs and even enter the bloodstream."
    },
    "O3": {
        "name": "Ozone",
        "description": "Ground-level ozone is created by chemical reactions between oxides of nitrogen (NOx) and volatile organic compounds (VOCs) in the presence of sunlight. It can trigger a variety of health problems, particularly for children, the elderly, and people of all ages who have lung diseases such as asthma."
    }
}
