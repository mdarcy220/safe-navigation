#!/usr/bin/python3

import numpy  as np
from numpy import linalg as LA
import cntk
#import cntk.contrib
import cntk_deeprl
import gym.spaces as gs
import Vector
from .AbstractNavAlgo import AbstractNavigationAlgorithm
from RobotControlInput import RobotControlInput
from .ValueIterationNavAlgo import ValueIterationNavigationAlgorithm, generic_value_iteration
import random
import math
import matplotlib.pyplot as plt
import os
import sys
import json

## A navigation algorithm to be used with robots, based on deep q-learning.
#
# @see
# \ref AbstractNavAlgo.AbstractNavigationAlgorithm
# 	"AbstractNavigationAlgorithm"
#
class DeepQIRLAlgorithm(AbstractNavigationAlgorithm):

	default_config = {
		'max_iters': sys.maxsize,
		'png_output_interval': 5000,
		'gpu_id': 1,
	}

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
	def __init__(self, sensors, target, cmdargs):
		self._sensors = sensors;
		self._cmdargs = cmdargs;
		self._target = target;
		self._config = DeepQIRLAlgorithm.default_config
		if os.path.isfile('local_configs/deep_q_irl_config.json'):
			with open('local_configs/deep_q_irl_config.json', 'r') as f:
				# Write keys in a loop to keep any defaults
				# that are not specified in the config file
				tmp_config = json.load(f)
				for key in tmp_config:
					self._config[key] = tmp_config[key]

		try:
		    cntk.try_set_default_device(cntk.device.gpu(self._config['gpu_id']));
		except:
		    cntk.try_set_default_device(cntk.device.cpu())

		#self._radar   = self._sensors['radar'];
		#self._radar_data = None
		#self._dynamic_radar_data = None

		#self._gps     = self._sensors['gps'];

		self._normal_speed = float(cmdargs.robot_speed);

		self.debug_info = {};

		##########################
		# ### IRL parameters ### #
		self._max_steps = 200;
		self._max_loops = 300;
		self._lr = 0.8;
		self._decay = 0.9
		self._IRLmaxIter = 1;
		# ### IRL parameters ### #
		##########################
		
		self._stepNum = 0;
		self._mdp = self._sensors['mdp'];
		self._features_DQN = self._get_features_DQN();
		self._features_IRL = self._get_featuresi_IRL();

		self._o_space_shape= (1,self._features_DQN[random.sample(self._mdp.states(),1)[0]].size)

		self._o_space = gs.Box(low=0, high=1, shape=self._o_space_shape);
		self._a_space = gs.Discrete(4);
		#self.learner = cntk_deeprl.agent.policy_gradient.ActorCritic # actor critic trainer
		self.learner = cntk_deeprl.agent.qlearning.QLearning # qlearning trainer
		if self.learner == cntk_deeprl.agent.qlearning.QLearning:
			self._qlearner = self.learner('local_configs/deepq_1.ini', self._o_space, self._a_space);
		elif self.learner == cntk_deeprl.agent.policy_gradient.ActorCritic:
			self._qlearner = self.learner('local_configs/polify_gradient_1.ini', self._o_space, self._a_space);
		else:
			raise TypeError("Invalid type for _qlearner")

		self.maxIter = self._config['max_iters']
		self._valueIteration = ValueIterationNavigationAlgorithm(self._sensors, self._target, self._cmdargs);
		self._demonstrations = self._add_demonstration_loop(self._max_steps, self._max_loops);
		# the following action set assumes that all
		# states have the same action set
		actions_set = self._mdp.actions(self._mdp._goal_state)
		self._actions = list([action for action in actions_set])
		self.IRL_network = IRL_network(self._features_IRL[:,0].shape,self._lr, hidden_layers = [50,50,20,20,10])
		#self.IRL_network = IRL_network(self._features_IRL[:,0].shape,self._lr, hidden_layers = [1000,800,600,400,200,100,10])
		self.main_loop()


	## Next action selector method.
	#
	# @see 
	# \ref AbstractNavAlgo.AbstractNavigationAlgorithm.select_next_action
	# 	"AbstractNavigationAlgorithm.select_next_action()"
	#
	def main_loop(self):
		max_k = 5000
		#IRL_network = self.IRL_network
		# reward is state based dictionary, reward_map is ND matrix
		reward, reward_map = self.forward_reward(self.IRL_network)
		for k in range(1,max_k):
			# get_policy requires state based dictionary of rewards
			policy = self.get_policy(reward)

			reward, reward_map = self.get_reward(self.IRL_network,policy)

			self.plot_reward_policy(reward_map,policy,k)

	def select_next_action(self):
		self._stepNum += 1;
		return RobotControlInput(0, 0)

	def _get_features_DQN(self):
		mdp = self._mdp
		features = mdp._features
		return features
	
	def _get_featuresi_IRL(self):
		# in this method we retrieve the features from the mdp
		# and we transform the from a dictionary of column vectors
		# to a 2D matrix
		# each column representing the feature vector for 
		# one of the states, ordered according to the general {x,y}
		mdp = self._mdp
		features = mdp._features
		rand_state = random.sample(mdp.states(),1)
		a_feature = features[rand_state[0]]
		feature_mat = np.zeros((a_feature.size, mdp._height* mdp._width), dtype = np.float32)
		for state in mdp.states():
			(x,y) = state
			feature_mat[:, y * mdp._width + x] = features[state]
			#print(feature_mat[:,(19-1) * mdp._width + 15])
		# Uncomment the following to normalize features
		#for i in range(feature_mat.shape[0]):
		#	feature_mat[i,:] = np.divide(feature_mat[i,:],abs(feature_mat[i,:]).max())

		return feature_mat
	
	def _add_demonstration_loop(self, max_steps, max_loops):
		demonstrations = []
		mdp = self._mdp
		height = mdp._height
		width = mdp._width
		for loop in range(0,max_loops):
			start_state = (1000,1000)
			while True:
			    start_state = (random.randint(1,math.ceil(self._mdp._width)-1), random.randint(math.ceil(self._mdp._height/8),math.ceil(self._mdp._height)-1))
			    #start_state = (random.randint(1,math.ceil(self._mdp._width/2)), random.randint(math.ceil(self._mdp._height/2),math.ceil(self._mdp._height)-3))
			    #start_state = (random.randint(1,1), random.randint(18,18))
			    if (self._mdp._walls[start_state[1], start_state[0]] == 0):
				    break
			#start_state = random.sample(self._mdp.states(),1)[0]
			demon_traj = self._valueIteration.add_demonstration_step(start_state,max_steps)
			if len(demon_traj) > 0:
			    demonstrations.append(demon_traj)
			#feat_exp = np.zeros((1,len(mdp.states())), dtype=np.float32)
			#for (state, action, next_state, r) in demon_traj:
			#	(x,y) = state
			#	feat_exp[0,y*width + x] += 1
			
			#self.show_reward(feat_exp,loop)
		return demonstrations


	def _do_value_iter(self, reward):
		def reward_func(state, action):
			return reward[0,state[1]*self._mdp._width+state[0]]
		return generic_value_iteration(self._mdp, reward_func, gamma=0.995, max_iter=1000, threshold=0.05)

	def get_reward(self, network, policy):
		mdp = self._mdp
		width = mdp._width
		height = mdp._height
		features = self._features_IRL

		states, rewards = network.forward_one_step(np.vstack(features.T))
		reward = list(rewards.values())[0].T
		
		#############################################
		# #### maxIter is placed for future use ### #
		# currently it can only take the value of 1 #
		maxIter = self._IRLmaxIter
		#############################################

		old_grad = np.zeros((features[:,0].shape))
		lr = self._lr
		decay = self._decay

		#self.show_reward(feat_exp,0)
		# tests contains test scenarios with different maps, start and
		# goal positions
		#tests = TestCases(self._cmdargs)
		count =0
		# sample size to take a batch of demonstrations each time
		sample_size = 100
		for i in range(maxIter):
			demon_traj = random.sample(self._demonstrations,sample_size)
			feat_exp = np.zeros((1,len(mdp.states())), dtype=np.float32)
			for traj in demon_traj:
				for (state, action, next_state, r) in traj:
					(x,y) = state
					feat_exp[0,y*width + x] += 1
			feat_exp /= sample_size
			
			newFeat_mult = self._visitation_trajectory_frequency(self._demonstrations, policy)
			grad = feat_exp - newFeat_mult
			grad = np.dot(grad, np.float32(lr))
			self.show_reward(grad)
			
			network.backward_one_step(states, rewards, np.vstack(grad.T))
			
			#if i%7 == 0:
				#lr = lr * decay
				#tests.solve_mdps(network,count)
				#count += 1

			states, rewards = network.forward_one_step(np.vstack(features.T))
			reward = list(rewards.values())[0].T
			#self.plot_reward_policy(reward,policy,i)
			#self.plot_reward(reward)
			print('grad_norm: ', LA.norm(grad))
			if i==0:
				old_grad = grad
				continue
			print ('grad_diff: ', LA.norm(grad-old_grad))
			old_grad = grad
		
		### Here rewards is the state based dictionary of rewards ###
		### and reward is the N-D array, where N is the number of ###
		### ############### per state (so far 1) ################ ###

		rewards = dict()	
		for state in mdp.states():
			(x,y) = state
			rewards[state] = reward[0,y*width+x]

		return rewards, reward

	def forward_reward(self, network):
		# ## Forward the reward network to get current reward ## #
		# ## for each state given its feature vector ######## ## #
		mdp = self._mdp
		width = mdp._width
		height = mdp._height
		features = self._features_IRL

		states, rewards = network.forward_one_step(np.vstack(features.T))
		reward = list(rewards.values())[0].T
		
		rewards = dict()	
		for state in mdp.states():
			(x,y) = state
			rewards[state] = reward[0,y*width+x]
		# rewards is a dictionary,while reward is a ND matrix
		return rewards, reward
	
	
	def get_policy(self, rewards):
		mdp = self._mdp
		goal_state = mdp._goal_state
		actions = self._actions
		max_dist = math.sqrt(mdp._width ** 2 + mdp._height ** 2)
		updates = 0
		counter = 0
		features = self._features_DQN
	
		##################################################
		# ## first step, empty qlearner step memory ######
		# ## as they are reward related, and the reward ##
		# ## map should have changed since the last call #
		
		self._qlearner._replay_memory.empty_memory()
		
		# ## then enter all the demonstration steps to the memory

		for traj in self._demonstrations:
			for i, (state, action, next_s, r) in enumerate(traj):
				reward = rewards[next_s]
				action = actions.index(action) 
				if i==0:
					last_state = self._qlearner._preprocess_state(
					    np.vstack(features[state]).T)
				else:
					last_state = next_state
				next_state = self._qlearner._preprocess_state(
				    np.vstack(features[next_s]).T)
				self._qlearner._replay_memory.store(
				    last_state,
				    action,
				    reward,
				    next_state,
				    0)

		#################################################
		# ## then start normal exploration exploitation #
		# ## and calculate the new policy accordingly ###

		memory_size = len(self._qlearner._replay_memory._memory)
		current_state = (mdp._goal_state[0]-1,mdp._goal_state[1]-1)
		start_position = current_state
		current_observation = np.vstack(features[current_state]).T
		current_action = self._qlearner.start(current_observation)

		#######################################################
		# #### to avoid overwhelming demonstration data ##### #
		# ## add steps n times equal to demonstration data ## #

		###############################################
		# ## n can be looked at as a ratio between ## #
		# ## randomly generated steps, and demonstration step
		# ## presented for the DQN network ########## #
		n = 0.4
		###############################################
		print ('DQN')

		for iteration in range(math.ceil(self._max_steps * self._max_loops * n)):
			action = actions[current_action[0]]
			next_state = mdp.get_successor_state(current_state,action)
			
			reward = rewards[next_state]
			observation = np.vstack(features[next_state]).T
			
			counter += 1
			
			(x,y) = next_state
			wall = mdp._walls[y,x]
			
			if next_state == mdp._goal_state or wall == 1 or counter > 1000:
				counter =0
				#print (next_state,reward,self._qlearner._evaluate_q(self._qlearner._q,observation),start_position)
				self._qlearner.step(reward,observation)
				updates += 1 
				current_state = self.start_position(updates)
				start_position = current_state
				observation = np.vstack(features[current_state]).T

				self._qlearner.start(observation)
				#print ('DQN', iteration)
			else:
				current_action = self._qlearner.step(reward,observation)
				#if iteration == 0:
					#print (self._qlearner._replay_memory._memory[memory_size-1])
					#print (self._qlearner._replay_memory._memory[memory_size])

				#print ('step', reward)
				current_state = next_state
			if iteration % self._config['png_output_interval'] == 0 and iteration>0:
				##TODO: assess policy, and save the one with the highest reward #
				self.calc_policy(iteration,actions)
				#print (self.assess_policy(self._qlearner,rewards,actions))
		return self.calc_policy(0,actions)
	
	def start_position(self, iteration):
		dispersion_factor = 0.5
		dispersion = iteration * dispersion_factor
		goal = self._mdp._goal_state
		x_range = (max(0,int(goal[0] - dispersion)), min (self._mdp._width-1,int( goal[0]+dispersion)))
		y_range = (max(0,int(goal[1] - dispersion)), min (self._mdp._height-1,int( goal[1]+dispersion)))
		while True:
			newPos = (random.randint(x_range[0],x_range[1]), random.randint(y_range[0],y_range[1]))
			if self._mdp._walls[newPos[1],newPos[0]] == 0:
				return newPos

	def calc_policy(self, iteration, actions):
		mdp = self._mdp
		policy = dict()
		rewards = np.zeros((1,mdp._height * mdp._width))
		features = self._features_DQN
		for state in mdp.states():
			(x,y) = state
			observation = np.vstack(features[state]).T
			if self.learner == cntk_deeprl.agent.policy_gradient.ActorCritic: # actor critic trainer
				qvals_actions = self._qlearner._evaluate_model(self._qlearner._policy_network, observation)
			elif self.learner == cntk_deeprl.agent.qlearning.QLearning: # qlearning trainer
				qvals_actions = self._qlearner._evaluate_q(self._qlearner._q,observation)
			sum_qvals = sum(qvals_actions)
			#print (qvals_actions)
			#break
			
			policy[state] = dict()
			for i,action in enumerate(actions):
				policy[state][action] = qvals_actions[i]/sum_qvals#math.exp(qvals_actions[i] - sum_qvals)

		#self.plot_reward_policy(rewards, policy, iteration)
		return policy
	
	def assess_policy(self, network, reward, actions):
		# return the average reward over a number of paths
		# all starting from a random location
		# and following the generated policy
		gamma = network._parameters.gamma
		features = self._features_DQN
		samples = 20
		r_avg = [0] * samples
		for i in range(samples):
			starting_position = self.random_start_position()
			r_avg[i] += reward[starting_position]
			current_step = starting_position
			for step in range(self._max_steps):
				q_values = network._evaluate_q(network._q,np.vstack(features[current_step]).T)
				max_index = np.argmax(q_values)
				action = actions[max_index]
				next_step = self._mdp.get_successor_state(current_step,action)
				r_avg[i] += reward[next_step] * gamma ** step
				current_step = next_step

		return sum (r_avg)/samples

	def random_start_position(self):
		while True:
			newPos = (random.randint(1,self._mdp._width-1), random.randint(1,self._mdp._height-1))
			if self._mdp._walls[newPos[1],newPos[0]] == 0:
				return newPos
	
	def _visitation_trajectory_frequency(self, demonstrations, policy):
		mdp = self._mdp
		height = mdp._height
		width = mdp._width
		T = self._max_steps
		N = height * width
		mu = np.zeros([N, T], dtype=np.float32)

		for demonstration in demonstrations:
			(s, a, sx, r) = demonstration[0]
			(x,y) = s
			mu[y*width +x , 0] += 1/self._max_loops
		mu[:,0] = mu[:,0]/T

		for t in range(T-1):
			mu_old = mu
			mu[mdp.goal_state(), t] = 0
			for s in mdp.states():
				(x,y) = s
				#mu[y*width + x,t+1] = sum([mu[y*width + x,t] * mdp.transition_prob(s,self._get_action(s_x, policy),s_x) for s_x in mdp.successors(s)])
				mu[y*width + x,t+1] = sum([sum([mu_old[y_*width + x_,t] * mdp.transition_prob((x_,y_),action,s)*policy[(x_,y_)][action]  for action in mdp.actions((x_,y_))]) for (x_,y_) in mdp.successors(s)])
		p = np.sum(mu,1)
		return p

	def plot_reward_policy(self, reward_map, policy, iteration=0, dpi=196.0):
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
			ax.arrow(state[0], state[1], avgarrow_vec[0]*0.1, avgarrow_vec[1]*0.1, head_width = scale * max(min(1,avgarrow_mag),0.3), head_length = scale * max(min(1,avgarrow_mag),0.3), color='r')

			# maxarrow points in the single most likely direction
			max_action = max((item for item in action_values.items()), key=lambda item: item[1])
			maxarrow_vec = Vector.unit_vec_from_degrees(max_action[0][0])
			ax.arrow(state[0], state[1], 0.1*maxarrow_vec[0], 0.1*maxarrow_vec[1], head_width= scale * max(min(1,max_action[1]),0.3), head_length = scale *max(min(1,max_action[1]),0.3), color='g')

		# Output the figure to the image file
		plt.savefig('../output_data/r_p{:02d}.png'.format(iteration))
		plt.close()


	def show_reward(self, reward_map, dpi=196.0):
		# Set up the figure
		plt.gcf().set_dpi(dpi)

		# Note that we're messing with the input args here
		reward_map = reward_map.reshape(self._mdp._height, self._mdp._width)
		plt.imshow(reward_map, cmap='hot', interpolation='nearest')

		#plt.show()
		plt.savefig('../output_data/grad.png')
		plt.close()


class IRL_network:
	
	def __init__(self, n_input, lr, hidden_layers = [300,400], l2 = 1, name='deep_irl_fc'):
		self._input = cntk.input_variable(n_input)
		self._output_size = l2
		self._lr_schedule = cntk.learning_rate_schedule(lr, cntk.UnitType.sample)
		self._output = cntk.input_variable(self._output_size)
		self.name = name
		self._num_hidden_layers = len(hidden_layers)
		self._hidden_layers = hidden_layers
		self._model,self._loss, self._learner, self._trainer = self.create_model()

	def create_model(self):
		hidden_layers = self._hidden_layers
		with cntk.layers.default_options(init = cntk.layers.glorot_uniform(), activation = cntk.ops.relu):
			h = self._input
			for i in range(self._num_hidden_layers):
				h = cntk.layers.Dense(hidden_layers[i])(h)
			model = cntk.layers.Dense(self._output_size, activation = None)(h)
			loss = cntk.reduce_mean(cntk.square(model - self._output), axis=0)
			meas = cntk.reduce_mean(cntk.square(model - self._output), axis=0)
			learner = cntk.adadelta(model.parameters, self._lr_schedule)
			trainer = cntk.Trainer(model, (loss,meas), learner)
			return model, loss, learner, trainer
	def forward_one_step(self, inputs):
		loss = self._loss
		outputs = np.vstack(np.ones((inputs.shape[0],1), dtype = np.float32))
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
