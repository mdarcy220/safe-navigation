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
		self._sensors = sensors;
		self._target  = target;
		self._cmdargs = cmdargs;
		self._max_steps = 600;
		self._max_loops = 5;
		self._lr = 0.1;
		self._decay = 0.99

		if real_algo_init is None:
			real_algo_init = LinearNavigationAlgorithm
		self._real_algo = real_algo_init(sensors, target, cmdargs)

		self._radar = self._sensors['radar'];
		self._radar_data = None
		self._dynamic_radar_data = None

		self._gps = self._sensors['gps'];
		self._mdp = self._sensors['mdp'];
		self._reward = self._init_reward();
		self.plot_reward(self._reward)

		self._valueIteration = ValueIterationNavigationAlgorithm(self._sensors, self._target, self._cmdargs);
		self._demonstrations = self._add_demonstration_loop(self._max_steps, self._max_loops);
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
	
	def _do_value_iter(self, reward):
		mdp = self._mdp
		gamma = 0.97


		old_values = {state: 0.0 for state in self._mdp.states()}
		old_values[self._mdp.goal_state()] = 1
		new_values = old_values

		qvals = dict()
		for state in mdp.states():
			qvals[state] = dict()
			for action in mdp.actions(state):
				qvals[state][action] = 0.0

		while True:
			old_values = new_values
			new_values = dict()
			for state in mdp.states():
				for action in mdp.actions(state):
					# Fear not: this massive line is just a Bellman-ish update
					qvals[state][action] = self._get_reward(state, action, reward) + gamma*sum(mdp.transition_prob(state, action, next_state)*old_values[next_state] for next_state in mdp.successors(state))

				## Softmax to get value
				#exp_qvals = {action: np.exp(qval) for action, qval in qvals[state].items()}
				#new_values[state] = max(exp_qvals.values())/sum(exp_qvals.values())

				# Just take the max to get values
				new_values[state] = max(qvals[state].values())

			# Quit if we have converged
			if max({abs(old_values[s] - new_values[s]) for s in mdp.states()}) < 0.01:
				break

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
		mdp = self._mdp
		reward = dict()
		num_states = len(mdp.states())
		rand = random.randint(0,num_states-1)
		for i, state in enumerate(mdp.states()):
		#	reward[state] =dict()
		#	num_actions = len(mdp.actions(state))
		#	for action in mdp.actions(state):
		#		reward[state][action] = 1.0/(num_states * num_actions)
			if i != rand:
				reward[state] = -1.0/num_states
			else:
				reward[state] = 1.0
				

		
		return reward
	
	def _get_reward(self, state, action, reward):
		return reward[state]
	
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
		reward = self._reward
		feat_true = dict()
		for state in mdp.states():
		    feat_true[state] = 0.0
		for traj in self._demonstrations:
			for (state, action, next_state, r) in traj:
			    feat_true[state] += 1/self._max_loops


		maxIter = 1000
		lr = self._lr
		decay = self._decay
		policy  = self._policy
		for i in range(maxIter):
			lr = lr*decay
			#new_demonstrations = self._add_demonstration_loop_local(self._max_steps, self._max_loops, policy)
			#newFeat = self._visitation_frequency(new_demonstrations)
			newFeat_mult = self._visitation_trajectory_frequency(self._demonstrations, policy)
			grad_avg = 0.0
			counter = 0
			for state in self._mdp.states():
				
				#for action in newFeat[state]:
				#	grad = feat_true[state][action] - newFeat[state][action]
				#	reward[state][action] += lr * grad
				#	grad_avg += grad
				#	counter +=1
				grad = feat_true[state] - newFeat_mult[state]
				#if state == (5,5):
				
				#print(grad)
					#print (feat_true[state])
					#print (newFeat_mult[state])
				reward[state] += lr*grad
				grad_avg += abs(grad)
				counter +=1
			sums = 0.0
			maxs = 0.0
			for state in mdp.states():
				if math.isnan(reward[state]):
					reward[state] = 0.0

			for state in mdp.states():
				reward[state] -= 0.00001

			
			policy = self._do_value_iter(reward)
			print(grad_avg/counter)
			if (abs(grad_avg/counter) < 10**-6):
			    break
			self.plot_reward(reward)

		print (max([max(reward[state].values()) for state in self._mdp.states()]))
		return reward

	

	def _visitation_frequency(self, demonstrations):
		mdp = self._mdp
		visited = dict()
		for state in mdp.states():
			#visited[state] = dict()
			#for action in mdp.actions(state):
			#	visited[state][action] = 0
			visited[state] = 0.0

		num_demonstrations = len(demonstrations)
		for demonstration in demonstrations:
			(state, action, _, r) = demonstration[0]
			visited[state] += 1/num_demonstrations
		
		return visited
	def _visitation_trajectory_frequency(self, demonstrations, policy):
		mdp = self._mdp
		states = dict()
		T = self._max_loops
		N = len(mdp.states())
		for i, state in enumerate(mdp.states()):
			states[state] = i
		mu = np.zeros([N, T])

		for demonstration in demonstrations:
			(s, a, sx, r) = demonstration[0]
			mu[states[s], 0] += 1
		mu[:,0] = mu[:,0]/T

		for s in mdp.states():
			for t in range(T-1):
				mu[states[s],t+1] = sum([mu[states[s_x],t] * mdp.transition_prob(s_x,s,self._get_action(s_x, policy)) for s_x in mdp.states()])
		p = np.sum(mu,1)
		visited = dict()
		for state in mdp.states():
			visited[state] = p[states[state]]
		return visited



	def plot_reward(self, rewards, figsize=(7,7)):
		sns.set(style="white")
		max_x = max([x for x,y in self._mdp.states()])
		max_y = max([y for x,y in self._mdp.states()])
		reward = np.zeros((max_x, max_y))
		for state in self._mdp.states():
			x,y = state
			reward[x-1,y-1] = rewards[state]

		plt.imshow(reward, cmap='hot', interpolation='nearest')

		plt.savefig('../output_data/reward_states_test3.png')
		pass


