#!/usr/bin/python

## @file run_default.py
#

import numpy	as np
import pickle
import base64

import Game
import GameSetupUtils

import DrawTool
from GeometricEnvironment import GeometricEnvironment
from GeometricRadar import GeometricRadar
from RadarSensor import RadarSensor
from Robot import Robot, RobotStats, GpsSensor
from Target import Target
import Vector
import os
import sys
import binascii
import random
import json

import MovementPattern
from DynamicObstacles import DynamicObstacle

from NavigationObjective import NavigationObjective

import NavigationAlgorithm.util

cmdarg_parser = GameSetupUtils.create_default_cmdline_parser()
cmdargs = cmdarg_parser.parse_args(sys.argv[1:])

params = GameSetupUtils.load_params(cmdargs.params_file)

env_size = (800, 600)

# Init environment
env = GeometricEnvironment(env_size[0], env_size[1], cmdargs.map_name, cmdargs=cmdargs)


# Init robots
radar = GeometricRadar(env, radius = cmdargs.radar_range);
robot_list = [];

def make_default_robot(robot_name, path_color):
	start_point = Target((50, 550), radius=20, color=0x00FF00)
	initial_position = np.array(start_point.position);
	target = Target((750, 70), radius=20)
	objective = NavigationObjective(target, env)

	env.non_interactive_objects += [start_point, target]

	robot = Robot(initial_position, cmdargs, env, path_color=path_color, name=robot_name, objective=objective);
	robot.put_sensor('radar', RadarSensor(env, robot, [], radar));
	robot.put_sensor('gps', GpsSensor(robot));
	if robot_name in params['robots']:
		robot.put_sensor('params', params['robots'][robot_name]);
	else:
		robot.put_sensor('params', {});

	return robot, target

for robot_name in params['robots']:
	robot, target = make_default_robot(robot_name, (0, 0, 255))
	robot.set_nav_algo(NavigationAlgorithm.util.algo_from_config(params['robots'][robot_name]['algorithm'], robot.get_sensors(), target, cmdargs));
	robot_list.append(robot);

# Create the simulator
simulator = Game.Game(cmdargs, env, output_type='json')
simulator.add_robots(robot_list)

# Set up Pygame display
#gameDisplay = GameSetupUtils.setup_pygame_window(simulator, env_size, window_title=cmdargs.window_title)

def construct_DrawTool():
	dtool = DrawTool.MultiDrawTool();
	#dtool.dtools.append(DrawTool.PygameDrawTool(gameDisplay));
	#dtool.dtools.append(DrawTool.SvgDrawTool(viewbox_rect=(0, 0, 800, 600), img_size=(1600, 1200)));
	return dtool
simulator.set_dtool_constructor(construct_DrawTool)


# For SvgDrawTool, set a post-update hook to save the SVG to a file
def save_current_frame(dtool):
	with open('imdir/frame-{:07d}.svg'.format(simulator.get_step_num()), 'x') as f:
		f.write(dtool.dtools[-1].get_svg_xml())
#simulator.add_trigger('post_update_display', save_current_frame)


# Run the simulation
simulator.GameLoop()

