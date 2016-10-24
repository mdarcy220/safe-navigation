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

        self.cmdargs               = cmdargs
        self.WhiteColor         = (255, 255, 255)
        self.BlackColor         = (0, 0, 0)
        self.Display_Width      = 1200
        self.Display_Height     = 600
        self.MainWindow_Title   = 'Robot Simulator'
        PG.display.set_caption (self.MainWindow_Title)
        self.gameDisplay        = PG.display.set_mode((self.Display_Width, self.Display_Height))
        self.Playground         = Playground_Object(800, self.Display_Height, cmdargs.map_name)
        self.TargetPoint        = Target_Object((740,50))
        self.Normal_Robot       = Robot_Object (self.gameDisplay, self.TargetPoint,(50,550), speed=cmdargs.robot_speed, cmdargs=cmdargs)
        self.Safe_Robot         = Robot_Object (self.gameDisplay, self.TargetPoint,(50,550), speed=cmdargs.robot_speed, cmdargs=cmdargs, issafe = True)

    def GameLoop(self):
        clock = PG.time.Clock()
        shouldClose = False
        while not shouldClose:

            for event in PG.event.get():
                if event.type == PG.QUIT:
                    shouldClose = True
                #if event.type == PG.MOUSEBUTTONUP:
                #    pos = PG.mouse.get_pos()
                #    self.Robot.location = pos
                #    self.Robot.PathList.append(pos)
                    # if event.type == PG.KEYDOWN:
            self.Playground.Nextstep(self.gameDisplay)
            clockrobot = 0

            if self.cmdargs.fast_computing:
                self.Normal_Robot.Coordinate = (50,550)
                self.Safe_Robot.Coordinate = (50,550)
                isAtTarget = False
                self.Normal_Robot.PathList.clear()
                self.Safe_Robot.PathList.clear()
                while (not isAtTarget):
                    isAtTarget = self.Normal_Robot.NextStep(self.Playground.GridData) and self.Safe_Robot.NextStep(self.Playground.GridData)
                    clockrobot = clockrobot + 1
            else:
                self.Normal_Robot.NextStep(self.Playground.GridData)
                self.Safe_Robot.NextStep(self.Playground.GridData)

            self.TargetPoint.draw(self.gameDisplay)
            self.Normal_Robot.draw(self.gameDisplay)
            self.Safe_Robot.draw(self.gameDisplay)
            PG.display.update()
#            print (clockrobot * 5)
#            print ("Distance : ")
#            print (len(self.Robot.PathList))
            clock.tick(1000)
        PG.quit()
        return 0
