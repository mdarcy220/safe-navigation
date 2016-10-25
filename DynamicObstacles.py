import numpy as np
import pygame as PG


class DynamicObs(object):
    def __init__(self):
        self.radius         =  0
        self.coordinate     = (0,0)
        self.origin         = (0,0)
        self.size           = [50,50]
        self.fillcolor      = (34,119,34)
        self.bordercolor    = (255,0,0)
        self.MovementMode   = 1
        self.shape          = 1
        self.speed          = 4
        self.tempind        = 1

    def SetCoordinates_Manually(self, Coordinate):
        self.coordinate = Coordinate

    def SetRadiusManually(self, Radius):
        self.radius = Radius

    def NextStep(self):
        if (self.MovementMode == 1):
            x = int(np.random.uniform(-self.speed,self.speed)) * 1
            y = int(np.random.uniform(-self.speed,self.speed)) * 1
            self.coordinate = np.add(self.coordinate, (x,y)).tolist()
        if (self.MovementMode == 2):
            self.tempind += 10
            self.coordinate = (self.origin[0] + int(np.cos(self.tempind * np.pi / 180) * 30), self.origin[1] + int(np.sin(self.tempind * np.pi / 180) * 30))
            if self.tempind == 360:
                self.tempind = 0
