import requests
import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from twilio.rest import Client

# Example JSON response from WAQI API
'''{"status":"ok","data":{"aqi":143,"idx":5773,"attributions":[{"url":"http://aqmthai.com/","name":"Division of Air Quality Data, Air Quality and Noise Management Bureau, Pollution Control Department.","logo":"Thailand-PCD.png"},{"url":"https://waqi.info/","name":"World Air Quality Index Project"}],"city":{"geo":[13.7563309,100.5017651],"name":"Bangkok","url":"https://aqicn.org/city/bangkok","location":""},"dominentpol":"pm25","iaqi":{"co":{"v":0.1},"h":{"v":62.9},"no2":{"v":2.4},"o3":{"v":15},"p":{"v":1010.7},"pm10":{"v":60},"pm25":{"v":143},"so2":{"v":0.6},"t":{"v":27.5},"w":{"v":0.5}},"time":{"s":"2025-02-11 22:00:00","tz":"+07:00","v":1739311200,"iso":"2025-02-11T22:00:00+07:00"},"forecast":{"daily":{"o3":[{"avg":13,"day":"2025-02-09","max":37,"min":3},{"avg":12,"day":"2025-02-10","max":74,"min":1},{"avg":13,"day":"2025-02-11","max":78,"min":1},{"avg":14,"day":"2025-02-12","max":80,"min":1},{"avg":14,"day":"2025-02-13","max":85,"min":1},{"avg":10,"day":"2025-02-14","max":68,"min":1},{"avg":10,"day":"2025-02-15","max":58,"min":1},{"avg":2,"day":"2025-02-16","max":4,"min":1}],"pm10":[{"avg":46,"day":"2025-02-09","max":46,"min":46},{"avg":52,"day":"2025-02-10","max":58,"min":46},{"avg":59,"day":"2025-02-11","max":64,"min":46},{"avg":72,"day":"2025-02-12","max":93,"min":58},{"avg":63,"day":"2025-02-13","max":73,"min":46},{"avg":56,"day":"2025-02-14","max":61,"min":46},{"avg":60,"day":"2025-02-15","max":72,"min":46},{"avg":52,"day":"2025-02-16","max":58,"min":46},{"avg":51,"day":"2025-02-17","max":53,"min":30}],"pm25":[{"avg":131,"day":"2025-02-09","max":138,"min":108},{"avg":149,"day":"2025-02-10","max":159,"min":138},{"avg":158,"day":"2025-02-11","max":164,"min":138},{"avg":174,"day":"2025-02-12","max":196,"min":159},{"avg":162,"day":"2025-02-13","max":174,"min":138},{"avg":156,"day":"2025-02-14","max":162,"min":138},{"avg":156,"day":"2025-02-15","max":164,"min":138},{"avg":146,"day":"2025-02-16","max":154,"min":138},{"avg":140,"day":"2025-02-17","max":154,"min":89}],"uvi":[{"avg":2,"day":"2025-02-09","max":10,"min":0},{"avg":2,"day":"2025-02-10","max":10,"min":0},{"avg":2,"day":"2025-02-11","max":10,"min":0},{"avg":2,"day":"2025-02-12","max":10,"min":0},{"avg":2,"day":"2025-02-13","max":10,"min":0},{"avg":2,"day":"2025-02-14","max":9,"min":0},{"avg":2,"day":"2025-02-15","max":9,"min":0},{"avg":0,"day":"2025-02-16","max":0,"min":0}]}},"debug":{"sync":"2025-02-12T00:42:31+09:00"}}}'''

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
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching AQI data: {e}")
        return None

def send_sms(message):
    """Sends an SMS message using Twilio."""
    try:
      message = client.messages.create(
          body=message,
          from_=TWILIO_PHONE_NUMBER,
          to=RECIPIENT_PHONE_NUMBER
      )
      print(f"SMS sent successfully! SID: {message.sid}")
    except Exception as e:
      print(f"Error sending SMS: {e}")


def check_and_send_unhealthy_alert(aqi_data):
    """Checks AQI and sends an alert if unhealthy levels are reached."""
    global unhealthy_alert_sent
    if aqi_data:
        try:
            pm25_value = aqi_data["data"]["iaqi"]["pm25"]["v"]
            if pm25_value > UNHEALTHY_THRESHOLD and not unhealthy_alert_sent:
                message = "The AQI in Bangkok is now at unhealthy levels."
                send_sms(message)
                unhealthy_alert_sent = True
        except KeyError as e:
            print(f"Error accessing PM2.5 data: {e}.  Check API response format.")

def send_daily_forecast(aqi_data):
    """Sends the daily AQI forecast at 6 AM Bangkok time."""
    if aqi_data:
      try:
        now_utc = datetime.utcnow()
        bangkok_offset = timedelta(hours=7)  # Bangkok is UTC+7
        now_bangkok = now_utc + bangkok_offset
        if now_bangkok.hour == 6 and now_bangkok.minute == 0:
            today = now_bangkok.strftime("%Y-%m-%d")
            forecast_data = next((f for f in aqi_data["data"]["forecast"]["daily"]["pm25"] if f["day"] == today), None)

            if forecast_data:
                message = f"Today's average AQI is expected to be {forecast_data['avg']}, with a max of {forecast_data['max']} and a min of {forecast_data['min']}."
                send_sms(message)
      except KeyError as e:
        print(f"Error accessing forecast data: {e}. Check API response format.")
      except Exception as e:
        print(f"An error occurred: {e}")


while True:
    aqi_data = get_aqi_data()
    check_and_send_unhealthy_alert(aqi_data)
    send_daily_forecast(aqi_data)
    time.sleep(600)  # Wait for 10 minutes (600 seconds)
    # Reset unhealthy alert at 6 AM Bangkok time
    now_utc = datetime.utcnow()
    bangkok_offset = timedelta(hours=7)
    now_bangkok = now_utc + bangkok_offset
    if now_bangkok.hour == 0 and now_bangkok.minute == 0:
        unhealthy_alert_sent = False