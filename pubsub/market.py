import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np

import math
import json

broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

def clean_market_data(df):
    try:
        df['HOEP'] = pd.to_numeric(df['HOEP'].str.replace(',', ''))
    except:
        #print("Already Number")
        ""
    return df

for i in range(2, 20):
    df = pd.DataFrame()
    if(i>9):
        df = df.append(
            pd.read_csv('../data/energy_price/PUB_PriceHOEPPredispOR_20'+str(i)+'.csv', skiprows=3))
    else: 
        df = df.append(
            pd.read_csv('../data/energy_price/PUB_PriceHOEPPredispOR_200'+str(i)+'.csv', skiprows=3))
    df = clean_market_data(df)

market = df

def on_timer_advance(client, userdata, message):

    global market
    data = {}
    timestep = int(message.payload.decode())
    print("Timer Advanced: "+str(timestep))

    market_params = market.iloc[math.floor(timestep/60)]
    energy_price = market_params['HOEP']

    data['market_params'] = market_params[0]
    data['energy_price'] = energy_price
    data['timestep'] = timestep
    client.publish(topic="market", payload=json.dumps(data), qos=1, retain=False)



#weather_predictions = weatherdata.iloc[math.floor(timestep/60):math.floor(timestep/60)+weather_pred_depth]

client.subscribe("timestep", qos=1)
client.message_callback_add("timestep", on_timer_advance)

client.loop_forever()
