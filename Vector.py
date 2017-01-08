import numpy as np;

## @package Vector
#
# Provides basic vector math routines
#
 
## Gets the angle from PointA to PointB
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
def getAngleBetweenPoints(PointA, PointB):
	vectorAB = np.subtract(PointB, PointA)
	return (np.arctan2(vectorAB[1], vectorAB[0]) * 180 / np.pi) % 360


## Gets the distance from PointA to PointB
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
def getDistanceBetweenPoints(PointA, PointB):
	vectorAB = np.subtract(PointA, PointB)
	return magnitudeOf(vectorAB)


## Creates a unit vector pointing at the specified angle.
#
# @param angle (float)
# <br>	-- The angle, in radians
#
# @returns (numpy array)
# <br>	Format: `[x, y]`
# <br>	-- A unit vector pointing at the specified angle.
#
def unitVectorFromAngle(angle):
	return np.array([np.cos(angle), np.sin(angle)], dtype='float64')


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
