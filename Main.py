import numpy as np
import argparse
import sys
from Game import Game_Object

def get_cmdline_args():
    parser = argparse.ArgumentParser(description="Safe Navigation simulator", prog=sys.argv[0])
    parser.add_argument('--enable-memory',
            help='Enable memory for the robot',
            dest='enable_memory',
            default=False,
            action='store_true'
    );
    parser.add_argument('--fast-computing',
            help='Enable fast computing mode',
            dest='fast_computing',
            default=False,
            action='store_true'
    );
    parser.add_argument('--target-distribution-type',
            help='Type of target distribution to use',
            dest='target_distribution_type',
            choices=['gaussian', 'rectangular'],
            default='gaussian',
            action='store'
    );
    parser.add_argument('--robot-speed',
            help='Base speed of the robot',
            dest='robot_speed',
            type=int,
            default=10,
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
    return parser.parse_args(sys.argv[1:])

if __name__ == '__main__':
    Game = Game_Object(get_cmdline_args())
    if (Game.GameLoop() == 1):
        print ("Error occured ... ")
    else:
        print ("Completed")
