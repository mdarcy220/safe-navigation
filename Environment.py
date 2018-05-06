#!/usr/bin/python3

## @package Environment
#

import numpy  as np
import pygame as PG
import DrawTool
from  DynamicObstacles import DynamicObstacle
import sys
import Vector


## Types of grid cells. Used in Environment grid_data
#
#
class ObsFlag:
	ANY_OBSTACLE     = 0b0001;
	DYNAMIC_OBSTACLE = 0b0010;
	STATIC_OBSTACLE  = 0b0100;


## Holds information related to the simulation environment, such as the
# position and motion of dynamic obstacles, and the static map.
#
class Environment:

	def __init__(self, width, height, map_filename, cmdargs=None):
		self.cmdargs = cmdargs
		self.width = width
		self.height = height
		self.dynamic_obstacles = []
		self.robots = []
		self.non_interactive_objects = []
		self._speed_mode = cmdargs.speedmode
		self._triggers = {'step': []}


	def add_robot(self, robot):
		if robot not in self.robots:
			self.robots.append(robot);

	def add_robots(self, robots):
		for robot in robots:
			self.add_robot(robot)

	def remove_robot(self, robot):
		self.robots.remove(robot)

	def remove_robot_by_name(self, robot_name):
		for robot in self.robots:
			if robot.name == robot_name:
				self.robots.remove(robot)
				return

	def add_trigger(self, exec_on, exec_func):
		if exec_on not in self._triggers:
			self._triggers[exec_on] = []
		self._triggers[exec_on].append(exec_func)


	def get_speed_mode(self):
		return self._speed_mode


	def load_map(self, map_filename):
		pass


	def apply_map_modifier_by_number(self, modifier_num):

		if (len(self.map_modifiers) <= modifier_num):
			return;
		map_modifier = self.map_modifiers[modifier_num];
		if map_modifier is None:
			return;

		map_modifier(self);


	def _update_dynamic_obstacles(self, timestep):
		for dynobs in self.dynamic_obstacles:
			dynobs.next_step(timestep);


	## Draws the environment onto the given display.
	#
	# @param dtool (`DrawTool` object)
	# <br>	-- The DrawTool to draw onto
	#
	def update_display(self, dtool):
		pass


	## Step the environment, updating dynamic obstacles
	#
	def next_step(self, timestep=1):
		for trigger in self._triggers['step']:
			trigger(timestep)

		self._update_dynamic_obstacles(timestep);

		for robot in self.robots:
			robot.next_step(timestep)


	## Checks what kind of obstacle the given point is
	# 
	# @param location (numpy array)
	# <br>  Format: `[x, y]`
	# <br>  -- Location to check
	#
	def get_obsflags(self, location):
		# Should be overridden by subclass
		# 0 means no obstacles
		return 0
