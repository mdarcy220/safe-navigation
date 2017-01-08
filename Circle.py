#!/usr/bin/python3

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


	def rectangle_overlap_angle_range(self, rect_pos, rect_dim):
		return Geometry.circle_rectangle_overlap_angle_range(self.center, self.radius, rect_pos, rect_dim);


	def circle_overlap_angle_range(self, circle2_center, circle2_radius):
		return Geometry.circle_circle_overlap_angle_range(self.center, self.radius, circle2_center, circle2_radius);


	def line_intersection(self, line):
		"""
		Returns the points of intersection of this circle with the
		given line.
		"""
		return Geometry.circle_line_intersection(self.center, self.radius, line);


	def __repr__(self):
		return "Circle({}, {})".format(self.center, self.radius);




