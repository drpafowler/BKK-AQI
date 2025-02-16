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
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
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

    # Declare aqi_df as global before using it
    global aqi_df

    # Check if the dataframe already exists and append data
    if 'aqi_df' in globals():
        global aqi_df
        aqi_df = pd.concat([aqi_df, new_data], ignore_index=True)
    else:
        aqi_df = new_data
    
    # Remove rows older than 25 hours
    cutoff_time = datetime.now(tz=timezone.utc) - timedelta(hours=25)
    aqi_df = aqi_df[aqi_df.index > cutoff_time] # This comparison now works

    # Pull the most recent so2 data
    recent_so2 = aqi_df['so2'].iloc[-1]

    # Pull the most recent 1 hours of data
    recent_data_1h = aqi_df[aqi_df.index >= (aqi_df.index.max() - pd.Timedelta(hours=1))]

    #calculate the mean of the most recent 1 hour of data for o3, no2, pm10 and so2
    mean_o3_1h = recent_data_1h['o3'].mean()
    mean_no2_1h = recent_data_1h['no2'].mean()
    mean_so2_1h = recent_data_1h['so2'].mean()
    mean_pm10_1h = recent_data_1h['pm10'].mean()
    mean_pm25_1h = recent_data_1h['pm25'].mean()
    mean_co_1h = recent_data_1h['co'].mean()

    # Calculate the max of the most recent 1 hour of data for o3, no2, and so2
    max_o3_1h = recent_data_1h['o3'].max()
    max_no2_1h = recent_data_1h['no2'].max()
    max_so2_1h = recent_data_1h['so2'].max()

    # Pull the most recent 3 hours of data
    recent_data_3h = aqi_df[aqi_df.index >= (aqi_df.index.max() - pd.Timedelta(hours=3))]

    # Calculate the mean of the recent 3 hours of data for pm10, pm25, o3, so2, no2 and co
    mean_pm10_3h = recent_data_3h['pm10'].mean()
    mean_pm25_3h = recent_data_3h['pm25'].mean()
    mean_o3_3h = recent_data_3h['o3'].mean()
    mean_so2_3h = recent_data_3h['so2'].mean()
    mean_no2_3h = recent_data_3h['no2'].mean()
    mean_co_3h = recent_data_3h['co'].mean()

    # Pull the most recent 4 hours of data
    recent_data_4h = aqi_df[aqi_df.index >= (aqi_df.index.max() - pd.Timedelta(hours=4))]

    # Calculate the mean of the recent 4 hours of data for o3
    mean_o3_4h = recent_data_4h['o3'].mean()

    # Pull the most recent 8 hours of data
    recent_data_8h = aqi_df[aqi_df.index >= (aqi_df.index.max() - pd.Timedelta(hours=8))]

    # Calculate the mean of the recent 8 hours of data for o3 and co
    mean_o3_8h = recent_data_8h['o3'].mean()
    mean_co_8h = recent_data_8h['co'].mean()

    # Pull the most recent 24 hours of data
    recent_data_24h = aqi_df[aqi_df.index >= (aqi_df.index.max() - pd.Timedelta(hours=24))]

    # Calculate the mean of the recent 24 hours of data for pm10, pm25, co2 and so2
    mean_pm10_24h = recent_data_24h['pm10'].mean()
    mean_pm25_24h = recent_data_24h['pm25'].mean()
    mean_so2_24h = recent_data_24h['so2'].mean()
    mean_co_24h = recent_data_24h['co'].mean()

    # Get PSI using the sg calculations 
    aqi_sg, aqi_data_sg = psi_sg.get_aqi(o3_8h=mean_o3_8h, co_8h=mean_co_8h, pm10_24h=mean_pm10_24h, pm25_24h=mean_pm25_24h, so2_24h=mean_so2_24h, no2_1h=mean_no2_1h)

    # Find the pollutant with the maximum AQI value
    max_pollutant_sg = max(aqi_data_sg, key=lambda k: aqi_data_sg[k][0])

    # Get AQI using the us calculations 
    aqi_us, aqi_data_us = aqi_us.get_aqi(o3_8h=mean_o3_8h, co_8h=mean_co_8h, pm10_24h=mean_pm10_24h, pm25_24h=mean_pm25_24h, so2_24h=mean_so2_24h, no2_1h=mean_no2_1h, o3_1h=max_o3_1h)

    # Find the pollutant with the maximum AQI value
    max_pollutant_us = max(aqi_data_us, key=lambda k: aqi_data_us[k][0])

    # AQI using the Australia calculations
    aqi_au, aqi_data_au = aqi_au.get_aqi(pm10_24h=mean_pm10_24h, pm25_24h=mean_pm25_24h, so2_24h=mean_so2_24h, no2_1h=mean_no2_1h, o3_1h=max_o3_1h, o3_4h=mean_o3_4h, co_8h=mean_co_8h)

    # Find the pollutant with the maximum AQI value
    max_pollutant_au = max(aqi_data_au, key=lambda k: aqi_data_au[k][0])

    # AQI using the EU calculations
    caqi_eu, aqi_data_eu = caqi_eu.get_caqi(pm10_24h=mean_pm10_24h, pm10_1h=mean_pm10_1h, pm25_24h=mean_pm25_24h, pm25_1h=mean_pm25_1h, so2_max_1h=max_so2_1h, no2_max_1h=max_no2_1h, o3_max_1h=max_o3_1h, co_1h=mean_co_1h)

    # AQI using the China calculations
    aqi_cn, aqi_data_cn = aqi_cn.get_aqi(pm10_24h=mean_pm10_24h, pm25_24h=mean_pm25_24h, so2_24h=mean_so2_24h, no2_24h=mean_no2_3h, o3_8h=mean_o3_8h, co_24h=mean_co_24h, o3_1h=mean_o3_1h)

    # Find the pollutant with the maximum AQI value
    max_pollutant_cn = max(aqi_data_cn, key=lambda k: aqi_data_cn[k][0])

    # using the uk calculations
    daqi_uk, aqi_data_uk = daqi_uk.get_daqi(pm10_24h=mean_pm10_24h, pm25_24h=mean_pm25_24h, so2_15m=recent_so2, no2_1h=mean_no2_1h, o3_1h=mean_o3_1h)

    # Find the pollutant with the maximum AQI value
    max_pollutant_uk = max(aqi_data_uk, key=lambda k: aqi_data_uk[k][0])

    # AQI using the Korean calculations
    cai_kr, aqi_data_kr = cai_kr.get_aqi(pm10_24h=mean_pm10_24h, pm25_24h=mean_pm25_24h, no2_1h=mean_no2_1h, so2_1h=mean_so2_1h, o3_1h=mean_o3_1h)

    # Find the pollutant with the maximum AQI value
    max_pollutant_kr = max(aqi_data_kr, key=lambda k: aqi_data_kr[k][0])

    # AQI using the Canadian calculations
    aqhi_ca, aqi_data_ca, _ = aqhi_ca.get_aqhi(pm10_3h=mean_pm10_3h, pm25_3h=mean_pm25_3h, no2_3h=mean_no2_3h, o3_3h=mean_o3_3h)

    return aqi_sg, aqi_data_sg, max_pollutant_sg, aqi_us, aqi_data_us, max_pollutant_us, aqi_au, aqi_data_au, max_pollutant_au, caqi_eu, aqi_data_eu, aqi_cn, aqi_data_cn, max_pollutant_cn, daqi_uk, aqi_data_uk, max_pollutant_uk, cai_kr, aqi_data_kr, max_pollutant_kr, aqhi_ca, aqi_data_ca, recent_data_1h, mean_co_1h, mean_no2_1h, mean_o3_1h, mean_pm10_1h, mean_pm25_1h, mean_so2_1h

# def send_alert(aqi_us):
#     # Sends an alert via Pushover if AQI is above the unhealthy threshold
#     push = http.client.HTTPSConnection("api.pushover.net:443")
#     push.request("POST", "/1/messages.json",
#         urllib.parse.urlencode({
#             "token": PUSHOVER_API_TOKEN,
#             "user": PUSHOVER_USER_KEY,
#             "message": f"Alert! The AQI in Bangkok is {aqi_us}, which is above the unhealthy threshold of {UNHEALTHY_THRESHOLD}."
#         }), { "Content-type": "application/x-www-form-urlencoded" })
#     response = push.getresponse()
#     if response.status == 200:
#         print("Alert sent successfully.")
#     else:
#         print(f"Failed to send alert: {response.status} - {response.read().decode()}")

def streamlit_dashboard(aqi_df, aqi_sg, aqi_data_sg, max_pollutant_sg, aqi_us, aqi_data_us, max_pollutant_us, aqi_au, aqi_data_au, max_pollutant_au, caqi_eu, aqi_data_eu, aqi_cn, aqi_data_cn, max_pollutant_cn, daqi_uk, aqi_data_uk, max_pollutant_uk, cai_kr, aqi_data_kr, max_pollutant_kr, aqhi_ca, aqi_data_ca, recent_data_1h, mean_co_1h, mean_no2_1h, mean_o3_1h, mean_pm10_1h, mean_pm25_1h, mean_so2_1h):
    st.set_page_config(layout="wide")
    st.title('Bangkok Air Quality Index (AQI) Dashboard')
    st.write('This dashboard provides real-time air quality data for Bangkok, Thailand.')
    option = st.sidebar.radio(
        "Select the AQI calculation method:",
        ('Australia', 'EU', 'China', 'US', 'Korea', 'UK', 'Canada', 'Singapore')
    )
    # refresh_interval = st.sidebar.selectbox("Select refresh interval (seconds):", [5, 10, 30, 60, 120, 300])

    # Create two rows
    row1_1, row1_2 = st.columns(2)

    # Add content to the first row, first column
    with row1_1:
        st.subheader("Bangkok's Air Quality Problem")

        st.image('./assets/tuktuk.jpg', caption='Bangkok Tuk Tuk')
    # Add content to the first row, second column
    with row1_2:
        st.subheader('Current Weather Data')
        st.write('Temperature:', recent_data_1h['temperature'].iloc[-1], '°C')
        st.write('Humidity:', recent_data_1h['h'].iloc[-1], '%')
        st.write('Pressure:', recent_data_1h['pressure'].iloc[-1], 'mbar')
        st.write('Wind Speed:', recent_data_1h['wind'].iloc[-1], 'm/s')
        st.subheader('Current Air Quality Data')
        if option == 'Australia':
            st.write('Australia AQI:', aqi_au)
            st.write('Pollutant with the maximum AQI value:', max_pollutant_au)
            st.write('Australia AQI General Message:', aqi_data_au[max_pollutant_au][1])
            st.write('Australia AQI Health Message:', aqi_data_au[max_pollutant_au][2])
        elif option == 'EU':
            st.write('EU CAQI:', caqi_eu)
        elif option == 'China':
            st.write('China AQI:', aqi_cn)
            st.write('Pollutant with the maximum AQI value:', max_pollutant_cn)
            st.write('China AQI General Message:', aqi_data_cn[max_pollutant_cn][1])
            st.write('China AQI Health Message:', aqi_data_cn[max_pollutant_cn][2])
        elif option == 'US':
            st.write('US AQI:', aqi_us)
            st.write('Pollutant with the maximum AQI value:', max_pollutant_us)
            st.write('US AQI General Message:', aqi_data_us[max_pollutant_us][1])
            st.write('US AQI Health Message:', aqi_data_us[max_pollutant_us][2])
        elif option == 'Korea':
            st.write('Korea CAI:', cai_kr)
            st.write('Pollutant with the maximum CAI value:', max_pollutant_kr)
            st.write('Korea CAI General Message:', aqi_data_kr[max_pollutant_kr][1])
            st.write('Korea CAI Health Message:', aqi_data_kr[max_pollutant_kr][2])
        elif option == 'UK':
            st.write('UK DAQI:', daqi_uk)
            st.write('Pollutant with the maximum DAQI value:', max_pollutant_uk)
            st.write('UK DAQI General Message:', aqi_data_uk[max_pollutant_uk][1])
            st.write('UK DAQI Health Message:', aqi_data_uk[max_pollutant_uk][2])
        elif option == 'Canada':
            st.write('Canada AQI:', aqhi_ca)
        elif option == 'Singapore':
            st.write('Singapore PSI:', aqi_sg)
            st.write('Pollutant with the maximum AQI value:', max_pollutant_sg)
            st.write('Singapore PSI General Message:', aqi_data_sg[max_pollutant_sg][1])
            st.write('Singapore PSI Health Message:', aqi_data_sg[max_pollutant_sg][2])

    # Create the second row
    row2 = st.container()

    # Add content to the second row
    with row2:
        st.subheader('Current Pollutant Levels')
        st.write("These are the current pollutant levels; however, notice that the different country's methods yield different AQI values.")
        pollutants = ['co ppm', 'no2 ppm', 'o3 ppm', 'pm10 μg/m3', 'pm25 μg/m3', 'so2 ppm']
        mean_values = [mean_co_1h, mean_no2_1h, mean_o3_1h, mean_pm10_1h, mean_pm25_1h, mean_so2_1h]

        fig, ax1 = plt.subplots(figsize=(10, 2.5))  
        fig.patch.set_facecolor('black')
        ax1.set_facecolor('black')

        color = 'tab:blue'
        ax1.set_xlabel('Pollutants', color='white')
        ax1.set_ylabel('Mean Values (1h) - Gases', color=color)
        ax1.bar(pollutants[:3] + pollutants[5:], mean_values[:3] + mean_values[5:], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.tick_params(axis='x', colors='white')

        ax2 = ax1.twinx()  
        color = 'tab:orange'
        ax2.set_ylabel('Mean Values (1h) - Particulates', color=color)
        ax2.bar(pollutants[3:5], mean_values[3:5], color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        ax1.set_title('Mean Values of Pollutants in the Last 1 Hour', color='white')

        fig.tight_layout()  

        st.pyplot(fig)

def main():
    global unhealthy_alert_sent, aqi_df, aqi_sg, aqi_data_sg, max_pollutant_sg, aqi_us, aqi_data_us, max_pollutant_us, aqi_au, aqi_data_au, max_pollutant_au, caqi_eu, aqi_data_eu, aqi_cn, aqi_data_cn, max_pollutant_cn, daqi_uk, aqi_data_uk, max_pollutant_uk, cai_kr, aqi_data_kr, max_pollutant_kr, aqhi_ca, aqi_data_ca, recent_data_1h, mean_co_1h, mean_no2_1h, mean_o3_1h, mean_pm10_1h, mean_pm25_1h, mean_so2_1h  # Declare all globals
    aqi_us = None
    try:
        aqi_data = get_aqi_data()
        if aqi_data is None:
            st.error("Failed to fetch AQI data. Check your API key and network connection.")
            return  # Stop execution if data fetching fails
        
        # Correctly unpack the returned values:
        results = process_aqi_data(aqi_data)
        if results: # Check if process_aqi_data returned successfully
            aqi_sg, aqi_data_sg, max_pollutant_sg, aqi_us, aqi_data_us, max_pollutant_us, aqi_au, aqi_data_au, max_pollutant_au, caqi_eu, aqi_data_eu, aqi_cn, aqi_data_cn, max_pollutant_cn, daqi_uk, aqi_data_uk, max_pollutant_uk, cai_kr, aqi_data_kr, max_pollutant_kr, aqhi_ca, aqi_data_ca, recent_data_1h, mean_co_1h, mean_no2_1h, mean_o3_1h, mean_pm10_1h, mean_pm25_1h, mean_so2_1h = results
        else:
            st.error("Failed to process AQI data.")
            return # Stop execution if processing fails
        

        streamlit_dashboard(aqi_df, aqi_sg, aqi_data_sg, max_pollutant_sg, aqi_us, aqi_data_us, max_pollutant_us, aqi_au, aqi_data_au, max_pollutant_au, caqi_eu, aqi_data_eu, aqi_cn, aqi_data_cn, max_pollutant_cn, daqi_uk, aqi_data_uk, max_pollutant_uk, cai_kr, aqi_data_kr, max_pollutant_kr, aqhi_ca, aqi_data_ca, recent_data_1h, mean_co_1h, mean_no2_1h, mean_o3_1h, mean_pm10_1h, mean_pm25_1h, mean_so2_1h)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()