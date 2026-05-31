from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add project to path so Airflow can find our modules
sys.path.insert(0, '/home/saurav/projects/stormflow')

from ingestion.fetch_weather import fetch_weather, parse_weather, save_to_database
from processing.transform_weather import create_spark_session, load_weather_from_postgres, generate_demand_data, save_to_postgres

# Default arguments for all tasks
default_args = {
    'owner': 'saurav',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

# Define the DAG
dag = DAG(
    'stormflow_pipeline',
    default_args=default_args,
    description='Weather driven demand forecasting pipeline',
    schedule_interval='@hourly',
    start_date=datetime(2026, 5, 31),
    catchup=False,
    tags=['stormflow', 'weather', 'demand']
)

def ingest_weather():
    """Task 1: Fetch and store weather data"""
    from dotenv import load_dotenv
    load_dotenv('/home/saurav/projects/stormflow/.env')
    
    raw_data = fetch_weather('Dublin,IE')
    if raw_data:
        # Save raw file
        from datetime import datetime
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = f'/home/saurav/projects/stormflow/data/raw/weather_{timestamp}.json'
        with open(raw_path, 'w') as f:
            json.dump(raw_data, f, indent=2)
        
        # Save to database
        parsed = parse_weather(raw_data)
        save_to_database(parsed)
        print(f"Weather ingested successfully: {parsed['temperature']}°C")
    else:
        raise Exception("Failed to fetch weather data!")

def transform_weather():
    """Task 2: Transform and generate demand data"""
    from dotenv import load_dotenv
    load_dotenv('/home/saurav/projects/stormflow/.env')
    
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("ERROR")
    
    weather_df = load_weather_from_postgres(spark)
    processed_df = generate_demand_data(weather_df)
    save_to_postgres(processed_df)
    
    spark.stop()
    print("Transformation complete!")

# Define tasks
task_ingest = PythonOperator(
    task_id='ingest_weather',
    python_callable=ingest_weather,
    dag=dag
)

task_transform = PythonOperator(
    task_id='transform_weather',
    python_callable=transform_weather,
    dag=dag
)

# Define dependencies — ingest MUST succeed before transform
task_ingest >> task_transform
