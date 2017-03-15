#!/usr/bin/python3

## @package Environment
#

import numpy  as np
import pygame as PG
from  DynamicObstacles import DynamicObstacle
import sys


## Holds information related to the simulation environment, such as the
# position and motion of dynamic obstacles, and the static map.
#
class Environment:

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
		self.static_overlay[masked_pix_arr == obstacle_pixel_val] |= 0b101;

		if (cmdargs):
			self.apply_map_modifier_by_number(self.cmdargs.map_modifier_num)
		# Set the speed mode
		self.set_speed_mode(self.cmdargs.speedmode)

		# Initialize the grid data
		self._grid_data_display = PG.Surface((self.width, self.height))
		self._update_grid_data();

	def _update_grid_data(self):
		self.update_display(self._grid_data_display);
		self.update_grid_data_from_display(self._grid_data_display);


	def _init_map_modifiers(self):
		self.map_modifiers.append(Environment._map_mod_1);
		self.map_modifiers.append(Environment._map_mod_2);
		self.map_modifiers.append(Environment._map_mod_3);
		self.map_modifiers.append(Environment._map_mod_4);
		self.map_modifiers.append(Environment._map_mod_5);
		self.map_modifiers.append(None); 
		self.map_modifiers.append(Environment._map_mod_7);
		self.map_modifiers.append(Environment._map_mod_8);
		self.map_modifiers.append(Environment._map_mod_9);
		self.map_modifiers.append(Environment._map_mod_10);
		self.map_modifiers.append(Environment._map_mod_11);
		self.map_modifiers.append(Environment._map_mod_12);


	def load_map(self, map_filename):
		image = PG.image.load(map_filename).convert_alpha();
		self.static_base_image = image;


	## Sets the speed mode of the obstacles
	#
	# Currently, these modes are defined as follows:
	# <br>	0. No speed mode (leave speeds as default)
	# <br>	1. All obstacles move at speed 4
	# <br>	2. All obstacles move at speed 8
	# <br>	3. Obstacles move at the robot's normal speed
	# <br>	4. Roughly half the obstacles move at speed 4, the other
	# 	half move at speed 8
	# <br>	5. All obstacles move at speed 6
	# <br>	6. All obstacles move at speed 12
	#
	#
	# @param speedmode (int)
	# <br>	-- The number of the speed mode to set
	#
	def set_speed_mode(self, speedmode):
		for obstacle in self.dynamic_obstacles:
			if speedmode == 0:
				pass; # Leave obstacle speeds as default
			elif speedmode == 1:
				obstacle.speed = 4;		 
			elif (speedmode == 2):
				obstacle.speed = 8;
			elif speedmode == 3:
				obstacle.speed = self.cmdargs.robot_speed;
			elif speedmode == 4:
				obstacle.speed = np.array ([4, 8])[np.random.randint(2)];
			elif speedmode == 5:
				obstacle.speed = 6;
			elif speedmode == 6:
				obstacle.speed = 12;
			elif speedmode == 7:
				obstacle.speed = 5;
			elif speedmode == 8:
				obstacle.speed = self.cmdargs.robot_speed;
			elif speedmode == 9:
				obstacle.speed = 15;
			elif speedmode == 10:
				obstacle.speed = np.random.uniform(low=5.0, high=15.0);
			else:
				sys.stderr.write("Invalid speed mode. Assuming mode 0.\n");
				sys.stderr.flush();
				break;


	def apply_map_modifier_by_number(self, modifier_num):

		if (len(self.map_modifiers) <= modifier_num):
			return;
		map_modifier = self.map_modifiers[modifier_num];
		if map_modifier is None:
			return;

		map_modifier(self);


	def _make_randompath_dynamic_obstacle(self,
						x_low=1,
						x_high=None,
						y_low=1,
						y_high=None,
						radius_low=5,
						radius_high=40,
						shape=1,
						speed_low=1.0,
						speed_high=9.0,
						num_path_points=50,
						path_x_low=1,
						path_x_high=None,
						path_y_low=1,
						path_y_high=None):
		x_high = self.width if x_high is None else x_high
		y_high = self.width if y_high is None else y_high
		path_x_high = self.width if path_x_high is None else path_x_high
		path_y_high = self.width if path_y_high is None else path_y_high
 
		dynobs = DynamicObstacle()
		x_coord = int(np.random.uniform(low=x_low, high=x_high))
		y_coord = int(np.random.uniform(low=y_low, high=y_high))
		dynobs.coordinate = np.array([x_coord, y_coord])
		dynobs.origin = dynobs.coordinate
		
		dynobs.movement_mode = 3
		dynobs.radius = int(np.random.uniform(radius_low, radius_high))
		dynobs.size = [dynobs.radius, dynobs.radius];
		dynobs.shape = shape
		dynobs.speed = np.random.uniform(low=speed_low, high=speed_high)
		for j in range(num_path_points):
			x_coord = int(np.random.uniform(path_x_low, path_x_high))
			y_coord = int(np.random.uniform(path_y_low, path_y_high))
			dynobs.path_list.append(np.array([x_coord, y_coord]))
		return dynobs


	def _map_mod_1(self):

		for i in range(1, 20):
			dynobs = self._make_randompath_dynamic_obstacle(radius_low=10, radius_high=35, speed_high=7.0)
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(4):
			dynobs = DynamicObstacle()
			x = int(np.random.uniform(100, 700))
			y = int(np.random.uniform(150, 450))
			dynobs.coordinate = np.array([x,y])
			dynobs.origin	= (x,y)
			dynobs.movement_mode = 2
			dynobs.radius = int(np.random.uniform(20, 30))
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(4):
			dynobs = DynamicObstacle()
			x = int(np.random.uniform(100, 700))
			y = int(np.random.uniform(150, 450))
			dynobs.coordinate = np.array([x, y])
			dynobs.origin = np.array([x, y])
			dynobs.movement_mode = 1
			dynobs.size = [int(np.random.uniform(20, 30)),int(np.random.uniform(20, 30))]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)


	def _map_mod_2(self,image):

		x1 = 100
		x2 = 400
		x3 = 600

		y1 = 50
		y2 = 350
		y3 = 175

		dynobs1 = DynamicObstacle()
		dynobs1.coordinate = np.array([x1, y1])
		dynobs1.origin = np.array([x1, y1])
		dynobs1.movement_mode = 2
		dynobs1.radius = 50
		dynobs1.shape = 1


		dynobs2 = DynamicObstacle()
		dynobs2.coordinate = np.array([x2, y2])
		dynobs2.origin = np.array([x2, y2])
		dynobs2.movement_mode = 2
		dynobs2.radius = 50
		dynobs2.shape = 1


		dynobs3 = DynamicObstacle()
		dynobs3.coordinate = np.array([x3, y3])
		dynobs3.origin = np.array([x3, y3])
		dynobs3.movement_mode = 2
		dynobs3.radius = 50
		dynobs3.shape = 1

		self.dynamic_obstacles.append(dynobs1)
		self.dynamic_obstacles.append(dynobs2)
		self.dynamic_obstacles.append(dynobs3)




	def _map_mod_3(self):
		for j in np.arange(8):
			dynobs = DynamicObstacle()
			x = int(np.random.uniform(100, 700))
			y = int(np.random.uniform(150, 450))
			dynobs.coordinate = np.array([x,y])
			dynobs.origin	= (x,y)
			dynobs.movement_mode = 2
			dynobs.radius = int(np.random.uniform(20, 30))
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)


	def _map_mod_4(self):

		for i in range(1, 20):
			dynobs = self._make_randompath_dynamic_obstacle()
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(10):
			dynobs = DynamicObstacle()
			x = int(np.random.uniform(0, 800))
			y = int(np.random.uniform(0, 600))
			dynobs.coordinate = np.array([x, y])
			dynobs.origin = np.array([x, y])
			dynobs.movement_mode = 2
			dynobs.radius = int(np.random.uniform(10, 20))
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(10):
			dynobs = DynamicObstacle()
			x = int(np.random.uniform(0, 800))
			y = int(np.random.uniform(0, 600))
			dynobs.coordinate = np.array([x, y])
			dynobs.origin = np.array([x, y])
			dynobs.movement_mode = 1
			dynobs.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)


	def _map_mod_5(self):

		for i in range(1, 20):
			dynobs = self._make_randompath_dynamic_obstacle(radius_low=10, radius_high=25)
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(10):
			dynobs = DynamicObstacle()
			x = int(np.random.uniform(0, 800))
			y = int(np.random.uniform(0, 600))
			dynobs.coordinate = np.array([x, y])
			dynobs.origin = np.array([x, y])
			dynobs.movement_mode = 2
			dynobs.radius = int(np.random.uniform(10, 20))
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(10):
			dynobs = DynamicObstacle()
			x = int(np.random.uniform(0, 800))
			y = int(np.random.uniform(0, 600))
			dynobs.coordinate = np.array([x, y])
			dynobs.origin = np.array([x, y])
			dynobs.movement_mode = 1
			dynobs.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)




	def _map_mod_7(self):
		x = [200, 300, 440, 560]
		y = [50, 200, 350, 500]

		for ind,i in enumerate(y):
			dynobs = DynamicObstacle()
			dynobs.coordinate = np.array([x[0], i])
			dynobs.origin = np.array([x[0], i])
			dynobs.movement_mode = 2
			dynobs.radius = 50
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)
		for ind, i in enumerate(y):
			dynobs = DynamicObstacle()
			dynobs.coordinate = np.array([x[2], i])
			dynobs.origin = np.array([x[2], i])
			dynobs.movement_mode = 2
			dynobs.radius = 50
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)

		for ind, i in enumerate(y):
			dynobs = DynamicObstacle()
			dynobs.coordinate = np.array([x[1], i])
			dynobs.origin = np.array([x[1], i])
			dynobs.movement_mode = 1
			dynobs.size = [50,50]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)
		for ind, i in enumerate(y):
			dynobs = DynamicObstacle()
			dynobs.coordinate = np.array([x[3], i])
			dynobs.origin = np.array([x[3], i])
			dynobs.movement_mode = 1
			dynobs.size = [50, 50]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)


	def _map_mod_8(self):

		x = [100, 400, 600, 100,700,650]
		y = [50, 350, 175, 200, 400,500]
		for ind,i in enumerate (x):
			dynobs = DynamicObstacle()
			dynobs.coordinate = np.array([i, y[ind]])
			dynobs.origin = np.array([i, y[ind]])
			dynobs.movement_mode = 2
			dynobs.radius = 20
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)


	def _map_mod_9(self):
		for i in range(1, 15):
			dynobs = self._make_randompath_dynamic_obstacle(radius_low=10, radius_high=25)
			self.dynamic_obstacles.append(dynobs)

	# Swarm of obstacles
	def _map_mod_10(self):
		for i in range(1, 70):
			dynobs = self._make_randompath_dynamic_obstacle(radius_low=10, radius_high=15, speed_high=11.0)
			self.dynamic_obstacles.append(dynobs)


	def _map_mod_11(self):
		for i in range(20):
			dynobs = self._make_randompath_dynamic_obstacle(radius_low=5, radius_high=30);
			dynobs.shape = 1 if i < 10 else 2;
			self.dynamic_obstacles.append(dynobs);


	def _map_mod_12(self):
		for i in range(20):
			dynobs = self._make_randompath_dynamic_obstacle(radius_low=5, radius_high=30, num_path_points=2);
			dynobs.shape = 1 if i < 10 else 2;
			self.dynamic_obstacles.append(dynobs);


	def _update_dynamic_obstacles(self):
		for dynobs in self.dynamic_obstacles:
			dynobs.next_step();


	## Draws the environment onto the given display.
	#
	# @param display (pygame.Surface object)
	# <br>	-- The display to draw onto
	#
	def update_display(self, display):
		display.blit(self.static_base_image, (0, 0))
		for i in self.dynamic_obstacles:
			if (i.shape == 1):
				PG.draw.circle(display, i.fillcolor, np.array(i.coordinate, dtype='int64'), i.radius)
			if (i.shape == 2):
				PG.draw.rect(display, i.fillcolor, i.coordinate.tolist() + i.size)


	## Update the grid data from the given display.
	#
	# This method uses a `pygame.Surface` to construct an occupancy
	# grid of obstacles, by checking which pixels correspond to the
	# colors of static and dynamic obstacles.
	#
	# Note that this method updates this `Environment`'s internal
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
		self.grid_data = np.array(self.static_overlay); #np.zeros((grid_data_width, grid_data_height), dtype=int)

#		obstacle_pixel_val = 0x555555 & pixel_mask # (85, 85, 85) represented as integer
#		self.grid_data[masked_pix_arr == obstacle_pixel_val] = 1

		dynamic_obstacle_pixel_val = 0x227722 & pixel_mask # (34, 119, 34) represented as integer
		self.grid_data[masked_pix_arr == dynamic_obstacle_pixel_val] |= 3
		
		# Uncomment the following lines to see the grid_data directly
		pix_arr[self.grid_data == 0] = 0xFFFFFF
		pix_arr[self.grid_data & 4 != 0] = 0x000000
		pix_arr[self.grid_data & 2 != 0] = 0x77aadd


	## Step the environment, updating dynamic obstacles and grid data.
	#
	def next_step(self):
		if self.needs_grid_data_update:
			self._update_grid_data();
		self._update_dynamic_obstacles();
		self.needs_grid_data_update = True
