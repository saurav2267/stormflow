import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
CITY = "Dublin"

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

if __name__ == "__main__":
    raw_data = fetch_weather(CITY)
    if raw_data:
        parsed = parse_weather(raw_data)
        print(json.dumps(parsed, indent=2))
