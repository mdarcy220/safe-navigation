
## @package Broadcaster
#

## A broadcaster that allows robots to send broadcasts.
#
#
class Broadcaster:
	##
	# @param robot
	# <br>  -- The robot this sensor is attached to
	#
	# @param channel
	# <br>  -- The BroadcastChannel object on which to send broadcasts.
	#          Receivers subscribed to this channel will be able to receive
	#          the broadcasts if they are in range.
	#
	# @param bcast_range
	# <br>  -- The range of this broadcaster. Robots outside the range will
	#          not receive the message.
	#
	def __init__(self, channel, bcast_range=float('inf')):
		self._robot = robot;
		self._channel = channel
		self._bcast_range = bcast_range


	def send_bcast(self, bcast_msg):
		self._channel.add_message(bcast_msg, self._robot.location, self._bcast_range, self._robot.stepNum)


