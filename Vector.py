import numpy as np;
 
# Gets the angle from PointA to PointB
def getAngleBetweenPoints(PointA, PointB):
	vectorAB = np.subtract(PointB, PointA)
	return (np.arctan2(vectorAB[1], vectorAB[0]) * 180 / np.pi) % 360


# Gets the distance from PointA to PointB
def getDistanceBetweenPoints(PointA, PointB):
	vectorAB = np.subtract(PointA, PointB)
	return magnitudeOf(vectorAB)


def unitVectorFromAngle(ang):
	return np.array([np.cos(ang), np.sin(ang)], dtype='float64')


def magnitudeOf(vec):
	return np.sqrt(np.dot(vec, vec))


# Returns (signed) difference between angles. This always returns the
# difference with the smallest absolute value, so for example 
# angle_diff_degrees(1, 359) would return -2 rather than 358.
def angle_diff_degrees(angle1, angle2):
	return (angle2 - angle1 + 180) % 360 - 180
