
from __future__ import division
import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
from pylab import rcParams
import random
import statistics
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import pickle
import math



num_houses = 4


broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

received = 0
timestep = 0

energy_price = 0
climate = {}
climate_prediction = []
market_prediction = []
battery_state = {}
pv = 0
wind = 0
pv_prediction = []
wind_prediction = []

loads = []

num_received = 0

#TODO global client added literally everywhere I think

#Given that all of the data for the iteration has been received,
#process the data and send the necessary controls
def get_controls():
    global timestep
    #This code is temporary
    load_controls = []
    tmp = {}
    defaults = [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True,]
    for i in range(0, num_houses):
        tmp['id'] = i
        tmp['controls'] = defaults
        load_controls.append(tmp)
    controls = {}
    controls['battery'] = 0
    controls['timestep'] = timestep

    return controls, load_controls

def run_num_received():
    global num_received
    global client
    print(num_received)
    num_received+=1
    if num_received==6:
        controls, load_controls = get_controls()
        client.publish(topic="controls", payload=json.dumps(controls), qos=1, retain=False)
        for i in range(0, num_houses):
            client.publish(topic="control-"+str(i), payload=json.dumps(load_controls[i]), qos=1, retain=False)
        num_received = 0

def on_renewable_prediction(client, userdata, message):
    print("ren_predict")
    newdata = json.loads(message.payload.decode())

    global pv_prediction
    global wind_prediction
    global pv
    global wind
    
    pv = newdata['pv_output']
    wind = newdata['wind_output']
    pv_prediction = newdata['pv_predictions']
    wind_prediction = newdata['pv_predictions']
    run_num_received()

def on_climate(client, userdata, message):
    print("climate")
    print(message.payload.decode())
    newdata = json.loads(message.payload.decode())

    global climate
    
    climate = newdata['weather_params']
    run_num_received()

def on_market(client, userdata, message):
    print("market")
    newdata = json.loads(message.payload.decode())

    global energy_price
    
    energy_price = newdata['energy_price']
    run_num_received()

def on_climate_prediction(client, userdata, message):
    print("clim_predict")
    newdata = json.loads(message.payload.decode())

    global climate_prediction

    
    climate_prediction = newdata['weather_predictions']
    run_num_received()

def on_market_prediction(client, userdata, message):

    print("market_predict")
    newdata = json.loads(message.payload.decode())

    global market_prediction

    
    market_prediction = newdata['market_predictions']
    run_num_received()

def on_battery(client, userdata, message):

    print("battery")
    newdata = json.loads(message.payload.decode())

    global battery_states

    
    battery_state = message.payload.decode()
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