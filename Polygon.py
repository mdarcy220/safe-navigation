#!/usr/bin/python3

## @package Human
#

from Shape import Shape
import numpy as np
import Geometry
import math

class Polygon(Shape):
	def __init__(self, Points):
		"""
		A polygon is defined as a list of points
		Each side of the polygon is the connection between two 
		consecutive points from the list
		with the last connection be the one between the last and first point

		The polygon internal part of the polygon 
		is considered to be to the right of each line

		Parameters:
		Points -- list containing the x and y coordinates of the vertices
		"""

		self.Points = Points;

	## Get the intersection point(s) of this polygon with the given line
	#  which is the intersection of each edge of the polygon with the
	#  specific line
	#
	# @param line
	# <br>	-- the line to get intersection points with
	#
	def line_intersection(self, line):
		"""
		Returns the points of intersection of this polygon with the
		given line.
		"""
		intersections = []
		for i in range(len(self.Points)):
			edge = [self.Points[i-1],self.Points[i]];
			intersection = Geometry.line_line_intersection(line,edge);
			if intersection is not None:
				intersections.append(list(intersection));
		return intersections;


	def __repr__(self):
		return "Polygon([])".format(self.Points);





