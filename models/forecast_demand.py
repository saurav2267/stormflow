import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import psycopg2
import os
import pickle
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def generate_historical_data():
    """Generate 30 days of realistic historical weather + demand data"""
    print("Generating 30 days of historical data...")
    
    np.random.seed(42)
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='h'
    )
    
    n = len(dates)
    
    # Realistic Dublin weather patterns
    temperature = 12 + 5 * np.sin(np.arange(n) * 2 * np.pi / 24) + np.random.normal(0, 2, n)
    humidity = 70 + 15 * np.random.normal(0, 1, n)
    humidity = np.clip(humidity, 30, 100)
    wind_speed = np.abs(np.random.normal(4, 2, n))
    
    # Conditions based on humidity
    conditions = []
    for h in humidity:
        if h > 85:
            conditions.append('rain')
        elif h > 70:
            conditions.append('broken clouds')
        else:
            conditions.append('clear sky')
    
    # Demand based on weather + time patterns
    demand = []
    for i, (temp, hum, wind, cond, date) in enumerate(
        zip(temperature, humidity, wind_speed, conditions, dates)
    ):
        base = 100
        # Weather effects
        if 'rain' in cond:
            base += 50
        elif 'cloud' in cond:
            base += 20
        
        # Temperature effect
        if temp < 8:
            base += 40
        elif temp < 12:
            base += 20
            
        # Hour of day effect (peak at lunch and dinner)
        hour = date.hour
        if hour in [12, 13]:
            base += 30
        elif hour in [18, 19, 20]:
            base += 50
        elif hour in [2, 3, 4]:
            base -= 60
            
        # Add randomness
        base += np.random.normal(0, 15)
        demand.append(max(0, int(base)))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'temperature': temperature,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'condition': conditions,
        'demand': demand
    })
    
    return df

def prepare_features(df):
    """Extract ML features from the dataframe"""
    df = df.copy()
    
    # Time features
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Weather features
    df['is_raining'] = df['condition'].str.contains('rain').astype(int)
    df['is_cloudy'] = df['condition'].str.contains('cloud').astype(int)
    
    # Peak hours
    df['is_lunch'] = df['hour'].isin([12, 13]).astype(int)
    df['is_dinner'] = df['hour'].isin([18, 19, 20]).astype(int)
    
    feature_cols = [
        'temperature', 'humidity', 'wind_speed',
        'hour', 'day_of_week', 'is_weekend',
        'is_raining', 'is_cloudy',
        'is_lunch', 'is_dinner'
    ]
    
    return df[feature_cols], df['demand']

def train_model(df):
    """Train XGBoost model"""
    print("Training XGBoost model...")
    
    X, y = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"Model MAE: {mae:.2f} orders")
    
    return model

def save_model(model):
    """Save trained model to disk"""
    model_path = 'models/demand_forecast_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

def predict_demand(model, temperature, humidity, wind_speed, condition, hour, day_of_week):
    """Predict demand for given conditions"""
    features = pd.DataFrame([{
        'temperature': temperature,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'hour': hour,
        'day_of_week': day_of_week,
        'is_weekend': 1 if day_of_week in [5, 6] else 0,
        'is_raining': 1 if 'rain' in condition else 0,
        'is_cloudy': 1 if 'cloud' in condition else 0,
        'is_lunch': 1 if hour in [12, 13] else 0,
        'is_dinner': 1 if hour in [18, 19, 20] else 0
    }])
    
    return int(model.predict(features)[0])

if __name__ == "__main__":
    # Generate training data
    df = generate_historical_data()
    print(f"Generated {len(df)} hours of historical data")
    print(df.head())
    
    # Train model
    model = train_model(df)
    
    # Save model
    save_model(model)
    
    # Test prediction
    prediction = predict_demand(
        model,
        temperature=10.0,
        humidity=85.0,
        wind_speed=5.0,
        condition='rain',
        hour=19,
        day_of_week=4
    )
    print(f"\nTest prediction:")
    print(f"Rainy Friday evening at 10°C → {prediction} orders expected")
