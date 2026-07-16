import streamlit as st

def set_page_config(page_title: str, layout: str = "wide"):
    """
    Sets the standard page configuration and injects the global styling.
    """
    st.set_page_config(
        page_title=f"{page_title} - AI Rainfall Prediction",
        page_icon="🌤️",
        layout=layout,
        initial_sidebar_state="collapsed"
    )
    inject_custom_css()

def inject_custom_css():
    """
    Injects custom CSS to override Streamlit defaults and enforce
    the clean light sky blue weather theme.
    """
    custom_css = """
    <style>
        /* Import Outfit or Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        /* Global Page Adjustments */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Outfit', sans-serif !important;
            background: linear-gradient(135deg, #EBF3FA 0%, #FFFFFF 100%) !important;
            color: #2C3E50 !important;
        }
        
        /* Hide Default Footer and Header */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* Top spacing correction */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* Title styling */
        h1, h2, h3, h4, h5, h6 {
            color: #005580 !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
        }
        
        /* Custom Weather Card Styling */
        .weather-card {
            background-color: #FFFFFF !important;
            border-radius: 16px !important;
            padding: 1.25rem !important;
            border: 1px solid #E1EDF5 !important;
            box-shadow: 0 8px 24px rgba(0, 136, 204, 0.04) !important;
            margin-bottom: 1rem !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .weather-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 30px rgba(0, 136, 204, 0.07) !important;
        }
        
        /* Result card header highlight */
        .result-highlight {
            background: linear-gradient(to right, #F0F8FF, #FFFFFF) !important;
            border-left: 6px solid #0088cc !important;
        }
        
        /* Weather KPI numbers */
        .weather-metric-value {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #0088cc !important;
            margin: 0.2rem 0 !important;
        }
        .weather-metric-label {
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            color: #7F8C8D !important;
        }
        
        /* Blue Accent Pill */
        .blue-pill {
            background-color: #E6F4FC !important;
            color: #0088cc !important;
            padding: 4px 12px !important;
            border-radius: 20px !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            display: inline-block !important;
        }
        
        /* Dynamic Falling Rain CSS Animation */
        .rain-container {
            position: relative;
            width: 100%;
            height: 60px;
            overflow: hidden;
            margin-top: 10px;
            border-radius: 8px;
            background: rgba(235, 243, 250, 0.5);
        }
        .rain-drop {
            position: absolute;
            width: 2px;
            height: 12px;
            background: linear-gradient(transparent, #0088cc);
            animation: fall 1.1s linear infinite;
        }
        @keyframes fall {
            0% {
                transform: translateY(-20px);
                opacity: 0;
            }
            50% {
                opacity: 0.6;
            }
            100% {
                transform: translateY(60px);
                opacity: 0;
            }
        }
        
        /* Drifting Clouds Animation */
        .cloud-drift-container {
            width: 100%;
            height: 100px;
            position: relative;
            overflow: hidden;
            background: linear-gradient(to bottom, #A1C4FD 0%, #C2E9FB 100%);
            border-radius: 16px;
            margin-bottom: 1.5rem;
        }
        .drifting-cloud {
            position: absolute;
            background: rgba(255, 255, 255, 0.85);
            border-radius: 100px;
            animation: drift 25s linear infinite;
        }
        .cloud-1 {
            width: 60px;
            height: 22px;
            top: 15px;
            left: -100px;
            animation-duration: 32s;
        }
        .cloud-2 {
            width: 100px;
            height: 30px;
            top: 40px;
            left: -150px;
            animation-duration: 18s;
            animation-delay: 4s;
        }
        .cloud-3 {
            width: 50px;
            height: 16px;
            top: 65px;
            left: -80px;
            animation-duration: 25s;
            animation-delay: 2s;
        }
        @keyframes drift {
            0% { left: -150px; }
            100% { left: 100%; }
        }
        
        /* Weather Category Cards colors */
        .cat-low { border-left: 5px solid #2ecc71 !important; }
        .cat-mod { border-left: 5px solid #3498db !important; }
        .cat-heavy { border-left: 5px solid #e67e22 !important; }
        .cat-vheavy { border-left: 5px solid #e74c3c !important; }
        
        /* Custom Header layout spacing */
        .weather-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: #FFFFFF;
            padding: 0.8rem 1.5rem;
            border-radius: 14px;
            border: 1px solid #E1EDF5;
            box-shadow: 0 4px 15px rgba(0, 136, 204, 0.02);
            margin-bottom: 1.5rem;
        }
        
        .weather-logo {
            font-size: 1.8rem;
            margin-right: 0.5rem;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_weather_kpi(label: str, value: str, icon: str = "☁️", category_class: str = ""):
    """
    Renders a custom styled weather card metric.
    """
    st.markdown(f"""
    <div class="weather-card {category_class}">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div class="weather-metric-label">{label}</div>
            <div style="font-size: 1.3rem;">{icon}</div>
        </div>
        <div class="weather-metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def render_rain_animation():
    """
    Renders a simple HTML rain animation inside Streamlit.
    """
    import random
    drops_html = ""
    for i in range(12):
        left_pos = random.randint(5, 95)
        anim_delay = random.uniform(0.1, 1.2)
        anim_duration = random.uniform(0.7, 1.2)
        drops_html += f'<div class="rain-drop" style="left: {left_pos}%; animation-delay: {anim_delay}s; animation-duration: {anim_duration}s;"></div>'
        
    st.markdown(f"""
    <div class="rain-container">
        {drops_html}
    </div>
    """, unsafe_allow_html=True)

def render_weather_header(subdivision_name: str, today_str: str):
    """
    Renders a commercial weather header with Dynamic info and simulated Light theme.
    """
    st.markdown(f"""
    <div class="weather-header">
        <div style="display: flex; align-items: center;">
            <span class="weather-logo">🌦️</span>
            <div>
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #005580;">AI Rainfall Prediction</h3>
                <span style="font-size: 0.75rem; color: #7F8C8D;">Real-Time Climate Forecasting Platform</span>
            </div>
        </div>
        <div style="text-align: right; display: flex; align-items: center; gap: 1.5rem;">
            <div>
                <div style="font-size: 0.8rem; color: #7F8C8D; font-weight: 500;">Search Location</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: #005580;">📍 {subdivision_name}</div>
            </div>
            <div>
                <div style="font-size: 0.8rem; color: #7F8C8D; font-weight: 500;">Current Date</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: #005580;">📅 {today_str}</div>
            </div>
            <div style="padding-left: 0.5rem; border-left: 1px solid #E1EDF5;">
                <span class="blue-pill" style="font-size: 0.75rem;">🌤️ Light Theme</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
