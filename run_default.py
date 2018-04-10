#!/usr/bin/python

## @file run.py
#

import pygame	as PG
import numpy	as np
import pickle
import base64

import Game

import DrawTool
from GridDataEnvironment import GridDataEnvironment
from GridDataRadar import GridDataRadar
from GeometricEnvironment import GeometricEnvironment
from GeometricRadar import GeometricRadar
from Robot import Robot, RobotStats, GpsSensor
from Target import Target
import time
import Vector
from MDPAdapterSensor import MDPAdapterSensor
import os
import sys
import json
import datetime
import binascii
import random

from NavigationObjective import NavigationObjective

from NavigationAlgorithm import DeepQNavigationAlgorithm
from NavigationAlgorithm import DynamicRrtNavigationAlgorithm
from NavigationAlgorithm import FuzzyNavigationAlgorithm
from NavigationAlgorithm import GlobalLocalNavigationAlgorithm
from NavigationAlgorithm import IntegratedEnvNavigationAlgorithm
from NavigationAlgorithm import LinearNavigationAlgorithm
from NavigationAlgorithm import ManualMouseNavigationAlgorithm
from NavigationAlgorithm import MpRrtNavigationAlgorithm
from NavigationAlgorithm import MultiLevelNavigationAlgorithm
from NavigationAlgorithm import SamplingNavigationAlgorithm
from NavigationAlgorithm import ValueIterationNavigationAlgorithm
from NavigationAlgorithm import InverseRLNavigationAlgorithm
from NavigationAlgorithm import DeepIRLAlgorithm
from NavigationAlgorithm import DeepQIRLAlgorithm
from NavigationAlgorithm import DeepPredNavigationAlgorithm
from NavigationAlgorithm import SFMNavigationAlgorithm

from Main import get_cmdline_args

cmdargs = get_cmdline_args()

#env_size = (800, 600)
env_size = (640, 480)


# Get start and end points
with open('obsmat.json', 'r') as f:
	obsmat = json.load(f)
	start_human_obs = obsmat[str(cmdargs.ped_id_to_replace)][0]
	end_human_obs = obsmat[str(cmdargs.ped_id_to_replace)][-1]
	obsmat = None

# Init environment
env = GeometricEnvironment(640, 480, cmdargs.map_name, cmdargs=cmdargs)
start_point = Target((start_human_obs['pos_y'], start_human_obs['pos_x']), color=0x00FF00)
target = Target((end_human_obs['pos_y'], end_human_obs['pos_x']))
objective = NavigationObjective(target, env)

env.non_interactive_objects += [start_point, target]

# Init robots
radar = GeometricRadar(env, radius = cmdargs.radar_range);
initial_position = np.array(start_point.position);
robot_list = [];

robot = Robot(initial_position, cmdargs, path_color=(0,0,255), name="NormalRobot");
robot.put_sensor('radar', radar);
robot.put_sensor('gps', GpsSensor(robot));
robot.put_sensor('debug', {'name': 'normal'});
robot.set_nav_algo(SFMNavigationAlgorithm(robot.get_sensors(), target, cmdargs));
robot_list.append(robot);

robot = Robot(initial_position, cmdargs, path_color=(0xf3,0x91,0x12), name="SafeRobot");
robot.put_sensor('radar', radar);
robot.put_sensor('gps', GpsSensor(robot));
robot.put_sensor('debug', {'name': 'safe'});
robot.set_nav_algo(DeepPredNavigationAlgorithm(robot.get_sensors(), target, cmdargs, net_type='perl'));
robot_list.append(robot);



# Create the simulator
simulator = Game.Game(cmdargs, env, objective)
simulator.add_robots(robot_list)


# If using PyGame for display, the following may be desirable
#
#PG.init()
#gameDisplay = PG.display.set_mode(env_size)
#PG.display.set_caption(cmdargs.window_title)
#def render_pygame(*args):
#	PG.display.update()
#simulator.add_trigger('post_update_display', render_pygame)
#
### Handles pygame events.
##
## Processes any received keypresses or mouse clicks.
##
#def handle_pygame_events():
#	for event in PG.event.get():
#		if event.type == PG.QUIT:
#			simulator.quit()
#		elif event.type == PG.KEYDOWN:
#			if event.key == PG.K_u:
#				self.update_game_image()
#			elif event.key == PG.K_q:
#				simulator.quit()
#			elif event.key == PG.K_e:
#				simulator_display_every_frame = (not simulator._display_every_frame)
#			elif event.key == PG.K_p:
#				simulator.pause()
#			elif event.key == PG.K_s:
#				simulator.step()
#simulator.add_trigger('pre_frame', handle_pygame_events)


def construct_DrawTool():
	dtool = DrawTool.MultiDrawTool();
	#dtool.dtools.append(DrawTool.PygameDrawTool(gameDisplay));
	dtool.dtools.append(DrawTool.SvgDrawTool());
	#dtool = DrawTool.PygameDrawTool(gameDisplay);
	return dtool
simulator.set_dtool_constructor(construct_DrawTool)


# For SvgDrawTool, set a post-update hook to save the SVG to a file
def save_current_frame(dtool):
	dtool.dtools[-1]._elems.insert(0, '<image x="0" y="0" width="800" height="600" xlink:href="../{}" />'.format(cmdargs.map_name))
	with open('imdir/frame-{:07d}.svg'.format(simulator.get_step_num()), 'x') as f:
		f.write(dtool.dtools[-1].get_svg_xml())
simulator.add_trigger('post_update_display', save_current_frame)


# Run the simulation
simulator.GameLoop()

