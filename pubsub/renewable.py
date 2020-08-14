import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
import math
import json


pv = pd.read_csv('../data/solar/Actual_44.05_-92.45_2006_DPV_20MW_5_Min.csv')
wind = pd.read_csv('../data/wind/wind_data.csv')


broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

wind_num = 1
pv_num = 1

def on_weather_advance(client, userdata, message):
    global pv
    global wind
    global wind_num
    global pv_num
    data = {}
    newdata = json.loads(message.payload.decode())


    timestep = newdata['timestep']
    print("Timer Advanced: "+str(timestep))

    pv_output = pv.iloc[math.floor(timestep/5)]['Power(MW)']*1000

    wind_output = wind.iloc[math.floor(timestep/10)]['LV ActivePower (kW)']
    
    data['pv_output'] = pv_output*pv_num
    data['wind_output'] = wind_output*wind_num

    data['timestep'] = timestep


    print(data)
    print("PUBLISHING")
    client.publish(topic="renewables_ouput", payload=json.dumps(data), qos=2, retain=True)


client.subscribe("climate", qos=1)
client.message_callback_add("climate", on_weather_advance)

client.loop_forever()