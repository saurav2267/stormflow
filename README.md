# 🌩️ Stormflow

A production-grade weather-driven demand forecasting pipeline built with Python, PySpark, Apache Airflow, and AI-powered insights.

## 🏗️ Architecture
Weather API → Airflow → PySpark → PostgreSQL → ML Forecast → AI Reports → Dashboard

## 🛠️ Tech Stack
- **Ingestion:** Python, OpenWeatherMap API
- **Processing:** PySpark
- **Orchestration:** Apache Airflow
- **Storage:** PostgreSQL
- **ML:** XGBoost / Prophet
- **AI Reports:** Ollama (llama3.2)
- **Visualization:** Streamlit

## 📁 Project Structure
- `ingestion/` - Weather data fetching scripts
- `processing/` - PySpark transformation scripts
- `dags/` - Airflow DAG definitions
- `models/` - ML forecasting models
- `reports/` - AI generated insight reports
- `data/` - Raw and processed data storage
- `tests/` - Unit tests

## 🚀 Setup
1. Clone the repo
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Add your API keys to `.env`
6. Run ingestion: `python3 ingestion/fetch_weather.py`