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

class feature_extractor:
	
	def __init__(self, feature_vector, learning_rate, name='feature_predicter'):
		self._input_size = feature_vector
		self._output_size = (1,feature_vector[1])
		self._input = C.sequence.input_variable(self._input_size)
		self._output = C.sequence.input_variable(self._output_size)
		print(self._output)
		self.name = name
		self._batch_size = 8
		self._max_iter = 1000000
		self._lr_schedule = C.learning_rate_schedule([learning_rate * (0.999**i) for i in range(1000)], C.UnitType.sample, epoch_size=self._max_iter*self._batch_size)
		self._model,self._loss, self._learner, self._trainer = self.create_model()

	def create_model(self):
		model1 = C.layers.Sequential([
		# Convolution layers
		C.layers.Convolution2D((1,3), num_filters=8, pad=True, reduction_rank=0, activation=C.ops.tanh,name='conv'),
		C.layers.Convolution2D((1,3), num_filters=16, pad=True, reduction_rank=1, activation=C.ops.tanh,name='conv'),
		C.layers.Convolution2D((1,3), num_filters=16, pad=False, reduction_rank=1, activation=C.ops.tanh,name='conv'),
		######
		# Dense layers
		C.layers.Dense(64, activation=C.ops.relu,name='dense1'),
		C.layers.Dense(32, activation=C.ops.relu,name='dense1'),
		C.layers.Dense(8, activation=C.ops.relu,name='dense1'),
		######
		# Recurrence
		C.layers.Recurrence(C.layers.LSTM(8, init=C.glorot_uniform()),name='lstm'),
		######
		# Prediction
		C.layers.Dense(4, activation=C.ops.relu,name='predict'),
		######
		# Decoder layers
		C.layers.Dense(32, activation=C.ops.relu,name='dense2'),
		C.layers.Dense(64, activation=C.ops.relu,name='dense2'),
		C.layers.Dense(120, activation=C.ops.relu,name='dense2')
		])(self._input)
		######
		# Reshape output
		model2 = C.ops.reshape(model1,(1,1,120))
		model3 = C.layers.Sequential([
		######
		# Deconvolution layers
		C.layers.ConvolutionTranspose((1,3), num_filters=3, strides=(1,3), pad=False, bias=False, init=C.glorot_uniform(1),name='conv2'),
		C.layers.ConvolutionTranspose((1,3), num_filters=1,  pad=True,name='conv2')
		])(model2)
		model = C.ops.reshape(model3,(1,360))

		err = C.ops.reshape(C.ops.minus(model,self._output), (self._output_size))
		sq_err = C.ops.square(err)
		mse = C.ops.reduce_mean(sq_err)
		rmse_loss = C.ops.sqrt(mse)
		rmse_eval = rmse_loss
		learner = C.adadelta(model.parameters, self._lr_schedule)
		progress_printer = C.logging.ProgressPrinter(tag='Training')
		trainer = C.Trainer(model, (rmse_loss,rmse_eval), learner, progress_printer)
		return model, rmse_loss, learner, trainer

	def train_network(self, data):
		for i in range(self._max_iter):
			input_sequence,output_sequence = self.sequence_minibatch(data, self._batch_size)
			self._trainer.train_minibatch({self._input: input_sequence, self._output: output_sequence})
			self._trainer.summarize_training_progress()
			if i%10 == 0:
				self._model.save('feature_predicter.dnn')

	def sequence_minibatch(self, data, batch_size):
		sequence_keys    = list(data.keys())
		minibatch_keys   = random.sample(sequence_keys,batch_size)
		minibatch_input  = []
		minibatch_output = []

		for key in minibatch_keys:
			_input,_ouput = self.input_output_sequence(data,key)
			minibatch_input.append(_input)
			minibatch_output.append(_ouput)
		
		return minibatch_input,minibatch_output
	
	def input_output_sequence(self, data, seq_key):
		data_k = data[seq_key]
		input_sequence = np.zeros((len(data_k)-2,self._input_size[0],self._input_size[1]), dtype=np.float32)
		output_sequence = np.zeros((len(data_k)-2,self._input_size[0]-1,self._input_size[1]), dtype=np.float32)
		for i in range(0,len(data_k)-2):
			input_sequence[i,0,:] = data_k[i]
			input_sequence[i,1,:] = data_k[i+1]
			output_sequence[i,0,:] = data_k[i+2]
		return input_sequence,output_sequence

