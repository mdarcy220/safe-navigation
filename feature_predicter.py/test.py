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


f1 = feature_extractor((1,360),1)
with open('human_observations.json') as json_data:
	data = json.load(json_data)
#print(np.array(data[list(data.keys())[0]]['radardata_list'][0]['observation']).shape)
#print(data.keys())
data_new = {}
for key in data.keys():
	data_new[key] = []
	observations = np.array(data[key]['radardata_list'])
	for i in range(len(observations)):
		observation = np.array(observations[i]['observation'], dtype=np.float32)
		data_new[key].append(observation)
f1.train_network(data_new)
