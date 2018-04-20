#!/usr/bin/python3

import numpy as np
from numpy import linalg as LA
import random
import matplotlib.pyplot as plt
from matplotlib import style
import math
import cntk as C

class feature_predicter_GRP:
	
	def __init__(self, feature_vector, target_vector, load_model = True, testing = False, learning_rate = 0.7, name='feature_predicter_GRP'):
		self._load_model = load_model
		self._input_size = feature_vector
		self._output_size = (1,feature_vector[1])
		self._target_size = target_vector
		self._input = C.sequence.input_variable(self._input_size)
		self._target = C.sequence.input_variable(self._target_size)
		self._output = C.sequence.input_variable(self._output_size)
		print(self._output)
		self.name = name
		self._batch_size = 4
		self._max_iter = 1000000
		self._lr_schedule = C.learning_rate_schedule([learning_rate * (0.997**i) for i in range(1000)], C.UnitType.sample, epoch_size=round(self._max_iter*self._batch_size/100))
		self._model,self._loss, self._learner, self._trainer = self.create_model()

	def create_model(self):
		hidden_layers = [8,8,8,8,8,8,8,8,8,8,8,1]
		
		first_input = C.ops.reshape(
		    C.ops.splice(self._input,self._target),
		    (2,self._input_size[0],self._input_size[1]))
		print(first_input)
		model = C.layers.Convolution2D(
		    (1,3), num_filters=8, pad=True, reduction_rank=1, activation=C.ops.tanh)(first_input)
		#print(model)		
		for h in hidden_layers:
			input_new = C.ops.splice(model,first_input,axis=0)
			#print(input_new)
			model = C.layers.Convolution2D(
			    (1,3), num_filters=h, pad=True, 
			    reduction_rank=1, activation=C.ops.tanh)(input_new)
			#print(model)
		model = C.ops.reshape(model,(1,360))
		#print(model)
		#C.logging.log_number_of_parameters(model)
		if self._load_model:
			model = C.load_model('dnns/feature_predicter_GRP.dnn')
		
		#print(model)
		err = C.ops.reshape(C.ops.minus(model,self._output), (self._output_size))
		sq_err = C.ops.square(err)
		mse = C.ops.reduce_mean(sq_err)
		rmse_loss = C.ops.sqrt(mse)
		rmse_eval = rmse_loss

		learner = C.adadelta(model.parameters)
		progress_printer = C.logging.ProgressPrinter(tag='Training')
		trainer = C.Trainer(model, (rmse_loss,rmse_eval), learner, progress_printer)
		return model, rmse_loss, learner, trainer

	def train_network(self, data, targets):
		for i in range(self._max_iter):
			input_sequence,target_sequence,output_sequence = self.sequence_minibatch(data, targets, self._batch_size)
			self._trainer.train_minibatch({
				self._model.arguments[0]: input_sequence,
				self._model.arguments[1]: target_sequence,
				self._output: output_sequence
				})
			self._trainer.summarize_training_progress()
			if i%100 == 0:
				self._model.save('dnns/feature_predicter_GRP.dnn')

	def sequence_minibatch(self, data, targets, batch_size):
		sequence_keys    = list(data.keys())
		minibatch_keys   = random.sample(sequence_keys,batch_size)
		minibatch_input  = []
		minibatch_target = []
		minibatch_output = []

		for key in minibatch_keys:
			_input,_target,_ouput = self.input_output_sequence(data,targets,key)
			for i in range(len(_input)):
				minibatch_input.append(_input[i])
				minibatch_target.append(_target[i])
				minibatch_output.append(_ouput[i])
		
		return minibatch_input,minibatch_target,minibatch_output
	
	def input_output_sequence(self, data, targets, seq_key):
		data_k = data[seq_key]
		input_sequence = np.zeros((len(data_k)-1,self._input_size[0],self._input_size[1]), dtype=np.float32)
		target_sequence = np.zeros((len(data_k)-1,self._target_size[0],self._target_size[1]), dtype=np.float32)
		output_sequence = np.zeros((len(data_k)-1,self._output_size[0],self._output_size[1]), dtype=np.float32)

		for i in range(0,len(data_k)-1):
			input_sequence[i,:,:]  = data_k[i]
			target_sequence[i,:,:] = targets[seq_key][i]
			output_sequence[i,0,:] = data_k[i+1]
		return input_sequence,target_sequence,output_sequence

