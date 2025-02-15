# import libraries
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import sqlite3  
from aqipy import aqi_us
from aqipy import aqi_cn
from aqipy import aqi_au
from aqipy import caqi_eu
from aqipy import cai_kr
from aqipy import daqi_uk
from aqipy import aqhi_ca
from aqipy import psi_sg

# Load data
import os

########################################
# connect to the db and load the data
########################################

conn = sqlite3.connect('./data/bkk_aqi.db')
c = conn.cursor()
aqi_data = pd.read_sql_query("SELECT * FROM aqi_data", conn)
aqi_data['time_iso'] = pd.to_datetime(aqi_data['time_iso'])
aqi_data = aqi_data.set_index('time_iso')

########################################
# organize the necessary data
########################################

# Pull the most recent so2 data
recent_so2 = aqi_data['so2'].iloc[-1]

# Pull the most recent 1 hours of data
recent_data_1h = aqi_data[aqi_data.index >= (aqi_data.index.max() - pd.Timedelta(hours=1))]

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
recent_data_3h = aqi_data[aqi_data.index >= (aqi_data.index.max() - pd.Timedelta(hours=3))]

# Calculate the mean of the recent 3 hours of data for pm10, pm25, o3, so2, no2 and co
mean_pm10_3h = recent_data_3h['pm10'].mean()
mean_pm25_3h = recent_data_3h['pm25'].mean()
mean_o3_3h = recent_data_3h['o3'].mean()
mean_so2_3h = recent_data_3h['so2'].mean()
mean_no2_3h = recent_data_3h['no2'].mean()
mean_co_3h = recent_data_3h['co'].mean()

# Pull the most recent 4 hours of data
recent_data_4h = aqi_data[aqi_data.index >= (aqi_data.index.max() - pd.Timedelta(hours=4))]

# Calculate the mean of the recent 4 hours of data for o3
mean_o3_4h = recent_data_4h['o3'].mean()

# Pull the most recent 8 hours of data
recent_data_8h = aqi_data[aqi_data.index >= (aqi_data.index.max() - pd.Timedelta(hours=8))]

# Calculate the mean of the recent 8 hours of data for o3 and co
mean_o3_8h = recent_data_8h['o3'].mean()
mean_co_8h = recent_data_8h['co'].mean()

# Pull the most recent 24 hours of data
recent_data_24h = aqi_data[aqi_data.index >= (aqi_data.index.max() - pd.Timedelta(hours=24))]

# Calculate the mean of the recent 24 hours of data for pm10, pm25, co2 and so2
mean_pm10_24h = recent_data_24h['pm10'].mean()
mean_pm25_24h = recent_data_24h['pm25'].mean()
mean_so2_24h = recent_data_24h['so2'].mean()
mean_co_24h = recent_data_24h['co'].mean()

########################################
# Necessary values for the different country AQI calculations
########################################

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

########################################
# Streamlit
########################################
st.set_page_config(layout="wide")
st.title('Bangkok Air Quality Index (AQI) Dashboard')
st.write('This dashboard provides real-time air quality data for Bangkok, Thailand.')
option = st.sidebar.radio(
    "Select the AQI calculation method:",
    ('Australia', 'EU', 'China', 'US', 'Korea', 'UK', 'Canada', 'Singapore')
)
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

    st.markdown("""
        <div style='font-size: 10px; line-height: 1;'>
            source: https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf<br>
            source: https://www.airnow.gov/sites/default/files/2018-05/aqi-technical-assistance-document-may2016.pdf<br>
            source: https://www.haze.gov.sg/docs/default-source/faq/computation-of-the-pollutant-standards-index-(psi).pdf<br>
            source: https://www.eea.europa.eu/themes/air/air-quality-index<br>
            source: https://uk-air.defra.gov.uk/assets/documents/reports/cat14/1304251155_Update_on_Implementation_of_the_DAQI_April_2013_Final.pdf<br>
            source: https://www.airqualityontario.com/science/aqhi/<br>
            source: https://www.airqualitynow.eu/download/CITEAIR-Comparing_Urban_Air_Quality_across_Borders.pdf<br>
            source: https://www.airkorea.or.kr/web/last_amb_hour_data?pMENU_NO=123<br>
            source: http://www.airkorea.or.kr/eng/khaiInfo?pMENU_NO=166<br>
            source: https://core.ac.uk/download/pdf/38094372.pdf<br>
            source: https://www.environment.nsw.gov.au/topics/air/understanding-air-quality-data/air-quality-index
        </div>
    """, unsafe_allow_html=True)

