import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
import math
import json

broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

pv = pd.read_csv('../data/solar/Actual_44.05_-92.45_2006_DPV_20MW_5_Min.csv')
wind = pd.read_csv('../data/wind/wind_data.csv')

wind_num = 0
pv_num = 0

def on_weather_advance(client, userdata, message):
    global pv
    global wind
    global wind_num
    global pv_num
    data = {}
    newdata = json.loads(message.payload.decode())


    timestep = newdata['timestep']
    print("Timer Advanced: "+str(timestep))

    pv_output = pv['Power(MW)'].iloc[math.floor(timestep/5)]*1000
    #pv_predictions = pvdata['Power(MW)'].iloc[math.floor(timestep/5):math.floor(timestep/5)+pv_pred_depth] *1000

    wind_output = wind['LV ActivePower (kW)'].iloc[math.floor(timestep/10)]
    #wind_predictions = winddata['LV ActivePower (kW)'].iloc[math.floor(timestep/10):math.floor(timestep/10)+wind_pred_depth]
    
    data['pv_output'] = pv_output*pv_num
    data['wind_output'] = wind_output*wind_num

    data['timestep'] = timestep
    print("PUBLISHING")
    client.publish(topic="renewables_ouput", payload=json.dumps(data), qos=2, retain=True)


client.subscribe("climate", qos=1)
client.message_callback_add("climate", on_weather_advance)

client.loop_forever()