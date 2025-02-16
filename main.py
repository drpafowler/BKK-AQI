'''
main.py
fetch real time AQI data from the WAQI API and send it to astreamlit dashboard
Example json message:
{"status":"ok","data":{"aqi":143,"idx":5773,"attributions":[{"url":"http://aqmthai.com/","name":"Division of Air Quality Data, Air Quality and Noise Management Bureau, Pollution Control Department.","logo":"Thailand-PCD.png"},{"url":"https://waqi.info/","name":"World Air Quality Index Project"}],"city":{"geo":[13.7563309,100.5017651],"name":"Bangkok","url":"https://aqicn.org/city/bangkok","location":""},"dominentpol":"pm25","iaqi":{"co":{"v":0.1},"h":{"v":62.9},"no2":{"v":2.4},"o3":{"v":15},"p":{"v":1010.7},"pm10":{"v":60},"pm25":{"v":143},"so2":{"v":0.6},"t":{"v":27.5},"w":{"v":0.5}},"time":{"s":"2025-02-11 22:00:00","tz":"+07:00","v":1739311200,"iso":"2025-02-11T22:00:00+07:00"},"forecast":{"daily":{"o3":[{"avg":13,"day":"2025-02-09","max":37,"min":3},{"avg":12,"day":"2025-02-10","max":74,"min":1},{"avg":13,"day":"2025-02-11","max":78,"min":1},{"avg":14,"day":"2025-02-12","max":80,"min":1},{"avg":14,"day":"2025-02-13","max":85,"min":1},{"avg":10,"day":"2025-02-14","max":68,"min":1},{"avg":10,"day":"2025-02-15","max":58,"min":1},{"avg":2,"day":"2025-02-16","max":4,"min":1}],"pm10":[{"avg":46,"day":"2025-02-09","max":46,"min":46},{"avg":52,"day":"2025-02-10","max":58,"min":46},{"avg":59,"day":"2025-02-11","max":64,"min":46},{"avg":72,"day":"2025-02-12","max":93,"min":58},{"avg":63,"day":"2025-02-13","max":73,"min":46},{"avg":56,"day":"2025-02-14","max":61,"min":46},{"avg":60,"day":"2025-02-15","max":72,"min":46},{"avg":52,"day":"2025-02-16","max":58,"min":46},{"avg":51,"day":"2025-02-17","max":53,"min":30}],"pm25":[{"avg":131,"day":"2025-02-09","max":138,"min":108},{"avg":149,"day":"2025-02-10","max":159,"min":138},{"avg":158,"day":"2025-02-11","max":164,"min":138},{"avg":174,"day":"2025-02-12","max":196,"min":159},{"avg":162,"day":"2025-02-13","max":174,"min":138},{"avg":156,"day":"2025-02-14","max":162,"min":138},{"avg":156,"day":"2025-02-15","max":164,"min":138},{"avg":146,"day":"2025-02-16","max":154,"min":138},{"avg":140,"day":"2025-02-17","max":154,"min":89}],"uvi":[{"avg":2,"day":"2025-02-09","max":10,"min":0},{"avg":2,"day":"2025-02-10","max":10,"min":0},{"avg":2,"day":"2025-02-11","max":10,"min":0},{"avg":2,"day":"2025-02-12","max":10,"min":0},{"avg":2,"day":"2025-02-13","max":10,"min":0},{"avg":2,"day":"2025-02-14","max":9,"min":0},{"avg":2,"day":"2025-02-15","max":9,"min":0},{"avg":0,"day":"2025-02-16","max":0,"min":0}]}},"debug":{"sync":"2025-02-12T00:42:31+09:00"}}}
'''

import requests
import os
import streamlit as st
import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from kafka import KafkaProducer
import http.client, urllib
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from aqipy import aqi_us
from aqipy import aqi_cn
from aqipy import aqi_au
from aqipy import caqi_eu
from aqipy import cai_kr
from aqipy import daqi_uk
from aqipy import aqhi_ca
from aqipy import psi_sg

# Load environment variables
load_dotenv()
API_KEY = os.getenv("WAQI_API_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER")

# Set the unhealthy AQI threshold
UNHEALTHY_THRESHOLD = 150

# Flag to track if an unhealthy alert has been sent
unhealthy_alert_sent = False


####################
# Helper Functions #
####################
def get_aqi_data():
    """Fetches AQI data from the WAQI API."""
    url = f"https://api.waqi.info/feed/bangkok/?token={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'ok':
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
        raise ValueError("Error fetching AQI data")

def process_aqi_data(aqi_data):
    # Process the AQI data
    aqi = aqi_data['aqi']
    co = aqi_data['co']
    h = aqi_data['h']
    no2 = aqi_data['no2']
    o3 = aqi_data['o3']
    pressure = aqi_data['pressure']
    pm10 = aqi_data['pm10']
    pm25 = aqi_data['pm25']
    so2 = aqi_data['so2']
    temperature = aqi_data['temperature']
    wind = aqi_data['wind']
    time_iso = aqi_data['time_iso']
    city_geo = aqi_data['city_geo']
    city_name = aqi_data['city_name']
    
    # Create a DataFrame
    new_data = pd.DataFrame({
        'aqi': [aqi],
        'co': [co],
        'h': [h],
        'no2': [no2],
        'o3': [o3],
        'pressure': [pressure],
        'pm10': [pm10],
        'pm25': [pm25],
        'so2': [so2],
        'temperature': [temperature],
        'wind': [wind],
        'time_iso': [time_iso],
        'city_geo': [city_geo],
        'city_name': [city_name]
    })
    # Convert the time_iso column to datetime and set it as the index
    new_data['time_iso'] = pd.to_datetime(new_data['time_iso'])
    new_data = new_data.set_index('time_iso')

    # Check if the dataframe already exists and append data
    if 'aqi_df' in globals():
        global aqi_df
        aqi_df = pd.concat([aqi_df, new_data], ignore_index=True)
    else:
        global aqi_df
        aqi_df = new_data
    
    # Remove rows older than 25 hours
    cutoff_time = datetime.now() - timedelta(hours=25)
    aqi_df = aqi_df[aqi_df.index > cutoff_time]
    
    return aqi_df

def send_alert(aqi_us):
    # Sends an alert via Pushover if AQI is above the unhealthy threshold
    push = http.client.HTTPSConnection("api.pushover.net:443")
    push.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": f"Alert! The AQI in Bangkok is {aqi_us}, which is above the unhealthy threshold of {UNHEALTHY_THRESHOLD}."
        }), { "Content-type": "application/x-www-form-urlencoded" })
    response = push.getresponse()
    if response.status == 200:
        print("Alert sent successfully.")
    else:
        print(f"Failed to send alert: {response.status} - {response.read().decode()}")
