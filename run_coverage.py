#!/usr/bin/python

## @file run_default.py
#

import numpy	as np
import pickle
import base64

import Game
import GameSetupUtils

import DrawTool
from GridDataEnvironment import GridDataEnvironment
from GridDataRadar import GridDataRadar
from GeometricEnvironment import GeometricEnvironment
from GeometricRadar import GeometricRadar
from Robot import Robot, RobotStats, GpsSensor
from Target import Target
import Vector
import os
import sys
import binascii
import random

from BroadcastChannel import BroadcastChannel
from ReceiverSensor import ReceiverSensor
from Broadcaster import Broadcaster
from FazliCoverageAlgorithm import FazliCoverageAlgorithm
import GraphRoadmap
from EventMap import EventMap
from EventSensor import EventSensor
from Polygon import Polygon

from NavigationObjective import NavigationObjective

from NavigationAlgorithm import DynamicRrtNavigationAlgorithm
from NavigationAlgorithm import GlobalLocalNavigationAlgorithm
from NavigationAlgorithm import SamplingNavigationAlgorithm

cmdarg_parser = GameSetupUtils.create_default_cmdline_parser()
cmdarg_parser.set_defaults(
	robot_speed = 10,
	radar_range = 35,
	map_modifier_num = 0,
	map_name = 'Maps/coverage/csu_based.json'
);
cmdargs = cmdarg_parser.parse_args(sys.argv[1:])

np.random.seed(122)

env_size = (800, 600)

# Init environment
env = GeometricEnvironment(env_size[0], env_size[1], cmdargs.map_name, cmdargs=cmdargs)
start_point = Target((50, 550), radius=20, color=0x00FF00)
target = Target((760, 50), radius=20)

env.non_interactive_objects += [start_point, target]

# Init robots
radar = GeometricRadar(env, radius = cmdargs.radar_range);
initial_position = np.array(start_point.position);
robot_list = [];

# Init basics for coverage algorithm
bcast_channel = BroadcastChannel()
def obs_on_line(line):
	for obs in env.static_obstacles:
		if radar._obs_dist_along_line(obs, line) < float('inf'):
			return True
	return False

visibility_range = cmdargs.radar_range

with open('tgrsave.pickle', 'rb') as f:
	roadmap = pickle.load(f)
env.add_trigger('post_draw', roadmap.draw)

# Construct the graph
#roadmap = GraphRoadmap.GraphRoadmap()
#for i in range(1):
#	node = GraphRoadmap.GraphNode((np.random.randint(0,800), np.random.randint(0,600)))
#	for node2 in roadmap.get_nodes():
#		if not obs_on_line((node.location, node2.location)):
#			node.add_neighbor(node2, Vector.distance_between(node.location, node2.location))
#	roadmap.add_node(node)

boundary_points = set()
boundary_guards = set()
def cover_b_point(b_point):
	print(b_point)
	for node in boundary_guards:
		if Vector.distance_between(node.location, b_point) <= visibility_range and not obs_on_line((b_point, node.location)):
			boundary_guards.add(node)
			return
	for node in roadmap.get_nodes():
		if Vector.distance_between(node.location, b_point) <= visibility_range and not obs_on_line((b_point, node.location)):
			boundary_guards.add(node)
			return

	node = GraphRoadmap.GraphNode((np.random.randint(0, env.width), np.random.randint(0, env.height)))
	while not (Vector.distance_between(node.location, b_point) <= visibility_range and not obs_on_line((b_point, node.location))):
		print(node.location, b_point, Vector.distance_between(node.location, b_point), obs_on_line((b_point, node.location)))

		has_one = False
		while not has_one:
			node = GraphRoadmap.GraphNode((np.random.randint(0, env.width), np.random.randint(0, env.height)))
			any_tooclose = False
			if len(roadmap.get_nodes()) < 2:
				has_one = True
			for node2 in roadmap.get_nodes():
				if Vector.distance_between(node.location, node2.location) < 30:
					has_one = False
					break
				if Vector.distance_between(node.location, node2.location) < 200 and not obs_on_line((node.location, node2.location)):
					has_one = True
	for node2 in roadmap.get_nodes():
		if Vector.distance_between(node.location, node2.location) < 200 and not obs_on_line((node.location, node2.location)):
			node.add_neighbor(node2, Vector.distance_between(node.location, node2.location))

	roadmap.add_node(node)
	print(b_point)
	boundary_guards.add(node)

stepsize = 4

def cover_poly(poly):
	last_vert = poly.get_vertices()[0]
	for vert in poly.get_vertices()[1:]:
		boundary_vec = np.subtract(vert, last_vert)

		boundary_mag = Vector.magnitudeOf(boundary_vec)
		if boundary_mag < 1e-6:
			continue

		boundary_unitvec = boundary_vec / boundary_mag

		# Offset vector so the boundary points aren't
		# quite on the boundary (so self-collisions
		# aren't detected when checking visibility)
		offset_vec = np.array([boundary_unitvec[1], boundary_unitvec[0]]) * 1e-1
		if obs.polygon.contains_point(last_vert + boundary_unitvec*1e-6 + offset_vec):
			offset_vec *= -1

		for s in np.arange(1e-4, boundary_mag, stepsize):
			b_point = (last_vert + boundary_unitvec * s) + offset_vec
			boundary_points.add((b_point[0], b_point[1]))

		last_vert = vert

for obs in env.static_obstacles:
	if obs.shape != 4:
		continue
	cover_poly(obs.polygon)
#cover_poly(Polygon([[1, 1], [1, env.height-1], [env.width-1, env.height-1], [env.width-1, 1], [1,1]]))


for b_point in sorted(boundary_points):
	cover_b_point(b_point)

#with open('tgrsave.pickle', 'wb') as f:
	#pickle.dump(roadmap, f)

event_map = EventMap([[0, 0], [env.width, env.height]], boundary_points)
env.add_trigger('step', event_map.step)
env.add_trigger('post_draw', event_map.draw)


for i in range(10):
	initial_position = random.sample(roadmap.get_nodes(), 1)[0].location
	robot    = Robot(initial_position, cmdargs, path_color=(0xf3,0x91,0x12), name='fazlicov{}'.format(i));
	robot.put_sensor('radar', radar);
	robot.put_sensor('gps', GpsSensor(robot));
	robot.put_sensor('bcast', Broadcaster(robot, bcast_channel));
	robot.put_sensor('recv', ReceiverSensor(robot, bcast_channel));
	robot.put_sensor('roadmap', roadmap);
	robot.put_sensor('event', EventSensor(robot, event_map, env, detection_range=cmdargs.radar_range));
	robot.put_sensor('debug', {'name': robot.name});
	robot.set_nav_algo(FazliCoverageAlgorithm(robot.get_sensors(), cmdargs));
	robot_list.append(robot);

# Create the simulator
simulator = Game.Game(cmdargs, env)
simulator.add_robots(robot_list)

# Set up Pygame display
gameDisplay = GameSetupUtils.setup_pygame_window(simulator, env_size, window_title=cmdargs.window_title)

def construct_DrawTool():
	dtool = DrawTool.MultiDrawTool();
	dtool.dtools.append(DrawTool.PygameDrawTool(gameDisplay));
	#dtool.dtools.append(DrawTool.SvgDrawTool());
	#dtool = DrawTool.PygameDrawTool(gameDisplay);
	return dtool
simulator.set_dtool_constructor(construct_DrawTool)


# For SvgDrawTool, set a post-update hook to save the SVG to a file
#def save_current_frame(dtool):
	#with open('imdir/frame-{:07d}.svg'.format(simulator.get_step_num()), 'x') as f:
	#	f.write(dtool.dtools[-1].get_svg_xml())
#simulator.add_trigger('post_update_display', save_current_frame)


# Run the simulation
simulator.GameLoop()

