#!/usr/bin/python3

import numpy  as np
import Vector
from .AbstractNavAlgo import AbstractNavigationAlgorithm
from .DynamicRrtNavAlgo import DynamicRrtNavigationAlgorithm
from .SamplingNavAlgo import SamplingNavigationAlgorithm
from .IntegratedEnvNavAlgo import IntegratedEnvNavigationAlgorithm
from Target import Target
from StaticMapper import StaticMapper


## A navigation algorithm to be used with robots, based on trajectory 
# sampling and RRT.
#
# @see
# \ref AbstractNavAlgo.AbstractNavigationAlgorithm
# 	"AbstractNavigationAlgorithm"
#
class GlobalLocalNavigationAlgorithm(AbstractNavigationAlgorithm):

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
	def __init__(self, sensors, target, cmdargs, global_algo_init = DynamicRrtNavigationAlgorithm, local_algo_init = SamplingNavigationAlgorithm):
		self._sensors = sensors;
		self._target  = target
		self._cmdargs = cmdargs;
		self._global_algo_init = global_algo_init;
		self._local_algo_init = local_algo_init;

		self._radar = sensors['radar'];
		self._gps   = sensors['gps'];
		sensors['mapper'] = StaticMapper(sensors);

		self.debug_info = {};

		self._waypoint_radius = 26

		self._global_algo = global_algo_init(sensors, target, cmdargs);
		self._next_waypoint = Target(self._gps.location(), radius = self._waypoint_radius);
		self._local_algo = local_algo_init(sensors, self._next_waypoint, cmdargs);
		self._tmp_counter = 0;


	def select_next_action(self):
		self._sensors['mapper'].add_observation(None, None, None);
		if self._tmp_counter > 30:
			self._tmp_counter = 0;
			self._global_algo = self._global_algo_init(self._sensors, self._target, self._cmdargs);
			self._global_algo.select_next_action();
			self._next_waypoint = Target(np.array(self._global_algo._solution[0].data), radius=self._waypoint_radius);
			self._local_algo = self._local_algo_init(self._sensors, self._next_waypoint, self._cmdargs);
		elif self._gps.distance_to(self._next_waypoint.position) < self._next_waypoint.radius or self._tmp_counter > 29:
			if self._gps.distance_to(self._next_waypoint.position) < self._next_waypoint.radius:
				self._tmp_counter = 0;
			self._global_algo.select_next_action();
			if len(self._global_algo._solution) > 0:
				self._next_waypoint = Target(np.array(self._global_algo._solution[0].data), radius=self._waypoint_radius);
			else:
				self._next_waypoint = self._target
			self._local_algo = self._local_algo_init(self._sensors, self._next_waypoint, self._cmdargs);
		self._tmp_counter += 1;
		next_action = self._local_algo.select_next_action();
		self.debug_info = {**self._local_algo.debug_info, **self._global_algo.debug_info};
		return next_action;
