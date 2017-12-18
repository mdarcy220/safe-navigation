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


	def load_map(self, map_filename):
		pass


	## Sets the speed mode of the obstacles
	#
	# Currently, these modes are defined as follows:
	# <br>	0. No speed mode (leave speeds as default)
	# <br>	1. All obstacles move at speed 4
	# <br>	2. All obstacles move at speed 8
	# <br>	3. Obstacles move at the robot's normal speed
	# <br>	4. Roughly half the obstacles move at speed 4, the other
	# 	half move at speed 8
	# <br>	5. All obstacles move at speed 6
	# <br>	6. All obstacles move at speed 12
	#
	#
	# @param speedmode (int)
	# <br>	-- The number of the speed mode to set
	#
	def set_speed_mode(self, speedmode):
		for obstacle in self.dynamic_obstacles:
			if speedmode == 0:
				pass; # Leave obstacle speeds as default
			elif speedmode == 1:
				obstacle.speed = 4;		 
			elif (speedmode == 2):
				obstacle.speed = 8;
			elif speedmode == 3:
				obstacle.speed = self.cmdargs.robot_speed;
			elif speedmode == 4:
				obstacle.speed = np.array ([4, 8])[np.random.randint(2)];
			elif speedmode == 5:
				obstacle.speed = 6;
			elif speedmode == 6:
				obstacle.speed = 12;
			elif speedmode == 7:
				obstacle.speed = 5;
			elif speedmode == 8:
				obstacle.speed = self.cmdargs.robot_speed;
			elif speedmode == 9:
				obstacle.speed = 15;
			elif speedmode == 10:
				obstacle.speed = np.random.uniform(low=5.0, high=15.0);
			else:
				sys.stderr.write("Invalid speed mode. Assuming mode 0.\n");
				sys.stderr.flush();
				break;


	def apply_map_modifier_by_number(self, modifier_num):

		if (len(self.map_modifiers) <= modifier_num):
			return;
		map_modifier = self.map_modifiers[modifier_num];
		if map_modifier is None:
			return;

		map_modifier(self);


	def _update_dynamic_obstacles(self):
		for dynobs in self.dynamic_obstacles:
			dynobs.next_step();


	## Draws the environment onto the given display.
	#
	# @param dtool (`DrawTool` object)
	# <br>	-- The DrawTool to draw onto
	#
	def update_display(self, dtool):
		pass


	## Step the environment, updating dynamic obstacles
	#
	def next_step(self):
		self._update_dynamic_obstacles();


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
