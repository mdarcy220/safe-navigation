#!/usr/bin/python3

import math
import json
import random

#######################
target_dist = 30
target_var = 5
#######################
with open('human_observations_eth.json') as json_data:
	data = json.load(json_data)

with open('human_observations_hotel.json') as json_data:
	data_hotel = json.load(json_data)

print(len(data.keys()))
data_hotel_new = {}
for key in data_hotel.keys():
	data_hotel_new[key+'h'] = data_hotel[key]
data.update(data_hotel_new)
print (len(data.keys()))
print (len(data_hotel.keys()))
n = len(data.keys())
keys = list(data.keys())
random.shuffle(keys)

train_keys = keys[0:round(2*n/3)]
test_keys = keys[round(2*n/3):n]

obs_train     = {key:data[key] for key in train_keys}
obs_test      = {key:data[key] for key in test_keys }


with open('complete_training_human_data.json','w') as f:
	json.dump(obs_train, f, indent=4, sort_keys=True)

with open('complete_testing_human_data.json', 'w') as f:
	json.dump(obs_test , f, indent=4, sort_keys=True)
