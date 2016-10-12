import pygame as PG

class Target_Object (object):
    def __init__(self, Coordinate ,radius = 20, width = 0, targetcolor = (255,0,0)):
        self.Coordinate = Coordinate
        self.Radius = radius
        self.Width = width
        self.TargetColor = targetcolor

    def SetWidth(self, width):
        self.Width = width

    def SetColor(self,Color):
        self.TargetColor = Color

    def SetRadius(self, Radius):
        self.Radius = Radius

    def draw(self, screen):
        PG.draw.circle(screen, self.TargetColor, self.Coordinate, int(self.Radius), self.Width)
        PG.draw.circle(screen,(255,255,255) ,self.Coordinate,int(self.Radius/1.5),self.Width)
        PG.draw.circle(screen,self.TargetColor,self.Coordinate,int(self.Radius/4),self.Width)
