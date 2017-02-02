#!/usr/bin/python3

## @package ObstaclePredictor
#

import numpy as np;
import Vector
from Counter import Counter
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, fcluster
from collections import defaultdict
from collections import OrderedDict

## Abstract base class for obstacle predictors.
#
# Obstacle predictors use observations of past obstacles to predict future
# locations of obstacles.
# 
# To use this class, the `#add_observation()` method should be called exactly
# once for every time step. If no observation is made for a time step,
# `#add_observation()` should still be called as follows to indicate the
# absence of an observation:
#
# `#add_observation(None, None, None, None)`
# 
#
# The `get_prediction` method is not subject to the same restrictions as
# `#add_observation()`, and may be called as needed, possibly multiple times
# per time step and possibly only once every several time steps.
#
class AbstractObstaclePredictor:
    ## Constructor
    #
    # @param data_size (int)
    # <br>	-- The number of data points in the `radar_data` and
    # `dynamic_obstacle_data` parameters that will be passed to
    # `#add_observation()`
    #
    def __init__(self, data_size):
        self.data_size = data_size;
        pass;

    ## Adds an observation to use when predicting future obstacle
    # states.
    #
    # This method should be called exactly once for each time step.
    # Even if no observations are made for a step, it should be called
    # as `#add_observation(None, None, None, None)`. If this condition
    # is not met, no guarantees are made about the accuracy of
    # `#get_prediction()`.
    #
    # @param location (numpy array)
    # <br>	Format: `[x, y]`
    # <br>	-- The location at which this observation was made
    # 	(location of the robot).
    #
    # @param radar_data (numpy array)
    # <br>	Format: `[ang_1_distance, ang_2_distance, ..., ang_n_distance]`
    # <br>	-- An array containing the distance to the
    # 	nearest obtacle (of any type; static or dynamic) at each of
    # 	a range of angles. The angles should be evenly distributed
    # 	between 0 and 360 degrees, so an array with 6 elements
    # 	would be expected to contain values for angles 0, 60, 120,
    # 	180, 240, and 300, in that order. More generally,
    # 	`radar_data[i]` should correspond to the angle given by
    # 	`i * (360 / len(radar_data))`. The size of the array must
    # 	be the same as the value of `#data_size` that this class
    # 	was initialized with.
    # <br>	See also: `Radar.Radar.scan`
    #
    # @param dynamic_obstacle_data (numpy array)
    # <br>	Format: `[ang_1_distance, ang_2_distance, ..., ang_n_distance]`
    # <br>	-- An array containing the distance to the nearest dynamic
    # 	obstacle at each of a range of angles. This is exactly the
    # 	same as `radar_data`, except that it should contain only
    # 	the data for dynamic obstacles, and not for the static
    # 	ones. Again, it must have exactly `#data_size` elements.
    #
    # @param func_get_dynamic_obstacle_at_angle (function)
    # <br>	-- A function that returns a
    # 	`DynamicObstacle.DynamicObstacle` object given an angle.
    # 	The returned object should be the nearest dynamic obstacle
    # 	at the given angle. The function should be callable as
    # 	follows, if `angle` is the angle (in degrees) to test:
    # <br>	`func_get_dynamic_obstacle_at_angle(angle)`
    # <br>	The caller must guarantee that the function will return the
    # 	correct dynamic obstacle at least until the next time
    # 	`#add_observation()` is called.
    #
    #
    # @returns nothing
    #
    def add_observation(self, location, radar_data, dynamic_obstacle_data, func_get_dynamic_obstacle_at_angle):
        pass;

    ## Gets the probability of an obstacle existing at the specified
    # point at the specified number of steps in the future.
    #
    # @param point (numpy array)
    # <br>	Format `[x, y]`
    # <br>	-- The point to test
    #
    # @param num_steps_in_future (int)
    # <br>	-- The number of steps in the future to check at. This
    # 	starts from 0, so if `num_steps_in_future` is 0 the
    # 	function will return the probability as estimated at the
    # 	time of the most recent observation. If it is 1 the
    # 	function will return the estimated value for one step after
    # 	the most recent observation, and so on.
    #
    #
    # @returns (float)
    # <br>	-- A value in the closed interval [0, 1], representing the
    # 	error occurs, this function returns a negative number.
    #
    def get_prediction(self, point, num_steps_in_future):
        pass;


## This is a basic placeholder implentation of the
# AbstractObstaclePredictor class. Its predictions should not be relied
# upon.
#
class DummyObstaclePredictor(AbstractObstaclePredictor):
    def __init__(self, data_size):
        # Might be good to cache values from observations to use
        # later. Let's initialize them now.
        self.data_size = data_size;
        self.last_location = None;
        self.last_radar_distribution = None;
        self.last_dynamic_obstacle_distribution = None;
        self.last_obstacle_getter_func = None;

    ## Dummy `#add_observation()` method. It has some commented-out
    # examples to illustrate how to do basic things
    #
    def add_observation(self, location, radar_all, radar_dynamic, get_obs_at_angle):
        # We'll need the given values to make up-to-date
        # predictions, so let's store this most recent
        # observation's values. Of course, this is a dummy
        # implementation, so we aren't actually going to do
        # anything with the values.
        self.last_location = location;
        self.last_radar_distribution = radar_all;
        self.last_dynamic_obstacle_distribution = radar_dynamic;

        # This get_obs_at_angle function is especially important to
        # update, since the one passed in from the previous call is
        # no longer guaranteed to work.
        self.last_obstacle_getter_func = get_obs_at_angle;

        # If we wanted to see how close the nearest dynamic
        # obstacle was at the angle 75, we could do this:
        angle = 75;
        index = int(np.round(angle * (self.data_size / 360.0)));
        distance = radar_dynamic[index];

        # If we wanted to, we could try calculate the area covered
        # by the closest dynamic obstacle at angle 75:
        dynobs = get_obs_at_angle(75);
        if dynobs is not None:
            shape = dynobs.shape  # Circle = 1, Rectangle = 2
            area = 0
            if shape == 1:
                area = np.pi * dynobs.radius * dynobs.radius
            elif shape == 2:
                area = dynobs.size[0] * dynobs.size[1]

        # Maybe we want to know exactly where the edge of the
        # dynamic obstacle at angle 75 is. We can start by taking
        # the `distance` variable we computed earlier and using it
        # to scale a unit vector in the specified direction. It
        # should be noted that the Vector.unitVectorFromAngle()
        # method takes an angle in radians, unlike most other
        # methods
        edge_point = location + (distance * Vector.unitVectorFromAngle(75 * np.pi / 180));

    ## Dummy method to get predictions
    #
    def get_prediction(self, location, time):
        # This method would use the data from previously added
        # observations to figure out where obstacles will be in the
        # future.

        # If we determined that there is a 62% chance of an
        # obstacle being at the point `location` at `time` steps in
        # the future, we could write:
        # return 0.62

        # Since this is just a dummy class, we aren't going to make
        # any predictions
        return -1;


## HMM-based obstacle predictor
#
# This is just a skeleton for now. More will be added later
#
class HMMObstaclePredictor(AbstractObstaclePredictor):
    ## See the corresponding superclass method for details
    #
    def __init__(self, data_size):
        self.data_size = data_size;
        self.radar_range = 100;
        self.obs_predictions = Counter();
        self.transitionProb = 0.9
        self.max_vel = 30 #Maximum velocity of obstacle
        self.max_prob = 0.9 #Maximum possible pobability
        self.neighbour_range = 20
        self.future_obs_points = {}

        self.last_clustered_obs = None
        self.current_clustered_obs = None

        #DEBUG
        self.dynamic_obstacles = {}

        ## See the corresponding superclass method for details
    #
    def add_observation(self, location, radar_all, radar_dynamic, get_obs_at_angle):

        #Reset prediction grid every time stamp
        self.obs_predictions = Counter();
        self.dynamic_obstacles = {}

        obstacle_points = self._convert_radar_to_grid(location, radar_dynamic, get_obs_at_angle)

        clustered_obs = self._cluster_points(obstacle_points)

        #DEBUG
        # if(len(self.current_clustered_obs) != len(self.dynamic_obstacles)):
        #     with open("incorrect.txt", "a") as myfile:
        #         myfile.write("1\n")
        #
        # with open("total.txt", "a") as myfile:
        #     myfile.write("1\n")
        #END DEBUG

        if(clustered_obs):
            self._map_obs_and_assign_prob(clustered_obs)
        else:
            self.current_clustered_obs = None

        self.last_clustered_obs = self.current_clustered_obs

    ## See the corresponding superclass method for details
    #
    def get_prediction(self, location, time):
        #calculate vector from robot location to the requested location

        grid_cell = tuple(np.array(location, dtype=np.int32).tolist());
        return self.obs_predictions[grid_cell];

    def _convert_radar_to_grid(self, location, radar_dynamic, get_obs_at_angle):
        obstacle_points = []
        obs_id = 0

        #Construct the grid out of radar data.
        for angle in range(360):
            index = int(np.round(angle * (self.data_size / 360.0)));
            distance = radar_dynamic[index];

            if distance != self.radar_range:
                obs_coordinate = (location + (distance * Vector.unitVectorFromAngle(angle * np.pi / 180)));
                obs_cell = tuple(np.array(obs_coordinate, dtype=np.int32).tolist());
                obstacle_points.append(obs_cell)

                #DEBUG
                dynamic_obs = get_obs_at_angle(angle);
                if dynamic_obs not in self.dynamic_obstacles.keys():
                    self.dynamic_obstacles[dynamic_obs] = obs_id;
                    obs_id += 1
                #END DEBUG

        return obstacle_points

    def _cluster_points(self, obstacle_points):
        clustered_obs = {}

        if(obstacle_points):
            #Cluster obstacle points
            Y = pdist(obstacle_points, 'euclidean')
            Z = linkage(Y, 'single', 'euclidean')
            F = fcluster(Z, 4, 'distance')

            #Assign an id to each point
            index = 0
            while index < len(obstacle_points):
                clustered_obs[obstacle_points[index]] = F[index]
                index += 1

            self.current_clustered_obs = self._switch_key_value(clustered_obs)
        return clustered_obs

    def _map_obs_and_assign_prob(self, clustered_obs):
        # Remove obstacles that has less than 3 observed points
        for k, v in list(self.current_clustered_obs.items()):
            if len(v) < 3:
                del self.current_clustered_obs[k]

        if self.last_clustered_obs:
            # Map last time stamp's obstacle with current obstacles
            distances, angles = self._get_obs_matrix(self.current_clustered_obs.copy(), self.last_clustered_obs.copy())

            # Calculate future posiiton of obstacles and assign probability
            for obs_point, id in clustered_obs.items():
                if id in distances.keys():
                    if len(distances[id].values()) == 0:
                        a = 10
                    distance = list(distances[id].values())[0]
                    angle = list(angles[id].values())[0]
                    future_obs_coordinate = (obs_point + (distance * Vector.unitVectorFromAngle(angle * np.pi / 180)));
                    future_obs_cell = tuple(np.array(future_obs_coordinate, dtype=np.int32).tolist());
                    self._assignProb(future_obs_cell)

    def _switch_key_value(self, grid_dynamic_obs):

        new_dict = defaultdict(list)

        for k, v in grid_dynamic_obs.items():
            new_dict[v].append(k)

        return new_dict

    def _get_obs_matrix(self, clustered_obs_fliped, last_clustered_obs_fliped):

        distances = {}
        angles = {}
        temp = []

        for id, points in clustered_obs_fliped.items():
            low, high = self._get_end_points(points)
            mid = (float(low[0] + high[0])/ 2 , float(low[1] + high[1])/ 2)

            if last_clustered_obs_fliped:
                distances[id] = {}
                angles[id] = {}
                for last_id, last_points in last_clustered_obs_fliped.items():
                    last_low, last_high = self._get_end_points(last_points)
                    last_mid = (float(last_low[0] + last_high[0]) / 2, float(last_low[1] + last_high[1]) / 2)

                    d1 = Vector.getDistanceBetweenPoints(last_low, low)
                    d2 = Vector.getDistanceBetweenPoints(last_high, high)
                    d = (d1 + d2 / 2)
                    distances[id][last_id] = d

                    angle = Vector.getAngleBetweenPoints(last_mid, mid)
                    angles[id][last_id] = angle

        x = 0
        confirmed_ids = []
        for k,v in distances.items():
            for last_id, dis in list(distances[k].items()):
                if dis > self.max_vel:
                    temp.append(dis)
                    del distances[k][last_id]
                    del angles[k][last_id]

            if len(distances[k]) == 1:
                confirmed_ids.append(list(distances[k].keys())[0])
            else:
                #If there is more than one possibilities
                x += 1

        # Delete keys with empty values (i.e obstacles that are newly introduced in this time stamp)
        for k, v in list(distances.items()):
            if len(v) == 0:
                del distances[k]
                del angles[k]

        if x > 0:
            # Order by min distance
            distances = OrderedDict(sorted(distances.items(), key=lambda t: min(t[1].values())))

            a = len(distances)

            for k,v in distances.items():
                while len(distances[k]) > 1:
                    minimum = min(distances[k].values())
                    #get ket from value
                    minimum_id = list(distances[k].keys())[list(distances[k].values()).index(minimum)]
                    if minimum_id in confirmed_ids:
                        del distances[k][minimum_id]
                        del angles[k][minimum_id]
                        if len(distances[k]) == 1:
                            confirmed_ids.append(list(distances[k].keys())[0])
                    else:
                        distances[k] = {}
                        distances[k][minimum_id] = minimum
                        angle = angles[k][minimum_id]
                        angles[k] = {}
                        angles[k][minimum_id] = angle
                        confirmed_ids.append(minimum_id)

        return distances, angles

    def _get_end_points(self, points_list):

        low = (float("inf"), float("inf"))
        high = (float("-inf"), float("-inf"))

        for x,y in points_list:
            if x < low[0]:
                low = (x, y)
            if x > high[0]:
                high = (x, y)

        return (low, high)

    def _assignProb(self, obs_point):
        neigh_points = self._generate_neighbour_points(obs_point)
        for point in neigh_points:
            prob = 1 - Vector.getDistanceBetweenPoints(point, obs_point) * 0.05
            if prob > self.obs_predictions[point]:
                self.obs_predictions[point] = prob

    def _generate_neighbour_points(self, point):
        result = []
        result.append(point)
        i = -self.neighbour_range
        while i < self.neighbour_range:
            j = -self.neighbour_range
            while j < self.neighbour_range:
                result.append((point[0] + i, point[1] + j))
                j += 1
            i += 1
        return result
