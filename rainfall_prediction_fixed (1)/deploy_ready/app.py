import streamlit as st
import os
import sys
import pandas as pd
import numpy as np
import random
import time
from datetime import datetime

# Ensure parent directory is in path for imports
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from utils.helper import set_page_config, render_weather_header, render_weather_kpi, render_rain_animation
from utils.visualization import (
    plot_monthly_bar,
    plot_monthly_line,
    plot_monthly_area,
    plot_annual_gauge,
    plot_rainfall_dist
)
from predict import Predictor

# Initialize page configuration and theme styles
set_page_config("AI Weather Predictions", layout="wide")

# Cached loader for the pre-trained forecasting engine
@st.cache_resource
def get_forecasting_engine():
    return Predictor()

@st.cache_data
def load_historical_data():
    dataset_path = os.path.join(BASE_DIR, "dataset", "rainfall.csv")
    if os.path.exists(dataset_path):
        return pd.read_csv(dataset_path)
    return None

# Load components (wrapped so any failure is visible in the app instead of a
# blank/redacted crash on Streamlit Cloud)
try:
    predictor = get_forecasting_engine()
except Exception as e:
    st.error(
        f"Failed to load the prediction model: {e}\n\n"
        "This usually means the scikit-learn version installed on the server "
        "doesn't match the version the .pkl files were trained with (this "
        "project's models were trained with scikit-learn 1.7.2 — see "
        "requirements.txt). Check 'Manage app' → logs for the pinned "
        "version actually installed."
    )
    st.stop()

try:
    df_historical = load_historical_data()
except Exception as e:
    st.error(f"Failed to load the historical dataset: {e}")
    df_historical = None

# Monthly constants
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# Determine subdivisions
if df_historical is not None:
    subdivisions = sorted(df_historical["SUBDIVISION"].unique())
else:
    subdivisions = ["ANDAMAN & NICOBAR ISLANDS", "KERALA", "PUNJAB", "KONKAN & GOA"]

# Initialize Session State variables
if "history" not in st.session_state:
    st.session_state["history"] = []

# Initialize session state for inputs to allow Resets and Sample loads
for m in MONTHS:
    key = f"{m.lower()}_val"
    if key not in st.session_state:
        st.session_state[key] = 0.0

if "selected_sub" not in st.session_state:
    st.session_state["selected_sub"] = subdivisions[0]

if "selected_yr" not in st.session_state:
    st.session_state["selected_yr"] = 2026

# Render commercial weather app header
today_str = datetime.now().strftime("%B %d, %Y")
render_weather_header(st.session_state["selected_sub"], today_str)

# Layout
col_form, col_weather = st.columns([1.6, 1.4])

with col_form:
    st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
    st.write("### 🌦️ Input Rainfall Observations")
    
    # Subdivision and Year Selection
    col_sub, col_year = st.columns(2)
    with col_sub:
        selected_subdivision = st.selectbox(
            "Target Subdivision / Region", 
            subdivisions, 
            key="sub_dropdown"
        )
        # Sync state
        st.session_state["selected_sub"] = selected_subdivision
        
    with col_year:
        selected_year = st.number_input(
            "Forecast Target Year", 
            min_value=1901, 
            max_value=2050, 
            value=st.session_state["selected_yr"], 
            step=1,
            key="year_box"
        )
        st.session_state["selected_yr"] = selected_year
        
    st.write("---")
    st.write("#### Monthly Precipitation Readings (mm)")
    
    # Arrange month input sliders in columns
    cols = st.columns(3)
    for i, m in enumerate(MONTHS):
        col_idx = i % 3
        with cols[col_idx]:
            key = f"{m.lower()}_val"
            # Monsoons have higher limits
            max_limit = 1500.0 if m in ["JUN", "JUL", "AUG", "SEP"] else 500.0
            st.slider(
                label=m,
                min_value=0.0,
                max_value=max_limit,
                key=key,
                step=1.0,
                format="%.1f"
            )
            
    st.write("<br>", unsafe_allow_html=True)
    
    # Form Action Buttons
    btn_predict, btn_sample, btn_reset = st.columns(3)
    
    with btn_sample:
        if st.button("📥 Load Sample Data", use_container_width=True):
            if df_historical is not None:
                sub_rows = df_historical[df_historical["SUBDIVISION"] == selected_subdivision]
                if not sub_rows.empty:
                    random_row = sub_rows.sample(1).iloc[0]
                    st.session_state["year_box"] = int(random_row["YEAR"])
                    st.session_state["selected_yr"] = int(random_row["YEAR"])
                    for m in MONTHS:
                        st.session_state[f"{m.lower()}_val"] = float(random_row[m])
                    st.success(f"Loaded historical record from year {int(random_row['YEAR'])}")
                    st.rerun()
                else:
                    st.warning("No sample entries found for this subdivision.")
            else:
                st.warning("Historical dataset is missing.")
                
    with btn_reset:
        if st.button("🔄 Reset Observations", use_container_width=True):
            for m in MONTHS:
                st.session_state[f"{m.lower()}_val"] = 0.0
            st.success("Observations reset to 0.0 mm.")
            st.rerun()
            
    with btn_predict:
        predict_clicked = st.button("🔮 Predict Rainfall", type="primary", use_container_width=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

# Process prediction inputs
monthly_vals = [st.session_state[f"{m.lower()}_val"] for m in MONTHS]
sum_inputs = sum(monthly_vals)

with col_weather:
    st.markdown("<div class='weather-card' style='height: 100%;'>", unsafe_allow_html=True)
    st.write("### 🌩️ Weather Forecast Analysis")
    
    prediction_result = None
    
    if predict_clicked:
        # Input validation
        if sum_inputs <= 0.0:
            st.error("Validation Error: Please enter rainfall values greater than 0.0 mm before predicting.")
        else:
            # Loading & Progress UI Experience
            progress_container = st.empty()
            with progress_container.container():
                st.write("Calculating regional precipitation levels...")
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.006)  # Simulated real-time calculation delay
                    progress_bar.progress(percent_complete + 1)
            progress_container.empty()
            
            # Perform prediction
            try:
                # predictor.predict returns a dict: predicted_annual, category, confidence, etc.
                res = predictor.predict(selected_subdivision, selected_year, monthly_vals)
                prediction_result = res
                
                # Append to history state
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state["history"].append({
                    "Timestamp": now_str,
                    "Subdivision": selected_subdivision,
                    "Year": selected_year,
                    "Predicted Annual Rainfall (mm)": round(res["predicted_annual"], 1),
                    "Rainfall Category": res["category"]
                })
                
                st.success("Successfully generated annual rainfall forecast!")
            except Exception as e:
                st.error(f"Error computing prediction: {e}")
                
    # Display results
    if prediction_result is not None:
        res = prediction_result
        
        # Color coding and icons matching category
        cat_classes = {
            "Low Rainfall": "cat-low",
            "Moderate Rainfall": "cat-mod",
            "Heavy Rainfall": "cat-heavy",
            "Very Heavy Rainfall": "cat-vheavy"
        }
        cat_icons = {
            "Low Rainfall": "☀️",
            "Moderate Rainfall": "☁️",
            "Heavy Rainfall": "🌧️",
            "Very Heavy Rainfall": "🌩️"
        }
        
        cat_class = cat_classes.get(res["category"], "")
        cat_icon = cat_icons.get(res["category"], "☁️")
        
        # Main Prediction Card (HTML style)
        st.markdown(f"""
        <div class="weather-card result-highlight {cat_class}">
            <div style="font-size: 0.85rem; text-transform: uppercase; color: #7F8C8D;">Predicted Annual Rainfall</div>
            <div style="font-size: 2.8rem; font-weight: 700; color: #0088cc; margin: 0.2rem 0;">{res['predicted_annual']:.1f} <span style="font-size: 1.5rem; font-weight: 500;">mm</span></div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem;">
                <span style="font-size: 1.3rem;">{cat_icon}</span>
                <span style="font-weight: 600; color: #2C3E50;">{res['category']}</span>
                <span class="blue-pill" style="margin-left: auto;">Confidence: {res['confidence']:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Natural Language AI Summary
        st.write("#### 💬 AI Weather Summary")
        
        # Dynamic Monsoon Description based on category
        if res["category"] == "Low Rainfall":
            monsoon_desc = "drier or semi-arid conditions. Such rainfall generally supports low-water requirement crops (like millets or pulses) and requires efficient irrigation planning."
        elif res["category"] == "Moderate Rainfall":
            monsoon_desc = "standard seasonal weather. Such rainfall generally supports moderate monsoon conditions and is highly suitable for diverse crops like wheat, maize, and mustard."
        elif res["category"] == "Heavy Rainfall":
            monsoon_desc = "strong monsoon conditions. Such rainfall generally supports heavy monsoon cycles and is highly favorable for seasonal crops like rice, jute, and sugarcane."
        else:
            monsoon_desc = "extreme monsoon cycles. Such rainfall generally supports very heavy monsoon conditions and might pose temporary flood watch warnings, but provides abundant water storage."
            
        summary_text = f"Based on the rainfall values entered for **{selected_subdivision}** in the year **{selected_year}**, the predicted annual rainfall is **{res['predicted_annual']:.1f} mm**. This indicates a **{res['category']}** region. Such rainfall generally supports {monsoon_desc}"
        
        st.markdown(f"""
        <div style="background-color: #F8FBFD; border: 1px solid #E1EDF5; border-radius: 12px; padding: 1rem; font-size: 0.95rem; line-height: 1.5; color: #34495E; margin-bottom: 1rem;">
            {summary_text}
        </div>
        """, unsafe_allow_html=True)
        
        render_rain_animation()
        
    else:
        st.info("👈 Enter monthly observations on the left and click 'Predict Rainfall' to generate the forecast cards.")
        st.write("<br><br>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

# Predictions Insights & Charts Section (shows after prediction)
if prediction_result is not None:
    st.write("---")
    st.write("### 📊 Prediction Insights & Dynamic Visualizations")
    
    # Calculate Insights
    max_idx = int(np.argmax(monthly_vals))
    min_idx = int(np.argmin(monthly_vals))
    wettest_month = MONTHS[max_idx]
    driest_month = MONTHS[min_idx]
    avg_monthly = sum_inputs / 12.0
    
    # Calculate seasonal totals
    winter_total = monthly_vals[0] + monthly_vals[1]
    summer_total = monthly_vals[2] + monthly_vals[3] + monthly_vals[4]
    monsoon_total = monthly_vals[5] + monthly_vals[6] + monthly_vals[7] + monthly_vals[8]
    post_monsoon_total = monthly_vals[9] + monthly_vals[10] + monthly_vals[11]
    
    # Determine seasonal trend
    if sum_inputs > 0:
        if monsoon_total / sum_inputs > 0.60:
            seasonal_trend = "Monsoon Dominant 🌧️"
        elif summer_total / sum_inputs > 0.40:
            seasonal_trend = "Summer Shower Focus ☀️"
        elif winter_total / sum_inputs > 0.40:
            seasonal_trend = "Winter Focus ❄️"
        elif post_monsoon_total / sum_inputs > 0.40:
            seasonal_trend = "Post-Monsoon Showers 🍂"
        else:
            seasonal_trend = "Evenly Distributed ⛅"
    else:
        seasonal_trend = "N/A"
        
    # Display Insights Weather Cards
    i_col1, i_col2, i_col3, i_col4, i_col5 = st.columns(5)
    with i_col1:
        render_weather_kpi("Wettest Month", f"{wettest_month} ({monthly_vals[max_idx]:.1f} mm)", "🌧️")
    with i_col2:
        render_weather_kpi("Driest Month", f"{driest_month} ({monthly_vals[min_idx]:.1f} mm)", "☀️")
    with i_col3:
        render_weather_kpi("Average Monthly", f"{avg_monthly:.1f} mm", "☁️")
    with i_col4:
        render_weather_kpi("Total Input Sum", f"{sum_inputs:.1f} mm", "📏")
    with i_col5:
        render_weather_kpi("Seasonal Trend", seasonal_trend, "🔄")
        
    # Interactive Plotly Charts Row
    chart_tabs = st.tabs([
        "📊 Monthly Bar Chart", 
        "📈 Monthly Line Chart", 
        "📉 Monthly Area Chart", 
        "🧭 Annual Gauge Meter", 
        "⛪ Historical Distribution"
    ])
    
    months_dict = {m: val for m, val in zip(MONTHS, monthly_vals)}
    
    with chart_tabs[0]:
        st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
        fig_bar = plot_monthly_bar(months_dict, title="Monthly Precipitation Bar breakdown")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with chart_tabs[1]:
        st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
        fig_line = plot_monthly_line(months_dict, title="Monthly Precipitation Line profile")
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with chart_tabs[2]:
        st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
        fig_area = plot_monthly_area(months_dict, title="Monthly Precipitation Area profile")
        st.plotly_chart(fig_area, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with chart_tabs[3]:
        st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
        # Fetch historical bounds for this subdivision if possible
        if df_historical is not None:
            sub_df = df_historical[df_historical["SUBDIVISION"] == selected_subdivision]
            sub_min = float(sub_df["ANNUAL"].min())
            sub_max = float(sub_df["ANNUAL"].max())
            sub_avg = float(sub_df["ANNUAL"].mean())
        else:
            sub_min, sub_max, sub_avg = 200.0, 5000.0, 1500.0
            
        fig_gauge = plot_annual_gauge(prediction_result["predicted_annual"], sub_min, sub_max, sub_avg)
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with chart_tabs[4]:
        st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
        # Show distribution compared to historical years
        if df_historical is not None:
            sub_df = df_historical[df_historical["SUBDIVISION"] == selected_subdivision]
            fig_dist = plot_rainfall_dist(sub_df, prediction_result["predicted_annual"], title=f"Historical Annual Rainfall Density: {selected_subdivision}")
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.warning("Historical dataset is missing to compute distribution density.")
        st.markdown("</div>", unsafe_allow_html=True)

# Prediction History Section (always visible at bottom)
st.write("---")
st.write("### 📁 Recent Predictions History")

if st.session_state["history"]:
    history_df = pd.DataFrame(st.session_state["history"])
    st.dataframe(history_df, use_container_width=True)
    
    col_h1, col_h2, _ = st.columns([1.5, 1.5, 5])
    with col_h1:
        # Download History as CSV
        csv_data = history_df.to_csv(index=False)
        st.download_button(
            label="📥 Download History CSV",
            data=csv_data,
            file_name="weather_forecast_history.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_h2:
        # Clear History
        if st.button("🗑️ Clear History Cache", use_container_width=True):
            st.session_state["history"] = []
            st.success("History cache cleared.")
            st.rerun()
else:
    st.info("No prediction history recorded in this session yet.")
