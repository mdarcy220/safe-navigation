# distutils: language = c
# distutils: sources = c_src/_Vector.c
# cython: profile = True

## @package Vector
#
# Provides basic vector math routines
#

cimport numpy as np

cdef extern from "c_src/_Vector.h":
	cdef double distance_between_doublearr(double * point_a, double * point_b, int size);


cdef inline double _cython_distance_between(np.ndarray[double, ndim=1, mode="c"] point_a, np.ndarray[double, ndim=1, mode="c"] point_b):
	return distance_between_doublearr(<double*> np.PyArray_DATA(point_a), <double*> np.PyArray_DATA(point_b), point_a.shape[0]);
cdef inline double _cython_wrap_distance_between(point_a, point_b):
	if isinstance(point_a, np.ndarray) and isinstance(point_b, np.ndarray) and point_a.dtype == np.float64 and point_b.dtype == np.float64:
		return _cython_distance_between(point_a, point_b);
	return _cython_distance_between(np.array(point_a, dtype=np.float64), np.array(point_b, dtype=np.float64));
