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
		self._input_size  = feature_vector
		self._output_size = action_vector
		self._target_size = target_vector
		self._input = C.input_variable(self._input_size)
		self._target = C.input_variable(self._target_size)
		self._output = C.input_variable(self._output_size)
		self.name = name
		self._batch_size = 8
		self._max_iter = 1000000
		self._lr_schedule = C.learning_rate_schedule([learning_rate * (0.999**i) for i in range(1000)], C.UnitType.sample, epoch_size=self._max_iter*self._batch_size)
		#self._model,self._loss, self._learner, self._trainer = self.create_model()
		self._model = self.create_model()
		self._predicted = {}

	def create_model(self):
		action_model = C.load_model('action_predicter.dnn')(self._input,self._target)
		action_model = action_model.clone(C.CloneMethod.freeze)
		print(action_model)
		node_outputs = C.logging.get_node_outputs(action_model)
		for out in node_outputs: print("{0} {1}".format(out.name, out.shape))
		print('model arguments',action_model.arguments)
		#loss = C.cross_entropy_with_softmax(action_model, self._output)
		#error = C.classification_error(action_model, self._output)
		
		#learner = C.adadelta(action_model.parameters, self._lr_schedule)
		#progress_printer = C.logging.ProgressPrinter(tag='Training')
		#trainer = C.Trainer(action_model, (loss,loss), learner)
		return action_model#, loss, learner, trainer

	def test_network(self, data, targets, actions):
		count = 0
		error = 0
		for key in data.keys():
			cn,er = self.test_seq(data,targets,actions,key)
			error += er
			count += cn
		print ('average classifiaction error:', error/count, 'for:', count, ' total steps')

	def test_seq(self, data, targets, actions, key):
		input_sequence,target_sequence,output_sequence = self.sequence_batch(data, targets, actions, key)
		predicted_values = self._model.eval({
			self._model.arguments[0]: input_sequence, 
			self._model.arguments[1]:target_sequence,
			})
		predicted_actions = []
		for value in predicted_values:
			action = list(np.zeros((32,1)))
			action[np.argmax(value)] = 1
			predicted_actions.append(action)
		count = 0
		error = 0
		for i in range(0,len(predicted_values)):
			error += sum(abs(sum(np.array(predicted_actions[i]) 
			    - np.array(output_sequence[i]))))/2.0
			count += 1
		return count, error

	def sequence_batch(self, data, targets, actions, key):
		batch_input  = []
		batch_target = []
		batch_output = []
		_input,_target,_ouput = self.input_output_sequence(data,targets,actions,key)
		for i in range(len(_input)):
			batch_input.append(_input[i])
			batch_target.append(_target[i])
			batch_output.append(_ouput[i])
		
		return batch_input,batch_target,batch_output
	
	def input_output_sequence(self, data, targets, actions, seq_key):
		data_k = data[seq_key]
		input_sequence = np.zeros((len(data_k),self._input_size[0],self._input_size[1]), dtype=np.float32)
		target_sequence = np.zeros((len(data_k),self._target_size[0],self._target_size[1]), dtype=np.float32)
		output_sequence = np.zeros((len(data_k),self._output_size[0],self._output_size[1]), dtype=np.float32)
		
		for i in range(0,len(data_k)):
			input_sequence[i,0,:] = data_k[i]
			target_sequence[i,:,:] = targets[seq_key][i]
			output_sequence[i,0,:] = actions[seq_key][i]
		return input_sequence,target_sequence,output_sequence
	
