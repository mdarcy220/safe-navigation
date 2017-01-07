#!/usr/bin/python3

import numpy as np
import Vector

DEGREE_TO_RADIAN_FACTOR = np.pi / 180.0;
RADIAN_TO_DEGREE_FACTOR = 180.0 / np.pi;

def circle_circle_intersection(circle1_center, circle1_radius, circle2_center, circle2_radius):

	# Method from http://paulbourke.net/geometry/circlesphere/
	p0 = circle1_center;
	p1 = circle2_center;
	r0 = circle1_radius;
	r1 = circle2_radius;

	vec_p0_p1 = p1 - p0;

	dSquared = np.dot(vec_p0_p1, vec_p0_p1);
	d = np.sqrt(dSquared);

	# Quick check based on distance and radii, to ensure the intersection exists
	if (r0 + r1) < d:
		return []; # Too far apart
	elif d < np.abs(r0 - r1):
		return []; # One inside the other
	elif d == 0:
		return []; # Concentric

	a = ((r0*r0) - (r1*r1) + dSquared) / (2*d)
	h = r0*r0 - a*a

	p2 = p0 + a * vec_p0_p1 / d

	p3x = p2[0] + h * (p1[1] - p0[1]) / d
	p3y = p2[1] - h * (p1[0] - p0[0]) / d
	p3 = np.array([p3x, p3y])

	p4x = p2[0] - h * (p1[1] - p0[1]) / d
	p4y = p2[1] + h * (p1[0] - p0[0]) / d
	p4 = np.array([p4x, p4y])	

	return [p3, p4]


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
	if discriminent < 0 or line_len_squared == 0:
		return [];


	# For the rest of cases, we know that the infinite line defined by
	# the points has an intersection, but we still need to check if the
	# line segment (non-infinite) actually intersects

	# Determine the candidate intersection points
	intersections = []

	sign_dy = np.sign(dy);
	if sign_dy == 0:
		sign_dy = 1;

	if discriminent == 0:  # One intersection
		x = ((determinent * dy) + (sign_dy * dx) * np.sqrt(discriminent)) / line_len_squared;
		y = ((determinent * dx) + np.abs(dy) * np.sqrt(discriminent)) / line_len_squared;
		intersections.append(np.array([x, y]));
	else:                  # Two intersections
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


def line_line_intersection(line1, line2):
	vec_line1 = line1[1] - line1[0];
	vec_line2 = line2[1] - line2[0];
	crossProd = np.cross(vec_line1, vec_line2)

	if crossProd == 0:
		return None;

	t = np.cross(line2[0] - line1[0], vec_line2) / crossProd
	u = np.cross(line2[0] - line1[0], vec_line1) / crossProd

	if 0 <= t and t <= 1 and 0 <= u and u <= 1:
		return line1[0] + (t * vec_line1);
	return None;


def rectangle_line_intersection(rect, line):
	# Rectangle should be a list of [np.array([x, y]), np.array([width, height])]
	# Line should be [np.array([x1, y1]), np.array([x2, y2])]

	inters = []

	# Make a list of points IN THE ORDER THEY ARE CONNECTED
	rect_points = [rect[0]]
	rect_points.append(rect[0] + np.array([rect[1][0], 0]))
	rect_points.append(rect[0] + rect[1])
	rect_points.append(rect[0] + np.array([0, rect[1][1]]))

	rect_lines = [];
	rect_lines.append(np.array([rect_points[0], rect_points[1]]));
	rect_lines.append(np.array([rect_points[1], rect_points[2]]));
	rect_lines.append(np.array([rect_points[2], rect_points[3]]));
	rect_lines.append(np.array([rect_points[3], rect_points[0]]));

	for rect_line in rect_lines:
		inter = line_line_intersection(line, rect_line);
		if not (inter is None):
			inters.append(inter);

	return inters;


def point_inside_rectangle(rect, point):
	return rect[0][0] <= point[0] and point[0] <= (rect[0][0] + rect[1][0]) and rect[0][1] <= point[1] and point[1] <= (rect[0][1] + rect[1][1]);


def circle_shadow_angle_range(center_point, circle_center, circle_radius):
	base_ang = Vector.getAngleBetweenPoints(center_point, circle_center);
	dist = Vector.getDistanceBetweenPoints(center_point, circle_center);
	if dist < circle_radius:
		return [0, 360];
	offset = np.arcsin(circle_radius / float(dist)) * RADIAN_TO_DEGREE_FACTOR;
	if np.isnan(offset):
		return [0, 360];
	else:
		return [base_ang - offset, base_ang + offset];


def rectangle_shadow_angle_range(center_point, rect_pos, rect_dim):
	rect_points = [rect_pos]
	rect_points.append(rect_pos + np.array([rect_dim[0], 0]))
	rect_points.append(rect_pos + rect_dim)
	rect_points.append(rect_pos + np.array([0, rect_dim[1]]))

	first_ang = Vector.getAngleBetweenPoints(center_point, rect_points[0]);

	angle_range = [first_ang, first_ang];

	for point in rect_points[1:]:
		vec = point - center_point;
		vec2 = Vector.unitVectorFromAngle(angle_range[0]*DEGREE_TO_RADIAN_FACTOR);
		crossProd = np.cross(vec2, vec);
		if crossProd < 0:
			angle_range[0] = Vector.getAngleBetweenPoints(center_point, point);
		vec2 = Vector.unitVectorFromAngle(angle_range[1]*DEGREE_TO_RADIAN_FACTOR);
		crossProd = np.cross(vec2, vec);
		if crossProd > 0:
			angle_range[1] = Vector.getAngleBetweenPoints(center_point, point);

	return angle_range;


def circle_circle_intersect_angle_range(circle_center, circle_radius, circle2_center, circle2_radius):
	points = circle_circle_intersection(circle_center, circle_radius, circle2_center, circle2_radius);
	if points is None or len(points) < 2:
		return None;
	ang1 = Vector.getAngleBetweenPoints(circle_center, points[0]);
	ang2 = Vector.getAngleBetweenPoints(circle_center, points[1]);
	vec1 = points[0] - circle_center;
	vec2 = points[1] - circle_center;
	crossProd = np.cross(vec1, vec2);
	if crossProd < 0:
		return [ang2, ang1];
	elif crossProd > 0:
		return [ang1, ang2];
	else:
		return [0, 360];


def circle_circle_overlap_angle_range(circle1_center, circle1_radius, circle2_center, circle2_radius):
	# Get an angle range (relative to circle1) that is guaranteed to contain the entire
	# overlap of circles 1 and 2. May return None if there is no overlap
	if Vector.getDistanceBetweenPoints(circle1_center, circle2_center) < circle1_radius:
		return circle_shadow_angle_range(circle1_center, circle2_center, circle2_radius);
	else:
		return circle_circle_intersect_angle_range(circle1_center, circle1_radius, circle2_center, circle2_radius);



def circle_rectangle_overlap_angle_range(circle_center, circle_radius, rect_pos, rect_dim):
	if point_inside_rectangle([rect_pos, rect_dim], circle_center):
		return [0, 360];
	# Start by checking if the rectangle is close enough to have an intersection at all
	rect_points = [rect_pos]
	rect_points.append(rect_pos + np.array([rect_dim[0], 0]))
	rect_points.append(rect_pos + rect_dim)
	rect_points.append(rect_pos + np.array([0, rect_dim[1]]))
	rect_lines = [];
	rect_lines.append(np.array([rect_points[0], rect_points[1]]));
	rect_lines.append(np.array([rect_points[1], rect_points[2]]));
	rect_lines.append(np.array([rect_points[2], rect_points[3]]));
	rect_lines.append(np.array([rect_points[3], rect_points[0]]));

	has_inter = False;
	for i in range(4):
		rect_line = rect_lines[i];
		rect_point = rect_points[i];
		if Vector.getDistanceBetweenPoints(rect_point, circle_center) < circle_radius:
			has_inter = True
			break;
		inters = circle_line_intersection(circle_center, circle_radius, rect_line);
		if inters is not None and 0 < len(inters):
			has_inter = True;
			break;
	if not has_inter:
		return None;

	return rectangle_shadow_angle_range(circle_center, rect_pos, rect_dim);


