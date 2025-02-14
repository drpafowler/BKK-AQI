import requests
import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from twilio.rest import Client


# Load environment variables
load_dotenv()
API_KEY = os.getenv("WAQI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
    """Sends an alert via Twilio if AQI is above the unhealthy threshold."""
    message = client.messages.create(
        body=f"Alert! The AQI in Bangkok is {aqi}, which is above the unhealthy threshold of {UNHEALTHY_THRESHOLD}.",
        from_=TWILIO_PHONE_NUMBER,
        to=RECIPIENT_PHONE_NUMBER
    )
    print(f"Alert sent: {message.sid}")

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