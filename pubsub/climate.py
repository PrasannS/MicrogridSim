import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
import math
import json

broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

climate = pd.read_csv('../data/load_profile/Climate_HourlyWeather.csv')
drop = ['Data Quality', 'Temp Flag', 'Dew Point Temp Flag', 'Wind Spd Flag', 'Stn Press Flag',
        'Hmdx Flag', 'Wind Chill Flag', 'Wind Dir Flag', 'Rel Hum Flag', 'Visibility Flag']
climate = climate.drop(columns = drop, axis=1)

def on_timer_advance(client, userdata, message):
    newdata = json.loads(message.payload.decode())

    global climate
    data = {}
    timestep = int(message.payload.decode())
    print("Timer Advanced: "+str(timestep))
    weather_params = climate.iloc[math.floor(timestep/60)][0]
    data['weather_params'] = weather_params
    data['timestep'] = timestep
    client.publish(topic="climate", payload=json.dumps(data), qos=1, retain=False)

client.subscribe("timestep", qos=1)
client.message_callback_add("timestep", on_timer_advance)

client.loop_forever()
