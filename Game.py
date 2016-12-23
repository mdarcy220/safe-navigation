import pygame	as PG
import numpy	as np

from  Environment import Environment
from  Robot import Robot, RobotStats
from  Target import Target
import time

class Game:
	def __init__(self, cmdargs):
		PG.init()
		self.cmdargs	   = cmdargs

		self.display_every_frame = True
		if cmdargs.batch_mode and not cmdargs.display_every_frame:
			self.display_every_frame = False

		self.Display_Width = 800
		self.Display_Height= 600
		self.gameDisplay = PG.display.set_mode((800, 600))
		self.env = Environment(800, self.gameDisplay.get_height(), cmdargs.map_name, cmdargs=cmdargs)
		self.target = Target((740,50))

		self.normal_robot  = Robot (self.gameDisplay, self.target, (50, 550), speed=cmdargs.robot_speed, cmdargs=cmdargs, using_safe_mode =False, name="NormalRobot")
		self.safe_robot    = Robot (self.gameDisplay, self.target, (50, 550), speed=cmdargs.robot_speed, cmdargs=cmdargs, using_safe_mode = True, name="SafeRobot")
		self.robot_list    = []
		self.robot_list.append(self.normal_robot)
		self.robot_list.append(self.safe_robot)

		PG.display.set_caption(cmdargs.window_title)


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
					self.display_every_frame = (not self.display_every_frame)
		return 0


	def update_game_image(self):
		self.target.draw(self.gameDisplay)
		for robot in self.robot_list:
			robot.draw(self.gameDisplay)


	def render_game_image(self):
		PG.display.update()


	def standard_game_loop(self):
		clock = PG.time.Clock()
		step_num = 0
		while True:
			# Handle events
			event_status = self.handle_pygame_events()
			if event_status == 1:
				return

			# Step the environment
			self.env.Nextstep(self.gameDisplay)
		
			allBotsAtTarget = True

			# Process robot actions
			for robot in self.robot_list:
				if not (robot.distanceToTarget() < 20):
					allBotsAtTarget = False
					robot.NextStep(self.env.grid_data)

			if (self.cmdargs.batch_mode) and (allBotsAtTarget):
				return
			if not allBotsAtTarget:
				step_num += 1
			if self.cmdargs.max_steps <= step_num:
				return

			# Draw everything
			if self.display_every_frame:
				self.update_game_image()
				self.render_game_image()

			# Tick the clock
			clock.tick(1000)
		
	def fast_computing_game_loop(self):
		safe_robot_at_target = False
		normal_robot_at_target = False 
		allRobotsAtTarget = False
		self.env.Nextstep(self.gameDisplay)
		step_num = 0
		while (not allRobotsAtTarget):
			allBotsAtTarget = True

			# Process robot actions
			for robot in self.robot_list:
				if not (robot.distanceToTarget() < 20):
					allBotsAtTarget = False
					robot.NextStep(self.env.grid_data)
			step_num += 1
			if self.cmdargs.max_steps <= step_num:
				return


	def make_csv_line(self):
		output_csv = str(self.cmdargs.speedmode) + ','
		output_csv += str(self.cmdargs.radar_resolution) +','
		output_csv += str(self.cmdargs.radar_noise_level) +','
		output_csv += str(self.cmdargs.robot_movement_momentum) +','
		output_csv += str(self.cmdargs.robot_memory_sigma) +','
		output_csv += str(self.cmdargs.robot_memory_decay) +','
		output_csv += str(self.cmdargs.robot_memory_size) +','
		output_csv += str(self.cmdargs.map_name) +','
		output_csv += str(self.cmdargs.map_modifier_num) +','
		output_csv += str(self.cmdargs.target_distribution_type) +','
		output_csv += str(self.cmdargs.use_integer_robot_location) +','

		normal_robot_stats = self.normal_robot.get_stats()
		safe_robot_stats = self.safe_robot.get_stats()

		output_csv += str(normal_robot_stats.num_glitches) + ","
		output_csv += str(safe_robot_stats.num_glitches) + ","

		output_csv += str(self.normal_robot.stepNum if self.check_robot_at_target(self.normal_robot) else "") + ","
		output_csv += str(self.safe_robot.stepNum if self.check_robot_at_target(self.safe_robot) else "") + ","

		output_csv += str(0 if self.check_robot_at_target(self.normal_robot) else 1) + ","
		output_csv += str(0 if self.check_robot_at_target(self.safe_robot) else 1) 


		return output_csv


	def check_robot_at_target(self, robot):
		return robot.distanceToTarget() < 20


	def GameLoop(self):
		if self.cmdargs.fast_computing:
			self.fast_computing_game_loop()
		else:
			self.standard_game_loop()

		print(self.make_csv_line());

		PG.quit()
		return 0
