#!/usr/bin/python

## @package Game
#

import pygame	as PG
import numpy	as np
import pickle
import base64

import DrawTool
from Environment import Environment
from Robot import Robot, RobotStats, GpsSensor
from Radar import Radar
from Target import Target
import time
import Vector
from MDPAdapterSensor import MDPAdapterSensor
import os

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
	def __init__(self, cmdargs):
		self._cmdargs = cmdargs

		if cmdargs.prng_start_state is not None:
			np.random.set_state(pickle.loads(base64.b64decode(str.encode(cmdargs.prng_start_state))));

		self._initial_random_state = base64.b64encode(pickle.dumps(np.random.get_state())).decode();

		self._display_every_frame = True
		if cmdargs.batch_mode and not cmdargs.display_every_frame:
			self._display_every_frame = False

		self._display_robot_perspective = cmdargs.display_robot_perspective;
		self._mask_layer = None;

		self._is_paused = False
		self._doing_step = False

		self._step_num = 0;

		# Initialize the game display to 800x600
		PG.init()
		self._gameDisplay = PG.display.set_mode((800, 600))

		# Init environment
		self._env = Environment(self._gameDisplay.get_width(), self._gameDisplay.get_height(), cmdargs.map_name, cmdargs=cmdargs)
		self._start_point = Target((50,550), color=0x00FF00)
		self._target = Target((760, 50))

		# Init robots
		radar = Radar(self._env, radius = cmdargs.radar_range, resolution = cmdargs.radar_resolution);
		initial_position = np.array(self._start_point.position);
		self._robot_list    = [];

		self._normal_robot  = Robot(initial_position, cmdargs, path_color=(0,0,255),   name="NormalRobot");
		self._normal_robot.put_sensor('radar', radar);
		self._normal_robot.put_sensor('gps', GpsSensor(self._normal_robot));
		self._normal_robot.put_sensor('mdp', MDPAdapterSensor(self._env, self._start_point.position, self._target.position, unique_id=os.path.basename(cmdargs.map_name)));
		self._normal_robot.put_sensor('debug', {'name': 'normal'});
		#self._normal_robot.set_nav_algo(DeepIRLAlgorithm(self._normal_robot.get_sensors(), self._target, cmdargs));
		self._normal_robot.set_nav_algo(DeepQIRLAlgorithm(self._normal_robot.get_sensors(), self._target, cmdargs));
		#self._normal_robot.set_nav_algo(InverseRLNavigationAlgorithm(self._normal_robot.get_sensors(), self._target, cmdargs));
		#self._normal_robot.set_nav_algo(DeepQNavigationAlgorithm(self._normal_robot.get_sensors(), self._target, cmdargs));
		#self._normal_robot.set_nav_algo(ValueIterationNavigationAlgorithm(self._normal_robot.get_sensors(), self._target, cmdargs));
		#self._normal_robot.set_nav_algo(DynamicRrtNavigationAlgorithm(self._normal_robot.get_sensors(), self._target, cmdargs));
		self._robot_list.append(self._normal_robot);


		self._safe_robot    = Robot(initial_position, cmdargs, path_color=(0xf3,0x91,0x12), name="SafeRobot");
		self._safe_robot.put_sensor('radar', radar);
		self._safe_robot.put_sensor('gps', GpsSensor(self._safe_robot));
		self._safe_robot.put_sensor('debug', {'name': 'safe'});
		self._safe_robot.set_nav_algo(GlobalLocalNavigationAlgorithm(self._safe_robot.get_sensors(), self._target, cmdargs, local_algo_init = SamplingNavigationAlgorithm));
		#self._robot_list.append(self._safe_robot);

		# Set window title
		PG.display.set_caption(cmdargs.window_title)


	## Handles pygame events.
	#
	# Processes any received keypresses or mouse clicks.
	#
	def handle_pygame_events(self):
		for event in PG.event.get():
			if event.type == PG.QUIT:
				return 1
			elif event.type == PG.KEYDOWN:
				if event.key == PG.K_u:
					self.update_game_image()
					self.render_game_image()
				elif event.key == PG.K_q:
					return 1
				elif event.key == PG.K_e:
					self._display_every_frame = (not self._display_every_frame)
				elif event.key == PG.K_p:
					self._is_paused = not self._is_paused;
				elif event.key == PG.K_s:
					self._doing_step = True
		return 0


	## Draws the game image
	#
	# It should be noted that this method does not call
	# `pygame.display.update()`, so the drawn screen is not yet
	# visible to the user. This is done for performance reasons, as
	# rendering the image to the screen is somewhat expensive and does
	# not always need to be done.
	#
	def update_game_image(self):
		#dtool = DrawTool.MultiDrawTool();
		#dtool.dtools.append(DrawTool.PygameDrawTool(self._gameDisplay));
		#dtool.dtools.append(DrawTool.SvgDrawTool());
		dtool = DrawTool.PygameDrawTool(self._gameDisplay);

		self._env.update_display(dtool);
		self._env.update_grid_data_from_display(self._gameDisplay)

		if self._display_every_frame:
			if self._display_robot_perspective:
				self._mask_layer = PG.Surface(self._gameDisplay.get_size(), flags = PG.SRCALPHA) if self._mask_layer is None else self._mask_layer;
				self._mask_layer.fill(0xFF444444);
				for robot in self._robot_list:
					robot.draw_radar_mask(self._mask_layer);
				self._gameDisplay.blit(self._mask_layer, (0,0));

			self._start_point.draw(dtool)
			self._target.draw(dtool)
			for robot in self._robot_list:
				robot.draw(dtool)

		#dtool.dtools[1]._elems.insert(0, '<image x="0" y="0" width="800" height="600" xlink:href="../{}" />'.format(self._cmdargs.map_name))
		#with open('imdir/frame-{:05d}.svg'.format(self._step_num), 'x') as f:
		#	f.write(dtool.dtools[1].get_svg_xml())


	## Renders the stored game image onto the screen, to make it
	# visible to the user.
	#
	def render_game_image(self):
		PG.display.update()


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
		while True:
			# Handle events
			event_status = self.handle_pygame_events()
			if event_status == 1:
				return

			if self._is_paused and not self._doing_step:
				clock.tick(10);
				continue
			self._doing_step = False

			allBotsAtTarget = True
			anyRobotQuit = False

			# Process robot actions
			for robot in self._robot_list:
				if robot.has_given_up():
					anyRobotQuit = True;
					break;
				if not (self.check_robot_at_target(robot)):
					allBotsAtTarget = False
					robot.NextStep(self._env.grid_data)

			# Step the environment
			self._env.next_step()

			shouldEndSimulation = (anyRobotQuit or allBotsAtTarget);

			if (self._cmdargs.batch_mode) and (shouldEndSimulation):
				return
			if not shouldEndSimulation:
				self._step_num += 1
			if self._cmdargs.max_steps <= self._step_num:
				return

			# Draw everything
			if self._display_every_frame:
				self.update_game_image()
				self.render_game_image()

			# Tick the clock
			clock.tick(self._cmdargs.max_fps)


	## Creates a result summary in CSV form
	#
	# @returns (string)
	# <br>	Format: field1,field2,...,fieldn
	# <br>	-- A CSV-formatted collection of fields representing
	# 	information about the run.
	#
	def make_csv_line(self):
		output_csv = str(self._cmdargs.speedmode) + ','
		output_csv += str(self._cmdargs.radar_resolution) +','
		output_csv += str(self._cmdargs.radar_noise_level) +','
		output_csv += str(self._cmdargs.robot_movement_momentum) +','
		output_csv += str(self._cmdargs.robot_memory_sigma) +','
		output_csv += str(self._cmdargs.robot_memory_decay) +','
		output_csv += str(self._cmdargs.robot_memory_size) +','
		output_csv += str(self._cmdargs.map_name) +','
		output_csv += str(self._cmdargs.map_modifier_num) +','
		output_csv += str(self._cmdargs.target_distribution_type) +','
		output_csv += str(self._cmdargs.use_integer_robot_location) +','

		normal_robot_stats = self._normal_robot.get_stats()
		safe_robot_stats = self._safe_robot.get_stats()

		output_csv += str(normal_robot_stats.num_dynamic_collisions) + ","
		output_csv += str(safe_robot_stats.num_dynamic_collisions) + ","

		output_csv += str(normal_robot_stats.num_static_collisions) + ","
		output_csv += str(safe_robot_stats.num_static_collisions) + ","

		output_csv += str(self._normal_robot.stepNum if self.check_robot_at_target(self._normal_robot) else "") + ","
		output_csv += str(self._safe_robot.stepNum if self.check_robot_at_target(self._safe_robot) else "") + ","

		output_csv += str(0 if self.check_robot_at_target(self._normal_robot) else 1) + ","
		output_csv += str(0 if self.check_robot_at_target(self._safe_robot) else 1) + ","
		if self._cmdargs.output_prng_state:
			output_csv += str(self._initial_random_state)
		else:
			output_csv += ","

		output_csv += str(normal_robot_stats.avg_decision_time()) + ","
		output_csv += str(safe_robot_stats.avg_decision_time())


		return output_csv


	## Checks if the robot is at the target
	#
	# @returns (boolean)
	# <br>	-- `True` if the robot is in the target zone, `False`
	# 	otherwise.
	#
	def check_robot_at_target(self, robot):
		return (Vector.distance_between(robot.location, self._target.position) < 20);


	## Runs the game
	#
	# This method dispatches the appropriate game loop based on the
	# command line arguments, and then prints the results as CSV when
	# finished.
	#
	def GameLoop(self):
		time.sleep(self._cmdargs.start_delay)

		self.standard_game_loop()

		print(self.make_csv_line());

		PG.quit()
		return 0
