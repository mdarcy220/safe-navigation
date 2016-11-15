import numpy  as np
import pygame as PG
from  DynamicObstacles import DynamicObs
class Environment(object):

	def __init__(self, Width, Height, MapName, position = (0,0), cmdargs=None):
		self.cmdargs			= cmdargs
		self.width	  = Width
		self.height   = Height
		self.grid_data			 = np.zeros((self.width,self.height ), dtype=int)
		self.MapName			= MapName
		self.Position			= position
		self.dynamic_obstacles	 = []
		self.map_modifiers = [None]
		self.init_map_modifiers()
		self.LoadMap(self.MapName)


	def init_map_modifiers(self):
		self.map_modifiers.append(self.Map1);
		self.map_modifiers.append(self.Map2);
		self.map_modifiers.append(self.Map3);
		self.map_modifiers.append(self.Map4);
		self.map_modifiers.append(self.Map5);
		self.map_modifiers.append(None); 
		self.map_modifiers.append(self.Map7);
		self.map_modifiers.append(self.Map8);
		self.map_modifiers.append(self.Map9);
		self.map_modifiers.append(self.Map10);


	def LoadMap(self, Mapname):
		image = PG.image.load(self.MapName)
		self.static_base_image = image
		if (self.cmdargs):
			self.apply_map_modifier_by_number(image, self.cmdargs.map_modifier_num)
		self.SetSpeeds(self.cmdargs.speedmode)


	def SetSpeeds(self, speedmode):
		#1	Obstacles slower
		#2	Obstacles faster
		#3	Obstacles same as robot
		#4	Obstacles 50% faster and 50% slower
		#5	Robot speed is always fastest		 
		
		for DO in self.dynamic_obstacles:
			if speedmode == 1:
				DO.speed = 4		 
			elif (speedmode == 2):
				DO.speed = 8
			elif speedmode == 3:
				DO.speed = self.cmdargs.robot_speed
			elif speedmode == 4:
				DO.speed = np.array ([4, 8])[np.random.randint(2)]
			elif speedmode == 5:
				DO.speed = 6
			elif speedmode == 6:
				DO.speed = 12
					
		

	def apply_map_modifier_by_number(self, image, modifier_num):

		if (len(self.map_modifiers) <= modifier_num):
			return
		map_modifier = self.map_modifiers[modifier_num]
		if map_modifier is None:
			return

		map_modifier(image)

	def make_randompath_dynamic_obstacle(self,
										x_low=1,
										x_high=None,
										y_low=1,
										y_high=None,
										radius_low=5,
										radius_high=40,
										shape=1,
										speed_low=1.0,
										speed_high=9.0,
										num_path_points=15,
										path_x_low=1,
										path_x_high=None,
										path_y_low=1,
										path_y_high=None):
		x_high = self.width if x_high is None else x_high
		y_high = self.width if y_high is None else y_high
		path_x_high = self.width if path_x_high is None else path_x_high
		path_y_high = self.width if path_y_high is None else path_y_high
 
		dynobs = DynamicObs()
		x_coord = int(np.random.uniform(low=x_low, high=x_high))
		y_coord = int(np.random.uniform(low=y_low, high=y_high))
		dynobs.coordinate = (x_coord, y_coord)
		dynobs.origin = dynobs.coordinate
		
		dynobs.movement_mode = 3
		dynobs.radius = int(np.random.uniform(radius_low, radius_high))
		dynobs.shape = shape
		dynobs.speed = np.random.uniform(low=speed_low, high=speed_high)
		for j in range(1, num_path_points):
			x_coord = int(np.random.uniform(path_x_low, path_x_high))
			y_coord = int(np.random.uniform(path_y_low, path_y_high))
			dynobs.path_list.append(np.array([x_coord, y_coord]))
		return dynobs


	def Map1(self, image):

		for i in range(1, 20):
			dynobs = self.make_randompath_dynamic_obstacle(radius_low=10, radius_high=35, speed_high=7.0)
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(4):
			dynobs = DynamicObs()
			x = int(np.random.uniform(100, 700))
			y = int(np.random.uniform(150, 450))
			dynobs.coordinate = (x,y)
			dynobs.origin	= (x,y)
			dynobs.movement_mode = 2
			dynobs.radius = int(np.random.uniform(20, 30))
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(4):
			dynobs = DynamicObs()
			x = int(np.random.uniform(100, 700))
			y = int(np.random.uniform(150, 450))
			dynobs.coordinate = (x, y)
			dynobs.origin = (x, y)
			dynobs.movement_mode = 1
			dynobs.size = [int(np.random.uniform(20, 30)),int(np.random.uniform(20, 30))]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)


	def Map2(self,image):

		x1 = 100
		x2 = 400
		x3 = 600

		y1 = 50
		y2 = 350
		y3 = 175

		dynobs1 = DynamicObs()
		dynobs1.coordinate = (x1, y1)
		dynobs1.origin = (x1, y1)
		dynobs1.movement_mode = 2
		dynobs1.radius = 50
		dynobs1.shape = 1


		dynobs2 = DynamicObs()
		dynobs2.coordinate = (x2, y2)
		dynobs2.origin = (x2, y2)
		dynobs2.movement_mode = 2
		dynobs2.radius = 50
		dynobs2.shape = 1


		dynobs3 = DynamicObs()
		dynobs3.coordinate = (x3, y3)
		dynobs3.origin = (x3, y3)
		dynobs3.movement_mode = 2
		dynobs3.radius = 50
		dynobs3.shape = 1

		self.dynamic_obstacles.append(dynobs1)
		self.dynamic_obstacles.append(dynobs2)
		self.dynamic_obstacles.append(dynobs3)




	def Map3(self, image):
		for j in np.arange(8):
			dynobs = DynamicObs()
			x = int(np.random.uniform(100, 700))
			y = int(np.random.uniform(150, 450))
			dynobs.coordinate = (x,y)
			dynobs.origin	= (x,y)
			dynobs.movement_mode = 2
			dynobs.radius = int(np.random.uniform(20, 30))
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)


	def Map4(self, image):

		for i in range(1, 20):
			dynobs = self.make_randompath_dynamic_obstacle()
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(10):
			dynobs = DynamicObs()
			x = int(np.random.uniform(0, 800))
			y = int(np.random.uniform(0, 600))
			dynobs.coordinate = (x, y)
			dynobs.origin = (x, y)
			dynobs.movement_mode = 2
			dynobs.radius = int(np.random.uniform(10, 20))
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(10):
			dynobs = DynamicObs()
			x = int(np.random.uniform(0, 800))
			y = int(np.random.uniform(0, 600))
			dynobs.coordinate = (x, y)
			dynobs.origin = (x, y)
			dynobs.movement_mode = 1
			dynobs.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)


	def Map5(self, image):

		for i in range(1, 20):
			dynobs = self.make_randompath_dynamic_obstacle(radius_low=10, radius_high=25)
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(10):
			dynobs = DynamicObs()
			x = int(np.random.uniform(0, 800))
			y = int(np.random.uniform(0, 600))
			dynobs.coordinate = (x, y)
			dynobs.origin = (x, y)
			dynobs.movement_mode = 2
			dynobs.radius = int(np.random.uniform(10, 20))
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)
		for j in np.arange(10):
			dynobs = DynamicObs()
			x = int(np.random.uniform(0, 800))
			y = int(np.random.uniform(0, 600))
			dynobs.coordinate = (x, y)
			dynobs.origin = (x, y)
			dynobs.movement_mode = 1
			dynobs.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)




	def Map7(self, image):
		x = [200, 300, 440, 560]
		y = [50, 200, 350, 500]

		for ind,i in enumerate(y):
			dynobs = DynamicObs()
			dynobs.coordinate = (x[0], i)
			dynobs.origin = (x[0], i)
			dynobs.movement_mode = 2
			dynobs.radius = 50
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)
		for ind, i in enumerate(y):
			dynobs = DynamicObs()
			dynobs.coordinate = (x[2], i)
			dynobs.origin = (x[2], i)
			dynobs.movement_mode = 2
			dynobs.radius = 50
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)

		for ind, i in enumerate(y):
			dynobs = DynamicObs()
			dynobs.coordinate = (x[1], i)
			dynobs.origin =  (x[1], i)
			dynobs.movement_mode = 1
			dynobs.size = [50,50]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)
		for ind, i in enumerate(y):
			dynobs = DynamicObs()
			dynobs.coordinate = (x[3], i)
			dynobs.origin = (x[3], i)
			dynobs.movement_mode = 1
			dynobs.size = [50, 50]
			dynobs.shape = 2
			self.dynamic_obstacles.append(dynobs)


	def Map8(self, image):

		x = [100, 400, 600, 100,700,650]
		y = [50, 350, 175, 200, 400,500]
		for ind,i in enumerate (x):
			dynobs = DynamicObs()
			dynobs.coordinate = (i, y[ind])
			dynobs.origin = (i, y[ind])
			dynobs.movement_mode = 2
			dynobs.radius = 20
			dynobs.shape = 1
			self.dynamic_obstacles.append(dynobs)


	def Map9(self, image):
		for i in range(1, 15):
			dynobs = self.make_randompath_dynamic_obstacle(radius_low=10, radius_high=25)
			self.dynamic_obstacles.append(dynobs)

	# Swarm of obstacles
	def Map10(self, image): 
		for i in range(1, 70):
			dynobs = self.make_randompath_dynamic_obstacle(radius_low=10, radius_high=15, speed_high=11.0)
			self.dynamic_obstacles.append(dynobs)


	def Nextstep (self, display):
		display.blit(self.static_base_image, self.Position)
		for i in self.dynamic_obstacles:
			i.NextStep()
			if (i.shape == 1):
				PG.draw.circle(display, i.fillcolor, np.array(i.coordinate, dtype='int64'), i.radius)
			if (i.shape == 2):
				PG.draw.rect(display, i.fillcolor, i.coordinate + i.size)

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
		self.grid_data = np.zeros((grid_data_width, grid_data_height), dtype=int)

		obstacle_pixel_val = 0x555555 & pixel_mask # (85, 85, 85) represented as integer
		self.grid_data[masked_pix_arr == obstacle_pixel_val] = 1

		dynamic_obstacle_pixel_val = 0x227722 & pixel_mask # (34, 119, 34) represented as integer
		self.grid_data[masked_pix_arr == dynamic_obstacle_pixel_val] = 3
		
		# Uncomment the following two lines to see the grid_data directly
		pix_arr[self.grid_data==0] = 0
		pix_arr[self.grid_data==3] = 0x115599
		pix_arr[self.grid_data==1] = 0xFFFFFF
