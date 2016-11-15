import pygame as PG

class Target:
	def __init__(self, position ,radius = 20, width = 0, color = (255,0,0)):
		self.position = position
		self.radius = radius
		self.width = width
		self.color = color

	def Setwidth(self, width):
		self.width = width

	def SetColor(self, color):
		self.color = color

	def Setradius(self, radius):
		self.radius = radius

	def draw(self, screen):
		PG.draw.circle(screen, self.color, self.position, int(self.radius), self.width)
		PG.draw.circle(screen,(255,255,255) ,self.position,int(self.radius/1.5),self.width)
		PG.draw.circle(screen,self.color,self.position,int(self.radius/4),self.width)
