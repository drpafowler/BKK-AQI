'''
producer.py
fetch real time AQI data from the WAQI API and send it to a Kafka topic.
Example json message:
{"status":"ok","data":{"aqi":143,"idx":5773,"attributions":[{"url":"http://aqmthai.com/","name":"Division of Air Quality Data, Air Quality and Noise Management Bureau, Pollution Control Department.","logo":"Thailand-PCD.png"},{"url":"https://waqi.info/","name":"World Air Quality Index Project"}],"city":{"geo":[13.7563309,100.5017651],"name":"Bangkok","url":"https://aqicn.org/city/bangkok","location":""},"dominentpol":"pm25","iaqi":{"co":{"v":0.1},"h":{"v":62.9},"no2":{"v":2.4},"o3":{"v":15},"p":{"v":1010.7},"pm10":{"v":60},"pm25":{"v":143},"so2":{"v":0.6},"t":{"v":27.5},"w":{"v":0.5}},"time":{"s":"2025-02-11 22:00:00","tz":"+07:00","v":1739311200,"iso":"2025-02-11T22:00:00+07:00"},"forecast":{"daily":{"o3":[{"avg":13,"day":"2025-02-09","max":37,"min":3},{"avg":12,"day":"2025-02-10","max":74,"min":1},{"avg":13,"day":"2025-02-11","max":78,"min":1},{"avg":14,"day":"2025-02-12","max":80,"min":1},{"avg":14,"day":"2025-02-13","max":85,"min":1},{"avg":10,"day":"2025-02-14","max":68,"min":1},{"avg":10,"day":"2025-02-15","max":58,"min":1},{"avg":2,"day":"2025-02-16","max":4,"min":1}],"pm10":[{"avg":46,"day":"2025-02-09","max":46,"min":46},{"avg":52,"day":"2025-02-10","max":58,"min":46},{"avg":59,"day":"2025-02-11","max":64,"min":46},{"avg":72,"day":"2025-02-12","max":93,"min":58},{"avg":63,"day":"2025-02-13","max":73,"min":46},{"avg":56,"day":"2025-02-14","max":61,"min":46},{"avg":60,"day":"2025-02-15","max":72,"min":46},{"avg":52,"day":"2025-02-16","max":58,"min":46},{"avg":51,"day":"2025-02-17","max":53,"min":30}],"pm25":[{"avg":131,"day":"2025-02-09","max":138,"min":108},{"avg":149,"day":"2025-02-10","max":159,"min":138},{"avg":158,"day":"2025-02-11","max":164,"min":138},{"avg":174,"day":"2025-02-12","max":196,"min":159},{"avg":162,"day":"2025-02-13","max":174,"min":138},{"avg":156,"day":"2025-02-14","max":162,"min":138},{"avg":156,"day":"2025-02-15","max":164,"min":138},{"avg":146,"day":"2025-02-16","max":154,"min":138},{"avg":140,"day":"2025-02-17","max":154,"min":89}],"uvi":[{"avg":2,"day":"2025-02-09","max":10,"min":0},{"avg":2,"day":"2025-02-10","max":10,"min":0},{"avg":2,"day":"2025-02-11","max":10,"min":0},{"avg":2,"day":"2025-02-12","max":10,"min":0},{"avg":2,"day":"2025-02-13","max":10,"min":0},{"avg":2,"day":"2025-02-14","max":9,"min":0},{"avg":2,"day":"2025-02-15","max":9,"min":0},{"avg":0,"day":"2025-02-16","max":0,"min":0}]}},"debug":{"sync":"2025-02-12T00:42:31+09:00"}}}
'''

import requests
import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from kafka import KafkaProducer

# Load environment variables
load_dotenv()
API_KEY = os.getenv("WAQI_API_KEY")
KAFKA_TOPIC = 'bkk-aqi'
KAFKA_BROKER = 'localhost:9092'

def get_aqi_data():
    """Fetches AQI data from the WAQI API."""
    url = f"https://api.waqi.info/feed/bangkok/?token={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'ok':
        # Extract relevant AQI data from the response
        aqi_data = {
            "aqi": data['data']['aqi'],
            "co": data['data']['iaqi']['co']['v'],
            "h": data['data']['iaqi']['h']['v'],
            "no2": data['data']['iaqi']['no2']['v'],
            "o3": data['data']['iaqi']['o3']['v'],
            "pressure": data['data']['iaqi']['p']['v'],
            "pm10": data['data']['iaqi']['pm10']['v'],
            "pm25": data['data']['iaqi']['pm25']['v'],
            "so2": data['data']['iaqi']['so2']['v'],
            "temperature": data['data']['iaqi']['t']['v'],
            "wind": data['data']['iaqi']['w']['v'],
            "time_iso": data['data']['time']['iso'],
            "city_geo": data['data']['city']['geo'],
            "city_name": data['data']['city']['name']
        }
        return aqi_data
    else:
        # Raise an error if the API response status is not 'ok'
        raise ValueError("Error fetching AQI data")

def main():
    # Initialize Kafka producer
    producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    
    while True:
        try:
            # Fetch AQI data
            aqi_data = get_aqi_data()
            print(f"Current AQI Data: {aqi_data}")
            
            # Send AQI data to Kafka topic
            producer.send(KAFKA_TOPIC, aqi_data)
            
            # Wait for 5 minutes before fetching data again
            time.sleep(300)
        except Exception as e:
            # Print any errors that occur
            print(f"Error: {e}")

if __name__ == "__main__":
    main()