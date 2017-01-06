import numpy  as np
import sys
from Circle import *
import Vector

class Radar:

	def __init__(self, env, radius = 100, color = (236,179,223), resolution = 4, degreeStep = 1):

		self.env         = env
		self.radius	 = radius
		self.beam_color  = color
		self.resolution  = resolution
		self.degreeStep  = degreeStep

		
		self.nPoints = int(360 / int(self.degreeStep)); 
		self.beams = np.zeros([self.nPoints, 2]);
		currentStep = 0
		for angle in np.arange(0, 360, self.degreeStep):
			ang_in_radians = angle * np.pi / 180
			self.beams[currentStep] = Vector.unitVectorFromAngle(ang_in_radians) * self.radius
			currentStep += 1


	def ScanRadar(self, center, grid_data):

		radar_data = np.ones(int(360 / int(self.degreeStep)))
		currentStep = 0
		x_upper_bound = min(799, grid_data.shape[0])
		y_upper_bound = min(599, grid_data.shape[1])
		for degree in np.arange(0, 360, self.degreeStep):
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


	def scan_dynamic_obstacles(self, center, grid_data):
		nPoints = self.nPoints
		beams = self.beams
		radar_data = np.ones(nPoints);

		sub_dynobs_list = [];
		for dynobs in self.env.dynamic_obstacles:
			thresh = (dynobs.radius + self.radius) * (dynobs.radius + self.radius)
			dist = np.dot(dynobs.coordinate - center, dynobs.coordinate - center)
			if dist < thresh:
				sub_dynobs_list.append(dynobs);

		for i in np.arange(0, nPoints, 1):
			for dynobs in sub_dynobs_list:
				inters = circle_line_intersection(np.array(list(dynobs.coordinate)), dynobs.radius, [center, center+beams[i]]);

				if len(inters) == 0:
					continue;

				inters_rel = np.array(inters) - center;
				if len(inters) == 1:
					radar_data[i] = Vector.magnitudeOf(inters_rel[0]);
				else:
					if np.dot(inters_rel[0], inters_rel[0]) < np.dot(inters_rel[1], inters_rel[1]):
						radar_data[i] = Vector.magnitudeOf(inters_rel[0]);
					else:
						radar_data[i] = Vector.magnitudeOf(inters_rel[1]);
		return radar_data;

	def scan_dynamic_obstacles_old(self, center, grid_data):

		radar_data = np.ones(int(360 / int(self.degreeStep)))
		currentStep = 0
		x_upper_bound = min(799, self.screen.get_width())
		y_upper_bound = min(599, self.screen.get_height())
		for degree in np.arange(0, 360, self.degreeStep):
			ang_in_radians = degree * np.pi / 180
			cos_cached = np.cos(ang_in_radians)
			sin_cached = np.sin(ang_in_radians)
			for i in np.arange(0, self.radius, self.resolution):
				x = int(cos_cached * i + center[0])
				y = int(sin_cached * i + center[1])
				if ((x < 0) or (y < 0) or (x_upper_bound <= x) or (y_upper_bound <= y)):
					radar_data[currentStep] = 1
					break
				if (grid_data[x, y] & 2):
					radar_data[currentStep] = i / self.radius
					break
				#self.screen.set_at((x, y), self.beam_color)
			currentStep = currentStep + 1
		return radar_data
