
import Vector

class NavigationObjective:
	def __init__(self, target, env):
		self._target = target
		self._env = env

	def test(self, robot):
		return (Vector.distance_between(robot.location, self._target.position) < 0.5)
		
