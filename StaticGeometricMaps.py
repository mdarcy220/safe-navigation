
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


def _create_obs_from_spec(obs_spec):
	obs_movement = MovementPattern.StaticMovement((0,0))
	if obs_spec['type'] == 'circle':
		obs_movement = MovementPattern.StaticMovement(obs_spec['center'])
		new_obs = DynamicObstacle(obs_movement)
		new_obs.shape = 1
		new_obs.radius = obs_spec['radius']
		new_obs.fillcolor = (0x55, 0x55, 0x55)
		return new_obs

	polygon = Polygon(np.array(obs_spec['points']))
	new_obs = DynamicObstacle(obs_movement)
	new_obs.shape = 4
	new_obs.polygon = polygon
	new_obs.fillcolor = (0x55, 0x55, 0x55)
	return new_obs


def load_map_file(map_filename):
	obs_list = []
	obs_spec_list = []
	with open(map_filename) as f:
		obs_spec_list = json.load(f)

	for obs_spec in obs_spec_list:
		obs_list.append(_create_obs_from_spec(obs_spec))

	return obs_list

