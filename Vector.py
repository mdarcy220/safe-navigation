import numpy as np;
 
# Gets the angle from PointA to PointB
def getAngleBetweenPoints(PointA, PointB):
    vectorAB = np.subtract(PointB, PointA)
    return (np.arctan2(vectorAB[1], vectorAB[0]) * 180 / np.pi) % 360


# Gets the distance from PointA to PointB
def getDistanceBetweenPoints(PointA, PointB):
    vectorAB = np.subtract(PointA, PointB)
    return np.sqrt(np.dot(vectorAB, vectorAB))
