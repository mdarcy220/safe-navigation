
## @file StaticGeometricMaps.py
#

import numpy  as np
import Vector
import Geometry
import os
import sys
from DynamicObstacles import DynamicObstacle
import MovementPattern
from Polygon import Polygon
import json


def _create_map_1(env):
	#obs_movement = MovementPattern.StaticMovement((0,0))
	#obs = DynamicObstacle(obs_movement)
	#obs.fillcolor = (0x55, 0x55, 0x55)
	#obs.shape = 4
	#obs.polygon = Polygon([
	#	(640, 80),
	#	(640, 480),
	#	(445, 450),
	#	(408, 300),
	#	(408, 165),
	#	(460, 108),
	#	(490, 104),
	#	(490, 91),
	#	(640, 80),
	#]);
	with open('obs2.json') as f:
		obslist = json.load(f)

	for obs in obslist:
		obs_movement = MovementPattern.StaticMovement((0,0))
		if obs['type'] == 'circle':
			obs_movement = MovementPattern.StaticMovement(obs['center'])
			obs2 = DynamicObstacle(obs_movement)
			obs2.shape = 1
			obs2.radius = obs['radius']
			obs2.fillcolor = (0x55, 0x55, 0x55)
			env.static_obstacles.append(obs2)
			continue
		polygon = Polygon(np.array(obs['points']))
		obs2 = DynamicObstacle(obs_movement)
		obs2.shape = 4
		obs2.polygon = polygon
		obs2.fillcolor = (0x55, 0x55, 0x55)
		env.static_obstacles.append(obs2)

	#env.static_obstacles.append(obs)


def _create_map_2(env):
	with open('obs2.json') as f:
		obslist = json.load(f)

	for obs in obslist:
		obs_movement = MovementPattern.StaticMovement((0,0))
		if obs['type'] == 'circle':
			obs_movement = MovementPattern.StaticMovement(obs['center'])
			obs2 = DynamicObstacle(obs_movement)
			obs2.shape = 1
			obs2.radius = obs['radius']
			obs2.fillcolor = (0x55, 0x55, 0x55)
			env.static_obstacles.append(obs2)
			continue
		polygon = Polygon(np.array(obs['points']))
		obs2 = DynamicObstacle(obs_movement)
		obs2.shape = 4
		obs2.polygon = polygon
		obs2.fillcolor = (0x55, 0x55, 0x55)
		env.static_obstacles.append(obs2)

	#env.static_obstacles.append(obs)

