import numpy  as np
import pygame as PG
import math
from Radar import  Radar_Object

class Robot_Object(object):
    def __init__(self, screen,  Target_Object, StartLocation, speed = 3):
        self.Coordinate  = StartLocation
        self.TargetObj   = Target_Object
        self.RobotSpd    = speed
        self.Radarobject = Radar_Object(screen)
        self.Screen = screen
        self.direction   = self.getDirectiontoTarget()
        self.PathList    = []


    def SetSpeed(self, speed):
        self.RobotSpd = speed

    def NextStep(self,Grid_data ,radarvision = 40):
        self.GridData = Grid_data
        self.DecisionMembershipfunction = self.Membershipfunction(radarvision)
        self.RadarData = self.Radarobject.ScanRadar(self.Coordinate, Grid_data)
        self.Opfunction = self.ProbabilityOperator(self.DecisionMembershipfunction, self.RadarData)
        tempi = 0
        tempk = []
        over = 0
        while tempi < 360:
            templ = []
            while (self.Opfunction[tempi] > 0.8):
                templ.append(tempi)
                tempi = tempi + 1
                if (tempi > 359):
                    tempi = tempi - 360
                    over  =1
            if len(templ) > 0:
                tempk.append(templ)
            if over == 1:
                break
            tempi = tempi + 1
        if len(tempk) == 0:
            return
            self.NextStep(radarvision + 10)
            return
        longest = max(tempk, key=len)
        DecidedAngle = (longest[0] + longest[len(longest) - 1]) / 2
        DecidedAngle = longest[int(len(longest) / 2)]
        x = self.Coordinate[0] + int(np.cos(DecidedAngle * np.pi / 180)* self.RobotSpd)
        y = self.Coordinate[1] + int(np.sin(DecidedAngle * np.pi / 180)* self.RobotSpd)
        self.Coordinate = (x,y)
        self.PathList.append((x,y))
        if (self.getDistancetoTarger() < 20):
            return True
            print (self.getDistancetoTarger())
        return False

    def ProbabilityOperator (self,x1, x2):
        return np.minimum(x1,x2)

    def Membershipfunction(self, tempo = 60):
        self.Mem  = np.zeros(360 / self.Radarobject.degreeStep)
        angle = int(self.getDirectiontoTarget())
        hasone = 0
        for i in np.arange(0,360,1):
            if (np.abs(i - angle) < tempo) or (np.abs(i + 360 - angle) < tempo) or (np.abs(i-360 - angle) < tempo):
                self.Mem[i] = 1
                hasone = 1
        if (hasone == 0):
            return
            return self.Membershipfunction(tempo+10)
        return self.Mem

    def draw(self, screen):

        PG.draw.circle(self.Screen, (0, 0, 255), self.Coordinate, 4, 0)
        for ind, o in enumerate(self.PathList):
            if ind == len(self.PathList) - 1:
                continue
            PG.draw.line(screen,(0,0,255),self.PathList[ind], self.PathList[ind +1], 5)
            #screen.set_at(o, (255,0,0))

    def getDistancetoTarger(self):
        subtract = np.subtract(self.Coordinate, self.TargetObj.Coordinate)
        Distance = np.sqrt(subtract[0]**2 + subtract[1]**2)
        print (Distance)
        return Distance

    def getDirectiontoTarget(self):
        subtract = np.subtract(self.Coordinate, self.TargetObj.Coordinate)
        Direction = np.arctan(subtract[1] / subtract[0]) * 180 / np.pi
        if Direction < 0 and Direction > -180:
            Direction = Direction + 360
        return Direction