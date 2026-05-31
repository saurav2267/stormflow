import requests
import json
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def get_latest_data():
    """Fetch latest weather and demand data from PostgreSQL"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
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
        LIMIT 5
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return rows

def build_prompt(data):
    """Build a prompt for the LLM based on current data"""
    latest = data[0]
    city, temp, humidity, condition, wind, timestamp, demand, impact = latest

    prompt = f"""You are a data analyst for a food delivery company in {city}, Ireland.

Current weather conditions:
- Temperature: {temp:.1f}°C
- Humidity: {humidity}%
- Condition: {condition}
- Wind Speed: {wind} m/s
- Weather Impact on Demand: {impact}
- Current Demand Forecast: {demand} orders

Recent trend (last 5 readings):
"""
    for row in data:
        prompt += f"- {row[5].strftime('%H:%M')}: {row[1]:.1f}°C, {row[3]}, demand: {row[6]}\n"

    prompt += """
Based on this data, write a concise operational report (3-4 sentences) for the operations team that includes:
1. Current weather summary
2. Demand forecast and what's driving it
3. One specific operational recommendation

Be direct and actionable. No bullet points, just clear paragraphs."""

    return prompt

def generate_report(prompt):
    """Send prompt to Ollama and get response"""
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })

    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama error: {response.status_code}")

def save_report(report):
    """Save report to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"reports/report_{timestamp}.txt"
    with open(report_path, "w") as f:
        f.write(f"Stormflow Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("="*50 + "\n\n")
        f.write(report)
    print(f"Report saved to {report_path}")
    return report_path

if __name__ == "__main__":
    print("Fetching latest data...")
    data = get_latest_data()

    print("Building prompt...")
    prompt = build_prompt(data)

    print("Generating AI report...")
    report = generate_report(prompt)

    print("\n" + "="*50)
    print("STORMFLOW INSIGHT REPORT")
    print("="*50)
    print(report)
    print("="*50 + "\n")

    save_report(report)
