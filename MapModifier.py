

## @package MapModifier
#

import numpy  as np
import Vector
import Geometry
import os
import sys
import json
from DynamicObstacles import DynamicObstacle
import MovementPattern


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

	speed = np.random.uniform(low=speed_low, high=speed_high)
	path_list = []
	for j in range(num_path_points):
		x_coord = int(np.random.uniform(path_x_low, path_x_high))
		y_coord = int(np.random.uniform(path_y_low, path_y_high))
		path_list.append((x_coord, y_coord))

	# For smooth looping, close the path
	path_list.append(path_list[0])

	obs_mover = MovementPattern.PathMovement(path_list, speed=speed, loop=True)

	dynobs = DynamicObstacle(obs_mover)

	dynobs.radius = int(np.random.uniform(radius_low, radius_high))
	dynobs.size = [dynobs.radius, dynobs.radius];
	dynobs.shape = shape

	return dynobs


## Gets the speed of the obstacles given the speed mode
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
def _get_speed_for_speedmode(speedmode):
	if speedmode == 0:
		return np.random.uniform(low=1.0, high=9.0);
	elif speedmode == 1:
		return 4;
	elif (speedmode == 2):
		return 8;
	elif speedmode == 3:
		return 10;
	elif speedmode == 4:
		return np.array ([4, 8])[np.random.randint(2)];
	elif speedmode == 5:
		return 6;
	elif speedmode == 6:
		return 12;
	elif speedmode == 7:
		return 5;
	elif speedmode == 8:
		return 10;
	elif speedmode == 9:
		return 15;
	elif speedmode == 10:
		return np.random.uniform(low=5.0, high=15.0);
	else:
		sys.stderr.write("Invalid speed mode. Assuming mode 0.\n");
		sys.stderr.flush();


## Creates kwargs to set speed_low and speed_high for
# make_randompath_dynamic_obstacle given a fixed speed
#
def _fixed_speed_kwargs(speed):
	return {'speed_low': speed, 'speed_high': speed}


def _map_mod_1(env):

	for i in range(1, 20):
		speed = _get_speed_for_speedmode(env.get_speed_mode())
		speed_args = _fixed_speed_kwargs(speed)
		dynobs = make_randompath_dynamic_obstacle(env, radius_low=10, radius_high=35, **speed_args)
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(4):
		x = int(np.random.uniform(100, 700))
		y = int(np.random.uniform(150, 450))
		origin = (x,y)

		speed = _get_speed_for_speedmode(env.get_speed_mode())
		obs_mover = MovementPattern.CircleMovement(origin, 30, speed=speed)

		dynobs = DynamicObstacle(obs_mover)

		dynobs.radius = int(np.random.uniform(20, 30))
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(4):
		x = int(np.random.uniform(100, 700))
		y = int(np.random.uniform(150, 450))
		origin = np.array([x, y])

		speed = _get_speed_for_speedmode(env.get_speed_mode())
		obs_mover = MovementPattern.RandomMovement(initial_pos=origin, speed=speed)

		dynobs = DynamicObstacle(obs_mover)

		dynobs.size = [int(np.random.uniform(20, 30)),int(np.random.uniform(20, 30))]
		dynobs.shape = 2
		env.dynamic_obstacles.append(dynobs)


def _map_mod_2(env):
	p_list = [
		[100, 50],
		[400, 350],
		[600, 175],
	]

	for p in p_list:
		x = p[0]
		y = p[1]
		origin = np.array([x, y])
		speed = _get_speed_for_speedmode(env.get_speed_mode())
		obs_mover = MovementPattern.CircleMovement(origin, 30, 10)

		dynobs = DynamicObstacle(obs_mover)

		dynobs.radius = 50
		dynobs.shape = 1

		env.dynamic_obstacles.append(dynobs)


def _map_mod_3(env):
	for j in np.arange(8):
		x = int(np.random.uniform(100, 700))
		y = int(np.random.uniform(150, 450))
		origin	= (x,y)

		speed = _get_speed_for_speedmode(env.get_speed_mode())
		obs_mover = MovementPattern.CircleMovement(origin, 30, speed=speed)

		dynobs = DynamicObstacle(obs_mover)

		dynobs.radius = int(np.random.uniform(20, 30))
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)


def _map_mod_4(env):

	for i in range(1, 20):
		speed = _get_speed_for_speedmode(env.get_speed_mode())
		speed_args = _fixed_speed_kwargs(speed)
		dynobs = make_randompath_dynamic_obstacle(env, **speed_args)
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(10):
		x = int(np.random.uniform(0, 800))
		y = int(np.random.uniform(0, 600))
		origin = np.array([x, y])

		speed = _get_speed_for_speedmode(env.get_speed_mode())
		obs_mover = MovementPattern.CircleMovement(origin, 30, speed=speed)

		dynobs = DynamicObstacle(obs_mover)

		dynobs.radius = int(np.random.uniform(10, 20))
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(10):
		x = int(np.random.uniform(0, 800))
		y = int(np.random.uniform(0, 600))
		origin = np.array([x, y])

		speed = _get_speed_for_speedmode(env.get_speed_mode())
		obs_mover = MovementPattern.RandomMovement(initial_pos=origin, speed=speed)

		dynobs = DynamicObstacle(obs_mover)

		dynobs.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
		dynobs.shape = 2
		env.dynamic_obstacles.append(dynobs)


def _map_mod_5(env):

	for i in range(1, 20):
		speed = _get_speed_for_speedmode(env.get_speed_mode())
		speed_args = _fixed_speed_kwargs(speed)
		dynobs = make_randompath_dynamic_obstacle(env, radius_low=10, radius_high=25, **speed_args)
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(10):
		x = int(np.random.uniform(0, 800))
		y = int(np.random.uniform(0, 600))
		origin = np.array([x, y])

		speed = _get_speed_for_speedmode(env.get_speed_mode())
		obs_mover = MovementPattern.CircleMovement(origin, 30, speed=speed)

		dynobs = DynamicObstacle(obs_mover)

		dynobs.radius = int(np.random.uniform(10, 20))
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)
	for j in np.arange(10):
		x = int(np.random.uniform(0, 800))
		y = int(np.random.uniform(0, 600))
		origin = np.array([x, y])

		speed = _get_speed_for_speedmode(env.get_speed_mode())
		obs_mover = MovementPattern.RandomMovement(initial_pos=origin, speed=speed)

		dynobs = DynamicObstacle(obs_mover)

		dynobs.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
		dynobs.shape = 2
		env.dynamic_obstacles.append(dynobs)


def _map_mod_7(env):
	y_arr = [50, 200, 350, 500]

	for x in [200, 440]:
		for ind,i in enumerate(y_arr):
			origin = np.array([x, i])

			speed = _get_speed_for_speedmode(env.get_speed_mode())
			obs_mover = MovementPattern.CircleMovement(origin, 30, speed=speed)

			dynobs = DynamicObstacle(obs_mover)

			dynobs.radius = 50
			dynobs.shape = 1
			env.dynamic_obstacles.append(dynobs)

	for x in [300, 560]:
		for ind, i in enumerate(y_arr):
			origin = np.array([x, i])

			speed = _get_speed_for_speedmode(env.get_speed_mode())
			obs_mover = MovementPattern.RandomMovement(initial_pos=origin, speed=speed)

			dynobs = DynamicObstacle(obs_mover)

			dynobs.size = [50,50]
			dynobs.shape = 2
			env.dynamic_obstacles.append(dynobs)


def _map_mod_8(env):

	x = [100, 400, 600, 100,700,650]
	y = [50, 350, 175, 200, 400,500]
	for ind,i in enumerate (x):
		origin = np.array([i, y[ind]])

		speed = _get_speed_for_speedmode(env.get_speed_mode())
		obs_mover = MovementPattern.CircleMovement(origin, 30, speed=speed)

		dynobs = DynamicObstacle(obs_mover)

		dynobs.radius = 20
		dynobs.shape = 1
		env.dynamic_obstacles.append(dynobs)


def _map_mod_9(env):
	for i in range(1, 15):
		speed = _get_speed_for_speedmode(env.get_speed_mode())
		speed_args = _fixed_speed_kwargs(speed)
		dynobs = make_randompath_dynamic_obstacle(env, radius_low=10, radius_high=25, **speed_args);
		env.dynamic_obstacles.append(dynobs)

# Swarm of obstacles
def _map_mod_10(env):
	for i in range(1, 70):
		speed = _get_speed_for_speedmode(env.get_speed_mode())
		speed_args = _fixed_speed_kwargs(speed)
		dynobs = make_randompath_dynamic_obstacle(env, radius_low=10, radius_high=15, **speed_args);
		env.dynamic_obstacles.append(dynobs)


def _map_mod_11(env):
	for i in range(20):
		dynobs = None;
		speed = _get_speed_for_speedmode(env.get_speed_mode())
		speed_args = _fixed_speed_kwargs(speed)
		while dynobs is None or Vector.distance_between(dynobs.coordinate, [50,550]) < 100:
			dynobs = make_randompath_dynamic_obstacle(env, radius_low=5, radius_high=30, **speed_args);
		dynobs.shape = 1 if i < 10 else 2;
		env.dynamic_obstacles.append(dynobs);


def _map_mod_12(env):
	for i in range(20):
		dynobs = None;
		speed = _get_speed_for_speedmode(env.get_speed_mode())
		speed_args = _fixed_speed_kwargs(speed)
		while dynobs is None or Vector.distance_between(dynobs.coordinate, [50,550]) < 100:
			dynobs = make_randompath_dynamic_obstacle(env, radius_low=5, radius_high=30, num_path_points=2, **speed_args);
		dynobs.shape = 1 if i < 10 else 2;
		env.dynamic_obstacles.append(dynobs);


## Load JSON file with obstacle movement data
#
def _map_mod_obsmat(env):
	H_pix2meter = np.array([
		[2.8128700e-02, 2.0091900e-03, -4.6693600e+00],
		[8.0625700e-04, 2.5195500e-02, -5.0608800e+00],
		[3.4555400e-04, 9.2512200e-05,  4.6255300e-01]
	])
	H_meter2pix = np.linalg.inv(H_pix2meter)

	with open('obsmat.json', 'r') as f:
		obsmat = json.load(f)
		time_offset = obsmat[str(env.cmdargs.ped_id_to_replace)][0]['time'] if env.cmdargs.ped_id_to_replace > 0 else 0
		for ped_id in obsmat:
			if ped_id == str(env.cmdargs.ped_id_to_replace):
				continue

			path_list = []
			firstpoint = obsmat[ped_id][0]
			path_list.append((-1000, -1000, firstpoint['time']-time_offset))
			for waypoint in obsmat[ped_id]:
				#pos = Geometry.apply_homography(H_meter2pix, (waypoint['pos_x'], waypoint['pos_y']))
				pos = (waypoint['pos_x'], waypoint['pos_y'])
				# Rotate 90 degrees to match video
				path_list.append((pos[1], pos[0], waypoint['time']-time_offset))

			# Get obstacles offscreen after they finish their path
			path_list.append((-1000, -1000, path_list[-1][2]+0.01))

			obs_mover = MovementPattern.PathMovement(path_list, loop=False)

			dynobs = DynamicObstacle(obs_mover, obs_id=int(ped_id))
			dynobs.shape = 3
			dynobs.width = 0.6
			dynobs.height = 0.3
			env.dynamic_obstacles.append(dynobs)

