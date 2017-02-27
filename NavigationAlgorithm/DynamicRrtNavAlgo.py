#!/usr/bin/python3


import numpy	as np
import Vector, time
from math import *
from .AbstractNavAlgo import AbstractNavigationAlgorithm
from Robot import RobotControlInput

## Implementation of the Dynamic Window algorithm for robotic navigation.
#
# @see
# \ref AbstractNavAlgo.AbstractNavigationAlgorithm
#		"AbstractNavigationAlgorithm"
#
class DynamicRrtNavigationAlgorithm(AbstractNavigationAlgorithm):
	def __init__(self, robot, cmdargs):
		# Init basic members
		self._robot = robot;
		self._cmdargs = cmdargs;
		self._data_size = robot.radar.get_data_size();
		self._radar_range = robot.radar.radius;
		self._radar_resolution = robot.radar.resolution;
		self._dynamic_radar_data = self._robot.radar.scan_dynamic_obstacles(self._robot.location);

		#Algo
		self._maxstepsize = cmdargs.robot_speed;
		self._numOfWayPoint = 0;
		self._wayPointCache = []
		self._goalThresold = self._maxstepsize * 0.75; #In pixel distance
		self._goalBias = 0.1;
		self._wayPointBias = 0.2;
		self._maxRrtSize = 20000;
		self.debug_info = {"path": None, "point": None}

		#Make initial RRT from start to goal
		self._solution = []
		self._initRRT(self._robot.target.position, self._robot.location, False);
		self._grow_rrt(False) #final_node = nearest node to robot's current position
		self._extract_solution() #path does not contain robot's current position

		# Set using_safe_mode to appease Robot.draw()
		self.using_safe_mode = True;

		self._last_solution_node = Node((int(self._robot.location[0]), int(self._robot.location[1])))

	## Next action selector method.
	#
	# @see 
	# \ref AbstractNavAlgo.AbstractNavigationAlgorithm.select_next_action
	#		"AbstractNavigationAlgorithm.select_next_action()"
	#
	def select_next_action(self):
		self._dynamic_radar_data = self._robot.radar.scan_dynamic_obstacles(self._robot.location);

		if self._last_solution_node.data != (int(self._robot.location[0]), int(self._robot.location[1])):
			self._solution.insert(0, self._last_solution_node)

		self._invalidateNodes();

		robot_location = self._robot.location
		grid_data = self._robot.radar._env.grid_data
		if grid_data[int(robot_location[0])][int(robot_location[1])] != 3:
			if self._solution_contains_invalid_node():
				self._regrow_rrt();
				self._extract_solution();
				self.debug_info["path"] = self._solution

			if len(self._solution) > 0:
				direction = Vector.getAngleBetweenPoints(self._robot.location, self._solution[0].data)
				dist = min(self._maxstepsize, Vector.getDistanceBetweenPoints(self._robot.location, self._solution[0].data))
			else:
				self._initRRT(self._robot.target.position, self._robot.location, False);
				self._grow_rrt(False);
				self._extract_solution();
				direction = Vector.getAngleBetweenPoints(self._robot.location, self._solution[0].data)
				dist = min(self._maxstepsize, Vector.getDistanceBetweenPoints(self._robot.location, self._solution[0].data))
			self.debug_info["path"] = self._solution
			self._last_solution_node = self._solution[0]
			del self._solution[0];
		else:
			#If robot is inside dynamic obstacle
			dist = 0
			direction = np.random.uniform(low=0, high=360);

		return RobotControlInput(dist, direction);

	def _regrow_rrt(self):
		nearest_valid_node = self._nearest_neighbour(self._robot.location, True)

		self._initRRT(nearest_valid_node.data, self._robot.location, True);
		self._grow_rrt(True);

	def _grow_rrt(self, regrow):
		#Always call initRRT before growRRT
		qNew = self._qstart;
		foundGoal = False;
		count = 0;

		while not foundGoal and count < self._maxRrtSize:
			qTarget = self._chose_target(); #Type Node
			if regrow:
				qNearest = self._nearest_neighbour(qTarget, True); #Type Node
			else:
				qNearest = self._nearest_neighbour(qTarget, False);

			qNew = Node(self._step_from_to(qNearest.data, qTarget.data))

			if not self._collides(qNearest.data, qNew.data, False):
				if regrow:
					if qNew.data not in self._rrt.toInvalidDataList():
						qNearest.addChild(qNew)
						if Vector.getDistanceBetweenPoints(qNew.data, self._qgoal.data) < self._goalThresold:
							foundGoal = True
						count += 1
					
				else:
					if qNew.data not in self._rrt.toDataList():
						qNearest.addChild(qNew)
						if Vector.getDistanceBetweenPoints(qNew.data, self._qgoal.data) < self._goalThresold:
							foundGoal = True
						count += 1

		if foundGoal:
			self._final_node = qNew
		else:
			self._final_node = None

	def _invalidateNodes(self):
		# Check if there is any dynamic obstacle within radar range
		dynamic_obstacle_points = self._convert_radar_to_grid()
		if len(dynamic_obstacle_points) > 0:
			nearby_nodes = self._rrt.get_nearby_nodes(self._robot.location, self._radar_range)
			for node in nearby_nodes:
				if node.parent:
					if self._anyParentsCollide(node):
						node.invalidate()
					else:
					 	node.validate()

	def _anyParentsCollide(self, node):
		parent = node.parent
		if parent is not None:
			if self._collides(node.data, parent.data, True):
				return True
			else:
				return self._anyParentsCollide(parent)
		else:
			return False
		

	def _initRRT(self, qstart, qgoal, append):
			self._qstart = Node(qstart);
			self._qgoal = Node(qgoal);

			if not append:
				self._rrt = Tree(self._qstart.data);

	def _solution_contains_invalid_node(self):
		for node in self._solution:
			if node.flag == 1:
				return True

		return False

	def _chose_target(self):
		randReal = np.random.uniform(0.0, 1.0);
		if self._numOfWayPoint > 0:
				randInt = np.random.randint(0, self._numOfWayPoint - 1);

		if randReal < self._goalBias:
			return self._qgoal;
		else:
			if randReal < (self._goalBias + self._wayPointBias) and self._wayPointCache:
				return self._wayPointCache[randInt];
			else:
				return self._get_safe_random_node();

	def _extract_solution(self):
		self._solution = []
		if self._final_node is not None:
			current_node = self._final_node; #Nearest node to the robot's current position
			i = 0;
			while current_node.data != self._robot.target.position:
				#Store some of the nodes to way point cache
				if i % 5 == 0:
					self._wayPointCache.append(current_node.parent)
				self._solution.append(current_node.parent);
				current_node = current_node.parent;

			self._numOfWayPoint = len(self._wayPointCache)
		else:
			#Algo ran out of max rrt size
			pass

	def _nearest_neighbour(self, qTarget, onlyValidNode):
		if onlyValidNode:
			tree_nodes = self._rrt.toListValidNodes()
		else:
			tree_nodes = self._rrt.toList();

		nearest_node = min(tree_nodes, key=lambda t: Vector.getDistanceBetweenPoints(t.data, qTarget.data))

		return nearest_node

	def _step_from_to(self, p1, p2):
		if Vector.getDistanceBetweenPoints(p1, p2) < self._maxstepsize:
			return p2
		else:
			theta = atan2(p2[1] - p1[1], p2[0] - p1[0])
			return p1[0] + self._maxstepsize * cos(theta), p1[1] + self._maxstepsize * sin(theta)

	def _get_safe_random_node(self):
		while True:
			rand_point = self._get_random_point()
			if not self._collides(None, rand_point, False):
				return Node(rand_point)

	def _collides(self, fromPoint, toPoint, dynamicOnly):
		grid_data = self._robot.radar._env.grid_data
	
		if fromPoint is not None:
			ang_in_radians = Vector.degrees_between(fromPoint, toPoint) * np.pi / 180
			dist = Vector.getDistanceBetweenPoints(fromPoint, toPoint)

			cos_cached = np.cos(ang_in_radians)
			sin_cached = np.sin(ang_in_radians)
			for i in np.arange(0, dist, 0.5):
				x = int(cos_cached * i + fromPoint[0])
				y = int(sin_cached * i + fromPoint[1])
				if grid_data[x][y] & 1 and Vector.distance_between((x,y), self._robot.location) < self._robot.radar.radius:
					return True
				if not dynamicOnly:
					if grid_data[x][y] & 4:
						return True
		else:
				# Check for dynamic obstacle
			if grid_data[int(toPoint[0])][int(toPoint[1])] & 1 and Vector.distance_between(toPoint, self._robot.location) < self._robot.radar.radius:
				return True
			# Check for static obstacle
			if not dynamicOnly:
				if grid_data[int(toPoint[0])][int(toPoint[1])] & 4:
					return True;

		return False;

	def _convert_radar_to_grid(self):
		obstacle_points = []

		# Construct the grid out of radar data.
		for angle in range(360):
			index = int(np.round(angle * (self._data_size / 360.0)));
			distance = self._dynamic_radar_data[index];

			if distance < self._radar_range:
				obs_coordinate = (self._robot.location + (distance * Vector.unitVectorFromAngle(angle * np.pi / 180)));
				obs_cell = tuple(np.array(obs_coordinate, dtype=np.int32).tolist());
				obstacle_points.append(obs_cell)

		return obstacle_points

	def _get_random_point(self):
		XDIM = 800
		YDIM = 600
		return np.random.random() * XDIM, np.random.random() * YDIM

class Tree:

	def __init__(self, root_data):
		self.root = Node(root_data);

	def toList(self):
		return self.root.toList();

	def toDataList(self):
		return [node.data for node in self.root.toList()]

	def toListValidNodes(self):
		return [node for node in self.root.toList() if node.flag == 0]

	def toValidDataList(self):
		return [node.data for node in self.root.toList() if node.flag == 0]
	
	def toListInvalidNodes(self):
		return [node for node in self.root.toList() if node.flag == 1]
	
	def toInvalidDataList(self):
		return [node.data for node in self.root.toList() if node.flag == 1]

	def get_nearby_nodes(self, center, distance):
		all_nodes = self.toList()
		nearby_nodes = []

		for node in all_nodes:
			if Vector.getDistanceBetweenPoints(center, node.data) <= distance:
				nearby_nodes.append(node)

		return nearby_nodes

	def getSize(self):
		return self.root.size;
	
class Node:

	def __init__(self, data):
		self.data = tuple((int(data[0]), int(data[1])));
		self._children = [];
		self.parent = None;
		self.size = 1;
		self.flag = 0; # 0 means valid

	def addChild(self, child):
		self._children.append(child);
		child.parent = self;
		self.incrementSize();

	def toList(self):
		result = []

		frontier = Stack();
		frontier.push(self);

		for node in self._children:
			frontier.push(node)

		while True:
			if len(result) == self.size:
				return result;
			else:
				currentNode = frontier.pop();
				result.append(currentNode);
				for node in currentNode._children:
					frontier.push(node);

	def toListValidChildren(self):
		result = []

		frontier = Stack();
		if self.flag == 0:
			frontier.push(self);
		else:
			return None #No valid nodes found

		for node in self._children:
			if node.flag == 0:
				frontier.push(node)

		while True:
			if len(result) == self.validSize:
				return result;
			else:
				currentNode = frontier.pop();
				result.append(currentNode);
				for node in currentNode._children:
					if node.flag == 0:
						frontier.push(node);

	def invalidate(self):
		self.flag = 1
		for child in self._children:
			child.invalidate()

	def validate(self):
		self.flag = 0
		if self.parent is not None:
			self.parent.validate()

	def incrementSize(self):
		self.size += 1;
		if self.parent:
			self.parent.incrementSize();


class Stack:
		"A container with a last-in-first-out (LIFO) queuing policy."
		def __init__(self):
				self.list = []

		def push(self,item):
				"Push 'item' onto the stack"
				self.list.append(item)

		def pop(self):
				"Pop the most recently pushed item from the stack"
				return self.list.pop()

		def isEmpty(self):
				"Returns true if the stack is empty"
				return len(self.list) == 0

