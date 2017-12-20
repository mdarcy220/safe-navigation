#!/usr/bin/python3

## @package Radar
#

import numpy as np
import sys
import Vector
import Geometry
import cython
from Radar import Radar

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
class GeometricRadar(Radar):


	## Constructor
	#
	# @param env (GeometricEnvironment object)
	# <br>	-- The environment (holds the information about the
	# 	obstacles for scanning)
	#
	# @param radius (float)
	# <br>	-- The range of the radar. Obstacles beyond this distance
	# 	will not be detected when scanning.
	#
	# @param degree_step (float)
	# <br>	-- The increment for the scanning beam. This controls how
	# 	many different angles are checked for obstacles.
	#
	def __init__(self, env, radius = 100, degree_step = 1):

		self._env        = env
		self.radius	 = radius
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
	def scan(self, center):
		return self.scan_obstacles_list(center, self._env.dynamic_obstacles + self._env.static_obstacles)


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


	def _get_obs_data_index_range(self, scan_center, obs):
		angle_range = [0, 360];
		if obs.shape == 1:
			angle_range = Geometry.circle_circle_overlap_angle_range(scan_center, self.radius, obs.coordinate, obs.radius);
		elif obs.shape == 2:
			angle_range = Geometry.circle_rectangle_overlap_angle_range(scan_center, self.radius, obs.coordinate, np.array(obs.size));
		elif obs.shape == 3:
			angle_range = Geometry.circle_circle_overlap_angle_range(scan_center, self.radius, obs.coordinate, max(obs.width,obs.height)/2);
		elif obs.shape == 4:
			points = obs.polygon.get_vertices()
			min_x = min(points, key=lambda p: p[0])[0]
			max_x = max(points, key=lambda p: p[0])[0]
			min_y = min(points, key=lambda p: p[1])[1]
			max_y = max(points, key=lambda p: p[1])[1]
			rect_pos = [min_x, min_y]
			rect_size = np.subtract((max_x, max_y), rect_pos)
			angle_range = Geometry.circle_rectangle_overlap_angle_range(scan_center, self.radius, rect_pos, rect_size);

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
	# 	`center`. This starts from angle 0 and increases in increments
	# 	of the `degree_step` of the `Radar`, so `output[i]` corresponds
	# 	to angle `i * degree_step`. The size of the output is then
	# 	equal to `floor(360/degree_step)`.
	#
	def scan_dynamic_obstacles(self, center):
		return self.scan_obstacles_list(center, self._env.dynamic_obstacles)


	## Produces a radar scan, including only obstacles in `obs_list`.
	#
	# 
	# @param center (numpy array)
	# <br>	Format `[x, y]`
	# <br>	-- The center point of the scan
	#
	# @param obs_list (list of DynamicObstacle)
	# <br>  -- The list of obstacles to include in the scan
	#
	# @returns (numpy array)
	# <br>	Format: `[ang1_val, ang2_val, ..., angn_val]`
	# <br>	-- An array of relative distances (in the range `[0, 1]`)
	# 	to the nearest dynamic obstacle for each angle outward from
	# 	`center`. This starts from angle 0 and increases in increments
	# 	of the `degree_step` of the `Radar`, so `output[i]` corresponds
	# 	to angle `i * degree_step`. The size of the output is then
	# 	equal to `floor(360/degree_step)`.
	#
	def scan_obstacles_list(self, center, obs_list):
		beams = self._beams
		radar_data = np.full([self._nPoints], self.radius, dtype=np.float64);

		for obs in obs_list:
			index_range = self._get_obs_data_index_range(center, obs);
			if index_range is None:
				continue;
			for i in np.arange(index_range[0], index_range[1], 1):
				dist = self._obs_dist_along_line(obs, (center, center+beams[i]))
				radar_data[i] = np.min([radar_data[i], float(dist)]);
			
		return radar_data;


	## Gets the distance to the given obstacle along the given line segment
	# (i.e., the distance from the first endpoint of the segment to the
	# intersection of the line and the obstacle). Returns float('inf') if
	# there are no intersections.
	def _obs_dist_along_line(self, obs, line):
		if obs.shape == 1:
			inters = Geometry.circle_line_intersection(obs.coordinate, obs.radius, line);
		elif obs.shape == 2:
			inters = Geometry.rectangle_line_intersection([obs.coordinate, np.array(obs.size)], line);
		elif obs.shape == 3:
			vec = obs.get_velocity_vector()
			angle = np.arctan2(vec[1], vec[0])
			inters = Geometry.ellipse_line_intersection(obs.coordinate, obs.width, obs.height, angle, line);
		elif obs.shape == 4:
			poly = obs.polygon
			inters = poly.line_intersection(line);

		if len(inters) == 0:
			return float('inf')

		inters_rel = np.array(inters) - line[0];
		dist = float('inf')
		if len(inters) == 1:
			dist = Vector.magnitudeOf(inters_rel[0]);
		elif np.dot(inters_rel[0], inters_rel[0]) < np.dot(inters_rel[1], inters_rel[1]):
			dist = Vector.magnitudeOf(inters_rel[0]);
		else:
			dist = Vector.magnitudeOf(inters_rel[1]);

		return dist


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
			dist = self._obs_dist_along_line(dynobs, (center, endpoint))
			if dist < min_dist or min_dist < 0:
				min_dist = dist;
				closest_dynobs = dynobs

		return closest_dynobs;

