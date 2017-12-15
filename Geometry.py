#!/usr/bin/python3

## @package Geometry
#
# This package provides geometry utilities.
#


import numpy as np
import Vector


## Factor to multiply by to convert degrees to radians
#
DEGREE_TO_RADIAN_FACTOR = np.pi / 180.0;

## Factor to multiply by to convert radians to degrees
#
RADIAN_TO_DEGREE_FACTOR = 180.0 / np.pi;


## Returns the points of intersection of the two given circles.
# 
# @param circle1_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the first circle's center
# 
# @param circle1_radius (float)
# <br>	-- the first circle's radius
# 
# @param circle2_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the second circle's center
# 
# @param circle2_radius (float)
# <br>	-- the second circle's radius
# 
# 
# @returns (list of numpy array)
# <br>	-- A list of points of intersection. Empty list if there is
# <br>	no intersection, and `None` on error.
#
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


## Returns the point(s) of intersection of the given circle
# object with the given line.
# 
# @param circle_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the center of the circle
# 
# @param circle_radius (float)
# <br>	-- the radius of the circle
# 
# @param line (list of numpy array)
# <br>	Format: `[[x1, y1], [x2, y2]]`
# <br>	-- the line to check
# 
# @returns (list of numpy array)
# <br>	Format: `[[x1, y1], ..., [xn, yn]]`
# <br>	-- Returns a list of intersection points. If there are no
# 	intersection points, an empty list will be returned. If an error
# 	occurs, `None` is returned.
#
def circle_line_intersection(circle_center, circle_radius, line):

	# Make things easier by shifting the coordinate system so the circle
	# is centered at the origin (0, 0)
	adjusted_line = np.subtract(line, circle_center);

	# Easier-to-read notation
	p1, p2 = adjusted_line[0], adjusted_line[1]
	x1, y1 = p1[0], p1[1];
	x2, y2 = p2[0], p2[1];

	# Distances
	dx = x2 - x1;
	dy = y2 - y1;

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
		y = ((-determinent * dx) + np.abs(dy) * np.sqrt(discriminent)) / line_len_squared;
		intersections.append(np.array([x, y]));

		x = ((determinent * dy) - (sign_dy * dx) * np.sqrt(discriminent)) / line_len_squared;
		y = ((-determinent * dx) - np.abs(dy) * np.sqrt(discriminent)) / line_len_squared;
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


## Returns the intersection of the given two lines.
# 
# 
# @param line1 (list of numpy array)
# <br>	Format: `[[x1, y1], [x2, y2]]`
# <br>	-- endpoints of first line segment
# 
# @param line2 (list of numpy array)
# <br>	Format: `[[x1, y1], [x2, y2]]`
# <br>	-- endpoints of second line segment
# 
# 
# @returns (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- coordinate of intersection if the lines intersect, `None`
# 	otherwise
#
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


## Returns the points of intersection of the given rectangle and line.
# 
# 
# @param rect (list of numpy array)
# <br>	Format: `[[x, y], [w, h]]`
# <br>	-- the rectangle
# 
# @param line (list of numpy array)
# <br>	Format `[[x1, y1], [x2, y2]]`
# <br>	-- the line
# 
# 
# @returns (list of numpy array)
# <br>	Format: `[[x1, y1], ..., [xn, yn]]`
# <br>	-- A list of points of intersection. Empty list if there are no
# 	intersections, and `None` on error.
#
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


## Checks if the point is inside the rectangle.
# 
# 
# @param rect (list of numpy array)
# <br>	Format: `[[x, y], [w, h]]`
# <br>	-- the rectangle
# 
# @param point (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the point
# 
# 
# @returns (boolean)
# <br>	-- `True` if the point is inside the rectangle (including on the
# 	bound), `False` otherwise
#
def point_inside_rectangle(rect, point):
	return rect[0][0] <= point[0] and point[0] <= (rect[0][0] + rect[1][0]) and rect[0][1] <= point[1] and point[1] <= (rect[0][1] + rect[1][1]);


## Gets the angle range of the "shadow" of the given circle with
# respect to the given point. The shadow can be thought of in the following
# way: Imagine the point as a light source and the circle as an opaque
# object. Then the circle would block light at some range of angles around
# the point. That area of blocked light is what "shadow" refers to here.
# 
# 
# @param center_point (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the point
# 
# @param circle_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the center of the circle
# 
# @param circle_radius (float)
# <br>	-- the radius of the circle
# 
# 
# @returns (numpy array)
# <br>	Format: `[start_ang, end_ang]`
# <br>	-- Returns start and end angles indicating the arc of shadow. The
# 	angles will be arranged such that the area of shadow is found by
# 	starting at `start_ang` and increasing the angle value (possibly
# 	requiring modulus if it wraps around) until `end_ang` is reached.
# 	Essentially, the shadow is found counterclockwise from `start_ang` to
# 	end_ang. The angles will be in degrees between 0 and 360.
#
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


## Gets the angle range of the "shadow" of the given rectangle with
# respect to the given point. The shadow can be thought of in the following
# way: Imagine the point as a light source and the rectangle as an opaque
# object. Then the circle would block light at some range of angles around
# the point. That area of blocked light is what "shadow" refers to here.
# 
# 
# @param center_point (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the point
# 
# @param rect_pos (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the location of the top-left corner of the rectangle
# 
# @param rect_dim (numpy array)
# <br>	Format: `[w, h]`
# <br>	-- the dimensions of the rectangle
# 
# 
# @returns (numpy array)
# <br>	Format: `[start_ang, end_ang]`
# <br>	-- Returns start and end angles indicating the arc of shadow. The
# 	angles will be arranged such that the area of shadow is found by
# 	starting at `start_ang` and increasing the angle value (possibly
# 	requiring modulus if it wraps around) until `end_ang` is reached.
# 	Essentially, the shadow is found counterclockwise from `start_ang` to
# 	`end_ang`. The angles will be in degrees between 0 and 360.
#
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


## Gets the angle range of the intersection of the given circles with
# respect to the first circle. This can be thought of as the angles between
# which the second circle overlaps the first one, with the angles being
# measured relative to the first circle (circle 1).
# 
# It should be noted that this method will ONLY work for circles whose
# borders intersect. If one circle is inside the other, no angles will be
# reported even though they still technically overlap.  For other cases you
# will most likely want to use one of the following methods instead:
# <br>	@see circle_shadow_angle_range()
# <br>	@see circle_circle_overlap_angle_range()
#
# 
# @param circle_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the center of circle 1
# 
# @param circle_radius (float)
# <br>	-- the radius of circle 1
# 
# 
# @param circle2_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the center of circle 2
# 
# @param circle2_radius (float)
# <br>	-- the radius of circle 2
# 
# @returns (numpy array)
# <br>	Format: `[start_ang, end_ang]`
# <br>	-- Returns start and end angles indicating the arc of overlap. The
# 	angles will be arranged such that the area of overlap is found by
# 	starting at `start_ang` and increasing the angle value (possibly
# 	requiring modulus if it wraps around) until `end_ang` is reached.
# 	Essentially, the overlap is found counterclockwise from `start_ang`
# 	to `end_ang`. The angles will be in degrees between 0 and 360. If
# 	there is no intersection, `None` is returned.
# 
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


## Gets the angle range of the overlap shadow of the given circles with
# respect to the first circle. This can be thought of as the angles between
# which the second circle overlaps the first one, with the angles being
# measured relative to the first circle (circle 1).
# 
# This is the recommended method to use, as it will correcly consider both
# partially intersecting circles and cases where the second circle is
# inside the first. See descriptions of the following methods to compare
# behavior:
# <br>	@see circle_shadow_angle_range()
# <br>	@see circle_circle_intersect_angle_range()
# 
# 
# @param circle1_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the center of circle 1
# 
# @param circle1_radius (float)
# <br>	-- the radius of circle 1
# 
# @param circle2_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the center of circle 2
# 
# @param circle2_radius (float)
# <br>	-- the radius of circle 2
# 
# @returns (numpy array)
# <br>	Format: `[start_ang, end_ang]`
# <br>	-- Returns start and end angles indicating the arc of overlap. The
# 	angles will be arranged such that the area of overlap is found by
# 	starting at `start_ang` and increasing the angle value (possibly
# 	requiring modulus if it wraps around) until `end_ang` is reached.
# 	Essentially, the overlap is found counterclockwise from `start_ang`
# 	to `end_ang`. The angles will be in degrees between 0 and 360. If
# 	there is no overlap, `None` is returned.
#
def circle_circle_overlap_angle_range(circle1_center, circle1_radius, circle2_center, circle2_radius):
	# Get an angle range (relative to circle1) that is guaranteed to contain the entire
	# overlap of circles 1 and 2. May return None if there is no overlap
	if Vector.getDistanceBetweenPoints(circle1_center, circle2_center) < circle1_radius:
		return circle_shadow_angle_range(circle1_center, circle2_center, circle2_radius);
	else:
		return circle_circle_intersect_angle_range(circle1_center, circle1_radius, circle2_center, circle2_radius);



## Gets the angle range of the overlap shadow of the given rectangle
# with respect to the circle.
# 
# This can be thought of as the angles between which the rectangle overlaps
# the first one, with the angles being measured relative to the circle.
# This is analogous to the method circle_circle_overlap_angle_range(), so
# it may be helpful to see that method's documentation for reference.
# 
# 
# @param circle_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the center of the circle
# 
# @param circle_radius (float)
# <br>	-- the radius of the circle
# 
# 
# @returns (numpy array or list)
# <br>	Format: `[start_ang, end_ang]`
# <br>	Desc: Returns start and end angles indicating the arc of overlap.
# 	The angles will be arranged such that the area of overlap is found
# 	by starting at `start_ang` and increasing the angle value (possibly
# 	requiring modulus if it wraps around) until `end_ang` is reached.
# 	Essentially, the overlap is found counterclockwise from `start_ang`
# 	to `end_ang`. The angles will be in degrees between 0 and 360. If
# 	there is no overlap, `None` is returned. If the circle is inside the
# 	rectangle, the angle range `[0, 360]` is returned.
#
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

## Rotates points about origin with angle alpha
# 
# 
# @param points (numpy array)
# <br>	Format: `[[x1, y1],..,[xn,yn]]`
# <br>  -- list of points to be rotated
#
# @param angle (float)
# <br>	-- rotation angle
# 
# 
# @returns (numpy array)
# <br>	Format: `[[x1,y1],...,[xn,yn]]`
# <br>	Desc: Returns a numpy array of the rotate pair of each 
#             input point.
#
def rotate_points_origin(points, angle):
  rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],[np.sin(angle), np.cos(angle)]])
  return np.dot(points,rotation_matrix)

## Return points to original origin after being rotated 
#  about origin with angle alpha
# 
# @param points (numpy array)
# <br>	Format: `[[x1, y1],..,[xn,yn]]`
# <br>  -- list of points to be rotated
#
# @param angle (float)
# <br>	-- rotation angle
# 
# 
# @returns (numpy array)
# <br>	Format: `[[x1,y1],...,[xn,yn]]`
# <br>	Desc: Returns a numpy array of the rotate pair of each 
#             input point.
#
def rotate_points_back_origin(points,angle):
  rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],[np.sin(angle), np.cos(angle)]])
  return np.dot(points,rotation_matrix.T)


## Returns the point(s) of intersection of the given ellipse
# object with the given line.
# 
# @param ellipse_center (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- the center of the ellipse
# 
# @param ellipse_width (float)
# <br>	-- the width of the ellipse
# 
# @param ellipse_height (float)
# <br>	-- the height of the ellipse
# 
# @param ellipse_angle (float)
# <br>	-- the angle of the ellipse
# 
# @param line (list of numpy array)
# <br>	Format: `[[x1, y1], [x2, y2]]`
# <br>	-- the line to check
# 
# @returns (list of numpy array)
# <br>	Format: `[[x1, y1], ..., [xn, yn]]`
# <br>	-- Returns a list of intersection points. If there are no
# 	intersection points, an empty list will be returned. If an error
# 	occurs, `None` is returned.
#
def ellipse_line_intersection(ellipse_center, ellipse_width, ellipse_height, ellipse_angle, line):

	# Make things easier by shifting the coordinate system so the circle
	# is centered at the origin (0, 0), then rotate the line points to
	# have non rotated ellipse
	adjusted_line = rotate_points_origin(np.subtract(line, ellipse_center),ellipse_angle);

	# Easier to work with half-width and half-height of ellipse
	a = ellipse_width/2;
	b = ellipse_height/2;

	# Easier-to-read notation
	p1, p2 = adjusted_line[0], adjusted_line[1]
	x1, y1 = p1[0], p1[1];
	x2, y2 = p2[0], p2[1];

	# Distances
	dx = x2 - x1;
	dy = y2 - y1;

	# Check first if the line is either horizontal or vertical
	if (dx !=0 and dy!=0):
		# Calculate line slope m
		m = dy/dx;
		c = y1 - m*x1;
		determinant = a**2 * m**2 + b**2 -c**2;
		if determinant < 0:
			return [];
		elif determinant == 0:
			x = -a**2 * m *c;
			y = b**2 * c;
			div = (a*m)**2 + b**2;
			x1 = x/div;
			y1 = y/div;

			intersections = [[x1,y1],[x2,y2]];
			
		else:
			determinant = a*b* np.sqrt(determinant);
			x = -a**2 * m *c;
			y = b**2 * c;
			div = (a*m)**2 + b**2;
			x1 = (x + determinant)/div;
			x2 = (x - determinant)/div;
			y1 = (y + m*determinant)/div;
			y2 = (y - m*determinant)/div;

			intersections = [[x1,y1],[x2,y2]];
	elif dx == 0:
		y = y1;
		if y>b or y<-b:
			return []
		elif y == b or y == -b:
			intersections = [[0,y]];
		else:
			x1 = a * np.sqrt(1-(y/b)**2);
			x2 = -x1;
			intersections = [[x1,y],[x2,y]];
	else:
		x = x1;
		if x>a or x<-a:
			return []
		elif x == a or x == -a:
			intersections = [[x,0]];
		else:
			y1 = a * np.sqrt(1-(x/a)**2);
			y2 = -y1;
			intersections = [[x,y1],[x,y2]];
				

	intersections = rotate_points_back_origin(intersections,ellipse_angle);
	intersections[:,0] += ellipse_center[0];
	intersections[:,1] += ellipse_center[1];

	return intersections

					








if __name__ == '__main__':
	print(circle_line_intersection(np.array([2.46,1.04]), 2.6**0.5, [[3.72,-1.96], [0.9,2.84]]))
	print(circle_line_intersection(np.array([2.46,1.04]), 2.6**0.5, [[0.9,2.84],[3.72,-1.96]]))

