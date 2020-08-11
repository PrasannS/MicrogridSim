
num_houses = 4


broker_url = "mqtt.eclipse.org"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

received = 0
timestep = 0

energy_price = 0
climate = {}
climate_prediction = []
market_prediction = []
battery_state = {}
pv = 0
wind = 0
pv_prediction = []
wind_prediction = []

num_received = 0

controls =  []

#TODO global client added literally everywhere I think

#Given that all of the data for the iteration has been received,
#process the data and send the necessary controls
def get_controls():
    global timestep

def run_num_received():
    global num_received
    global client
    global controlss
    num+=1
    if num==7:
        get_controls()
        client.publish(topic="controls", payload=controls, qos=1, retain=False)
        num = 0

def on_renewable_prediction(client, userdata, messages):
    global pv_prediction
    global wind_prediction
    
    pv_prediction = message.payload.decode()['pv_predictions']
    wind_prediction = message.payload.decode()['pv_predictions']
    run_num_received()


def on_renewable(client, userdata, messages):
    global pv
    global wind
    global timestep
    timesteps = message.payload.decode()['timestep']
    pv = message.payload.decode()['pv_output']
    wind = message.payload.decode()['wind_output']
    run_num_received()

def on_climate(client, userdata, messages):
    global climate
    
    climate = message.payload.decode()['weather_params']
    run_num_received()


def on_market(client, userdata, messages):
    global energy_price
    
    energy_price = message.payload.decode()['energy_price']
    run_num_received()


def on_climate_prediction(client, userdata, messages):
    global climate_prediction

    
    climate_prediction = message.payload.decode()['climate_predictions']
    run_num_received()

def on_market_prediction(client, userdata, messages):
    global market_prediction

    
    market_prediction = message.payload.decode()['market_predictions']
    run_num_received()


def on_battery(client, userdata, messages):
    global battery_states

    
    battery_state = message.payload.decode()
    run_num_received()



client.subscribe("battery", qos=1)
client.subscribe("climate", qos=1)
client.subscribe("climate_prediction", qos=1)
client.subscribe("renewables", qos=1)
client.subscribe("renewables_prediction", qos=1)
client.subscribe("market", qos=1)
client.subscribe("market_prediction", qos=1)
client.message_callback_add("battery", on_battery)
client.message_callback_add("climate", on_climate)
client.message_callback_add("market", on_market)
client.message_callback_add("renewables", on_renewable)
client.message_callback_add("climate_prediction", on_climates)
client.message_callback_add("renewables_prediction", on_renewable_prediction)
client.message_callback_add("market_prediction", on_market_prediction)

client.loop_forever()