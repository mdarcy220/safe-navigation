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
#from cntk.ops.functions import UserFunction
#from cntk import output_variable
# Network to choose correct action based on past two observations,
# and the predicted desired observation.

# The input to this network is all three observations (actual and predicted)
# The model is defined here as just the action-decision part,
# with the input from the feature prediction network precalculated; 
# this is done to speed up the training process.
# In real world processing, the two networks has to be concatenated.
"""
@C.Function
class vectors_to_angle(UserFunction):
	def __init__(self,arg1, arg2,name='vectors_to_angle'):
		super(vectors_to_angle, self).__init__([arg1,arg2], name=name)
	def forward(self,arguments,device=None, outputs_to_retain=None):
		v1 = arguments[0]
		v2 = arguments[1]
		angle_cosine = np.dot(v1,v2) /(math.sqrt(np.dot(v1,v1)) * math.sqrt(np.dot(v2,v2)))
		angle = np.arccos(angle_cosine)
		return angle
	def backward(self):
		return None
	def infer_outputs(self):
        	return [output_variable(self.inputs[0].shape, self.inputs[0].dtype,self.inputs[0].dynamic_axes)]
		
def vector_to_vector_angle(v1:,v2:C.Tensor[2]):
	v1 = v1
	v2 = v2
	angle_cosine = np.dot(v1,v2) /(math.sqrt(np.dot(v1,v1)) * math.sqrt(np.dot(v2,v2)))
	angle = np.arccos(angle_cosine)
	return angle	
"""
class action_modified:
	
	def __init__(self, feature_vector, target_vector, action_vector, velocity, load_model = True, testing = False, max_velocity = 0.31, learning_rate = 0.5, name='action_predicter',file_name = 'dnns/action_predicter_m.dnn'):
		self._load_model  = load_model
		self._input_size  = feature_vector
		self._output_size = action_vector
		self._target_size = target_vector
		self._velocity_size = velocity
		self._input = C.input_variable(self._input_size)
		self._target = C.input_variable(self._target_size)
		self._output = C.input_variable(self._output_size)
		self._output_velocity = C.input_variable(self._velocity_size)
		self._file_name = file_name
		#self._input           = C.sequence.input_variable(self._input_size)
		#self._target          = C.sequence.input_variable(self._target_size)
		#self._output          = C.sequence.input_variable(self._output_size)
		#self._output_velocity = C.sequence.input_variable(self._velocity_size)
		self.name = name
		self._max_velocity = max_velocity
		self._batch_size = 8
		self._max_iter = 1000000
		self._lr_schedule = C.learning_rate_schedule([learning_rate * (0.999**i) for i in range(1000)], C.UnitType.sample, epoch_size=self._max_iter*self._batch_size)
		#self._model,self._loss, self._learner, self._trainer = self.create_model()
		if testing:
			self._model = self.load_models()
		else:
			self._model,self._loss, self._learner, self._trainer = self.create_model()
		self._predicted = {}

	def load_models(self):
		action_model = C.load_model(self._file_name)(self._input,self._target)
		action_model = action_model.clone(C.CloneMethod.freeze)
		print(action_model)
		node_outputs = C.logging.get_node_outputs(action_model)
		for out in node_outputs: print("{0} {1}".format(out.name, out.shape))
		print('model arguments',action_model.arguments)
		return action_model

	def create_model(self):
		hidden_layers = [8,8,8,8,8,8,8,8,8,8,16,32]
		first_input = C.ops.splice(self._input,self._target)
		first_input_size = first_input.shape
		first_input = C.ops.reshape(first_input,(first_input_size[0],1,first_input_size[1]))

		model = C.layers.Convolution2D((1,3), num_filters=8,pad=True, reduction_rank=1,activation=C.ops.tanh)(first_input)
		for i,h in enumerate(hidden_layers):
			#if i >0:
				#input_new = C.ops.splice(model,input_new,axis=0)
			#else:
			input_new = C.ops.splice(model,first_input,axis=0)
			model1 = C.layers.Convolution2D((1,3), num_filters=int(0.5*h),pad=True, reduction_rank=1,activation=C.ops.tanh)(input_new)
			model2 = C.layers.Convolution2D((1,5), num_filters=int(0.25*h),pad=True, reduction_rank=1,activation=C.ops.tanh)(input_new)
			model3 = C.layers.Convolution2D((1,1), num_filters=int(0.25*h),pad=True, reduction_rank=1,activation=C.ops.tanh)(input_new)
			model = C.ops.splice(model1,model2,model3,axis=0)
			print (model)
		"""	
		model = C.layers.Sequential([
		# Convolution layers
		C.layers.Convolution2D((1,3), num_filters=8, pad=True, reduction_rank=1, activation=C.ops.tanh, name='conv_a'),
		C.layers.Convolution2D((1,3), num_filters=16, pad=True, reduction_rank=1, activation=C.ops.tanh, name='conv2_a'),
		C.layers.Convolution2D((1,3), num_filters=32, pad=False, reduction_rank=1, activation=C.ops.tanh, name='conv3_a'),
		######
		# Dense layers
		C.layers.Dense(1024, activation=C.ops.relu,name='dense5_a'),
		# Recurrence
		#C.layers.Recurrence(C.layers.LSTM(2048, init=C.glorot_uniform()),name='lstm_a'),
		C.layers.Dense(1024,activation=None)
		])(model)
		######
		"""
		# Prediction
		direction = C.layers.Sequential([
		C.layers.Dense(720, activation=C.ops.relu,name='dense6_a'),
		C.layers.Dense(360, activation=None,name='dense7_a')
		])(model)
		velocity = C.layers.Sequential([
		C.layers.Dense(128,activation=C.ops.relu),
		C.layers.Dense(64,activation=None),
		C.layers.Dense(1,activation=None)
		])(model)
		model = C.ops.splice(direction,velocity)
		#model = velocity
		if self._load_model:
			model = C.load_model(self._file_name)
			direction = model[0:360]
			velocity  = model[360]
		
		C.logging.log_number_of_parameters(model)
		print(model)
		#loss = C.squared_error(direction, self._output) +  C.squared_error(velocity, self._output_velocity)
		#error = C.classification_error(direction, self._output) +   C.squared_error(velocity, self._output_velocity)	
		loss = C.cross_entropy_with_softmax(direction, self._output) + C.squared_error(velocity, self._output_velocity)
		error = C.classification_error(direction, self._output) + C.squared_error(velocity, self._output_velocity)
		
		learner = C.adadelta(model.parameters,l2_regularization_weight=0.001)
		progress_printer = C.logging.ProgressPrinter(tag='Training')
		trainer = C.Trainer(model, (loss,error), learner, progress_printer)
		return model, loss, learner, trainer

	def test_network(self, data, targets, actions, velocities, printing=False):
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
		if printing:
			print ('average classifiaction error:', cl_error/count, 'for:', count, ' total steps')
			print ('average angular classifiaction error:', cl_error_2/count, 'for:', count, ' total steps', 'with angle',180*math.acos(1- (cl_error_2/count))/math.pi)
			print ('rmse normalized velocity error:', math.sqrt(v_error/count), 'for:', count, ' total steps')
			print ('rmse actual velocity error:', self._max_velocity*math.sqrt(v_error/count), 'for:', count, ' total steps')
		return cl_error/count,180*math.acos(1- (cl_error_2/count))/math.pi,self._max_velocity*math.sqrt(v_error/count)

	def train_network(self, data, targets, actions_prob, velocities,actions):
		angle_error=360
		angle_old = float('inf')
		for i in range(self._max_iter):
			input_sequence,target_sequence,output_sequence,velocity_sequence = self.sequence_minibatch(data, targets, actions, velocities,self._batch_size)
			self._trainer.train_minibatch({self._model.arguments[0]: input_sequence, self._model.arguments[1]: target_sequence, 
			    self._output:output_sequence,self._output_velocity:velocity_sequence})
			self._trainer.summarize_training_progress()
			if i%100 == 0:
				c,angle_error_temp,v = self.test_network(data,targets,actions,velocities)
				if i>5000 and (abs(angle_error_temp - angle_old)<10^-2 or angle_error_temp > angle_old +5 ):
					break
				else:
					angle_old = angle_error_temp
				if angle_error_temp  <angle_error:
					angle_error = angle_error_temp
					self._model.save(self._file_name)
				print (angle_error_temp, angle_error,angle_old)

	def test_seq(self, data, targets, actions, velocities, key):
		input_sequence,target_sequence,output_sequence,velocity_sequence = self.sequence_batch(data, targets, actions, velocities, key)
		predicted_values = self._model.eval({
			self._model.arguments[0]: input_sequence, 
			self._model.arguments[1]:target_sequence
			})
		predicted_actions  = []
		predicted_velocity = []
		#for k in range(0,len(predicted_values)):
			#predicted_seq = []
			#print (predicted_values)
		for value in predicted_values:
			#print (value)
			direction = value[0:360]
			velocity  = value[360]
			action = np.zeros(360)
			action[np.argmax(direction)] = 1
			#predicted_seq.append(action)
			predicted_actions.append(action)
			predicted_velocity.append(velocity)
		count     = 0
		error   = 0
		error_2 = 0
		v_error    = 0
		#for k in range(0,len(predicted_values)):
		for i in range(0,len(predicted_values)):
			pre_cl  = np.where(predicted_actions[i] == 1)[0]
			real_cl = np.where(output_sequence[i].flatten() == 1)[0]
			error   += 0 if pre_cl == real_cl else 1 
			error_2 += abs(1 - math.cos((max(real_cl,pre_cl) - min(real_cl,pre_cl))*math.pi/180))
			
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
			_input,_target,_output,_vel = self.input_output_sequence_train(data,targets,actions,vel,key)
			for i in range(len(_input)):
				minibatch_input.append(_input[i])
				minibatch_target.append(_target[i])
				minibatch_output.append(_output[i])
				minibatch_veloc.append(_vel[i])
			#minibatch_input.append(_input)
			#minibatch_target.append(_target)
			#minibatch_output.append(_output)
			#minibatch_veloc.append(_vel)
		
		return minibatch_input,minibatch_target,minibatch_output,minibatch_veloc
	
	def sequence_batch(self, data, targets, actions, vel, key):
		batch_input  = []
		batch_target = []
		batch_output = []
		batch_veloc  = []
		_input,_target,_output,_vel = self.input_output_sequence_test(data,targets,actions,vel,key)
		for i in range(len(_input)):
			batch_input.append(_input[i])
			batch_target.append(_target[i])
			batch_output.append(_output[i])
			batch_veloc.append(_vel[i])
		
		return batch_input,batch_target,batch_output,batch_veloc
	
	def input_output_sequence_test(self, data, targets, actions, vel, seq_key):
		data_k = data[seq_key]
		input_sequence = np.zeros((len(data_k)-1,self._input_size[0],self._input_size[1]), dtype=np.float32)
		target_sequence = np.zeros((len(data_k)-1,self._target_size[0],self._target_size[1]), dtype=np.float32)
		output_sequence = np.zeros((len(data_k)-1,self._output_size[0],self._output_size[1]), dtype=np.float32)
		vel_sequence    = np.zeros((len(data_k)-1,self._velocity_size[0],self._velocity_size[1]), dtype=np.float32)
		
		for i in range(0,len(data_k)-1):
			input_sequence [i,0,:] = data_k[i]
			input_sequence [i,1,:] = data_k[i+1]
			target_sequence[i,:,:] = targets[seq_key][i]
			output_sequence[i,0,:] = actions[seq_key][i+1]
			vel_sequence   [i,0,:] = vel[seq_key][i+1]
		return input_sequence,target_sequence,output_sequence,vel_sequence
	
	def input_output_sequence_train(self, data, targets, actions, vel, seq_key):
		data_k = data[seq_key]
		input_sequence = np.zeros((len(data_k)-1,self._input_size[0],self._input_size[1]), dtype=np.float32)
		target_sequence = np.zeros((len(data_k)-1,self._target_size[0],self._target_size[1]), dtype=np.float32)
		output_sequence = np.zeros((len(data_k)-1,self._output_size[0],self._output_size[1]), dtype=np.float32)
		vel_sequence = np.zeros((len(data_k)-1,self._velocity_size[0],self._velocity_size[1]), dtype=np.float32)
		
		for i in range(0,len(data_k)-1):
			input_sequence [i,0,:] = data_k[i]
			input_sequence [i,1,:] = data_k[i+1]
			target_sequence[i,:,:] = targets[seq_key][i]
			output_sequence[i,:,:] = actions[seq_key][i+1]
			vel_sequence   [i,0,:] = vel[seq_key][i+1]
		return input_sequence,target_sequence,output_sequence,vel_sequence
	
