import numpy as np
import pygame as PG
import Vector

class DynamicObs:
	def __init__(self):
		self.radius		=  0
		self.coordinate		= np.array([0,0])
		self.origin		= np.array([0,0])
		self.size		= [50,50]
		self.fillcolor		= (34,119,34)
		self.bordercolor	= (255,0,0)
		self.movement_mode	= 1
		self.shape		= 1
		self.speed		= 8
		self.tempind		= 1
		self.path_list		= []
		self.cur_path_ind	= 0

	def set_coordinate(self, coordinate):
		self.coordinate = coordinate

	def set_radius(self, radius):
		self.radius = radius

	def NextStep(self):
		if (self.movement_mode == 1):
			self.coordinate = np.add(self.coordinate, np.random.uniform(-self.speed, self.speed, size=[2]))
		elif (self.movement_mode == 2):
			self.tempind += 10
			self.coordinate = np.add(self.origin, [int(np.cos(self.tempind * np.pi / 180) * 30), int(np.sin(self.tempind * np.pi / 180) * 30)])
			if self.tempind == 360:
				self.tempind = 0
		elif (self.movement_mode == 3):
			if not self.cur_path_ind:
				self.cur_path_ind = 0
			if (not self.path_list) or (len(self.path_list) == 0):
				return
			elif (len(self.path_list) <= self.cur_path_ind):
				self.cur_path_ind -= len(self.path_list)
			next_waypoint = self.path_list[self.cur_path_ind]
			dist2waypoint = Vector.getDistanceBetweenPoints(next_waypoint, self.coordinate)
			if (dist2waypoint <= 2*self.speed):
				self.coordinate = np.array(next_waypoint)
				self.cur_path_ind += 1
				return
			movement_vec = np.array([next_waypoint[0] - self.coordinate[0], next_waypoint[1] - self.coordinate[1]], dtype='float64')
			movement_vec *= self.speed / Vector.magnitudeOf(movement_vec)
			self.coordinate = np.array(np.add(self.coordinate, movement_vec), dtype='float64')
