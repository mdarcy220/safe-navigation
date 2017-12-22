
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


def _create_map_1(env):
	obs_movement = MovementPattern.StaticMovement((0,0))
	obs = DynamicObstacle(obs_movement)
	obs.fillcolor = (0x55, 0x55, 0x55)
	obs.shape = 4
	obs.polygon = Polygon([
		(640, 80),
		(640, 480),
		(445, 450),
		(408, 300),
		(408, 165),
		(460, 108),
		(490, 104),
		(490, 91),
		(640, 80),
	]);

	env.static_obstacles.append(obs)

