import requests
import json
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
CITY = "Dublin,IE"

def fetch_weather(city):
    """Fetch current weather data for a given city"""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  # Celsius
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def parse_weather(data):
    """Extract only what we need from the response"""
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
        "timestamp": datetime.now().isoformat()
    }

def save_to_database(parsed_data):
    """Save parsed weather data to PostgreSQL"""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO weather_data 
        (city, temperature, humidity, condition, wind_speed, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        parsed_data["city"],
        parsed_data["temperature"],
        parsed_data["humidity"],
        parsed_data["condition"],
        parsed_data["wind_speed"],
        parsed_data["timestamp"]
    ))

    conn.commit()
    cursor.close()
    conn.close()
    print("Data saved to database!")

if __name__ == "__main__":
    raw_data = fetch_weather(CITY)
    if raw_data:
        # Save raw data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = f"data/raw/weather_{timestamp}.json"
        with open(raw_path, "w") as f:
            json.dump(raw_data, f, indent=2)
        print(f"Raw data saved to {raw_path}")

        # Parse and save to database
        parsed = parse_weather(raw_data)
        save_to_database(parsed)
        print(json.dumps(parsed, indent=2))