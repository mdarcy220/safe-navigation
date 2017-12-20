#!/usr/bin/python3

## @package Polygon
#

from Shape import Shape
import numpy as np
import Geometry

class Polygon(Shape):
	## A polygon is defined as a list of points Each side of the
	# polygon is the connection between two consecutive points from the
	# list with the last connection be the one between the last and first
	# point
	# 
	# The polygon internal part of the polygon is considered to be to the
	# right of each line
	# 
	# @param vertices (array-like)
	# Format: `[[x1, y1], [x1, y2], ..., [xn, yn]]`
	# <br>  -- list containing the x and y coordinates of the vertices
	#
	def __init__(self, vertices):
		self._vertices = np.array(vertices)


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
		for i in range(len(self._vertices)):
			edge = [self._vertices[i-1],self._vertices[i]];
			intersection = Geometry.line_line_intersection(line, edge);
			if intersection is not None:
				intersections.append(list(intersection));
		return intersections;


	def __repr__(self):
		return "Polygon([])".format(self._vertices);





