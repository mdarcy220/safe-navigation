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
import json

from NavigationObjective import NavigationObjective

from NavigationAlgorithm import SFMNavigationAlgorithm
from NavigationAlgorithm import DeepPredNavigationAlgorithm

cmdarg_parser = GameSetupUtils.create_default_cmdline_parser()
cmdarg_parser.add_argument('--net-load-filename',
		help='File to load DeepMoTIon network from',
		dest='net_load_filename',
		type=str,
		default='',
		action='store'
);
cmdarg_parser.add_argument('--ped-id-to-replace',
		help='The pedestrian ID to swap for the robot',
		dest='ped_id_to_replace',
		type=int,
		default=0,
		action='store'
);
cmdargs = cmdarg_parser.parse_args(sys.argv[1:])

with open('obsmat.json', 'r') as f:
	obsmat = json.load(f)
	start_human_obs = obsmat[str(cmdargs.ped_id_to_replace)][0]
	end_human_obs = obsmat[str(cmdargs.ped_id_to_replace)][-1]
	obsmat = None

env_size = (640, 480)

# Init environment
env = GeometricEnvironment(env_size[0], env_size[1], cmdargs.map_name, cmdargs=cmdargs)
start_point = Target((start_human_obs['pos_y'], start_human_obs['pos_x']), radius=0.75, color=0x00FF00)
target = Target((end_human_obs['pos_y'], end_human_obs['pos_x']), radius=0.75)
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
	robot.debug_info['ped_id'] = cmdargs.ped_id_to_replace;

	return robot

robot = make_default_robot('SFMRobot', (0, 0, 255))
robot.set_nav_algo(SFMNavigationAlgorithm(robot.get_sensors(), target, cmdargs));
robot_list.append(robot);

robot = make_default_robot('DeepMotionRobot', (0xf3,0x91,0x12))
robot.set_nav_algo(DeepPredNavigationAlgorithm(robot.get_sensors(), target, cmdargs, net_type='perl', net_load_file=cmdargs.net_load_filename));
robot_list.append(robot);


# Create the simulator
simulator = Game.Game(cmdargs, env)
simulator.add_robots(robot_list)

def construct_DrawTool():
	dtool = DrawTool.MultiDrawTool();
	dtool.dtools.append(DrawTool.SvgDrawTool(viewbox_rect=(-15, -3, 6.3292717, 11.292512), img_size=(1600, 900), svg_transform="rotate(90,-2.4945089,-5.5210241)"));
	return dtool
simulator.set_dtool_constructor(construct_DrawTool)


# For SvgDrawTool, set a post-update hook to save the SVG to a file
def save_current_frame(dtool):
	with open('imdir/frame-{:07d}.svg'.format(simulator.get_step_num()), 'x') as f:
		f.write(dtool.dtools[-1].get_svg_xml())
simulator.add_trigger('post_update_display', save_current_frame)


# Run the simulation
simulator.GameLoop()

