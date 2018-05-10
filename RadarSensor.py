
## @package Radar
#

import numpy as np
import math
import sys
import Vector
import Geometry
import cython
from GeometricRadar import GeometricRadar


## Wrapper for GeometricRadar, to allow for opaque robots (i.e., so the scan
# can pick up other robots) and auto-select the centerpoint of the scan instead
# of relying on the caller specify it.
#
# Many of the methods in this class are simple wrappers around methods in Radar
# or GeometricRadar, so see the documentation for those for more info.
#
class RadarSensor:
	## Constructor.
	#
	# @param robot
	# <br>  The robot this sensor will be attached to
	#
	# @param other_robots (list)
	# <br>  The other robots to scan for in the environment
	#
	# @param radar
	# <br>  The Radar to scan with (e.g., GeometricRadar)
	#
	# @param env
	# <br>  The environment
	#
	def __init__(self, env, robot, other_robots, radar):
		self._env = env
		self._robot = robot
		self._radar = radar

		self.set_other_robots(other_robots)


	def set_other_robots(self, other_robots):
		self._other_robots = other_robots


	def _robot_obs_list(self):
		return [other_robot.get_obstacle() for other_robot in self._other_robots if other_robot.get_obstacle() is not None]


	def scan(self, *args):
		return self.scan_obstacles_list(self._env.dynamic_obstacles + self._env.static_obstacles + self._robot_obs_list())


	@property
	def radius(self):
		return self._radar.radius

	@radius.setter
	def radius(self, value):
		self._radar.radius = value


	## Gets the degree step of the underlying Radar
	#
	def get_degree_step(self):
		return self._radar.get_degree_step();


	## Gets the size of the radar data returned from the scanning
	# methods.
	#
	def get_data_size(self):
		return self._radar.get_data_size();


	def scan_dynamic_obstacles(self, *args, **kwargs):
		return self.scan_obstacles_list(self._env.dynamic_obstacles + self._robot_obs_list())


	def scan_static_obstacles_one_by_one(self, center):
		return self.scan_obstacles_list_to_list(center, self._env.static_obstacles)


	def scan_dynamic_obstacles_one_by_one(self, center):
		return self.scan_obstacles_list_to_list(center, self._env.dynamic_obstacles + self._robot_obs_list())


	def scan_obstacles_list_to_list(self, center, obs_list):
		#center = self._robot.location
		return self._radar.scan_obstacles_list_to_list(center, obs_list)


	def scan_obstacles_list(self, obs_list):
		center = self._robot.location
		return self._radar.scan_obstacles_list(center, obs_list)


	def get_dynobs_at_angle(self, angle):
		center = self._robot.location
		return self._radar.get_dynobs_at_angle(center, angle)

