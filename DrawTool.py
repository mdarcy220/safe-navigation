#!/usr/bin/python3

import numpy as np
import pygame as PG


## Draws things
#
class DrawTool:
	def __init__(self):
		self._color = (0,0,0);
		self._stroke_width = 1;

	def draw_circle(self, center, radius):
		pass;

	## Draws an ellipse
	# 
	# @param angle (float)
	# <br>  -- The counterclockwise angle of rotation of the ellipse, in radians.
	# 
	def draw_ellipse(self, center, width, height, angle):
		pass

	def draw_poly(self, points):
		pass;

	def draw_lineseries(self, points):
		pass;

	def draw_line(self, point1, point2):
		pass;

	def draw_rect(self, point, dimension):
		pass;

	def draw_image(self, image_data, location):
		pass;

	def set_color(self, color):
		self._color = color;

	def get_color(self):
		return self._color;

	def set_stroke_width(self, width):
		self._stroke_width = width;

	def get_stroke_width(self):
		return self._stroke_width;


## Draws to the screen using Pygame
#
class PygameDrawTool(DrawTool):
	def __init__(self, pg_surface):
		self._pg_surface = pg_surface;


	def draw_circle(self, center, radius):
		PG.draw.circle(self._pg_surface, self._color, center, radius, self._stroke_width);


	def draw_ellipse(self, center, width, height, angle):
		surface = PG.Surface((width, height), PG.SRCALPHA, 32).convert_alpha()
		PG.draw.ellipse(surface, self._color,(0,0,width,height),0)
		rot_surface = PG.transform.rotate(surface, angle*180/np.pi)
		rcx, rcy = rot_surface.get_rect().center
		self._pg_surface.blit(rot_surface, center)


	def draw_poly(self, points):
		PG.draw.polygon(self._pg_surface, self._color, points, self._stroke_width);


	def draw_lineseries(self, points, closed=False):
		PG.draw.lines(self._pg_surface, self._color, closed, points, self._stroke_width);


	def draw_line(self, point1, point2):
		PG.draw.line(self._pg_surface, self._color, point1, point2, self._stroke_width);


	def draw_rect(self, point, dimension):
		PG.draw.rect(self._pg_surface, self._color, [point[0], point[1], dimension[0], dimension[1]], self._stroke_width);


	def draw_image(self, image_data, location):
		self._pg_surface.blit(image_data, location);


def _color_to_int(color_tuple):
	if isinstance(color_tuple, tuple) or isinstance(color_tuple, list):
		total = len(color_tuple);
		color_int = 0;
		for i in range(len(color_tuple)):
			color_int |= np.uint8(color_tuple[i]) << (total-i-1)*8
		return color_int
	return color_tuple


## Draws to SVG markup
#
class SvgDrawTool(DrawTool):
	def __init__(self):
		self._svg_template_xml = """<svg width="800px" height="600px" viewBox="0 0 800 600"><g id="layer1">{}</g></svg>""";
		self._elems = [];
		self._color = 0;
		self._stroke_width = 1

	def get_svg_xml(self):
		return self._svg_template_xml.format("\n".join(self._elems));


	def _gen_style_str(self):
		style_attr = "stroke-width:{:d};".format(self._stroke_width);
		color = '#{:06x}'.format(_color_to_int(self._color));
		style_attr += ("fill:none;stroke:{};" if self._stroke_width != 0 else "fill:{};stroke:none;").format(color);
		return style_attr


	def draw_circle(self, center, radius):
		style_attr = self._gen_style_str();
		self._elems.append("""<circle id="circle{:d}" r="{:f}" cx="{:f}" cy="{:f}" style="{}"/>""".format(len(self._elems), radius, center[0], center[1], style_attr));


	def draw_ellipse(self, center, width, height, angle):
		style_attr = self._gen_style_str()
		self._elems.append("""<ellipse id="ellipse{:d}" rx="{rx:f}" ry="{ry:f}" cx="{cx:f}" cy="{cy:f}" style="{style:s}" transform="rotate({angle:f}, {cx:f}, {cy:f})"/>""".format(len(self._elems), rx=width/2, ry=height/2, cx=center[0], cy=center[1], style=style_attr, angle=angle*180/np.pi))


	def draw_poly(self, points):
		self.draw_lineseries(points, True);


	def draw_lineseries(self, points, closed=False):
		if len(points) == 0:
			return
		style_attr = self._gen_style_str();
		d = "";
		d += "M {:f},{:f} ".format(points[0][0], points[0][1]);
		for point in points[1:]:
			d += " L {:f},{:f} ".format(point[0], point[1]);
		if closed:
			d += " z ";
		self._elems.append("""<path id="path{:d}" style="{}" d="{}" />""".format(len(self._elems), style_attr, d));


	def draw_line(self, point1, point2):
		style_attr = self._gen_style_str();
		self._elems.append("""<line id="line{:d}" style="{}" x1="{:f}" y1="{:f}" x2="{:f}" y2="{:f}" />""".format(len(self._elems), style_attr, point1[0], point1[1], point2[0], point2[1]));


	def draw_rect(self, point, dimension):
		style_attr = self._gen_style_str();
		self._elems.append("""<rect id="rect{:d}" style="{}" x="{:f}" y="{:f}" width="{:f}" height="{:f}" />""".format(len(self._elems), style_attr, point[0], point[1], dimension[0], dimension[1]));


	def draw_image(self, image_data, location):
		pass;


## Composite tool that duplicates drawing commands over all its component tools
#
class MultiDrawTool:
	def __init__(self):
		self.dtools = []

	def draw_circle(self, center, radius):
		for dtool in self.dtools:
			dtool.draw_circle(center, radius)

	def draw_ellipse(self, *args, **kwargs):
		for dtool in self.dtools:
			dtool.draw_ellipse(*args, **kwargs)

	def draw_poly(self, points):
		for dtool in self.dtools:
			dtool.draw_poly(points)

	def draw_lineseries(self, points):
		for dtool in self.dtools:
			dtool.draw_lineseries(points)

	def draw_line(self, point1, point2):
		for dtool in self.dtools:
			dtool.draw_line(point1, point2)

	def draw_rect(self, point, dimension):
		for dtool in self.dtools:
			dtool.draw_rect(point, dimension)

	def draw_image(self, image_data, location):
		for dtool in self.dtools:
			dtool.draw_image(image_data, location)

	def set_color(self, color):
		for dtool in self.dtools:
			dtool.set_color(color)

	def get_color(self):
		if len(self.dtools) == 0:
			return (0,0,0)
		return self.dtools[0].get_color()

	def set_stroke_width(self, width):
		for dtool in self.dtools:
			dtool.set_stroke_width(width)

	def get_stroke_width(self):
		if len(self.dtools) == 0:
			return 0
		return self.dtools[0].get_stroke_width()
