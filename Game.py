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

        self.cmdargs       = cmdargs
        self.WhiteColor    = (255, 255, 255)
        self.BlackColor    = (0, 0, 0)
        self.Display_Width = 1200
        self.Display_Height= 600
        self.gameDisplay   = PG.display.set_mode((self.Display_Width, self.Display_Height))
        self.Playground    = Playground_Object(800, self.Display_Height, cmdargs.map_name, cmdargs=cmdargs)
        self.TargetPoint   = Target_Object((740,50))
        self.Normal_Robot  = Robot_Object (self.gameDisplay, self.TargetPoint,(50,550), speed=cmdargs.robot_speed, cmdargs=cmdargs)
        self.Safe_Robot    = Robot_Object (self.gameDisplay, self.TargetPoint,(50,550), speed=cmdargs.robot_speed, cmdargs=cmdargs, issafe = True)

        PG.display.set_caption('Robot Simulator')

    def GameLoop(self):
        clock = PG.time.Clock()
        shouldClose = False
        while not shouldClose:

            for event in PG.event.get():
                if event.type == PG.QUIT:
                    shouldClose = True
            self.Playground.Nextstep(self.gameDisplay)
            clockrobot = 0

            if self.cmdargs.fast_computing:
                isAtTarget = False
                while (not isAtTarget):
                    normal_Glitches, IsNormalatTarget = self.Normal_Robot.NextStep(self.Playground.GridData)
                    Safe_Glitches  , IsSafeatTarget     = self.Safe_Robot.NextStep(self.Playground.GridData)
                    isAtTarget =  IsNormalatTarget and IsSafeatTarget
                    
                if (isAtTarget):
                    output = str(normal_Glitches) + "|" + str(Safe_Glitches) + "|" + str(self.Normal_Robot.stepNum) + "|" + str(self.Safe_Robot.stepNum)
                    shouldClose = True
            else:
                self.Normal_Robot.NextStep(self.Playground.GridData)
                self.Safe_Robot.NextStep(self.Playground.GridData)
                
                self.TargetPoint.draw(self.gameDisplay)
                self.Normal_Robot.draw(self.gameDisplay)
                self.Safe_Robot.draw(self.gameDisplay)
                PG.display.update()
            clockrobot = clockrobot + 1
            clock.tick(1000)
        print (output)
        PG.quit()
        return 0
