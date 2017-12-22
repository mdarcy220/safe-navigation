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
		self._bounding_rectangle = self._calc_bounding_rectangle()


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


	## Determines whether this polygon contains the specified point
	# 
	# @param testp (array-like)
	# <br>  Format: `[x, y]`
	# <br>  -- The point to test for inclusion
	#
	def contains_point(self, testp):
		# First do a course check to see if it is even close
		rect = self._bounding_rectangle
		if not Geometry.point_inside_rectangle(rect, testp):
			return False

		# Based on the C source code by Randolph Franklin on Wikipedia
		# Commons, this method uses ray casting to check inclusion of
		# a point inside a polygon

		v = self._vertices

		containsPoint = False
		for i in range(len(self._vertices)):
			if ((v[i][1] > testp[1]) != (v[i-1][1] > testp[1])) and (testp[0] < (v[i-1][0] - v[i][0]) * (testp[1] - v[i][1]) / (v[i-1][1] - v[i][1]) + v[i][0]):
				containsPoint = ~containsPoint
		return containsPoint


	def _calc_bounding_rectangle(self):
		min_x = min(self._vertices, key=lambda p: p[0])[0]
		max_x = max(self._vertices, key=lambda p: p[0])[0]
		min_y = min(self._vertices, key=lambda p: p[1])[1]
		max_y = max(self._vertices, key=lambda p: p[1])[1]
		rect_pos = [min_x, min_y]
		rect_size = np.subtract((max_x, max_y), rect_pos)
		return [rect_pos, rect_size]


	def get_bounding_rectangle(self):
		return self._bounding_rectangle


	def get_vertices(self):
		return self._vertices


	def __repr__(self):
		return "Polygon([{}])".format(self._vertices);





