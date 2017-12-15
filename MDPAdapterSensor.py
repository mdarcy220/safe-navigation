#!/usr/bin/env -p python3

import numpy as np
import math
import os
import pickle
import sys

class MDP:
	def __init__(self):
		pass

	def get_states(self):
		pass

	def get_actions(self, state):
		pass;

	def get_successors(self, state, action):
		pass

	def get_start_state(self):
		pass

	def get_goal_state(self):
		pass

	def get_reward(self, state, action, next_state):
		pass



# The Env->MDP adapter.
# A good obstacle model remains lacking. It wouldn't be hard to add some logic
# to the transition function to handle them manually, but the hard part is
# getting the obstacle states automatically from the environment, especially
# moving obstacles.
#
class MDPAdapterSensor(MDP):
	## Init the adapter
	# 
	# @param num_actions (int)
	# <br>	The number of actions that should be available (i.e., possible
	# 	directions; the default of 4 would be NESW for example)
	# 
	def __init__(self, env, start_state, goal_state, cell_size=30, num_actions=4, robot_speed=10, unique_id='', local = False):
		self._env = env
		self._cell_size = cell_size
		self._start_state = self.discretize(start_state)
		self._goal_state = self.discretize(goal_state)
		self._height = int(np.ceil(env.height/cell_size))
		self._width = int(np.ceil(env.width/cell_size))
		self._walls = self._init_walls(self._env, self._cell_size)
		print (self._goal_state, self._walls[self._goal_state[1],self._goal_state[0]])
		self._states = self._init_states(env, cell_size)
		self._actions = MDPAdapterSensor._init_actions(num_actions, robot_speed)
		self.local = local

		trans_table_filename = '{}_{:d}_{:d}.pickle'.format(unique_id, cell_size, num_actions)
		if os.path.isfile(trans_table_filename):
			with open(trans_table_filename, 'rb') as f:
				self._transition_table = pickle.load(f)
		else:
			self._transition_table = self._init_transition_table()
			if unique_id != '':
				with open(trans_table_filename, 'wb') as f:
					pickle.dump(self._transition_table, f)

		self._features = self._get_features(self._states, self._walls, self._goal_state)


	def _init_transition_table(self):
		transition_table = {}
		for state in self._states:
			transition_table[state] = {}
			for action in self._actions:
				transition_table[state][action] = {}
				for next_state in self._states:
					prob = self._compute_transition_prob(state, action, next_state)
					if 0 < prob:
						transition_table[state][action][next_state] = prob
		return transition_table


	def discretize(self, continuous_state):
		return (continuous_state[0]//self._cell_size, continuous_state[1]//self._cell_size)


	def _init_states(self, env, cell_size):
		states = set()
		for x in range(self._width):
			for y in range(self._height):
				states.add((x, y))
		return states

	def _init_walls(self, env, cell_size):
		# numpy array with entry of zero if free space and one if
		# not free
		# entries are according to states, y for columns and x for rows
		grid_data = env.grid_data
		walls = np.zeros((self._height,self._width), dtype=np.float32)
		for x in range(self._width):
			for y in range(self._height):
				temp_wall = grid_data[x*cell_size:(x+1)*cell_size-1,y*cell_size:(y+1)*cell_size-1]
				walls[y,x] = 1 if np.sum(temp_wall) > 0 else 0
		return walls


	
	def _init_actions(num_actions, robot_speed):
		return {(action, robot_speed) for action in np.arange(0, 360, 360/num_actions)}


	def states(self):
		return self._states


	def actions(self, state):
		return self._actions


	def get_cell_size(self):
		return self._cell_size


	## Returns successors for the given state
	#
	def successors(self, state):
		all_successors = set()
		for action in self._transition_table[state].keys():
			all_successors |= {successor for successor in self._transition_table[state][action].keys() if self._walls[successor[1],successor[0]] < 1}
			if((state[1] == 13 or state[1] == 5) and self.local):
				successors = set(all_successors)
				for successor in successors:
					(x,y) = successor
					if(y == state[1] - 1 or y == state[1]):
						all_successors.remove(successor)
						
					
		return all_successors


	def get_successor_state(self, state, action):
	  transition_probs = []
	  next_states = []
	  for next_state in self.successors(state):
	    next_states.append(next_state)
	    transition_probs.append(self.transition_prob(state, action, next_state))
	  return next_states[transition_probs.index(max(transition_probs))]


	def transition_prob(self, state, action, next_state):
		if state not in self._transition_table:
			return self._compute_transition_prob(state, action, next_state)
		if action not in self._transition_table[state]:
			return self._compute_transition_prob(state, action, next_state)
		if next_state not in self._transition_table[state][action]:
			return 0
		return self._transition_table[state][action][next_state]


	def _compute_transition_prob(self, state, action, next_state):
		# Some of the numbers are a little tricky here; they need to be
		# scaled down by the cell size because the entire state space
		# is also scaled down by the cell size

		cur_x = state[0]
		cur_y = state[1]

		direction = action[0]
		# Scaled-down speed
		#scaled_speed = action[1]/self._cell_size
		scaled_speed = 1.0

		next_x = next_state[0]
		next_y = next_state[1]

		# Because everything is scaled down, all cells in the state
		# space are 1x1
		scaled_cell_area = 1.0

		# Get the area of overlap of the next state with the current
		# state shifted based on the action
		action_x = scaled_speed * np.cos(np.pi*direction/180)
		action_y = scaled_speed * np.sin(np.pi*direction/180)

		shifted_cur_x = cur_x + action_x
		shifted_cur_y = cur_y + action_y

		# Cell dimensions are 1x1 in the scaled-down state space, hence
		# the 1-minus-abs instead of cell_size-minus-abs for
		# calculating overlap
		overlap_x = max(0, 1 - abs(next_x - shifted_cur_x))
		overlap_y = max(0, 1 - abs(next_y - shifted_cur_y))

		overlap_area = overlap_x * overlap_y
		if self._walls[next_y,next_x] != 0:
			return 0
		return overlap_area / scaled_cell_area


	def start_state(self):
		return self._start_state

	def goal_state(self):
		return self._goal_state



	def reward(self, state, action, next_state):
		reachGoalProb = self.transition_prob(state, action, self._goal_state)
		if reachGoalProb > 0:
			return reachGoalProb
		return 0.0

	def _get_features(self, states, walls, goal):
		features = dict()
		max_dist = math.sqrt(self._height ** 2 + self._width ** 2)
		for state in states:
			(x,y) = state
			
			if y>=13:
				if x<15:
					local_goal = (14,13)
				else:
					local_goal = (x,13)
			elif(y>=8):
				local_goal = (12,5)
			elif(y>=5):
				if x>11:
					local_goal = (12,5)
				else:
					local_goal = (x,5)
			else:
				local_goal = goal
			#local_goal = goal
			"""
			feature = np.zeros(2)
			feature[0] = x
			feature[1] = y
			"""
			feature = np.zeros(3, dtype=np.float32)
			if walls[y,x] == 1:
				feature[0:3] = 0
				#feature[6] = 1
				#feature[0:6] = 0
				#feature[5] = 1
				#feature[0:4] = 0
				#feature[5] = 100
			else:
				#feature[5] = 0
				#i=1
				#while(walls[y+i,x] == 0):
				#	i += 1
				#feature[0] = i/max_dist
				i=1
				while(walls[y-i,x] == 0):
					i += 1
				feature[2] =  i/max_dist
				#i=1
				#while(walls[y,x+i] == 0):
				#	i += 1
				#feature[2] = i/max_dist
				#i=1
				#while(walls[y,x-i] == 0):
				#	i += 1
				#feature[3] = i/max_dist
				#i=1
				#while(walls[y+i,x+i] == 0):
				#	i += 1
				#feature[6] =100 * (max_dist - i*math.sqrt(2))/max_dist
				#i=1
				#while(walls[y-i,x-i] == 0):
				#	i += 1
				#feature[7] = 100 * (max_dist - i*math.sqrt(2))/max_dist
				#i=1
				#while(walls[y+i,x-i] == 0):
				#	i += 1
				#feature[8] = 100 * (max_dist - i*math.sqrt(2))/max_dist
				#i=1
				#while(walls[y-i,x+i] == 0):
				#	i += 1
				#feature[9] = 100 * (max_dist - i*math.sqrt(2))/max_dist
			#feature[4] =  (max_dist -  math.sqrt((x - goal[0]) ** 2 + (y - goal[1]) ** 2 ))/max_dist
			#feature = np.zeros(2)
				feature[0] = max_dist/(abs(x-local_goal[0]) +0.1*max_dist)
				feature[1] = max_dist/(abs(y-local_goal[1]) + 0.1*max_dist)
			"""
			features[state] = feature
			# testing with a simpler feature vector
			# f_1 is a negative number if state is wall
			# f_2 is max_dist - dist to goal
			feature = np.zeros(2)
			if walls[y,x] == 1:
				feature[0] = -max_dist
			feature[1] = max_dist - math.sqrt((x - goal[0]) ** 2 + (y - goal[1]) ** 2 )
			
			feature = np.zeros(2)
			temp = np.zeros(2)
			if walls[y,x] == 1:
				#feature[0:1] = 0
				feature[0] = 1
				#feature[2] = 0
			else:
				#temp[0] = abs(self._height/2 - y)/self._height
				#temp[1] = abs(self._width/2 -  x)/self._width
				#feature[0] = 1 if temp[0] > temp[1] else 0
				#feature[1] = 1 - feature[0]
				feature[0] = 0
				#if (walls[y+1,x] ==1 or walls[y-1,x] ==1 or walls[y,x+1] ==1 or walls[y,x-1] ==1):
				#	feature[0] = 1
				#	feature[2] = 1
				#	feature[3] = 0
				#elif (walls[y+2,x] ==1 or walls[y-2,x] ==1 or walls[y,x+2] ==1 or walls[y,x-2] ==1):
				#	feature[0] = 1
				#	feature[2] = 1
				#	feature[3] = 1
				#else:
				#	feature[2] = 0
				#	feature[3] = 0

			dist = math.sqrt((x - goal[0]) ** 2 + (y - goal[1]) ** 2 )
			if(dist < 5.0 and walls[y,x] == 0):
				feature[1] = 1
				#feature[2] = 1
			else:
				feature[1] = 0
			"""
			
			features[state] = feature
		return features


## Class to get features from MDP states
#
class MdpFeatureExtractor:
	## Constructor
	#
	# @param feature_names (list-like)
	# <br>	Format: `[name1, name2, ...]`
	# <br>	A list of names of features to include in the feature vector
	# 
	# @param feature_params (dict)
	# <br>	Format: `{name1: {param1: value1, ...}, name2: ...}`
	# <br>	A dict with keys being the feature names from the
	# 	`feature_names` parameter, and values being dicts of specific
	# 	parameters to configure the extraction of those features.
	#
	def __init__(self, feature_names, feature_params=dict()):
		self._feature_names = feature_names
		self._feature_params = feature_params

		# This extractor cache allows feature extractors to store
		# information between calls for different states. This can be
		# useful when it is easiest to compute the value of a feature
		# for all states in one pass and cache the result so all later
		# calls can complete in O(1) time
		self._extractor_cache = {name: dict() for name in feature_names}

		# Functions to map feature names to the functions used to
		# extract them
		self._feature_extractor_funcs = self._init_feature_extractor_funcs()


	def _init_feature_extractor_funcs(self):
		return {
			'nearest_wall_dist_0deg': MdpFeatureExtractor._feature_nearest_wall_dist_0deg,
			'nearest_wall_dist_45deg': MdpFeatureExtractor._feature_nearest_wall_dist_45deg,
			'nearest_wall_dist_90deg': MdpFeatureExtractor._feature_nearest_wall_dist_90deg,
			'nearest_wall_dist_135deg': MdpFeatureExtractor._feature_nearest_wall_dist_135deg,
			'nearest_wall_dist_180deg': MdpFeatureExtractor._feature_nearest_wall_dist_180deg,
			'nearest_wall_dist_225deg': MdpFeatureExtractor._feature_nearest_wall_dist_225deg,
			'nearest_wall_dist_270deg': MdpFeatureExtractor._feature_nearest_wall_dist_270deg,
			'nearest_wall_dist_315deg': MdpFeatureExtractor._feature_nearest_wall_dist_315deg,
			'goal_dist': MdpFeatureExtractor._feature_goal_dist,
			'inverse_goal_dist': MdpFeatureExtractor._feature_inverse_goal_dist,
			'iswall': MdpFeatureExtractor._feature_iswall,
		}
		

	def extract_feature_dict(self, mdp):
		features = dict()
		for state in mdp.states():
			features[state] = []
			for feature_name in self._feature_names:
				feature_params = self._feature_params[feature_name] if feature_name in self._feature_params else dict()
				features[state].append(self._feature_extractor_funcs[feature_name](state, mdp, feature_params, self._extractor_cache[feature_name]))
			features[state] = np.array(features[state], dtype=np.float32)
		return features


	def _feature_iswall(state, mdp, params, cache):
		if 'scale' not in cache:
			if 'scale' in params:
				cache['scale'] = params['scale']
			else:
				cache['scale'] = 100
		scale = cache['scale']

		x, y = state

		return (scale if mdp._walls[y, x] == 1 else 0)


	def _nearest_wall_dist_extractor_generic(angle_degrees, state, mdp, params, cache):
		angle_radians = angle_degrees * np.pi / 180

		# These selectors will control the direction in which the wall
		# is searched for
		x_component = np.cos(angle_radians)
		y_component = np.sin(angle_radians)

		# To move square by square in the grid, we need to make the
		# step size the distance to the edge of a unit square in the
		# direction of the unit vector (x_component, y_component).
		# For example, this is 1 when the vector points a direction
		# like (0, 1) but is sqrt(2) if the vector is pointing a 45
		# degrees.
		step_dist = 1.0 / max(abs(x_component), abs(y_component))

		if 'max_dist' not in cache:
			cache['max_dist'] = math.sqrt(mdp._height ** 2 + mdp._width ** 2)
		max_dist = cache['max_dist']

		if 'scale' not in cache:
			if 'scale' in params:
				cache['scale'] = params['scale']
			else:
				cache['scale'] = 100
		scale = cache['scale']

		x, y = state

		if mdp._walls[y, x] == 1:
			return 0

		dist = step_dist
		while (mdp._walls[int(round(y + y_component*dist)), int(round(x + x_component*dist))] == 0):
			dist += step_dist
		return scale * (max_dist - dist)/max_dist


	def _feature_nearest_wall_dist_0deg(state, mdp, params, cache):
		return MdpFeatureExtractor._nearest_wall_dist_extractor_generic(0, state, mdp, params, cache)


	def _feature_nearest_wall_dist_45deg(state, mdp, params, cache):
		return MdpFeatureExtractor._nearest_wall_dist_extractor_generic(45, state, mdp, params, cache)


	def _feature_nearest_wall_dist_90deg(state, mdp, params, cache):
		return MdpFeatureExtractor._nearest_wall_dist_extractor_generic(90, state, mdp, params, cache)


	def _feature_nearest_wall_dist_135deg(state, mdp, params, cache):
		return MdpFeatureExtractor._nearest_wall_dist_extractor_generic(135, state, mdp, params, cache)


	def _feature_nearest_wall_dist_180deg(state, mdp, params, cache):
		return MdpFeatureExtractor._nearest_wall_dist_extractor_generic(180, state, mdp, params, cache)


	def _feature_nearest_wall_dist_225deg(state, mdp, params, cache):
		return MdpFeatureExtractor._nearest_wall_dist_extractor_generic(225, state, mdp, params, cache)


	def _feature_nearest_wall_dist_270deg(state, mdp, params, cache):
		return MdpFeatureExtractor._nearest_wall_dist_extractor_generic(270, state, mdp, params, cache)


	def _feature_nearest_wall_dist_315deg(state, mdp, params, cache):
		return MdpFeatureExtractor._nearest_wall_dist_extractor_generic(315, state, mdp, params, cache)


	def _feature_goal_dist(state, mdp, params, cache):
		if 'max_dist' not in cache:
			cache['max_dist'] = math.sqrt(mdp._height ** 2 + mdp._width ** 2)
		max_dist = cache['max_dist']

		if 'scale' not in cache:
			if 'scale' in params:
				cache['scale'] = params['scale']
			else:
				cache['scale'] = 100
		scale = cache['scale']

		goal = mdp._goal_state
		x, y = state

		return scale * (max_dist - math.sqrt((x - goal[0]) ** 2 + (y - goal[1]) ** 2))/max_dist


	def _feature_inverse_goal_dist(state, mdp, params, cache):
		if 'max_dist' not in cache:
			cache['max_dist'] = math.sqrt(mdp._height ** 2 + mdp._width ** 2)
		max_dist = cache['max_dist']

		if 'scale' not in cache:
			if 'scale' in params:
				cache['scale'] = params['scale']
			else:
				cache['scale'] = 100
		scale = cache['scale']

		goal = mdp._goal_state
		x, y = state

		return scale * max_dist/(max_dist - math.sqrt((x - goal[0]) ** 2 + (y - goal[1]) ** 2))

