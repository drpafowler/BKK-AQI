import requests
import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import http.client, urllib


# Load environment variables
load_dotenv()
API_KEY = os.getenv("WAQI_API_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER")

# Set the unhealthy AQI threshold
UNHEALTHY_THRESHOLD = 150

# Flag to track if an unhealthy alert has been sent
unhealthy_alert_sent = False

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

def send_alert(aqi):
    """Sends an alert via Pushover if AQI is above the unhealthy threshold."""
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": f"Alert! The AQI in Bangkok is {aqi}, which is above the unhealthy threshold of {UNHEALTHY_THRESHOLD}."
        }), { "Content-type": "application/x-www-form-urlencoded" })
    response = conn.getresponse()
    if response.status == 200:
        print("Alert sent successfully.")
    else:
        print(f"Failed to send alert: {response.status} - {response.read().decode()}")

def main():
    global unhealthy_alert_sent
    while True:
        try:
            aqi = get_aqi_data()
            print(f"Current AQI: {aqi}")
            if aqi > UNHEALTHY_THRESHOLD and not unhealthy_alert_sent:
                send_alert(aqi)
                unhealthy_alert_sent = True
            elif aqi <= UNHEALTHY_THRESHOLD:
                unhealthy_alert_sent = False
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(3600)  # Wait for 1 hour before checking again

if __name__ == "__main__":
    main()