import streamlit as st
from config import COLORADO_ZIPS, POLLUTANTS
from data_loader import get_air_quality_data, get_asthma_data, get_map_data
from visualizations import (
    create_aqi_map,
    show_aqi_rankings,
    plot_pollution_trend,
    plot_asthma_vs_pollution
)
import base64

# Page config
st.set_page_config(page_title="Colorado Air & Asthma Tracker", page_icon="🫁", layout="wide")

# Custom CSS for styling - Enhanced for a professional look with updated header
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
        
        /* Remove white strips/boxes */
        .css-18e3th9, .css-1d391kg, .css-12oz5g7, .st-emotion-cache-18e3th9, .st-emotion-cache-1d391kg {
            padding: 0 !important;
            background-color: #f8fafc !important;
        }
        
        /* Ensure consistent background for all elements */
        div[data-testid="stVerticalBlock"] {
            background-color: #f8fafc !important;
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            background-color: #f8fafc;
        }

        h1 {
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
            color: #1e3a8a;
            text-align: center;
        }

        h2 {
            font-weight: 600;
            font-size: 1.8rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #1e3a8a;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.5rem;
            text-align: center;
        }

        h3 {
            font-weight: 600;
            font-size: 1.4rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: #2563eb;
            text-align: center;
        }

        p, li {
            font-size: 1rem;
            line-height: 1.6;
            color: #1f2937;
            text-align: center;
        }
        
        div {
            font-size: 1rem;
            line-height: 1.6;
            color: #1f2937;
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
            text-align: center;
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
            text-align: center;
        }

        /* Footer styling */
        .footer {
            text-align: center;
            padding: 2rem 0;
            font-size: 0.875rem;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
            margin-top: 3rem;
            background-color: #f8fafc;
        }
        
        /* Section card styling - with consistent background */
        .section-card {
            background-color: #ffffff;
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
            transition: transform 0.2s ease-in-out;
            text-align: center;
        }
        
        .section-card:hover {
            transform: translateY(-2px);
        }
        
        /* Updated Navigation bar styling - white background with centered links */
        .nav-container {
            background-color: #ffffff;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .nav-logo {
            width: 32px;
            height: 32px;
            cursor: pointer;
            transition: transform 0.2s;
            color: #2563eb;
        }
        
        .nav-logo:hover {
            transform: scale(1.1);
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
            margin: 0 auto;
        }
        
        .nav-link {
            color: #1f2937;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s;
            padding: 0.5rem 1rem;
        }
        
        .nav-link:hover {
            color: #2563eb;
        }
        
        .nav-link.active {
            color: #2563eb;
            font-weight: 600;
        }
        
        /* Colorful tab navigation inspired by portfolio site */
        .tab-nav {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
            overflow-x: auto;
            padding-bottom: 0.5rem;
            justify-content: center;
        }
        
        .tab-link {
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 500;
            text-decoration: none;
            color: white;
            transition: all 0.2s;
            text-align: center;
            min-width: 100px;
        }
        
        .tab-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .tab-home {
            background-color: #3b82f6;
        }
        
        .tab-about {
            background-color: #8b5cf6;
        }
        
        .tab-data {
            background-color: #10b981;
        }
        
        .tab-resources {
            background-color: #f59e0b;
        }
        
        /* Hero section styling */
        .hero-section {
            background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1519501025264-65ba15a82390?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80');
            background-size: cover;
            background-position: center;
            color: white;
            padding: 4rem 2rem;
            border-radius: 0.75rem;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .hero-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: white;
            text-align: center;
        }
        
        .hero-subtitle {
            font-size: 1.25rem;
            max-width: 700px;
            margin: 0 auto 2rem auto;
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
        }
        
        .hero-button {
            background-color: #2563eb;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s;
        }
        
        .hero-button:hover {
            background-color: #1d4ed8;
            transform: translateY(-2px);
        }
        
        /* About section styling */
        .about-container {
            display: flex;
            gap: 2rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .about-text {
            flex: 2;
            min-width: 300px;
            text-align: center;
        }
        
        .about-skills {
            flex: 1;
            background-color: #f1f5f9;
            padding: 1.5rem;
            border-radius: 0.75rem;
            min-width: 250px;
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
        
        /* PM2.5 info styling - integrated into the UI */
        .pm25-info {
            background-color: #f0f9ff;
            border-left: 4px solid #0ea5e9;
            padding: 0.75rem 1rem;
            border-radius: 0 0.5rem 0.5rem 0;
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #0369a1;
            text-align: center;
        }
        
        /* Fix for Streamlit info box */
        .stAlert {
            background-color: #f0f9ff !important;
            border-left-color: #0ea5e9 !important;
        }
        
        /* Breadcrumb styling */
        .breadcrumb {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
            font-size: 0.875rem;
            justify-content: center;
        }
        
        .breadcrumb-item {
            color: #6b7280;
        }
        
        .breadcrumb-separator {
            margin: 0 0.5rem;
            color: #9ca3af;
        }
        
        .breadcrumb-current {
            color: #2563eb;
            font-weight: 500;
        }
        
        /* Stats counter styling */
        .stats-container {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-item {
            background-color: white;
            border-radius: 0.75rem;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            flex: 1;
            min-width: 150px;
            transition: transform 0.2s;
        }
        
        .stat-item:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #2563eb;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: #6b7280;
        }
    </style>
""", unsafe_allow_html=True)

# Blue lung icon SVG for logo
def get_lung_icon():
    lung_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#2563eb" width="32" height="32">
        <path d="M12 2a1 1 0 0 1 1 1c0 .24-.103.446-.271.623A4.126 4.126 0 0 0 11 7.5V9h1c3.866 0 7 3.134 7 7v5a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-5a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v5a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1v-5c0-3.866 3.134-7 7-7h1V7.5a4.126 4.126 0 0 0-1.729-3.377A1.003 1.003 0 0 1 7 3a1 1 0 0 1 1-1h4zm5.971 16H20v-4c0-3.314-2.686-6-6-6h-1v4.586l3.707-3.707a1 1 0 0 1 1.414 1.414l-5.828 5.828a1 1 0 0 1-1.414 0l-5.828-5.828a1 1 0 0 1 1.414-1.414L10 12.586V8H9c-3.314 0-6 2.686-6 6v4h2.971l.029-4L8 16l-.029 2H10v-5a3 3 0 0 1 3-3h1a3 3 0 0 1 3 3v5h2v-2l2-2v4z"/>
    </svg>
    """
    return lung_svg

# Updated navigation with white background and centered links
st.markdown(f"""
<div class="nav-container">
    <div class="nav-logo" id="home-logo">
        {get_lung_icon()}
    </div>
    <div class="nav-links">
        <a href="#" class="nav-link" id="home-link">Home</a>
        <a href="#" class="nav-link" id="about-link">About</a>
        <a href="#" class="nav-link" id="data-link">Data</a>
        <a href="#" class="nav-link" id="resources-link">Resources</a>
    </div>
    <div style="width: 32px;"></div> <!-- Empty div for balance -->
</div>

<div class="tab-nav">
    <a href="#" class="tab-link tab-home" id="tab-home">Home</a>
    <a href="#" class="tab-link tab-about" id="tab-about">About</a>
    <a href="#" class="tab-link tab-data" id="tab-data">Data</a>
    <a href="#" class="tab-link tab-resources" id="tab-resources">Resources</a>
</div>
""", unsafe_allow_html=True)

# Get the query parameters - Updated to use non-experimental API
query_params = st.query_params
page = query_params.get("page", "home")

# Create tabs for Home and About, but hide the tab bar
tab1, tab2 = st.tabs(["Home", "About"])

# Home page content
with tab1:
    if page == "about":
        # If page is about, we'll show the about content in tab2
        pass
    else:
        # Hero section with Colorado background
        st.markdown(f"""
        <div class="hero-section">
            <h1 class="hero-title">Colorado Air & Asthma Tracker</h1>
            <p class="hero-subtitle">Explore real-time air quality across Colorado and understand its impact on asthma rates. Make informed decisions for your respiratory health.</p>
            <a href="#data" class="hero-button">Explore Data</a>
        </div>
        """, unsafe_allow_html=True)
        
        # Breadcrumb navigation
        st.markdown("""
        <div class="breadcrumb">
            <span class="breadcrumb-item">USA</span>
            <span class="breadcrumb-separator">›</span>
            <span class="breadcrumb-current">Colorado</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats counters
        st.markdown("""
        <div class="stats-container">
            <div class="stat-item">
                <div class="stat-value">471</div>
                <div class="stat-label">Monitoring Stations</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">8.7%</div>
                <div class="stat-label">Avg. Asthma Rate</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">24/7</div>
                <div class="stat-label">Real-time Updates</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">PM2.5</div>
                <div class="stat-label">Primary Pollutant</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Map section
        st.markdown('<div class="section-card" id="data">', unsafe_allow_html=True)
        st.markdown("## Colorado Air Quality Map")
        st.markdown('<p class="caption">Interactive map showing air quality levels across Colorado. Larger circles indicate higher pollution levels. Color indicates AQI category.</p>', unsafe_allow_html=True)

        # Map visualization
        map_data = get_map_data()
        create_aqi_map(map_data)
        st.markdown('</div>', unsafe_allow_html=True)

        # Rankings section
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## Air Quality Rankings")
        st.markdown('<p class="caption">Comparison of the most polluted and cleanest cities in Colorado based on current air quality data.</p>', unsafe_allow_html=True)

        # Rankings visualization
        show_aqi_rankings(map_data)
        st.markdown('</div>', unsafe_allow_html=True)

        # ZIP and pollutant selection
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## Location & Pollutant Selection")
        st.markdown('<p class="caption">Select a specific ZIP code to view detailed air quality data.</p>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            zip_code = st.selectbox("Choose a ZIP Code", COLORADO_ZIPS)
        with col2:
            # Only show PM2.5 as per user request - with improved styling
            pollutant = "PM2.5"
            st.markdown('<div class="pm25-info">Currently focusing on PM2.5 data only</div>', unsafe_allow_html=True)
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
        
        # Footer
        st.markdown("""
        <div class="footer">
            <p>© 2025 Colorado Air & Asthma Tracker | Created by Mateus</p>
            <p>Data sources: AirNow API, CDC Asthma Data</p>
        </div>
        """, unsafe_allow_html=True)

# About page content
with tab2:
    if page == "about":
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

# JavaScript to handle navigation and tab switching
st.markdown("""
<script>
    // Function to show About section
    function showAbout() {
        // Hide all tabs
        const tabs = document.querySelectorAll('.stTabs [data-baseweb="tab-panel"]');
        tabs.forEach(tab => {
            tab.style.display = 'none';
        });
        
        // Show the About tab (second tab)
        tabs[1].style.display = 'block';
        
        // Update active link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.getElementById('about-link').classList.add('active');
        
        // Update tab links
        document.querySelectorAll('.tab-link').forEach(link => {
            link.classList.remove('active');
        });
        document.getElementById('tab-about').classList.add('active');
    }
    
    // Function to show Home section
    function showHome() {
        // Hide all tabs
        const tabs = document.querySelectorAll('.stTabs [data-baseweb="tab-panel"]');
        tabs.forEach(tab => {
            tab.style.display = 'none';
        });
        
        // Show the Home tab (first tab)
        tabs[0].style.display = 'block';
        
        // Update active link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.getElementById('home-link').classList.add('active');
        
        // Update tab links
        document.querySelectorAll('.tab-link').forEach(link => {
            link.classList.remove('active');
        });
        document.getElementById('tab-home').classList.add('active');
    }
    
    // Hide the tab bar
    document.querySelector('.stTabs [data-baseweb="tab-list"]').style.display = 'none';
    
    // Get current page from URL
    const urlParams = new URLSearchParams(window.location.search);
    const currentPage = urlParams.get('page') || 'home';
    
    // Show the appropriate tab based on the URL
    if (currentPage === 'about') {
        showAbout();
    } else {
        showHome();
    }
    
    // Add event listener to home link
    document.getElementById('home-link').addEventListener('click', function(e) {
        e.preventDefault();
        showHome();
    });
    
    // Add event listener to about link
    document.getElementById('about-link').addEventListener('click', function(e) {
        e.preventDefault();
        showAbout();
    });
    
    // Add event listener to data link
    document.getElementById('data-link').addEventListener('click', function(e) {
        e.preventDefault();
        showHome();
        // Scroll to data section
        document.getElementById('data').scrollIntoView({behavior: 'smooth'});
    });
    
    // Add event listener to tab links
    document.getElementById('tab-home').addEventListener('click', function(e) {
        e.preventDefault();
        showHome();
    });
    
    document.getElementById('tab-about').addEventListener('click', function(e) {
        e.preventDefault();
        showAbout();
    });
    
    document.getElementById('tab-data').addEventListener('click', function(e) {
        e.preventDefault();
        showHome();
        // Scroll to data section
        document.getElementById('data').scrollIntoView({behavior: 'smooth'});
    });
    
    // Add event listener to logo for home functionality
    document.getElementById('home-logo').addEventListener('click', function(e) {
        e.preventDefault();
        showHome();
        // Scroll to top
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
    
    // Add active class to current link
    if (currentPage === 'about') {
        document.getElementById('about-link').classList.add('active');
        document.getElementById('tab-about').classList.add('active');
    } else {
        document.getElementById('home-link').classList.add('active');
        document.getElementById('tab-home').classList.add('active');
    }
</script>
""", unsafe_allow_html=True)
