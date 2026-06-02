# 🌩️ Stormflow — Weather-Driven Demand Forecasting Pipeline

A **production-grade, end-to-end data engineering pipeline** that correlates real-time weather data with food delivery demand forecasting, powered by AI-generated operational insights.

> Built as a portfolio project demonstrating real-world data engineering skills.

---

## 🎯 What It Does

Stormflow automatically:
1. **Fetches** real-time weather data from OpenWeatherMap every hour
2. **Processes** and transforms data using Apache PySpark
3. **Forecasts** food delivery demand based on weather patterns using XGBoost
4. **Generates** AI-powered operational reports using Ollama (llama3.2)
5. **Visualizes** everything in a live Streamlit dashboard

---

## 🏗️ Architecture
OpenWeatherMap API
↓
Python Ingestion Layer
↓
PostgreSQL (Raw Storage)
↓
PySpark Transformations
↓
XGBoost Demand Forecasting
↓
Ollama AI Report Generation (llama3.2)
↓
Streamlit Live Dashboard
↑
Apache Airflow (Orchestrates everything hourly)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Ingestion | Python, Requests, OpenWeatherMap API |
| Processing | Apache PySpark 4.1 |
| Storage | PostgreSQL 16 |
| Orchestration | Apache Airflow 2.9 |
| ML Forecasting | XGBoost, Scikit-learn |
| AI Reports | Ollama, llama3.2 |
| Dashboard | Streamlit, Plotly |
| Environment | WSL Ubuntu, Python 3.12 |
| Version Control | Git, GitHub |

---

## 📁 Project Structure
stormflow/
├── dags/                    # Airflow DAG definitions
│   └── stormflow_dag.py     # Main pipeline DAG (hourly)
├── ingestion/               # Data ingestion layer
│   ├── fetch_weather.py     # OpenWeatherMap API client
│   └── setup_database.py   # PostgreSQL schema setup
├── processing/              # PySpark transformation layer
│   └── transform_weather.py # Weather + demand processing
├── models/                  # ML forecasting
│   └── forecast_demand.py   # XGBoost demand forecasting
├── reports/                 # AI insight reports
│   └── generate_report.py   # Ollama report generation
├── dashboard/               # Visualization layer
│   └── app.py               # Streamlit dashboard
├── data/
│   ├── raw/                 # Immutable raw API responses
│   └── processed/           # Transformed data
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md

---

## 🚀 Setup & Installation

### Prerequisites
- WSL Ubuntu / Linux
- Python 3.12+
- Java 21 (for PySpark)
- PostgreSQL 16
- Ollama with llama3.2

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/saurav2267/stormflow.git
cd stormflow
```

**2. Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your actual values
nano .env
```

**5. Set up PostgreSQL**
```bash
sudo service postgresql start
python3 ingestion/setup_database.py
```

**6. Initialize Airflow**
```bash
export AIRFLOW_HOME=~/airflow
airflow db init
airflow standalone
```

**7. Run the dashboard**
```bash
streamlit run dashboard/app.py
```

---

## 📊 Pipeline DAG

The Airflow DAG runs hourly and executes tasks in order:
[ingest_weather] ──→ [transform_weather]

- **ingest_weather** — fetches weather data, saves raw JSON, stores in PostgreSQL
- **transform_weather** — PySpark processes data, generates demand forecast, saves results

---

## 🤖 AI Insight Reports

Every pipeline run generates a human-readable operational report using llama3.2:
Stormflow Report — 2026-06-02 11:42
Current weather conditions show 15.7°C with 83%
humidity and light rain. Demand forecast stands at
116 orders with low weather impact. Recommend
maintaining standard rider distribution across
Dublin city centre.

---

## 📈 Key Features

- **Real-time data** — live weather from OpenWeatherMap API
- **Immutable raw layer** — raw data never modified, always recoverable
- **Automated orchestration** — Airflow runs pipeline every hour, 24/7
- **ML forecasting** — XGBoost model trained on 30 days of historical data
- **AI narratives** — LLM generates plain-English reports from data
- **Interactive dashboard** — Streamlit with live Plotly charts
- **Production patterns** — virtual environments, .env secrets, parameterized SQL

---

## 🧠 Skills Demonstrated

- Data pipeline architecture & design
- REST API integration
- SQL schema design & query optimization
- Apache PySpark distributed processing
- Apache Airflow DAG authoring & scheduling
- Machine learning (XGBoost, feature engineering)
- LLM integration & prompt engineering
- Data visualization (Streamlit, Plotly)
- Git workflow & project documentation

---
