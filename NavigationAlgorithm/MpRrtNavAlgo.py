#!/usr/bin/python3


import numpy    as np
import Vector, time
from math import *
from .AbstractNavAlgo import AbstractNavigationAlgorithm
from ObstaclePredictor import HMMObstaclePredictor
from Robot import RobotControlInput

## Implementation of the Dynamic Window algorithm for robotic navigation.
#
# @see
# \ref AbstractNavAlgo.AbstractNavigationAlgorithm
#               "AbstractNavigationAlgorithm"
#
class MpRrtNavigationAlgorithm(AbstractNavigationAlgorithm):
        def __init__(self, robot, cmdargs):
                # Init basic members
                self._robot = robot;
                self._cmdargs = cmdargs;
                self._data_size = robot.radar.get_data_size();
                self._radar_range = robot.radar.radius;
                self._radar_resolution = robot.radar.resolution;
                self._dynamic_radar_data = self._robot.radar.scan_dynamic_obstacles(self._robot.location);
                self._robot_speed = cmdargs.robot_speed;
                self._target = self._robot.target.position;

                #Algo
                self._maxstepsize = self._robot_speed * 2;
                self._goalThreshold = self._robot_speed * 0.75; #In pixel distance
                self._goalBias = 0.05; #As mentioned in the paper
                self._forestBias = 0.1; #As mentioned in the paper
                self._maxRrtSize = 5000;
                self._forest = Forest();

                #Time Dimention
                self._time = 0;
                self._minTimeMultiplier = 3;
                self._maxPredictTime = 5;
                self._obstacle_predictor = HMMObstaclePredictor(360, robot.radar.radius, self._maxPredictTime);


                self.debug_info = {"path": [], "path2": []}

                #Make initial RRT from start to goal
                self._solution = [];
                self._rrt = Tree(Node((self._robot.location[0], self._robot.location[1], self._time)));
                qgoal = Node((self._target[0], self._target[1], self._minTimeMultiplier * self._minTime(self._robot.location, self._target)));
                self._status = self._grow_rrt(self._rrt, qgoal, self._goalThreshold, False);
                self._extract_solution();

                # Set using_safe_mode to appease Robot.draw()
                self.using_safe_mode = False;

                self._last_solution_node = Node((int(self._robot.location[0]), int(self._robot.location[1]), self._time));
                self._has_given_up = False;

        ## Next action selector method.
        #
        # @see 
        # \ref AbstractNavAlgo.AbstractNavigationAlgorithm.select_next_action
        #               "AbstractNavigationAlgorithm.select_next_action()"
        #
        def select_next_action(self):
                #Scan the radar
                self._dynamic_radar_data = self._robot.radar.scan_dynamic_obstacles(self._robot.location);
                self._radar_data = self._robot.radar.scan(self._robot.location);

                # Give the current observation to the obstacle motion predictor
                self._obstacle_predictor.add_observation(self._robot.location,
                        self._radar_data,
                        self._dynamic_radar_data,
                        self._obstacle_predictor_dynobs_getter_func
                );

                if self._last_solution_node.data != (int(self._robot.location[0]), int(self._robot.location[1]), self._time):
                        self._solution.insert(0, self._last_solution_node)

                self._pruneAndPrepend();
              
                if not self._rrt.hasGoal(self._target, self._goalThreshold):
                        self._rrt = Tree(Node((self._robot.location[0], self._robot.location[1], self._time)));
                        qgoal = Node((self._target[0], self._target[1], self._minTimeMultiplier * self._minTime(self._robot.location, self._target)));
                        self._status = self._grow_rrt(self._rrt, qgoal, self._goalThreshold, True);
                        self._extract_solution();

                if self._status == 0:
                        #There is a valid path from robot to goal
                        while 0 < len(self._solution) and (Vector.distance_between(self._robot.location, self._solution[0].data[:2]) < 1.5 or self._solution[0].data[2] <= self._time):
                                del self._solution[0];

                        timeDiff = self._solution[0].data[2] - self._time; #Should always be > 0
                        direction = Vector.degrees_between(self._robot.location, self._solution[0].data[:2]);
                        dist = min(self._maxstepsize, Vector.distance_between(self._robot.location, self._solution[0].data[:2]) / timeDiff);
                        self.debug_info["path"] = self._solution;
                        self._last_solution_node = self._solution[0];
                        self._time += 1;
                if self._status == 1:
                        #No valid path found
                        self._has_given_up = True
                        dist = 0
                        direction = np.random.uniform(low=0, high=360);
                if self._status == 2:
                        #Robot or goal is inside dynamic obstacle
                        dist = 0
                        direction = np.random.uniform(low=0, high=360);

                return RobotControlInput(dist, direction);


        def has_given_up(self):
                return self._has_given_up

        def _minTime(self, sPoint, gPoint):
                return  np.ceil(Vector.distance_between(sPoint, gPoint) / self._robot_speed);

        def _grow_rrt(self, tree, qgoal, goalThreshold, useForest):

               # grid_data = self._robot.radar._env.grid_data;
                if self._collides(None, tree.root.data, True):
                        return 2;
                if self._collides(None, qgoal.data, True):
                        return 2;

                foundGoal = False;
                count = 0;

                while not foundGoal and count < self._maxRrtSize:
                        qTarget = self._chose_target(qgoal);
                        qNearest = self._nearest_neighbour(tree, qTarget);
                        
                        if useForest and qTarget in self._forest.toList():
                                if self._connect(qNearest, qTarget):
                                        self._forest.removeSubTree(qTarget);
                                        if tree.hasGoal(qgoal.data[:2], goalThreshold):
                                                foundGoal = True;
                        else:
                                qNew = self._extend(qNearest, qTarget)

                                if not self._collides(qNearest.data, qNew.data, False):
                                        if qNew.data not in tree.toDataList():
                                                if qNearest.addChild(qNew): #addChild prohibits cycles in tree
                                                        if tree.hasGoal(qgoal.data[:2], goalThreshold):
                                                                foundGoal = True
                                                        count += 1

                if foundGoal:
                        return 0;
                else:
                        return 1;

        def _pruneAndPrepend(self):
                # Check if there is any dynamic obstacle within radar range
                # Prune
                dynamic_obstacle_points = self._convert_radar_to_grid()
                invalidTreeNodes = []
                if len(dynamic_obstacle_points) > 0:
                        nearby_nodes = self._rrt.get_nearby_nodes(self._robot.location, self._radar_range)
                        for node in nearby_nodes:
                                if not self._isNodeReachable(node):
                                        node.disconnect(); #Don't add to forest
                                        continue;
        
                                if node.parent and self._collides(node.parent.data, node.data, True):
                                        node.disconnect();
                                        invalidTreeNodes.append(node);

                        nearby_nodes = self._forest.get_nearby_nodes(self._robot.location, self._radar_range);
                        for node in nearby_nodes:
                                if not self._isNodeReachable(node):
                                        self._forest.delete(node);
                                        continue;
                                if node.parent:
                                        if self._collides(node.parent.data, node.data, True):
                                                self._forest.disconnect(node);

                        for node in invalidTreeNodes:
                                self._forest.addSubTree(node);

                #Prepend
                robot_location = (int(self._robot.location[0]), int(self._robot.location[1]))
                if self._rrt.root.data[:2] != robot_location and len(self._solution) > 0:
                        if self._solution[0].data[:2] != robot_location:
                                #Set root of the tree to robot's current position
                                self._rrt = Tree(Node((self._robot.location[0], self._robot.location[1], self._time)));

                                if not self._connect(self._rrt.root, self._solution[0]):
                                        #If can't connect to the previous tree, put the whole tree to forest
                                        self._forest.addSubTree(self._solution[0])
                                        self._rrt = Tree(Node((self._robot.location[0], self._robot.location[1], self._time)));
                                        qgoal = Node((self._target[0], self._target[1], self._minTimeMultiplier * self._minTime(self._robot.location, self._target)));
                                        self._grow_rrt(self._rrt, qgoal, self._goalThreshold, True);
                        else:
                                self._rrt = Tree(self._solution[0])

        def _isNodeReachable(self, node):
                timeOffset = node.data[2] - self._time;
                if timeOffset <= 0:
                        return False;

                if self._minTime(self._robot.location, node.data[:2]) > timeOffset:
                        return False;

                return True;

        def _chose_target(self, qgoal):
                randReal = np.random.uniform(0.0, 1.0);

                if randReal < self._goalBias:
                        return qgoal;
                else:
                        if randReal < (self._goalBias + self._forestBias) and not self._forest.isEmpty():
                                rand_node = self._forest.getRandomRoot();
                                if not self._collides(None, rand_node.data, False):
                                        return rand_node
                                else:
                                        return self._get_safe_random_node();
                        else:
                                return self._get_safe_random_node();

        def _extract_solution(self):
                self._solution = []; 
                visited = [];

                frontier = Stack();
               
                root = self._rrt.root;

                currentpath = [root];
                frontier.push((root, currentpath));

                while not frontier.isEmpty():
                        currentNode, currentpath = frontier.pop();
                        if currentNode.data not in visited:
                                visited.append(currentNode.data)

                                if Vector.distance_between(currentNode.data[:2], self._robot.target.position) < self._goalThreshold:
                                        self._solution = currentpath;
                                        break;
                                childrenNodes = currentNode.children;
                                for childnode in childrenNodes:
                                        newPath = currentpath + [childnode];
                                        frontier.push((childnode, newPath));
                
                return self._solution;


        def _nearest_neighbour(self, tree, qTarget):
                tree_nodes = tree.toList();

                nearest_node = min(tree_nodes, key=lambda t: (t.data[0]-qTarget.data[0])**2 + (t.data[1]-qTarget.data[1])**2)

                return nearest_node

        def _extend(self, n1, n2):
                p1 = n1.data[:2];
                p2 = n2.data[:2];
                if Vector.getDistanceBetweenPoints(p1, p2) < self._maxstepsize:
                        return n2;
                else:
                        theta = atan2(p2[1] - p1[1], p2[0] - p1[0]);
                        x = p1[0] + self._maxstepsize * cos(theta);
                        y = p1[1] + self._maxstepsize * sin(theta);
                        t = int(np.random.uniform(n1.data[2], n1.data[2] + self._minTimeMultiplier * self._minTime(n1.data[:2], (x,y) )));
                        return Node((x, y, t));

        def _connect(self, n1, n2):
                if self._collides(n1.data, n2.data, False):
                        return False;
                else:
                        qNew = n1;
                        while(qNew.data != n2.data):
                                qTemp = self._extend(qNew, n2);
                                qNew.addChild(qTemp);
                                qNew = qTemp;
                        return True;


        def _get_safe_random_node(self):
                while True:
                        rand_point = self._get_random_point(); #3D point
                        if not self._collides(None, rand_point, False):
                                return Node(rand_point)

        def _collides(self, fromData, toData, dynamicOnly):
                toPoint = toData[:2];
                grid_data = self._robot.radar._env.grid_data;

                if fromData is not None:
                        fromPoint = fromData[:2];
                        timeOffset = toData[2] - fromData[2]; 
                        
                        ang_in_radians = Vector.degrees_between(fromPoint, toPoint) * np.pi / 180
                        dist = Vector.getDistanceBetweenPoints(fromPoint, toPoint)

                        cos_cached = np.cos(ang_in_radians)
                        sin_cached = np.sin(ang_in_radians)
                        for i in np.arange(0, dist, 0.5):
                                x = int(cos_cached * i + fromPoint[0])
                                y = int(sin_cached * i + fromPoint[1])
                                if grid_data[x][y] & 1 and Vector.distance_between((x,y), self._robot.location) < self._robot.radar.radius:
                                        return True
                                if timeOffset > 0 and timeOffset <= self._maxPredictTime:
                                        for i in np.arange(1, timeOffset, 1):
                                                if self._obstacle_predictor.get_prediction((x,y), i) > 0.5:
                                                        return True;
                                if not dynamicOnly:
                                        if grid_data[x][y] & 4:
                                                return True
                else:
                                # Check for dynamic obstacle
                        timeOffset = toData[2] - self._time;
                        if timeOffset > 0 and timeOffset <= self._maxPredictTime:
                                for i in np.arange(1, timeOffset, 1):
                                        if self._obstacle_predictor.get_prediction(toPoint, i) > 0.5:
                                                return True;


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
                XDIM = 800;
                YDIM = 600;
                x = np.random.random() * XDIM;
                y = np.random.random() * YDIM; 
                t = int(np.random.uniform(self._time, self._time + self._minTimeMultiplier * self._minTime(self._robot.location, (x,y) )));
                return x, y, t;

        def _obstacle_predictor_dynobs_getter_func(self, angle):
                return self._robot.radar.get_dynobs_at_angle(self._robot.location, angle);

class Tree:

        def __init__(self, root):
                self.root = root;
                self.isListUpToDate = True;

        def toList(self):
                return self.root.toList();

        def toPointList(self):
                return [node.data[:2] for node in self.root.toList()]
        
        def toDataList(self):
                return [node.data for node in self.root.toList()]

        def get_nearby_nodes(self, center, distance):
                all_nodes = self.toList();
                nearby_nodes = []

                for node in all_nodes:
                        if Vector.getDistanceBetweenPoints(center, node.data[:2]) <= distance:
                                nearby_nodes.append(node)

                return nearby_nodes

        def hasGoal(self, goalPoint, goalThreshold):
                if len(self.get_nearby_nodes(goalPoint, goalThreshold)) > 0:
                        return True;
                else:
                        return False; 

class Node:

        def __init__(self, data):
                self.data = tuple((int(data[0]), int(data[1]), int(data[2])));
                self.children = [];
                self.parent = None;

        def addChild(self, child):
                if self.data in child.toDataList():
                        return False;

                if child.parent:
                        child.parent.children.remove(child);

                self.children.append(child);
                child.parent = self;
                return True;

        def toList(self):
                result = []

                frontier = Stack();
                frontier.push(self);

                for node in self.children:
                        frontier.push(node)

                while True:
                        currentNode = frontier.pop();
                        result.append(currentNode);
                        if frontier.isEmpty():
                                return result;
                        else:
                                for node in currentNode.children:
                                        frontier.push(node);

        def toPointList(self):
                pointList = []
                for node in self.toList():
                        pointList.append(node.data[:2])
                return pointList;
        
        def toDataList(self):
                dataList = []
                for node in self.toList():
                        dataList.append(node.data)
                return dataList;

        def disconnect(self):
                if self.parent:
                        self.parent.children.remove(self);
                        self.parent = None;

class Forest:
        def __init__(self):
                self._subTreeRoots = [];
                self._nodeList = [];
                self._isListUpToDate = True;

        def isEmpty(self):
                if self._subTreeRoots:
                        return False;
                else:
                        return True;

        def addSubTree(self, root):
                self._isListUpToDate = False;
                for node in self._subTreeRoots:
                        if node.data == root.data:
                                index = self._subTreeRoots.index(node);
                                self._subTreeRoots[index] = root;
                                return;

                self._subTreeRoots.append(root);

        def removeSubTree(self, root):
                if root in self._subTreeRoots:
                        self._subTreeRoots.remove(root);
                        self._isListUpToDate = False;

        def disconnect(self, node):
                if node.parent:
                        node.parent.children.remove(node);
                        node.parent = None;
                        self.addSubTree(node);
                else:
                        #Node is a root and already exist in the forest
                        pass;

        def delete(self, node):
                if node.parent:
                        node.parent.children.remove(node);
                        node.parent = None;
                        self._isListUpToDate = False;
                else:
                        self.removeSubTree(node);

        def get_nearby_nodes(self, center, distance):
                all_nodes = self.toList();
                nearby_nodes = [];

                for node in all_nodes:
                        if Vector.distance_between(center, node.data[:2]) <= distance:
                                nearby_nodes.append(node)

                return all_nodes;

        def toList(self):
                if not self._isListUpToDate:
                        all_nodes = set();
                        for root in self._subTreeRoots:
                                all_nodes.update(root.toList());
                
                        self._nodeList = list(all_nodes); 
                        self._isListUpToDate = True;
                
                return self._nodeList;

        def getSubTreeRoots(self):
                return self._subTreeRoots;

        def getRandomRoot(self):
                if len(self._subTreeRoots) == 1:
                        return self._subTreeRoots[0];
                else:
                        if len(self._subTreeRoots) > 1:
                                randInt = np.random.randint(0, len(self._subTreeRoots) - 1);
                                return self._subTreeRoots[randInt];


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

