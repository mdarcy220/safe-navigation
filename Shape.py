#!/usr/bin/python3

from enum import Enum;

class Shape:
	def __init__(self):
		pass; # Placeholder -- This is an abstract class

	## Get the intersection point(s) of this Shape with the given line
	#
	# @param line
	# <br>	-- the line to get intersection points with
	#
	def line_intersection(self, line):
		pass

	## Determines whether this Shape contains the specified point
	# 
	# @param testp (array-like)
	# <br>  Format: `[x, y]`
	# <br>  -- The point to test for inclusion
	#
	def contains_point(self, point):
		pass

	def __str__(self):
		return self.__repr__();

	def __repr__(self):
		return "Shape";


