import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Create a connection to PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def create_tables():
    """Create the weather data table"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            temperature FLOAT NOT NULL,
            humidity INTEGER NOT NULL,
            condition VARCHAR(200),
            wind_speed FLOAT,
            timestamp TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
