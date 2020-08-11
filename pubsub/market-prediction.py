import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np

broker_url = "mqtt.eclipse.org"
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
            pd.read_csv('./data/energy_price/PUB_PriceHOEPPredispOR_20'+str(i)+'.csv', skiprows=3))
    else: 
        df = df.append(
            pd.read_csv('./data/energy_price/PUB_PriceHOEPPredispOR_200'+str(i)+'.csv', skiprows=3))
    df = clean_market_data(df)

market = df

def on_market_advance(client, userdata, message):
    global market
    timestep = message.payload.decode()['timestep']
    print("Timer Advanced: "+timestep)

    market_predictions = market['HOEP'].iloc[math.floor(timestep/60):math.floor(timestep/60)+market_pred_depth]

    data['market_predictions'] = market_predictions

    data['timestep'] = timestep
    client.publish(topic="market_predictions", payload=data, qos=1, retain=False)



#weather_predictions = weatherdata.iloc[math.floor(timestep/60):math.floor(timestep/60)+weather_pred_depth]

client.subscribe("market", qos=1)
client.message_callback_add("market", on_timer_advance)

client.loop_forever()