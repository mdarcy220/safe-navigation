#!/usr/bin/env -p python3

import numpy as np


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
		self._states = MDPAdapterSensor._init_states(env, cell_size)
		self._actions = MDPAdapterSensor._init_actions(num_actions, robot_speed)


	def discretize(self, continuous_state):
		return (continuous_state[0]//self._cell_size, continuous_state[1]//self._cell_size)


	def _init_states(env, cell_size):
		states = set()
		for x in range(int(np.ceil(env.width/cell_size))+1):
			for y in range(int(np.ceil(env.height/cell_size))+1):
				states.add((x, y))
		return states


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
		return {state for state in possible_successors if state in self._states}


	def transition_prob(self, state, action, next_state):
		# Some of the numbers are a little tricky here; they need to be
		# scaled down by the cell size because the entire state space
		# is also scaled down by the cell size

		cur_x = state[0]
		cur_y = state[1]

		direction = action[0]
		# Scaled-down speed
		scaled_speed = action[1]/self._cell_size

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

		return overlap_area / scaled_cell_area


	def start_state(self):
		return self._start_state

	def goal_state(self):
		return self._goal_state


	def reward(self, state, action, next_state):
		return self.transition_prob(state, action, self._goal_state)

