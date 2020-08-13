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


broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_connection = redis.Redis(connection_pool=pool)
pipe = redis_connection.pipeline()

def run_num_received():
    global num_received
    global client
    global pipe
    print(num_received)
    num_received+=1
    if num_received==6:
        pipe.execute()
        num_received = 0

def on_renewable_prediction(client, userdata, message):
    print("ren_predict")
    newdata = json.loads(message.payload.decode())

    global pv
    global wind
    global pipe
    
    pv.append(newdata['pv_output'])
    wind.append(newdata['wind_output'])
    pv_prediction = newdata['pv_predictions']
    wind_prediction = newdata['pv_predictions']
    run_num_received()

    pipe.set('pv_predicted', json.dumps(pv_prediction))
    pipe.set('wind_predicted', json.dumps(pv_prediction))
    pipe.set('pv', json.dumps(pv))
    pipe.set('wind', json.dumps(wind))


def on_climate(client, userdata, message):
    print("climate")
    print(message.payload.decode())
    newdata = json.loads(message.payload.decode())

    global climate
    global pipe

    climate.append(newdata['weather_params'])

    pipe.set("climate", json.dumps(climate))
    run_num_received()


def on_market(client, userdata, message):
    print("market")
    newdata = json.loads(message.payload.decode())

    global energy_price
    global pipe
    
    energy_price.append(newdata['energy_price'])
    pipe.set("market", json.dumps(energy_price))
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

    
    global battery_state

    
    battery_state.append(newdata)
    pipe.set("battery", json.dumps(battery_state))
    run_num_received()



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
