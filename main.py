import pandas as pd
import os
from aqipy import aqi_us
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import http.client, urllib
import sqlite3

# Load environment variables
load_dotenv()
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER")

# Set the unhealthy AQI threshold
UNHEALTHY_THRESHOLD = 150

# Flag to track if an unhealthy alert has been sent
unhealthy_alert_sent = False

def get_aqi_data():
    try:
        conn = sqlite3.connect('./data/bkk_aqi.db')
        aqi_data = pd.read_sql_query("SELECT * FROM aqi_data", conn)
        aqi_data['time_iso'] = pd.to_datetime(aqi_data['time_iso'])
        aqi_data = aqi_data.set_index('time_iso')
        # Pull the most recent 1 hours of data
        recent_data_1h = aqi_data[aqi_data.index >= (aqi_data.index.max() - pd.Timedelta(hours=1))]
        #calculate the mean of the most recent 1 hour of data for o3, no2, pm10 and so2
        mean_o3_1h = recent_data_1h['o3'].mean()
        mean_no2_1h = recent_data_1h['no2'].mean()
        # Pull the most recent 8 hours of data
        recent_data_8h = aqi_data[aqi_data.index >= (aqi_data.index.max() - pd.Timedelta(hours=8))]
        # Calculate the mean of the recent 8 hours of data for o3 and co
        mean_o3_8h = recent_data_8h['o3'].mean()
        mean_co_8h = recent_data_8h['co'].mean()
        # Pull the most recent 24 hours of data
        recent_data_24h = aqi_data[aqi_data.index >= (aqi_data.index.max() - pd.Timedelta(hours=24))]
        # Calculate the mean of the recent 24 hours of data for pm25, pm,10 and so2
        mean_pm25_24h = recent_data_24h['pm25'].mean()
        mean_pm10_24h = recent_data_24h['pm10'].mean()
        mean_so2_24h = recent_data_24h['so2'].mean()
        # Calculate the US AQI based on the mean values
        aqi_us_value, aqi_data_us = aqi_us.get_aqi(o3_8h=mean_o3_8h, co_8h=mean_co_8h, pm10_24h=mean_pm10_24h, pm25_24h=mean_pm25_24h, so2_24h=mean_so2_24h, no2_1h=mean_no2_1h, o3_1h=mean_o3_1h)
        return aqi_us_value
    except Exception as e:
        print(f"Error: {e}")
        return None

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

def main():
    global unhealthy_alert_sent
    while True:
        try:
            aqi_data = get_aqi_data()
            if aqi_data is not None:
                print(f"Current AQI: {aqi_data}")
                if aqi_data > UNHEALTHY_THRESHOLD and not unhealthy_alert_sent:
                    send_alert(aqi_data)
                    unhealthy_alert_sent = True
                elif aqi_data <= UNHEALTHY_THRESHOLD:
                    unhealthy_alert_sent = False
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(3600)  # Wait for 1 hour before sending again

if __name__ == "__main__":
    main()