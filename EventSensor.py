

import Vector

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
	def __init__(self, robot, event_map, detection_range=float('inf')):
		self._robot = robot;
		self._event_map = event_map
		self._detection_range = detection_range


	def get_events(self):
		events = []
		for event in self._event_map.get_events():
			if Vector.distance_between(event.location, self._robot.location) <= self._detection_range:
				events.append(event)

		return events


	## Clears events within the detection range
	#
	# This will remove all events within the detection range from the event
	# map. This means other sensors viewing the same EventMap will also
	# cease to see the handled events.
	#
	def handle_all_events(self):
		removal_set = set()
		for event in self._event_map.get_events():
			if Vector.distance_between(event.location, self._robot.location) <= self._detection_range:
				removal_set.add(event)
		for event in removal_set:
			self._event_map.remove_event(event)


