#!/usr/bin/python3
# distutils: language = c
# distutils: source = c_src/_GridDataRadar.c

## @package C_GridDataRadar
#

cimport numpy as np

cdef extern from "c_src/_GridDataRadar.h":
	cdef void _c_scan_generic(double centerx,
		double centery,
		double radius,
		long * grid_data,
		int grid_data_width,
		int grid_data_height,
		int cell_type_flags,
		double resolution,
		double degreeStep,
		double * out_data,
		int out_data_size
	);

cdef inline void scan_generic(double centerx,
	double centery,
	double radius,
	np.ndarray[long, ndim=2, mode="c"] grid_data,
	int cell_type_flags,
	double resolution,
	double degreeStep,
	np.ndarray[double] out_data):

	_c_scan_generic(float(centerx),
		float(centery),
		float(radius),
		<long *> np.PyArray_DATA(grid_data),
		int(grid_data.shape[0]),
		int(grid_data.shape[1]),
		int(cell_type_flags),
		resolution,
		int(degreeStep),
		<double *> np.PyArray_DATA(out_data),
		int(out_data.shape[0]));
