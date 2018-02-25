

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


	def get_neighbors(self):
		return self._neighbors


## Holds a graph that represents a roadmap of the environment.
# 
class GraphRoadmap:
	def __init__(self):
		self._nodes = set()


	## Add a node to this graph
	# 
	def add_node(self, node):
		self._nodes.add(node)

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


	def find_path(self, start_node, end_node):
		def euclidean_heuristic(node):
			return Vector.magnitudeOf(np.subtract(end_node.location, node.location))

		def goal_test(node):
			return node == end_node

		return GraphRoadmap.graph_search(start_node, goal_test, euclidean_heuristic)

