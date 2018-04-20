

import queue
import Vector
import numpy as np

## @package GraphRoadmap
#


class GraphNode:
	def __init__(self, location, neighbors=None):
		if neighbors is None:
			neighbors = dict()
		self.location = location
		self._neighbors = neighbors


	## Add a neighbor
	# 
	# @param adjacent_node (GraphAdjacentNode object)
	# 
	def add_neighbor(self, node, cost):
		self._neighbors[node] = cost
		if self not in node._neighbors:
			node.add_neighbor(self, cost)


	def remove_neighbor(self, neighbor):
		if neighbor not in self._neighbors:
			return

		if self in neighbor._neighbors:
			del neighbor._neighbors[self]

		del self._neighbors[neighbor]


	def get_neighbors(self):
		return self._neighbors


	def __lt__(self, other):
		if not isinstance(other, GraphNode):
			return True
		return id(self) < id(other)


## Holds a graph that represents a roadmap of the environment.
# 
class GraphRoadmap:
	def __init__(self):
		self._nodes = set()
		self._path_cache = dict()


	## Add a node to this graph
	# 
	def add_node(self, node):
		self._nodes.add(node)


	def remove_node(self, node):
		for neighbor in node.get_neighbors():
			node.remove_neighbor(neighbor)

		self._nodes.remove(node)


	def get_nodes(self):
		return self._nodes

	def graph_search(start_node, goal_test, heuristic=None, frontierType=queue.PriorityQueue):
		if heuristic is None:
			heuristic = lambda state: 0
		visited = set()

		frontier = frontierType()
		frontier.put_nowait((0, start_node, []))

		while not frontier.empty():
			curCost, curState, curActionList = frontier.get_nowait()

			if curState in visited:
				continue

			visited.add(curState)

			if goal_test(curState):
				return curActionList

			neighbor_costs = curState.get_neighbors()
			for successor in neighbor_costs:
				newState = successor
				newActionList = curActionList + [successor]

				# Subtract heuristic(curState) because it included the heuristic
				# added in when it was put on the frontier
				newCost = curCost + neighbor_costs[successor] + heuristic(successor) - heuristic(curState)

				frontier.put_nowait((newCost, newState, newActionList))
		return []


	## Finds a path between two nodes
	#
	# @return path_list
	# <br>  Format: `[node1, node2, ...]`
	# <br>  -- A path consisting of a list of nodes. Note that the path
	#          does not include start_node, but does include end_node.
	#
	def find_path(self, start_node, end_node):
		def euclidean_heuristic(node):
			return Vector.magnitudeOf(np.subtract(end_node.location, node.location))

		def goal_test(node):
			return node == end_node

		if start_node not in self._path_cache:
			self._path_cache[start_node] = dict()

		if end_node not in self._path_cache[start_node]:
			self._path_cache[start_node][end_node] = GraphRoadmap.graph_search(start_node, goal_test, euclidean_heuristic)

		# Make sure to do a copy here, since the caller may modify the
		# returned path
		return [node for node in self._path_cache[start_node][end_node]]



	def path_cost(self, path, start_loc=None):
		if len(path) == 0:
			return 0

		if start_loc is None:
			start_loc = path[0].location

		cost = Vector.distance_between(start_loc, path[0].location)
		prev_node = path[0]
		for node in path:
			# Assume node is in the neighbors of prev_node. This is
			# a bit unsafe, but it is the caller's job to make sure
			# the path is valid.
			cost += prev_node.get_neighbors()[node]
			prev_node = node

		return cost


	def draw(self, dtool):
		dtool.set_color((30,30,60));
		for node in self.get_nodes():
			x = node.location[0]
			y = node.location[1]
			dtool.set_stroke_width(0);
			dtool.draw_circle((x,y), 3)
			#dtool.set_stroke_width(1);
			#for neighbor in node.get_neighbors():
			#	dtool.draw_line((x,y), (neighbor.location[0], neighbor.location[1]))

