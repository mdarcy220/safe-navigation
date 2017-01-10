#!/usr/bin/python3

## @package ObstaclePredictor
#

import numpy as np;
import Vector

## Abstract base class for obstacle predictors.
#
# Obstacle predictors use observations of past obstacles to predict future
# locations of obstacles.
# 
# To use this class, the `#add_observation()` method should be called exactly
# once for every time step. If no observation is made for a time step,
# `#add_observation()` should still be called as follows to indicate the
# absence of an observation:
# 
# `#add_observation(None, None, None, None)`
# 
#
# The `get_prediction` method is not subject to the same restrictions as
# `#add_observation()`, and may be called as needed, possibly multiple times
# per time step and possibly only once every several time steps.
#
class AbstractObstaclePredictor:
	## Constructor
	#
	# @param data_size (int)
	# <br>	-- The number of data points in the `radar_data` and
	# `dynamic_obstacle_data` parameters that will be passed to
	# `#add_observation()`
	#
	def __init__(self, data_size):
		self.data_size = data_size;
		pass;


	## Adds an observation to use when predicting future obstacle
	# states.
	# 
	# This method should be called exactly once for each time step.
	# Even if no observations are made for a step, it should be called
	# as `#add_observation(None, None, None, None)`. If this condition
	# is not met, no guarantees are made about the accuracy of
	# `#get_prediction()`.
	#
	# @param location (numpy array)
	# <br>	Format: `[x, y]`
	# <br>	-- The location at which this observation was made
	# 	(location of the robot).
	#
	# @param radar_data (numpy array)
	# <br>	Format: `[ang_1_distance, ang_2_distance, ..., ang_n_distance]`
	# <br>	-- An array containing the distance to the
	# 	nearest obtacle (of any type; static or dynamic) at each of
	# 	a range of angles. The angles should be evenly distributed
	# 	between 0 and 360 degrees, so an array with 6 elements
	# 	would be expected to contain values for angles 0, 60, 120,
	# 	180, 240, and 300, in that order. More generally,
	# 	`radar_data[i]` should correspond to the angle given by
	# 	`i * (360 / len(radar_data))`. The size of the array must
	# 	be the same as the value of `#data_size` that this class
	# 	was initialized with.
	# <br>	See also: `Radar.Radar.scan`
	#
	# @param dynamic_obstacle_data (numpy array)
	# <br>	Format: `[ang_1_distance, ang_2_distance, ..., ang_n_distance]`
	# <br>	-- An array containing the distance to the nearest dynamic
	# 	obstacle at each of a range of angles. This is exactly the
	# 	same as `radar_data`, except that it should contain only
	# 	the data for dynamic obstacles, and not for the static
	# 	ones. Again, it must have exactly `#data_size` elements.
	#
	# @param func_get_dynamic_obstacle_at_angle (function)
	# <br>	-- A function that returns a
	# 	`DynamicObstacle.DynamicObstacle` object given an angle.
	# 	The returned object should be the nearest dynamic obstacle
	# 	at the given angle. The function should be callable as
	# 	follows, if `angle` is the angle (in degrees) to test:
	# <br>	`func_get_dynamic_obstacle_at_angle(angle)`
	# <br>	The caller must guarantee that the function will return the
	# 	correct dynamic obstacle at least until the next time
	# 	`#add_observation()` is called.
	#
	#
	# @returns nothing
	# 
	def add_observation(self, location, radar_data, dynamic_obstacle_data, func_get_dynamic_obstacle_at_angle):
		pass;


	## Gets the probability of an obstacle existing at the specified
	# point at the specified number of steps in the future.
	#
	# @param point (numpy array)
	# <br>	Format `[x, y]`
	# <br>	-- The point to test
	#
	# @param num_steps_in_future (int)
	# <br>	-- The number of steps in the future to check at. This
	# 	starts from 0, so if `num_steps_in_future` is 0 the
	# 	function will return the probability as estimated at the
	# 	time of the most recent observation. If it is 1 the
	# 	function will return the estimated value for one step after
	# 	the most recent observation, and so on.
	#
	# 
	# @returns (float)
	# <br>	-- A value in the closed interval [0, 1], representing the
	# 	probability that the given point will be occupied by an
	# 	obstacle at the given number of steps in the future. If an
	# 	error occurs, this function returns a negative number.
	#
	def get_prediction(self, point, num_steps_in_future):
		pass;



## This is a basic placeholder implentation of the
# AbstractObstaclePredictor class. Its predictions should not be relied
# upon.
#
class DummyObstaclePredictor(AbstractObstaclePredictor):
	def __init__(self, data_size):
		# Might be good to cache values from observations to use
		# later. Let's initialize them now.
		self.data_size = data_size;
		self.last_location = None;
		self.last_radar_distribution = None;
		self.last_dynamic_obstacle_distribution = None;
		self.last_obstacle_getter_func = None;


	## Dummy `#add_observation()` method. It has some commented-out
	# examples to illustrate how to do basic things
	#
	def add_observation(self, location, radar_all, radar_dynamic, get_obs_at_angle):
		# We'll need the given values to make up-to-date
		# predictions, so let's store this most recent
		# observation's values. Of course, this is a dummy
		# implementation, so we aren't actually going to do
		# anything with the values.
		self.last_location = location;
		self.last_radar_distribution = radar_all;
		self.last_dynamic_obstacle_distribution = radar_dynamic;

		# This get_obs_at_angle function is especially important to
		# update, since the one passed in from the previous call is
		# no longer guaranteed to work.
		self.last_obstacle_getter_func = get_obs_at_angle;

		# If we wanted to see how close the nearest dynamic
		# obstacle was at the angle 75, we could do this:
		angle = 75;
		index = int(np.round(angle * (self.data_size / 360.0)));
		distance = radar_dynamic[index];

		# If we wanted to, we could try calculate the area covered
		# by the closest dynamic obstacle at angle 75:
		dynobs = get_obs_at_angle(75);
		if dynobs is not None:
			shape = dynobs.shape # Circle = 1, Rectangle = 2
			area = 0
			if shape == 1:
				area = np.pi * dynobs.radius * dynobs.radius
			elif shape == 2:
				area = dynobs.size[0] * dynobs.size[1]

		# Maybe we want to know exactly where the edge of the
		# dynamic obstacle at angle 75 is. We can start by taking
		# the `distance` variable we computed earlier and using it
		# to scale a unit vector in the specified direction. It
		# should be noted that the Vector.unitVectorFromAngle()
		# method takes an angle in radians, unlike most other
		# methods
		edge_point = location + (distance * Vector.unitVectorFromAngle(75 * np.pi / 180));


	## Dummy method to get predictions
	#
	def get_prediction(self, location, time):
		# This method would use the data from previously added
		# observations to figure out where obstacles will be in the
		# future.

		# If we determined that there is a 62% chance of an
		# obstacle being at the point `location` at `time` steps in
		# the future, we could write:
		# return 0.62

		# Since this is just a dummy class, we aren't going to make
		# any predictions
		return -1;


## HMM-based obstacle predictor
#
# This is just a skeleton for now. More will be added later
#
class HMMObstaclePredictor(AbstractObstaclePredictor):
	## See the corresponding superclass method for details
	#
	def __init__(self, data_size):
		pass;


	## See the corresponding superclass method for details
	#
	def add_observation(self, location, radar_all, radar_dynamic, get_obs_at_angle):
		pass;

	
	## See the corresponding superclass method for details
	#
	def get_prediction(self, location, time):
		return -1;
