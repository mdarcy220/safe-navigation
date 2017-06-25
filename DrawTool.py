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

	def draw_poly(self, points):
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


class PygameDrawTool(DrawTool):
	def __init__(self, pg_surface):
		self._pg_surface = pg_surface;


	def draw_circle(self, center, radius):
		PG.draw.circle(self._pg_surface, self._color, center, radius, self._stroke_width);


	def draw_poly(self, points):
		PG.draw.polygon(self._pg_surface, self._color, points, self._stroke_width);


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

class SvgDrawTool(DrawTool):
	def __init__(self):
		self._svg_template_xml = """<svg width="800px" height="600px" viewBox="0 0 800 600"><g id="layer1">{}</g></svg>""";
		self._elems = [];
		self._color = 0;
		self._stroke_width = 1

	def get_svg_xml(self):
		return self._svg_template_xml.format(" ".join(self._elems));


	def _gen_style_str(self):
		style_attr = "stroke-width:{:d};".format(self._stroke_width);
		color = '#'+hex(_color_to_int(self._color))[2:];
		style_attr += ("fill:none;stroke:{};" if self._stroke_width != 0 else "fill:{};stroke:none;").format(color);
		return style_attr


	def draw_circle(self, center, radius):
		style_attr = self._gen_style_str();
		self._elems.append("""<circle id="circle{:d}" r="{:f}" cx="{:f}" cy="{:f}" style="{}"/>""".format(len(self._elems), radius, center[0], center[1], style_attr));


	def draw_poly(self, points):
		if len(points) == 0:
			return
		style_attr = self._gen_style_str();
		d = "";
		d += "M {:f},{:f} ".format(points[0][0], points[0][1]);
		for point in points[1:]:
			d += " L {:f},{:f} ".format(point[0], point[1]);
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

