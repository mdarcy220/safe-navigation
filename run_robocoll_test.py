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

def make_default_robot(robot_name, path_color, debug_name=None):
	if debug_name is None:
		debug_name = robot_name

	start_point = Target((50, np.random.randint(450, 550)), radius=20, color=0x00FF00)
	initial_position = np.array(start_point.position);

	robot = Robot(initial_position, cmdargs, path_color=path_color, name=robot_name);
	robot.put_sensor('radar', RadarSensor(env, robot, [], radar));
	robot.put_sensor('gps', GpsSensor(robot));
	robot.put_sensor('debug', {'name': debug_name});

	robot_obstacle = DynamicObstacle(MovementPattern.RobotBodyMovement(robot))
	robot_obstacle.shape = 1
	robot_obstacle.radius = 10
	robot_obstacle.fillcolor = (0xcc, 0x88, 0x44)
	robot.set_obstacle(robot_obstacle)

	return robot

robot = make_default_robot('ProbLPRobot', (0, 0, 255), 'problp')
robot.set_nav_algo(GlobalLocalNavigationAlgorithm(robot.get_sensors(), target, cmdargs, local_algo_init = SamplingNavigationAlgorithm));
robot_list.append(robot);

robot = make_default_robot('ProbLPRobot2', (0, 0, 255), 'problp2')
robot.set_nav_algo(GlobalLocalNavigationAlgorithm(robot.get_sensors(), target, cmdargs, local_algo_init = SamplingNavigationAlgorithm));
robot_list.append(robot);

robot = make_default_robot('ProbLPRobot3', (0, 0, 255), 'problp3')
robot.set_nav_algo(GlobalLocalNavigationAlgorithm(robot.get_sensors(), target, cmdargs, local_algo_init = SamplingNavigationAlgorithm));
robot_list.append(robot);

for robot in robot_list:
	robot.get_sensors()['radar'].set_other_robots([robot2 for robot2 in robot_list if robot2 != robot])

# Create the simulator
simulator = Game.Game(cmdargs, env, objective)
simulator.add_robots(robot_list)

# Set up Pygame display
gameDisplay = GameSetupUtils.setup_pygame_window(simulator, env_size, window_title=cmdargs.window_title)

def construct_DrawTool():
	dtool = DrawTool.MultiDrawTool();
	dtool.dtools.append(DrawTool.PygameDrawTool(gameDisplay));
	dtool.dtools.append(DrawTool.SvgDrawTool(viewbox_rect=(0, 0, 800, 600), img_size=(1600, 1200)));
	return dtool
simulator.set_dtool_constructor(construct_DrawTool)


# For SvgDrawTool, set a post-update hook to save the SVG to a file
def save_current_frame(dtool):
	with open('imdir/frame-{:07d}.svg'.format(simulator.get_step_num()), 'x') as f:
		f.write(dtool.dtools[-1].get_svg_xml())
simulator.add_trigger('post_update_display', save_current_frame)


# Run the simulation
simulator.GameLoop()

