
import Vector

## @package Receiver
#

## Receives broadcasts for a robot
#
#
class ReceiverSensor:
	##
	# @param robot
	# <br>  -- The robot this sensor is attached to
	#
	# @param channel
	# <br>  -- The BroadcastChannel object on which to listen for broadcasts.
	#
	def __init__(self, robot, channel):
		self._robot = robot;
		self._channel = channel


	def get_recent_bcasts(self):
		messages = self._channel.get_messages_from_time(self._robot.stepNum-1)
		received_messages = []
		for msg in messages:
			if Vector.distance_between(msg['location'], self._robot.location) <= msg['range']:
				received_messages.append(msg)

		return received_messages

