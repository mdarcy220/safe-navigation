#!/usr/bin/python3

from Robot import RobotControlInput
from .AbstractNavAlgo import AbstractNavigationAlgorithm
from .LinearNavAlgo import LinearNavigationAlgorithm  
from .ValueIterationNavAlgo import ValueIterationNavigationAlgorithm

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

## Maximum Entropy Deep Inverse Reinforcement Learning navigation algorithm.
# This is actually just a wrapper around another navigation algorithm, and this
# class observes the actions of the real nav algo to do inverse RL.
#
class DeepIRLAlgorithm(AbstractNavigationAlgorithm):

	## Initializes the navigation algorithm.
	# 
	# @param sensors (dict of sensors)
	# <br>	-- the sensors that this algorithm has access to
	#
	# @param target (Target obj)
	# <br>	-- the target for the navigation
	#
	# @param cmdargs (object)
	# <br>	-- A command-line arguments object generated by `argparse`.
	# 
	def __init__(self, sensors, target, cmdargs, real_algo_init=None):
		# in what follows, we place everything in a numpy array before
		# proceeding
		# for states, the array is a 1D array, with entries as y *
		# width + x

		self._sensors = sensors;
		self._target  = target;
		self._cmdargs = cmdargs;
		self._max_steps = 300;
		self._max_loops = 1;
		self._lr = 1.11;
		self._decay = 0.9

		if real_algo_init is None:
			real_algo_init = LinearNavigationAlgorithm
		self._real_algo = real_algo_init(sensors, target, cmdargs)

		self._radar = self._sensors['radar'];
		self._radar_data = None
		self._dynamic_radar_data = None

		self._gps = self._sensors['gps'];
		self._mdp = self._sensors['mdp'];
		self._features = self._get_features();

		self._valueIteration = ValueIterationNavigationAlgorithm(self._sensors, self._target, self._cmdargs);
		#self._demonstrations = self._add_demonstration_loop(self._max_steps, self._max_loops);
		self._demonstrations = self.hand_crafted_demonstrations()

		self._reward = self.IRLloop()




	## Select the next action for the robot
	#
	# This function uses the robot's radar and location information, as
	# well as internally stored information about previous locations,
	# to compute the next action the robot should take.

	#

	# @returns (`Robot.RobotControlInput` object)
	# <br>	-- A control input representing the next action the robot
	# 	should take.
	#
	## Adds a (state, action) pair to the current demonstration for the IRL
	# algorithm.
	#



	def hand_crafted_demonstrations(self):
		sequence = []
		
		step = ((1,18),0.0,(2,18), 0.0)
		sequence.append(step)
		for i in range(2,17):
			step = ((i,18), 0.0, (i+1,18), 0.0)
			sequence.append(step)
		for i in range(18,11, -1):
			step = ((17,i), 0.0, (17,i-1), 0.0)
			sequence.append(step)
		for i in range(17,11, -1):
			step = ((i,11), 0.0, (i-1,11), 0.0)
			sequence.append(step)
		for i in range(11,2, -1):
			step = ((11,i), 0.0, (11,i-1), 0.0)
			sequence.append(step)
		for i in range(11,24):
			step = ((i,2), 0.0, (i+1,2), 0.0)
			sequence.append(step)
		step = ((24,2), 0.0, (24,1), 0.0)
		sequence.append(step)
		"""
		(x,y)= (1,18)
		flip = 1
		while (x < 24 or y >1):
			if flip == 1:
				step = ((x,y), 0.0, (x+1,y), 0.0)
				x += 1
				flip = 0
			else:
				step = ((x,y), 0.0, (x,y-1), 0.0)
				if y == 1:
					flip = 1
					continue
				else:
					y -= 1
					flip = 1
			sequence.append(step)
		"""
		demo = []
		demo.append(sequence)
		
		return demo

	def _add_demonstration_loop(self, max_steps, max_loops):
		demonstrations = []
		for loop in range(0,max_loops):
			start_state = (1000,1000)
			while True:
			    start_state = (random.randint(1,self._mdp._width-2), random.randint(1,self._mdp._height-2))
			    #start_state = (random.randint(1,1), random.randint(18,18))
			    if (self._mdp._walls[start_state[1], start_state[0]] == 0):
				    break
			#start_state = random.sample(self._mdp.states(),1)[0]
			demon_traj = self._valueIteration.add_demonstration_step(start_state,max_steps)
			if len(demon_traj) > 0:
			    demonstrations.append(demon_traj)
		return demonstrations


	def has_given_up(self):
		return False;
	def _do_value_iter(self, reward):
		mdp = self._mdp
		gamma = 0.98


		old_values = {state: 0.0 for state in self._mdp.states()}
		old_values[self._mdp.goal_state()] = 1
		new_values = old_values

		qvals = dict()
		for state in mdp.states():
			qvals[state] = dict()
			for action in mdp.actions(state):
				qvals[state][action] = 0.0

		iteration = 0
		max_iter = 1000
		while (iteration < max_iter):
			old_values = new_values
			new_values = dict()
			for state in mdp.states():
				(x,y) = state
				for action in mdp.actions(state):
					# Fear not: this massive line is just a Bellman-ish update
					old_qvals = (mdp.transition_prob(state, action, next_state)*old_values[next_state] for next_state in mdp.successors(state))
					qvals[state][action] = reward[0,y*mdp._width+x] + gamma*softmax(old_qvals)
					#qvals[state][action] = reward[0,y*mdp._width+x] + gamma*sum(mdp.transition_prob(state, action, next_state)*old_values[next_state] for next_state in mdp.successors(state))
					#qvals[state][action] = mdp.reward(state,action,None) + gamma*sum(mdp.transition_prob(state, action, next_state)*old_values[next_state] for next_state in mdp.successors(state))

				## Softmax to get value
				#exp_qvals = {action: np.exp(qval) for action, qval in qvals[state].items()}
				#new_values[state] = max(exp_qvals.values())/sum(exp_qvals.values())

				# Just take the max to get values
				new_values[state] = max(qvals[state].values())

			# Quit if we have converged
			if max({abs(old_values[s] - new_values[s]) for s in mdp.states()}) < 0.01:
				break
			iteration += 1

		policy = dict()
		for state in mdp.states():
			policy[state] = dict()
			exp_qvals = {action: np.exp(qval)*10 for action, qval in qvals[state].items()}
			sum_exp_qvals = sum(exp_qvals.values())
			for action in mdp.actions(state):
				#print(policy[state], exp_qvals, qvals[state])
				policy[state][action] = exp_qvals[action]/sum_exp_qvals

		return policy


	def _get_features(self):
		# in this method we retrieve the features from the mdp
		# and we transform the from a dictionary of column vectors
		# to a 2D matrix
		# each column representing the feature vector for 
		# one of the states, ordered according to the general {x,y}
		mdp = self._mdp
		features = mdp._features
		rand_state = random.sample(mdp.states(),1)
		a_feature = features[rand_state[0]]
		feature_mat = np.zeros((a_feature.size, mdp._height* mdp._width), dtype = np.float64)
		for state in mdp.states():
			(x,y) = state
			feature_mat[:, y * mdp._width + x] = features[state]
			#print(feature_mat[:,(19-1) * mdp._width + 15])
		# Uncomment the following to normalize features
		#for i in range(feature_mat.shape[0]):
		#	feature_mat[i,:] = np.divide(feature_mat[i,:],abs(feature_mat[i,:]).max())

		return feature_mat
	
	
	def _get_action(self, state, policy):
		total = 0.0
		rand = np.random.random()
		for action in policy[state]:
			total += self._policy[state][action]
			if rand < total:
				return action
		return list(policy[state].keys())[random.randint(0,3)]

	def IRLloop(self):
		mdp = self._mdp
		height = mdp._height
		width = mdp._width
		network = the_network(self._features[:,0].shape,self._lr, hidden_layers = [1000,200,10])

		states, rewards = network.forward_one_step(np.vstack(self._features.T))
		reward = list(rewards.values())[0].T
		feat_exp = np.zeros((1,len(mdp.states())))
		for traj in self._demonstrations:
			for (state, action, next_state, r) in traj:
				(x,y) = state
				feat_exp[0,y*width + x] += 1
		feat_exp /= self._max_loops


		maxIter = 200
		old_grad = np.zeros((self._features[:,0].shape))
		lr = self._lr
		decay = self._decay

		self.show_reward(feat_exp,0)
		for i in range(maxIter):
			if i%7 == 0:
				lr = lr * decay 
			grad = np.zeros((self._features[:,0].shape))
			policy = self._do_value_iter(reward)
			newFeat_mult = self._visitation_trajectory_frequency(self._demonstrations, policy)
			grad = feat_exp - newFeat_mult
			grad = np.dot(grad,lr)
			self.show_reward(grad,i+1)
			network.backward_one_step(states, rewards, np.vstack(grad.T))
			
			states, rewards = network.forward_one_step(np.vstack(self._features.T))
			reward = list(rewards.values())[0].T
			
			self.plot_reward_policy(reward,policy,i)
			self.plot_reward(reward)
			print('grad_norm: ', LA.norm(grad))
			if i==0:
				old_grad = grad
				continue
			print ('grad_diff: ', LA.norm(grad-old_grad))
			old_grad = grad

		return reward
	
	def _visitation_trajectory_frequency(self, demonstrations, policy):
		mdp = self._mdp
		height = mdp._height
		width = mdp._width
		T = self._max_steps
		N = height * width
		mu = np.zeros([N, T])

		for demonstration in demonstrations:
			(s, a, sx, r) = demonstration[0]
			(x,y) = s
			mu[y*width +x , 0] += 1/self._max_loops
		mu[:,0] = mu[:,0]/T

		for t in range(T-1):
			mu_old = mu
			for s in mdp.states():
				(x,y) = s
				#mu[y*width + x,t+1] = sum([mu[y*width + x,t] * mdp.transition_prob(s,self._get_action(s_x, policy),s_x) for s_x in mdp.successors(s)])
				mu[y*width + x,t+1] = sum([sum([mu_old[y*width + x,t] * mdp.transition_prob(s,action,s_x)*policy[s][action] for s_x in mdp.successors(s)]) for action in mdp.actions(s)])
		p = np.sum(mu,1)
		
		return p

	def show_reward(self, reward_map, iteration, dpi=196.0):
		# Set up the figure
		plt.gcf().set_dpi(dpi)

		# Note that we're messing with the input args here
		reward_map = reward_map.reshape(self._mdp._height, self._mdp._width)
		plt.imshow(reward_map, cmap='hot', interpolation='nearest')

		plt.savefig('../output_data/gra{:02d}.png'.format(iteration))
		plt.close()
	
	
	def plot_reward(self, rewards, figsize=(7,7)):
		sns.set(style="white")
		#max_x = max([x for x,y in self._mdp.states()])
		#max_y = max([y for x,y in self._mdp.states()])
		#reward = np.zeros((max_x, max_y))

		#for state in self._mdp.states():
		#	x,y = state
		#	reward[x-1,y-1] = rewards[state]
		reward = rewards.reshape(self._mdp._height, self._mdp._width)

		plt.imshow(reward, cmap='hot', interpolation='nearest')

		plt.savefig('../output_data/reward.png')
		plt.close()


	def plot_reward_policy(self, reward_map, policy, iteration, dpi=196.0):
		# Set up the figure
		plt.gcf().set_dpi(dpi)
		ax = plt.axes()

		# Note that we're messing with the input args here
		reward_map = reward_map.reshape(self._mdp._height, self._mdp._width)
		plt.imshow(reward_map, cmap='hot', interpolation='nearest')

		# The scale controls the size of the arrows
		scale = 0.8

		for state in self._mdp.states():
			# Init a dict of the values for each action
			action_values = {action:policy[state][action] for action in self._mdp.actions(state)}

			# avgarrow points in the average direction the robot
			# will travel based on the stochastic policy
			avgarrow_vec = np.sum(item[1]*Vector.unit_vec_from_degrees(item[0][0]) for item in action_values.items())
			avgarrow_mag = Vector.magnitudeOf(avgarrow_vec)
			avgarrow_vec = avgarrow_vec/avgarrow_mag
			ax.arrow(state[0], state[1], avgarrow_vec[0]*0.1, avgarrow_vec[1]*0.1, head_width = scale * avgarrow_mag, head_length = scale * avgarrow_mag)

			# maxarrow points in the single most likely direction
			max_action = max((item for item in action_values.items()), key=lambda item: item[1])
			maxarrow_vec = Vector.unit_vec_from_degrees(max_action[0][0])
			ax.arrow(state[0], state[1], 0.1*maxarrow_vec[0], 0.1*maxarrow_vec[1], head_width= scale * max_action[1], head_length = scale * max_action[1], color='g')

		# Output the figure to the image file
		plt.savefig('../output_data/r_p{:02d}.png'.format(iteration))
		plt.close()

class the_network:
	
	def __init__(self, n_input, lr, hidden_layers = [300,400], l2 = 1, name='deep_irl_fc'):
		self._input = C.input_variable(n_input)
		self._output_size = l2
		self._lr_schedule = C.learning_rate_schedule(lr, C.UnitType.sample)
		self._output = C.input_variable(self._output_size)
		self.name = name
		self._num_hidden_layers = len(hidden_layers)
		self._hidden_layers = hidden_layers
		self._model,self._loss, self._learner, self._trainer = self.create_model()

	def create_model(self):
		hidden_layers = self._hidden_layers
		with C.layers.default_options(init = C.layers.glorot_uniform(), activation = C.ops.relu):
			h = self._input
			for i in range(self._num_hidden_layers):
				h = C.layers.Dense(hidden_layers[i])(h)
			model = C.layers.Dense(self._output_size, activation = None)(h)
			loss = C.reduce_mean(C.square(model - self._output), axis=0)
			meas = C.reduce_mean(C.square(model - self._output), axis=0)
			learner = C.adadelta(model.parameters, self._lr_schedule)
			trainer = C.Trainer(model, (loss,meas), learner)
			return model, loss, learner, trainer
	def forward_one_step(self, inputs):
		loss = self._loss
		outputs = np.vstack(np.ones((inputs.shape[0],1), dtype = np.float64))
		arguments = {self._input: inputs, self._output: outputs}
		return loss.forward(arguments, outputs = loss.outputs, keep_for_backward = loss.outputs)

	def backward_one_step(self, states, rewards, gradL_D):
		root_gradients = {v: gradL_D for v,o in rewards.items()}
		loss = self._loss
		vargrads_map = loss.backward(states,root_gradients, variables = loss.parameters)
		grads = dict()
		for var, grad in vargrads_map.items():
			grads[var] = grad
		updated = self._learner.update(grads,len(rewards))
		
def softmax(values):
	return math.log(sum (math.exp(value) for value in values))
