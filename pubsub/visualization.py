import plotly.graph_objects as go

import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
import json


import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import redis

import psycopg2

received = 0
timestep = 0

energy_price = [0]
climate = []
climate_prediction = []
market_prediction = []
battery_state = []
pv = [0]
wind = [0]
pv_prediction = []
wind_prediction = []

loads = []

num_received = 0

num_houses = 4

CONNECTION = "postgres://admin:admin@localhost:5432/testdb"

conn = psycopg2.connect(CONNECTION)
# insert_data(conn)
cur = conn.cursor()


broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_connection = redis.Redis(connection_pool=pool)
pipe = redis_connection.pipeline()


weather_cols = ['Date', 'Year', 'Month', 'Day', 'Time', 'Temperature', 'Dew Point Temp',
                'Rel Humidity', 'Wind Dir', 'Wind Spd', 'Visibility', 'Stn Press', 'Hmdx', 'Wind Chill',
                'Weather']

load_infos = ['B1E', 'B1E_INFO', 'B2E', 'B2E_INFO', 'BME', 'BME_INFO', 'CDE', 'CDE_INFO', 'CWE', 'CWE_INFO', 'DNE', 'DNE_INFO', 'DWE', 'DWE_INFO', 'EBE', 'EBE_INFO', 'EQE', 'EQE_INFO','FGE', 'FGE_INFO', 'FRE', 'FRE_INFO', 'GRE', 'GRE_INFO', 'HPE', 'HPE_INFO', 'HTE', 'HTE_INFO', 'OFE', 'OFE_INFO', 'OUE', 'OUE_INFO', 'RSE', 'RSE_INFO', 'TVE', 'TVE_INFO', 'UTE', 'UTE_INFO']


def init_tables():
    global cur

    creates = []

    creates.append("""CREATE TABLE weather (
                                        date TEXT,
                                        weather TEXT, 
                                        dewpoint DOUBLE PRECISION,
                                        relhumidity DOUBLE PRECISION,
                                        winddir DOUBLE PRECISION,
                                        windspd DOUBLE PRECISION,
                                        visibility DOUBLE PRECISION,
                                        stnpress DOUBLE PRECISION,
                                        hmdx DOUBLE PRECISION,
                                        windchill DOUBLE PRECISION,
                                        temp DOUBLE PRECISION,
                                        timestep INTEGER,
                                    );""")

    creates.append("SELECT create_hypertable('weather', 'timestep');")

    creates.append("""CREATE TABLE market (
                                        price DOUBLE PRECISION, 
                                        timestep INTEGER,
                                    );""")

    creates.append("SELECT create_hypertable('market', 'timestep');")

    creates.append("""CREATE TABLE renewable (
                                        wind DOUBLE PRECISION, 
                                        solar DOUBLE PRECISION,s
                                        timestep INTEGER,
                                    );""")

    creates.append("SELECT create_hypertable('renewable', 'timestep');")

    creates.append("""CREATE TABLE battery (
                                        charged DOUBLE PRECISION,
                                        timestep INTEGER,
                                    );""")

    creates.append("SELECT create_hypertable('battery', 'timestep');")

    tmp = ""
    for i in range(0, len(load_infos)):

        if "INFO" not in load_infos[i]:
            tmp+load_infos[i]+" TEXT,\n"

    for i in range(0, num_houses):
        creates.append("""CREATE TABLE load-"""+str(num_houses)+""" (
                                        timestep INTEGER NOT NULL,
                                        """+tmp+"""
                                    );""")
        creates.append("SELECT create_hypertable('load-" +str(num_houses)+"', 'timestep');")

    tmp = ""
    for i in range(0, len(load_infos)):
        if "INFO" not in load_infos[i]:
            tmp += load_infos[i]+" INTEGER,\n"

    for i in range(0, num_houses):
        creates.append("""CREATE TABLE control-"""+str(num_houses)+""" (
                                        timestep INTEGER NOT NULL,
                                        """+tmp+"""
                                    );""")
        creates.append("SELECT create_hypertable('control-" +str(num_houses)+"', 'timestep');")

    for c in creates:
        cur.execute(c)


def run_num_received():
    global num_received
    global client
    global conn
    print(num_received)
    num_received += 1
    if num_received == 6:
        conn.commit()
        num_received = 0


def on_renewable_prediction(client, userdata, message):
    print("ren_predict")
    newdata = json.loads(message.payload.decode())

    data = (newdata['wind_output'], newdata['pv_output'], newdata['timestep'])

    ren = "INSERT INTO renewable (wind, solar, timestep) VALUES (%s ,%s, %s)"

    cur.execute(ren, data)

    run_num_received()

def on_climate(client, userdata, message):
    print("climate")
    print(message.payload.decode())
    newdata = json.loads(message.payload.decode())

    climcols = ['date','weather','dewpoint','relhumidity','winddir','windspd','visibility','stnpress','hmdx','windchill','temp','timestep',]

    ren = "INSERT INTO climate (date,weather,dewpoint,relhumidity,winddir,windspd,visibility,stnpress,hmdx,windchill,temp,timestep,) VALUES (%s ,%s, %s,%s ,%s, %s,%s ,%s, %s,%s ,%s, %s,)"

    tmp = []
    for w in weather_cols:
            tmp.append(newdata[w])
    data = tuple(temp)

    cur.execute(ren, data)
    run_num_received()

def on_market(client, userdata, message):
    print("market")
    newdata = json.loads(message.payload.decode())

    ren = "INSERT INTO market (market,timestep,) VALUES (%s ,%s)"

    data = (newdata['market'], newdata['timestep'])
    
    global cur
    cur.execute(ren, data)

    run_num_received()


def on_climate_prediction(client, userdata, message):
    print("clim_predict")
    newdata = json.loads(message.payload.decode())

    global climate_prediction
    global pipe

    climate_prediction = newdata['weather_predictions']
    pipe.set("climate_prediction", json.dumps(climate_prediction))
    run_num_received()


def on_market_prediction(client, userdata, message):

    print("market_predict")
    newdata = json.loads(message.payload.decode())

    global market_prediction
    global pipe

    market_prediction = newdata['market_predictions']
    pipe.set("market_prediction", json.dumps(market_prediction))
    run_num_received()


def on_battery(client, userdata, message):

    print("battery")
    newdata = json.loads(message.payload.decode())

    ren = "INSERT INTO battery (charged,timestep,) VALUES (%s ,%s)"

    data = (newdata['charged'], newdata['timestep'])
    global cur
    cur.execute(ren, data)

    run_num_received()


loads = [[], [], [], [], [], [], [], [], [], [], [], [], [], [],[], [], [], [], [], [], [], [], [], [], [], [], [], [], ]


def on_load(client, userdata, messasge):
    global loads
    newdata = json.loads(message.payload.decode())


client.subscribe("battery", qos=1)
client.message_callback_add("battery", on_battery)

client.subscribe("climate_predictions", qos=1)
client.message_callback_add("climate_predictions", on_climate_prediction)


client.subscribe("renewables_prediction", qos=1)
client.message_callback_add("renewables_prediction", on_renewable_prediction)


client.subscribe("market", qos=1)
client.message_callback_add("market", on_market)


client.subscribe("market_predictions", qos=1)
client.message_callback_add("market_predictions", on_market_prediction)


for i in range(0, num_houses):
    client.subscribe("load-"+str(i), qos=1)


client.subscribe("climate", qos=1)
client.message_callback_add("climate", on_climate)


client.loop_forever()
