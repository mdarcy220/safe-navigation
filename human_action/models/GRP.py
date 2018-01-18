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

class GRP:
	
	def __init__(self, feature_vector, target_vector, action_vector, velocity, load_model = True, testing = False, max_velocity = 0.31, learning_rate = 0.5, name='action_predicter'):
		self._load_model  = load_model
		self._input_size  = feature_vector
		self._output_size = action_vector
		self._target_size = target_vector
		self._velocity_size = velocity
		self._input = C.input_variable(self._input_size)
		self._target = C.input_variable(self._target_size)
		self._output = C.input_variable(self._output_size)
		self._output_velocity = C.input_variable(self._velocity_size)
		self.name = name
		self._max_velocity = max_velocity
		self._batch_size = 1
		self._max_iter = 1000000
		self._lr_schedule = C.learning_rate_schedule([learning_rate * (0.999**i) for i in range(1000)], C.UnitType.sample, epoch_size=self._max_iter*self._batch_size)
		if testing:
			self._model = self.load_models()
		else:
			self._model,self._loss, self._learner, self._trainer = self.create_model()
		self._predicted = {}

	def load_models(self):
		action_model = C.load_model('dnns/GRP.dnn')(self._input,self._target)
		action_model = action_model.clone(C.CloneMethod.freeze)
		print(action_model)
		node_outputs = C.logging.get_node_outputs(action_model)
		for out in node_outputs: print("{0} {1}".format(out.name, out.shape))
		print('model arguments',action_model.arguments)
		return action_model

	def create_model(self):
		hidden_layers = [8,8,8,8,8,8,8,8,8]
		
		first_input = C.ops.reshape(
		    C.ops.splice(self._input,self._target),
		    (1,self._input_size[0]*2,self._input_size[1]))
		print(first_input)
		model = C.layers.Convolution2D(
		    (1,3), num_filters=8, pad=True, reduction_rank=1, activation=C.ops.tanh)(first_input)
		
		for h in hidden_layers:
			input_new = C.ops.splice(model,first_input)
			model = C.layers.Convolution2D(
			    (1,3), num_filters=h, pad=True, 
			    reduction_rank=1, activation=C.ops.tanh)(input_new)
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
		if self._load_model:
			model = C.load_model('dnns/GRP.dnn')
			direction = model[0:32]
			velocity  = model[32]
		
		print(model)
		loss = C.cross_entropy_with_softmax(direction, self._output) + C.squared_error(velocity, self._output_velocity) 
		error = C.classification_error(direction, self._output)  + C.squared_error(velocity, self._output_velocity) 
		
		learner = C.adadelta(model.parameters)
		progress_printer = C.logging.ProgressPrinter(tag='Training')
		trainer = C.Trainer(model, (loss,error), learner, progress_printer)
		return model, loss, learner, trainer

	def test_network(self, data, targets, actions, velocities):
		count      = 0
		cl_error   = 0
		cl_error_2 = 0
		v_error    = 0
		for key in data.keys():
			cn,cl_er,cl_er_2,v_er = self.test_seq(data,targets,actions,velocities,key)
			cl_error   += cl_er
			cl_error_2 += cl_er_2
			v_error    += v_er
			count      += cn
		print ('average classifiaction error:', cl_error/count, 'for:', count, ' total steps')
		print ('average angular classifiaction error:', cl_error_2/count, 'for:', count, ' total steps', 'with angle', 180*math.acos(1-(cl_error_2/count))/math.pi)
		print ('rmse normalized velocity error:', math.sqrt(v_error/count), 'for:', count, ' total steps')
		print ('rmse actual velocity error:', self._max_velocity*math.sqrt(v_error/count), 'for:', count, ' total steps')
		return cl_error/count,cl_error_2/count

	def train_network(self, data, targets, actions, velocities):
		for i in range(self._max_iter):
			input_sequence,target_sequence,output_sequence,velocity_sequence = self.sequence_minibatch(data, targets, actions,velocities,self._batch_size)
			self._trainer.train_minibatch({self._model.arguments[0]: input_sequence, self._model.arguments[1]: target_sequence, 
			    self._output: output_sequence, self._output_velocity:velocity_sequence})
			self._trainer.summarize_training_progress()
			if i%100 == 0:
				self._model.save('dnns/GRP.dnn')

	def test_seq(self, data, targets, actions, velocities, key):
		input_sequence,target_sequence,output_sequence,velocity_sequence = self.sequence_batch(data, targets, actions, velocities, key)
		predicted_values = self._model.eval({
			self._model.arguments[0]: input_sequence, 
			self._model.arguments[1]:target_sequence,
			})
		predicted_actions  = []
		predicted_velocity = []
		for value in predicted_values:
			direction = value[0:32]
			velocity  = value[32]
			action = np.zeros(32)
			action[np.argmax(direction)] = 1
			predicted_actions.append(action)
			predicted_velocity.append(velocity)
		count   = 0
		error   = 0
		error_2 = 0
		v_error = 0
		for i in range(0,len(predicted_values)):
			pre_cl  = np.where(predicted_actions[i] == 1)[0]
			real_cl = np.where(output_sequence[i].flatten() == 1)[0]
			error   += 0 if pre_cl == real_cl else 1 
			error_2 += abs(1 - math.cos((max(real_cl,pre_cl) - min(real_cl,pre_cl))*math.pi/32))
			#print (predicted_velocity[i], velocity_sequence[i][0])
			v_error += np.power(predicted_velocity[i] - velocity_sequence[i][0][0],2)
			count += 1
		return count, error, error_2, v_error
	
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
	
	def sequence_batch(self, data, targets, actions, vel, key):
		batch_input  = []
		batch_target = []
		batch_output = []
		batch_veloc  = []
		_input,_target,_ouput,_vel = self.input_output_sequence(data,targets,actions,vel,key)
		for i in range(len(_input)):
			batch_input.append(_input[i])
			batch_target.append(_target[i])
			batch_output.append(_ouput[i])
			batch_veloc.append(_vel[i])
		
		return batch_input,batch_target,batch_output,batch_veloc
	
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
	
