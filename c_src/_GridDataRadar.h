#ifndef _GRID_DATA_RADAR_H_
#define _GRID_DATA_RADAR_H_

void _c_scan_generic(double centerx,
		double centery,
		double radius,
		long * grid_data,
		int grid_data_width,
		int grid_data_height,
		int cell_type_flags,
		double resolution,
		double degreeStep,
		double * out_data,
		int out_data_size);

#endif
