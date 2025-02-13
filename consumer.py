import json
import sqlite3
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import time

'''
example data: {'aqi': 138, 'co': 0.1, 'h': 48, 'no2': 2.4, 'o3': 19.4, 'pressure': 1010, 'pm10': 58, 'pm25': 138, 'so2': 0.6, 'temperature': 30, 'wind': 2, 'time_iso': '2025-02-13T20:00:00+07:00', 'city_geo': [13.7563309, 100.5017651], 'city_name': 'Bangkok'}
'''

# Load environment variables
KAFKA_TOPIC = 'bkk-aqi'
KAFKA_BROKER = 'localhost:9092'

def sql_connect():
    conn = sqlite3.connect('data/bkk_aqi.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS aqi_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aqi INTEGER,
            co REAL,
            h INTEGER,
            no2 REAL,
            o3 REAL,
            pressure INTEGER,
            pm10 INTEGER,
            pm25 INTEGER,
            so2 REAL,
            temperature INTEGER,
            wind INTEGER,
            time_iso TEXT,
            city_geo_lat REAL,
            city_geo_lon REAL,
            city_name TEXT
        )
    ''')
    conn.commit()
    return conn, c

def consume_and_store():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='bkk-aqi-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    conn, c = sql_connect()

    for message in consumer:
        data = message.value
        timestamp = data.get('timestamp')
        aqi = data.get('aqi')
        c.execute('SELECT * FROM aqi_data ORDER BY id DESC LIMIT 1')
        last_row = c.fetchone()
        
        if last_row:
            last_data = {
            'aqi': last_row[1],
            'co': last_row[2],
            'h': last_row[3],
            'no2': last_row[4],
            'o3': last_row[5],
            'pressure': last_row[6],
            'pm10': last_row[7],
            'pm25': last_row[8],
            'so2': last_row[9],
            'temperature': last_row[10],
            'wind': last_row[11],
            'time_iso': last_row[12],
            'city_geo': [last_row[13], last_row[14]],
            'city_name': last_row[15]
            }
            
            if data == last_data:
                print("Data is the same as the last entry, skipping insert.")
                continue
        c.execute('''
            INSERT INTO aqi_data (aqi, co, h, no2, o3, pressure, pm10, pm25, so2, temperature, wind, time_iso, city_geo_lat, city_geo_lon, city_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('aqi'),
            data.get('co'),
            data.get('h'),
            data.get('no2'),
            data.get('o3'),
            data.get('pressure'),
            data.get('pm10'),
            data.get('pm25'),
            data.get('so2'),
            data.get('temperature'),
            data.get('wind'),
            data.get('time_iso'),
            data.get('city_geo')[0],
            data.get('city_geo')[1],
            data.get('city_name')
        ))
        conn.commit()
        print(f"Inserted data: {data}")

    conn.close()

if __name__ == "__main__":
    consume_and_store()