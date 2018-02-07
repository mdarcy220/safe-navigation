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
import scipy.stats

from models import action_predicter_f 
from models import action_predicter 
from models import action_modified
from models import feature_predicter_ours
from models import GRP
from models import GRP_f
from models import feature_predicter_GRP

### User inputs ###

network_list = ['action+','action','action_m','feature','GRP','GRP+','GRP_feature']

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
data_new        = {}
actions         = {}
cosined_actions = {}
targets         = {}
vel             = {}
def build_train_data(angle_tol = 0):
        data_file = 'data/training_human_data.json'
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
	confidence = list()
	for i in range(0,180):
		confidence.append(scipy.stats.norm(0,angle_tol).pdf(i))
	for i in range(-180,0):
		confidence.append(scipy.stats.norm(0,angle_tol).pdf(i))
	#confidence = [0.325,0.6065,0.8825,1,0.8825,0.6065,0.325]
	confidence = np.reshape(np.array(confidence,dtype=np.float32),(1,360))
	confidence = np.roll(confidence,180)
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


def build_test_data():
        data_file = 'data/testing_human_data.json'
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

#network_list = ['action+','action','feature','GRP','GRP+','GRP_feature']
def train(file_name):
	if network == 'GRP':
		f1 = GRP((2,360),(1,361),(1,360),(1,1),load_network=False,False,max_velocity,file_name=file_name)
		f1.train_network(data_new,targets,cosined_actions,vel,actions)
	elif network == 'action_m':
		f1 = action_modified((2,360),(1,361),(1,360),(1,1),load_network=False,False,max_velocity)
		f1.train_network(data_new,targets,actions,vel)
	else:
		sys.exit(1)

def test(file_name):
	if network == 'GRP':
		f1 = GRP((2,360),(1,361),(1,360),(1,1),True,True,max_velocity,file_name = file_name)
		return f1.test_network(data_new,targets,cosined_actions,vel,True)
	elif network == 'action_m':
		f1 = action_modified((2,360),(1,361),(1,360),(1,1),load_network=True,True,max_velocity)
		return f1.test_network(data_new,targets,actions,vel,True)
	else:
		sys.exit(1)

if __name__ == '__main__':
	main()

def main():
	stds = [0,1,2,3,4,5,6,7,8,9,10,15,20,25,30,40,50,60,70,80,90]
	for std in stds:
		build_train_data(std)
		train('dnns/GRP_'+str(std)+'.dnn')
		build_test_data()
		cl_error,an_error,v_error = test('dnns/GRP_'+str(std)+'.dnn')
		if os.path.isFile('recording.json'):
			with open ('recording.json') as recording_data:
				recording = json.load(recording_data)
		else:
			recording = []
		this_recording = {}
		this_recording['name'] = 'GRP'
		this_recording['std'] = std
		this_recording['classification_error'] = cl_error
		this_recording['angular_error'] = an_error
		this_recording['velocity_error'] = v_error

		recording.append(this_recording)
		
		with open('recording.json') as recording_data:
			json.dump(recording, f, indent=4, sort_keys=True)



		


	
