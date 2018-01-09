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
from model import feature_extractor
import json

#######################
target_dist = 30
target_var = 5
#######################
f1 = feature_extractor((2,360),(1,32),0.7)
with open('training_human_data.json') as json_data:
	data = json.load(json_data)
#print(np.array(data[list(data.keys())[0]]['radardata_list'][0]['observation']).shape)
#print(data[list(data.keys())[0]]['radardata_list'][0]['position'])
#print(len(data[list(data.keys())[0]]['radardata_list']))

#print(data.keys())
data_new = {}
targets = {}
for key in data.keys():
	data_new[key] = []
	targets[key]  = []
	observations  = np.array(data[key]['radardata_list'])
	n = len(observations)
	for i in range(n):
		observation = np.array(observations[i]['observation'], dtype=np.float32)
		data_new[key].append(observation)
		### compute target list ###
		target_position = np.zeros((1,2))
		if i+target_dist+target_var < n:
			for j in range(i+target_dist,i+target_dist+target_var):
				target_position += np.array(observations[j]['position'])
			target_position = target_position/target_var
			#target_position[0] = -target_position[0]/target_var
			#target_position[1] = -target_position[1]/target_var
		else:
			target_position += np.array(observations[n-1]['position'])
		target_direction = target_position - np.array(observations[i]['position'])
		target_angle    = math.atan2(target_direction[0,1],target_direction[0,0])
		target_angle    =  math.degrees(target_angle)
		target_angle    = (target_angle+360) % 360
		target_action   = np.zeros((1,32),dtype=np.float32)
		target_angle    = int(round(target_angle*31/360))
		target_action[0,target_angle] = 1
		targets[key].append(target_action)
				
f1.train_network(data_new,targets)

