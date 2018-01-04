#!/usr/bin/python3

import numpy as np
from numpy import linalg as LA
import random
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import seaborn as sns
import math
import cntk as C
from model import action_prediction 
import json


f1 = action_prediction((2,360),(1,32),0.5)
with open('human_observations.json') as json_data:
	data = json.load(json_data)
#print(np.array(data[list(data.keys())[0]]['radardata_list'][0]['observation']).shape)
#print(np.array(data[list(data.keys())[0]]['radardata_list'][0]['vel']))
#print(data.keys())
data_new = {}
actions  = {}
for key in data.keys():
	data_new[key] = []
	actions[key] = []
	observations = np.array(data[key]['radardata_list'])
	for i in range(len(observations)):
		observation = np.array(observations[i]['observation'], dtype=np.float32)
		data_new[key].append(observation)
		
		velocity = np.array(observations[i]['vel'], dtype=np.float32)
		angle    = math.atan2(velocity[1],velocity[0])
		action   = np.zeros((1,32),dtype=np.float32)
		the_angle = int(round(angle*31/360))
		action[the_angle] = 1
		actions[key].append(action)
f1.train_network(data_new, actions)
