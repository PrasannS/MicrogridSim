broker_url = "mqtt.eclipse.org"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

climate = pd.read_csv('../data/load_profile/Climate_HourlyWeather.csv')
drop = ['Data Quality', 'Temp Flag', 'Dew Point Temp Flag', 'Wind Spd Flag', 'Stn Press Flag',
        'Hmdx Flag', 'Wind Chill Flag', 'Wind Dir Flag', 'Rel Hum Flag', 'Visibility Flag']
climate = climate.drop(columns = drop, axis=1)

def on_weather_advance(client, userdata, message):
    global climate
    timestep = message.payload.decode()['timestep']
    print("Timer Advanced: "+timestep)
    weather_predictions = weatherdata.iloc[math.floor(timestep/60):math.floor(timestep/60)+weather_pred_depth]
    data['weather_predictions'] = weather_predictions
    data['timestep'] = timestep
    client.publish(topic="climate-predictions", payload=data, qos=1, retain=False)

client.subscribe("climate", qos=1)
client.message_callback_add("climate", on_weather_advance)

client.loop_forever()