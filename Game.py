import pygame       as PG

import configparser as cp
import numpy        as np

from  Playground  import Playground_Object
from  Robot       import Robot_Object
from  Target      import Target_Object
from  Monitoring  import Monitors
import time

class Game_Object(object):
    def __init__(self, cmdargs):
        PG.init()
        self.StaticObstacles = []

        self.cmdargs            = cmdargs
        self.WhiteColor         = (255, 255, 255)
        self.BlackColor         = (0, 0, 0)
        self.Display_Width      = 1200
        self.Display_Height     = 600
        self.gameDisplay        = PG.display.set_mode((self.Display_Width, self.Display_Height))
        self.Playground         = Playground_Object(800, self.Display_Height, cmdargs.map_name, cmdargs=cmdargs)
        self.TargetPoint        = Target_Object((740,50))
        self.Robot              = Robot_Object (self.gameDisplay, self.TargetPoint,(50,550), speed=cmdargs.robot_speed, cmdargs=cmdargs)
        self.Monitor            = Monitors(self.Robot, PG.display, self.Playground.Playground)
        PG.display.set_caption('Robot Simulator')

    def GameLoop(self):
        clock = PG.time.Clock()
        shouldClose = False
        while not shouldClose:

            for event in PG.event.get():
                if event.type == PG.QUIT:
                    shouldClose = True
                if event.type == PG.MOUSEBUTTONUP:
                    pos = PG.mouse.get_pos()
                    self.Robot.location = pos
                    self.Robot.PathList.append(pos)
            self.Playground.Nextstep(self.gameDisplay)
            clockrobot = 0

            if self.cmdargs.fast_computing:
                self.Robot.Coordinate = (50,550)
                isAtTarget = False
                self.Robot.PathList.clear()
                while (not isAtTarget):
                    isAtTarget = self.Robot.NextStep(self.Playground.GridData)
                    clockrobot = clockrobot + 1
            else:
                self.Robot.NextStep(self.Playground.GridData)

            self.TargetPoint.draw(self.gameDisplay)
            self.Robot.draw(self.gameDisplay)
            self.Monitor.draw()
            PG.display.update()
#            print (clockrobot * 5)
#            print ("Distance : ")
#            print (len(self.Robot.PathList))
            clock.tick(1000)
        PG.quit()
        return 0
