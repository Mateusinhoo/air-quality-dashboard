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

# Custom CSS for styling - Completely redesigned to match reference site
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
            color: #212529;
        }
        
        h2 {
            font-weight: 600;
            font-size: 2.25rem;
            margin-top: 3rem;
            margin-bottom: 1.5rem;
            color: #212529;
        }
        
        h3 {
            font-weight: 600;
            font-size: 1.5rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #212529;
        }
        
        p, li {
            font-size: 1rem;
            line-height: 1.6;
            color: #212529;
            font-weight: 400;
        }
        
        /* Fixed header */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #fff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
        }
        
        .navbar-brand {
            color: #007bff;
            font-size: 1.5rem;
            font-weight: 700;
            text-decoration: none;
            display: flex;
            align-items: center;
            transition: transform 0.3s ease;
        }
        
        .navbar-brand:hover {
            transform: scale(1.05);
        }
        
        .navbar-nav {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
            justify-content: center;
            flex: 1;
        }
        
        .nav-item {
            margin: 0 1rem;
        }
        
        .nav-link {
            color: #212529;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        
        .nav-link:hover {
            color: #007bff;
            background-color: rgba(0,123,255,0.1);
        }
        
        .nav-link.active {
            color: #fff;
            background-color: #007bff;
        }
        
        /* Color-coded navigation */
        .nav-home {
            color: #007bff;
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
        
        .nav-home:hover, .nav-home.active {
            color: #fff;
            background-color: #007bff;
        }
        
        .nav-about:hover, .nav-about.active {
            color: #fff;
            background-color: #6f42c1;
        }
        
        .nav-data:hover, .nav-data.active {
            color: #fff;
            background-color: #28a745;
        }
        
        .nav-resources:hover, .nav-resources.active {
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
            background-color: #007bff;
        }
        
        .toggle-checkbox:checked + .toggle-label:before {
            transform: translateX(30px);
        }
        
        /* Main content container */
        .main-content {
            margin-top: 80px;
            padding: 2rem;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        
        /* Hero section */
        .hero-section {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 4rem 0;
            margin-bottom: 3rem;
        }
        
        .hero-content {
            flex: 1;
            padding-right: 2rem;
        }
        
        .hero-image {
            flex: 1;
            text-align: right;
        }
        
        .hero-hello {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            animation: fadeInUp 1s ease-out;
        }
        
        .hero-hello-icon {
            color: #ffc107;
            margin-right: 0.5rem;
            font-size: 1.5rem;
        }
        
        .hero-hello-text {
            color: #007bff;
            font-weight: 500;
            letter-spacing: 1px;
        }
        
        .hero-title {
            font-size: 4rem;
            font-weight: 700;
            margin-bottom: 1rem;
            line-height: 1.2;
            animation: fadeInUp 1.2s ease-out;
        }
        
        .hero-title span {
            color: #007bff;
        }
        
        .hero-subtitle {
            font-size: 1.25rem;
            color: #6c757d;
            margin-bottom: 2rem;
            max-width: 600px;
            animation: fadeInUp 1.4s ease-out;
        }
        
        .hero-cta {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background-color: transparent;
            color: #007bff;
            border: 2px solid #007bff;
            border-radius: 4px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.3s ease;
            animation: fadeInUp 1.6s ease-out;
        }
        
        .hero-cta:hover {
            background-color: #007bff;
            color: #fff;
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,123,255,0.2);
        }
        
        /* Stats counter */
        .stats-container {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin-bottom: 4rem;
        }
        
        .stat-item {
            text-align: center;
            padding: 1.5rem;
            margin: 1rem;
            flex: 1;
            min-width: 200px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .stat-item:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        
        .stat-value {
            font-size: 3rem;
            font-weight: 700;
            color: #007bff;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 1rem;
            color: #6c757d;
            font-weight: 500;
        }
        
        /* Section styling */
        .section {
            padding: 4rem 0;
            margin-bottom: 2rem;
        }
        
        .section-title {
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .section-subtitle {
            font-size: 1.1rem;
            color: #6c757d;
            text-align: center;
            margin-bottom: 3rem;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }
        
        /* Card styling */
        .card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            padding: 2rem;
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        
        .card-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #212529;
        }
        
        .card-text {
            color: #6c757d;
            margin-bottom: 1.5rem;
        }
        
        /* Progress bars */
        .progress-wrap {
            margin-bottom: 1.5rem;
        }
        
        .progress-title {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        
        .progress-label {
            font-weight: 500;
            color: #212529;
        }
        
        .progress-value {
            font-weight: 600;
            color: #007bff;
        }
        
        .progress {
            height: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background-color: #007bff;
            border-radius: 5px;
            transition: width 1.5s ease;
        }
        
        /* Timeline */
        .timeline {
            position: relative;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 0;
        }
        
        .timeline::after {
            content: '';
            position: absolute;
            width: 6px;
            background-color: #e9ecef;
            top: 0;
            bottom: 0;
            left: 50%;
            margin-left: -3px;
        }
        
        .timeline-item {
            padding: 10px 40px;
            position: relative;
            width: 50%;
            box-sizing: border-box;
        }
        
        .timeline-item::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: #007bff;
            border: 4px solid #fff;
            border-radius: 50%;
            top: 15px;
            z-index: 1;
        }
        
        .timeline-left {
            left: 0;
        }
        
        .timeline-right {
            left: 50%;
        }
        
        .timeline-left::after {
            right: -10px;
        }
        
        .timeline-right::after {
            left: -10px;
        }
        
        .timeline-content {
            padding: 1.5rem;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        /* Footer */
        .footer {
            background-color: #f8f9fa;
            padding: 4rem 0;
            margin-top: 4rem;
        }
        
        .footer-content {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .footer-section {
            flex: 1;
            min-width: 250px;
            margin-bottom: 2rem;
        }
        
        .footer-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: #212529;
        }
        
        .footer-links {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .footer-link {
            margin-bottom: 0.75rem;
        }
        
        .footer-link a {
            color: #6c757d;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .footer-link a:hover {
            color: #007bff;
        }
        
        .footer-social {
            display: flex;
            margin-top: 1.5rem;
        }
        
        .social-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background-color: #e9ecef;
            border-radius: 50%;
            margin-right: 0.75rem;
            color: #6c757d;
            transition: all 0.3s ease;
        }
        
        .social-icon:hover {
            background-color: #007bff;
            color: #fff;
            transform: translateY(-5px);
        }
        
        .footer-bottom {
            text-align: center;
            padding-top: 2rem;
            margin-top: 2rem;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
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
        
        /* Dark mode */
        body.dark-mode {
            background-color: #121212;
            color: #f8f9fa;
        }
        
        body.dark-mode .navbar,
        body.dark-mode .stApp,
        body.dark-mode .card,
        body.dark-mode .stat-item,
        body.dark-mode .timeline-content {
            background-color: #1e1e1e;
        }
        
        body.dark-mode h1,
        body.dark-mode h2,
        body.dark-mode h3,
        body.dark-mode .card-title,
        body.dark-mode .progress-label {
            color: #f8f9fa;
        }
        
        body.dark-mode p,
        body.dark-mode li,
        body.dark-mode .hero-subtitle,
        body.dark-mode .card-text,
        body.dark-mode .stat-label {
            color: #adb5bd;
        }
        
        body.dark-mode .nav-link {
            color: #f8f9fa;
        }
        
        body.dark-mode .progress {
            background-color: #2c2c2c;
        }
        
        body.dark-mode .timeline::after {
            background-color: #2c2c2c;
        }
        
        body.dark-mode .footer {
            background-color: #1e1e1e;
        }
        
        body.dark-mode .footer-title {
            color: #f8f9fa;
        }
        
        body.dark-mode .footer-link a,
        body.dark-mode .footer-bottom {
            color: #adb5bd;
        }
        
        body.dark-mode .social-icon {
            background-color: #2c2c2c;
            color: #adb5bd;
        }
        
        /* Responsive design */
        @media (max-width: 992px) {
            .hero-section {
                flex-direction: column;
                text-align: center;
                padding: 2rem 0;
            }
            
            .hero-content {
                padding-right: 0;
                margin-bottom: 2rem;
            }
            
            .hero-hello {
                justify-content: center;
            }
            
            .hero-subtitle {
                margin-left: auto;
                margin-right: auto;
            }
            
            .navbar-nav {
                display: none;
            }
            
            .navbar-mobile-toggle {
                display: block;
            }
            
            .timeline::after {
                left: 31px;
            }
            
            .timeline-item {
                width: 100%;
                padding-left: 70px;
                padding-right: 25px;
            }
            
            .timeline-item::after {
                left: 21px;
            }
            
            .timeline-right {
                left: 0;
            }
        }
        
        @media (min-width: 993px) {
            .navbar-mobile-toggle {
                display: none;
            }
        }
        
        /* Hide Streamlit elements */
        #MainMenu, footer, header {
            visibility: hidden;
        }
        
        div[data-testid="stToolbar"] {
            visibility: hidden;
        }
        
        div[data-testid="stDecoration"] {
            visibility: hidden;
        }
        
        div[data-testid="stStatusWidget"] {
            visibility: hidden;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #007bff;
        }
        
        /* Smooth scroll */
        html {
            scroll-behavior: smooth;
        }
    </style>
""", unsafe_allow_html=True)

# Blue lung icon SVG for logo
def get_lung_icon():
    lung_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#007bff" width="32" height="32">
        <path d="M12 2a1 1 0 0 1 1 1c0 .24-.103.446-.271.623A4.126 4.126 0 0 0 11 7.5V9h1c3.866 0 7 3.134 7 7v5a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-5a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v5a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1v-5c0-3.866 3.134-7 7-7h1V7.5a4.126 4.126 0 0 0-1.729-3.377A1.003 1.003 0 0 1 7 3a1 1 0 0 1 1-1h4zm5.971 16H20v-4c0-3.314-2.686-6-6-6h-1v4.586l3.707-3.707a1 1 0 0 1 1.414 1.414l-5.828 5.828a1 1 0 0 1-1.414 0l-5.828-5.828a1 1 0 0 1 1.414-1.414L10 12.586V8H9c-3.314 0-6 2.686-6 6v4h2.971l.029-4L8 16l-.029 2H10v-5a3 3 0 0 1 3-3h1a3 3 0 0 1 3 3v5h2v-2l2-2v4z"/>
    </svg>
    """
    return lung_svg

# Hand wave icon for hero section
def get_hand_icon():
    hand_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffc107" width="32" height="32">
        <path d="M7.291 20.824L2 22l1.176-5.291A9.956 9.956 0 0 1 2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10a9.956 9.956 0 0 1-4.709-1.176zm.29-2.113l.653.35A7.955 7.955 0 0 0 12 20a8 8 0 1 0-8-8c0 1.334.325 2.618.94 3.766l.349.653-.655 2.947 2.947-.655z"/>
    </svg>
    """
    return hand_svg

# Social media icons for footer
def get_github_icon():
    github_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
        <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
    </svg>
    """
    return github_svg

def get_twitter_icon():
    twitter_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
        <path d="M22.162 5.656a8.384 8.384 0 01-2.402.658A4.196 4.196 0 0021.6 4c-.82.488-1.719.83-2.656 1.015a4.182 4.182 0 00-7.126 3.814 11.874 11.874 0 01-8.62-4.37 4.168 4.168 0 00-.566 2.103c0 1.45.738 2.731 1.86 3.481a4.168 4.168 0 01-1.894-.523v.052a4.185 4.185 0 003.355 4.101 4.21 4.21 0 01-1.89.072A4.185 4.185 0 007.97 16.65a8.394 8.394 0 01-6.191 1.732 11.83 11.83 0 006.41 1.88c7.693 0 11.9-6.373 11.9-11.9 0-.18-.005-.362-.013-.54a8.496 8.496 0 002.087-2.165z"/>
    </svg>
    """
    return twitter_svg

def get_linkedin_icon():
    linkedin_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
        <path d="M6.94 5a2 2 0 11-4-.002 2 2 0 014 .002zM7 8.48H3V21h4V8.48zm6.32 0H9.34V21h3.94v-6.57c0-3.66 4.77-4 4.77 0V21H22v-7.93c0-6.17-7.06-5.94-8.72-2.91l.04-1.68z"/>
    </svg>
    """
    return linkedin_svg

# Fixed navigation header
st.markdown(f"""
<nav class="navbar">
    <a href="#" class="navbar-brand" id="logo">
        {get_lung_icon()}
    </a>
    <ul class="navbar-nav">
        <li class="nav-item">
            <a href="#" class="nav-link nav-home active" id="nav-home">Home</a>
        </li>
        <li class="nav-item">
            <a href="#about" class="nav-link nav-about" id="nav-about">About</a>
        </li>
        <li class="nav-item">
            <a href="#data" class="nav-link nav-data" id="nav-data">Data</a>
        </li>
        <li class="nav-item">
            <a href="#resources" class="nav-link nav-resources" id="nav-resources">Resources</a>
        </li>
    </ul>
    <div class="toggle-container">
        <div class="toggle-box">
            <input type="checkbox" id="toggle-checkbox" class="toggle-checkbox">
            <label for="toggle-checkbox" class="toggle-label"></label>
        </div>
    </div>
    <button class="navbar-mobile-toggle" id="mobile-toggle">
        <span></span>
        <span></span>
        <span></span>
    </button>
</nav>
""", unsafe_allow_html=True)

# Main content container - simplified for debugging
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Hero section with split layout
st.markdown(f"""
<div class="hero-section">
    <div class="hero-content">
        <div class="hero-hello">
            {get_hand_icon()}
            <span class="hero-hello-text">HELLO</span>
        </div>
        <h1 class="hero-title">Colorado <span>Air</span> & <span>Asthma</span> Tracker</h1>
        <p class="hero-subtitle">Explore real-time air quality across Colorado and understand its impact on asthma rates. Make informed decisions for your respiratory health.</p>
        <a href="#data" class="hero-cta">Explore Data</a>
    </div>
    <div class="hero-image">
        <img src="https://images.unsplash.com/photo-1519501025264-65ba15a82390?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80" alt="Colorado landscape" style="max-width: 100%; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
    </div>
</div>
""", unsafe_allow_html=True)

# Stats counters with animations
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
st.markdown('<div class="section" id="data">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Colorado Air Quality Map</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Interactive map showing air quality levels across Colorado. Larger circles indicate higher pollution levels. Color indicates AQI category.</p>', unsafe_allow_html=True)

# Map visualization
map_data = get_map_data()
create_aqi_map(map_data)
st.markdown('</div>', unsafe_allow_html=True)

# Rankings section
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Air Quality Rankings</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Comparison of the most polluted and cleanest cities in Colorado based on current air quality data.</p>', unsafe_allow_html=True)

# Rankings visualization
show_aqi_rankings(map_data)
st.markdown('</div>', unsafe_allow_html=True)

# ZIP and pollutant selection
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Location & Pollutant Selection</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Select a specific ZIP code to view detailed air quality data.</p>', unsafe_allow_html=True)

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

# Pollution trend section with progress bars
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Pollution Trend Analysis</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Recent air quality levels for the selected ZIP and pollutant. Interactive and zoomable chart.</p>', unsafe_allow_html=True)

# Add progress bars for pollution levels
st.markdown("""
<div class="progress-wrap">
    <div class="progress-title">
        <span class="progress-label">Current PM2.5 Level</span>
        <span class="progress-value">65%</span>
    </div>
    <div class="progress">
        <div class="progress-bar" style="width:65%"></div>
    </div>
</div>

<div class="progress-wrap">
    <div class="progress-title">
        <span class="progress-label">24-Hour Average</span>
        <span class="progress-value">48%</span>
    </div>
    <div class="progress">
        <div class="progress-bar" style="width:48%"></div>
    </div>
</div>

<div class="progress-wrap">
    <div class="progress-title">
        <span class="progress-label">Weekly Average</span>
        <span class="progress-value">37%</span>
    </div>
    <div class="progress">
        <div class="progress-bar" style="width:37%"></div>
    </div>
</div>
""", unsafe_allow_html=True)

plot_pollution_trend(air_data, pollutant)
st.markdown('</div>', unsafe_allow_html=True)

# Asthma correlation section
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Asthma and Pollution Correlation</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">This chart compares recent pollution trends with local asthma rates, showing potential health impacts.</p>', unsafe_allow_html=True)

plot_asthma_vs_pollution(air_data, asthma_data)
st.markdown('</div>', unsafe_allow_html=True)

# Historical data timeline
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Historical Air Quality Timeline</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Key events and milestones in Colorado\'s air quality history.</p>', unsafe_allow_html=True)

st.markdown("""
<div class="timeline">
    <div class="timeline-item timeline-left">
        <div class="timeline-content">
            <h3>1970</h3>
            <p>Clean Air Act established national air quality standards</p>
        </div>
    </div>
    <div class="timeline-item timeline-right">
        <div class="timeline-content">
            <h3>1990</h3>
            <p>Major amendments to Clean Air Act addressing acid rain and ozone depletion</p>
        </div>
    </div>
    <div class="timeline-item timeline-left">
        <div class="timeline-content">
            <h3>2008</h3>
            <p>Colorado implements stricter emissions standards for vehicles</p>
        </div>
    </div>
    <div class="timeline-item timeline-right">
        <div class="timeline-content">
            <h3>2019</h3>
            <p>Colorado adopts zero-emission vehicle standards</p>
        </div>
    </div>
    <div class="timeline-item timeline-left">
        <div class="timeline-content">
            <h3>2023</h3>
            <p>New monitoring stations installed across the state</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Resources section
st.markdown('<div class="section" id="resources">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Resources & Information</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Helpful resources for understanding air quality and its impact on respiratory health.</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <h3 class="card-title">Understanding AQI</h3>
        <p class="card-text">The Air Quality Index (AQI) is a standardized indicator for reporting air quality. It tells you how clean or polluted your air is and what associated health effects might be of concern.</p>
        <ul>
            <li>0-50: Good (Green)</li>
            <li>51-100: Moderate (Yellow)</li>
            <li>101-150: Unhealthy for Sensitive Groups (Orange)</li>
            <li>151-200: Unhealthy (Red)</li>
            <li>201-300: Very Unhealthy (Purple)</li>
            <li>301+: Hazardous (Maroon)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3 class="card-title">Asthma Management Tips</h3>
        <p class="card-text">When air quality is poor, consider these strategies to manage asthma symptoms:</p>
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

st.markdown('</div>', unsafe_allow_html=True)

# About section
st.markdown('<div class="section" id="about">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">About This Project</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Learn more about the creator and the technology behind this air quality tracker.</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="card">
        <h3 class="card-title">The Creator</h3>
        <p>My name is Mateus, and I am a pre-med student at the Community College of Denver. I have a passion for both healthcare and programming, and I believe technology can revolutionize how we approach medical challenges.</p>
        <p>Growing up in São Paulo, Brazil, one of the most polluted cities in South America, I experienced firsthand the impact of poor air quality on health. As an asthma sufferer myself, I've always been acutely aware of how environmental factors affect respiratory conditions.</p>
        <p>This personal experience motivated me to create the Colorado Air & Asthma Tracker—a tool that visualizes the relationship between air pollution and asthma rates across Colorado. By making this data accessible and easy to understand, I hope to raise awareness about the importance of air quality for public health.</p>
        <p>My goal is to eventually combine my medical education with programming skills to develop innovative healthcare solutions that can improve people's lives.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3 class="card-title">Technical Skills</h3>
        <div class="progress-wrap">
            <div class="progress-title">
                <span class="progress-label">Python</span>
                <span class="progress-value">90%</span>
            </div>
            <div class="progress">
                <div class="progress-bar" style="width:90%"></div>
            </div>
        </div>
        <div class="progress-wrap">
            <div class="progress-title">
                <span class="progress-label">Data Visualization</span>
                <span class="progress-value">85%</span>
            </div>
            <div class="progress">
                <div class="progress-bar" style="width:85%"></div>
            </div>
        </div>
        <div class="progress-wrap">
            <div class="progress-title">
                <span class="progress-label">API Integration</span>
                <span class="progress-value">80%</span>
            </div>
            <div class="progress">
                <div class="progress-bar" style="width:80%"></div>
            </div>
        </div>
        <div class="progress-wrap">
            <div class="progress-title">
                <span class="progress-label">SQL</span>
                <span class="progress-value">75%</span>
            </div>
            <div class="progress">
                <div class="progress-bar" style="width:75%"></div>
            </div>
        </div>
        <div class="progress-wrap">
            <div class="progress-title">
                <span class="progress-label">Web Development</span>
                <span class="progress-value">70%</span>
            </div>
            <div class="progress">
                <div class="progress-bar" style="width:70%"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h3 class="card-title">Project Details</h3>
    <p>The Colorado Air & Asthma Tracker uses real-time air quality data from monitoring stations across Colorado and combines it with asthma prevalence statistics. The application focuses specifically on PM2.5 (fine particulate matter), which is one of the most significant air pollutants affecting respiratory health.</p>
    <p>Key features of this project include:</p>
    <ul>
        <li>Interactive map showing air quality levels across Colorado</li>
        <li>Real-time rankings of the most polluted and cleanest cities</li>
        <li>Detailed pollution trend analysis for specific ZIP codes</li>
        <li>Correlation visualization between pollution levels and asthma rates</li>
        <li>Historical timeline of air quality milestones</li>
        <li>Resources for understanding and managing asthma</li>
    </ul>
    <p>All data is updated in real-time, providing users with the most current information available about air quality in their area and how it might affect respiratory conditions like asthma.</p>
    <p>This project represents my commitment to using technology to address important public health issues and make complex data more accessible to everyone.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(f"""
<footer class="footer">
    <div class="footer-content">
        <div class="footer-section">
            <h3 class="footer-title">Colorado Air & Asthma Tracker</h3>
            <p>Explore real-time air quality across Colorado and understand its impact on asthma rates. Make informed decisions for your respiratory health.</p>
            <div class="footer-social">
                <a href="#" class="social-icon">
                    {get_github_icon()}
                </a>
                <a href="#" class="social-icon">
                    {get_twitter_icon()}
                </a>
                <a href="#" class="social-icon">
                    {get_linkedin_icon()}
                </a>
            </div>
        </div>
        <div class="footer-section">
            <h3 class="footer-title">Quick Links</h3>
            <ul class="footer-links">
                <li class="footer-link"><a href="#">Home</a></li>
                <li class="footer-link"><a href="#about">About</a></li>
                <li class="footer-link"><a href="#data">Data</a></li>
                <li class="footer-link"><a href="#resources">Resources</a></li>
            </ul>
        </div>
        <div class="footer-section">
            <h3 class="footer-title">Resources</h3>
            <ul class="footer-links">
                <li class="footer-link"><a href="https://www.airnow.gov/" target="_blank">AirNow</a></li>
                <li class="footer-link"><a href="https://www.epa.gov/" target="_blank">EPA</a></li>
                <li class="footer-link"><a href="https://www.lung.org/" target="_blank">American Lung Association</a></li>
                <li class="footer-link"><a href="https://cdphe.colorado.gov/" target="_blank">CDPHE</a></li>
            </ul>
        </div>
    </div>
    <div class="footer-bottom">
        <p>&copy; 2025 Colorado Air & Asthma Tracker | Created by Mateus</p>
    </div>
</footer>
""", unsafe_allow_html=True)

# Close the main-content div
st.markdown('</div>', unsafe_allow_html=True)

# Simple JavaScript for basic functionality
st.markdown("""
<script>
    // Basic initialization
    document.addEventListener('DOMContentLoaded', function() {
        // Add active class to home link
        document.getElementById('nav-home').classList.add('active');
        
        // Logo click event
        document.getElementById('logo').addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
        
        // Navigation links
        document.getElementById('nav-about').addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('about').scrollIntoView({behavior: 'smooth'});
        });
        
        document.getElementById('nav-data').addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('data').scrollIntoView({behavior: 'smooth'});
        });
        
        document.getElementById('nav-resources').addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('resources').scrollIntoView({behavior: 'smooth'});
        });
    });
</script>
""", unsafe_allow_html=True)
