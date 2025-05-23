import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta

# Initialize SQLAlchemy with PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = None
Base = declarative_base()

if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        Session = None
else:
    print("Warning: DATABASE_URL environment variable is not set.")
    Session = None

class Location(Base):
    """Model for storing location information"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    zip_code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    state = Column(String, default="CO")
    
    # Relationships
    air_quality_readings = relationship("AirQualityReading", back_populates="location")
    
    def __repr__(self):
        return f"<Location(zip_code='{self.zip_code}', name='{self.name}')>"

class Pollutant(Base):
    """Model for storing pollutant information"""
    __tablename__ = "pollutants"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # PM2.5, O3, etc.
    full_name = Column(String, nullable=False)  # "Fine Particulate Matter", "Ozone", etc.
    description = Column(String)
    
    # Relationships
    air_quality_readings = relationship("AirQualityReading", back_populates="pollutant")
    
    def __repr__(self):
        return f"<Pollutant(name='{self.name}', full_name='{self.full_name}')>"

class AirQualityReading(Base):
    """Model for storing air quality readings"""
    __tablename__ = "air_quality_readings"
    
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    pollutant_id = Column(Integer, ForeignKey("pollutants.id"), nullable=False)
    date_observed = Column(Date, nullable=False)
    time_observed = Column(DateTime)
    aqi = Column(Integer)  # Air Quality Index
    concentration = Column(Float)  # Concentration value
    units = Column(String)  # Units of measurement (e.g., µg/m³)
    category = Column(String)  # Good, Moderate, etc.
    source = Column(String, default="AirNow API")  # Data source
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    location = relationship("Location", back_populates="air_quality_readings")
    pollutant = relationship("Pollutant", back_populates="air_quality_readings")
    
    def __repr__(self):
        return f"<AirQualityReading(location_id={self.location_id}, pollutant_id={self.pollutant_id}, date_observed='{self.date_observed}', aqi={self.aqi})>"

# Create all tables
def initialize_database():
    """Initialize the database tables"""
    Base.metadata.create_all(engine)

# Functions to interact with the database
def add_or_update_location(zip_code, name, state="CO"):
    """Add a new location or update an existing one"""
    session = Session()
    
    try:
        location = session.query(Location).filter_by(zip_code=zip_code).first()
        
        if not location:
            location = Location(zip_code=zip_code, name=name, state=state)
            session.add(location)
        else:
            # Update name if it's different
            if location.name != name:
                location.name = name
        
        session.commit()
        return location.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_or_update_pollutant(name, full_name, description=None):
    """Add a new pollutant or update an existing one"""
    session = Session()
    
    try:
        pollutant = session.query(Pollutant).filter_by(name=name).first()
        
        if not pollutant:
            pollutant = Pollutant(name=name, full_name=full_name, description=description)
            session.add(pollutant)
        else:
            # Update information if different
            if pollutant.full_name != full_name:
                pollutant.full_name = full_name
            if description and pollutant.description != description:
                pollutant.description = description
        
        session.commit()
        return pollutant.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def store_air_quality_reading(location_id, pollutant_id, date_observed, aqi, concentration=None, 
                             units=None, category=None, time_observed=None, source="AirNow API"):
    """Store a new air quality reading"""
    session = Session()
    
    try:
        # Check if a reading for this location, pollutant, and date already exists
        existing_reading = session.query(AirQualityReading).filter_by(
            location_id=location_id,
            pollutant_id=pollutant_id,
            date_observed=date_observed
        ).first()
        
        if existing_reading:
            # Update the existing reading
            existing_reading.aqi = aqi
            existing_reading.concentration = concentration
            existing_reading.units = units
            existing_reading.category = category
            existing_reading.time_observed = time_observed
            existing_reading.source = source
        else:
            # Create a new reading
            reading = AirQualityReading(
                location_id=location_id,
                pollutant_id=pollutant_id,
                date_observed=date_observed,
                time_observed=time_observed,
                aqi=aqi,
                concentration=concentration,
                units=units,
                category=category,
                source=source
            )
            session.add(reading)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_air_quality_data(zip_codes, start_date=None, end_date=None, pollutant_names=None):
    """
    Retrieve air quality data for specified ZIP codes and date range
    
    Args:
        zip_codes (list): List of ZIP codes to get data for
        start_date (datetime, optional): Start date for data retrieval
        end_date (datetime, optional): End date for data retrieval
        pollutant_names (list, optional): List of pollutant names to filter by
        
    Returns:
        dict: Dictionary with ZIP codes as keys and readings as values
    """
    session = Session()
    
    try:
        # Default to last 7 days if no date range specified
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # Query all matching locations
        locations = session.query(Location).filter(Location.zip_code.in_(zip_codes)).all()
        location_map = {loc.id: loc.zip_code for loc in locations}
        location_ids = list(location_map.keys())
        
        # Query all pollutants if not specified
        if pollutant_names:
            pollutants = session.query(Pollutant).filter(Pollutant.name.in_(pollutant_names)).all()
        else:
            pollutants = session.query(Pollutant).all()
        pollutant_map = {poll.id: poll.name for poll in pollutants}
        pollutant_ids = list(pollutant_map.keys())
        
        # Query readings
        query = session.query(AirQualityReading).filter(
            AirQualityReading.location_id.in_(location_ids),
            AirQualityReading.pollutant_id.in_(pollutant_ids),
            AirQualityReading.date_observed >= start_date,
            AirQualityReading.date_observed <= end_date
        ).order_by(AirQualityReading.date_observed)
        
        readings = query.all()
        
        # Organize results by ZIP code and pollutant
        result = {}
        for zip_code in zip_codes:
            result[zip_code] = {"PM2.5": [], "O3": []}
        
        for reading in readings:
            zip_code = location_map.get(reading.location_id)
            pollutant = pollutant_map.get(reading.pollutant_id)
            
            if zip_code in result and pollutant in ["PM2.5", "O3"]:
                result[zip_code][pollutant].append({
                    "AQI": reading.aqi,
                    "DateObserved": reading.date_observed.strftime("%Y-%m-%d"),
                    "TimeObserved": reading.time_observed.strftime("%H:%M") if reading.time_observed else None,
                    "Category": reading.category,
                    "ParameterName": pollutant
                })
        
        return result
    except Exception as e:
        print(f"Error retrieving air quality data: {e}")
        return {}
    finally:
        session.close()

def get_latest_air_quality(zip_codes, pollutant_names=None):
    """
    Retrieve the latest air quality data for specified ZIP codes
    
    Args:
        zip_codes (list): List of ZIP codes to get data for
        pollutant_names (list, optional): List of pollutant names to filter by
        
    Returns:
        dict: Dictionary with ZIP codes as keys and latest readings as values
    """
    session = Session()
    
    try:
        # Query all matching locations
        locations = session.query(Location).filter(Location.zip_code.in_(zip_codes)).all()
        location_map = {loc.id: loc.zip_code for loc in locations}
        location_ids = list(location_map.keys())
        
        # Query all pollutants if not specified
        if pollutant_names:
            pollutants = session.query(Pollutant).filter(Pollutant.name.in_(pollutant_names)).all()
        else:
            pollutants = session.query(Pollutant).all()
        pollutant_map = {poll.id: poll.name for poll in pollutants}
        pollutant_ids = list(pollutant_map.keys())
        
        # Dictionary to store results
        result = {}
        
        # For each location and pollutant, get the latest reading
        for location_id in location_ids:
            zip_code = location_map[location_id]
            result[zip_code] = {}
            
            for pollutant_id in pollutant_ids:
                pollutant_name = pollutant_map[pollutant_id]
                
                # Only include PM2.5 and O3 in the results
                if pollutant_name not in ["PM2.5", "O3"]:
                    continue
                
                # Get the latest reading for this location and pollutant
                latest = session.query(AirQualityReading).filter(
                    AirQualityReading.location_id == location_id,
                    AirQualityReading.pollutant_id == pollutant_id
                ).order_by(AirQualityReading.date_observed.desc()).first()
                
                if latest:
                    result[zip_code][pollutant_name] = {
                        "AQI": latest.aqi,
                        "DateObserved": latest.date_observed.strftime("%Y-%m-%d"),
                        "TimeObserved": latest.time_observed.strftime("%H:%M") if latest.time_observed else None,
                        "Category": latest.category,
                        "ParameterName": pollutant_name
                    }
        
        return result
    except Exception as e:
        print(f"Error retrieving latest air quality data: {e}")
        return {}
    finally:
        session.close()

def store_api_data(air_quality_data, location_name_map):
    """
    Store air quality data from the API in the database
    
    Args:
        air_quality_data (dict): Dictionary with ZIP codes as keys and readings as values
        location_name_map (dict): Dictionary mapping ZIP codes to location names
    """
    session = Session()
    
    try:
        # Add/update pollutants if needed
        pm25_id = add_or_update_pollutant("PM2.5", "Fine Particulate Matter", 
                                         "Fine particulate matter (PM2.5) consists of tiny particles or droplets in the air that are 2.5 microns or less in width.")
        
        o3_id = add_or_update_pollutant("O3", "Ozone", 
                                       "Ground-level ozone is created by chemical reactions between oxides of nitrogen (NOx) and volatile organic compounds (VOCs) in the presence of sunlight.")
        
        pollutant_map = {"PM2.5": pm25_id, "O3": o3_id}
        
        # Process each location and reading
        for zip_code, pollutant_data in air_quality_data.items():
            # Add/update location
            location_name = location_name_map.get(zip_code, f"Location {zip_code}")
            location_id = add_or_update_location(zip_code, location_name)
            
            # Store readings for each pollutant
            for pollutant_name, reading in pollutant_data.items():
                if pollutant_name in pollutant_map and isinstance(reading, dict) and 'AQI' in reading:
                    # Parse date
                    date_str = reading.get('DateObserved', '').strip()
                    try:
                        date_observed = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except:
                        # If date parsing fails, use current date
                        date_observed = datetime.now().date()
                    
                    # Parse time if available
                    time_observed = None
                    time_str = reading.get('HourObserved')
                    if time_str and date_observed:
                        try:
                            time_observed = datetime.combine(
                                date_observed, 
                                datetime.strptime(str(time_str).zfill(2), '%H').time()
                            )
                        except:
                            pass
                    
                    # Store the reading
                    store_air_quality_reading(
                        location_id=location_id,
                        pollutant_id=pollutant_map[pollutant_name],
                        date_observed=date_observed,
                        time_observed=time_observed,
                        aqi=reading.get('AQI'),
                        concentration=reading.get('Concentration'),
                        units=reading.get('Unit'),
                        category=reading.get('Category')
                    )
    except Exception as e:
        session.rollback()
        print(f"Error storing API data: {e}")
    finally:
        session.close()

# Initialize database when imported
try:
    if DATABASE_URL:
        initialize_database()
except Exception as e:
    print(f"Error initializing database: {e}")