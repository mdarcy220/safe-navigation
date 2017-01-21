#!/usr/bin/python3

## @package MultiLevelNavAlgo
#
# Classes for the multi-level navigation algorithm.
#

import numpy as np;
import Vector;
from queue import Queue, PriorityQueue;
from Robot import RobotControlInput;
from .AbstractNavAlgo import AbstractNavigationAlgorithm;
from .SamplingNavAlgo import SamplingNavigationAlgorithm;


## Represents an edge in a graph (in particular, the graph used in the
# MultiLevelNavigationAlgorithm).
#
# Note: The edges represented by this class are directional, having a
# "from" node and a "to" node.
#
class NodeEdge:
	
	## @var from_node (Node object)
	# <br>	-- the starting node for this edge
	#
	# @var to_node (Node object)
	# <br>	-- the ending node for this edge
	#
	# @var weight (float)
	# <br>	-- the weight of this edge
	#

	## Constructor
	#
	def __init__(self, from_node, to_node, weight=0.0):
		self.from_node = from_node;
		self.to_node = to_node;
		self.weight = weight;

	## Check if this edge is equal to the given edge
	# 
	# @param other_edge (NodeEdge object)
	# <br>	-- the edge to compare to
	#
	# @return (boolean)
	# <br>	-- `True` if equal, `False` otherwise
	#
	def __eq__(self, other_edge):
		if other_edge is None:
			return False;
		return other_edge.from_node == self.from_node and other_edge.to_node == self.to_node and other_edge.weight == self.weight;


	## Compare this edge to another edge
	# 
	# @param other_edge (NodeEdge object)
	# <br>	-- the edge to compare to
	#
	# @return (int)
	# <br>	-- negative if this NodeEdge is "less than" the other, 0 if
	# 	equal, and positive if this is "greater than" the other
	#
	def __cmp__(self, other_edge):
		if self.__eq__(other_edge):
			return 0;
		return self.weight - other_edge.weight;

	
	## Check if this edge is less than another edge
	# 
	# @param other_edge (NodeEdge object)
	# <br>	-- the edge to compare to
	#
	# @return (boolean)
	# <br>	-- `True` if `self.__cmp__(other_edge)` is negative,
	# 	`False` otherwise.
	#
	def __lt__(self, other_edge):
		return self.__cmp__(other_edge) < 0;


	## Check if this edge is greater than another edge
	# 
	# @param other_edge (NodeEdge object)
	# <br>	-- the edge to compare to
	#
	# @return (boolean)
	# <br>	-- `True` if `self.__cmp__(other_edge)` is positive,
	# 	`False` otherwise.
	#
	def __gt__(self, other_edge):
		return 0 < self.__cmp__(other_edge);

## Represents a node in a graph (in particular, the graph used in the
# MultiLevelNavigationAlgorithm).
#
class Node:

	## @var pos (numpy array)
	# <br>	Format: `[x, y]`
	# <br>	-- the location of this Node in the environment
	#
	# @var edges (list of NodeEdge objects)
	# <br>	-- edges to adjacent nodes
	#
	# @var visited (boolean)
	# <br>	-- whether this node has been visited yet (used in the
	# 	MultiLevelNavigationAlgorithm)
	#

	## Constructor
	#
	def __init__(self, pos):
		self.pos = pos;
		self.edges = [];
		self.visited = False;

	## Add an edge with the given weight from this Node to the other node specified.
	#
	# @param other_node (Node object)
	# <br>	-- the other node
	#
	# @param weight (float)
	# <br>	-- the weight of the edge
	#
	def add_connection(self, other_node, weight=1.0):
		edge = NodeEdge(self, other_node, weight);
		self.edges.append(edge);


	## Forms an undirected connection between two nodes, with the specified
	# edge weight.
	#
	def connect_nodes_undirected(node1, node2, weight=1.0):
		node1.add_connection(node2, weight);
		node2.add_connection(node1, weight);

	## Check if this node is equal to the given node
	# 
	# @param other_node (Node object)
	# <br>	-- the node to compare to
	#
	# @return (boolean)
	# <br>	-- `True` if equal, `False` otherwise
	#
	def __eq__(self, other_node):
		if other_node is None:
			return False;
		return np.array_equal(self.pos, other_node.pos);


	## Compare this node to another node
	# 
	# @param other_node (Node object)
	# <br>	-- the node to compare to
	#
	# @return (int)
	# <br>	-- negative if this Node is "less than" the other, 0 if
	# 	equal, and positive if this is "greater than" the other
	#
	def __cmp__(self, other_node):
		if self.__eq__(other_node):
			return 0;
		if other_node is None:
			return -1;
		return int(np.sign(np.sum(self.pos - other_node.pos)));


## The main class for the multi-level navigation algorithm.
#
# The details for the algorithm itself can be found in the 
# [technical spec](@ref md_NavigationAlgorithm_multilevel_technical_spec).
#
class MultiLevelNavigationAlgorithm(AbstractNavigationAlgorithm):

	## @var debug_info (dict)
	# <br>	-- holds information that other classes could use for
	# debugging
	#
	# @var using_safe_mode (boolean)
	# <br>	-- Whether the algorithm is running in "safe mode". This
	# 	does not do anything, and is only included for
	# 	compatibility with other classes
	#

	## Constructor
	#
	# @param robot (\link Robot::Robot Robot \endlink object)
	# <br>	-- the robot this nav algorithm is being used for
	#
	# @param cmdargs (argparse-generated command args)
	# <br>	-- command-line arguments
	#
	# @param using_safe_mode (boolean)
	# <br>	-- Same as the class member variable with the same name.
	# 	Defaults to `True`.
	#
	def __init__(self, robot, cmdargs, using_safe_mode = True):
		self.using_safe_mode = using_safe_mode;
		self._robot = robot;
		self._cmdargs = cmdargs;

		self.debug_info = {};

		self._localplanner = SamplingNavigationAlgorithm(robot, cmdargs);

		self._normal_speed = 10;

		self._POINT_RADIUS = 2;
		self._CHECK_RADIUS = 90;
		self._graph_branch_factor = 22;

		self._node_list = [];
		self._node_list.append(Node(robot.location));
		self._goal_node = Node(robot.target.position);
		self._node_list.append(self._goal_node);

		self._radar_data = np.zeros(robot.radar.get_data_size());
		self._cur_path = [];
		self._cur_path_index = 0;
		self._steps_since_last_waypoint = 0;

	## Selects the next action.
	#
	# @see AbstractNavAlgo.AbstractNavigationAlgorithm.select_next_action
	#
	def select_next_action(self):
		self._radar_data = self._robot.radar.scan(self._robot.location);

		if self._cur_path_index < len(self._cur_path):
			next_waypoint = self._cur_path[self._cur_path_index].to_node;
			if self._is_at_node(next_waypoint):
				self._cur_path_index += 1;
				self._steps_since_last_waypoint = 0
			elif 15 < self._steps_since_last_waypoint:
				last_waypoint = self._cur_path[self._cur_path_index].from_node;
				for edge in last_waypoint.edges:
					if edge.to_node == next_waypoint:
						edge.weight = float("inf");
				node = Node(self._robot.location);
				self._node_list.append(node);
				self._update_global_plan();
		if not (self._cur_path_index < len(self._cur_path)):
			self._update_global_plan();

		self._steps_since_last_waypoint += 1
		return self._select_next_action_local();


	def _update_global_plan(self):
		cur_pos = self._robot.location;
		cur_node = self._get_closest_node_to(cur_pos)

		if not self._is_at_node(cur_node):
			new_node = Node(cur_pos);
			self._node_list.append(new_node);
			cur_node = new_node;

		tbc_points = self._get_nodes_to_be_checked(cur_node);

		for node in tbc_points:
			weight = float("inf");
			if self._has_local_path_to(node.pos):
				weight = Vector.getDistanceBetweenPoints(node.pos, cur_node.pos)
			# Update edge
			Node.connect_nodes_undirected(cur_node, node, weight);

		cur_node.visited = True;

		next_node, path = self._find_next_node_to_explore(cur_node, heuristic=self._euclidean_heuristic);
		if next_node is None:
			for i in range(int(len(self._node_list)/4)):
				self._node_list[np.random.randint(len(self._node_list))].visited = False;
			self._cur_path_index -= 1;
			self._graph_branch_factor += 1;
			return;
		self._cur_path = path;
		self._cur_path_index = 1;


	def _select_next_action_local(self):
		next_waypoint = self._cur_path[self._cur_path_index].to_node;
		angle = Vector.getAngleBetweenPoints(self._robot.location, next_waypoint.pos);
		speed = Vector.getDistanceBetweenPoints(self._robot.location, next_waypoint.pos);
		if self._normal_speed < speed:
			speed = self._normal_speed;
		return RobotControlInput(speed, angle);


	def _is_at_node(self, node):
		return Vector.getDistanceBetweenPoints(self._robot.location, node.pos) <= self._POINT_RADIUS;


	def _find_next_node_to_explore(self, start_node, heuristic=None):
		if heuristic is None:
			heuristic = self._null_heuristic;
		frontier = PriorityQueue();
		initial_path = [NodeEdge(start_node, start_node, weight=0.0)];
		initial_path_cost = self._get_edgepath_cost(initial_path);
		initial_path_heuristic_value = heuristic(initial_path[-1].to_node);
		frontier.put_nowait((initial_path_cost+initial_path_heuristic_value, initial_path));
		visited = [];

		while True:
			if frontier.empty():
				return None, None;
			cur_state = frontier.get_nowait()[1];
			cur_edge = cur_state[-1];
			cur_node = cur_edge.to_node;
			if cur_node == self._goal_node or not cur_node.visited:
				return cur_node, cur_state;
			if cur_node in visited:
				continue;
			else:
				visited.append(cur_node);
			for edge in cur_node.edges:
				successor = cur_state[:] + [edge];
				cost = self._get_edgepath_cost(successor);
				heuristic_value = 0.8*heuristic(edge.to_node);
				if cost < float("inf"):
					frontier.put_nowait((cost+heuristic_value, successor));


	def _find_path(self, start_node, end_node, heuristic=None):
		if heuristic is None:
			heuristic = self._null_heuristic;
		frontier = PriorityQueue();
		initial_path = [NodeEdge(start_node, start_node, weight=0.0)];
		initial_path_cost = self._get_edgepath_cost(initial_path);
		initial_path_heuristic_value = heuristic(initial_path[-1].to_node);
		frontier.put_nowait((initial_path_cost+initial_path_heuristic_value, initial_path));
		visited = [];

		while True:
			if frontier.empty():
				return None;
			cur_state = frontier.get_nowait()[1];
			cur_edge = cur_state[-1];
			cur_node = cur_edge.to_node;
			if cur_node == end_node:
				return cur_state;
			visited.append(cur_node)
			for edge in cur_node.edges:
				if edge.to_node not in visited:
					successor = cur_state[:] + [edge];
					cost = self._get_edgepath_cost(successor);
					heuristic_value = heuristic(edge.to_node);
					if cost < float("inf"):
						frontier.put_nowait((cost+heuristic_value, successor));
				


	## Get the cost of a path, where the path is given as a list of edges
	#
	def _get_edgepath_cost(self, path):
		cost = 0;
		for edge in path:
			cost += edge.weight;
		return cost;


	def _null_heuristic(self, node):
		return 0;


	def _euclidean_heuristic(self, node):
		return Vector.getDistanceBetweenPoints(node.pos, self._goal_node.pos);


	def _get_closest_node_to(self, pos):
		if len(self._node_list) == 0:
			return None;
		closest = self._node_list[0];
		min_dist2 = np.dot(closest.pos - pos, closest.pos - pos);
		for node in self._node_list:
			vec = node.pos - pos;
			dist2 = np.dot(vec, vec);
			if dist2 < min_dist2:
				min_dist2 = dist2;
				closest = node;
		return closest;


	def _get_nodes_to_be_checked(self, cur_node):
		check_points = [];

		# Step 1.a: include pre-existing nearby points
		check_radius_squared = self._CHECK_RADIUS * self._CHECK_RADIUS;
		for node in self._node_list:
			vec = node.pos - cur_node.pos;
			if np.dot(vec, vec) < check_radius_squared:
				check_points.append(node);

		# Step 1.b: Generate new points
		if len(check_points) < self._graph_branch_factor:
			max_dist = self._CHECK_RADIUS / 1.01;
			min_dist = self._CHECK_RADIUS / 3.0;
			for i in range(0, 40):
				# Generate a new point in the robot's visual range
				angle = float(i)*180/20.0
				dist = np.random.uniform(min(max_dist, self._radar_data[int(np.round(angle/self._robot.radar.get_degree_step()))]) - min_dist) + min_dist;
				vec = Vector.unitVectorFromAngle(angle) * dist;
				node = Node(cur_node.pos + vec);
				should_append = True
				for node2 in self._node_list:
					vec = node2.pos - node.pos;
					if np.dot(vec, vec) < 25*25:
						should_append = False
						break;
				if should_append:
					check_points.append(node);
					self._node_list.append(node);
		return check_points;


	def _has_local_path_to(self, position):
		ang = Vector.getAngleBetweenPoints(self._robot.location, position);
		index = int(np.round(ang)) % 360;

		return Vector.getDistanceBetweenPoints(self._robot.location, position) < self._radar_data[index]-7;
