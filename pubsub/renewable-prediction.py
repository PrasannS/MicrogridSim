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
pv_pred_depth = 200
wind_pred_depth = 400
# small modification
def on_renewables_advance(client, userdata, message):
    global pv
    global wind
    global wind_num
    global pv_num
    global pv_pred_depth
    global wind_pred_depth
    newdata = json.loads(message.payload.decode())

    data = {}


    timestep = newdata['timestep']
    print(timestep)


    pv_predictions = pv['Power(MW)'].iloc[math.floor(timestep/5):math.floor(timestep/5)+pv_pred_depth] *1000
    wind_predictions = wind['LV ActivePower (kW)'].iloc[math.floor(timestep/10):math.floor(timestep/10)+wind_pred_depth]
    
    data['pv_output']= newdata['pv_output']
    data['wind_output']= newdata['wind_output']
    data['pv_predictions'] = (pv_predictions*pv_num).to_list()
    data['wind_predictions'] = (wind_predictions*wind_num).to_list()

    data['timestep'] = timestep
    client.publish(topic="renewables_prediction", payload=json.dumps(data), qos=1, retain=False)


client.subscribe("renewables_ouput", qos=1)
client.message_callback_add("renewables_ouput", on_renewables_advance)

client.loop_forever()