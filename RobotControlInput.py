#!/usr/bin/python3

## Represents a control input for a robot. The control consists of a speed
# and a direction, which together define a single action for the robot to
# take.
#
class RobotControlInput:
	def __init__(self, speed=0, angle=0):
		self.speed = speed;
		self.angle = angle;

