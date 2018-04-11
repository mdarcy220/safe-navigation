
import pygame as PG
import argparse
import sys

## Sets of a Pygame display and controller for the given Game with the given environment dimensions.
#
# `env_size` should be passed as a tuple of (width, height).
#
# Returns the gameDisplay from `PG.display.set_mode`. This is useful for
# setting up a DrawTool later.
#
def setup_pygame_window(sim, env_size, window_title='Pygame Window'):

	PG.init()
	gameDisplay = PG.display.set_mode(env_size)
	PG.display.set_caption(window_title)
	def render_pygame(*args):
		PG.display.update()
	sim.add_trigger('post_update_display', render_pygame)

	## Handles pygame events.
	#
	# Processes any received keypresses or mouse clicks.
	#
	def handle_pygame_events():
		for event in PG.event.get():
			if event.type == PG.QUIT:
				sim.quit()
			elif event.type == PG.KEYDOWN:
				if event.key == PG.K_u:
					self.update_game_image()
				elif event.key == PG.K_q:
					sim.quit()
				elif event.key == PG.K_e:
					sim_display_every_frame = (not sim._display_every_frame)
				elif event.key == PG.K_p:
					sim.pause()
				elif event.key == PG.K_s:
					sim.step()
	sim.add_trigger('pre_frame', handle_pygame_events)

	return gameDisplay


def create_default_cmdline_parser():
	parser = argparse.ArgumentParser(description="Safe Navigation simulator", prog=sys.argv[0])
	parser.add_argument('--enable-memory',
			help='Enable memory for the robot',
			dest='enable_memory',
			default=False,
			action='store_true'
	);
	parser.add_argument('--enable-pdf-smoothing-filter',
			help='Run a filter to smooth the combined distribution',
			dest='enable_pdf_smoothing_filter',
			default=False,
			action='store_true'
	);
	parser.add_argument('--show-real-time-plot',
			help='Show a real-time plot of PDFs',
			dest='show_real_time_plot',
			default=False,
			action='store_true'
	);
	parser.add_argument('--use-integer-robot-location',
			help='Set the simulation to store the robot location as an integer instead of a floating-point value',
			dest='use_integer_robot_location',
			default=False,
			action='store_true'
	);
	parser.add_argument('--display-every-frame',
			help='Display every frame ',
			dest='display_every_frame',
			default=False,
			action='store_true'
	);
	parser.add_argument('--unique-id',
			help='A unique identifier for this simulation (printed in the CSV output). If omitted, a random identifier is generated.',
			dest='unique_id',
			default='',
			action='store'
	);
	parser.add_argument('--target-distribution-type',
			help='Type of target distribution to use',
			dest='target_distribution_type',
			choices=['gaussian', 'rectangular', 'dotproduct'],
			default='gaussian',
			action='store'
	);
	parser.add_argument('--robot-movement-momentum',
			help='Momentum for robot movement (range 0 to 1, 0 means no momentum)',
			dest='robot_movement_momentum',
			type=float,
			default=0.0,
			action='store'
	);
	parser.add_argument('--robot-memory-size',
			help='Maximum number of visited points to store in memory',
			dest='robot_memory_size',
			type=int,
			default=500,
			action='store'
	);
	parser.add_argument('--robot-memory-sigma',
			help='Sigma of the robot memory gaussian',
			dest='robot_memory_sigma',
			type=float,
			default=25,
			action='store'
	);
	parser.add_argument('--robot-memory-decay',
			help='Decay factor for the effect of remembered points over time',
			dest='robot_memory_decay',
			type=float,
			default=1,
			action='store'
	);
	parser.add_argument('--ped-id-to-replace',
			help='The pedestrian ID to swap for the robot',
			dest='ped_id_to_replace',
			type=int,
			default=0,
			action='store'
	);
	parser.add_argument('--max-fps',
			help='Max number of frames per second. Note that setting this to a small value will NOT improve the performance of the simulation, because it runs at one step per frame. For best performance, set this to a very high value, but low values may be useful for debugging.',
			dest='max_fps',
			type=int,
			default=0,
			action='store'
	);
	parser.add_argument('--max-steps',
			help='Maximum number of steps to take before terminating the simulation. Defaults to 1,000,000',
			dest='max_steps',
			type=int,
			default=1000000,
			action='store'
	);
	parser.add_argument('--robot-speed',
			help='Base speed of the robot',
			dest='robot_speed',
			type=int,
			default=6,
			action='store'
	);
	parser.add_argument('--map-modifier-num',
			help='Numeric ID of desired map modifier.',
			dest='map_modifier_num',
			type=int,
			default=-1,
			action='store'
	);
	parser.add_argument('--speed-mode',
			help='Speed mode of the Obstacles and the Robot',
			dest='speedmode',
			type=int,
			default=1,
			action='store'
	);
	parser.add_argument('--radar-range',
			help='Range of the rader, in pixels',
			dest='radar_range',
			type=float,
			default=100,
			action='store'
	);
	parser.add_argument('--radar-resolution',
			help='Resolution of the rader, in pixels',
			dest='radar_resolution',
			type=float,
			default=4,
			action='store'
	);
	parser.add_argument('--radar-noise-level',
			help='Width of Gaussian for radar noise',
			dest='radar_noise_level',
			type=float,
			default=0.02,
			action='store'
	);
	parser.add_argument('--map-name',
			help='Name of the map file to test on',
			dest='map_name',
			type=str,
			default='',
			action='store'
	);
	parser.add_argument('--debug-level',
			help='Amount of debugging info to show',
			dest='debug_level',
			type=int,
			default=0,
			action='store'
	);
	parser.add_argument('--start-delay',
			help='Number of seconds to wait before starting',
			dest='start_delay',
			type=int,
			default=0,
			action='store'
	);
	parser.add_argument('--window-title',
			help='What to set the window title to',
			dest='window_title',
			type=str,
			default='Robot Simulator',
			action='store'
	);
	parser.add_argument('--output-prng-state',
			help='Include the starting state of the PRNG in the final output (pickled, encoded as base64)',
			dest='output_prng_state',
			default=False,
			action='store_true'
	);
	parser.add_argument('--prng-start-state',
			help='Base64-encoded pickle of the starting state for the PRNG',
			dest='prng_start_state',
			type=str,
			default=None,
			action='store'
	);


	return parser
