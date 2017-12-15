#!/usr/bin/python3

## @package Human
#

from Shape import Shape
import numpy as np
import Geometry
import math

class Human(Shape):
	def __init__(self, center, width, height, v_x,v_y):
		"""
		Parameters:
		center -- a numpy array or list containing the x and y coordinates of the Human
		width -- the ellipse's width
		height -- the ellipse's height
		v_x -- x direction of the ellipse
		v_y -- y direction of the ellipse
		"""

		self.center = np.array(center);
		self.width = float(width);
		self.height = float(height);
		if v_x !=0:
			self.angle = float(math.atan2(v_y,v_x))
		else:
			self.angle = 0.0




	## Get the intersection point(s) of this circle with the given line
	#
	# @param line
	# <br>	-- the line to get intersection points with
	#
	def line_intersection(self, line):
		"""
		Returns the points of intersection of this Human with the
		given line.
		"""
		return Geometry.ellipse_line_intersection(self.center, self.width, self.height, self.angle, line);


	def __repr__(self):
		return "Human({}, {}, {}, {})".format(self.center, self.width, self.height, self.angle);





