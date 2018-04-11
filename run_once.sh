#!/bin/bash

python_args=( -m "cProfile" -o "/tmp/safenav_profile1.profile")

simulator_args=();
simulator_args+=( --debug-level 1 );
simulator_args+=( --robot-speed 10 );
simulator_args+=( --radar-range 100 );
simulator_args+=( --max-steps 5000 );
simulator_args+=( --max-fps 0 );
simulator_args+=( --robot-movement-momentum 0.0 );
simulator_args+=( --speed-mode 0 );
simulator_args+=( --map-modifier-num 12 );
simulator_args+=( --display-every-frame );


time python3 ${python_args[@]} run_default.py ${simulator_args[@]};

gprof2dot -f pstats /tmp/safenav_profile1.profile -o /tmp/safenav_profile1.dot;
dot -T svg /tmp/safenav_profile1.dot > /tmp/safenav_profile1.svg;

