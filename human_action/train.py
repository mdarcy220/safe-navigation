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
import sys
import json

from models import action_predicter_f 
from models import action_predicter 
from models import feature_predicter_ours
from models import GRP
from models import GRP_f
from models import feature_predicter_GRP

### User inputs ###

network_list = ['action+','action','feature','GRP','GRP+','GRP_feature']

if len(sys.argv) < 2:
	print("Usage: python3 test.py network_module data_file(optional)")
	sys.exit(1)
elif len(sys.argv) <3:
    network = sys.argv[1];
    data_file = 'data/training_human_data.json'
else:
    network = sys.argv[1]
    data_file = sys.argv[2];
if network not in network_list:
    print ('Please input network from the following list:', network_list)
    sys.exit(1)

######################

### DATA INPUT ###

#######################
target_dist = 30
target_var = 50000
#######################
max_velocity = 0.31
learning_rate = 0.1
with open(data_file) as json_data:
	data = json.load(json_data)
#print(np.array(data[list(data.keys())[0]]['radardata_list'][0]['observation']).shape)
#print(np.array(data[list(data.keys())[0]]['radardata_list'][0]['vel']))
#print(data.keys())
data_new        = {}
actions         = {}
cosined_actions = {}
targets         = {}
vel             = {}
confidence = [0.325,0.6065,0.8825,1,0.8825,0.6065,0.325]
for i in range(360-7):
	confidence.append(0)
confidence = np.reshape(np.array(confidence,dtype=np.float32),(1,360))
confidence = np.roll(confidence,-3)
# confidence is calculated as the gaussian distribution
# centered in the middle with standard deviation 3
# This vector has been reweighted to give a value of 1 at the mean

for key in data.keys():
	data_new  [key] = []
	actions   [key] = []
	cosined_actions[key] = []
	targets   [key] = []
	vel       [key] = []
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
		action   = np.zeros((1,360),dtype=np.float32)
		the_angle = int(round(angle))
		action[0,the_angle] = 1
		cosined_action = np.multiply(action,np.roll(confidence,the_angle))
		cosined_actions[key].append(cosined_action)
		actions[key].append(action)
		
		veloc  = np.zeros((1,1))
		velo   = np.sqrt(np.sum(np.power(velocity,2)))
		velo   = velo if velo < max_velocity else max_velocity
		veloc += velo/max_velocity
		vel[key].append(veloc)
		
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
		target_action   = np.zeros((1,361),dtype=np.float32)
		target_angle    = int(math.floor(target_angle))
		target_action[0,target_angle] = 1
		target_dist = math.sqrt(np.sum(np.power(target_direction,2)))
		target_action[0,360] = target_dist
		targets[key].append(target_action)

		#target_observation = np.zeros((1,360))
		#if i+target_dist+target_var < n:
		#	for j in range(i+target_dist,i+target_dist+target_var):
		#		target_observation += np.array(observations[j]['observation'])
		#	target_observation = target_observation/target_var
		#else:
		#	target_observation += np.array(observations[n-1]['observation'])
		#target_obs[key].append(target_observation)


load_network = input('start a new network (y/n). (THE OLD NETWORK WILL BE DELETED IF YES)')

if load_network == 'y' or load_network == 'Y':
    load_network = False
    print ('Warning, pretrained network will be deleted!')
elif load_network == 'n' or load_network == 'N':
    load_network = True
else:
    'Failed to provide input'
    sys.exit(1)

#print('Testing system is still being built')
#sys.exit(1)
#######################

#network_list = ['action+','action','feature','GRP','GRP+','GRP_feature']

if network == 'GRP':
    f1 = GRP((1,360),(1,360),(1,32),(1,1),load_network,False,max_velocity)
    f1.train_network(data_new,target_obs,cosined_actions,vel)
elif network == 'action+':
    f1 = action_predicter_f((3,360),(1,361),(1,360),(1,1),load_network,False,max_velocity)
    f1.train_network(data_new,targets,cosined_actions,vel)
elif network == 'action':
    f1 = action_predicter_f((2,360),(1,361),(1,360),(1,1),load_network,False,max_velocity)
    f1.train_network(data_new,targets,cosined_actions,vel)
elif network == 'feature':
    f1 = feature_predicter_ours((2,360),(1,361),load_network,False,0.7)
    f1.train_network(data_new,targets)
elif network == 'GRP_feature':
    f1 = feature_predicter_GRP((1,360),(1,360),load_network,False,0.7)
    f1.train_network(data_new,target_obs)
elif network == 'GRP+':
    f1 = GRP_f((1,360),(1,360),load_network,False,0.7)
    f1.train_network(data_new,target_obs)
else:
    sys.exit(1)
