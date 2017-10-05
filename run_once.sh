#!/bin/bash

python_args=( -m "cProfile" -o "/tmp/safenav_profile1.profile")

simulator_args=();
simulator_args+=( --debug-level 1 );
simulator_args+=( --robot-speed 10 );
simulator_args+=( --radar-range 100 );
simulator_args+=( --radar-resolution 5 );
simulator_args+=( --batch-mode );
simulator_args+=( --max-steps 5000 );
simulator_args+=( --robot-movement-momentum 0.0 );
simulator_args+=( --speed-mode 10 );
simulator_args+=( --map-modifier-num 11 );
simulator_args+=( --map-name "Maps/empty.png" );
simulator_args+=( --display-every-frame );


time python3 ${python_args[@]} Main.py ${simulator_args[@]};

gprof2dot -f pstats /tmp/safenav_profile1.profile -o /tmp/safenav_profile1.dot

