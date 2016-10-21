import numpy as np
import argparse
import sys
from Game import Game_Object

def get_cmdline_args():
    parser = argparse.ArgumentParser(description="Safe Navigation simulator", prog=sys.argv[0])
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
    return parser.parse_args(sys.argv[1:])

if __name__ == '__main__':
    Game = Game_Object(get_cmdline_args())
    if (Game.GameLoop() == 1):
        print ("Error occured ... ")
    else:
        print ("Completed")
