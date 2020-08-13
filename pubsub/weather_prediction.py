import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np

import json
import math


broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

climate = pd.read_csv('../data/load_profile/Climate_HourlyWeather.csv')
drop = ['Data Quality', 'Temp Flag', 'Dew Point Temp Flag', 'Wind Spd Flag', 'Stn Press Flag',
        'Hmdx Flag', 'Wind Chill Flag', 'Wind Dir Flag', 'Rel Hum Flag', 'Visibility Flag']
climate = climate.drop(columns = drop, axis=1)

weather_pred_depth = 1000

def on_weather_advance(client, userdata, message):
    
    newdata = json.loads(message.payload.decode())

    data = {}

    global climate
    global weather_pred_depth
    timestep = newdata['timestep']
    print(str(timestep))
    weather_predictions = climate.iloc[math.floor(timestep/60):math.floor(timestep/60)+weather_pred_depth]
    data['weather_predictions'] = weather_predictions.to_dict('records')
    data['timestep'] = timestep
    client.publish(topic="climate_predictions", payload=json.dumps(data), qos=1, retain=False)

client.subscribe("climate", qos=1)
client.message_callback_add("climate", on_weather_advance)

client.loop_forever()