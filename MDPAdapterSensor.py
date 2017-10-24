#!/usr/bin/env -p python3

import numpy as np
import math

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
	def __init__(self, env, start_state, goal_state, cell_size=30, num_actions=4, robot_speed=10):
		self._env = env
		self._cell_size = cell_size
		self._start_state = self.discretize(start_state)
		self._goal_state = self.discretize(goal_state)
		self._height = int(np.ceil(env.height/cell_size))
		self._width = int(np.ceil(env.width/cell_size))
		self._walls = self._init_walls(self._env, self._cell_size)
		self._states = self._init_states(env, cell_size)
		self._actions = MDPAdapterSensor._init_actions(num_actions, robot_speed)
		self._transition_table = self._init_transition_table()
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
		walls = np.zeros((self._height,self._width))
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
		x = state[0]
		y = state[1]
		possible_successors = {(x+1, y+1),
		        (x+1, y),
		        (x+1, y-1),
		        (x, y+1),
		        (x, y),
		        (x, y-1),
		        (x-1, y+1),
		        (x-1, y),
		        (x-1, y-1)
		       }
		#return {state for state in possible_successors if state in self._states }
		return {state for state in possible_successors if state in self._states and self._walls[state[1],state[0]] <1}


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
		scaled_speed = 3*action[1]/self._cell_size

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
		return -0.5


	def _get_features(self, states, walls, goal):
		features = dict()
		max_dist = math.sqrt(self._height ** 2 + self._width ** 2)
		for state in states:
			(x,y) = state
			
			feature = np.zeros(5)
			if walls[y,x] == 1:
				feature[0:4] = max_dist
			else:
				i=1
				while(walls[y+i,x] == 0):
					i += 1
				feature[0] = i
				i=1
				while(walls[y-i,x] == 0):
					i += 1
				feature[1] = i
				i=1
				while(walls[y,x+i] == 0):
					i += 1
				feature[2] = i
				i=1
				while(walls[y,x-i] == 0):
					i += 1
				feature[3] = i
			feature[4] = math.sqrt((x - goal[0]) ** 2 + (y - goal[1]) ** 2 )
			features[state] = feature
			"""
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




