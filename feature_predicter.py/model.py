#!/usr/bin/python3

import numpy as np
from numpy import linalg as LA
import random
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import seaborn as sns
import math
import Vector
import cntk as C

class feature_extractor:
	
	def __init__(self, feature_vector, learning_rate, name='deep_irl_fc'):
		self._input_size = feature_vector
		self._input = C.input_variable(feature_vector)
		self._lr_schedule = C.learning_rate_schedule(learning_rate, C.UnitType.sample)
		self._output = C.input_variable(feature_vector)
		self.name = name
		self._model,self._loss, self._learner, self._trainer = self.create_model()

	def create_model(self):
		model1 = C.layers.Sequential([
		# Convolution layers
		C.layers.Convolution2D((1,5), num_filters=8, pad=True, reduction_rank=0, activation=C.ops.tanh),
		#C.layers.Convolution2D((1,3), num_filters=16, pad=True, reduction_rank=1, activation=C.ops.tanh),
		#C.layers.Convolution2D((1,5), num_filters=16, pad=False, reduction_rank=1, activation=C.ops.tanh),
		######
		# Dense layers
		C.layers.Dense(16, activation=C.ops.relu),
		C.layers.Dense(4, activation=C.ops.relu),
		######
		# Recurrence
		#C.layers.Recurrence(C.layers.LSTM(4, init=C.glorot_uniform())),
		######
		# Prediction
		C.layers.Dense(4, activation=C.ops.relu),
		######
		# Decoder layers
		C.layers.Dense(32, activation=C.ops.relu)
		])
		######
		# Reshape output
		model2 = C.ops.reshape(model1,(2,16))
		model3 = C.layers.Sequential([
		######
		# Deconvolution layers
		C.layers.ConvolutionTranspose((1,3), num_filters=16, strides=(1,1), pad=False, bias=False, init=C.glorot_uniform(1))
		])
		model = model3(model2)

		err = C.ops.reshape(C.ops.minus(model,self._output), (self._input_size))
		sq_err = C.ops.square(err)
		mse = C.ops.reduce_mean(sq_err)
		rmse_loss = C.ops.sqrt(mse)
		rmse_eval = rmse_loss
		learner = C.adadelta(model.parameters, self._lr_schedule)
		trainer = C.Trainer(model, (rmse_loss,rmse_eval), learner)
		return model, rmse_loss, learner, trainer
	def train_network(self,data):
		pass		
