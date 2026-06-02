import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import os
import pickle
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Stormflow Dashboard",
    page_icon="🌩️",
    layout="wide"
)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_weather_data():
    """Load weather and demand data from PostgreSQL"""
    conn = get_connection()
    query = """
        SELECT 
            w.id,
            w.city,
            w.temperature,
            w.humidity,
            w.condition,
            w.wind_speed,
            w.timestamp,
            p.demand,
            p.weather_impact
        FROM weather_data w
        JOIN processed_weather p ON w.id = p.id
        ORDER BY w.timestamp DESC
        LIMIT 100
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def load_latest_report():
    """Load the most recent AI report"""
    import glob
    reports = glob.glob('reports/report_*.txt')
    if not reports:
        return "No reports generated yet."
    latest = max(reports)
    with open(latest, 'r') as f:
        return f.read()

def get_weather_emoji(condition):
    """Get emoji for weather condition"""
    condition = condition.lower()
    if 'rain' in condition:
        return '🌧️'
    elif 'cloud' in condition:
        return '☁️'
    elif 'clear' in condition:
        return '☀️'
    elif 'snow' in condition:
        return '❄️'
    else:
        return '🌤️'

# Main Dashboard
st.title("🌩️ Stormflow — Weather Demand Intelligence")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load data
df = load_weather_data()

if df.empty:
    st.error("No data available yet. Run the pipeline first!")
    st.stop()

latest = df.iloc[0]

# ── Row 1: Current conditions ──
st.subheader("Current Conditions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    emoji = get_weather_emoji(latest['condition'])
    st.metric(
        label=f"{emoji} Temperature",
        value=f"{latest['temperature']:.1f}°C"
    )

with col2:
    st.metric(
        label="💧 Humidity",
        value=f"{latest['humidity']}%"
    )

with col3:
    st.metric(
        label="💨 Wind Speed",
        value=f"{latest['wind_speed']} m/s"
    )

with col4:
    st.metric(
        label="🛵 Demand Forecast",
        value=f"{latest['demand']} orders",
        delta=f"Impact: {latest['weather_impact']}"
    )

st.divider()

# ── Row 2: Charts ──
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌡️ Temperature Trend")
    fig_temp = px.line(
        df.sort_values('timestamp'),
        x='timestamp',
        y='temperature',
        title='Temperature Over Time',
        color_discrete_sequence=['#FF6B6B']
    )
    fig_temp.update_layout(
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        showlegend=False
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with col_right:
    st.subheader("🛵 Demand Trend")
    fig_demand = px.bar(
        df.sort_values('timestamp'),
        x='timestamp',
        y='demand',
        title='Demand Forecast Over Time',
        color='weather_impact',
        color_discrete_map={
            'low': '#2ECC71',
            'medium': '#F39C12',
            'high': '#E74C3C'
        }
    )
    fig_demand.update_layout(
        xaxis_title="Time",
        yaxis_title="Orders",
    )
    st.plotly_chart(fig_demand, use_container_width=True)

st.divider()

# ── Row 3: Weather vs Demand correlation ──
st.subheader("🔍 Weather vs Demand Correlation")
fig_scatter = px.scatter(
    df,
    x='temperature',
    y='demand',
    color='weather_impact',
    size='humidity',
    hover_data=['condition', 'wind_speed', 'timestamp'],
    title='Temperature vs Demand (size = humidity)',
    color_discrete_map={
        'low': '#2ECC71',
        'medium': '#F39C12',
        'high': '#E74C3C'
    }
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ── Row 4: AI Report ──
st.subheader("🤖 Latest AI Insight Report")
report = load_latest_report()
st.info(report)

st.divider()

# ── Row 5: Raw data table ──
st.subheader("📋 Recent Data")
st.dataframe(
    df[['timestamp', 'temperature', 'humidity', 
        'condition', 'wind_speed', 'demand', 'weather_impact']]
    .sort_values('timestamp', ascending=False)
    .head(10),
    use_container_width=True
)
