import numpy  as np
import pygame as PG

class Monitors(object):
    def __init__(self, Robot, MainDisplay, PlaygroundDisplay):
        self.Width     = MainDisplay.get_surface().get_width() - PlaygroundDisplay.get_width() - 1
        self.Robot     = Robot
        self.Display   = MainDisplay
        self.YPosition = 0
        self.XPosition = PlaygroundDisplay.get_width() + 1

    def draw(self):
        self.draw_Monitor1_Cartesian()

    def draw_Monitor1_Cartesian(self):
        Image = PG.Surface([self.Width, 300])
        Image.fill((255,255,255))

