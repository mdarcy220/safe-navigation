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
import random

#######################
target_dist = 30
target_var = 5
#######################
with open('human_observations.json') as json_data:
	data = json.load(json_data)

n = len(data.keys())
keys = list(data.keys())
random.shuffle(keys)

train_keys = keys[0:round(2*n/3)]
test_keys = keys[round(2*n/3):n]

obs_train     = {key:data[key] for key in train_keys}
obs_test      = {key:data[key] for key in test_keys }


with open('training_human_data.json','w') as f:
	json.dump(obs_train, f, indent=4, sort_keys=True)

with open('testing_human_data.json', 'w') as f:
	json.dump(obs_test , f, indent=4, sort_keys=True)
