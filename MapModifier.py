

## @package MapModifier
#

import numpy  as np
from DynamicObstacles import DynamicObstacle


def make_randompath_dynamic_obstacle(env,
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
	x_high = env.width if x_high is None else x_high
	y_high = env.height if y_high is None else y_high
	path_x_high = env.width if path_x_high is None else path_x_high
	path_y_high = env.height if path_y_high is None else path_y_high

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


def _map_mod_1(env):

	for i in range(1, 20):
		dynobs = make_randompath_dynamic_obstacle(env, radius_low=10, radius_high=35, speed_high=7.0)
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(4):
		dynobs = DynamicObstacle()
		x = int(np.random.uniform(100, 700))
		y = int(np.random.uniform(150, 450))
		dynobs.coordinate = np.array([x,y])
		dynobs.origin	= (x,y)
		dynobs.movement_mode = 2
		dynobs.radius = int(np.random.uniform(20, 30))
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(4):
		dynobs = DynamicObstacle()
		x = int(np.random.uniform(100, 700))
		y = int(np.random.uniform(150, 450))
		dynobs.coordinate = np.array([x, y])
		dynobs.origin = np.array([x, y])
		dynobs.movement_mode = 1
		dynobs.size = [int(np.random.uniform(20, 30)),int(np.random.uniform(20, 30))]
		dynobs.shape = 2
		env.dynamic_obstacles.append(dynobs)


def _map_mod_2(env,image):

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

	env.dynamic_obstacles.append(dynobs1)
	env.dynamic_obstacles.append(dynobs2)
	env.dynamic_obstacles.append(dynobs3)




def _map_mod_3(env):
	for j in np.arange(8):
		dynobs = DynamicObstacle()
		x = int(np.random.uniform(100, 700))
		y = int(np.random.uniform(150, 450))
		dynobs.coordinate = np.array([x,y])
		dynobs.origin	= (x,y)
		dynobs.movement_mode = 2
		dynobs.radius = int(np.random.uniform(20, 30))
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)


def _map_mod_4(env):

	for i in range(1, 20):
		dynobs = make_randompath_dynamic_obstacle(env)
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(10):
		dynobs = DynamicObstacle()
		x = int(np.random.uniform(0, 800))
		y = int(np.random.uniform(0, 600))
		dynobs.coordinate = np.array([x, y])
		dynobs.origin = np.array([x, y])
		dynobs.movement_mode = 2
		dynobs.radius = int(np.random.uniform(10, 20))
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(10):
		dynobs = DynamicObstacle()
		x = int(np.random.uniform(0, 800))
		y = int(np.random.uniform(0, 600))
		dynobs.coordinate = np.array([x, y])
		dynobs.origin = np.array([x, y])
		dynobs.movement_mode = 1
		dynobs.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
		dynobs.shape = 2
		env.dynamic_obstacles.append(dynobs)


def _map_mod_5(env):

	for i in range(1, 20):
		dynobs = make_randompath_dynamic_obstacle(env, radius_low=10, radius_high=25)
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(10):
		dynobs = DynamicObstacle()
		x = int(np.random.uniform(0, 800))
		y = int(np.random.uniform(0, 600))
		dynobs.coordinate = np.array([x, y])
		dynobs.origin = np.array([x, y])
		dynobs.movement_mode = 2
		dynobs.radius = int(np.random.uniform(10, 20))
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(10):
		dynobs = DynamicObstacle()
		x = int(np.random.uniform(0, 800))
		y = int(np.random.uniform(0, 600))
		dynobs.coordinate = np.array([x, y])
		dynobs.origin = np.array([x, y])
		dynobs.movement_mode = 1
		dynobs.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
		dynobs.shape = 2
		env.dynamic_obstacles.append(dynobs)




def _map_mod_7(env):
	x = [200, 300, 440, 560]
	y = [50, 200, 350, 500]

	for ind,i in enumerate(y):
		dynobs = DynamicObstacle()
		dynobs.coordinate = np.array([x[0], i])
		dynobs.origin = np.array([x[0], i])
		dynobs.movement_mode = 2
		dynobs.radius = 50
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)
	for ind, i in enumerate(y):
		dynobs = DynamicObstacle()
		dynobs.coordinate = np.array([x[2], i])
		dynobs.origin = np.array([x[2], i])
		dynobs.movement_mode = 2
		dynobs.radius = 50
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)

	for ind, i in enumerate(y):
		dynobs = DynamicObstacle()
		dynobs.coordinate = np.array([x[1], i])
		dynobs.origin = np.array([x[1], i])
		dynobs.movement_mode = 1
		dynobs.size = [50,50]
		dynobs.shape = 2
		env.dynamic_obstacles.append(dynobs)
	for ind, i in enumerate(y):
		dynobs = DynamicObstacle()
		dynobs.coordinate = np.array([x[3], i])
		dynobs.origin = np.array([x[3], i])
		dynobs.movement_mode = 1
		dynobs.size = [50, 50]
		dynobs.shape = 2
		env.dynamic_obstacles.append(dynobs)


def _map_mod_8(env):

	x = [100, 400, 600, 100,700,650]
	y = [50, 350, 175, 200, 400,500]
	for ind,i in enumerate (x):
		dynobs = DynamicObstacle()
		dynobs.coordinate = np.array([i, y[ind]])
		dynobs.origin = np.array([i, y[ind]])
		dynobs.movement_mode = 2
		dynobs.radius = 20
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)


def _map_mod_9(env):
	for i in range(1, 15):
		dynobs = make_randompath_dynamic_obstacle(env, radius_low=10, radius_high=25)
		env.dynamic_obstacles.append(dynobs)

# Swarm of obstacles
def _map_mod_10(env):
	for i in range(1, 70):
		dynobs = make_randompath_dynamic_obstacle(env, radius_low=10, radius_high=15, speed_high=11.0)
		env.dynamic_obstacles.append(dynobs)


def _map_mod_11(env):
	for i in range(20):
		dynobs = None;
		while dynobs is None or Vector.distance_between(dynobs.coordinate, [50,550]) < 100:
			dynobs = make_randompath_dynamic_obstacle(env, radius_low=5, radius_high=30);
		dynobs.shape = 1 if i < 10 else 2;
		env.dynamic_obstacles.append(dynobs);


def _map_mod_12(env):
	for i in range(20):
		dynobs = None;
		while dynobs is None or Vector.distance_between(dynobs.coordinate, [50,550]) < 100:
			dynobs = make_randompath_dynamic_obstacle(env, radius_low=5, radius_high=30, num_path_points=2);
		dynobs.shape = 1 if i < 10 else 2;
		env.dynamic_obstacles.append(dynobs);
