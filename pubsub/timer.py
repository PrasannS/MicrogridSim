import paho.mqtt.client as mqtt

broker_url = "mqtt.eclipse.org"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

timestep = 1


client.publish(topic="timestep", payload=timestep, qos=1, retain=False)
timestep+=1
received = 0

def on_received(client, userdata, messages):
    global received
    received +=1
    if received==5:
        received = 0
        client.publish(topic="timestep", payload=timestep, qos=1, retain=False)
        timestep+=1


client.subscribe("battery", qos=1)
client.subscribe("controls", qos=1)
client.subscribe("climate_prediction", qos=1)
client.subscribe("renewables_prediction", qos=1)
client.subscribe("market_prediction", qos=1)
client.message_callback_add("battery", on_received)
client.message_callback_add("controller", on_received)
client.message_callback_add("climate_prediction", on_received)
client.message_callback_add("renewables_prediction", on_received)
client.message_callback_add("market_prediction", on_received)
client.loop_forever()