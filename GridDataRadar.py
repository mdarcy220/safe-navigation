#!/usr/bin/python3

## @package Radar
#

import numpy as np
import sys
import Vector
import Geometry
import math
import cython
from Environment import ObsFlag

## Produces simulated radar output for the robot
#
# This class simulates a radar device. Using information from the
# environment, it produces a radar scan that shows the relative distance to
# obstacles.
#
#
# RADAR DATA FORMAT:
#
# Several methods in this class return a data format that will hereafter be
# referred to as the "radar data format". The details of this format are
# as follows:
#
# The radar data format is an array-like format, generally stored in a
# numpy array. The array contains the distance to the nearest obtacle at
# each of a range of angles. The angles are evenly distributed between 0
# and 360 degrees, so an array with 6 elements contains values for angles
# 0, 60, 120, 180, 240, and 300, in that order. More generally, if the
# array is called `radar_data`, then `radar_data[i]` corresponds to the
# angle given by `i * (360 / len(radar_data))`.
#
# Example: If the value of `radar_data` is `[24, 20, 21, 25]`, it could be
# interpreted in the following way: At an angle of 0 degrees from the
# center point, the nearest obstacle is 24 units away. At an angle of 90
# degrees, the nearest obstacle is 20 units away, and so on.
#
# The distances in radar data format are capped at the range of the radar,
# so if the radar range is 100, any angles for which no obstacle is
# observed will be reported as a distance of 100. For example, the array
# `[95, 99, 100, 90]` would indicate that no obstacle was observed at the
# angle of 180 degrees.
#
class GridDataRadar:


	## Constructor
	#
	# @param env (Environment object)
	# <br>	-- The environment (holds the information about the
	# 	obstacles for scanning)
	#
	# @param radius (float)
	# <br>	-- The range of the radar. Obstacles beyond this distance
	# 	will not be detected when scanning.
	#
	# @param resolution (int)
	# <br>	-- The resolution used for sampling-based scanning.
	# 
	# @param degree_step (float)
	# <br>	-- The increment for the scanning beam. This controls how
	# 	many different angles are checked for obstacles.
	#
	def __init__(self, env, radius = 100, resolution = 4, degree_step = 1):

		self._env        = env
		self.radius	 = radius
		self.resolution  = resolution
		self.set_degree_step(degree_step);


	## Produces a radar scan
	#
	# @param center (numpy array)
	# <br>	Format `[x, y]`
	# <br>	-- The center point of the scan
	#
	#
	# @returns (numpy array)
	# <br>	Format: `[ang1_val, ang2_val, ..., angn_val]`
	# <br>	-- An array of distances (in the range `[0, 1]`)
	# 	to the nearest obstacle for each angle outward from
	# 	`center`.  This starts from angle 0 and increases in
	# 	increments of the `degree_step` of the `Radar`, so
	# 	`output[i]` corresponds to angle `i * degree_step`. The
	# 	size of the output is then equal to
	# 	`floor(360/degree_step)`.
	#
	def scan(self, center, cell_type = ObsFlag.ANY_OBSTACLE):

		if cython.compiled:
			grid_data = self._env.grid_data;
			radar_data = np.full([self._nPoints], self.radius, dtype=np.float64);
			scan_generic(center[0],
				center[1],
				self.radius,
				grid_data,
				cell_type,
				self.resolution,
				self._degree_step,
				radar_data);
			return radar_data;

		grid_data = self._env.grid_data;

		radar_data = np.full([self._nPoints], self.radius, dtype=np.float64)
		currentStep = 0
		x_upper_bound = min(799, grid_data.shape[0])
		y_upper_bound = min(599, grid_data.shape[1])
		for degree in np.arange(0, 360, self._degree_step):
			ang_in_radians = degree * np.pi / 180
			cos_cached = np.cos(ang_in_radians)
			sin_cached = np.sin(ang_in_radians)
			for i in np.arange(0, self.radius, self.resolution):
				x = int(cos_cached * i + center[0])
				y = int(sin_cached * i + center[1])
				if ((x < 0) or (y < 0) or (x_upper_bound <= x) or (y_upper_bound <= y)):
					radar_data[currentStep] = i
					break
				if (grid_data[x,y] & cell_type):
					radar_data[currentStep] = i
					break
			currentStep = currentStep + 1
		return radar_data


	## Sets the degree step of the `Radar`.
	#
	# @param newDegreeStep (float)
	# <br>	-- the new degree step
	#
	def set_degree_step(self, newDegreeStep):
		self._degree_step = newDegreeStep;
		# Recalculate beams
		self._nPoints = int(360 / int(self._degree_step)); 
		self._beams = np.zeros([self._nPoints, 2]);
		currentStep = 0
		for angle in np.arange(0, 360, self._degree_step):
			ang_in_radians = angle * np.pi / 180
			self._beams[currentStep] = Vector.unit_vec_from_radians(ang_in_radians) * self.radius
			currentStep += 1


	## Gets the degree step
	#
	def get_degree_step(self):
		return self._degree_step;


	## Gets the size of the radar data returned from the scanning
	# methods.
	#
	def get_data_size(self):
		return self._nPoints;


	def _get_dynobs_data_index_range(self, scan_center, dynobs):
		angle_range = [0, 360];
		if dynobs.shape == 1:
			angle_range = Geometry.circle_circle_overlap_angle_range(scan_center, self.radius, dynobs.coordinate, dynobs.radius);
		elif dynobs.shape == 2:
			angle_range = Geometry.circle_rectangle_overlap_angle_range(scan_center, self.radius, dynobs.coordinate, np.array(dynobs.size));

		if angle_range is None:
			return None;
		index1 = np.ceil(angle_range[0] / self._degree_step);
		index2 = min(360, np.floor(angle_range[1] / self._degree_step));
		if index2 < index1:
			index1 -= self._nPoints;
		return [int(index1), int(index2)]


	## Produces a radar scan, ignoring static obstacles and including
	# only dynamic obstacles.
	#
	# 
	# @param center (numpy array)
	# <br>	Format `[x, y]`
	# <br>	-- The center point of the scan
	#
	# @returns (numpy array)
	# <br>	Format: `[ang1_val, ang2_val, ..., angn_val]`
	# <br>	-- An array of relative distances (in the range `[0, 1]`)
	# 	to the nearest dynamic obstacle for each angle outward from
	# 	`center`. This starts from angle 0 and increases in
	# 	increments of the `degree_step` of the `Radar`, so
	# 	`output[i]` corresponds to angle `i * degree_step`. The
	# 	size of the output is then equal to
	# 	`floor(360/degree_step)`.
	#
	def scan_dynamic_obstacles(self, center):
		return self.scan(center, cell_type = ObsFlag.DYNAMIC_OBSTACLE);
		#nPoints = self._nPoints
		#beams = self._beams
		#radar_data = np.full([nPoints], self.radius, dtype=np.float64);
		#sub_dynobs_list = [];
		#for dynobs in self._env.dynamic_obstacles:
		#	index_range = self._get_dynobs_data_index_range(center, dynobs);
		#	if index_range is None:
		#		continue;
		#	for i in np.arange(index_range[0], index_range[1], 1):
		#		if dynobs.shape == 1:
		#			inters = Geometry.circle_line_intersection(dynobs.coordinate, dynobs.radius, [center, center+beams[i]]);
		#		elif dynobs.shape == 2:
		#			inters = Geometry.rectangle_line_intersection([dynobs.coordinate, np.array(dynobs.size)], [center, center+beams[i]]);
		#		if len(inters) == 0:
		#			continue;

		#		inters_rel = np.array(inters) - center;
		#		dist = 1
		#		if len(inters) == 1:
		#			dist = Vector.magnitudeOf(inters_rel[0]);
		#		else:
		#			if np.dot(inters_rel[0], inters_rel[0]) < np.dot(inters_rel[1], inters_rel[1]):
		#				dist = Vector.magnitudeOf(inters_rel[0]);
		#			else:
		#				dist = Vector.magnitudeOf(inters_rel[1]);
		#		radar_data[i] = np.min([radar_data[i], float(dist)]);
		#	
		#return radar_data;


	## Gets the `DynamicObstacle` object corresponding to the nearest
	# dynamic obstacle along the beam at the specified angle.
	#
	#
	# @param center (numpy array)
	# <br>	Format `[x, y]`
	# <br>	-- The center point of the scan
	#
	# @param angle (float)
	# <br>	-- The angle (in degrees)
	#
	# @returns (float)
	# <br>	-- The relative distance to the nearest obstacle within the
	# 	radar's range at the given angle. The value is between 0
	# 	and 1.
	#
	def get_dynobs_at_angle(self, center, angle):
		ang_in_radians = angle * np.pi / 180.0;
		endpoint = center + Vector.unitVectorFromAngle(ang_in_radians) * self.radius;
		min_dist = -1;
		closest_dynobs = None;
		for dynobs in self._env.dynamic_obstacles:
			if dynobs.shape == 1:
				inters = Geometry.circle_line_intersection(dynobs.coordinate, dynobs.radius, [center, endpoint]);
			elif dynobs.shape == 2:
				inters = Geometry.rectangle_line_intersection([dynobs.coordinate, np.array(dynobs.size)], [center, endpoint]);
			if len(inters) == 0:
				continue;

			inters_rel = np.array(inters) - center;
			dist = 1
			if len(inters) == 1:
				dist = Vector.magnitudeOf(inters_rel[0]);
			else:
				if np.dot(inters_rel[0], inters_rel[0]) < np.dot(inters_rel[1], inters_rel[1]):
					dist = Vector.magnitudeOf(inters_rel[0]);
				else:
					dist = Vector.magnitudeOf(inters_rel[1]);

			if dist < min_dist or min_dist < 0:
				min_dist = dist;
				closest_dynobs = dynobs

		return closest_dynobs;

