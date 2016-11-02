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
