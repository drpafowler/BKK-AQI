import requests
import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import kafka

# Load environment variables
load_dotenv()
API_KEY = os.getenv("WAQI_API_KEY")

def get_aqi_data():
    """Fetches AQI data from the WAQI API."""
    url = f"https://api.waqi.info/feed/bangkok/?token={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'ok':
        aqi = data['data']['aqi']
        return aqi
    else:
        raise ValueError("Error fetching AQI data")

def main():
    producer = kafka.KafkaProducer(bootstrap_servers='localhost:9092')
    while True:
        try:
            aqi = get_aqi_data()
            print(f"Current AQI: {aqi}")
            producer.send('aqi', json.dumps(aqi).encode())
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()