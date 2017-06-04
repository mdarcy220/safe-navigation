#!/usr/bin/python3

## @package DynamicObstacle
#

import numpy as np
import pygame as PG
import Vector


## Represents a dynamic obstacle
#
# 
class DynamicObstacle:

	## @var shape 
	# (int) 
	# <br>	The shape of the obstacle. If set to 1, the obstacle is circular.
	# If set to 2, the object is rectanglar. See the #radius and #size
	# attributes for controlling the dimensions of these shapes.
	#
	# @var radius
	# (float)
	# <br>	The radius, if the shape is a circle
	#
	# @var size
	# (numpy array)
	# <br>	Format `[w, h]`
	# <br>	The dimensions, if the shape is a rectangle
	#
	# @var origin
	# (numpy array)
	# <br>	Format: `[x, y]`
	# <br>	The origin around which the obstacle rotates (for circular
	# 	motion only)
	#
	# @var coordinate
	# (numpy array)
	# <br>	Format: `[x, y]`
	# <br>	The current location of the obstacle. For rectangles, this
	# 	point is for their top-left corner (the point on the
	# 	rectangle with the smallest x and y values), and for
	# 	circles it is the center of the circle.
	#
	# @var speed (float)
	# 	The speed of the obstacle
	#
	# @var movement_mode
	# (int)
	# <br>	There are three movement modes. They are defined as follows:
	# <br><br>	**Mode 1.** Fully random motion. The obstacle picks
	# 		a new direction on each step.
	# <br>		**Mode 2.** Circular motion. The obstacle moves in
	# 		a circle of radius 30. Note that the `#radius` field
	# 		of the obstacle relates to its shape, and NOT to
	# 		this motion.
	# <br>		**Mode 3.** Moving along a path. The obstacle moves
	# 		towards the next point in its `#path_list` field.
	# 		When the point is reached, it selects the next
	# 		point and moves towards that one.
	# 

	## Constructor. See the member descriptions for what each of these
	# variables means in more detail.
	#
	def __init__(self):
		self.radius		= 0 # Used for Circle shape
		self.coordinate		= np.array([0, 0]) # Location
		self.origin		= np.array([0, 0]) # Point around which the obstacle rotates for circular motion
		self.size		= [50, 50] # Used for Rectangle shape
		self.fillcolor		= (0x22, 0x77, 0x22)
		self.bordercolor	= (0xFF, 0x00, 0x00)
		self.movement_mode	= 1
		self.shape		= 1 # 1 = Circle, 2 = Rectangle
		self.speed		= 8
		self.tempind		= 1
		self.path_list		= []
		self.cur_path_ind	= 0

	def set_coordinate(self, coordinate):
		self.coordinate = coordinate

	def set_radius(self, radius):
		self.radius = radius

	def get_velocity_vector(self):
		if self.movement_mode == 1:
			return np.random.uniform(-self.speed, self.speed, size=[2]);
		elif self.movement_mode == 2:
			return np.array([int(np.cos(self.tempind * np.pi / 180) * 30), int(np.sin(self.tempind * np.pi / 180) * 30)]);
		elif self.movement_mode == 3:
			if not self.cur_path_ind:
				self.cur_path_ind = 0
			if (not self.path_list) or (len(self.path_list) == 0):
				return
			elif (len(self.path_list) <= self.cur_path_ind):
				self.cur_path_ind -= len(self.path_list)
			next_waypoint = self.path_list[self.cur_path_ind]
			dist2waypoint = Vector.distance_between(next_waypoint, self.coordinate)
			if (dist2waypoint <= 2*self.speed):
				return np.subtract(next_waypoint, self.coordinace)
			movement_vec = np.array([next_waypoint[0] - self.coordinate[0], next_waypoint[1] - self.coordinate[1]], dtype='float64')
			return movement_vec * self.speed / Vector.magnitudeOf(movement_vec)
		else:
			return np.zeros(2)
			

	## Does a motion step for this obstacle, updating its position and
	# direction according to its movement mode.
	#
	def next_step(self):
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
			dist2waypoint = Vector.distance_between(next_waypoint, self.coordinate)
			if (dist2waypoint <= 2*self.speed):
				self.coordinate = np.array(next_waypoint)
				self.cur_path_ind += 1
				return
			movement_vec = np.array([next_waypoint[0] - self.coordinate[0], next_waypoint[1] - self.coordinate[1]], dtype='float64')
			movement_vec *= self.speed / Vector.magnitudeOf(movement_vec)
			self.coordinate = np.array(np.add(self.coordinate, movement_vec), dtype='float64')
