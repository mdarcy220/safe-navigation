
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
import xml.etree.ElementTree
import re


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


def _rect_to_poly_obs(rect):
	poly_points = []
	poly_points.append([rect['x'], rect['y']])
	poly_points.append([rect['x']+rect['width'], rect['y']])
	poly_points.append([rect['x']+rect['width'], rect['y']+rect['height']])
	poly_points.append([rect['x'], rect['y']+rect['height']])
	poly_points.append([rect['x'], rect['y']])

	return {'type': 'polygon', 'points': poly_points}

def _svg_circle_to_circle_obs(circle):
	return {'type': 'circle', 'center': circle['center'], 'radius': circle['radius']}

## Loads an SVG as a static map
#
# Note: SVG semantics can be complex, and this function handles only the
# simplest of the simple: No transforms, no paths, no ellipses, no clipping, no
# styling; it ONLY grabs `rect` and `circle` elements as obstacles. The main
# reason for supporting SVGs in the first place is just to make it easy to
# view/edit maps in other software, so universal SVG to map conversion is not
# a priority.
#
def load_svg_map(svg_filename):

	namespaces = {'svg': 'http://www.w3.org/2000/svg'}
	e = xml.etree.ElementTree.parse(svg_filename).getroot()

	obs_spec_list = []
	for atype in e.findall('.//svg:rect', namespaces):
		new_rect = dict()
		new_rect = {k: float(atype.get(k)) for k in {'x', 'y', 'width', 'height'}}
		obs_spec_list.append(_rect_to_poly_obs(new_rect))

	for atype in e.findall('.//svg:circle', namespaces):
		new_circle = dict()
		new_circle = {k: float(atype.get(k)) for k in {'r', 'y', 'width', 'height'}}
		new_circle['radius'] = new_circle['r']
		new_citcle['center'] = [new_citcle['x'], new_citcle['y']]
		obs_spec_list.append(_svg_circle_to_circle_obs(new_circle))

	obs_list = []
	for obs_spec in obs_spec_list:
		obs_list.append(_create_obs_from_spec(obs_spec))

	return obs_list


def load_json_map(json_filename):
	if json_filename == '':
		return []

	obs_list = []
	obs_spec_list = []
	with open(json_filename) as f:
		obs_spec_list = json.load(f)

	for obs_spec in obs_spec_list:
		obs_list.append(_create_obs_from_spec(obs_spec))

	return obs_list


## Convenience function that dispatches load_json_map or load_svg_map based on
## the file extension.
#
def load_map_file(map_filename):
	if re.match(r".*\.svg$", map_filename, re.IGNORECASE):
		return load_svg_map(map_filename)
	return load_json_map(map_filename)

