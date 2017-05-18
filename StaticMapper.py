#!/usr/bin/python3


import numpy as np
import Vector


class StaticMapper:
	def __init__(self, sensors, initial_gridsize=[800,600]):
		self._radar = sensors['radar'];
		self._gps = sensors['gps'];
		self._griddata = np.zeros(np.array(initial_gridsize), dtype=int);


	def add_observation(self, location=None, full_scan = None, dynamic_scan = None):
		location = location if location is not None else self._gps.location();
		full_scan = full_scan if full_scan is not None else self._radar.scan(location);
		dynamic_scan = dynamic_scan if dynamic_scan is not None else self._radar.scan_dynamic_obstacles(location);

		adjusted_scan = np.array(full_scan, dtype=np.float64);
		dynamic_scan = np.convolve(dynamic_scan, np.ones(5)/5.0, 'same');
		adjusted_scan[dynamic_scan < self._radar.radius-0.001] = self._radar.radius;
		adjusted_scan += 1;

		points = self._obs_points_from_radar(adjusted_scan, location=location);
		grid_data = self._griddata
		for point in points:
			self._set_point_area(grid_data, point, 0b00000101);

		self._set_point_area(grid_data, self._gps.location(), 0b00000000);


	def _set_point_area(self, grid_data, point, value):
		x = int(point[0]);
		y = int(point[1]);
		grid_data[x-2, y-2] = value;
		grid_data[x-1, y-2] = value;
		grid_data[x,   y-2] = value;
		grid_data[x+1, y-2] = value;
		grid_data[x+2, y-2] = value;

		grid_data[x-2, y-1] = value;
		grid_data[x-1, y-1] = value;
		grid_data[x,   y-1] = value;
		grid_data[x+1, y-1] = value;
		grid_data[x+2, y-1] = value;

		grid_data[x-2, y  ] = value;
		grid_data[x-1, y  ] = value;
		grid_data[x,   y  ] = value;
		grid_data[x+1, y  ] = value;
		grid_data[x+2, y  ] = value;

		grid_data[x-2, y+1] = value;
		grid_data[x-1, y+1] = value;
		grid_data[x,   y+1] = value;
		grid_data[x+1, y+1] = value;
		grid_data[x+2, y+1] = value;

		grid_data[x-2, y+2] = value;
		grid_data[x-1, y+2] = value;
		grid_data[x,   y+2] = value;
		grid_data[x+1, y+2] = value;
		grid_data[x+2, y+2] = value;
		

	def get_grid_data(self):
		return self._griddata;

		
	## Convert radar data to a list of observed obstacle locations
	#
	# @param radar_data
	# (numpy array)
	# <br>	Format: `[ang1_dist, ang2_dist, ...]`
	# <br>	The radar data to convert. It has the same format as 
	# 	described in the `Radar.Radar` class.
	# <br>	See also: `Radar.Radar.scan`
	#
	# @param location
	# (numpy array)
	# <br>	Format: `[x, y]`
	# <br>	Point of reference for the conversion. All obstacle points 
	# 	are translated by this value
	#
	def _obs_points_from_radar(self, radar_data, location=np.array([0, 0])):
		points = [];
		radar_range = self._radar.radius

		vec_buf = np.zeros(2, dtype=np.float64);

		for angle_deg in np.arange(0, len(radar_data), 1):
			dist = radar_data[angle_deg];
			if dist < radar_range-3:
				new_point = location + (dist * Vector.unit_vec_from_radians(angle_deg * np.pi / 180, buf=vec_buf));
				if not (0 < len(points) and Vector.distance_between(points[-1], new_point) < 3):
					points.append(new_point);
		return points;

