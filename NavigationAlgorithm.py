#!/usr/bin/python3

## @package NavigationAlgorithm
#


import numpy  as np
import pygame as PG
from Robot import RobotControlInput
import Distributions
import Vector
import matplotlib.pyplot as plt
import time
import scipy.signal


## A navigation algorithm to be used with robots.
#
#
class NavigationAlgorithm:

	## Initializes the navigation algorithm.
	# 
	# @param robot (Robot object)
	# <br>	-- the robot that this algorithm is navigating for
	#
	# @param cmdargs (object)
	# <br>	-- A command-line arguments object generated by `argparse`.
	# 
	# @param using_safe_mode (boolean)
	# <br>	-- Whether the robot should operate in "safe mode", which
	# 	slightly changes the way the navigation algorithm works.
	#
	def __init__(self, robot, cmdargs, using_safe_mode=False):
		self._robot = robot;
		self._cmdargs = cmdargs;
		self.using_safe_mode = using_safe_mode

		self.debug_info = {
			"last_mbv": np.array([0, 0])
		};

		self.normal_speed = cmdargs.robot_speed
		self.max_speed = 10
		if (self._cmdargs.speedmode == 5):
			self.normal_speed = 10
		if (not self.using_safe_mode):
			self.normal_speed = 10

		self._speed_adjust_pdf = Distributions.Gaussian()
		self._speed_adjust_pdf.degree_resolution = 2

		self._PDF = Distributions.Gaussian()
		if (self._cmdargs.target_distribution_type == 'rectangular'):
			self._PDF = Distributions.Rectangular()

		# Number of steps taken in the navigation
		self.stepNum = 0

		# Function that selects an angle based on a distribution
		self._pdf_angle_selector = self._center_of_gravity_pdfselector
		# Function that combines pdfs
		self._combine_pdfs	= np.minimum

		# Memory of visited points
		self.visited_points	= []

		# Movement and memory parameters
		self.memory_sigma = cmdargs.robot_memory_sigma
		self.memory_decay = cmdargs.robot_memory_decay
		self.memory_size  = cmdargs.robot_memory_size

		# Used to allow real-time plotting
		if cmdargs.show_real_time_plot:
			plt.ion()
			plt.show()


	## Select the next action for the robot
	#
	# This function uses the robot's radar and location information, as
	# well as internally stored information about previous locations,
	# to compute the next action the robot should take.
	#
	# @returns (RobotControlInput object)
	# <br>	-- A control input representing the next action the robot
	# 	should take.
	#
	def select_next_action(self):
		# Variable naming note: some variables have _pdf on their
		# name, which is meant to indicate that they represent some
		# kind of probability distribution over the possible
		# movement directions

		self.stepNum += 1

		targetpoint_pdf = self._create_targetpoint_pdf();

		# The combined PDF will store the combination of all the
		# PDFs, but for now that's just the targetpoint PDF
		combined_pdf = targetpoint_pdf

		# Scan the radar to get obstacle information
		raw_radar_data = self._robot.radar.scan(self._robot.location);
		raw_dynamic_radar_data = self._robot.radar.scan_dynamic_obstacles(self._robot.location);

		normalized_radar_data = raw_radar_data / self._robot.radar.radius;
		if (0 < self._cmdargs.radar_noise_level):
			normalized_radar_data += self._gaussian_noise(self._cmdargs.radar_noise_level, normalized_radar_data.size)

		# Add the obstacle distribution into the combined PDF
		combined_pdf = self._combine_pdfs(combined_pdf, normalized_radar_data)

		# Process memory
		if self._cmdargs.enable_memory:
			mem_bias_pdf = self._create_memory_bias_pdf();

			# Add the memory distribution to the combined PDF
			combined_pdf = self._combine_pdfs(combined_pdf, mem_bias_pdf)


		# Possibly smooth the combined distribution, to avoid
		# having sudden jumps in value
		if (self._cmdargs.enable_pdf_smoothing_filter):
			combined_pdf = self._putfilter(combined_pdf)

		combined_pdf = np.maximum(combined_pdf, 0);
		direction = self._pdf_angle_selector(combined_pdf) * self._PDF.degree_resolution

		# Set the speed
		speed = self._select_speed(direction, raw_dynamic_radar_data);

		if (self._cmdargs.show_real_time_plot):
			self._update_plot([
				combined_pdf,
				targetpoint_pdf,
				mem_bias_pdf,
				radar_data
			]);


		return RobotControlInput(speed, direction);


	def _create_memory_bias_pdf(self):
		# Get memory effect vector
		mem_bias_vec = self._calc_memory_bias_vector()
		self.debug_info["last_mbv"] = mem_bias_vec

		mem_bias_ang = Vector.getAngleBetweenPoints([0, 0], mem_bias_vec)
		mem_bias_mag = Vector.getDistanceBetweenPoints([0, 0], mem_bias_vec)

		# Create memory distribution based on dot product with memory vector
		mem_bias_pdf = np.array([np.cos(np.abs(mem_bias_ang - ang) * np.pi/180) for ang in np.arange(0, 360, self._PDF.degree_resolution)])
		mem_bias_pdf += 1 # Add 1 to get the cosine function above 0
		if np.amax(mem_bias_pdf) > 0:
			mem_bias_pdf = mem_bias_pdf / np.amax(mem_bias_pdf)

		if (self.stepNum % 1) == 0:
			self.visited_points.append(self._robot.location)

		return mem_bias_pdf;


	## Creates the targetpoint distribution.
	#
	# The targetpoint PDF relates to the target/goal. It should be
	# higher for angles that point towards the goal, and lower for
	# angles that point away
	#
	# @returns (numpy array)
	# <br>	-- the targetpoint distribution for the robot's current
	# 	location
	#
	def _create_targetpoint_pdf(self):
		targetpoint_pdf = self._PDF.get_distribution(self._robot.angleToTarget())
		if (self._cmdargs.target_distribution_type == 'dotproduct'):
			targetpoint_ang = self._robot.angleToTarget()
			targetpoint_pdf = np.array([(self.speed*(np.cos(np.abs(targetpoint_ang - ang) * np.pi/180)+1)/2) for ang in np.arange(0, 360, self._PDF.degree_resolution)], dtype='float64')
			targetpoint_pdf = (targetpoint_pdf / np.amax(targetpoint_pdf)) * 0.8 + 0.2
		return targetpoint_pdf;


	def _select_speed(self, direction, raw_dynamic_radar_data):
		speed = self.normal_speed
		if (self.using_safe_mode):
			dynamic_pdf = raw_dynamic_radar_data / self._robot.radar.radius;
			self.debug_info["drawing_pdf"] = dynamic_pdf
			speed = self._adjust_speed_for_safety(dynamic_pdf, direction)
		return speed;


	def _update_plot(self, pdf_list):
		plt.cla()
		for pdf in pdf_list:
			plt.plot(pdf);
		plt.axis([0,360,0,1.1])
		plt.pause(0.00001)
		


	## Creates an array for adding noise to a distribution
	#
	# @param noise_level (float)
	# <br>	-- The amplitude of the noise
	#
	# @param size (int)
	# <br>	-- The size of the array to generate
	#
	# @returns (numpy array)
	# <br>	-- An array of noise values, that can be added to a
	# 	distribution to make it noisy.
	def _gaussian_noise(self, noise_level, size):
		noise_pdf = np.random.normal(0, noise_level, size)
		return noise_pdf


	## Smooths the given distribution
	#
	def _putfilter(self, inputsignal):
		N = 10 #order of the butterworth  filter
		Wn = 0.1 #Nyquest Sampling frequency
		b, a = scipy.signal.butter(N, Wn, 'low') #create butterworth filter
		outputsignal = scipy.signal.filtfilt(b, a, inputsignal)
		return outputsignal


	## Selects a safe speed for the robot based on the given dynamic
	# obstacle distribution and movement angle
	#
	def _adjust_speed_for_safety(self, dynamic_pdf, movement_ang):
		closest_obs_degree	 = np.argmin (dynamic_pdf)
		closest_obs_dist = np.min(dynamic_pdf)
		angle_from_movement = np.absolute(Vector.angle_diff_degrees(movement_ang, closest_obs_degree))

		angle_weight_pdf = self._speed_adjust_pdf.get_distribution(90)

		speed = self.normal_speed
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

		speed = self.normal_speed + (1.25*back_obs_ratio - front_obs_ratio) * (speed_range / 2.0)
		return np.clip(speed, min_speed, max_speed)


	def _center_of_gravity_pdfselector(self, pdf):
		width = 60
		maxval_ind = np.argmax(pdf)
		sum_num = 0
		sum_den = 0
		for n in np.arange(int(maxval_ind - width / 2), int(maxval_ind + width/2), 1):
			sum_num += pdf[n % 360] * n
			sum_den += pdf[n % 360]
		center_of_mass = int(sum_num / (sum_den + 0.00001)) # Add a small number (0.00001) in case sum_den is 0
		return center_of_mass % 360


	def _threshold_midpoint_pdfselector(self, pdf):
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


	def _max_value_pdfselector(self, pdf):
		return np.argmax(pdf)


	def _calc_memory_bias_vector(self):
		sigma = self.memory_sigma
		decay = self.memory_decay
		size = int(self.memory_size)
		sigmaSquared = sigma * sigma
		gaussian_derivative = lambda x: -x*(np.exp(-(x*x/(2*sigmaSquared))) / sigmaSquared)
		vec = np.array([0, 0], dtype='float64')
		i = size
		for point in self.visited_points[-size:]:
		#for point in [PG.mouse.get_pos()]:
			effect_magnitude = gaussian_derivative(Vector.getDistanceBetweenPoints(point, self._robot.location))
			effect_vector = (decay**i) * effect_magnitude * np.subtract(point, self._robot.location)
			vec += effect_vector
			i -= 1
		return vec

