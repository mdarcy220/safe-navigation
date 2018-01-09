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

# Network to choose correct action based on past two observations,
# and the predicted desired observation.

# The input to this network is all three observations (actual and predicted)
# The model is defined here as just the action-decision part,
# with the input from the feature prediction network precalculated; 
# this is done to speed up the training process.
# In real world processing, the two networks has to be concatenated.

class action_prediction:
	
	def __init__(self, feature_vector, target_vector, action_vector, learning_rate, name='action_predicter'):
		self._input_size  = (feature_vector[0]+1,feature_vector[1])
		self._output_size = action_vector
		self._target_size = target_vector
		self._input = C.sequence.input_variable(self._input_size)
		self._target = C.sequence.input_variable(self._target_size)
		self._output = C.sequence.input_variable(self._output_size)
		self.name = name
		self._batch_size = 8
		self._max_iter = 1000000
		self._lr_schedule = C.learning_rate_schedule([learning_rate * (0.999**i) for i in range(1000)], C.UnitType.sample, epoch_size=self._max_iter*self._batch_size)
		self._model,self._loss, self._learner, self._trainer = self.create_model()
		self._predicted = {}

	def create_model(self):
		modeli = C.layers.Sequential([
		# Convolution layers
		C.layers.Convolution2D((1,3), num_filters=8, pad=True, reduction_rank=0, activation=C.ops.tanh, name='conv_a'),
		C.layers.Convolution2D((1,3), num_filters=16, pad=True, reduction_rank=1, activation=C.ops.tanh, name='conv2_a'),
		C.layers.Convolution2D((1,3), num_filters=16, pad=False, reduction_rank=1, activation=C.ops.tanh, name='conv3_a'),
		######
		# Dense layers
		C.layers.Dense(128, activation=C.ops.relu,name='dense1_a'),
		C.layers.Dense(64, activation=C.ops.relu,name='dense2_a'),
		C.layers.Dense(32, activation=C.ops.relu,name='dense3_a')
		])(self._input)
		### target
		modelt = C.layers.Sequential([
		C.layers.Dense(32, activation=C.ops.relu,name='dense4_a')
		]) (self._target)
		### concatenate both processed target and observations
		inputs = C.ops.splice(modeli,modelt)
		### Use input to predict next hidden state, and generate
		### next observation
		model = C.layers.Sequential([
		######
		C.layers.Dense(32, activation=C.ops.relu,name='dense5_a'),
		# Recurrence
		C.layers.Recurrence(C.layers.LSTM(32, init=C.glorot_uniform()),name='lstm_a'),
		######
		# Prediction
		C.layers.Dense(32, activation=None,name='dense6_a')
		])(inputs)
		
		loss = C.cross_entropy_with_softmax(model, self._output)
		error = C.classification_error(model, self._output)
		
		learner = C.adadelta(model.parameters, self._lr_schedule)
		progress_printer = C.logging.ProgressPrinter(tag='Training')
		trainer = C.Trainer(model, (loss,loss), learner, progress_printer)
		return model, loss, learner, trainer

	def train_network(self, data, targets, actions):
		self.predict(data,targets)
		for i in range(self._max_iter):
			input_sequence,target_sequence,output_sequence = self.sequence_minibatch(data, targets, actions,self._batch_size)
			self._trainer.train_minibatch({self._input: input_sequence, self._target: target_sequence, self._output: output_sequence})
			self._trainer.summarize_training_progress()
			if i%10 == 0:
				self._model.save('action_predicter.dnn')

	def sequence_minibatch(self, data, targets, actions, batch_size):
		sequence_keys    = list(data.keys())
		minibatch_keys   = random.sample(sequence_keys,batch_size)
		minibatch_input  = []
		minibatch_target = []
		minibatch_output = []

		for key in minibatch_keys:
			_input,_target,_ouput = self.input_output_sequence(data,targets,actions,key)
			minibatch_input.append(_input)
			minibatch_target.append(_target)
			minibatch_output.append(_ouput)
		
		return minibatch_input,minibatch_target,minibatch_output
	
	def input_output_sequence(self, data, targets, actions, seq_key):
		data_k = data[seq_key]
		input_sequence = np.zeros((len(data_k)-2,self._input_size[0],self._input_size[1]), dtype=np.float32)
		target_sequence = np.zeros((len(data_k)-2,self._target_size[0],self._target_size[1]), dtype=np.float32)
		output_sequence = np.zeros((len(data_k)-2,self._output_size[0],self._output_size[1]), dtype=np.float32)
		
		for i in range(0,len(data_k)-2):
			input_sequence[i,0,:] = data_k[i]
			input_sequence[i,1,:] = data_k[i+1]
			input_sequence[i,2,:] = self._predicted[seq_key][i+2]
			target_sequence[i,:,:] = targets[seq_key][i]
			output_sequence[i,0,:] = actions[seq_key][i+2]
		return input_sequence,target_sequence,output_sequence
	
	def predict(self, data, targets):
		sequence_keys = list(data.keys())
		feature_predicter = C.load_model('feature_predicter.dnn')
		k = 1
		for key in sequence_keys:
			self._predicted[key] = [0,0]
			data_k = data[key]
			target_k = targets[key]

			for i in range(0,len(data_k)-2):
				input_vect = np.zeros((self._input_size[0]-1,self._input_size[1]), dtype=np.float32)
				input_vect[0,:] = data_k[i]
				input_vect[1,:] = data_k[i+1]
				self._predicted[key].append(feature_predicter(input_vect,target_k[i])[0])

