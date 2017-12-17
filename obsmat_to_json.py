#!/usr/bin/env -p python3

import json
import os
import sys

if len(sys.argv) < 3:
	print("Usage: python3 obsmat2json.py path/to/obsmat.txt path/to/output.json")
	sys.exit(1)

obsmat_filename = sys.argv[1];
output_filename = sys.argv[2];

pedestrians = dict()

with open(obsmat_filename, 'r') as f:
	for line in f.readlines():
		# Remove trailing newline
		line = line[:-1]

		# Weird line format; vals separated by three spaces, with three
		# leading spaces before the first val in the line
		fields = [field for field in line.split(' ') if field != '']

		# If this is the first time seeing the pedestrian, add them
		pedestrian_id = int(float(fields[1]))
		if pedestrian_id not in pedestrians:
			pedestrians[pedestrian_id] = []

		# Add the sample
		pedestrians[pedestrian_id].append({
			'time':  float(fields[0]),
			'pos_x': float(fields[2]),
			'pos_y': float(fields[4]),
			'vel_x': float(fields[5]),
			'vel_y': float(fields[7]),
		})

with open(output_filename, 'w') as f:
	json.dump(pedestrians, f, indent=4, sort_keys=True)

