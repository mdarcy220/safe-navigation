#!/usr/bin/python3


import numpy  as np
import Vector
from .AbstractNavAlgo import AbstractNavigationAlgorithm
from Robot import RobotControlInput
from ObstaclePredictor import DummyObstaclePredictor, HMMObstaclePredictor
from queue import Queue, PriorityQueue



## A navigation algorithm to be used with robots, based on trajectory 
# sampling and RRT.
#
# @see
# \ref AbstractNavAlgo.AbstractNavigationAlgorithm
# 	"AbstractNavigationAlgorithm"
#
class SamplingNavigationAlgorithm(AbstractNavigationAlgorithm):
	def __init__(self, robot, cmdargs):
		self._robot = robot;
		self._cmdargs = cmdargs;
		self._normal_speed = cmdargs.robot_speed;
		self._max_sampling_iters = 400
		self._radar_data = None
		self._safety_threshold = 0.25;
		self._stepNum = 0;

		# Memory parameters
		self.visited_points	= []
		self.memory_sigma = cmdargs.robot_memory_sigma
		self.memory_decay = cmdargs.robot_memory_decay
		self.memory_size  = cmdargs.robot_memory_size
		self._mem_bias_vec = np.array([0.7, 0.7])
		self.using_safe_mode = True

		#Obstecle Predictor
		self._obstacle_predictor = HMMObstaclePredictor(360);

	## Next action selector method.
	#
	# @see 
	# \ref AbstractNavAlgo.AbstractNavigationAlgorithm.select_next_action
	# 	"AbstractNavigationAlgorithm.select_next_action()"
	#
	def select_next_action(self):
		dynamic_radar_data = self._robot.radar.scan_dynamic_obstacles(self._robot.location);
		self._stepNum += 1;
		self._radar_data = self._robot.radar.scan(self._robot.location);

		self._obstacle_predictor.add_observation(self._robot.location,
				self._radar_data,
				dynamic_radar_data,
				self._obstacle_predictor_dynobs_getter_func
		);

		# Init queue
		traj_queue = Queue();
		traj_queue.put([]);

		best_traj = [self._robot.location];

		for i in range(self._max_sampling_iters):
			if traj_queue.empty():
				break
			traj = traj_queue.get_nowait();
			comp_result = self._compare_trajectories(traj, best_traj);
			if comp_result < 0:
				best_traj = traj
			if self._is_trajectory_feasible(best_traj) and not self._is_trajectory_feasible(traj) and i > 1:
				continue
			child_trajs = self._sample_child_trajectories([]);
			for child_traj in child_trajs:
				traj_queue.put_nowait(child_traj);

		next_point = best_traj[0];
		direction = Vector.getAngleBetweenPoints(self._robot.location, next_point);
		if self._stepNum % 1 == 0:
			self.visited_points.append(self._robot.location);
			self._mem_bias_vec = self._calc_memory_bias_vector();
			if Vector.magnitudeOf(self._mem_bias_vec) > 0:
				self._mem_bias_vec = self._mem_bias_vec / Vector.magnitudeOf(self._mem_bias_vec);
		if np.array_equal(next_point, self._robot.location):
			# Next point is equal to current point, so stop the
			# robot
			return RobotControlInput(0, 0);

		return RobotControlInput(self._normal_speed, direction);


	## Compares two trajectories
	#
	# @return (int)
	# <br>	`< 0` if traj1 is better than traj2
	# <br>	`0` if equally good
	# <br>	`> 0` if traj1 is worse than traj2
	#
	def _compare_trajectories(self, traj1, traj2):
		traj1_empty = (len(traj1) == 0)
		traj2_empty = (len(traj2) == 0)
		if traj1_empty and traj2_empty:
			return 0;
		elif traj1_empty:
			return 1;
		elif traj2_empty:
			return -1;

		safety1 = self._safety_heuristic(traj1);
		safety2 = self._safety_heuristic(traj2);

		if self._safety_threshold < safety1 and self._safety_threshold < safety2:
			return int(np.sign(safety1 - safety2));
		elif self._safety_threshold < safety1:
			return 1;
		elif self._safety_threshold < safety2:
			return -1;

		heuristic1 = self._eval_distance_heuristic(traj1);
		heuristic2 = self._eval_distance_heuristic(traj2);
		return int(np.sign(heuristic1*(safety1+0.01) - heuristic2*(safety2+0.01)));


	def _sample_child_trajectories(self, seed_traj):
		# Note: When appending to this `children` variable, we use
		# `seed_traj + new_point`, i.e. using the Python list
		# concatenation operator. This will automatically make a
		# copy of seed_traj and add the new point to that, so
		# seed_traj will be unmodified (and thus, can be reused)
		children = [];

		seed_endpoint = seed_traj[-1] if 0 < len(seed_traj) else self._robot.location;

		# Append a "stopping" trajectory
		new_traj = list(seed_traj);
		new_traj.append(seed_endpoint);
		children.append(new_traj)

		# Append a "straight to the goal" trajectory
		angle_to_goal = self._robot.angleToTarget() * np.pi / 180.0
		towards_goal = Vector.unitVectorFromAngle(angle_to_goal) * self._normal_speed;
		waypoint_towards_goal = np.add(seed_endpoint, towards_goal);
		new_traj = list(seed_traj);
		new_traj.append(waypoint_towards_goal);
		children.append(new_traj);

		# Append some random trajectories
		for i in range(8):
			vec = Vector.unitVectorFromAngle(np.random.normal(2*np.pi)) * self._normal_speed;
			waypoint = np.add(seed_endpoint, vec);
			new_traj = list(seed_traj);
			new_traj.append(waypoint);
			children.append(new_traj);

		return children;


	def _eval_distance_heuristic(self, traj):
		endpoint = traj[-1];
		targetpoint = self._robot.target.position;
		target_vec = targetpoint - self._robot.location;
		target_vec = target_vec / Vector.magnitudeOf(target_vec);
		my_vec = (endpoint - self._robot.location);
		mem_vec = self._mem_bias_vec;
		base_heuristic = (-min(np.dot(my_vec, target_vec), np.dot(my_vec, mem_vec)))
		len_mod_factor = len(traj) if 0 <= np.sign(base_heuristic) else 1.0/len(traj);
		return base_heuristic*len_mod_factor;


	def _calc_memory_bias_vector(self):
		sigma = self.memory_sigma
		decay = self.memory_decay
		size = int(self.memory_size)
		sigmaSquared = sigma * sigma
		gaussian_derivative = lambda x: -x*(np.exp(-(x*x/(2*sigmaSquared))) / sigmaSquared)
		vec = np.array([0, 0], dtype='float64')
		i = size
		for point in self.visited_points[-size:]:
			effect_magnitude = gaussian_derivative(Vector.getDistanceBetweenPoints(point, self._robot.location))
			effect_vector = (decay**i) * effect_magnitude * np.subtract(point, self._robot.location)
			vec += effect_vector
			i -= 1
		return vec


	def _safety_heuristic(self, traj):
		if len(traj) == 0:
			return 0.0;
		radar_data = self._radar_data;
		endpoint = traj[-1];
		degree_step = self._robot.radar.get_degree_step();
		data_size = self._robot.radar.get_data_size();
		radar_range = self._robot.radar.radius;

		endpoint_dist = Vector.getDistanceBetweenPoints(self._robot.location, endpoint);
		angle_to_endpoint = Vector.getAngleBetweenPoints(self._robot.location, endpoint);

		index1 = int(np.ceil(angle_to_endpoint / degree_step)) % data_size;
		index2 = int(np.floor(angle_to_endpoint / degree_step)) % data_size;

		if (radar_data[index1]-5) <= endpoint_dist or (radar_data[index2]-5) <= endpoint_dist:
			return 1.0;

		index3 = (index1 + 1) % data_size;
		index4 = (index2 - 1) % data_size;

		f1 = radar_data[index1] - endpoint_dist;
		f2 = radar_data[index2] - endpoint_dist;
		f3 = radar_range - endpoint_dist;

		width=60
		sum_radar = np.sum(radar_data.take(range(int(index1-width/2), int(index1+width/2)), mode='wrap'))

		return 1.0 - (sum_radar/(radar_range*width))


	def _is_trajectory_feasible(self, traj):
		return self._safety_heuristic(traj) < self._safety_threshold;

	def _obstacle_predictor_dynobs_getter_func(self, angle):
		return self._robot.radar.get_dynobs_at_angle(self._robot.location, angle)

