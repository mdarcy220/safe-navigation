import numpy  as np
import pygame as PG
import math
from Radar import  Radar_Object
#import Queue
import Distributions

class Robot_Object(object):
    def __init__(self, screen,  Target_Object, StartLocation, speed = 3, cmdargs=None):
        self.cmdargs            = cmdargs
        self.Coordinate         = StartLocation
        self.TargetObj          = Target_Object
        self.RobotSpd           = speed
        self.Radarobject        = Radar_Object(screen)
        self.Screen             = screen
        self.direction          = self.getDirectiontoTarget()
        self.PathList           = []
        #self.GaussianCenters    = Queue.Queue()
        self.PDF                = Distributions.Distributions()

    def SetSpeed(self, speed):
        self.RobotSpd = speed


    def NextStep(self, Grid_data):
        self.GridData = Grid_data
        DecisionMembershipfunction = self.PDF.Radar_GaussianDistribution(self.getDirectiontoTarget())
        if (not (self.cmdargs is None)) and (self.cmdargs.target_distribution_type == 'rectangular'):
            DecisionMembershipfunction = self.PDF.Radar_RectangularDistribution(self.getDirectiontoTarget())            
        self.RadarData = self.Radarobject.ScanRadar(self.Coordinate, Grid_data)
        self.Opfunction = self.ProbabilityOperator(DecisionMembershipfunction, self.RadarData)
        DecidedAngle = np.argmax(self.Opfunction) * self.PDF.DegreeResolution

        x = self.Coordinate[0] + int(np.cos(DecidedAngle * np.pi / 180) * self.RobotSpd)
        y = self.Coordinate[1] + int(np.sin(DecidedAngle * np.pi / 180) * self.RobotSpd)
        self.Coordinate = (x,y)
        self.PathList.append((x,y))
        #self.GaussianCenters.put((x,y))
        
        #while self.GaussianCenters.qsize() > 100:
        #    self.GaussianCenters.get()
        if (self.getDistancetoTarget() < 20):
            return True
            #print (self.getDistancetoTarget())
        return False


    def ProbabilityOperator (self, x1, x2):
        return np.minimum(x1, x2)


    def draw(self, screen):
        PG.draw.circle(self.Screen, (0, 0, 255), self.Coordinate, 4, 0)
        for ind, o in enumerate(self.PathList):
            if ind == len(self.PathList) - 1:
                continue
            PG.draw.line(screen,(0,0,255),self.PathList[ind], self.PathList[ind +1], 5)
            #screen.set_at(o, (255,0,0))


    def getDistancetoTarget(self):
        subtract = np.subtract(self.TargetObj.Coordinate, self.Coordinate)
        Distance = np.sqrt(subtract[0]**2 + subtract[1]**2)
        print(Distance)
        return Distance


    def getDirectiontoTarget(self):
        subtract = np.subtract(self.TargetObj.Coordinate, self.Coordinate)
        direction = 0
        if subtract[0] == 0:
            direction = np.sign(subtract[1]) * 90
        else:
            direction = np.arctan(subtract[1] / subtract[0]) * 180 / np.pi

        if subtract[0] < 0:
            direction += 180
        direction %= 360
        return direction
