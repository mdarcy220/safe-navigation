

import Vector
from GeometricRadar import GeometricRadar

## @package EventSensor
#

## A sensor for generic events occuring in the environment
#
#
class EventSensor:
	##
	# @param robot
	# <br>  -- The robot this sensor is attached to
	#
	# @param event_map
	# <br>  -- The EventMap object to check for events.
	#
	# @param detection_range
	# <br>  -- The range of this detector. Only events within this range of the robot will be detected/handled by the sensor.
	#
	def __init__(self, robot, event_map, env, detection_range=float('inf')):
		self._robot = robot;
		self._event_map = event_map
		self._env = env
		self._radar = GeometricRadar(env)
		self._detection_range = detection_range


	def get_events(self):
		events = []
		for event in self._event_map.get_events():
			if Vector.distance_between(event.location, self._robot.location) <= self._detection_range and not self._obs_on_line([event.location, self._robot.location]):
				events.append(event)

		return events


	def _obs_on_line(self, line):
		for obs in self._env.static_obstacles:
			if self._radar._obs_dist_along_line(obs, line) < float('inf'):
				return True
		return False


	## Clears events within the detection range
	#
	# This will remove all events within the detection range from the event
	# map. This means other sensors viewing the same EventMap will also
	# cease to see the handled events.
	#
	def handle_all_events(self):
		for event in self.get_events():
			self._event_map.remove_event(event)


