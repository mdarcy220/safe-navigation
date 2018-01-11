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


#######################
target_dist = 30
target_var = 5
#######################
f1 = action_prediction((1,360),(1,360),(1,32),0.5)


with open('../feature_predicter/training_human_data.json') as json_data:
	data = json.load(json_data)
#print(np.array(data[list(data.keys())[0]]['radardata_list'][0]['observation']).shape)
#print(np.array(data[list(data.keys())[0]]['radardata_list'][0]['vel']))
#print(data.keys())
data_new = {}
actions  = {}
targets = {}
for key in data.keys():
	data_new[key] = []
	actions[key] = []
	targets[key] = []
	observations = np.array(data[key]['radardata_list'])
	n = len(observations)
	for i in range(len(observations)):
		observation = np.array(observations[i]['observation'], dtype=np.float32)
		data_new[key].append(observation)
		### compute action list ###
		velocity = np.array(observations[i]['vel'], dtype=np.float32)
		angle    = math.atan2(velocity[1],velocity[0])
		angle    = math.degrees(angle)
		angle    = (angle+360) % 360
		action   = np.zeros((1,32),dtype=np.float32)
		the_angle = int(round(angle*31/360))
		action[0,the_angle] = 1
		actions[key].append(action)
		### compute target list ###
		target_position = np.zeros((1,360))
		if i+target_dist+target_var < n:
			for j in range(i+target_dist,i+target_dist+target_var):
				target_position += np.array(observations[j]['observation'])
			target_position = target_position/target_var
			#target_position[0] = -target_position[0]/target_var
			#target_position[1] = -target_position[1]/target_var
		else:
			target_position += np.array(observations[n-1]['observation'])
		targets[key].append(target_position)


f1.train_network(data_new, targets, actions)


