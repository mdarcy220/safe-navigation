import numpy  as np
import pygame as PG
import math
from Radar import Radar
import Distributions
import Vector
import matplotlib.pyplot as plt
import time
import scipy.signal


class RobotStats:
	def __init__(self):
		self.num_glitches = 0
		self.num_steps = 0


class Robot:
	def __init__(self, screen, target, initial_position, speed = 6, cmdargs=None, using_safe_mode = False, name=""):
		self.cmdargs		= cmdargs
		self.target		= target
		self.location		= initial_position
		self.speed		= speed
		self.stats		= RobotStats()
		self.name		= name
		self.using_safe_mode	= using_safe_mode
		self.drawcoll = 0

		self.normal_speed		= speed
		self.max_speed			= 10
		if (self.cmdargs.speedmode == 5):
			self.normal_speed = 10
		if (not self.using_safe_mode):
			self.normal_speed = 10
		self.NumberofGlitches		= 0
		
		self.speed = self.normal_speed

		self.speed_adjust_pdf = Distributions.Gaussian()
		self.speed_adjust_pdf.degree_resolution = 2
		

		radar_resolution = cmdargs.radar_resolution

		self.radar	= Radar(screen, resolution=radar_resolution)
		self.PathList	= []
		self.PDF	= Distributions.Gaussian()
		if (self.cmdargs.target_distribution_type == 'rectangular'):
			self.PDF = Distributions.Rectangular()
		# Function that selects an angle based on a distribution
		self.pdf_angle_selector = self.center_of_gravity_pdfselector
		# Function that combines pdfs
		self.combine_pdfs	= np.minimum

		# Memory of visited points
		self.visited_points	= []
		# Stores the memory and movement vectors (for drawing in debug mode)
		self.last_mbv		= np.array([0, 0])
		self.last_mmv		= np.array([0, 0])
		self.movement_momentum	= 0
		self.memory_sigma 	= 25
		self.memory_decay 	= 1
		self.memory_size  	= 500
		if (not (cmdargs is None)):
			self.movement_momentum = cmdargs.robot_movement_momentum
			self.memory_sigma = cmdargs.robot_memory_sigma
			self.memory_decay = cmdargs.robot_memory_decay
			self.memory_size  = cmdargs.robot_memory_size

		# Number of times NextStep was called
		self.stepNum			= 0

		self.last_glitch_step	= -1

		# Used to allow real-time plotting
		if (not (cmdargs is None)) and (cmdargs.show_real_time_plot):
			plt.ion()
			plt.show()

	def get_stats(self):
		return self.stats


	def SetSpeed(self, speed):
		self.speed = speed


	def gaussian_noise(self, noise_level, size):
		noise_pdf = np.random.normal(0, noise_level, size)
		return noise_pdf


	def NextStep(self, grid_data):
		self.stepNum += 1
		self.stats.num_steps += 1

		targetpoint_pdf = self.PDF.get_distribution(self.angleToTarget())
		if (self.cmdargs.target_distribution_type == 'dotproduct'):
			targetpoint_ang = self.angleToTarget()
			targetpoint_pdf = np.array([(self.speed*(np.cos(np.abs(targetpoint_ang - ang) * np.pi/180)+1)/2) for ang in np.arange(0, 360, self.PDF.degree_resolution)], dtype='float64')
			targetpoint_pdf = (targetpoint_pdf / np.amax(targetpoint_pdf)) * 0.8 + 0.2

		self.combined_pdf = targetpoint_pdf

		radar_data = self.radar.ScanRadar(self.location, grid_data)
		if (0 < self.cmdargs.radar_noise_level):
			radar_data += self.gaussian_noise(self.cmdargs.radar_noise_level, radar_data.size)

		self.combined_pdf = self.combine_pdfs(self.combined_pdf, radar_data)

		if (not (self.cmdargs is None)) and (self.cmdargs.enable_memory):
			# Get memory effect vector
			mem_bias_vec = self.calc_memory_bias_vector()
			self.last_mbv = mem_bias_vec

			mem_bias_ang = Vector.getAngleBetweenPoints((0,0), mem_bias_vec)
			mem_bias_mag = Vector.getDistanceBetweenPoints((0,0), mem_bias_vec)

			# Create memory distribution based on dot product with memory vector
			mem_bias_pdf = np.array([np.cos(np.abs(mem_bias_ang - ang) * np.pi/180) for ang in np.arange(0, 360, self.PDF.degree_resolution)])
			mem_bias_pdf += 1 # Add 1 to get the cosine function above 0
			if np.amax(mem_bias_pdf) > 0:
				mem_bias_pdf = mem_bias_pdf / np.amax(mem_bias_pdf)
			self.combined_pdf = self.combine_pdfs(self.combined_pdf, mem_bias_pdf)

			if (self.stepNum % 1) == 0:
				self.visited_points.append(self.location)

		if (self.cmdargs.enable_pdf_smoothing_filter):
			self.combined_pdf = self.putfilter(self.combined_pdf)

		self.combined_pdf = np.maximum(self.combined_pdf, 0);
		movement_ang = self.pdf_angle_selector(self.combined_pdf) * self.PDF.degree_resolution
		
		if (self.using_safe_mode):
			dynamic_pdf = self.radar.scan_dynamic_obstacles(self.location, grid_data)
			self.adjust_speed_for_safety(dynamic_pdf, movement_ang)

		if (self.cmdargs.show_real_time_plot):
			plt.cla()
			plt.plot(self.combined_pdf)
			plt.plot(targetpoint_pdf)
			plt.plot(mem_bias_pdf)
			plt.plot(radar_data)
			plt.axis([0,360,0,1.1])
			plt.pause(0.00001)

		accel_vec = np.array([np.cos(movement_ang * np.pi / 180), np.sin(movement_ang * np.pi / 180)], dtype='float64') * self.speed
		movement_vec = np.add(self.last_mmv * self.movement_momentum, accel_vec * (1.0 - self.movement_momentum))
		if Vector.magnitudeOf(movement_vec) > self.speed:
			movement_vec *= self.speed / Vector.magnitudeOf(movement_vec) # Set length equal to self.speed
		self.last_mmv = movement_vec

		new_location = np.add(self.location, movement_vec)
		if (grid_data[int(new_location[0]), int(new_location[1])] & 1):
			if self.stepNum - self.last_glitch_step > 1:
				if not self.cmdargs.batch_mode:
					print('Robot ({}) glitched into obstacle!'.format(self.name))
				self.drawcoll = 10
				self.stats.num_glitches += 1
			self.last_glitch_step = self.stepNum
			new_location = np.add(new_location, -movement_vec*1.01 + np.random.uniform(-.5, .5, size=2));
			if(Vector.getDistanceBetweenPoints(self.location, new_location) > 2*self.speed):
				new_location = np.add(self.location, np.random.uniform(-0.5, 0.5, size=2))

		if (self.cmdargs.use_integer_robot_location):
			new_location = np.array(new_location, dtype=int)
		self.location = new_location

		self.PathList.append(np.array(self.location, dtype=int))


	def putfilter(self, inputsignal):
		N = 10 #order of the butterworth  filter
		Wn = 0.1 #Nyquest Sampling frequency
		b, a = scipy.signal.butter(N, Wn, 'low') #create butterworth filter
		outputsignal = scipy.signal.filtfilt(b, a, inputsignal)
		return outputsignal


	# Adjusts the speed of the robot based on the given dynamic obstacle 
	# distribution and movement angle
	def adjust_speed_for_safety(self, dynamic_pdf, movement_ang):
		closest_obs_degree	 = np.argmin (dynamic_pdf)
		closest_obs_dist = np.min(dynamic_pdf)
		angle_from_movement = np.absolute(Vector.angle_diff_degrees(movement_ang, closest_obs_degree))

		angle_weight_pdf = self.speed_adjust_pdf.get_distribution(90)

		self.speed = self.normal_speed
		min_speed = 2
		max_speed = 10
		speed_range = 2*(max_speed - min_speed)

		front_pdf = 1 - dynamic_pdf.take(np.arange(-90, 90, 1), mode='wrap')
		front_pdf[front_pdf > 0.05] = 1
		front_pdf *= angle_weight_pdf
		front_obs_ratio = front_pdf.sum() / front_pdf.size

		back_pdf = 1- dynamic_pdf.take(np.arange(90, 270, 1), mode='wrap')
		back_pdf[back_pdf > 0.05] = 1
		back_pdf *= angle_weight_pdf
		back_obs_ratio = back_pdf.sum() / back_pdf.size

		self.speed = self.normal_speed + (1.25*back_obs_ratio - front_obs_ratio) * (speed_range / 2.0)
		self.speed = np.clip(self.speed, min_speed, max_speed)


	def center_of_gravity_pdfselector(self, pdf):
		width = 60
		maxval_ind = np.argmax(pdf)
		sum_num = 0
		sum_den = 0
		for n in np.arange(int(maxval_ind - width / 2), int(maxval_ind + width/2), 1):
			sum_num += pdf[n % 360] * n
			sum_den += pdf[n % 360]
		center_of_mass = int(sum_num / (sum_den + 0.00001)) # Add a small number (0.00001) in case sum_den is 0
		return center_of_mass % 360


	def threshold_midpoint_pdfselector(self, pdf):
		maxval_ind = np.argmax(pdf)
		maxval = pdf[maxval_ind]
		threshold = 0.8 * maxval
		runStart = 0
		runLen = 0
		runPos = 0
		bestLen = 0
		bestStart = maxval_ind
		while runPos < len(pdf):
			if threshold <= pdf[runPos]:
				runLen += 1
			else:
				if bestLen < runLen:
					bestStart = runStart
					bestLen = runLen
				runStart = runPos
				runLen = 0
			runPos += 1
		return bestStart+int(bestLen/2)


	def max_value_pdfselector(self, pdf):
		return np.argmax(pdf)


	def calc_memory_bias_vector(self):
		sigma = self.memory_sigma
		decay = self.memory_decay
		size = int(self.memory_size)
		sigmaSquared = sigma * sigma
		gaussian_derivative = lambda x: -x*(np.exp(-(x*x/(2*sigmaSquared))) / sigmaSquared)
		vec = np.array([0, 0], dtype='float64')
		i = size
		for point in self.visited_points[-size:]:
		#for point in [PG.mouse.get_pos()]:
			effect_magnitude = gaussian_derivative(Vector.getDistanceBetweenPoints(point, self.location))
			effect_vector = (decay**i) * effect_magnitude * np.subtract(point, self.location)
			vec += effect_vector
			i -= 1
		return vec


	def draw(self, screen):
		# Be careful when uncommenting things in this function.
		# Each line drawn makes it more likely that the robot goes through obstacles
		#PG.draw.circle(screen, (0, 0, 255), np.array(self.location, dtype=int), 4, 0)
		BlueColor  = (0, 0, 255)
		GreenColor = (10, 100, 10)
		if (self.using_safe_mode):
			PathColor = GreenColor
		else:
			PathColor = BlueColor
		for ind, o in enumerate(self.PathList):
			if ind == len(self.PathList) - 1:
				continue
			PG.draw.line(screen,PathColor,self.PathList[ind], self.PathList[ind +1], 2)
		if (0 < self.cmdargs.debug_level):
			if self.drawcoll > 0:
				PG.draw.circle(screen, (255, 127, 127), np.array(self.location, dtype=int), 15, 1)
				self.drawcoll = self.drawcoll - 1
			# Draw line representing memory effect
			#PG.draw.line(screen, (0,255,0), np.array(self.location, dtype=int), np.array(self.location+self.last_mbv*100, dtype=int), 1)

			# Draw line representing movement
			#PG.draw.line(screen, (255,0,0), np.array(self.location, dtype=int), np.array(self.location+self.last_mmv*100, dtype=int), 1)

			# Draw circle representing radar range
			PG.draw.circle(screen, PathColor, np.array(self.location, dtype=int), self.radar.radius, 2)

			# Draw distribution values around robot
			#self.draw_pdf(screen, self.combined_pdf)


	def draw_pdf(self, screen, pdf):
		scale = self.radar.radius
		last_point = [self.location[0] + (pdf[0] * scale), self.location[1]]
		for index in np.arange(0, len(pdf), 1):
			ang = index * self.PDF.degree_resolution * np.pi / 180
			cur_point = self.location + scale*pdf[index]*np.array([np.cos(ang), np.sin(ang)], dtype='float64')
			PG.draw.line(screen, (0,200,200), last_point, cur_point, 1)
			last_point = cur_point


	def distanceToTarget(self):
		return Vector.getDistanceBetweenPoints(self.target.position, self.location)

	def angleToTarget(self):
		return Vector.getAngleBetweenPoints(self.location, self.target.position)
