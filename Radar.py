import numpy as np
import sys
from Circle import *
import Vector, Geometry
import math


class Radar:

	def __init__(self, env, radius = 100, resolution = 4, degree_step = 1):

		self.env         = env
		self.radius	 = radius
		self.resolution  = resolution
		self.set_degree_step(degree_step);


	def ScanRadar(self, center, grid_data):

		radar_data = np.ones(int(360 / int(self._degree_step)))
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
					radar_data[currentStep] = i / self.radius
					break
				if (grid_data[x,y] & 1):
					radar_data[currentStep] = i / self.radius
					break
			currentStep = currentStep + 1
		return radar_data


	def set_degree_step(self, newDegreeStep):
		self._degree_step = newDegreeStep;
		# Recalculate beams
		self._nPoints = int(360 / int(self._degree_step)); 
		self._beams = np.zeros([self._nPoints, 2]);
		currentStep = 0
		for angle in np.arange(0, 360, self._degree_step):
			ang_in_radians = angle * np.pi / 180
			self._beams[currentStep] = Vector.unitVectorFromAngle(ang_in_radians) * self.radius
			currentStep += 1


	def get_dynobs_data_index_range(self, scan_center, dynobs):
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


	def scan_dynamic_obstacles(self, center, grid_data):
		nPoints = self._nPoints
		beams = self._beams
		radar_data = np.ones([nPoints], dtype=np.float64);
		sub_dynobs_list = [];
		for dynobs in self.env.dynamic_obstacles:
			index_range = self.get_dynobs_data_index_range(center, dynobs);
			if index_range is None:
				continue;
			for i in np.arange(index_range[0], index_range[1], 1):
				if dynobs.shape == 1:
					inters = Geometry.circle_line_intersection(dynobs.coordinate, dynobs.radius, [center, center+beams[i]]);
				elif dynobs.shape == 2:
					inters = Geometry.rectangle_line_intersection([dynobs.coordinate, np.array(dynobs.size)], [center, center+beams[i]]);
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
				radar_data[i] = np.min([radar_data[i], float(dist) / float(self.radius)]);
			
		return radar_data;


	def get_dynobs_at_angle(self, center, angle):
		ang_in_radians = angle * np.pi / 180.0;
		endpoint = center + np.array([np.sin(ang_in_radians), np.cos(ang_in_radians)], dtype=np.float64) * self.radius;
		min_dist = -1;
		closest_dynobs = None;
		for dynobs in self.env.dynamic_obstacles:
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

