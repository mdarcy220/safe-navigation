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

    def ScanRadar(self, CoordinateofCenter, Grid_Data):

        radar_data = np.ones(360 / int(self.degreeStep))
        currentStep = 0
        x_upper_bound = min(799, self.screen.get_width())
        y_upper_bound = min(599, self.screen.get_height())
        for degree in np.arange(0, 360, self.degreeStep):
            ang_in_radians = degree * math.pi / 180
            cos_cached = math.cos(ang_in_radians)
            sin_cached = math.sin(ang_in_radians)
            for i in range(0, self.RadarRadius, 1):
                x = int(cos_cached * i + CoordinateofCenter[0])
                y = int(sin_cached * i + CoordinateofCenter[1])
                if ((x < 0) or (y < 0) or (x_upper_bound <= x) or (y_upper_bound <= y)):
                    radar_data[currentStep] = i / self.RadarRadius
                    break
                if (Grid_Data[x,y] == 1):
                    radar_data[currentStep] = i / self.RadarRadius
                    break
                #self.screen.set_at((x, y), self.RadarColor)
            currentStep = currentStep + 1
        return radar_data
