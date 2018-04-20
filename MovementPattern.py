
## @package ParametricPathMovement
#

import numpy as np
import Vector


class MovementPattern:
	def __init__(self, initial_pos=(0, 0)):
		self._pos = np.array(initial_pos, dtype=np.float64)


	## Advances the current position of this movement based on the given
	# timestep and returns the new position
	#
	def step(self, timestep):
		pass


	## Returns the current position
	#
	def get_pos(self):
		return self._pos


## A static MovementPattern that does not move. Good for static obstacles.
#
class StaticMovement(MovementPattern):
	def __init__(self, initial_pos):
		super().__init__(initial_pos=initial_pos)

	def step(self, timestep):
		pass

	def get_pos(self):
		return self._pos


## A MovementPattern that is static relative to a given Robot. Useful for an
# Obstacle that represents the physical body of a Robot.
#
class RobotBodyMovement(MovementPattern):
	def __init__(self, robot):
		super().__init__(initial_pos=robot.location)
		self._robot = robot

	def step(self, timestep):
		pass

	def get_pos(self):
		return self._robot.location


## Represents a movement through space modeled as a parametric curve
#
class ParametricPathMovement(MovementPattern):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._cur_time = 0.0

		self._pos = self.pos_at(0)


	## Gets the (x, y) coordinates of this path at the given time
	# 
	def pos_at(self, time):
		pass


	def step(self, timestep):
		self._cur_time += timestep
		self._pos = self.pos_at(self._cur_time)
		return self._pos


## Circular movement
#
class CircleMovement(ParametricPathMovement):
	def __init__(self, center, radius, speed, *args, angle_offset=0, **kwargs):
		self._center = center;
		self._radius = radius;
		self._speed = speed;
		self._angle_offset = angle_offset

		self._angular_speed = self._speed / self._radius
		print(self._angular_speed, self._speed, self._radius)

		super().__init__(*args, **kwargs);


	## Get position at time. Overrides method from ParametricPathMovement
	# 
	def pos_at(self, time):
		angle = (time * self._angular_speed) + self._angle_offset
		return np.add(self._center, (np.cos(angle)*self._radius, np.sin(angle) * self._radius))


## Movement along a fixed closed path
#
class PathMovement(ParametricPathMovement):

	## Constructor
	#
	# @param path_list (array-like)
	# <br>  Format: `[[x1, y1], ..., [xn, yn]]` OR
	# <br>  `[[x1, y1, t1], [x2, y2, t2], ..., [xn, yn, tn]]`
	# <br>  -- List of points in the path to travel along. Note that if
	#          using the `[x, y, t]` format, where `t` is the time at which
	#          the object should arrive at the given `(x, y)`, the `speed`
	#          parameter won't be used. Also, the values of `t` in the list
	#          must come in strictly ascending order, and the format of the
	#          path is decided based on the first element (i.e., if
	#          `path_list[0]` is `[x, y]`, any `t` in subsequent elements
	#          will be ignored, and if the first element is `[x, y, t]`
	#          then all elements are expected to have a `t` parameter)
	#
	# @param speed (numeric)
	# <br>  -- The speed, if the object is to move at a fixed speed. Not
	#          used if the path is given with timestamps.
	#
	# @param loop (boolean)
	# <br>  -- Whether to loop when the path is completed. If `True`, then
	#          when the object reaches the end of the `path_list` it
	#          teleports back to the starting point. To achieve continuous
	#          motion, it is recommended to make the last point in
	#          `path_list` have the same `(x, y)` location as the first
	#          point, to move the object back without teleporting.
	#
	def __init__(self, path_list, *args, speed=0, loop=True, **kwargs):

		if len(path_list) < 2:
			raise ValueError("Need at least two points for a path")

		self._path_list = np.array(path_list)
		self._speed = speed;
		self._loop = loop;

		path_type = 'fixed_speed';
		if len(self._path_list[0]) == 3:
			path_type = 'timestamped'

		# Convert fixed-speed paths to timestamped, so we only have to
		# work with one type
		new_path = self._path_list
		if path_type == 'fixed_speed' and speed == 0:
			# Special case when speed == 0, to avoid divide-by-zero
			new_path = [(self._path_list[0][0], self._path_list[0][1], 0.0), (self._path_list[0][0], self._path_list[0][1], 1.0)]
			self._path_list = np.array(new_path)
		elif path_type == 'fixed_speed':
			new_path = [(self._path_list[0][0], self._path_list[0][1], 0.0)]
			last_point = new_path[0]
			for point in self._path_list[1:]:
				old_time = last_point[2]
				new_time = old_time + (Vector.distance_between(last_point[:2], point[:2]) / speed)

				# Timestamps should be strictly ascending, so skip duplicate points
				if new_time == old_time:
					continue

				new_point = (point[0], point[1], new_time)
				new_path.append(new_point)

				last_point = new_point
			self._path_list = np.array(new_path)

		self._path_length = self._path_list[-1][2]

		super().__init__(*args, **kwargs);


	## Get position at time. Overrides method from ParametricPathMovement
	# 
	def pos_at(self, time):
		if self._loop:
			time = time % self._path_length

		# Find the segment the current time lies on
		for i in range(len(self._path_list)-1):
			cur_time = self._path_list[i][2]
			next_time = self._path_list[i+1][2]
			if cur_time <= time and time < next_time:
				segment_time = next_time - cur_time
				time_diff = time - cur_time
				segment_vec = self._path_list[i+1][:2] - self._path_list[i][:2]
				return self._path_list[i][:2] + (segment_vec * time_diff / segment_time)

		# Corner cases when the time is before the beginning of the
		# path or after the end
		if time <= self._path_list[0][2]:
			return self._path_list[0][:2]
		elif time >= self._path_list[-1][2]:
			return self._path_list[-1][:2]

		# We should have covered all cases, so if we get here something
		# went wrong
		raise Exception('Unknown error: Unable to determine path position')



## Represents a random movement through space
#
class RandomMovement(MovementPattern):
	def __init__(self, *args, random_interval=0.99, speed=1, **kwargs):
		self._random_interval = random_interval
		self._speed = speed

		self._leftover = 0.0

		super().__init__(*args, **kwargs)


	def step(self, timestep):
		intervals = (timestep + self._leftover) / self._random_interval
		num_moves = int(np.floor(intervals))
		self._leftover = intervals - num_moves

		for i in range(num_moves):
			self._pos += self._speed * Vector.unit_vec_from_radians(np.random.uniform(0, 2*np.pi))

		return self._pos

