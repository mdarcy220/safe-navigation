import math
import pygame as PG
import numpy  as np
import sys

class Radar:

	def __init__(self, screen, radius = 100, color = (236,179,223), resolution = 4):

		self.screen	 = screen
		self.radius	 = radius
		self.beam_color  = color
		self.resolution  = resolution
		self.image	 = PG.Surface([self.radius * 2,  self.radius * 2])
		self.image.fill((255,255,255))
		self.image.set_colorkey((255,255,255))
		self.degreeStep  = 1

	def ScanRadar(self, center, grid_data):

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
					radar_data[currentStep] = i / self.radius
					break
				if (grid_data[x,y] & 1):
					radar_data[currentStep] = i / self.radius
					break
				#self.screen.set_at((x, y), self.beam_color)
			currentStep = currentStep + 1
		return radar_data


	def scan_dynamic_obstacles(self, center, grid_data):

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
