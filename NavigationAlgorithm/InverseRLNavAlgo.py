#!/usr/bin/python3

from Robot import RobotControlInput
from .AbstractNavAlgo import AbstractNavigationAlgorithm
from .LinearNavAlgo import LinearNavigationAlgorithm  
from .ValueIterationNavAlgo import ValueIterationNavigationAlgorithm

import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import seaborn as sns
import math
import Vector

## Maximum Entropy Deep Inverse Reinforcement Learning navigation algorithm.
# This is actually just a wrapper around another navigation algorithm, and this
# class observes the actions of the real nav algo to do inverse RL.
#
class InverseRLNavigationAlgorithm(AbstractNavigationAlgorithm):

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
		# for states, the array is a 1D array, with entries as (y-1) *
		# width + x

		self._sensors = sensors;
		self._target  = target;
		self._cmdargs = cmdargs;
		self._max_steps = 52;
		self._max_loops = 1;
		self._lr = 0.01;
		self._decay = 0.99

		if real_algo_init is None:
			real_algo_init = LinearNavigationAlgorithm
		self._real_algo = real_algo_init(sensors, target, cmdargs)

		self._radar = self._sensors['radar'];
		self._radar_data = None
		self._dynamic_radar_data = None

		self._gps = self._sensors['gps'];
		self._mdp = self._sensors['mdp'];
		self._features = self._get_features();
		self._theta = self._init_theta();
		#self._reward = self._init_reward();
		self._reward = self._get_reward(self._features, self._theta)
		self.plot_reward(self._reward)

		#self._valueIteration = ValueIterationNavigationAlgorithm(self._sensors, self._target, self._cmdargs);
		#self._demonstrations = self._add_demonstration_loop(self._max_steps, self._max_loops);
		self._demonstrations = self.hand_crafted_demonstrations()
		self._policy = self._do_value_iter(self._reward)

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
	#def select_next_action(self):
	#	state = self._get_state();
	#	action = self._get_action(state);

	#	self._add_demonstration_step(state, action);

	#	return action;


	## Gets the state representation for IRL
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


		
	def _get_state(self):
		return (self._gps.location(), self._radar.scan(self._gps.location()));


	## Gets the action taken by the demonstrator for IRL
	#
	def _get_action(self, state):
		# We won't actually use the "state" parameter here, since the

		# real algo can scan the radar itself to get the state. It is
		# included because it could be used if we decided to use a
		# different type of demonstrator

		return self._real_algo.select_next_action();


	## Adds a (state, action) pair to the current demonstration for the IRL
	# algorithm.
	#
	def _add_demonstration_loop(self, max_steps, max_loops):
		demonstrations = []
		for loop in range(0,max_loops):
			start_state = (1000,1000)
			start_state = (random.randint(1,5), random.randint(17,19))
			#start_state = random.sample(self._mdp.states(),1)[0]
			demon_traj = self._valueIteration.add_demonstration_step(start_state,max_steps)
			demonstrations.append(demon_traj)
		return demonstrations

	def _add_demonstration_loop_local(self, max_steps, max_loops, policy):
		demonstrations = []
		for loop in range(0,max_loops):
			start_state = (1000,1000)
			start_state = (random.randint(1,5), random.randint(17,19))
			#start_state = random.sample(self._mdp.states(),1)[0]
			demon_traj = self._add_demonstration_step(start_state,max_steps, policy)
			demonstrations.append(demon_traj)
		return demonstrations


	def has_given_up(self):
		return False;
	"""
	def _do_value_iter(self, reward):
		mdp = self._mdp
		height = mdp._height
		width = mdp._width
		gamma = 0.97
		Z = 1.0 - mdp._walls
		# here we're assuming that 9 successor states do exist
		# in case less exist, then the value for the one that does not
		# exist will always be zero
		# ordered as
		#(x+1, y+1), (x+1,y), (x+1,y-1), (x, y+1),
		#(x,y), (x, y-1), (x-1, y+1), (x-1,y), (x-1,y-1)
		# and that we have 4 actions
		Z_a = np.zeros((height, width, 4))
		exp_reward = np.exp(reward)

		max_itertions = 10
		for i in range(max_itertions):
			for state in mdp.states():
				(x,y) = state
				successors = mdp.successors(state)
				actions = mdp.actions(state)
				for i, action in enumerate(actions):
					for successor in successors:
						trans = mdp.transition_prob(state, action, successor)
						(x_1,y_1) = successor
						Z_a[y,x,i] +=  trans * exp_reward[0,y_1*height + x_1] * Z[y,x]
			for state in mdp.states():
				(x,y) = state
				Z[y,x] = np.sum (Z_a[y,x,:])
		policy = dict()
		for state in mdp.states():
			policy[state] = dict()
			(x,y) = state
			for i, action in enumerate(mdp.actions(state)):
				policy[state][action] = Z_a[y,x,i]/ Z[y,x]
		#print('policies')
		#state = (1,18)
		#print([policy[state][action] for action in mdp.actions(state)])
		#state = (17,18)
		#print([policy[state][action] for action in mdp.actions(state)])
		#state = (17,1)
		#print([policy[state][action] for action in mdp.actions(state)])
		return policy
	"""
	def _do_value_iter(self, reward):
		mdp = self._mdp
		gamma = 0.993


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
					#qvals[state][action] = reward[0,y*mdp._width+x] + gamma*sum(mdp.transition_prob(state, action, next_state)*old_values[next_state] for next_state in mdp.successors(state))
					qvals[state][action] = mdp.reward(state,action,None) + gamma*sum(mdp.transition_prob(state, action, next_state)*old_values[next_state] for next_state in mdp.successors(state))

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


	def _init_reward(self):
		# the reward function is a 1D numpy array corresponding to
		# states
		# accessed as (y-1) * width + x
		# where {x,y} are the coordinates of the state
		mdp = self._mdp
		reward = np.zeros((mdp._height * mdp._width))
		num_states = reward.size
		reward[:] = -1.0/num_states
		return reward
	

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
		feature_mat = np.zeros((a_feature.size, mdp._height* mdp._width))
		for state in mdp.states():
			(x,y) = state
			feature_mat[:, y * mdp._width + x] = features[state]
			#print(feature_mat[:,(19-1) * mdp._width + 15])
		for i in range(feature_mat.shape[0]):
			feature_mat[i,:] = np.divide(feature_mat[i,:],abs(feature_mat[i,:]).max())

		return feature_mat
	
	def _init_theta(self):
		mdp = self._mdp
		features = mdp._features
		rand_state = random.sample(mdp.states(),1)
		a_feature = features[rand_state[0]]
		# testing with a smaller range of initial theata
		theta = np.random.uniform( 0.5, 0.8, (1,a_feature.size))
		theta[0,0] *= -1
		theta[0,2] *= -1
		theta[0,3] *= -1
		return theta
		

	def _get_reward(self, features, theta):
		reward = np.dot(theta,features)
		reward -= 0.1
		return reward
	
	def _get_action(self, state, policy):
		total = 0.0
		rand = np.random.random()
		for action in policy[state]:
			total += self._policy[state][action]
			if rand < total:
				return action
		return list(policy[state].keys())[random.randint(0,3)]


	## Adds a (state, action) pair to the current demonstration for the IRL
	# algorithm.
	#
	def _add_demonstration_step(self, state, max_steps, policy):
		# returns sequence of (state, action, next_state, reward)
		# until goal is reached, or max number of steps taken
		sequence = []
		steps = 0
		while state != self._mdp.goal_state() and steps < max_steps:
			# return (s, a, s', r)
			action = self._get_action(state, policy)
			next_state = self._mdp.get_successor_state(state, action)
			# the reward here is set to a trivial zero to decrease
			# redundant runtie because it is
			# not required later
			step = (state, action, next_state, 0.0)
			sequence.append(step)
			state = next_state
			steps += 1
		return sequence



	def IRLloop(self):
		mdp = self._mdp
		height = mdp._height
		width = mdp._width
		reward = self._reward
		feat_exp = np.zeros((self._features[:,0].shape))
		for traj in self._demonstrations:
			for (state, action, next_state, r) in traj:
				(x,y) = state
				visit_feat = self._features[:, y*height + x]
				feat_exp += visit_feat
		feat_exp /= self._max_loops


		maxIter = 1000
		lr = self._lr
		decay = self._decay
		policy  = self._policy

		#print (self._theta)
		#print (feat_exp)
		for i in range(maxIter):
			lr = lr*decay
			grad = np.zeros((self._features[:,0].shape))
			#new_demonstrations = self._add_demonstration_loop_local(self._max_steps, self._max_loops, policy)
			#newFeat = self._visitation_frequency(new_demonstrations)
			newFeat_mult = self._visitation_trajectory_frequency(self._demonstrations, policy)
			grad = feat_exp - np.dot(self._features, newFeat_mult)
			grad_avg  = sum(abs(grad))/grad.size
			grad = np.dot(grad,lr)
			#grad_exp = np.exp(grad)
			#self._theta *= grad_exp
			self._theta += np.dot(grad, lr)
			#self._theta /= self._theta.sum()
			reward = self._get_reward(self._features, self._theta)
			policy = self._do_value_iter(reward)
			if (grad_avg < 10**-6):
				break
			self.plot_reward_policy(reward,policy,i)
			#print (grad)
			
			print ('grad_avg: ', grad_avg)
			print ('theta: ', self._theta)
			#print (np.dot(self._features, newFeat_mult))

		print (max([max(reward[state].values()) for state in self._mdp.states()]))
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
			mu[y*height +x , 0] += 1
		mu[:,0] = mu[:,0]/T

		for t in range(T-1):
			for s in mdp.states():
				(x,y) = s
				#mu[y*height + x,t+1] = sum([mu[y*height + x,t] * mdp.transition_prob(s,self._get_action(s_x, policy),s_x) for s_x in mdp.successors(s)])
				mu[y*height + x,t+1] = sum([sum([mu[y*height + x,t] * mdp.transition_prob(s,action,s_x)*policy[s][action] for s_x in mdp.successors(s)]) for action in mdp.actions(s)])
		p = np.sum(mu,1)
		
		#for state in mdp.states():
		#	visited[state] = p[states[state]]
		return p



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
		ax = plt.axes()
		ax.arrow(0, 0, 0.5, 0.5, head_width=0.05, head_length=0.1, fc='k', ec='k')

		plt.savefig('../output_data/reward_states_test3.png')


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

