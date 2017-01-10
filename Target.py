#!/usr/bin/python3

## @package Target
#

import pygame as PG

## Represents a target point
#
class Target:
	def __init__(self, position ,radius = 20, width = 0, color = (255,0,0)):
		self.position = position
		self.radius = radius
		self._linewidth = width
		self._color = color

	## Draws this target point to the specified surface.
	#
	# @param screen (pygame.Surface object)
	# <br>	-- the surface to draw to
	#
	def draw(self, screen):
		PG.draw.circle(screen, self._color, self.position, int(self.radius), self._linewidth)
		PG.draw.circle(screen, (255,255,255) ,self.position, int(self.radius/1.5), self._linewidth)
		PG.draw.circle(screen, self._color, self.position, int(self.radius/4), self._linewidth)
