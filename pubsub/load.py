from __future__ import division
import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
from pylab import rcParams
import simpy
import random
import statistics
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import pickle
import math

broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

controllables = ['CDE', 'CWE', 'DWE', 'FGE', 'FRE', 'HPE', 'HTE']
state_connected = ['FGE', 'FRE', 'HPE', 'HTE']
load_data = pickle.load( open( "../data/ampds.p", "rb" ) )

def get_rands_from_data(inputdata, num):

    #print(inputdata)
    data = inputdata.fillna(0)
    hist, bins = np.histogram(data, bins=50)

    bin_midpoints = bins[:-1] + np.diff(bins)/2
    cdf = np.cumsum(hist)
    cdf = cdf / cdf[-1]
    values = np.random.rand(num)
    value_bins = np.searchsorted(cdf, values)
    random_from_cdf = bin_midpoints[value_bins]

    return random_from_cdf

#TODO add some sophistication so that it's time-based
def get_distrs_from_ds(ds):
    distrs = []
    for key in ds.keys():
        if "INFO" not in key:
            distrs.append(ds[key]['apparent'])
    #print(distrs)
    return distrs

# - is_controllable
# - state_connection
# - time_triggers
#add sophistication for the special keys
def init_info(ds ,isDefault):
    infos = []
    controllables = ['CDE', 'CWE', 'DWE', 'FGE', 'FRE', 'HPE', 'HTE']
    state_connected = ['FGE', 'FRE', 'HPE', 'HTE']
    for key in ds.keys():
        if "INFO" not in key:
            tmp = ds[key+"_INFO"]
            if isDefault:
                tmp['is_controllable']= key in controllables
                tmp['state_connection'] = [0.0, 0.0]
                if key in state_connected:
                    tmp['state_connection'] = [0.01, -0.1]
            infos.append(tmp)
    return infos

class Meter(object):

    load_distros = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]
    load_infos = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]

    #structure of load infos - 
    # - is_controllable
    # - state_connection
    #consumption of power by appliances on time step

    loads = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]
    states = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]
    state_targets = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]

    net_load = 0
    #power_thresh = 200
    
    def __init__(self, json_path):
        #params = json.load(open(json_path))
        ""

class House(object):
    
    controls = [False,False,False,False,False,False,False,False,False,False,False,False,False]
    
    meter = Meter('house_params.json')
    
    
    def __init__(self, json_path):
        self.meter.meter = Meter(json_path)

    def get_state(self):
        data = {}
        data['controls'] = self.controls
        data['loads'] = self.meter.loads
        return data


    def update_state(self):
        infos = self.meter.load_infos
        for i in range(0, len(infos)):
            #state connection is in format [effect when on, effect when off], 2 numbers
            #TODO add in state initialization
            if infos[i]['state_connection'][0]>0 and self.controls[i]:
                self.meter.states[i]+=infos[i]['state_connection'][0]
            else :
                self.meter.states[i]+=infos[i]['state_connection'][1]

    def update_loads(self):
        load=0 
        infos = self.meter.load_infos
        for i in range(0, len(infos)):
            if self.controls[i]:
                tmp = get_rands_from_data(self.meter.load_distros[i], 1)[0]
                if len(self.meter.loads)==i:
                    self.meter.loads.append(0)
                self.meter.loads[i]= tmp
                #print(tmp)
        #print(self.meter.load_distros)
        #print(self.meter.loads)


    #critical loads can be treated as 1 in this scenario    
    def get_critical_load(self):
        infos = self.meter.load_infos
        crit_load = 0
        for i in range(0, len(infos)):
            if infos[i]['is_controllable'] == False:
                crit_load+=self.meter.loads[i]
                self.controls[i] = True
        return crit_load
    
    def get_control_loads(self):
        infos = self.meter.load_infos
        load = 0
        for i in range(0, len(infos)):
            if infos[i]['is_controllable']:
                load+=self.meter.loads[i]

        return load

    
    #important to call these 3 at least once before running simulation
    def set_load_distros(self, distros):
        self.meter.load_distros = distros

    def set_dur_distros(self, distros):
        self.duration_distros = distros

    #performs all functions for a typical iteration
    def run_load(self):
        #print("Next")
        self.meter.net_load = 0
        self.update_loads()
        self.meter.net_load+=self.get_critical_load()
        self.meter.net_load+=self.get_control_loads()
        #print(self.meter.load_distros)
        self.update_state()
        #print(self.meter.load_infos)
        #print("LOAD IS"+str(self.meter.net_load))
        return self.meter.net_load

    def set_infos(self, infs):
        self.meter.load_infos = infs
        for i in range(0, len(infs)):
            self.controls.append(not infs[i]['is_controllable'])

total_load =  0
timestep = 0
num_houses = 4
houses = []

infos = init_info(load_data, True)
distrs = get_distrs_from_ds(load_data)

for i in range(0, num_houses):
        h = House('house_params.json')
        h.set_load_distros(distrs)
        #h.meter.infos = infos
        h.set_infos(infos)
        houses.append(h)

    
def on_timer_advance(client, userdata, message):
    newdata = int(message.payload.decode())

    global timestep
    global houses
    data = {}
    tmp = {}
    
    timestep = newdata
    print(str(timestep))

    i = 0
    for h in houses:
        tmp = h.get_state()
        tmp['total'] = h.run_load()
        tmp['timestamp'] = timestep
        tmp['id'] = i
        i+=1
        client.publish(topic="load-"+str(i), payload=json.dumps(data), qos=1, retain=False)

    data['timestep'] = timestep
    data['finished'] = True
    client.publish(topic="loads", payload=json.dumps(data), qos=1, retain=False)

def on_control_received(client, userdata, message):
    newdata = json.loads(message.payload.decode())

    global houses
    load_id = newdata['id']
    houses[i] = newdata['control']


client.subscribe("timestep", qos=1)

for i in range(0, num_houses):
    client.subscribe("control-"+str(i), qos=1)
    client.message_callback_add("control"+str(i), on_control_received)
client.message_callback_add("timestep", on_timer_advance)

client.loop_forever()