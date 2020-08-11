broker_url = "mqtt.eclipse.org"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

pv = pd.read_csv('../data/solar/Actual_44.05_-92.45_2006_DPV_20MW_5_Min.csv')
wind = pd.read_csv('../data/wind/wind_data.csv')

wind_num = 0
pv_num = 0
pv_pred_depth = 200
wind_pred_depth = 400

def on_renewables_advance(client, userdata, message):
    global pv
    global wind
    global wind_num
    global pv_num
    global pv_pred_depth
    global wind_pred_depth


    timestep = message.payload.decode()['timestep']
    print("Timer Advanced: "+timestep)

    
    pv_predictions = pvdata['Power(MW)'].iloc[math.floor(timestep/5):math.floor(timestep/5)+pv_pred_depth] *1000
    wind_predictions = winddata['LV ActivePower (kW)'].iloc[math.floor(timestep/10):math.floor(timestep/10)+wind_pred_depth]
    
    data['pv_predictions'] = pv_predictions*pv_num
    data['wind_predictions'] = wind_predictions*wind_num

    data['timestep'] = timestep
    client.publish(topic="renewables_prediction", payload=data, qos=1, retain=False)


client.subscribe("renewables_ouput", qos=1)
client.message_callback_add("renewables_ouput", on_renewables_advance)

client.loop_forever()