#!/usr/bin/python3


import numpy  as np
import Vector
from .AbstractNavAlgo import AbstractNavigationAlgorithm
from Robot import RobotControlInput


## Implementation of the Dynamic Window algorithm for robotic navigation.
#
# @see
# \ref AbstractNavAlgo.AbstractNavigationAlgorithm
# 	"AbstractNavigationAlgorithm"
#
class DWANavigationAlgorithm(AbstractNavigationAlgorithm):
	def __init__(self, robot, cmdargs):
		# Init basic members
		self._robot = robot;
		self._cmdargs = cmdargs;
		self._normal_speed = cmdargs.robot_speed;
		self._stepNum = 0;

		# Set using_safe_mode to appease Robot.draw()
		self.using_safe_mode = True;

		self.debug_info = {
			'drawing_pdf': np.zeros(360)
		};


	## Next action selector method.
	#
	# @see 
	# \ref AbstractNavAlgo.AbstractNavigationAlgorithm.select_next_action
	# 	"AbstractNavigationAlgorithm.select_next_action()"
	#
	def select_next_action(self):
		self._stepNum += 1;
		#radar_data = self._robot.radar.scan(self._robot.location);
		#dynamic_radar_data = self._robot.radar.scan_dynamic_obstacles(self._robot.location);

		# We can cheat and get the grid data by accessing a private member
		# DO NOT MODIFY THIS GRID DATA, or it will modify the actual
		# environment. If you need to modify it, make a copy of it and
		# modify the copy.
		#grid_data = self._robot.radar._env.grid_data;

		direction = np.random.uniform(low=0, high=360);

		return RobotControlInput(self._normal_speed, direction);

