#!/usr/bin/python3

## @package Circle
#

from Shape import Shape
import numpy as np
import Geometry

class Circle(Shape):
	def __init__(self, center, radius):
		"""
		Parameters:
		center -- a numpy array or list containing the x and y coordinates of the circle
		radius -- the circle's radius
		"""

		self.center = np.array(center);
		self.radius = float(radius);


	## Get the overlap of this circle with the given rectangle
	#
	def rectangle_overlap_angle_range(self, rect_pos, rect_dim):
		return Geometry.circle_rectangle_overlap_angle_range(self.center, self.radius, rect_pos, rect_dim);

	## Get the overlap of this circle with the given circle
	#
	def circle_overlap_angle_range(self, circle2_center, circle2_radius):
		return Geometry.circle_circle_overlap_angle_range(self.center, self.radius, circle2_center, circle2_radius);


	## Get the intersection point(s) of this circle with the given line
	#
	# @param line
	# <br>	-- the line to get intersection points with
	#
	def line_intersection(self, line):
		"""
		Returns the points of intersection of this circle with the
		given line.
		"""
		return Geometry.circle_line_intersection(self.center, self.radius, line);


	## Determines whether this Circle contains the specified point
	# 
	# @param testp (array-like)
	# <br>  Format: `[x, y]`
	# <br>  -- The point to test for inclusion
	#
	def contains_point(self, point):
		vec = np.subtract(point, self.center)
		return np.dot(vec, vec) < (self.radius * self.radius)


	def __repr__(self):
		return "Circle({}, {})".format(self.center, self.radius);





