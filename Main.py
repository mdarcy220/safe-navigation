import numpy as np
import argparse
import sys
from Game import Game

def get_cmdline_args():
	parser = argparse.ArgumentParser(description="Safe Navigation simulator", prog=sys.argv[0])
	parser.add_argument('--enable-memory',
			help='Enable memory for the robot',
			dest='enable_memory',
			default=False,
			action='store_true'
	);
	parser.add_argument('--batch-mode',
			help='Enable batch mode (no output except csv line)',
			dest='batch_mode',
			default=False,
			action='store_true'
	);
	parser.add_argument('--enable-pdf-smoothing-filter',
			help='Run a filter to smooth the combined distribution',
			dest='enable_pdf_smoothing_filter',
			default=False,
			action='store_true'
	);
	parser.add_argument('--fast-computing',
			help='Enable fast computing mode',
			dest='fast_computing',
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
			default=50505050500,
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
			help='Name of the map to test on',
			dest='map_name',
			type=str,
			default='Maps/Maps_c.png',
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
	return parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
	Game = Game(get_cmdline_args())
	Game.GameLoop()
