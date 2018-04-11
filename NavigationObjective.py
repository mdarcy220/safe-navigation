
import Vector

class Objective:
	def __init__(self):
		pass

	def test(self):
		raise NotImplementedError('Objective.test needs to be overridden by subclass')

class NavigationObjective(Objective):
	def __init__(self, target, env):
		super().__init__()

		self._target = target
		self._env = env

	def test(self, robot):
		return (Vector.distance_between(robot.location, self._target.position) < self._target.radius)
		
