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

from NavigationObjective import NavigationObjective

from NavigationAlgorithm import DynamicRrtNavigationAlgorithm
from NavigationAlgorithm import GlobalLocalNavigationAlgorithm
from NavigationAlgorithm import SamplingNavigationAlgorithm

cmdarg_parser = GameSetupUtils.create_default_cmdline_parser()
cmdargs = cmdarg_parser.parse_args(sys.argv[1:])

env_size = (800, 600)

# Init environment
env = GeometricEnvironment(env_size[0], env_size[1], cmdargs.map_name, cmdargs=cmdargs)
start_point = Target((50, 550), radius=20, color=0x00FF00)
target = Target((760, 50), radius=20)
objective = NavigationObjective(target, env)

env.non_interactive_objects += [start_point, target]

# Init robots
radar = GeometricRadar(env, radius = cmdargs.radar_range);
initial_position = np.array(start_point.position);
robot_list = [];

def make_default_robot(robot_name, path_color):
	robot = Robot(initial_position, cmdargs, path_color=path_color, name=robot_name, objective=objective);
	robot.put_sensor('radar', radar);
	robot.put_sensor('gps', GpsSensor(robot));
	robot.put_sensor('params', {'name': robot_name});

	return robot

robot = make_default_robot('NormalRobot', (0, 0, 255))
robot.set_nav_algo(DynamicRrtNavigationAlgorithm(robot.get_sensors(), target, cmdargs));
robot_list.append(robot);

robot = make_default_robot('SafeRobot', (0xf3,0x91,0x12))
robot.set_nav_algo(GlobalLocalNavigationAlgorithm(robot.get_sensors(), target, cmdargs, local_algo_init = SamplingNavigationAlgorithm));
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

