#!/usr/bin/python3

## @package GridDataEnvironment
#

import numpy  as np
import pygame as PG
import DrawTool
from  DynamicObstacles import DynamicObstacle
import sys
import Vector
import MapModifier
from Environment import ObsFlag, Environment


## Holds information related to the simulation environment, such as the
# position and motion of dynamic obstacles, and the static map.
#
class GridDataEnvironment(Environment):

	def __init__(self, width, height, map_filename, cmdargs=None):
		self.cmdargs = cmdargs
		self.width = width
		self.height = height
		self.grid_data = np.zeros((self.width, self.height), dtype=np.uint8)
		self.dynamic_obstacles = []

		# Note: Order is important here:
		#  - init_map_modifiers() MUST be called BEFORE
		#    loading and initilizing the map, or else the modifiers
		#    will not work
		#  - The map modifier must be applied before setting the
		#    speed mode

		# Init map modifiers
		self.map_modifiers = [None];
		self._init_map_modifiers();

		# Load the static map and apply the modifier to produce
		# dynamic obstacles
		self.load_map(map_filename)

		# Create static overlay (BEFORE applying map modifier)
		pix_arr = PG.surfarray.pixels2d(self.static_base_image.copy())
		pixel_mask = 0b11111100;
		masked_pix_arr = np.bitwise_and(pix_arr, np.array([pixel_mask], dtype='uint8'));
		grid_data_width = max(self.width, masked_pix_arr.shape[0]);
		grid_data_height = max(self.height, masked_pix_arr.shape[1]);
		self.static_overlay = np.zeros((grid_data_width, grid_data_height), dtype=int);
		obstacle_pixel_val = 0x555555 & pixel_mask # (85, 85, 85) represented as integer
		self.static_overlay[masked_pix_arr == obstacle_pixel_val] |= (ObsFlag.STATIC_OBSTACLE | ObsFlag.ANY_OBSTACLE);
		del pix_arr

		if (cmdargs):
			self.apply_map_modifier_by_number(self.cmdargs.map_modifier_num)
		# Set the speed mode
		self.set_speed_mode(self.cmdargs.speedmode)

		# Initialize the grid data
		self._grid_data_display = PG.Surface((self.width, self.height))
		self._update_grid_data();


	def _update_grid_data(self):
		self.update_display(DrawTool.PygameDrawTool(self._grid_data_display));
		self.update_grid_data_from_display(self._grid_data_display);


	def _init_map_modifiers(self):
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
		image = PG.image.load(map_filename).convert_alpha();
		self.static_base_image = image;


	## Draws the environment onto the given display.
	#
	# @param dtool (`DrawTool` object)
	# <br>	-- The DrawTool to draw onto
	#
	def update_display(self, dtool):
		dtool.draw_image(self.static_base_image, (0, 0))
		dtool.set_stroke_width(0);
		for i in self.dynamic_obstacles:
			dtool.set_color(i.fillcolor);
			if (i.shape == 1):
				dtool.draw_circle(np.array(i.coordinate, dtype='int64'), i.radius)
			if (i.shape == 2):
				dtool.draw_rect(i.coordinate.tolist(), i.size)
			if (i.shape == 3):
				dtool.draw_ellipse(np.array(i.coordinate, dtype='int64'), i.width, i.height, np.arctan2(i.direction[1], i.direction[0]))


	## Update the grid data from the given display.
	#
	# This method uses a `pygame.Surface` to construct an occupancy
	# grid of obstacles, by checking which pixels correspond to the
	# colors of static and dynamic obstacles.
	#
	# Note that this method updates this `GridDataEnvironment`'s internal
	# `grid_data` field rather than returning the result.
	#
	# @param display (`pygame.Surface`)
	# <br>	-- The display to use
	#
	def update_grid_data_from_display(self, display):
		self.needs_grid_data_update = False

		# Set grid_data to 1 where the corresponding pixel is obstacle-colored
		# Note: This approach forces grid_data to be at least as large as the pixel array,
		# potentially wasting some memory compared to using a nested for loop. It is
		# written this way intentionally to improve computation time (>1000%)

		pix_arr = PG.surfarray.pixels2d(display)

		# Mask pixel data to account for small errors in color
		# Note: This only works because it has been determined through 
		# experimentation that almost all color errors occur in the last two
		# bits of the value.
		pixel_mask = 0b11111100
		masked_pix_arr = np.bitwise_and(pix_arr, np.array([pixel_mask], dtype='uint8'))

		grid_data_width = max(self.width, masked_pix_arr.shape[0])
		grid_data_height = max(self.height, masked_pix_arr.shape[1] )
		self.grid_data = np.array(self.static_overlay);

		dynamic_obstacle_pixel_val = 0x44ccee & pixel_mask
		self.grid_data[masked_pix_arr == dynamic_obstacle_pixel_val] |= (ObsFlag.DYNAMIC_OBSTACLE | ObsFlag.ANY_OBSTACLE)
		
		# Uncomment the following lines to see the grid_data directly
		pix_arr[self.grid_data == 0] = 0xFFFFFF
		pix_arr[self.grid_data & ObsFlag.STATIC_OBSTACLE != 0] = 0x000000
		pix_arr[self.grid_data & ObsFlag.DYNAMIC_OBSTACLE != 0] = 0x44ccee
		del pix_arr


	## Step the environment, updating dynamic obstacles and grid data.
	#
	def next_step(self):
		if self.needs_grid_data_update:
			self._update_grid_data();
		self._update_dynamic_obstacles();
		self.needs_grid_data_update = True


	## Checks what kind of obstacle the given point is
	# 
	# @param location (numpy array)
	# <br>  Format: `[x, y]`
	# <br>  -- Location to check
	#
	def get_obsflags(self, location):
		return self.grid_data[int(location[0])][int(location[1])]
