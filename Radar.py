import math
import pygame as PG
import numpy  as np
import sys

class Radar_Object(object):

    def __init__(self, screen, Radius = 100, radarcolor = (236,179,223)):

        self.screen   = screen
        self.RadarRadius = Radius
        self.RadarColor  = radarcolor
        self.image       = PG.Surface([self.RadarRadius * 2,  self.RadarRadius * 2])
        self.image.fill((255,255,255))
        self.image.set_colorkey((255,255,255))
        self.degreeStep = 1
        self.RadarData = np.ones(360 / int(self.degreeStep))

    def ScanRadar(self, CoordinateofCenter , Grid_Data):

        self.RadarData = np.ones(360 / int(self.degreeStep))
        currentStep = 0
        for degree in np.arange(0, 360 , self.degreeStep):
            for i in range(0, self.RadarRadius, 10):
                x = math.cos(degree * math.pi / 180) * i
                y = math.sin(degree * math.pi / 180) * i
                x = int(CoordinateofCenter[0] + x)
                y = int(CoordinateofCenter[1] + y)
                if ((x < 0) or (y < 0) or (x >= self.screen.get_width()) or (y >= self.screen.get_height())):
                    self.RadarData[currentStep] = i / self.RadarRadius
                    continue
                if (x > 799 or y > 599):
                    self.RadarData[currentStep] = i / self.RadarRadius
                    continue
                if (Grid_Data[x,y] == 1 ):
                    self.RadarData[currentStep] = i / self.RadarRadius
                    break
                #self.screen.set_at((x, y), self.RadarColor)
            currentStep = currentStep + 1
        return self.RadarData