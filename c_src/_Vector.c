#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "_Vector.h"

double distance_between_doublearr(double * point_a, double * point_b, int size)
{
	double total = 0.0;
	int i;
	for(i = 0; i < size; i++) {
		double tmp = point_b[i] - point_a[i];
		total += tmp * tmp;
	}
	return sqrt(total);
}
