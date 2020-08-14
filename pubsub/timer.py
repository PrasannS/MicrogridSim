import paho.mqtt.client as mqtt
import json
import time

broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

timestep = 1


print("process started")

client.publish(topic="timestep", payload=timestep, qos=1, retain=False)
timestep+=1
received = 0

def on_received(client, userdata, message):
    global received
    global timestep
    received +=1
    #print("RECEIVED MESSAGE"+ str(json.loads(message.payload.decode())))
    print("RECEIVED "+str(received))
    if received==5:
        time.sleep(.01)
        received = 0
        client.publish(topic="timestep", payload=timestep, qos=1, retain=False)
        timestep+=1

        print("Timestep is - "+str(timestep))


client.subscribe("battery", qos=1)
client.subscribe("controls", qos=1)
client.subscribe("climate_predictions", qos=1)
client.subscribe("renewables_prediction", qos=1)
client.subscribe("market_predictions", qos=1)
client.message_callback_add("battery", on_received)
client.message_callback_add("controls", on_received)
client.message_callback_add("climate_predictions", on_received)
client.message_callback_add("renewables_prediction", on_received)
client.message_callback_add("market_predictions", on_received)
client.loop_forever()