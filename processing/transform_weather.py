from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, rand, round as spark_round
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType, IntegerType
import os
from dotenv import load_dotenv

load_dotenv()

def create_spark_session():
    """Create and return a SparkSession"""
    return SparkSession.builder \
        .appName("stormflow") \
        .config("spark.driver.memory", "2g") \
        .config("spark.jars", "drivers/postgresql-42.7.3.jar") \
        .getOrCreate()

def load_weather_from_postgres(spark):
    """Load weather data from PostgreSQL into a Spark DataFrame"""
    jdbc_url = f"jdbc:postgresql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    df = spark.read \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "weather_data") \
        .option("user", os.getenv("DB_USER")) \
        .option("password", os.getenv("DB_PASSWORD")) \
        .option("driver", "org.postgresql.Driver") \
        .load()
    
    return df

def generate_demand_data(weather_df):
    """Generate synthetic delivery demand based on weather conditions"""
    df = weather_df.withColumn(
        "base_demand",
        when(col("condition").contains("rain"), 150)
        .when(col("condition").contains("snow"), 180)
        .when(col("condition").contains("cloud"), 120)
        .when(col("condition").contains("clear"), 80)
        .otherwise(100)
    )

    # Add randomness to make it realistic
    df = df.withColumn(
        "demand",
        spark_round(col("base_demand") * (0.8 + rand() * 0.4)).cast(IntegerType())
    )

    # Add weather impact score
    df = df.withColumn(
        "weather_impact",
        when(col("temperature") < 5, "high")
        .when(col("temperature") < 15, "medium")
        .otherwise("low")
    )

    return df.select(
        "id", "city", "temperature", "humidity",
        "condition", "wind_speed", "timestamp",
        "demand", "weather_impact"
    )

def save_to_postgres(df):
    """Save processed data back to PostgreSQL"""
    jdbc_url = f"jdbc:postgresql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    df.write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "processed_weather") \
        .option("user", os.getenv("DB_USER")) \
        .option("password", os.getenv("DB_PASSWORD")) \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()
    
    print("Processed data saved to PostgreSQL!")


if __name__ == "__main__":
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("ERROR")
    
    print("Loading weather data from PostgreSQL...")
    weather_df = load_weather_from_postgres(spark)
    
    print("Generating synthetic demand data...")
    processed_df = generate_demand_data(weather_df)
    
    print("Processed data sample:")
    processed_df.show(truncate=False)
    
    print("Saving to PostgreSQL...")
    save_to_postgres(processed_df)
    
    spark.stop()
