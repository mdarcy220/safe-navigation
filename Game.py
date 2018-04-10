#!/usr/bin/python

## @package Game
#

import pygame	as PG
import numpy	as np
import pickle
import base64

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

from enum import Enum

class GameState(Enum):
	INITIALIZING = 1
	RUNNING = 2
	PAUSED = 3
	QUITTING = 4
	FINISHED = 5


## Handles the main game loop
#
# This class manages the simulation. It handles the pygame window and
# events, and holds the game loop that controls the execution of the
# simulation.
#
class Game:
	## Constructor
	#
	# Initializes the game.
	#
	# @param cmdargs (object)
	# <br>	-- A command-line arguments storage object generated by
	# 	`argparse`.
	#
	# @param env (Environment object)
	# <br>	-- `Environment` object to use for simulation
	#
	# @param objective (Objective object)
	# <br>	-- `Objective` object to use for simulator end condition (e.g.,
	#          a `NavigationObjective` object)
	#
	# @param dtool_constructor (function)
	# <br>	-- Function to construct DrawTool for drawing. It is called
	#          with no arguments. The default is the base DrawTool
	#          constructor, which does not draw anything.
	#
	def __init__(self, cmdargs, env, objective, dtool_constructor=DrawTool.DrawTool):
		self._cmdargs = cmdargs
		self._env = env
		self._objective = objective
		self._dtool_constructor = dtool_constructor

		# Init trigger table
		self._triggers = dict()

		# Fires on every frame (even when paused)
		self._triggers['pre_frame'] = []

		# Fires before each step()
		self._triggers['pre_step'] = []

		# Fires after each step()
		self._triggers['post_step'] = []

		# Fires before each display update
		self._triggers['pre_update_display'] = []

		# Fires after each display update
		self._triggers['post_update_display'] = []


		if cmdargs.prng_start_state is not None:
			np.random.set_state(pickle.loads(base64.b64decode(str.encode(cmdargs.prng_start_state))));

		self._initial_random_state = base64.b64encode(pickle.dumps(np.random.get_state())).decode();

		self._display_every_frame = cmdargs.display_every_frame

		self._unique_id = cmdargs.unique_id
		if cmdargs.unique_id == '':
			self._unique_id = self._generate_unique_id()


		self._robot_list = []

		self._cur_state = GameState.INITIALIZING
		self._doing_step = False

		self._step_num = 0;


	def set_dtool_constructor(self, dtool_constructor):
		self._dtool_constructor = dtool_constructor


	def get_step_num(self):
		return self._step_num


	def add_robots(self, robot_list):
		self._robot_list += robot_list


	def remove_robot_by_name(self, robot_name):
		for robot in robot_list:
			if robot.name == robot_name:
				robot_list.remove(robot)
				return

	def add_trigger(self, trigger_type, trigger):
		if trigger_type not in self._triggers:
			raise KeyError('No such trigger type in trigger table: {}'.format(trigger_type))

		self._triggers[trigger_type].append(trigger)


	def _generate_unique_id(self):
		return datetime.datetime.now().isoformat() + '_' + binascii.hexlify(bytearray(random.getrandbits(8) for _ in range(4))).decode()



	def _run_triggers_for(self, trigger_type, *trigger_args, **trigger_kwargs):
		if trigger_type not in self._triggers:
			return

		for trigger in self._triggers[trigger_type]:
			trigger(*trigger_args, **trigger_kwargs)


	## Draws the game image
	#
	# It should be noted that this method does not call
	# `pygame.display.update()`, so the drawn screen is not yet
	# visible to the user. This is done for performance reasons, as
	# rendering the image to the screen is somewhat expensive and does
	# not always need to be done.
	#
	def update_game_image(self):
		dtool = self._dtool_constructor()

		self._run_triggers_for('pre_update_display', dtool)

		self._env.update_display(dtool);

		if self._display_every_frame:
			for robot in self._robot_list:
				robot.draw(dtool)

		self._run_triggers_for('post_update_display', dtool)


	def step(self):
		self._run_triggers_for('pre_step')

		self._doing_step = False

		allBotsAtTarget = True
		anyRobotQuit = False

		# Process robot actions
		for robot in self._robot_list:
			if robot.has_given_up():
				anyRobotQuit = True;
				break;
			if not (self._objective.test(robot)):
				allBotsAtTarget = False
				robot.NextStep(self._env)

		# Step the environment
		self._env.next_step()

		# Increment the step num
		self._step_num += 1

		# Quit if necessary
		if anyRobotQuit or allBotsAtTarget or self._cmdargs.max_steps <= self._step_num:
			self.quit()
			return

		# Draw everything
		if self._display_every_frame:
			self.update_game_image()

		self._run_triggers_for('post_step')


	def pause(self):
		if self._cur_state not in {GameState.PAUSED, GameState.RUNNING}:
			raise Exception('Cannot pause from this GameState: {}'.format(self._cur_state))

		self._cur_state = GameState.PAUSED

	def quit(self):
		if self._cur_state == GameState.FINISHED:
			return

		self._cur_state = GameState.QUITTING


	## The game loop used for normal execution.
	# 
	# Broadly, the game loop consists of the following steps:
	# <br>	1. Check for any user input events and process them.
	# <br>	2. Have each robot do a game step, allowing them to
	# 	process their next action and move.
	# <br>	3. Have the environment do a game step to update dynamic
	# 	obstacles.
	# <br>	4. Check exit conditions (have all robots reached the
	# 	goal?).
	# <br>	5. Create and display the game image.
	#
	def standard_game_loop(self):
		clock = PG.time.Clock()
		self._step_num = 0

		self._cur_state = GameState.RUNNING

		while self._cur_state != GameState.QUITTING:

			self._run_triggers_for('pre_frame')

			if self._cur_state == GameState.PAUSED:
				clock.tick(10);
				continue

			self.step()

			# Tick the clock
			clock.tick(self._cmdargs.max_fps)

		self._cur_state = GameState.FINISHED


	## Creates a result summary in CSV form
	#
	# @returns (string)
	# <br>	Format: field1,field2,...,fieldn
	# <br>	-- A CSV-formatted collection of fields representing
	# 	information about the run for the given robot.
	#
	def make_csv_robot_line(self, robot):

		# Quick helper function for strings
		def sanitize_str_obj(obj):
			return '"' + str(obj).replace("\"", "\"\"") + '"'

		csv_fields = []

		csv_fields.append(sanitize_str_obj(self._unique_id))
		csv_fields.append(sanitize_str_obj(robot.name))

		csv_fields.append(str(self._cmdargs.speedmode))
		csv_fields.append(str(self._cmdargs.radar_resolution))
		csv_fields.append(str(self._cmdargs.radar_noise_level))
		csv_fields.append(str(self._cmdargs.robot_movement_momentum))

		csv_fields.append(sanitize_str_obj(self._cmdargs.map_name))

		csv_fields.append(str(self._cmdargs.map_modifier_num))
		csv_fields.append(str(self._cmdargs.use_integer_robot_location))

		csv_fields.append(str(robot.get_stats().num_dynamic_collisions))
		csv_fields.append(str(robot.get_stats().num_static_collisions))

		csv_fields.append(str(robot.stepNum if self._objective.test(robot) else ""))

		csv_fields.append(str(0 if self._objective.test(robot) else 1))

		csv_fields.append(str(robot.get_stats().avg_decision_time()))

		extra_data = dict()
		extra_data['min_proximities'] = robot.debug_info['min_proximities']
		extra_data['trajectory'] = [loc.tolist() for loc in robot._visited_points]
		extra_data['ped_id'] = robot.debug_info['ped_id']
		if self._cmdargs.output_prng_state:
			extra_data['prng_state'] = str(self._initial_random_state)

		extra_data_str = sanitize_str_obj(json.dumps(extra_data))

		csv_fields.append(extra_data_str)

		return ','.join(csv_fields)


	## Runs the game
	#
	# This method dispatches the appropriate game loop based on the
	# command line arguments, and then prints the results as CSV when
	# finished.
	#
	def GameLoop(self):
		time.sleep(self._cmdargs.start_delay)

		self.standard_game_loop()

		for robot in self._robot_list:
			sys.stdout.write(self.make_csv_robot_line(robot) + '\n');

		#PG.quit()
		return 0

