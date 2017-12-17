#include <math.h>
#include <stdio.h>
#include "_GridDataRadar.h"

#define MIN_RESOLUTION 0.00001

void _c_scan_generic(double centerx, double centery, double radius, long * grid_data, int grid_data_width, int grid_data_height, int cell_type_flags, double resolution, double degreeStep, double * out_data, int out_data_size)
{
	
	int i;
	double degree;
	double check_dist;

	if (resolution <= MIN_RESOLUTION) {
		resolution = MIN_RESOLUTION;
	}

	for(i = 0, degree = 0.0; i < out_data_size && degree <= 360.0; i++, degree+=degreeStep) {
		double ang_in_radians = degree * M_PI / 180.0;
		double cos_cached = cos(ang_in_radians);
		double sin_cached = sin(ang_in_radians);
		for(check_dist = 0; check_dist < radius; check_dist += resolution) {
			int x = (int)(cos_cached * check_dist + centerx);
			int y = (int)(sin_cached * check_dist + centery);
			if((x < 0) || (y < 0) || (grid_data_width <= x) || (grid_data_height <= y) || (grid_data[x * grid_data_height + y] & cell_type_flags)) {
				out_data[i] = check_dist;
				break;
			}
		}
	}
}
