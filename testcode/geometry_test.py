#!/usr/bin/python3

from Polygon import Polygon
import numpy as np
from Human import Human
import Geometry

def test_generic(actual_outputs, correct_outputs, abs_error, do_pass, do_fail):

	# Keep track of correct outputs we've already matched. Important in
	# case of duplicates, i.e., if there needs to be exactly two points
	# that are almost exactly the same
	eliminated_correct_outputs = set()

	# Make sure these are indexable, and sort for better visual matchup in
	# printout
	correct_outputs = sorted([out for out in correct_outputs], key=lambda x: x[0])
	actual_outputs = sorted([out for out in actual_outputs], key=lambda x: x[0])

	if len(actual_outputs) != len(correct_outputs):
		do_fail('Wrong number of results')
		return False

	# Performance isn't an issue for now; just use a nested loop
	for output in actual_outputs:
		for i in range(len(correct_outputs)):
			if i in eliminated_correct_outputs:
				continue
			correct_output = correct_outputs[i]
			if abs(output[0] - correct_output[0]) <= abs_error and abs(output[1] - correct_output[1]) <= abs_error:
				eliminated_correct_outputs.add(i)
				break
	if len(eliminated_correct_outputs) == len(correct_outputs):
		do_pass()
		return True
	else:
		do_fail('Wrong answer')
		return False


## Tests the Polygon.line_intersection function against a known correct output
# 
# @param polygon_list
# <br> Format: `[[x1, y1], [x2, y2], ... [xn, yn]]`
# <br> -- List of points to construct the polygon
#
# @param line
# <br> -- Points defining the line; see Geometry definition
#
# @param correct_outputs
# <br> -- List of correct intersection points
#
# @param abs_error (float)
# <br> -- The maximum absolute error for considering "correct" values
#
def test_polygon_line_intersection(polygon_list, line, correct_outputs, abs_error=1e-8):
	polygon = Polygon(np.array(polygon_list))
	actual_outputs = polygon.line_intersection(line)

	def do_fail(msg):
		print('FAIL: {}'.format(msg))
		print('    Polygon: {}'.format(', '.join(map(str, polygon_list))))
		print('    Line:    {}'.format(', '.join(map(str, line))))
		print('    Correct: {}'.format(', '.join(map(str, correct_outputs))))
		print('    Actual:  {}'.format(', '.join(map(str, actual_outputs))))
		print()

	def do_pass(msg=''):
		print('PASS: {}'.format('[' + ', '.join(map(str, polygon_list)) + '] with [' + ', '.join(map(str, line)) + ']'))

	return test_generic(actual_outputs, correct_outputs, abs_error, do_pass, do_fail)


def test_human_line_intersection(human_center, human_width, human_height, human_v_x, human_v_y, line, correct_outputs, abs_error=1e-8):
	human = Human(human_center, human_width, human_height, human_v_x, human_v_y)
	human_str = 'Human({}, {}, {}, {}, {})'.format(human_center, human_width, human_height, human_v_x, human_v_y)
	actual_outputs = human.line_intersection(line)

	def do_fail(msg):
		print('FAIL: {}'.format(msg))
		print('    Human:   {}'.format(human_str))
		print('    Line:    {}'.format(', '.join(map(str, line))))
		print('    Correct: {}'.format(', '.join(map(str, correct_outputs))))
		print('    Actual:  {}'.format(', '.join(map(str, actual_outputs))))
		print()

	def do_pass(msg=''):
		print('PASS: {}'.format(human_str + ' with [' + ', '.join(map(str, line)) + ']'))

	return test_generic(actual_outputs, correct_outputs, abs_error, do_pass, do_fail)


polygon_1_list = np.array([[2,10],[12,10],[12,4]])

test_polygon_line_intersection(polygon_1_list, np.array([[10,0], [10,10]]), [[10,10],[10,5.2]])
test_polygon_line_intersection(polygon_1_list, np.array([[0,0],[250/13,10]]), [[12,6.24],[10,5.2]])


polygon_2_list = np.array([[2,5],[7,5],[7,4],[9,4],[9,3],[2,3]])

test_polygon_line_intersection(polygon_2_list, np.array([[2,3], [3,5]]), [[2,3],[3,5]])
test_polygon_line_intersection(polygon_2_list, np.array([[9,3.5],[8.8,4]]), [[9,3.5],[8.8,4]])
test_polygon_line_intersection(polygon_2_list, np.array([[2,3], [2,5]]), [[2,3],[2,5]])

# TODO: These commented-out test cases may have incorrect answers (as in, the
# manually-calculated "correct" value is wrong). Do not use until
# double-checked.

#human_1_args = [[2,3],4,6,1,0]
#
#test_human_line_intersection(*human_1_args,np.array([[0,0],[1,1]]), [[3.91,3.91],[0.71,0.71]])
#test_human_line_intersection(*human_1_args,np.array([[0,1],[1,4]]), [[1.65,5.95],[0.22,1.65]])
#test_human_line_intersection(*human_1_args,np.array([[0,6],[1,6]]), [[2,6]])
#test_human_line_intersection(*human_1_args,np.array([[0,0],[1,0]]), [[2,0]])
#test_human_line_intersection(*human_1_args,np.array([[0,0],[0,1]]), [[0,3]])
#test_human_line_intersection(*human_1_args,np.array([[4,0],[4,1]]), [[4,3]])


human_2_args = [[5,5],6,2,1,1]

test_human_line_intersection(*human_2_args, np.array([[0,0],[5+1.5*np.sqrt(2),5-1.5*np.sqrt(2)]]), [])
test_human_line_intersection(*human_2_args, np.array([[0,5],[5,5]]), [[3.658359213500125, 5]])

human_3_args = [[0,0],4,2,0,0]
test_human_line_intersection(*human_3_args, np.array([[0,0],[5,5]]), [[0.894427190999916, 0.894427190999916]])

