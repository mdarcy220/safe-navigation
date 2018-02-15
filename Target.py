#!/usr/bin/python3

## @package Target
#

import pygame as PG

## Represents a target point
#
class Target:
	def __init__(self, position ,radius = 0.75, width = 0, color = (255,0,0)):
		self.position = position
		self.radius = radius
		self._linewidth = width
		self._color = color

	## Draws this target point to the specified surface.
	#
	# @param dtool (`DrawTool` object)
	# <br>	-- the DrawTool to draw to
	#
	def draw(self, dtool):
		dtool.set_color(self._color);
		dtool.set_stroke_width(0);
		dtool.draw_circle(self.position, (self.radius))
		dtool.set_color((0xFF, 0xFF, 0xFF));
		dtool.draw_circle(self.position, (self.radius/1.5))
		dtool.set_color(self._color);
		dtool.draw_circle(self.position, (self.radius/4))
