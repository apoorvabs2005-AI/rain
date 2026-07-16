import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# Theme Colors: Sky blue theme matching Light Theme Weather Apps
PRIMARY_COLOR = "#0088cc"  # Sky blue
SECONDARY_COLOR = "#66ccff" # Light cloud blue
ACCENT_COLOR = "#005580"    # Dark blue slate
BG_COLOR = "#F4F9FC"        # Cloud white-blue
PAPER_BG_COLOR = "#FFFFFF"  # White
TEXT_COLOR = "#2C3E50"      # Dark slate text

def apply_layout_theme(fig, title_text):
    """
    Applies the custom weather-inspired light theme layout to a Plotly figure.
    """
    fig.update_layout(
        title={
            'text': title_text,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16, 'color': TEXT_COLOR, 'family': "Segoe UI, sans-serif"}
        },
        paper_bgcolor=PAPER_BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family="Segoe UI, sans-serif"),
        margin=dict(t=60, b=40, l=50, r=30),
        xaxis=dict(
            gridcolor="#EBF3F9",
            linecolor=SECONDARY_COLOR,
            tickfont=dict(color=TEXT_COLOR)
        ),
        yaxis=dict(
            gridcolor="#EBF3F9",
            linecolor=SECONDARY_COLOR,
            tickfont=dict(color=TEXT_COLOR)
        ),
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor=SECONDARY_COLOR,
            borderwidth=1
        )
    )
    return fig

def plot_monthly_bar(months_data: dict, title="Monthly Rainfall Breakdown"):
    """
    Draws a vertical bar chart showing monthly rainfall.
    """
    months = list(months_data.keys())
    values = list(months_data.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=months,
            y=values,
            marker_color=PRIMARY_COLOR,
            marker_line_color=ACCENT_COLOR,
            marker_line_width=1,
            opacity=0.85,
            hovertemplate="Month: %{x}<br>Rainfall: %{y:.1f} mm<extra></extra>"
        )
    ])
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Rainfall (mm)",
        height=320
    )
    return apply_layout_theme(fig, title)

def plot_monthly_line(months_data: dict, title="Monthly Rainfall Line Profile"):
    """
    Draws a line chart showing monthly rainfall trends.
    """
    months = list(months_data.keys())
    values = list(months_data.values())
    
    fig = go.Figure(data=[
        go.Scatter(
            x=months,
            y=values,
            mode="lines+markers",
            line=dict(color=PRIMARY_COLOR, width=3),
            marker=dict(size=6, color=ACCENT_COLOR),
            hovertemplate="Month: %{x}<br>Rainfall: %{y:.1f} mm<extra></extra>"
        )
    ])
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Rainfall (mm)",
        height=320
    )
    return apply_layout_theme(fig, title)

def plot_monthly_area(months_data: dict, title="Monthly Rainfall Area Profile"):
    """
    Draws an area chart showing monthly rainfall filled to zero.
    """
    months = list(months_data.keys())
    values = list(months_data.values())
    
    fig = go.Figure(data=[
        go.Scatter(
            x=months,
            y=values,
            mode="lines+markers",
            line=dict(color=PRIMARY_COLOR, width=3),
            marker=dict(size=6, color=ACCENT_COLOR),
            fill="tozeroy",
            fillcolor="rgba(102, 204, 255, 0.3)",
            hovertemplate="Month: %{x}<br>Rainfall: %{y:.1f} mm<extra></extra>"
        )
    ])
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Rainfall (mm)",
        height=320
    )
    return apply_layout_theme(fig, title)

def plot_annual_gauge(value: float, min_val: float, max_val: float, avg_val: float, title="Predicted Annual Rainfall Gauge"):
    """
    Creates a Gauge chart representing predicted annual rainfall in mm relative to historical bounds.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={'reference': avg_val, 'relative': False, 'position': "top", 'valueformat': ".1f", 'increasing': {'color': "#0088cc"}, 'decreasing': {'color': "#e74c3c"}},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Rainfall (mm)", 'font': {'size': 12, 'color': TEXT_COLOR}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': TEXT_COLOR},
            'bar': {'color': PRIMARY_COLOR},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': SECONDARY_COLOR,
            'steps': [
                {'range': [min_val, avg_val], 'color': '#EBF3F9'},
                {'range': [avg_val, max_val], 'color': '#D0ECFC'}
            ],
            'threshold': {
                'line': {'color': '#e74c3c', 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(t=50, b=10, l=30, r=30),
        paper_bgcolor=PAPER_BG_COLOR
    )
    return fig

def plot_rainfall_dist(df: pd.DataFrame, predicted_value: float = None, title="Historical Annual Rainfall Distribution"):
    """
    Plots a histogram showing historical annual rainfall, with a line marker for the predicted annual total.
    """
    fig = px.histogram(
        df, 
        x="ANNUAL", 
        nbins=30,
        color_discrete_sequence=[PRIMARY_COLOR],
        opacity=0.75,
        labels={"ANNUAL": "Annual Rainfall (mm)"}
    )
    
    if predicted_value is not None:
        fig.add_vline(
            x=predicted_value,
            line_width=4,
            line_dash="dash",
            line_color="#e67e22",
            annotation_text=f"Prediction: {predicted_value:.1f} mm",
            annotation_position="top right",
            annotation_font=dict(color="#e67e22", size=12)
        )
        
    fig.update_layout(
        xaxis_title="Annual Rainfall (mm)",
        yaxis_title="Years Frequency",
        height=320
    )
    return apply_layout_theme(fig, title)
