import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
import json

broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

capacity = 20000
charged = 0

def on_timer_advance(client, userdata, message):
    global capacity
    global charged
    timestep = int(message.payload.decode())
    print("Timer Advanced: "+str(timestep))

    data = {}

    data['capacity'] = capacity
    data['charged'] = charged
    data['timestep'] = timestep
    client.publish(topic="battery", payload=json.dumps(data), qos=1, retain=False)

def on_receive_control(client, userdata, message):
    global charged
    newdata = json.loads(message.payload.decode())
    change = newdata['battery']
    charged += change


client.subscribe("timestep", qos=1)
client.subscribe("controls", qos=1)
client.message_callback_add("timestep", on_timer_advance)
client.message_callback_add("controls", on_receive_control)


client.loop_forever()