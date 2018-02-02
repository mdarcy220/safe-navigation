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
	
	def __init__(self, feature_vector, target_vector, action_vector, velocity, learning_rate, name='action_predicter'):
		self._input_size  = feature_vector
		self._output_size = action_vector
		self._target_size = target_vector
		self._velocity_size = velocity
		self._input = C.input_variable(self._input_size)
		self._target = C.input_variable(self._target_size)
		self._output = C.input_variable(self._output_size)
		self._output_velocity = C.input_variable(self._velocity_size)
		self.name = name
		self._batch_size = 1
		self._max_iter = 1000000
		self._lr_schedule = C.learning_rate_schedule([learning_rate * (0.999**i) for i in range(1000)], C.UnitType.sample, epoch_size=self._max_iter*self._batch_size)
		self._model,self._loss, self._learner, self._trainer = self.create_model()
		self._predicted = {}

	def create_model(self):
		hidden_layers = [8,8,8,8,8,8,8,8,8]
		
		#first_input = C.ops.reshape(
		#    C.ops.splice(self._input, self._target),
		#    (1,self._input_size[0]*2,self._input_size[1]))
		#print(first_input)
		first_input = C.ops.reshape(self._input, (1, self._input_size[0], self._input_size[1]))
		model = C.layers.Convolution2D(
		    (1,3), num_filters=8, pad=True, reduction_rank=1, activation=C.ops.tanh)(first_input)
		
		for h in hidden_layers:
			input_new = C.ops.splice(model,first_input)
			model = C.layers.Convolution2D(
			    (1,3), num_filters=h, pad=True, 
			    reduction_rank=1, activation=C.ops.tanh)(input_new)

		model = C.ops.splice(model, self._target)

		######
		# Dense layers
		direction = C.layers.Sequential([
		C.layers.Dense(256, activation=C.ops.relu),
		C.layers.Dense(128, activation=C.ops.relu),
		C.layers.Dense(64, activation=C.ops.relu),
		C.layers.Dense(32, activation=None),
		])(model)

		velocity = C.layers.Sequential([
		C.layers.Dense(128,activation=C.ops.relu),
		C.layers.Dense(64,activation=None),
		C.layers.Dense(1,activation=None)
		])(model)

		model = C.ops.splice(direction,velocity)
		print(model)
		
		loss = C.cross_entropy_with_softmax(direction, self._output) + C.squared_error(velocity, self._output_velocity) 
		error = C.classification_error(direction, self._output)  + C.squared_error(velocity, self._output_velocity) 
		
		learner = C.adadelta(model.parameters)
		progress_printer = C.logging.ProgressPrinter(tag='Training', freq=50)
		trainer = C.Trainer(model, (loss,error), learner, progress_printer)
		return model, loss, learner, trainer

	def train_network(self, data, targets, actions, velocities):
		for i in range(self._max_iter):
			input_sequence,target_sequence,output_sequence,velocity_sequence = self.sequence_minibatch(data, targets, actions,velocities,self._batch_size)
			self._trainer.train_minibatch({self._input: input_sequence, self._target: target_sequence, self._output: output_sequence, self._output_velocity: velocity_sequence})
			if i % 500 == 0:
				self._trainer.summarize_training_progress()
				self._model.save('GRP.dnn')

	def sequence_minibatch(self, data, targets, actions, vel, batch_size):
		sequence_keys    = list(data.keys())
		minibatch_keys   = random.sample(sequence_keys,batch_size)
		minibatch_input  = []
		minibatch_target = []
		minibatch_output = []
		minibatch_veloc  = []

		for key in minibatch_keys:
			_input,_target,_output,_vel = self.input_output_sequence(data,targets,actions,vel,key)
			for i in range(len(_input)):
				minibatch_input.append(_input[i])
				minibatch_target.append(_target[i])
				minibatch_output.append(_output[i])
				minibatch_veloc.append(_vel[i])
		
		return minibatch_input,minibatch_target,minibatch_output,minibatch_veloc
	
	def input_output_sequence(self, data, targets, actions, vel, seq_key):
		data_k = data[seq_key]
		input_sequence = np.zeros((len(data_k),self._input_size[0],self._input_size[1]), dtype=np.float32)
		target_sequence = np.zeros((len(data_k),self._target_size[0],self._target_size[1]), dtype=np.float32)
		output_sequence = np.zeros((len(data_k),self._output_size[0],self._output_size[1]), dtype=np.float32)
		vel_sequence = np.zeros((len(data_k),self._velocity_size[0],self._velocity_size[1]), dtype=np.float32)
		
		for i in range(0,len(data_k)):
			input_sequence[i,:,:] = data_k[i]
			target_sequence[i,:,:] = targets[seq_key][i]
			output_sequence[i,:,:] = actions[seq_key][i]
			vel_sequence   [i,:,:] = vel[seq_key][i]
		return input_sequence,target_sequence,output_sequence,vel_sequence
	
