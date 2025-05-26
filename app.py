import streamlit as st
import base64
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

# Custom CSS for styling - Streamlit-compatible approach
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Base styles */
    html, body, [class*="css"], .stApp {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Reset Streamlit defaults */
    .stApp {
        background-color: #fff;
    }
    
    .css-18e3th9, .css-1d391kg, .css-12oz5g7, .st-emotion-cache-18e3th9, .st-emotion-cache-1d391kg {
        padding: 0 !important;
        background-color: #fff !important;
    }
    
    div[data-testid="stVerticalBlock"] {
        background-color: #fff !important;
    }
    
    .block-container {
        padding-top: 0;
        padding-bottom: 0;
        max-width: 100%;
        margin: 0 auto;
        background-color: #fff;
    }
    
   /* Typography */
    h1 {
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 1rem;
        color: #1E90FF !important;
    }

    h2 {
        font-weight: 600;
        font-size: 2.25rem;
        margin-top: 3rem;
        margin-bottom: 1.5rem;
        color: #1E90FF !important;
        text-align: center;
    }

    h3 {
        font-weight: 600;
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #1E90FF !important;
    }
    
    p, li {
        font-size: 1rem;
        line-height: 1.6;
        color: #212529;
        font-weight: 400;
    }
    
    /* Header styling */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: white;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .logo-container {
        display: flex;
        align-items: center;
    }
    
    .logo-text {
        color: #1E90FF;
        font-weight: 700;
        font-size: 1.5rem;
        margin-left: 0.5rem;
    }
    
    .nav-links {
        display: flex;
        gap: 1.5rem;
    }
    
    .nav-link {
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    
    .nav-link:hover {
        background-color: rgba(30,144,255,0.1);
    }
    
    .nav-home {
        color: #1E90FF;
    }
    
    .nav-about {
        color: #6f42c1;
    }
    
    .nav-data {
        color: #28a745;
    }
    
    .nav-resources {
        color: #fd7e14;
    }
    
    .nav-home:hover {
        color: #fff;
        background-color: #1E90FF;
    }
    
    .nav-about:hover {
        color: #fff;
        background-color: #6f42c1;
    }
    
    .nav-data:hover {
        color: #fff;
        background-color: #28a745;
    }
    
    .nav-resources:hover {
        color: #fff;
        background-color: #fd7e14;
    }
    
    /* Theme toggle */
    .toggle-container {
        display: flex;
        align-items: center;
    }
    
    .toggle-box {
        position: relative;
        width: 60px;
        height: 30px;
    }
    
    .toggle-checkbox {
        opacity: 0;
        width: 0;
        height: 0;
    }
    
    .toggle-label {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: .4s;
        border-radius: 34px;
    }
    
    .toggle-label:before {
        position: absolute;
        content: "";
        height: 22px;
        width: 22px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }
    
    .toggle-checkbox:checked + .toggle-label {
        background-color: #1E90FF;
    }
    
    .toggle-checkbox:checked + .toggle-label:before {
        transform: translateX(30px);
    }
    
    /* Hero section */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 3rem 0;
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1519501025264-65ba15a82390?ixlib=rb-1.2.1&auto=format&fit=crop&w=1200&q=80');
        background-size: cover;
        background-position: center;
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        max-width: 800px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .hero-button {
        background-color: #1E90FF;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 5px;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .hero-button:hover {
        background-color: #0056b3;
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* Stats cards */
    .stats-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        flex: 1;
        min-width: 200px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E90FF;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #6c757d;
        font-weight: 500;
        text-align: center;
    }
    
    /* Section styling */
    .section-title {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1E90FF;
        text-align: center;
    }
    
    .section-subtitle {
        font-size: 1.1rem;
        color: #757575;
        margin-bottom: 2rem;
        text-align: center;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        display: block;
    }
    
    /* Card styling */
    .content-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .content-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* Progress bars */
    .progress-container {
        margin-bottom: 1.5rem;
    }
    
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    
    .progress-name {
        font-weight: 500;
    }
    
    .progress-value {
        font-weight: 600;
        color: #1E90FF;
    }
    
    .progress-bar-bg {
        height: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 5px;
    }
    
    .progress-pm25 {
        width: 65%;
        background-color: #1E90FF;
    }
    
    .progress-24h {
        width: 48%;
        background-color: #1E90FF;
    }
    
    .progress-weekly {
        width: 37%;
        background-color: #1E90FF;
    }
    
    /* Skills progress bars */
    .progress-python {
        width: 90%;
        background-color: #1E90FF;
    }
    
    .progress-dataviz {
        width: 85%;
        background-color: #1E90FF;
    }
    
    .progress-api {
        width: 80%;
        background-color: #1E90FF;
    }
    
    .progress-sql {
        width: 75%;
        background-color: #1E90FF;
    }
    
    .progress-webdev {
        width: 70%;
        background-color: #1E90FF;
    }
    
    /* Timeline */
    .timeline-container {
        position: relative;
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 0;
    }
    
    .timeline-item {
        padding: 1.5rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        position: relative;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .timeline-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .timeline-year {
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        color: #1E90FF;
    }
    
    /* Footer */
    .footer {
        background-color: #f5f5f5;
        padding: 3rem 0;
        margin-top: 3rem;
        text-align: center;
    }
    
    .footer-text {
        color: #757575;
        text-align: center;
    }
    
    /* Utility classes */
    .text-blue {
        color: #1E90FF;
    }
    
    .text-center {
        text-align: center;
    }
    
    .mb-4 {
        margin-bottom: 1.5rem;
    }
    
    /* AQI categories */
    .aqi-category {
        color: #1E90FF;
        font-weight: 500;
    }
    
    /* City names and rankings */
    .city-name, .city-value {
        color: #1E90FF;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    div[data-testid="stToolbar"] {
        visibility: hidden;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    .animate-fadeInUp {
        animation: fadeInUp 1s ease-out;
    }
    
    .animate-fadeIn {
        animation: fadeIn 1s ease-out;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .stats-container {
            flex-direction: column;
        }
        
        .nav-links {
            gap: 0.5rem;
        }
        
        .nav-link {
            padding: 0.25rem 0.5rem;
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header with navigation
st.markdown("""
<div class="header-container">
    <div class="logo-container">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#1E90FF" width="32" height="32">
            <path d="M12 2a1 1 0 0 1 1 1c0 .24-.103.446-.271.623A4.126 4.126 0 0 0 11 7.5V9h1c3.866 0 7 3.134 7 7v5a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-5a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v5a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1v-5c0-3.866 3.134-7 7-7h1V7.5a4.126 4.126 0 0 0-1.729-3.377A1.003 1.003 0 0 1 7 3a1 1 0 0 1 1-1h4z"/>
        </svg>
        <span class="logo-text">Colorado Air & Asthma Tracker</span>
    </div>
    <div class="nav-links">
        <a href="#" class="nav-link nav-home">Home</a>
        <a href="#about" class="nav-link nav-about">About</a>
        <a href="#data" class="nav-link nav-data">Data</a>
        <a href="#resources" class="nav-link nav-resources">Resources</a>
        <div class="toggle-container">
            <div class="toggle-box">
                <input type="checkbox" id="toggle-checkbox" class="toggle-checkbox">
                <label for="toggle-checkbox" class="toggle-label"></label>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">Colorado Air & Asthma Tracker</h1>
    <p class="hero-subtitle">Explore real-time air quality across Colorado and understand its impact on asthma rates. Make informed decisions for your respiratory health.</p>
    <a href="#data" class="hero-button">Explore Data</a>
</div>
""", unsafe_allow_html=True)

# Stats section
st.markdown("""
<div class="stats-container">
    <div class="stat-card">
        <div class="stat-value">471</div>
        <div class="stat-label">Monitoring Stations</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">8.7%</div>
        <div class="stat-label">Avg. Asthma Rate</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">24/7</div>
        <div class="stat-label">Real-time Updates</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">PM2.5</div>
        <div class="stat-label">Primary Pollutant</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Map section
st.markdown("""
    '<div id="data">
    <h2 class="section-title">Colorado Air Quality Map</h2>
    <p class="section-subtitle">Interactive map showing air quality levels across Colorado. Larger circles indicate higher pollution levels. Color indicates AQI category.</p>

# Map section
st.markdown('<div id="data"></div>', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Colorado Air Quality Map</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Interactive map showing air quality levels across Colorado. Larger circles indicate higher pollution levels. Color indicates AQI category.</p>', unsafe_allow_html=True)

# Map visualization
map_data = get_map_data()
create_aqi_map(map_data)

# Rankings section
st.markdown('<h2 class="section-title">Air Quality Rankings</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Comparison of the most polluted and cleanest cities in Colorado based on current air quality data.</p>', unsafe_allow_html=True)

# Rankings visualization
show_aqi_rankings(map_data)

# ZIP and pollutant selection
st.markdown('<h2 class="section-title">Location & Pollutant Selection</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Select a specific ZIP code to view detailed air quality data.</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    zip_code = st.selectbox("Choose a ZIP Code", COLORADO_ZIPS)
with col2:
    # Only show PM2.5 as per user request
    pollutant = "PM2.5"
    st.info("Currently focusing on PM2.5 data only")

# Data fetch
air_data = get_air_quality_data(zip_code, pollutant)
asthma_data = get_asthma_data(zip_code)

# Pollution trend section with progress bars
st.markdown('<h2 class="section-title">Pollution Trend Analysis</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Recent air quality levels for the selected ZIP and pollutant. Interactive and zoomable chart.</p>', unsafe_allow_html=True)

# Add progress bars for pollution levels - Fixed the display issue
st.markdown("""
<div class="content-card">
    <div class="progress-container">
        <div class="progress-label">
            <span class="progress-name">Current PM2.5 Level</span>
            <span class="progress-value">65%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill progress-pm25"></div>
        </div>
    </div>
    
    <div class="progress-container">
        <div class="progress-label">
            <span class="progress-name">24-Hour Average</span>
            <span class="progress-value">48%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill progress-24h"></div>
        </div>
    </div>
    
    <div class="progress-container">
        <div class="progress-label">
            <span class="progress-name">Weekly Average</span>
            <span class="progress-value">37%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill progress-weekly"></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

plot_pollution_trend(air_data, pollutant)

# Asthma correlation section
st.markdown('<h2 class="section-title">Asthma and Pollution Correlation</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">This chart compares recent pollution trends with local asthma rates, showing potential health impacts.</p>', unsafe_allow_html=True)

plot_asthma_vs_pollution(air_data, asthma_data)

# Historical data timeline
st.markdown('<h2 class="section-title">Historical Air Quality Timeline</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Key events and milestones in Colorado\'s air quality history.</p>', unsafe_allow_html=True)

st.markdown("""
<div class="timeline-container">
    <div class="timeline-item">
        <div class="timeline-year">1970</div>
        <p>Clean Air Act established national air quality standards</p>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">1990</div>
        <p>Major amendments to Clean Air Act addressing acid rain and ozone depletion</p>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2008</div>
        <p>Colorado implements stricter emissions standards for vehicles</p>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2019</div>
        <p>Colorado adopts zero-emission vehicle standards</p>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2023</div>
        <p>New monitoring stations installed across the state</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Resources section
st.markdown('<div id="resources"></div>', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Resources & Information</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Helpful resources for understanding air quality and its impact on respiratory health.</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="content-card">
        <h3>Understanding AQI</h3>
        <p>The Air Quality Index (AQI) is a standardized indicator for reporting air quality. It tells you how clean or polluted your air is and what associated health effects might be of concern.</p>
        <ul>
            <li><span class="aqi-category">Good</span> (Green): 0-50</li>
            <li><span class="aqi-category">Moderate</span> (Yellow): 51-100</li>
            <li><span class="aqi-category">Unhealthy for Sensitive Groups</span> (Orange): 101-150</li>
            <li><span class="aqi-category">Unhealthy</span> (Red): 151-200</li>
            <li><span class="aqi-category">Very Unhealthy</span> (Purple): 201-300</li>
            <li><span class="aqi-category">Hazardous</span> (Maroon): 301+</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="content-card">
        <h3>Asthma Management Tips</h3>
        <p>When air quality is poor, consider these strategies to manage asthma symptoms:</p>
        <ul>
            <li>Stay indoors with windows closed</li>
            <li>Use HEPA air purifiers</li>
            <li>Avoid outdoor exercise during high pollution times</li>
            <li>Keep rescue medications accessible</li>
            <li>Follow your asthma action plan</li>
            <li>Stay hydrated</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# About section
st.markdown('<div id="about"></div>', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">About This Project</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Learn more about the creator and the technology behind this air quality tracker.</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="content-card">
        <h3>The Creator</h3>
        <p>My name is Mateus, and I am a pre-med student at the Community College of Denver. I have a passion for both healthcare and programming, and I believe technology can revolutionize how we approach medical challenges.</p>
        <p>Growing up in São Paulo, Brazil, one of the most polluted cities in South America, I experienced firsthand the impact of poor air quality on health. As an asthma sufferer myself, I've always been acutely aware of how environmental factors affect respiratory conditions.</p>
        <p>This personal experience motivated me to create the Colorado Air & Asthma Tracker—a tool that visualizes the relationship between air pollution and asthma rates across Colorado. By making this data accessible and easy to understand, I hope to raise awareness about the importance of air quality for public health.</p>
        <p>My goal is to eventually combine my medical education with programming skills to develop innovative healthcare solutions that can improve people's lives.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="content-card">
        <h3>Technical Skills</h3>
        <div class="progress-container">
            <div class="progress-label">
                <span class="progress-name">Python</span>
                <span class="progress-value">90%</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill progress-python"></div>
            </div>
        </div>
        <div class="progress-container">
            <div class="progress-label">
                <span class="progress-name">Data Visualization</span>
                <span class="progress-value">85%</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill progress-dataviz"></div>
            </div>
        </div>
        <div class="progress-container">
            <div class="progress-label">
                <span class="progress-name">API Integration</span>
                <span class="progress-value">80%</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill progress-api"></div>
            </div>
        </div>
        <div class="progress-container">
            <div class="progress-label">
                <span class="progress-name">SQL</span>
                <span class="progress-value">75%</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill progress-sql"></div>
            </div>
        </div>
        <div class="progress-container">
            <div class="progress-label">
                <span class="progress-name">Web Development</span>
                <span class="progress-value">70%</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill progress-webdev"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="content-card">
    <h3>Project Details</h3>
    <p class="text-center">The Colorado Air & Asthma Tracker uses real-time air quality data from monitoring stations across Colorado and combines it with asthma prevalence statistics. The application focuses specifically on PM2.5 (fine particulate matter), which is one of the most significant air pollutants affecting respiratory health.</p>
    <p class="text-center">Key features of this project include:</p>
    <ul>
        <li>Interactive map showing air quality levels across Colorado</li>
        <li>Real-time rankings of the most polluted and cleanest cities</li>
        <li>Detailed pollution trend analysis for specific ZIP codes</li>
        <li>Correlation visualization between pollution levels and asthma rates</li>
        <li>Historical timeline of air quality milestones</li>
        <li>Resources for understanding and managing asthma</li>
    </ul>
    <p class="text-center">All data is updated in real-time, providing users with the most current information available about air quality in their area and how it might affect respiratory conditions like asthma.</p>
    <p class="text-center">This project represents my commitment to using technology to address important public health issues and make complex data more accessible to everyone.</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p class="footer-text">&copy; 2025 Colorado Air & Asthma Tracker | Created by Mateus</p>
</div>
""", unsafe_allow_html=True)

# Add JavaScript for theme toggle and animations
st.markdown("""
<script>
    // Theme toggle functionality
    const toggleCheckbox = document.getElementById('toggle-checkbox');
    toggleCheckbox.addEventListener('change', function() {
        if(this.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'enabled');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'disabled');
        }
    });
    
    // Check for saved theme preference
    if(localStorage.getItem('darkMode') === 'enabled') {
        toggleCheckbox.checked = true;
        document.body.classList.add('dark-mode');
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
</script>
""", unsafe_allow_html=True)
