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
	# <br>	The shape of the obstacle. If set to 1, the obstacle is
	#       circular.  If set to 2, the object is rectanglar. If set to 3,
	#       the obstacle is elliptical. If 4, it is a polygon. See the
	#       #radius, #size, #width, #height, #direction, and #polygon
	#       attributes for controlling the dimensions of these shapes.
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
	# @var width
	# (float)
	# <br>	The width (2*x depth), if the shape is an ellipse
	#
	# @var height
	# (float)
	# <br>	The height (2*y depth), if the shape is an ellipse
	# 
	# @var polygon
	# (Polygon object)
	# <br>	An object representing the polygon, if the shape is a Polygon
	#
	# @var coordinate
	# (numpy array)
	# <br>	Format: `[x, y]`
	# <br>	The current location of the obstacle. For rectangles, this
	# 	point is for their top-left corner (the point on the
	# 	rectangle with the smallest x and y values), and for
	# 	circles and ellipses it is the center of the circle.
	# 

	## Constructor. See the member descriptions for what each of these
	# variables means in more detail.
	#
	def __init__(self, movement, obs_id=0):
		self._movement          = movement
		self._obs_id            = obs_id

		self.coordinate		= movement.get_pos()
		self._last_position     = self.coordinate

		self.radius		= 0 # Used for Circle shape
		self.width              = 0 # Used for Ellipse shape
		self.height             = 0 # Used for Ellipse shape
		self.size		= [50, 50] # Used for Rectangle shape
		self.polygon            = None # Used for Polygon shape
		self.fillcolor		= (0x44, 0xcc, 0xee)
		self.bordercolor	= (0xFF, 0x00, 0x00)
		self.shape		= 1 # 1 = Circle, 2 = Rectangle, 3 = Ellipse


	def set_coordinate(self, coordinate):
		self.coordinate = coordinate

	def set_radius(self, radius):
		self.radius = radius

	def set_width(self, width):
		self.width = width

	def set_height(self, height):
		self.height = height

	def get_velocity_vector(self):
		return self.coordinate - self._last_position


	## Does a motion step for this obstacle, updating its position and
	# direction according to its movement mode.
	#
	def next_step(self, timestep):
		self._last_position = self.coordinate

		self._movement.step(timestep)
		self.coordinate = self._movement.get_pos()

