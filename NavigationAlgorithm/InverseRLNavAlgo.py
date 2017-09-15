#!/usr/bin/python3

from Robot import RobotControlInput
from .LinearNavAlgo import LinearNavigationAlgorithm


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

		if real_algo_init is None:
			real_algo_init = LinearNavigationAlgorithm
		self._real_algo = real_algo_init(sensors, target, cmdargs)

		self._radar   = self._sensors['radar'];
		self._radar_data = None
		self._dynamic_radar_data = None

		self._gps     = self._sensors['gps'];


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
	def select_next_action(self):
		return self._real_algo.select_next_action();


	def has_given_up(self):
		return False;


