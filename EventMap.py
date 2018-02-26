

import numpy as np

## @package EventMap
#


class Event:
	def __init__(self, location, time):
		self.location = location
		self.time = time


class EventMap:
	##
	#
	# @param map_rect (2d array-like)
	# <br>  Format: `[[x, y], [width, height]]`
	# <br>  -- Rectangle defining the area that events can occur
	#
	def __init__(self, map_rect):
		self._map_rect = map_rect
		self._location = self._map_rect[0]
		self._dimensions = self._map_rect[1]
		self._events = set()
		self._step_num = 0


	def remove_event(self, event):
		self._events.remove(event)


	def get_events(self):
		return self._events


	def step(self, timestep):
		self._step_num += timestep
		event_x = np.random.uniform(self._dimensions[0]/2) + self._location[0]
		event_y = np.random.uniform(self._dimensions[1]/2) + self._location[1]
		self._events.add(Event([event_x, event_y], self._step_num))


	def draw(self, dtool):
		dtool.set_color((30, 30, 120))
		dtool.set_stroke_width(0);
		for event in self._events:
			dtool.draw_circle((event.location[0],event.location[1]), 2)
			

