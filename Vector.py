import numpy as np;

## @package Vector
#
# Provides basic vector math routines
#

## @deprecated
# Gets the angle between points A and B
#
# DEPRECATED: Use `degrees_between()` instead
#
# @param PointA (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The first point
#
# @param PointB (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The second point
#
# @returns (float)
# <br>	-- The angle from the first point to the second point, in degrees
#
# @see `degrees_between()`
#
def getAngleBetweenPoints(PointA, PointB):
	return degrees_between(PointA, PointB);


## Gets the angle from point a to point b
#
# The return value of this function is guaranteed to be such that `point_b`
# is equal to `point_a + [np.cos(angle*np.pi/180), np.sin(angle*np.pi/180)]
# * scale`, where `scale` is the distance between points a and b.
#
# @param point_a (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The first point
#
# @param PointB (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The second point
#
# @returns (float)
# <br>	-- The angle from the first point to the second point, in degrees
#
def degrees_between(point_a, point_b):
	vectorAB = np.subtract(point_b, point_a);
	return (np.arctan2(vectorAB[1], vectorAB[0]) * 180 / np.pi) % 360;
	


## Gets the distance between the given two points
#
# @param point_a (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The first point
#
# @param point_b (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The second point
#
# @returns (float)
# <br>	-- The Euclidean distance between the points
#
def distance_between(point_a, point_b):
	vectorAB = np.subtract(point_a, point_b);
	return magnitudeOf(vectorAB);


## @deprecated
# Gets the distance from PointA to PointB
#
# DEPRECATED: Use `distance_between()` instead
#
# @param PointA (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The first point
#
# @param PointB (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The second point
#
# @returns (float)
# <br>	-- The Euclidean distance between the points
#
# @see `distance_between()`
#
def getDistanceBetweenPoints(PointA, PointB):
	return distance_between(PointA, PointB);


## @deprecated Use `unit_vec_from_radians()` instead
#
# DEPRECATED.
# Creates a unit vector pointing at the specified angle.
#
# @param angle (float)
# <br>	-- The angle, in radians
#
# @returns (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- A unit vector pointing at the specified angle.
#
# @see `unit_vec_from_radians()`
# @see `unit_vec_from_degrees()`
#
def unitVectorFromAngle(angle):
	return unit_vec_from_radians(angle);


## Creates a unit vector pointing at the specified angle.
#
# @param angle (float)
# <br>	-- The angle, in radians
#
# @returns (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- A unit vector pointing at the specified angle.
#
def unit_vec_from_radians(angle):
	return np.array([np.cos(angle), np.sin(angle)], dtype='float64')


## Creates a unit vector pointing at the specified angle.
#
# @param angle (float)
# <br>	-- The angle, in degrees
#
# @returns (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- A unit vector pointing at the specified angle.
#
def unit_vec_from_degrees(angle):
	return unit_vec_from_radians(angle * np.pi / 180);


## Calculates the magnitude of the given vector
#
# @param vec (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The vector
#
# @returns (float)
# <br>	-- the magnitude of the vector
#
def magnitudeOf(vec):
	return np.sqrt(np.dot(vec, vec))


## Calculates the angle of the given vector
#
# The return value is the same as calling `degrees_between([0, 0], vec)`
#
# @param vec (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- The vector
#
# @returns (float)
# <br>	-- the angle of the vector, in degrees
#
def angle_degree_of(vec):
	return np.sqrt(np.dot(vec, vec))


## Returns (signed) difference between angles.
#
# Note: This always returns the difference with the smallest absolute
# value, so for example `angle_diff_degrees(1, 359)` would return -2 rather
# than 358.
#
# @param angle1 (float)
# <br>	-- The first angle, in degrees
#
# @param angle2 (float)
# <br>	-- The second angle, in degrees
#
# @returns (float)
# <br>	-- The difference between the angles, equivalent to the second
# 	angle minus the first, mapped within the interval `[0, 180]`
#
def angle_diff_degrees(angle1, angle2):
	return (angle2 - angle1 + 180) % 360 - 180
