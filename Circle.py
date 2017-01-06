#!/usr/bin/python3

from Shape import Shape
import numpy as np


class Circle(Shape):
	def __init__(self, center, radius):
		"""
		Parameters:
		center -- a numpy array or list containing the x and y coordinates of the circle
		radius -- the circle's radius
		"""

		self.center = np.array(center);
		self.radius = float(radius);


	def __repr__(self):
		return "Circle({}, {})".format(self.center, self.radius);



def circle_line_intersection(circle_center, circle_radius, line):
	"""
	Returns the point(s) of intersection of the given circle
	object with the given line.

	circle_center (numpy array) -- the center of the circle

	circle_radius (scalar) -- the radius of the circle

	line -- a list of 1D numpy arrays. The format should be such that
	line[0][0] is the x of the first point, line[0][1] is the y of 
	the first point, line[1][0] is the x of the second point, and
	line[1][1] is the y of the second point.

	return value -- a list of 1D numpy arrays, each representing
	the coordinates of an intersection point. If there are no
	intersection points, an empty list will be returned. If an
	error occurs, None is returned.
	"""

	# Make things easier by shifting the coordinate system so the circle
	# is centered at the origin (0, 0)
	adjusted_line = np.subtract(line, circle_center);

	# Easier-to-read notation
	p1, p2 = adjusted_line[0], adjusted_line[1]
	x1, y1 = p1[0], p1[1];
	x2, y2 = p2[0], p2[1];

	# Distances
	dx = np.abs(x2 - x1);
	dy = np.abs(y2 - y1);

	# Leave these in squared form since we never need the raw distance
	line_len_squared = dx*dx + dy*dy;
	circle_radius_squared = circle_radius * circle_radius;

	# determinent and discriminent, based on Wolfram MathWorld:
	# http://mathworld.wolfram.com/Circle-LineIntersection.html
	determinent = (x1*y2) - (y1*x2);
	discriminent = circle_radius_squared * line_len_squared - (determinent * determinent);

	# For cases with 0 collisions, we're done here
	if discriminent < 0:
		return [];


	# For the rest of cases, we know that the infinite line defined by
	# the points has an intersection, but we still need to check if the
	# line segment (non-infinite) actually intersects

	# Determine the candidate intersection points
	intersections = []
	if discriminent == 0:  # One intersection
		x = ((determinent * dy) + (np.sign(dy) * dx) * np.sqrt(discriminent)) / line_len_squared;
		y = ((determinent * dx) + np.abs(dy) * np.sqrt(discriminent)) / line_len_squared;
		intersections.append(np.array([x, y]));
	else:                  # Two intersections
		sign_dy = np.sign(dy);
		if sign_dy == 0:
			sign_dy = 1;

		x = ((determinent * dy) + (sign_dy * dx) * np.sqrt(discriminent)) / line_len_squared;
		y = ((determinent * dx) + np.abs(dy) * np.sqrt(discriminent)) / line_len_squared;
		intersections.append(np.array([x, y]));

		x = ((determinent * dy) - (sign_dy * dx) * np.sqrt(discriminent)) / line_len_squared;
		y = ((determinent * dx) - np.abs(dy) * np.sqrt(discriminent)) / line_len_squared;
		intersections.append(np.array([x, y]));

	# Set up vectors
	vec_p1_p2 = p2 - p1;
	vec_p2_p1 = p1 - p2;

	final_intersections = []

	# Check if points are valid
	for inter in intersections:
		vec_p1_inter = inter - p1;
		vec_p2_inter = inter - p2;
		if 0 <= np.dot(vec_p1_p2, vec_p1_inter) and 0 <= np.dot(vec_p2_p1, vec_p2_inter):
			# Shift coordinates back to normal when appending
			final_intersections.append(inter + circle_center);

	return final_intersections;


