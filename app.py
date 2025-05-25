import streamlit as st
from config import COLORADO_ZIPS, POLLUTANTS
from data_loader import get_air_quality_data, get_asthma_data, get_map_data
from visualizations import (
    create_aqi_map,
    show_aqi_rankings,
    plot_pollution_trend,
    plot_asthma_vs_pollution
)

# Page config
st.set_page_config(page_title="Colorado Air & Asthma Tracker", page_icon="🫁", layout="wide")

# Custom CSS for styling - Enhanced for a clean, professional look with consistent background
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Set consistent background color for the entire page */
        .stApp {
            background-color: #f8fafc;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
            color: #1e3a8a;
        }

        h2 {
            font-weight: 600;
            font-size: 1.8rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #1e3a8a;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.5rem;
        }

        h3 {
            font-weight: 600;
            font-size: 1.4rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: #2563eb;
        }

        p, li, div {
            font-size: 1rem;
            line-height: 1.6;
            color: #4b5563;
        }

        .stMetric {
            border: 1px solid #e5e7eb;
            padding: 1.5rem;
            border-radius: 0.75rem;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            text-align: center;
        }

        /* Card styling for sections - with consistent background */
        .card {
            background-color: #ffffff;
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }

        /* Button styling */
        .stButton button {
            background-color: #2563eb;
            color: white;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
            border: none;
        }

        /* Selectbox styling */
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 0.5rem;
            border: 1px solid #e5e7eb;
        }

        /* Radio button styling */
        .stRadio [role="radiogroup"] {
            padding: 0.5rem;
            background-color: #f9fafb;
            border-radius: 0.5rem;
        }

        /* Separator styling */
        hr {
            margin-top: 2rem;
            margin-bottom: 2rem;
            border: 0;
            height: 1px;
            background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0));
        }

        /* Caption styling */
        .caption {
            font-size: 0.875rem;
            color: #6b7280;
            font-style: italic;
            margin-bottom: 1rem;
        }

        /* Footer styling */
        .footer {
            text-align: center;
            padding: 2rem 0;
            font-size: 0.875rem;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
            margin-top: 3rem;
        }
        
        /* Section card styling - with consistent background */
        .section-card {
            background-color: #ffffff;
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
        }
        
        /* Navigation bar styling */
        .nav-container {
            background-color: #1e3a8a;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
            margin-bottom: 2rem;
            border-radius: 0.5rem;
        }
        
        .nav-title {
            font-weight: 700;
            font-size: 1.5rem;
            color: white;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            transition: background-color 0.2s;
        }
        
        .nav-link:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .nav-link.active {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        /* About section styling */
        .about-container {
            display: flex;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .about-text {
            flex: 2;
        }
        
        .about-skills {
            flex: 1;
            background-color: #f1f5f9;
            padding: 1.5rem;
            border-radius: 0.75rem;
        }
        
        .skill-item {
            display: flex;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        
        .skill-dot {
            width: 10px;
            height: 10px;
            background-color: #2563eb;
            border-radius: 50%;
            margin-right: 0.75rem;
        }
    </style>
""", unsafe_allow_html=True)

# Navigation
st.markdown("""
<div class="nav-container">
    <div class="nav-title">Colorado Air & Asthma Tracker</div>
    <div class="nav-links">
        <a href="?page=home" class="nav-link active" id="home-link">Home</a>
        <a href="?page=about" class="nav-link" id="about-link">About</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Get the query parameters - Updated to use non-experimental API
query_params = st.query_params
page = query_params.get("page", "home")

# Home page content
if page == "home":
    # Title and intro
    st.markdown("# Colorado Air & Asthma Tracker")
    st.markdown("Explore real-time air quality across Colorado ZIP codes and how it correlates with asthma.")

    # Map section
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("## Colorado Air Quality Map")
    st.markdown('<p class="caption">Interactive map showing air quality levels across Colorado. Larger circles indicate higher pollution levels.</p>', unsafe_allow_html=True)

    # Map visualization
    map_data = get_map_data()
    create_aqi_map(map_data)
    st.markdown('</div>', unsafe_allow_html=True)

    # Rankings section
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("## Air Quality Rankings")
    st.markdown('<p class="caption">Comparison of the most polluted and cleanest ZIP codes in Colorado based on current air quality data.</p>', unsafe_allow_html=True)

    # Rankings visualization
    show_aqi_rankings(map_data)
    st.markdown('</div>', unsafe_allow_html=True)

    # ZIP and pollutant selection
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("## Location & Pollutant Selection")
    st.markdown('<p class="caption">Select a specific ZIP code and pollutant type to view detailed data.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        zip_code = st.selectbox("Choose a ZIP Code", COLORADO_ZIPS)
    with col2:
        # Only show PM2.5 as per user request
        pollutant = "PM2.5"
        st.info("Currently focusing on PM2.5 data only")
    st.markdown('</div>', unsafe_allow_html=True)

    # Data fetch
    air_data = get_air_quality_data(zip_code, pollutant)
    asthma_data = get_asthma_data(zip_code)

    # Pollution trend section
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("## Pollution Trend Analysis")
    st.markdown('<p class="caption">Recent air quality levels for the selected ZIP and pollutant. Interactive and zoomable chart.</p>', unsafe_allow_html=True)

    plot_pollution_trend(air_data, pollutant)
    st.markdown('</div>', unsafe_allow_html=True)

    # Asthma correlation section
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("## Asthma and Pollution Correlation")
    st.markdown('<p class="caption">This chart compares recent pollution trends with local asthma rates, showing potential health impacts.</p>', unsafe_allow_html=True)

    plot_asthma_vs_pollution(air_data, asthma_data)
    st.markdown('</div>', unsafe_allow_html=True)

# About page content
elif page == "about":
    st.markdown("# About This Project")
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="about-container">', unsafe_allow_html=True)
    
    # About text section
    st.markdown('<div class="about-text">', unsafe_allow_html=True)
    st.markdown("## The Creator")
    st.markdown("""
    My name is Mateus, and I am a pre-med student at the Community College of Denver. I have a passion for both healthcare and programming, and I believe technology can revolutionize how we approach medical challenges.
    
    Growing up in São Paulo, Brazil, one of the most polluted cities in South America, I experienced firsthand the impact of poor air quality on health. As an asthma sufferer myself, I've always been acutely aware of how environmental factors affect respiratory conditions.
    
    This personal experience motivated me to create the Colorado Air & Asthma Tracker—a tool that visualizes the relationship between air pollution and asthma rates across Colorado. By making this data accessible and easy to understand, I hope to raise awareness about the importance of air quality for public health.
    
    My goal is to eventually combine my medical education with programming skills to develop innovative healthcare solutions that can improve people's lives.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Skills section
    st.markdown('<div class="about-skills">', unsafe_allow_html=True)
    st.markdown("## Technical Skills")
    
    st.markdown("""
    This project was built entirely by me using:
    
    <div class="skill-item"><div class="skill-dot"></div>Python (Streamlit, Pandas, Plotly)</div>
    <div class="skill-item"><div class="skill-dot"></div>SQL for data management</div>
    <div class="skill-item"><div class="skill-dot"></div>API integration (AirNow, CDC)</div>
    <div class="skill-item"><div class="skill-dot"></div>Data visualization</div>
    <div class="skill-item"><div class="skill-dot"></div>Geospatial mapping</div>
    <div class="skill-item"><div class="skill-dot"></div>Statistical analysis</div>
    <div class="skill-item"><div class="skill-dot"></div>Responsive web design</div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Project details
    st.markdown("## Project Details")
    st.markdown("""
    The Colorado Air & Asthma Tracker uses real-time air quality data from monitoring stations across Colorado and combines it with asthma prevalence statistics. The application focuses specifically on PM2.5 (fine particulate matter), which is one of the most significant air pollutants affecting respiratory health.
    
    Key features of this project include:
    
    - Interactive map showing air quality levels across Colorado
    - Real-time rankings of the most polluted and cleanest cities
    - Detailed pollution trend analysis for specific ZIP codes
    - Correlation visualization between pollution levels and asthma rates
    
    All data is updated in real-time, providing users with the most current information available about air quality in their area and how it might affect respiratory conditions like asthma.
    
    This project represents my commitment to using technology to address important public health issues and make complex data more accessible to everyone.
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# JavaScript to handle navigation
st.markdown("""
<script>
    // Get current page from URL
    const urlParams = new URLSearchParams(window.location.search);
    const currentPage = urlParams.get('page') || 'home';
    
    // Update active link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.getElementById(currentPage + '-link').classList.add('active');
</script>
""", unsafe_allow_html=True)

# Enhanced footer
st.markdown("""
<div class="footer">
    <div>
        <strong>Data Sources:</strong> AirNow API & CDC Asthma Data | 
        <strong>Updated:</strong> Real-time | 
        <strong>Coverage:</strong> Colorado ZIP Codes
    </div>
    <div style="margin-top: 0.5rem;">
        Built for Colorado • Powered by Streamlit • © 2025
    </div>
</div>
""", unsafe_allow_html=True)
