#!/usr/bin/python3

## @package GeometricEnvironment
#

import numpy  as np
import pygame as PG
import DrawTool
from DynamicObstacles import DynamicObstacle
import sys
import Vector
from Environment import Environment, ObsFlag
import MapModifier
import StaticGeometricMaps
import Geometry


## Holds information related to the simulation environment, such as the
# position and motion of dynamic obstacles, and the static map.
#
class GeometricEnvironment(Environment):

	def __init__(self, width, height, map_filename, cmdargs=None):
		super().__init__(width, height, map_filename, cmdargs);
		self.cmdargs = cmdargs
		self.width = width
		self.height = height
		self.dynamic_obstacles = []
		self.static_obstacles = []

		# Note: Order is important here:
		#  - init_map_modifiers() MUST be called BEFORE
		#    loading and initilizing the map, or else the modifiers
		#    will not work

		# Init map modifiers
		self._init_map_modifiers();

		# Load the static map and apply the modifier to produce
		# dynamic obstacles
		self.load_map(map_filename)

		if (cmdargs):
			self.apply_map_modifier_by_number(self.cmdargs.map_modifier_num)


	def _init_map_modifiers(self):
		self.map_modifiers = [None];
		self.map_modifiers.append(MapModifier._map_mod_1);
		self.map_modifiers.append(MapModifier._map_mod_2);
		self.map_modifiers.append(MapModifier._map_mod_3);
		self.map_modifiers.append(MapModifier._map_mod_4);
		self.map_modifiers.append(MapModifier._map_mod_5);
		self.map_modifiers.append(None); 
		self.map_modifiers.append(MapModifier._map_mod_7);
		self.map_modifiers.append(MapModifier._map_mod_8);
		self.map_modifiers.append(MapModifier._map_mod_9);
		self.map_modifiers.append(MapModifier._map_mod_10);
		self.map_modifiers.append(MapModifier._map_mod_11);
		self.map_modifiers.append(MapModifier._map_mod_12);
		self.map_modifiers.append(MapModifier._map_mod_obsmat);


	def load_map(self, map_filename):
		StaticGeometricMaps._create_map_1(self)


	def apply_map_modifier_by_number(self, modifier_num):

		if (len(self.map_modifiers) <= modifier_num):
			return;
		map_modifier = self.map_modifiers[modifier_num];
		if map_modifier is None:
			return;

		map_modifier(self);


	## Draws the environment onto the given display.
	#
	# @param dtool (`DrawTool` object)
	# <br>	-- The DrawTool to draw onto
	#
	def update_display(self, dtool):
		dtool.set_stroke_width(0);
		self._draw_static_obstacles(dtool)
		for obs in self.dynamic_obstacles:
			dtool.set_color(obs.fillcolor);
			self._draw_obstacle(dtool, obs)


	def _draw_static_obstacles(self, dtool):
		# Draw the background
		dtool.set_color((0xFF, 0xFF, 0xFF))
		dtool.draw_rect([-20,-20], [self.width, self.height])

		# Draw static obstacles
		for obs in self.static_obstacles:
			dtool.set_color(obs.fillcolor)
			self._draw_obstacle(dtool, obs)


	def _draw_obstacle(self, dtool, obs):
		if (obs.shape == 1):
			dtool.draw_circle(np.array(obs.coordinate), obs.radius)
		elif (obs.shape == 2):
			dtool.draw_rect(obs.coordinate.tolist(), obs.size)
		elif (obs.shape == 3):
			vec = obs.get_velocity_vector()
			angle = np.arctan2(vec[1], vec[0])
			dtool.draw_ellipse(np.array(obs.coordinate), obs.width, obs.height, angle)
		elif (obs.shape == 4):
			dtool.draw_poly(obs.polygon.get_vertices())


	## Checks what kind of obstacle the given point is
	# 
	# @param location (numpy array)
	# <br>  Format: `[x, y]`
	# <br>  -- Location to check
	#
	def get_obsflags(self, location):
		flags = 0x00000000
		for obs in self.dynamic_obstacles:
			vec = np.subtract(location, obs.coordinate)
			if (obs.shape == 1 and np.dot(vec, vec) < obs.radius) \
				or (obs.shape == 2 and Geometry.point_inside_rectangle([obs.coordinate, obs.size], location)) \
				or (obs.shape == 3 and np.dot(vec, vec) < max(obs.width, obs.height)**2/4 and Geometry.point_inside_ellipse(obs.coordinate, obs.width, obs.height, np.arctan2(obs.get_velocity_vector()[1], obs.get_velocity_vector()[0]), location)) \
				or (obs.shape == 4 and obs.polygon.contains_point(location)):
				flags |= ObsFlag.DYNAMIC_OBSTACLE
				break

		for obs in self.static_obstacles:
			vec = np.subtract(location, obs.coordinate)
			if (obs.shape == 1 and np.dot(vec, vec) < obs.radius) \
				or (obs.shape == 2 and Geometry.point_inside_rectangle([obs.coordinate, obs.size], location)) \
				or (obs.shape == 3 and np.dot(vec, vec) < max(obs.width, obs.height)**2/4 and Geometry.point_inside_ellipse(obs.coordinate, obs.width, obs.height, np.arctan2(obs.get_velocity_vector()[1], obs.get_velocity_vector()[0]), location)) \
				or (obs.shape == 4 and obs.polygon.contains_point(location)):
				flags |= ObsFlag.STATIC_OBSTACLE
				break

		if flags & (ObsFlag.DYNAMIC_OBSTACLE | ObsFlag.STATIC_OBSTACLE):
			flags |= ObsFlag.ANY_OBSTACLE

		return flags

